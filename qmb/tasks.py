"""The task kinds: how a `[[tasks]]` table of a batch file becomes tasks, and how one task is computed.

A task is one computation with one answer.  Where the article states the answer, the task carries it as
`predicted`, and where a stored result carries the original number, the task names it as `evidence`.  Both
come from two places: the closed forms of `families`, and `claims/expected.json`, which lists the values
typed from the article and those read from the stored results (tools/expected.py writes and checks it).

Kinds and the keys of their `[[tasks]]` table:

    quiver        family, values | range            height of the quiver and of each of its mutations
    barrier       family, values | range, method    least height joining the quiver to its opposite
    reach         family, values | range, method,   quivers reached below the barrier, and how many of
                  prune_forks                       them are as low as the start
    route         family, values | range, method    the route of the family's theorem, replayed
    certificate   names, audit_tmax                 the verdict of a certificate program
    conj55        heights                           Conjecture 5.5 at one height, by enumeration
    conj55_program  N, workers                      the original program for all heights up to N
    census, core, tube   stages, procs              one stage of Sections 8 and 13, by its own program
    synthetic     items                             no mathematics: sleeps, holds memory or fails

`method` is "search" (this package, the default), "np_barrier" (the C program, after `make build`; it holds
entries in 32 bits, so a task whose barrier is 2^31 or more ends "unsupported"), or for `reach` also
"np_qa_core" (the program of note 20); for `route` it is "replay" (the default) or
"shortest".  A table with `control = { predicted = ... }` makes negative controls: the same tasks under
other ids, with a predicted value that is wrong on purpose.

A computed value agrees with a predicted one when they are equal, or, when both are tables, when the
computed table has every key of the predicted one with the same value.
"""

from __future__ import annotations

import ast
import json
import os
import re
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import conj55, search
from .backends import (
    EXPERIMENTS,
    INT_MAX,
    REPOSITORY,
    BackendError,
    binary,
    np_barrier,
    program,
    require,
    scratch,
)
from .families import Family, family, replay
from .quiver import height, isomorphic, mutate, opposite, vertices

Task = dict[str, Any]
Result = dict[str, Any]

EXPECTED = REPOSITORY / "claims" / "expected.json"


class TaskError(ValueError):
    """A batch description or a task that cannot be used."""


class Unsupported(Exception):
    """The method of a task cannot compute it; the message says why.  The task ends "unsupported"."""


def _fits_np_barrier(bound: int) -> None:
    """np_barrier.c holds every entry in 32 bits and discards a quiver with a larger one, so it sees the
    whole region below a barrier, and the join at it, only when the barrier is below 2^31."""
    if bound > INT_MAX:
        raise Unsupported(
            f"np_barrier.c holds entries in 32 bits, and the barrier of this task, {bound}, is above 2^31 - 1"
        )


def load_expected(path: Path = EXPECTED) -> dict[str, dict[str, Any]]:
    """Predicted values and evidence by task id; empty if the file is absent."""
    if not path.exists():
        return {}
    tasks: dict[str, dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))["tasks"]
    return tasks


def agrees(value: Any, predicted: Any) -> bool | None:
    if predicted is None:
        return None
    if isinstance(predicted, dict) and isinstance(value, dict):
        return all(key in value and value[key] == wanted for key, wanted in predicted.items())
    return bool(value == predicted)


# ---------------------------------------------------------------------------------------------------
# expansion


def _values(table: Task, where: str) -> list[int]:
    if ("values" in table) == ("range" in table):
        raise TaskError(f"{where} needs either values or range")
    if "values" in table:
        values = table["values"]
    else:
        bounds = table["range"]
        if not (isinstance(bounds, list) and len(bounds) == 2 and all(isinstance(b, int) for b in bounds)):
            raise TaskError(f"{where}: range must be [first, last]")
        values = list(range(bounds[0], bounds[1] + 1))
    if not isinstance(values, list) or not values or not all(type(v) is int for v in values):
        raise TaskError(f"{where}: values must be a list of whole numbers")
    return values


def _known(table: Task, where: str, *keys: str) -> None:
    unknown = set(table) - {"kind", "control", *keys}
    if unknown:
        raise TaskError(f"{where}: unknown key {sorted(unknown)[0]!r}")


