from rich.console import Console
from rich.table import Table

console = Console()

def build_bar(amount, max_amount, width=20):
    """Creates an ASCII bar chart string."""
    if max_amount <= 0:
        return ""
    blocks = int((amount / max_amount) * width)
    if blocks == 0 and amount > 0:
        blocks = 1
    return "[bright_green]" + ("█" * blocks) + "[/bright_green]"

def view_expense(expenses, empty_message="No expenses recorded yet.", sort_by="none"):
    if not expenses:
        console.print(f"[yellow]{empty_message}[/yellow]")
        return

    sorted_items = list(expenses.items())
    if sort_by == "date":
        sorted_items.sort(key=lambda item: item[1].get("Date", ""), reverse=True)
    elif sort_by == "amount":
        sorted_items.sort(key=lambda item: item[1]["Amount"], reverse=True)
    elif sort_by == "category":
        sorted_items.sort(key=lambda item: item[1]["Category"].lower())

    table = Table(title="Your Expenses", title_style="bold cyan")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Date", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Amount", justify="right", style="bright_blue")
    table.add_column("Description")

    for expense_id, details in sorted_items:
        d = details.get("Date") or "unknown"
        table.add_row(
            str(expense_id),
            d,
            details['Category'],
            f"{details['Amount']:.2f}",
            details['Description']
        )
    console.print(table)


def filter_expenses(expenses, start_date="", end_date="", category="", keyword=""):
    results = {}
    for expense_id, details in expenses.items():
        expense_date = details.get("Date", "")

        if start_date and (not expense_date or expense_date < start_date):
            continue
        if end_date and (not expense_date or expense_date > end_date):
            continue
        if category and details["Category"].lower() != category.lower():
            continue
        if keyword and keyword.lower() not in details["Description"].lower():
            continue

        results[expense_id] = details

    return results


def summary(expenses):
    if not expenses:
        console.print("[yellow]No expenses recorded yet.[/yellow]")
        return

    total = sum(d["Amount"] for d in expenses.values())
    console.print(f"\n[bold]Total spent:[/bold] [bright_blue]{total:.2f}[/bright_blue]")

    dates = [d.get("Date") for d in expenses.values() if d.get("Date")]
    if dates:
        console.print(f"[bold]Date range:[/bold] {min(dates)} to {max(dates)}")

    by_category = {}
    for d in expenses.values():
        by_category[d["Category"]] = by_category.get(d["Category"], 0.0) + d["Amount"]

    max_amount = max(by_category.values()) if by_category else 0

    table = Table(title="Spending by Category", title_style="bold green")
    table.add_column("Category", style="green")
    table.add_column("Amount", justify="right", style="bright_blue")
    table.add_column("Visual", style="bright_green")

    for category, amount in sorted(by_category.items()):
        bar = build_bar(amount, max_amount)
        table.add_row(category, f"{amount:.2f}", bar)
        
    console.print(table)


def monthly_summary(expenses):
    if not expenses:
        console.print("[yellow]No expenses recorded yet.[/yellow]")
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
        console.print("[yellow]No dated expenses to summarize.[/yellow]")
        return

    table = Table(title="Monthly Summary", title_style="bold cyan")
    table.add_column("Month", style="magenta")
    table.add_column("Expenses", justify="right", style="green")
    table.add_column("Total", justify="right", style="bright_blue")

    grand_total = 0.0
    grand_count = 0
    for month in sorted(by_month.keys()):
        info = by_month[month]
        table.add_row(month, str(info['_count']), f"{info['_total']:.2f}")
        grand_total += info["_total"]
        grand_count += info["_count"]

    table.add_section()
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{grand_count}[/bold]", f"[bold]{grand_total:.2f}[/bold]")
    console.print(table)

    if undated:
        undated_total = sum(expenses[i]["Amount"] for i in undated)
        console.print(
            f"\n[yellow](+{len(undated)} expense(s) with unknown date, "
            f"total {undated_total:.2f} — not included above)[/yellow]"
        )

    month_choice = input(
        "\nCategory breakdown for a month? Enter YYYY-MM (blank to skip) : "
    ).strip()
    if not month_choice:
        return

    if month_choice not in by_month:
        console.print(f"[red]No data for {month_choice}.[/red]")
        return

    info = by_month[month_choice]
    
    cat_table = Table(title=f"{month_choice} Breakdown", title_style="bold green")
    cat_table.add_column("Category", style="green")
    cat_table.add_column("Amount", justify="right", style="bright_blue")
    cat_table.add_column("Visual", style="bright_green")

    max_cat_amount = max(info["categories"].values()) if info["categories"] else 0

    for category in sorted(info["categories"].keys()):
        amt = info["categories"][category]
        bar = build_bar(amt, max_cat_amount) # NEW
        cat_table.add_row(category, f"{amt:.2f}", bar)

    cat_table.add_section()
    cat_table.add_row("[bold]TOTAL[/bold]", f"[bold]{info['_total']:.2f}[/bold]", "")
    console.print(cat_table)