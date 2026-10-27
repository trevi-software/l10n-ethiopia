# Copyright (C) 2025 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    ethiopic_name = fields.Char()

    exclude_rest_days = fields.Boolean(
        help="If this is enabled, rest days will not be counted as leave days.",
    )

    def _get_remaining_leaves(self, employee_id):
        employee_ids = [employee_id]
        res = {
            ee_id: {
                leave_type.id: {
                    "max_leaves": 0,
                    "leaves_taken": 0,
                    "remaining_leaves": 0,
                    "virtual_remaining_leaves": 0,
                    "virtual_leaves_taken": 0,
                }
                for leave_type in self
            }
            for ee_id in employee_ids
        }

        if employee_id:
            # Use get_allocation_data (Odoo 18 API) instead of deprecated get_days
            employee = self.env["hr.employee"].browse(employee_id)
            allocation_data = self.get_allocation_data(employee).get(employee, [])
            for leave_type_data in allocation_data:
                if len(leave_type_data) >= 4:
                    name, values, requires_allocation, lt_id = leave_type_data
                    if lt_id in self.ids:
                        res[employee_id][lt_id] = {
                            "max_leaves": values.get("max_leaves", 0),
                            "leaves_taken": values.get("leaves_taken", 0),
                            "remaining_leaves": values.get("remaining_leaves", 0),
                            "virtual_remaining_leaves": values.get(
                                "virtual_remaining_leaves", 0
                            ),
                            "virtual_leaves_taken": values.get(
                                "virtual_leaves_taken", 0
                            ),
                        }
        return res
