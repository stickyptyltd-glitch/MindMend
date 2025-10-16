# Gemini Migration Checklist
**Project:** MindMend
**Date Started:** [TODO]
**Target Completion:** [TODO]
**Owner:** [TODO]

---

## How to Use This Checklist

1. Check off items as you complete them: `- [ ]` → `- [x]`
2. Add dates and notes for each completed item
3. Update this file in git after each session
4. Review progress weekly with the team

---

## Phase 1: Discovery & Planning ⏱️ Est: 1 week

### Infrastructure Audit

- [ ] **Run collect_state.sh script**
  - Date: ___________
  - Artifacts location: `docs/migration/gemini/artifacts/`
  - Note: ___________________________________

- [ ] **Review infrastructure inventory**
  - Date: ___________
  - GKE clusters identified: ___________
  - Services count: ___________
  - Note: ___________________________________

- [ ] **Document current deployment architecture**
  - Date: ___________
  - Reviewed: DEPLOYMENTS.md
  - Note: ___________________________________

### AI Agent Inventory

- [ ] **Audit codebase for OpenAI usage**
  ```bash
  grep -r "import openai\|from openai" --include="*.py" .
  ```
  - Date: ___________
  - Files found: ___________
  - Note: ___________________________________

- [ ] **Audit codebase for Anthropic/Claude usage**
  ```bash
  grep -r "import anthropic\|from anthropic" --include="*.py" .
  ```
  - Date: ___________
  - Files found: ___________
  - Note: ___________________________________

- [ ] **Complete AGENT_INVENTORY.yaml**
  - Date: ___________
  - Total agents documented: ___________
  - Priority: Critical=___ High=___ Medium=___ Low=___
  - Note: ___________________________________

- [ ] **Document all AI model parameters**
  - Date: ___________
  - temperature ranges: ___________
  - max_tokens ranges: ___________
  - Note: ___________________________________

### Performance Baselines

- [ ] **Measure current API latency**
  ```bash
  # P50, P95, P99
  ```
  - Date: ___________
  - P50: _____ ms
  - P95: _____ ms
  - P99: _____ ms

- [ ] **Measure current error rate**
  - Date: ___________
  - Error rate: _____ %
  - Note: ___________________________________

- [ ] **Document current costs**
  - Date: ___________
  - OpenAI monthly: $__________
  - Anthropic monthly: $__________
  - Total: $__________

### Planning & Approvals

- [ ] **Review GEMINI_MIGRATION_PLAN.md**
  - Date: ___________
  - Reviewed by: ___________________________________
  - Approved by: ___________________________________

- [ ] **Schedule migration timeline**
  - Date: ___________
  - Start date: ___________
  - Canary date: ___________
  - Cutover date: ___________

- [ ] **Identify stakeholders and assign RACI**
  - Date: ___________
  - Responsible: ___________________________________
  - Accountable: ___________________________________
  - Consulted: ___________________________________
  - Informed: ___________________________________

- [ ] **Create risk mitigation plan**
  - Date: ___________
  - Reviewed: RISKS.md
  - Critical risks count: ___________

---

## Phase 2: Environment Setup ⏱️ Est: 1 week

### GCP Configuration

- [ ] **Enable Vertex AI API**
  ```bash
  gcloud services enable aiplatform.googleapis.com --project=mindmend-production
  ```
  - Date: ___________
  - Status: ___________________________________

- [ ] **Check Vertex AI quotas**
  - Date: ___________
  - Online prediction: _____ requests/min
  - Quota sufficient: Yes / No
  - Increase requested: Yes / No / N/A

- [ ] **Request quota increases (if needed)**
  - Date requested: ___________
  - Date approved: ___________
  - New limits: ___________________________________

### IAM & Security

- [ ] **Create Vertex AI service account**
  ```bash
  gcloud iam service-accounts create vertex-ai-client
  ```
  - Date: ___________
  - SA email: ___________________________________

- [ ] **Configure Workload Identity**
  - Date: ___________
  - K8s SA: ___________________________________
  - GCP SA binding: ✓

- [ ] **Grant required IAM roles**
  - Date: ___________
  - roles/aiplatform.user: ✓
  - roles/secretmanager.secretAccessor: ✓
  - Other: ___________________________________

