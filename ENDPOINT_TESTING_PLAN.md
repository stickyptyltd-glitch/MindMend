# Comprehensive Endpoint Testing Plan
**Date:** 2025-10-10
**Status:** 📋 Ready to Execute

## Overview
Systematic testing plan for all 345+ endpoints in the MindMend platform to ensure full functionality and identify any broken endpoints or integration issues.

## Testing Strategy

### Token-Efficient Approach
Rather than testing all 345 routes individually, we'll:
1. **Test critical user flows** end-to-end
2. **Group-test related endpoints** (e.g., all admin routes together)
3. **Use automated testing scripts** where possible
4. **Focus on error-prone areas** identified during admin panel fixes

---

## Phase 1: Critical Path Testing (Priority 1)

### 1.1 User Authentication Flow
**Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/reset-password` - Password reset

**Test Script:**
```bash
# Register new user
curl -X POST http://34.143.177.214/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# Login
curl -X POST http://34.143.177.214/auth/login \
  -d "email=test@example.com&password=Test123!" \
  -c /tmp/user_session.txt

# Check authenticated access
curl -b /tmp/user_session.txt http://34.143.177.214/dashboard
```

**Expected Results:**
- Registration creates new Patient record
- Login returns valid session cookie
- Dashboard accessible with session
- Logout clears session

---

### 1.2 Admin Authentication Flow
**Status:** ✅ **VERIFIED WORKING** (v7 deployment)

**Endpoints:**
- `GET /admin/login` - Admin login page
- `POST /admin/login` - Admin authentication
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/logout` - Admin logout

**Verification:**
- ✅ Login working (admin@mindmend.com)
- ✅ Dashboard rendering with data
- ✅ Session persistence functional

---

### 1.3 AI Chat/Therapy Session Flow
**Endpoints:**
- `GET /dashboard` - User dashboard
- `POST /start-session` - Start therapy session
- `POST /send-message` - Send message to AI
- `POST /end-session` - End session
- `GET /session-history` - View past sessions

**Test Scenarios:**
1. User starts new therapy session
2. Send messages and receive AI responses
3. Check session data is saved
4. Verify emotion detection working
5. End session and verify completion

---

### 1.4 Payment/Subscription Flow
**Endpoints:**
- `GET /pricing` - View pricing plans
- `POST /create-checkout-session` - Start Stripe checkout
- `POST /webhook/stripe` - Handle Stripe webhooks
- `GET /subscription-status` - Check subscription
- `POST /cancel-subscription` - Cancel subscription

**Test Requirements:**
- ⚠️ Requires Stripe test keys configured
- Test with Stripe test cards (4242 4242 4242 4242)
- Verify webhook handling

---

## Phase 2: Module-Based Testing (Priority 2)

### 2.1 Admin Panel Routes
**Module:** `/admin/*`
**Total Routes:** ~30 estimated

**Route Groups:**
1. **Dashboard & Overview**
   - `/admin/` - Main dashboard ✅
   - `/admin/dashboard` - Dashboard ✅
   - `/admin/quick-actions` - Quick actions
   - `/admin/system-status` - System status

2. **User Management**
   - `/admin/users` - User list
   - `/admin/users/<id>` - User details
   - `/admin/users/<id>/edit` - Edit user
   - `/admin/users/<id>/delete` - Delete user

3. **Financial Management**
   - `/admin/finance` - Finance dashboard
   - `/admin/revenue` - Revenue analytics
   - `/admin/subscriptions` - Subscription management
   - `/admin/payments` - Payment records

4. **AI Management**
   - `/admin/ai-models` - AI model management
   - `/admin/ai-performance` - AI performance metrics
   - `/admin/ai-training` - Model training

5. **System Management**
   - `/admin/settings` - System settings
   - `/admin/logs` - System logs
   - `/admin/backups` - Database backups
   - `/admin/audit` - Audit logs

**Testing Method:**
```python
# Automated script to test all admin routes
import requests

admin_routes = [
    '/admin/dashboard',
    '/admin/users',
    '/admin/finance',
    '/admin/ai-models',
    '/admin/settings'
]

session = requests.Session()
session.post('http://34.143.177.214/admin/login',
             data={'email': 'admin@mindmend.com', 'password': 'Admin123!'})

for route in admin_routes:
    response = session.get(f'http://34.143.177.214{route}')
    print(f"{route}: {response.status_code}")
```

