# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from openerp.osv import fields, osv


class res_country_state(osv.Model):

    _inherit = 'res.country.state'

    _columns = {
        'ethiopic_name': fields.char('Ethiopic Name', size=256, select=True),
        'et_code': fields.char('Ethiopic Code', size=16, select=True),
    }
