"""barrier: the least height joining a quiver of a family to its opposite.

    family, values | range, method

`method` is "search" (this package, the default) or "np_barrier" (the C program, after `make build`; it
holds entries in 32 bits, so a task whose barrier is 2^31 or more ends "unsupported").

Predicted: the barrier of the family's closed form.
"""

from __future__ import annotations

from collections.abc import Iterator

from .. import search
from ..backends import np_barrier
from ..quiver import height, isomorphic, opposite, vertices
from .base import FamilyTask, Kind, Result, Table, choice, family_tasks, known, start

METHODS = ("search", "np_barrier")


class BarrierTask(FamilyTask):
    method: str  # one of METHODS


def expand(table: Table, where: str) -> Iterator[BarrierTask]:
    known(table, where, "family", "values", "range", "method")
    method = choice(table, "method", where, METHODS)
    for chosen, value, member in family_tasks(table, where):
        suffix = "" if method == "search" else f"@{method}"
        yield {
            **member,
            "id": f"barrier/{chosen.key}/{chosen.parameter}={value}{suffix}",
            "group": f"barrier {chosen.name}",
            "method": method,
            "predicted": chosen.barrier(value),
        }


def run(task: BarrierTask) -> Result:
    chosen, value, quiver = start(task)
    if task["method"] == "search":
        found = search.barrier(quiver)
        return {
            "value": found.level,
            "method": "least-height-first search, no pruning",
            "popped": found.popped,
        }
    # the search stops where it finds the join; the cap only bounds it
    bound = chosen.barrier(value)
    result = np_barrier(quiver, low=height(quiver), cap=4 * bound + 1024, n=vertices(quiver), barrier=bound)
    joined = result.target is not None and isomorphic(result.target, opposite(quiver))
    return {
        "value": result.iso if joined else None,
        "method": "np_barrier.c, no pruning",
        "popped": result.popped,
        "first_other_low_quiver_is_the_opposite": joined,
        "search_status": result.status,
    }


KIND = Kind(expand, run)
