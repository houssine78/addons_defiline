# -*- encoding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _

class search_ref_wizard(models.TransientModel):
    _name = 'search.respondent.wizard'
    
    name = fields.Char('Respondent search',help='Enter your emails or references separeted by a semicolon')
    on_reference = fields.Boolean('On reference', default=True)
    on_email = fields.Boolean('On email')
    on_customer_participation = fields.Boolean('On customer participation')
    customer = fields.Many2one('res.partner', domain=[('customer','=',True)], string="Customer")   
    participation = fields.Selection([('part','Participation for this customer'),
                                 ('no_part','No participation for this customer')], default='part', string="Option")
     
    @api.onchange('on_reference')
    def onchange_reference(self):
        if self.on_reference:
            self.on_email = False
            self.on_customer_participation = False
            
    @api.onchange('on_email')
    def onchange_email(self):    
        if self.on_email:
            self.on_reference = False
            self.on_customer_participation = False
    
    @api.onchange('on_customer_participation')
    def onchange_oncustomer(self):    
        if self.on_customer_participation:
            self.on_reference = False
            self.on_email = False   
                
    @api.multi   
    def search_on_respondent(self):
        if self.name:
            list = self.name.lower().split(';')
            search_list = []
            for name in list:
                search_list.append(str(name).strip())
        
        if self.on_reference:
            respondent_ids = self.env['res.partner'].search([('is_respondent','=',True),('ref_number', 'in', search_list)])
        elif self.on_email:
            respondent_ids = self.env['res.partner'].search([('is_respondent','=',True),('email', 'in', search_list)])
        elif self.on_customer_participation:
            participations = self.env['event.registration'].search([('customer','=',self.customer.id),('state','in',['done','open'])])
            all_respondents = self.env['res.partner'].search([('is_respondent','=',True)])
            participators = participations.mapped('partner_id')
            if self.participation == 'part':
                respondent_ids = participators
            else:
                respondent_ids = all_respondents - participators
        else:
            print('you must choose at least one option')
            
        act_obj = self.env['ir.actions.act_window']
        res_id = act_obj.search([('name', '=', 'Respondents')])
        act_win = act_obj.search_read([('id','=',res_id.id)], [])[0]
        act_win['domain'] = [('id','in',respondent_ids.ids)]
        act_win['name'] = _('Respondents')
        
        return act_win
    
