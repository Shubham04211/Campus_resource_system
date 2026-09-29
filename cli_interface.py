"""
CLI Interface: Console driver and menu controller for Campus Resource System.
"""

import sys
from datetime import datetime, timedelta
from typing import Optional

from app.models import User, Resource
from app.booking_engine import BookingEngine
from app.analytics import ResourceAnalytics


def seed_sample_data(engine: BookingEngine):
    """Populates initial sample resources and users if state is uninitialized."""
    if engine.users and engine.resources:
        return

    # Seed Users
    users = [
        User("STU101", "Aarav Sharma", "aarav.s@vit.edu", "STUDENT", "Computer Science"),
        User("STU102", "Priya Patel", "priya.p@vit.edu", "STUDENT", "Electronics"),
        User("FAC201", "Dr. Rajesh Kumar", "rajesh.k@vit.edu", "FACULTY", "Computer Science"),
        User("ADM301", "Admin Control", "admin@vit.edu", "ADMIN", "Facilities Office")
    ]
    for u in users:
        engine.add_user(u)

    # Seed Campus Resources
    resources = [
        Resource("RES-AUD1", "SJT Grand Auditorium", "AUDITORIUM", 300, "SJT Ground Floor"),
        Resource("RES-SEM1", "Newton Hall 201", "SEMINAR_HALL", 80, "TT Building 2nd Floor"),
        Resource("RES-LAB1", "Advanced Software Lab 3", "COMPUTER_LAB", 40, "SJT 4th Floor"),
        Resource("RES-MGT1", "Team Discussion Room A", "MEETING_ROOM", 8, "Library 1st Floor"),
        Resource("RES-AV1", "High-Definition Portable Projector", "PROJECTOR_KIT", 1, "AV Store Room")
    ]
    for r in resources:
        engine.add_resource(r)

    # Seed Sample Bookings for today
    today_str = datetime.now().strftime("%Y-%m-%d")
    s1 = datetime.strptime(f"{today_str} 09:00", "%Y-%m-%d %H:%M")
    e1 = datetime.strptime(f"{today_str} 11:00", "%Y-%m-%d %H:%M")
    engine.create_booking("FAC201", "RES-SEM1", s1, e1, "Guest Lecture on AI Architectures")

    s2 = datetime.strptime(f"{today_str} 14:00", "%Y-%m-%d %H:%M")
    e2 = datetime.strptime(f"{today_str} 16:00", "%Y-%m-%d %H:%M")
    engine.create_booking("STU101", "RES-MGT1", s2, e2, "Capstone Project Sprint Meeting")