---

### 2.2 Biometric Data Routes
**Module:** `/biometric/*`
**Purpose:** Wearable device integration

**Endpoints:**
- `POST /biometric/upload` - Upload biometric data
- `GET /biometric/history` - View history
- `GET /biometric/insights` - Get AI insights
- `POST /biometric/sync` - Sync with wearable

**Test Data:**
```json
{
  "heart_rate": 75,
  "stress_level": 45,
  "sleep_hours": 7.5,
  "hrv": 65,
  "timestamp": "2025-10-10T12:00:00Z"
}
```

---

### 2.3 Video Analysis Routes
**Module:** `/video/*`
**Purpose:** Real-time emotion detection

**Endpoints:**
- `POST /video/start` - Start video analysis
- `POST /video/frame` - Upload video frame
- `GET /video/results` - Get analysis results
- `POST /video/stop` - Stop analysis

**Test Requirements:**
- Requires video frames or webcam access
- Tests emotion detection models
- Verifies WebSocket connections

---

### 2.4 Crisis Intervention Routes
**Module:** `/crisis/*`
**Purpose:** Emergency response system

**Endpoints:**
- `POST /crisis/alert` - Create crisis alert
- `GET /crisis/resources` - Get emergency resources
- `POST /crisis/contact` - Contact emergency services
- `GET /crisis/hotlines` - List crisis hotlines

**Critical:** These routes must be thoroughly tested for reliability

---

### 2.5 Exercise/Activity Routes
**Module:** `/activities/*` or `/exercises/*`

**Endpoints:**
- `GET /exercises` - List exercises
- `GET /exercises/<id>` - Exercise details
- `POST /exercises/complete` - Mark complete
- `GET /exercises/recommendations` - AI recommendations

---

## Phase 3: API Endpoint Testing (Priority 3)

### 3.1 REST API Routes
**Base:** `/api/*`

**Categories:**
1. **Dashboard API**
   - `GET /api/dashboard/metrics`
   - `GET /api/dashboard/alerts`
   - `GET /api/dashboard/user-activity`

2. **Session API**
   - `GET /api/sessions`
   - `GET /api/sessions/<id>`
   - `POST /api/sessions/start`
   - `POST /api/sessions/end`

3. **User API**
   - `GET /api/users/profile`
   - `PUT /api/users/profile`
   - `GET /api/users/stats`

---

## Phase 4: WebSocket/Real-time Testing (Priority 3)

### 4.1 Socket.IO Endpoints
**Namespace:** Socket.IO events

**Events to Test:**
- `connect` - WebSocket connection
- `video_frame` - Real-time video processing
- `biometric_update` - Real-time biometric data
- `chat_message` - Real-time chat
- `disconnect` - Cleanup

**Test Tools:**
- Python socketio client
- JavaScript socket.io-client

---

## Phase 5: Error Handling & Edge Cases (Priority 4)

### 5.1 Authentication Edge Cases
- Invalid credentials
- Expired sessions
- Missing CSRF tokens
- Rate limiting

### 5.2 Data Validation
- Invalid JSON payloads
- Missing required fields
- SQL injection attempts (security)
- XSS attempts (security)

### 5.3 Performance
- Large file uploads
- Concurrent requests
- Long-running sessions
- Memory leaks

---

## Automated Testing Script

