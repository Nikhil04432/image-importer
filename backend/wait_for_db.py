import time
import psycopg2
import os

db_url = os.getenv("DATABASE_URL")

while True:
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print("Postgres is ready")
        break
    except Exception:
        print("Waiting for Postgres...")
        time.sleep(2)
