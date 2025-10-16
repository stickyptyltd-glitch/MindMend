# MindMend → Gemini Migration Kit

**Project:** ST1CKY / MindMend
**GCP Project:** mindmend-production (840448055519)
**Target:** Migrate AI agents from Anthropic/Claude to Google Gemini (Vertex AI)
**Region:** australia-southeast1
**Date:** 2025-10-10 (AEDT)

---

## Overview

This folder contains a complete, runnable migration kit to move MindMend's AI agents from current providers (OpenAI, Anthropic/Claude) to Google Gemini on Google Cloud Platform via Vertex AI.

**Goals:**
1. **Parity First:** Like-for-like replacement with no functionality loss
2. **Regional Compliance:** Deploy in australia-southeast1 (Melbourne)
3. **Zero Downtime:** Canary rollout with instant rollback capability
4. **Cost Optimization:** Monitor and optimize per-request costs
5. **Enhanced Safety:** Leverage Gemini's safety filters for mental health content

---

## Folder Structure

```
docs/migration/gemini/
├── README.md                   # This file
├── STATUS.md                   # Current platform status
├── BUILD_HISTORY.md            # Build and deployment history
├── DEPLOYMENTS.md              # Infrastructure inventory
├── AGENT_INVENTORY.yaml        # All AI agents documented
├── GEMINI_MIGRATION_PLAN.md    # Step-by-step migration plan
├── SDK_DIFFS.md                # Code examples (before/after)
├── CI_CD_UPDATES.md            # GitHub Actions setup
├── SECRETS_AND_IAM.md          # Security configuration
├── TESTING_AND_EVALS.md        # Test strategy
├── ROLLBACK_PLAN.md            # Emergency rollback procedure
├── RUNBOOK.md                  # On-call operations guide
├── CHANGELOG.md                # Migration changelog
├── CHECKLIST.md                # End-to-end checklist
├── RISKS.md                    # Risk register
├── scripts/
│   ├── collect_state.sh        # Gather infrastructure state
│   ├── build_history.sh        # Generate build history
│   ├── ci_sample_workflow.yml  # GitHub Actions template
│   ├── model_swap_checks.py    # Validation scripts
│   └── cost_latency_probe.py   # Performance measurement
└── artifacts/                  # Generated data (gitignored)
    ├── *.json                  # Infrastructure state
    ├── *.txt                   # Summary reports
    └── benchmarks/             # Performance baselines
```

---

## Quick Start

### Prerequisites

```bash
# 1. Authenticate to GCP
gcloud auth login
gcloud config set project mindmend-production

# 2. Install dependencies
pip install google-cloud-aiplatform google-auth jq

# 3. Get kubectl access
gcloud container clusters get-credentials mindmend-cluster \
  --zone=asia-southeast1-a \
  --project=mindmend-production
```

### Step 1: Collect Current State

```bash
cd /home/mindmendxyz/MindMend
./docs/migration/gemini/scripts/collect_state.sh
```

This generates:
- Infrastructure inventory (JSON)
- Current deployment state
- Service configuration
- Baseline metrics

**Output:** `docs/migration/gemini/artifacts/`

### Step 2: Review Documentation

Read these files in order:

1. **STATUS.md** - Understand current platform health
2. **AGENT_INVENTORY.yaml** - Review all AI agents to migrate
3. **GEMINI_MIGRATION_PLAN.md** - Understand the migration phases
4. **SDK_DIFFS.md** - See code changes required

### Step 3: Audit AI Usage

```bash
# Find all OpenAI usage
grep -r "import openai" --include="*.py" .

# Find all AI model configurations
grep -r "temperature\|max_tokens" --include="*.py" . | grep -v "node_modules"

# Check environment variables
env | grep -E "OPENAI|ANTHROPIC|CLAUDE|AI"
```

### Step 4: Enable Vertex AI

```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com \
  --project=mindmend-production

# Check quotas
gcloud alpha services quotas list \
  --service=aiplatform.googleapis.com \
  --project=mindmend-production \
  --filter="metric.displayName:prediction"
```

### Step 5: Create Staging Environment

See `GEMINI_MIGRATION_PLAN.md` for detailed instructions.

```bash
# Create staging cluster (example)
gcloud container clusters create mindmend-staging \
  --zone=australia-southeast1-a \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --project=mindmend-production
```

### Step 6: Run Test Migration

Follow the canary plan in `TESTING_AND_EVALS.md`:

1. Deploy modified code to staging
2. Run golden prompt tests
3. Compare latency and cost
4. Validate safety filters

---

## Critical Files Summary

| File | Purpose | Action Required |
|------|---------|-----------------|
| **AGENT_INVENTORY.yaml** | Document all AI agents | ✏️ Fill [TODO] placeholders |
| **GEMINI_MIGRATION_PLAN.md** | Step-by-step migration guide | 📖 Read and follow |
| **SDK_DIFFS.md** | Code transformation examples | 💻 Implement in codebase |
| **RUNBOOK.md** | On-call operations | 🚨 Bookmark for incidents |
| **ROLLBACK_PLAN.md** | Emergency rollback | 🔄 Practice once before go-live |
| **CHECKLIST.md** | End-to-end checklist | ✅ Track progress |

---

## Key Commands

### Infrastructure

```bash
# Get current project info
gcloud config list

# Describe project
gcloud projects describe mindmend-production

# List all GKE clusters
gcloud container clusters list --project=mindmend-production

# Get cluster details
gcloud container clusters describe mindmend-cluster \
  --zone=asia-southeast1-a \
  --project=mindmend-production

# List all deployments
kubectl get deployments --all-namespaces

# Get current pods
kubectl get pods --all-namespaces
```

### Container Images

