# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2020 Open Architect Consulting sprl.
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
import logging
import pytz

from urlparse import urljoin

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from openerp.addons.web.http import request

from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class EventOrderLine(models.Model):
    _name="event.order.line"
    
    def _is_catering(self):
        ids = self.env['product.category'].search([('name','ilike','catering')]).ids
        return [('categ_id','in',ids)] 
    
    product_id = fields.Many2one('product.product', domain=_is_catering, string="Product")
    quantity = fields.Integer("Quantity")
    event_id = fields.Many2one('event.event')

class ResCompany(models.Model):
    _inherit = "res.company"

    location_ids = fields.Many2many('event.location',
                                    'company_event_location_rel',
                                    string="location")
    
class EventLocation(models.Model):
    _name = "event.location"
    
    name = fields.Char("Location")


class website(models.Model):
    _inherit = 'website'
    
    def get_postits(self):
        env = request.env
       
        domain = [('publish','=',True),
                  ('date_begin','<=',date.today()),
                  ('date_end','>=',date.today())]
       
        session_lang = request.lang
        
        if session_lang == 'nl_BE':
            domain.append(('display_nl','=',True))
        elif session_lang == 'en_US':
            domain.append(('display_en','=',True))
        else:
            domain.append(('display_fr','=',True))
         
        groups = env['event.event'].sudo().search(domain)
        
        return groups


