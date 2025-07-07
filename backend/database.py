import sqlite3
from datetime import datetime

DB_PATH = "database/alarms.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alarms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        sequence TEXT,
        confidence REAL,
        video TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_alarm(sequence, confidence, video_name=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO alarms (timestamp, sequence, confidence, video)
    VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), sequence, confidence, video_name))
    conn.commit()
    conn.close()
