import json
import os
from datetime import date
from .config import RECURRING_FILE
from .storage import save_csv
from .logbook import log_action
from rich.console import Console

console = Console()

def load_recurring():
    if not os.path.exists(RECURRING_FILE):
        return []
    try:
        with open(RECURRING_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_recurring(rules):
    with open(RECURRING_FILE, "w", encoding="utf-8") as file:
        json.dump(rules, file, indent=4)

def process_recurring(expenses):
    """Checks if any recurring expenses are due today and adds them."""
    rules = load_recurring()
    if not rules:
        return

    today = date.today()
    current_month = today.strftime("%Y-%m")
    current_day = today.day
    added_count = 0

    for rule in rules:
        if rule.get("last_added") == current_month:
            continue

        if current_day >= rule["day"]:
            expense_id = max(expenses.keys(), default=0) + 1
            
            expense_date = f"{current_month}-{rule['day']:02d}"
            
            expenses[expense_id] = {
                "Amount": rule["amount"],
                "Category": rule["category"],
                "Description": f"{rule['description']} (Recurring)",
                "Date": expense_date
            }
            
            rule["last_added"] = current_month
            added_count += 1
            
            log_action("ADD", f"id={expense_id} amount={rule['amount']:.2f} category={rule['category']} date={expense_date} (Auto-Recurring)")

    if added_count > 0:
        save_csv(expenses)
        save_recurring(rules)
        console.print(f"\n[bold green]✨ Auto-added {added_count} recurring expense(s) for this month![/bold green]")