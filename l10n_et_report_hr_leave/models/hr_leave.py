# Copyright (C) 2025 Trevi Software (https://trevi.et)
# Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from pytz import UTC, timezone

from odoo import api, fields, models

from odoo.addons.ethiopic_calendar.models.ethiopic_calendar import (
    ET_MONTHS_SELECTION_AM,
)
from odoo.addons.ethiopic_calendar.models.pycalcal import pycalcal as pcc

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = "hr.leave"

    return_date_et = fields.Char("Ethiopic Return Date")

    local_date_from = fields.Datetime(compute="_compute_local_date_from_to")

    local_date_to = fields.Datetime(compute="_compute_local_date_from_to")

    rest_days = fields.Float(
        "Rest (Days)",
        compute="_compute_rest_days",
        store=True,
        readonly=False,
        copy=False,
        tracking=True,
        help="Number of rest days of the time off request",
    )

    public_holiday_days = fields.Float(
        "Public Holiday (Days)",
        compute="_compute_public_holiday_days",
        store=True,
        readonly=False,
        copy=False,
        tracking=True,
        help="Number of public holidays in the time off request",
    )

    real_days = fields.Float(
        "Real (Days)",
        compute="_compute_real_days",
        store=True,
        readonly=False,
        copy=False,
        tracking=True,
        help="Number of actual days, including holidays and days off, "
        "in the time off request",
    )

    available_leave_days = fields.Float(
        compute="_compute_available_leave_days",
        readonly=True,
        tracking=False,
        help="Number of available leave days for the employee",
    )

    taken_leave_days = fields.Float(
        compute="_compute_taken_leave_days",
        readonly=True,
        tracking=False,
        help="Number of available leave days for the employee",
    )

    def _compute_rest_days(self):
        for record in self:
            record.rest_days = 0

    def _as_local_datetime(self, value):
        """``value``, a naive UTC datetime, in the employee's own time zone."""
        if not value:
            return False
        return (
            UTC.localize(value)
            .astimezone(timezone(self.employee_id.tz or "UTC"))
            .replace(tzinfo=None)
        )

    @api.depends("date_from", "date_to", "employee_id")
    def _compute_public_holiday_days(self):
        for record in self:
            # date_from/date_to are datetimes in UTC while a holiday's date is a
            # calendar date in the employee's time zone: an 08:00 start in UTC+14
            # falls on the previous UTC date, so compare the employee's own dates
            # (a holiday sitting on the day before the request must not be counted,
            # and one on the last requested day must be).
            date_from = record._as_local_datetime(record.date_from)
            date_to = record._as_local_datetime(record.date_to)
            if not date_from or not date_to:
                record.public_holiday_days = 0
                continue
            public_holidays = self.env["calendar.public.holiday.line"].search(
                [
                    ("date", ">=", date_from.date()),
                    ("date", "<=", date_to.date()),
                ]
            )
            record.public_holiday_days = len(public_holidays)

    @api.depends("number_of_days", "rest_days", "public_holiday_days")
    def _compute_real_days(self):
        for record in self:
            record.real_days = (
                record.number_of_days + record.rest_days + record.public_holiday_days
            )

    @api.depends("number_of_days")
    def _compute_taken_leave_days(self):
        leaves = self.env["hr.leave"]
        for record in self:
            taken_leaves = leaves.search(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("holiday_status_id", "=", record.holiday_status_id.id),
                    ("state", "=", "validate"),
                ]
            )
            record.taken_leave_days = sum(taken_leaves.mapped("number_of_days"))

    def _balance_date(self):
        """Date the balance is looked at: the leave's start, or today."""
        self.ensure_one()
        local_start = self._as_local_datetime(self.date_from)
        if local_start:
            return local_start.date()
        return fields.Date.context_today(self)

    def _allocation_balance(self, target_date):
        """What the employee still has for this leave type at ``target_date``.

        Odoo's own date-aware calculation is reused (the one behind the time off
        dashboard): an allocation only counts for the period it is valid in, and
        only for what it still has left, so expired allocations and ones that have
        not started yet do not inflate the balance.

        The request itself is ignored, so the figures answer "what can this
        employee still take" rather than counting this request as already taken.
        """
        self.ensure_one()
        balance = {"remaining": 0.0, "taken": 0.0}
        if not self.employee_id or not self.holiday_status_id:
            return balance
        per_allocation, _extra = self.employee_id.with_context(
            ignored_leave_ids=self.ids
        )._get_consumed_leaves(self.holiday_status_id, target_date)
        allocation_data = (
            (per_allocation or {})
            .get(self.employee_id, {})
            .get(self.holiday_status_id, {})
        )
        for allocation, data in allocation_data.items():
            if allocation:
                # the same validity rule core applies to this very data
                if allocation.date_from > target_date:
                    continue
                if allocation.date_to and allocation.date_to < target_date:
                    continue
            remaining = data.get("remaining_leaves", 0.0)
            balance["remaining"] += remaining
            balance["taken"] += data.get("max_leaves", 0.0) - remaining
        return balance

    @api.depends(
        "number_of_days", "date_from", "date_to", "employee_id", "holiday_status_id"
    )
    def _compute_available_leave_days(self):
        for record in self:
            record.available_leave_days = record._allocation_balance(
                record._balance_date()
            )["remaining"]

    @api.model
    def time2ethiopic(self, year, month, day):
        # Convert to Ethiopic calendar
        pcc_date = pcc.ethiopic_from_fixed(
            pcc.fixed_from_gregorian(pcc.gregorian_date(year, month, day))
        )

        return (
            ""
            + ET_MONTHS_SELECTION_AM[pcc_date[1] - 1][1]
            + " "
            + str(pcc_date[2])
            + ", "
            + str(pcc_date[0])
        )

    @api.onchange("date_to")
    def onchange_enddate(self):
        for record in self:
            dt = record.date_to
            if record.date_to:
                record.return_date_et = record.time2ethiopic(
                    int(dt.strftime("%Y")),
                    int(dt.strftime("%m")),
                    int(dt.strftime("%d")),
                )

    @api.model
    def format_date(self, date_str):
        if not date_str:
            return ""
        d = fields.Datetime.to_datetime(date_str)
        return d.strftime("%b %d, %Y")

    @api.model
    def format_date_et(self, date_str):
        if not date_str:
            return ""
        d = fields.Datetime.to_datetime(date_str)
        return self.env["hr.leave"].time2ethiopic(d.year, d.month, d.day)

    @api.model
    def get_remaining_leaves(self, leave):
        """Days the employee can still take, or '' for a type without allocation.

        Reported for the day the request starts on, and computed with the same
        date-aware balance the rest of this module uses.
        """
        if not leave.holiday_status_id.requires_allocation:
            return ""
        return leave._allocation_balance(leave._balance_date())["remaining"]

    @api.model
    def get_taken_leaves(self, leave):
        """Days already taken for this type, excluding this request itself.

        Returns '' for a type that needs no allocation (the report prints a blank
        in that case).
        """
        if not leave.holiday_status_id.requires_allocation:
            return ""
        return leave._allocation_balance(leave._balance_date())["taken"]

    @api.model
    def get_hrm(self):
        hrm_data = ("", "", self.env._("HR Manager"), "የሠው ሃይል አስተዳደር")
        hrm_id = self.env["ir.config_parameter"].sudo().get_param("hr.hr_manager_id")
        if hrm_id:
            hrm = self.env["hr.employee"].browse(hrm_id)
            hrm_data = (
                hrm.name,
                hrm.ethiopic_name,
                hrm.contract_id.job_id.name,
                hrm.contract_id.job_id.ethiopic_name,
            )

        return hrm_data

    @api.depends("date_from", "date_to", "employee_id")
    def _compute_local_date_from_to(self):
        for record in self:
            record.local_date_from = record._as_local_datetime(record.date_from)
            record.local_date_to = record._as_local_datetime(record.date_to)
