# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    dayflow_emp_id = fields.Char(related='employee_id.dayflow_emp_id', readonly=True, string='Employee ID')

    @api.model
    def _get_dayflow_dashboard_action(self):
        return self.env.ref('dayflow_hr.action_dayflow_dashboard').read()[0]

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            # If user does not have an employee record yet and is an internal user, link or create one
            if user.has_group('base.group_user') and not user.employee_id:
                existing_employee = self.env['hr.employee'].sudo().search([
                    '|', ('user_id', '=', user.id), ('work_email', '=', user.email)
                ], limit=1)
                if existing_employee:
                    existing_employee.user_id = user.id
                else:
                    self.env['hr.employee'].sudo().create({
                        'name': user.name,
                        'user_id': user.id,
                        'work_email': user.email,
                    })
        return users
