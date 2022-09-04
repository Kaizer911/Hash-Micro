# See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ServiceTeam(models.Model):
    _name = "service.team"
    _description = "Service Team"

    name = fields.Char("Name", required=True, index=True)
    team_leader_id = fields.Many2one("res.users", "Team Leader", ondelete="cascade")
    team_member_ids = fields.Many2many("res.users", string="Team Members")
