from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import time

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

endpoint_stats = {}
user_behavior = {}

# -------------------------
# CLASSIFY USER
# -------------------------
def classify_user(risk):
    if risk >= 6:
        return "ATTACKER"
    elif risk >= 3:
        return "SUSPICIOUS"
    return "NORMAL"

# -------------------------
# CRITICAL ENDPOINT DETECTION
# -------------------------
def detect_critical_endpoints():
    critical = []

    for path, data in endpoint_stats.items():
        if any(word in path for word in ["admin", "delete", "payment"]):
            critical.append(path)

        elif data["count"] < 3 and any(m in data["methods"] for m in ["DELETE", "POST"]):
            critical.append(path)

    return critical

# -------------------------
# RISK ENGINE
# -------------------------
def detect_suspicious_user(user_id):
    history = user_behavior.get(user_id, [])
    critical_endpoints = detect_critical_endpoints()

    risk = 0

    for action in history:
        path = action["path"]
        method = action["method"]

        if path in critical_endpoints:
            risk += 2

        if method in ["DELETE", "POST"]:
            risk += 1

    if len(history) > 10:
        risk += 1

    paths = [h["path"] for h in history]

    if any("/admin" in p for p in paths) and "/login" not in paths:
        risk += 2

    return risk

# -------------------------
# MIDDLEWARE
# -------------------------
@app.middleware("http")
async def track(request: Request, call_next):

    path = request.url.path
    method = request.method
    user_id = request.client.host

    if path.startswith("/static") or path == "/dashboard-data":
        return await call_next(request)

    if path not in endpoint_stats:
        endpoint_stats[path] = {"count": 0, "methods": set()}

    endpoint_stats[path]["count"] += 1
    endpoint_stats[path]["methods"].add(method)

    if user_id not in user_behavior:
        user_behavior[user_id] = []

    user_behavior[user_id].append({
        "path": path,
        "method": method
    })

    risk = detect_suspicious_user(user_id)
    status = classify_user(risk)

    if status == "SUSPICIOUS":
        time.sleep(1)

    if status == "ATTACKER":
        if "admin" in path or "delete" in path or "payment" in path:
            return JSONResponse(status_code=403, content={"message": "Access Denied 🚫"})

    return await call_next(request)

# -------------------------
# DASHBOARD DATA
# -------------------------
@app.get("/dashboard-data")
def dashboard_data():

    result = []

    for user_id, actions in user_behavior.items():
        risk = detect_suspicious_user(user_id)
        status = classify_user(risk)

        result.append({
            "user": user_id,
            "requests": len(actions),
            "risk": risk,
            "status": status
        })

    return result

# -------------------------
# UI
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>SOC System Running</h2>
    <a href='/static/dashboard.html'>Open Dashboard</a>
    """

# -------------------------
# SAMPLE APIS
# -------------------------
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