import psycopg2
import psycopg2.extras
from config import Config
from datetime import date

conn = psycopg2.connect(**Config.db_connection_params())
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    eid = 1
    year = 2026
    month = 8
    print("Checking for EID", eid, "YEAR", year, "MONTH", month)
    cur.execute("SELECT id, amount FROM advances WHERE employee_id = %s AND status = 'Approved'", (eid,))
    new_advances = cur.fetchall()
    print("Advances found:", new_advances)
    for adv in new_advances:
        cur.execute("UPDATE advances SET status = 'Deducted', deduction_year = %s, deduction_month = %s WHERE id = %s", (year, month, adv["id"]))
        print("Updated advance", adv["id"])
    
    cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM advances WHERE employee_id = %s AND status = 'Deducted' AND deduction_year = %s AND deduction_month = %s", (eid, year, month))
    salary_advance = float(cur.fetchone()["total"])
    print("Salary Advance Deducted:", salary_advance)
conn.rollback()
