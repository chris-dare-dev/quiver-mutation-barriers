"""quiver: the height of a quiver of a family and of each of its mutations.

    family, values | range

Predicted: the height the article states for the family.
"""

from __future__ import annotations

from collections.abc import Iterator

from ..quiver import height, mutate, vertices
from .base import FamilyTask, Kind, Result, Table, family_tasks, known, start


def expand(table: Table, where: str) -> Iterator[FamilyTask]:
    known(table, where, "family", "values", "range")
    for chosen, value, member in family_tasks(table, where):
        yield {
            **member,
            "id": f"quiver/{chosen.key}/{chosen.parameter}={value}",
            "group": f"quiver {chosen.name}",
            "predicted": {"height": chosen.height(value)},
        }


def run(task: FamilyTask) -> Result:
    _, _, quiver = start(task)
    return {
        "value": {
            "height": height(quiver),
            "mutation_heights": [height(mutate(quiver, k)) for k in range(vertices(quiver))],
        },
        "method": "integer mutation",
        "quiver": list(quiver),
    }


KIND = Kind(expand, run)
