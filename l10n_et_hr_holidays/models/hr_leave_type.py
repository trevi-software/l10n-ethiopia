# Copyright (C) 2025 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class hr_holidays_status(models.Model):
    
    _inherit = 'hr.leave.type'
    
    ethiopic_name = fields.Char()
    
    exclude_rest_days = fields.Boolean(string="Exclude Rest Days",
                                       help="If this is enabled, rest days will not be counted "
                                            "as leave days.")
