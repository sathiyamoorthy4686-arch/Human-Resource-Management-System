# -*- coding: utf-8 -*-
import logging
import os
from datetime import date, datetime, timedelta
import requests
from odoo import http, fields, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

class DayflowController(http.Controller):

    @http.route('/dayflow/gemini_chat', type='json', auth='user')
    def gemini_chat(self, message):
        message = (message or '').strip()
        if not message:
            return {'error': _('Please enter a message.')}
        if len(message) > 2000:
            return {'error': _('Message is too long. Please keep it under 2000 characters.')}
        if not GEMINI_API_KEY:
            return {'error': _('Gemini is not configured. Set GEMINI_API_KEY on the Odoo server.')}

        prompt = (
            'You are Dayflow HR Assistant. Answer general HRMS questions clearly and briefly. '
            'Do not make approval, rejection, payroll, or employment decisions. '
            'Tell the user to contact HR for account-specific or confidential matters. '
            'User question: %s' % message
        )
        try:
            response = requests.post(
                'https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent' % GEMINI_MODEL,
                params={'key': GEMINI_API_KEY},
                json={'contents': [{'parts': [{'text': prompt}]}]},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            answer = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
            return {'answer': answer or _('Gemini returned an empty response.')}
        except requests.RequestException:
            _logger.exception('Gemini request failed')
            return {'error': _('The AI assistant is temporarily unavailable.')}

    @http.route('/dayflow/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        is_officer = user.has_group('hr.group_hr_user')
        is_admin = user.has_group('hr.group_hr_manager')
        
        role_label = 'HR Administrator' if is_admin else ('HR Officer' if is_officer else 'Employee')
        role_type = 'admin' if is_admin else ('officer' if is_officer else 'employee')

        # Employee details
        emp_data = {
            'id': employee.id if employee else False,
            'name': user.name,
            'email': user.email or '',
            'dayflow_emp_id': employee.dayflow_emp_id if employee else 'N/A',
            'job_title': employee.job_title if employee else 'Team Member',
            'department': employee.department_id.name if (employee and employee.department_id) else 'General',
            'role': role_type,
            'role_label': role_label,
            'is_officer': is_officer or is_admin,
            'is_admin': is_admin,
            'avatar_url': f'/web/image/hr.employee/{employee.id}/image_128' if employee else f'/web/image/res.users/{user.id}/image_128',
            'work_phone': employee.work_phone or employee.mobile_phone or '' if employee else '',
            'private_city': employee.private_city or '' if employee else '',
        }

        # Attendance info
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        
        is_checked_in = False
        check_in_time = None
        worked_hours_today = 0.0
        attendance_status = 'absent'

        if employee:
            is_checked_in = employee.attendance_state == 'checked_in'
            last_attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', fields.Datetime.to_string(today_start))
            ], order='check_in desc', limit=1)
            
            if last_attendance:
                check_in_time = fields.Datetime.to_string(last_attendance.check_in)
                if not last_attendance.check_out:
                    worked_hours_today = (datetime.now() - last_attendance.check_in).total_seconds() / 3600.0
                else:
                    worked_hours_today = last_attendance.worked_hours

            attendance_status = employee.current_dayflow_status or ('present' if is_checked_in else 'absent')

        # Leave Balances
        leave_types = request.env['hr.leave.type'].sudo().search([])
        paid_leave = leave_types.filtered(lambda t: 'paid' in t.name.lower() or 'pto' in t.name.lower() or 'annual' in t.name.lower())[:1]
        sick_leave = leave_types.filtered(lambda t: 'sick' in t.name.lower())[:1]
        unpaid_leave = leave_types.filtered(lambda t: 'unpaid' in t.name.lower())[:1]

        # Recent leave requests
        recent_leaves = []
        if employee:
            leaves = request.env['hr.leave'].sudo().search([
                ('employee_id', '=', employee.id)
            ], order='date_from desc', limit=5)
            for l in leaves:
                recent_leaves.append({
                    'id': l.id,
                    'type': l.holiday_status_id.name,
                    'category': l.dayflow_leave_category,
                    'date_from': l.date_from.strftime('%b %d, %Y') if l.date_from else '',
                    'date_to': l.date_to.strftime('%b %d, %Y') if l.date_to else '',
                    'number_of_days': l.number_of_days,
                    'state': l.state,
                    'state_label': dict(l._fields['state'].selection).get(l.state, l.state),
                    'remarks': l.remarks or l.name or '',
                    'manager_comment': l.manager_comment or '',
                })

        # Payroll / Salary info for current employee
        salary_data = {}
        if employee:
            currency_symbol = employee.currency_id.symbol if employee.currency_id else '$'
            salary_data = {
                'salary_amount': employee.salary_amount or 0.0,
                'currency_symbol': currency_symbol,
                'salary_type': dict(employee._fields['salary_type'].selection).get(employee.salary_type, 'Monthly Fixed'),
                'bank_name': employee.bank_name or 'Not Specified',
                'bank_account_no': employee.bank_account_no or '•••• ••••',
            }

        # HR Admin metrics
        admin_metrics = {}
        if is_officer or is_admin:
            total_employees = request.env['hr.employee'].sudo().search_count([('active', '=', True)])
            present_count = request.env['hr.employee'].sudo().search_count([
                ('attendance_state', '=', 'checked_in'),
                ('active', '=', True)
            ])
            # Leaves today
            leaves_today = request.env['hr.leave'].sudo().search([
                ('state', '=', 'validate'),
                ('date_from', '<=', fields.Datetime.now()),
                ('date_to', '>=', fields.Datetime.now()),
            ])
            on_leave_count = len(leaves_today.mapped('employee_id'))
            absent_count = max(0, total_employees - present_count - on_leave_count)

            # Pending leave approvals
            pending_leaves_records = request.env['hr.leave'].sudo().search([
                ('state', 'in', ['confirm'])
            ], order='date_from asc', limit=10)

            pending_leaves = []
            for pl in pending_leaves_records:
                pending_leaves.append({
                    'id': pl.id,
                    'employee_id': pl.employee_id.id,
                    'employee_name': pl.employee_id.name,
                    'employee_emp_id': pl.employee_id.dayflow_emp_id or '',
                    'employee_avatar': f'/web/image/hr.employee/{pl.employee_id.id}/image_128',
                    'department': pl.employee_id.department_id.name if pl.employee_id.department_id else 'Team',
                    'leave_type': pl.holiday_status_id.name,
                    'category': pl.dayflow_leave_category,
                    'date_from': pl.date_from.strftime('%b %d, %Y') if pl.date_from else '',
                    'date_to': pl.date_to.strftime('%b %d, %Y') if pl.date_to else '',
                    'days': pl.number_of_days,
                    'remarks': pl.remarks or pl.name or 'No remarks provided',
                })

            # All employees summary list
            all_emps = request.env['hr.employee'].sudo().search([('active', '=', True)], limit=20)
            emp_list = []
            for e in all_emps:
                emp_list.append({
                    'id': e.id,
                    'name': e.name,
                    'emp_id': e.dayflow_emp_id or 'DF-%04d' % e.id,
                    'job_title': e.job_title or 'Employee',
                    'department': e.department_id.name if e.department_id else 'General',
                    'work_email': e.work_email or '',
                    'status': e.current_dayflow_status,
                    'attendance_state': e.attendance_state,
                    'salary': e.salary_amount,
                    'avatar': f'/web/image/hr.employee/{e.id}/image_128',
                })

            admin_metrics = {
                'total_employees': total_employees,
                'present_today': present_count,
                'absent_today': absent_count,
                'on_leave_today': on_leave_count,
                'pending_leaves': pending_leaves,
                'pending_count': len(pending_leaves_records),
                'employees': emp_list,
            }

        # Activity Alerts Feed
        activity_feed = [
            {
                'title': 'Welcome to Dayflow HRMS',
                'description': 'Every workday, perfectly aligned. Use your workspace to track attendance, manage time-off, and view your profile.',
                'type': 'info',
                'time': 'System Announcement'
            },
            {
                'title': 'Time-Off Policy Reminder',
                'description': 'Submit your Paid, Sick, or Unpaid leave requests at least 48 hours in advance when possible.',
                'type': 'notice',
                'time': 'Policy Update'
            }
        ]

        return {
            'user': emp_data,
            'attendance': {
                'is_checked_in': is_checked_in,
                'check_in_time': check_in_time,
                'worked_hours': round(worked_hours_today, 2),
                'status': attendance_status,
            },
            'recent_leaves': recent_leaves,
            'salary': salary_data,
            'admin': admin_metrics,
            'activities': activity_feed,
        }

    @http.route('/dayflow/attendance_toggle', type='json', auth='user')
    def toggle_attendance(self):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        if not employee:
            return {'error': _("No linked employee record found for your user.")}
        
        # Check current status
        if employee.attendance_state == 'checked_in':
            # Perform check out
            action = employee.attendance_action_change()
            return {'status': 'checked_out', 'message': _('Successfully checked out. Have a great day!')}
        else:
            # Perform check in
            action = employee.attendance_action_change()
            return {'status': 'checked_in', 'message': _('Welcome to work! Checked in successfully.')}

    @http.route('/dayflow/approve_leave', type='json', auth='user')
    def approve_leave(self, leave_id, comment=None):
        if not (request.env.user.has_group('hr.group_hr_user') or request.env.user.has_group('hr.group_hr_manager')):
            return {'error': _("Unauthorized: Only HR Officers / Admins can approve leaves.")}
        leave = request.env['hr.leave'].sudo().browse(leave_id)
        if not leave.exists():
            return {'error': _("Leave request not found.")}
        
        if comment:
            leave.manager_comment = comment
        leave.action_approve()
        return {'success': True, 'message': _("Leave request for %s has been approved.") % leave.employee_id.name}

    @http.route('/dayflow/refuse_leave', type='json', auth='user')
    def refuse_leave(self, leave_id, comment=None):
        if not (request.env.user.has_group('hr.group_hr_user') or request.env.user.has_group('hr.group_hr_manager')):
            return {'error': _("Unauthorized: Only HR Officers / Admins can refuse leaves.")}
        leave = request.env['hr.leave'].sudo().browse(leave_id)
        if not leave.exists():
            return {'error': _("Leave request not found.")}
        
        if comment:
            leave.manager_comment = comment
        leave.action_refuse()
        return {'success': True, 'message': _("Leave request for %s has been rejected.") % leave.employee_id.name}

class DayflowAuthSignupHome(AuthSignupHome):
    
    def _prepare_signup_values(self, qcontext):
        values = super(DayflowAuthSignupHome, self)._prepare_signup_values(qcontext)
        if 'dayflow_emp_id' in qcontext:
            values['dayflow_emp_id'] = qcontext.get('dayflow_emp_id')
        return values

    def do_signup(self, qcontext):
        super(DayflowAuthSignupHome, self).do_signup(qcontext)
        # Check role selection if provided
        user = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))], limit=1)
        if user:
            role = qcontext.get('role')
            if role == 'hr_officer':
                officer_group = request.env.ref('hr.group_hr_user', raise_if_not_found=False)
                if officer_group:
                    user.write({'groups_id': [(4, officer_group.id)]})
            
            # Ensure employee record exists with proper Dayflow Employee ID
            emp_id = qcontext.get('dayflow_emp_id')
            if emp_id and user.employee_id:
                user.employee_id.dayflow_emp_id = emp_id
