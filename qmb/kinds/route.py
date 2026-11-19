"""route: the route of a family's theorem from a quiver to its opposite.

    family, values | range, method

`method` is "replay" (the default: the word of the theorem, mutation by mutation) or "shortest" (a
breadth-first search at the barrier, for the number of mutations and the top only).

Predicted: the number of mutations and the top of the route and, replayed, where it is at the top and
that it ends at the opposite; for Q_a also what the article says about the fifth vertex.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .. import search
from ..families import replay
from .base import FamilyTask, Kind, Result, Table, TaskError, choice, family_tasks, known, start

METHODS = ("replay", "shortest")


class RouteTask(FamilyTask):
    method: str  # one of METHODS


def expand(table: Table, where: str) -> Iterator[RouteTask]:
    known(table, where, "family", "values", "range", "method")
    method = choice(table, "method", where, METHODS)
    for chosen, value, member in family_tasks(table, where):
        if chosen.word is None or chosen.route_mutations is None or chosen.route_at_top is None:
            raise TaskError(f"{where}: the article gives no route for {chosen.name}")
        if chosen.key == "R" and value % 2:
            raise TaskError(f"{where}: the route of Theorem 7.2 is stated for even b")
        predicted: dict[str, Any] = {"mutations": chosen.route_mutations(value), "top": chosen.barrier(value)}
        if method == "replay":
            predicted |= {"at_top": chosen.route_at_top(value), "ends_at_opposite": True}
            if chosen.key == "Qa":
                predicted |= {"mutations_at_x": 0, "entries_away_from_x_at_most_2a_plus_2": True}
        suffix = "" if method == "replay" else f"@{method}"
        yield {
            **member,
            "id": f"route/{chosen.key}/{chosen.parameter}={value}{suffix}",
            "group": f"route {chosen.name}",
            "method": method,
            "cost": member["cost"] if method == "replay" else 10 * member["cost"],
            "predicted": predicted,
        }


def run(task: RouteTask) -> Result:
    chosen, value, quiver = start(task)
    if task["method"] == "shortest":
        count, heights = search.shortest(quiver, chosen.barrier(value))
        return {
            "value": None if count is None else {"mutations": count, "top": max(heights)},
            "method": "breadth-first search at the barrier",
        }
    assert chosen.word is not None
    route = replay(quiver, chosen.word(value), fifth_vertex=chosen.key == "Qa")
    found: dict[str, Any] = {
        "mutations": route.mutations,
        "top": route.top,
        "at_top": route.at_top,
        "ends_at_opposite": route.ends_at_opposite,
        "first_heights": list(route.heights[:4]),
    }
    if chosen.key == "Qa":
        assert route.largest_away_from_x is not None
        found["mutations_at_x"] = route.mutations_at_x
        found["largest_entry_away_from_x"] = route.largest_away_from_x
        found["entries_away_from_x_at_most_2a_plus_2"] = route.largest_away_from_x <= 2 * value + 2
    return {"value": found, "method": f"the route of {chosen.article}, replayed by integer mutation"}


KIND = Kind(expand, run)
