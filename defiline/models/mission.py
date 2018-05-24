# -*- coding: utf-8 -*-
##############################################################################
#
#    NetSkill Group, Business Open Source Solution
#    Copyright (C) 2013-2015 NetSkill Group sprl.
#    Author : Houssine BAKKALI
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from datetime import date,datetime

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class mission(models.Model):
    _name = 'mission.mission'
    
    name = fields.Char(string='Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('customer','=',True)]", required=True)
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')
    event_ids = fields.One2many('event.event', 'mission_id', string='Groups')
    manager_id = fields.Many2one('res.users', string='Project Manager', domain="[('partner_id.is_respondent','=',False),('is_manager','=',True)]", required=True)
    state = fields.Selection([('draft','Draft'),('open','Open'),('closed','Closed'),('invoiced','Invoiced')], string='State', default='draft')
    simple_task_extra_price = fields.Float(string='Unit price')
    simple_task_extra_qty = fields.Float(string='Quantity')
    complex_task_extra_price = fields.Float(string='Unit price')
    complex_task_extra_qty = fields.Float(string='Quantity')
    last_minute = fields.Boolean(string='Last minute request?')
    last_minute_extra = fields.Float(string='Extra percentage',digits_compute= dp.get_precision('Discount'))
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    #invoice_ids = fields.Many2many(related='sale_order_id.invoice_ids', string='Invoice')
    material_received = fields.Date(string='Material received date')
    description_date = fields.Date(string='Project description date') 
    google_form_date = fields.Date(string='Quizz creation date')
    recruitment_date = fields.Date(string='Recruitment date')
    group_sent_date = fields.Date(string='Send group to customer date')
    
    @api.one
    def set_to_open(self):
        self.state = 'open'
    
    @api.one
    def set_to_done(self):
        for project in self.event_ids:
            if project.state != 'done':
                raise except_orm(_("Warning"), _("You can't close a project for which a group still open"))
        
        self.state = 'closed'
    
    @api.one    
    def set_to_draft(self):
        self.state = 'draft'
        
#     @api.one
#     def invoice_mission(self):
#         if self.state != 'closed':
#             raise except_orm(_("Warning"), _("You can't invoice a mission that hasve focus group that still open"))
#         
#         for event in self.event_ids:
#             event.update_invoice()
    
