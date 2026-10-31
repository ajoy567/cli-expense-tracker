import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_FILE = os.path.join(BASE_DIR, "expense_tracker.csv")
DB_FILE = os.path.join(BASE_DIR, "expense_tracker.db")
LOG_FILE = os.path.join(BASE_DIR, "activity.log")
BUDGET_FILE = os.path.join(BASE_DIR, "budget.json")
RECURRING_FILE = os.path.join(BASE_DIR, "recurring.json")

FIELDNAMES = ["ID", "Amount", "Category", "Description", "Date"]