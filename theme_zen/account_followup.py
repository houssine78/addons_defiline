# -*- coding: utf-8 -*-
import time
from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class res_partner(models.Model):

    _inherit = 'res.partner'   

    def do_partner_print(self, cr, uid, wizard_partner_ids, data, context=None):
        #wizard_partner_ids are ids from special view, not from res.partner
        if not wizard_partner_ids:
            return {}
        data['partner_ids'] = wizard_partner_ids
        datas = {
             'ids': wizard_partner_ids,
             'model': 'account_followup.followup',
             'form': data
        }
        
        report_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('model', '=', 'account_followup.followup'),('is_default','=',True)], limit=1)
        if not report_ids:
            report_ids = self.pool.get('ir.actions.report.xml').search(cr, uid, [('model', '=', 'account_followup.followup')], limit=1)
        report_obj = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_ids[0], context=context)
        return self.pool['report'].get_action(cr, uid, [], report_obj.report_name, data=datas, context=context)

