# Deployments Inventory
**Generated:** 2025-10-10 (AEDT)
**Project:** mindmend-production
**Current Region:** asia-southeast1-a (to migrate to australia-southeast1)

---

## GKE Clusters

### mindmend-cluster

```bash
# Get cluster details
gcloud container clusters describe mindmend-cluster \
  --zone=asia-southeast1-a \
  --project=mindmend-production
```

**Configuration:**
- **Location:** asia-southeast1-a
- **Master Version:** 1.33.4-gke.1245000
- **Node Version:** 1.33.4-gke.1245000
- **Machine Type:** e2-medium
- **Nodes:** 3
- **Status:** RUNNING
- **Stack Type:** IPV4

---

## Kubernetes Deployments

### mindmend-backend
- **Replicas:** 2/2
- **Image:** `gcr.io/mindmend-production/mindmend-app:security-fix-v4`
- **Container:** mindmend-app
- **Port:** 8000/TCP
- **Resources:**
  - CPU: [Check with kubectl describe]
  - Memory: [Check with kubectl describe]
- **Health Check:** HTTP /health on port 8000
- **Env Vars:** DATABASE_URL, REDIS_URL, OPENAI_API_KEY, SESSION_SECRET, STRIPE_*

```bash
# Get full details
kubectl describe deployment mindmend-backend
kubectl get deployment mindmend-backend -o yaml
```

### postgres
- **Replicas:** 1/1
- **Image:** postgres:latest
- **Port:** 5432/TCP
- **PVC:** postgres-data-persistentvolumeclaim
- **Env Vars:** POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

### redis
- **Replicas:** 1/1
- **Image:** redis:latest
- **Port:** 6379/TCP
- **PVC:** redis-data-persistentvolumeclaim

### nginx-deployment
- **Replicas:** 2/2
- **Image:** nginx:latest
- **Ports:** 80/TCP, 443/TCP
- **Config:** nginx-cm0-configmap

### celery-worker
- **Replicas:** 1/1
- **Image:** `gcr.io/mindmend-production/mindmend-app:security-fix-v4`
- **Command:** celery worker

### celery-beat
- **Replicas:** 1/1
- **Image:** `gcr.io/mindmend-production/mindmend-app:security-fix-v4`
- **Command:** celery beat

### ollama
- **Replicas:** 1/1
- **Image:** ollama/ollama:latest
- **Port:** 11434/TCP

---

## Services

```bash
# List all services
kubectl get services --all-namespaces
```

| Service | Type | Cluster IP | External IP | Ports |
|---------|------|------------|-------------|-------|
| mindmend-backend-service | LoadBalancer | [TODO] | 34.143.177.214 | 8000:xxxxx/TCP |
| postgres-service | ClusterIP | [TODO] | None | 5432/TCP |
| redis-service | ClusterIP | [TODO] | None | 6379/TCP |
| nginx-service | LoadBalancer | [TODO] | [TODO] | 80:xxxxx/TCP, 443:xxxxx/TCP |
| ollama-service | ClusterIP | [TODO] | None | 11434/TCP |

---

## Ingress

```bash
# Get ingress configuration
kubectl get ingress --all-namespaces
kubectl describe ingress mindmend-ingress
```

**Configuration:** [TODO: Check if ingress controller is configured]

---

## ConfigMaps

```bash
# List config maps
kubectl get configmaps
```

Known ConfigMaps:
- app-cm2-configmap
- app-cm4-configmap
- env-production-configmap
- postgres-cm1-configmap
- postgres-cm2-configmap
- nginx-cm0-configmap

---

## Secrets

```bash
# List secrets (DO NOT display values)
kubectl get secrets
gcloud secrets list --project=mindmend-production
```

Known Secrets:
- DATABASE_URL
- REDIS_URL
- OPENAI_API_KEY
- SESSION_SECRET
- STRIPE_SECRET_KEY
- STRIPE_PUBLISHABLE_KEY
- JWT_SECRET

---

## Persistent Volumes

```bash
# List PVCs
kubectl get pvc
```

Known PVCs:
- postgres-data-persistentvolumeclaim (database data)
- redis-data-persistentvolumeclaim (cache data)
- app-logs-persistentvolumeclaim (application logs)
- app-uploads-persistentvolumeclaim (user uploads)

---

## Cloud Run Services

```bash
# Check for Cloud Run services
gcloud run services list \
  --region=australia-southeast1 \
  --project=mindmend-production
```

