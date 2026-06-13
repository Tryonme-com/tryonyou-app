import sys

with open("main_engine.py", "r") as f:
    content = f.read()

# Modify init_db to set WAL mode and increase timeout
old_init_db = """def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS refs (
                ref_id TEXT PRIMARY KEY,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            \"\"\"
        )"""

new_init_db = """def init_db() -> None:
    with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS refs (
                ref_id TEXT PRIMARY KEY,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            \"\"\"
        )"""
content = content.replace(old_init_db, new_init_db)

# Add _save_to_db helper function
new_post_slack = """def _post_to_slack(url: str, text: str) -> None:
    response = requests.post(
        url,
        json={"replace_original": True, "text": text},
        timeout=10,
    )
    response.raise_for_status()


def _save_to_db(ref_id: str, action_id: str) -> None:
    with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            "INSERT OR REPLACE INTO refs (ref_id, status) VALUES (?, ?)",
            (ref_id, action_id),
        )
        conn.commit()"""

content = content.replace("""def _post_to_slack(url: str, text: str) -> None:
    response = requests.post(
        url,
        json={"replace_original": True, "text": text},
        timeout=10,
    )
    response.raise_for_status()""", new_post_slack)

# Replace the synchronous sqlite3 call in the endpoint with run_in_executor
old_sqlite_call = """    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO refs (ref_id, status) VALUES (?, ?)",
            (ref_id, action_id),
        )
        conn.commit()"""

new_sqlite_call = """    try:
        await asyncio.get_running_loop().run_in_executor(
            executor,
            _save_to_db,
            ref_id,
            action_id,
        )
    except Exception:
        logger.exception("Error guardando en la base de datos")
        raise HTTPException(status_code=500, detail="Error interno")"""

content = content.replace(old_sqlite_call, new_sqlite_call)

with open("main_engine.py", "w") as f:
    f.write(content)
