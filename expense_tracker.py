import csv
import os
from datetime import date, datetime

CSV_FILE = "expense_tracker.csv"
LOG_FILE = "activity.log"
FIELDNAMES = ["ID", "Amount", "Category", "Description", "Date"]


# ------------------------------- logging ----------------------------------

def log_action(action, message):
    """
    Append one line to the activity log.
    Format:  YYYY-MM-DD HH:MM:SS  ACTION  message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}  {action:<6}  {message}\n")


def view_recent_activity(n=10):
    """Show the last n entries from activity.log."""
    if not os.path.exists(LOG_FILE):
        print("No activity recorded yet.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if not lines:
        print("No activity recorded yet.")
        return

    recent = lines[-n:]
    print(f"\n--- Last {len(recent)} activity entries ---")
    for line in recent:
        print(line.rstrip())


# ------------------------------- persistence ------------------------------

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


# ------------------------------- actions ----------------------------------

def add_expense(expenses, expense_id, amount, category, description, expense_date):
    expenses[expense_id] = {
        "Amount": amount,
        "Category": category,
        "Description": description,
        "Date": expense_date,
    }
    save_csv(expenses)
    log_action(
        "ADD",
        f"id={expense_id} amount={amount:.2f} category={category} "
        f"date={expense_date or 'unknown'}"
    )


def edit_expense(expenses, expense_id, new_amount, new_category, new_description, new_date):
    old = expenses.get(expense_id, {})

    # Build a diff so the log shows only what actually changed.
    changes = []
    if round(old.get("Amount", 0.0), 2) != round(new_amount, 2):
        changes.append(f"amount {old.get('Amount', 0.0):.2f} -> {new_amount:.2f}")
    if old.get("Category") != new_category:
        changes.append(f"category {old.get('Category')} -> {new_category}")
    if old.get("Description") != new_description:
        changes.append(f"description '{old.get('Description')}' -> '{new_description}'")
    if old.get("Date", "") != new_date:
        changes.append(f"date {old.get('Date') or 'unknown'} -> {new_date or 'unknown'}")

    expenses[expense_id] = {
        "Amount": new_amount,
        "Category": new_category,
        "Description": new_description,
        "Date": new_date,
    }
    save_csv(expenses)

    if changes:
        log_action("EDIT", f"id={expense_id} " + "; ".join(changes))
    else:
        log_action("EDIT", f"id={expense_id} (no changes)")


def delete_expense(expenses, expense_id):
    if expense_id in expenses:
        old = expenses[expense_id]
        del expenses[expense_id]
        save_csv(expenses)
        log_action(
            "DELETE",
            f"id={expense_id} amount={old['Amount']:.2f} category={old['Category']} "
            f"date={old.get('Date') or 'unknown'} description='{old['Description']}'"
        )
        return True
    return False


# ------------------------------- filtering --------------------------------

def filter_expenses(expenses, start_date="", end_date="", category="", keyword=""):
    results = {}
    for expense_id, details in expenses.items():
        expense_date = details.get("Date", "")

        if start_date:
            if not expense_date or expense_date < start_date:
                continue
        if end_date:
            if not expense_date or expense_date > end_date:
                continue
        if category:
            if details["Category"].lower() != category.lower():
                continue
        if keyword:
            if keyword.lower() not in details["Description"].lower():
                continue

        results[expense_id] = details

    return results


# ------------------------------- views ------------------------------------

def view_expense(expenses, empty_message="No expenses recorded yet."):
    if not expenses:
        print(empty_message)
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


def monthly_summary(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return

    by_month = {}
    undated = []

    for expense_id, details in expenses.items():
        month = details.get("Date", "")[:7]
        if not month:
            undated.append(expense_id)
            continue

        if month not in by_month:
            by_month[month] = {"_total": 0.0, "_count": 0, "categories": {}}

        by_month[month]["_total"] += details["Amount"]
        by_month[month]["_count"] += 1
        cat = details["Category"]
        by_month[month]["categories"][cat] = (
            by_month[month]["categories"].get(cat, 0.0) + details["Amount"]
        )

    if not by_month:
        print("No dated expenses to summarize.")
        return

    print("\n--- Monthly Summary ---")
    print(f"{'Month':<10} {'Expenses':>8} {'Total':>12}")
    print("-" * 32)

    grand_total = 0.0
    grand_count = 0
    for month in sorted(by_month.keys()):
        info = by_month[month]
        print(f"{month:<10} {info['_count']:>8} {info['_total']:>12.2f}")
        grand_total += info["_total"]
        grand_count += info["_count"]

    print("-" * 32)
    print(f"{'TOTAL':<10} {grand_count:>8} {grand_total:>12.2f}")

    if undated:
        undated_total = sum(expenses[i]["Amount"] for i in undated)
        print(
            f"\n(+{len(undated)} expense(s) with unknown date, "
            f"total {undated_total:.2f} — not included above)"
        )

    month_choice = input(
        "\nCategory breakdown for a month? Enter YYYY-MM (blank to skip) : "
    ).strip()
    if not month_choice:
        return

    if month_choice not in by_month:
        print(f"No data for {month_choice}.")
        return

    info = by_month[month_choice]
    print(f"\n--- {month_choice} breakdown ---")
    for category in sorted(info["categories"].keys()):
        print(f"  {category}: {info['categories'][category]:.2f}")
    print(f"  TOTAL: {info['_total']:.2f}")


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
    while True:
        raw = input(prompt_text).strip()
        if not raw:
            return date.today().isoformat()
        try:
            return date.fromisoformat(raw).isoformat()
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD (e.g. 2026-10-17). Try again...")


def prompt_optional_date(prompt_text):
    while True:
        raw = input(prompt_text).strip()
        if not raw:
            return ""
        try:
            return date.fromisoformat(raw).isoformat()
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, or press Enter to skip. Try again...")


# ------------------------------- main loop --------------------------------

def main():
    expenses = load_csv()

    print("\nCLI EXPENSE TRACKER")

    while True:
        print("\n------------------------------ Your Options ------------------------------")
        print("1. Add Expense")
        print("2. View Expense")
        print("3. Search / Filter")
        print("4. Summary")
        print("5. Monthly Summary")
        print("6. Recent Activity")
        print("7. Edit Expense")
        print("8. Delete Expense")
        print("9. Exit")

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
                if not expenses:
                    print("No expenses to search.")
                    continue

                print("Leave any field blank to ignore that filter.")
                start_date = prompt_optional_date("From date (YYYY-MM-DD) : ")
                end_date = prompt_optional_date("To date   (YYYY-MM-DD) : ")
                category = input("Category (blank = any) : ").strip()
                keyword = input("Keyword in description (blank = any) : ").strip()

                results = filter_expenses(expenses, start_date, end_date, category, keyword)

                if not results:
                    print("No matching expenses.")
                    continue

                view_expense(results, empty_message="No matching expenses.")
                total = sum(d["Amount"] for d in results.values())
                print(f"\n{len(results)} matching expense(s), total: {total:.2f}")

            case '4':
                summary(expenses)

            case '5':
                monthly_summary(expenses)

            case '6':
                view_recent_activity(10)

            case '7':
                if not expenses:
                    print("No expenses to edit.")
                    continue
                view_expense(expenses)
                expense_id = prompt_existing_id(expenses)
                current = expenses[expense_id]
                print("Press Enter on any field to keep the current value.")

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

                raw = input(f"New category [{current['Category']}] : ").strip()
                new_category = raw if raw else current["Category"]

                raw = input(f"New description [{current['Description']}] : ").strip()
                new_description = raw if raw else current["Description"]

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

            case '8':
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

            case '9':
                print("Exiting the app. Goodbye!")
                break

            case _:
                print("Invalid Input! Please try again...")


if __name__ == "__main__":
    main()