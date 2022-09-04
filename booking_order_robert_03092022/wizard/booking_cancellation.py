# -*- coding: utf-8 -*-

from odoo import fields, models

class BookingCancellation(models.TransientModel):
    _name = 'booking.cancellation'
    _description = 'Booking Cancellation'

    name = fields.Char(string='Reason for cancellation')
    
    def action_confirm(self):
        record = self.env['work.order'].browse(self._context.get('record_ids'))

        record.write({
            'notes': self.name, 
            'state': 'cancel'
        })

        return True