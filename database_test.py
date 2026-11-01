import sqlite3
import pytest
import database
from models import Task
from errors import TaskDontExistError

@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    database.create_table(connection)
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
    assert [task.priority for task in tasks] == [1, 3, 2]

def test_task_title_with_apostrophe(conn):
    task = Task("Zadzwoń do O'Brien", 15)
    database.add_task(conn, task)
    tasks = database.search_tasks(conn, "O'Brien")
    assert len(tasks) == 1
    assert tasks[0].title == "Zadzwoń do O'Brien"

def test_delete_nonexistent_task(conn):
    with pytest.raises(TaskDontExistError):
        database.delete_task(conn, 999)