### Full Endpoint Test Script
```python
#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for MindMend platform
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://34.143.177.214'

class EndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            'passed': [],
            'failed': [],
            'errors': []
        }

    def test_endpoint(self, method, path, data=None, auth_required=False):
        """Test a single endpoint"""
        try:
            url = f"{BASE_URL}{path}"

            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)

            if response.status_code < 400:
                self.results['passed'].append({
                    'path': path,
                    'status': response.status_code,
                    'method': method
                })
                return True
            else:
                self.results['failed'].append({
                    'path': path,
                    'status': response.status_code,
                    'method': method,
                    'error': response.text[:200]
                })
                return False

        except Exception as e:
            self.results['errors'].append({
                'path': path,
                'method': method,
                'error': str(e)
            })
            return False

    def test_admin_routes(self):
        """Test all admin panel routes"""
        # Login first
        self.session.post(f"{BASE_URL}/admin/login", data={
            'email': 'admin@mindmend.com',
            'password': 'Admin123!'
        })

        admin_routes = [
            ('GET', '/admin/dashboard'),
            ('GET', '/admin/users'),
            ('GET', '/admin/finance'),
            ('GET', '/admin/subscriptions'),
            ('GET', '/admin/system-status'),
            ('GET', '/admin/api/dashboard/metrics'),
            ('GET', '/admin/api/dashboard/alerts')
        ]

        for method, path in admin_routes:
            self.test_endpoint(method, path, auth_required=True)

    def test_auth_routes(self):
        """Test authentication routes"""
        auth_routes = [
            ('GET', '/auth/login'),
            ('GET', '/auth/register'),
            ('GET', '/admin/login')
        ]

        for method, path in auth_routes:
            self.test_endpoint(method, path)

    def generate_report(self):
        """Generate test report"""
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['errors'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        errors = len(self.results['errors'])

        print(f"\n{'='*60}")
        print(f"ENDPOINT TEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"\nTotal Endpoints Tested: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"⚠️  Errors: {errors} ({errors/total*100:.1f}%)")

        if self.results['failed']:
            print(f"\n{'='*60}")
            print("FAILED ENDPOINTS:")
            print(f"{'='*60}")
            for item in self.results['failed']:
                print(f"\n{item['method']} {item['path']}")
                print(f"  Status: {item['status']}")
                print(f"  Error: {item['error'][:100]}")

        if self.results['errors']:
            print(f"\n{'='*60}")
            print("ENDPOINT ERRORS:")
            print(f"{'='*60}")
            for item in self.results['errors']:
                print(f"\n{item['method']} {item['path']}")
                print(f"  Error: {item['error']}")

if __name__ == '__main__':
    tester = EndpointTester()

    print("Testing authentication routes...")
    tester.test_auth_routes()

    print("Testing admin panel routes...")
    tester.test_admin_routes()

    tester.generate_report()
```

---

## Test Execution Schedule

### Immediate (Today)
- ✅ Admin authentication (COMPLETED)
- ✅ Admin dashboard (COMPLETED)
- Run automated admin route tests
- Test user registration/login flow

### Next Session
- Test AI chat/therapy session flow
- Test biometric data upload
- Test crisis intervention routes
- Review payment integration

### Following Sessions
- Complete API endpoint testing
- WebSocket testing
- Performance testing
- Security testing

---

## Success Criteria

### For Each Endpoint:
- ✅ Returns appropriate HTTP status code
- ✅ No unhandled exceptions
- ✅ Valid response format (HTML/JSON)
- ✅ Proper authentication/authorization
- ✅ Data validation working
- ✅ Database operations successful

### For Critical Flows:
- ✅ End-to-end user journey works
- ✅ Data persists correctly
- ✅ AI responses generated
- ✅ Payments process successfully
- ✅ Crisis alerts trigger properly

---

## Known Issues to Watch For

Based on admin panel fixes, watch for:
1. **Template variable mismatches** - Variable names must match between views and templates
2. **Missing database models** - Ensure all referenced models exist
3. **Route reference errors** - Verify route names match blueprint definitions
4. **Model import issues** - Check for correct model names (e.g., AdminUser not Admin)
5. **Database initialization** - Ensure all tables exist

---

## Documentation Updates Needed

After testing, update:
- API documentation with working endpoints
- User guide with verified flows
- Admin manual with tested features
- Developer guide with route catalog

Remove obsolete documentation:
- Old deployment scripts that have been superseded
- Outdated API references
- Deprecated endpoint documentation

---

## Tools & Resources

### Testing Tools
- `curl` - Command-line HTTP testing
- `requests` (Python) - HTTP library
- `pytest` - Automated testing framework
- Postman/Insomnia - API testing GUI

### Monitoring
- `kubectl logs` - Check application logs
- `/admin/system-status` - System health dashboard
- Database queries - Verify data integrity

---

*Plan created: 2025-10-10*
*Last updated: After v7 admin panel deployment*
