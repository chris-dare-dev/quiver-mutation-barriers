"""conj55_program: Conjecture 5.5 for all heights up to N, by the original program n4_conj55.py.

    N, workers

Predicted: the table and the totals the program printed for the article, which claims/expected.json holds;
`parse_summary` reads them from the program's output, here and when tools/expected.py reads the stored log.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from typing import Any, NotRequired, TypedDict

from ..backends import program, require, scratch
from .base import Kind, Result, Table, TaskError, known


# the keys of a task are those of its table, and N is one of them
class ProgramTask(TypedDict):
    id: str
    group: str
    cost: float
    N: int
    workers: int
    article: str
    predicted: Any


def expand(table: Table, where: str) -> Iterator[ProgramTask]:
    known(table, where, "N", "workers")
    bound, workers = table.get("N"), table.get("workers", 4)
    if type(bound) is not int or not 2 <= bound <= 18 or type(workers) is not int or workers < 1:
        raise TaskError(f"{where}: N must be a whole number from 2 to 18 and workers at least 1")
    yield {
        "id": f"conj55_program/N={bound}",
        "group": "conj55",
        "cost": bound**3,
        "N": bound,
        "workers": workers,
        "article": "Proposition 12.1",
        "predicted": None,
    }


class Height(TypedDict):
    """One row of the table: the quivers of one height."""

    quivers: int
    reach_acyclic: int
    fail: int
    counterexamples: int
    undetermined: int


# the keys are the program's own, and one of them is a word of Python
Totals = TypedDict("Totals", {"quivers": int, "pass": int, "fail": int, "counterexamples": int, "left": int})


class Summary(TypedDict):
    """What `n4_conj55.py summary` printed; a part is absent when its line is."""

    heights: dict[str, Height]
    totals: NotRequired[Totals]
    failing_by_certificate: NotRequired[dict[str, int]]
    largest_search_is_h3_h2_5: NotRequired[bool]


def parse_summary(output: str) -> Summary:
    """The per-height table and the totals printed by `n4_conj55.py summary`."""
    heights: dict[str, Height] = {}
    found: Summary = {"heights": heights}
    for line in output.splitlines():
        cells = [cell.strip().replace(",", "") for cell in line.strip("|").split("|")]
        if line.startswith("|") and cells[0].isdigit():
            heights[cells[0]] = {
                "quivers": int(cells[1]),
                "reach_acyclic": int(cells[5]),
                "fail": int(cells[6]),
                "counterexamples": int(cells[9]),
                "undetermined": int(cells[10]),
            }
        elif line.startswith("totals: "):
            totals = ast.literal_eval(line.removeprefix("totals: "))
            found["totals"] = {
                "quivers": totals["quivers"],
                "pass": totals["pass"],
                "fail": totals["fail"],
                "counterexamples": totals["counterexamples"],
                "left": totals["left"],
            }
        elif line.startswith("failing quivers by certificate"):
            found["failing_by_certificate"] = ast.literal_eval(line.partition(": ")[2])
        elif line.startswith("resolve, largest cor52 bound K per height"):
            bounds = ast.literal_eval(line.partition(": ")[2].partition(" (second")[0])
            found["largest_search_is_h3_h2_5"] = all(
                k == (h**3 + h * h + 5, h**3 + h * h + 5) for h, k in bounds.items()
            )
    return found


def run(task: ProgramTask) -> Result:
    require("numpy")
    bound = task["N"]
    with scratch(task["id"]) as work:
        program(
            "n4_conj55.py",
            "run",
            "--H",
            bound,
            "--N",
            bound,
            "--store-h",
            bound,
            "--out",
            "run.json.gz",
            cwd=work,
        )
        program(
            "n4_conj55.py", "resolve", "--inp", "run.json.gz", "--out", "resolve.json.gz", "--H", bound,
            "--every", 20000, "--workers", task["workers"], cwd=work,
        )  # fmt: skip
        summary = program(
            "n4_conj55.py", "summary", "--run", "run.json.gz", "--resolve", "resolve.json.gz", cwd=work
        )
    return {"value": parse_summary(summary), "method": "n4_conj55.py run, resolve, summary"}


KIND = Kind(expand, run)
