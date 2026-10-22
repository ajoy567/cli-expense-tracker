import os
from datetime import datetime

from .config import LOG_FILE


def log_action(action, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp}  {action:<6}  {message}\n")


def view_recent_activity(n=10):
    if not os.path.exists(LOG_FILE):
        print("No activity recorded yet.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if not lines:
        print("No activity recorded yet.")
        return

    recent = lines[-n:]
    print(f"\n--- Last {len(recent)} activity entries ---")
    for line in recent:
        print(line.rstrip())