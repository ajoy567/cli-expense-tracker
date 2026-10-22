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