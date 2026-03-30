from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class PetProfile:
    pet_id: int
    name: str
    species: str
    age: Optional[int] = None
    weight: Optional[float] = None
    preferences: Dict[str, str] = field(default_factory=dict)
    health_notes: List[str] = field(default_factory=list)

    def update_preferences(self, prefs: Dict[str, str]) -> None:
        self.preferences.update(prefs)

    def add_health_note(self, note: str) -> None:
        self.health_notes.append(f"{datetime.now().isoformat()}: {note}")

    def needs_medication(self, now: Optional[datetime] = None) -> bool:
        return False

    def summary(self) -> Dict:
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "weight": self.weight,
            "preferences": self.preferences,
            "health_notes": self.health_notes,
        }


@dataclass
class CareTask:
    task_id: int
    pet_id: int
    task_type: str
    duration_minutes: int = 30
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None
    priority: int = 1
    status: str = "pending"

    @property
    def duration(self) -> timedelta:
        return timedelta(minutes=self.duration_minutes)

    def is_schedulable(self, slot: "ScheduleSlot") -> bool:
        if not slot.is_free():
            return False
        slot_length = slot.end_time - slot.start_time
        return slot_length >= self.duration

    def mark_done(self) -> None:
        self.status = "done"

    def reschedule(self, earliest_start: datetime, latest_end: datetime) -> None:
        self.earliest_start = earliest_start
        self.latest_end = latest_end

    def describe(self) -> Dict:
        return {
            "task_id": self.task_id,
            "pet_id": self.pet_id,
            "task_type": self.task_type,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "status": self.status,
        }


@dataclass
class ScheduleSlot:
    slot_id: int
    start_time: datetime
    end_time: datetime
    task: Optional[CareTask] = None
    assigned_to: Optional[int] = None

    def is_free(self) -> bool:
        return self.task is None

    def assign(self, task: CareTask) -> None:
        if not self.is_free():
            raise ValueError("Slot already occupied")
        self.task = task
        self.task.status = "scheduled"

    def clear(self) -> None:
        if self.task is not None:
            self.task.status = "pending"
        self.task = None

    def conflicts(self, other_slot: "ScheduleSlot") -> bool:
        return not (self.end_time <= other_slot.start_time or self.start_time >= other_slot.end_time)


class ScheduleManager:
    def __init__(self):
        self.pets: Dict[int, PetProfile] = {}
        self.tasks: Dict[int, CareTask] = {}
        self.slots: List[ScheduleSlot] = []
        self.constraints: List = []

    def add_pet(self, pet: PetProfile) -> None:
        self.pets[pet.pet_id] = pet

    def add_task(self, task: CareTask) -> None:
        self.tasks[task.task_id] = task

    def build_day_slots(self, start: datetime, end: datetime, interval_minutes: int = 30) -> None:
        self.slots = []
        slot_id = 1
        current = start
        while current < end:
            slot_end = current + timedelta(minutes=interval_minutes)
            self.slots.append(ScheduleSlot(slot_id, current, slot_end))
            current = slot_end
            slot_id += 1

    def find_available_slot(self, task: CareTask) -> Optional[ScheduleSlot]:
        for slot in self.slots:
            if task.is_schedulable(slot):
                if task.earliest_start and slot.start_time < task.earliest_start:
                    continue
                if task.latest_end and slot.end_time > task.latest_end:
                    continue
                return slot
        return None

    def assign_task(self, task_id: int, slot_id: int) -> ScheduleSlot:
        task = self.tasks.get(task_id)
        slot = next((s for s in self.slots if s.slot_id == slot_id), None)
        if not task or not slot:
            raise ValueError("Invalid task or slot")
        slot.assign(task)
        return slot

    def generate_schedule(self) -> None:
        unassigned = [t for t in self.tasks.values() if t.status == "pending"]
        unassigned.sort(key=lambda t: -t.priority)
        for task in unassigned:
            slot = self.find_available_slot(task)
            if slot:
                slot.assign(task)

    def validate(self) -> bool:
        return all(slot.task is None or slot.task.status == "scheduled" for slot in self.slots)

    def adjust_for_priority(self) -> None:
        pass

