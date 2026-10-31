from errors import TaskManagerError
import pytest
from models import Task, TaskManager, TaskDontExistError, InvalidTaskError
from dataclasses import asdict

def test_invalid_priority():
    with pytest.raises(InvalidTaskError):
        Task("Nauczyć się Pythona", 60, priority=4)

def test_task_equality_ignores_case():
    task1 = Task("Nauczyć się Pythona", 60)
    task2 = Task("NAUCZYĆ SIĘ PYTHONA", 30)
    assert task1 == task2

def test_manager_length_after_adding_task():
    manager = TaskManager()
    task = Task("Napisać raport", 45)
    manager.add_task(task)
    assert len(manager) == 1

def test_adding_duplicate_task():
    manager = TaskManager()
    task1 = Task("Napisać raport", 45)
    task2 = Task("NAPISAĆ RAPORT", 60)
    manager.add_task(task1)
    with pytest.raises(TaskManagerError):
        manager.add_task(task2)

def test_deleting_nonexistent_task():
    manager = TaskManager()
    with pytest.raises(TaskDontExistError) as info:
        manager.delete_task("Pranie")
    assert info.value.task_id == "Pranie"

def test_task_dict_round_trip():
    task = Task("Pranie", 30)
    restored_task = Task.from_dict(task.to_dict())
    assert asdict(restored_task) == asdict(task)

def test_delete_existing_task():
    manager = TaskManager()
    task = Task("Napisać raport", 45)
    manager.add_task(task)
    manager.delete_task("Napisać raport")
    assert len(manager) == 0