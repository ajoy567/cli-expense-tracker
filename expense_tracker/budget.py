import json
import os
from datetime import date
from .config import BUDGET_FILE
from rich.console import Console
console = Console()

def load_budgets():
    """Load budgets from JSON file."""
    if not os.path.exists(BUDGET_FILE):
        return {}
    try:
        with open(BUDGET_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_budgets(budgets):
    """Save budgets to JSON file."""
    with open(BUDGET_FILE, "w", encoding="utf-8") as file:
        json.dump(budgets, file, indent=4)

def check_budget(category, expenses):
    """
    Check if the current month's spending exceeds the budget for this category.
    Returns a warning string, or None if everything is fine.
    """
    budgets = load_budgets()
    
    budget_limit = next((v for k, v in budgets.items() if k.lower() == category.lower()), None)

    if budget_limit is None:
        return None

    current_month = date.today().strftime("%Y-%m")
    
    spent = sum(
        details["Amount"] for details in expenses.values()
        if details["Category"].lower() == category.lower() 
        and details.get("Date", "").startswith(current_month)
    )

    if spent > budget_limit:
        return f"[bold red] WARNING: You have exceeded your {category} budget! (Spent: {spent:.2f}, Limit: {budget_limit:.2f})[/bold red]"
    return None