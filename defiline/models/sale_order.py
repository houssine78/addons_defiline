# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import orm
from openerp.exceptions import except_orm
from openerp import SUPERUSER_ID

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    po_number = fields.Char(string="PO Number")

class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.one
    @api.depends('partner_id')
    def _compute_ref(self):
        if self.partner_id.parent_id:
            self.funct_ref = self.partner_id.parent_id.ref
        else:
            self.funct_ref = self.partner_id.ref
            
    customer_ref = fields.Char(related='partner_id.ref', string='Customer Reference')
    funct_ref = fields.Char(string="Customer Reference", readonly=True, compute='_compute_ref')
    po_number = fields.Char(string='PO Number')
    subject = fields.Char(string='Offer subject')
    date_order = fields.Date(string='Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Date.today)
    quotation_validity = fields.Char(string='Quotation Validity')
    informal_order_lines = fields.One2many('informal.sale.order.line', 'order_id', string='Informal order lines',copy=True)
    mission_id = fields.Many2one('mission.mission', string='Project',copy=False)
    date_sent = fields.Date(string="Sent Date", readonly=True, select=True, copy=False, help="Date on which quotation is sent.")
    request_date = fields.Date(string="Request Date", select=True, copy=False, help="Date on which quotation request has been received.")
    allow_survey_creation = fields.Boolean(compute='_allow_survey_creation',string="Allow survey creation", store=True)
    allow_invoice_creation = fields.Boolean(compute='_allow_invoice_creation',string="Allow invoice creation", store=True)
    is_survey = fields.Boolean(string="is a Project?", default=True) 
    
    @api.multi
    @api.depends('state', 'mission_id', 'is_survey')
    def _allow_survey_creation(self):
        if self.state == 'manual' and self.is_survey == True and (self.mission_id != None or len(self.mission_id.ids) > 0):
            self.allow_survey_creation = True
        else:
            self.allow_survey_creation = False
            
    @api.multi
    @api.depends('is_survey')
    def _allow_invoice_creation(self):
        if self.is_survey == False :
            self.allow_invoice_creation = True
        else:
            self.allow_invoice_creation = False
            
    @api.multi
    def action_quotation_send(self):
        self.date_sent = fields.Date.context_today(self)
        return super(sale_order, self).action_quotation_send()
    
    @api.one
    def print_quotation(self):
        self.date_sent = fields.Date.context_today(self)
        return super(sale_order, self).print_quotation()
    
    @api.v7
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=None)
        invoice_vals['comment'] = ""
        return invoice_vals
    
    def make_invoices(self):

        if self.state != 'manual':
            raise except_orm(_('Warning!'), _("You shouldn't manually invoice the following sale order %s") % (self.name))

        self.action_invoice_create()

        # Dummy call to workflow, will not create another invoice but bind the new invoice to the subflow
        self.signal_workflow('manual_invoice')

        return True
    
    def check_section_on_lines(self):
        for line in self.order_line:
            if line.sale_layout_cat_id == None or line.sale_layout_cat_id == False or len(line.sale_layout_cat_id) == 0:
                raise except_orm(_('Warning!'), 
                        _("You haven't selected a section for the following sale order line '%s'."
                          " Please choose a section for this sale order line") % (line.name))
            elif line.sale_layout_cat_id.is_focus_group == False:
                raise except_orm(_('Warning!'), 
                        _("The selected section of the following sale order line '%s' is not of the type group."
                          " Please select a section of the type 'group' or select a proper section") % (line.name))
                
    @api.one
    def action_button_confirm(self):
        if self.is_survey:
            self.check_section_on_lines()
        
        return super(sale_order, self).action_button_confirm()
    
    @api.one
    def create_survey(self):
        mission_data = {}
        group_data = {}
        
        self.check_section_on_lines()
        
        mission_data['name'] = self.subject
        mission_data['partner_id'] = self.partner_id.id
        mission_data['manager_id'] = self.user_id.id
        mission_data['sale_order_id'] = self.id
        mission_id = self.env['mission.mission'].create(mission_data)

        self.write({'mission_id':mission_id.id})

        layout_cat_list = []
        for line in self.order_line:
            if line.sale_layout_cat_id.is_focus_group and line.sale_layout_cat_id not in layout_cat_list :
                layout_cat_list.append(line.sale_layout_cat_id)
         
        group_data['mission_id'] = mission_id.id
        group_data['customer_id'] = self.partner_id.id
        
        group_ids = []
        inc_eff_id = self.env['focus.group.product'].search([('type','=','incitive_eff')])[0].product_id.id
        inc_bkp_id = self.env['focus.group.product'].search([('type','=','incitive_bkp')])[0].product_id.id
        recruitment_id = self.env['focus.group.product'].search([('type','=','recruitment')])[0].product_id.id
        
        sequence_obj = self.pool.get('ir.sequence')
        sequence_id = sequence_obj.search(self.env.cr, SUPERUSER_ID, [('code','=','group.reference')])[0]
        
        for layout_cat_id in layout_cat_list:
            group_data['sale_layout_cat_id'] = layout_cat_id
            group_data['name'] = layout_cat_id.name
            #copy incentive price from order to group
            inc_eff_line = self.env['sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id),('product_id','=',inc_eff_id)])
            inc_bkp_line = self.env['sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id),('product_id','=',inc_bkp_id)])
            recuitment_line = self.env['sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id),('product_id','=',recruitment_id)])
            
            if inc_eff_line:
                group_data['incentive'] = inc_eff_line[0].price_unit
            else:
                inc_eff_line = self.env['informal.sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id),('product_id','=',inc_eff_id)])
                if inc_eff_line:
                    group_data['incentive'] = inc_eff_line[0].price_unit
            
            if inc_bkp_line:
                group_data['incentive_backup'] = inc_bkp_line[0].price_unit
            else:
                inc_bkp_line = self.env['informal.sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id),('product_id','=',inc_bkp_id)])
                if inc_bkp_line:
                    group_data['incentive_backup'] = inc_bkp_line[0].price_unit
            
            if recuitment_line:
                group_data['recruitment'] = recuitment_line[0].product_uos_qty
                
            group = self.env['event.event'].create(group_data)
            line_ids = self.env['sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id)])
            informal_line_ids = self.env['informal.sale.order.line'].search([('order_id','=',self.id),('sale_layout_cat_id','=',layout_cat_id.id)])
            line_ids.write({'event_id':group.id})
            informal_line_ids.write({'event_id':group.id})
            
            group_data['reference_number'] = sequence_obj.next_by_id(self.env.cr,SUPERUSER_ID,sequence_id)
            group.write(group_data)
            
            group_data['incentive'] = False
            group_data['incentive_backup'] = False
            group_ids.append(group.id)
        
        for group_id in group_ids:
            self.env['operational.flow'].create({'order_id':self.id,'focus_group_id':group_id})
        
        self.make_invoices()
            
class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    event_id = fields.Many2one('event.event', string='Group')
    
    # we override the button_confirm method of the event_sale module as it doesn't correspond 
    # to what is needed. 
    @api.one
    def button_confirm(self):
        self.state = 'confirmed'
    
class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        """Save the layout when converting to an invoice line."""
        invoice_vals = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        if line.event_id:
            invoice_vals['event_id'] = line.event_id.id
            invoice_vals['name'] = line.name
        return invoice_vals
    
class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
     
    event_id = fields.Many2one('event.event', string='Group')
    
    @api.model
    def create(self,vals):
        invoice_line = super(account_invoice_line,self).create(vals)
        if self.event_id:
            invoice_lines = self.search([('event_id','=',self.event_id)])
            line = invoice_lines[0]
            self.write(self.id,{'invoice_id': line.invoice_id})
        return invoice_line
        
class SaleLayoutCategory(models.Model):
    _inherit = 'sale_layout.category'
     
    is_focus_group = fields.Boolean('Is group')

class focus_group_product(models.Model):
    _name = "focus.group.product"
    _description = "type"
     
    product_id = fields.Many2one('product.product', string='Product')

    type = fields.Selection([('facility','Facility'),
                             ('facility_supplement','Facility supplement'),
                             ('streaming','Streaming'),
                             ('translator','Translator'),
                             ('recruitment','Recruitment'),
                             ('listing','Listing initial fee'),
                             ('note_taking','Note taking'),
                             ('catering','Catering'),
                             ('incitive_eff','Incentive Effective'),
                             ('incitive_bkp','Incentive Backup'),
                             ('managing_fee','Managing fee'),
                             ],string='Type')    