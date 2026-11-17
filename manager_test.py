import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from manager import repository
from manager.models import Base
from errors import TaskManagerError, TaskDontExistError, InvalidTaskError

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_add_task_with_two_tags(session):
    task = repository.add_task(session, "Napisać raport", 60, priority=2, tags=["praca", "excel"])
    tags = repository.get_task_tags(session, task.id)
    assert tags == ["excel", "praca"]

def test_get_undone_tasks(session):
    repository.add_task(session, "Zakupy", 30)
    done_task = repository.add_task(session, "Pranie", 20)
    repository.add_task(session, "Raport", 90, priority=3)
    repository.mark_as_done(session, done_task.id)

    tasks = repository.get_undone_tasks(session)
    assert [task.title for task in tasks] == ["Raport", "Zakupy"]

def test_mark_as_done_nonexistent_task(session):
    with pytest.raises(TaskDontExistError):
        repository.mark_as_done(session, 42)

def test_add_duplicate_task(session):
    repository.add_task(session, "Nauczyć się SQL", 60)
    with pytest.raises(TaskManagerError):
        repository.add_task(session, "NAUCZYĆ SIĘ SQL", 30)

def test_add_task_with_invalid_priority(session):
    with pytest.raises(InvalidTaskError):
        repository.add_task(session, "Nauczyć się Pythona", 60, priority=4)

def test_delete_task_removes_tags(session):
    task = repository.add_task(session, "Zakupy", 30, tags=["dom"])
    repository.delete_task(session, task.id)
    assert repository.get_all_tasks(session) == []
    assert repository.get_task_tags(session, task.id) == []

def test_sort_tasks_by_priority(session):
    repository.add_task(session, "Pranie", 30, priority=1)
    repository.add_task(session, "Nauka Pythona", 60, priority=3)
    repository.add_task(session, "Zakupy", 20, priority=2)
    tasks = repository.get_all_tasks(session)
    assert [task.priority for task in tasks] == [3, 2, 1]
