# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    dayflow_status = fields.Selection([
        ('present', 'Present'),
        ('half_day', 'Half-day'),
        ('absent', 'Absent'),
        ('on_leave', 'On Leave'),
    ], string='Status', compute='_compute_dayflow_status', store=True, index=True)

    dayflow_note = fields.Char(string='Check-in Note')

    @api.depends('worked_hours', 'check_in', 'check_out', 'employee_id')
    def _compute_dayflow_status(self):
        for att in self:
            if not att.check_out:
                att.dayflow_status = 'present'
            elif att.worked_hours >= 7.0:
                att.dayflow_status = 'present'
            elif 3.0 <= att.worked_hours < 7.0:
                att.dayflow_status = 'half_day'
            else:
                att.dayflow_status = 'present'
