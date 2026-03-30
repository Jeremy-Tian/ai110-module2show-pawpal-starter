import pytest
from datetime import datetime

from pawpal_system import Task, Pet


def test_task_completion_changes_status():
    task = Task(task_id=1, description="Test task", pet_id=1, duration_minutes=15)
    assert task.status == "pending"

    task.mark_completed()
    assert task.status == "completed"


def test_pet_add_task_increases_task_count():
    pet = Pet(pet_id=10, name="Test Pet", species="cat")
    assert len(pet.tasks) == 0

    task = Task(task_id=2, description="Feed", pet_id=10, duration_minutes=10)
    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert pet.tasks[0] == task
