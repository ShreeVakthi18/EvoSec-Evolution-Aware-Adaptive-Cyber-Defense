"""
Regression tests that mirror TEST_PLAN.md / TEST_RESULTS.md (TC-01..TC-05).

These exist to guarantee the hardening work in this pass did not change the
original detection/enforcement behavior of EAACD.
"""
from tests.conftest import make_client


def test_tc01_normal_user_behavior():
    c = make_client("10.0.1.1")
    for _ in range(15):
        c.get("/login")
        c.get("/search")
        c.get("/profile")

    data = c.get("/dashboard-data").json()
    assert len(data) == 1
    user = data[0]
    assert user["status"] == "NORMAL"
    assert user["risk"] < 3
    assert user["requests"] == 45


def test_tc02_suspicious_behavior_detection():
    c = make_client("10.0.1.2")
    c.get("/login")
    c.get("/admin/dashboard")  # 1st admin hit: risk 2, still NORMAL
    resp = c.get("/admin/dashboard")  # 2nd admin hit: risk 4 -> SUSPICIOUS
    assert resp.status_code == 200  # suspicious users are not blocked, only slowed

    data = c.get("/dashboard-data").json()
    user = next(u for u in data if u["user"] == "10.0.1.2")
    assert user["status"] == "SUSPICIOUS"
    assert 3 <= user["risk"] < 6


def test_tc03_attacker_detection_and_response():
    c = make_client("10.0.1.3")
    c.get("/admin/dashboard")
    c.get("/admin/dashboard")
    resp = c.delete("/admin/delete-user")  # escalates to ATTACKER and is blocked

    assert resp.status_code == 403
    assert resp.json()["message"] == "Access Denied \U0001f6ab"

    data = c.get("/dashboard-data").json()
    user = next(u for u in data if u["user"] == "10.0.1.3")
    assert user["status"] == "ATTACKER"
    assert user["risk"] >= 6


def test_tc04_critical_endpoint_protection_after_attacker_classification():
    c = make_client("10.0.1.4")
    c.get("/admin/dashboard")
    c.get("/admin/dashboard")
    c.delete("/admin/delete-user")  # now classified ATTACKER

    # Every critical endpoint must now be denied...
    assert c.get("/admin/dashboard").status_code == 403
    assert c.post("/payment/transfer").status_code == 403

    # ...but non-critical endpoints keep working, preserving the deception
    # property (the attacker sees no obvious sign of being blocked
    # everywhere).
    assert c.get("/login").status_code == 200
    assert c.get("/search").status_code == 200


def test_tc05_dashboard_reflects_live_state_transitions():
    c = make_client("10.0.1.5")

    data = c.get("/dashboard-data").json()
    assert data == []  # no users tracked yet

    c.get("/login")
    data = c.get("/dashboard-data").json()
    assert data[0]["status"] == "NORMAL"

    c.get("/admin/dashboard")
    c.get("/admin/dashboard")
    data = c.get("/dashboard-data").json()
    assert data[0]["status"] == "SUSPICIOUS"

    c.delete("/admin/delete-user")
    data = c.get("/dashboard-data").json()
    assert data[0]["status"] == "ATTACKER"
    assert data[0]["requests"] == 4
