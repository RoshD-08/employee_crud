import psycopg2
import psycopg2.extras
from config import Config
conn = psycopg2.connect(**Config.db_connection_params())
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT id, employment_status FROM employees WHERE id = 1")
    print(cur.fetchone())
