# -*- coding: utf-8 -*-
from openerp import models, fields, api

class AddRespondentsWizard(models.TransientModel):
    _name = 'add.respondents.wizard'
    
    respondent_refs = fields.Char(string="Respondent registration", required=True, help='Enter your emails or references separeted by a semicolon')
    on_reference = fields.Boolean('On reference', default=True)
    on_email = fields.Boolean('On email')
    
    @api.onchange('on_reference')
    def onchange_reference(self):
        if self.on_reference:
            self.on_email = False
            
    @api.onchange('on_email')
    def onchange_email(self):    
        if self.on_email:
            self.on_reference = False
            
    @api.one
    def add_respondents(self):
        event_id = self._context.get('active_ids')[0]
        list = self.respondent_refs.lower().split(';')
        search_list = []
        
        for ref in list:
            search_list.append(str(ref).strip())
        
        if search_list : 
            if self.on_reference:
                registred_list = self.env['event.registration'].search([('event_id','=',event_id),('respondent_ref_number', 'in', search_list)])
                for registred in registred_list:
                    if registred.respondent_ref_number in search_list:
                        search_list.remove(registred.respondent_ref_number)
                        
                respondents = self.env['res.partner'].search([('is_respondent','=',True),('ref_number', 'in', search_list)])
            else:
                registred_list = self.env['event.registration'].search([('event_id','=',event_id),('email', 'in', search_list)])
                for registred in registred_list:
                    if registred.email in search_list:
                        search_list.remove(registred.email)
                    
                respondents = self.env['res.partner'].search([('is_respondent','=',True),('email', 'in', search_list)])
                
            for respondent in respondents:
               subscription = self.env['event.registration'].create({'partner_id':respondent.id, 'event_id':event_id})
               subscription._onchange_partner()
