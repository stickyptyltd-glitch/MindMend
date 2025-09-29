# MindMend

CI/CD
- Status: ![CI/CD](https://github.com/stickyptyltd-glitch/MindMend/actions/workflows/cicd.yml/badge.svg)
- Workflows: `.github/workflows/cicd.yml` builds to Artifact Registry and deploys to GKE; a second job deploys to the VM via SSH.

Deploy
- Push to main triggers deploys to GKE and the VM (when secrets are set).
- GKE manifests live under `k8s/`; Helm chart under `charts/mindmend`.

Secrets
- Stored in Google Secret Manager; synced to Kubernetes via CSI (`k8s/secretmanager-csi.yaml`).
- Required keys: `database-url`, `redis-url`, `openai-api-key`, `stripe-secret-key`, `stripe-publishable-key`, `session-secret`, `email-host`, `email-port`, `email-user`, `email-password`, `email-from`.

Security
- Ingress uses HTTPS with HSTS (`k8s/frontendconfig.yaml`).
- Cloud Armor policy recommended (`scripts/cloud-armor-setup.sh`).
- NetworkPolicies restrict pod traffic (`k8s/networkpolicy.yaml`).

Accounts
- Admin: `/admin` (DB-backed; email verification + reset).
- Counselor: `/counselor/login` (DB-backed; email verification + reset).
- Newsletter: `/subscribe-newsletter`, CSV export at `/admin/newsletter/export`.

Handoff
- See `.claude/agents/codex-handoff.md` for current state and decisions.

