from sqlalchemy.orm import Session
from errors import TaskManagerError, TaskDontExistError
from zadania import get_raport, get_todays_plan
from manager import repository
from manager.database import engine, DB_PATH
import database

PRIORITY_NAMES = {1: "niski", 2: "średni", 3: "wysoki"}

db_path = DB_PATH

def add_task_menu(session: Session) -> None:
    title = input("Nazwa zadania: ").strip()
    title = title[:1].upper() + title[1:]

    tags_input = input("Tagi (po przecinku): ")
    tags = {tag.strip() for tag in tags_input.split(",") if tag.strip()}

    try:
        minutes = int(input("Planowany czas (min): ").strip())
        priority_input = input("Priorytet (1-3, domyślnie 1): ").strip()
        priority = int(priority_input) if priority_input else 1
        task = repository.add_task(session, title, minutes, priority, tags)
        print(f"Pomyślnie dodano zadanie: {title} (id: {task.id})")
    except (TaskManagerError, ValueError) as error:
        session.rollback()
        print(f"Błąd: {error}")

def show_tasks(session: Session) -> None:
    try:
        order_by = input("Sortuj po (priority/minutes/title): ") or "priority"
        tasks = repository.get_all_tasks(session, order_by)
        print(*tasks, sep="\n")
    except ValueError as error:
        print(f"Błąd: {error}")

def show_undone_tasks(session: Session) -> None:
    tasks = repository.get_undone_tasks(session)
    print(*tasks, sep="\n")

def complete_task_menu(session: Session) -> None:
    try:
        task_id = int(input("ID zadania do oznaczenia jako zrobione: "))
        task = repository.mark_as_done(session, task_id)
        print(f"Pomyślnie oznaczono zadanie '{task.title}' jako zrobione!")
    except (TaskDontExistError, ValueError) as error:
        print(f"Błąd: {error}")

def delete_task_menu(session: Session) -> None:
    try:
        task_id = int(input("ID zadania do usunięcia: "))
        task = repository.delete_task(session, task_id)
        print(f"Pomyślnie usunięto zadanie '{task.title}' z listy!")
    except (TaskDontExistError, ValueError) as error:
        print(f"Błąd: {error}")

def search_tasks_menu(session: Session) -> None:
    phrase = input("Szukaj zadania: ").strip()
    tasks = repository.search_tasks(session, phrase)
    print(*tasks, sep="\n")

def show_report() -> None:
    conn = database.get_connection(db_path)
    try:
        tasks = database.get_all_tasks(conn)
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

def show_summary(session: Session) -> None:
    tasks = repository.get_all_tasks(session)

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

def show_tag_reports() -> None:
    conn = database.get_connection(db_path)
    try:
        minutes_by_tag = database.get_minutes_by_tag(conn)
        priority_counts = database.get_priority_counts(conn, 2)
        unused_tags = database.get_unused_tags(conn)
    finally:
        conn.close()

    minutes_text = ", ".join(f"{name} {minutes}" for name, minutes in minutes_by_tag)
    priorities_text = ", ".join(
        f"{PRIORITY_NAMES[priority]} ({priority}) – {count} zadania"
        for priority, count in priority_counts
    )
    unused_text = ", ".join(unused_tags)

    print("\n=== Raporty ===")
    print(f"Minuty według tagów: {minutes_text or 'brak'}")
    print(f"Priorytety z co najmniej 2 zadaniami: {priorities_text or 'brak'}")
    print(f"Tagi bez zadań: {unused_text or 'brak'}")

def main():
    with Session(engine) as session:
        actions = {
            "1": lambda: add_task_menu(session),
            "2": lambda: show_tasks(session),
            "3": lambda: search_tasks_menu(session),
            "4": lambda: complete_task_menu(session),
            "5": lambda: delete_task_menu(session),
            "6": lambda: show_undone_tasks(session),
            "7": show_report,
            "8": lambda: show_summary(session),
            "9": show_tag_reports,
        }

        while True:
            print()
            print("1. Dodaj zadanie")
            print("2. Pokaż zadania")
            print("3. Szukaj zadania")
            print("4. Ustaw jako zrobione")
            print("5. Usuń zadanie")
            print("6. Pokaż do zrobienia")
            print("7. Pokaz raport")
            print("8. Pokaz podsumowanie")
            print("9. Raporty")
            print("10. Koniec")

            action = input("Podaj numer akcji (1-10): ").strip()

            if action == "10":
                break

            selected_action = actions.get(action)
            if selected_action is None:
                print("Nieprawidłowa akcja!")
                continue
            selected_action()

if __name__ == "__main__":
    main()
