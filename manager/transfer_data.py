import database as db
from sqlalchemy import select
from sqlalchemy.orm import Session
from manager import repository
from manager.database import OLD_DB_PATH, engine
from manager.models import Task

def get_raw_tasks() -> list:
    conn = db.get_connection(OLD_DB_PATH)
    try:
        return db.get_all_tasks(conn)
    finally:
        conn.close()

def task_exists(session: Session, title: str) -> bool:
    task = session.scalars(select(Task).where(Task.title == title)).first()
    return task is not None

def main():
    transferred = 0
    skipped = 0
    with Session(engine) as session:
        for old_task in get_raw_tasks():
            if task_exists(session, old_task.title):
                skipped += 1
                continue
            task = repository.add_task(
                session, 
                old_task.title, 
                old_task.minutes, 
                old_task.priority, 
                old_task.tags
            )
            if old_task.is_done:
                repository.mark_as_done(session, task.id)
            transferred += 1
    print(f"Przeniesiono: {transferred}, pominięto: {skipped}.")

if __name__ == "__main__":
    main()
