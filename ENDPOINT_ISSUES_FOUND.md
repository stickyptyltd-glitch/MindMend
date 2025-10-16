# Endpoint Issues Found During Testing
**Date Started:** 2025-10-10
**Status:** 🔍 Active Testing

## Critical Issues Found

### Issue #1: User Registration Broken (405 Method Not Allowed)
**Severity:** 🔴 **CRITICAL** - Blocks all new user signups
**Status:** ✅ FIXED in v8

**Problem:**
- Registration POST request redirects to `/onboarding`
- `/onboarding` endpoint only accepted GET requests
- Resulted in 405 Method Not Allowed error
- Users unable to complete registration

**Root Cause:**
```python
# general.py:18 (BEFORE FIX)
@general_bp.route("/onboarding")  # No methods specified = GET only
def onboarding():
    return render_template("onboarding.html")
```

**Fix Applied:**
```python
# general.py:18 (AFTER FIX)
@general_bp.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    return render_template("onboarding.html")
```

**Files Modified:**
- `/home/mindmendxyz/MindMend/general.py:18`

**Testing Evidence:**
```bash
# From logs:
10.28.2.30 - - [10/Oct/2025:08:28:13 +0000] "POST /register HTTP/1.0" 302 209
10.28.2.30 - - [10/Oct/2025:08:28:13 +0000] "POST /onboarding HTTP/1.0" 405 153
```

**Impact:**
- Prevented ALL new user registrations
- Affected user acquisition and growth
- Critical production issue

**Deployment:**
- Fixed in v8 deployment
- Awaiting build completion and deployment verification

---

## Issues Under Investigation

### Potential Issue #2: Similar Method Missing Issues
**Status:** 🔍 Investigating

Based on the `/onboarding` issue, checking for other routes that may be missing POST methods but receive POST redirects.

**Routes to Check:**
- Routes that are redirect targets
- Form submission endpoints
- Authentication flows

**Search Pattern:**
```bash
# Find routes with no methods specified
grep -n "@.*_bp.route(" general.py | grep -v "methods="
```

---

## Testing Progress

### ✅ Completed Tests
1. **Homepage** - ✅ Working (returns 200)
2. **Login Page (GET)** - ✅ Working (returns 200)
3. **Register Page (GET)** - ✅ Working (returns 200)
4. **Admin Login** - ✅ Working (tested in v7)
5. **Admin Dashboard** - ✅ Working (tested in v7)

### 🔍 In Progress
6. **User Registration (POST)** - 🔧 FIXING (v8 deployment)

### ⏳ Pending Tests
7. User Login (POST)
8. Dashboard Access (authenticated)
9. AI Chat Session
10. Biometric Data Upload
11. Video Analysis
12. Crisis Intervention
13. Payment/Subscription
14. Admin Panel Features
15. API Endpoints

---

## Deployment History

| Version | Changes | Issues Fixed | Status |
|---------|---------|--------------|--------|
| v1-v7 | Admin panel fixes | Database init, template vars, routes | ✅ Deployed |
| v8 | Registration fix | Issue #1: /onboarding 405 error | 🔄 Building |

---

## Pattern Analysis

### Common Issue Patterns Discovered:
1. **Missing HTTP Methods** - Routes not specifying required methods
2. **Template Variable Mismatches** - View/template variable name differences (found in v3-v7)
3. **Missing Database Models** - Referenced models not in database (found in v2)
4. **Import Name Mismatches** - Model names inconsistent (found in v7)

### Recommendations:
1. **Audit all route decorators** for missing methods specifications
2. **Check redirect chains** to ensure target routes accept correct methods
3. **Validate template variables** systematically across all views
4. **Review model imports** for consistency

---

## Next Steps

1. ✅ Complete v8 deployment
2. ✅ Test user registration end-to-end
3. 🔍 Search for similar method specification issues
4. 🔍 Test user login flow
5. 🔍 Test authenticated dashboard access
6. 🔍 Continue with comprehensive endpoint testing per plan

---

*Last Updated: 2025-10-10 - Issue #1 discovered and fixed*
