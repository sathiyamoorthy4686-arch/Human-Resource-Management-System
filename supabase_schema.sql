-- =========================================================
-- Dayflow HRMS - Supabase PostgreSQL Database Schema
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard)
-- =========================================================

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_plain VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'employee',
    role_label VARCHAR(100) DEFAULT 'Employee',
    is_admin BOOLEAN DEFAULT FALSE,
    is_officer BOOLEAN DEFAULT FALSE,
    employee_id INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. EMPLOYEES TABLE
CREATE TABLE IF NOT EXISTS public.employees (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES public.users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    dayflow_emp_id VARCHAR(50) UNIQUE NOT NULL,
    job_title VARCHAR(100) DEFAULT 'Staff',
    department VARCHAR(100) DEFAULT 'General',
    work_email VARCHAR(255) UNIQUE NOT NULL,
    work_phone VARCHAR(50),
    mobile_phone VARCHAR(50),
    private_city VARCHAR(100) DEFAULT 'Headquarters',
    salary_amount NUMERIC(12, 2) DEFAULT 6500.00,
    salary_type VARCHAR(50) DEFAULT 'Monthly Fixed',
    bank_name VARCHAR(100) DEFAULT 'State Bank of India',
    bank_account_no VARCHAR(100) DEFAULT 'IN •••• 1000',
    emergency_contact_name VARCHAR(100),
    emergency_contact_relation VARCHAR(100),
    emergency_contact_phone VARCHAR(50),
    attendance_state VARCHAR(50) DEFAULT 'checked_out',
    last_check_in TIMESTAMP WITH TIME ZONE,
    worked_hours NUMERIC(5, 2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. ATTENDANCE LOGS TABLE
CREATE TABLE IF NOT EXISTS public.attendance_logs (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES public.employees(id) ON DELETE CASCADE,
    employee_name VARCHAR(255),
    dayflow_emp_id VARCHAR(50),
    department VARCHAR(100),
    date DATE DEFAULT CURRENT_DATE,
    check_in VARCHAR(50),
    check_out VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Present',
    worked_hours VARCHAR(50) DEFAULT '0.0 hrs',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. LEAVES TABLE
CREATE TABLE IF NOT EXISTS public.leaves (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES public.employees(id) ON DELETE CASCADE,
    employee_name VARCHAR(255),
    dayflow_emp_id VARCHAR(50),
    department VARCHAR(100),
    type VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT 'paid',
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    number_of_days NUMERIC(4, 1) DEFAULT 1.0,
    state VARCHAR(50) DEFAULT 'confirm',
    state_label VARCHAR(100) DEFAULT 'Pending Approval',
    remarks TEXT,
    manager_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. ENABLE ROW LEVEL SECURITY (RLS) & PUBLIC READ/WRITE POLICIES
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attendance_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leaves ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public all access on users" ON public.users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on employees" ON public.employees FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on attendance_logs" ON public.attendance_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on leaves" ON public.leaves FOR ALL USING (true) WITH CHECK (true);

-- 6. SEED MASTER HR ADMINISTRATOR (Sathiya Moorthy)
INSERT INTO public.users (id, login, email, password_hash, password_plain, name, role, role_label, is_admin, is_officer, employee_id)
VALUES (
    1,
    'sathiyamoorthy@dayflow.demo',
    'sathiyamoorthy@dayflow.demo',
    '2ca8b4ac0dcb6624fd8f89a7dc14271bb90286bba8e295e4d9b5b53181185d2c',
    'sathiya',
    'Sathiya Moorthy',
    'admin',
    'HR Director / Administrator',
    TRUE,
    TRUE,
    1
) ON CONFLICT (email) DO NOTHING;

INSERT INTO public.employees (id, user_id, name, dayflow_emp_id, job_title, department, work_email, work_phone, mobile_phone, private_city, salary_amount, salary_type, bank_name, bank_account_no, attendance_state)
VALUES (
    1,
    1,
    'Sathiya Moorthy',
    'DF-1001',
    'HR Director & Administrator',
    'Human Resources',
    'sathiyamoorthy@dayflow.demo',
    '+91 98765-43210',
    '+91 98765-43211',
    'Headquarters',
    9500.00,
    'Monthly Fixed',
    'State Bank of India',
    'IN89 •••• 5001',
    'checked_out'
) ON CONFLICT (work_email) DO NOTHING;
