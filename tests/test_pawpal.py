"""Tests for the PawPal+ logic layer."""

import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Scheduler, Task  # noqa: E402

TODAY = date.today()


@pytest.fixture
def household():
    """An owner with two pets and no tasks yet."""
    owner = Owner("Jordan", available_minutes=60)
    dog = Pet("Mochi", "dog")
    cat = Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat, Scheduler(owner)


# ----- Task & Pet basics ----------------------------------------------------


def test_mark_complete_changes_status():
    task = Task("Morning walk", "07:30")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Breakfast", "08:00"))
    assert pet.task_count() == 1
    assert pet.tasks[0].pet_name == "Mochi"


def test_remove_task_decreases_count():
    pet = Pet("Mochi", "dog")
    task = Task("Breakfast", "08:00")
    pet.add_task(task)
    pet.remove_task(task)
    assert pet.task_count() == 0


def test_time_is_normalized_to_zero_padded():
    assert Task("Walk", "7:05").time == "07:05"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"time": "25:00"},
        {"time": "noon"},
        {"time": "08:00", "priority": "urgent"},
        {"time": "08:00", "frequency": "monthly"},
        {"time": "08:00", "duration_minutes": 0},
    ],
)
def test_invalid_task_fields_raise(kwargs):
    with pytest.raises(ValueError):
        Task("Bad task", **kwargs)


def test_owner_rejects_duplicate_pet_names(household):
    owner, *_ = household
    with pytest.raises(ValueError):
        owner.add_pet(Pet("mochi", "dog"))  # case-insensitive duplicate


def test_owner_collects_tasks_across_pets(household):
    owner, dog, cat, _ = household
    dog.add_task(Task("Walk", "07:00"))
    cat.add_task(Task("Feed", "08:00"))
    assert {t.description for t in owner.get_all_tasks()} == {"Walk", "Feed"}


# ----- Sorting ----------------------------------------------------------------


