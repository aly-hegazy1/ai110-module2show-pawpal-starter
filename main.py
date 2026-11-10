"""CLI demo for PawPal+: builds an owner, pets, and tasks, then prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(title: str, tasks: list[Task]) -> None:
    """Print a list of tasks as a readable block."""
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (nothing scheduled)")
    for task in tasks:
        print(f"  {task}")


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    mochi.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    luna.add_task(Task("Breakfast", "08:00", 10, "high", "daily"))
    luna.add_task(Task("Flea medication", "12:00", 5, "high", "weekly"))

    scheduler = Scheduler(owner)
    print_schedule(f"Today's Schedule for {owner.name}", scheduler.get_tasks_for_date())


if __name__ == "__main__":
    main()
