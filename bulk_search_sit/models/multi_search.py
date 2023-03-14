# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

from odoo.osv import expression
from odoo.osv.query import Query
from odoo.models import BaseModel, api

@api.model
def _where_calc(self, domain, active_test=True):

	"""Computes the WHERE clause needed to implement an OpenERP domain.
	:param domain: the domain to compute
	:type domain: list
	:param active_test: whether the default filtering of records with ``active``
						field set to ``False`` should be applied.
	:return: the query expressing the given domain as provided in domain
	:rtype: osv.query.Query
	"""
	# if the object has an active field ('active', 'x_active'), filter out all
	# inactive records unless they were explicitly asked for
	if self._active_name and active_test and self._context.get('active_test', True):
		# the item[0] trick below works for domain items and '&'/'|'/'!'
		# operators too
		if not any(item[0] == self._active_name for item in domain):
			domain = [(self._active_name, '=', 1)] + domain
	self.env.cr.execute(
		"SELECT id FROM ir_module_module WHERE name='bulk_search_sit' and state='installed' limit 1")
	is_multi_search_installed = self.env.cr.fetchone()
	if domain:
		modified_domain = []
		# _logger.info(str(domain))
		for domain_tuple in domain:
			if not is_multi_search_installed:
				modified_domain.append(domain_tuple)
				continue
			if type(domain_tuple) in (list, tuple):
				if str(domain_tuple[1]) == 'ilike' or str(domain_tuple[0]) == 'partner_id' and  str(domain_tuple[1]) == 'child_of':
					if isinstance(domain_tuple[2],(list,tuple,str,dict)):
						multi_name = domain_tuple[2].split(',')
						len_name = len(multi_name) - 1
						if len_name >= 1:
							for length in multi_name:
								modified_domain.append('|')
							for f_name in multi_name:
								modified_domain.append([domain_tuple[0], domain_tuple[1], f_name.strip()])

			modified_domain.append(domain_tuple)
			domain = modified_domain
		return expression.expression(domain, self).query
	else:
		return Query(self.env.cr, self._table, self._table_query)

BaseModel._where_calc = _where_calc
	
