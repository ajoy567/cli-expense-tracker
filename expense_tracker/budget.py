from datetime import date
from .storage import get_connection
from rich.console import Console

console = Console()

def load_budgets():
    """
    Load budgets from SQLite into a dictionary.
    """
    budgets = {}
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, amount FROM budgets")
        for row in cursor.fetchall():
            budgets[row["category"]] = row["amount"]
    return budgets

def save_budgets(budgets):
    """
    Save the dictionary of budgets back to SQLite.
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM budgets")
        for cat, amt in budgets.items():
            conn.execute("INSERT INTO budgets (category, amount) VALUES (?, ?)", (cat, amt))

def check_budget(category, expenses):
    """
    Check if the current month's spending exceeds the budget for this category.
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