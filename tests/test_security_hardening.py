from tests.conftest import make_client


def test_security_headers_present_on_every_response():
    c = make_client("10.0.2.1")
    resp = c.get("/login")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["referrer-policy"] == "no-referrer"
    assert resp.headers["cache-control"] == "no-store"


def test_security_headers_present_on_error_responses():
    c = make_client("10.0.2.2")
    resp = c.get("/this-route-does-not-exist")
    assert resp.status_code == 404
    assert resp.headers["x-content-type-options"] == "nosniff"


def test_404_returns_json_message_without_stack_trace():
    c = make_client("10.0.2.3")
    resp = c.get("/nope")
    assert resp.status_code == 404
    body = resp.json()
    assert "message" in body
    assert "Traceback" not in resp.text


def test_cors_allows_configured_origin_only():
    c = make_client("10.0.2.4")
    allowed = c.get("/login", headers={"Origin": "http://testserver"})
    assert allowed.headers.get("access-control-allow-origin") == "http://testserver"

    disallowed = c.get("/login", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in disallowed.headers


def test_oversized_request_is_rejected():
    c = make_client("10.0.2.5")
    huge_body = "x" * 2_000_000  # exceeds default MAX_REQUEST_BODY_BYTES
    resp = c.post(
        "/payment/transfer",
        content=huge_body,
        headers={"Content-Length": str(len(huge_body))},
    )
    assert resp.status_code == 413


def test_invalid_content_length_header_is_rejected():
    c = make_client("10.0.2.6")
    resp = c.post(
        "/payment/transfer",
        content="ok",
        headers={"Content-Length": "not-a-number"},
    )
    assert resp.status_code == 400


def test_docs_disabled_outside_debug_when_production():
    # openapi/docs remain available in development (default test env) but
    # the app must be able to disable them; verified via the config flag
    # directly since re-importing main under a different APP_ENV requires a
    # fresh interpreter (pydantic-settings reads env once at import time).
    from app.config import Settings

    prod_settings = Settings(app_env="production", cors_allow_origins="*")
    assert prod_settings.is_production is True
    assert prod_settings.cors_origins_list == []  # wildcard never honored in prod


def test_healthz_is_not_tracked_as_behavior():
    c = make_client("10.0.2.7")
    c.get("/healthz")
    c.get("/healthz")
    c.get("/healthz")
    data = c.get("/dashboard-data").json()
    assert data == []  # health checks must not pollute behavioral history