def _choice(table: Task, key: str, where: str, choices: tuple[str, ...]) -> str:
    chosen = table.get(key, choices[0])
    if chosen not in choices:
        raise TaskError(f"{where}: {key} must be one of {', '.join(choices)}")
    return str(chosen)


def _family_tasks(table: Task, where: str) -> Iterator[tuple[Family, int, Task]]:
    chosen = family(str(table.get("family", "")))
    for value in _values(table, where):
        chosen.check(value)
        yield chosen, value, {"family": chosen.key, "value": value, "cost": value, "article": chosen.article}


def _expand_quiver(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "family", "values", "range")
    for chosen, value, task in _family_tasks(table, where):
        yield task | {
            "id": f"quiver/{chosen.key}/{chosen.parameter}={value}",
            "group": f"quiver {chosen.name}",
            "predicted": {"height": chosen.height(value)},
        }


def _expand_barrier(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "family", "values", "range", "method")
    method = _choice(table, "method", where, ("search", "np_barrier"))
    for chosen, value, task in _family_tasks(table, where):
        suffix = "" if method == "search" else f"@{method}"
        yield task | {
            "id": f"barrier/{chosen.key}/{chosen.parameter}={value}{suffix}",
            "group": f"barrier {chosen.name}",
            "method": method,
            "predicted": chosen.barrier(value),
        }


def _expand_reach(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "family", "values", "range", "method", "prune_forks")
    method = _choice(table, "method", where, ("search", "np_barrier", "np_qa_core"))
    prune = bool(table.get("prune_forks", False))
    for chosen, value, task in _family_tasks(table, where):
        if method == "np_qa_core" and chosen.key != "Qa":
            raise TaskError(f"{where}: np_qa_core computes the family Qa only")
        suffix = ("/forks-pruned" if prune else "") + ("" if method == "search" else f"@{method}")
        yield task | {
            "id": f"reach/{chosen.key}/{chosen.parameter}={value}{suffix}",
            "group": f"reach {chosen.name}",
            "method": method,
            "prune_forks": prune,
            "bound": chosen.barrier(value),
            # Theorem 5.1 (1): every mutation of G_k is as high as the barrier, so G_k is alone below it
            "predicted": {"quivers": 1, "low": 1} if chosen.key == "G" else None,
        }


def _expand_route(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "family", "values", "range", "method")
    method = _choice(table, "method", where, ("replay", "shortest"))
    for chosen, value, task in _family_tasks(table, where):
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
        yield task | {
            "id": f"route/{chosen.key}/{chosen.parameter}={value}{suffix}",
            "group": f"route {chosen.name}",
            "method": method,
            "cost": task["cost"] if method == "replay" else 10 * task["cost"],
            "predicted": predicted,
        }


CERTIFICATES: dict[str, dict[str, Any]] = {
    "R_b": {
        "program": ["n4_doors.py", "prove2"],
        "predicted": {"claims": 30, "certified": True},
        "article": "Theorem 7.2",
    },
    "Q_t": {
        "program": ["n4_doors.py", "prove"],
        "predicted": {"claims": 43, "certified": True},
        "article": "Section 7",
    },
    "P+_t": {
        "program": ["np_corridor_prove.py", "prove", "--T0", "8"],
        "predicted": {
            "claims": 938,
            "members": 149,
            "certified": True,
            "exits": {"fork": 54, "height": 428, "member": 161, "new": 123},
        },
        "article": "Theorem 9.1",
    },
}


def _expand_certificate(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "names", "audit_tmax")
    names = table.get("names", list(CERTIFICATES))
    audit = table.get("audit_tmax", 11)
    if not isinstance(names, list) or type(audit) is not int or not 7 <= audit <= 14:
        raise TaskError(f"{where}: names must be a list and audit_tmax a whole number from 7 to 14")
    for name in names:
        if name not in CERTIFICATES:
            raise TaskError(f"{where}: no certificate {name!r}; there are {', '.join(CERTIFICATES)}")
        spec = CERTIFICATES[name]
        audited = name == "P+_t"
        yield {
            "id": f"certificate/{name}" + (f"/audit-to-{audit}" if audited else ""),
            "group": "certificate",
            "cost": 3 * (audit - 7) if audited else 1,
            "name": name,
            "program": [*spec["program"], *(["--audit-tmax", str(audit)] if audited else [])],
            "article": spec["article"],
            "predicted": spec["predicted"],
        }


