# Copyright (C) 2025 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrLeavePublicHolidayDays(TransactionCase):
    """Regression tests for the public-holiday count the leave report relies on."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Leave = cls.env["hr.leave"]
        cls.Holiday = cls.env["calendar.public.holiday"]
        cls.HolidayLine = cls.env["calendar.public.holiday.line"]
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Ethiopian Leave Employee"}
        )
        cls.leave_type = cls.env["hr.leave.type"].create(
            {"name": "Public Holiday Test", "requires_allocation": False}
        )
        cls.public_holiday = cls.Holiday.create({"year": 2026})

    def _add_holiday(self, day):
        return self.HolidayLine.create(
            {
                "name": "Test holiday",
                "date": fields.Date.to_date(day),
                "public_holiday_id": self.public_holiday.id,
            }
        )

    def _leave(self, request_from, request_to):
        return self.Leave.create(
            {
                "name": "Public holiday probe",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": fields.Date.to_date(request_from),
                "request_date_to": fields.Date.to_date(request_to),
            }
        )

    def test_last_day_holiday_is_counted(self):
        """A holiday falling on the last day of the leave must be counted."""
        self._add_holiday("2026-03-05")
        leave = self._leave("2026-03-05", "2026-03-05")
        self.assertEqual(
            leave.public_holiday_days,
            1.0,
            "A single-day leave that falls on a public holiday must count it",
        )

    def test_holiday_count_is_recomputed_when_dates_change(self):
        """Moving the leave to dates with another holiday count must refresh it."""
        self._add_holiday("2026-03-05")
        leave = self._leave("2026-03-02", "2026-03-04")
        self.assertEqual(leave.public_holiday_days, 0.0)
        leave.write(
            {
                "request_date_from": fields.Date.to_date("2026-03-04"),
                "request_date_to": fields.Date.to_date("2026-03-06"),
            }
        )
        self.assertEqual(
            leave.public_holiday_days,
            1.0,
            "The stored count must be recomputed when the leave dates change",
        )


@tagged("post_install", "-at_install")
class TestAvailableLeaveDays(TransactionCase):
    """The balance on an application only counts allocations valid for the request."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Leave = cls.env["hr.leave"]
        cls.Allocation = cls.env["hr.leave.allocation"]
        cls.employee = cls.env["hr.employee"].create({"name": "Balance Employee"})
        cls.leave_type = cls.env["hr.leave.type"].create(
            {"name": "Balance Test", "requires_allocation": True}
        )

    def _allocation(self, days, date_from, date_to):
        # In 19.0 an allocation must be created in the 'confirm' state and then
        # approved; creating it directly as 'validate' raises a UserError.
        allocation = self.Allocation.create(
            {
                "name": "Balance allocation",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "number_of_days": days,
                "date_from": fields.Date.to_date(date_from),
                "date_to": fields.Date.to_date(date_to),
                "state": "confirm",
            }
        )
        allocation.action_approve()
        return allocation

    def _leave(self, request_from, request_to):
        return self.Leave.create(
            {
                "name": "Balance probe",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": fields.Date.to_date(request_from),
                "request_date_to": fields.Date.to_date(request_to),
            }
        )

    def test_expired_allocation_is_not_available(self):
        """An allocation that expired before the request must not be counted."""
        self._allocation(10, "2025-01-01", "2025-12-31")
        self._allocation(5, "2026-01-01", "2026-12-31")

        leave = self._leave("2026-03-02", "2026-03-04")

        self.assertEqual(
            leave.available_leave_days,
            5.0,
            "Only the allocation that covers the requested days is available",
        )

    def test_future_allocation_is_not_available(self):
        """An allocation that has not started yet must not be counted."""
        self._allocation(5, "2026-01-01", "2026-12-31")
        self._allocation(7, "2026-06-01", "2026-12-31")

        leave = self._leave("2026-03-02", "2026-03-04")

        self.assertEqual(
            leave.available_leave_days,
            5.0,
            "An allocation starting after the request is not available",
        )

    def test_taken_days_are_subtracted(self):
        """What was already taken from the allocation is not available."""
        self._allocation(10, "2026-01-01", "2026-12-31")
        taken = self._leave("2026-02-02", "2026-02-03")
        taken.action_approve()

        leave = self._leave("2026-03-02", "2026-03-04")

        self.assertEqual(
            leave.available_leave_days,
            8.0,
            "The two days already taken must not be available again",
        )

    def test_type_without_allocation_reports_nothing(self):
        """A type that needs no allocation keeps the report's blank figures."""
        # requires_allocation defaults to True in 19.0: a type that needs no
        # allocation has to say so, or creating the leave below is refused.
        leave_type = self.env["hr.leave.type"].create(
            {"name": "No Allocation", "requires_allocation": False}
        )
        leave = self.Leave.create(
            {
                "name": "No allocation probe",
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "request_date_from": fields.Date.to_date("2026-03-02"),
                "request_date_to": fields.Date.to_date("2026-03-04"),
            }
        )

        self.assertEqual(leave.get_remaining_leaves(leave), "")
        self.assertEqual(leave.get_taken_leaves(leave), "")


@tagged("post_install", "-at_install")
class TestHolidayDaysTimeZone(TransactionCase):
    """A holiday is a calendar day in the employee's time zone, not in UTC."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Leave = cls.env["hr.leave"]
        cls.Holiday = cls.env["calendar.public.holiday"]
        cls.HolidayLine = cls.env["calendar.public.holiday.line"]
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Kiritimati Employee", "tz": "Pacific/Kiritimati"}
        )
        cls.leave_type = cls.env["hr.leave.type"].create(
            {"name": "Time zone Test", "requires_allocation": False}
        )
        cls.public_holiday = cls.Holiday.create({"year": 2026})

    def test_holiday_before_the_request_is_not_counted(self):
        """An 08:00 start in UTC+14 is the previous day in UTC: the holiday that
        sits on that UTC day is not part of the request."""
        self.HolidayLine.create(
            {
                "name": "Test holiday",
                "date": fields.Date.to_date("2026-03-04"),
                "public_holiday_id": self.public_holiday.id,
            }
        )
        leave = self.Leave.create(
            {
                "name": "Time zone probe",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": fields.Date.to_date("2026-03-05"),
                "request_date_to": fields.Date.to_date("2026-03-05"),
            }
        )

        self.assertEqual(
            leave.date_from.strftime("%Y-%m-%d"),
            "2026-03-04",
            "premise: the UTC start of a UTC+14 request is the previous day",
        )
        self.assertEqual(
            leave.public_holiday_days,
            0.0,
            "A holiday on the UTC day before the request must not be counted",
        )
