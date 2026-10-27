# Copyright (C) 2022 Trevi Software (https://trevi.et)
# Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime

from odoo import api, fields, models

from odoo.addons.ethiopic_calendar.models.ethiopic_calendar import (
    ET_DAYOFMONTH_SELECTION,
    ET_MONTHS_SELECTION,
)
from odoo.addons.ethiopic_calendar.models.pycalcal import pycalcal as pcc


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _get_year(self):
        res = []

        # Employees are assumed to be at least 16 years old, and the range reaches
        # back 100 years so that a birthday of anyone alive today has a matching
        # choice: the previous 59-year window could not represent, say, 1940, and
        # converting such a birthday to the Ethiopic calendar then failed.
        year = datetime.now().year
        year -= 16

        # Convert to Ethiopic calendar
        pccDate = pcc.ethiopic_from_fixed(
            pcc.fixed_from_gregorian(pcc.gregorian_date(year, 1, 1))
        )
        year = pccDate[0]

        i = year
        while i > (year - 100):
            res.append((str(i), str(i)))
            i -= 1

        return res

    @api.model
    def _get_certificate_selection(self):
        """Extend core's certificate selection with the Ethiopian school levels.

        Odoo 19 exposes ``certificate`` through this method instead of a static
        list (so ``selection_add`` raises an AssertionError), which also means the
        field itself stays core's: the core values keep their keys and only get the
        Ethiopian labels, and the extra levels are appended here.
        """
        labels = {
            "graduate": "Secondary School",
            "bachelor": "Batchelor (BA)",
            "master": "Master (MA)",
            "doctor": "Doctorate",
        }
        selection = [
            (value, labels.get(value, label))
            for value, label in super()._get_certificate_selection()
        ]
        return selection + [
            ("diploma", "Diploma"),
            ("none", "No Formal Education"),
            ("primary", "Primary School"),
        ]

    ethiopic_name = fields.Char()
    use_ethiopic_dob = fields.Boolean("Use Ethiopic Birthday")
    etcal_dob_month = fields.Selection(
        ET_MONTHS_SELECTION, "Month", groups="hr.group_hr_user", tracking=True
    )
    etcal_dob_day = fields.Selection(
        ET_DAYOFMONTH_SELECTION, "Day", groups="hr.group_hr_user", tracking=True
    )
    etcal_dob_year = fields.Selection(
        _get_year, "Year", groups="hr.group_hr_user", tracking=True
    )

    def _compute_display_name(self):
        # 'hr.employee.base' no longer exists in 19.0, this used to live there.
        use_ethiopic_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_et_hr.use_ethiopic_employee_name")
        )
        if not use_ethiopic_name:
            return super()._compute_display_name()
        for rec in self:
            rec.display_name = rec.ethiopic_name or rec.name

    @api.onchange("etcal_dob_day", "etcal_dob_month", "etcal_dob_year")
    def onchange_etdob(self):
        """Fill the Gregorian birthday from a complete Ethiopic entry."""
        for rec in self:
            if rec.etcal_dob_day and rec.etcal_dob_month and rec.etcal_dob_year:
                dob = pcc.gregorian_from_fixed(
                    pcc.fixed_from_ethiopic(
                        pcc.ethiopic_date(
                            int(rec.etcal_dob_year),
                            int(rec.etcal_dob_month),
                            int(rec.etcal_dob_day),
                        )
                    )
                )
                rec.birthday = fields.Date.to_string(
                    date(year=dob[0], month=dob[1], day=dob[2])
                )
            # A partial Ethiopic entry leaves the stored birthday alone: erasing it
            # here would lose the Gregorian date as soon as the fields are cleared.

    @api.onchange("use_ethiopic_dob")
    def onchange_use_ethiopic_dob(self):
        """Fill the Ethiopic parts from the current birthday when switching.

        The three parts are only ever converted Ethiopic -> Gregorian, so turning
        the entry on must not feed the parts that are already on the record back
        into the conversion: a birthday corrected while the entry was off would be
        overwritten with the stale Ethiopic date.
        """
        for rec in self:
            birthday = fields.Date.to_date(rec.birthday)
            if not birthday:
                # An empty Gregorian birthday means the old Ethiopic parts are
                # stale: clear them, or turning the entry back on would show the
                # previous date while the birthday stays empty.
                rec.etcal_dob_year = False
                rec.etcal_dob_month = False
                rec.etcal_dob_day = False
                continue
            if not rec.use_ethiopic_dob:
                continue
            ethiopic = pcc.ethiopic_from_fixed(
                pcc.fixed_from_gregorian(
                    pcc.gregorian_date(birthday.year, birthday.month, birthday.day)
                )
            )
            rec.etcal_dob_year = str(ethiopic[0])
            rec.etcal_dob_month = str(ethiopic[1])
            rec.etcal_dob_day = str(ethiopic[2])
