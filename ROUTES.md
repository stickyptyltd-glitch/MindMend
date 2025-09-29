# Route & Blueprint Map

This map lists primary routes. Prefixes are shown per blueprint; not every minor API is included.

## App (root app)
- `/` Home (smart dashboard/marketing)
- `/onboarding`, `/activities`, `/media-pack`
- `/register`, `/login`, `/logout`, `/forgot-password`
- Therapy: `/individual`, `/individual-therapy`, `/relationship`, `/group`
- Video: `/video-assessment`, `/emotion-tracking`, `POST /api/log-emotion`
- Dashboard/API: `/dashboard`, `GET /api/dashboard-stats`

## Admin (`/admin`, admin_panel.py)
- `/` login/dashboard, `/logout`
- Management: `/user-management`, `/financial-overview`, `/system-monitoring`, `/deployment-tools`
- AI/Research: `/ai-assistant`, `/research-management`, `/ai-models`, `/ai-model-manager`
- APIs: `/api/ai-models/status`, `POST /api/ai-models/test`, `/api/enhancement-modules/status`

## Counselor (`counselor_dashboard.py`)
- `/counselor/*`: dashboard, employment, apply, schedule, clients, earnings, training
- Auth: `/counselor/login`, `/counselor/logout`
- APIs: `POST /counselor/api/session-notes`, `POST /counselor/api/availability`

## Payments (`/payments`, payment_integration.py)
- `/plans`, `POST /create-checkout-session`, `/success`, `/cancel`
- Webhooks: `POST /webhook/stripe`
- Mobile: `POST /mobile/apple-pay`, `POST /mobile/google-pay`

## OAuth (`/oauth`, oauth_system.py)
- `/login/<provider>`, `/<provider>/callback`, `POST /unlink/<provider>`, `/status`

## Mobile (`/mobile`, mobile_app.py)
- Health: `/api/health`
- Auth: `POST /api/auth/mobile-login`
- Therapy: `POST /api/therapy/mobile-session`
- Payments: `POST /api/payments/mobile-checkout`
- Biometric: `POST /api/biometric/sync`
- Downloads: `/download/ios`, `/download/android`, `/manifest.json`, `/sw.js`

## Emotion API (`/api/emotion`, emotion_detection_api.py)
- `POST /analyze`, `GET /trends`, `POST /therapy-adjustment`, `GET /status`, `POST /clear-history`

## Crisis API (`/api/crisis`, crisis_intervention_api.py)
- `POST /analyze`, `POST /emergency-override`, `GET /status`

## Health & Ops
- App health: Docker/Nginx exposes `/health` (see `docker/nginx.conf` and monitoring scripts)
- Monitoring utilities: `scripts/monitor.sh`, `monitoring.py`

Tip: For a full list, ripgrep for routes: `rg -n "@\w+_?bp?\.route\(" MindMend`

