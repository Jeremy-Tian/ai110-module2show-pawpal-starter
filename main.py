from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def run_demo():
    owner = Owner(owner_id=1, name="Alex")

    # Create pets
    pet1 = Pet(pet_id=101, name="Buddy", species="dog", age=5)
    pet2 = Pet(pet_id=102, name="Whiskers", species="cat", age=3)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Add tasks for pets
    now = datetime.now().replace(second=0, microsecond=0)
    pet1.add_task(Task(task_id=1001, description="Morning walk", pet_id=101, duration_minutes=30))
    pet1.add_task(Task(task_id=1002, description="Feed breakfast", pet_id=101, duration_minutes=15))
    pet2.add_task(Task(task_id=1003, description="Give meds", pet_id=102, duration_minutes=10))

    # Build schedule
    scheduler = Scheduler(owner)
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

    print("\n=== Schedule Slots ===")
    for slot in scheduler.get_schedule():
        task_desc = slot.task.description if slot.task else "FREE"
        print(f"Slot {slot.slot_id} {slot.start_time.time()} - {slot.end_time.time()} => {task_desc}")

    print("\nValidation:", scheduler.validate())


if __name__ == "__main__":
    run_demo()