def _expand_conj55(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "heights")
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


def _expand_conj55_program(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "N", "workers")
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


CENSUS_FILES = [
    "n4_classes_B512.jsonl",
    "n4_classes_k5_B512.jsonl",
    "n4_classes_k67_B256.jsonl",
    "n4_classes_k8_B192.jsonl.gz",
    "n4_classes_k9_B192.jsonl.gz",
]


@dataclass(frozen=True)
class Stage:
    """One program of Sections 8 and 13, run on stored inputs, and the lines of its output that count."""

    kind: str
    commands: tuple[tuple[str, ...], ...]  # each: a script, relative to the repository, and its arguments
    inputs: tuple[str, ...]  # stored results the program reads, by the names it expects
    counts: tuple[tuple[str, str], ...]  # (key, pattern with one group) searched in the output
    modules: tuple[str, ...]
    cost: int
    article: str


STAGES: dict[str, Stage] = {
    "finite-cores": Stage(
        kind="core",
        commands=(
            (
                "experiments/n4_opposite_run.py",
                "cores",
                "--cap",
                "800",
                "--level-cap",
                "1000000",
                "--procs",
                "{procs}",
                "--out",
                "n4_opposite_cores.jsonl.gz",
            ),
        ),
        inputs=tuple(CENSUS_FILES),
        counts=(
            ("classes", r"^(\d+) census classes read"),
            ("finite_cores", r"^total: core found (\d+),"),
            ("search_stopped_at_a_cap", r"^total: core found \d+, search stopped at a cap (\d+) "),
        ),
        modules=("numpy",),
        cost=600,
        article="Section 13",
    ),
    "tube-certificates-note-14": Stage(
        kind="tube",
        commands=(
            (
                "experiments/n4_opposite_tubes.py",
                "run",
                "--procs",
                "{procs}",
                "--cores",
                "n4_opposite_cores.jsonl.gz",
                "--out",
                "n4_opposite_tubes.jsonl.gz",
            ),
        ),
        inputs=("n4_opposite_cores.jsonl.gz",),
        counts=(("classes", r"^(\d+) classes$"), ("certified", r"^certified: (\d+);")),
        modules=("numpy",),
        cost=3600,
        article="Section 13",
    ),
    "tube-certificates-note-22": Stage(
        kind="tube",
        commands=(
            (
                "experiments/n4_tube_lemma.py",
                "certify2",
                "--budget",
                "12",
                "--procs",
                "{procs}",
                "--out",
                "n4_tube_certify2.jsonl.gz",
            ),
        ),
        inputs=("n4_tube_classify.jsonl.gz", "n4_opposite_tubes.jsonl.gz", "n4_opposite_plateaus.jsonl.gz"),
        counts=(
            ("classes", r"^(\d+) classes; second-pass"),
            ("certified", r"^certified: (\d+); with a bottom"),
        ),
        modules=("numpy",),
        cost=2700,
        article="Section 13",
    ),
    "decided-classes": Stage(
        kind="census",
        commands=(("verify/review23_n22_counts.py",),),
        inputs=(
            "n4_opposite_cores.jsonl.gz",
            "n4_opposite_plateaus.jsonl.gz",
            "n4_opposite_tubes.jsonl.gz",
            "n4_tube_certify2.jsonl.gz",
            "n4_tube_classify.jsonl.gz",
        ),
        counts=(
            ("classes", r"^census classes: (\d+);"),
            ("mirror_pairs", r"^mirror map: .* pairs (\d+)$"),
            ("finite_cores", r"^finite cores (\d+);"),
            ("tube_certificates_note_14", r"note-14 tube certificates (\d+);"),
            ("tube_certificates_note_22", r"note-22 certificates (\d+);"),
            ("disconnected", r"^\s+disconnected\s+\{'classes': (\d+),"),
            ("acyclic_bottom", r"^\s+acyclic bottom\s+\{'classes': (\d+),"),
            ("open_classes", r"open classes (\d+):"),
            (
                "settled_by_cores_and_tubes",
                r"pairwise distinct \(finite cores \+ tube certificates\): (\d+);",
            ),
            ("decided", r"covered: (\d+)$"),
        ),
        modules=(),
        cost=20,
        article="Section 13",
    ),
}


