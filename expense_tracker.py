import csv
import os

CSV_FILE = "expense_tracker.csv"
FIELDNAMES = ["ID", "Amount", "Category", "Description"]


# ------------------------------- persistence ------------------------------

def save_csv(expenses):
    """
    Save all expenses to the CSV file using the csv module.
    The csv module handles quoting, so commas inside categories or
    descriptions no longer corrupt the file.
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
            ])


def load_csv():
    """
    Load expenses from the CSV file. Handles both the new format (with a
    header) and the old format (no header), and silently skips corrupt rows.

    Returns:
        dict: {expense_id: {"Amount": float, "Category": str, "Description": str}}
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
        description = ",".join(row[3:]).strip()

        result[expense_id] = {
            "Amount": round(amount, 2),
            "Category": category,
            "Description": description,
        }

    return result


# ------------------------------- actions ----------------------------------

def add_expense(expenses, expense_id, amount, category, description):
    """
    Add a new expense to the expenses dictionary and persist it to disk.
    """
    expenses[expense_id] = {
        "Amount": amount,
        "Category": category,
        "Description": description,
    }
    save_csv(expenses)


def edit_expense(expenses, expense_id, new_amount, new_category, new_description):
    """
    Replace the details of an existing expense and save.
    """
    expenses[expense_id] = {
        "Amount": new_amount,
        "Category": new_category,
        "Description": new_description,
    }
    save_csv(expenses)


def delete_expense(expenses, expense_id):
    """
    Remove an expense by ID and save. Returns True if it was removed.
    """
    if expense_id in expenses:
        del expenses[expense_id]
        save_csv(expenses)
        return True
    return False


# ------------------------------- views ------------------------------------

def view_expense(expenses):
    """
    Display all expenses currently stored in the expenses dictionary.
    """
    if not expenses:
        print("No expenses recorded yet.")
        return

    for expense_id, details in expenses.items():
        print(
            f"{expense_id}. {details['Category']} | "
            f"{details['Amount']:.2f} | {details['Description']}"
        )


def summary(expenses):
    """
    Show the total spent and the total per category.
    """
    if not expenses:
        print("No expenses recorded yet.")
        return

    total = sum(d["Amount"] for d in expenses.values())
    print(f"Total spent: {total:.2f}")

    by_category = {}
    for d in expenses.values():
        by_category[d["Category"]] = by_category.get(d["Category"], 0.0) + d["Amount"]

    for category, amount in sorted(by_category.items()):
        print(f"  {category}: {amount:.2f}")


# ------------------------------- input helpers ----------------------------

def prompt_amount(prompt_text="Enter the amount : "):
    """Ask for a positive decimal amount until valid."""
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
    """Ask for a non-empty string until valid."""
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again...")


def prompt_existing_id(expenses, prompt_text="Enter the expense ID : "):
    """Ask for an ID that exists in the expenses dict."""
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
                expense_id = max(expenses.keys(), default=0) + 1
                add_expense(expenses, expense_id, amount, category, description)
                print(f"Expense added with ID {expense_id}!")

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

                # Amount (optional)
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

                # Category (optional)
                raw = input(f"New category [{current['Category']}] : ").strip()
                new_category = raw if raw else current["Category"]

                # Description (optional)
                raw = input(f"New description [{current['Description']}] : ").strip()
                new_description = raw if raw else current["Description"]

                edit_expense(expenses, expense_id, new_amount, new_category, new_description)
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