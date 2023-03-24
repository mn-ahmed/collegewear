# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    type = fields.Selection(
        [('new_cancel', 'New Order and Cancel Selected'), ('new_delete', 'New order and Delete all selected order'),
         ('exist_cancel', 'Merge order on existing selected order and cancel others'),
         ('exist_delete', 'Merge order on existing selected order and delete others')], 'Default Merge Type',
        required=True,related="company_id.type",readonly=False)

    notify = fields.Boolean(string="Notify in Chatter",related="company_id.notify",readonly=False)

class Company(models.Model):
    _inherit = 'res.company'
    
    type = fields.Selection(
        [('new_cancel', 'New Order and Cancel Selected'), ('new_delete', 'New order and Delete all selected order'),
         ('exist_cancel', 'Merge order on existing selected order and cancel others'),
         ('exist_delete', 'Merge order on existing selected order and delete others')], 'Default Merge Type',
        required=True)

    notify = fields.Boolean(string="Notify in Chatter")

    