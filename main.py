from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def run_demo():
    owner = Owner(owner_id=1, name="Alex")

    # Create pets
    pet1 = Pet(pet_id=101, name="Buddy", species="dog", age=5)
    pet2 = Pet(pet_id=102, name="Whiskers", species="cat", age=3)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Add tasks for pets (out of order) and with scheduled times
    now = datetime.now().replace(second=0, microsecond=0)
    # Add two tasks with exact same scheduled_time for conflict detection
    conflict_time = now + timedelta(hours=1)
    pet1.add_task(Task(task_id=1002, description="Feed breakfast", pet_id=101, scheduled_time=conflict_time, duration_minutes=15))
    pet1.add_task(Task(task_id=1005, description="Play fetch", pet_id=101, scheduled_time=conflict_time, duration_minutes=20))

    # Add other tasks
    pet2.add_task(Task(task_id=1003, description="Give meds", pet_id=102, scheduled_time=now + timedelta(minutes=45), duration_minutes=10))
    pet1.add_task(Task(task_id=1001, description="Morning walk", pet_id=101, scheduled_time=now + timedelta(minutes=15), duration_minutes=30))
    pet2.add_task(Task(task_id=1004, description="Evening grooming", pet_id=102, duration_minutes=20))
    pet2.tasks[1].status = "completed"  # mark one task complete manually

    scheduler = Scheduler(owner)

    # Sorting tasks by scheduled_time via new scheduler method
    sorted_tasks = scheduler.sort_tasks_by_time(owner.get_all_tasks())

    # Filtering tasks for Buddy only and pending status
    buddy_pending = scheduler.filter_tasks(status="pending", pet_name="Buddy")

    # Build schedule
    scheduler.build_day_slots(start=now, end=now + timedelta(hours=3), interval_minutes=30)
    scheduler.schedule_tasks()

    # Output results
    print("=== Owner / Pets / Tasks ===")
    print(f"Owner: {owner.name} (id={owner.owner_id})")
    print("Pets:")
    for pet in owner.pets.values():
        print("  ", pet.summary())
        for task in pet.tasks:
            print("    -", task.task_id, task.description, task.status, task.scheduled_time)

    print("\n=== Sorted Tasks (by time) ===")
    for task in sorted_tasks:
        print("    ", task.task_id, task.description, task.status, task.scheduled_time)

    print("\n=== Filtered Tasks (Buddy pending) ===")
    for task in buddy_pending:
        print("    ", task.task_id, task.description, task.status, task.scheduled_time)

    print("\n=== Schedule Slots ===")
    for slot in scheduler.get_schedule():
        task_desc = slot.task.description if slot.task else "FREE"
        print(f"Slot {slot.slot_id} {slot.start_time.time()} - {slot.end_time.time()} => {task_desc}")

    print("\nValidation:", scheduler.validate())


if __name__ == "__main__":
    run_demo()
