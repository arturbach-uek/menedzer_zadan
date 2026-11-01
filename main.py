from pathlib import Path
from models import Task, RecurringTask, TaskManager
from errors import TaskManagerError, TaskDontExistError, InvalidTaskError
from zadania import get_raport, get_todays_plan, export_tasks_csv
import database
import sqlite3

BASE_DIR = Path(__file__).resolve().parent

json_path = BASE_DIR / "database" / "tasks.json"
csv_path = BASE_DIR / "database" / "tasks.csv"
db_path = BASE_DIR / "database" / "tasks.db"

def get_db_connection():
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def add_task_menu(manager: TaskManager) -> None:
    title = input("Nazwa zadania: ").strip()
    title = title[:1].upper() + title[1:]

    tags_input = input("Tagi (po przecinku): ")
    tags = {tag.strip() for tag in tags_input.split(",") if tag.strip()}

    try:
        minutes = int(input("Planowany czas (min): ").strip())
        priority_input = input("Priorytet (1-3, domyślnie 1): ").strip()
        priority = int(priority_input) if priority_input else 1
        recurring_input = input("Czy zadanie jest cykliczne (tak/nie): ").strip().lower()
        if recurring_input == "tak":
            interval_input = input("Co ile dni powtarzać zadanie (domyślnie 7): ").strip()
            interval = int(interval_input) if interval_input else 7
            task = RecurringTask(
                title=title, 
                minutes=minutes, 
                priority=priority, 
                tags=tags, 
                recurrence_interval_days=interval
            )
        else:
            task = Task(title=title, minutes=minutes, priority=priority, tags=tags)
    except InvalidTaskError as error:
        print(f"Błąd: {error}")
        return

    try:
        conn = get_db_connection()
        task_id = database.add_task(conn, task)

        manager.add_task(task)

        task.id = task_id
        print(f"Pomyślnie dodano zadanie: {title} (id: {task_id})")

    except (TaskManagerError, ValueError) as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()

def show_tasks() -> None:
    try:
        order_by = input("Sortuj po (priority/minutes/title): ") or "priority"
        conn = get_db_connection()
        tasks = database.get_all_tasks(conn, order_by)
        print(*tasks, sep="\n")
    except ValueError as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()

def complete_task_menu(manager: TaskManager) -> None:
    try:
        task_id = int(input("ID zadania do oznaczenia jako zrobione: "))

        conn = get_db_connection()
        database.mark_as_done(conn, task_id)

        task = manager.get_task_by_id(task_id)
        task.mark_as_done()

        print(f"Pomyślnie oznaczono zadanie '{task.title}' jako zrobione!")
    except (TaskDontExistError, ValueError) as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()

def delete_task_menu(manager: TaskManager) -> None:
    try:
        task_id = int(input("ID zadania do usunięcia: "))

        conn = get_db_connection()
        database.delete_task(conn, task_id)

        task = manager.get_task_by_id(task_id)
        manager.delete_task(task.title)

        print(f"Pomyślnie usunięto zadanie '{task.title}' z listy!")
    except ValueError as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()

def search_tasks_menu() -> None:
    try:
        phrase = input("Szukaj zadania: ").strip()
        conn = get_db_connection()
        tasks = database.search_tasks(conn, phrase)
        print(*tasks, sep="\n")
    except ValueError as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()
def show_report() -> None:
    try:
        conn = get_db_connection()
        tasks = database.get_all_tasks(conn)
    except ValueError as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()

    sorted_tasks, total_minutes, tags = get_raport(tasks)
    total_minutes = sum(total_minutes)
    print(f"\n{'=' * 45}")
    print(f"{'RAPORT ZADAŃ':^45}")
    print(f"{'=' * 45}")

    if not sorted_tasks:
        print("Brak niezrobionych zadań!")
    else:
        for task in sorted_tasks:
            print(f"\n{task.id}. {task.title}")
            print(f"{'Priorytet:':<15} {task.priority}/3")
            print(f"{'Czas:':<15} {task.minutes} min")

    print(f"\n{'-' * 45}")
    print(f"{'Łączny czas:':<20} {total_minutes} min")
    print(f"{'Liczba zadań:':<20} {len(sorted_tasks)}")
    print(f"{'Tagi:':<20} {', '.join(sorted(tags)) if tags else 'brak'}")

    print(f"\n{'=' * 45}")
    print(f"{'PLAN NA DZIŚ':^45}")
    print(f"{'=' * 45}")

    todays_plan = list(get_todays_plan(tasks))
    plan_minutes = sum(task.minutes for task in todays_plan)
    
    if not todays_plan:
        print("Brak zadań do zaplanowania.")
    else:
        for task in todays_plan:
            print(f"{task.id}. {task.title} ({task.minutes} min)")
        print(f"\nŁączny czas planu: {plan_minutes} min")

    print(f"{'=' * 45}\n")

def show_summary() -> None:
    try:
        conn = get_db_connection()
        tasks = database.get_all_tasks(conn)
    except ValueError as error:
        print(f"Błąd: {error}")
    finally:
        conn.close()

    total_tasks = len(tasks)
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

def main():
    conn = get_db_connection()

    try:
        database.create_table(conn)
        database.import_from_json(conn, json_path)
        tasks = database.get_all_tasks(conn)
    finally:
        conn.close()

    manager = TaskManager()
    manager.tasks = tasks
    actions = {
        "1": lambda: add_task_menu(manager),
        "2": show_tasks,
        "3": search_tasks_menu,
        "4": lambda: complete_task_menu(manager),
        "5": lambda: delete_task_menu(manager),
        "6": lambda: export_tasks_csv([task.to_dict() for task in tasks], csv_path),
        "7": show_report,
        "8": show_summary,
    }

    while True:
        print()
        print("1. Dodaj zadanie")
        print("2. Pokaż zadania")
        print("3. Szukaj zadania")
        print("4. Ustaw jako zrobione")
        print("5. Usuń zadanie")
        print("6. Eksportuj zadania do csv")
        print("7. Pokaz raport")
        print("8. Pokaz podsumowanie")
        print("9. Koniec")

        action = input("Podaj numer akcji (1-7): ").strip()

        if action == "9":
            break

        selected_action = actions.get(action)
        if selected_action is None:
            print("Nieprawidłowa akcja!")
            continue
        selected_action()

if __name__ == "__main__":
    main()