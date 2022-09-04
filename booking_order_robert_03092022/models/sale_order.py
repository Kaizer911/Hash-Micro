# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_booking_order = fields.Boolean(default=False)
    service_team_id = fields.Many2one("service.team", "Team")
    team_leader_id = fields.Many2one("res.users", "Team Leader")
    team_member_ids = fields.Many2many("res.users", string="Team Members")
    booking_start = fields.Datetime(string="Booking Start")
    booking_end = fields.Datetime(string="Booking End")
    work_order_ids = fields.One2many('work.order', 'sale_order_id', string='Booking Order')
    work_order_count = fields.Integer(string='Work Orders', compute='_compute_work_order_ids')

    @api.depends('work_order_ids')
    def _compute_work_order_ids(self):
        for rec in self:
            rec.work_order_count = len(rec.work_order_ids)

    @api.onchange("service_team_id")
    def _onchange_service_team_id(self):
        if self.service_team_id:
            self.update(
                {
                    "team_leader_id": self.service_team_id.team_leader_id.id,
                    "team_member_ids": self.service_team_id.team_member_ids.ids,
                }
            )
        else:
            self.update(
                {
                    "team_leader_id": False,
                    "team_member_ids": False,
                }
            )

    def _get_action_view_work_order(self, work_orders):
        action = self.env["ir.actions.actions"]._for_xml_id("booking_order_robert_03092022.action_work_order_tree")

        if len(work_orders) > 1:
            action['domain'] = [('id', 'in', work_orders.ids)]
        elif work_orders:
            form_view = [(self.env.ref('booking_order_robert_03092022.view_work_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = work_orders[0].id
        return action

    def action_view_work_order(self):
        return self._get_action_view_work_order(self.work_order_ids)

    def check_overlap(self, service_team_id=False, date_from=False, date_to=False):
        params = { 
            'service_team_id': service_team_id,
            'date_from': date_from,
            'date_to': date_to
        }
        query = """
                SELECT id 
                FROM work_order 
                WHERE service_team_id = {service_team_id} AND
                    state NOT IN  ('done', 'cancel') AND
                    (date_planned_end BETWEEN '{date_from}' AND '{date_to}') OR (date_planned_start <= '{date_from}' AND date_planned_end >= '{date_to}')
                """.format(**params)
        
        self._cr.execute(query)
        result = self.env.cr.dictfetchall()

        return result

    def action_confirm(self):
        for rec in self:
            if rec.is_booking_order:
                date_from = fields.Datetime.to_string(
                    fields.Datetime.context_timestamp(self, rec.booking_start)
                )

                date_to = fields.Datetime.to_string(
                    fields.Datetime.context_timestamp(self, rec.booking_end)
                )

                datas = self.check_overlap(service_team_id=rec.service_team_id.id, date_from=date_from, date_to=date_to)

                if datas:
                    for data in datas:
                        work_order = self.env["work.order"].browse(data.get("id"))
                        if work_order:
                            raise ValidationError(_("Team already has work order during that period on {}. Please book on another date.".format(work_order.sale_order_id.name)))
                        # else:
                            # raise ValidationError(_("Team is available for booking"))

                vals = {
                    "name": self.env["ir.sequence"].next_by_code("work.order"),
                    "sale_order_id": rec.id,
                    "service_team_id": rec.service_team_id.id,
                    "team_leader_id": rec.team_leader_id.id,
                    "team_member_ids": rec.team_member_ids.ids,
                    "date_planned_start": rec.booking_start,
                    "date_planned_end": rec.booking_end,
                    "state": 'pending',
                }

                work_order_id = self.env["work.order"].create(vals)
                # raise ValidationError(work_order_id.name)

        return super().action_confirm()

    def action_check(self):
        for rec in self:
            date_from = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, rec.booking_start)
            )

            date_to = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, rec.booking_end)
            )

            datas = self.check_overlap(service_team_id=rec.service_team_id.id, date_from=date_from, date_to=date_to)

            if datas:
                for data in datas:
                    work_order = self.env["work.order"].browse(data.get("id"))
                    if work_order:
                        raise ValidationError(_("Team already has work order during that period on {}".format(work_order.sale_order_id.name)))
            else:
                raise ValidationError(_("Team is available for booking"))

        return True
