"""What the kinds share: the types of a task and of its result, and the reading of a `[[tasks]]` table.

A kind declares the keys of its tasks once, as a TypedDict that its expansion writes and its computation
reads.  `Common` is what every kind writes; `tasks.expand_batch` then adds `kind`, `set` and `evidence`,
fills `predicted` from data/claims/expected.json where the kind left it open, and marks a negative control.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, Generic, TypedDict, TypeVar

from ..families import Family, family

Table = dict[str, Any]  # a `[[tasks]]` table of a batch file
Task = dict[str, Any]  # a task of any kind, as the runner hands it over
Result = dict[str, Any]


class Common(TypedDict):
    """The keys of every task."""

    id: str
    group: str
    cost: float
    predicted: Any


class Member(TypedDict):
    """The keys that place a task on one quiver of a family, whatever its kind."""

    family: str
    value: int
    cost: float
    article: str


class FamilyTask(Member, Common):
    """A task on one quiver of a family."""


P = TypeVar("P")


class TaskError(ValueError):
    """A batch description or a task that cannot be used."""


@dataclass(frozen=True)
class Kind(Generic[P]):
    """A kind of task: how a `[[tasks]]` table becomes tasks, and how one of them is computed.  `P` is
    the type of its tasks."""

    expand: Callable[[Table, str], Iterator[P]]
    run: Callable[[P], Result]


def values(table: Table, where: str) -> list[int]:
    if ("values" in table) == ("range" in table):
        raise TaskError(f"{where} needs either values or range")
    if "values" in table:
        found = table["values"]
    else:
        bounds = table["range"]
        if not (isinstance(bounds, list) and len(bounds) == 2 and all(isinstance(b, int) for b in bounds)):
            raise TaskError(f"{where}: range must be [first, last]")
        found = list(range(bounds[0], bounds[1] + 1))
    if not isinstance(found, list) or not found or not all(type(v) is int for v in found):
        raise TaskError(f"{where}: values must be a list of whole numbers")
    return found


def known(table: Table, where: str, *keys: str) -> None:
    unknown = set(table) - {"kind", "control", *keys}
    if unknown:
        raise TaskError(f"{where}: unknown key {sorted(unknown)[0]!r}")


def choice(table: Table, key: str, where: str, choices: tuple[str, ...]) -> str:
    chosen = table.get(key, choices[0])
    if chosen not in choices:
        raise TaskError(f"{where}: {key} must be one of {', '.join(choices)}")
    return str(chosen)


def family_tasks(table: Table, where: str) -> Iterator[tuple[Family, int, Member]]:
    """The family of a table and each of its values, with the keys every task on a family has."""
    chosen = family(str(table.get("family", "")))
    for value in values(table, where):
        chosen.check(value)
        yield chosen, value, {"family": chosen.key, "value": value, "cost": value, "article": chosen.article}


def start(task: Member) -> tuple[Family, int, tuple[int, ...]]:
    """The family of a task on a family, its value, and the quiver it starts from."""
    chosen = family(task["family"])
    return chosen, task["value"], chosen.quiver(task["value"])
