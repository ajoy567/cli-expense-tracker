from datetime import date
from .storage import get_connection, save_db
from .logbook import log_action
from rich.console import Console

console = Console()

def load_recurring():
    """
    Load recurring rules from SQLite.
    """
    rules = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, category, description, day, last_added FROM recurring_rules")
        for row in cursor.fetchall():
            rules.append({
                "id": row["id"],
                "amount": row["amount"],
                "category": row["category"],
                "description": row["description"],
                "day": row["day"],
                "last_added": row["last_added"]
            })
    return rules

def save_recurring(rules):
    """
    Save rules to SQLite. (Kept for backwards compatibility, though not strictly needed now).
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM recurring_rules")
        for rule in rules:
            conn.execute(
                "INSERT INTO recurring_rules (amount, category, description, day, last_added) VALUES (?, ?, ?, ?, ?)",
                (rule["amount"], rule["category"], rule["description"], rule["day"], rule.get("last_added", ""))
            )

def process_recurring(expenses):
    """
    Checks if any recurring expenses are due today and adds them.
    """
    rules = load_recurring()
    if not rules:
        return

    today = date.today()
    current_month = today.strftime("%Y-%m")
    current_day = today.day
    added_count = 0

    with get_connection() as conn:
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
                
                conn.execute(
                    "UPDATE recurring_rules SET last_added = ? WHERE id = ?",
                    (current_month, rule["id"])
                )
                added_count += 1
                
                log_action("ADD", f"id={expense_id} amount={rule['amount']:.2f} category={rule['category']} date={expense_date} (Auto-Recurring)")

    if added_count > 0:
        save_db(expenses)
        console.print(f"\n[bold green] Auto-added {added_count} recurring expense(s) for this month![/bold green]")
        
def delete_recurring(rule_id):
    """
    Deletes a recurring rule by its database ID.
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM recurring_rules WHERE id = ?", (rule_id,))