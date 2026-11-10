# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. **Add a pet**: enter the owner's name and add one or more pets (name, species, age).
2. **Schedule a care task**: give a pet a task such as a walk, feeding, or medication, with a time, duration, priority, and how often it repeats (once, daily, weekly).
3. **See today's schedule**: view today's tasks across all pets in time order, with warnings when two tasks clash, and mark tasks done as the day goes on.

**a. Initial design**

My first UML draft (`diagrams/uml_draft.mmd`) had four classes:

- **Task** (dataclass): one care activity. It holds a description, a start time (`"HH:MM"`), a duration, a priority, a frequency, and whether it's done. Its only behavior is `mark_complete()`.
- **Pet** (dataclass): a pet's details plus the list of tasks that belong to it. It can add and remove tasks.
- **Owner**: the person using the app. It keeps a list of pets and how many minutes they have for pet care each day, and can collect every task across all its pets.
- **Scheduler**: the "brain." It takes an `Owner` and reads tasks through it, then sorts them and builds a daily plan. It doesn't store tasks itself.

Relationships: an Owner *has* many Pets (aggregation), a Pet *owns* many Tasks (composition), and the Scheduler *uses* an Owner.

**b. Design changes**

Yes. When I asked the AI to review the skeleton, it pointed out two gaps, and I agreed with both:

1. **Tasks didn't know which pet they belonged to.** `Owner.get_all_tasks()` returns one flat list, so the schedule couldn't say "Mochi: Morning walk" and a conflict warning couldn't name the pets involved. I added a `pet_name` field to `Task`. `Pet.add_task()` fills it in automatically, so the user never has to type it twice.
2. **Tasks had no date.** Without one, a recurring task can't be rescheduled for "tomorrow," and "today's schedule" can't be told apart from next week's. I added a `due_date` field that defaults to today.

I also added `Owner.get_pet(name)` so the UI and the Scheduler can find a pet by name instead of scanning the list themselves. `add_pet()` now rejects duplicate names, since names are how pets get looked up.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers four things:

- **Time of day.** Every task has an `HH:MM` start time, and the schedule is always shown in that order.
- **Priority** (high, medium, low). It decides which tasks make it into the day when time is short.
- **The owner's time budget** (`Owner.available_minutes`). The daily plan never schedules more minutes than the owner has.
- **Completion and due date.** Finished tasks and tasks due on other days are left out of today's plan.

I treated priority as the main constraint. A missed medication or meal matters much more than a missed puzzle-toy session, so the planner fills the budget with high-priority tasks first. Time of day decides the order tasks are *shown* in, but not which ones get *chosen*.

**b. Tradeoffs**

**The planner is greedy, not optimal.** `generate_daily_plan()` goes down the list by priority and keeps each task that still fits in the remaining minutes. It never goes back to try a different combination. That means it can leave time unused. With 25 minutes left and two 15-minute low-priority tasks plus one 20-minute task ahead of them, it takes the 20-minute task and then can't fit either 15-minute one. A knapsack-style search could pack the time better.

I think that's the right call here. For pet care, "most important things first" is what an owner would do themselves, and it's easy to explain in one sentence. A plan that is technically more efficient but drops a medication to fit two play sessions would be worse.

**Conflicts are warnings, not blockers.** `detect_conflicts()` checks real overlapping time windows (start + duration), not just identical start times. But it only *reports* the overlaps. It doesn't move tasks around. Some overlaps are fine in practice (you can put the cat's food down while the dog is on a walk), so the owner decides, not the code.

**Comparing with the AI's suggestion.** When I asked how to simplify `detect_conflicts()`, the AI suggested `itertools.combinations(tasks, 2)` to check every pair in one line. That's shorter, but it always checks all n² pairs. I kept my version, which sorts first and `break`s out of the inner loop once a later task starts after the current one ends. It's still easy to read, and the comment explains the early exit.

---

## 3. AI Collaboration

**a. How you used AI**

I used **Claude Code in agent mode inside VS Code** for the whole build. I gave it the full project brief and had it work through the phases in order: draft UML → class skeleton → core implementation and CLI demo → Streamlit wiring → algorithms → tests → UI polish and docs. It committed after each phase, so the git history works as a set of checkpoints I can review or roll back to.

The most useful features were:

- **Multi-file agent edits.** Recurrence touched `Task` (`next_occurrence`), `Scheduler` (`mark_task_complete`), `main.py`, the tests, and the README together. Doing that by hand file by file would have been easy to get out of sync.
- **Running code to check itself.** The agent ran `python main.py`, `python -m pytest`, and a headless Streamlit `AppTest` after each change, instead of just claiming the code worked. Reading the CLI output is how the sorting bug below was caught.
- **Design review prompts.** "Review this skeleton for missing relationships or bottlenecks" produced the two design changes in 1b (`pet_name` and `due_date` on `Task`).

