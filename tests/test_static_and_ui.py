from tests.conftest import make_client


def test_home_page_links_to_dashboard_and_banking_panel():
    c = make_client("10.0.4.1")
    resp = c.get("/")
    assert resp.status_code == 200
    assert "/static/dashboard.html" in resp.text
    assert "/static/index.html" in resp.text


def test_static_dashboard_html_is_served():
    c = make_client("10.0.4.2")
    resp = c.get("/static/dashboard.html")
    assert resp.status_code == 200
    assert "Security Operations Dashboard" in resp.text


def test_static_index_html_is_served():
    c = make_client("10.0.4.3")
    resp = c.get("/static/index.html")
    assert resp.status_code == 200
    assert "Banking Control Panel" in resp.text


def test_path_traversal_via_static_mount_is_blocked():
    c = make_client("10.0.4.4")
    resp = c.get("/static/../main.py")
    assert resp.status_code in (403, 404)

    resp2 = c.get("/static/%2e%2e/main.py")
    assert resp2.status_code in (403, 404)


def test_healthz_returns_ok():
    c = make_client("10.0.4.5")
    resp = c.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