- [ ] **Create secrets in Secret Manager**
  - Date: ___________
  - VERTEX_AI_PROJECT: ✓
  - VERTEX_AI_LOCATION: ✓
  - Other: ___________________________________

- [ ] **Test secret access from pods**
  - Date: ___________
  - Test result: PASS / FAIL
  - Note: ___________________________________

### Staging Environment

- [ ] **Create staging GKE cluster**
  - Date: ___________
  - Cluster name: ___________________________________
  - Zone: australia-southeast1-a
  - Nodes: ___________

- [ ] **Deploy current app to staging**
  - Date: ___________
  - Image tag: ___________________________________
  - Pods running: _____ / _____

- [ ] **Verify staging health checks**
  - Date: ___________
  - Health endpoint: ___________________________________
  - Status: PASS / FAIL

- [ ] **Configure staging DNS/ingress**
  - Date: ___________
  - URL: ___________________________________
  - SSL: ✓ / ✗

### CI/CD Setup

- [ ] **Configure GitHub OIDC to GCP**
  - Date: ___________
  - Workload Identity Pool: github-pool
  - Provider: github
  - Status: ✓

- [ ] **Create GitHub Actions workflows**
  - Date: ___________
  - deploy-staging.yml: ✓
  - deploy-production.yml: ✓
  - test.yml: ✓

- [ ] **Test CI/CD pipeline in staging**
  - Date: ___________
  - Test build: ___________________________________
  - Result: PASS / FAIL

---

## Phase 3: Code Changes ⏱️ Est: 1-2 weeks

### SDK Installation

- [ ] **Add google-cloud-aiplatform to requirements.txt**
  ```
  google-cloud-aiplatform==1.38.0
  ```
  - Date: ___________
  - Version: ___________________________________

- [ ] **Add google-auth to requirements.txt**
  - Date: ___________
  - Version: ___________________________________

- [ ] **Test pip install locally**
  - Date: ___________
  - Result: PASS / FAIL

### Abstraction Layer

- [ ] **Create AI model abstraction module**
  - Date: ___________
  - File: ___________________________________
  - Supports: OpenAI / Gemini / Both

- [ ] **Implement Gemini client wrapper**
  - Date: ___________
  - Streaming support: ✓ / ✗
  - Error handling: ✓ / ✗

- [ ] **Add feature flag for model selection**
  - Date: ___________
  - Env var: AI_PROVIDER
  - Values: openai / gemini / auto

### Endpoint Updates

- [ ] **Update /api/therapy-session**
  - Date: ___________
  - Gemini integration: ✓
  - Tests passing: ✓ / ✗

- [ ] **Update /api/analyze-text**
  - Date: ___________
  - Gemini integration: ✓
  - Tests passing: ✓ / ✗

- [ ] **Update /api/couples_session**
  - Date: ___________
  - Gemini integration: ✓
  - Tests passing: ✓ / ✗

- [ ] **Update /api/personalized_activities**
  - Date: ___________
  - Gemini integration: ✓
  - Tests passing: ✓ / ✗

- [ ] **Update /api/dashboard/ai-insights**
  - Date: ___________
  - Gemini integration: ✓
  - Tests passing: ✓ / ✗

- [ ] **Update /api/ai-models/diagnose**
  - Date: ___________
  - Gemini integration: ✓
  - Tests passing: ✓ / ✗

- [ ] **Update other AI endpoints (list below)**
  - Endpoint: _______________ Date: _____ Status: ✓ / ✗
  - Endpoint: _______________ Date: _____ Status: ✓ / ✗
  - Endpoint: _______________ Date: _____ Status: ✓ / ✗

### Configuration

- [ ] **Update environment variables**
  - Date: ___________
  - VERTEX_AI_PROJECT: ✓
  - VERTEX_AI_LOCATION: ✓
  - GEMINI_MODEL: ___________________________________

- [ ] **Configure model parameters**
  - Date: ___________
  - temperature: ✓
  - max_output_tokens: ✓
  - safety_settings: ✓

- [ ] **Update Docker build**
  - Date: ___________
  - Dockerfile updated: ✓
  - Build successful: ✓

---

## Phase 4: Testing ⏱️ Est: 1 week

