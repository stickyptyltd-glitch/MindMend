# MindMend Gemini Migration Runbook
**For:** On-call Engineers, DevOps Team
**Date:** 2025-10-10 (AEDT)
**Version:** 1.0

---

## Purpose

This is a **single-sitting, do-this-now** operations guide for executing and managing the Gemini migration. Follow steps in order.

---

## Prerequisites Checklist

Before starting ANY migration work:

```bash
# 1. Authenticate to GCP
gcloud auth login
gcloud config set project mindmend-production

# 2. Verify cluster access
kubectl cluster-info
kubectl get nodes

# 3. Verify you have required roles
gcloud projects get-iam-policy mindmend-production \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)"

# Expected roles:
# - roles/container.admin (GKE access)
# - roles/aiplatform.user (Vertex AI access)
# - roles/secretmanager.admin (Secret access)

# 4. Install required tools
pip install google-cloud-aiplatform google-auth
kubectl version
jq --version
```

**Stop if any prerequisite fails. Escalate immediately.**

---

## Phase 1: Pre-Migration State Collection

**Duration:** 15 minutes
**Risk:** Low

### 1.1 Collect Infrastructure State

```bash
cd /home/mindmendxyz/MindMend
./docs/migration/gemini/scripts/collect_state.sh
```

**Expected:** JSON files in `docs/migration/gemini/artifacts/`

**Verify:**
```bash
ls -lh docs/migration/gemini/artifacts/
cat docs/migration/gemini/artifacts/summary.txt
```

### 1.2 Baseline Performance

```bash
# Check current pod resource usage
kubectl top pods --namespace=default

# Check current response times (last 1h)
gcloud logging read "resource.type=k8s_container AND \
  httpRequest.latency:*" \
  --limit=100 \
  --format=json \
  --project=mindmend-production | \
  jq -r '.[] | .httpRequest.latency' | \
  awk '{s+=$1; n++} END {print "Avg latency:",s/n,"s"}'
```

**Record these values in `artifacts/baseline.txt`**

### 1.3 Verify Current Health

```bash
# Check all pods are healthy
kubectl get pods --all-namespaces | grep -v "Running\|Completed"

# If any unhealthy pods, STOP and investigate
# Expected: No output (all pods running)

# Check external health endpoint
curl -f http://34.143.177.214/health || echo "HEALTH CHECK FAILED"

# Expected: {"status":"healthy"}
```

**Stop if health checks fail.**

---

## Phase 2: Enable Vertex AI

**Duration:** 10 minutes
**Risk:** Low

### 2.1 Enable APIs

```bash
# Enable Vertex AI
gcloud services enable aiplatform.googleapis.com \
  --project=mindmend-production

# Verify enabled
gcloud services list --enabled \
  --filter="NAME:aiplatform.googleapis.com" \
  --project=mindmend-production
```

### 2.2 Check Quotas

```bash
# Check current quotas
gcloud alpha services quotas list \
  --service=aiplatform.googleapis.com \
  --project=mindmend-production \
  --filter="metric.displayName:prediction" \
  --format="table(metric.displayName,quotaId,effectiveLimit,dimensions)"

# If limits are too low (<1000 requests/min), request increase:
# https://console.cloud.google.com/iam-admin/quotas?project=mindmend-production
```

**Required minimums:**
- Online prediction requests: 1000/min
- Batch prediction requests: 100/min

---

## Phase 3: Configure IAM & Secrets

**Duration:** 15 minutes
**Risk:** Medium

### 3.1 Create Service Account

```bash
# Create SA for Vertex AI access
gcloud iam service-accounts create vertex-ai-client \
  --display-name="Vertex AI Client for MindMend" \
  --project=mindmend-production

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding mindmend-production \
  --member="serviceAccount:vertex-ai-client@mindmend-production.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Grant to backend pods
kubectl create serviceaccount vertex-ai-sa --namespace=default

# Bind to GCP SA (Workload Identity)
gcloud iam service-accounts add-iam-policy-binding \
  vertex-ai-client@mindmend-production.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:mindmend-production.svc.id.goog[default/vertex-ai-sa]" \
  --project=mindmend-production
```

### 3.2 Create Secrets