**Status:** None currently deployed (using GKE)

---

## Cloud Functions

```bash
# Check for Cloud Functions
gcloud functions list \
  --project=mindmend-production
```

**Status:** [TODO: Check if any functions exist]

---

## Cloud Workflows

```bash
# List workflows
gcloud workflows list \
  --location=australia-southeast1 \
  --project=mindmend-production
```

**Status:** [TODO: Check if any workflows exist]

---

## Cloud Scheduler

```bash
# List scheduled jobs
gcloud scheduler jobs list \
  --project=mindmend-production
```

**Status:** [TODO: Check for cron jobs]

---

## Pub/Sub

```bash
# List topics
gcloud pubsub topics list --project=mindmend-production

# List subscriptions
gcloud pubsub subscriptions list --project=mindmend-production
```

**Status:** [TODO: Check for pub/sub usage]

---

## Collecting Full Inventory

Run the automated collection script:

```bash
./docs/migration/gemini/scripts/collect_state.sh
```

This will generate:
- deployments.json - Full deployment configs
- services.json - All service details
- configmaps.json - ConfigMap inventory
- pvc.json - Persistent volume claims
- Full infrastructure snapshot

---

## Migration Target Architecture

### Proposed Changes for australia-southeast1

1. **Create new GKE cluster** in australia-southeast1
2. **Replicate all deployments** with same configuration
3. **Migrate data** from asia-southeast1-a
4. **Update DNS** to point to new load balancer
5. **Decommission** old cluster after validation

### Minimal Required Services

For Gemini migration, we need:
- **mindmend-backend** (modified to use Vertex AI)
- **postgres** (unchanged)
- **redis** (unchanged)
- **nginx** (unchanged)

Optional services:
- ollama (may be deprecated if Gemini is primary)
- celery (depends on usage)

---

## Environment Variables Audit

### AI-Related Environment Variables

```bash
# Current AI configuration
echo "OPENAI_API_KEY: [REDACTED]"
echo "ANTHROPIC_API_KEY: [CHECK IF EXISTS]"

# Required for Gemini
# GOOGLE_CLOUD_PROJECT: mindmend-production
# GOOGLE_APPLICATION_CREDENTIALS: [service account key path]
# VERTEX_AI_LOCATION: australia-southeast1
```

### Migration Strategy
1. Add Gemini env vars alongside OpenAI
2. Implement feature flag for model selection
3. Gradually shift traffic to Gemini
4. Remove OpenAI vars after validation

---

## Resource Quotas & Limits

```bash
# Check current resource quotas
gcloud compute project-info describe \
  --project=mindmend-production

# Check GKE quotas
kubectl describe resourcequota --all-namespaces
```

### Current Usage (e2-medium × 3 nodes)
- vCPUs: ~6
- Memory: ~12GB
- Disk: [TODO]

### Vertex AI Quotas to Check
```bash
# Check Vertex AI quotas
gcloud services list --enabled \
  --filter="NAME:aiplatform.googleapis.com" \
  --project=mindmend-production

# Request quota increase if needed
gcloud alpha services quota update \
  --service=aiplatform.googleapis.com \
  --consumer=projects/mindmend-production \
  --metric=aiplatform.googleapis.com/online_prediction_requests_per_base_model \
  --value=NEW_LIMIT
```

---

## Networking

### IP Addresses

```bash
# List static IPs
gcloud compute addresses list --project=mindmend-production

# Current external IP
34.143.177.214 (LoadBalancer)
```

### DNS Configuration

```bash
# Current DNS
mindmend.xyz → 34.143.177.214
```

### Firewall Rules

```bash
# List firewall rules
gcloud compute firewall-rules list --project=mindmend-production
```

---

## Monitoring & Logging

### Cloud Monitoring

```bash
# Check monitoring configuration
gcloud monitoring dashboards list --project=mindmend-production
```

**Status:** [TODO: Check if dashboards configured]

### Cloud Logging

```bash
# Check logging configuration
gcloud logging sinks list --project=mindmend-production
```

**Export:** logs-router-logs bucket

---

## Next Steps

1. Run `collect_state.sh` to gather complete inventory
2. Review all services and identify AI dependencies
3. Plan data migration from asia-southeast1-a to australia-southeast1
4. Create staging cluster in australia-southeast1
5. Test Gemini integration in staging before production
