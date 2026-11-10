"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
FREQUENCIES = ("once", "daily", "weekly")


def time_to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def minutes_to_time(total: int) -> str:
    """Convert minutes after midnight back to an "HH:MM" string."""
    return f"{total // 60:02d}:{total % 60:02d}"


@dataclass
class Task:
    """A single pet care activity scheduled at a time of day."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def __post_init__(self) -> None:
        """Validate fields and normalize the time to zero-padded "HH:MM"."""
        try:
            hours, minutes = (int(part) for part in self.time.split(":"))
        except ValueError:
            raise ValueError(f"Time must look like HH:MM, got {self.time!r}.") from None
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError(f"Time {self.time!r} is not a valid time of day.")
        self.time = f"{hours:02d}:{minutes:02d}"
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"Priority must be one of {list(PRIORITY_RANK)}.")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"Frequency must be one of {list(FREQUENCIES)}.")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes.")

    @property
    def start_minutes(self) -> int:
        """Start time as minutes after midnight."""
        return time_to_minutes(self.time)

    @property
    def end_minutes(self) -> int:
        """End time (start + duration) as minutes after midnight."""
        return self.start_minutes + self.duration_minutes

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy of this task for its next due date, or None if it doesn't repeat."""
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        return replace(self, due_date=self.due_date + step, completed=False)

    def __str__(self) -> str:
        """Return a one-line, human-readable summary of the task."""
        status = "✓" if self.completed else " "
        who = f"{self.pet_name}: " if self.pet_name else ""
        when = "" if self.due_date == date.today() else f"{self.due_date.isoformat()} "
        return (
            f"[{status}] {when}{self.time}  {who}{self.description} "
            f"({self.duration_minutes} min, {self.priority}, {self.frequency})"
        )


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if it is present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str, available_minutes: int = 120):
        """Create an owner with a daily time budget for pet care."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet; raise ValueError if the name is blank or already taken."""
        if not pet.name.strip():
            raise ValueError("Pet name can't be empty.")
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name}.")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name (case-insensitive), or return None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class DailyPlan:
    """The result of planning one day: which tasks fit the time budget and why."""

    day: date
    budget_minutes: int
    scheduled: list[Task] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    @property
    def minutes_used(self) -> int:
        """Total minutes of the scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled)

    def explain(self) -> list[str]:
        """Return human-readable lines explaining what was scheduled and skipped."""
        lines = [
            f"Planned {len(self.scheduled)} task(s) using {self.minutes_used} of "
            f"{self.budget_minutes} available minutes."
        ]
        for t in self.scheduled:
            lines.append(f"  ✔ {t.time} {t.pet_name}: {t.description} — {t.priority} priority")
        for t in self.skipped:
            lines.append(
                f"  ✘ {t.pet_name}: {t.description} skipped — needs {t.duration_minutes} min, "
                f"not enough time left after higher-priority tasks"
            )
        return lines


class Scheduler:
    """The 'brain' that retrieves and organizes tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that reads pets and tasks through an owner."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    # ----- sorting & filtering -------------------------------------------

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks in chronological order by due date, then "HH:MM" time (stable for ties)."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, t.start_minutes))

    def sort_by_priority(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered high → low priority, breaking ties by time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.start_minutes))

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        tasks: list[Task] | None = None,
    ) -> list[Task]:
        """Return tasks matching a pet name and/or completion status; None means 'any'."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return [
            t
            for t in tasks
            if (pet_name is None or t.pet_name.lower() == pet_name.lower())
            and (completed is None or t.completed == completed)
        ]

    def get_tasks_for_date(self, day: date | None = None) -> list[Task]:
        """Return tasks due on the given day (default: today), in time order."""
        day = day or date.today()
        return self.sort_by_time([t for t in self.get_all_tasks() if t.due_date == day])

    # ----- recurring tasks ------------------------------------------------

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task; for daily/weekly tasks, add and return the next occurrence.

        Completing an already-completed task does nothing and returns None, so a
        double-click can't create duplicate future tasks.
        """
        if task.completed:
            return None
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    # ----- conflict detection -----------------------------------------------

    def detect_conflicts(self, day: date | None = None) -> list[str]:
        """Return a warning for each pair of unfinished tasks whose time windows overlap on a day."""
        tasks = [t for t in self.get_tasks_for_date(day) if not t.completed]
        warnings: list[str] = []
        for i, first in enumerate(tasks):
            for second in tasks[i + 1 :]:
                if second.start_minutes >= first.end_minutes:
                    break  # sorted by start, so no later task can overlap `first`
                who = (
                    f"both for {first.pet_name}"
                    if first.pet_name == second.pet_name
                    else f"{first.pet_name} and {second.pet_name}"
                )
                warnings.append(
                    f"⚠ Conflict: '{first.description}' ({first.time}–"
                    f"{minutes_to_time(first.end_minutes)}) overlaps '{second.description}' "
                    f"({second.time}–{minutes_to_time(second.end_minutes)}), {who}."
                )
        return warnings

    # ----- daily plan ---------------------------------------------------------

    def generate_daily_plan(self, day: date | None = None) -> DailyPlan:
        """Pick unfinished tasks for a day by priority until the owner's time budget runs out."""
        day = day or date.today()
        plan = DailyPlan(day=day, budget_minutes=self.owner.available_minutes)
        remaining = self.owner.available_minutes
        pending = self.filter_tasks(completed=False, tasks=self.get_tasks_for_date(day))
        for task in self.sort_by_priority(pending):
            if task.duration_minutes <= remaining:
                plan.scheduled.append(task)
                remaining -= task.duration_minutes
            else:
                plan.skipped.append(task)
        plan.scheduled = self.sort_by_time(plan.scheduled)
        return plan
