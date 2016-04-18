# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Ethiopia - Base VAT',
    'version': '1.0',
    'category': 'Localization',
    'description': """
Base Module Localization for Ethiopia Partners VAT
==================================================

    - Rename VAT field to TIN and introduce another field: 'vat_number' for
      VAT registration number in Partner objects
    - Disable VAT check as it is irrelevant in Ethiopia.
    - Do our own basic VAT checks for uniqueness and correctness
    """,
    'author': 'Clear ICT Solutions, Odoo Community Association (OCA)',
    'website': 'http://www.clearict.com',
    'depends': [
        'base',
        'base_vat',
        'l10n_et_base',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'res_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
