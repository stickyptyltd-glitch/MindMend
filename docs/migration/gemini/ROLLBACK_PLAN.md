# Gemini Migration Rollback Plan

**Project:** MindMend AI Migration
**Purpose:** Emergency rollback procedures for Gemini migration
**Target RTO:** < 5 minutes
**Target RPO:** 0 (no data loss)
**Date:** 2025-10-10

---

## Quick Reference

### Immediate Rollback Command (< 30 seconds)

```bash
# EMERGENCY: Rollback to OpenAI immediately
kubectl set env deployment/mindmend-backend-canary AI_PROVIDER=openai
kubectl rollout restart deployment/mindmend-backend-canary
```

### Full Rollback Command (< 5 minutes)

```bash
# Scale down Gemini canary
kubectl scale deployment/mindmend-backend-canary --replicas=0

# Scale up OpenAI deployment
kubectl scale deployment/mindmend-backend --replicas=4

# Verify rollback
kubectl rollout status deployment/mindmend-backend
curl http://34.143.177.214/health
```

---

## Rollback Triggers

Execute rollback immediately if ANY of the following occur:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| **Error Rate** | > 5% for 5 minutes | Immediate rollback |
| **Latency p95** | > 3x baseline for 10 minutes | Immediate rollback |
| **Latency p99** | > 5x baseline | Immediate rollback |
| **Critical User Complaints** | > 3 in 15 minutes | Immediate rollback |
| **Cost Spike** | > 50% over budget | Investigate, prepare rollback |
| **Quota Exhaustion** | Vertex AI quota exceeded | Immediate rollback |
| **Safety Filter Issues** | False positive rate > 5% | Immediate rollback |
| **Authentication Failures** | > 10 permission denied errors | Immediate rollback |
| **Complete Service Outage** | No responses for 2 minutes | Immediate rollback |

---

## Rollback Scenarios

### Scenario 1: Feature Flag Rollback (Fastest - < 30 seconds)

**When to use:**
- Canary deployment is running
- Need instant rollback
- No infrastructure changes needed

**Procedure:**

```bash
# Step 1: Switch provider to OpenAI
kubectl set env deployment/mindmend-backend-canary AI_PROVIDER=openai

# Step 2: Verify change
kubectl get deployment mindmend-backend-canary -o yaml | grep AI_PROVIDER

# Step 3: Monitor logs
kubectl logs deployment/mindmend-backend-canary -f | grep "AI client"
# Should see: "Initializing AI client with provider: openai"

# Step 4: Verify health
curl http://34.143.177.214/health
curl -X POST http://34.143.177.214/api/therapy-session \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' | jq .provider
# Should return: "openai"
```

**Verification:**
- ✅ Health check returns 200
- ✅ AI responses work
- ✅ Provider shows "openai"
- ✅ Error rate drops to normal

**Time:** ~30 seconds

---

### Scenario 2: Traffic Shift Rollback (Standard - < 2 minutes)

**When to use:**
- Canary deployment has issues
- Need to shift traffic back to stable version
- Old deployment still running

**Procedure:**

```bash
# Step 1: Scale down canary
kubectl scale deployment/mindmend-backend-canary --replicas=0

# Step 2: Verify canary scaled down
kubectl get pods -l version=gemini
# Should show: No resources found

# Step 3: Scale up stable OpenAI deployment
kubectl scale deployment/mindmend-backend --replicas=4

# Step 4: Wait for rollout
kubectl rollout status deployment/mindmend-backend
# Should complete in ~60 seconds

# Step 5: Verify traffic routing
kubectl get pods -l app=mindmend
# Should show 4 pods from mindmend-backend

# Step 6: Test endpoint
for i in {1..10}; do
  curl -s -X POST http://34.143.177.214/api/therapy-session \
    -H "Content-Type: application/json" \
    -d '{"message":"test"}' | jq .provider
done
# All should return: "openai"
```

**Verification:**
- ✅ Canary pods terminated
- ✅ Stable deployment running
- ✅ 100% traffic on OpenAI
- ✅ Metrics return to baseline

**Time:** ~2 minutes

---

### Scenario 3: Container Rollback (Full - < 5 minutes)

**When to use:**
- Code changes introduced bugs
- Need to rollback to previous container image
- Complete deployment rollback required

**Procedure:**

