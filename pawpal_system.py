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
    priority: int = 1
    frequency: Optional[str] = None  # e.g., 'daily', 'weekly'
    status: str = "pending"  # 'pending', 'scheduled', 'completed'

    def mark_scheduled(self, scheduled_time: datetime) -> None:
        """Mark the task as scheduled at a specific time."""
        self.scheduled_time = scheduled_time
        self.status = "scheduled"

    def mark_completed(self) -> Optional["Task"]:
        """Mark the task status as completed and return next recurrence task if applicable."""
        self.status = "completed"

        if self.frequency and self.scheduled_time:
            if self.frequency.lower() == "daily":
                next_time = self.scheduled_time + timedelta(days=1)
            elif self.frequency.lower() == "weekly":
                next_time = self.scheduled_time + timedelta(weeks=1)
            else:
                return None

            return Task(
                task_id=-1,
                description=self.description,
                pet_id=self.pet_id,
                scheduled_time=next_time,
                duration_minutes=self.duration_minutes,
                frequency=self.frequency,
                status="pending",
            )

        return None

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

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by scheduled_time, then by duration (desc), then by priority.

        Tasks with no scheduled_time are pushed to the end to avoid unintentional ordering.
        """
        # Tasks can have scheduled_time optionally; None values are pushed to end.
        return sorted(
            tasks,
            key=lambda t: (
                t.scheduled_time or datetime.max,
                -t.duration_minutes,
                t.priority,
            ),
        )

    def filter_tasks(self, status: Optional[str] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filter tasks by status and/or pet name.

        status: pending/scheduled/completed
        pet_name: case-insensitive pet name string.
        """
        tasks = self.owner.get_all_tasks()
        if status:
            tasks = [t for t in tasks if t.status == status]

        if pet_name:
            pets_by_name = {p.name.lower(): p.pet_id for p in self.owner.pets.values()}
            target_id = pets_by_name.get(pet_name.lower())
            if target_id is None:
                return []
            tasks = [t for t in tasks if t.pet_id == target_id]

        return tasks

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

    def detect_conflicts(self) -> List[str]:
        """Return lightweight conflict warnings for overheard tasks, not exceptions."""
        warnings: List[str] = []
        scheduled_slots = [s for s in self.slots if s.task is not None]

        for i, a in enumerate(scheduled_slots):
            for b in scheduled_slots[i + 1:]:
                if a.conflicts(b):
                    pet_a = self.owner.get_pet(a.task.pet_id)
                    pet_b = self.owner.get_pet(b.task.pet_id)
                    pet_a_name = pet_a.name if pet_a else f"pet_id:{a.task.pet_id}"
                    pet_b_name = pet_b.name if pet_b else f"pet_id:{b.task.pet_id}"
                    warnings.append(
                        f"Conflict: '{a.task.description}' ({pet_a_name}) and '{b.task.description}' ({pet_b_name}) overlap at {a.start_time.time()}"
                    )

        return warnings


    def get_schedule(self) -> List[ScheduleSlot]:
        """Return the current schedule data structure."""
        return self.slots

    def clear_schedule(self) -> None:
        """Clear all slot assignments and reset task status to pending."""
        for slot in self.slots:
            slot.clear()


