def test_onboarding_ok(client):
    res = client.get("/onboarding")
    assert res.status_code == 200


def test_subscribe_ok(client):
    res = client.get("/subscribe")
    assert res.status_code == 200


def test_activities_ok(client):
    res = client.get("/activities")
    assert res.status_code == 200


def test_media_pack_ok(client):
    res = client.get("/media-pack")
    assert res.status_code == 200


def test_couples_session_requires_login(client):
    res = client.get("/couples/session", follow_redirects=False)
    assert res.status_code in (301, 302)
    # Should redirect to couples login
    assert "/couples/login" in res.headers.get("Location", "")


def test_checkout_without_stripe_keys_graceful(client):
    # Without valid Stripe keys, app should handle error by redirecting to /subscribe
    res = client.post("/create-checkout-session", follow_redirects=False)
    assert res.status_code in (302, 303)
    assert "/subscribe" in res.headers.get("Location", "")


def test_dashboard_stats_ok(client):
    res = client.get("/api/dashboard-stats")
    assert res.status_code == 200
    data = res.get_json()
    # Expect core keys present even if empty
    for key in [
        "total_sessions",
        "this_week_sessions",
        "completed_exercises",
        "avg_mood_week",
        "streak_days",
        "improvement_percentage",
    ]:
        assert key in data


def test_counselor_login_flow(client):
    # Dashboard should redirect to login if not authenticated
    res = client.get("/counselor/dashboard", follow_redirects=False)
    assert res.status_code in (301, 302)
    assert "/counselor/login" in res.headers.get("Location", "")

    # Post valid demo credentials then get redirected to dashboard
    res = client.post(
        "/counselor/login",
        data={"email": "therapist@mindmend.com.au", "password": "x"},
        follow_redirects=False,
    )
    assert res.status_code in (301, 302)
    assert "/counselor/dashboard" in res.headers.get("Location", "")