```bash
# Step 1: Identify previous working image
gcloud container images list-tags \
  gcr.io/mindmend-production/mindmend-app \
  --limit=10 \
  --format="table(tags,timestamp)"

# Identify the pre-gemini tag (e.g., security-fix-v4)
PREVIOUS_IMAGE="gcr.io/mindmend-production/mindmend-app:security-fix-v4"

# Step 2: Rollback deployment to previous image
kubectl set image deployment/mindmend-backend \
  mindmend-app=$PREVIOUS_IMAGE

# Step 3: Monitor rollout
kubectl rollout status deployment/mindmend-backend

# Step 4: Scale down canary completely
kubectl scale deployment/mindmend-backend-canary --replicas=0

# Step 5: Delete canary deployment (optional, for clean state)
kubectl delete deployment mindmend-backend-canary

# Step 6: Verify rollback
kubectl describe deployment mindmend-backend | grep Image
# Should show previous image

# Step 7: Test functionality
./docs/migration/gemini/scripts/smoke_test.sh
```

**Verification:**
- ✅ Old container image running
- ✅ No Gemini code deployed
- ✅ All tests passing
- ✅ Metrics return to baseline

**Time:** ~5 minutes

---

### Scenario 4: Database Rollback (If schema changes made)

**When to use:**
- Migration included database schema changes
- Need to revert schema
- Data migration occurred

**Procedure:**

```bash
# Step 1: Connect to database
kubectl exec -it deployment/postgres-deployment -- \
  psql -U mindmend_user -d mindmend_production

# Step 2: Check for migration tables
\dt
# Look for new tables or columns related to Gemini

# Step 3: Rollback migrations (if Flask-Migrate used)
# From application pod
kubectl exec -it deployment/mindmend-backend -- bash
python << EOF
from app import app, db
from flask_migrate import downgrade

with app.app_context():
    downgrade(revision='<previous_revision_id>')
EOF

# Step 4: Verify schema
\d sessions
\d patients
# Ensure no Gemini-specific columns remain

# Step 5: Exit database
\q
```

**NOTE:** Only required if schema changes were made. Current migration does NOT include schema changes.

**Time:** ~10 minutes

---

## Rollback Validation Checklist

After executing rollback, verify each item:

### Health Checks
- [ ] `/health` endpoint returns 200
- [ ] Database connection working
- [ ] Redis connection working
- [ ] All pods in Ready state

### Functional Tests
- [ ] User can log in
- [ ] Therapy session works
- [ ] AI responses are generated
- [ ] Sessions are saved to database
- [ ] Dashboard loads correctly

### Performance Tests
```bash
# Run quick load test
for i in {1..100}; do
  curl -s -X POST http://34.143.177.214/api/therapy-session \
    -H "Content-Type: application/json" \
    -d '{"message":"test"}' > /dev/null &
done
wait

# Check error rate
kubectl logs deployment/mindmend-backend | grep ERROR | wc -l
# Should be 0 or very low
```

### Metrics Validation
- [ ] Error rate < 1%
- [ ] Latency p95 back to baseline
- [ ] No 500 errors
- [ ] CPU/memory usage normal
- [ ] Active users not affected

### Monitoring
```bash
# Check recent logs
kubectl logs deployment/mindmend-backend --tail=100 | grep -i "error\|fail"

# Check pod status
kubectl get pods --all-namespaces | grep -v Running

# Check recent errors in GCP Logging
gcloud logging read \
  'resource.type="k8s_container" severity>=ERROR' \
  --limit=50 \
  --project=mindmend-production \
  --format="table(timestamp,jsonPayload.message)"
```

---

## Post-Rollback Actions

### Immediate (Within 1 hour)

1. **Notify Stakeholders**
   ```bash
   # Send notification to team
   # Include: What happened, current status, next steps
   ```

2. **Preserve Evidence**
   ```bash
   # Save logs from failed deployment
   kubectl logs deployment/mindmend-backend-canary > rollback_logs.txt

   # Export metrics
   python docs/migration/gemini/scripts/cost_latency_probe.py \
     --endpoint http://34.143.177.214 \
     --duration 60 \
     --output artifacts/post_rollback_metrics.json
   ```

3. **Create Incident Report**
   - What triggered rollback
   - What actions were taken
   - What was the impact
   - Root cause (if known)

### Within 24 Hours

4. **Root Cause Analysis**
   - Review logs and metrics
   - Identify exact failure point
   - Document lessons learned

5. **Fix Planning**
   - Determine fix required
   - Update migration plan
   - Schedule retry (if applicable)

6. **Update Documentation**
   - Update CHANGELOG.md
   - Add to RISKS.md if new risk discovered
   - Update RUNBOOK.md with learnings

### Within 1 Week

7. **Post-Mortem Meeting**
   - What went wrong
   - Why it happened
   - How to prevent in future
   - Action items

8. **Update Rollback Plan**
   - Add any new rollback scenarios discovered
   - Improve procedures based on experience
   - Practice rollback in staging

---

## Monitoring During Rollback

### Key Metrics to Watch

