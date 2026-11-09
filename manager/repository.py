from collections.abc import Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from errors import TaskManagerError, InvalidTaskError, TaskDontExistError
from manager.models import Tag, Task, TaskTag

ORDER_OPTIONS = {
    "priority": (Task.priority.desc(), Task.id),
    "minutes": (Task.minutes, Task.id),
    "title": (Task.title, Task.id),
    "id": (Task.id,),
}

def add_task(
    session: Session,
    title: str,
    minutes: int,
    priority: int = 1,
    tags: Iterable[str] = ()
) -> Task:
    if not title.strip():
        raise InvalidTaskError("tytuł", title)
    if minutes <= 0:
        raise InvalidTaskError("minuty", minutes)
    if priority not in range(1, 4):
        raise InvalidTaskError("priorytet", priority)

    existing_titles = session.scalars(select(Task.title))
    if any(existing_title.lower() == title.strip().lower() for existing_title in existing_titles):
        raise TaskManagerError(f"Zadanie '{title.strip()}' już istnieje.")

    task = Task(title=title.strip(), minutes=minutes, priority=priority)
    session.add(task)
    session.flush()

    for name in {tag.strip().lower() for tag in tags if tag.strip()}:
        tag = session.scalars(select(Tag).where(Tag.name == name)).first()
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()
        session.add(TaskTag(task_id=task.id, tag_id=tag.id))

    session.commit()
    return task

def search_tasks(session: Session, phrase: str) -> list[Task]:
    query = select(Task).where(Task.title.contains(phrase)).order_by(Task.id)
    return list(session.scalars(query))

def get_task_by_id(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise TaskDontExistError(task_id)
    return task

def get_all_tasks(session: Session, order_by: str = "priority") -> list[Task]:
    order_by = order_by.strip().lower()
    if order_by not in ORDER_OPTIONS:
        raise ValueError("Nieprawidłowe sortowanie")
    query = select(Task).order_by(*ORDER_OPTIONS[order_by])
    return list(session.scalars(query))

def get_undone_tasks(session: Session) -> list[Task]:
    select_query = (
        select(Task)
        .where(Task.is_done == False)
        .order_by(Task.priority.desc(), Task.minutes)
    )
    return list(session.scalars(select_query))

def get_task_tags(session: Session, task_id: int) -> list[str]:
    select_query = (
        select(Tag.name)
        .join(TaskTag, TaskTag.tag_id == Tag.id)
        .where(TaskTag.task_id == task_id)
        .order_by(Tag.name)
    )
    return list(session.scalars(select_query))

def mark_as_done(session: Session, task_id: int) -> Task:
    task = get_task_by_id(session, task_id)
    task.is_done = True
    session.commit()
    return task

def delete_task(session: Session, task_id: int) -> Task:
    task = get_task_by_id(session, task_id)
    session.execute(delete(TaskTag).where(TaskTag.task_id == task_id))
    session.delete(task)
    session.commit()
    return task