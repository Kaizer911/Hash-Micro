# See LICENSE file for full copyright and licensing details.

{
    "name": "Booking Order",
    "version": "1.0.0.0",
    "author": "Kaizer",
    "category": "Booking Order",
    "depends": ["sale", "sale_management"],
    "license": "LGPL-3",
    "summary": "Booking Order",
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "report/work_order_report_templates.xml",
        "report/work_order_report.xml",
        "views/work_order.xml",
        "views/service_team.xml",
        "views/sale_order.xml",
        "views/actions.xml",
        "views/menus.xml",
        "wizard/booking_cancellation.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
    "application": True,
}
