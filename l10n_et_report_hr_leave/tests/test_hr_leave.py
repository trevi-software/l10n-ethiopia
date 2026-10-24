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