```bash
# Store project ID
echo -n "mindmend-production" | \
  gcloud secrets create VERTEX_AI_PROJECT \
    --data-file=- \
    --replication-policy=automatic \
    --project=mindmend-production

# Store location
echo -n "australia-southeast1" | \
  gcloud secrets create VERTEX_AI_LOCATION \
    --data-file=- \
    --replication-policy=automatic \
    --project=mindmend-production

# Grant access to backend SA
for SECRET in VERTEX_AI_PROJECT VERTEX_AI_LOCATION; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:vertex-ai-client@mindmend-production.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=mindmend-production
done
```

### 3.3 Verify Access

```bash
# Test secret access
gcloud secrets versions access latest \
  --secret=VERTEX_AI_PROJECT \
  --project=mindmend-production

# Expected: mindmend-production
```

---

## Phase 4: Deploy Canary Build

**Duration:** 30 minutes
**Risk:** High (TEST IN STAGING FIRST)

### 4.1 Build Gemini-Enabled Image

```bash
cd /home/mindmendxyz/MindMend

# Checkout feature branch (if exists)
git checkout gemini-migration || echo "Using current branch"

# Build with Gemini SDK
docker build \
  -t gcr.io/mindmend-production/mindmend-app:gemini-canary-v1 \
  --build-arg ENABLE_GEMINI=true \
  .

# Push to registry
docker push gcr.io/mindmend-production/mindmend-app:gemini-canary-v1
```

### 4.2 Create Canary Deployment

**IMPORTANT:** Do this in STAGING first!

```bash
# Create canary deployment (10% traffic)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mindmend-backend-canary
  labels:
    app: mindmend-backend
    version: canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mindmend-backend
      version: canary
  template:
    metadata:
      labels:
        app: mindmend-backend
        version: canary
    spec:
      serviceAccountName: vertex-ai-sa
      containers:
      - name: mindmend-app
        image: gcr.io/mindmend-production/mindmend-app:gemini-canary-v1
        ports:
        - containerPort: 8000
        env:
        - name: AI_PROVIDER
          value: "gemini"
        - name: VERTEX_AI_PROJECT
          valueFrom:
            secretKeyRef:
              name: vertex-secrets
              key: project_id
        - name: VERTEX_AI_LOCATION
          value: "australia-southeast1"
        - name: GEMINI_MODEL
          value: "gemini-1.5-pro"
        - name: CANARY_PERCENTAGE
          value: "10"
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
EOF

# Wait for canary to be ready
kubectl rollout status deployment/mindmend-backend-canary

# Verify canary pod is running
kubectl get pods -l app=mindmend-backend,version=canary
```

### 4.3 Configure Traffic Split

```bash
# Update service to include canary (weighted routing)
# This is load balancer dependent - example for Istio:

kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: mindmend-backend-service
spec:
  selector:
    app: mindmend-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
EOF

# For basic k8s, use label selector to include both stable and canary
# Traffic will be distributed based on replica count
```

---

## Phase 5: Monitor Canary

**Duration:** 2-48 hours
**Risk:** Medium

### 5.1 Real-Time Monitoring

```bash
# Watch canary logs
kubectl logs -f deployment/mindmend-backend-canary

# Watch for errors
kubectl logs deployment/mindmend-backend-canary | grep -i error

# Watch resource usage
watch kubectl top pods -l version=canary
```

### 5.2 Check Error Rate

```bash
# Errors in last 15 minutes
gcloud logging read "resource.type=k8s_container AND \
  resource.labels.pod_name:canary AND \
  severity>=ERROR AND \
  timestamp>=\"$(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --limit=50 \
  --project=mindmend-production

# Count errors
gcloud logging read "resource.type=k8s_container AND \
  resource.labels.pod_name:canary AND \
  severity>=ERROR" \
  --limit=1000 \
  --format=json | jq 'length'
```

**Rollback if error count > 50 in 15 minutes**

### 5.3 Check Latency

```bash
# Average response time for canary
gcloud logging read "resource.type=k8s_container AND \
  resource.labels.pod_name:canary AND \
  httpRequest.latency:*" \
  --limit=100 \
  --format=json | \
  jq -r '.[] | .httpRequest.latency' | \
  awk '{s+=$1; n++} END {print "Avg:",s/n,"s"}'
```

