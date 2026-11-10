"""PawPal+ Streamlit UI. All scheduling logic lives in pawpal_system.py."""

from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this script on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=60)
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def task_rows(tasks: list[Task]) -> list[dict]:
    """Turn tasks into rows for st.table / st.dataframe."""
    return [
        {
            "Done": "✅" if t.completed else "⬜",
            "Date": t.due_date.strftime("%a %b %d"),
            "Time": t.time,
            "Pet": t.pet_name,
            "Task": t.description,
            "Minutes": t.duration_minutes,
            "Priority": t.priority,
            "Repeats": t.frequency,
        }
        for t in tasks
    ]


st.title("🐾 PawPal+")
st.caption("Plan your pets' day: walks, meals, meds, and more.")

# ----- Sidebar: owner + pets -------------------------------------------------
with st.sidebar:
    st.header("Owner")
    owner.name = st.text_input("Your name", value=owner.name)
    owner.available_minutes = int(
        st.number_input(
            "Minutes available for pet care today",
            min_value=5,
            max_value=600,
            step=5,
            value=owner.available_minutes,
        )
    )

    st.header("Pets")
    with st.form("add_pet", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
        if st.form_submit_button("Add pet"):
            try:
                owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                st.success(f"Added {pet_name.strip()} 🐾")
            except ValueError as err:
                st.error(str(err))

    for pet in owner.pets:
        st.write(f"**{pet.name}** · {pet.species}, {pet.age} yr · {pet.task_count()} task(s)")

if not owner.pets:
    st.info("👈 Start by adding a pet in the sidebar.")
    st.stop()

# ----- Add a task -------------------------------------------------------------
with st.expander("➕ Schedule a task", expanded=not owner.get_all_tasks()):
    with st.form("add_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        pet_choice = c1.selectbox("Pet", [p.name for p in owner.pets])
        description = c2.text_input("Task", placeholder="Morning walk")
        c3, c4, c5 = st.columns(3)
        due = c3.date_input("Date", value=date.today())
        start = c4.time_input("Time", value=time(8, 0), step=300)
        duration = c5.number_input("Minutes", min_value=1, max_value=480, value=20)
        c6, c7 = st.columns(2)
        priority = c6.selectbox("Priority", ["high", "medium", "low"], index=1)
        frequency = c7.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task", type="primary"):
            if not description.strip():
                st.error("Give the task a name.")
            else:
                owner.get_pet(pet_choice).add_task(
                    Task(
                        description.strip(),
                        start.strftime("%H:%M"),
                        int(duration),
                        priority,
                        frequency,
                        due_date=due,
                    )
                )
                st.success(f"Scheduled '{description.strip()}' for {pet_choice} at {start:%H:%M}.")

# ----- Schedule view ------------------------------------------------------------
st.subheader("📅 Schedule")
c1, c2, c3 = st.columns(3)
view_day = c1.date_input("Day", value=date.today(), key="view_day")
pet_filter = c2.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
status_filter = c3.selectbox("Show", ["All", "To do", "Done"])

day_tasks = scheduler.get_tasks_for_date(view_day)
shown = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed={"All": None, "To do": False, "Done": True}[status_filter],
    tasks=day_tasks,
)

conflicts = scheduler.detect_conflicts(view_day)
if conflicts:
    st.warning(
        f"**{len(conflicts)} scheduling conflict(s)** — these tasks overlap. "
        "Consider moving one, or make sure someone can handle both at once.\n\n"
        + "\n".join(f"- {w.removeprefix('⚠ Conflict: ')}" for w in conflicts)
    )
elif day_tasks:
    st.success("No conflicts — every task has its own time slot.")

if shown:
    st.table(task_rows(shown))
else:
    st.info("Nothing matches these filters for this day.")

# ----- Mark complete -------------------------------------------------------------
pending = scheduler.filter_tasks(completed=False, tasks=day_tasks)
if pending:
    labels = {f"{t.time} · {t.pet_name}: {t.description}": t for t in pending}
    c1, c2 = st.columns([3, 1])
    choice = c1.selectbox("Mark a task done", list(labels), label_visibility="collapsed")
    if c2.button("✔ Done"):
        next_task = scheduler.mark_task_complete(labels[choice])
        if next_task:
            st.toast(f"Nice! Next '{next_task.description}' added for {next_task.due_date:%a %b %d}.")
        else:
            st.toast("Nice! Task completed.")
        st.rerun()

# ----- Daily plan ------------------------------------------------------------------
st.divider()
st.subheader("🧠 Smart daily plan")
st.caption(
    f"Picks the most important unfinished tasks that fit in your "
    f"{owner.available_minutes} available minutes, then lists them in time order."
)
if st.button("Generate plan", type="primary"):
    plan = scheduler.generate_daily_plan(view_day)
    if not plan.scheduled and not plan.skipped:
        st.info("Nothing left to plan for this day. 🎉")
    else:
        st.success(
            f"Planned {len(plan.scheduled)} task(s) using {plan.minutes_used} of "
            f"{plan.budget_minutes} minutes."
        )
        if plan.scheduled:
            st.table(task_rows(plan.scheduled))
        for t in plan.skipped:
            st.warning(
                f"Skipped **{t.pet_name}: {t.description}** ({t.duration_minutes} min, "
                f"{t.priority}) — not enough time left after higher-priority tasks."
            )
        with st.expander("Why this plan?"):
            st.text("\n".join(plan.explain()))
