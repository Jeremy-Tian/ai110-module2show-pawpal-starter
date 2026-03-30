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

- The scheduler considers time availability (daily time slots), priority, and task status. It builds a 30-minute slot grid from a work window then assigns pending tasks greedily.
- Time is primary (tasks have scheduled_time or best fit), priority is secondary (shorter duration tasks can be sorted ahead), and preferences can be added later through task metadata.
- I chose these because they are most user-visible and easy to test: owners care about no overlaps and getting urgent tasks done first.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

In the current implementation, conflict detection only checks for exact slot-time overlaps using discrete schedule slots, which is fast and easy to reason about. The tradeoff is that we do not detect partial overlaps (e.g., task A from 9:15-9:45 and task B from 9:30-10:00 in a 30-minute slot model), which simplifies the logic but may miss some real-world collisions. This is reasonable for the MVP because it keeps the scheduler lightweight and deterministic, with a clear next step to add interval arithmetic for finer-grained conflict checks.

In the current implementation, conflict detection only checks for exact slot-time overlaps using discrete schedule slots, which is fast and easy to reason about. The tradeoff is that we do not detect partial overlaps (e.g., task A from 9:15-9:45 and task B from 9:30-10:00 in a 30-minute slot model), which simplifies the logic but may miss some real-world collisions. This is reasonable for the MVP because it keeps the scheduler lightweight and deterministic, with a clear next step to add interval arithmetic for finer-grained conflict checks.

---

## 3. AI Collaboration

**a. How you used AI**

- I used Copilot to brainstorm class designs, generate skeletons, and fill in the detailed implementation with Python dataclasses and schedule algorithms.
- Useful prompts included asking for method names and responsibilities (e.g., `Task`, `Pet`, `Owner`, `Scheduler`), and then refining with `sort_tasks_by_time`, `filter_tasks`, `detect_conflicts`, and recurrence logic.
- I also used the AI to translate requirements into concrete code paths for Streamlit state management (`st.session_state`) and for writing tests.

**b. Judgment and verification**

- One moment I didn’t accept an AI suggestion as-is was when AI proposed nested loops for task conflict checking that could lead to O(n^2) behavior without early exits. I kept a more explicit slot-based conflict strategy with `ScheduleSlot.conflicts()` and a lightweight `detect_conflicts()` method.
- I verified AI code suggestions by writing unit tests and running `pytest` after each change. When errors appeared (e.g., missing `priority` field), I adjusted the code accordingly and reran tests.

**c. Chat session organization**

- Splitting the work into separate chat sessions for planning, implementation, testing, and documentation helped keep each phase focused and reduced context switching.
- I used the earlier phase to lock down architecture, later phases for coding, then dedicated QA phase for tests and bug fixes.
- This approach kept the project coherent and made it easier to trace where each feature came from.

**d. Lead architect takeaway**

- Being the lead architect means deciding when an AI suggestion adds value vs. when it overcomplicates the design. I prioritized clarity and maintainability over clever but opaque code.
- A good pattern was to use AI as a coding assistant, then enforce design rules via tests and incremental commits.
- Outcome: a robust system with clear architecture, good coverage, and a professional UI pipeline.

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
