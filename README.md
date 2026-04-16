# EvoSec – Evolution-Aware Adaptive Cyber Defense

> *"A user is not dangerous because of a single action — they are dangerous because of how they evolve, and where they choose to act."*

I built EvoSec because I realized something that most security systems completely ignore — attackers do not announce themselves. They move slowly, blend into normal traffic, and gradually probe deeper until they reach something critical. I wanted to build something that thinks the way a real analyst thinks: watching behavioral evolution, understanding which assets actually matter, and responding with intelligence instead of brute-force blocking.

- This is **not** just a monitoring system.
- This is **not** just a detection system.
- EvoSec is a system that **understands behavior**, **knows where damage can happen**, and **responds differently based on how much risk has evolved** — including deceiving the attacker when the threat level demands it.

---

## The Problem I Was Solving

- Modern web systems receive millions of API requests every day — it is completely impractical to place a human analyst behind every single one.
- Rule-based systems that look at individual actions in isolation will always miss the attacker who moves carefully and stays just below the detection threshold.
- The real threat is not the user who fires one suspicious request — it is the user whose behavior gradually drifts from browsing into reconnaissance, and from reconnaissance into targeting the most sensitive parts of the system.
- Most systems treat every endpoint equally, which means they waste processing power monitoring low-value actions while missing the moment an attacker pivots toward a payment route or an admin deletion endpoint.
- Manually labeling which parts of a system are sensitive does not scale — I designed EvoSec to **automatically identify critical assets** so the system builds its own understanding of what matters without requiring manual configuration every time.
- The core insight I encoded into this system is that risk is not about a single request — it is about the **intersection of behavioral evolution and critical asset interaction**.

---

## What I Built and How It Works

### Automatic Critical Asset Detection

- The first thing EvoSec does is build a map of which endpoints are high-value targets — automatically, without any manual labeling.
- Endpoints containing keywords like `admin`, `delete`, or `payment` are immediately flagged as critical based on route structure analysis.
- Beyond name-based detection, the system also identifies routes that are accessed rarely but receive destructive HTTP methods like DELETE or POST — because low-frequency, high-impact interactions are a classic indicator of targeted exploitation rather than casual browsing.
- This means the system always knows where damage can happen, even on routes it has never seen before.

### Behavioral Evolution Tracking

- Every request a user makes is stored in a behavioral history log tied to their identity.
- The system does not just look at what a user is doing right now — it looks at the **full arc of their session**.
- A user who starts at `/login`, moves to `/search`, then `/profile`, and then suddenly jumps directly to `/admin/dashboard` without any intermediate authenticated flow is exhibiting a pattern that looks very different from a genuine administrator.
- EvoSec captures this evolution and uses it as the foundation of its risk computation — something no single-request inspection system can do.

### Dynamic Risk Scoring Engine

- The risk engine combines two signals: how the user's behavior has evolved over time, and which assets they have been interacting with.
- Each interaction with a critical endpoint raises the score.
- Each use of a destructive HTTP method raises it further.
- Accessing administrative routes without passing through a login path triggers an additional penalty.
- Sessions that accumulate an unusually high number of requests receive elevated scores to catch automated probing behavior.
- The score rises continuously as behavior becomes more concerning — meaning the system catches slow, deliberate attackers just as effectively as fast, noisy ones.

### Adaptive Response System

- Instead of treating every user the same way, the system responds differently based on the computed risk level.
- **Low risk** → completely normal access with zero friction applied.
- **Medium risk** → subtle friction introduced — responses are delayed, slowing down automated tools without alerting a human attacker that anything unusual is happening.
- **High risk** → the system does not simply block the user and reveal that they have been detected. Instead, it redirects them to a controlled deception environment where they interact with decoy APIs and fake data while the real system remains completely untouched.
- This lets the system observe attacker behavior safely and gather intelligence without ever exposing real infrastructure.

### Real-Time SOC Dashboard

- The dashboard provides complete, live visibility into everything the system is tracking.
- It displays every active user, their request count, their computed risk score, and their current classification status.
- Attackers are flagged with animated alerts so they are immediately visible at a glance.
- The activity log updates continuously with new user detections and threat events, giving the feel of a live security operations center rather than a static report.

