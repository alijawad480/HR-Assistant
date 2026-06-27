import sqlite3
import os
from datetime import datetime

DB_PATH = "database/chat_history.db"


def init_db():
    """
    Create the database and tables if they don't exist.
    Call this once when the app starts.
    """
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Database ready")


def save_message(session_id, role, message):
    """
    Save a single message to the database.
    role is either 'user' or 'assistant'
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (session_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, message, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_chat_history(session_id):
    """
    Get all messages for a specific session in order.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message, created_at
        FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "role": row[0],
            "message": row[1],
            "created_at": row[2]
        })

    return history


def get_all_sessions():
    """
    Get list of all unique sessions.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT session_id, MIN(created_at) as started_at
        FROM chat_history
        GROUP BY session_id
        ORDER BY started_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    sessions = []
    for row in rows:
        sessions.append({
            "session_id": row[0],
            "started_at": row[1]
        })

    return sessions
