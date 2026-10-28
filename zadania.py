from functools import wraps
from collections.abc import Iterator
from pathlib import Path
import json
import csv

class TaskNotFoundError(Exception):
    pass

def log_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def load_tasks(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Brak pliku {path}. Rozpoczynam z pustą listą zadań.")
        return []
    try:
        with open(path, "r", encoding="utf-8-sig") as file:
            tasks = json.load(file)
    except json.JSONDecodeError:
        backup_path = path.with_suffix(".json.bak")
        path.replace(backup_path)
        print(f"Niepoprawny JSON. Kopia pliku została zapisana jako {backup_path}.")
        print("Rozpoczynam z pustą listą zadań.")
        return []
    for task in tasks:
        if isinstance(task["tags"], str):
            task["tags"] = {tag.strip() for tag in task["tags"].split(",") if tag.strip()}
        else:
            task["tags"] = set(task["tags"])
    return tasks

def save_tasks(tasks: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tasks_to_save = [
        {**task, "tags": sorted(task["tags"])}
        for task in tasks
    ]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(tasks_to_save, file, ensure_ascii=False, indent=4)

def export_tasks_csv(tasks: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["title", "tags", "minutes", "priority", "done", "recurrence_interval_days"]
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for task in tasks:
            row = {**task, "tags": ", ".join(sorted(task["tags"]))}
            writer.writerow(row)
    print(f"Zadania wyeksportowano do pliku: {path}")

@log_action
def add_task(
    tasks: list[dict],
    title: str,
    minutes: int,
    priority: int = 1,
    tags: set[str] | None = None,
    is_done: bool = False
) -> dict:
    """Adds task to tasks list
    Args:
        tasks: list containing all tasks
        title: name of the task
        minutes: time needed to complete the task
        priority: task priority from 1 to 3
        tags: words describing the task
        is_done: whether the task is completed
    Returns:
        Dictionary with added task.
    """
    if tags is None: 
        tags = set()

    if not title.strip():
        raise ValueError("Tytuł nie może być pusty!")
    
    if priority not in range(1, 4):
        raise ValueError("Priorytet musi być z zakresu 1-3!")
    
    if minutes <= 0:
        raise ValueError("Planowany czas musi być większy niż 0")
    
    task = {
        "title": title,
        "tags": tags,
        "minutes": minutes,
        "priority": priority,
        "done": is_done,
    }
    tasks.append(task)
    return task

def get_tasks(tasks: list[dict]) -> None:
    """Displays formatted list of all tasks in console

    Args:
        tasks: list containing all tasks
    """
    if not tasks:
        print("Brak zadań!")
        return
    for index, task in enumerate(tasks, start=1):
        checked = "x" if task["done"] else " "
        print(f"{index}. [{checked}] {task["title"]} ({task["minutes"]} min, priorytet {task["priority"]})")

@log_action
def complete_task(tasks: list[dict], task_number: int) -> bool:
    """Oznacza wybrane zadanie jako wykonane na podstawie jego numeru na liście.

    Args:
        tasks: list containing all tasks
        task_number: task number from list (counted from 1)

    Returns:
        True: if task is succesfully mark as done
        False: if list is empty oraz task_number is invalid
    
    Raises:
        TaskNotFoundError: if the task number is outside the valid range.
    """
    if not tasks:
        return False
    
    if task_number < 1 or task_number > len(tasks):
        raise TaskNotFoundError("Nie ma takiego zadania!")
    
    tasks[task_number - 1]["done"] = True
    return True
def get_raport(tasks: list[dict]) -> tuple[list[dict], Iterator[int], set[str]]:
    incomplete_tasks = [task for task in tasks if not task.is_done]
    sorted_tasks = sorted(incomplete_tasks, key=lambda task: (-task.priority, task.minutes))
    total_minutes = (task.minutes for task in incomplete_tasks)
    tags = {tag for task in incomplete_tasks for tag in task.tags}
    return sorted_tasks, total_minutes, tags

def get_todays_plan(tasks: list[dict], minutes_limit: int = 240):
    sorted_tasks, _, _ = get_raport(tasks)
    total_minutes = 0

    for task in sorted_tasks:
        if total_minutes + task.minutes > minutes_limit:
            break

        total_minutes += task.minutes
        yield task

if __name__ == "__main__":
    test_tasks = []
    add_task(test_tasks, "Wypić kawę", 100, 2, {"praca", "dom"})
    export_tasks_csv(test_tasks, Path("database") / "test.csv")