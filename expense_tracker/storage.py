import sqlite3
import csv
import os
from datetime import date
from .config import DB_FILE, CSV_FILE

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT
            )
        ''')

def migrate_csv_to_db():
    """If the old CSV exists, import its data into SQLite and delete the CSV."""
    if not os.path.exists(CSV_FILE):
        return

    print("Migrating old CSV data to SQLite...")
    with get_connection() as conn:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            rows = list(csv.reader(file))
            
        start = 0
        if rows and rows[0] and rows[0][0].strip().lower() == "id":
            start = 1
            
        for row in rows[start:]:
            if len(row) < 4:
                continue
            try:
                expense_id = int(row[0])
                amount = float(row[1])
                category = row[2].strip()
                description = row[3].strip()
                expense_date = row[4].strip() if len(row) >= 5 else ""
                
                conn.execute(
                    "INSERT OR IGNORE INTO expenses (id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                    (expense_id, amount, category, description, expense_date)
                )
            except (ValueError, TypeError):
                continue
                
    os.rename(CSV_FILE, CSV_FILE + ".bak")
    print("Migration complete! Old CSV backed up.")

def load_db():
    """Loads expenses from SQLite into a dictionary."""
    init_db()
    migrate_csv_to_db()

    expenses = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, category, description, date FROM expenses")
        for row in cursor.fetchall():
            expenses[row["id"]] = {
                "Amount": row["amount"],
                "Category": row["category"],
                "Description": row["description"],
                "Date": row["date"] or ""
            }
    return expenses

def save_db(expenses):
    """Saves the dictionary back to SQLite."""
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses")
        for expense_id, details in expenses.items():
            conn.execute(
                "INSERT INTO expenses (id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                (expense_id, details["Amount"], details["Category"], details["Description"], details.get("Date", ""))
            )