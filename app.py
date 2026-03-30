from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=1, name="Jordan")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

with st.expander("Add a new pet", expanded=True):
    new_pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="pet_species")
    new_pet_age = st.number_input("Age", min_value=0, max_value=30, value=2, key="pet_age")

    if st.button("Add pet"):
        pet_id = len(st.session_state.owner.pets) + 1
        new_pet = Pet(pet_id=pet_id, name=new_pet_name, species=new_pet_species, age=int(new_pet_age))
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added pet {new_pet_name}.")

pet_options = [f"{p.pet_id}: {p.name}" for p in st.session_state.owner.pets.values()]
selected_pet_key = "selected_pet"
selected_pet_display = st.selectbox("Select pet", options=pet_options or ["No pets yet"], key=selected_pet_key)

st.markdown("### Add task to selected pet")
if st.session_state.owner.pets:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration")
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority")

    if st.button("Add task"):
        pet_id = int(selected_pet_display.split(":")[0])
        task_id = sum(len(p.tasks) for p in st.session_state.owner.pets.values()) + 1
        task = Task(task_id=task_id, description=task_title, pet_id=pet_id, duration_minutes=int(duration), status="pending")
        st.session_state.owner.get_pet(pet_id).add_task(task)
        st.success(f"Added task to {st.session_state.owner.get_pet(pet_id).name}.")
else:
    st.info("Add a pet first to enable tasks")

st.markdown("### Current pet/tasks")
for pet in st.session_state.owner.pets.values():
    st.write(pet.summary())
    for t in pet.tasks:
        st.write(f"- [{t.status}] {t.description} ({t.duration_minutes} min)")

st.divider()

st.subheader("Build Schedule")
st.caption("Click to generate a schedule using the owner/pet/task scheduler logic.")

if st.button("Generate schedule"):
    scheduler = st.session_state.scheduler
    scheduler.owner = st.session_state.owner
    scheduler.build_day_slots(start=datetime.now(), end=datetime.now() + timedelta(hours=4), interval_minutes=30)
    scheduler.schedule_tasks()

    st.success("Schedule generated")
    st.write("Current schedule:")
    for slot in scheduler.get_schedule():
        task_text = f"{slot.task.description} ({slot.task.status})" if slot.task else "FREE"
        st.write(f"{slot.start_time.time()} - {slot.end_time.time()}: {task_text}")

    st.write("Schedule valid:", scheduler.validate())
