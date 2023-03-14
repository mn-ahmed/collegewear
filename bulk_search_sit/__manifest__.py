# -*- coding: utf-8 -*-
{
    'name': 'Bulk Search with comma separated',
    'category' : 'General',
    'summary' : """ Records bulk search on any page/model.
    """,
    'description': """
                Search for records in bulks on any page/model easily.
    """,
    'version': '15.0.1.0.0',
    'live_test_url': 'https://silentinfotech.com/blog/bulk-search-record/',
    'website': 'https://silentinfotech.com',
    'author': 'Silent Infotech Pvt. Ltd.',
    'price': 5.00,
    'currency': 'USD',
    'depends': ['base'],
    'data': [
             ], 
    'images': ['static/description/banner.png'],
    'license': u'OPL-1',
    'application': True,
    'auto_install': False,
    'installable': True,
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'test': [],
    'assets': {
       'web.assets_backend': {
           '/bulk_search_sit/static/src/js/systray.js',
       },
       'web.assets_qweb': {
           '/bulk_search_sit/static/src/xml/systray.xml',
       },
    },

    
}


