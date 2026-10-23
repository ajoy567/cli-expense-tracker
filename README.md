# CLI Expense Tracker

![Python application](https://github.com/ajoy567/cli-expense-tracker/actions/workflows/python-app.yml/badge.svg)

A Python command-line app to track expenses, saved locally to CSV so your data persists between runs.

## Features

- Add expenses with amount, category, description, and date
- View all saved expenses
- Search / Filter by date range, category, or keyword
- See a summary: total spent, total per category, and date range
- Monthly summary with per-month totals and category breakdown
- Edit and Delete existing expenses
- Activity log (`activity.log`) keeps track of adds, edits, and deletes

## Requirements

- Python 3.10 or newer (the app uses `match`/`case`)

## How to Run

From the project root (the folder containing `main.py`):

```bash
python main.py
