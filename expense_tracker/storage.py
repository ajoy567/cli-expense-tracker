import sqlite3
import csv
import json
import os
from datetime import date
from .config import DB_FILE, CSV_FILE, BUDGET_FILE, RECURRING_FILE

def get_connection():
    """
    Returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Creates all tables if they don't exist.
    """
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
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                amount REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recurring_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                description TEXT,
                day INTEGER,
                last_added TEXT
            )
        ''')

def migrate_csv_to_db():
    """
    Migrates old CSV data to SQLite.
    """
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

def migrate_json_to_db():
    """
    Migrates old budget.json and recurring.json files to SQLite.
    """
    if os.path.exists(BUDGET_FILE):
        print("Migrating budgets.json to SQLite...")
        try:
            with open(BUDGET_FILE, "r", encoding="utf-8") as f:
                budgets = json.load(f)
                with get_connection() as conn:
                    for cat, amt in budgets.items():
                        conn.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (cat, amt))
            os.rename(BUDGET_FILE, BUDGET_FILE + ".bak")
        except Exception as e:
            print(f"Budget migration failed: {e}")

    if os.path.exists(RECURRING_FILE):
        print("Migrating recurring.json to SQLite...")
        try:
            with open(RECURRING_FILE, "r", encoding="utf-8") as f:
                rules = json.load(f)
                with get_connection() as conn:
                    for rule in rules:
                        conn.execute(
                            "INSERT INTO recurring_rules (amount, category, description, day, last_added) VALUES (?, ?, ?, ?, ?)",
                            (rule["amount"], rule["category"], rule["description"], rule["day"], rule.get("last_added", ""))
                        )
            os.rename(RECURRING_FILE, RECURRING_FILE + ".bak")
        except Exception as e:
            print(f"Recurring migration failed: {e}")

def load_db():
    """
    Loads expenses from SQLite into a dictionary.
    """
    init_db()
    migrate_csv_to_db()
    migrate_json_to_db()

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
    """
    Saves the dictionary back to SQLite.
    """
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM expenses")
        for expense_id, details in expenses.items():
            conn.execute(
                "INSERT INTO expenses (id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                (expense_id, details["Amount"], details["Category"], details["Description"], details.get("Date", ""))
            )
            