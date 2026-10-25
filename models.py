class TaskNotFoundError(Exception):
    pass

class Task():
    def __init__(self, title, minutes, priority=1, tags=None):
        if not title.strip():
            raise ValueError("Tytuł nie może być pusty!")
        if priority not in range(1, 4):
            raise ValueError("Priorytet musi być z zakresu 1-3!")
        if minutes <= 0:
            raise ValueError("Planowany czas musi być większy niż 0!")
        
        self.title = title
        self.minutes = minutes
        self.priority = priority
        self.tags = set(tags or [])
        self.done = False

    def mark_as_done(self):
        if not self.done:
            self.done = True

    def __str__(self):
        checked = "x" if self.done else " "
        return f"[{checked}] {self.title} ({self.minutes} min, P{self.priority})"

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return self.title.lower() == other.title.lower()

class RecurringTask(Task):
    def __init__(self, title, minutes, how_often_days, priority=1, tags=None):
        if not title.strip():
            raise ValueError("Tytuł nie może być pusty!")
        super().__init__(title, minutes, priority, tags)
        self.how_often_days = how_often_days

    def __str__(self):
        recurrence = "codziennie" if self.how_often_days == 1 else f"co {self.how_often_days} dni"
        return f"{super().__str__()} ↻ {recurrence}"