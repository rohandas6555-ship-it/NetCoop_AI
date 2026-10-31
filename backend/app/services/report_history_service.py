import sqlite3, json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "netcoop_users.db"

def save_report(user_id, report):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            incident_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            filename TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            report_json TEXT NOT NULL
        )""")
        conn.execute("""INSERT INTO reports(user_id, incident_id, status, filename, report_json)
            VALUES(?,?,?,?,?)""", (user_id, report["incident_id"], report["status"],
            report.get("evidence_sources", [{}])[0].get("file", ""),
            json.dumps(report, ensure_ascii=False)))
        conn.commit()
    finally:
        conn.close()

def list_reports(user_id, limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            incident_id TEXT NOT NULL UNIQUE, status TEXT NOT NULL, filename TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, report_json TEXT NOT NULL)""")
        rows = conn.execute("""SELECT incident_id,status,filename,created_at
            FROM reports WHERE user_id=? ORDER BY id DESC LIMIT ?""",
            (user_id, min(max(int(limit),1),100))).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_report(user_id, incident_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT report_json FROM reports WHERE user_id=? AND incident_id=?",
                           (user_id, incident_id)).fetchone()
        return json.loads(row["report_json"]) if row else None
    finally:
        conn.close()
