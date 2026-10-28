import pytest
from models import Task, TaskManager, TaskDontExistError, InvalidTaskError

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
    with pytest.raises(ValueError):
        manager.add_task(task2)

def test_deleting_nonexistent_task():
    manager = TaskManager()
    with pytest.raises(TaskDontExistError):
        manager.delete_task("Nieistniejące zadanie")

def test_delete_existing_task():
    manager = TaskManager()
    task = Task("Napisać raport", 45)
    manager.add_task(task)
    manager.delete_task("Napisać raport")
    assert len(manager) == 0