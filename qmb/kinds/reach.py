"""reach: the quivers reached from a quiver of a family below its barrier, and how many are as low as it.

    family, values | range, method, prune_forks

`method` is "search" (this package, the default), "np_barrier" (the C program, after `make build`; it
holds entries in 32 bits, so a task whose barrier is 2^31 or more ends "unsupported"), "np_qa_core" (the
program of note 20, family Qa) or "review17" (the second enumerator of note 17, in Python integers,
family P+, without pruning).  Each method is one function below, named in METHODS.

A task carries `bound`, the barrier of the family's closed form, and `prune_forks`.  Predicted: for G_k
that the quiver is alone below its barrier; for the others what claims/expected.json holds.  `parse_plain`
reads a line of review17.py and `parse_core` a row of np_qa_core.py, here and when tools/expected.py reads
the stored logs.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from .. import search
from ..backends import binary, np_barrier, program, require, scratch
from ..quiver import height, vertices
from .base import FamilyTask, Kind, Result, Table, TaskError, choice, family_tasks, known, start


class ReachTask(FamilyTask):
    method: str  # a key of METHODS
    prune_forks: bool
    bound: int  # the barrier of the family's closed form


def _search(task: ReachTask, quiver: tuple[int, ...]) -> Result:
    prune = task["prune_forks"]
    region = search.below(quiver, task["bound"], prune_forks=prune)
    return {
        "value": {"quivers": region.quivers, "low": region.low},
        "method": "flood below the barrier" + (", forks not expanded" if prune else ", no pruning"),
        "opposite_reached": region.has_opposite,
        "forks_met": region.forks,
    }


def _np_barrier(task: ReachTask, quiver: tuple[int, ...]) -> Result:
    bound = task["bound"]
    if task["prune_forks"]:
        raise TaskError("np_barrier counts forks among the quivers reached; use search or np_qa_core")
    result = np_barrier(quiver, low=height(quiver), cap=bound - 1, n=vertices(quiver), barrier=bound)
    if result.status not in ("cap", "closed"):
        return {"value": None, "method": "np_barrier.c", "search_status": result.status}
    return {
        "value": {"quivers": result.popped, "low": result.plateau},
        "method": "np_barrier.c, cap one below the barrier, no pruning",
        "search_status": result.status,
    }


@dataclass(frozen=True)
class Plain:
    """One line of `review17.py plain` for P+_t: what it reached below the barrier it computed."""

    t: int
    barrier: int
    quivers: int
    low: int
    leading_above: int  # mutations that lead to the barrier or above


_PLAIN = re.compile(
    r"P\+_t t=(\d+) w=\d+ H=(\d+): (\d+) quivers reached below H, (\d+) of height <= w, "
    r"(\d+) mutations lead to height >= H"
)


def parse_plain(line: str) -> Plain | None:
    """The line of `review17.py plain` for one t; None for any other line."""
    match = _PLAIN.match(line)
    return None if match is None else Plain(*(int(number) for number in match.groups()))


def _review17(task: ReachTask, quiver: tuple[int, ...]) -> Result:
    value, bound = task["value"], task["bound"]
    with scratch(task["id"]) as work:
        output = program(
            "../verify/review17.py", "plain", "--tmin", value, "--tmax", value, "--family", "plus",
            "--workers", 1, cwd=work,
        )  # fmt: skip
    row = next((row for row in map(parse_plain, output.splitlines()) if row is not None), None)
    found = row is not None and row.t == value and row.barrier == bound
    return {
        "value": {"quivers": row.quivers, "low": row.low} if row is not None and found else None,
        "method": "verify/review17.py plain, no pruning",
        "mutations_leading_above": row.leading_above if row is not None else None,
    }


@dataclass(frozen=True)
class Core:
    """One row of `np_qa_core.py family`: its search from Q_a below the barrier it computed."""

    status: str  # "closed" when the search ended within its caps
    barrier: int
    members: int  # quivers reached
    low: int  # of these, of height at most that of the start
    low_forks: int  # forks of height at most that of the start
    stored: int
    passed_through: int
    ok: bool  # what the program's own checks of the row say

    def region(self, bound: int) -> dict[str, int] | None:
        """What a task reports as reached below `bound`; None unless the search closed below that very
        barrier without a fork as low as the start."""
        closed = self.status == "closed" and self.barrier == bound and self.low_forks == 0
        return {"quivers": self.members, "low": self.low} if closed else None


def core_row(row: Mapping[str, Any]) -> Core:
    """A row of `np_qa_core.py family`, read from its JSON object."""
    return Core(
        status=row["status"],
        barrier=row["H"],
        members=row["members"],
        low=row["members_of_height_le_w"],
        low_forks=row["forks_of_height_le_w"],
        stored=row["stored"],
        passed_through=row["passed_through"],
        ok=bool(row.get("ok")),
    )


def parse_core(line: str) -> Core:
    """A row of `np_qa_core.py family`, read from the line the program wrote."""
    return core_row(json.loads(line))


def _np_qa_core(task: ReachTask, quiver: tuple[int, ...]) -> Result:
    value, bound = task["value"], task["bound"]
    require("numpy")
    mode = "chain" if task["prune_forks"] else "chain-nofork"
    with scratch(task["id"]) as work:
        # np_qa_core.py keeps the summary of every search under ~/.cache/qmb-np/ and prints a kept one
        # instead of searching again.  The task gives it the empty scratch directory as its home, so that
        # what it reports was computed by this process and nothing outside the scratch directory is read
        # or written.
        program(
            "np_qa_core.py", "family", "--amin", value, "--amax", value, "--workers", 1, "--mode", mode,
            "--out", "family.jsonl", cwd=work,
            env={"NP_QA_CORE_BIN": str(binary("np_qa_core")), "HOME": str(work)},
        )  # fmt: skip
        core = parse_core((work / "family.jsonl").read_text().splitlines()[0])
    return {
        "value": core.region(bound),
        "method": f"np_qa_core.py family, mode {mode}",
        "search_status": core.status,
        "stored": core.stored,
        "passed_through": core.passed_through,
    }


METHODS: dict[str, Callable[[ReachTask, tuple[int, ...]], Result]] = {
    "search": _search,
    "np_barrier": _np_barrier,
    "np_qa_core": _np_qa_core,
    "review17": _review17,
}


def expand(table: Table, where: str) -> Iterator[ReachTask]:
    known(table, where, "family", "values", "range", "method", "prune_forks")
    method = choice(table, "method", where, tuple(METHODS))
    prune = bool(table.get("prune_forks", False))
    for chosen, value, member in family_tasks(table, where):
        if method == "np_qa_core" and chosen.key != "Qa":
            raise TaskError(f"{where}: np_qa_core computes the family Qa only")
        if method == "review17" and (chosen.key != "P+" or prune):
            raise TaskError(f"{where}: review17 computes the family P+ only, without pruning")
        suffix = ("/forks-pruned" if prune else "") + ("" if method == "search" else f"@{method}")
        yield {
            **member,
            "id": f"reach/{chosen.key}/{chosen.parameter}={value}{suffix}",
            "group": f"reach {chosen.name}",
            "method": method,
            "prune_forks": prune,
            "bound": chosen.barrier(value),
            # Theorem 5.1 (1): every mutation of G_k is as high as the barrier, so G_k is alone below it
            "predicted": {"quivers": 1, "low": 1} if chosen.key == "G" else None,
        }


def run(task: ReachTask) -> Result:
    _, _, quiver = start(task)
    return METHODS[task["method"]](task, quiver)


KIND = Kind(expand, run)
