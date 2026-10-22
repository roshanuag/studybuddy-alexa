from datetime import date, timedelta
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


def add_plan(exam_title: str, exam_date: str, titles: list[str], dates: list[str]) -> dict:
    """Save a revision plan for an exam. titles[i] is studied on dates[i].
    All dates are YYYY-MM-DD and must be before exam_date.
    The exam itself and a full-revision session the day before are added automatically."""
    if len(titles) != len(dates):
        return {"error": "titles and dates must have the same length"}
    try:
        exam_day = date.fromisoformat(exam_date)
    except ValueError:
        return {"error": "exam_date must be YYYY-MM-DD"}
    late = [t for t, d in zip(titles, dates) if d >= exam_date]
    if late:
        return {"error": f"These topics are on or after the exam: {late}. Schedule them earlier."}
    day_before = (exam_day - timedelta(days=1)).isoformat()
    added = [add_task(t, d) for t, d in zip(titles, dates)]
    added.append(add_task(f"Full revision: {exam_title}", day_before))
    added.append(add_task(exam_title, exam_date))
    return {"added": added}


def mark_done(task_id: int) -> dict:
    """Mark a task as completed by its id."""
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
