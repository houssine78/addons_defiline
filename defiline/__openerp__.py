# -*- coding: utf-8 -*-
##############################################################################
#
#    NetSkill Group, Business Open Source Solution
#    Copyright (C) 2015-2016 NetSkill Group sprl.
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
{
    'name': 'Defiline customization',
    'description': 'This module aims cutomize Odoo to Defiline needs',
    'category': 'Survey',
    'version': '8.0.1.0.3',
    'author': 'Houssine BAKKALI',
    'depends': ['base','mail','sale','account','event_sale','sale_layout','website','survey', 'base_location',
                'partner_firstname'],
    'data': [
        'security/defiline_security.xml',
        'security/ir.model.access.csv',
        'data/defiline_data.xml',
        'view/survey_templates.xml',
        'view/survey_views.xml',
        'view/postit_templates.xml',
        'view/respondent_templates.xml',
        'view/respondent_views.xml',
        'view/mission_views.xml',
        'view/moderator_views.xml',
        'view/contact_views.xml',
        'view/event_view.xml',
        'view/operational_flow_view.xml',
        'view/sale_order_view.xml',
        'wizard/add_calls_wizard.xml',
        'wizard/search_ref_wizard.xml',
        'wizard/add_respondents_wizard.xml',
        'wizard/import_respondents_wizard.xml',
        'wizard/import_wizard.xml',
        'wizard/admin_wizard.xml',
        'report/report_sale_order.xml',
        'report/report_quotation_layouted.xml',
    ],
    'installable' : True,
    'application' : True,
}