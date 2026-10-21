from zadania import (
    add_task, 
    get_tasks, 
    complete_task, 
    get_raport, 
    get_todays_plan,
    load_tasks,
    save_tasks,
    export_tasks_csv,
    TaskNotFoundError
)
from pathlib import Path
tasks_path = Path.cwd() / "database" / "tasks.json"
csv_path = Path.cwd() / "database" / "tasks.csv"

def add_task_menu(tasks):
    title = input("Nazwa zadania: ").strip()
    title = title[:1].upper() + title[1:]

    tags_input = input("Tagi (po przecinku): ")
    tags = {tag.strip() for tag in tags_input.split(",") if tag.strip()}

    try:
        planned_time_minutes = int(input("Planowany czas (min): "))
    except ValueError:
        print("Błąd: planowany czas musi być liczbą całkowitą.")
        return

    priority_input = input("Priorytet (1-3, domyślnie 1): ").strip()

    try:
        priority = int(priority_input) if priority_input else 1
    except ValueError:
        print("Błąd: priorytet musi być liczbą całkowitą.")
        return

    done_input = input("Czy oznaczyć jako zrobione (tak/nie, domyślnie nie): ").strip().lower()
    mark_as_done = done_input == "tak"

    try:
        add_task(tasks, title, planned_time_minutes, priority, tags, mark_as_done)
        print(f"Pomyślnie dodano zadanie: {title}")
    except ValueError as error:
        print(f"Błąd: {error}")

def complete_task_menu(tasks):
    try:
        task_number = int(input(f"Numer zadania (1-{len(tasks)}): "))
    except ValueError:
        print("Błąd: numer zadania musi być liczbą całkowitą.")
        return
    
    try:
        result = complete_task(tasks, task_number)
        if result:
            print(f"Pomyślnie oznaczono zadanie {task_number} jako zrobione!")
        else:
            print("Nie można oznaczyć zadania: lista zadań jest pusta.")
    except TaskNotFoundError as error:
        print(error)

def show_report(tasks):
    sorted_tasks, total_minutes, tags = get_raport(tasks)
    total_minutes = sum(total_minutes)

    print(f"\n{'=' * 45}")
    print(f"{'RAPORT ZADAŃ':^45}")
    print(f"{'=' * 45}")

    if not sorted_tasks:
        print("Brak niezrobionych zadań!")
    else:
        for number, task in enumerate(sorted_tasks, start=1):
            print(f"\n{number}. {task['title']}")
            print(f"{'Priorytet:':<15} {task['priority']}/3")
            print(f"{'Czas:':<15} {task['minutes']} min")

    print(f"\n{'-' * 45}")
    print(f"{'Łączny czas:':<20} {total_minutes} min ({total_minutes / 60:.1f} godz.)")
    print(f"{'Liczba zadań:':<20} {len(sorted_tasks)}")
    print(f"{'Tagi:':<20} {', '.join(sorted(tags)) if tags else 'brak'}")
    print(f"{'=' * 45}")

    print(f"\n{'=' * 45}")
    print(f"{'PLAN NA DZIŚ':^45}")
    print(f"{'=' * 45}")

    todays_plan = list(get_todays_plan(tasks))

    if not todays_plan:
        print("Brak zadań do zaplanowania.")
    else:
        for number, task in enumerate(todays_plan, start=1):
            print(f"{number}. {task['title']} ({task['minutes']} min)")

        plan_minutes = sum(task["minutes"] for task in todays_plan)
        print(f"\n{'Łączny czas planu:':<25} {plan_minutes} min")

    print(f"{'=' * 45}\n")

def show_summary(tasks):
    total_tasks = len(tasks)
    completed_tasks = sum(task["done"] for task in tasks)
    remaining_tasks = total_tasks - completed_tasks
    total_minutes = sum(task["minutes"] for task in tasks)
    completed_minutes = sum(task["minutes"] for task in tasks if task["done"])

    print("\n--- PODSUMOWANIE ---")
    print(f"Liczba wszystkich zadań: {total_tasks}")
    print(f"Zrobione: {completed_tasks}")
    print(f"Pozostało: {remaining_tasks}")
    print(f"Łączny planowany czas: {total_minutes} min")
    print(f"Czas zrobionych zadań: {completed_minutes} min")
    print("Do widzenia!")

def main():
    tasks = load_tasks(tasks_path)
    actions = {
        "1": lambda: (add_task_menu(tasks), save_tasks(tasks, tasks_path)),
        "2": lambda: get_tasks(tasks),
        "3": lambda: (complete_task_menu(tasks), save_tasks(tasks, tasks_path)),
        "4": lambda: show_report(tasks),
        "5": lambda: export_tasks_csv(tasks, csv_path),
        "6": lambda: show_summary(tasks)
    }

    while True:
        print("\n1. Dodaj zadanie")
        print("2. Pokaż zadania")
        print("3. Oznacz jako zrobione")
        print("4. Raport")
        print("5. Eksport do csv")
        print("6. Koniec")

        action = input(f"Podaj numer akcji (1-{len(actions)}): ").strip()

        if action == "6":
            save_tasks(tasks, tasks_path)
            actions[action]()
            break

        selected_action = actions.get(action)
        if selected_action is None:
            print("Nieprawidłowa akcja!")
            continue

        selected_action()

if __name__ == "__main__":
    main()
