from pathlib import Path
import pytest
from zadania import add_task, complete_task, TaskNotFoundError, load_tasks, save_tasks

def test_add_task_increases_list_length():
    tasks = []
    add_task(tasks, "Nauczyć się pytest", 60)
    assert len(tasks) == 1

def test_complete_task_sets_done_to_true():
    tasks = [
        {
            "title": "Nauka Pythona",
            "tags": set(),
            "minutes": 60,
            "priority": 1,
            "done": False,
        }
    ]
    complete_task(tasks, 1)
    assert tasks[0]["done"] is True

def test_complete_task_with_invalid_number_raises_error():
    tasks = [{"title": "Zadanie", "done": False}]
    with pytest.raises(TaskNotFoundError):
        complete_task(tasks, 2)

def test_add_task_with_invalid_priority_raises_value_error():
    tasks = []
    with pytest.raises(ValueError):
        add_task(tasks, "Zadanie", 30, priority=4)
        
def test_save_and_load_two_tasks(tmp_path: Path):
    tasks = []

    add_task(tasks, "Nauczyć się pytest", 60, tags={"nauka", "python"})
    add_task(tasks, "Napisać testy", 30, priority=2, tags={"testy"})

    file_path = tmp_path / "tasks.json"

    save_tasks(tasks, file_path)
    loaded_tasks = load_tasks(file_path)

    assert len(loaded_tasks) == 2
    assert loaded_tasks[0]["title"] == "Nauczyć się pytest"
    assert loaded_tasks[0]["minutes"] == 60
    assert loaded_tasks[0]["tags"] == {"nauka", "python"}
    assert loaded_tasks[1]["title"] == "Napisać testy"
    assert loaded_tasks[1]["priority"] == 2
    assert loaded_tasks[1]["tags"] == {"testy"}
