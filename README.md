# CLI Expense Tracker

A Python command-line app to track expenses, saved to a CSV file so your data persists between runs.

## Features

- Add an expense with amount, category, and description
- View all saved expenses
- See a summary: total spent and total per category
- Data is stored in `expense_tracker.csv` and loaded automatically on startup

## Requirements

- Python 3.10 or newer (the app uses `match`/`case`)

## How to Run

```bash
python expense_tracker.py
```

## Usage

When the app starts, you'll see a menu:

```
1. Add Expense
2. View Expense
3. Summary
4. Exit
```

Type the number of your choice and follow the prompts.

## Example

```
1. brought groceries | 450 | weekly vegetables
2. Transport | 120 | bus pass
```

## Project Structure

```
expense_tracker.py     # main program
expense_tracker.csv    # created automatically when you add your first expense
```

## What I Learned

- Passing data between functions instead of creating new copies
- Reading and writing CSV files for persistence
- Building a menu-driven CLI with a `while` loop and `match`/`case`

## Future Improvements

- Delete and edit expenses
- Add dates to each expense
- Use Python's `csv` module for more robust file handling
- Input validation for categories