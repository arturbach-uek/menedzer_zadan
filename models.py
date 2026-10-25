class Task():
    def __init__(self, title, minutes, priority=1, tags=None):
        if not title.strip():
            raise ValueError("Tytuł nie może być pusty!")
        if priority not in range(1, 4):
            raise ValueError("Priorytet musi być z zakresu 1-3!")
        if minutes <= 0:
            raise ValueError("Planowany czas musi być większy niż 0")
        
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
