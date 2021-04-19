# -*- coding: utf-8 -*-
   
import time
from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class account_invoice(models.Model):

    _inherit = 'account.invoice'   

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        report_obj = self.env['ir.actions.report.xml'].search([('model', '=', 'account.invoice')])
        return self.env['report'].get_action(self, report_obj.report_name)

