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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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
