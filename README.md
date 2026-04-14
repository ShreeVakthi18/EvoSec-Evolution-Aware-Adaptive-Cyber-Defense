# EvoSec – Evolution-Aware Adaptive Cyber Defense

Evolution-aware cybersecurity system that detects attackers by analyzing behavioral changes over time and interaction with critical assets. It dynamically adapts responses using risk scoring, including throttling, verification, and controlled restriction.

---

## Overview

EvoSec is a real-time security monitoring system built using FastAPI. It tracks user API activity, analyzes behavior over time, and assigns dynamic risk scores. Based on risk levels, the system adjusts responses to protect sensitive operations.

A SOC-style dashboard provides real-time visibility into user activity, risk levels, and system state.

---

## Key Features

### Request Monitoring
Captures all incoming API requests using middleware, including endpoints, HTTP methods, and activity data.

### Behavioral Analysis
Tracks user actions over time to identify unusual patterns and deviations.

### Critical Endpoint Detection
Identifies sensitive routes such as admin, delete, and payment endpoints.

### Risk Scoring Engine
Evaluates risk using:
- endpoint sensitivity  
- request frequency  
- behavioral patterns  

### Adaptive Response
- Low risk → normal access  
- Medium risk → delayed or restricted actions  
- High risk → blocked critical operations  

### Real-Time Dashboard
Displays:
- active users  
- risk scores  
- user status  
- live activity logs  

---

## System Workflow

User → API Gateway → Behavior Tracking → Logging → Risk Analysis → Classification → Response → Dashboard

---

## Technology Stack

- Backend: FastAPI  
- Frontend: HTML, CSS, JavaScript  
- Communication: REST APIs  
- Storage: In-memory  

---

## Risk Classification

- 0–2 → Normal  
- 3–5 → Suspicious  
- 6+ → Attacker  

---

## API Endpoints

### User
- `/login`  
- `/search`  
- `/profile`  

### Sensitive
- `/admin/dashboard`  
- `/admin/delete-user`  
- `/payment/transfer`  

### Monitoring
- `/dashboard-data`  

---

## Core Concept

Security decisions are based on behavioral evolution and interaction with critical components, not single requests.

---

## Step-by-Step Architecture

### Step 1: Entry Point  
User → Web App → API Gateway  

<img src="https://github.com/user-attachments/assets/eb510143-85f3-4890-9feb-b24e78071c3c" width="400"/>

---

### Step 2: Behavior Tracking  
API Gateway → Request Handler → Behavior Logs  

<img src="https://github.com/user-attachments/assets/2a5d2f0e-dde5-472a-ba50-78c27080021a" width="500"/>

---

### Step 3: Risk Analysis  
Behavior Logs → Risk Engine → Classifier  

<img src="https://github.com/user-attachments/assets/2df03920-daad-436b-9da0-850519f06b3b" width="500"/>

---

### Step 4: Adaptive Response  
Classifier → Response Engine → API Gateway  

<img src="https://github.com/user-attachments/assets/f0dd8aad-68d4-423f-bec7-a4927bb7fc5c" width="500"/>

---

### Step 5: Monitoring  
Logs → Dashboard  
Classifier → Dashboard  

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
User accesses common endpoints with stable behavior. No risk detected.

**Flow:**  
User → API → Tracking → Analysis → Normal  

**Dashboard**

<img src="https://github.com/user-attachments/assets/2204e120-b6ed-4e7f-bb90-4c0b49fadf10" width="800"/>

**Index**

<img src="https://github.com/user-attachments/assets/b9d6bd4b-cf02-4ab7-b7e4-6381bf0f9831" width="800"/>

---

### Suspicious User
User shows unusual patterns such as repeated or sensitive access.

**Flow:**  
User → API → Tracking → Analysis → Suspicious  

**Dashboard**

<img src="https://github.com/user-attachments/assets/d76d034b-0163-4e26-8795-66dba5ecb6c3" width="800"/>

**Index**

<img src="https://github.com/user-attachments/assets/de46235b-c823-4b14-85b6-d9e8b90a02e7" width="800"/>

---

### Attacker
User repeatedly accesses critical endpoints or performs high-risk actions.

**Flow:**  
User → API → Tracking → Analysis → Attacker → Blocked  

**Dashboard**

<img src="https://github.com/user-attachments/assets/61394294-038e-46c7-b0b1-8904f3ba0b53" width="800"/>

**Index**

<img src="https://github.com/user-attachments/assets/8866af98-12d8-49b3-82be-71f38f1cb12f" width="800"/>

---

## Project Highlights

- Real-time API monitoring  
- Behavior-based anomaly detection  
- Risk scoring system  
- Adaptive response control  
- SOC-style dashboard  

---

## Future Improvements

- JWT-based user identity  
- Time-based anomaly detection  
- Machine learning risk scoring  
- Database integration  
- Deception / honeypot environment  

---

## Author

This project demonstrates adaptive cybersecurity, behavioral analysis, and real-time monitoring concepts.
