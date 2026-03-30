import pytest
from datetime import datetime, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler, ScheduleSlot


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


def test_sort_tasks_by_time_puts_none_last():
    owner = Owner(owner_id=1, name='Test')
    pet = Pet(pet_id=10, name='Test Pet', species='dog')
    owner.add_pet(pet)

    t1 = Task(task_id=1, description='A', pet_id=10, scheduled_time=datetime(2026, 1, 1, 9, 0), duration_minutes=10)
    t2 = Task(task_id=2, description='B', pet_id=10, scheduled_time=None, duration_minutes=15)
    t3 = Task(task_id=3, description='C', pet_id=10, scheduled_time=datetime(2026, 1, 1, 8, 0), duration_minutes=5)
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_tasks_by_time(owner.get_all_tasks())

    assert [t.task_id for t in sorted_tasks] == [3, 1, 2]


def test_recurring_task_generation_daily():
    task = Task(task_id=99, description='Daily walk', pet_id=20, scheduled_time=datetime(2026, 1, 2, 7, 0), duration_minutes=30, frequency='daily')
    next_task = task.mark_completed()

    assert task.status == 'completed'
    assert next_task is not None
    assert next_task.pet_id == task.pet_id
    assert next_task.description == task.description
    assert next_task.status == 'pending'
    assert next_task.scheduled_time == datetime(2026, 1, 3, 7, 0)


def test_conflict_detection_reports_overlapping_slots():
    owner = Owner(owner_id=1, name='Test')
    pet = Pet(pet_id=10, name='Test Pet', species='dog')
    owner.add_pet(pet)

    t1 = Task(task_id=1, description='Task 1', pet_id=10, scheduled_time=datetime(2026, 1, 1, 9, 0), duration_minutes=30)
    t2 = Task(task_id=2, description='Task 2', pet_id=10, scheduled_time=datetime(2026, 1, 1, 9, 0), duration_minutes=30)

    slot1 = ScheduleSlot(slot_id=1, start_time=datetime(2026, 1, 1, 9, 0), end_time=datetime(2026, 1, 1, 9, 30), task=t1)
    slot2 = ScheduleSlot(slot_id=2, start_time=datetime(2026, 1, 1, 9, 0), end_time=datetime(2026, 1, 1, 9, 30), task=t2)

    scheduler = Scheduler(owner)
    scheduler.slots = [slot1, slot2]

    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert 'Conflict' in warnings[0]

