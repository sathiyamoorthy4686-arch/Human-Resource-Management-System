# Dayflow HRMS (dayflow_hr) - Odoo 17

> *"Every workday, perfectly aligned."*

Dayflow is a modern, unified Human Resource Management System (HRMS) built as a custom Odoo 17 module extending Odoo's native `hr`, `hr_attendance`, and `hr_holidays` modules.

---

## 1. Core Modules Extended vs Custom Built

| Component | Architecture Strategy | Extended Core Module / Implementation |
| :--- | :--- | :--- |
| **Authentication & Registration** | Extended | Extends `auth_signup` and `res.users` with automatic employee profile provisioning and Dayflow ID assignment. |
| **Employee Directory & Profiles** | Extended | Extends `hr.employee` with custom Dayflow ID (`dayflow_emp_id`), salary structures, emergency contacts, and live work status. |
| **Attendance Management** | Extended | Extends `hr_attendance` with attendance classification (`Present`, `Half-day`, `Absent`, `On Leave`), live timer, and one-click toggle. |
| **Leave & Time-Off** | Extended | Extends `hr_holidays` (`hr.leave`) with pre-seeded Paid, Sick, and Unpaid leave types, custom employee remarks, and HR approval/rejection feedback comments. |
| **Interactive Dashboard** | Custom Built | Custom Odoo 17 OWL (OpenObject Web Library) Client Action (`dayflow_hr.dashboard`) providing dual role-tailored dashboards. |
| **Salary & Compensation** | Extended / Custom | Lightweight, secure payroll/salary layer on `hr.employee` with record-level and field-level access control. |

---

## 2. Role Setup & Security Model

Dayflow enforces strict **two-tier role-based access control** at the database, model, and record levels using Odoo's built-in security groups:

### A. Employee (`base.group_user` / Internal User)
- **Scope**: Self-scoped access only.
- **Profile Permissions**: Read-only for organizational data (job title, department, manager, salary, employee ID). Can only edit:
  - Phone numbers (`work_phone`, `mobile_phone`, `private_phone`)
  - Address (`private_street`, `private_city`, `private_zip`, `private_country_id`)
  - Profile avatar (`image_1920`)
  - Emergency contact details
- **Attendance**: Can check in/out and view only their own historical attendance records (enforced by `ir.rule`).
- **Time Off**: Can submit Paid, Sick, and Unpaid leave requests and track their own status.
- **Salary**: Read-only view of their own salary and payment information.

### B. Admin / HR Officer (`hr.group_hr_user` & `hr.group_hr_manager`)
- **Scope**: Organization-wide management and approval privileges.
- **Profile Permissions**: Full CRUD permissions across all employee records, including job assignment, salary updates, and ID assignment.
- **Attendance**: Full visibility over daily/weekly logs for all staff with real-time status monitoring.
- **Time Off**: Full approval workflow with the ability to approve/refuse requests and attach manager feedback notes.
- **Salary**: Full management of employee compensation, salary structures, and banking details.

---

## 3. Demo Dataset & Seeded Users

The module includes comprehensive demo data (`demo/hr_demo_data.xml`) ready for testing:

| Name | Role | Email / Login | Department | Dayflow ID |
| :--- | :--- | :--- | :--- | :--- |
| **Alex Morgan** | HR Director (Admin/Officer) | `alex.morgan@dayflow.demo` | Human Resources | `DF-1001` |
| **Jordan Smith** | Senior Engineer (Employee) | `jordan.smith@dayflow.demo` | Engineering | `DF-1002` |
| **Taylor Reed** | Marketing Manager (Employee) | `taylor.reed@dayflow.demo` | Marketing & Growth | `DF-1003` |
| **Casey Patel** | Operations Lead (Employee) | `casey.patel@dayflow.demo` | Operations | `DF-1004` |

- **Sample Records Included**:
  - Pending Paid Time Off (PTO) request by Jordan Smith.
  - Approved Sick Leave request with manager approval comment for Taylor Reed.
  - Recent attendance logs with check-in/out timestamps and worked hour calculations.

---

## 4. Module Structure

```
dayflow_hr/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py              # API for dashboard metrics, attendance toggle, and leave approvals
├── models/
│   ├── __init__.py
│   ├── hr_employee.py       # Profile attributes, Dayflow ID, edit restrictions, salary
│   ├── hr_attendance.py     # Attendance status computation (Present, Half-day, Absent, On Leave)
│   ├── hr_leave.py          # Time-off workflow enhancements & manager comments
│   └── res_users.py         # Automatic employee provisioning & dashboard routing
├── security/
│   ├── ir.model.access.csv  # CRUD permissions
│   └── hr_security.xml      # Record rules (ir.rule) enforcing self-isolation vs HR full-access
├── data/
│   ├── hr_leave_type_data.xml # Paid, Sick, and Unpaid leave types
│   └── dayflow_data.xml       # Employee ID sequence (DF-XXXX)
├── demo/
│   └── hr_demo_data.xml     # Seeded demo employees, attendance, and leave records
├── views/
│   ├── dayflow_menus.xml    # Rebranded Dayflow app navigation & client actions
│   ├── hr_employee_views.xml# Custom Employee form, Kanban, and Tree views
│   ├── hr_attendance_views.xml # Daily/weekly attendance logs & status filters
│   ├── hr_leave_views.xml   # Leave requests & approval interfaces
│   └── hr_salary_views.xml  # Compensation & banking management view
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       ├── xml/dayflow_dashboard.xml # OWL template for Employee & Admin dashboards
│       ├── js/dayflow_dashboard.js   # OWL Client Action component
│       └── scss/dayflow_dashboard.scss # Dayflow modern UI styling
└── README.md
```

---

## 5. Installation & Verification

1. Place the `dayflow_hr` folder into your Odoo 17 custom addons path (e.g. `addons_path = /path/to/custom_addons`).
2. Update the apps list via Odoo Settings or restart Odoo with `-u dayflow_hr -d your_database`.
3. In Apps, search for **Dayflow HRMS** and click **Install** (or install with `--load-language` and `--demo` enabled for sample records).
4. Log in as an Employee (`jordan.smith@dayflow.demo`) to verify self-service view, or as HR Admin (`alex.morgan@dayflow.demo`) to access full HR administration.
