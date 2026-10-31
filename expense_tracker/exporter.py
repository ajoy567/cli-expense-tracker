import os
from .config import BASE_DIR
from rich.console import Console

console = Console()

def export_month_to_markdown(expenses, month):
    """
    Generates a Markdown report for a specific month (YYYY-MM).
    Returns the file path if successful, or None if no data found.
    """
    month_expenses = {k: v for k, v in expenses.items() if v.get("Date", "").startswith(month)}
    
    if not month_expenses:
        console.print(f"[yellow]No expenses found for {month}.[/yellow]")
        return None

    total_spent = 0.0
    by_category = {}
    
    sorted_expenses = sorted(month_expenses.items(), key=lambda item: item[1].get("Date", ""))

    for expense_id, details in sorted_expenses:
        amount = details["Amount"]
        total_spent += amount
        cat = details["Category"]
        by_category[cat] = by_category.get(cat, 0.0) + amount

    md = []
    md.append(f"# Expense Report: {month}\n")
    
    md.append("## Summary")
    md.append(f"- **Total Spent:** {total_spent:.2f}")
    md.append(f"- **Number of Expenses:** {len(month_expenses)}\n")
    
    md.append("### Spending by Category")
    md.append("| Category | Amount |")
    md.append("| :--- | :--- |")
    for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        md.append(f"| {cat} | {amt:.2f} |")
    md.append("\n")
    
    md.append("## Detailed Expenses")
    md.append("| ID | Date | Category | Amount | Description |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    for expense_id, details in sorted_expenses:
        desc = details['Description'].replace("|", "-") 
        md.append(f"| {expense_id} | {details['Date']} | {details['Category']} | {details['Amount']:.2f} | {desc} |")

    filename = f"report_{month}.md"
    filepath = os.path.join(BASE_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    return filename