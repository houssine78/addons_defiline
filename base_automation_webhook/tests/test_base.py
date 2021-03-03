# -*- coding: utf-8 -*-
# Copyright 2019-2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
# License OPL-1 (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#odoo-apps) for derivative work.

from openerp.tests.common import TransactionCase


class TestAutomation(TransactionCase):
    at_install = True
    post_install = True

    def test_requests(self):
        """Check that requests package is available"""
        self.env["res.partner"].create({"name": "New Contact"})
