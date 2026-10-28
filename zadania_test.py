from pathlib import Path
import pytest
from models import Task, TaskManager, TaskDontExistError, InvalidTaskError
from zadania import load_tasks, save_tasks

def test_add_task_increases_list_length():
    manager = TaskManager()
    manager.add_task(Task("Nauczyć się pytest", 60))
    assert len(manager) == 1

def test_complete_task_sets_done_to_true():
    task = Task("Nauka Pythona", 60)
    task.mark_as_done()
    assert task.is_done is True

def test_delete_task_with_invalid_title_raises_error():
    manager = TaskManager()
    with pytest.raises(TaskDontExistError):
        manager.delete_task("Zadanie")

def test_add_task_with_invalid_priority_raises_value_error():
    with pytest.raises(InvalidTaskError):
        Task("Zadanie", 30, priority=4)

def test_save_and_load_two_tasks(tmp_path: Path):
    tasks = [
        Task("Nauczyć się pytest", 60, tags={"nauka", "python"}),
        Task("Napisać testy", 30, priority=2, tags={"testy"}),
    ]
    file_path = tmp_path / "tasks.json"
    save_tasks([task.to_dict() for task in tasks], file_path)
    loaded_tasks = load_tasks(file_path)
    assert len(loaded_tasks) == 2
    assert loaded_tasks[0]["title"] == "Nauczyć się pytest"
    assert loaded_tasks[0]["minutes"] == 60
    assert set(loaded_tasks[0]["tags"]) == {"nauka", "python"}
    assert loaded_tasks[1]["title"] == "Napisać testy"
    assert loaded_tasks[1]["priority"] == 2
    assert set(loaded_tasks[1]["tags"]) == {"testy"}