---

## System Workflow

### Step 1: Entry Point

- Every user request enters through the web application and passes through the API gateway.
- EvoSec intercepts it at the middleware layer before any business logic runs.

**Flow:** User → Web Application → API Gateway

<img src="https://github.com/user-attachments/assets/eb510143-85f3-4890-9feb-b24e78071c3c" width="400"/>

---

### Step 2: Behavior Tracking

- The request handler extracts the user identity, the endpoint being accessed, and the HTTP method being used.
- This information is appended to the user's behavioral history in the tracking store.
- Each new request builds on the record of how their session has evolved from the very first action to the current one.

**Flow:** API Gateway → Request Handler → Behavioral History Store

<img src="https://github.com/user-attachments/assets/2a5d2f0e-dde5-472a-ba50-78c27080021a" width="500"/>

---

### Step 3: Risk Analysis

- Once the new action is recorded, the risk engine reads the user's full behavioral history alongside the current map of critical endpoints.
- It evaluates every action in the history against both the critical asset list and the detected pattern of behavioral evolution.
- A user who has only touched safe endpoints with normal methods scores low.
- A user whose history shows a gradual path from normal browsing into critical endpoint access scores progressively higher with every additional concerning action.

**Flow:** Behavior History → Risk Engine → Classification Layer

<img src="https://github.com/user-attachments/assets/2df03920-daad-436b-9da0-850519f06b3b" width="500"/>

---

### Step 4: Adaptive Response

- The classification layer takes the final risk score and decides exactly how to respond.
- A normal user passes through without any modification to their experience.
- A suspicious user experiences delayed responses that slow down automated probing without revealing that anything is happening.
- A high-risk user attempting to reach a critical endpoint is either blocked directly or redirected into the deception layer — while the real system continues operating normally and the attacker has no idea they have been isolated.

**Flow:** Classification → Response Engine → API Gateway Control

<img src="https://github.com/user-attachments/assets/f0dd8aad-68d4-423f-bec7-a4927bb7fc5c" width="500"/>

---

### Step 5: Monitoring Layer

- Every classification decision, every new user detection, and every threat event is streamed to the SOC dashboard in real time.
- The dashboard aggregates all active user data and presents a live view showing exactly who is on the system, what their risk level is, and whether any threats require immediate attention.

**Flow:** Logs + Classification Data → SOC Dashboard

<img src="https://github.com/user-attachments/assets/f9c2e52b-adc1-4233-9a36-d178d2d6fbd7" width="450"/>

---

## Final Architecture

<img src="https://github.com/user-attachments/assets/e22ce21e-d392-47da-a0e3-7e19959d3bbe" width="800"/>

---

## Results

### Index Page

<img src="https://github.com/user-attachments/assets/413873bb-2ddc-4163-905d-f664a4933e45" width="800"/>

---

### Dashboard

<img src="https://github.com/user-attachments/assets/fa85c2e6-8978-4422-9dc8-062e0541737d" width="800"/>

---

## Workflow Scenarios

### Normal User

- Follows a stable, predictable behavioral path with no signs of escalation.
- Accesses only low-sensitivity endpoints using safe HTTP methods throughout the session.
- The risk engine keeps their score at a low level and the system places no restrictions on their access.

**Flow:** User → API → Tracking → Analysis → Normal Access

**Dashboard**

<img src="https://github.com/user-attachments/assets/2204e120-b6ed-4e7f-bb90-4c0b49fadf10" width="800"/>

**Index**

<img src="https://github.com/user-attachments/assets/b9d6bd4b-cf02-4ab7-b7e4-6381bf0f9831" width="800"/>

---

### Suspicious User

- Begins to deviate from normal behavioral patterns — accessing endpoints in an unusual order or using methods that do not match their apparent role.
- Starts probing routes that sit closer to sensitive parts of the system without a legitimate reason to be there.
- The risk engine picks up on this gradual shift and elevates their score into the suspicious range.
- The system responds by introducing friction — slowing down their responses and making automated exploitation harder — without revealing that they are being watched.

**Flow:** User → API → Tracking → Risk Analysis → Suspicious State → Friction Applied

**Dashboard**

