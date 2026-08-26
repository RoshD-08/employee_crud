-- schema.sql
-- Run this once against your PostgreSQL database to create the table this app needs.
--
--   createdb employee_db
--   psql -d employee_db -f schema.sql

-- ── Authentication & RBAC ──
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'HR', 'Finance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default users (password: 'password123')
INSERT INTO users (username, password_hash, role)
VALUES 
    ('admin', 'scrypt:32768:8:1$c0rPVVcHsJL3woTa$19ec59bbb199561e00b233fe22b8f04288bcfb47de1dd1674890138ad48f578400785931377d2bb9f1a6e376482fd3a12f37e8561c03ad6a658ff01e76cfa39f', 'Admin'),
    ('hr', 'scrypt:32768:8:1$c0rPVVcHsJL3woTa$19ec59bbb199561e00b233fe22b8f04288bcfb47de1dd1674890138ad48f578400785931377d2bb9f1a6e376482fd3a12f37e8561c03ad6a658ff01e76cfa39f', 'HR'),
    ('finance', 'scrypt:32768:8:1$c0rPVVcHsJL3woTa$19ec59bbb199561e00b233fe22b8f04288bcfb47de1dd1674890138ad48f578400785931377d2bb9f1a6e376482fd3a12f37e8561c03ad6a658ff01e76cfa39f', 'Finance')
ON CONFLICT (username) DO NOTHING;


CREATE TABLE IF NOT EXISTS employees (
    id             SERIAL PRIMARY KEY,
    first_name     VARCHAR(50)    NOT NULL,
    last_name      VARCHAR(50)    NOT NULL,
    email          VARCHAR(120)   NOT NULL UNIQUE,
    phone          VARCHAR(20),
    department     VARCHAR(60)    NOT NULL,
    position       VARCHAR(60)    NOT NULL,
    salary         NUMERIC(10, 2) NOT NULL DEFAULT 0,
    hire_date      DATE           NOT NULL DEFAULT CURRENT_DATE,
    created_at     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Keep updated_at current on every UPDATE
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_employees_updated_at ON employees;
CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Optional: a few sample rows so the UI isn't empty on first run
INSERT INTO employees (first_name, last_name, email, phone, department, position, salary, hire_date)
VALUES
    ('Amara',  'Silva',     'amara.silva@company.com',   '077-123-4567', 'Engineering', 'Software Engineer', 185000.00, '2023-03-14'),
    ('Nuwan',  'Perera',    'nuwan.perera@company.com',  '071-987-6543', 'Sales',       'Account Executive', 145000.00, '2022-11-02'),
    ('Ishara', 'Fernando',  'ishara.fernando@company.com','070-555-2211','Human Resources','HR Manager',      190000.00, '2021-06-19')
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- Migration columns — safe to re-run (ADD COLUMN IF NOT EXISTS)
-- ============================================================

-- Original location columns
ALTER TABLE employees ADD COLUMN IF NOT EXISTS address   TEXT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS latitude  NUMERIC(9, 6);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS longitude NUMERIC(9, 6);

-- ── Personal details ──
ALTER TABLE employees ADD COLUMN IF NOT EXISTS date_of_birth         DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS gender                VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS national_id           VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_contact_name  VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20);

-- ── Employment type & status ──
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employment_type   VARCHAR(30) DEFAULT 'Full-time';
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employment_status VARCHAR(30) DEFAULT 'Active';

-- ── Allowances ──
ALTER TABLE employees ADD COLUMN IF NOT EXISTS housing_allowance   NUMERIC(10, 2) DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS transport_allowance  NUMERIC(10, 2) DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS medical_allowance    NUMERIC(10, 2) DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS other_allowance      NUMERIC(10, 2) DEFAULT 0;

-- ── Bank / payment details ──
ALTER TABLE employees ADD COLUMN IF NOT EXISTS payment_method       VARCHAR(30) DEFAULT 'Bank Transfer';
ALTER TABLE employees ADD COLUMN IF NOT EXISTS bank_name            VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS bank_branch          VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS bank_account_number  VARCHAR(50);

-- ── Tax & statutory ──
ALTER TABLE employees ADD COLUMN IF NOT EXISTS tax_id              VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS epf_number          VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS esi_number          VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS tax_filing_status   VARCHAR(30);

-- ── Payroll: employee category & leave quotas ──
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_category      VARCHAR(20) DEFAULT 'Employee';
ALTER TABLE employees ADD COLUMN IF NOT EXISTS annual_leave_allowed   INTEGER DEFAULT 14;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS casual_leave_allowed   INTEGER DEFAULT 7;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS medical_leave_allowed  INTEGER DEFAULT 7;

-- ── Backfill sample rows with payroll data ──
UPDATE employees SET
    date_of_birth = '1995-07-22', gender = 'Female', national_id = '957221234V',
    employment_type = 'Full-time', employment_status = 'Active',
    housing_allowance = 25000, transport_allowance = 10000, medical_allowance = 15000,
    payment_method = 'Bank Transfer', bank_name = 'Commercial Bank',
    bank_branch = 'Colombo Fort', bank_account_number = '1234567890',
    tax_id = 'TIN-2023-00451', epf_number = 'EPF-ENG-0011',
    emergency_contact_name = 'Kamal Silva', emergency_contact_phone = '077-999-8888',
    employee_category = 'Employee', annual_leave_allowed = 14,
    casual_leave_allowed = 7, medical_leave_allowed = 7
WHERE email = 'amara.silva@company.com' AND employee_category IS NULL;

