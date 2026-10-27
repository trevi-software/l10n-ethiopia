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
        cls.Job = cls.env["hr.job"]
        cls.Department = cls.env["hr.department"]
        cls.Currency = cls.env["res.currency"]
        cls.Wizard = cls.env["hr.employee.wizard.new"]
        # The Ethiopic year selection is derived from today's date and only offers
        # adult birth years, so pick a year it really offers instead of a hardcoded
        # one that the range drifts out of.
        cls.applicant_year = cls._valid_ethiopic_year(cls.Applicant, "etcal_dob_year")
        cls.wizard_year = cls._valid_ethiopic_year(cls.Wizard, "etcal_dob_year")

    @staticmethod
    def _valid_ethiopic_year(model, field_name):
        """Return one of the years the Ethiopic year selection currently offers."""
        field = model._fields[field_name]
        selection = (
            field.selection(model) if callable(field.selection) else field.selection
        )
        return selection[0][0]

    def test_ethiopian_fields_on_applicant(self):
        """Test that Ethiopian-specific fields exist on hr.applicant."""
        applicant = self.Applicant.create(
            {
                # Odoo 19 merged hr.candidate into hr.applicant: the applicant
                # itself now carries the personal data (partner_name, ...).
                "partner_name": "Test Applicant",
                # Ethiopia-specific fields
                "ethiopic_name": "ተስተዋል ማክበሻ",
                "use_ethiopic_dob": True,
                "etcal_dob_day": "5",
                "etcal_dob_month": "8",
                "etcal_dob_year": self.applicant_year,
            }
        )
        self.assertEqual(applicant.ethiopic_name, "ተስተዋል ማክበሻ")
        self.assertTrue(applicant.use_ethiopic_dob)
        self.assertEqual(applicant.etcal_dob_day, "5")
        self.assertEqual(applicant.etcal_dob_month, "8")
        self.assertEqual(applicant.etcal_dob_year, self.applicant_year)

    def test_ethiopic_dob_onchange(self):
        """Test Ethiopian calendar DOB onchange."""
        applicant = self.Applicant.new({"partner_name": "Test Applicant"})
        applicant.etcal_dob_day = "5"
        applicant.etcal_dob_month = "8"
        applicant.etcal_dob_year = self.applicant_year
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
                "etcal_dob_year": self.wizard_year,
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
        wizard.etcal_dob_year = self.wizard_year
        wizard.onchange_etdob()
        self.assertTrue(wizard.birth_date)

    def test_applicant_to_employee_creation(self):
        """Test creating employee from applicant with Ethiopian data."""
        applicant = self.Applicant.create(
            {
                "partner_name": "Test Applicant",
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
