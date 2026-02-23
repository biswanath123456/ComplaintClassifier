import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "complaints.db")

# Database helper functions
def get_connection():
    return sqlite3.connect(DB_PATH)

# Initialize the database and create the complaints table if it doesn't exist
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_text   TEXT NOT NULL,
            category         TEXT NOT NULL,
            priority         TEXT NOT NULL,
            rule_override    INTEGER NOT NULL,
            classified_at    TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# CRUD operations
def save_complaint(complaint_text, category, priority, rule_override):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (complaint_text, category, priority, rule_override, classified_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        complaint_text,
        category,
        priority,
        1 if rule_override else 0,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

# Query functions for dashboard
def get_all_complaints():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get counts for categories and priorities
def get_category_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM complaints GROUP BY category")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get counts for priorities
def get_priority_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT priority, COUNT(*) as count FROM complaints GROUP BY priority")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Get trend of high priority complaints over time
def get_high_priority_trend():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(classified_at) as day, COUNT(*) as count
        FROM complaints
        WHERE priority = 'High'
        GROUP BY day
        ORDER BY day ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def init_feedback_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id        INTEGER NOT NULL,
            complaint_text      TEXT NOT NULL,
            predicted_category  TEXT NOT NULL,
            predicted_priority  TEXT NOT NULL,
            correct_category    TEXT NOT NULL,
            correct_priority    TEXT NOT NULL,
            is_correct          INTEGER NOT NULL,
            submitted_at        TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_feedback(complaint_id, complaint_text, predicted_category,
                  predicted_priority, correct_category, correct_priority):
    is_correct = int(
        predicted_category == correct_category and
        predicted_priority == correct_priority
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (
            complaint_id, complaint_text, predicted_category, predicted_priority,
            correct_category, correct_priority, is_correct, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_id, complaint_text, predicted_category, predicted_priority,
        correct_category, correct_priority, is_correct,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_all_feedback():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_feedback_accuracy():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(is_correct) as correct
        FROM feedback
    """)
    row = cursor.fetchone()
    conn.close()
    total = row[0] or 0
    correct = row[1] or 0
    accuracy = round(correct / total, 3) if total > 0 else 0
    return {"total": total, "correct": correct, "accuracy": accuracy}

# Initialize table on import
init_db()
init_feedback_table()