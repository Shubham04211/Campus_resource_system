"""
Configuration and Operational Settings for Campus Resource System.
"""

import os
from datetime import time

# Operating hours for campus facility booking
CAMPUS_OPEN_TIME = time(8, 0)    # 08:00 AM
CAMPUS_CLOSE_TIME = time(20, 0)  # 08:00 PM

# Maximum booking duration allowed per single session (in hours)
MAX_BOOKING_HOURS_STUDENT = 3
MAX_BOOKING_HOURS_FACULTY = 8

# Resource categories supported on campus
RESOURCE_CATEGORIES = {
    "AUDITORIUM": "Large capacity hall for events and seminars",
    "SEMINAR_HALL": "Medium capacity hall with AV projection",
    "COMPUTER_LAB": "Lab equipped with desktop workstations",
    "MEETING_ROOM": "Discussion room for faculty or project teams",
    "PROJECTOR_KIT": "Portable audio-visual equipment"
}

# Role-based permissions matrix
ROLE_PERMISSIONS = {
    "STUDENT": ["MEETING_ROOM", "COMPUTER_LAB", "PROJECTOR_KIT"],
    "FACULTY": ["AUDITORIUM", "SEMINAR_HALL", "COMPUTER_LAB", "MEETING_ROOM", "PROJECTOR_KIT"],
    "ADMIN": ["AUDITORIUM", "SEMINAR_HALL", "COMPUTER_LAB", "MEETING_ROOM", "PROJECTOR_KIT"]
}

# Persistence file path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STORAGE_FILE = os.path.join(DATA_DIR, "system_state.json")
