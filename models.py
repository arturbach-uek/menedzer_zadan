from dataclasses import dataclass, field
from errors import TaskDontExistError, InvalidTaskError

@dataclass
class Task:
    title: str
    minutes: int
    priority: int = 1
    tags: set = field(default_factory=set)
    is_done: bool = False

    def __post_init__(self):
        if not self.title.strip():
            raise InvalidTaskError("Tytuł nie może być pusty!")
        if self.priority not in range(1, 4):
            raise InvalidTaskError("Priorytet musi być z zakresu 1-3!")
        if self.minutes <= 0:
            raise InvalidTaskError("Planowany czas musi być większy niż 0!")

        self.tags = set(self.tags)

    @property
    def czy_pilne(self):
        return not self.is_done and self.priority >= 2

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data["title"],
            minutes=data["minutes"],
            priority=data.get("priority", 1),
            tags=set(data.get("tags", [])),
            is_done=data.get("is_done", False),
        )

    def to_dict(self):
        return {
            "title": self.title,
            "minutes": self.minutes,
            "priority": self.priority,
            "tags": sorted(self.tags),
            "is_done": self.is_done,
        }
    
    def mark_as_done(self):
        self.is_done = True

    def __str__(self):
        status_marker = "x" if self.is_done else " "
        return f"[{status_marker}] {self.title} ({self.minutes} min, P{self.priority})"

    def __eq__(self, other_task):
        if not isinstance(other_task, Task):
            return NotImplemented
        return self.title.lower() == other_task.title.lower()

@dataclass(eq=False)
class RecurringTask(Task):
    recurrence_interval_days: int = 7

    def __post_init__(self):
        super().__post_init__()
        if self.recurrence_interval_days <= 0:
            raise ValueError("Liczba dni między powtórzeniami musi być większa niż 0!")

    def __str__(self):
        recurrence_label = (
            "codziennie" 
            if self.recurrence_interval_days == 1 
            else f"co {self.recurrence_interval_days} dni"
        )
        return f"{super().__str__()} ↻ {recurrence_label}"

class TaskManager():
    def __init__(self):
        self.tasks = []
    def add_task(self, new_task):
        if new_task in self.tasks:
            raise ValueError("Task jest już zapisany na liście zadań!")
        self.tasks.append(new_task)

    def delete_task(self, title):
        for existing_task in self.tasks:
            if existing_task.title.lower() == title.lower():
                self.tasks.remove(existing_task)
                return
        raise TaskDontExistError("Task nie istnieje na liście zadań!")

    def __len__(self):
        return len(self.tasks)