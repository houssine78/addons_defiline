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
from openerp import fields as fields2
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT

from openerp import SUPERUSER_ID, models, api
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.exceptions import except_orm

class res_users(orm.Model):
    _inherit = 'res.users'
    
    def _get_is_manager(self, cr, uid, ids, name, arg, context=None):
        res_users = self.pool.get('res.users')
        user = res_users.browse(cr,uid,ids, context)
        
        return user.has_group(self, cr, uid, 'defiline.group_opinions_assistant')
    
    def _is_manager_search(self, cr, uid, obj, name, args, context=None):
        res_group = self.pool.get('res.groups')
        group_id = res_group.search(cr, uid, [('name','=','Assistant')])
        group = res_group.browse(cr,uid, group_id, context)
        ids = []
        for user in group.users:
            ids.append(user.id)
        return  [('id', 'in', ids)]
    
    _columns = {
        'is_manager': fields.function(_get_is_manager, fnct_search=_is_manager_search, type="boolean", string='Is Manager'),
    }

class res_partner_gender(orm.Model):
    _name = 'res.partner.gender'
    
    _columns = {
        'code': fields.char('code', required=True),
        'name': fields.char('Gender', required=True),
    }

class res_partner_education_level(orm.Model):
    _name = 'res.partner.education.level'
    
    _columns = {
        'name': fields.char('Education level', required=True, translate=True),
        'code': fields.char('Code', required=True),
    }
        
class res_partner(orm.Model):
    _inherit = "res.partner"
    
#     def fields_get(self, cr, uid, fields=None, context=None, write_access=True):
#         fields_to_hide = ['display_name','name']
#         res = super(res_partner, self).fields_get(cr, uid, fields, context)
#         for field in fields_to_hide:
#             res[field]['selectable'] = False
#         return res
    
    def create(self, cr, uid, vals, context):
        if vals.get('customer',False) and vals.get('customer',False) == True:
            if vals.get('parent_id',False) == False:
                sequence_obj = self.pool.get('ir.sequence')
                sequence_id = sequence_obj.search(cr, SUPERUSER_ID, [('code','=','customer.reference')])[0]
                partner_ref = sequence_obj.next_by_id(cr,SUPERUSER_ID,sequence_id)
                vals['ref'] = partner_ref
        return super(res_partner, self).create(cr, uid, vals, context)
    
    def unlink(self, cr, uid, ids, context):
        user_obj = self.pool.get('res.users')

        for partner in self.browse(cr, uid, ids, context): 
            if partner.is_respondent == True:
                if len(partner.user_ids.ids) > 0:
                    user_obj.unlink(cr, SUPERUSER_ID, partner.user_ids.ids, context)
                else:
                    user_ids = user_obj.search(cr, SUPERUSER_ID,[('partner_id','=',partner.id),('active','=',False)])
                    users = user_obj.browse(cr, SUPERUSER_ID, user_ids, context)
                    user_obj.unlink(cr, SUPERUSER_ID, users.ids, context)
            super(res_partner, self).unlink(cr, uid, [partner.id], context)
        return True
        
    def add_phone_call(self, cr, uid, ids, context):
        return {
            'name': 'Add phone call',
            'res_model': 'add.calls.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy':True,
            'context': context
        } 

    _columns = {
        'status': fields.selection([('sab','SAB'),
                                     ('bad','BAD'),
                                     ('zz','ZZ'),],string='Status'),
        'ref_number':fields.integer('Reference Number'),
        'is_respondent' : fields.boolean('Respondent', select=True),
        'is_moderator' : fields.boolean('Moderator', select=True),
        'gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'marital_status': fields.selection([('single', 'Single'), ('cohabiting', 'Cohabiting'),
                                   ('married', 'Married'), ('divorced', 'Divorced'),
                                   ('widowed', 'Widowed'),('with_parents','Living with parents')],'Marital status'),
        'professional_status': fields.selection([('lookingfor', 'Looking for'), ('employee', 'Employee'),
                                   ('worker', 'Worker'), ('student', 'Student'),
                                   ('housewife', 'Housewife/Houseman'),('retired','Retired'),
                                   ('independant','Independant')],'Professional status', select=True),
        'edu_level_id': fields.many2one('res.partner.education.level', 'Educational level'),
        'partner_edu_level_id': fields.many2one('res.partner.education.level', 'Partner educational level'),
        'nationality_id': fields.many2one('res.country', 'Nationality', ondelete='restrict'),
        'knows_french': fields.boolean("Knows french"),
        'knows_dutch': fields.boolean("Knows dutch"),
        'knows_english': fields.boolean("Knows english"),
        'knows_spanish': fields.boolean("Knows spanish"),
        'knows_italian': fields.boolean("Knows italian"),
        'knows_german': fields.boolean("Knows german"),
        'knows_arabic': fields.boolean("Knows arabic"),
        'knows_eastern': fields.boolean("Knows eastern language"),
        'knows_nordic': fields.boolean("Knows nordic language"),
        'numberofchildren' : fields.integer('Number of children'),
        'child1_yearofbirth':fields.char('Year of Birth'),
        'child1_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child2_yearofbirth':fields.char('Year of Birth'),
        'child2_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child3_yearofbirth':fields.char('Year of Birth'),
        'child3_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child4_yearofbirth':fields.char('Year of Birth'),
        'child4_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child5_yearofbirth':fields.char('Year of Birth'),
        'child5_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child6_yearofbirth':fields.char('Year of Birth'),
        'child6_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child7_yearofbirth':fields.char('Year of Birth'),
        'child7_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child8_yearofbirth':fields.char('Year of Birth'),
        'child8_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child9_yearofbirth':fields.char('Year of Birth'),
        'child9_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'child10_yearofbirth':fields.char('Year of Birth'),
        'child10_gender': fields.selection([('M', 'Male'), ('F', 'Female')],'Gender'),
        'has_car': fields.boolean("Has car"),
        'car_brand': fields.char("Car brand"),
        'car_model': fields.char("Car model"),
        'is_smoker': fields.boolean("Is smoker"),
        'tobacco_brand': fields.char("Tobacco brand"),
        'hypermarket': fields.char("Hypermarket"),
        'hypermarket_other': fields.char("Hypermarket"),
        'buys_big_brand': fields.boolean("Buy big brand"),
        'buys_sign_brand': fields.boolean("Buy sign brand"),
        'has_pet_cat': fields.boolean("Has pet cat"),
        'has_pet_dog': fields.boolean("Has pet dog"),
        'has_pet_other': fields.boolean("Has pet other"),
        'allow_brussels': fields.boolean("Allow Brussels"),
        'allow_namur': fields.boolean("Allow Namur"),
        'allow_liege': fields.boolean("Allow Liege"),
        'allow_mons': fields.boolean("Allow Mons"),
        'allow_charleroi': fields.boolean("Allow Charleroi"),
        'allow_gent': fields.boolean("Allow Gent"),
        'allow_antwerpen': fields.boolean("Allow Antwerpen"),
        'allow_brugge': fields.boolean("Allow Brugge"),
        'registration_validation_url': fields.char('Registration validation url'),
        'token_validated': fields.boolean('Token validated'),
        'mobile_operator': fields.char('Mobile operator'),
        'profession_name': fields.char('Profession name'),
        'business_type' : fields.char('Type of business', select=True),
        'profession_indie_comp': fields.boolean('Independant complementary'),
        'availability': fields.selection([('day','Day'),('evening','Evening'),('both','Day and evening')],'Availability'),
        'moderator_project': fields.one2many('event.event','moderator', 'Projects history'), 
        'projects': fields.one2many('event.registration','partner_id',string='Groups history'),
        'profile_last_update': fields.date('Last profile update',readonly=True),
        'informed_by_mail': fields.boolean('Keep me informed by email'),
        'informed_by_sms': fields.boolean('Keep me informed by sms'),
    }

