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
from openerp import models, fields, api, _

class operational_flow(models.Model):
    _name="operational.flow"
    
    @api.multi
    def _get_invoice(self):
        for flow in self:
            if len(flow.order_id.invoice_ids) > 0:
                flow.invoice = flow.order_id.invoice_ids[0]
    
    @api.multi
    def _compute_product(self):
        for flow in self:
            for order_line in flow.focus_group_id.sale_order_lines:
                if order_line.product_id.categ_id.name == 'Recruitment':
                    flow.recruitment_price = order_line.price_unit
                    flow.recruitment_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Listing':
                    flow.listing_price = order_line.price_unit
                    flow.listing_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Incentive Effective':
                    flow.incitive_price = order_line.price_unit
                    flow.incitive_qty_order = order_line.product_uom_qty 
                elif order_line.product_id.categ_id.name == 'Incentive Backup':
                    flow.incitive_bkp_price = order_line.price_unit
                    flow.incitive_bkp_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Managing fee':
                    flow.managing_fee_price = order_line.price_unit
                    flow.managing_fee_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Catering Sandwiches':
                    flow.cat_san_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Catering take away':
                    flow.cat_trait_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Catering fruits/desserts':
                    flow.cat_fruit_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Catering Exceptional':
                    flow.cat_excep_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Catering drink package':
                    flow.cat_drink_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Note taking':
                    flow.note_taking_price = order_line.price_unit
                    flow.note_taking_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Facility':
                    flow.facility_price = order_line.price_unit
                    flow.facility_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Streaming':
                    flow.streaming_price = order_line.price_unit
                    flow.streaming_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Overdue':
                    flow.overdue_price = order_line.price_unit
                    flow.overdue_qty_order = order_line.product_uom_qty
                elif order_line.product_id.categ_id.name == 'Photocopy':
                    flow.copy_price = order_line.price_unit
                    flow.copy_qty_order = order_line.product_uom_qty   
        
            for invoice_line in flow.focus_group_id.invoice_lines:
                if invoice_line.product_id.categ_id.name == 'Recruitment':
                    flow.recruitment_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Listing':   
                    flow.listing_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Incentive Effective':   
                    flow.incitive_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Incentive Backup':   
                    flow.incitive_bkp_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Managing fee':
                    flow.managing_fee_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Catering Sandwiches':
                    flow.cat_san_price = invoice_line.price_unit
                    flow.cat_san_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Catering take away':
                    flow.cat_trait_price = invoice_line.price_unit
                    flow.cat_trait_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Catering fruits/desserts':
                    flow.cat_fruit_price = invoice_line.price_unit
                    flow.cat_fruit_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Catering Exceptional':
                    flow.cat_excep_price = invoice_line.price_unit
                    flow.cat_excep_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Catering drink package':
                    flow.cat_drink_price = invoice_line.price_unit
                    flow.cat_drink_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Note taking':
                    flow.note_taking_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Facility':
                    flow.facility_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Streaming':
                    flow.streaming_qty_invoice = invoice_line.quantity    
                elif invoice_line.product_id.categ_id.name == 'Overdue':
                    flow.overdue_qty_invoice = invoice_line.quantity
                elif invoice_line.product_id.categ_id.name == 'Photocopy':
                    flow.copy_qty_invoice = invoice_line.quantity
    
    focus_group_id = fields.Many2one('event.event', string='Focus group')
    focus_group_name = fields.Char(related='focus_group_id.name', string='Focus-group')
    focus_group_manager = fields.Many2one(related='focus_group_id.user_id', string='Responsible')
    focus_group_start_date = fields.Datetime(related='focus_group_id.start_date')
    focus_group_end_date = fields.Datetime(related='focus_group_id.end_date')
    focus_group_address_id = fields.Many2one(related='focus_group_id.address_id')
    mission_id = fields.Many2one(related='focus_group_id.mission_id', string="Survey")
    order_id = fields.Many2one('sale.order', string='Sale Order')
    customer = fields.Many2one(related='order_id.partner_id', string="Customer")
    customer_ref = fields.Char(related='customer.ref', string='Customer Reference')
    #sale_order_name = fields.Char(related='sale_order_id.name', string='Sale Order Name')
    quotation_request_date = fields.Date(related='order_id.request_date',string="Request Date")
    order_date_sent = fields.Date(related='order_id.date_sent', string='Sent Date')
    order_date_confirm = fields.Date(related='order_id.date_confirm',string="Confirmation Date")
    po_number = fields.Char(related='order_id.po_number', string='PO Number')
    material_received_date = fields.Date(related='mission_id.material_received')
    mission_description_date = fields.Date(related='mission_id.description_date')
    google_form_date = fields.Date(related='mission_id.google_form_date')
    postit_online = fields.Date(related='focus_group_id.date_begin')
    emailing_date = fields.Date(related='focus_group_id.emailing_date')
    recruitment_date = fields.Date(related='mission_id.recruitment_date')
    group_sent_date = fields.Date(related='mission_id.group_sent_date')
    group_confirmation_date = fields.Date(related='focus_group_id.confirmation_date')
    invoice = fields.Many2one(compute='_get_invoice', comodel_name='account.invoice')
    invoice_state = fields.Selection(related='invoice.state')
    invoice_date = fields.Date(related='invoice.date_invoice')
    recruitment_price = fields.Float(compute='_compute_product', string='Recruitment price')
    recruitment_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    recruitment_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    listing_price = fields.Float(compute='_compute_product', string='Listing price')
    listing_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    listing_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    incitive_price = fields.Float(compute='_compute_product', string='Incitive price')
    incitive_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    incitive_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    incitive_bkp_price = fields.Float(compute='_compute_product', string='Incitive Backup price')
    incitive_bkp_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    incitive_bkp_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    managing_fee_price = fields.Float(compute='_compute_product', string='Managing fee price')
    managing_fee_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    managing_fee_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    cat_san_price = fields.Float(compute='_compute_product', string='Catering Sandwiches price')
    cat_san_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    cat_san_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    cat_trait_price = fields.Float(compute='_compute_product', string='Catering Caterer price')
    cat_trait_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    cat_trait_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    cat_fruit_price = fields.Float(compute='_compute_product', string='Catering desserts price')
    cat_fruit_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    cat_fruit_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    cat_excep_price = fields.Float(compute='_compute_product', string='Catering Exceptional price')
    cat_excep_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    cat_excep_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    cat_drink_price = fields.Float(compute='_compute_product', string='Catering Exceptional price')
    cat_drink_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    cat_drink_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    note_taking_price = fields.Float(compute='_compute_product', string='Note taking price')
    note_taking_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    note_taking_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    facility_price = fields.Float(compute='_compute_product', string='Facility price')
    facility_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    facility_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    streaming_price = fields.Float(compute='_compute_product', string='Streaming price')
    streaming_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    streaming_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    overdue_price = fields.Float(compute='_compute_product', string='Facility overdue price')
    overdue_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    overdue_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')
    copy_price = fields.Float(compute='_compute_product', string='Photocopy price')
    copy_qty_order = fields.Integer(compute='_compute_product', string='Quotation quantity')
    copy_qty_invoice = fields.Integer(compute='_compute_product', string='Invoice quantity')