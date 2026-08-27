from app import get_db_connection
import psycopg2

conn = get_db_connection()
try:
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS photo VARCHAR(255);")
    conn.commit()
    print("Column added successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