def _expand_stage(kind: str) -> Callable[[Task, str], Iterator[Task]]:
    def expand(table: Task, where: str) -> Iterator[Task]:
        _known(table, where, "stages", "procs")
        procs = table.get("procs", 4)
        names = table.get("stages")
        if not isinstance(names, list) or not names or type(procs) is not int or procs < 1:
            raise TaskError(f"{where} needs a list of stages, and procs at least 1")
        for name in names:
            stage = STAGES.get(name)
            if stage is None or stage.kind != kind:
                own = [key for key, value in STAGES.items() if value.kind == kind]
                raise TaskError(f"{where}: no {kind} stage {name!r}; there are {', '.join(own)}")
            yield {
                "id": f"{kind}/{name}",
                "group": kind,
                "cost": stage.cost,
                "stage": name,
                "procs": procs,
                "inputs": list(stage.inputs),
                "article": stage.article,
                "predicted": None,
            }

    return expand


def _expand_synthetic(table: Task, where: str) -> Iterator[Task]:
    _known(table, where, "items")
    items = table.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) and "name" in item for item in items):
        raise TaskError(f"{where}: items must be a list of tables with a name")
    for item in items:
        unknown = set(item) - {"name", "cost", "sleep_seconds", "allocate_mb", "fail", "value", "predicted"}
        if unknown:
            raise TaskError(f"{where}: unknown key {sorted(unknown)[0]!r} in an item")
        yield {
            "id": f"synthetic/{item['name']}",
            "group": "synthetic",
            "cost": item.get("cost", 0),
            "sleep_seconds": item.get("sleep_seconds", 0),
            "allocate_mb": item.get("allocate_mb", 0),
            "fail": bool(item.get("fail", False)),
            "value": item.get("value"),
            "predicted": item.get("predicted"),
        }


EXPANDERS: dict[str, Callable[[Task, str], Iterator[Task]]] = {
    "quiver": _expand_quiver,
    "barrier": _expand_barrier,
    "reach": _expand_reach,
    "route": _expand_route,
    "certificate": _expand_certificate,
    "conj55": _expand_conj55,
    "conj55_program": _expand_conj55_program,
    "census": _expand_stage("census"),
    "core": _expand_stage("core"),
    "tube": _expand_stage("tube"),
    "synthetic": _expand_synthetic,
}


def expand_batch(description: Task, expected: dict[str, dict[str, Any]] | None = None) -> list[Task]:
    """The tasks of a batch description {"tasks": [...]}, in the order given."""
    expected = load_expected() if expected is None else expected
    tasks: list[Task] = []
    for index, table in enumerate(description.get("tasks", [])):
        where = f"tasks[{index}]"
        kind = table.get("kind")
        if kind not in EXPANDERS:
            raise TaskError(f"{where}: kind must be one of {', '.join(EXPANDERS)}")
        control = table.get("control")
        if control is not None and (not isinstance(control, dict) or set(control) != {"predicted"}):
            raise TaskError(f"{where}: control must be a table with the one key predicted")
        for task in EXPANDERS[kind](table, where):
            known = expected.get(task["id"], {})
            if isinstance(task["predicted"], dict) and isinstance(known.get("predicted"), dict):
                task["predicted"] = task["predicted"] | known["predicted"]
            elif task["predicted"] is None:
                task["predicted"] = known.get("predicted")
            task["evidence"] = known.get("evidence", [])
            task |= {"kind": kind, "set": index}
            if control is not None:
                task["id"] += "!control"
                task["group"] = "negative control"
                task["predicted"] = control["predicted"]
                task["control"] = True
                task["evidence"] = []
            tasks.append(task)
    ids = [task["id"] for task in tasks]
    if len(set(ids)) != len(ids):
        repeated = next(i for i in ids if ids.count(i) > 1)
        raise TaskError(f"two tasks of the batch have the id {repeated}")
    return tasks


# ---------------------------------------------------------------------------------------------------
# running


def _start(task: Task) -> tuple[Family, int, tuple[int, ...]]:
    chosen = family(task["family"])
    return chosen, task["value"], chosen.quiver(task["value"])


