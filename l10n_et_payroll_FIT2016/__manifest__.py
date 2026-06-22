# Copyright (C) 2022 Trevi Software (https://trevi.et)
# Copyright (C) 2014 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Federal Income Tax Tables 2008",
    "summary": "Ethiopian Federal Income Tax tables (rev. 2008)",
    "version": "15.0.1.0.0",
    "category": "Localization",
    "images": ["static/src/img/main_screenshot.png"],
    "license": "AGPL-3",
    "author": "TREVI Software",
    "website": "https://github.com/OCA/l10n-ethiopia",
    "depends": [
        "payroll",
        "payroll_default_salary_rules",
    ],
    "data": [
        "data/payroll_data.xml",
    ],
    "installable": True,
}
