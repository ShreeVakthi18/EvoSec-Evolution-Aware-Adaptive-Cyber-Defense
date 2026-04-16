# EvoSec – Evolution-Aware Adaptive Cyber Defense

## Why this project was built

Most traditional security systems analyze requests in isolation and make decisions based on single events. This approach works for obvious attacks, but it fails to capture how real attackers behave over time.

In practice, attackers do not begin with clearly malicious actions. They often start by behaving like normal users, exploring the system gradually before attempting to access sensitive functionality. Because of this, early-stage attackers appear harmless, while detection at later stages may come too late.

This project was built to address that gap by focusing on how user behavior evolves rather than evaluating requests independently.

---

## Overview

EvoSec is a real-time security monitoring system developed using FastAPI. It continuously tracks user interactions with APIs, builds a behavioral history, and updates a dynamic risk score based on how that behavior changes over time.

Instead of reacting to individual requests, the system evaluates patterns, trends, and movement toward critical endpoints. Based on this evolving context, it adjusts how the system responds to each user.

A lightweight dashboard is included to visualize user activity, risk levels, and system decisions in real time.

---

## What the system does

The system observes user behavior across multiple requests and continuously evaluates whether that behavior remains consistent or starts to deviate.

It considers factors such as:
- how frequently a user makes requests  
- which endpoints they access  
- whether they begin interacting with sensitive parts of the system  

Rather than making immediate decisions, the system gradually builds confidence before classifying a user as normal, suspicious, or high risk.

---

## How it works internally

When a request is received, it is first intercepted by middleware, where key information such as the endpoint, request method, timestamp, and user identifier is collected.

This information is then appended to the user’s activity history. The system analyzes this history to determine whether the user’s behavior is changing compared to previous actions.

At this stage, the system evaluates multiple aspects:
- whether the user is accessing new or unusual endpoints  
- whether request frequency is increasing  
- whether there is movement toward critical endpoints such as admin or payment APIs  

Based on these observations, a risk score is updated incrementally. The system does not make sudden decisions; instead, it allows behavior to accumulate and reveal patterns.

Once the risk score crosses certain thresholds, the system adjusts its response accordingly.

---

## Adaptive response model

The system responds differently depending on the calculated risk level.

- When the risk is low, the user experiences normal system behavior.  
- When the risk becomes moderate, the system introduces slight delays to slow down interaction and observe further behavior.  
- When the risk becomes high, access to sensitive endpoints is restricted to prevent potential damage.  

This approach reduces false positives while still allowing the system to react before an attack fully develops.

---

## Key Features

### Request Monitoring  
All incoming API requests are captured using middleware, ensuring that no interaction goes unnoticed.

### Behavioral Tracking  
Each user’s actions are stored as a sequence, allowing the system to understand how behavior evolves over time.

### Critical Endpoint Awareness  
Sensitive routes such as admin, delete, and payment-related APIs are identified and treated with higher importance.

### Risk Scoring Engine  
The system computes a dynamic risk score based on behavioral changes, endpoint sensitivity, and request patterns.

### Adaptive Response System  
Instead of applying a single rule, the system adjusts its response dynamically based on the user’s risk level.

### Real-Time Dashboard  
A dashboard provides visibility into user activity, classification, and system decisions as they happen.

---

## System Workflow

The overall system flow can be summarized as follows:

User → API Gateway → Request Capture → Behavior Tracking → Risk Evaluation → Classification → Adaptive Response → Dashboard

---

## Technology Stack

- Backend: FastAPI  
- Frontend: HTML, CSS, JavaScript  
- Communication: REST APIs  
- Storage: In-memory tracking for fast processing  

---

## API Endpoints

### Public/User Endpoints
- `/login`  
- `/search`  
- `/profile`  

### Sensitive Endpoints
- `/admin/dashboard`  
- `/admin/delete-user`  
- `/payment/transfer`  

### Monitoring Endpoint
- `/dashboard-data`  

---

## Core Concept

The system focuses on understanding how user behavior changes over time. Instead of analyzing isolated actions, it evaluates the direction in which a user’s activity is moving and responds before that behavior becomes harmful.

---

## Step-by-Step Architecture

### Step 1: Entry Point  
User → Web Application → API Gateway  

<img src="https://github.com/user-attachments/assets/eb510143-85f3-4890-9feb-b24e78071c3c" width="400"/>

---

### Step 2: Behavior Tracking  
API Gateway → Request Handler → Behavioral History Store  

<img src="https://github.com/user-attachments/assets/2a5d2f0e-dde5-472a-ba50-78c27080021a" width="500"/>

---

### Step 3: Risk Analysis  
Behavior History → Risk Engine → Classification Layer  

<img src="https://github.com/user-attachments/assets/2df03920-daad-436b-9da0-850519f06b3b" width="500"/>

---

### Step 4: Adaptive Response  
Classification → Response Engine → API Gateway Control  

<img src="https://github.com/user-attachments/assets/f0dd8aad-68d4-423f-bec7-a4927bb7fc5c" width="500"/>

---

### Step 5: Monitoring Layer  
Logs and classification results are visualized through the SOC-style dashboard.  

<img src="https://github.com/user-attachments/assets/f9c2e52b-adc1-4233-9a36-d178d2d6fbd7" width="450"/>

---

## Final Architecture

<img src="https://github.com/user-attachments/assets/e22ce21e-d392-47da-a0e3-7e19959d3bbe" width="800"/>

---

## Behavior Scenarios

### Normal User  
The user follows consistent patterns and interacts only with common endpoints.

### Suspicious User  
The user begins to show deviations, such as unusual navigation or occasional access to sensitive APIs.

### High-Risk User  
The user repeatedly targets critical endpoints and demonstrates clear abnormal behavior.

---

## Project Highlights

- Continuous behavior tracking across requests  
- Detection of gradual transition from normal to malicious activity  
- Awareness of critical system components  
- Adaptive response instead of static blocking  
- Real-time monitoring through dashboard  

---

## Future Improvements

- Integration of persistent storage for long-term tracking  
- Authentication-based user identification (JWT/session)  
- More advanced scoring techniques  
- Addition of deception mechanisms such as honeypot endpoints  

---

## Author

This project was developed to explore how behavioral analysis can improve real-time security systems by detecting threats as they evolve rather than after they occur.