def _run_quiver(task: Task) -> Result:
    _, _, quiver = _start(task)
    return {
        "value": {
            "height": height(quiver),
            "mutation_heights": [height(mutate(quiver, k)) for k in range(vertices(quiver))],
        },
        "method": "integer mutation",
        "quiver": list(quiver),
    }


def _run_barrier(task: Task) -> Result:
    chosen, value, quiver = _start(task)
    if task["method"] == "search":
        found = search.barrier(quiver)
        return {
            "value": found.level,
            "method": "least-height-first search, no pruning",
            "popped": found.popped,
        }
    _fits_np_barrier(chosen.barrier(value))
    # the search stops where it finds the join; the cap only bounds it
    cap = min(4 * chosen.barrier(value) + 1024, INT_MAX)
    result = np_barrier(quiver, low=height(quiver), cap=cap, n=vertices(quiver))
    joined = result["status"] == "found" and isomorphic(result["target"], opposite(quiver))
    return {
        "value": result.get("iso") if joined else None,
        "method": "np_barrier.c, no pruning",
        "popped": result["popped"],
        "first_other_low_quiver_is_the_opposite": joined,
        "search_status": result["status"],
    }


def _run_reach(task: Task) -> Result:
    _, value, quiver = _start(task)
    bound, prune = task["bound"], task["prune_forks"]
    if task["method"] == "search":
        region = search.below(quiver, bound, prune_forks=prune)
        return {
            "value": {"quivers": region.quivers, "low": region.low},
            "method": "flood below the barrier" + (", forks not expanded" if prune else ", no pruning"),
            "opposite_reached": region.has_opposite,
            "forks_met": region.forks,
        }
    if task["method"] == "np_barrier":
        if prune:
            raise TaskError("np_barrier counts forks among the quivers reached; use search or np_qa_core")
        _fits_np_barrier(bound)
        result = np_barrier(quiver, low=height(quiver), cap=bound - 1, n=vertices(quiver))
        if result["status"] not in ("cap", "closed"):
            return {"value": None, "method": "np_barrier.c", "search_status": result["status"]}
        return {
            "value": {"quivers": result["popped"], "low": result["plateau"]},
            "method": "np_barrier.c, cap one below the barrier, no pruning",
            "search_status": result["status"],
        }
    require("numpy")
    mode = "chain" if prune else "chain-nofork"
    with scratch(task["id"]) as work:
        program(
            "np_qa_core.py", "family", "--amin", value, "--amax", value, "--workers", 1, "--mode", mode,
            "--out", "family.jsonl", cwd=work, env={"NP_QA_CORE_BIN": str(binary("np_qa_core"))},
        )  # fmt: skip
        row = json.loads((work / "family.jsonl").read_text().splitlines()[0])
    closed = row["status"] == "closed" and row["H"] == bound and row["forks_of_height_le_w"] == 0
    return {
        "value": {"quivers": row["members"], "low": row["members_of_height_le_w"]} if closed else None,
        "method": f"np_qa_core.py family, mode {mode}",
        "search_status": row["status"],
        "stored": row["stored"],
        "passed_through": row["passed_through"],
    }


def _run_route(task: Task) -> Result:
    chosen, value, quiver = _start(task)
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


def _run_certificate(task: Task) -> Result:
    script, *arguments = task["program"]
    with scratch(task["id"]) as work:
        output = program(script, *arguments, cwd=work)
    verdict = re.search(r"^(\d+) claims, (?:(\d+) members, )?(.+)$", output, re.MULTILINE)
    if verdict is None:
        return {"value": None, "method": " ".join(task["program"])}
    found: dict[str, Any] = {"claims": int(verdict[1]), "certified": verdict[3].strip() == "ALL CERTIFIED"}
    if verdict[2] is not None:
        found["members"] = int(verdict[2])
    exits = re.search(r"^exits by verdict: (\{.*\})$", output, re.MULTILINE)
    if exits is not None:
        found["exits"] = ast.literal_eval(exits[1])
    return {"value": found, "method": " ".join(task["program"])}


def _run_conj55(task: Task) -> Result:
    quivers, reaching = conj55.split(task["height"])
    return {"value": {"quivers": quivers, "reach_acyclic": reaching}, "method": "enumeration and flood"}