class event(models.Model):
    _inherit = "event.event"
    
    user_id = fields.Many2one('res.users', string='Responsible User',
        default=lambda self: self.env.user, readonly=False, 
        domain=[('is_respondent','=',False)], states={'done': [('readonly', True)]})
    reference_number = fields.Char(string="Reference number")
    moderator = fields.Many2one('res.partner', string="Moderator", domain=[('is_moderator','=',True)])
    mission_id = fields.Many2one('mission.mission', string='Project')
    customer = fields.Many2one(string="Customer", related="mission_id.partner_id")
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer','=',True)])
    customer_ref = fields.Char(related='customer_id.commercial_partner_id.ref', string='Customer Ref')
    event_order_lines = fields.One2many('event.order.line','event_id',string="Catering order lines")
    extra_time = fields.Integer(string='Extra half-hour')
    title = fields.Char(string='Post-it title', translate=True)
    postit_description = fields.Char(string='Post-it description', translate=True)
    start_date_date = fields.Date(string='At start date',
                                  store=True, readonly=True,
                                  compute='_compute_at_start_date')
    start_date = fields.Datetime(string='Start')
    end_date = fields.Datetime(string='End')
    publish = fields.Boolean(string='Publish') 
    display_fr = fields.Boolean(string="Display on french website")
    display_nl = fields.Boolean(string="Display on ducth website")
    display_en = fields.Boolean(string="Display on english website")      
    survey_id = fields.Many2one('survey.survey', string='Quizz')
    survey_public_url = fields.Char(related='survey_id.public_url',string='Quizz public url')
    survey_public_url_html = fields.Char(related='survey_id.public_url_html',string='Quizz public url html')
    incentive = fields.Float('Incentive')
    incentive_backup = fields.Float('Incentive Backup')
    sale_order_lines = fields.One2many('sale.order.line', 'event_id', string='Sale order lines')
    invoice_lines = fields.One2many('account.invoice.line', 'event_id', string='Invoice lines')  
    sale_layout_cat_id = fields.Integer(string='Sale layout')
    facility = fields.Float(string="Duration")
    supplement = fields.Integer(string="Supplement/day")
    streaming = fields.Integer(string="Streaming/day")
    starting_fee_qty = fields.Integer(string="Starting fee quantity")
    note_taking = fields.Integer(string="Note taking/hours")
    translator = fields.Integer(string="Translator")
    emailing_date = fields.Date(string='Emailing date')
    confirmation_date = fields.Date(string='Confirmation date to participants')
    reply_to = fields.Char(string='Reply-To Email',
        readonly=False, states={'done': [('readonly', True)]}, default='opinons@opinions.be',
        help="The email address of the organizer is likely to be put here, with the effect to be in the 'Reply-To' of the mails sent automatically at event or registrations confirmation. You can also put the email address of your mail gateway if you use one.")
    
    #put fields non mandatory and changing the type
    date_begin = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    
    registered = fields.Integer(string='Number of registered respondents',
        store=True, readonly=True, compute='_compute_registered')
    booking = fields.Selection([('info','Info'),
                                ('option','Option'),
                                ('reservation','Reservation')],string='Booking type')
    recruitment = fields.Integer(string='Number of respondents to recruit')
    description = fields.Char(string='Description', oldname='note')
    memo = fields.Char(string='Group feedback')
    image = fields.Binary(string="Image")
    image_static_url = fields.Char(compute="_compute_image_url",
                                   string="Static url for image",
                                   store=True)
    geolocation_ids = fields.Many2many('event.location',
                                       'event_location_rel',
                                       string="Geolocation") 

    _order = "start_date asc, id asc"

    @api.multi
    @api.depends('image')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        for event in self:
            image_url = urljoin(base_url, "%s/%s" % ('/post_it_image', event.id))
            event.image_static_url = image_url

    @api.one
    @api.depends('registration_ids.state', 'registration_ids.nb_register')
    def _compute_registered(self):
        self.registered = self.env['event.registration'].search_count([('event_id','=',self.id)
                                                                     ,('state','in',['draft','open','done'])])
    @api.multi
    @api.depends('start_date')
    def _compute_at_start_date(self):
        tz = pytz.timezone(self.user_id.tz) or pytz.utc
        for event in self:
            if self.start_date:
                self.start_date_date = pytz.utc.localize(datetime.strptime(self.start_date, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)    
        
    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:
            start_date = fields.Datetime.from_string(self.start_date)
 
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id.parent_id:
            self.customer_ref = self.customer_id.parent_id.ref
        else:
            self.customer_ref = self.customer_id.ref 
    
    @api.one
    @api.constrains('date_begin', 'date_end')
    def _check_postit_date(self):
        if self.date_end < self.date_begin:
            raise except_orm(_('Error'),_('Post-it End Date cannot be set before Post-it Start Date.'))
    
    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_closing_date(self):
        if self.end_date < self.start_date:
            raise except_orm(_('Error'),_('End Date cannot be set before Start Date.'))
     
    def get_product_from_type(self, product_id, type, mapper):
        for key, value in mapper.items():
            if type == value and product_id == key:
                return key
        return False
    
    @api.multi
    def register_from_ref(self):
        
        act_obj = self.env['ir.actions.act_window']
        # Quick FIX as search on the name doesn't return the action anymore
        # So we make the search on the res_model
        res_id = act_obj.search([('res_model', '=', 'add.respondents.wizard')])
        act_win = act_obj.search_read([('id','=',res_id.id)], [])[0]
        
        return act_win
   
    @api.one
    def confirm_event(self):
        super(event,self).confirm_event()
        self.confirmation_date = fields.Date.context_today(self)  


class event_registration(models.Model):
    _inherit = 'event.registration'
    _order = 'event_begin_date desc'
    
    mission_id = fields.Many2one(string="Project", related="event_id.mission_id")
    customer = fields.Many2one(string="Customer", related="event_id.customer_id")
    mobile = fields.Char(string='Mobile')
    respondent_ref_number = fields.Char(string='Reference', readonly=True)
    state = fields.Selection([
            ('draft', 'Unconfirmed'),
            ('cancel', 'Cancelled'),
            ('missed', 'Missed'),
            ('open', 'Confirmed'),
            ('done', 'Attended'),
        ], string='Status', default='open', readonly=True, copy=False)
    
    event_begin_date = fields.Datetime(string="On", related='event_id.start_date',
        readonly=True, store=True)
    event_end_date = fields.Datetime(string="End Date", related='event_id.end_date',
        readonly=True)
    backup = fields.Boolean(string='Backup')
    
    @api.multi
    def view_respondent(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        form = self.env.ref('defiline.view_respondent_form', False)
        return {
            'name': _('Respondent'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'view_id': form.id,
            'res_id':self.partner_id.id,
            'nodestroy': True,
            'target': 'current',
        }
    
    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            contact_id = self.partner_id.address_get().get('default', False)
            self.name = self.partner_id.name
            self.respondent_ref_number = self.partner_id.ref_number
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                self.email = contact.email
                self.phone = contact.phone
                self.mobile = contact.mobile
    
    @api.one
    def button_reg_missed(self):
        self.state = 'missed'
    
    @api.one
    def button_reg_deleted(self):
        self.unlink()
        return True