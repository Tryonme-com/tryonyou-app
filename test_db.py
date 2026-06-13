import sqlite3
DB_PATH = "benchmark.db"

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM refs")
    print("Row count:", cursor.fetchone()[0])
