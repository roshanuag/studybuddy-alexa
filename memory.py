import json
import os

FILE = "tasks.json"

def load_tasks() -> list:
    """Return all study tasks as a list."""
    if not os.path.exists(FILE):
        return []                      # no file yet = no tasks yet
    with open(FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks: list) -> None:
    """Save the full task list to disk."""
    with open(FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(title: str, date: str) -> dict:
    """Add a study task. date must be YYYY-MM-DD."""
    tasks = load_tasks()
    new_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": new_id, "title": title, "date": date, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    return task

def mark_done(task_id: int) -> dict:
    """Mark a task as completed by its id."""
    print(f"[tool] mark_done called with task_id={task_id}")
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            return t
    return {"error": "task not found"}

def reschedule_task(task_id: int, new_date: str) -> dict:
    """Move a task to a new date by its id. new_date must be YYYY-MM-DD."""
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["date"] = new_date
            save_tasks(tasks)
            return t
    return {"error": "task not found"}

def get_missed(today: str) -> list:
    """Return unfinished tasks dated before today (YYYY-MM-DD)."""
    return [t for t in load_tasks() if t["date"] < today and not t["done"]]

if __name__ == "__main__":
    print(add_task("Revise DSA arrays", "2026-10-20"))
    print(get_missed("2026-10-21"))