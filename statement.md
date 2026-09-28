# Project Statement & System Scope
**Project Title**: Campus Space & Resource Allocation System  
**Course Context**: VITyarthi Flipped Course Evaluation  
**Author**: Student Project Submission (Problem Solving)

---

## 1. Problem Statement
Educational campuses manage numerous shared resources including auditoriums, seminar halls, computer laboratories, discussion rooms, and portable audio-visual equipment. Traditional resource allocation methods (such as paper logs, localized spreadsheets, or uncoordinated email requests) suffer from critical operational flaws:
1. **Schedule Overlaps & Double-Booking**: Simultaneous requests for the same room or equipment result in scheduling conflicts and event delays.
2. **Unauthorized Category Access**: Students or unauthorized personnel reserving specialized high-capacity venues (e.g., Grand Auditoriums) without departmental approval.
3. **Lack of Operational Visibility**: Facility managers lack real-time metrics on venue utilization rates, peak usage hours, and departmental allocation trends.
4. **Unregulated Reservation Lengths**: Absence of strict duration caps leads to monopolization of key study spaces and computer labs.

---

## 2. Scope of the Project
The **Campus Space & Resource Allocation System** is a modular Python application designed to automate, validate, and analyze venue and resource reservations across campus facilities. 

### In-Scope Features:
- **Role-Based Access Control (RBAC)**: Differential permissions for `STUDENT`, `FACULTY`, and `ADMIN` roles across 5 distinct resource categories.
- **Interval Overlap & Conflict Engine**: Algorithmic validation preventing double-booking based on strict interval intersection (`max(start_a, start_b) < min(end_a, end_b)`).
- **Policy Enforcement**: Automatic enforcement of operating hours (08:00–20:00) and role-specific duration caps (3 hours for students, 8 hours for faculty).
- **Analytics & Utilization Metrics**: System-wide calculations for peak usage hours, department-level booking distributions, and resource utilization hours.
- **State Persistence**: JSON-based state persistence ensuring zero state loss across application restarts.

### Out-of-Scope (Future Enhancements):
- Multi-campus physical GPS integration.
- Hardware RFID card swipe integration for physical door unlocking.

---

## 3. Target Users & Stakeholders

| User Role | Primary Needs & Workflow |
| :--- | :--- |
| **Students** | Reserve discussion rooms, computer labs, and AV kits for capstone projects and group study sessions within 3-hour caps. |
| **Faculty Members** | Book auditoriums and seminar halls for academic workshops, guest lectures, and department meetings up to 8 hours. |
| **Facility Administrators** | Monitor overall resource utilization, handle emergency cancellations, add new facility inventory, and export analytical reports. |

---

## 4. Key High-Level Features
- **Dynamic Resource Search**: Query available resources filtered by date, time window, and required minimum seat capacity.
- **Reservation Lifecycle Management**: Instant reservation confirmation, owner-driven or admin-driven cancellations, and conflict warnings.
- **Interactive Command-Line Interface**: Clean menu system with built-in validation, error messaging, and seed data loading.
- **Automated Test Suite**: Full `unittest` coverage validating domain models, policy engines, and analytics calculators.
