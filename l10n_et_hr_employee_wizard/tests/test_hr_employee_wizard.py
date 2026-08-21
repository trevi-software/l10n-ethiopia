# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrEmployeeWizard(TransactionCase):
    """Test Ethiopian localization for HR Employee Wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env["res.company"]
        cls.Employee = cls.env["hr.employee"]
        cls.Applicant = cls.env["hr.applicant"]
        cls.Job = cls.env["hr.job"]
        cls.Department = cls.env["hr.department"]
        cls.Currency = cls.env["res.currency"]
        cls.Wizard = cls.env["hr.employee.wizard.new"]

    def test_ethiopian_fields_on_applicant(self):
        """Test that Ethiopian-specific fields exist on hr.applicant."""
        applicant = self.Applicant.create(
            {
                "name": "Test Applicant",
                "email_from": "test@example.com",
                "partner_phone": "+251911000000",
                # Ethiopia-specific fields
                "tin": "0000123456",
                "pension_number": "PEN123456",
                "medical_certificate_number": "MED789012",
                "work_permit_number": "WP345678",
                "work_permit_expiry": fields.Date.today(),
                "nationality_id": self.env.ref("base.et").id,
                "region_id": self.env.ref("base.state_et_14").id,
                "zone_id": self.env.ref("base.state_et_14_01").id,
                "woreda_id": self.env.ref("base.state_et_14_01_01").id,
                "kebele_id": "01",
                "house_number": "B-123",
                "phone2": "+251922000000",
                "emergency_contact": "John Doe",
                "emergency_phone": "+251933000000",
                "blood_group": "O+",
                "disability": False,
                "bank_account_id": "1000123456789",
                "bank_branch": "Bole Branch",
                "salary_scale_id": self.env.ref(
                    "l10n_et_hr_payroll.salary_scale_1"
                ).id,
                "grade_id": self.env.ref("l10n_et_hr_payroll.grade_1").id,
                "step_id": self.env.ref("l10n_et_hr_payroll.step_1").id,
                "hire_date": fields.Date.today(),
                "confirmation_date": fields.Date.today(),
                "contract_type_id": self.env.ref(
                    "hr_contract.contract_type_permanent"
                ).id,
                "ethiopic_name": "ተስተዋል ማክበሻ",
                "etcal_dob_day": 15,
                "etcal_dob_month": 8,
                "etcal_dob_year": 2010,
            }
        )
        self.assertEqual(applicant.tin, "0000123456")
        self.assertEqual(applicant.pension_number, "PEN123456")
        self.assertEqual(applicant.ethiopic_name, "ተስተዋል ማክበሻ")
        self.assertEqual(applicant.etcal_dob_day, 15)
        self.assertEqual(applicant.etcal_dob_month, 8)
        self.assertEqual(applicant.etcal_dob_year, 2010)

    def test_ethiopic_dob_onchange(self):
        """Test Ethiopian calendar DOB onchange."""
        applicant = self.Applicant.new(
            {
                "name": "Test Applicant",
                "etcal_dob_day": 15,
                "etcal_dob_month": 8,
                "etcal_dob_year": 2010,
            }
        )
        applicant.onchange_etdob()
        # The onchange should set birth_date to the Gregorian equivalent
        self.assertTrue(applicant.birth_date)

    def test_wizard_contains_ethiopian_fields(self):
        """Test that wizard form contains Ethiopian fields."""
        wizard = self.Wizard.new(
            {
                "name": "Test Recruitment",
                "company_id": self.env.company.id,
                # Ethiopia-specific fields
                "tin": "0000123456",
                "pension_number": "PEN123456",
                "medical_certificate_number": "MED789012",
                "work_permit_number": "WP345678",
                "work_permit_expiry": fields.Date.today(),
                "nationality_id": self.env.ref("base.et").id,
                "region_id": self.env.ref("base.state_et_14").id,
                "zone_id": self.env.ref("base.state_et_14_01").id,
                "woreda_id": self.env.ref("base.state_et_14_01_01").id,
                "kebele_id": "01",
                "house_number": "B-123",
                "phone2": "+251922000000",
                "emergency_contact": "John Doe",
                "emergency_phone": "+251933000000",
                "blood_group": "O+",
                "disability": False,
                "disability_card_number": "DC123",
                "disability_card_expiry": fields.Date.today(),
                "bank_account_id": "1000123456789",
                "bank_branch": "Bole Branch",
                "salary_scale_id": self.env.ref(
                    "l10n_et_hr_payroll.salary_scale_1"
                ).id,
                "grade_id": self.env.ref(
                    "l10n_et_hr_payroll.grade_1"
                ).id,
                "step_id": self.env.ref("l10n_et_hr_payroll.step_1").id,
                "hire_date": fields.Date.today(),
                "confirmation_date": fields.Date.today(),
                "contract_type_id": self.env.ref(
                    "hr_contract.contract_type_permanent"
                ).id,
                "ethiopic_name": "ተስተዋል ማክበሻ",
                "etcal_dob_day": 15,
                "etcal_dob_month": 8,
                "etcal_dob_year": 2010,
            }
        )
        self.assertEqual(wizard.tin, "0000123456")
        self.assertEqual(wizard.pension_number, "PEN123456")
        self.assertEqual(wizard.ethiopic_name, "ተስተዋል ማክበሻ")

    def test_wizard_ethiopic_dob_onchange(self):
        """Test wizard Ethiopian calendar DOB onchange."""
        wizard = self.Wizard.new(
            {
                "name": "Test Recruitment",
                "company_id": self.env.company.id,
                "etcal_dob_day": 15,
                "etcal_dob_month": 8,
                "etcal_dob_year": 2010,
            }
        )
        wizard.onchange_etdob()
        self.assertTrue(wizard.birth_date)

    def test_applicant_to_employee_creation(self):
        """Test creating employee from applicant with Ethiopian data."""
        applicant = self.Applicant.create(
            {
                "name": "Test Applicant",
                "email_from": "test@example.com",
                "partner_phone": "+251911000000",
                "tin": "0000123456",
                "pension_number": "PEN123456",
                "medical_certificate_number": "MED789012",
                "nationality_id": self.env.ref("base.et").id,
                "ethiopic_name": "ተስተዋል ማክበሻ",
            }
        )
        # Test the create_employee_from_applicant method
        action = applicant.create_employee_from_applicant()
        self.assertEqual(action["res_model"], "hr.employee.wizard.new")
        self.assertIn("context", action)
        self.assertEqual(action["context"].get("default_tin"), applicant.tin)
        self.assertEqual(
            action["context"].get("default_pension_number"), applicant.pension_number
        )
        self.assertEqual(
            action["context"].get("default_ethiopic_name"), applicant.ethiopic_name
        )
