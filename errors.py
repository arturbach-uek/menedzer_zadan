class TaskManagerError(Exception):
    pass

class TaskDontExistError(TaskManagerError):
    def __init__(self, task_id):
        self.task_id = task_id
        super().__init__(f"Zadanie „{task_id}” nie istnieje.")

class InvalidTaskError(TaskManagerError):
    def __init__(self, field, value):
        self.field = field
        self.value = value
        super().__init__(f"Niepoprawna wartość {value} dla pola {field}.")