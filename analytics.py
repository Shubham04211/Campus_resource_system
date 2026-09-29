"""
Analytics Module: Computes capacity metrics, usage trends, and operational statistics.
"""

from typing import Dict, Any, List
from collections import defaultdict

from app.models import Booking
from app.booking_engine import BookingEngine


class ResourceAnalytics:
    """Generates utilization metrics and operational summary reports for resource managers."""

    def __init__(self, engine: BookingEngine):
        self.engine = engine

    def get_resource_utilization_stats(self) -> List[Dict[str, Any]]:
        """Calculates total confirmed bookings, total reserved hours, and average booking length per resource."""
        stats = []

        for res_id, res in self.engine.resources.items():
            confirmed_bookings = [
                b for b in self.engine.bookings.values()
                if b.resource_id == res_id and b.status == Booking.STATUS_CONFIRMED
            ]

            total_hours = sum(b.time_slot.duration_hours for b in confirmed_bookings)
            count = len(confirmed_bookings)
            avg_duration = (total_hours / count) if count > 0 else 0.0

            stats.append({
                "resource_id": res_id,
                "name": res.name,
                "category": res.category,
                "capacity": res.capacity,
                "total_bookings": count,
                "total_hours_reserved": round(total_hours, 2),
                "avg_booking_hours": round(avg_duration, 2)
            })

        return sorted(stats, key=lambda x: x["total_hours_reserved"], reverse=True)

    def get_peak_booking_hours(self) -> Dict[int, int]:
        """Analyzes active bookings to identify peak operational hours (08:00 - 20:00)."""
        hourly_counts: Dict[int, int] = defaultdict(int)

        for booking in self.engine.bookings.values():
            if booking.status != Booking.STATUS_CONFIRMED:
                continue

            start_hour = booking.time_slot.start_time.hour
            end_hour = booking.time_slot.end_time.hour

            for hour in range(start_hour, end_hour):
                hourly_counts[hour] += 1

        return dict(sorted(hourly_counts.items()))

    def get_department_usage_summary(self) -> Dict[str, int]:
        """Aggregates confirmed booking counts broken down by academic department."""
        dept_counts: Dict[str, int] = defaultdict(int)

        for booking in self.engine.bookings.values():
            if booking.status != Booking.STATUS_CONFIRMED:
                continue

            user = self.engine.users.get(booking.user_id)
            dept = user.department if user else "UNKNOWN"
            dept_counts[dept] += 1

        return dict(dept_counts)
