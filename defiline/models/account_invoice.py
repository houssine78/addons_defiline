# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    po_number = fields.Char(string="PO Number")


class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"

    state = fields.Selection(related='invoice_id.state',
                             readonly=True,
                             store=True,
                             copy=False)
    date_invoice = fields.Date(related='invoice_id.date_invoice',
                                    readonly=True,
                                    store=True,
                                    copy=False)
    number = fields.Char(related='invoice_id.number',
                         store=True,
                         readonly=True,
                         copy=False)
    journal_id = fields.Many2one(related='invoice_id.journal_id',
                                 store=True,
                                 readonly=True,
                                 copy=False)