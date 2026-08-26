import psycopg2
import psycopg2.extras
from config import Config
conn = psycopg2.connect(**Config.db_connection_params())
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT id, amount FROM advances WHERE employee_id = 1 AND status = 'Approved'")
    print(cur.fetchall())