### Unit Tests

- [ ] **Write unit tests for Gemini wrapper**
  - Date: ___________
  - Test file: ___________________________________
  - Coverage: _____ %

- [ ] **Write unit tests for each endpoint**
  - Date: ___________
  - Tests passing: _____ / _____

- [ ] **Test error handling**
  - Date: ___________
  - Quota exceeded: ✓
  - Authentication failure: ✓
  - Timeout: ✓
  - Safety filter: ✓

### Integration Tests

- [ ] **Test Gemini API connectivity**
  - Date: ___________
  - Result: PASS / FAIL
  - Latency: _____ ms

- [ ] **Test streaming responses**
  - Date: ___________
  - Result: PASS / FAIL

- [ ] **Test with real therapy prompts**
  - Date: ___________
  - Prompts tested: _____
  - Success rate: _____ %

### Performance Tests

- [ ] **Benchmark latency vs OpenAI**
  - Date: ___________
  - OpenAI P95: _____ ms
  - Gemini P95: _____ ms
  - Delta: _____ %

- [ ] **Cost analysis**
  - Date: ___________
  - OpenAI per 1k tokens: $_____
  - Gemini per 1k tokens: $_____
  - Projected monthly: $_____

- [ ] **Load testing**
  - Date: ___________
  - Tool: ___________________________________
  - Peak RPS: _____
  - Result: PASS / FAIL

### Quality Evaluation

- [ ] **Create golden prompt test suite**
  - Date: ___________
  - Prompts: _____
  - File: ___________________________________

- [ ] **Run evaluation on OpenAI**
  - Date: ___________
  - Quality score: _____ / 10

- [ ] **Run evaluation on Gemini**
  - Date: ___________
  - Quality score: _____ / 10
  - Acceptable: Yes / No

- [ ] **Test safety filters**
  - Date: ___________
  - False positives: _____
  - False negatives: _____
  - Acceptable: Yes / No

### Staging Deployment

- [ ] **Deploy to staging with Gemini**
  - Date: ___________
  - Image: ___________________________________
  - Pods: _____ / _____

- [ ] **Smoke tests in staging**
  - Date: ___________
  - Health check: ✓
  - Auth flow: ✓
  - AI endpoints: ✓

- [ ] **Manual testing in staging**
  - Date: ___________
  - Tester: ___________________________________
  - Issues found: _____
  - All resolved: Yes / No

---

## Phase 5: Canary Rollout ⏱️ Est: 1 week

### Canary Deployment (10%)

- [ ] **Build production canary image**
  - Date: ___________
  - Tag: gemini-canary-v1
  - Pushed to GCR: ✓

- [ ] **Deploy canary to production**
  - Date: ___________
  - Replicas: _____
  - Traffic: 10%

- [ ] **Configure monitoring alerts**
  - Date: ___________
  - Error rate alert: ✓
  - Latency alert: ✓
  - Quota alert: ✓

### 10% Monitoring (48 hours)

- [ ] **Hour 1: Initial monitoring**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Status: PASS / FAIL

- [ ] **Hour 6: Check metrics**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Status: PASS / FAIL

- [ ] **Hour 24: Daily review**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Status: PASS / FAIL

- [ ] **Hour 48: Gate decision**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Decision: PROCEED / ROLLBACK
  - Approved by: ___________________________________

### Canary Expansion (50%)

- [ ] **Scale canary to 50% traffic**
  - Date: ___________
  - Replicas adjusted: _____
  - Traffic split: 50/50

### 50% Monitoring (48 hours)

- [ ] **Hour 1: Initial monitoring**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Status: PASS / FAIL

- [ ] **Hour 24: Daily review**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Status: PASS / FAIL

- [ ] **Hour 48: Gate decision**
  - Time: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Decision: PROCEED / ROLLBACK
  - Approved by: ___________________________________

---

## Phase 6: Full Cutover ⏱️ Est: 1 day

### Production Cutover

- [ ] **Update main deployment to Gemini**
  - Date: ___________
  - Time: ___________
  - Image: gemini-canary-v1

- [ ] **Delete canary deployment**
  - Date: ___________
  - Cleanup complete: ✓

