"""
EAACD - Evolution-Aware Adaptive Cyber Defense
Production-hardened FastAPI application.

Behavioral/detection logic lives in app/risk_engine.py and is unchanged
from the original prototype other than being configurable and
thread-safe. This module wires up: middleware ordering, request-size
limiting, security headers, CORS, structured logging, and fail-safe
error handling.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.logging_config import log_event, logger
from app.risk_engine import (
    classify_user,
    dashboard_snapshot,
    detect_suspicious_user,
    is_critical_path,
    store,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="EAACD - Evolution-Aware Adaptive Cyber Defense",
    version="1.0.0",
    # Disable interactive docs in production to reduce information disclosure.
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    debug=settings.debug and not settings.is_production,
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# CORS (manual, dependency-free implementation so behavior is explicit and
# testable; production never receives a wildcard origin - see app/config.py)
# ---------------------------------------------------------------------------
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "OPTIONS" and origin:
        allowed = origin in settings.cors_origins_list
        headers = {}
        if allowed:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
            headers["Access-Control-Allow-Headers"] = "Content-Type"
        return JSONResponse(content={}, status_code=204 if allowed else 403, headers=headers)

    response = await call_next(request)
    if origin and origin in settings.cors_origins_list:
        response.headers["Access-Control-Allow-Origin"] = origin
    return response


# ---------------------------------------------------------------------------
# Security headers - applied to every response, including error responses.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# ---------------------------------------------------------------------------
# Request body size limiting - rejects oversized requests before they reach
# any handler, preventing trivial memory-exhaustion DoS.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def body_size_limit_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > settings.max_request_body_bytes:
                return JSONResponse(
                    status_code=413,
                    content={"message": "Request entity too large"},
                )
        except ValueError:
            return JSONResponse(status_code=400, content={"message": "Invalid Content-Length header"})
    return await call_next(request)


# ---------------------------------------------------------------------------
# Core behavioral tracking + adaptive enforcement middleware.
# This preserves the original detection/enforcement workflow:
#   track -> score -> classify -> (delay | block) -> continue
# ---------------------------------------------------------------------------
@app.middleware("http")
async def track_and_enforce(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    path = request.url.path
    method = request.method

    # Endpoints excluded from behavioral tracking (monitoring/static assets).
    if path.startswith("/static") or path in ("/dashboard-data", "/healthz"):
        return await call_next(request)

    user_id = request.client.host if request.client else "unknown"

    store.record(user_id, path, method)

    risk = detect_suspicious_user(user_id)
    status = classify_user(risk)

    log_event(
        "request_scored",
        request_id=request_id,
        path=path,
        method=method,
        user=user_id,
        risk=risk,
        status=status,
    )

    if status == "SUSPICIOUS" and settings.suspicious_response_delay_seconds > 0:
        # Non-blocking delay - the original prototype used time.sleep(1),
        # which blocks the entire event loop for every concurrent request.
        # asyncio.sleep yields control back to the loop instead.
        await asyncio.sleep(settings.suspicious_response_delay_seconds)

    if status == "ATTACKER" and is_critical_path(path):
        log_event(
            "access_denied",
            request_id=request_id,
            path=path,
            method=method,
            user=user_id,
            risk=risk,
        )
        return JSONResponse(status_code=403, content={"message": "Access Denied \U0001f6ab"})

    return await call_next(request)


# ---------------------------------------------------------------------------
# Fail-safe error handling - never leak stack traces or internals to clients.
# ---------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"message": "Invalid request"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "unhandled_exception",
        extra={"extra_fields": {"event": "unhandled_exception", "request_id": request_id, "error": str(exc)}},
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "request_id": request_id},
    )


# ---------------------------------------------------------------------------
# Monitoring / health
# ---------------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    return {"status": "ok", "time": time.time()}


@app.get("/dashboard-data")
def dashboard_data():
    return dashboard_snapshot()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>SOC System Running</h2>
    <a href='/static/index.html'>Open Banking Control Panel</a>
    <br/>
    <a href='/static/dashboard.html'>Open Security Operations Dashboard</a>
    """


# ---------------------------------------------------------------------------
# Sample protected application (the "banking" app EAACD is defending)
# ---------------------------------------------------------------------------
@app.get("/login")
def login():
    return {"message": "Login page"}


@app.get("/search")
def search():
    return {"message": "Search results"}


@app.get("/profile")
def profile():
    return {"message": "User profile"}


@app.get("/admin/dashboard")
def admin_dashboard():
    return {"message": "Admin dashboard"}


@app.delete("/admin/delete-user")
def delete_user():
    return {"message": "User deleted"}


@app.post("/payment/transfer")
def payment():
    return {"message": "Money transferred"}
