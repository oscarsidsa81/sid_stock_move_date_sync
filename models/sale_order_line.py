# -*- coding: utf-8 -*-
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _sid_get_sale_target_move_date(self, changed_vals=None):
        self.ensure_one()
        if self.state != "sale":
            return False
        if getattr(self, "product_type", False) == "service":
            return False

        date_1 = getattr(self, "estimated_delivery_date", False)
        date_2 = getattr(self, "calculated_date", False)
        candidates = [d for d in [date_1, date_2] if d]
        return max(candidates) if candidates else False

    def _sid_get_sale_sync_moves(self):
        self.ensure_one()
        return self.env["stock.move"].sudo().search([
            ("sale_line_id", "=", self.id),
            ("state", "not in", ["done", "cancel"]),
            ("picking_type_id.code", "=", "outgoing"),
            ("location_dest_id.usage", "=", "customer"),
        ])

    def _sid_sync_sale_move_dates(self, changed_vals=None):
        for line in self:
            target_date = line._sid_get_sale_target_move_date(changed_vals=changed_vals)
            if not target_date:
                continue
            moves = line._sid_get_sale_sync_moves()
            if moves:
                moves.write({"date": target_date})

    def write(self, vals):
        tracked_keys = {"estimated_delivery_date", "calculated_date", "state", "product_type"}
        must_sync = bool(tracked_keys.intersection(vals))
        res = super().write(vals)
        if must_sync:
            self._sid_sync_sale_move_dates(changed_vals=vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line, vals in zip(lines, vals_list):
            if line.state == "sale":
                line._sid_sync_sale_move_dates(changed_vals=vals)
        return lines
