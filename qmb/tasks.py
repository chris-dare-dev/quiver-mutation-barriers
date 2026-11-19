"""The tasks: how a `[[tasks]]` table of a batch file becomes tasks, and how one task is computed.

A task is one computation with one answer.  Where the article states the answer, the task carries it as
`predicted`, and where a stored result carries the original number, the task names it as `evidence`.  Both
come from two places: the closed forms of `families`, and `claims/expected.json`, which lists the values
typed from the article and those read from the stored results (tools/expected.py writes and checks it).

The kinds, one module of `kinds/` each; the module says the keys of its `[[tasks]]` table and its methods:

    quiver          height of the quiver and of each of its mutations
    barrier         least height joining the quiver to its opposite
    reach           quivers reached below the barrier, and how many of them are as low as the start
    route           the route of the family's theorem, replayed
    certificate     the verdict of a certificate program
    conj55          Conjecture 5.5 at one height, by enumeration
    conj55_program  the original program for all heights up to N
    census, core, tube   one stage of Sections 8 and 13, by its own program (kinds/stages.py)
    synthetic       no mathematics: sleeps, holds memory or fails

A table with `control = { predicted = ... }` makes negative controls: the same tasks under other ids,
with a predicted value that is wrong on purpose.

A computed value agrees with a predicted one when they are equal, or, when both are tables, when the
computed table has every key of the predicted one with the same value.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .backends import REPOSITORY, Unsupported
from .kinds import barrier, certificate, conj55, conj55_program, quiver, reach, route, stages, synthetic
from .kinds.base import Kind, Result, Task, TaskError
from .kinds.certificate import CERTIFICATES, parse_verdict
from .kinds.conj55_program import parse_summary as parse_conj55_summary
from .kinds.reach import core_row as np_qa_core_row
from .kinds.reach import parse_core as parse_np_qa_core
from .kinds.reach import parse_plain as parse_review17
from .kinds.stages import STAGES, parse_counts

__all__ = [
    "CERTIFICATES",
    "EXPECTED",
    "KINDS",
    "STAGES",
    "TaskError",
    "Unsupported",
    "agrees",
    "expand_batch",
    "load_expected",
    "np_qa_core_row",
    "parse_conj55_summary",
    "parse_counts",
    "parse_np_qa_core",
    "parse_review17",
    "parse_verdict",
    "run_task",
]

EXPECTED = REPOSITORY / "claims" / "expected.json"

KINDS: dict[str, Kind[Any]] = {
    "quiver": quiver.KIND,
    "barrier": barrier.KIND,
    "reach": reach.KIND,
    "route": route.KIND,
    "certificate": certificate.KIND,
    "conj55": conj55.KIND,
    "conj55_program": conj55_program.KIND,
    "census": stages.kind("census"),
    "core": stages.kind("core"),
    "tube": stages.kind("tube"),
    "synthetic": synthetic.KIND,
}


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


def expand_batch(description: Task, expected: dict[str, dict[str, Any]] | None = None) -> list[Task]:
    """The tasks of a batch description {"tasks": [...]}, in the order given."""
    expected = load_expected() if expected is None else expected
    tasks: list[Task] = []
    for index, table in enumerate(description.get("tasks", [])):
        where = f"tasks[{index}]"
        kind = table.get("kind")
        if kind not in KINDS:
            raise TaskError(f"{where}: kind must be one of {', '.join(KINDS)}")
        control = table.get("control")
        if control is not None and (not isinstance(control, dict) or set(control) != {"predicted"}):
            raise TaskError(f"{where}: control must be a table with the one key predicted")
        for task in KINDS[kind].expand(table, where):
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


def run_task(task: Task) -> Result:
    """The outcome of one task: "ok" when the value agrees with the predicted one or there is none to
    agree with, "mismatch" when it differs or no value could be computed where one is predicted, and
    "unsupported" when the task's method cannot compute it at all."""
    kind = task.get("kind")
    if kind not in KINDS:
        raise TaskError(f"kind must be one of {', '.join(KINDS)}")
    started = time.perf_counter()
    predicted = task.get("predicted")
    try:
        result = KINDS[kind].run(task)
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
