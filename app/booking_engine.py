"""
Booking Engine: Handles business rules, conflict resolution, and reservation lifecycles.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, time
import uuid
import json
import os

from app.models import User, Resource, Booking, TimeSlot
from app.config import (
    CAMPUS_OPEN_TIME, CAMPUS_CLOSE_TIME,
    MAX_BOOKING_HOURS_STUDENT, MAX_BOOKING_HOURS_FACULTY,
    ROLE_PERMISSIONS, RESOURCE_CATEGORIES, STORAGE_FILE
)


class BookingEngine:
    """Manages system state, enforces policy rules, and prevents scheduling conflicts."""

    def __init__(self, storage_path: str = STORAGE_FILE):
        self.storage_path = storage_path
        self.users: Dict[str, User] = {}
        self.resources: Dict[str, Resource] = {}
        self.bookings: Dict[str, Booking] = {}

    def add_user(self, user: User) -> bool:
        if user.user_id in self.users:
            return False
        self.users[user.user_id] = user
        return True

    def add_resource(self, resource: Resource) -> bool:
        if resource.resource_id in self.resources:
            return False
        if resource.category not in RESOURCE_CATEGORIES:
            raise ValueError(f"Invalid resource category: {resource.category}")
        self.resources[resource.resource_id] = resource
        return True

    def validate_booking_request(self, user_id: str, resource_id: str, time_slot: TimeSlot) -> Tuple[bool, str]:
        """Runs validation pipeline: User Existence -> Role Authorization -> Duration -> Operating Hours -> Overlap Conflict."""
        # 1. User check
        if user_id not in self.users:
            return False, f"User ID '{user_id}' not registered in the system."
        user = self.users[user_id]

        # 2. Resource check
        if resource_id not in self.resources:
            return False, f"Resource ID '{resource_id}' does not exist."
        resource = self.resources[resource_id]

        if not resource.is_active:
            return False, f"Resource '{resource.name}' is currently offline/under maintenance."

        # 3. Role-based category access check
        allowed_categories = ROLE_PERMISSIONS.get(user.role, [])
        if resource.category not in allowed_categories:
            return False, f"Role '{user.role}' is not authorized to reserve '{resource.category}' resources."

        # 4. Duration cap enforcement
        duration = time_slot.duration_hours
        max_duration = MAX_BOOKING_HOURS_FACULTY if user.role in ["FACULTY", "ADMIN"] else MAX_BOOKING_HOURS_STUDENT
        if duration > max_duration:
            return False, f"Requested duration ({duration:.1f}h) exceeds maximum permitted limit ({max_duration}h) for role '{user.role}'."

        # 5. Operating hours check
        if time_slot.start_time.time() < CAMPUS_OPEN_TIME or time_slot.end_time.time() > CAMPUS_CLOSE_TIME:
            return False, f"Booking window must be within campus operating hours ({CAMPUS_OPEN_TIME.strftime('%H:%M')} - {CAMPUS_CLOSE_TIME.strftime('%H:%M')})."

        # 6. Check interval conflicts against existing confirmed bookings
        conflict = self.find_conflicting_booking(resource_id, time_slot)
        if conflict:
            return False, f"Schedule conflict with existing booking '{conflict.booking_id}' ({conflict.time_slot.start_time.strftime('%H:%M')} - {conflict.time_slot.end_time.strftime('%H:%M')})."

        return True, "Request is valid."

    def find_conflicting_booking(self, resource_id: str, time_slot: TimeSlot) -> Optional[Booking]:
        """Scans active bookings for temporal overlaps."""
        for booking in self.bookings.values():
            if booking.resource_id == resource_id and booking.status == Booking.STATUS_CONFIRMED:
                if booking.time_slot.overlaps_with(time_slot):
                    return booking
        return None

    def create_booking(self, user_id: str, resource_id: str, start_time: datetime, end_time: datetime, purpose: str) -> Booking:
        """Executes a validated booking request and records it."""
        slot = TimeSlot(start_time, end_time)
        is_valid, msg = self.validate_booking_request(user_id, resource_id, slot)
        if not is_valid:
            raise ValueError(f"Booking Failed: {msg}")

        booking_id = f"BKG-{uuid.uuid4().hex[:6].upper()}"
        new_booking = Booking(booking_id, user_id, resource_id, slot, purpose)
        self.bookings[booking_id] = new_booking
        return new_booking

    def cancel_booking(self, booking_id: str, requesting_user_id: str) -> bool:
        """Cancels a booking if requested by the owner or an admin."""
        if booking_id not in self.bookings:
            raise KeyError(f"Booking ID '{booking_id}' not found.")

        booking = self.bookings[booking_id]
        requesting_user = self.users.get(requesting_user_id)

        if not requesting_user:
            raise ValueError("Invalid requesting user.")

        # Allow owner or admin to cancel
        if booking.user_id != requesting_user_id and requesting_user.role != "ADMIN":
            raise PermissionError("Only the booking owner or an administrator can cancel this reservation.")

        if booking.status == Booking.STATUS_CANCELLED:
            return False  # Already cancelled

        booking.cancel()
        return True

    def get_available_resources(self, category: Optional[str], start_time: datetime, end_time: datetime, min_capacity: int = 0) -> List[Resource]:
        """Returns resources matching criteria that have no scheduling conflicts during the requested slot."""
        slot = TimeSlot(start_time, end_time)
        available = []

        for res in self.resources.values():
            if not res.is_active or res.capacity < min_capacity:
                continue
            if category and res.category != category.upper():
                continue

            # Check if conflict exists
            if not self.find_conflicting_booking(res.resource_id, slot):
                available.append(res)

        return available

    def save_state(self):
        """Persists current users, resources, and bookings to JSON file."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "users": [u.to_dict() for u in self.users.values()],
            "resources": [r.to_dict() for r in self.resources.values()],
            "bookings": [b.to_dict() for b in self.bookings.values()]
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_state(self):
        """Restores state from JSON persistence file if available."""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.users = {u["user_id"]: User.from_dict(u) for u in data.get("users", [])}
            self.resources = {r["resource_id"]: Resource.from_dict(r) for r in data.get("resources", [])}
            self.bookings = {b["booking_id"]: Booking.from_dict(b) for b in data.get("bookings", [])}
        except Exception as e:
            print(f"Warning: Failed to load state from {self.storage_path}: {e}")
