# -*- coding: utf-8 -*-
from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _sid_get_purchase_target_move_date(self, changed_vals=None):
        self.ensure_one()
        if self.state != "purchase":
            return False
        if getattr(self, "product_type", False) == "service":
            return False

        changed_vals = changed_vals or {}

        if "contract_date" in changed_vals:
            return self.contract_date or False
        if "estimated_date" in changed_vals:
            return self.estimated_date or False
        if "state" in changed_vals:
            return self.contract_date or self.estimated_date or False

        return self.contract_date or self.estimated_date or False

    def _sid_get_purchase_sync_moves(self):
        self.ensure_one()
        return self.env["stock.move"].sudo().search([
            ("purchase_line_id", "=", self.id),
            ("state", "not in", ["done", "cancel"]),
            ("picking_type_id.code", "in", ["incoming", "internal"]),
        ])

    def _sid_sync_purchase_move_dates(self, changed_vals=None):
        for line in self:
            target_date = line._sid_get_purchase_target_move_date(changed_vals=changed_vals)
            if not target_date:
                continue
            moves = line._sid_get_purchase_sync_moves()
            if moves:
                moves.write({"date": target_date})

    def write(self, vals):
        tracked_keys = {"contract_date", "estimated_date", "state", "product_type"}
        must_sync = bool(tracked_keys.intersection(vals))
        res = super().write(vals)
        if must_sync:
            self._sid_sync_purchase_move_dates(changed_vals=vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line, vals in zip(lines, vals_list):
            if line.state == "purchase":
                line._sid_sync_purchase_move_dates(changed_vals=vals)
        return lines
