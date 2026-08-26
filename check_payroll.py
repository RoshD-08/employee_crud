import psycopg2
import psycopg2.extras
from config import Config
conn = psycopg2.connect(**Config.db_connection_params())
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT * FROM payroll")
    payrolls = cur.fetchall()
    for p in payrolls:
        print(f"Emp {p['employee_id']} - {p['year']}/{p['month']} : Advance={p['salary_advance']}, Loan={p['loan_deduction']}")
