# Evolution-Aware Adaptive Cyber Defense (EAACD)

## Validation Test Plan

This document defines the functional validation scenarios used to verify the core security capabilities of the Evolution-Aware Adaptive Cyber Defense (EAACD) framework.

| Test ID | Test Scenario | Expected Result |
|---------|---------------|-----------------|
| TC-01 | Normal User Behaviour | User remains classified as NORMAL with low risk score. |
| TC-02 | Suspicious Behaviour Detection | User risk increases and is classified as SUSPICIOUS with adaptive response delay. |
| TC-03 | Attacker Detection & Access Restriction | User classified as ATTACKER and critical endpoint access is denied (HTTP 403). |
| TC-04 | Critical Asset Detection | Access to automatically identified critical endpoints increases cumulative risk score. |
| TC-05 | Security Dashboard Monitoring | Dashboard updates request count, risk score, threat status, and activity logs in real time. |
