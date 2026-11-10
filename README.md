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

## 🖥️ Sample Output

Output of `python main.py`:

```
Today's Schedule for Jordan
---------------------------
  [ ] 07:30  Mochi: Morning walk (30 min, high, daily)
  [ ] 08:00  Luna: Breakfast (10 min, high, daily)
  [ ] 12:00  Luna: Flea medication (5 min, high, weekly)
  [ ] 18:00  Mochi: Evening walk (30 min, medium, daily)
```

## 🧪 Testing PawPal+

Run the suite from the project root:

```bash
python -m pytest
```

`tests/test_pawpal.py` has 30 tests covering:

- **Basics.** `mark_complete()` flips the status, adding and removing tasks changes a pet's task count, `Owner` collects tasks across all pets and rejects duplicate pet names.
- **Validation.** Bad times (`"25:00"`, `"noon"`), unknown priorities or frequencies, and non-positive durations raise `ValueError`. `"7:05"` is normalized to `"07:05"`.
- **Sorting.** Tasks come back in chronological order even when added out of order. Tomorrow's tasks sort after today's. Equal priorities are tie-broken by time. An empty schedule returns an empty list.
- **Filtering.** By pet name (case-insensitive), by completed or not completed, and an unknown pet returns nothing.
- **Recurrence.** Completing a daily task adds a new, incomplete copy due tomorrow. A weekly task's copy is due in 7 days. A one-time task doesn't recur. The new copy is independent of the original.
- **Conflict detection.** Identical start times are flagged, overlapping durations for the same pet are flagged, back-to-back tasks (08:00–08:30 then 08:30) are *not* flagged, completed and other-day tasks are ignored, and one long task can conflict with several others.
- **Daily plan.** High-priority tasks win when time is short, the plan never exceeds the owner's budget, skipped tasks are explained, and completed tasks or empty schedules give an empty plan.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.1.1, pluggy-1.5.0
rootdir: /Users/alyhegazy/Desktop/CodePath /ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 30 items

tests/test_pawpal.py ..............................                      [100%]

============================== 30 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Every scheduling rule has a test, including the edge cases I could think of (empty schedules, exact-time ties, back-to-back tasks). I'm holding back one star because the Streamlit UI is only checked by hand, and the planner's greedy choice isn't compared against an optimal plan.

## 📐 Smarter Scheduling

All scheduling logic lives in `Scheduler` in `pawpal_system.py`.

| Feature | Method(s) | How it works |
|---------|-----------|--------------|
| Sorting by time | `Scheduler.sort_by_time()` | `sorted()` with a lambda key of `(due_date, minutes after midnight)`, so `"07:30"` comes before `"18:00"` and tomorrow's tasks come after today's. Times are normalized to zero-padded `HH:MM` when a `Task` is created. |
| Sorting by priority | `Scheduler.sort_by_priority()` | Orders high → medium → low, then by time. Used by the daily planner. |
| Filtering | `Scheduler.filter_tasks(pet_name=, completed=)` | Keeps tasks matching a pet name (case-insensitive) and/or completion status. Passing `None` means "don't filter on this." `get_tasks_for_date()` filters by due date. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Completing a `daily` or `weekly` task creates a fresh copy due `today + timedelta(days=1)` or `+ timedelta(weeks=1)` and adds it to the same pet. `once` tasks just get marked done. |
| Conflict detection | `Scheduler.detect_conflicts()` | Sorts the day's unfinished tasks by start time and flags any pair whose `[start, start + duration)` windows overlap, for the same pet or different pets. It returns warning strings instead of raising, so the app keeps running. |
| Daily plan within a time budget | `Scheduler.generate_daily_plan()` → `DailyPlan` | Greedy: takes unfinished tasks for the day in priority order and keeps each one that still fits in `Owner.available_minutes`. `DailyPlan.explain()` says why each task was kept or skipped. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
