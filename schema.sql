-- schema.sql
-- Run this once against your PostgreSQL database to create the table this app needs.
--
--   createdb employee_db
--   psql -d employee_db -f schema.sql

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

-- Add to the employees table (or run standalone if table already exists)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS address   TEXT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS latitude  NUMERIC(9, 6);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS longitude NUMERIC(9, 6);