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

import logging
import base64
import re

import werkzeug
import werkzeug.urls
import werkzeug.utils
from urlparse import urljoin

import random

import datetime

from ast import literal_eval

from openerp.addons.auth_signup.res_users import SignupError
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _

import json

_logger = logging.getLogger(__name__)

PROFILE_FIELDS = ['title','lang','street','zip','city','country_id','email','phone','mobile','birthdate',
    'gender','marital_status','professional_status','edu_level_id',
    'partner_edu_level_id','nationality_id','knows_french','knows_dutch','knows_english',
    'knows_spanish','knows_italian','knows_german','knows_arabic','knows_eastern','knows_nordic', 'children',
    'has_car','car_brand','car_model','is_smoker',
    'tobacco_brand','hypermarket','buys_big_brand','buys_sign_brand','has_pet_cat','has_pet_dog',
    'has_pet_other','allow_brussels', 'allow_namur','allow_liege','allow_mons','allow_charleroi',
    'allow_gent','allow_antwerpen','allow_brugge','mobile_operator','profession_name','business_type',
    'profession_indie_comp','availability','hypermarket_other','availability','image','informed_by_mail','informed_by_sms']

def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))

class register(http.Controller):
    
    def create_respondent(self, request, values, kwargs):
        cr, uid, env, context = request.cr, request.uid, request.env, request.context
        
        ir_config_parameter = request.registry['ir.config_parameter']
        template_user_id = literal_eval(ir_config_parameter.get_param(cr, SUPERUSER_ID, 'defiline.template_respondent_id', 'False'))
        assert template_user_id and request.registry['res.users'].exists(cr, SUPERUSER_ID, template_user_id, context=context), 'Signup: invalid template user'

        context['no_reset_password'] = True
        return request.registry['res.users'].copy(cr, SUPERUSER_ID,template_user_id, values,context)
    
    def token_url(self, env, route, token):
        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        return urljoin(base_url, "%s?token=%s" % (route, token))
    
    @http.route(['/profile/get_location'], type='json', auth="public", methods=['POST'], website=True)
    def get_location(self, zip, **kw):
        values = {}
        better_zips = request.env['res.better.zip'].sudo().search([('name','=',zip)])
        for better_zip in better_zips:
            values[str(better_zip.id)]= {
            'display_name': better_zip.display_name,
            'city': better_zip.city,
            'state_id': better_zip.state_id.id,
            }
        return values
        
    @http.route(['/page/show_registration'], type='http', auth="public", website=True)
    def show_registration(self, **kwargs):
        env = request.env
        values = {}
        errors = {}
        
        values['titles']= env['res.partner.title'].sudo().search([('domain','=','contact')])
        values['langs'] = env['res.partner.lang'].sudo().search([])
        if 'website_respondent_register_error' in request.session:
            errors = request.session.pop('website_respondent_register_error')
        if kwargs == {}: 
            if 'website_respondent_register_default' in request.session:
                kwargs = request.session.pop('website_respondent_register_default')
        for field in ['title','firstname','lastname','email', 'confirm_email', 'password', 'confirm_password','birthdate','accept_general_conditions']:
            if kwargs.get(field):
                if field == 'title':
                    values[field] = int(kwargs.pop(field))
                else:
                    values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        values['errors'] = errors
        return request.website.render("defiline.registration", values)
    
    @http.route(['/page/register'], methods=['POST'], type='http', auth="public", website=True)
    def register(self, **post):
        env = request.env
        error = {}
        for field_name in ['title','firstname','lastname', 'password', 'confirm_password', 'email','confirm_email','birthdate','lang']:
            if not post.get(field_name):
                error[field_name] = 'missing'
        if post.get("password") != post.get("confirm_password"):
            error["password"] = "Password confirmation doesn't match."
        if post.get("email") != post.get("confirm_email"):
            error["email"] = "Email confirmation doesn't match."
        else:
            email_check = env['res.partner'].sudo().search([('is_respondent','=',True)
                                                            ,('email','=',post.get("email"))])
            if len(email_check) == 0:
               email_check = env['res.partner'].sudo().search([('is_respondent','=',True)
                                                        ,('email','=',post.get("email"))
                                                        ,('active','=',False)])
            if len(email_check) > 0:
                error["email"] = _("This email address is already registered. If you forgot your password go to the login page and click on the reset password link") 
        if error:
            request.session['website_respondent_register_error'] = error
            request.session['website_respondent_register_default'] = post
            return request.redirect('/page/show_registration')

        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']  # Allow in description

        values = {}

        for field_name, field_value in post.items():
            if field_name in request.registry['res.users']._fields and field_name not in _BLACKLIST:
                values[field_name] = field_value

        values["login"] = values['email'].lower()
        values["email"] = values['email'].lower()
        values["share"] = False
        values["data_usage_approval"] = True
        values["name"] = env['res.partner'].sudo()._get_computed_name(values['firstname'],values['lastname'])
        user_id = self.create_respondent(request, values, post)
        respondent = env['res.users'].sudo().browse(user_id)
        
        route = '/page/registration_confirmation'
        token = random_token()
        token_url = self.token_url(env, route, token) + '&password='+post.get("password")
        expiration_date = datetime.date.today() + datetime.timedelta(days=3)
        respondent.partner_id.sudo().write({'is_respondent':True,
                                            'signup_token':token,
                                            'registration_validation_url':token_url,
                                            'validation_url_expiration':expiration_date,
                                            'birthdate':values['birthdate']})
        
        email_template = env['email.template'].sudo().search([('name', '=', 'Confirmation Email')])[0]
        email_template.send_mail(user_id, False)
        
        respondent.partner_id.sudo().write({'active':False})
        respondent.sudo().write({'active':False})
        
        # return request.website.render(post.get("view_callback", "defiline.registration_thanks"), values)
        return request.redirect('/page/thankyou')

    @http.route(['/page/thankyou'], type='http', auth="public", website=True)
    def show_page_thankyou(self, **kwargs):
        return request.website.render("defiline.registration_thanks")
        
    @http.route(['/page/registration_confirmation'],  type='http', auth="public", website=True)
    def registration_confirmation(self, **kwargs):
        """ find the partner corresponding to a token, and possibly check its validity  """
        env, db, context = request.env, request.db, request.context
        partner_obj = env['res.partner']
        token = request.params.get('token')
        password = request.params.get('password')
        partner = partner_obj.sudo().search([('signup_token', '=', token),('active','=',False)])
        if not partner:
            # if not partner then we search without the (active = False) domain filter
            partner = partner_obj.sudo().search([('signup_token', '=', token)])
        if not partner:
            # redirect to a error page
            return request.website.render("defiline.registration_confirmation_error")
        if partner.token_validated:
            return request.website.render("defiline.registration_confirmation_already_done")
        sequence = env['ir.sequence'].sudo().search([('code','=','respondent.reference')])[0]
        partner_ref = request.registry['ir.sequence'].next_by_id(request.cr,SUPERUSER_ID,sequence.id)
        partner.sudo().write({'active':True, 'token_validated':True,'ref_number':int(partner_ref)})
        user = env['res.users'].sudo().search([('partner_id', '=', partner.id),('active','=',False)])
        user.sudo().write({'active':True})
        request.cr.commit()
        request.session.authenticate(request.session.db, user.login, password)

        return request.redirect('/page/myprofile')
    
    def get_profile_display_info(self, request):
        uid, env = request.uid, request.env
        values = {}
        errors = {}
            
        user = env['res.users'].sudo().browse(uid)
        fields_desc = env['res.partner'].sudo().fields_get(['marital_status','professional_status','availability', 'gender'])
        values['marital_statuses'] = fields_desc['marital_status']['selection']
        values['professional_statuses'] = fields_desc['professional_status']['selection']
        values['availabilities'] = fields_desc['availability']['selection']
        values['partner'] = user.partner_id
        values['errors'] = errors
        values['better_zips'] = env['res.better.zip'].sudo().search([('name','=',user.partner_id.zip)]) 
        values['titles']= env['res.partner.title'].sudo().search([('domain','=','contact')])
        values['countries'] = env['res.country'].sudo().search([])
        values['genders'] = fields_desc['gender']['selection']
        values['edu_levels'] = env['res.partner.education.level'].sudo().search([])
        values['langs'] = env['res.lang'].sudo().search([])
        values['children'] = self.format_children(user,values['genders'])
        
        return values
    
    @http.route(['/page/myprofile'], type='http', auth="user", website=True)
    def show_profile(self, **kwargs):
        values = self.get_profile_display_info(request)
        
        return request.website.render("defiline.profile_respondent", values)
    
    def format_children(self, user, genders):
        numberofchildren = user.partner_id.numberofchildren
        gender_dic = {}
        fields = []

        for gender in genders:
            gender_dic[gender[0]] = gender[1]

        i=1 
        while i <= numberofchildren :
            fields.append('child'+str(i)+'_yearofbirth')
            fields.append('child'+str(i)+'_gender')
            i+=1
        partner_field_values = user.partner_id.read(fields)[0]
        i = 1
        children = ''
        while i <= numberofchildren :
            children += partner_field_values['child'+str(i)+'_yearofbirth']
            children += partner_field_values['child'+str(i)+'_gender']
            if i < numberofchildren:
                children += ','
            i+=1
        return children

    @http.route(['/page/delete_profile'], methods=['POST'], type='http', auth="user", website=True)
    def delete_profile(self):
        uid, env = request.uid, request.env
        request.session.logout(keep_db=True)
        #delete user and partner
        user = env['res.users'].sudo().browse(uid)
        partner = env['res.partner'].sudo().browse(user.partner_id.id)
        change_pass_wiz = env['change.password.user'].sudo().search([('user_login', '=', user.login)])
        if change_pass_wiz:
            change_pass_wiz.sudo().unlink()
        partner.sudo().unlink()
        
        # redirect to Homepage
        return werkzeug.utils.redirect('/', 303)

    @http.route(['/page/data_usage_approval'], methods=['POST'], type='http', auth="user", website=True)
    def data_usage_approval(self):
        uid, env = request.uid, request.env
        values = {}

        user = env['res.users'].sudo().browse(uid)
        user.partner_id.sudo().write({'data_usage_approval':True})

        values = self.get_profile_display_info(request)
        values['success'] = True

        return request.website.render("defiline.profile_respondent", values)

    @http.route(['/page/data_usage_confirmation'],  type='http', auth="public", website=True)
    def data_usage_confirmation(self, **kwargs):
        env = request.env
        token = request.params.get('data_usage_token')
        partner = env['res.partner'].sudo().search([('data_usage_token', '=', token)])
        if not partner:
            # redirect to a error page
            return request.website.render("defiline.data_usage_error")
        if partner.data_usage_approval:
            return request.website.render("defiline.data_usage_confirmation_already_done")
        partner.sudo().write({'data_usage_approval':True})

        return request.redirect('defiline.data_usage_confirmation_ok')

    @http.route(['/page/data_usage_delete'],  type='http', auth="public", website=True)
    def data_usage_delete(self, **kwargs):
        env = request.env
        token = request.params.get('data_usage_token')
        partner = env['res.partner'].sudo().search([('data_usage_token', '=', token)])
        if not partner:
            # redirect to a error page
            return request.website.render("defiline.data_usage_error")
        if partner.data_usage_approval:
            return request.website.render("defiline.data_usage_confirmation_already_done")
        partner.sudo().unlink()

        return request.redirect('defiline.data_usage_delete_ok')

    @http.route(['/page/save_profile'], methods=['POST'], type='http', auth="user", website=True)
    def save_profile(self, **post):
        cr, uid, context, env = request.cr, request.uid, request.context, request.env  
        values = {}
        result = {}
        user = env['res.users'].sudo().browse(uid)
        #"children"
        res_partner_fields = env['res.partner'].fields_get()
        for field in PROFILE_FIELDS:
            if field == 'children':
                children = [] 
                if post.get(field):
                    children = post.get(field).split(',')
                i = 0
                for child in children:
                    i +=1
                    values['child'+str(i)+'_yearofbirth'] = child[0:4]
                    values['child'+str(i)+'_gender'] = child[4:5]
                values['numberofchildren'] = i    
            elif field == 'mobile':
                mobile = re.sub('[^0-9]+', '', post.get("mobile"))
                if mobile.startswith('00'):
                    values[field] = mobile[2:len(mobile)]
                elif mobile.startswith('0'):
                    values[field] = '32' + mobile[1:len(mobile)]
                elif mobile.startswith('+'): 
                    values[field] = mobile[1:len(mobile)]
            elif field == 'hypermarket':
                if post.get(field) == 'Other':
                    values[field] = post.get('hypermarket_other')
                else:
                    values[field] = post.get(field)
            elif res_partner_fields[field]['type'] == 'boolean':
                if post.get(field) and (post.get(field) == 'True' or post.get(field) == 'on'):
                    values[field] = True
                else:
                    values[field] = False
            elif res_partner_fields[field]['type'] == 'many2one':
                if post.get(field) and post.get(field) != '':
                    values[field] = post.get(field)
                else:
                    values[field] = False
            elif field == 'image' and post.get(field).filename != '':
                values[field] = base64.encodestring(post.get(field).read())
            elif post.get(field):
                values[field] = post.get(field)
        values['profile_last_update'] = datetime.date.today()
        user.partner_id.sudo().write(values)
        
        #reload data from db
        values = self.get_profile_display_info(request)
        values['success'] = True
        
        return request.website.render("defiline.profile_respondent", values)
