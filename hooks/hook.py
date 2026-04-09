# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_sync_stock_move_dates(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    purchase_lines = env["purchase.order.line"].search([
        ("state", "=", "purchase"),
        ("product_type", "!=", "service"),
    ])
    purchase_lines._sid_sync_purchase_move_dates()

    sale_lines = env["sale.order.line"].search([
        ("state", "=", "sale"),
        ("product_type", "!=", "service"),
    ])
    sale_lines._sid_sync_sale_move_dates()
