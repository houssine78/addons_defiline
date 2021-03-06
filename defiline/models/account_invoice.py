# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    po_number = fields.Char(string="PO Number")


class AccountInvoiceLine(models.Model):
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
    event_id = fields.Many2one('event.event',
                               string='Group')
    

    @api.model
    def create(self,vals):
        invoice_line = super(AccountInvoiceLine,self).create(vals)
        if self.event_id:
            invoice_lines = self.search([('event_id','=',self.event_id)])
            line = invoice_lines[0]
            self.write(self.id,{'invoice_id': line.invoice_id})
        return invoice_line
