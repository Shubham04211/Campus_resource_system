"""
Core Domain Models: User, Resource, Booking, and TimeSlot.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid


class User:
    """Represents a campus member requesting or managing facility access."""

    def __init__(self, user_id: str, name: str, email: str, role: str, department: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role.upper()
        self.department = department

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "department": self.department
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            role=data["role"],
            department=data["department"]
        )


class Resource:
    """Represents a physical space or piece of campus equipment."""

    def __init__(self, resource_id: str, name: str, category: str, capacity: int, location: str, is_active: bool = True):
        self.resource_id = resource_id
        self.name = name
        self.category = category.upper()
        self.capacity = capacity
        self.location = location
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "category": self.category,
            "capacity": self.capacity,
            "location": self.location,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        return cls(
            resource_id=data["resource_id"],
            name=data["name"],
            category=data["category"],
            capacity=data["capacity"],
            location=data["location"],
            is_active=data.get("is_active", True)
        )


class TimeSlot:
    """Encapsulates start and end timestamps and validates interval sanity."""

    def __init__(self, start_time: datetime, end_time: datetime):
        if end_time <= start_time:
            raise ValueError("Booking end time must be strictly after start time.")
        self.start_time = start_time
        self.end_time = end_time

    @property
    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600.0

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Determines if two time intervals overlap (strictly inclusive boundary test)."""
        return max(self.start_time, other.start_time) < min(self.end_time, other.end_time)

    def to_dict(self) -> Dict[str, str]:
        return {
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M")
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'TimeSlot':
        start = datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M")
        end = datetime.strptime(data["end_time"], "%Y-%m-%d %H:%M")
        return cls(start, end)


class Booking:
    """Represents a scheduled reservation of a resource by a user."""

    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"

    def __init__(self, booking_id: str, user_id: str, resource_id: str, time_slot: TimeSlot, purpose: str, status: str = STATUS_CONFIRMED):
        self.booking_id = booking_id
        self.user_id = user_id
        self.resource_id = resource_id
        self.time_slot = time_slot
        self.purpose = purpose
        self.status = status
        self.created_at = datetime.now()

    def cancel(self):
        self.status = self.STATUS_CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "time_slot": self.time_slot.to_dict(),
            "purpose": self.purpose,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Booking':
        b = cls(
            booking_id=data["booking_id"],
            user_id=data["user_id"],
            resource_id=data["resource_id"],
            time_slot=TimeSlot.from_dict(data["time_slot"]),
            purpose=data["purpose"],
            status=data["status"]
        )
        if "created_at" in data:
            b.created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")
        return b
