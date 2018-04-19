import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-l10n-ethiopia",
    description="Meta package for oca-l10n-ethiopia Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-l10n_et_base',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
