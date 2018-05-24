# -*- coding: utf-8 -*-

from openerp import models, fields, api

import re

class AdminActionWizard(models.TransientModel):
    _name = 'admin.action.wizard'
    
    action = fields.Selection([('format_mobile','Format mobile'),
                             ],string="Action")
    
    def format_mobile(self):
        respondents = self.env['res.partner'].search([('is_respondent','=',True)])
        for respondent in respondents:
            if respondent.mobile:
                mobile = re.sub('[^0-9]+', '', respondent.mobile)
                
                if mobile.startswith('00'):
                    mobile = mobile[2:len(mobile)]
                elif mobile.startswith('0'):
                    mobile = '32' + mobile[1:len(mobile)]
                elif mobile.startswith('+'): 
                    mobile = mobile[1:len(mobile)]
                
                if mobile != respondent.mobile:
                    respondent.mobile = mobile
    
    
    
    @api.one
    def run_action(self):
        
        if self.action == "format_mobile":
            self.format_mobile()
        return {'type': 'ir.actions.act_window_close'}
        
    
