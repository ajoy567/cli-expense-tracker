import csv
import os
from datetime import date

CSV_FILE = "expense_tracker.csv"
FIELDNAMES = ["ID", "Amount", "Category", "Description", "Date"]


# ------------------------------- persistence ------------------------------

def save_csv(expenses):
    """
    Save all expenses to the CSV file using the csv module.
    Date is written as YYYY-MM-DD (empty string if unknown).
    """
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
    """
    Load expenses from the CSV file.

    Supports both:
      - Old format: ID, Amount, Category, Description              (4 columns)
      - New format: ID, Amount, Category, Description, Date        (5 columns)

    Old rows get an empty Date ("") which is displayed as "unknown".
    """
    if not os.path.exists(CSV_FILE):
        return {}

    result = {}

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    if not rows:
        return result

    start = 0
    if rows[0] and rows[0][0].strip().lower() == "id":
        start = 1  # skip header

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

        # Date is the 5th column, optional for legacy rows.
        expense_date = ""
        if len(row) >= 5:
            raw_date = row[4].strip()
            if raw_date:
                try:
                    expense_date = date.fromisoformat(raw_date).isoformat()
                except ValueError:
                    expense_date = ""  # invalid date → treat as unknown

        result[expense_id] = {
            "Amount": round(amount, 2),
            "Category": category,
            "Description": description,
            "Date": expense_date,
        }

    return result


# ------------------------------- actions ----------------------------------

def add_expense(expenses, expense_id, amount, category, description, expense_date):
    expenses[expense_id] = {
        "Amount": amount,
        "Category": category,
        "Description": description,
        "Date": expense_date,
    }
    save_csv(expenses)


def edit_expense(expenses, expense_id, new_amount, new_category, new_description, new_date):
    expenses[expense_id] = {
        "Amount": new_amount,
        "Category": new_category,
        "Description": new_description,
        "Date": new_date,
    }
    save_csv(expenses)


def delete_expense(expenses, expense_id):
    if expense_id in expenses:
        del expenses[expense_id]
        save_csv(expenses)
        return True
    return False


# ------------------------------- views ------------------------------------

def view_expense(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return

    for expense_id, details in expenses.items():
        d = details.get("Date") or "unknown"
        print(
            f"{expense_id}. {d} | {details['Category']} | "
            f"{details['Amount']:.2f} | {details['Description']}"
        )


def summary(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return

    total = sum(d["Amount"] for d in expenses.values())
    print(f"Total spent: {total:.2f}")

    dates = [d.get("Date") for d in expenses.values() if d.get("Date")]
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")

    by_category = {}
    for d in expenses.values():
        by_category[d["Category"]] = by_category.get(d["Category"], 0.0) + d["Amount"]

    for category, amount in sorted(by_category.items()):
        print(f"  {category}: {amount:.2f}")


# ------------------------------- input helpers ----------------------------

def prompt_amount(prompt_text="Enter the amount : "):
    while True:
        raw = input(prompt_text).strip()
        try:
            amount = float(raw)
        except ValueError:
            print("Amount must be a number. Please try again...")
            continue
        if amount <= 0:
            print("Amount must be greater than zero. Please try again...")
            continue
        return round(amount, 2)


def prompt_non_empty(prompt_text):
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again...")


def prompt_existing_id(expenses, prompt_text="Enter the expense ID : "):
    while True:
        raw = input(prompt_text).strip()
        try:
            expense_id = int(raw)
        except ValueError:
            print("ID must be a whole number. Please try again...")
            continue
        if expense_id not in expenses:
            print(f"No expense found with ID {expense_id}. Please try again...")
            continue
        return expense_id


def prompt_date(prompt_text="Enter date (YYYY-MM-DD) [today] : "):
    """Ask for a date. Blank input = today's date."""
    while True:
        raw = input(prompt_text).strip()
        if not raw:
            return date.today().isoformat()
        try:
            return date.fromisoformat(raw).isoformat()
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD (e.g. 2026-10-17). Try again...")


# ------------------------------- main loop --------------------------------

def main():
    expenses = load_csv()

    print("\nCLI EXPENSE TRACKER")

    while True:
        print("\n------------------------------ Your Options ------------------------------")
        print("1. Add Expense")
        print("2. View Expense")
        print("3. Summary")
        print("4. Edit Expense")
        print("5. Delete Expense")
        print("6. Exit")

        choice = input("Enter your choice : ").strip()

        match choice:
            case '1':
                amount = prompt_amount()
                category = prompt_non_empty("Enter the category of the expense : ")
                description = prompt_non_empty("Enter description for the expense : ")
                expense_date = prompt_date()
                expense_id = max(expenses.keys(), default=0) + 1
                add_expense(expenses, expense_id, amount, category, description, expense_date)
                print(f"Expense added with ID {expense_id} on {expense_date}!")

            case '2':
                view_expense(expenses)

            case '3':
                summary(expenses)

            case '4':
                if not expenses:
                    print("No expenses to edit.")
                    continue
                view_expense(expenses)
                expense_id = prompt_existing_id(expenses)
                current = expenses[expense_id]
                print("Press Enter on any field to keep the current value.")

                # Amount
                while True:
                    raw = input(f"New amount [{current['Amount']:.2f}] : ").strip()
                    if not raw:
                        new_amount = current["Amount"]
                        break
                    try:
                        val = float(raw)
                    except ValueError:
                        print("Amount must be a number. Please try again...")
                        continue
                    if val <= 0:
                        print("Amount must be greater than zero. Please try again...")
                        continue
                    new_amount = round(val, 2)
                    break

                # Category
                raw = input(f"New category [{current['Category']}] : ").strip()
                new_category = raw if raw else current["Category"]

                # Description
                raw = input(f"New description [{current['Description']}] : ").strip()
                new_description = raw if raw else current["Description"]

                # Date
                current_date_display = current.get("Date") or "unknown"
                while True:
                    raw = input(f"New date (YYYY-MM-DD) [{current_date_display}] : ").strip()
                    if not raw:
                        new_date = current.get("Date", "")
                        break
                    try:
                        new_date = date.fromisoformat(raw).isoformat()
                        break
                    except ValueError:
                        print("Invalid date. Please use YYYY-MM-DD (e.g. 2026-10-17). Try again...")

                edit_expense(expenses, expense_id, new_amount, new_category, new_description, new_date)
                print("Expense updated!")

            case '5':
                if not expenses:
                    print("No expenses to delete.")
                    continue
                view_expense(expenses)
                expense_id = prompt_existing_id(expenses)
                confirm = input(f"Delete expense {expense_id}? (y/n) : ").strip().lower()
                if confirm == 'y':
                    delete_expense(expenses, expense_id)
                    print("Expense deleted!")
                else:
                    print("Delete cancelled.")

            case '6':
                print("Exiting the app. Goodbye!")
                break

            case _:
                print("Invalid Input! Please try again...")


if __name__ == "__main__":
    main()