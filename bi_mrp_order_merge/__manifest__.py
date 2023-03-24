# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Merge Manufacturing Orders in Odoo",
    "version" : "15.0.0.1",
    "category" : "Manufacturing",
    'summary': 'Merge Order Merge MRP order Merge MO Merge Manufacturing merger MO Merge multiple Manufacturing orders merge combine Manufacturing merge mrp orders merge production order merge Manufacturing orders merge combine MRP order combine MO merge multiple MO merge',
    "description": """
    
        Merge manufacturing orders in odoo,
        Default Merge Type in odoo,
        Notify in Chatter in odoo,
        New Order and Cancel Selected Orders in odoo,
        New Order and Delete Selected Orders in odoo,
        Merge Order on Existing Selected Order and Cancel Others in odoo,
        Merge Order on Existing Selected Order and Delete Others in odoo,
    
    """,
    "author": "BrowseInfo",
    'website': 'https://www.browseinfo.in',
    "price": 15,
    "currency": 'EUR',
    "depends" : ['base','mrp'],
    "data": [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'wizard/merge_mrp.xml',
    ],
    "license":'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/tm14uKesqSE',
    "images":["static/description/Banner.png"],
    'license': 'OPL-1',
}