def parse_conj55_summary(output: str) -> dict[str, Any]:
    """The per-height table and the totals printed by `n4_conj55.py summary`."""
    heights: dict[str, dict[str, int]] = {}
    found: dict[str, Any] = {"heights": heights}
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
                key: totals[key] for key in ("quivers", "pass", "fail", "counterexamples", "left")
            }
        elif line.startswith("failing quivers by certificate"):
            found["failing_by_certificate"] = ast.literal_eval(line.partition(": ")[2])
        elif line.startswith("resolve, largest cor52 bound K per height"):
            bounds = ast.literal_eval(line.partition(": ")[2].partition(" (second")[0])
            found["largest_search_is_h3_h2_5"] = all(
                k == (h**3 + h * h + 5, h**3 + h * h + 5) for h, k in bounds.items()
            )
    return found


def _run_conj55_program(task: Task) -> Result:
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
    return {"value": parse_conj55_summary(summary), "method": "n4_conj55.py run, resolve, summary"}


def data_directory() -> Path:
    return Path(os.environ.get("QMB_DATA") or EXPERIMENTS)


def parse_counts(stage: Stage, output: str) -> dict[str, int] | None:
    """The counts of a stage in what its program printed; None if one is missing."""
    found = {}
    for key, pattern in stage.counts:
        match = re.search(pattern, output, re.MULTILINE)
        if match is None:
            return None
        found[key] = int(match[1])
    return found


def _run_stage(task: Task) -> Result:
    stage = STAGES[task["stage"]]
    require(*stage.modules)
    data = data_directory()
    missing = [name for name in stage.inputs if not (data / name).is_file()]
    if missing:
        raise BackendError(
            f"the stored result {missing[0]} is not in {data}: unpack the data archive (DATA.md), "
            "or set QMB_DATA to the directory that holds its files"
        )
    output = ""
    with scratch(task["id"]) as work:
        for name in stage.inputs:
            (work / name).symlink_to((data / name).resolve())
        for script, *arguments in stage.commands:
            filled = [argument.replace("{procs}", str(task["procs"])) for argument in arguments]
            output += program(str(Path("..") / script), *filled, cwd=work)
    return {
        "value": parse_counts(stage, output),
        "method": "; ".join(" ".join(command) for command in stage.commands).replace(
            "{procs}", str(task["procs"])
        ),
        "inputs": "stored results of the data archive",
    }


def _run_synthetic(task: Task) -> Result:
    if task["fail"]:
        raise BackendError("synthetic task asked to fail")
    held = bytearray(b"x") * (int(task["allocate_mb"]) << 20)
    time.sleep(float(task["sleep_seconds"]))
    return {"value": len(held) >> 20 if task["value"] is None else task["value"], "method": "synthetic"}


RUNNERS: dict[str, Callable[[Task], Result]] = {
    "quiver": _run_quiver,
    "barrier": _run_barrier,
    "reach": _run_reach,
    "route": _run_route,
    "certificate": _run_certificate,
    "conj55": _run_conj55,
    "conj55_program": _run_conj55_program,
    "census": _run_stage,
    "core": _run_stage,
    "tube": _run_stage,
    "synthetic": _run_synthetic,
}


def run_task(task: Task) -> Result:
    """The outcome of one task: "ok" when the value agrees with the predicted one or there is none to
    agree with, "mismatch" when it differs or no value could be computed where one is predicted, and
    "unsupported" when the task's method cannot compute it at all."""
    kind = task.get("kind")
    if kind not in RUNNERS:
        raise TaskError(f"kind must be one of {', '.join(RUNNERS)}")
    started = time.perf_counter()
    predicted = task.get("predicted")
    try:
        result = RUNNERS[kind](task)
    except Unsupported as reason:
        return {
            "status": "unsupported",
            "value": None,
            "predicted": predicted,
            "agrees": None,
            "method": task.get("method"),
            "reason": str(reason),
        }
    agreement = agrees(result["value"], predicted)
    status = "mismatch" if agreement is False or (result["value"] is None and predicted is not None) else "ok"
    return result | {
        "status": status,
        "predicted": predicted,
        "agrees": agreement,
        "compute_seconds": round(time.perf_counter() - started, 3),
    }
