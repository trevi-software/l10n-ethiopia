from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _get_durations(self, check_leave_type=True, resource_calendar=None):
        """Override to handle exclude_rest_days context for public holidays."""
        if self.env.context.get("exclude_rest_days"):
            self = self.with_context(exclude_rest_days=True)
        return super()._get_durations(
            check_leave_type=check_leave_type, resource_calendar=resource_calendar
        )

    @api.depends("number_of_days")
    def _compute_number_of_hours_display(self):
        """If the leave is validated, we need to inject the context here for
        including the public holidays if applicable.

        For such cases, we need to serialize the call to super in fragments.
        """
        to_serialize = self.filtered(
            lambda x: x.state == "validate" and x.holiday_status_id.exclude_rest_days
        )
        for leave in to_serialize:
            leave = leave.with_context(
                exclude_rest_days=True, employee_id=leave.employee_id.id
            )
            super(HrLeave, leave)._compute_number_of_hours_display()
        return super(HrLeave, self - to_serialize)._compute_number_of_hours_display()