```bash
# List all images
gcloud container images list \
  --repository=gcr.io/mindmend-production \
  --project=mindmend-production

# List tags for mindmend-app
gcloud container images list-tags \
  gcr.io/mindmend-production/mindmend-app \
  --limit=20
```

### Logs and Monitoring

```bash
# Recent errors
gcloud logging read "severity>=ERROR" \
  --limit=50 \
  --project=mindmend-production

# Application logs
kubectl logs deployment/mindmend-backend -f

# Check Vertex AI usage
gcloud ai operations list \
  --region=australia-southeast1 \
  --project=mindmend-production
```

### Secrets

```bash
# List secrets (DO NOT display values)
gcloud secrets list --project=mindmend-production

# Create new secret for Vertex AI
gcloud secrets create VERTEX_AI_PROJECT \
  --replication-policy=automatic \
  --project=mindmend-production

# Grant access to service account
gcloud secrets add-iam-policy-binding VERTEX_AI_PROJECT \
  --member="serviceAccount:mindmend-backend@mindmend-production.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=mindmend-production
```

---

## Migration Phases

### Phase 1: Discovery (Week 1)
- ✅ Collect infrastructure state
- ✅ Audit AI agent usage
- ✅ Document current performance
- ⏳ Identify Anthropic/Claude usage (if any)

### Phase 2: Staging Setup (Week 1-2)
- ⏳ Create australia-southeast1 staging cluster
- ⏳ Deploy current app to staging
- ⏳ Configure Vertex AI access
- ⏳ Test Gemini API connectivity

### Phase 3: SDK Integration (Week 2-3)
- ⏳ Install google-cloud-aiplatform
- ⏳ Create AI model abstraction layer
- ⏳ Implement feature flags
- ⏳ Unit test all endpoints

### Phase 4: Canary Testing (Week 3-4)
- ⏳ Deploy to staging with Gemini
- ⏳ Run golden prompt evaluation
- ⏳ Performance benchmark
- ⏳ Cost analysis

### Phase 5: Production Rollout (Week 4-5)
- ⏳ 10% traffic to Gemini
- ⏳ Monitor for 48 hours
- ⏳ 50% traffic to Gemini
- ⏳ Monitor for 48 hours
- ⏳ 100% cutover

### Phase 6: Cleanup (Week 5-6)
- ⏳ Remove old API keys
- ⏳ Update documentation
- ⏳ Post-migration report

---

## Success Criteria

- ✅ Zero downtime during migration
- ✅ Latency within 20% of baseline
- ✅ Error rate < 1%
- ✅ Cost per request within budget
- ✅ All safety tests passing
- ✅ User satisfaction maintained

---

## Rollback Procedure (Emergency)

If critical issues occur:

```bash
# 1. Immediate traffic shift (< 30 seconds)
kubectl set image deployment/mindmend-backend \
  mindmend-app=gcr.io/mindmend-production/mindmend-app:pre-gemini-tag

# 2. Verify rollback
kubectl rollout status deployment/mindmend-backend

# 3. Check health
curl http://34.143.177.214/health

# 4. Monitor logs
kubectl logs deployment/mindmend-backend -f | grep -i error
```

See **ROLLBACK_PLAN.md** for complete procedure.

---

## Support & Escalation

| Issue | Contact | Action |
|-------|---------|--------|
| Migration questions | DevOps team | Review docs first |
| API quota exceeded | GCP support | File quota increase ticket |
| Model quality issues | AI/ML team | Review evaluation results |
| Production incident | On-call engineer | Follow RUNBOOK.md |
| Security concern | Security team | Halt rollout immediately |

---

## Next Steps

1. **Right Now:**
   ```bash
   ./docs/migration/gemini/scripts/collect_state.sh
   ```

2. **Today:**
   - Review STATUS.md and AGENT_INVENTORY.yaml
   - Fill in [TODO] placeholders
   - Audit codebase for AI usage

3. **This Week:**
   - Read GEMINI_MIGRATION_PLAN.md completely
   - Set up staging environment
   - Enable Vertex AI API

4. **Next Week:**
   - Implement SDK changes (see SDK_DIFFS.md)
   - Create feature flags
   - Begin canary testing

5. **Week 3+:**
   - Production canary rollout
   - Monitor and optimize
   - Complete migration

---

## Resources

### Documentation
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Quickstart](https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-multimodal)
- [Python SDK Reference](https://cloud.google.com/python/docs/reference/aiplatform/latest)

### Pricing
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Gemini Models Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)

### Support
- [GCP Support Console](https://console.cloud.google.com/support)
- [Vertex AI Quotas](https://console.cloud.google.com/iam-admin/quotas)

---

## Checklist

- [ ] Run `collect_state.sh` and review artifacts
- [ ] Complete AGENT_INVENTORY.yaml with actual values
- [ ] Audit codebase for OpenAI/Anthropic usage
- [ ] Enable Vertex AI API in mindmend-production
- [ ] Check and request quota increases if needed
- [ ] Create staging cluster in australia-southeast1
- [ ] Set up GitHub Actions CI/CD (see CI_CD_UPDATES.md)
- [ ] Configure IAM and secrets (see SECRETS_AND_IAM.md)
- [ ] Implement SDK changes in feature branch
- [ ] Run testing suite (see TESTING_AND_EVALS.md)
- [ ] Execute canary rollout plan
- [ ] Monitor for 48 hours at each rollout stage
- [ ] Complete cutover to 100% Gemini
- [ ] Verify and clean up old API keys
- [ ] Document lessons learned
- [ ] Update runbooks with Gemini specifics

---

**Status:** 📋 Planning Phase
**Owner:** [TODO: Assign owner]
**Target Completion:** [TODO: Set date]
**Last Updated:** 2025-10-10

---

For questions or issues with this migration kit, see the **RUNBOOK.md** or contact the platform team.
