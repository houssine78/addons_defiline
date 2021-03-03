# -*- coding: utf-8 -*-
# Copyright 2019-2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
# License OPL-1 (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#odoo-apps) for derivative work.

import requests
# The file name is choosen in favor of model name in next odoo versions
from openerp import api, models


class IrActionsServer(models.Model):

    _inherit = "ir.actions.server"

    @api.model
    def _get_eval_context(self, action=None):
        eval_context = super(IrActionsServer, self)._get_eval_context(action)

        def make_request(*args, **kwargs):
            return requests.request(*args, **kwargs)

        eval_context["make_request"] = make_request
        return eval_context