```bash
# Create monitoring dashboard
cat > /tmp/rollback_monitor.sh << 'EOF'
#!/bin/bash

while true; do
  clear
  echo "=== ROLLBACK MONITORING DASHBOARD ==="
  echo "Time: $(date)"
  echo ""

  echo "=== Pod Status ==="
  kubectl get pods -l app=mindmend -o wide | grep -v Terminating
  echo ""

  echo "=== Recent Errors ==="
  kubectl logs deployment/mindmend-backend --tail=20 | grep -i error || echo "No errors"
  echo ""

  echo "=== Request Rate ==="
  kubectl logs deployment/mindmend-backend --tail=500 | grep "POST /api" | wc -l
  echo ""

  echo "=== Health Check ==="
  curl -s http://34.143.177.214/health | jq . || echo "Health check failed"
  echo ""

  sleep 10
done
EOF

chmod +x /tmp/rollback_monitor.sh
/tmp/rollback_monitor.sh
```

### Alert Contacts

| Issue | Contact | Phone | Escalation |
|-------|---------|-------|-----------|
| Rollback not working | DevOps On-Call | [TODO] | VP Engineering |
| Database issues | DBA | [TODO] | CTO |
| User impact | Customer Support | [TODO] | CPO |
| Security concern | Security Team | [TODO] | CISO |

---

## Testing Rollback Procedures

### Monthly Rollback Drill

Execute this drill monthly to ensure team readiness:

```bash
# 1. Deploy canary with Gemini
kubectl apply -f k8s/canary-deployment.yaml

# 2. Wait 5 minutes for stability
sleep 300

# 3. Execute Scenario 2 rollback
# (Follow Scenario 2 procedure above)

# 4. Validate all checks pass

# 5. Document time taken and any issues

# 6. Clean up
kubectl delete deployment mindmend-backend-canary
```

**Success Criteria:**
- Rollback completed in < 5 minutes
- All validation checks pass
- No user impact
- Team confident in procedure

---

## Partial Rollback Scenarios

### Rollback Single Endpoint

If only one endpoint has issues:

```python
# Add endpoint-specific provider override
from models.ai_provider import get_ai_client

@app.route('/api/problematic-endpoint', methods=['POST'])
def problematic_endpoint():
    # Force OpenAI for this endpoint only
    ai_client = get_ai_client(provider="openai")
    # ... rest of handler
```

### Rollback for Specific User Segment

```python
# A/B test rollback - exclude certain users
from models.ai_provider import get_ai_client

def get_ai_provider_for_user(user_id):
    # Rollback for enterprise users only
    if user.subscription_tier == "enterprise":
        return "openai"
    else:
        return "gemini"

ai_client = get_ai_client(provider=get_ai_provider_for_user(current_user.id))
```

---

## Emergency Contacts

### On-Call Rotation

| Day | Primary | Backup |
|-----|---------|--------|
| Weekday | DevOps Engineer | SRE Team |
| Weekend | SRE On-Call | Platform Lead |
| Holiday | Designated On-Call | CTO |

### Escalation Path

```
Level 1: DevOps Engineer (15 minutes)
    ↓
Level 2: DevOps Lead (30 minutes)
    ↓
Level 3: VP Engineering (60 minutes)
    ↓
Level 4: CTO (Critical issues)
```

---

## Rollback Success Criteria

Rollback is considered successful when:

✅ All pods Running and Ready
✅ Health check returns 200
✅ AI responses working (OpenAI)
✅ Error rate < 1%
✅ Latency back to baseline
✅ No active user complaints
✅ All validation checks pass
✅ Monitoring shows normal metrics
✅ Team notified and aware
✅ Incident report created

---

## Appendix: Common Issues

### Issue: Pods stuck in Terminating

```bash
# Force delete stuck pods
kubectl delete pod <pod-name> --grace-period=0 --force
```

### Issue: Image pull errors

```bash
# Verify image exists
gcloud container images list-tags gcr.io/mindmend-production/mindmend-app

# Ensure cluster has pull permissions
gcloud projects add-iam-policy-binding mindmend-production \
  --member="serviceAccount:mindmend-cluster@mindmend-production.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Issue: Database connection pool exhausted

```bash
# Restart database connections
kubectl rollout restart deployment/postgres-deployment
```

### Issue: ConfigMap not updated

```bash
# Force configmap reload
kubectl rollout restart deployment/mindmend-backend
```

---

**Status:** Ready for Use
**Last Updated:** 2025-10-10
**Last Tested:** [TODO: Schedule rollback drill]
**Version:** 1.0

---

## Remember

> "The best rollback is the one you never need to execute."
> - Practice regularly
> - Monitor proactively
> - Rollback decisively when needed

**DO NOT HESITATE to rollback if metrics exceed thresholds. User trust is more important than migration completion.**
