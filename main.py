from datetime import date
from rich.console import Console
from rich.panel import Panel

console = Console()

from expense_tracker.storage import load_csv
from expense_tracker.budget import load_budgets, save_budgets, check_budget
from expense_tracker.logbook import view_recent_activity
from expense_tracker.actions import add_expense, edit_expense, delete_expense
from expense_tracker.reports import (
    view_expense, summary, monthly_summary, filter_expenses,
)
from expense_tracker.prompts import (
    prompt_amount, prompt_non_empty, prompt_existing_id,
    prompt_date, prompt_optional_date,
)


def show_menu():
    menu_text = (
        "[1] Add Expense\n"
        "[2] View Expense\n"
        "[3] Search / Filter\n"
        "[4] Summary\n"
        "[5] Monthly Summary\n"
        "[6] Recent Activity\n"
        "[7] Set Budget\n"
        "[8] Edit Expense\n"
        "[9] Delete Expense\n"
        "[10] Exit"
    )
    console.print(Panel(menu_text, title="Your Options", border_style="blue", padding=(1, 2)))


def handle_add(expenses):
    amount = prompt_amount()
    category = prompt_non_empty("Enter the category of the expense : ")
    description = prompt_non_empty("Enter description for the expense : ")
    expense_date = prompt_date()
    expense_id = max(expenses.keys(), default=0) + 1
    add_expense(expenses, expense_id, amount, category, description, expense_date)
    print(f"Expense added with ID {expense_id} on {expense_date}!")


def handle_search(expenses):
    if not expenses:
        print("No expenses to search.")
        return

    print("Leave any field blank to ignore that filter.")
    start_date = prompt_optional_date("From date (YYYY-MM-DD) : ")
    end_date = prompt_optional_date("To date   (YYYY-MM-DD) : ")
    category = input("Category (blank = any) : ").strip()
    keyword = input("Keyword in description (blank = any) : ").strip()

    results = filter_expenses(expenses, start_date, end_date, category, keyword)
    if not results:
        print("No matching expenses.")
        return

    view_expense(results, empty_message="No matching expenses.")
    total = sum(d["Amount"] for d in results.values())
    print(f"\n{len(results)} matching expense(s), total: {total:.2f}")


def handle_edit(expenses):
    if not expenses:
        print("No expenses to edit.")
        return

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


def handle_delete(expenses):
    if not expenses:
        print("No expenses to delete.")
        return

    view_expense(expenses)
    expense_id = prompt_existing_id(expenses)
    confirm = input(f"Delete expense {expense_id}? (y/n) : ").strip().lower()
    if confirm == 'y':
        delete_expense(expenses, expense_id)
        print("Expense deleted!")
    else:
        print("Delete cancelled.")
        
def handle_set_budget():
    budgets = load_budgets()
    print("\n--- Set Monthly Budget ---")
    
    if budgets:
        for cat, amt in budgets.items():
            print(f"  {cat}: {amt:.2f}")
    else:
        print("  (No budgets set yet)")
        
    category = prompt_non_empty("Enter category to set budget for : ")
    amount = prompt_amount(f"Enter monthly budget for {category} : ")
    
    budgets[category] = amount
    save_budgets(budgets)
    print(f"Budget for {category} set to {amount:.2f}!")


def main():
    expenses = load_csv()
    print("\nCLI EXPENSE TRACKER")

    while True:
        show_menu()
        choice = input("Enter your choice : ").strip()

        match choice:
            case '1':
                handle_add(expenses)
            case '2':
                view_expense(expenses)
            case '3':
                handle_search(expenses)
            case '4':
                summary(expenses)
            case '5':
                monthly_summary(expenses)
            case '6':
                view_recent_activity(10)
            case '7':
                handle_set_budget()
            case '8':
                handle_edit(expenses)
            case '9':
                handle_delete(expenses)
            case '10':
                print("Exiting the app. Goodbye!")
                break
            case _:
                print("Invalid Input! Please try again...")


if __name__ == "__main__":
    main()