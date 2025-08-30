# Copyright (C) 2025 Trevi Software (https://trevi.et)
# Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import api, fields, models

from odoo.addons.ethiopic_calendar.models.ethiopic_calendar import ET_MONTHS_SELECTION_AM
from odoo.addons.ethiopic_calendar.models.pycalcal import pycalcal as pcc


class HolidaysRequest(models.Model):
    
    _inherit = 'hr.leave'

    return_date_et = fields.Char('Ethiopic Return Date')

    @api.model
    def time2ethiopic(self, year, month, day):
        
        # Convert to Ethiopic calendar
        pcc_date = pcc.ethiopic_from_fixed(
                    pcc.fixed_from_gregorian(
                        pcc.gregorian_date(year, month, day)))
        
        return u'' + ET_MONTHS_SELECTION_AM[pcc_date[1]-1]+' '+str(pcc_date[2])+', '+str(pcc_date[0])

    @api.onchange('date_to')
    def onchange_enddate(self, employee_id,
                         date_from, date_to, holiday_status_id, no_days, context=None):
        
        res = super(HolidaysRequest, self).onchange_enddate(employee_id, date_from, date_to,
                                                        holiday_status_id, no_days, context=context)
        if res.get('value', False) and res['value'].get('return_date'):
            dt = datetime.strptime(res['value']['return_date'], '%B %d, %Y')
            res['value'].update({'return_date_et': self.time2ethiopic(int(dt.strftime('%Y')),
                                                                      int(dt.strftime('%m')),
                                                                      int(dt.strftime('%d')))})
        elif res.get('value', False):
            res['value'].update({'return_date_et': False})
        return res

    @api.model
    def format_date(self, date_str):
        
        if not date_str:
            return ''
        d = datetime.strptime(date_str, OE_DTFORMAT)
        return d.strftime("%b %d, %Y")

    @api.model
    def format_date_et(self, date_str):
        
        if not date_str:
            return ''
        d = datetime.strptime(date_str, OE_DTFORMAT)
        return self.env['hr.leave'].time2ethiopic(d.year, d.month, d.day)

    @api.model
    def get_remaining_leaves(self, leave):
        
        obj = self.env['hr.leave.type']
        res = obj.get_remaining_days_by_employee([leave.holiday_status_id.id],
                                                 leave.employee_id.id)
        res = res[leave.employee_id.id]
        if res[leave.holiday_status_id.id].get('max_leaves', False) and res[leave.holiday_status_id.id]['max_leaves'] > 0:
            days = res[leave.holiday_status_id.id]['remaining_leaves']
            if leave.state not in ['validate', 'validate1']:
                days = res[leave.holiday_status_id.id]['remaining_leaves'] - leave.number_of_days_temp
        else:
            days = ''
        
        return days
    
    @api.model
    def get_taken_leaves(self, leave):
        
        obj = self.env['hr.leave.type']
        res = obj.get_remaining_days_by_employee([leave.holiday_status_id.id],
                                                 leave.employee_id.id)
        res = res[leave.employee_id.id]
        if res[leave.holiday_status_id.id].get('max_leaves', False) and res[leave.holiday_status_id.id]['max_leaves'] > 0:
            days = res[leave.holiday_status_id.id]['max_leaves'] - res[leave.holiday_status_id.id]['remaining_leaves']
            
            # We only want leaves taken so far, *EXCLUDING* this one
            if leave.state in ['validate', 'validate1']:
                days -= leave.number_of_days_temp
        else:
            days = ''
        
        return days
    
    @api.model
    def get_hrm(self):
        
        hrm_data = ('', '', _('HR Manager'), u'የሠው ሃይል አስተዳደር')
        hrm_dict = self.env['hr.config.settings'].get_default_hr_manager_id(False)
        hrm_id = hrm_dict['hr_manager_id']
        if hrm_id != False:
            hrm = self.env['hr.employee'].browse(hrm_id)
            hrm_data = (
                hrm.name,
                hrm.ethiopic_name,
                hrm.contract_id.job_id.name,
                hrm.contract_id.job_id.ethiopic_name
            )
        
        return hrm_data
