"""conj55: Conjecture 5.5 at one height, by the enumeration of this package.

    heights

Predicted: the counts of the article's table, which data/claims/expected.json holds.
"""

from __future__ import annotations

from collections.abc import Iterator

from ..conj55 import split
from .base import Common, Kind, Result, Table, TaskError, known


class Conj55Task(Common):
    height: int
    article: str


def expand(table: Table, where: str) -> Iterator[Conj55Task]:
    known(table, where, "heights")
    heights = table.get("heights")
    if (
        not isinstance(heights, list)
        or not heights
        or not all(type(h) is int and 1 <= h <= 8 for h in heights)
    ):
        raise TaskError(f"{where}: heights must be a list of whole numbers from 1 to 8")
    for h in heights:
        yield {
            "id": f"conj55/h={h}",
            "group": "conj55",
            "cost": h**3,
            "height": h,
            "article": "Proposition 12.1",
            "predicted": None,
        }


def run(task: Conj55Task) -> Result:
    quivers, reaching = split(task["height"])
    return {"value": {"quivers": quivers, "reach_acyclic": reaching}, "method": "enumeration and flood"}


KIND = Kind(expand, run)