def test_sort_by_time_returns_chronological_order(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Evening walk", "18:00"))
    cat.add_task(Task("Breakfast", "07:45"))
    dog.add_task(Task("Lunch", "12:00"))
    dog.add_task(Task("Early pill", "6:30"))
    times = [t.time for t in scheduler.sort_by_time()]
    assert times == ["06:30", "07:45", "12:00", "18:00"]


def test_sort_by_time_puts_later_dates_after_today(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Tomorrow early", "06:00", due_date=TODAY + timedelta(days=1)))
    dog.add_task(Task("Today late", "21:00"))
    assert [t.description for t in scheduler.sort_by_time()] == ["Today late", "Tomorrow early"]


def test_sort_by_priority_breaks_ties_by_time(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Low", "06:00", priority="low"))
    dog.add_task(Task("High late", "20:00", priority="high"))
    dog.add_task(Task("High early", "09:00", priority="high"))
    assert [t.description for t in scheduler.sort_by_priority()] == ["High early", "High late", "Low"]


def test_sorting_empty_schedule_returns_empty_list(household):
    *_, scheduler = household
    assert scheduler.sort_by_time() == []
    assert scheduler.get_tasks_for_date() == []


# ----- Filtering --------------------------------------------------------------


def test_filter_by_pet_name(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Walk", "07:00"))
    cat.add_task(Task("Feed", "08:00"))
    assert [t.description for t in scheduler.filter_tasks(pet_name="luna")] == ["Feed"]


def test_filter_by_completion_status(household):
    _, dog, _, scheduler = household
    done = Task("Walk", "07:00")
    dog.add_task(done)
    dog.add_task(Task("Feed", "08:00"))
    done.mark_complete()
    assert [t.description for t in scheduler.filter_tasks(completed=False)] == ["Feed"]
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Walk"]


def test_filter_for_unknown_pet_is_empty(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Walk", "07:00"))
    assert scheduler.filter_tasks(pet_name="Ghost") == []


# ----- Recurrence -------------------------------------------------------------


def test_completing_daily_task_creates_task_for_tomorrow(household):
    _, dog, _, scheduler = household
    walk = Task("Walk", "07:30", frequency="daily")
    dog.add_task(walk)

    next_walk = scheduler.mark_task_complete(walk)

    assert walk.completed is True
    assert next_walk is not None
    assert next_walk.due_date == TODAY + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk.time == "07:30"
    assert next_walk in dog.tasks
    assert dog.task_count() == 2


def test_completing_weekly_task_creates_task_next_week(household):
    _, _, cat, scheduler = household
    meds = Task("Flea meds", "12:00", frequency="weekly")
    cat.add_task(meds)
    next_meds = scheduler.mark_task_complete(meds)
    assert next_meds.due_date == TODAY + timedelta(weeks=1)


def test_completing_one_time_task_does_not_recur(household):
    _, dog, _, scheduler = household
    vet = Task("Vet visit", "10:00", frequency="once")
    dog.add_task(vet)
    assert scheduler.mark_task_complete(vet) is None
    assert dog.task_count() == 1


def test_completing_twice_does_not_duplicate_next_occurrence(household):
    _, dog, _, scheduler = household
    walk = Task("Walk", "07:30", frequency="daily")
    dog.add_task(walk)
    scheduler.mark_task_complete(walk)
    assert scheduler.mark_task_complete(walk) is None
    assert dog.task_count() == 2


def test_next_occurrence_is_independent_copy():
    walk = Task("Walk", "07:30", frequency="daily")
    copy = walk.next_occurrence()
    copy.description = "Changed"
    assert walk.description == "Walk"


# ----- Conflict detection -------------------------------------------------------


def test_detects_tasks_at_exact_same_time(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Walk", "08:00", 30))
    cat.add_task(Task("Feed", "08:00", 10))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0]


def test_detects_overlapping_durations_for_same_pet(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Walk", "08:00", 30))
    dog.add_task(Task("Brush", "08:20", 10))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "both for Mochi" in warnings[0]


def test_back_to_back_tasks_do_not_conflict(household):
    _, dog, _, scheduler = household
    dog.add_task(Task("Walk", "08:00", 30))
    dog.add_task(Task("Feed", "08:30", 10))
    assert scheduler.detect_conflicts() == []


def test_completed_and_other_day_tasks_are_ignored_for_conflicts(household):
    _, dog, cat, scheduler = household
    done = Task("Walk", "08:00", 30)
    dog.add_task(done)
    done.mark_complete()
    cat.add_task(Task("Feed", "08:00", 10))
    cat.add_task(Task("Tomorrow", "08:00", 10, due_date=TODAY + timedelta(days=1)))
    assert scheduler.detect_conflicts() == []


def test_one_long_task_conflicts_with_several(household):
    _, dog, cat, scheduler = household
    dog.add_task(Task("Long hike", "09:00", 120))
    cat.add_task(Task("Feed", "09:30", 10))
    cat.add_task(Task("Meds", "10:30", 5))
    assert len(scheduler.detect_conflicts()) == 2


# ----- Daily plan ---------------------------------------------------------------


def test_plan_prefers_high_priority_within_budget(household):
    owner, dog, cat, scheduler = household
    owner.available_minutes = 40
    dog.add_task(Task("Play", "07:00", 30, "low"))
    dog.add_task(Task("Walk", "09:00", 30, "high"))
    cat.add_task(Task("Meds", "12:00", 5, "high"))

    plan = scheduler.generate_daily_plan()

    assert [t.description for t in plan.scheduled] == ["Walk", "Meds"]  # time order
    assert [t.description for t in plan.skipped] == ["Play"]
    assert plan.minutes_used <= owner.available_minutes
    assert any("skipped" in line for line in plan.explain())


def test_plan_excludes_completed_tasks(household):
    _, dog, _, scheduler = household
    walk = Task("Walk", "07:00", 20)
    dog.add_task(walk)
    walk.mark_complete()
    assert scheduler.generate_daily_plan().scheduled == []


def test_plan_for_pet_with_no_tasks_is_empty(household):
    *_, scheduler = household
    plan = scheduler.generate_daily_plan()
    assert plan.scheduled == [] and plan.skipped == [] and plan.minutes_used == 0