**Rollback if latency > 2x baseline**

### 5.4 Check Quota Usage

```bash
# Check Vertex AI usage
gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint" \
  --limit=100 \
  --format=json \
  --project=mindmend-production

# Check for quota exceeded errors
gcloud logging read "protoPayload.status.code=8" \
  --limit=50 \
  --format=json \
  --project=mindmend-production
```

**Quota error code 8 = RESOURCE_EXHAUSTED**

---

## Phase 6: Rollback (If Needed)

**Duration:** < 2 minutes
**Risk:** Low

### IMMEDIATE ROLLBACK

```bash
# Scale canary to zero
kubectl scale deployment mindmend-backend-canary --replicas=0

# Verify traffic restored
kubectl get pods -l app=mindmend-backend

# Check health
curl http://34.143.177.214/health

# Monitor logs
kubectl logs deployment/mindmend-backend -f | grep -i error
```

### COMPLETE ROLLBACK

```bash
# Delete canary deployment
kubectl delete deployment mindmend-backend-canary

# Revert to previous stable image
kubectl set image deployment/mindmend-backend \
  mindmend-app=gcr.io/mindmend-production/mindmend-app:security-fix-v4

# Wait for rollback
kubectl rollout status deployment/mindmend-backend

# Verify
kubectl rollout history deployment/mindmend-backend
```

### Post-Rollback Actions

```bash
# Collect failure logs
kubectl logs deployment/mindmend-backend-canary > \
  /tmp/canary-failure-logs-$(date +%Y%m%d-%H%M%S).txt

# Export Cloud Logging
gcloud logging read "resource.labels.pod_name:canary" \
  --limit=1000 \
  --format=json \
  --project=mindmend-production > \
  /tmp/canary-failure-cloudlogs-$(date +%Y%m%d-%H%M%S).json

# Create incident report
# [TODO: Link to incident template]
```

---

## Phase 7: Gradual Rollout (If Canary Successful)

### 7.1 Increase to 50%

**After 48 hours of successful 10% canary:**

```bash
# Scale canary to match production
kubectl scale deployment/mindmend-backend-canary --replicas=1
kubectl scale deployment/mindmend-backend --replicas=1

# This gives 50/50 traffic split

# Monitor for 48 hours (repeat Phase 5 monitoring)
```

### 7.2 Full Cutover (100%)

**After 48 hours of successful 50% traffic:**

```bash
# Update main deployment to Gemini image
kubectl set image deployment/mindmend-backend \
  mindmend-app=gcr.io/mindmend-production/mindmend-app:gemini-canary-v1

# Wait for rollout
kubectl rollout status deployment/mindmend-backend

# Delete canary deployment
kubectl delete deployment mindmend-backend-canary

# Verify all pods on Gemini
kubectl get pods -l app=mindmend-backend -o \
  jsonpath='{.items[*].spec.containers[0].image}'

# Expected: gcr.io/mindmend-production/mindmend-app:gemini-canary-v1 (all pods)
```

### 7.3 Post-Cutover Monitoring

Monitor for 7 days:

```bash
# Daily health check script
#!/bin/bash
echo "=== Daily Gemini Health Check - $(date) ==="

echo "1. Error Rate:"
gcloud logging read "severity>=ERROR" --limit=1000 \
  --format=json | jq 'length'

echo "2. Average Latency:"
gcloud logging read "httpRequest.latency:*" --limit=100 \
  --format=json | jq -r '.[] | .httpRequest.latency' | \
  awk '{s+=$1; n++} END {print s/n,"s"}'

echo "3. Vertex AI Quota:"
gcloud alpha services quotas list \
  --service=aiplatform.googleapis.com \
  --filter="metric.displayName:prediction" \
  --format="value(effectiveLimit)" \
  --project=mindmend-production

echo "4. Pod Status:"
kubectl get pods -l app=mindmend-backend

echo "=== End Report ==="
```

---

## Phase 8: Cleanup

**After 7 days of successful operation:**

### 8.1 Remove Old API Keys

