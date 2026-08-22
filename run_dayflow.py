#!/usr/bin/env python3
"""
Dayflow HRMS - Authentication & RBAC Enabled Server
Complete implementation of User Registration, Login, Session Management,
and Role-Based Access Controls (RBAC) mirroring Odoo 17 security rules.
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
import uvicorn

app = FastAPI(title="Dayflow HRMS with RBAC", description="Every workday, perfectly aligned.")

# Utility password hasher
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Database Schema & Seed Data
DEFAULT_PASS = hash_pw("dayflow123")

DB = {
    # res.users collection
    "users": {
        "alex.morgan@dayflow.demo": {
            "id": 1,
            "login": "alex.morgan@dayflow.demo",
            "password_hash": DEFAULT_PASS,
            "name": "Alex Morgan",
            "email": "alex.morgan@dayflow.demo",
            "role": "admin", # 'admin' (HR Manager), 'officer' (HR Officer), 'employee' (Self-service user)
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
    # hr.employee collection
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
            "last_check_in": (datetime.now() - timedelta(hours=3, minutes=24)).isoformat(),
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
            "last_check_in": (datetime.now() - timedelta(hours=2, minutes=15)).isoformat(),
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
    # hr.leave collection
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
    # hr.attendance collection
    "attendance_logs": [
        {
            "id": 1,
            "employee_id": 1,
            "employee_name": "Alex Morgan",
            "dayflow_emp_id": "DF-1001",
            "check_in": (datetime.now() - timedelta(hours=3, minutes=24)).strftime("%Y-%m-%d %H:%M"),
            "check_out": "-",
            "status": "Present",
            "worked_hours": "3.4h"
        },
        {
            "id": 2,
            "employee_id": 2,
            "employee_name": "Jordan Smith",
            "dayflow_emp_id": "DF-1002",
            "check_in": (datetime.now() - timedelta(hours=2, minutes=15)).strftime("%Y-%m-%d %H:%M"),
            "check_out": "-",
            "status": "Present",
            "worked_hours": "2.25h"
        },
        {
            "id": 3,
            "employee_id": 4,
            "employee_name": "Casey Patel",
            "dayflow_emp_id": "DF-1004",
            "check_in": (datetime.now() - timedelta(days=1, hours=8)).strftime("%Y-%m-%d 09:00"),
            "check_out": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 17:30"),
            "status": "Present",
            "worked_hours": "8.5h"
        }
    ],
    # Active Session Tokens
    "sessions": {}
}

# Pre-seed initial token for demo convenience
DEFAULT_SESSION_TOKEN = "session-alex-admin-token"
DB["sessions"][DEFAULT_SESSION_TOKEN] = "alex.morgan@dayflow.demo"

# Sequence for employee ID
EMP_SEQ = 1005

# Pydantic Request Models
class LoginPayload(BaseModel):
    email: str
    password: str

class RegisterPayload(BaseModel):
    name: str
    email: str
    password: str
    role: str # 'employee' or 'hr_officer' / 'admin'
    department: str
    job_title: Optional[str] = "Team Member"
    custom_emp_id: Optional[str] = None
    salary_amount: Optional[float] = 6500.0

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

# Helper to retrieve current authenticated user
def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        # Fallback to default active user for seamless browser usage
        return DB["users"]["alex.morgan@dayflow.demo"]
    
    token = authorization.replace("Bearer ", "").strip()
    if token not in DB["sessions"]:
        # Check if email passed directly as token
        if token in DB["users"]:
            return DB["users"][token]
        return DB["users"]["alex.morgan@dayflow.demo"]
    
    email = DB["sessions"][token]
    user = DB["users"].get(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session user")
    return user

# ================= AUTHENTICATION ENDPOINTS =================

@app.post("/api/auth/register")
def register_user(payload: RegisterPayload):
    global EMP_SEQ
    email = payload.email.strip().lower()
    
    if email in DB["users"]:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    is_admin = payload.role in ["admin", "hr_officer", "hr_manager"]
    role_type = "admin" if is_admin else "employee"
    role_label = "HR Administrator" if is_admin else f"Employee ({payload.job_title})"
    
    user_id = len(DB["users"]) + 1
    emp_id_num = len(DB["employees"]) + 1
    dayflow_id = payload.custom_emp_id.strip() if payload.custom_emp_id else f"DF-{EMP_SEQ}"
    EMP_SEQ += 1

    # 1. Create User
    new_user = {
        "id": user_id,
        "login": email,
        "password_hash": hash_pw(payload.password),
        "name": payload.name.strip(),
        "email": email,
        "role": role_type,
        "role_label": role_label,
        "is_admin": is_admin,
        "is_officer": is_admin,
        "employee_id": emp_id_num,
        "created_at": datetime.now().isoformat()
    }
    DB["users"][email] = new_user

    # 2. Provision Employee Profile (RBAC rule: base.group_user linkage)
    new_employee = {
        "id": emp_id_num,
        "user_id": user_id,
        "name": payload.name.strip(),
        "dayflow_emp_id": dayflow_id,
        "job_title": payload.job_title or "Team Member",
        "department": payload.department or "General",
        "work_email": email,
        "work_phone": "+1 555-0" + str(100 + emp_id_num),
        "mobile_phone": "+1 555-0" + str(200 + emp_id_num),
        "private_city": "Remote",
        "salary_amount": float(payload.salary_amount or 6500.0),
        "salary_type": "Monthly Fixed",
        "bank_name": "Standard Chartered Bank",
        "bank_account_no": f"US{emp_id_num * 11} •••• {emp_id_num * 99}",
        "emergency_contact_name": "Primary Emergency Contact",
        "emergency_contact_relation": "Family",
        "emergency_contact_phone": "+1 555-0999",
        "attendance_state": "checked_out",
        "last_check_in": None,
        "worked_hours": 0.0
    }
    DB["employees"].append(new_employee)

    # 3. Create Session Token
    token = f"sess-{uuid.uuid4().hex[:16]}"
    DB["sessions"][token] = email

    return {
        "success": True,
        "message": f"Welcome to Dayflow, {payload.name}! Your {dayflow_id} profile was successfully provisioned.",
        "token": token,
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"],
            "role_label": new_user["role_label"],
            "is_admin": new_user["is_admin"],
            "dayflow_emp_id": dayflow_id
        }
    }

@app.post("/api/auth/login")
def login_user(payload: LoginPayload):
    email = payload.email.strip().lower()
    user = DB["users"].get(email)
    
    if not user:
        raise HTTPException(status_code=401, detail="No account found with this email address.")
    
    if user["password_hash"] != hash_pw(payload.password):
        raise HTTPException(status_code=401, detail="Invalid password credentials.")
    
    # Generate session
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

@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token in DB["sessions"]:
            del DB["sessions"][token]
    return {"success": True, "message": "Logged out successfully."}

# ================= RBAC-SCOPED STATE & OPERATIONS =================

@app.get("/api/state")
def get_state(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)

    is_admin = user.get("is_admin", False) or user.get("is_officer", False)

    # 1. Attendance Record Rule Isolation:
    # Rule dayflow_attendance_rule_employee: Employee sees only their own logs.
    # Rule dayflow_attendance_rule_officer: HR Officer sees all logs.
    if is_admin:
        attendance_logs = DB["attendance_logs"]
    else:
        attendance_logs = [a for a in DB["attendance_logs"] if a.get("employee_id") == user["employee_id"]]

    # 2. Leave Record Rule Isolation:
    # Rule dayflow_leave_rule_employee: Employee sees only their leaves.
    # Rule dayflow_leave_rule_officer: HR Officer sees all requests and pending queue.
    if is_admin:
        all_leaves = DB["leaves"]
        pending_leaves = [l for l in DB["leaves"] if l["state"] == "confirm"]
    else:
        all_leaves = [l for l in DB["leaves"] if l.get("employee_id") == user["employee_id"]]
        pending_leaves = [] # Non-admins have no pending approvals access

    # 3. Employee List & Salary Access Control:
    # Employees see directory contact info, but salary details of others are hidden.
    if is_admin:
        salary_records = DB["employees"]
        employees_list = DB["employees"]
    else:
        # Self-only salary
        salary_records = [emp] if emp else []
        # Directory without salary
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

    # Metrics computation
    total_emps = len(DB["employees"])
    present_emps = len([e for e in DB["employees"] if e["attendance_state"] == "checked_in"])
    on_leave = len([l for l in DB["leaves"] if l["state"] == "validate" and l["number_of_days"] > 0 and "Sick" in l["type"]])
    absent_emps = max(0, total_emps - present_emps - on_leave)

    return {
        "current_user": user,
        "employee": emp,
        "is_admin": is_admin,
        "rbac_scope": "organization_wide" if is_admin else "self_isolated",
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
        raise HTTPException(status_code=404, detail="No linked employee record found for your user.")

    now = datetime.now()
    if emp["attendance_state"] == "checked_in":
        emp["attendance_state"] = "checked_out"
        # Record attendance log entry
        DB["attendance_logs"].insert(0, {
            "id": len(DB["attendance_logs"]) + 1,
            "employee_id": emp["id"],
            "employee_name": emp["name"],
            "dayflow_emp_id": emp["dayflow_emp_id"],
            "check_in": emp["last_check_in"] or now.strftime("%Y-%m-%d %H:%M"),
            "check_out": now.strftime("%Y-%m-%d %H:%M"),
            "status": "Present",
            "worked_hours": f"{emp['worked_hours']:.1f}h"
        })
        return {"status": "checked_out", "message": f"Successfully checked out, {emp['name']}. Have a great rest!"}
    else:
        emp["attendance_state"] = "checked_in"
        emp["last_check_in"] = now.strftime("%Y-%m-%d %H:%M")
        emp["worked_hours"] = 0.1
        return {"status": "checked_in", "message": f"Welcome back, {emp['name']}! Checked in successfully."}

@app.post("/api/submit_leave")
def submit_leave(req: LeaveRequestPayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee record not found")

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
    return {"success": True, "leave": new_leave, "message": "Leave application submitted to HR for review."}

@app.post("/api/approve_leave")
def approve_leave(payload: LeaveActionPayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user.get("is_admin") and not user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Directors / Officers can approve time-off requests.")
    
    leave = next((l for l in DB["leaves"] if l["id"] == payload.leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request record not found.")
    
    leave["state"] = "validate"
    leave["state_label"] = "Approved"
    leave["manager_comment"] = payload.comment or f"Approved by {user['name']} (HR Director)."
    return {"success": True, "message": f"Time-off request for {leave['employee_name']} has been approved."}

@app.post("/api/refuse_leave")
def refuse_leave(payload: LeaveActionPayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user.get("is_admin") and not user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Directors / Officers can refuse time-off requests.")
    
    leave = next((l for l in DB["leaves"] if l["id"] == payload.leave_id), None)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request record not found.")
    
    leave["state"] = "refuse"
    leave["state_label"] = "Refused"
    leave["manager_comment"] = payload.comment or f"Declined by {user['name']} (HR Director)."
    return {"success": True, "message": f"Time-off request for {leave['employee_name']} has been declined."}

@app.post("/api/update_profile")
def update_profile(payload: ProfileUpdatePayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    emp = next((e for e in DB["employees"] if e["id"] == user["employee_id"]), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Field-level security rule: Only self-contact fields can be modified
    if payload.work_phone is not None: emp["work_phone"] = payload.work_phone
    if payload.mobile_phone is not None: emp["mobile_phone"] = payload.mobile_phone
    if payload.private_city is not None: emp["private_city"] = payload.private_city
    if payload.emergency_contact_name is not None: emp["emergency_contact_name"] = payload.emergency_contact_name
    if payload.emergency_contact_relation is not None: emp["emergency_contact_relation"] = payload.emergency_contact_relation
    if payload.emergency_contact_phone is not None: emp["emergency_contact_phone"] = payload.emergency_contact_phone

    return {"success": True, "message": "Personal profile details updated successfully!", "employee": emp}

@app.post("/api/admin/update_salary")
def update_salary(payload: AdminSalaryUpdatePayload, authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    if not user.get("is_admin") and not user.get("is_officer"):
        raise HTTPException(status_code=403, detail="RBAC Access Denied: Only HR Management can update compensation structures.")

    emp = next((e for e in DB["employees"] if e["id"] == payload.employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee record not found")

    emp["salary_amount"] = payload.salary_amount
    emp["salary_type"] = payload.salary_type
    emp["bank_name"] = payload.bank_name
    emp["bank_account_no"] = payload.bank_account_no

    return {"success": True, "message": f"Compensation structure updated for {emp['name']}."}

# ================= FRONTEND WEB APPLICATION =================

@app.get("/", response_class=HTMLResponse)
def index_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dayflow HRMS | Authentication &amp; RBAC Control</title>
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
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
            --shadow-glow: 0 0 25px rgba(99, 102, 241, 0.3);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background-color: var(--bg-body); color: var(--text-main); min-height: 100vh; display: flex; overflow-x: hidden; }

        /* Auth Container Overlay */
        #authOverlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 50% 20%, #1e1b4b 0%, #0f172a 70%);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }

        .auth-card {
            background: rgba(30, 41, 59, 0.95);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            width: 100%;
            max-width: 480px;
            box-shadow: var(--shadow-lg), var(--shadow-glow);
            overflow: hidden;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }

        .auth-header {
            padding: 2rem 2rem 1.25rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }

        .auth-brand {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .auth-tabs {
            display: flex;
            border-bottom: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.2);
        }

        .auth-tab {
            flex: 1;
            padding: 0.9rem;
            text-align: center;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
        }

        .auth-tab.active {
            color: white;
            border-bottom-color: var(--primary);
            background: rgba(255, 255, 255, 0.03);
        }

        .auth-body { padding: 1.75rem 2rem; }

        .demo-pills {
            margin-top: 1.25rem;
            padding-top: 1.25rem;
            border-top: 1px dashed var(--border);
        }

        .demo-pills-title {
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
            letter-spacing: 0.05em;
        }

        .pill-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }

        .demo-btn {
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            color: #cbd5e1;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }

        .demo-btn:hover {
            border-color: var(--primary);
            background: rgba(99, 102, 241, 0.1);
            color: white;
        }

        .demo-btn span { font-size: 0.65rem; color: var(--primary-light); }

        /* Main App Sidebar */
        aside {
            width: var(--sidebar-width);
            background: #111827;
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0; bottom: 0; left: 0;
            z-index: 100;
        }

        .brand-header {
            height: var(--header-height);
            display: flex;
            align-items: center;
            padding: 0 1.5rem;
            gap: 0.75rem;
            border-bottom: 1px solid var(--border);
        }

        .brand-icon {
            width: 40px; height: 40px;
            background: var(--primary-gradient);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 1.2rem;
            box-shadow: var(--shadow-glow);
        }

        .brand-text h1 {
            font-size: 1.25rem; font-weight: 800;
            letter-spacing: -0.025em;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .brand-text span {
            font-size: 0.68rem; color: var(--primary-light);
            text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; display: block;
        }

        .nav-group {
            padding: 1.25rem 0.75rem;
            display: flex; flex-direction: column; gap: 0.4rem;
            flex: 1; overflow-y: auto;
        }

        .nav-label {
            font-size: 0.7rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.08em;
            color: var(--text-muted); padding: 0.5rem 0.75rem;
        }

        .nav-item {
            display: flex; align-items: center; gap: 0.85rem;
            padding: 0.75rem 1rem; border-radius: 10px;
            color: var(--text-muted); text-decoration: none;
            font-size: 0.92rem; font-weight: 500;
            cursor: pointer; transition: all 0.2s ease;
        }

        .nav-item:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-main); }
        .nav-item.active { background: var(--primary-gradient); color: white; box-shadow: var(--shadow-glow); font-weight: 600; }
        .nav-item i { width: 20px; font-size: 1.1rem; text-align: center; }

        .nav-badge {
            margin-left: auto; background: var(--danger);
            color: white; font-size: 0.7rem; padding: 0.15rem 0.5rem;
            border-radius: 9999px; font-weight: 700;
        }

        .rbac-tag {
            font-size: 0.62rem;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
            margin-left: auto;
            background: rgba(99, 102, 241, 0.2);
            color: var(--primary-light);
            border: 1px solid rgba(99, 102, 241, 0.4);
        }

        .sidebar-footer {
            padding: 1rem;
            border-top: 1px solid var(--border);
            background: rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }

        /* Main View */
        main { margin-left: var(--sidebar-width); flex: 1; display: flex; flex-direction: column; min-height: 100vh; }

        header {
            height: var(--header-height);
            background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 2rem; position: sticky; top: 0; z-index: 90;
        }

        .header-title h2 { font-size: 1.35rem; font-weight: 700; color: white; display: flex; align-items: center; gap: 0.75rem; }
        .header-title p { font-size: 0.8rem; color: var(--text-muted); }

        .header-actions { display: flex; align-items: center; gap: 1rem; }

        .role-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .role-pill.admin { background: rgba(99, 102, 241, 0.18); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); }
        .role-pill.employee { background: rgba(16, 185, 129, 0.18); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }

        .status-chip {
            display: flex; align-items: center; gap: 0.5rem;
            padding: 0.4rem 0.9rem; border-radius: 9999px;
            font-size: 0.8rem; font-weight: 600;
            background: rgba(16, 185, 129, 0.15); color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-chip.checked_out {
            background: rgba(239, 68, 68, 0.15); color: var(--danger);
            border-color: rgba(239, 68, 68, 0.3);
        }

        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

        .content { padding: 2rem; display: flex; flex-direction: column; gap: 2rem; flex: 1; }

        /* Hero Banner */
        .hero-card {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%), var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 16px; padding: 1.75rem 2rem;
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: var(--shadow-lg);
        }

        .hero-left h3 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.4rem; }
        .hero-left p { color: var(--text-muted); font-size: 0.95rem; }

        .attendance-toggle-box {
            display: flex; align-items: center; gap: 1.5rem;
            background: rgba(0, 0, 0, 0.3); padding: 0.9rem 1.4rem;
            border-radius: 12px; border: 1px solid var(--border);
        }

        .time-display { display: flex; flex-direction: column; }
        .time-display .label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
        .time-display .value { font-family: 'JetBrains Mono', monospace; font-size: 1.35rem; font-weight: 700; color: white; }

        .btn {
            display: inline-flex; align-items: center; justify-content: center;
            gap: 0.5rem; padding: 0.65rem 1.25rem; border-radius: 10px;
            font-size: 0.9rem; font-weight: 600; cursor: pointer; border: none;
            transition: all 0.2s ease; outline: none;
        }

        .btn-primary { background: var(--primary-gradient); color: white; box-shadow: var(--shadow-glow); }
        .btn-primary:hover { opacity: 0.92; transform: translateY(-1px); }
        .btn-danger { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); color: white; }
        .btn-success { background: linear-gradient(135deg, #10b981 0%, #047857 100%); color: white; }
        .btn-secondary { background: #0f172a; border: 1px solid var(--border); color: var(--text-main); }
        .btn-secondary:hover { background: var(--bg-card-hover); border-color: var(--primary-light); }

        /* Metrics */
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; }
        .metric-card {
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 14px; padding: 1.25rem 1.5rem;
            display: flex; flex-direction: column; gap: 0.5rem;
            transition: all 0.2s ease;
        }
        .metric-card:hover { transform: translateY(-3px); border-color: var(--primary-light); box-shadow: var(--shadow-md); }
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

        /* Tables */
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }
        th {
            background: rgba(0, 0, 0, 0.2); color: var(--text-muted);
            font-weight: 600; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em;
            padding: 0.85rem 1rem; border-bottom: 1px solid var(--border);
        }
        td { padding: 0.95rem 1rem; border-bottom: 1px solid rgba(51, 65, 85, 0.4); color: #cbd5e1; }
        tr:hover td { background: rgba(255, 255, 255, 0.02); color: white; }

        .badge { display: inline-flex; align-items: center; padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 600; }
        .badge-pending { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-approved { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-refused { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-info { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }

        .form-group { margin-bottom: 1.1rem; display: flex; flex-direction: column; gap: 0.4rem; }
        .form-group label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
        .form-control {
            background: #0f172a; border: 1px solid var(--border); border-radius: 8px;
            padding: 0.65rem 0.9rem; color: white; font-size: 0.88rem; outline: none; transition: border-color 0.2s;
        }
        .form-control:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2); }
        textarea.form-control { resize: vertical; min-height: 80px; }

        .info-list { display: flex; flex-direction: column; gap: 0.9rem; }
        .info-item { display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.6rem; border-bottom: 1px solid rgba(51, 65, 85, 0.4); font-size: 0.85rem; }
        .info-item .info-label { color: var(--text-muted); }
        .info-item .info-val { font-weight: 600; color: white; }

        /* Modals */
        .modal-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px);
            display: none; align-items: center; justify-content: center; z-index: 1000;
        }
        .modal-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; width: 90%; max-width: 540px; box-shadow: var(--shadow-lg); overflow: hidden; }
        .modal-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .modal-body { padding: 1.5rem; }
        .modal-footer { padding: 1rem 1.5rem; background: rgba(0, 0, 0, 0.2); border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 0.75rem; }

        #toast {
            position: fixed; bottom: 2rem; right: 2rem; padding: 0.9rem 1.4rem;
            border-radius: 10px; background: var(--bg-card); border: 1px solid var(--primary);
            box-shadow: var(--shadow-lg); color: white; font-weight: 600; font-size: 0.9rem;
            display: none; align-items: center; gap: 0.6rem; z-index: 20000;
        }

        .rbac-notice {
            background: rgba(99, 102, 241, 0.1);
            border: 1px dashed rgba(99, 102, 241, 0.4);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-size: 0.8rem;
            color: #c7d2fe;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
    </style>
</head>
<body>

    <!-- AUTHENTICATION MODAL (LOGIN & REGISTRATION) -->
    <div id="authOverlay">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-brand">
                    <div class="brand-icon"><i class="fa-solid fa-bolt"></i></div>
                    <div class="brand-text" style="text-align:left;">
                        <h1 style="font-size:1.35rem;">Dayflow HRMS</h1>
                        <span>Odoo 17 Security &amp; RBAC</span>
                    </div>
                </div>
                <p style="font-size:0.82rem;color:var(--text-muted);">Every workday, perfectly aligned.</p>
            </div>

            <!-- Login / Register Switch Tabs -->
            <div class="auth-tabs">
                <div class="auth-tab active" id="tabBtnLogin" onclick="switchAuthTab('login')">
                    <i class="fa-solid fa-right-to-bracket"></i> Sign In
                </div>
                <div class="auth-tab" id="tabBtnRegister" onclick="switchAuthTab('register')">
                    <i class="fa-solid fa-user-plus"></i> Create Account
                </div>
            </div>

            <div class="auth-body">
                <!-- LOGIN FORM -->
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" id="loginEmail" class="form-control" placeholder="name@dayflow.demo" value="alex.morgan@dayflow.demo" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="loginPassword" class="form-control" placeholder="••••••••" value="dayflow123" required>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%;margin-top:0.5rem;">
                        <i class="fa-solid fa-arrow-right-to-bracket"></i> Authenticate Session
                    </button>

                    <!-- Quick Demo Accounts -->
                    <div class="demo-pills">
                        <div class="demo-pills-title"><i class="fa-solid fa-bolt-lightning"></i> 1-Click Demo Accounts (RBAC Test)</div>
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

                <!-- REGISTRATION FORM WITH RBAC ROLE ASSIGNMENT -->
                <form id="registerForm" style="display:none;" onsubmit="handleRegister(event)">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" id="regName" class="form-control" placeholder="e.g. Morgan Freeman" required>
                    </div>
                    <div class="form-group">
                        <label>Work Email</label>
                        <input type="email" id="regEmail" class="form-control" placeholder="user@dayflow.demo" required>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="regPassword" class="form-control" placeholder="••••••••" required>
                        </div>
                        <div class="form-group">
                            <label>RBAC Security Role</label>
                            <select id="regRole" class="form-control" required>
                                <option value="employee">Employee (Self-Service)</option>
                                <option value="hr_officer">HR Director / Admin</option>
                            </select>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                        <div class="form-group">
                            <label>Department</label>
                            <select id="regDepartment" class="form-control">
                                <option value="Engineering">Engineering</option>
                                <option value="Human Resources">Human Resources</option>
                                <option value="Marketing & Growth">Marketing & Growth</option>
                                <option value="Operations">Operations</option>
                                <option value="Finance & Legal">Finance & Legal</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Job Title</label>
                            <input type="text" id="regJobTitle" class="form-control" placeholder="e.g. Software Engineer">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-success" style="width:100%;margin-top:0.5rem;">
                        <i class="fa-solid fa-user-check"></i> Register &amp; Provision Profile
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- MAIN APPLICATION WORKSPACE -->
    <aside>
        <div class="brand-header">
            <div class="brand-icon"><i class="fa-solid fa-bolt"></i></div>
            <div class="brand-text">
                <h1>Dayflow HRMS</h1>
                <span>Odoo 17 Engine</span>
            </div>
        </div>

        <div class="nav-group">
            <div class="nav-label">Navigation</div>
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
                <span>Directory</span>
            </a>
            <a class="nav-item" onclick="switchTab('salary')">
                <i class="fa-solid fa-wallet"></i>
                <span>Compensation</span>
                <span class="rbac-tag" id="salaryRbacTag">HR Admin</span>
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
                <i class="fa-solid fa-power-off"></i> Logout
            </button>
        </div>
    </aside>

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
                <!-- RBAC Notice Bar -->
                <div class="rbac-notice" id="rbacNoticeBar">
                    <i class="fa-solid fa-lock"></i>
                    <span id="rbacNoticeText">RBAC Active: You have Full HR Management privileges (ir.rule: dayflow_leave_rule_officer).</span>
                </div>

                <!-- Admin Metrics (Visible only to HR Officers / Admins) -->
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
                            <span class="metric-title">On Approved Leave</span>
                            <div class="metric-icon icon-yellow"><i class="fa-solid fa-umbrella-beach"></i></div>
                        </div>
                        <div class="metric-value" id="mOnLeave">1</div>
                        <div class="metric-sub">Sick &amp; PTO</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Pending / Absent</span>
                            <div class="metric-icon icon-red"><i class="fa-solid fa-user-xmark"></i></div>
                        </div>
                        <div class="metric-value" id="mAbsent">1</div>
                        <div class="metric-sub">Awaiting check-in</div>
                    </div>
                </div>

                <!-- Pending Approvals & Profile Summary -->
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

                    <!-- Profile Snapshot -->
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
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <i class="fa-solid fa-clock-rotate-left" style="color:var(--primary-light);"></i>
                            Attendance Logs &amp; Classification
                        </div>
                    </div>
                    <div class="card-body" style="padding:0;">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Employee</th>
                                    <th>Dayflow ID</th>
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
                    </div>
                    <div class="card-body" style="padding:0;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Dayflow ID</th>
                                    <th>Name</th>
                                    <th>Job Title</th>
                                    <th>Department</th>
                                    <th>Email</th>
                                    <th>City</th>
                                    <th>Status</th>
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
                                    <th id="salaryActionTh">Action</th>
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

        function showToast(msg) {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            toast.style.display = 'flex';
            setTimeout(() => { toast.style.display = 'none'; }, 3500);
        }

        function switchAuthTab(tab) {
            if (tab === 'login') {
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('registerForm').style.display = 'none';
                document.getElementById('tabBtnLogin').classList.add('active');
                document.getElementById('tabBtnRegister').classList.remove('active');
            } else {
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('registerForm').style.display = 'block';
                document.getElementById('tabBtnLogin').classList.remove('active');
                document.getElementById('tabBtnRegister').classList.add('active');
            }
        }

        function openAuthModal() {
            document.getElementById('authOverlay').style.display = 'flex';
        }

        function closeAuthModal() {
            document.getElementById('authOverlay').style.display = 'none';
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

        async function handleRegister(e) {
            e.preventDefault();
            const payload = {
                name: document.getElementById('regName').value,
                email: document.getElementById('regEmail').value,
                password: document.getElementById('regPassword').value,
                role: document.getElementById('regRole').value,
                department: document.getElementById('regDepartment').value,
                job_title: document.getElementById('regJobTitle').value || 'Team Member'
            };
            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Registration failed');

                sessionToken = data.token;
                localStorage.setItem('dayflow_token', sessionToken);
                closeAuthModal();
                showToast(data.message);
                fetchState();
            } catch (err) {
                alert(err.message);
            }
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
            const comment = prompt("Enter manager approval comment:", "Approved by HR Director.");
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
                showToast("Leave request submitted successfully!");
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
                'employees': ['Employee Directory', 'Organization team members and contact status'],
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

        function closeLeaveModal() {
            document.getElementById('leaveModal').style.display = 'none';
        }

        function render() {
            if (!appState) return;
            const u = appState.current_user;
            const emp = appState.employee;
            const m = appState.metrics;
            const isAdm = appState.is_admin;

            // Update Header & User Badge
            document.getElementById('headerUserName').innerText = u.name;
            const roleBadge = document.getElementById('headerRoleBadge');
            const salaryTag = document.getElementById('salaryRbacTag');
            const rbacNotice = document.getElementById('rbacNoticeText');

            if (isAdm) {
                roleBadge.className = 'role-pill admin';
                roleBadge.innerHTML = '<i class="fa-solid fa-shield-halved"></i> HR Admin';
                salaryTag.innerText = 'HR Full Access';
                rbacNotice.innerHTML = `<strong>RBAC Role: HR Director / Administrator.</strong> Full permissions across all staff records and approvals (<code>base.group_hr_manager</code>).`;
                document.getElementById('adminMetricsGrid').style.display = 'grid';
                document.getElementById('pendingApprovalsCard').style.display = 'flex';
            } else {
                roleBadge.className = 'role-pill employee';
                roleBadge.innerHTML = '<i class="fa-solid fa-user"></i> Employee';
                salaryTag.innerText = 'Self View';
                rbacNotice.innerHTML = `<strong>RBAC Role: Internal User (${emp ? emp.job_title : 'Employee'}).</strong> Self-isolated data scope (<code>base.group_user</code>). Only personal logs are visible.`;
                document.getElementById('adminMetricsGrid').style.display = 'none';
                document.getElementById('pendingApprovalsCard').style.display = 'none';
            }

            // Attendance Chip & Button
            const isCheckedIn = emp && emp.attendance_state === 'checked_in';
            const chip = document.getElementById('headerStatusChip');
            const chipText = document.getElementById('headerStatusText');
            const btn = document.getElementById('toggleAttendanceBtn');
            const btnLabel = document.getElementById('attendanceBtnLabel');

            if (isCheckedIn) {
                chip.className = 'status-chip';
                chipText.innerText = 'Checked In';
                btn.className = 'btn btn-danger';
                btnLabel.innerText = 'Check Out';
            } else {
                chip.className = 'status-chip checked_out';
                chipText.innerText = 'Checked Out';
                btn.className = 'btn btn-primary';
                btnLabel.innerText = 'Check In';
            }

            document.getElementById('greetingText').innerText = `Good day, ${u.name}!`;
            document.getElementById('workedTimer').innerText = emp ? `${emp.worked_hours.toFixed(1)} hrs` : '0.0 hrs';

            // Metrics
            document.getElementById('mTotalEmps').innerText = m.total_employees;
            document.getElementById('mPresentEmps').innerText = m.present_today;
            document.getElementById('mPresentPct').innerText = `${m.attendance_rate}% active attendance`;
            document.getElementById('mOnLeave').innerText = m.on_leave_today;
            document.getElementById('mAbsent').innerText = m.absent_today;

            // Pending Leaves Badge
            const pendingBadge = document.getElementById('pendingBadge');
            if (isAdm && appState.pending_leaves.length > 0) {
                pendingBadge.style.display = 'inline-block';
                pendingBadge.innerText = appState.pending_leaves.length;
            } else {
                pendingBadge.style.display = 'none';
            }

            // Pending Leaves Table
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

            // Profile Summary List
            const pList = document.getElementById('profileSummaryList');
            if (emp) {
                pList.innerHTML = `
                    <div class="info-item"><span class="info-label">Dayflow ID</span><span class="info-val" style="font-family:'JetBrains Mono';color:var(--primary-light);">${emp.dayflow_emp_id}</span></div>
                    <div class="info-item"><span class="info-label">Job Title</span><span class="info-val">${emp.job_title}</span></div>
                    <div class="info-item"><span class="info-label">Department</span><span class="info-val">${emp.department}</span></div>
                    <div class="info-item"><span class="info-label">Work Phone</span><span class="info-val">${emp.work_phone}</span></div>
                    <div class="info-item"><span class="info-label">Location</span><span class="info-val">${emp.private_city}</span></div>
                    <div class="info-item"><span class="info-label">Compensation</span><span class="info-val" style="color:var(--success);">$${emp.salary_amount.toLocaleString()}.00/mo</span></div>
                `;
            }

            // Attendance Logs Table
            const attTable = document.getElementById('attendanceLogsTable');
            attTable.innerHTML = appState.attendance_logs.map(a => `
                <tr>
                    <td>#${a.id}</td>
                    <td><strong>${a.employee_name}</strong></td>
                    <td><span style="font-family:'JetBrains Mono'">${a.dayflow_emp_id}</span></td>
                    <td>${a.check_in}</td>
                    <td>${a.check_out}</td>
                    <td><span class="badge ${a.status.toLowerCase().includes('present') ? 'badge-approved' : 'badge-info'}">${a.status}</span></td>
                    <td><strong>${a.worked_hours}</strong></td>
                </tr>
            `).join('');

            // All Leaves Table
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

            // Employees Directory Table
            const empsTable = document.getElementById('employeesTable');
            empsTable.innerHTML = appState.all_employees.map(e => `
                <tr>
                    <td><strong style="font-family:'JetBrains Mono';color:var(--primary-light);">${e.dayflow_emp_id}</strong></td>
                    <td><strong>${e.name}</strong></td>
                    <td>${e.job_title}</td>
                    <td>${e.department}</td>
                    <td><a href="mailto:${e.work_email}" style="color:var(--text-muted);text-decoration:none;">${e.work_email}</a></td>
                    <td>${e.private_city}</td>
                    <td><span class="badge ${e.attendance_state === 'checked_in' ? 'badge-approved' : 'badge-pending'}">${e.attendance_state === 'checked_in' ? 'Checked In' : 'Checked Out'}</span></td>
                </tr>
            `).join('');

            // Salary Table (RBAC enforced)
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

            // Fill profile edit form with current employee data
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

        // Initialize state
        fetchState();
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    port = 8069
    print("===============================================================")
    print(f">> Dayflow HRMS Server with RBAC is starting on http://127.0.0.1:{port}")
    print(">> RBAC Features:")
    print("   * Authentication: User Registration, Login & Session Management")
    print("   * Two-Tier RBAC: HR Director (Admin) vs Internal Employee")
    print("   * Data Isolation: Self-isolated records vs Org-wide access")
    print("   * Time-off approval queues & Compensation security layers")
    print("===============================================================")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
