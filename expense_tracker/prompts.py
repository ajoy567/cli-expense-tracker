from datetime import date


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