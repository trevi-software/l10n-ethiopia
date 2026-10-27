# Copyright (C) 2022 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    ethiopic_name = fields.Char()

    def _compute_display_name(self):
        use_ethiopic_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_et_hr.use_ethiopic_department_name")
        )
        if not use_ethiopic_name or self.env.context.get("hierarchical_naming"):
            return super()._compute_display_name()
        for rec in self:
            rec.display_name = rec.ethiopic_name or rec.name

    @api.depends("name", "ethiopic_name", "parent_id.complete_name")
    def _compute_complete_name(self):
        use_ethiopic_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_et_hr.use_ethiopic_department_name")
        )
        if use_ethiopic_name:
            for department in self:
                name = department.name
                if department.ethiopic_name:
                    name = department.ethiopic_name
                if department.parent_id:
                    department.complete_name = (
                        f"{department.parent_id.complete_name} / {name}"
                    )
                else:
                    department.complete_name = name
        else:
            super()._compute_complete_name()

        return self
