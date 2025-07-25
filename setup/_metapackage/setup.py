import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-l10n-ethiopia",
    description="Meta package for oca-l10n-ethiopia Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ethiopic_calendar',
        'odoo14-addon-l10n_et_hr',
        'odoo14-addon-l10n_et_hr_employee_wizard',
        'odoo14-addon-l10n_et_payroll_FIT2016',
        'odoo14-addon-l10n_et_payroll_FIT2025',
        'odoo14-addon-l10n_et_payroll_category',
        'odoo14-addon-l10n_et_tz',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
