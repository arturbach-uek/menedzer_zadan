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
        self.is_done = False

    def mark_as_done(self):
        if not self.done:
            self.done = True

    def __str__(self):
        status_marker = "x" if self.done else " "
        return f"[{status_marker}] {self.title} ({self.minutes} min, P{self.priority})"

    def __eq__(self, other_task):
        if not isinstance(other_task, Task):
            return NotImplemented
        return self.title.lower() == other_task.title.lower()

class RecurringTask(Task):
    def __init__(self, title, minutes, recurrence_interval_days, priority=1, tags=None):
        if not title.strip():
            raise ValueError("Tytuł nie może być pusty!")
        super().__init__(title, minutes, priority, tags)
        if recurrence_interval_days < 0:
            raise ValueError("Liczba dni między powtórzeniami musi być większa niż 0!")
        self.recurrence_interval_days = recurrence_interval_days

    def __str__(self):
        recurrence_label = "codziennie" if self.recurrence_interval_days == 1 else f"co {self.recurrence_interval_days} dni"
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
        raise TaskNotFoundError("Task nie istnieje na liście zadań!")

    def __len__(self):
        return len(self.tasks)