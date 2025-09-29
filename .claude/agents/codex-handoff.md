# Agent Handoff: Codex -> Other Agents

Summary
- GKE manifests added under `MindMend/k8s` (namespace, app, services, ingress, cert-manager, storage, redis/postgres, networkpolicy, GSM CSI template).
- GitHub Actions OIDC CI/CD at `.github/workflows/cicd.yml` builds to Artifact Registry (australia-southeast1) and deploys to GKE.
- Security hardening: DB-backed admin/counselor, admin audit log, rate limiting, IP allowlist, email-based password reset.
- Vultr scripts removed; GCP only.

Decisions
- Region migration target: `australia-southeast1`. Current cluster: `asia-southeast1-a`.
- Ingress with cert-manager (Let’s Encrypt) for `mindmend.xyz`.
- Storage: PD (RWO) for Postgres/Redis; Filestore (RWX) for uploads.
- Ollama CPU-only for now; GPU pool disabled until quota.

Pending/Next
- Apply k8s NetworkPolicies and cert-manager resources (requires kubectl).
- Configure email secrets via K8s Secret or Google Secret Manager CSI.
- Optionally switch deployment to use GSM CSI objects exclusively.
- Add admin management UI for full CRUD if desired.

Secrets/Env
- K8s Secret `mindmend-secrets` keys used by app: DATABASE_URL, REDIS_URL, OPENAI_API_KEY, STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, SESSION_SECRET, EMAIL_*.
- CSI template at `k8s/secretmanager-csi.yaml` for GSM → `mindmend-secrets-gsm`.

Contact Points
- Admin: `/admin` (DB auth)
- Counselor: `/counselor/login` (DB auth)
- User: `/login`

