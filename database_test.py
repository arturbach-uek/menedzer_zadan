import sqlite3
import pytest
import database
from models import Task
from errors import TaskDontExistError

@pytest.fixture
def conn():
    connection = database.get_connection(":memory:")
    database.create_tables(connection)
    yield connection
    connection.close()

def test_add_and_get_task(conn):
    task = Task("Nauczyć się SQL", 60, priority=2)
    task_id = database.add_task(conn, task)
    tasks = database.get_all_tasks(conn)
    assert len(tasks) == 1
    assert tasks[0].id == task_id
    assert tasks[0].title == "Nauczyć się SQL"
    assert tasks[0].minutes == 60
    assert tasks[0].priority == 2

def test_sort_tasks_by_priority(conn):
    database.add_task(conn, Task("Pranie", 30, priority=1))
    database.add_task(conn, Task("Nauka Pythona", 60, priority=3))
    database.add_task(conn, Task("Zakupy", 20, priority=2))
    tasks = database.get_all_tasks(conn)
    assert [task.priority for task in tasks] == [3, 2, 1]

def test_task_title_with_apostrophe(conn):
    task = Task("Zadzwoń do O'Brien", 15)
    database.add_task(conn, task)
    tasks = database.search_tasks(conn, "O'Brien")
    assert len(tasks) == 1
    assert tasks[0].title == "Zadzwoń do O'Brien"

def test_delete_nonexistent_task(conn):
    with pytest.raises(TaskDontExistError):
        database.delete_task(conn, 999)

def test_add_tag_to_nonexistent_task(conn):
    with pytest.raises(sqlite3.IntegrityError):
        database.add_tag(conn, 999, "praca")

def test_delete_task_removes_its_tags(conn):
    task_id = database.add_task(conn, Task("Pranie", 30))
    database.add_tag(conn, task_id, "dom")
    database.delete_task(conn, task_id)
    links_count = conn.execute("SELECT COUNT(*) FROM task_tags").fetchone()[0]
    assert links_count == 0

def test_minutes_by_tag_report(conn):
    report_id = database.add_task(conn, Task("Raport", 30))
    mail_id = database.add_task(conn, Task("Mail", 45))
    shopping_id = database.add_task(conn, Task("Zakupy", 20))
    database.add_tag(conn, report_id, "praca")
    database.add_tag(conn, mail_id, "praca")
    database.add_tag(conn, shopping_id, "dom")
    assert dict(database.get_minutes_by_tag(conn)) == {"praca": 75, "dom": 20}