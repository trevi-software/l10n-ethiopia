# Copyright (C) 2022 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    ethiopic_name = fields.Char(readonly=True)

    def _compute_display_name(self):
        # 'hr.employee.base' no longer exists in 19.0: hr.employee.public now
        # inherits from nothing, so it needs its own copy of the override.
        use_ethiopic_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_et_hr.use_ethiopic_employee_name")
        )
        if not use_ethiopic_name:
            return super()._compute_display_name()
        for rec in self:
            rec.display_name = rec.ethiopic_name or rec.name
