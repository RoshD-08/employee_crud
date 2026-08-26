import psycopg2
from app import get_db_connection

def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS advances (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
                amount NUMERIC(10, 2) NOT NULL,
                date_requested DATE NOT NULL DEFAULT CURRENT_DATE,
                reason TEXT,
                status VARCHAR(20) DEFAULT 'Pending', -- Pending, Approved, Deducted, Rejected
                deduction_year INTEGER,
                deduction_month INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
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
                status VARCHAR(20) DEFAULT 'Pending', -- Pending, Approved, Completed, Rejected
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS loan_installments (
                id SERIAL PRIMARY KEY,
                loan_id INTEGER NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()
        print("Database tables created.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
