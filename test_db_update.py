from app import get_db_connection, _UPDATE_SQL, _INSERT_COLS
import psycopg2.extras
import json

conn = get_db_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute("SELECT * FROM employees ORDER BY id DESC LIMIT 1;")
row = cur.fetchone()

print("Row id:", row['id'])
print("Current photo:", row.get('photo'))

# update photo
cur.execute("UPDATE employees SET photo = 'test.jpg' WHERE id = %s", (row['id'],))
conn.commit()

cur.execute("SELECT * FROM employees WHERE id = %s", (row['id'],))
row = cur.fetchone()
print("Updated photo:", row.get('photo'))
conn.close()
