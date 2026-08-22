# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    remarks = fields.Text(string='Employee Remarks / Reason')
    manager_comment = fields.Text(string='HR / Manager Comments', tracking=True)
    
    dayflow_leave_category = fields.Selection([
        ('paid', 'Paid Time Off'),
        ('sick', 'Sick Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ], string='Leave Category', compute='_compute_dayflow_leave_category', store=True)

    @api.depends('holiday_status_id')
    def _compute_dayflow_leave_category(self):
        for leave in self:
            name = (leave.holiday_status_id.name or '').lower()
            if 'paid' in name or 'pto' in name or 'annual' in name:
                leave.dayflow_leave_category = 'paid'
            elif 'sick' in name:
                leave.dayflow_leave_category = 'sick'
            elif 'unpaid' in name:
                leave.dayflow_leave_category = 'unpaid'
            else:
                leave.dayflow_leave_category = 'other'

    def action_dayflow_approve(self, comment=None):
        """Approve leave request with optional manager comment"""
        for record in self:
            if comment:
                record.manager_comment = comment
            record.action_approve()
        return True

    def action_dayflow_refuse(self, comment=None):
        """Refuse/Reject leave request with optional manager comment"""
        for record in self:
            if comment:
                record.manager_comment = comment
            record.action_refuse()
        return True
