# Build History
**Generated:** 2025-10-10 (AEDT)
**Project:** mindmend-production
**Repository:** stickyptyltd-glitch/MindMend

---

## Recent Builds

| Date | Commit | Actor | Tag/Branch | Artifact | Environment | Result | Duration |
|------|--------|-------|------------|----------|-------------|--------|----------|
| 2025-10-10 | b6f335a | mindmendxyz | main | security-fix-v4 | production | ✅ SUCCESS | ~2.5min |
| 2025-10-10 | b6f335a | mindmendxyz | main | feature-update-v1 | production | ✅ SUCCESS | ~3min |
| 2025-09-26 | [TODO] | [TODO] | main | security-fix-v3 | production | ✅ SUCCESS | [TODO] |
| 2025-09-26 | [TODO] | [TODO] | main | security-fix-v2 | production | ✅ SUCCESS | [TODO] |
| 2025-09-26 | [TODO] | [TODO] | main | security-fix-v1 | production | ✅ SUCCESS | [TODO] |

**Current Production Image:**
```
gcr.io/mindmend-production/mindmend-app:security-fix-v4
Digest: sha256:fd3a3945d0740131aa5a9c4f43b419721070a81f49d8c6839493bdcb2349213a
```

---

## Git Commit History (Last 15)

```bash
# Generated from: git log --oneline -15
b6f335a fix: Update url_for('session') to url_for('therapy_session') in templates
bbd5080 fix: Remove MFA check for AdminUser (field doesn't exist yet)
4c842c1 fix: Use AdminUser.role field for session role assignment
cc2d12c fix: Update admin login to use AdminUser model instead of Patient table
c4b02e8 fix: Remove Subscription/Payment imports from finance.py
b06359a fix: Remove non-existent Subscription/Payment imports from all admin modules
2e3e1f9 fix: Remove non-existent Subscription and Payment imports from admin dashboard
005a48d feat: Add pyotp and qrcode dependencies for admin MFA support
c4e2c32 fix: Restore full admin/auth.py with authentication decorators
4e68fe2 fix: Change admin import from admin_panel to admin package
[5 more commits omitted]
```

---

## Cloud Build History

### How to Query

```bash
# List recent builds
gcloud builds list \
  --limit=20 \
  --project=mindmend-production \
  --format="table(id,createTime,status,images,buildTriggerId)"

# Get specific build details
gcloud builds describe BUILD_ID \
  --project=mindmend-production

# List build triggers
gcloud beta builds triggers list \
  --project=mindmend-production
```

### Expected Output Format

```
ID                                    CREATE_TIME                STATUS   IMAGES
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  2025-10-10T06:30:00+00:00  SUCCESS  gcr.io/mindmend-production/mindmend-app:security-fix-v4
```

**Note:** Run `./scripts/build_history.sh` to generate complete history.

---

## GitHub Actions Runs

### How to Query

```bash
# List recent workflow runs
gh run list --repo stickyptyltd-glitch/MindMend --limit 20

# Get specific run details
gh run view RUN_ID --repo stickyptyltd-glitch/MindMend

# List all workflows
gh workflow list --repo stickyptyltd-glitch/MindMend
```

### Current Workflows

```bash
# Check if workflows exist
ls -la .github/workflows/

# Expected workflows (to be created):
# - deploy-production.yml
# - deploy-staging.yml
# - test.yml
# - security-scan.yml
```

**Status:** GitHub Actions workflows not yet configured. Manual Docker builds are being used.

---

## Container Image History

### Artifact Registry / GCR

```bash
# List all images in GCR
gcloud container images list \
  --repository=gcr.io/mindmend-production \
  --project=mindmend-production

# List tags for mindmend-app
gcloud container images list-tags \
  gcr.io/mindmend-production/mindmend-app \
  --limit=20 \
  --format="table(tags,digest,timestamp)"

# Get image details
gcloud container images describe \
  gcr.io/mindmend-production/mindmend-app:security-fix-v4
```

### Known Image Tags

| Tag | Digest (short) | Size | Created | Purpose |
|-----|---------------|------|---------|---------|
| security-fix-v4 | fd3a3945d074 | [TODO] | 2025-10-10 | API security hardening (14 endpoints) |
| feature-update-v1 | e1c024b2bba6 | [TODO] | 2025-10-10 | User features (profile, settings, etc) |
| security-fix-v3 | [TODO] | [TODO] | 2025-09-26 | Phase 3 fixes (15 vulnerabilities) |
| security-fix-v2 | [TODO] | 2025-09-26 | Phase 2 fixes (14 vulnerabilities) |
| security-fix-v1 | [TODO] | 2025-09-26 | Phase 1 fixes |

