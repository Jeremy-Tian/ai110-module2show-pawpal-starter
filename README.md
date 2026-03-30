# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ now includes additional scheduler features:

- Sorting: `Scheduler.sort_tasks_by_time()` sorts tasks by scheduled time first, then by duration/priority for deterministic assignments.
- Filtering: `Scheduler.filter_tasks(status, pet_name)` supports quick views for pending/completed work and pet-centric task lists.
- Conflict detection: `Scheduler.detect_conflicts()` identifies overlapping slot assignments with friendly warning messages instead of crashes.
- Daily/weekly recurrence (via `Task.frequency`) is now implemented as a future extension point in the task model.

## Testing PawPal+

Run:

```bash
python -m pytest
```

Tests cover:

- Task completion state transitions (`pending` → `completed`).
- Pet task management (`Pet.add_task`).
- Sorting tasks by absolute `scheduled_time`, with unscheduled tasks at end.
- Daily recurrence generation when completing a `daily` task.
- Conflict detection when two schedule slots overlap.

Confidence Level: ⭐⭐⭐⭐☆ (4/5)

The suite has green tests for current core behaviors; additional edge cases can be added for weekly recurrence and multi-level constraints.

