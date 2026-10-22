import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_FILE = os.path.join(BASE_DIR, "expense_tracker.csv")
LOG_FILE = os.path.join(BASE_DIR, "activity.log")

FIELDNAMES = ["ID", "Amount", "Category", "Description", "Date"]