# Campus Space & Resource Allocation System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)


> **VITyarthi Flipped Course Project Submission**  
> A modular, policy-enforced Python platform for managing campus facilities, resolving scheduling conflicts, and analyzing resource utilization.

---

##  Project Overview
Educational institutions require transparent, conflict-free management of shared spaces (auditoriums, labs, meeting rooms) and physical assets (AV kits, projectors). This project delivers an end-to-end allocation engine that prevents double-booking, enforces role-based security policies, and provides detailed utilization analytics for facility managers.

---

##  Key Features
- **Conflict-Free Engine**: Mathematical interval intersection checks prevent scheduling overlaps.
-  **Role-Based Access Control**:
  - `STUDENT`: Access to Meeting Rooms, Computer Labs, Projector Kits (Max 3 hours/booking).
  - `FACULTY`: Access to Auditoriums, Seminar Halls, Labs, Meeting Rooms (Max 8 hours/booking).
  - `ADMIN`: Full system access and cancellation overrides.
- 🕒 **Campus Operating Hours**: Automated enforcement of operational windows (08:00 - 20:00).
- 📊 **Utilization Analytics**: Peak booking hour reports, departmental usage breakdown, and total reserved hours.
- 💾 **State Persistence**: Automatic JSON state saving/restoration.
- 🧪 **Automated Unit Testing**: Comprehensive test suite using Python's native `unittest` framework.

---

##  Technology Stack & Dependencies
- **Language**: Python 3.8+
- **Core Libraries**: `datetime`, `json`, `uuid`, `unittest`, `collections`
- **Report Generation**: `reportlab` / `fpdf2`, `matplotlib`

---

##  Installation & Execution Guide

### 1. Prerequisites
Ensure Python 3.8 or higher is installed on your system.

### 2. Setup
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/Shubham04211/Campus_resource_system.git
cd Campus_resource_system
```

Install dependencies (for PDF report and charting tools):
```bash
pip install -r requirements.txt
```
### 3. Run the Application
Start the interactive command-line application:
```bash
PYTHONPATH=. python3 app/cli_interface.py
```

---

## Testing Instructions

Run the automated test suite to verify system integrity and conflict engine logic:
```bash
PYTHONPATH=. python3 -m unittest discover -s tests
```

### Expected Output:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.028s

OK
```

---

## 📂 Project Repository Structure
```text
campus_resource_system/
├── statement.md                  # Problem statement, scope, target users & features
├── README.md                     # Setup, execution guide & technical specifications
├── requirements.txt              # Project dependencies
├── app/                          # Core application package
│   ├── __init__.py               # Package metadata
│   ├── config.py                 # System constants, categories & permissions
│   ├── models.py                 # Domain models (User, Resource, Booking, TimeSlot)
│   ├── booking_engine.py         # Conflict resolution & booking validation engine
│   ├── analytics.py              # Facility usage metrics & peak hour analysis
│   └── cli_interface.py          # Interactive console driver & seed data loader
├── tests/                        # Unit testing suite
│   ├── __init__.py
│   └── test_booking_engine.py    # Automated test cases
├── diagrams/                     # Text-based visual architecture diagrams
│   └── architecture_flow.txt     # System flow & module interactions
└── Campus_Resource_System_Report.pdf  # Comprehensive 15-Section PDF Project Report
```

---

## 📜 License & Compliance
Submitted in fulfillment of the **VITyarthi Build Your Own Project** flipped course evaluation guidelines. All code and documentation adhere strictly to academic integrity expectations.
