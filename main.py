"""CLI demo for PawPal+: exercises sorting, filtering, recurrence, conflicts, and planning."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a list of tasks as a readable block."""
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (nothing scheduled)")
    for task in tasks:
        print(f"  {task}")


def main() -> None:
    owner = Owner("Jordan", available_minutes=60)
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of time order to show sorting.
    mochi.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    luna.add_task(Task("Flea medication", "12:00", 5, "high", "weekly"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "07:45", 10, "high", "daily"))  # overlaps the walk
    mochi.add_task(Task("Puzzle toy", "15:00", 20, "low"))
    luna.add_task(Task("Brushing", "18:15", 15, "low", "weekly"))  # overlaps evening walk

    scheduler = Scheduler(owner)

    print_tasks(f"Today's Schedule for {owner.name} (sorted by time)", scheduler.get_tasks_for_date())

    print("\nConflict check")
    print("--------------")
    for warning in scheduler.detect_conflicts() or ["No conflicts found."]:
        print(f"  {warning}")

    print_tasks("Only Mochi's tasks (filtered, in the order they were added)", scheduler.filter_tasks(pet_name="Mochi"))

    morning_walk = next(t for t in mochi.tasks if t.description == "Morning walk")
    next_walk = scheduler.mark_task_complete(morning_walk)
    print(f"\nMarked '{morning_walk.description}' complete → next one added for {next_walk.due_date}")

    print_tasks("Still to do (incomplete, sorted)", scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))

    plan = scheduler.generate_daily_plan()
    print("\nToday's plan (priority first, within time budget)")
    print("-------------------------------------------------")
    for line in plan.explain():
        print(f"  {line}")


if __name__ == "__main__":
    main()
