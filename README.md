# EAACD — Evolution-Aware Adaptive Cyber Defense

> *"A user is not dangerous because of a single action — they are dangerous because of how they evolve, and where they choose to act."*

A production-hardened FastAPI middleware that tracks how a user's behavior *evolves* across requests — rather than judging each request in isolation — and automatically identifies which endpoints are worth protecting, so it can adapt its response as risk rises: from silent monitoring, to friction, to blocking access to critical assets.

---

## Screenshots

**Banking Control Panel** — the demo target application EAACD protects:

<img src="https://github.com/user-attachments/assets/413873bb-2ddc-4163-905d-f664a4933e45" width="800"/>

**SOC Dashboard** — live view of tracked users, risk scores, and classification state:

<img src="https://github.com/user-attachments/assets/fa85c2e6-8978-4422-9dc8-062e0541737d" width="800"/>

---

## Live Demo

- Banking Control Panel: [evosec-evolution-aware-adaptive-cyber.onrender.com/static/index.html](https://evosec-evolution-aware-adaptive-cyber.onrender.com/static/index.html)
- SOC Dashboard: [evosec-evolution-aware-adaptive-cyber.onrender.com/static/dashboard.html](https://evosec-evolution-aware-adaptive-cyber.onrender.com/static/dashboard.html)

> Hosted on Render's free tier — the instance may take a few seconds to wake up on first request after being idle, and being a single free-tier instance, behavioral state resets on redeploy/restart.

---

## Overview

Most detection systems evaluate one request against a ruleset and allow or block it. That approach misses an attacker who moves slowly and stays under the threshold for any single action.

EAACD instead tracks a user's full behavioral history and asks two questions on every request:

1. **Where has this user been, and where are they going?** (behavioral evolution)
2. **Does that path touch a critical asset?** (automatically detected, not manually labeled)

The combination of those two signals drives a continuous risk score, which in turn drives a graduated response — not a binary allow/block decision.

---

## Key Features

- **Automatic critical-asset detection** — endpoints containing `admin`, `delete`, or `payment` are flagged as critical by route-name analysis; routes hit rarely but with destructive methods (`DELETE`/`POST`) are flagged too, so the system doesn't need every sensitive route hand-labeled, even ones it has never seen before.
- **Behavioral evolution tracking** — every request (path, method, source identity) is appended to a per-user history, so classification reflects the arc of a session, not a single hit. A user who goes `/login → /search → /profile → /admin/dashboard` looks very different from one who jumps straight to `/admin/dashboard`.
- **Dynamic, continuous risk scoring** — score rises with critical-endpoint access, destructive methods, admin access without a prior login step, and abnormally high request volume, so both fast noisy attacks and slow deliberate ones get caught.
- **Adaptive, graduated response** — `NORMAL → SUSPICIOUS → ATTACKER`, escalating from doing nothing, to a non-blocking response delay, to denying access on critical paths — while non-critical paths (`/login`, `/search`, `/profile`) keep working normally even for an `ATTACKER`-classified user, so detection isn't revealed outright.
- **Real-time SOC dashboard** — polls `/dashboard-data` every 2 seconds to show active users, request counts, risk scores, and classification, with visual emphasis (color badges, pulse/blink animation) on elevated and attacker-classified sessions.
- **Production hardening layered on top of the original detection logic** — see below — without changing the detection formula, thresholds, or enforcement behavior.

---

## System Architecture / Workflow

Every request passes through the middleware pipeline, in order:

```
CORS check → security headers → body-size limit → track & score & enforce → route handler
```

**Step 1 — Entry Point.** Every request enters through the web application and the API gateway; EAACD intercepts it at the middleware layer before any business logic runs.

**Flow:** User → Web Application → API Gateway

<img src="https://github.com/user-attachments/assets/eb510143-85f3-4890-9feb-b24e78071c3c" width="400"/>

**Step 2 — Behavior Tracking.** User identity, endpoint, and HTTP method are extracted and appended to that user's behavioral history in the tracking store.

**Flow:** API Gateway → Request Handler → Behavioral History Store

<img src="https://github.com/user-attachments/assets/2a5d2f0e-dde5-472a-ba50-78c27080021a" width="500"/>

**Step 3 — Risk Analysis.** The risk engine reads the user's full history against the critical-endpoint map and the detected pattern of behavioral evolution, producing a score that climbs progressively as the pattern looks more concerning.

**Flow:** Behavior History → Risk Engine → Classification Layer

<img src="https://github.com/user-attachments/assets/2df03920-daad-436b-9da0-850519f06b3b" width="500"/>

**Step 4 — Adaptive Response.** The classification layer maps the score to a response: pass through normally, delay responses, or block/redirect on critical paths — while the real system underneath continues operating normally.

**Flow:** Classification → Response Engine → API Gateway Control

<img src="https://github.com/user-attachments/assets/f0dd8aad-68d4-423f-bec7-a4927bb7fc5c" width="500"/>

**Step 5 — Monitoring Layer.** Every classification decision, new-user detection, and threat event streams to the SOC dashboard in real time.

**Flow:** Logs + Classification Data → SOC Dashboard

<img src="https://github.com/user-attachments/assets/f9c2e52b-adc1-4233-9a36-d178d2d6fbd7" width="450"/>

**Final Architecture:**

<img src="https://github.com/user-attachments/assets/e22ce21e-d392-47da-a0e3-7e19959d3bbe" width="800"/>

---

## Behavioral Detection & Progressive Enforcement

| Score | Classification | Enforcement |
|---|---|---|
| 0 – 2 | 🟢 NORMAL | Full access, no restrictions |
| 3 – 5 | 🟡 SUSPICIOUS | Responses delayed (throttle) — friction applied silently, no outward signal |
| 6+ | 🔴 ATTACKER | Critical endpoints return `403 Access Denied`; non-critical endpoints keep responding normally |

This is a **throttle → restrict → isolate** progression: friction increases with confidence, and only confirmed high-risk sessions lose access to sensitive routes, so an attacker isn't tipped off the moment they're first flagged.

**Sample protected surface (demo "banking" app):**

- Public: `/login`, `/search`, `/profile`
- Critical (flagged automatically): `/admin/dashboard`, `/admin/delete-user`, `/payment/transfer`
- Monitoring: `/dashboard-data`, `/healthz`

### Normal User

Follows a stable path with no escalation — only low-sensitivity endpoints, safe HTTP methods. Score stays low; no restrictions applied. The dashboard shows a 🟢 `NORMAL` badge, `Threats: 0`, `Status: OK`, and a single `New user detected` log entry.

<img src="https://github.com/user-attachments/assets/2204e120-b6ed-4e7f-bb90-4c0b49fadf10" width="800"/>

Clicking **Login**, **Search**, or **Profile** in the Banking Control Panel fires safe `GET` requests; none are critical endpoints, so responses return immediately with no delay.

<img src="https://github.com/user-attachments/assets/b9d6bd4b-cf02-4ab7-b7e4-6381bf0f9831" width="800"/>

### Suspicious User

Begins probing routes closer to sensitive parts of the system without a legitimate reason — e.g. repeated **Admin** or **Delete User** clicks without a prior login. Once the score crosses 3, the badge shifts to 🟡 `SUSPICIOUS`, the Risk card pulses, but `Status` stays `OK` and no threat alert fires — the friction (a non-blocking ~1s delay) is applied invisibly.

<img src="https://github.com/user-attachments/assets/d76d034b-0163-4e26-8795-66dba5ecb6c3" width="800"/>

From the panel, this shows up only as button clicks feeling noticeably slower — responses still look normal, with no error or block.

<img src="https://github.com/user-attachments/assets/de46235b-c823-4b14-85b6-d9e8b90a02e7" width="800"/>

### High-Risk / Attacker

A deliberate escalation toward `/admin/dashboard`, `/admin/delete-user`, and `/payment/transfer` pushes the score to 6+. The dashboard flips to a blinking 🔴 `ATTACKER` badge, `Threats` increments, `Status` reads `ATTENTION REQUIRED`, and the activity log fires an `Attack detected from [IP]` entry each poll cycle.

<img src="https://github.com/user-attachments/assets/61394294-038e-46c7-b0b1-8904f3ba0b53" width="800"/>

On the panel, further clicks to critical endpoints now return `{"message": "Access Denied 🚫"}` (HTTP 403) — the route handler is never reached and no real data is touched — while **Login**, **Search**, and **Profile** continue to respond normally, so the system doesn't reveal outright that detection has occurred.

<img src="https://github.com/user-attachments/assets/8866af98-12d8-49b3-82be-71f38f1cb12f" width="800"/>

---

## Production Hardening

The behavioral detection logic itself is unchanged from the original prototype. What was added around it:

- **Security headers** on every response, including error responses: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store`, and `Strict-Transport-Security` in production.
- **CORS allow-list**, implemented explicitly in middleware — no wildcard origin is ever honored in production.
- **Request body size limiting** — oversized requests are rejected with `413` before reaching any handler; a malformed `Content-Length` header is rejected with `400`.
- **Fail-safe error handling** — `HTTPException` and validation errors return clean JSON; any unhandled exception is logged server-side with a request ID and returns a generic `500` with no stack trace or internal detail exposed to the client.
- **Structured, security-relevant logging** — path, method, source identifier, computed risk, and classification are logged per request; no request bodies, headers, or credential-like values are logged.
- **Bounded, thread-safe in-memory state** — the behavioral store is designed to be safe under concurrent access and bounded so a long-running process doesn't grow memory without limit.
- **Environment-driven configuration** — runtime mode, CORS origins, risk weights/thresholds, delay duration, and body-size limits are all configurable via environment variables rather than hard-coded.
- **Docs disabled in production** — `/docs`, `/redoc`, and `/openapi.json` are only exposed when not running in production mode.
- **Non-root, health-checked Docker image** with pinned dependencies (see `requirements.txt`).

---

## Testing

```text
pytest -v

20 passed
```

This result was reproduced independently: the repository was cloned into a fresh environment, dependencies installed, and the suite run against a clean checkout, alongside manually confirming the app starts under Uvicorn and that the dashboard and Banking Control Panel load and respond correctly at normal browser zoom.

The automated suite covers:

- **Regression scenarios** — the original prototype's test cases (normal browsing stays low-risk; repeated admin/delete access escalates to `SUSPICIOUS` without blocking; further escalation reaches `ATTACKER`, at which point critical endpoints return `403` while `/login` and `/search` keep working; and the dashboard reflects these live state transitions).
- **Security hardening** — security headers present on both success and error responses, CORS allow-list enforcement, oversized-body rejection, malformed-header rejection, JSON-only error bodies with no stack traces, and health checks excluded from behavioral tracking.
- **State management** — concurrent simulated users exercising the middleware without corrupting shared state, and per-user history staying within a configured bound.
- **Static assets & UI** — the dashboard and banking panel are served correctly, path-traversal attempts against the static file mount are rejected, and the health check responds.

---

## Technologies Used

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Configuration | pydantic-settings (environment-variable driven) |
| Frontend | HTML, CSS, JavaScript |
| Communication | REST APIs |
| State Storage | Bounded, thread-safe in-memory session tracking |
| Testing | pytest |
| Packaging | Docker (non-root user, pinned base image, container health check) |

---

## Project Structure

```
main.py                 # FastAPI app, middleware pipeline, routes
app/
  config.py             # Environment-driven settings
  risk_engine.py         # Behavioral store + scoring/classification logic
  logging_config.py      # Structured logging helpers
static/
  index.html              # Banking Control Panel (demo target app)
  dashboard.html           # SOC Dashboard (polls /dashboard-data)
tests/                     # Automated regression + hardening test suite
```

---

## Local Setup

```bash
git clone https://github.com/<your-username>/<repository>.git
cd <repository>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Run the test suite:

```bash
pip install -r requirements-dev.txt
pytest -v
```

Start the app:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open:

- Home: `http://localhost:8000`
- Banking Control Panel: `http://localhost:8000/static/index.html`
- SOC Dashboard: `http://localhost:8000/static/dashboard.html`
- Health check: `http://localhost:8000/healthz`

All tunables (CORS origins, risk weights/thresholds, response delay, request size limit, logging) are environment variables — see `.env.example` for the documented list.

---

## Docker Deployment

```bash
cp .env.example .env
docker compose up --build
```

`docker-compose.yml` pins `WEB_CONCURRENCY=1` deliberately — the behavioral store is in-process memory, so running multiple workers or replicas would give each process a different, disagreeing view of a user's risk (see Limitations).

---

## Current Limitations

This is a **production-hardened, deployable prototype** — not an enterprise SOC platform. Specifically:

- **In-memory behavioral state.** All history and risk state live in one process's memory and are lost on restart; there is no shared or persistent store.
- **IP-based identity.** Users are tracked by source IP (`request.client.host`), which can misattribute users behind NAT/shared proxies, and can be reset by an attacker who rotates IPs.
- **No authentication or authorization layer**, on any endpoint — including the SOC dashboard's data feed. This is a defensive detection/middleware layer, not an identity system.
- **Deception is an enforcement stub, not a honeypot.** `ATTACKER`-classified requests to critical endpoints currently receive a `403`, not a fully realistic decoy environment.
- **TLS termination is a deployment concern**, not something this application does itself — `Strict-Transport-Security` is only emitted in production on the assumption TLS is terminated by an upstream proxy/load balancer.
- **Single-process scaling.** Because state is in-memory, horizontal scaling to multiple workers/replicas requires moving to a shared backend (e.g. Redis) first — intentionally not implemented here.

---

## Author

I built EAACD to demonstrate that behavioral intelligence and adaptive, graduated response are a sound foundation for threat detection — understanding *how* threats evolve, not just reacting to individual events in isolation — then hardened it into a small, honestly-documented, production-adjacent prototype: the same detection philosophy, running on a codebase that fails safely, is configurable per environment, and is covered by an automated regression suite.