class CLIApp:
    def __init__(self):
        self.engine = BookingEngine()
        self.engine.load_state()
        seed_sample_data(self.engine)
        self.analytics = ResourceAnalytics(self.engine)

    def print_header(self):
        print("=" * 65)
        print("    CAMPUS SPACE & RESOURCE ALLOCATION SYSTEM (VITyarthi)")
        print("=" * 65)

    def main_menu(self):
        while True:
            self.print_header()
            print("1. List Available Campus Resources")
            print("2. Search Resources by Capacity & Availability")
            print("3. Create Facility Reservation")
            print("4. View Active Bookings")
            print("5. Cancel Reservation")
            print("6. View System Utilization Analytics")
            print("7. Save & Exit")
            print("-" * 65)

            choice = input("Select an option (1-7): ").strip()

            if choice == "1":
                self.list_resources()
            elif choice == "2":
                self.search_resources()
            elif choice == "3":
                self.make_booking()
            elif choice == "4":
                self.view_bookings()
            elif choice == "5":
                self.cancel_booking()
            elif choice == "6":
                self.view_analytics()
            elif choice == "7":
                self.engine.save_state()
                print("\n[INFO] System state saved successfully. Exiting.")
                break
            else:
                print("\n[ERROR] Invalid choice. Please select 1-7.")

    def list_resources(self):
        print("\n--- REGISTERED CAMPUS RESOURCES ---")
        print(f"{'ID':<10} | {'Name':<28} | {'Category':<14} | {'Cap':<5} | {'Location'}")
        print("-" * 75)
        for r in self.engine.resources.values():
            status = "ACTIVE" if r.is_active else "MAINT"
            print(f"{r.resource_id:<10} | {r.name:<28} | {r.category:<14} | {r.capacity:<5} | {r.location}")
        input("\nPress Enter to return to menu...")

    def search_resources(self):
        print("\n--- SEARCH AVAILABLE RESOURCES ---")
        date_str = input("Enter Date (YYYY-MM-DD) [e.g. 2026-10-01]: ").strip()
        start_str = input("Enter Start Time (HH:MM) [e.g. 10:00]: ").strip()
        end_str = input("Enter End Time (HH:MM) [e.g. 12:00]: ").strip()

        try:
            start_dt = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date_str} {end_str}", "%Y-%m-%d %H:%M")
            
            avail = self.engine.get_available_resources(None, start_dt, end_dt)
            print(f"\n[RESULTS] Found {len(avail)} available resource(s):")
            for r in avail:
                print(f" -> [{r.resource_id}] {r.name} ({r.category}) - Cap: {r.capacity} @ {r.location}")
        except Exception as e:
            print(f"\n[ERROR] Invalid date/time format: {e}")

        input("\nPress Enter to return to menu...")

    def make_booking(self):
        print("\n--- CREATE RESERVATION ---")
        user_id = input("Enter User ID [e.g. STU101, FAC201]: ").strip()
        res_id = input("Enter Resource ID [e.g. RES-MGT1]: ").strip()
        date_str = input("Enter Date (YYYY-MM-DD): ").strip()
        start_str = input("Enter Start Time (HH:MM): ").strip()
        end_str = input("Enter End Time (HH:MM): ").strip()
        purpose = input("Enter Purpose/Event Name: ").strip()

        try:
            start_dt = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date_str} {end_str}", "%Y-%m-%d %H:%M")

            booking = self.engine.create_booking(user_id, res_id, start_dt, end_dt, purpose)
            print(f"\n[SUCCESS] Reservation Confirmed! Booking ID: {booking.booking_id}")
        except Exception as e:
            print(f"\n[FAILURE] {e}")

        input("\nPress Enter to return to menu...")

    def view_bookings(self):
        print("\n--- ACTIVE FACILITY RESERVATIONS ---")
        print(f"{'Booking ID':<12} | {'User ID':<8} | {'Resource':<12} | {'Start Time':<16} | {'End Time':<16} | {'Status'}")
        print("-" * 80)
        for b in self.engine.bookings.values():
            res = self.engine.resources.get(b.resource_id)
            res_name = res.name[:12] if res else b.resource_id
            print(f"{b.booking_id:<12} | {b.user_id:<8} | {res_name:<12} | {b.time_slot.start_time.strftime('%Y-%m-%d %H:%M'):<16} | {b.time_slot.end_time.strftime('%Y-%m-%d %H:%M'):<16} | {b.status}")
        input("\nPress Enter to return to menu...")

    def cancel_booking(self):
        print("\n--- CANCEL RESERVATION ---")
        bkg_id = input("Enter Booking ID: ").strip()
        user_id = input("Enter Requesting User ID: ").strip()

        try:
            success = self.engine.cancel_booking(bkg_id, user_id)
            if success:
                print(f"\n[SUCCESS] Reservation '{bkg_id}' has been cancelled.")
            else:
                print(f"\n[INFO] Reservation '{bkg_id}' was already cancelled.")
        except Exception as e:
            print(f"\n[ERROR] {e}")

        input("\nPress Enter to return to menu...")

    def view_analytics(self):
        print("\n--- UTILIZATION & ANALYTICS REPORT ---")
        stats = self.analytics.get_resource_utilization_stats()
        print(f"\nResource Utilization Breakdown:")
        print(f"{'Resource':<25} | {'Category':<14} | {'Bookings':<8} | {'Total Hours'}")
        print("-" * 65)
        for s in stats:
            print(f"{s['name']:<25} | {s['category']:<14} | {s['total_bookings']:<8} | {s['total_hours_reserved']} hrs")

        peak = self.analytics.get_peak_booking_hours()
        print(f"\nPeak Booking Hours (Hour: Reserved Slots):")
        for h, count in peak.items():
            print(f"  {h:02d}:00 - {h+1:02d}:00 -> {count} slot(s)")

        dept = self.analytics.get_department_usage_summary()
        print(f"\nDepartmental Activity Breakdown:")
        for d, count in dept.items():
            print(f"  {d}: {count} booking(s)")

        input("\nPress Enter to return to menu...")


def main():
    app = CLIApp()
    app.main_menu()


if __name__ == "__main__":
    main()
