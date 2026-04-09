# -*- coding: utf-8 -*-
{
    "name": "sid_stock_move_date_sync",
    "version": "15.0.1.0.0",
    "category": "Stock",
    "summary": "Sincroniza fechas de lineas de compra/venta con movimientos de stock.",
    "author": "ovilches81",
    "license": "LGPL-3",
    "depends": [
        "stock",
        "purchase_stock",
        "sale_stock",
        "sid_purchase_core",
        "sid_sale_line_core",
        "oct_fecha_contrato_compras",
        "oct_fecha_contrato_ventas",
    ],
    "data": [],
    "post_init_hook": "post_init_sync_stock_move_dates",
    "installable": True,
    "application": False,
}
