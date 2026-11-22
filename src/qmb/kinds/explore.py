"""explore: what the searches of this package find for a quiver that is not one of the article's.

    quiver, name, cap, budget, predicted

`quiver` is the upper triangle of the exchange matrix, row by row: (b01, b02, b03, b12, b13, b23) on four
vertices, with b_ij > 0 for b_ij arrows i -> j.  `name` ends the id of the task; without it the entries do.

The mutation class of most quivers is infinite, and most quivers are not joined to their opposite at any
height a search reaches, so the search is stopped: at the height `cap` if there is one, and after
`budget` quivers (BUDGET unless the table says otherwise).  Both are counts, so the answer does not depend
on the machine or its load.

The value is a table.  It always has `height`.  Where the opposite was reached it has `barrier`, the
least height at which it is; `quivers` and `low`, the quivers reached below the barrier and how many of
them are as low as the start; and `mutations`, the least number of mutations of a route that stays at or
below the barrier (absent if the budget ended that search).  Where the search was stopped first it has
`no_route_up_to` instead: the height that was searched whole, at or below which no route to the opposite
stays.  Where the whole mutation class was seen and the opposite is not in it, it has `whole_class`, the
number of quivers of the class up to relabelling.

Predicted: nothing, unless the table gives `predicted`, a table with some of the keys of the value.
Without it the task ends "ok" whenever the search ends: there is nothing to agree with.

`survey` is the computation, and `lines` says its result in words (python3 -m qmb explore).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .. import search
from ..quiver import height, mutate, vertices
from .base import Common, Kind, Result, Table, TaskError, known

BUDGET = 100_000  # quivers a search takes before it is stopped
VALUE_KEYS = ("height", "barrier", "quivers", "low", "mutations", "no_route_up_to", "whole_class")


class ExploreTask(Common):
    quiver: list[int]
    cap: int | None
    budget: int


def check(quiver: object, cap: object, budget: object, where: str) -> tuple[int, ...]:
    """The quiver as a tuple, once it and the two stops are known to be usable."""
    if not isinstance(quiver, list | tuple) or not quiver or not all(type(entry) is int for entry in quiver):
        raise TaskError(f"{where}: quiver must be a list of whole numbers, the entries b_ij for i < j")
    try:
        vertices(quiver)
    except ValueError as problem:
        raise TaskError(f"{where}: {problem} (3 vertices have 3 entries, 4 have 6, 5 have 10)") from None
    if cap is not None and (type(cap) is not int or cap < height(quiver)):
        low = height(quiver)
        raise TaskError(f"{where}: cap must be a whole number, at least the height {low} of the quiver")
    if type(budget) is not int or budget < 1:
        raise TaskError(f"{where}: budget must be a whole number, at least 1")
    return tuple(quiver)


def expand(table: Table, where: str) -> Iterator[ExploreTask]:
    known(table, where, "quiver", "name", "cap", "budget", "predicted")
    cap, budget = table.get("cap"), table.get("budget", BUDGET)
    quiver = check(table.get("quiver"), cap, budget, where)
    name = table.get("name", ",".join(map(str, quiver)))
    if not isinstance(name, str) or not name or any(letter.isspace() for letter in name):
        raise TaskError(f"{where}: name must be a word, without spaces")
    predicted = table.get("predicted")
    if predicted is not None and (not isinstance(predicted, dict) or not set(predicted) <= set(VALUE_KEYS)):
        raise TaskError(f"{where}: predicted must be a table with keys among {', '.join(VALUE_KEYS)}")
    yield {
        "id": f"explore/{name}",
        "group": "explore",
        "cost": 1,
        "predicted": predicted,
        "quiver": list(quiver),
        "cap": cap,
        "budget": budget,
    }


def survey(quiver: tuple[int, ...], *, cap: int | None = None, budget: int = BUDGET) -> Result:
    """The height of a quiver, the height at which it is joined to its opposite, and what lies below."""
    found = search.barrier(quiver, cap=cap, budget=budget)
    value: dict[str, Any] = {"height": height(quiver)}
    stopped = None
    if found.level is not None:
        region = search.below(quiver, found.level)
        value |= {"barrier": found.level, "quivers": region.quivers, "low": region.low}
        mutations, _ = search.shortest(quiver, found.level, budget=budget)
        if mutations is not None:
            value["mutations"] = mutations
    elif found.cleared is None:
        value["whole_class"] = found.popped
    else:
        value["no_route_up_to"] = found.cleared
        stopped = "cap" if found.cleared == cap else "budget"
    return {
        "value": value,
        "method": "least-height-first search, no pruning",
        "quiver": list(quiver),
        "vertices": vertices(quiver),
        "mutation_heights": [height(mutate(quiver, k)) for k in range(vertices(quiver))],
        "popped": found.popped,
        "stopped": stopped,
        "cap": cap,
        "budget": budget,
    }


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def lines(result: Result) -> list[str]:
    """What a survey found, in sentences."""
    value, quiver = result["value"], tuple(result["quiver"])
    level, low, budget = value.get("barrier"), value["height"], result["budget"]
    said = [
        f"quiver    {quiver} on {result['vertices']} vertices, of height {low}",
        f"mutation  at each vertex in turn gives heights {', '.join(map(str, result['mutation_heights']))}",
    ]
    if level is not None:
        below, as_low, moves = _count(value["quivers"], "quiver"), value["low"], value.get("mutations")
        said += [
            f"barrier   {level}: the opposite is reached through heights at most {level}, and not below",
            f"below it  {below} up to relabelling, the start included; {as_low} of height at most {low}",
        ]
        if moves is None:
            said.append(f"route     not counted: the search for a shortest one passed {budget} quivers")
        elif moves == 0:
            said.append("route     none needed: the opposite is the quiver itself, its vertices relabelled")
        else:
            said.append(f"route     {_count(moves, 'mutation')} at the least, staying at or below {level}")
    elif "whole_class" in value:
        size = _count(value["whole_class"], "quiver")
        said += [
            f"barrier   none: the mutation class has {size} up to relabelling,",
            "          and the opposite is not one of them",
        ]
    else:
        bound = value["no_route_up_to"]
        why = (
            f"the cap of {result['cap']} left quivers out"
            if result["stopped"] == "cap"
            else f"the search was stopped at its budget of {budget} quivers"
        )
        said += [
            f"barrier   not found: no route to the opposite stays at or below height {bound}",
            f"          ({why}; a higher route is not excluded)",
        ]
    said.append(f"searched  {_count(result['popped'], 'quiver')}, taken in order of height")
    return said


def run(task: ExploreTask) -> Result:
    quiver = check(task["quiver"], task["cap"], task["budget"], "task")
    return survey(quiver, cap=task["cap"], budget=task["budget"])


KIND = Kind(expand, run)
