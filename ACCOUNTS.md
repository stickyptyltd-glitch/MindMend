# Accounts & Access Guide

This guide explains how to access Admin, Therapist, and User portals, how credentials are stored, and how to manage accounts securely in each environment.

## Portals
- Admin: `https://mindmend.xyz/admin`
- Therapist: `https://mindmend.xyz/counselor/login`
- User: `https://mindmend.xyz/login`

## Credential Sources
- Production (Kubernetes):
  - Admin/Therapist credentials stored in the application database.
  - Bootstrap admin credentials can be provided via env (Kubernetes Secret) using `ADMIN_EMAIL` and `ADMIN_PASSWORD` as a fallback if no DB admin exists.
- Local: use `.env.local` or seed accounts via the manager script.

## Managing Accounts
- Script: `python MindMend/manage_accounts.py`
- Examples:
  - Create super admin:
    `python MindMend/manage_accounts.py create-admin --email admin@mindmend.xyz --password 'Strong#Pass123' --name 'Platform Owner'`
  - Create therapist:
    `python MindMend/manage_accounts.py create-counselor --email therapist@mindmend.com.au --password 'Strong#Pass123' --name 'Dr. Jane Doe'`
  - List accounts:
    `python MindMend/manage_accounts.py list`

Notes:
- Tables are created automatically on first run (`db.create_all()`), so no migrations are needed for initial setup.
- Passwords are stored hashed.

## Kubernetes Secrets (bootstrap admin)
If you need emergency/admin bootstrap without DB access, set these keys in the `mindmend-secrets` Secret:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

Commands:
- Create/update:
  ```
  kubectl -n mindmend create secret generic mindmend-secrets \
    --from-literal=ADMIN_EMAIL=admin@mindmend.xyz \
    --from-literal=ADMIN_PASSWORD='Strong#Pass123' \
    --dry-run=client -o yaml | kubectl apply -f -
  ```
- Verify (requires cluster access):
  ```
  kubectl -n mindmend get secret mindmend-secrets -o jsonpath='{.data.ADMIN_EMAIL}' | base64 -d; echo
  ```

## Best Practices
- Use DB-backed accounts for all admins and therapists.
- Restrict who can read Kubernetes Secrets (RBAC); do not print secrets in CI logs.
- Rotate admin passwords regularly; prefer role-based accounts (`super_admin`, `admin`).
- Consider moving secrets into Google Secret Manager with the CSI driver.

## Troubleshooting
- Forgot admin password: create a new admin via the manager script, then remove the bootstrap env credentials.
- Counselor unable to login: ensure counselor exists and is `is_active=true`; reset password via the script.

