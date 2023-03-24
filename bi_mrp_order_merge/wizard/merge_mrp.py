# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class MrpProductionMerge(models.TransientModel):
    _name = 'mrp.production.merge'
    _description = 'Merge MRP orders'

    def _default_merge_type(self):
        company = self.env.user.company_id
        if company.type:
            return company.type
        else:
            return 'new_cancel'

    mrp_to_merge = fields.Many2many('mrp.production',string='Orders to merge')
    type = fields.Selection(
        [('new_cancel', 'New Order and Cancel Selected'), ('new_delete', 'New order and Delete all selected order'),
         ('exist_cancel', 'Merge order on existing selected order and cancel others'),
         ('exist_delete', 'Merge order on existing selected order and delete others')], 'Merge Type',
        required=True,default=lambda self: self._default_merge_type())
    mrp_order = fields.Many2one('mrp.production', string='Merge with')
    location_src_id = fields.Many2one('stock.location', string='Components Location')
    location_dest_id = fields.Many2one('stock.location', string='Finished Products Location')

    @api.model
    def default_get(self, fields):
        rec = super(MrpProductionMerge, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        if active_ids:
            mrp_ids = []
            mrp_production = self.env['mrp.production'].browse(active_ids)
            mrp_production_obj = self.env['mrp.production'].browse(self._context.get('active_ids', []))
            mrp_states = []
            mrp_product = []
            mrp_bill = []
            for mrp in mrp_production:
                if mrp.product_id.id not in mrp_product:
                    mrp_product.append( mrp.product_id.id)
                if mrp.bom_id.id not in mrp_bill:
                    mrp_bill.append( mrp.bom_id.id)
                if mrp.state not in mrp_states:
                    mrp_states.append(mrp.state)
            if any(mrp.state == 'planned' or mrp.state == 'to_close' or mrp.state == 'done' or mrp.state == 'cancel' for mrp in mrp_production) or len(mrp_states)>1:
                raise UserError('Selected records state needs to be same either Draft, Confirmed or In Progress.')
            if len(mrp_product)>1 or len(mrp_bill)>1:
                raise UserError('You can only merge same product/bill of material manufacturing orders.')
            if len(mrp_production_obj) < 2:
                raise UserError('Please select multiple mrp orders to merge in the list view.')

            mrp_ids = [mrp.id for mrp in mrp_production]

            if 'mrp_to_merge' in fields:
                rec.update({'mrp_to_merge': mrp_ids})
        return rec

    def merge_mrp_orders(self):
        company = self.env.user.company_id
        mrp_obj = self.env['mrp.production']
        mod_obj = self.env['ir.model.data']
        stock_move_obj = self.env['stock.move']
        form_view_id = mod_obj._xmlid_to_res_id('mrp.mrp_production_form_view')
        mrp_production = mrp_obj.browse(self._context.get('active_ids', []))
        partners_list = []
        partners_list_write = []
        line_list = []
        cancel_list = []
        copy_list = []
        vals = {}
        customer_ref = []
        partner_name = False
        myString = ''

        if len(mrp_production) < 2:
            raise UserError('Please select multiple mrp orders to merge in the list view.')

        msg_origin = ""
        origin_list = []
        product_qty_list = []
        orignal_mrp_list = []
        for mrp in mrp_production:
            product_qty_list.append(mrp.product_qty)
            origin_list.append(mrp.name)
            orignal_mrp_list.append(mrp.id)
        
        if len(origin_list) == 1:
            msg_origin = msg_origin + origin_list[0] + "."
        elif len(origin_list) > 1:
            msg_origin = ', '.join(set(origin_list))

        if self.type == 'new_cancel':
            new_mrp = mrp_obj.create(
                {'product_id': mrp_production[0].product_id.id,'bom_id': mrp_production[0].bom_id.id,
                 'product_qty': sum(product_qty_list),'state': 'draft',
                 'product_uom_id':mrp_production[0].bom_id.product_uom_id.id,
                 'location_src_id':self.location_src_id.id,'location_dest_id':self.location_dest_id.id})
            for mrp in mrp_production:
                cancel_list.append(mrp)
                
                for line in mrp.move_raw_ids:
                    vals = {
                        'product_id': line.product_id.id or False,
                        'name':line.product_id.name or False,
                        'product_uom_qty': line.product_uom_qty or False,
                        'product_uom': new_mrp.bom_id.product_uom_id.id or False,
                        'location_id':line.location_id.id or False,
                        'location_dest_id':line.location_dest_id.id or False,
                        'production_id': new_mrp.id,
                        'origin': new_mrp.name
                    }
                    new_mrp.write({'move_raw_ids':[(0, 0, vals)],})
            
            if company.notify:
                msg_body = _("This mrp order has been created from: <b>%s</b>") % (msg_origin)
                new_mrp.message_post(body=msg_body)
            for orders in cancel_list:
                orders.action_cancel()

            result = {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_mrp.id,
            'views': [(False, 'form')],
            }
            return result

        if self.type == 'new_delete':
            new_mrp = mrp_obj.create(
                {'product_id': mrp_production[0].product_id.id,'bom_id': mrp_production[0].bom_id.id,
                 'product_qty': sum(product_qty_list),'state': 'draft',
                 'product_uom_id':mrp_production[0].bom_id.product_uom_id.id,
                 'location_src_id':self.location_src_id.id,'location_dest_id':self.location_dest_id.id})
            for mrp in mrp_production:
                cancel_list.append(mrp)
                for line in mrp.move_raw_ids:
                    vals = {
                        'product_id': line.product_id.id or False,
                        'name':line.product_id.name or False,
                        'product_uom_qty': line.product_uom_qty or False,
                        'product_uom': new_mrp.bom_id.product_uom_id.id or False,
                        'location_id':line.location_id.id or False,
                        'location_dest_id':line.location_dest_id.id or False,
                        'production_id': new_mrp.id,
                        'origin': new_mrp.name
                    }
                    new_mrp.write({'move_raw_ids':[(0, 0, vals)],})

            if company.notify:
                msg_body = _("This mrp order has been created from: <b>%s</b>") % (msg_origin)
                new_mrp.message_post(body=msg_body)
            if new_mrp.id in cancel_list:
                cancel_list.remove(new_mrp.id)
            for orders in cancel_list:
                for m_order in self.env['mrp.production'].browse(orders.id):
                    m_order.action_cancel()
                    m_order.unlink()
            result = {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_mrp.id,
            'views': [(False, 'form')],
            }
            return result

        if self.type == 'exist_cancel':
            if self.mrp_order.id not in orignal_mrp_list:
                product_qty_list.append(self.mrp_order.product_qty)
                
            for mrp in mrp_production:
                cancel_list.append(mrp.id)    
                for line in mrp.move_raw_ids:
                    if mrp.id != self.mrp_order.id:
                        vals = {
                        'product_id': line.product_id.id or False,
                        'name':line.product_id.name or False,
                        'product_uom_qty': line.product_uom_qty or False,
                        'product_uom': self.mrp_order.bom_id.product_uom_id.id or False,
                        'location_id':line.location_id.id or False,
                        'location_dest_id':line.location_dest_id.id or False,
                        'production_id': self.mrp_order.id,
                        'origin': self.mrp_order.name
                        }
                        self.mrp_order.write({'product_qty': sum(product_qty_list),'move_raw_ids':[(0, 0, vals)],})
            if company.notify:
                msg_body = _("This mrp order has been created from: <b>%s</b>") % (msg_origin)
                self.mrp_order.message_post(body=msg_body)
            if self.mrp_order.id in cancel_list:
                cancel_list.remove(self.mrp_order.id)
            for orders in cancel_list:
                for m_order in self.env['mrp.production'].browse(orders):
                    m_order.action_cancel()
            result = {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.mrp_order.id,
            'views': [(False, 'form')],
            }
            return result

        if self.type == 'exist_delete':
            if self.mrp_order.id not in orignal_mrp_list:
                product_qty_list.append(self.mrp_order.product_qty)
            for mrp in mrp_production:
                cancel_list.append(mrp.id)    
                for line in mrp.move_raw_ids:
                    if mrp.id != self.mrp_order.id:
                        vals = {
                            'product_id': line.product_id.id or False,
                            'name':line.product_id.name or False,
                            'product_uom_qty': line.product_uom_qty or False,
                            'product_uom': self.mrp_order.bom_id.product_uom_id.id or False,
                            'location_id':line.location_id.id or False,
                            'location_dest_id':line.location_dest_id.id or False,
                            'production_id': self.mrp_order.id,
                            'origin': self.mrp_order.name
                            }
                        self.mrp_order.write({'product_qty': sum(product_qty_list),'move_raw_ids':[(0, 0, vals)],})
            if company.notify:
                msg_body = _("This mrp order has been created from: <b>%s</b>") % (msg_origin)
                self.mrp_order.message_post(body=msg_body)
            if self.mrp_order.id in cancel_list:
                cancel_list.remove(self.mrp_order.id)
            for orders in cancel_list:
                for m_order in self.env['mrp.production'].browse(orders):
                    m_order.action_cancel()
                    m_order.unlink()
            result = {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.mrp_order.id,
            'views': [(False, 'form')],
            }
            return result