```bash
# DO NOT delete immediately - keep for 30 days as backup

# Rotate OPENAI_API_KEY to backup secret
gcloud secrets create OPENAI_API_KEY_BACKUP \
  --data-file=<(gcloud secrets versions access latest --secret=OPENAI_API_KEY) \
  --project=mindmend-production

# Update deployment to remove OPENAI_API_KEY env var
kubectl edit deployment mindmend-backend
# Remove OPENAI_API_KEY from env section

# Verify app still works without it
curl http://34.143.177.214/health
```

### 8.2 Update Documentation

```bash
# Mark migration as complete
echo "Migration completed: $(date)" >> docs/migration/gemini/CHANGELOG.md

# Update runbooks
sed -i 's/OpenAI/Gemini/g' docs/runbooks/*.md

# Commit changes
git add docs/
git commit -m "docs: Update for Gemini migration completion"
git push origin main
```

---

## Emergency Contacts

| Issue | Contact | Phone | Email | Hours |
|-------|---------|-------|-------|-------|
| **Production Down** | On-Call Engineer | [TODO] | [TODO] | 24/7 |
| **GCP Quota Issues** | GCP Support | [TODO] | [TODO] | 24/7 |
| **Model Quality Issues** | AI/ML Team Lead | [TODO] | [TODO] | Business |
| **Security Incident** | Security Team | [TODO] | [TODO] | 24/7 |
| **Database Issues** | DBA | [TODO] | [TODO] | 24/7 |

**Emergency Slack Channel:** #mindmend-incidents
**PagerDuty:** [TODO: Add integration key]

---

## Monitoring Dashboards

### Cloud Console URLs

```
# Kubernetes Engine
https://console.cloud.google.com/kubernetes/workload?project=mindmend-production

# Vertex AI
https://console.cloud.google.com/vertex-ai?project=mindmend-production

# Cloud Logging
https://console.cloud.google.com/logs/query?project=mindmend-production

# Cloud Monitoring
https://console.cloud.google.com/monitoring?project=mindmend-production

# Quotas
https://console.cloud.google.com/iam-admin/quotas?project=mindmend-production
```

### Key Metrics to Watch

1. **Error Rate:** < 1%
2. **Latency P95:** < 2000ms
3. **Latency P99:** < 5000ms
4. **Pod CPU:** < 80%
5. **Pod Memory:** < 80%
6. **Vertex AI Quota:** > 20% remaining

---

## Success Criteria

- [ ] Canary running for 48+ hours with < 1% errors
- [ ] Latency within 20% of baseline
- [ ] No quota exceeded errors
- [ ] No safety filter false positives
- [ ] User satisfaction maintained (check feedback)
- [ ] Cost per request within budget
- [ ] All automated tests passing

---

## Common Issues & Solutions

### Issue 1: Quota Exceeded

**Symptom:** Error code 8 (RESOURCE_EXHAUSTED)

**Solution:**
```bash
# Request quota increase
https://console.cloud.google.com/iam-admin/quotas

# Temporary: Implement exponential backoff
# Fallback to OpenAI if quota exhausted
```

### Issue 2: High Latency

**Symptom:** Response time > 2x baseline

**Solution:**
```bash
# Switch to faster model
GEMINI_MODEL=gemini-1.5-flash

# Reduce max_tokens
MAX_OUTPUT_TOKENS=500

# Enable caching (for repeated prompts)
```

### Issue 3: Safety Filter False Positives

**Symptom:** Valid therapy responses blocked

**Solution:**
```bash
# Adjust safety settings in code
BLOCK_MEDIUM_AND_ABOVE → BLOCK_ONLY_HIGH

# Document all cases for future fine-tuning
```

### Issue 4: Authentication Errors

**Symptom:** 401/403 from Vertex AI

**Solution:**
```bash
# Verify service account
gcloud iam service-accounts list

# Check workload identity binding
kubectl describe serviceaccount vertex-ai-sa

# Re-authenticate
gcloud auth application-default login
```

---

## Post-Migration Checklist

- [ ] All canary monitoring passed
- [ ] Full rollout completed
- [ ] Old API keys backed up
- [ ] Documentation updated
- [ ] Team trained on new monitoring
- [ ] Incident response tested
- [ ] Cost tracking configured
- [ ] Performance baselines updated
- [ ] User feedback collected
- [ ] Post-mortem completed (if issues occurred)

---

**Last Updated:** 2025-10-10
**Owner:** [TODO: Assign]
**Next Review:** [TODO: Schedule]
