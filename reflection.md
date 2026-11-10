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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

I tested five areas: task and pet basics plus input validation, sorting, filtering, recurrence, conflict detection, and the budget-limited daily plan (30 tests in all, listed in the README).

The most valuable tests were the **edge cases at boundaries**:

- *Back-to-back tasks*: a walk from 08:00 to 08:30 followed by a feeding at 08:30 must **not** count as a conflict. This test pins down that the overlap check uses `>=` and not `>`.
- *Sorting across days*: this test came from a bug I actually hit in the demo. Tomorrow's recurring 07:30 walk was sorting ahead of today's 18:00 task, because the sort only looked at the time. Fixing the key to `(due_date, time)` and adding this test keeps it from coming back.
- *Recurrence creates an independent copy*: if the "next" task shared state with the original, completing one would affect the other.

These matter because the scheduler's job is to be trusted. If the owner sees a false conflict warning, or a missing medication, they'll stop using the app.

**b. Confidence**

Fairly confident (4/5). All 30 tests pass, and each scheduling rule has a happy-path test and at least one edge case. Next I would test:

- Tasks that run past midnight (a 23:30 task lasting 60 minutes). Right now the end time just goes past 24:00 and isn't wrapped onto the next day.
- Completing the same recurring task twice. Right now that would create two "tomorrow" copies.
- The Streamlit UI itself, using `streamlit.testing.v1.AppTest`, so the forms and session state are covered automatically instead of only by hand.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
