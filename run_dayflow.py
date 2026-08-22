#!/usr/bin/env python3
"""
Dayflow HRMS - Authentication, RBAC & Attendance Management Server
Real-Time Attendance Logging, HR Employee Provisioning & Credential System.
"""

import os
import json
import uuid
import random
import string
import hashlib
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
import uvicorn

app = FastAPI(title="Dayflow HRMS", description="Every workday, perfectly aligned.")

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

DEFAULT_PASS = hash_pw("dayflow123")

# Time helpers
now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
two_days_ago_str = (now - timedelta(days=2)).strftime("%Y-%m-%d")
three_days_ago_str = (now - timedelta(days=3)).strftime("%Y-%m-%d")

DB = {
    "users": {
        "alex.morgan@dayflow.demo": {
            "id": 1,
            "login": "alex.morgan@dayflow.demo",
            "password_hash": DEFAULT_PASS,
            "password_plain": "dayflow123",
            "name": "Alex Morgan",
            "email": "alex.morgan@dayflow.demo",
            "role": "admin",
            "role_label": "HR Director / Administrator",
            "is_admin": True,
            "is_officer": True,
            "employee_id": 1,
            "created_at": "2026-01-01T09:00:00"
        },
        "jordan.smith@dayflow.demo": {
            "id": 2,
            "login": "jordan.smith@dayflow.demo",
            "password_hash": DEFAULT_PASS,
            "password_plain": "dayflow123",
            "name": "Jordan Smith",
            "email": "jordan.smith@dayflow.demo",
            "role": "employee",
            "role_label": "Senior Software Engineer",
            "is_admin": False,
            "is_officer": False,
            "employee_id": 2,
            "created_at": "2026-01-15T09:00:00"
        },
        "taylor.reed@dayflow.demo": {
            "id": 3,
            "login": "taylor.reed@dayflow.demo",
            "password_hash": DEFAULT_PASS,
            "password_plain": "dayflow123",
            "name": "Taylor Reed",
            "email": "taylor.reed@dayflow.demo",
            "role": "employee",
            "role_label": "Growth Marketing Lead",
            "is_admin": False,
            "is_officer": False,
            "employee_id": 3,
            "created_at": "2026-02-01T09:00:00"
        },
        "casey.patel@dayflow.demo": {
            "id": 4,
            "login": "casey.patel@dayflow.demo",
            "password_hash": DEFAULT_PASS,
            "password_plain": "dayflow123",
            "name": "Casey Patel",
            "email": "casey.patel@dayflow.demo",
            "role": "employee",
            "role_label": "Operations Specialist",
            "is_admin": False,
            "is_officer": False,
            "employee_id": 4,
            "created_at": "2026-02-10T09:00:00"
        }
    },
    "employees": [
        {
            "id": 1,
            "user_id": 1,
            "name": "Alex Morgan",
            "dayflow_emp_id": "DF-1001",
            "job_title": "HR Director & People Lead",
            "department": "Human Resources",
            "work_email": "alex.morgan@dayflow.demo",
            "work_phone": "+1 555-0101",
            "mobile_phone": "+1 555-0102",
            "private_city": "San Francisco",
            "salary_amount": 8500.0,
            "salary_type": "Monthly Fixed",
            "bank_name": "First Republic Bank",
            "bank_account_no": "US89 •••• 3000",
            "emergency_contact_name": "Sarah Morgan",
            "emergency_contact_relation": "Spouse",
            "emergency_contact_phone": "+1 555-0109",
            "attendance_state": "checked_in",
            "last_check_in": (now - timedelta(hours=3, minutes=24)).strftime("%Y-%m-%d %H:%M"),
            "worked_hours": 3.4
        },
        {
            "id": 2,
            "user_id": 2,
            "name": "Jordan Smith",
            "dayflow_emp_id": "DF-1002",
            "job_title": "Senior Software Engineer",
            "department": "Engineering",
            "work_email": "jordan.smith@dayflow.demo",
            "work_phone": "+1 555-0201",
            "mobile_phone": "+1 555-0202",
            "private_city": "Austin",
            "salary_amount": 9200.0,
            "salary_type": "Monthly Fixed",
            "bank_name": "Silicon Valley Bank",
            "bank_account_no": "US44 •••• 0002",
            "emergency_contact_name": "David Smith",
            "emergency_contact_relation": "Parent",
            "emergency_contact_phone": "+1 555-0209",
            "attendance_state": "checked_in",
            "last_check_in": (now - timedelta(hours=2, minutes=15)).strftime("%Y-%m-%d %H:%M"),
            "worked_hours": 2.25
        },
        {
            "id": 3,
            "user_id": 3,
            "name": "Taylor Reed",
            "dayflow_emp_id": "DF-1003",
            "job_title": "Growth Marketing Lead",
            "department": "Marketing & Growth",
            "work_email": "taylor.reed@dayflow.demo",
            "work_phone": "+1 555-0301",
            "mobile_phone": "+1 555-0302",
            "private_city": "New York",
            "salary_amount": 7800.0,
            "salary_type": "Monthly Fixed",
            "bank_name": "Chase Bank",
            "bank_account_no": "US12 •••• 4591",
            "emergency_contact_name": "Emma Reed",
            "emergency_contact_relation": "Sibling",
            "emergency_contact_phone": "+1 555-0309",
            "attendance_state": "checked_out",
            "last_check_in": None,
            "worked_hours": 0.0
        },
        {
            "id": 4,
            "user_id": 4,
            "name": "Casey Patel",
            "dayflow_emp_id": "DF-1004",
            "job_title": "Operations Specialist",
            "department": "Operations",
            "work_email": "casey.patel@dayflow.demo",
            "work_phone": "+1 555-0401",
            "mobile_phone": "+1 555-0402",
            "private_city": "Chicago",
            "salary_amount": 7400.0,
            "salary_type": "Monthly Fixed",
            "bank_name": "Bank of America",
            "bank_account_no": "US33 •••• 7712",
            "emergency_contact_name": "Rohan Patel",
            "emergency_contact_relation": "Spouse",
            "emergency_contact_phone": "+1 555-0409",
            "attendance_state": "checked_out",
            "last_check_in": None,
            "worked_hours": 0.0
        }
    ],
    "leaves": [
        {
            "id": 1,
            "employee_id": 2,
            "employee_name": "Jordan Smith",
            "dayflow_emp_id": "DF-1002",
            "department": "Engineering",
            "type": "Paid Time Off (PTO)",
            "category": "paid",
            "date_from": (date.today() + timedelta(days=5)).strftime("%b %d, %Y"),
            "date_to": (date.today() + timedelta(days=7)).strftime("%b %d, %Y"),
            "number_of_days": 3,
            "state": "confirm",
            "state_label": "Pending Approval",
            "remarks": "Annual family vacation trip to Rocky Mountains.",
            "manager_comment": ""
        },
        {
            "id": 2,
            "employee_id": 3,
            "employee_name": "Taylor Reed",
            "dayflow_emp_id": "DF-1003",
            "department": "Marketing & Growth",
            "type": "Sick Leave",
            "category": "sick",
            "date_from": (date.today() - timedelta(days=3)).strftime("%b %d, %Y"),
            "date_to": (date.today() - timedelta(days=2)).strftime("%b %d, %Y"),
            "number_of_days": 2,
            "state": "validate",
            "state_label": "Approved",
            "remarks": "Flu symptoms and fever. Doctor advised 2 days rest.",
            "manager_comment": "Approved by Alex Morgan. Rest well!"
        }
    ],
    # Rich Attendance Records
    "attendance_logs": [
        {
            "id": 1,
            "employee_id": 1,
            "employee_name": "Alex Morgan",
            "dayflow_emp_id": "DF-1001",
            "department": "Human Resources",
            "date": today_str,
            "check_in": f"{today_str} 08:30",
            "check_out": "In Progress (Active)",
            "status": "Present",
            "worked_hours": "3.4 hrs"
        },
        {
            "id": 2,
            "employee_id": 2,
            "employee_name": "Jordan Smith",
            "dayflow_emp_id": "DF-1002",
            "department": "Engineering",
            "date": today_str,
            "check_in": f"{today_str} 09:15",
            "check_out": "In Progress (Active)",
            "status": "Present",
            "worked_hours": "2.2 hrs"
        },
        {
            "id": 3,
            "employee_id": 1,
            "employee_name": "Alex Morgan",
            "dayflow_emp_id": "DF-1001",
            "department": "Human Resources",
            "date": yesterday_str,
            "check_in": f"{yesterday_str} 09:00",
            "check_out": f"{yesterday_str} 17:30",
            "status": "Present",
            "worked_hours": "8.5 hrs"
        },
        {
            "id": 4,
            "employee_id": 2,
            "employee_name": "Jordan Smith",
            "dayflow_emp_id": "DF-1002",
            "department": "Engineering",
            "date": yesterday_str,
            "check_in": f"{yesterday_str} 09:05",
            "check_out": f"{yesterday_str} 18:00",
            "status": "Present",
            "worked_hours": "8.9 hrs"
        },
        {
            "id": 5,
            "employee_id": 4,
            "employee_name": "Casey Patel",
            "dayflow_emp_id": "DF-1004",
            "department": "Operations",
            "date": yesterday_str,
            "check_in": f"{yesterday_str} 08:45",
            "check_out": f"{yesterday_str} 17:15",
            "status": "Present",
            "worked_hours": "8.5 hrs"
        },
        {
            "id": 6,
            "employee_id": 3,
            "employee_name": "Taylor Reed",
            "dayflow_emp_id": "DF-1003",
            "department": "Marketing & Growth",
            "date": two_days_ago_str,
            "check_in": f"{two_days_ago_str} 09:10",
            "check_out": f"{two_days_ago_str} 13:30",
            "status": "Half-day",
            "worked_hours": "4.3 hrs"
        },
        {
            "id": 7,
            "employee_id": 2,
            "employee_name": "Jordan Smith",
            "dayflow_emp_id": "DF-1002",
            "department": "Engineering",
            "date": three_days_ago_str,
            "check_in": f"{three_days_ago_str} 09:00",
            "check_out": f"{three_days_ago_str} 17:45",
            "status": "Present",
            "worked_hours": "8.7 hrs"
        }
    ],
    "sessions": {}
}