---

## Deployment History

### Kubernetes Rollout History

```bash
# Get rollout history for main deployment
kubectl rollout history deployment/mindmend-backend \
  --namespace=default

# Get specific revision details
kubectl rollout history deployment/mindmend-backend \
  --namespace=default \
  --revision=N
```

### Recent Deployments

```bash
# Show recent deployment events
kubectl get events \
  --namespace=default \
  --sort-by='.lastTimestamp' \
  --field-selector involvedObject.kind=Deployment | tail -20
```

Expected output:
```
REVISION  CHANGE-CAUSE
1         Initial deployment
2         security-fix-v1
3         security-fix-v2
4         security-fix-v3
5         feature-update-v1
6         security-fix-v4 (current)
```

---

## Build Artifacts Locations

### Docker Images
- **Registry:** GCR (gcr.io/mindmend-production)
- **Repository:** mindmend-app
- **Retention:** [TODO: Configure lifecycle policy]

### Source Code
- **GitHub:** stickyptyltd-glitch/MindMend
- **Branch:** main (15 commits ahead of origin)
- **Local:** /home/mindmendxyz/MindMend

### Build Logs
- **Cloud Build:** Console → Cloud Build → History
- **kubectl logs:** `kubectl logs deployment/mindmend-backend -f`
- **Cloud Logging:** logs-router-logs bucket

---

## Build Reproducibility

### Prerequisites for Local Build

```bash
# 1. Clone repository
git clone https://github.com/stickyptyltd-glitch/MindMend.git
cd MindMend

# 2. Build Docker image
docker build -t gcr.io/mindmend-production/mindmend-app:local .

# 3. Test locally
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  gcr.io/mindmend-production/mindmend-app:local

# 4. Push to registry (requires auth)
gcloud auth configure-docker gcr.io
docker push gcr.io/mindmend-production/mindmend-app:local
```

### Dockerfile Location
`/home/mindmendxyz/MindMend/Dockerfile`

### Key Build Args
- Base image: `python:3.11-slim`
- Working directory: `/app`
- Build time: ~90 seconds (cached), ~5 minutes (clean)

---

## Versioning Strategy

### Current Strategy
Manual tagging based on purpose:
- `security-fix-vN` - Security patches
- `feature-update-vN` - New features
- `hotfix-vN` - Urgent production fixes

### Proposed Strategy (Post-Migration)
```
<major>.<minor>.<patch>-<environment>

Examples:
- 1.0.0-prod
- 1.1.0-staging
- 1.1.1-hotfix
```

### Semantic Versioning Rules
- **Major:** Breaking changes, major features
- **Minor:** New features, backward compatible
- **Patch:** Bug fixes, security patches

---

## CI/CD Pipeline Status

### Current State
❌ **Not Configured**

Manual process:
1. Make code changes locally
2. Run `docker build` manually
3. Push to GCR manually
4. Run `kubectl set image` manually
5. Monitor rollout manually

### Desired State (Post-Migration)
✅ **Automated CI/CD**

Automated process:
1. Push to GitHub branch
2. GitHub Actions triggers
3. Build + test + scan
4. Push to Artifact Registry
5. Deploy to staging (auto)
6. Deploy to production (manual approval)
7. Automated rollback on failure

See `CI_CD_UPDATES.md` for implementation plan.

---

## Commands to Regenerate This Document

Run the following script:
```bash
./docs/migration/gemini/scripts/build_history.sh > docs/migration/gemini/BUILD_HISTORY.generated.md
```

Script queries:
- Git log history
- GCR image tags
- Cloud Build history
- GitHub Actions runs (via gh CLI)
- Kubernetes rollout history

---

## Audit Trail

### Build Approvals
[TODO: Document approval process for production builds]

### Change Management
[TODO: Document change request process]

### Compliance
[TODO: Document SOC2/HIPAA build requirements]

---

## Next Steps

1. **Implement GitHub Actions CI/CD**
   - Create workflows in `.github/workflows/`
   - Configure OIDC auth to GCP
   - Add staging/production gates

2. **Set up Artifact Registry**
   - Migrate from GCR to Artifact Registry (recommended)
   - Configure vulnerability scanning
   - Set up image lifecycle policies

3. **Automate Build History Collection**
   - Schedule `build_history.sh` to run daily
   - Store results in Cloud Storage
   - Create dashboard for visualization

4. **Version Tag Cleanup**
   - Implement semantic versioning
   - Add git tags to releases
   - Create CHANGELOG.md automation
