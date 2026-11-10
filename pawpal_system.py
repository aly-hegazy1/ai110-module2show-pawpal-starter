"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field


@dataclass
class Task:
    description: str
    time: str  # "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int = 120):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        pass

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        pass

    def generate_daily_plan(self) -> list[Task]:
        pass
