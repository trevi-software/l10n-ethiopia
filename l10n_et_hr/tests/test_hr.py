# Copyright (C) 2022 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import fields
from odoo.tests import Form, TransactionCase


class RecruitmentTestCase(TransactionCase):
    def setUp(self):
        super().setUp()

        self.Employee = self.env["hr.employee"]
        self.ee = self.Employee.create(
            {
                "name": "Mike",
                "ethiopic_name": "ሚኪ",
            }
        )
        self.dept = self.env["hr.department"].create(
            {
                "name": "Admin",
                "ethiopic_name": "አስተዳደር",
            }
        )
        self.job = self.env["hr.job"].create(
            {
                "name": "somejob",
                "ethiopic_name": "ቦዘኔ",
            }
        )

    def test_name_get(self):
        use_ethiopic_name = self.env["ir.config_parameter"].get_param(
            "l10n_et_hr.use_ethiopic_employee_name"
        )
        self.assertEqual(
            use_ethiopic_name, False, "By default the ethiopic name knob is OFF"
        )

        self.assertEqual(
            self.ee.display_name,
            "Mike",
            "By default the content of the name field is displayed",
        )

    def test_name_get_ethiopic(self):
        self.env["ir.config_parameter"].set_param(
            "l10n_et_hr.use_ethiopic_employee_name", True
        )
        self.ee.invalidate_recordset()

        use_ethiopic_name = self.env["ir.config_parameter"].get_param(
            "l10n_et_hr.use_ethiopic_employee_name"
        )
        self.assertTrue(use_ethiopic_name, "I turned the ethiopic name knob ON")

        self.assertEqual(
            self.ee.display_name,
            "ሚኪ",
            "The content of 'ethiopic_name' field is displayed",
        )

    def test_onchange_dob(self):
        f = Form(self.Employee)
        f.name = "Test"
        f.use_ethiopic_dob = (True,)
        f.etcal_dob_year = "2000"
        f.etcal_dob_month = "1"
        f.etcal_dob_day = "1"

        self.assertEqual(
            f.birthday,
            date(2007, 9, 12),
            "When the ethiopic dob was set the 'birthday' field was modified",
        )

    def test_onchange_dob_seeds_ethiopic_from_birthday(self):
        """Turning the Ethiopic entry on fills the three parts from the birthday."""
        self.ee.birthday = date(1990, 1, 1)

        f = Form(self.ee)
        f.use_ethiopic_dob = True

        self.assertEqual(f.etcal_dob_year, "1982")
        self.assertEqual(f.etcal_dob_month, "4")
        self.assertEqual(f.etcal_dob_day, "23")

    def test_onchange_dob_keeps_birthday_when_incomplete(self):
        """An incomplete Ethiopic entry must not erase the stored birthday."""
        self.ee.birthday = date(1990, 1, 1)

        f = Form(self.ee)
        f.use_ethiopic_dob = True
        # Clearing one of the three parts makes the entry incomplete again.
        f.etcal_dob_day = False

        self.assertEqual(
            fields.Date.to_date(f.birthday),
            date(1990, 1, 1),
            "An incomplete ethiopic date must keep the birthday that was stored",
        )

    def test_department_name_get(self):
        use_ethiopic_name = self.env["ir.config_parameter"].get_param(
            "l10n_et_hr.use_ethiopic_department_name"
        )
        self.assertEqual(
            use_ethiopic_name,
            False,
            "By default the department ethiopic name knob is OFF",
        )

        self.assertEqual(
            self.dept.display_name,
            "Admin",
            "By default the content of the department name field is displayed",
        )

    def test_department_name_get_ethiopic(self):
        self.env["ir.config_parameter"].set_param(
            "l10n_et_hr.use_ethiopic_department_name", True
        )
        self.dept.invalidate_recordset()

        use_ethiopic_name = self.env["ir.config_parameter"].get_param(
            "l10n_et_hr.use_ethiopic_department_name"
        )
        self.assertTrue(
            use_ethiopic_name, "I turned the ethiopic department name knob ON"
        )

        self.assertEqual(
            self.dept.display_name,
            "አስተዳደር",
            "The content of 'ethiopic_name' field is displayed",
        )

    def test_job_name_get(self):
        use_ethiopic_name = self.env["ir.config_parameter"].get_param(
            "l10n_et_hr.use_ethiopic_job_name"
        )
        self.assertEqual(
            use_ethiopic_name, False, "By default the job ethiopic name knob is OFF"
        )

        self.assertEqual(
            self.job.display_name,
            "somejob",
            "By default the content of the job name field is displayed",
        )

    def test_job_name_get_ethiopic(self):
        self.env["ir.config_parameter"].set_param(
            "l10n_et_hr.use_ethiopic_job_name", True
        )
        self.job.invalidate_recordset()

        use_ethiopic_name = self.env["ir.config_parameter"].get_param(
            "l10n_et_hr.use_ethiopic_job_name"
        )
        self.assertTrue(use_ethiopic_name, "I turned the ethiopic job name knob ON")

        self.assertEqual(
            self.job.display_name,
            "ቦዘኔ",
            "The content of 'ethiopic_name' field is displayed",
        )

    def test_employee_name_get(self):
        self.assertEqual(
            self.ee.display_name,
            "Mike",
            "The display_name field is working as expected",
        )

        self.env["ir.config_parameter"].set_param(
            "l10n_et_hr.use_ethiopic_employee_name", True
        )
        self.ee.invalidate_recordset()
        self.assertEqual(
            self.ee.display_name,
            "ሚኪ",
            "The display_name field is working as expected",
        )
