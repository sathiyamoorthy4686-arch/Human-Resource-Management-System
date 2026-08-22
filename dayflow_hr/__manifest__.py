# -*- coding: utf-8 -*-
{
    'name': 'Dayflow HRMS',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Every workday, perfectly aligned.',
    'description': """
Dayflow HRMS - Human Resource Management System
================================================
"Every workday, perfectly aligned."

A streamlined HRMS built by extending Odoo's core hr, hr_attendance, and hr_holidays modules.

Key Features:
-------------
* Rebranded Dayflow interface with dedicated Employee and Admin/HR Officer dashboards.
* Role-based access control (Admin / HR Officer vs Employee) enforced at record and model level.
* Real-time attendance tracking with status classification (Present, Absent, Half-day, On Leave).
* Intuitive Time-Off requests supporting Paid, Sick, and Unpaid leave workflows with approval notes.
* Lightweight employee profile and salary structure management with strict field-level edit restrictions.
* Native Odoo authentication and signup integration.
    """,
    'author': 'Dayflow HR',
    'website': 'https://www.dayflowhr.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'hr_holidays',
        'web',
        'auth_signup',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'data/hr_leave_type_data.xml',
        'data/dayflow_data.xml',
        'views/dayflow_menus.xml',
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_salary_views.xml',
    ],
    'demo': [
        'demo/hr_demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dayflow_hr/static/src/scss/dayflow_dashboard.scss',
            'dayflow_hr/static/src/xml/dayflow_dashboard.xml',
            'dayflow_hr/static/src/js/dayflow_dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