<img src="https://github.com/user-attachments/assets/d76d034b-0163-4e26-8795-66dba5ecb6c3" width="800"/>

**Index**

<img src="https://github.com/user-attachments/assets/de46235b-c823-4b14-85b6-d9e8b90a02e7" width="800"/>

---

### High-Risk / Attacker

- Has accumulated enough behavioral signals that the system is confident they represent a genuine threat.
- Their history shows a deliberate escalation toward critical endpoints — actively attempting to reach admin, delete, or payment routes.
- The risk engine raises their score above the attacker threshold.
- The system does not simply block them and reveal that detection has occurred — instead, it routes them into a decoy environment where they interact with fake data and believe they are still inside the real system.
- The actual infrastructure is completely isolated and protected throughout the entire process.

**Flow:** User → API → Tracking → Risk Engine → Attacker Classification → Blocked or Redirected to Deception Layer

**Dashboard**

<img src="https://github.com/user-attachments/assets/61394294-038e-46c7-b0b1-8904f3ba0b53" width="800"/>

**Index**

<img src="https://github.com/user-attachments/assets/8866af98-12d8-49b3-82be-71f38f1cb12f" width="800"/>

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Communication | REST APIs |
| State Storage | In-memory session tracking |

---

## Risk Classification

| Score | Classification | System Response |
|---|---|---|
| 0 – 2 | 🟢 Normal | Full access, no restrictions |
| 3 – 5 | 🟡 Suspicious | Delayed responses, restricted actions |
| 6+ | 🔴 Attacker | Blocked or redirected to deception layer |

---

## API Surface

### Public Endpoints
- `/login` — Standard user login route.
- `/search` — Search functionality.
- `/profile` — User profile access.

### Sensitive Endpoints
- `/admin/dashboard` — Administrative dashboard, flagged as critical.
- `/admin/delete-user` — Destructive admin operation, flagged as critical.
- `/payment/transfer` — Payment operation, flagged as critical.

### Monitoring
- `/dashboard-data` — Feeds the SOC dashboard with live user activity and classification data.

---

## What Makes This Different

- Most intrusion detection systems I have studied react to individual events — they look at one request, check it against a ruleset, and either allow or block it.
- This approach will always fail against a patient attacker who moves slowly and stays just below the detection threshold for each individual action.
- What I built here is fundamentally different because it evaluates the **trajectory of behavior**, not just the current position.
- The combination of behavioral evolution tracking with automatic critical asset detection means the system focuses its intelligence exactly where it matters most — on users who are moving toward the parts of the system where real damage can be done.
- The deception layer means that even when a high-risk user is identified, the system does not immediately reveal that it knows — it creates an opportunity to observe, gather intelligence, and protect real infrastructure without ever putting it at risk.

---

## Future Improvements

- **JWT-based identity tracking** — Replace IP-based tracking so the system follows authenticated sessions accurately even across IP changes.
- **Time-series behavioral modeling** — Understand not just what a user has done but how quickly their behavior is escalating, since speed of escalation is itself a strong threat signal.
- **Machine learning risk scoring** — Allow the system to learn from historical attack data and improve accuracy over time without manual tuning.
- **Persistent database integration** — Allow behavioral history to survive server restarts and enable long-term pattern analysis.
- **Full honeypot environment** — Build out the deception layer into a realistic fake environment with plausible data, so that attackers spend significant time operating inside a controlled sandbox while the real system remains completely untouched.

---

## Project Highlights

- Real-time API behavior monitoring that captures every request as part of a continuous behavioral record.
- Evolution-based anomaly detection that identifies threats invisible to single-request inspection systems.
- Automatic critical asset identification so the system always knows where to focus its attention.
- Adaptive response enforcement that scales from invisible friction all the way to deception-layer isolation.
- SOC-style visualization dashboard that gives complete situational awareness at a glance.

---

## Author

I built EvoSec to demonstrate that behavioral intelligence and adaptive threat response are the right foundations for next-generation cybersecurity systems. The core insight driving this entire project is that security should understand **how threats evolve** — not just react to individual events in isolation. Every design decision in this system, from automatic critical asset detection to the deception-layer response, flows from that single principle.
