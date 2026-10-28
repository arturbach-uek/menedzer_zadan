from pathlib import Path
from models import Task, RecurringTask, TaskManager
from errors import TaskManagerError
from zadania import get_raport, get_todays_plan, load_tasks, save_tasks, export_tasks_csv

tasks_path = Path.cwd() / "database" / "tasks.json"
csv_path = Path.cwd() / "database" / "tasks.csv"

def task_from_dict(data: dict) -> Task:
    task_data = {**data, "is_done": data.get("is_done", data.get("done", False))}
    if "recurrence_interval_days" in data:
        return RecurringTask(
            title=task_data["title"],
            minutes=task_data["minutes"],
            priority=task_data.get("priority", 1),
            tags=set(task_data.get("tags", [])),
            is_done=task_data["is_done"],
            recurrence_interval_days=data["recurrence_interval_days"],
        )
    return Task.from_dict(task_data)

def task_to_dict(task: Task) -> dict:
    data = task.to_dict()
    data["done"] = data.pop("is_done")
    if isinstance(task, RecurringTask):
        data["recurrence_interval_days"] = task.recurrence_interval_days
    return data

def save_task_manager(manager: TaskManager) -> None:
    save_tasks([task_to_dict(task) for task in manager.tasks], tasks_path)

def add_task_menu(manager: TaskManager) -> None:
    title = input("Nazwa zadania: ").strip()
    title = title[:1].upper() + title[1:]

    tags_input = input("Tagi (po przecinku): ")
    tags = {tag.strip() for tag in tags_input.split(",") if tag.strip()}

    try:
        minutes = int(input("Planowany czas (min): "))
        priority_input = input("Priorytet (1-3, domyślnie 1): ").strip()
        priority = int(priority_input) if priority_input else 1
    except ValueError:
        print("Błąd: czas i priorytet muszą być liczbami całkowitymi.")
        return

    done_input = input("Czy oznaczyć jako zrobione (tak/nie, domyślnie nie): ").strip().lower()
    is_done = done_input == "tak"
    recurring_input = input("Czy zadanie jest cykliczne (tak/nie): ").strip().lower()

    try:
        if recurring_input == "tak":
            interval_input = input("Co ile dni powtarzać zadanie (domyślnie 7): ").strip()
            interval = int(interval_input) if interval_input else 7
            task = RecurringTask(title, minutes, priority, tags, is_done, interval)
        else:
            task = Task(title, minutes, priority, tags, is_done)

        manager.add_task(task)
        save_task_manager(manager)
        print(f"Pomyślnie dodano zadanie: {title}")

    except (TaskManagerError, ValueError) as error:
        print(f"Błąd: {error}")

def show_tasks(manager: TaskManager) -> None:
    if not manager.tasks:
        print("Brak zadań!")
        return

    for number, task in enumerate(manager.tasks, start=1):
        print(f"{number}. {task}")
        if isinstance(task, RecurringTask):
            print(f"Powtarzanie: co {task.recurrence_interval_days} dni")

def complete_task_menu(manager: TaskManager) -> None:
    if not manager.tasks:
        print("Nie można oznaczyć zadania: lista jest pusta.")
        return

    try:
        task_number = int(input(f"Numer zadania (1-{len(manager)}): "))
    except ValueError:
        print("Błąd: numer zadania musi być liczbą całkowitą.")
        return

    if task_number < 1 or task_number > len(manager):
        print("Nie ma takiego zadania!")
        return

    task = manager.tasks[task_number - 1]
    task.mark_as_done()
    save_task_manager(manager)
    print(f"Pomyślnie oznaczono zadanie {task_number} jako zrobione!")

def delete_task_menu(manager: TaskManager) -> None:
    title = input("Nazwa zadania do usunięcia: ").strip()

    try:
        manager.delete_task(title)
        save_task_manager(manager)
        print(f"Usunięto zadanie: {title}")
    except TaskManagerError as error:
        print(f"Błąd: {error}")
    except ValueError as error:
        print(f"Błąd: {error}")

def show_report(manager: TaskManager) -> None:
    sorted_tasks, total_minutes, tags = get_raport(manager.tasks)
    total_minutes = sum(total_minutes)

    print(f"\n{'=' * 45}")
    print(f"{'RAPORT ZADAŃ':^45}")
    print(f"{'=' * 45}")

    if not sorted_tasks:
        print("Brak niezrobionych zadań!")
    else:
        for number, task in enumerate(sorted_tasks, start=1):
            print(f"\n{number}. {task.title}")
            print(f"{'Priorytet:':<15} {task.priority}/3")
            print(f"{'Czas:':<15} {task.minutes} min")

    print(f"\n{'-' * 45}")
    print(f"{'Łączny czas:':<20} {total_minutes} min")
    print(f"{'Liczba zadań:':<20} {len(sorted_tasks)}")
    print(f"{'Tagi:':<20} {', '.join(sorted(tags)) if tags else 'brak'}")

    print(f"\n{'=' * 45}")
    print(f"{'PLAN NA DZIŚ':^45}")
    print(f"{'=' * 45}")

    todays_plan = list(get_todays_plan(manager.tasks))
    plan_minutes = sum(task.minutes for task in todays_plan)
    
    if not todays_plan:
        print("Brak zadań do zaplanowania.")
    else:
        for number, task in enumerate(todays_plan, start=1):
            print(f"{number}. {task.title} ({task.minutes} min)")
        print(f"\nŁączny czas planu: {plan_minutes} min")

    print(f"{'=' * 45}\n")

def show_summary(manager: TaskManager) -> None:
    tasks = manager.tasks
    total_tasks = len(manager)
    completed_tasks = sum(task.is_done for task in tasks)
    remaining_tasks = total_tasks - completed_tasks
    total_minutes = sum(task.minutes for task in tasks)
    completed_minutes = sum(task.minutes for task in tasks if task.is_done)

    print("\n--- PODSUMOWANIE ---")
    print(f"Liczba wszystkich zadań: {total_tasks}")
    print(f"Zrobione: {completed_tasks}")
    print(f"Pozostało: {remaining_tasks}")
    print(f"Łączny planowany czas: {total_minutes} min")
    print(f"Czas zrobionych zadań: {completed_minutes} min")
    print("Do widzenia!")

def main():
    saved_tasks = load_tasks(tasks_path)
    manager = TaskManager()
    manager.tasks = [task_from_dict(data) for data in saved_tasks]
    actions = {
        "1": lambda: add_task_menu(manager),
        "2": lambda: show_tasks(manager),
        "3": lambda: complete_task_menu(manager),
        "4": lambda: show_report(manager),
        "5": lambda: export_tasks_csv(
            [task_to_dict(task) for task in manager.tasks],
            csv_path,
        ),
        "6": lambda: delete_task_menu(manager),
        "7": lambda: show_summary(manager),
    }

    while True:
        print("\n1. Dodaj zadanie")
        print("2. Pokaż zadania")
        print("3. Oznacz jako zrobione")
        print("4. Raport")
        print("5. Eksport do CSV")
        print("6. Usuń zadanie")
        print("7. Koniec")

        action = input("Podaj numer akcji (1-7): ").strip()

        if action == "7":
            save_task_manager(manager)
            actions[action]()
            break

        selected_action = actions.get(action)
        if selected_action is None:
            print("Nieprawidłowa akcja!")
            continue
        selected_action()

if __name__ == "__main__":
    main()