# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

In the initial design I defined a clean, object-oriented logic layer that separates domain modeling from schedule orchestration. The core classes in `pawpal_system.py` are:

- `PetProfile`: represents a pet's identity and care preferences, holding attributes like `name`, `species`, `age`, `weight`, `preferences`, and `health_notes`. Responsibilities include updating preferences, recording health notes, and summarizing current pet state.

- `CareTask`: represents an individual care action, holding `task_id`, `pet_id`, `task_type`, `duration_minutes`, time constraints (`earliest_start`, `latest_end`), `priority`, and `status`. Responsibilities include checking schedulability, rescheduling, marking completion, and producing a task summary.

- `ScheduleSlot`: represents a discrete time block that can be assigned to one task, holding `slot_id`, `start_time`, `end_time`, `task`, and `assigned_to`. Responsibilities include monitoring free state, assigning/clearing tasks, and checking slot conflicts.

- `ScheduleManager`: orchestrates the full schedule, with collections of pets, tasks, slots, and constraints. Responsibilities include adding pets/tasks, building daily time slots, finding and assigning available slots, generating schedules by priority, and validating schedule consistency.

This design provides clear single-responsibility classes and keeps the scheduling logic manageable and testable.

**b. Design changes**

Yes, the implementation evolved as I moved from the UML-like plan into Python code. I started with a lightweight function-based approach in `app.py` and later restructured to dedicated classes in `pawpal_system.py` to improve maintainability and explicit domain boundaries.

- `PetProfile` and `CareTask` were converted to `@dataclass` style for cleaner attribute handling and easier construction.
- `ScheduleSlot` was introduced as explicit slot model with conflict detection.
- `ScheduleManager` was made responsible for building slots, finding available slots, assigning tasks, and schedule validation.
- Added design review notes around potential expansions: stronger pet-task relationship, per-pet overlap checks, caregiver modelling, and constraint rule engine.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

In the current implementation, conflict detection only checks for exact slot-time overlaps using discrete schedule slots, which is fast and easy to reason about. The tradeoff is that we do not detect partial overlaps (e.g., task A from 9:15-9:45 and task B from 9:30-10:00 in a 30-minute slot model), which simplifies the logic but may miss some real-world collisions. This is reasonable for the MVP because it keeps the scheduler lightweight and deterministic, with a clear next step to add interval arithmetic for finer-grained conflict checks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
