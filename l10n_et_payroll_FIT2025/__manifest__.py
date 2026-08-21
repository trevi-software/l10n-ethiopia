# Copyright (C) 2022 Trevi Software (https://trevi.et)
# Copyright (C) 2014 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Federal Income Tax Tables 2017",
    "summary": "Ethiopian Federal Income Tax tables (rev. 2017)",
    "version": "18.0.1.0.0",
    "category": "Localization",
    "images": ["static/src/img/main_screenshot.png"],
    "license": "AGPL-3",
    "author": "TREVI Software",
    "website": "https://github.com/OCA/l10n-ethiopia",
    "depends": [
        "payroll",
        "l10n_et_payroll_category",
    ],
    "data": [
        "data/payroll_data.xml",
    ],
    "installable": True,
}
