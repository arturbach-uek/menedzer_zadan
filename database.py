from models import Task
import sqlite3

def create_table(conn):
    create_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            priority INTEGER NOT NULL,
            is_done INTEGER NOT NULL DEFAULT 0
        )
    """
    with conn:
        conn.execute(create_query)

def add_task(conn, task: Task) -> int:
    insert_query = "INSERT INTO tasks(title, minutes, priority) VALUES (?, ?, ?)"
    with conn:
        cursor = conn.execute(insert_query, (task.title, task.minutes, task.priority))
    return cursor.lastrowid

def search_tasks(conn, phrase: str) -> list[Task]:
    search_query = "SELECT * FROM tasks WHERE title LIKE ?"
    with conn:
        cursor = conn.execute(search_query, (f"%{phrase}%", ))
    
    found_tasks = [Task.from_dict(dict(task)) for task in cursor.fetchall()]
    return found_tasks

def get_all_tasks(conn, order_by="priority") -> list[Task]:
    allowed_columns = {
        "priority": "priority DESC", 
        "minutes": "minutes", 
        "title": "title"
    }

    order_by = order_by.lower().strip()
    if order_by not in allowed_columns:
        raise ValueError("Nieprawidłowe sortowanie")

    select_query = "SELECT title, minutes, priority FROM tasks ORDER BY ?"
    with conn:
        cursor = conn.execute(select_query, (allowed_columns[order_by], ))
        tasks = [Task.from_dict(dict(task)) for task in cursor.fetchall()]
    return tasks