UPDATE employees SET
    date_of_birth = '1990-03-15', gender = 'Male', national_id = '900751890V',
    employment_type = 'Full-time', employment_status = 'Active',
    housing_allowance = 20000, transport_allowance = 8000, medical_allowance = 12000,
    payment_method = 'Bank Transfer', bank_name = 'Sampath Bank',
    bank_branch = 'Nugegoda', bank_account_number = '9876543210',
    tax_id = 'TIN-2022-00312', epf_number = 'EPF-SAL-0025',
    emergency_contact_name = 'Dilani Perera', emergency_contact_phone = '071-888-7777',
    employee_category = 'Labourer', annual_leave_allowed = 14,
    casual_leave_allowed = 7, medical_leave_allowed = 7
WHERE email = 'nuwan.perera@company.com' AND employee_category IS NULL;

UPDATE employees SET
    date_of_birth = '1988-11-08', gender = 'Female', national_id = '885121456V',
    employment_type = 'Full-time', employment_status = 'Active',
    housing_allowance = 30000, transport_allowance = 12000, medical_allowance = 18000,
    payment_method = 'Bank Transfer', bank_name = 'HNB',
    bank_branch = 'Bambalapitiya', bank_account_number = '5555666677',
    tax_id = 'TIN-2021-00198', epf_number = 'EPF-HR-0003',
    emergency_contact_name = 'Rohan Fernando', emergency_contact_phone = '070-777-6666',
    employee_category = 'Employee', annual_leave_allowed = 14,
    casual_leave_allowed = 7, medical_leave_allowed = 7
WHERE email = 'ishara.fernando@company.com' AND employee_category IS NULL;


-- ============================================================
-- NEW TABLES: Attendance, Payroll, Company Settings
-- ============================================================

-- ── Attendance: one row per employee per day ──
CREATE TABLE IF NOT EXISTS attendance (
    id               SERIAL PRIMARY KEY,
    employee_id      INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    work_date        DATE NOT NULL,
    arrival_time     TIME,
    departure_time   TIME,
    is_sunday        BOOLEAN DEFAULT FALSE,
    status           VARCHAR(20) NOT NULL DEFAULT 'Present',
    leave_type       VARCHAR(20),
    late_arrival     BOOLEAN DEFAULT FALSE,
    early_departure  BOOLEAN DEFAULT FALSE,
    ot_hours         NUMERIC(5, 2) DEFAULT 0,
    ot_hours_sunday  NUMERIC(5, 2) DEFAULT 0,
    notes            TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, work_date)
);

-- ── Payroll: one row per employee per month ──
CREATE TABLE IF NOT EXISTS payroll (
    id                     SERIAL PRIMARY KEY,
    employee_id            INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    year                   INTEGER NOT NULL,
    month                  INTEGER NOT NULL,
    -- Earnings
    basic_salary           NUMERIC(10, 2) NOT NULL,
    total_allowances       NUMERIC(10, 2) DEFAULT 0,
    ot_hours_weekday       NUMERIC(5, 2) DEFAULT 0,
    ot_hours_sunday        NUMERIC(5, 2) DEFAULT 0,
    ot_hours_sunday_triple NUMERIC(5, 2) DEFAULT 0,
    ot_payment             NUMERIC(10, 2) DEFAULT 0,
    bonus                  NUMERIC(10, 2) DEFAULT 0,
    incentive              NUMERIC(10, 2) DEFAULT 0,
    gross_salary           NUMERIC(12, 2) DEFAULT 0,
    -- Deductions
    epf_employee           NUMERIC(10, 2) DEFAULT 0,
    no_pay_deduction       NUMERIC(10, 2) DEFAULT 0,
    salary_advance         NUMERIC(10, 2) DEFAULT 0,
    loan_deduction         NUMERIC(10, 2) DEFAULT 0,
    other_deductions       NUMERIC(10, 2) DEFAULT 0,
    total_deductions       NUMERIC(12, 2) DEFAULT 0,
    -- Company contributions
    epf_employer           NUMERIC(10, 2) DEFAULT 0,
    etf_employer           NUMERIC(10, 2) DEFAULT 0,
    -- Result
    net_salary             NUMERIC(12, 2) DEFAULT 0,
    -- Attendance summary
    working_days           INTEGER DEFAULT 0,
    late_arrivals          INTEGER DEFAULT 0,
    early_departures       INTEGER DEFAULT 0,
    absences               INTEGER DEFAULT 0,
    no_pay_days            INTEGER DEFAULT 0,
    annual_leave_taken     INTEGER DEFAULT 0,
    casual_leave_taken     INTEGER DEFAULT 0,
    medical_leave_taken    INTEGER DEFAULT 0,
    -- Meta
    status                 VARCHAR(20) DEFAULT 'Draft',
    payment_status         VARCHAR(20) DEFAULT 'Pending',
    payment_date           DATE,
    payment_reference      VARCHAR(100),
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, year, month)
);

-- ── Company settings: bonus & incentive amounts ──
CREATE TABLE IF NOT EXISTS company_settings (
    id            SERIAL PRIMARY KEY,
    setting_key   VARCHAR(50) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO company_settings (setting_key, setting_value)
VALUES ('annual_bonus', '0'), ('monthly_incentive', '0')
ON CONFLICT (setting_key) DO NOTHING;
-- ── Advances & Loans ──
CREATE TABLE IF NOT EXISTS advances (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    date_requested DATE NOT NULL DEFAULT CURRENT_DATE,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    deduction_year INTEGER,
    deduction_month INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    installments INTEGER NOT NULL CHECK (installments > 0 AND installments <= 12),
    monthly_installment NUMERIC(10, 2) NOT NULL,
    remaining_amount NUMERIC(10, 2) NOT NULL,
    remaining_installments INTEGER NOT NULL,
    date_requested DATE NOT NULL DEFAULT CURRENT_DATE,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_installments (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