class ResPartnerLang(models.Model):    
    _name = 'res.partner.lang'
    
    name = fields2.Char(string='Lang', required=True, translate=True)
    res_lang = fields2.Many2one('res.lang',string='Res lang', required=True)
    code = fields2.Char(related='res_lang.code', string='Local code')
    
class ResPartner(models.Model):    
    _inherit = 'res.partner'
    
    @api.model
    def _get_computed_name(self, lastname, firstname):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        return u" ".join((p for p in (firstname, lastname) if p))
    
    def _search_age(self, operator, value):
        if operator not in ('=', '!=', '<', '<=', '>', '>=', 'in', 'not in'):
            return []
        query = """SELECT id FROM "%s" WHERE extract(year from age(CURRENT_DATE, birthdate)) %s %%s""" % \
                (self._table, operator)
        self.env.cr.execute(query, (value,))
        ids = [t[0] for t in self.env.cr.fetchall()]
        return [('id', 'in', ids)]

    @api.one
    @api.depends('birthdate')
    def _compute_age(self):
        if self.birthdate:
            dBday = datetime.strptime(self.birthdate, OE_DFORMAT).date()
            dToday = datetime.now().date()
            self.age = dToday.year - dBday.year - ((
                dToday.month, dToday.day) < (dBday.month, dBday.day))
    
    @api.one
    @api.depends('projects','projects.state','projects.backup')
    def _get_last_participation(self):
        if self.projects :
            last_date = False
            for project in self.projects:
                if project.backup == False and project.state not in ['draft','cancel','missed']:
                    if last_date == False:
                        last_date = project.event_id.start_date
                    elif last_date < project.event_id.start_date:
                        last_date = project.event_id.start_date
            self.last_participation_date = last_date
        else:
            self.last_participation_date = False
    
#     def _search_on_last_participation(self, operator, value):
#         if operator not in ('=', '<', '<=', '>', '>='):
#             return []
#         
#         query = """SELECT distinct partner_id FROM event_registration WHERE event_id in (SELECT id FROM event_event WHERE start_date %s %%s)"""% \
#                 (operator)
#         self.env.cr.execute(query, (value,))
#         ids = [t[0] for t in self.env.cr.fetchall()]
#         return [('id', 'in', ids)]
            
    birthdate = fields2.Date(string='Birthdate')       
    age = fields2.Integer(
        string='Age',
        readonly=True,
        compute='_compute_age',
        search='_search_age'
    )
    last_participation_date = fields2.Date(
        string='Last participation date',
        compute='_get_last_participation', store=True
#         search='_search_on_last_participation'
        )
    