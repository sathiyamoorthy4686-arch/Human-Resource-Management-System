# Dayflow HRMS & Employee Management System

> *"Every workday, perfectly aligned."*

A unified, modern Human Resource Management System (HRMS) featuring strict **Role-Based Access Control (RBAC)**, real-time attendance tracking, leave approval workflows, employee profile directories, and salary administration.

---

## 🌟 Key Features

### 1. Authentication & Role-Based Access Control (RBAC)
- **Two-Tier RBAC Architecture**:
  - **HR Administrator / Officer (`base.group_hr_manager` / `hr.group_hr_user`)**: Organization-wide visibility, company metrics, leave approval/refusal management, salary structure management, and full employee CRUD.
  - **Employee / Self-Service User (`base.group_user`)**: Self-isolated scope. View only personal attendance history, submitted time-off requests, personal confidential compensation, and self-service contact updates.
- **User Registration & Profile Provisioning**: Auto-assigns Dayflow Employee ID (e.g. `DF-1001`) and default employee structure.

### 2. Real-Time Attendance Management
- One-click Check-in and Check-out toggle with live worked-hours counter.
- Automatic attendance classification (*Present, Half-day, Absent, On Leave*).
- Complete historical attendance logging.

### 3. Time-Off & Leave Management
- Multi-category leave requests: **Paid Time Off (PTO)**, **Sick Leave**, and **Unpaid Leave**.
- HR approval queue with customizable manager feedback notes.

### 4. Interactive Dashboards & Directory
- Real-time organization metrics: total employees, present count, absent count, and attendance percentage.
- Searchable employee directory and contact cards.
- Profile self-service updates (phone, city, emergency contact details).

---

## 👥 Demo Accounts (Pre-Seeded)

| Name | Role | Email / Login | Password | Dayflow ID |
| :--- | :--- | :--- | :--- | :--- |
| **Alex Morgan** | HR Director (Admin) | `alex.morgan@dayflow.demo` | `dayflow123` | `DF-1001` |
| **Jordan Smith** | Senior Engineer (Employee) | `jordan.smith@dayflow.demo` | `dayflow123` | `DF-1002` |
| **Taylor Reed** | Marketing Lead (Employee) | `taylor.reed@dayflow.demo` | `dayflow123` | `DF-1003` |
| **Casey Patel** | Operations Specialist (Employee) | `casey.patel@dayflow.demo` | `dayflow123` | `DF-1004` |

---

## 🚀 How to Run

### Option 1: Standalone Interactive Web App (Instant)
Run the application locally without requiring full Odoo / PostgreSQL installation:

```bash
python run_dayflow.py
```

- Open in browser: **`http://127.0.0.1:8069`**
- Test 1-click login as **Alex Morgan (Admin)** or **Jordan Smith (Employee)** to experience RBAC isolation.

### Option 2: Odoo 17 Custom Module
Add the `dayflow_hr` folder into your Odoo 17 `addons_path`:

```ini
addons_path = /path/to/odoo/addons,/path/to/HRMS
```

Update or start Odoo:
```bash
python odoo-bin -c odoo.conf -d dayflow_db -u dayflow_hr --demo
```

---

## 📂 Repository Structure

```text
├── dayflow_hr/                  # Odoo 17 Custom Addon Module
│   ├── controllers/             # Dashboard API & attendance endpoints
│   ├── data/                    # Sequences and leave type data
│   ├── demo/                    # Seeded users and employee records
│   ├── models/                  # hr_employee, hr_attendance, hr_leave, res_users
│   ├── security/                # ir.model.access.csv and hr_security.xml (RBAC)
│   ├── static/                  # OWL Dashboard JS, XML templates, and SCSS
│   ├── views/                   # Kanban, Tree, Form, and Menu XML views
│   └── __manifest__.py          # Odoo module manifest
├── run_dayflow.py               # Standalone FastAPI + RBAC interactive web server
└── README.md
```

---

## 📄 License
This project is licensed under LGPL-3.
