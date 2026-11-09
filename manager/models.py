from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    minutes: Mapped[int]
    priority: Mapped[int] = mapped_column(default=1, server_default="1")
    is_done: Mapped[bool] = mapped_column(default=False, server_default="0")

    @property
    def is_urgent(self) -> bool:
        return not self.is_done and self.priority >= 2

    def __str__(self) -> str:
        status_marker = "x" if self.is_done else " "
        return f"{self.id} | [{status_marker}] {self.title} ({self.minutes} min, P{self.priority})"

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title}, is_done={self.is_done})"

    def __eq__(self, other_task):
        if not isinstance(other_task, Task):
            return NotImplemented
        return self.title.lower() == other_task.title.lower()

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name={self.name})"

class TaskTag(Base):
    __tablename__ = "task_tags"
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)