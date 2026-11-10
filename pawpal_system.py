"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


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

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def __str__(self) -> str:
        """Return a one-line, human-readable summary of the task."""
        status = "✓" if self.completed else " "
        who = f"{self.pet_name}: " if self.pet_name else ""
        return (
            f"[{status}] {self.time}  {who}{self.description} "
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
        """Add a pet; raise ValueError if a pet with that name already exists."""
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


class Scheduler:
    """The 'brain' that retrieves and organizes tasks across an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that reads pets and tasks through an owner."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_tasks_for_date(self, day: date | None = None) -> list[Task]:
        """Return tasks due on the given day (default: today), in time order."""
        day = day or date.today()
        return sorted(
            (t for t in self.get_all_tasks() if t.due_date == day),
            key=lambda t: t.time,
        )
