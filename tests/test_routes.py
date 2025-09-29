def test_home_ok(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"<!DOCTYPE html" in res.data or b"<html" in res.data


def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data and data.get("status") == "healthy"

