import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-l10n-ethiopia",
    description="Meta package for oca-l10n-ethiopia Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-l10n_et_base',
        'odoo8-addon-l10n_et_base_vat',
        'odoo8-addon-l10n_et_title',
        'odoo8-addon-l10n_et_toponym',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
