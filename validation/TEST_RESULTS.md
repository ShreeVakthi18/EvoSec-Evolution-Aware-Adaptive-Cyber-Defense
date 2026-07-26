# Validation Results

---

# TC-01 – Normal User Behaviour

## Objective

Validate that legitimate user activity is processed normally without triggering adaptive security controls.

---

## Test Steps

1. Launch the Banking Control Panel.
2. Launch the Security Operations Dashboard.
3. Perform normal application usage by repeatedly accessing:
   - Login
   - Search
   - Profile
4. Observe the dashboard metrics after multiple requests.

---

## Expected Result

- User is classified as **NORMAL**.
- Risk score remains low.
- No threats are detected.
- Request counter increases correctly.
- Dashboard updates in real time.

---

## Actual Result

The framework successfully processed **52 API requests** generated through normal application usage.

Observed dashboard metrics:

- **Active Users:** 1
- **Threats Detected:** 0
- **System Status:** OK
- **Average Risk Score:** 1.00
- **User Classification:** NORMAL

The adaptive security engine correctly recognised the activity as legitimate and did not apply any defensive restrictions.

---

## Evidence

### Dashboard

![TC-01 Dashboard](screenshots/TC01_Normal.png)

---

## Result

✅ **PASS**

# TC-02 – Suspicious Behaviour Detection

## Objective

Validate that the adaptive risk engine identifies suspicious user behaviour and applies adaptive security controls before escalating to an attacker classification.

---

## Test Steps

1. Launch the Banking Control Panel.
2. Launch the Security Operations Dashboard.
3. Perform a controlled sequence of requests to privileged administrative endpoints.
4. Observe the user's cumulative risk score and security classification.

---

## Expected Result

- User is classified as **SUSPICIOUS**.
- Risk score exceeds the suspicious threshold.
- Dashboard updates the user's security status.
- Adaptive security response is initiated.

---

## Actual Result

The adaptive risk engine successfully identified abnormal access patterns after **3 API requests**.

Observed dashboard metrics:

- **Active Users:** 1
- **Threats Detected:** 0
- **System Status:** OK
- **Processed Requests:** 3
- **Risk Score:** 4
- **User Classification:** SUSPICIOUS

The framework correctly classified the session as **SUSPICIOUS**, demonstrating behavioural analysis before escalation to the attacker stage.

---

## Evidence

### Dashboard

![TC-02 Dashboard](screenshots/TC02_Suspicious.png)

---

## Result

✅ PASS

# TC-03 – Attacker Detection & Adaptive Response

## Objective

Validate that the Evolution-Aware Adaptive Cyber Defense framework detects malicious behaviour, classifies the session as an attacker, and continuously monitors ongoing attack activity.

---

## Test Steps

1. Launch the Banking Control Panel.
2. Launch the Security Operations Dashboard.
3. Generate malicious activity by repeatedly accessing privileged endpoints:
   - Admin Dashboard
   - Delete User
   - Transfer Money
4. Continue until the cumulative risk exceeds the attacker threshold.
5. Observe the dashboard and live security log.

---

## Expected Result

- User is classified as **ATTACKER**.
- Threat counter increases.
- Dashboard status changes to **ATTENTION REQUIRED**.
- Live attack alerts are generated continuously.
- Adaptive security controls are activated.

---

## Actual Result

The adaptive risk engine successfully identified repeated malicious requests and escalated the session to **ATTACKER**.

### Observed Dashboard Metrics

| Metric | Value |
|--------|------:|
| Active Users | 1 |
| Threats Detected | 1 |
| System Status | ATTENTION REQUIRED |
| Processed Requests | 4 |
| Risk Score | 6 |
| User Classification | ATTACKER |

The Security Operations Dashboard continuously generated real-time attack alerts while monitoring the attacker session, demonstrating continuous behavioural analysis and threat monitoring.

---

## Evidence

### Dashboard

![TC-03 Dashboard](screenshots/TC03_Attacker.png)

### Live Attack Monitoring

![TC-03 Attack Alerts](screenshots/TC03_AttackAlerts.png)

The dashboard repeatedly generated alerts similar to:

```
🚨 Attack detected from 127.0.0.1
```

confirming continuous monitoring of malicious activity.

---

## Result

✅ PASS

# TC-04 – Critical Endpoint Protection

## Objective

Validate that the Evolution-Aware Adaptive Cyber Defense framework protects critical application endpoints by denying access after malicious behaviour is detected.

---

## Test Steps

1. Launch the Banking Control Panel.
2. Launch the Security Operations Dashboard.
3. Generate malicious activity until the user is classified as **ATTACKER**.
4. Attempt to access protected endpoints:
   - Admin Dashboard
   - Delete User
   - Transfer Money
5. Observe the API response.

---

## Expected Result

- User is classified as **ATTACKER**.
- Adaptive security controls are activated.
- Requests to critical endpoints are blocked.
- The application returns **HTTP 403 – Access Denied**.

---

## Actual Result

After the adaptive risk engine classified the session as **ATTACKER**, subsequent requests to protected endpoints were automatically denied.

The framework successfully prevented access to sensitive resources by returning an HTTP 403 response with an **Access Denied** message, demonstrating adaptive protection of critical application assets.

### API Response

```json
{
  "message": "Access Denied 🚫"
}
```

---

## Evidence

### Protected Endpoint Response

![TC-04 Access Denied](screenshots/TC04_AccessDenied.png)

---

## Result

✅ PASS


# TC-05 – Real-Time Security Dashboard Monitoring

## Objective

Validate that the Security Operations Dashboard continuously reflects user activity, cumulative risk scores, threat status, and security events in real time.

---

## Test Steps

1. Launch the Security Operations Dashboard.
2. Perform various user actions through the Banking Control Panel.
3. Observe the dashboard while requests are processed.
4. Verify that dashboard metrics and activity logs update automatically without refreshing the page.

---

## Expected Result

- Active user count updates automatically.
- User request count increases in real time.
- Risk score changes based on user behaviour.
- User classification changes dynamically (NORMAL → SUSPICIOUS → ATTACKER).
- Threat counter updates immediately after attacker detection.
- Live security events are displayed in the activity log.

---

## Actual Result

The Security Operations Dashboard continuously monitored application activity and updated all security metrics automatically.

During validation, the dashboard successfully displayed:

- Active user count
- Total processed requests
- Dynamic cumulative risk score
- User classification
- Threat count
- Live attack notifications
- Overall system security status

All dashboard components refreshed automatically without requiring manual page reloads.

---

## Evidence

### Live Dashboard

![TC-05 Dashboard](screenshots/TC05_Dashboard.png)

### Real-Time Activity Log

![TC-05 Activity Log](screenshots/TC05_LiveLogs.png)

---

## Result

✅ PASS

# Validation Summary

| Test ID | Description | Status |
|---------|-------------|--------|
| TC-01 | Normal User Behaviour | ✅ PASS |
| TC-02 | Suspicious Behaviour Detection | ✅ PASS |
| TC-03 | Attacker Detection & Access Restriction | ✅ PASS |
| TC-04 | Critical Asset Detection | ✅ PASS |
| TC-05 | Security Dashboard Monitoring | ✅ PASS |
