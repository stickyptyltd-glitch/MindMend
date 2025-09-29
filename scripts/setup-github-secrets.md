# Setup GitHub Actions Secrets (gh CLI)

Prereqs: Install GitHub CLI (gh) and authenticate: `gh auth login`.

Set these repo secrets (replace values):

```
REPO="stickyptyltd-glitch/MindMend"
PROJECT_ID="mindmend-production"
PROJECT_NUMBER="$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')"

# OIDC
gh secret set GCP_WORKLOAD_IDP -r "$REPO" -b "projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
gh secret set GCP_SERVICE_ACCOUNT -r "$REPO" -b "ci-deployer@$PROJECT_ID.iam.gserviceaccount.com"

# GKE
gh secret set GKE_CLUSTER_NAME -r "$REPO" -b "mindmend-cluster"
gh secret set GKE_CLUSTER_LOCATION -r "$REPO" -b "asia-southeast1-a"

# VM (replace with your values)
gh secret set VM_HOST -r "$REPO" -b "34.11.18.218"
gh secret set VM_USER -r "$REPO" -b "your_ssh_user"
gh secret set VM_DIR  -r "$REPO" -b "/var/www/mindmend"
gh secret set VM_PORT -r "$REPO" -b "22"

# Private key: reads from file and stores content
gh secret set VM_KEY -r "$REPO" < /path/to/id_ed25519
```

Notes:
- Ensure the public key for `VM_KEY` is in the VM user's `~/.ssh/authorized_keys`.
- OIDC pool/provider and CI service account must exist in GCP.
- After secrets are set, push to `main` to trigger deploy.

