"""
Unit Tests for Booking Engine and Conflict Resolution.
"""

import unittest
from datetime import datetime, time, timedelta
import os
import shutil

from app.models import User, Resource, Booking, TimeSlot
from app.booking_engine import BookingEngine
from app.analytics import ResourceAnalytics


class TestBookingEngine(unittest.TestCase):

    def setUp(self):
        # Setup temporary test directory and isolated engine
        self.test_dir = "/workspace/scratch/test_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.storage_file = os.path.join(self.test_dir, "test_state.json")
        self.engine = BookingEngine(storage_path=self.storage_file)

        # Register test entities
        self.student = User("STU001", "Test Student", "stu@vit.edu", "STUDENT", "Computer Science")
        self.faculty = User("FAC001", "Test Faculty", "fac@vit.edu", "FACULTY", "Electronics")
        self.engine.add_user(self.student)
        self.engine.add_user(self.faculty)

        self.lab = Resource("RES-LAB", "CS Lab 1", "COMPUTER_LAB", 30, "SJT 301")
        self.audi = Resource("RES-AUD", "Main Audi", "AUDITORIUM", 500, "SJT Ground")
        self.engine.add_resource(self.lab)
        self.engine.add_resource(self.audi)

        self.today = datetime.now().strftime("%Y-%m-%d")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_valid_booking_creation(self):
        start = datetime.strptime(f"{self.today} 10:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{self.today} 12:00", "%Y-%m-%d %H:%M")
        
        booking = self.engine.create_booking("STU001", "RES-LAB", start, end, "Lab Practice")
        self.assertIsNotNone(booking.booking_id)
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
        self.assertEqual(len(self.engine.bookings), 1)

    def test_schedule_conflict_detection(self):
        start1 = datetime.strptime(f"{self.today} 10:00", "%Y-%m-%d %H:%M")
        end1 = datetime.strptime(f"{self.today} 12:00", "%Y-%m-%d %H:%M")
        self.engine.create_booking("STU001", "RES-LAB", start1, end1, "Lab Session 1")

        # Overlapping slot (11:00 to 13:00)
        start2 = datetime.strptime(f"{self.today} 11:00", "%Y-%m-%d %H:%M")
        end2 = datetime.strptime(f"{self.today} 13:00", "%Y-%m-%d %H:%M")

        with self.assertRaises(ValueError) as ctx:
            self.engine.create_booking("FAC001", "RES-LAB", start2, end2, "Lab Session 2")
        self.assertIn("Schedule conflict", str(ctx.exception))

    def test_role_authorization_enforcement(self):
        start = datetime.strptime(f"{self.today} 10:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{self.today} 12:00", "%Y-%m-%d %H:%M")

        # Student attempting to book Auditorium should fail
        with self.assertRaises(ValueError) as ctx:
            self.engine.create_booking("STU001", "RES-AUD", start, end, "Student Event")
        self.assertIn("not authorized", str(ctx.exception))

        # Faculty attempting to book Auditorium should succeed
        bkg = self.engine.create_booking("FAC001", "RES-AUD", start, end, "Department Seminar")
        self.assertEqual(bkg.status, Booking.STATUS_CONFIRMED)

    def test_duration_limit_enforcement(self):
        start = datetime.strptime(f"{self.today} 09:00", "%Y-%m-%d %H:%M")
        # 5 hours duration (exceeds student 3-hour limit)
        end = datetime.strptime(f"{self.today} 14:00", "%Y-%m-%d %H:%M")

        with self.assertRaises(ValueError) as ctx:
            self.engine.create_booking("STU001", "RES-LAB", start, end, "Marathon Coding")
        self.assertIn("exceeds maximum permitted limit", str(ctx.exception))

    def test_operating_hours_enforcement(self):
        # Booking past 20:00 (8 PM)
        start = datetime.strptime(f"{self.today} 19:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{self.today} 21:00", "%Y-%m-%d %H:%M")

        with self.assertRaises(ValueError) as ctx:
            self.engine.create_booking("FAC001", "RES-AUD", start, end, "Late Night Event")
        self.assertIn("operating hours", str(ctx.exception))

    def test_booking_cancellation(self):
        start = datetime.strptime(f"{self.today} 10:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{self.today} 11:00", "%Y-%m-%d %H:%M")
        bkg = self.engine.create_booking("STU001", "RES-LAB", start, end, "Group Study")

        # Cancel by owner
        success = self.engine.cancel_booking(bkg.booking_id, "STU001")
        self.assertTrue(success)
        self.assertEqual(self.engine.bookings[bkg.booking_id].status, Booking.STATUS_CANCELLED)

        # Slot should now be available again
        bkg2 = self.engine.create_booking("STU001", "RES-LAB", start, end, "Replacement Group Study")
        self.assertEqual(bkg2.status, Booking.STATUS_CONFIRMED)

    def test_analytics_metrics(self):
        start = datetime.strptime(f"{self.today} 10:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{self.today} 12:00", "%Y-%m-%d %H:%M")
        self.engine.create_booking("STU001", "RES-LAB", start, end, "Session 1")

        analytics = ResourceAnalytics(self.engine)
        stats = analytics.get_resource_utilization_stats()
        
        lab_stat = next(s for s in stats if s["resource_id"] == "RES-LAB")
        self.assertEqual(lab_stat["total_bookings"], 1)
        self.assertEqual(lab_stat["total_hours_reserved"], 2.0)


if __name__ == "__main__":
    unittest.main()
