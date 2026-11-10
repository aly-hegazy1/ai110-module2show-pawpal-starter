import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Streamlit reruns this script on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        try:
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added {pet_name}.")
        except ValueError as err:
            st.error(str(err))

if owner.pets:
    st.subheader("Schedule a task")
    with st.form("add_task", clear_on_submit=True):
        pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        time_value = st.time_input("Time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            owner.get_pet(pet_choice).add_task(
                Task(description, time_value.strftime("%H:%M"), int(duration), priority, frequency)
            )
            st.success(f"Added '{description}' for {pet_choice}.")

st.divider()
st.subheader("Today's schedule")
tasks = Scheduler(owner).get_tasks_for_date()
if tasks:
    st.table([{"Time": t.time, "Pet": t.pet_name, "Task": t.description} for t in tasks])
else:
    st.info("No tasks yet. Add a pet, then schedule a task.")
