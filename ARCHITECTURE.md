# Project Architecture & File Guide

Here is what every file and folder in this project does.

## 1. The Entry Point

* **`main.py`**: The starting point of the app. It handles the Rich menu, routes every choices to the correct functions, and calls `load_db()` to start the app.

## 2. The `expense_tracker/` Package

This folder contains the "brain" of the app. Each file handles one specific job:

* **`config.py`**: The control center. It defines where the database, log file, and JSON files are saved.
* **`storage.py`**: The database engine. It handles creating the SQLite tables, saving to the database, and migrating old CSV files.
* **`actions.py`**: The action logic. It handles adding, editing, and deleting expenses from the database.
* **`reports.py`**: The viewer. It handles filtering, sorting, building the Rich tables, and drawing the bar charts.
* **`prompts.py`**: The validator. It holds the `input()` loops to make sure anyone don't type "abc" when it asks for a number.
* **`budget.py`**: The budget manager. It checks if your current month's spending has exceeded a category limit.
* **`recurring.py`**: The automatic bill payer. It checks the date on startup and automatically adds expenses (like Rent or Netflix) if they are due. It works by reading your custom rules (e.g., "Add 1500 for Rent on the 1st of every month") and remembering the last time it added the expense so it doesn't accidentally double-charge you.
* **`logbook.py`**: The historian. It writes every add, edit, and delete action to `activity.log`.
* **`exporter.py`**: The reporter. It turns database data into a beautiful Markdown file (`report_YYYY-MM.md`).

## 3. The `tests/` Folder

* **`test_tracker.py`**: The safety net. Contains 12 automated tests that check if the math, filtering, and database saving work correctly.

## 4. The Data Files (Gitignored)

* **`expense_tracker.db`**: The SQLite database holding all expenses.
* **`budget.json`**: Holds category budget limits.
* **`recurring.json`**: Holds recurring bill rules.
* **`activity.log`**: A text file, logging every action takes.
* **`expense_tracker.csv.bak`**: Your old CSV file, saved as a backup.

## 5. The CI/CD Folder

* **`.github/workflows/python-app.yml`**: Tells GitHub to run `pytest` automatically every time you push code.
