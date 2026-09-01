# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestHrEmployeeWizard(TransactionCase):
    """Test Ethiopian localization for HR Employee Wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env["res.company"]
        cls.Employee = cls.env["hr.employee"]
        cls.Applicant = cls.env["hr.applicant"]
        cls.Candidate = cls.env["hr.candidate"]
        cls.Job = cls.env["hr.job"]
        cls.Department = cls.env["hr.department"]
        cls.Currency = cls.env["res.currency"]
        cls.Wizard = cls.env["hr.employee.wizard.new"]

    def test_ethiopian_fields_on_applicant(self):
        """Test that Ethiopian-specific fields exist on hr.applicant."""
        candidate = self.Candidate.create({"partner_name": "Test Applicant"})
        applicant = self.Applicant.create(
            {
                "candidate_id": candidate.id,
                # Ethiopia-specific fields
                "ethiopic_name": "ተስተዋል ማክበሻ",
                "use_ethiopic_dob": True,
                "etcal_dob_day": "5",
                "etcal_dob_month": "8",
                "etcal_dob_year": "2009",
            }
        )
        self.assertEqual(applicant.ethiopic_name, "ተስተዋል ማክበሻ")
        self.assertTrue(applicant.use_ethiopic_dob)
        self.assertEqual(applicant.etcal_dob_day, "5")
        self.assertEqual(applicant.etcal_dob_month, "8")
        self.assertEqual(applicant.etcal_dob_year, "2009")

    def test_ethiopic_dob_onchange(self):
        """Test Ethiopian calendar DOB onchange."""
        candidate = self.Candidate.create({"partner_name": "Test Applicant"})
        applicant = self.Applicant.new({"candidate_id": candidate.id})
        applicant.etcal_dob_day = "5"
        applicant.etcal_dob_month = "8"
        applicant.etcal_dob_year = "2009"
        applicant.onchange_etdob()
        # The onchange should set birth_date to the Gregorian equivalent
        self.assertTrue(applicant.birth_date)

    def test_wizard_contains_ethiopian_fields(self):
        """Test that wizard form contains Ethiopian fields."""
        wizard = self.Wizard.create(
            {
                "name": "Test Recruitment",
                "company_id": self.env.company.id,
                "ethiopic_name": "ተስተዋል ማክበሻ",
                "use_ethiopic_dob": True,
                "etcal_dob_day": "5",
                "etcal_dob_month": "8",
                "etcal_dob_year": "2009",
                "house_no": "B-123",
                "kebele": "01",
                "woreda": "Bole Subcity",
            }
        )
        self.assertEqual(wizard.ethiopic_name, "ተስተዋል ማክበሻ")
        self.assertTrue(wizard.use_ethiopic_dob)
        self.assertEqual(wizard.house_no, "B-123")
        self.assertEqual(wizard.kebele, "01")
        self.assertEqual(wizard.woreda, "Bole Subcity")

    def test_wizard_ethiopic_dob_onchange(self):
        """Test wizard Ethiopian calendar DOB onchange."""
        wizard = self.Wizard.new(
            {
                "name": "Test Recruitment",
                "company_id": self.env.company.id,
            }
        )
        wizard.etcal_dob_day = "5"
        wizard.etcal_dob_month = "8"
        wizard.etcal_dob_year = "2009"
        wizard.onchange_etdob()
        self.assertTrue(wizard.birth_date)

    def test_applicant_to_employee_creation(self):
        """Test creating employee from applicant with Ethiopian data."""
        candidate = self.Candidate.create({"partner_name": "Test Applicant"})
        applicant = self.Applicant.create(
            {
                "candidate_id": candidate.id,
                "email_from": "test@example.com",
                "ethiopic_name": "ተስተዋል ማክበሻ",
            }
        )
        action = applicant.create_employee_from_applicant()
        # The base implementation opens the employee form — the inherited
        # one additionally injects Ethiopian defaults in the context.
        self.assertEqual(
            action["context"].get("default_ethiopic_name"),
            applicant.ethiopic_name,
        )
        self.assertEqual(
            action["context"].get("default_use_ethiopic_dob"),
            applicant.use_ethiopic_dob,
        )
