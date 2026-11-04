from errors import TaskDontExistError
from models import Task
from pathlib import Path
import sqlite3
import json

def get_connection(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables(conn):
    with conn:
        create_tasks_query = """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                minutes INTEGER NOT NULL,
                priority INTEGER NOT NULL,
                is_done INTEGER NOT NULL DEFAULT 0
            )
        """
        conn.execute(create_tasks_query)

        create_tags_query = """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
        """
        conn.execute(create_tags_query)

        create_task_tags_query = """
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """
        conn.execute(create_task_tags_query)

def add_task(conn, task: Task) -> int:
    insert_query = "INSERT INTO tasks(title, minutes, priority) VALUES (?, ?, ?)"
    with conn:
        cursor = conn.execute(insert_query, (task.title, task.minutes, task.priority))
    return cursor.lastrowid

def add_tag(conn, task_id: int, tag_name: str) -> None:
    with conn:
        insert_tag_query = "INSERT OR IGNORE INTO tags(name) VALUES (?)"
        conn.execute(insert_tag_query, (tag_name, ))

        select_tag_id_query = "SELECT id FROM tags WHERE name = ?"
        tag_id = conn.execute(select_tag_id_query, (tag_name, )).fetchone()["id"]

        insert_task_tag_query = "INSERT INTO task_tags(task_id, tag_id) VALUES (?, ?)"
        conn.execute(insert_task_tag_query, (task_id, tag_id))

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

    select_query = f"SELECT id, title, minutes, priority, is_done FROM tasks ORDER BY {allowed_columns[order_by]}"
    with conn:
        cursor = conn.execute(select_query)
        tasks = [Task.from_dict(dict(task)) for task in cursor.fetchall()]
    return tasks

def mark_as_done(conn, task_id) -> bool:
    update_query = "UPDATE tasks SET is_done = 1 WHERE id = ?"
    with conn:
        cursor = conn.execute(update_query, (task_id, ))
        if cursor.rowcount == 0:
            raise TaskDontExistError(task_id)
    return True

def delete_task(conn, task_id) -> bool:
    delete_query = "DELETE FROM tasks WHERE id = ?"
    with conn:
        cursor = conn.execute(delete_query, (task_id, ))
        if cursor.rowcount == 0:
            raise TaskDontExistError(task_id)
    return True

def import_from_json(conn, file_path) -> int:
    if not Path(file_path).exists():
        return 0
    with conn:
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM tasks"
        tasks_count = cursor.execute(count_query)
        if tasks_count.fetchone()[0]:
            return 0
        
        with open(file_path, "r", encoding="utf-8-sig") as file:
            tasks_data = [
                (
                    task.get("title"), 
                    task.get("minutes"), 
                    task.get("priority", 1), 
                    task.get("is_done", 0)
                ) 
                for task in json.load(file)
            ]
        
        insert_query = "INSERT INTO tasks(title, minutes, priority, is_done) VALUES (?, ?, ?, ?)"
        cursor = conn.executemany(insert_query, tasks_data)
    return cursor.rowcount