DEFAULT_SESSION_TOKEN = "session-alex-admin-token"
DB["sessions"][DEFAULT_SESSION_TOKEN] = "alex.morgan@dayflow.demo"
EMP_SEQ = 1005

class LoginPayload(BaseModel):
    email: str
    password: str

class HRCreateEmployeePayload(BaseModel):
    name: str
    email: str
    password: str
    role: str
    department: str
    job_title: str
    salary_amount: float
    salary_type: Optional[str] = "Monthly Fixed"
    bank_name: Optional[str] = "Company Payroll Bank"
    bank_account_no: Optional[str] = "US •••• 1000"
    dayflow_emp_id: Optional[str] = None
    private_city: Optional[str] = "Headquarters"
    work_phone: Optional[str] = None

class ResetPasswordPayload(BaseModel):
    email: str
    new_password: str

class LeaveRequestPayload(BaseModel):
    leave_type: str
    date_from: str
    date_to: str
    days: float
    remarks: str

class LeaveActionPayload(BaseModel):
    leave_id: int
    comment: Optional[str] = ""

class ProfileUpdatePayload(BaseModel):
    work_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    private_city: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class AdminSalaryUpdatePayload(BaseModel):
    employee_id: int
    salary_amount: float
    salary_type: str
    bank_name: str
    bank_account_no: str

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        return DB["users"]["alex.morgan@dayflow.demo"]
    token = authorization.replace("Bearer ", "").strip()
    if token not in DB["sessions"]:
        if token in DB["users"]:
            return DB["users"][token]
        return DB["users"]["alex.morgan@dayflow.demo"]
    email = DB["sessions"][token]
    user = DB["users"].get(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session user")
    return user

# ================= AUTHENTICATION ENDPOINTS =================

@app.post("/api/auth/login")
def login_user(payload: LoginPayload):
    email = payload.email.strip().lower()
    user = DB["users"].get(email)
    if not user:
        raise HTTPException(status_code=401, detail="No account found with this email ID.")
    if user["password_hash"] != hash_pw(payload.password):
        raise HTTPException(status_code=401, detail="Invalid password credentials.")
    token = f"sess-{uuid.uuid4().hex[:16]}"
    DB["sessions"][token] = email
    return {
        "success": True,
        "message": f"Welcome back, {user['name']}!",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "role_label": user["role_label"],
            "is_admin": user["is_admin"],
            "is_officer": user["is_officer"]
        }
    }

# ================= HR EXCLUSIVE: CREATE EMPLOYEE EMAIL ID & ACCOUNT =================

@app.post("/api/admin/create_employee")
def hr_create_employee(payload: HRCreateEmployeePayload, authorization: Optional[str] = Header(None)):
    global EMP_SEQ
    hr_user = get_current_user(authorization)
    if not hr_user.get("is_admin") and not hr_user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Directors / Officers can create new employee accounts.")

    email = payload.email.strip().lower()
    if email in DB["users"]:
        raise HTTPException(status_code=400, detail="An employee with this Email ID already exists in the system.")

    password_clean = payload.password.strip()
    if not password_clean:
        password_clean = "Dayflow@" + "".join(random.choices(string.digits, k=4))

    user_id = len(DB["users"]) + 1
    emp_id_num = len(DB["employees"]) + 1
    dayflow_id = payload.dayflow_emp_id.strip() if payload.dayflow_emp_id else f"DF-{EMP_SEQ}"
    EMP_SEQ += 1

    is_admin_role = payload.role in ["admin", "hr_officer", "hr_manager"]
    role_type = "admin" if is_admin_role else "employee"
    role_label = "HR Administrator" if is_admin_role else f"Employee ({payload.job_title})"

    new_user = {
        "id": user_id,
        "login": email,
        "password_hash": hash_pw(password_clean),
        "password_plain": password_clean,
        "name": payload.name.strip(),
        "email": email,
        "role": role_type,
        "role_label": role_label,
        "is_admin": is_admin_role,
        "is_officer": is_admin_role,
        "employee_id": emp_id_num,
        "created_at": datetime.now().isoformat()
    }
    DB["users"][email] = new_user

    new_emp = {
        "id": emp_id_num,
        "user_id": user_id,
        "name": payload.name.strip(),
        "dayflow_emp_id": dayflow_id,
        "job_title": payload.job_title,
        "department": payload.department,
        "work_email": email,
        "work_phone": payload.work_phone or ("+1 555-0" + str(100 + emp_id_num)),
        "mobile_phone": "+1 555-0" + str(200 + emp_id_num),
        "private_city": payload.private_city or "Headquarters",
        "salary_amount": float(payload.salary_amount or 6500.0),
        "salary_type": payload.salary_type or "Monthly Fixed",
        "bank_name": payload.bank_name or "Silicon Valley Bank",
        "bank_account_no": payload.bank_account_no or f"US{emp_id_num*17} •••• {emp_id_num*88}",
        "emergency_contact_name": "Emergency Contact",
        "emergency_contact_relation": "Family",
        "emergency_contact_phone": "+1 555-0999",
        "attendance_state": "checked_out",
        "last_check_in": None,
        "worked_hours": 0.0
    }
    DB["employees"].append(new_emp)

    # Pre-seed initial onboarding attendance log
    DB["attendance_logs"].insert(0, {
        "id": len(DB["attendance_logs"]) + 1,
        "employee_id": emp_id_num,
        "employee_name": payload.name.strip(),
        "dayflow_emp_id": dayflow_id,
        "department": payload.department,
        "date": today_str,
        "check_in": f"{today_str} 09:00",
        "check_out": f"{today_str} 17:00",
        "status": "Present",
        "worked_hours": "8.0 hrs"
    })

    return {
        "success": True,
        "message": f"Successfully created employee profile & email ID for {payload.name} ({email}) with Dayflow ID {dayflow_id}!",
        "employee": new_emp,
        "credentials": {
            "name": payload.name.strip(),
            "email": email,
            "password": password_clean,
            "dayflow_emp_id": dayflow_id,
            "role": role_label,
            "department": payload.department
        }
    }

@app.post("/api/admin/reset_password")
def hr_reset_password(payload: ResetPasswordPayload, authorization: Optional[str] = Header(None)):
    hr_user = get_current_user(authorization)
    if not hr_user.get("is_admin") and not hr_user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Management can reset passwords.")

    email = payload.email.strip().lower()
    user = DB["users"].get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    user["password_hash"] = hash_pw(payload.new_password)
    user["password_plain"] = payload.new_password

    return {
        "success": True,
        "message": f"Password for {user['name']} ({email}) has been successfully updated to: {payload.new_password}",
        "email": email,
        "new_password": payload.new_password
    }

@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token in DB["sessions"]:
            del DB["sessions"][token]
    return {"success": True, "message": "Logged out successfully."}

# ================= STATE & WORKFLOWS =================

@app.get("/api/state")
def get_state(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)
    is_admin = user.get("is_admin", False) or user.get("is_officer", False)

    # Attendance logs: HR sees all, Employee sees own
    if is_admin:
        attendance_logs = DB["attendance_logs"]
        all_leaves = DB["leaves"]
        pending_leaves = [l for l in DB["leaves"] if l["state"] == "confirm"]
        salary_records = DB["employees"]
        
        employees_list = []
        for e in DB["employees"]:
            u = DB["users"].get(e["work_email"])
            employees_list.append({
                **e,
                "login_password": u.get("password_plain", "dayflow123") if u else "dayflow123"
            })
    else:
        attendance_logs = [a for a in DB["attendance_logs"] if a.get("employee_id") == user["employee_id"]]
        all_leaves = [l for l in DB["leaves"] if l.get("employee_id") == user["employee_id"]]
        pending_leaves = []
        salary_records = [emp] if emp else []
        employees_list = [
            {
                "id": e["id"],
                "name": e["name"],
                "dayflow_emp_id": e["dayflow_emp_id"],
                "job_title": e["job_title"],
                "department": e["department"],
                "work_email": e["work_email"],
                "private_city": e["private_city"],
                "attendance_state": e["attendance_state"]
            }
            for e in DB["employees"]
        ]

    total_emps = len(DB["employees"])
    present_emps = len([e for e in DB["employees"] if e["attendance_state"] == "checked_in"])
    on_leave = len([l for l in DB["leaves"] if l["state"] == "validate" and l["number_of_days"] > 0 and "Sick" in l["type"]])
    absent_emps = max(0, total_emps - present_emps - on_leave)

    return {
        "current_user": user,
        "employee": emp,
        "is_admin": is_admin,
        "metrics": {
            "total_employees": total_emps,
            "present_today": present_emps,
            "on_leave_today": on_leave,
            "absent_today": absent_emps,
            "attendance_rate": round((present_emps / total_emps * 100), 1) if total_emps > 0 else 0
        },
        "pending_leaves": pending_leaves,
        "all_leaves": all_leaves,
        "all_employees": employees_list,
        "salary_records": salary_records,
        "attendance_logs": attendance_logs
    }

