# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from datetime import datetime

class WorkOrder(models.Model):
    _name = "work.order"
    _description = "Work Order"

    name = fields.Char("WO Number", index=True)
    sale_order_id = fields.Many2one("sale.order", string="Booking Order Reference")
    service_team_id = fields.Many2one("service.team", "Team", required=True)
    team_leader_id = fields.Many2one("res.users", "Team Leader")
    team_member_ids = fields.Many2many("res.users", string="Team Members")
    date_planned_start = fields.Datetime(string="Planned Start", required=True)
    date_planned_end = fields.Datetime(string="Planned End", required=True)
    date_start = fields.Datetime(string="Date Start")
    date_end = fields.Datetime(string="Date End")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("inprogress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled")
        ], string='Status', readonly=True, copy=False, index=True, tracking=2, default='pending')
    notes = fields.Text(string="Notes")

    total_planned_days = fields.Integer(string='Total Booking Days', compute='_compute_total_planned_days', store=True, readonly=False, copy=False, tracking=True)
    total_working_days = fields.Integer(string='Total Working Days', compute='_compute_total_working_days', store=True, readonly=False, copy=False, tracking=True)


    @api.depends('date_planned_start', 'date_planned_end')
    def _compute_total_planned_days(self):
        for rec in self:
            if rec.date_planned_end and rec.date_planned_start:
                delta = abs(rec.date_planned_end - rec.date_planned_start)
                rec.total_planned_days = delta.days
            else:
                rec.total_planned_days = 0

    @api.depends('date_start', 'date_end')
    def _compute_total_working_days(self):
        for rec in self:
            if rec.date_end and rec.date_start:
                delta = abs(rec.date_end - rec.date_start)
                rec.total_working_days = delta.days
            else:
                rec.total_working_days = 0

    def action_work_start(self):
        self.write({
            "state": "inprogress",
            "date_start": fields.Datetime.now()
        })

    def action_work_end(self):
        self.write({
            "state": "done",
            "date_end": fields.Datetime.now()
        })

    def action_work_reset(self):
        self.write({
            "state": "pending",
            "date_start": False
        })

    def action_work_cancel(self):
        return {
            'name': _('Reason of Cancellation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'booking.cancellation',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {
                'record_ids': self.ids,
            }
        }
