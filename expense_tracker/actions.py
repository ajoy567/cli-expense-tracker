from .storage import save_csv
from .logbook import log_action
from .budget import check_budget


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
        f"date={expense_date or 'unknown'}",
    )
    
    warning = check_budget(category, expenses)
    if warning:
        print(f"\n{warning}\n")


def edit_expense(expenses, expense_id, new_amount, new_category, new_description, new_date):
    old = expenses.get(expense_id, {})

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

    log_action("EDIT", f"id={expense_id} " + ("; ".join(changes) if changes else "(no changes)"))


def delete_expense(expenses, expense_id):
    if expense_id in expenses:
        old = expenses[expense_id]
        del expenses[expense_id]
        save_csv(expenses)
        log_action(
            "DELETE",
            f"id={expense_id} amount={old['Amount']:.2f} category={old['Category']} "
            f"date={old.get('Date') or 'unknown'} description='{old['Description']}'",
        )
        return True
    return False