@app.post("/api/toggle_attendance")
def toggle_attendance(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found")

    cur_time = datetime.now()
    cur_time_str = cur_time.strftime("%Y-%m-%d %H:%M")
    cur_date_str = cur_time.strftime("%Y-%m-%d")

    if emp["attendance_state"] == "checked_in":
        # Check out
        emp["attendance_state"] = "checked_out"
        
        # Find active log or create one
        active_log = next((a for a in DB["attendance_logs"] if a.get("employee_id") == emp["id"] and "In Progress" in str(a.get("check_out", ""))), None)
        if active_log:
            active_log["check_out"] = cur_time_str
            active_log["status"] = "Present"
            active_log["worked_hours"] = f"{emp['worked_hours']:.1f} hrs"
        else:
            DB["attendance_logs"].insert(0, {
                "id": len(DB["attendance_logs"]) + 1,
                "employee_id": emp["id"],
                "employee_name": emp["name"],
                "dayflow_emp_id": emp["dayflow_emp_id"],
                "department": emp["department"],
                "date": cur_date_str,
                "check_in": emp["last_check_in"] or cur_time_str,
                "check_out": cur_time_str,
                "status": "Present",
                "worked_hours": f"{emp['worked_hours']:.1f} hrs"
            })
        return {"status": "checked_out", "message": f"Successfully checked out, {emp['name']}. Have a great evening!"}
    else:
        # Check in
        emp["attendance_state"] = "checked_in"
        emp["last_check_in"] = cur_time_str
        emp["worked_hours"] = 0.1

        # Add active log immediately
        DB["attendance_logs"].insert(0, {
            "id": len(DB["attendance_logs"]) + 1,
            "employee_id": emp["id"],
            "employee_name": emp["name"],
            "dayflow_emp_id": emp["dayflow_emp_id"],
            "department": emp["department"],
            "date": cur_date_str,
            "check_in": cur_time_str,
            "check_out": "In Progress (Active)",
            "status": "Present",
            "worked_hours": "0.1 hrs"
        })
        return {"status": "checked_in", "message": f"Welcome, {emp['name']}! Checked in for today's workday."}

@app.post("/api/submit_leave")
def submit_leave(req: LeaveRequestPayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    cat_map = {"Paid Time Off (PTO)": "paid", "Sick Leave": "sick", "Unpaid Leave": "unpaid"}
    new_leave = {
        "id": len(DB["leaves"]) + 1,
        "employee_id": emp["id"],
        "employee_name": emp["name"],
        "dayflow_emp_id": emp["dayflow_emp_id"],
        "department": emp["department"],
        "type": req.leave_type,
        "category": cat_map.get(req.leave_type, "paid"),
        "date_from": req.date_from,
        "date_to": req.date_to,
        "number_of_days": req.days,
        "state": "confirm",
        "state_label": "Pending Approval",
        "remarks": req.remarks or "Time-off request",
        "manager_comment": ""
    }
    DB["leaves"].insert(0, new_leave)
    return {"success": True, "leave": new_leave, "message": "Time-off application submitted to HR."}

@app.post("/api/approve_leave")
def approve_leave(payload: LeaveActionPayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user.get("is_admin") and not user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Management can approve leaves.")
    leave = next((l for l in DB["leaves"] if l["id"] == payload.leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")
    leave["state"] = "validate"
    leave["state_label"] = "Approved"
    leave["manager_comment"] = payload.comment or f"Approved by {user['name']}."
    return {"success": True, "message": f"Leave approved for {leave['employee_name']}."}

@app.post("/api/refuse_leave")
def refuse_leave(payload: LeaveActionPayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user.get("is_admin") and not user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Management can refuse leaves.")
    leave = next((l for l in DB["leaves"] if l["id"] == payload.leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave record not found")
    leave["state"] = "refuse"
    leave["state_label"] = "Refused"
    leave["manager_comment"] = payload.comment or f"Declined by {user['name']}."
    return {"success": True, "message": f"Leave request for {leave['employee_name']} declined."}

@app.post("/api/update_profile")
def update_profile(payload: ProfileUpdatePayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if payload.work_phone is not None: emp["work_phone"] = payload.work_phone
    if payload.mobile_phone is not None: emp["mobile_phone"] = payload.mobile_phone
    if payload.private_city is not None: emp["private_city"] = payload.private_city
    if payload.emergency_contact_name is not None: emp["emergency_contact_name"] = payload.emergency_contact_name
    if payload.emergency_contact_relation is not None: emp["emergency_contact_relation"] = payload.emergency_contact_relation
    if payload.emergency_contact_phone is not None: emp["emergency_contact_phone"] = payload.emergency_contact_phone

    return {"success": True, "message": "Profile updated successfully!", "employee": emp}

@app.post("/api/admin/update_salary")
def update_salary(payload: AdminSalaryUpdatePayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user.get("is_admin") and not user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Management can update compensation.")

    emp = next((e for e in DB["employees"] if e["id"] == payload.employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee record not found")

    emp["salary_amount"] = payload.salary_amount
    emp["salary_type"] = payload.salary_type
    emp["bank_name"] = payload.bank_name
    emp["bank_account_no"] = payload.bank_account_no

    return {"success": True, "message": f"Salary updated for {emp['name']}."}

# ================= USER INTERFACE =================

@app.get("/", response_class=HTMLResponse)
def index_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dayflow HRMS | Human Resource Management System</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --primary: #6366f1;
            --primary-light: #818cf8;
            --primary-dark: #4f46e5;
            --primary-gradient: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg-body: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #273549;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --sidebar-width: 260px;
            --header-height: 72px;
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            --shadow-glow: 0 0 25px rgba(99, 102, 241, 0.3);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: var(--bg-body); color: var(--text-main); min-height: 100vh; display: flex; overflow-x: hidden; }

        /* Auth Overlay */
        #authOverlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 50% 20%, #1e1b4b 0%, #0f172a 70%);
            z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 1.5rem;
        }

        .auth-card {
            background: rgba(30, 41, 59, 0.95); backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 20px;
            width: 100%; max-width: 480px; box-shadow: var(--shadow-lg), var(--shadow-glow);
            overflow: hidden; animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }

        .auth-header { padding: 2rem 2rem 1.25rem; text-align: center; border-bottom: 1px solid var(--border); }
        .auth-brand { display: inline-flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
        .auth-body { padding: 1.75rem 2rem; }

        .demo-pills { margin-top: 1.25rem; padding-top: 1.25rem; border-top: 1px dashed var(--border); }
        .demo-pills-title { font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: var(--text-muted); margin-bottom: 0.6rem; letter-spacing: 0.05em; }
        .pill-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }

        .demo-btn {
            background: #0f172a; border: 1px solid var(--border); border-radius: 8px;
            padding: 0.5rem 0.75rem; color: #cbd5e1; font-size: 0.75rem; font-weight: 600;
            cursor: pointer; text-align: left; transition: all 0.2s ease; display: flex; flex-direction: column; gap: 0.15rem;
        }
        .demo-btn:hover { border-color: var(--primary); background: rgba(99, 102, 241, 0.1); color: white; }
        .demo-btn span { font-size: 0.65rem; color: var(--primary-light); }

        /* Sidebar */
        aside {
            width: var(--sidebar-width); background: #111827; border-right: 1px solid var(--border);
            display: flex; flex-direction: column; position: fixed; top: 0; bottom: 0; left: 0; z-index: 100;
        }

        .brand-header {
            height: var(--header-height); display: flex; align-items: center;
            padding: 0 1.5rem; gap: 0.75rem; border-bottom: 1px solid var(--border);
        }

        .brand-icon {
            width: 40px; height: 40px; background: var(--primary-gradient);
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            color: white; font-size: 1.2rem; box-shadow: var(--shadow-glow);
        }

        .brand-text h1 {
            font-size: 1.25rem; font-weight: 800; letter-spacing: -0.025em;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .brand-text span { font-size: 0.68rem; color: var(--primary-light); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; display: block; }
        .nav-group { padding: 1.25rem 0.75rem; display: flex; flex-direction: column; gap: 0.4rem; flex: 1; overflow-y: auto; }
        .nav-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); padding: 0.5rem 0.75rem; }

        .nav-item {
            display: flex; align-items: center; gap: 0.85rem; padding: 0.75rem 1rem;
            border-radius: 10px; color: var(--text-muted); text-decoration: none;
            font-size: 0.92rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease;
        }
        .nav-item:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-main); }
        .nav-item.active { background: var(--primary-gradient); color: white; box-shadow: var(--shadow-glow); font-weight: 600; }
        .nav-item i { width: 20px; font-size: 1.1rem; text-align: center; }

        .nav-badge { margin-left: auto; background: var(--danger); color: white; font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 9999px; font-weight: 700; }
        .sidebar-footer { padding: 1rem; border-top: 1px solid var(--border); background: rgba(0, 0, 0, 0.2); display: flex; flex-direction: column; gap: 0.6rem; }

        /* Main Area */
        main { margin-left: var(--sidebar-width); flex: 1; display: flex; flex-direction: column; min-height: 100vh; }

        header {
            height: var(--header-height); background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(12px); border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 2rem; position: sticky; top: 0; z-index: 90;
        }

        .header-title h2 { font-size: 1.35rem; font-weight: 700; color: white; display: flex; align-items: center; gap: 0.75rem; }
        .header-title p { font-size: 0.8rem; color: var(--text-muted); }
        .header-actions { display: flex; align-items: center; gap: 1rem; }

        .role-pill {
            display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.8rem;
            border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
        }
        .role-pill.admin { background: rgba(99, 102, 241, 0.18); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); }
        .role-pill.employee { background: rgba(16, 185, 129, 0.18); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }

        .status-chip {
            display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.9rem;
            border-radius: 9999px; font-size: 0.8rem; font-weight: 600;
            background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .status-chip.checked_out { background: rgba(239, 68, 68, 0.15); color: var(--danger); border-color: rgba(239, 68, 68, 0.3); }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

        .content { padding: 2rem; display: flex; flex-direction: column; gap: 2rem; flex: 1; }

        .hero-card {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%), var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 1.75rem 2rem;
            display: flex; align-items: center; justify-content: space-between; box-shadow: var(--shadow-lg);
        }

        .hero-left h3 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.4rem; }
        .hero-left p { color: var(--text-muted); font-size: 0.95rem; }

        .attendance-toggle-box {
            display: flex; align-items: center; gap: 1.5rem; background: rgba(0, 0, 0, 0.3);
            padding: 0.9rem 1.4rem; border-radius: 12px; border: 1px solid var(--border);
        }
        .time-display { display: flex; flex-direction: column; }
        .time-display .label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .time-display .value { font-family: 'JetBrains Mono', monospace; font-size: 1.35rem; font-weight: 700; color: white; }

        .btn {
            display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
            padding: 0.65rem 1.25rem; border-radius: 10px; font-size: 0.9rem; font-weight: 600;
            cursor: pointer; border: none; transition: all 0.2s ease; outline: none;
        }
        .btn-primary { background: var(--primary-gradient); color: white; box-shadow: var(--shadow-glow); }
        .btn-primary:hover { opacity: 0.92; transform: translateY(-1px); }
        .btn-danger { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); color: white; }
        .btn-success { background: linear-gradient(135deg, #10b981 0%, #047857 100%); color: white; }
        .btn-secondary { background: #0f172a; border: 1px solid var(--border); color: var(--text-main); }
        .btn-secondary:hover { background: var(--bg-card-hover); border-color: var(--primary-light); }

        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; }
        .metric-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
        .metric-header { display: flex; align-items: center; justify-content: space-between; }
        .metric-title { font-size: 0.82rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        .metric-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
        .icon-blue { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
        .icon-green { background: rgba(16, 185, 129, 0.15); color: #34d399; }
        .icon-yellow { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
        .icon-red { background: rgba(239, 68, 68, 0.15); color: #f87171; }
        .metric-value { font-size: 1.85rem; font-weight: 800; color: white; font-family: 'JetBrains Mono', monospace; }
        .metric-sub { font-size: 0.75rem; color: var(--text-muted); }

        .grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }
        @media (max-width: 1024px) { .grid-2 { grid-template-columns: 1fr; } }

        .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }
        .card-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .card-title { font-size: 1.1rem; font-weight: 700; color: white; display: flex; align-items: center; gap: 0.6rem; }
        .card-body { padding: 1.5rem; flex: 1; }

        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }
        th { background: rgba(0, 0, 0, 0.2); color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em; padding: 0.85rem 1rem; border-bottom: 1px solid var(--border); }
        td { padding: 0.95rem 1rem; border-bottom: 1px solid rgba(51, 65, 85, 0.4); color: #cbd5e1; }
        tr:hover td { background: rgba(255, 255, 255, 0.02); color: white; }

        .badge { display: inline-flex; align-items: center; padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 600; }
        .badge-pending { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-approved { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-refused { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-info { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }

        .form-group { margin-bottom: 1.1rem; display: flex; flex-direction: column; gap: 0.4rem; }
        .form-group label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
        .form-control { background: #0f172a; border: 1px solid var(--border); border-radius: 8px; padding: 0.65rem 0.9rem; color: white; font-size: 0.88rem; outline: none; }
        .form-control:focus { border-color: var(--primary); }
        textarea.form-control { resize: vertical; min-height: 80px; }

        .info-list { display: flex; flex-direction: column; gap: 0.9rem; }
        .info-item { display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.6rem; border-bottom: 1px solid rgba(51, 65, 85, 0.4); font-size: 0.85rem; }
        .info-item .info-label { color: var(--text-muted); }
        .info-item .info-val { font-weight: 600; color: white; }

        .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px); display: none; align-items: center; justify-content: center; z-index: 1000; }
        .modal-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; width: 90%; max-width: 580px; box-shadow: var(--shadow-lg); overflow: hidden; }
        .modal-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .modal-body { padding: 1.5rem; max-height: 75vh; overflow-y: auto; }
        .modal-footer { padding: 1rem 1.5rem; background: rgba(0, 0, 0, 0.2); border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 0.75rem; }

        #toast { position: fixed; bottom: 2rem; right: 2rem; padding: 0.9rem 1.4rem; border-radius: 10px; background: var(--bg-card); border: 1px solid var(--primary); box-shadow: var(--shadow-lg); color: white; font-weight: 600; font-size: 0.9rem; display: none; align-items: center; gap: 0.6rem; z-index: 20000; }
        .rbac-notice { background: rgba(99, 102, 241, 0.1); border: 1px dashed rgba(99, 102, 241, 0.4); border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.8rem; color: #c7d2fe; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.6rem; }

        .copy-box {
            background: #0f172a; border: 1px solid var(--border); border-radius: 8px;
            padding: 0.6rem 0.9rem; display: flex; align-items: center; justify-content: space-between;
            font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #cbd5e1; margin-bottom: 0.75rem;
        }
        .copy-btn { background: none; border: none; color: var(--primary-light); cursor: pointer; font-size: 0.9rem; padding: 0.2rem 0.5rem; }
        .copy-btn:hover { color: white; }

        /* Attendance Tab Hero */
        .att-banner {
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body>

    <!-- AUTHENTICATION LOGIN OVERLAY -->
    <div id="authOverlay">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-brand">
                    <div class="brand-icon"><i class="fa-solid fa-bolt"></i></div>
                    <div class="brand-text" style="text-align:left;">
                        <h1 style="font-size:1.35rem;">Dayflow HRMS</h1>
                        <span>Human Resource Portal</span>
                    </div>
                </div>
                <p style="font-size:0.82rem;color:var(--text-muted);">Sign in with your employee email &amp; password</p>
            </div>

            <div class="auth-body">
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label>Employee / HR Email ID</label>
                        <input type="email" id="loginEmail" class="form-control" placeholder="name@dayflow.demo" value="alex.morgan@dayflow.demo" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="loginPassword" class="form-control" placeholder="••••••••" value="dayflow123" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%;margin-top:0.5rem;">
                        <i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In to HRMS
                    </button>

                    <!-- Quick Demo Accounts -->
                    <div class="demo-pills">
                        <div class="demo-pills-title"><i class="fa-solid fa-bolt-lightning"></i> 1-Click Quick Demo Sign In</div>
                        <div class="pill-grid">
                            <button type="button" class="demo-btn" onclick="quickFill('alex.morgan@dayflow.demo', 'dayflow123')">
                                <strong>Alex Morgan</strong>
                                <span>HR Director (Admin)</span>
                            </button>
                            <button type="button" class="demo-btn" onclick="quickFill('jordan.smith@dayflow.demo', 'dayflow123')">
                                <strong>Jordan Smith</strong>
                                <span>Senior Engineer (Employee)</span>
                            </button>
                            <button type="button" class="demo-btn" onclick="quickFill('taylor.reed@dayflow.demo', 'dayflow123')">
                                <strong>Taylor Reed</strong>
                                <span>Marketing Lead (Employee)</span>
                            </button>
                            <button type="button" class="demo-btn" onclick="quickFill('casey.patel@dayflow.demo', 'dayflow123')">
                                <strong>Casey Patel</strong>
                                <span>Operations (Employee)</span>
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- MAIN APP SIDEBAR -->
    <aside>
        <div class="brand-header">
            <div class="brand-icon"><i class="fa-solid fa-bolt"></i></div>
            <div class="brand-text">
                <h1>Dayflow HRMS</h1>
                <span>Odoo 17 Engine</span>
            </div>
        </div>

        <div class="nav-group">
            <div class="nav-label">Workspace</div>
            <a class="nav-item active" onclick="switchTab('dashboard')">
                <i class="fa-solid fa-chart-pie"></i>
                <span>Dashboard</span>
            </a>
            <a class="nav-item" onclick="switchTab('attendance')">
                <i class="fa-solid fa-clock"></i>
                <span>Attendance</span>
            </a>
            <a class="nav-item" onclick="switchTab('leaves')">
                <i class="fa-solid fa-calendar-check"></i>
                <span>Time-Off &amp; Leaves</span>
                <span class="nav-badge" id="pendingBadge" style="display:none;">1</span>
            </a>
            <a class="nav-item" onclick="switchTab('employees')">
                <i class="fa-solid fa-users"></i>
                <span>Employee Directory</span>
            </a>
            <a class="nav-item" onclick="switchTab('salary')">
                <i class="fa-solid fa-wallet"></i>
                <span>Compensation</span>
            </a>
            <a class="nav-item" onclick="switchTab('profile')">
                <i class="fa-solid fa-user-gear"></i>
                <span>My Profile</span>
            </a>
        </div>

        <div class="sidebar-footer">
            <button class="btn btn-secondary" style="width:100%;font-size:0.8rem;padding:0.5rem;" onclick="openAuthModal()">
                <i class="fa-solid fa-arrow-right-arrow-left"></i> Switch Account
            </button>
            <button class="btn btn-danger" style="width:100%;font-size:0.8rem;padding:0.5rem;" onclick="handleLogout()">
                <i class="fa-solid fa-power-off"></i> Sign Out
            </button>
        </div>
    </aside>

    <!-- MAIN VIEW -->
    <main>
        <header>
            <div class="header-title">
                <h2 id="pageTitle">
                    HR Administrator Dashboard
                    <span class="role-pill admin" id="headerRoleBadge"><i class="fa-solid fa-shield-halved"></i> HR Admin</span>
                </h2>
                <p id="pageSubtitle">Every workday, perfectly aligned.</p>
            </div>

            <div class="header-actions">
                <div class="status-chip" id="headerStatusChip">
                    <div class="status-dot"></div>
                    <span id="headerStatusText">Checked In</span>
                </div>

                <!-- HR ONLY: CREATE EMPLOYEE BUTTON -->
                <button class="btn btn-success" id="hrCreateEmpHeaderBtn" style="font-size:0.82rem;padding:0.45rem 0.9rem;" onclick="openCreateEmpModal()">
                    <i class="fa-solid fa-user-plus"></i> Create New Employee &amp; Email ID
                </button>

                <div class="btn btn-secondary" style="padding:0.4rem 0.8rem;font-size:0.85rem;border-radius:9999px;" onclick="openAuthModal()">
                    <i class="fa-solid fa-circle-user" style="color:var(--primary-light);"></i>
                    <span id="headerUserName">Alex Morgan</span>
                </div>
            </div>
        </header>

        <div class="content">

            <!-- Hero Attendance Banner -->
            <div class="hero-card">
                <div class="hero-left">
                    <h3 id="greetingText">Good day, Alex Morgan!</h3>
                    <p id="heroSubText">Track attendance, manage workflows, and oversee organizational policies with RBAC precision.</p>
                </div>
                <div class="attendance-toggle-box">
                    <div class="time-display">
                        <span class="label">Worked Today</span>
                        <span class="value" id="workedTimer">03:24:10</span>
                    </div>
                    <button class="btn btn-primary" id="toggleAttendanceBtn" onclick="toggleAttendance()">
                        <i class="fa-solid fa-fingerprint"></i>
                        <span id="attendanceBtnLabel">Check Out</span>
                    </button>
                </div>
            </div>

            <!-- Tab: Dashboard -->
            <div id="tab-dashboard" class="tab-pane">
                <div class="rbac-notice" id="rbacNoticeBar">
                    <i class="fa-solid fa-lock"></i>
                    <span id="rbacNoticeText">RBAC Active: You have Full HR Management privileges.</span>
                </div>

                <!-- Admin Metrics -->
                <div class="metrics-grid" id="adminMetricsGrid">
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Total Employees</span>
                            <div class="metric-icon icon-blue"><i class="fa-solid fa-users"></i></div>
                        </div>
                        <div class="metric-value" id="mTotalEmps">4</div>
                        <div class="metric-sub">Organization wide</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Present Today</span>
                            <div class="metric-icon icon-green"><i class="fa-solid fa-user-check"></i></div>
                        </div>
                        <div class="metric-value" id="mPresentEmps">2</div>
                        <div class="metric-sub" id="mPresentPct">50% active attendance</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">On Leave</span>
                            <div class="metric-icon icon-yellow"><i class="fa-solid fa-umbrella-beach"></i></div>
                        </div>
                        <div class="metric-value" id="mOnLeave">1</div>
                        <div class="metric-sub">Sick &amp; PTO</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Absent / Pending</span>
                            <div class="metric-icon icon-red"><i class="fa-solid fa-user-xmark"></i></div>
                        </div>
                        <div class="metric-value" id="mAbsent">1</div>
                        <div class="metric-sub">Awaiting check-in</div>
                    </div>
                </div>

                <!-- Approvals & Profile -->
                <div class="grid-2" style="margin-top: 1.5rem;">
                    <div class="card" id="pendingApprovalsCard">
                        <div class="card-header">
                            <div class="card-title">
                                <i class="fa-solid fa-inbox" style="color:var(--primary-light);"></i>
                                Pending Leave Approvals (HR Queue)
                            </div>
                            <button class="btn btn-secondary" style="font-size:0.8rem;padding:0.35rem 0.75rem;" onclick="openLeaveModal()">
                                <i class="fa-solid fa-plus"></i> New Request
                            </button>
                        </div>
                        <div class="card-body" style="padding:0;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Employee</th>
                                        <th>Type</th>
                                        <th>Duration</th>
                                        <th>Days</th>
                                        <th>Remarks</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody id="pendingLeavesTable"></tbody>
                            </table>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">
                                <i class="fa-solid fa-id-card-clip" style="color:var(--accent);"></i>
                                Profile Summary
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="info-list" id="profileSummaryList"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab: Attendance -->
            <div id="tab-attendance" class="tab-pane" style="display:none;">
                
                <!-- ATTENDANCE QUICK ACTION BANNER -->
                <div class="att-banner">
                    <div style="display:flex;align-items:center;gap:1rem;">
                        <div class="brand-icon" style="width:48px;height:48px;font-size:1.4rem;">
                            <i class="fa-solid fa-business-time"></i>
                        </div>
                        <div>
                            <h3 style="font-size:1.15rem;font-weight:700;" id="attTabTitle">Daily Attendance Record</h3>
                            <p style="font-size:0.82rem;color:var(--text-muted);" id="attTabSub">
                                Real-time check-in, check-out timestamps, and automatic status classification.
                            </p>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:1rem;">
                        <button class="btn btn-primary" onclick="toggleAttendance()">
                            <i class="fa-solid fa-fingerprint"></i> <span id="attBannerBtnLabel">Check Out</span>
                        </button>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-clock-rotate-left" style="color:var(--primary-light);"></i>
                            <span id="attCardHeading">Attendance Logs &amp; Classification</span>
                        </div>
                        <button class="btn btn-secondary" style="font-size:0.8rem;padding:0.35rem 0.75rem;" onclick="fetchState()">
                            <i class="fa-solid fa-rotate"></i> Refresh Logs
                        </button>
                    </div>
                    <div class="card-body" style="padding:0;">
                        <table>
                            <thead>
                                <tr>
                                    <th># Log</th>
                                    <th>Employee</th>
                                    <th>Dayflow ID</th>
                                    <th>Department</th>
                                    <th>Date</th>
                                    <th>Check In</th>
                                    <th>Check Out</th>
                                    <th>Status</th>
                                    <th>Worked</th>
                                </tr>
                            </thead>
                            <tbody id="attendanceLogsTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Tab: Leaves -->
            <div id="tab-leaves" class="tab-pane" style="display:none;">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-calendar-days" style="color:var(--primary-light);"></i>
                            Time-Off &amp; Leave Requests
                        </div>
                        <button class="btn btn-primary" onclick="openLeaveModal()">
                            <i class="fa-solid fa-plus"></i> Request Time-Off
                        </button>
                    </div>
                    <div class="card-body" style="padding:0;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Employee</th>
                                    <th>Leave Type</th>
                                    <th>Duration</th>
                                    <th>Days</th>
                                    <th>Status</th>
                                    <th>Remarks</th>
                                    <th>Manager Feedback</th>
                                </tr>
                            </thead>
                            <tbody id="allLeavesTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Tab: Employees -->
            <div id="tab-employees" class="tab-pane" style="display:none;">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-address-book" style="color:var(--primary-light);"></i>
                            Employee Directory
                        </div>
                        <button class="btn btn-success" id="hrAddEmpBtnTab" onclick="openCreateEmpModal()">
                            <i class="fa-solid fa-user-plus"></i> Create New Employee &amp; Email ID
                        </button>
                    </div>
                    <div class="card-body" style="padding:0;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Dayflow ID</th>
                                    <th>Name</th>
                                    <th>Job Title</th>
                                    <th>Department</th>
                                    <th>Official Email ID</th>
                                    <th>Location</th>
                                    <th>Status</th>
                                    <th id="credentialsHeader">Credentials / Action</th>
                                </tr>
                            </thead>
                            <tbody id="employeesTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Tab: Salary -->
            <div id="tab-salary" class="tab-pane" style="display:none;">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-sack-dollar" style="color:var(--primary-light);"></i>
                            Compensation &amp; Payroll Layer
                        </div>
                    </div>
                    <div class="card-body" style="padding:0;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Employee</th>
                                    <th>Dayflow ID</th>
                                    <th>Salary Amount</th>
                                    <th>Structure</th>
                                    <th>Bank Name</th>
                                    <th>Account Number</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="salaryTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Tab: Profile Settings -->
            <div id="tab-profile" class="tab-pane" style="display:none;">
                <div class="card" style="max-width:720px;margin:0 auto;">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-user-pen" style="color:var(--primary-light);"></i>
                            Self-Service Profile Information
                        </div>
                    </div>
                    <div class="card-body">
                        <form id="profileForm" onsubmit="saveProfile(event)">
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                                <div class="form-group">
                                    <label>Work Phone</label>
                                    <input type="text" id="profWorkPhone" class="form-control" placeholder="+1 555-XXXX">
                                </div>
                                <div class="form-group">
                                    <label>Mobile Phone</label>
                                    <input type="text" id="profMobilePhone" class="form-control" placeholder="+1 555-XXXX">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Private City / Location</label>
                                <input type="text" id="profCity" class="form-control" placeholder="City">
                            </div>
                            <h4 style="margin:1.25rem 0 0.75rem;font-size:0.95rem;color:var(--primary-light);">Emergency Contact Details</h4>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                                <div class="form-group">
                                    <label>Contact Name</label>
                                    <input type="text" id="profEmergName" class="form-control" placeholder="Full Name">
                                </div>
                                <div class="form-group">
                                    <label>Relationship</label>
                                    <input type="text" id="profEmergRel" class="form-control" placeholder="Spouse / Parent / Sibling">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Emergency Phone</label>
                                <input type="text" id="profEmergPhone" class="form-control" placeholder="+1 555-XXXX">
                            </div>
                            <button type="submit" class="btn btn-primary" style="margin-top:0.5rem;width:100%;">
                                <i class="fa-solid fa-floppy-disk"></i> Save Profile Details
                            </button>
                        </form>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <!-- HR MODAL: CREATE EMPLOYEE EMAIL ID & ACCOUNT WITH PASSWORD -->
    <div id="createEmpModal" class="modal-overlay">
        <div class="modal-card">
            <div class="modal-header">
                <h3 style="font-size:1.15rem;font-weight:700;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fa-solid fa-user-plus" style="color:var(--success);"></i>
                    Create New Employee &amp; Email ID
                </h3>
                <i class="fa-solid fa-xmark" style="cursor:pointer;font-size:1.2rem;" onclick="closeCreateEmpModal()"></i>
            </div>
            <div class="modal-body">
                <form id="createEmpForm" onsubmit="handleHRCreateEmployee(event)">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                        <div class="form-group">
                            <label>Employee Full Name *</label>
                            <input type="text" id="newEmpName" class="form-control" placeholder="e.g. Kavitha Murugan" oninput="autoSuggestEmail(this.value)" required>
                        </div>
                        <div class="form-group">
                            <label>Assigned Official Email ID *</label>
                            <input type="email" id="newEmpEmail" class="form-control" placeholder="kavitha.m@dayflow.demo" required>
                        </div>
                    </div>

                    <!-- PASSWORD CONFIGURATION SECTION -->
                    <div class="form-group" style="background:rgba(0,0,0,0.2);padding:0.9rem;border-radius:10px;border:1px solid var(--border);">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                            <label style="color:white;font-weight:700;"><i class="fa-solid fa-key" style="color:var(--primary-light);"></i> Initial Login Password *</label>
                            <button type="button" class="btn btn-secondary" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="generateStrongPassword()">
                                <i class="fa-solid fa-dice"></i> Generate Random
                            </button>
                        </div>
                        <div style="position:relative;display:flex;align-items:center;">
                            <input type="text" id="newEmpPassword" class="form-control" style="font-family:'JetBrains Mono';padding-right:2.5rem;" value="Dayflow@2026" required>
                            <i class="fa-solid fa-eye" id="pwdToggleIcon" style="position:absolute;right:0.9rem;cursor:pointer;color:var(--text-muted);" onclick="togglePasswordVisibility('newEmpPassword', 'pwdToggleIcon')"></i>
                        </div>
                        <span style="font-size:0.72rem;color:var(--text-muted);margin-top:0.3rem;display:block;">
                            The employee will use this password and their email ID to log in to the Dayflow HR portal.
                        </span>
                    </div>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                        <div class="form-group">
                            <label>Department *</label>
                            <select id="newEmpDept" class="form-control">
                                <option value="Engineering">Engineering</option>
                                <option value="Human Resources">Human Resources</option>
                                <option value="Marketing & Growth">Marketing & Growth</option>
                                <option value="Operations">Operations</option>
                                <option value="Finance & Accounts">Finance & Accounts</option>
                                <option value="Quality Assurance">Quality Assurance</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Job Title *</label>
                            <input type="text" id="newEmpJobTitle" class="form-control" placeholder="e.g. Senior QA Engineer" required>
                        </div>
                    </div>

                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                        <div class="form-group">
                            <label>Security Role *</label>
                            <select id="newEmpRole" class="form-control">
                                <option value="employee">Employee (Self-Service)</option>
                                <option value="hr_officer">HR Director / Administrator</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Monthly Salary ($)</label>
                            <input type="number" id="newEmpSalary" class="form-control" value="7500" min="1000" step="100">
                        </div>
                    </div>

                    <div class="modal-footer" style="padding-right:0;padding-left:0;border:none;margin-top:1rem;">
                        <button type="button" class="btn btn-secondary" onclick="closeCreateEmpModal()">Cancel</button>
                        <button type="submit" class="btn btn-success"><i class="fa-solid fa-user-check"></i> Provision Employee Account</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- SUCCESS CREDENTIALS MODAL -->
    <div id="credentialsSuccessModal" class="modal-overlay">
        <div class="modal-card" style="max-width:500px;">
            <div class="modal-header" style="background:rgba(16,185,129,0.15);border-bottom:1px solid rgba(16,185,129,0.3);">
                <h3 style="font-size:1.15rem;font-weight:700;color:var(--success);display:flex;align-items:center;gap:0.5rem;">
                    <i class="fa-solid fa-circle-check"></i> Employee Account Created!
                </h3>
                <i class="fa-solid fa-xmark" style="cursor:pointer;font-size:1.2rem;" onclick="closeCredentialsModal()"></i>
            </div>
            <div class="modal-body">
                <p style="font-size:0.88rem;color:#cbd5e1;margin-bottom:1.25rem;">
                    The employee has been provisioned. Share these login credentials with the team member:
                </p>

                <div class="form-group">
                    <label>Employee Name &amp; ID</label>
                    <div class="copy-box"><span id="succEmpName">Kavitha Murugan (DF-1005)</span></div>
                </div>

                <div class="form-group">
                    <label>Official Email ID</label>
                    <div class="copy-box">
                        <span id="succEmpEmail">kavitha.m@dayflow.demo</span>
                        <button class="copy-btn" onclick="copyText('succEmpEmail')"><i class="fa-solid fa-copy"></i> Copy</button>
                    </div>
                </div>

                <div class="form-group">
                    <label>Assigned Password</label>
                    <div class="copy-box">
                        <span id="succEmpPassword" style="color:var(--success);font-weight:700;">Dayflow@2026</span>
                        <button class="copy-btn" onclick="copyText('succEmpPassword')"><i class="fa-solid fa-copy"></i> Copy</button>
                    </div>
                </div>

                <div style="margin-top:1.5rem;display:flex;gap:0.75rem;">
                    <button class="btn btn-primary" style="flex:1;" onclick="testLoginAsCreated()">
                        <i class="fa-solid fa-arrow-right-to-bracket"></i> Sign in as this Employee
                    </button>
                    <button class="btn btn-secondary" onclick="closeCredentialsModal()">Done</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Leave Request Modal -->
    <div id="leaveModal" class="modal-overlay">
        <div class="modal-card">
            <div class="modal-header">
                <h3 style="font-size:1.15rem;font-weight:700;">Submit Time-Off Request</h3>
                <i class="fa-solid fa-xmark" style="cursor:pointer;font-size:1.2rem;" onclick="closeLeaveModal()"></i>
            </div>
            <div class="modal-body">
                <form id="leaveForm" onsubmit="submitLeave(event)">
                    <div class="form-group">
                        <label>Leave Category / Type</label>
                        <select id="leaveTypeInput" class="form-control">
                            <option value="Paid Time Off (PTO)">Paid Time Off (PTO)</option>
                            <option value="Sick Leave">Sick Leave</option>
                            <option value="Unpaid Leave">Unpaid Leave</option>
                        </select>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                        <div class="form-group">
                            <label>Start Date</label>
                            <input type="date" id="leaveDateFrom" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>End Date</label>
                            <input type="date" id="leaveDateTo" class="form-control" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Total Days</label>
                        <input type="number" id="leaveDays" class="form-control" min="0.5" step="0.5" value="1" required>
                    </div>
                    <div class="form-group">
                        <label>Employee Remarks / Reason</label>
                        <textarea id="leaveRemarks" class="form-control" placeholder="Provide details about your leave request..."></textarea>
                    </div>
                    <div class="modal-footer" style="padding-right:0;padding-left:0;border:none;margin-top:1rem;">
                        <button type="button" class="btn btn-secondary" onclick="closeLeaveModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary"><i class="fa-solid fa-paper-plane"></i> Submit Request</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast"><i class="fa-solid fa-circle-check"></i> <span id="toastMsg">Action completed</span></div>

    <script>
        let sessionToken = localStorage.getItem('dayflow_token') || 'session-alex-admin-token';
        let appState = null;
        let activeTab = 'dashboard';
        let lastCreatedCredentials = null;

        function showToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            toast.style.display = 'flex';
            setTimeout(() => { toast.style.display = 'none'; }, 3500);
        }

        function copyText(elemId) {
            const txt = document.getElementById(elemId).innerText;
            navigator.clipboard.writeText(txt);
            showToast("Copied to clipboard!");
        }

        function openAuthModal() { document.getElementById('authOverlay').style.display = 'flex'; }
        function closeAuthModal() { document.getElementById('authOverlay').style.display = 'none'; }

        function openCreateEmpModal() {
            document.getElementById('createEmpModal').style.display = 'flex';
        }
        function closeCreateEmpModal() {
            document.getElementById('createEmpModal').style.display = 'none';
        }

        function openCredentialsModal(creds) {
            lastCreatedCredentials = creds;
            document.getElementById('succEmpName').innerText = `${creds.name} (${creds.dayflow_emp_id})`;
            document.getElementById('succEmpEmail').innerText = creds.email;
            document.getElementById('succEmpPassword').innerText = creds.password;
            document.getElementById('credentialsSuccessModal').style.display = 'flex';
        }

        function closeCredentialsModal() {
            document.getElementById('credentialsSuccessModal').style.display = 'none';
        }

        function testLoginAsCreated() {
            if (!lastCreatedCredentials) return;
            closeCredentialsModal();
            quickFill(lastCreatedCredentials.email, lastCreatedCredentials.password);
            openAuthModal();
        }

        function generateStrongPassword() {
            const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%";
            let pwd = "DF@";
            for (let i = 0; i < 6; i++) {
                pwd += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            document.getElementById('newEmpPassword').value = pwd;
            showToast("Generated strong password!");
        }

        function togglePasswordVisibility(inputId, iconId) {
            const inp = document.getElementById(inputId);
            const ico = document.getElementById(iconId);
            if (inp.type === "password") {
                inp.type = "text";
                ico.className = "fa-solid fa-eye-slash";
            } else {
                inp.type = "password";
                ico.className = "fa-solid fa-eye";
            }
        }

        function autoSuggestEmail(name) {
            if (!name) return;
            const cleaned = name.toLowerCase().trim().replace(/[^a-z0-9 ]/g, '').replace(/\\s+/g, '.');
            document.getElementById('newEmpEmail').value = `${cleaned}@dayflow.demo`;
        }

        function quickFill(email, pw) {
            document.getElementById('loginEmail').value = email;
            document.getElementById('loginPassword').value = pw;
        }

        async function handleLogin(e) {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Login failed');
                
                sessionToken = data.token;
                localStorage.setItem('dayflow_token', sessionToken);
                closeAuthModal();
                showToast(`Welcome back, ${data.user.name}!`);
                fetchState();
            } catch (err) {
                alert(err.message);
            }
        }

        async function handleHRCreateEmployee(e) {
            e.preventDefault();
            const payload = {
                name: document.getElementById('newEmpName').value,
                email: document.getElementById('newEmpEmail').value,
                password: document.getElementById('newEmpPassword').value,
                role: document.getElementById('newEmpRole').value,
                department: document.getElementById('newEmpDept').value,
                job_title: document.getElementById('newEmpJobTitle').value,
                salary_amount: parseFloat(document.getElementById('newEmpSalary').value) || 7500.0
            };

            try {
                const res = await fetch('/api/admin/create_employee', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Failed to create employee');

                closeCreateEmpModal();
                document.getElementById('createEmpForm').reset();
                document.getElementById('newEmpPassword').value = "Dayflow@2026";
                openCredentialsModal(data.credentials);
                fetchState();
            } catch (err) {
                alert(err.message);
            }
        }

        async function handleResetPassword(email, name) {
            const newPw = prompt(`Enter new password for ${name} (${email}):`, "Dayflow@" + Math.floor(1000 + Math.random() * 9000));
            if (!newPw) return;

            const res = await fetch('/api/admin/reset_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                body: JSON.stringify({ email: email, new_password: newPw })
            });
            const data = await res.json();
            if (!res.ok) return alert(data.detail || 'Password reset failed');
            showToast(data.message);
            alert(`✅ Password Updated for ${name}!\n\nEmail: ${email}\nNew Password: ${newPw}`);
            fetchState();
        }

        async function handleLogout() {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${sessionToken}` }
            });
            localStorage.removeItem('dayflow_token');
            sessionToken = '';
            showToast('Logged out successfully.');
            openAuthModal();
        }

        async function fetchState() {
            try {
                const res = await fetch('/api/state', {
                    headers: { 'Authorization': `Bearer ${sessionToken}` }
                });
                if (res.status === 401) {
                    openAuthModal();
                    return;
                }
                appState = await res.json();
                closeAuthModal();
                render();
            } catch (err) {
                console.error(err);
            }
        }

        async function toggleAttendance() {
            const res = await fetch('/api/toggle_attendance', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${sessionToken}` }
            });
            const data = await res.json();
            showToast(data.message);
            fetchState();
        }

        async function approveLeave(id) {
            const comment = prompt("Enter manager approval feedback:", "Approved by HR Director.");
            if (comment === null) return;
            const res = await fetch('/api/approve_leave', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                body: JSON.stringify({ leave_id: id, comment: comment })
            });
            const data = await res.json();
            if (!res.ok) return alert(data.detail || 'Approval failed');
            showToast(data.message);
            fetchState();
        }

        async function refuseLeave(id) {
            const comment = prompt("Enter refusal reason:", "Declined due to team schedule overlap.");
            if (comment === null) return;
            const res = await fetch('/api/refuse_leave', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                body: JSON.stringify({ leave_id: id, comment: comment })
            });
            const data = await res.json();
            if (!res.ok) return alert(data.detail || 'Refusal failed');
            showToast(data.message);
            fetchState();
        }

        async function submitLeave(e) {
            e.preventDefault();
            const payload = {
                leave_type: document.getElementById('leaveTypeInput').value,
                date_from: document.getElementById('leaveDateFrom').value,
                date_to: document.getElementById('leaveDateTo').value,
                days: parseFloat(document.getElementById('leaveDays').value),
                remarks: document.getElementById('leaveRemarks').value
            };
            const res = await fetch('/api/submit_leave', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                closeLeaveModal();
                showToast("Leave request submitted to HR!");
                fetchState();
            }
        }

        async function saveProfile(e) {
            e.preventDefault();
            const payload = {
                work_phone: document.getElementById('profWorkPhone').value,
                mobile_phone: document.getElementById('profMobilePhone').value,
                private_city: document.getElementById('profCity').value,
                emergency_contact_name: document.getElementById('profEmergName').value,
                emergency_contact_relation: document.getElementById('profEmergRel').value,
                emergency_contact_phone: document.getElementById('profEmergPhone').value
            };
            const res = await fetch('/api/update_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            showToast(data.message);
            fetchState();
        }

        function switchTab(tabId) {
            activeTab = tabId;
            document.querySelectorAll('.tab-pane').forEach(el => el.style.display = 'none');
            document.getElementById('tab-' + tabId).style.display = 'block';

            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');

            const isAdm = appState && appState.is_admin;
            const titles = {
                'dashboard': [isAdm ? 'HR Administrator Dashboard' : 'Employee Workspace', isAdm ? 'Organization overview and RBAC approval queue' : 'Your personal workday schedule & attendance'],
                'attendance': [isAdm ? 'All Staff Attendance Logs' : 'My Attendance History', 'Daily check-in logs and status classification'],
                'leaves': ['Time-Off & Leave Management', isAdm ? 'All leave applications and company-wide requests' : 'Your submitted leave requests and balances'],
                'employees': ['Employee Directory', 'Organization team members and login accounts'],
                'salary': ['Compensation & Banking', isAdm ? 'Full company salary administration' : 'Your confidential compensation record'],
                'profile': ['My Profile', 'Manage personal and emergency contact details']
            };
            if (titles[tabId]) {
                document.getElementById('pageTitle').innerHTML = `${titles[tabId][0]} ${isAdm ? '<span class="role-pill admin"><i class="fa-solid fa-shield-halved"></i> HR Admin</span>' : '<span class="role-pill employee"><i class="fa-solid fa-user"></i> Employee</span>'}`;
                document.getElementById('pageSubtitle').innerText = titles[tabId][1];
            }
        }

        function openLeaveModal() {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('leaveDateFrom').value = today;
            document.getElementById('leaveDateTo').value = today;
            document.getElementById('leaveModal').style.display = 'flex';
        }

        function closeLeaveModal() { document.getElementById('leaveModal').style.display = 'none'; }

        function render() {
            if (!appState) return;
            const u = appState.current_user;
            const emp = appState.employee;
            const m = appState.metrics;
            const isAdm = appState.is_admin;

            document.getElementById('headerUserName').innerText = u.name;
            const roleBadge = document.getElementById('headerRoleBadge');
            const rbacNotice = document.getElementById('rbacNoticeText');
            const hrHeaderBtn = document.getElementById('hrCreateEmpHeaderBtn');
            const hrAddEmpBtnTab = document.getElementById('hrAddEmpBtnTab');

            if (isAdm) {
                roleBadge.className = 'role-pill admin';
                roleBadge.innerHTML = '<i class="fa-solid fa-shield-halved"></i> HR Admin';
                rbacNotice.innerHTML = `<strong>RBAC Role: HR Director / Administrator.</strong> Full organizational permissions and employee provisioning privileges.`;
                document.getElementById('adminMetricsGrid').style.display = 'grid';
                document.getElementById('pendingApprovalsCard').style.display = 'flex';
                hrHeaderBtn.style.display = 'inline-flex';
                if (hrAddEmpBtnTab) hrAddEmpBtnTab.style.display = 'inline-flex';
                document.getElementById('attCardHeading').innerText = 'All Staff Attendance Logs (Organization Wide)';
                document.getElementById('attTabTitle').innerText = 'Company-Wide Attendance Monitoring';
                document.getElementById('attTabSub').innerText = 'Live overview of active check-ins, worked hours, and daily attendance records.';
            } else {
                roleBadge.className = 'role-pill employee';
                roleBadge.innerHTML = '<i class="fa-solid fa-user"></i> Employee';
                rbacNotice.innerHTML = `<strong>RBAC Role: Employee (${emp ? emp.job_title : 'Team Member'}).</strong> Self-isolated data scope.`;
                document.getElementById('adminMetricsGrid').style.display = 'none';
                document.getElementById('pendingApprovalsCard').style.display = 'none';
                hrHeaderBtn.style.display = 'none';
                if (hrAddEmpBtnTab) hrAddEmpBtnTab.style.display = 'none';
                document.getElementById('attCardHeading').innerText = 'My Personal Attendance Logs';
                document.getElementById('attTabTitle').innerText = 'My Workday Attendance';
                document.getElementById('attTabSub').innerText = 'Your personal check-in/out timestamps and worked hours.';
            }

            const isCheckedIn = emp && emp.attendance_state === 'checked_in';
            const chip = document.getElementById('headerStatusChip');
            const chipText = document.getElementById('headerStatusText');
            const btn = document.getElementById('toggleAttendanceBtn');
            const btnLabel = document.getElementById('attendanceBtnLabel');
            const attBannerBtnLabel = document.getElementById('attBannerBtnLabel');

            if (isCheckedIn) {
                chip.className = 'status-chip';
                chipText.innerText = 'Checked In';
                btn.className = 'btn btn-danger';
                btnLabel.innerText = 'Check Out';
                if (attBannerBtnLabel) attBannerBtnLabel.innerText = 'Check Out';
            } else {
                chip.className = 'status-chip checked_out';
                chipText.innerText = 'Checked Out';
                btn.className = 'btn btn-primary';
                btnLabel.innerText = 'Check In';
                if (attBannerBtnLabel) attBannerBtnLabel.innerText = 'Check In';
            }

            document.getElementById('greetingText').innerText = `Good day, ${u.name}!`;
            document.getElementById('workedTimer').innerText = emp ? `${emp.worked_hours.toFixed(1)} hrs` : '0.0 hrs';

            document.getElementById('mTotalEmps').innerText = m.total_employees;
            document.getElementById('mPresentEmps').innerText = m.present_today;
            document.getElementById('mPresentPct').innerText = `${m.attendance_rate}% active attendance`;
            document.getElementById('mOnLeave').innerText = m.on_leave_today;
            document.getElementById('mAbsent').innerText = m.absent_today;

            const pendingBadge = document.getElementById('pendingBadge');
            if (isAdm && appState.pending_leaves.length > 0) {
                pendingBadge.style.display = 'inline-block';
                pendingBadge.innerText = appState.pending_leaves.length;
            } else {
                pendingBadge.style.display = 'none';
            }

            const ptBody = document.getElementById('pendingLeavesTable');
            if (appState.pending_leaves.length === 0) {
                ptBody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--text-muted);">No pending leave approvals in queue! 🎉</td></tr>`;
            } else {
                ptBody.innerHTML = appState.pending_leaves.map(l => `
                    <tr>
                        <td><strong>${l.employee_name}</strong><br><span style="font-size:0.75rem;color:var(--text-muted);">${l.department} (${l.dayflow_emp_id})</span></td>
                        <td><span class="badge badge-info">${l.type}</span></td>
                        <td>${l.date_from} &rarr; ${l.date_to}</td>
                        <td><strong>${l.number_of_days}d</strong></td>
                        <td style="max-width:180px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${l.remarks}</td>
                        <td>
                            <div style="display:flex;gap:0.4rem;">
                                <button class="btn btn-success" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="approveLeave(${l.id})"><i class="fa-solid fa-check"></i> Approve</button>
                                <button class="btn btn-danger" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="refuseLeave(${l.id})"><i class="fa-solid fa-xmark"></i> Refuse</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            }

            const pList = document.getElementById('profileSummaryList');
            if (emp) {
                pList.innerHTML = `
                    <div class="info-item"><span class="info-label">Dayflow ID</span><span class="info-val" style="font-family:'JetBrains Mono';color:var(--primary-light);">${emp.dayflow_emp_id}</span></div>
                    <div class="info-item"><span class="info-label">Job Title</span><span class="info-val">${emp.job_title}</span></div>
                    <div class="info-item"><span class="info-label">Department</span><span class="info-val">${emp.department}</span></div>
                    <div class="info-item"><span class="info-label">Official Email</span><span class="info-val">${emp.work_email}</span></div>
                    <div class="info-item"><span class="info-label">Location</span><span class="info-val">${emp.private_city}</span></div>
                    <div class="info-item"><span class="info-label">Compensation</span><span class="info-val" style="color:var(--success);">$${emp.salary_amount.toLocaleString()}.00/mo</span></div>
                `;
            }

            // Attendance Logs Table (with Empty State fallback)
            const attTable = document.getElementById('attendanceLogsTable');
            if (!appState.attendance_logs || appState.attendance_logs.length === 0) {
                attTable.innerHTML = `
                    <tr>
                        <td colspan="9" style="text-align:center;padding:3rem 1.5rem;">
                            <div style="display:flex;flex-direction:column;align-items:center;gap:0.75rem;">
                                <i class="fa-solid fa-clock-rotate-left" style="font-size:2.2rem;color:var(--primary-light);opacity:0.6;"></i>
                                <h4 style="font-size:1.05rem;color:white;">No attendance records found yet</h4>
                                <p style="font-size:0.85rem;color:var(--text-muted);max-width:400px;">
                                    Click <strong>Check In</strong> above to record your attendance for today's workday!
                                </p>
                                <button class="btn btn-primary" style="margin-top:0.4rem;" onclick="toggleAttendance()">
                                    <i class="fa-solid fa-fingerprint"></i> Check In Now
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            } else {
                attTable.innerHTML = appState.attendance_logs.map(a => {
                    const isPresent = (a.status || '').toLowerCase().includes('present');
                    const isHalf = (a.status || '').toLowerCase().includes('half');
                    let badgeClass = isPresent ? 'badge-approved' : (isHalf ? 'badge-pending' : 'badge-info');
                    return `
                        <tr>
                            <td><strong style="color:var(--text-muted);">#${a.id}</strong></td>
                            <td><strong style="color:white;">${a.employee_name}</strong></td>
                            <td><span style="font-family:'JetBrains Mono';color:var(--primary-light);">${a.dayflow_emp_id || 'DF-XXXX'}</span></td>
                            <td><span style="font-size:0.82rem;color:var(--text-muted);">${a.department || 'General'}</span></td>
                            <td>${a.date || a.check_in.split(' ')[0]}</td>
                            <td><span style="color:#6ee7b7;"><i class="fa-solid fa-arrow-right-to-bracket"></i> ${a.check_in}</span></td>
                            <td>${a.check_out && a.check_out.includes('Progress') ? `<span class="badge badge-pending"><i class="fa-solid fa-circle-dot"></i> In Progress</span>` : `<span style="color:#f87171;"><i class="fa-solid fa-arrow-right-from-bracket"></i> ${a.check_out || '—'}</span>`}</td>
                            <td><span class="badge ${badgeClass}">${a.status}</span></td>
                            <td><strong style="font-family:'JetBrains Mono';">${a.worked_hours}</strong></td>
                        </tr>
                    `;
                }).join('');
            }

            const allLeavesTable = document.getElementById('allLeavesTable');
            allLeavesTable.innerHTML = appState.all_leaves.map(l => {
                let badgeCls = 'badge-pending';
                if (l.state === 'validate') badgeCls = 'badge-approved';
                if (l.state === 'refuse') badgeCls = 'badge-refused';
                return `
                    <tr>
                        <td><strong>${l.employee_name}</strong> (${l.dayflow_emp_id})</td>
                        <td>${l.type}</td>
                        <td>${l.date_from} &rarr; ${l.date_to}</td>
                        <td>${l.number_of_days} Days</td>
                        <td><span class="badge ${badgeCls}">${l.state_label}</span></td>
                        <td>${l.remarks}</td>
                        <td><span style="color:var(--primary-light);font-size:0.8rem;">${l.manager_comment || '—'}</span></td>
                    </tr>
                `;
            }).join('');

            const empsTable = document.getElementById('employeesTable');
            empsTable.innerHTML = appState.all_employees.map(e => `
                <tr>
                    <td><strong style="font-family:'JetBrains Mono';color:var(--primary-light);">${e.dayflow_emp_id}</strong></td>
                    <td><strong>${e.name}</strong></td>
                    <td>${e.job_title}</td>
                    <td>${e.department}</td>
                    <td><a href="mailto:${e.work_email}" style="color:var(--primary-light);text-decoration:none;font-weight:600;">${e.work_email}</a></td>
                    <td>${e.private_city}</td>
                    <td><span class="badge ${e.attendance_state === 'checked_in' ? 'badge-approved' : 'badge-pending'}">${e.attendance_state === 'checked_in' ? 'Checked In' : 'Checked Out'}</span></td>
                    <td>
                        ${isAdm ? `
                            <div style="display:flex;gap:0.4rem;align-items:center;">
                                <button class="btn btn-secondary" style="padding:0.25rem 0.55rem;font-size:0.75rem;" onclick="handleResetPassword('${e.work_email}', '${e.name}')">
                                    <i class="fa-solid fa-key"></i> Reset Pwd
                                </button>
                            </div>
                        ` : `<span style="font-size:0.75rem;color:var(--text-muted);">Active</span>`}
                    </td>
                </tr>
            `).join('');

            const salTable = document.getElementById('salaryTable');
            salTable.innerHTML = appState.salary_records.map(e => `
                <tr>
                    <td><strong>${e.name}</strong></td>
                    <td>${e.dayflow_emp_id}</td>
                    <td><strong style="color:var(--success);font-size:0.95rem;">$${e.salary_amount.toLocaleString()}.00</strong></td>
                    <td>${e.salary_type}</td>
                    <td>${e.bank_name}</td>
                    <td><span style="font-family:'JetBrains Mono'">${e.bank_account_no}</span></td>
                    <td>
                        ${isAdm ? `<button class="btn btn-secondary" style="padding:0.25rem 0.6rem;font-size:0.75rem;" onclick="promptSalaryEdit(${e.id}, ${e.salary_amount})"><i class="fa-solid fa-pen-to-square"></i> Edit</button>` : `<span style="font-size:0.75rem;color:var(--text-muted);"><i class="fa-solid fa-lock"></i> Confidential</span>`}
                    </td>
                </tr>
            `).join('');

            if (emp) {
                document.getElementById('profWorkPhone').value = emp.work_phone || '';
                document.getElementById('profMobilePhone').value = emp.mobile_phone || '';
                document.getElementById('profCity').value = emp.private_city || '';
                document.getElementById('profEmergName').value = emp.emergency_contact_name || '';
                document.getElementById('profEmergRel').value = emp.emergency_contact_relation || '';
                document.getElementById('profEmergPhone').value = emp.emergency_contact_phone || '';
            }
        }

        async function promptSalaryEdit(empId, currentAmt) {
            const newAmtStr = prompt("Enter new monthly salary amount ($):", currentAmt);
            if (newAmtStr === null) return;
            const newAmt = parseFloat(newAmtStr);
            if (isNaN(newAmt)) return alert("Please enter a valid number.");

            const res = await fetch('/api/admin/update_salary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${sessionToken}` },
                body: JSON.stringify({
                    employee_id: empId,
                    salary_amount: newAmt,
                    salary_type: "Monthly Fixed",
                    bank_name: "Silicon Valley Bank",
                    bank_account_no: "US99 •••• 1234"
                })
            });
            const data = await res.json();
            if (!res.ok) return alert(data.detail || 'Update failed');
            showToast(data.message);
            fetchState();
        }

        fetchState();
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    port = 8069
    print("===============================================================")
    print(f">> Dayflow HRMS Server is starting on http://127.0.0.1:{port}")
    print(">> Features:")
    print("   * Attendance Logs & Status Classification (Present, Half-Day)")
    print("   * Create New Employee & Email ID with Password Generator")
    print("   * Employee Credential Copy Modal & Password Reset Workflow")
    print("   * RBAC Security: HR Director (Admin) vs Internal Employee")
    print("===============================================================")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