The most helpful prompts were specific and checkable. "Make the demo show a task being skipped for lack of time" worked much better than "make the demo better."

**b. Judgment and verification**

**The first version of `sort_by_time()` was wrong.** It sorted only by the `HH:MM` string. That looked fine until the demo marked a daily walk complete: the new walk for *tomorrow* at 07:30 jumped to the top of the "still to do" list, ahead of today's 07:45 breakfast. The sort key was changed to `(due_date, minutes after midnight)`, and a regression test (`test_sort_by_time_puts_later_dates_after_today`) now covers that case. This is why I treat the printed output as evidence and actually read it, rather than trusting that the code "looks right."

**A more "Pythonic" conflict check was turned down.** The shorter alternative, `itertools.combinations(tasks, 2)`, checks every pair. The version I kept sorts by start time and `break`s out early, which is faster and still readable with one comment. See 2b.

**A Streamlit API that was being phased out was removed.** The polished UI first used `use_container_width=True`, which Streamlit 1.54 marks as deprecated. Its replacement (`width="stretch"`) needs a newer Streamlit than `requirements.txt` allows, so the argument was simply dropped rather than raising the version requirement.

Verification was always one of three things: a pytest test, the `main.py` output, or driving `app.py` headlessly with `streamlit.testing.v1.AppTest` (add a pet, add overlapping tasks, check that the warning appears, click Done, check that tomorrow's copy exists).

---

## 4. Testing and Verification

**a. What you tested**

I tested five areas: task and pet basics plus input validation, sorting, filtering, recurrence, conflict detection, and the budget-limited daily plan (31 tests in all, listed in the README).

The most valuable tests were the **edge cases at boundaries**:

- *Back-to-back tasks*: a walk from 08:00 to 08:30 followed by a feeding at 08:30 must **not** count as a conflict. This test pins down that the overlap check uses `>=` and not `>`.
- *Sorting across days*: this test came from a bug I actually hit in the demo. Tomorrow's recurring 07:30 walk was sorting ahead of today's 18:00 task, because the sort only looked at the time. Fixing the key to `(due_date, time)` and adding this test keeps it from coming back.
- *Recurrence creates an independent copy*: if the "next" task shared state with the original, completing one would affect the other.

These matter because the scheduler's job is to be trusted. If the owner sees a false conflict warning, or a missing medication, they'll stop using the app.

**b. Confidence**

Fairly confident (4/5). All 31 tests pass, and each scheduling rule has a happy-path test and at least one edge case. Next I would test:

- Tasks that run past midnight (a 23:30 task lasting 60 minutes). Right now the end time just goes past 24:00 and isn't wrapped onto the next day.
- The Streamlit UI itself, using `streamlit.testing.v1.AppTest`, so the forms and session state are covered automatically instead of only by hand.

---

## 5. Reflection

**a. What went well**

The separation between logic and UI. `app.py` contains no scheduling rules at all. Every button calls a `Scheduler` or `Owner` method, so the same behavior is checked by the CLI demo, the pytest suite, and the web app. I'm also happy that conflict warnings use real time windows (start + duration) and say *which* pets clash, which is what an owner actually needs to know.

**b. What you would improve**

- **Save data between sessions.** Right now everything lives in `st.session_state` and disappears when the tab closes. I'd save the owner to JSON (or SQLite) and load it on startup.
- **A smarter planner.** I'd suggest a free time slot when tasks conflict, instead of only warning, and possibly let the owner pin "must do" tasks so the planner never skips them.
- **Editing and deleting tasks in the UI.** `Pet.remove_task()` exists, but the UI doesn't expose it yet.
- **Midnight-crossing tasks.** Handle a task that starts at 23:30 and runs past midnight properly.

**c. Key takeaway**

Being the "lead architect" means owning the **design and the verification**, not the typing. The AI can write a whole class in seconds, but it doesn't know that tomorrow's walk shouldn't sort ahead of today's breakfast unless something shows it. The UML, the small focused methods, and the tests are what let me check AI-written code quickly and confidently. Clear structure up front (a Scheduler that reads through the Owner instead of keeping its own copy of tasks) made every later AI change smaller and easier to review.

On sessions: I ran this as **one continuous agent session** rather than a separate chat per phase, with a commit at the end of each phase as the boundary. That kept context (like the `pet_name` design change) available in later phases. The cost is that a single long session can carry early assumptions forward without anyone questioning them. Starting a fresh session for testing would have been a useful "second opinion" on the code.
