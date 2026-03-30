from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# TASK: Represents one activity with schedule metadata.
@dataclass
class Task:
    """A single scheduled activity for a pet."""
    task_id: int
    description: str
    pet_id: int
    scheduled_time: Optional[datetime] = None
    duration_minutes: int = 30
    frequency: Optional[str] = None  # e.g., 'daily', 'weekly'
    status: str = "pending"  # 'pending', 'scheduled', 'completed'

    def mark_scheduled(self, scheduled_time: datetime) -> None:
        """Mark the task as scheduled at a specific time."""
        self.scheduled_time = scheduled_time
        self.status = "scheduled"

    def mark_completed(self) -> None:
        """Mark the task status as completed."""
        self.status = "completed"

    def is_overdue(self, now: Optional[datetime] = None) -> bool:
        """Check if the task is overdue relative to current time."""
        now = now or datetime.now()
        return self.scheduled_time is not None and self.scheduled_time < now and self.status != "completed"


@dataclass
class Pet:
    """A pet profile that contains task assignments."""
    pet_id: int
    name: str
    species: str
    age: Optional[int] = None
    weight: Optional[float] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        if task.pet_id != self.pet_id:
            raise ValueError("Task pet_id does not match")
        self.tasks.append(task)

    def get_open_tasks(self) -> List[Task]:
        """Return tasks that are not completed."""
        return [t for t in self.tasks if t.status != "completed"]

    def summary(self) -> Dict:
        """Return a simple summary of pet info and task count."""
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "weight": self.weight,
            "task_count": len(self.tasks),
        }


@dataclass
class Owner:
    """The owner that manages multiple pets."""
    owner_id: int
    name: str
    pets: Dict[int, Pet] = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet to this owner."""
        self.pets[pet.pet_id] = pet

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet from owner by ID."""
        self.pets.pop(pet_id, None)

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Retrieve a single pet by ID."""
        return self.pets.get(pet_id)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks for all owned pets."""
        tasks: List[Task] = []
        for pet in self.pets.values():
            tasks.extend(pet.tasks)
        return tasks


@dataclass
class ScheduleSlot:
    slot_id: int
    start_time: datetime
    end_time: datetime
    task: Optional[Task] = None

    def is_free(self) -> bool:
        return self.task is None

    def assign(self, task: Task) -> None:
        if not self.is_free():
            raise ValueError("Slot already occupied")
        self.task = task
        task.mark_scheduled(self.start_time)

    def clear(self) -> None:
        if self.task is not None:
            self.task.status = "pending"
        self.task = None

    def conflicts(self, other: "ScheduleSlot") -> bool:
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)


class Scheduler:
    """The schedule engine that assigns tasks to available timeslots."""

    def __init__(self, owner: Owner):
        """Initialize scheduler with an owner context."""
        self.owner = owner
        self.slots: List[ScheduleSlot] = []

    def build_day_slots(self, start: datetime, end: datetime, interval_minutes: int = 30) -> None:
        """Initialize daily schedule slots for a time range."""
        self.slots = []
        slot_id = 1
        current = start
        while current < end:
            slot_end = current + timedelta(minutes=interval_minutes)
            self.slots.append(ScheduleSlot(slot_id=slot_id, start_time=current, end_time=slot_end))
            current = slot_end
            slot_id += 1

    def get_pending_tasks(self) -> List[Task]:
        """Retrieve pending tasks across all pets for this owner."""
        return [t for t in self.owner.get_all_tasks() if t.status == "pending"]

    def schedule_tasks(self) -> None:
        """Greedy scheduling of pending tasks into open slots."""
        tasks = sorted(self.get_pending_tasks(), key=lambda t: t.duration_minutes, reverse=True)
        for task in tasks:
            for slot in self.slots:
                if slot.is_free():
                    slot.assign(task)
                    break

    def validate(self) -> bool:
        """Validate that there are no conflicting slot assignments."""
        scheduled_slots = [s for s in self.slots if s.task is not None]
        for i, a in enumerate(scheduled_slots):
            for b in scheduled_slots[i + 1:]:
                if a.conflicts(b):
                    return False
        return True

    def get_schedule(self) -> List[ScheduleSlot]:
        """Return the current schedule data structure."""
        return self.slots

    def clear_schedule(self) -> None:
        """Clear all slot assignments and reset task status to pending."""
        for slot in self.slots:
            slot.clear()


