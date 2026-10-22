import csv
import os
from datetime import date

from .config import CSV_FILE, FIELDNAMES


def save_csv(expenses):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDNAMES)
        for expense_id, details in expenses.items():
            writer.writerow([
                expense_id,
                f"{details['Amount']:.2f}",
                details["Category"],
                details["Description"],
                details.get("Date", ""),
            ])


def load_csv():
    if not os.path.exists(CSV_FILE):
        return {}

    result = {}
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    if not rows:
        return result

    start = 0
    if rows[0] and rows[0][0].strip().lower() == "id":
        start = 1

    for row in rows[start:]:
        if len(row) < 4:
            continue
        try:
            expense_id = int(row[0])
            amount = float(row[1])
        except (ValueError, TypeError):
            continue

        category = row[2].strip()
        description = row[3].strip()

        expense_date = ""
        if len(row) >= 5:
            raw_date = row[4].strip()
            if raw_date:
                try:
                    expense_date = date.fromisoformat(raw_date).isoformat()
                except ValueError:
                    expense_date = ""

        result[expense_id] = {
            "Amount": round(amount, 2),
            "Category": category,
            "Description": description,
            "Date": expense_date,
        }

    return result