- [ ] **Verify all pods on Gemini**
  - Date: ___________
  - Pods: _____ / _____
  - All running Gemini: ✓

### Post-Cutover Monitoring

- [ ] **Day 1: Intensive monitoring**
  - Date: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Incidents: _____

- [ ] **Day 2: Continued monitoring**
  - Date: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Incidents: _____

- [ ] **Day 3: Stability check**
  - Date: ___________
  - Errors: _____
  - Latency P95: _____ ms
  - Incidents: _____

- [ ] **Week 1: Weekly review**
  - Date: ___________
  - Avg errors: _____
  - Avg latency: _____ ms
  - User satisfaction: _____ / 10
  - Status: STABLE / ISSUES

---

## Phase 7: Cleanup ⏱️ Est: 1 week

### Old API Key Management

- [ ] **Backup OpenAI API key**
  - Date: ___________
  - Location: ___________________________________

- [ ] **Remove OpenAI key from production**
  - Date: ___________
  - Env var removed: ✓
  - Verified app works without it: ✓

- [ ] **Backup Anthropic API key (if exists)**
  - Date: ___________
  - Location: ___________________________________

- [ ] **Schedule key deletion (30 days)**
  - Date: ___________
  - Deletion date: ___________
  - Calendar reminder set: ✓

### Documentation

- [ ] **Update platform documentation**
  - Date: ___________
  - README.md: ✓
  - Architecture diagrams: ✓

- [ ] **Update runbooks**
  - Date: ___________
  - RUNBOOK.md: ✓
  - On-call procedures: ✓

- [ ] **Update API documentation**
  - Date: ___________
  - Swagger/OpenAPI: ✓

- [ ] **Create migration post-mortem**
  - Date: ___________
  - File: ___________________________________
  - Shared with team: ✓

### Cost Tracking

- [ ] **Configure cost tracking dashboard**
  - Date: ___________
  - Dashboard URL: ___________________________________

- [ ] **Compare actual vs projected costs**
  - Date: ___________
  - Projected: $_____
  - Actual: $_____
  - Variance: _____ %

- [ ] **Optimize costs (if needed)**
  - Date: ___________
  - Actions taken: ___________________________________

---

## Phase 8: Validation ⏱️ Est: 1 week

### Success Metrics

- [ ] **Verify error rate < 1%**
  - Date: ___________
  - Actual: _____ %
  - Result: PASS / FAIL

- [ ] **Verify latency within 20% of baseline**
  - Date: ___________
  - Baseline P95: _____ ms
  - Current P95: _____ ms
  - Delta: _____ %
  - Result: PASS / FAIL

- [ ] **Verify zero quota issues**
  - Date: ___________
  - Quota errors: _____
  - Result: PASS / FAIL

- [ ] **Verify user satisfaction maintained**
  - Date: ___________
  - Survey results: _____ / 10
  - Result: PASS / FAIL

- [ ] **Verify cost within budget**
  - Date: ___________
  - Monthly cost: $_____
  - Budget: $_____
  - Result: PASS / FAIL

### Team Training

- [ ] **Train team on Gemini monitoring**
  - Date: ___________
  - Attendees: _____
  - Materials: ___________________________________

- [ ] **Train team on incident response**
  - Date: ___________
  - Attendees: _____
  - Drill completed: ✓

- [ ] **Update on-call documentation**
  - Date: ___________
  - RUNBOOK.md reviewed: ✓

### Final Approval

- [ ] **Engineering sign-off**
  - Date: ___________
  - Approved by: ___________________________________

- [ ] **Product sign-off**
  - Date: ___________
  - Approved by: ___________________________________

- [ ] **Security sign-off**
  - Date: ___________
  - Approved by: ___________________________________

- [ ] **Executive sign-off**
  - Date: ___________
  - Approved by: ___________________________________

---

## Migration Complete! 🎉

**Completion Date:** ___________
**Total Duration:** _____ weeks
**Final Status:** SUCCESS / PARTIAL / FAILED

**Lessons Learned:**
[Write key lessons learned here]

**Future Improvements:**
[Write future improvements here]

---

**Next Review Date:** ___________
**Migration Kit Location:** `/docs/migration/gemini/`
**Post-Mortem Document:** ___________________________________
