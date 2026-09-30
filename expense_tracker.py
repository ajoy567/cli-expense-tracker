def add_expense(expenses, expense_id, amount, category, description):
    
    """
    Add a new expense to the expenses dictionary using a unique expense ID.

    Stores the expense amount, category, and description, then updates the CSV
    file so the data persists after the program is closed.
    """
    
    expenses[expense_id] = {
        "Amount": amount,
        "Category": category,
        "Description": description
    }
    save_csv(expenses)


def view_expense(expenses):
    
    """
    Display all expenses currently stored in the expenses dictionary.

    Shows each expense ID along with its associated details in a user-friendly format.
    """
    
    if not expenses:
        print("No expenses recorded yet.")
        return

    for expense_id, details in expenses.items():
        print(f"{expense_id}. {details['Category']} | {details['Amount']} | {details['Description']}")


def save_csv(expenses):
    
    """
    Save all expenses from the expenses dictionary to a CSV file.

    Converts the in-memory expense data into a file format so that expenses
    can be restored when the program is run again.
    """
    
    with open("expense_tracker.csv", "w") as file:
        for expense_id, details in expenses.items():
            file.write(f"{expense_id},{details['Amount']},{details['Category']},{details['Description']}\n")


def load_csv():
    
    """
    Load expense data from the CSV file,
    reconstruct the expenses dictionary,
    and return it.

    Returns:
        dict: {expense_id: {"Amount": ..., "Category": ..., "Description": ...}}
    """
    
    try:
        with open("expense_tracker.csv", 'r') as file:
            data = file.read()
            inner_dict_keys = ["Amount", "Category", "Description"]

            result = {}

            for line in data.strip().split('\n'):
                if not line:
                    continue

                # maxsplit=3 keeps any commas inside the description intact
                parts = [p.strip() for p in line.split(',', 3)]

                expense_id = int(parts[0])
                values = [int(parts[1])] + parts[2:]

                result[expense_id] = dict(zip(inner_dict_keys, values))

            return result
    except FileNotFoundError:
        return {}


def summary(expenses):
    
    """
    Show the total spent and the total per category.
    """
    
    if not expenses:
        print("No expenses recorded yet.")
        return

    total = sum(d["Amount"] for d in expenses.values())
    print(f"Total spent: {total}")

    by_category = {}
    for d in expenses.values():
        by_category[d["Category"]] = by_category.get(d["Category"], 0) + d["Amount"]

    for category, amount in by_category.items():
        print(f"  {category}: {amount}")


def main():

    expenses = load_csv()

    print("\n CLI EXPENSE TRACKER")

    while True:
        print("\n------------------------------ Your Options ------------------------------")
        print("1. Add Expense")
        print("2. View Expense")
        print("3. Summary")
        print("4. Exit")

        choice = input("Enter your choice : ")

        match choice:
            case '1':
                try:
                    amount = int(input("Enter the amount : "))
                except ValueError:
                    print("Amount must be a whole number. Please try again...")
                    continue
                category = input("Enter the category of the expense : ")
                description = input("Enter description for the expense : ")
                expense_id = max(expenses.keys(), default=0) + 1
                add_expense(expenses, expense_id, amount, category, description)
                print("Expense added!")
            case '2':
                view_expense(expenses)
            case '3':
                summary(expenses)
            case '4':
                print("Exiting the app. Goodbye!")
                break
            case _:
                print("Invalid Input! Please try again...")


if __name__ == "__main__":
    main()