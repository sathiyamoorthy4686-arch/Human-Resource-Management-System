# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dayflow_emp_id = fields.Char(
        string='Employee ID',
        copy=False,
        index=True,
        tracking=True,
        help='Unique Dayflow Employee Identifier'
    )
    
    salary_amount = fields.Monetary(
        string='Monthly Base Salary',
        currency_field='currency_id',
        tracking=True,
        groups='hr.group_hr_user,base.group_user',
        help='Monthly base salary amount'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    salary_type = fields.Selection([
        ('monthly', 'Monthly Fixed'),
        ('hourly', 'Hourly Rate'),
        ('annual', 'Annual Salary'),
    ], string='Salary Structure', default='monthly')
    
    bank_name = fields.Char(string='Bank Name')
    bank_account_no = fields.Char(string='Bank Account Number')
    
    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_relation = fields.Char(string='Relationship')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    
    current_dayflow_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half-day'),
        ('on_leave', 'On Leave'),
    ], string='Work Status', compute='_compute_current_dayflow_status', store=False)

    @api.depends('attendance_state')
    def _compute_current_dayflow_status(self):
        today = fields.Date.today()
        for emp in self:
            # Check if employee has approved leave today
            leaves_today = self.env['hr.leave'].sudo().search_count([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('date_from', '<=', fields.Datetime.now()),
                ('date_to', '>=', fields.Datetime.now()),
            ])
            if leaves_today > 0:
                emp.current_dayflow_status = 'on_leave'
            elif emp.attendance_state == 'checked_in':
                emp.current_dayflow_status = 'present'
            else:
                # Check if worked half day earlier today
                last_attendance = self.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', emp.id),
                    ('check_in', '>=', fields.Datetime.to_datetime(today)),
                ], limit=1, order='check_in desc')
                if last_attendance and last_attendance.worked_hours > 0:
                    emp.current_dayflow_status = 'half_day' if last_attendance.worked_hours < 7.0 else 'present'
                else:
                    emp.current_dayflow_status = 'absent'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('dayflow_emp_id'):
                vals['dayflow_emp_id'] = self.env['ir.sequence'].next_by_code('dayflow.employee.id') or _('DF-%04d') % (self.env['hr.employee'].search_count([]) + 1)
        return super(HrEmployee, self).create(vals_list)

    def write(self, vals):
        is_officer = self.env.user.has_group('hr.group_hr_user') or self.env.user.has_group('hr.group_hr_manager')
        if not is_officer and not self.env.is_superuser():
            # Standard employee is editing
            allowed_fields = {
                'mobile_phone', 'work_phone', 'private_phone', 'private_email',
                'private_street', 'private_street2', 'private_city', 'private_state_id',
                'private_zip', 'private_country_id', 'image_1920', 'image_128',
                'emergency_contact_name', 'emergency_contact_relation', 'emergency_contact_phone'
            }
            attempted_restricted_fields = set(vals.keys()) - allowed_fields
            if attempted_restricted_fields:
                raise AccessError(_(
                    "You are only permitted to update your personal contact details (address, phone) and profile picture. "
                    "Restricted field changes: %s"
                ) % ', '.join(attempted_restricted_fields))
        return super(HrEmployee, self).write(vals)
