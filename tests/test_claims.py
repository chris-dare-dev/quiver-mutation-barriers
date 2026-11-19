"""The registry of claims and the tables generated from it."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from typing import Any

from taskbatch.settings import REPOSITORY

from . import helpers

sys.path.insert(0, str(REPOSITORY / "tools"))

import claims


def record(
    task_id: str, status: str = "ok", value: Any = 1, day: str = "2026-11-17", **payload: Any
) -> dict[str, Any]:
    """The record of a task of TASKS as it is now; `payload` changes the task it was computed for."""
    known = {key: item for key, item in TASKS.get(task_id, {"kind": "k"}).items() if key != "batches"}
    return dict(
        helpers.record(
            known | {"id": task_id} | payload,
            status,
            value=value,
            predicted=value,
            agrees=status == "ok",
            wall_seconds=0.5,
            started_at=f"{day}T10:00:00+00:00",
            code={"commit": "a" * 40, "dirty": False},
        )
    )


TASKS = {
    "barrier/R/b=8": {
        "id": "barrier/R/b=8",
        "kind": "barrier",
        "batches": ["smoke"],
        "predicted": 101,
        "evidence": [{"file": "f.log", "line": 4}],
    },
    "barrier/R/b=9": {
        "id": "barrier/R/b=9",
        "kind": "barrier",
        "batches": ["long"],
        "predicted": 132,
        "evidence": [],
    },
    "barrier/R/b=8!control": {
        "id": "barrier/R/b=8!control",
        "kind": "barrier",
        "batches": ["negative-control"],
        "control": True,
    },
}
CLAIM = {"id": "thm", "table": "t", "cells": ["R_b"], "tasks": ["barrier/R/*"]}


class Registry(unittest.TestCase):
    def test_the_registry_fits_the_batch_files(self) -> None:
        registry, tasks = claims.load_registry(), claims.batch_tasks()
        claims.validate(registry, tasks)
        self.assertGreater(len(tasks), 500)
        self.assertEqual(len({claim["id"] for claim in registry["claim"]}), len(registry["claim"]))

    def test_what_does_not_fit_is_reported(self) -> None:
        registry = {
            "table": {"t": {"heading": "T", "columns": ["a"]}},
            "claim": [
                {"id": "x", "table": "t", "cells": ["1"], "tasks": ["barrier/Z/*"]},
                {"id": "y", "table": "u", "cells": ["1"], "tasks": []},
            ],
            "headline": [{"label": "l", "task": "barrier/R/b=9"}],
        }
        with self.assertRaises(claims.RegistryError) as raised:
            claims.validate(registry, TASKS)
        message = str(raised.exception)
        for part in (
            "no task of any batch matches 'barrier/Z/*'",
            "no table 'u'",
            "either tasks or a reason",
            "barrier/R/b=8 (smoke) belongs to no claim",
            "not a task of batches/smoke.toml",
        ):
            self.assertIn(part, message)
        self.assertNotIn("!control", message)

    def test_a_star_after_a_number_is_refused(self) -> None:
        # "b=8*" is meant for b = 8 and would also take b = 80
        registry = {
            "table": {"t": {"heading": "T", "columns": ["a"]}},
            "claim": [
                {"id": "x", "table": "t", "cells": ["1"], "tasks": ["barrier/R/b=8*", "barrier/R/b=9"]}
            ],
            "headline": [],
        }
        with self.assertRaisesRegex(claims.RegistryError, "the \\* follows a digit"):
            claims.validate(registry, TASKS)
        registry["claim"][0]["tasks"] = ["barrier/R/b=8", "barrier/R/b=9"]
        claims.validate(registry, TASKS)

    def test_negative_controls_never_count_for_a_claim(self) -> None:
        self.assertEqual(claims.claim_tasks(CLAIM, TASKS), ["barrier/R/b=8", "barrier/R/b=9"])


class Summaries(unittest.TestCase):
    def test_a_claim_without_a_record_reads_not_re_run(self) -> None:
        text = claims.summary(CLAIM, TASKS, {})
        self.assertIn("**not re-run**: 2 tasks in `long`, `smoke`, no record", text)
        self.assertNotRegex(text, r"\bok\b")

    def test_a_claim_is_ok_only_when_every_task_is(self) -> None:
        latest = {"barrier/R/b=8": record("barrier/R/b=8")}
        text = claims.summary(CLAIM, TASKS, latest)
        self.assertIn("tasks: ok 1; not re-run 1 (of 2); 2026-11-17, `aaaaaaa`", text)
        self.assertNotIn("**ok**", text)
        latest["barrier/R/b=9"] = record("barrier/R/b=9", status="mismatch")
        self.assertIn("tasks: ok 1; mismatch 1 (of 2)", claims.summary(CLAIM, TASKS, latest))
        latest["barrier/R/b=9"] = record("barrier/R/b=9", day="2026-11-18")
        self.assertIn("all 2 tasks **ok**; 2026-11-17 to 2026-11-18", claims.summary(CLAIM, TASKS, latest))

    def test_a_claim_without_tasks_says_why(self) -> None:
        claim = {"id": "c", "table": "t", "cells": ["x"], "tasks": [], "no_task": "a proof by hand"}
        self.assertEqual(claims.summary(claim, TASKS, {}), "no task: a proof by hand")

    def test_the_detail_page_lists_predicted_evidence_and_record(self) -> None:
        registry = {"claim": [CLAIM]}
        page = claims.detail(registry, TASKS, {"barrier/R/b=8": record("barrier/R/b=8", value=101)})
        self.assertIn(
            "| `barrier/R/b=8` | smoke | 101 | `f.log`, line 4 | ok, 2026-11-17, `aaaaaaa`, 0.5 s | 101 |",
            page,
        )
        self.assertIn("| `barrier/R/b=9` | long | 132 |  | not re-run |  |", page)

    def test_a_record_of_a_task_that_changed_since_is_stale_and_supports_nothing(self) -> None:
        old = record("barrier/R/b=9", value=131, predicted=131)
        self.assertEqual(claims.standing(TASKS["barrier/R/b=9"], old), "stale")
        self.assertEqual(
            claims.standing(TASKS["barrier/R/b=9"], record("barrier/R/b=9", set=3, cost=2)), "ok"
        )
        latest = {"barrier/R/b=8": record("barrier/R/b=8"), "barrier/R/b=9": old}
        text = claims.summary(CLAIM, TASKS, latest)
        self.assertIn("tasks: ok 1; stale 1 (of 2); 2026-11-17, `aaaaaaa`", text)
        self.assertNotIn("**ok**", text)
        page = claims.detail({"claim": [CLAIM]}, TASKS, latest)
        self.assertIn(
            "| `barrier/R/b=9` | long | 132 |  "
            "| stale: recorded 2026-11-17 at `aaaaaaa` for the task as it was then |  |",
            page,
        )
        # a claim whose only records are stale names no day and no commit
        text = claims.summary(CLAIM, TASKS, {"barrier/R/b=9": old})
        self.assertIn("tasks: stale 1; not re-run 1 (of 2); [tasks]", text)
        # the headline table shows no computed value for a stale record
        registry = {"headline": [{"label": "R_9", "task": "barrier/R/b=9"}]}
        self.assertIn("| R_9 | 132 |  | stale | `barrier/R/b=9` |", claims.headline(registry, TASKS, latest))

    def test_values_in_cells(self) -> None:
        self.assertEqual(claims.cell(1242), "1,242")
        self.assertEqual(claims.cell({"quivers": 35, "low": 1}), "quivers 35, low 1")
        self.assertEqual(claims.cell([8, 24]), "(8, 24)")
        self.assertEqual(claims.cell(True), "yes")
        self.assertEqual(claims.cell(None), "")
        self.assertEqual(len(claims.cell("x" * 500)), 160)


class Files(unittest.TestCase):
    def test_the_committed_tables_are_what_the_generator_writes(self) -> None:
        stale = [
            path.name for path, text in claims.outputs().items() if path.read_text(encoding="utf-8") != text
        ]
        self.assertEqual(stale, [], "run `make tables`")

    def test_generated_parts_need_their_markers(self) -> None:
        begin, end = "<!-- BEGIN GENERATED x: tools/claims.py tables -->", "<!-- END GENERATED x -->"
        text = f"before\n{begin}\nold\n{end}\nafter\n"
        self.assertEqual(
            claims.splice(text, "x", ["new"], Path("f.md")), f"before\n{begin}\nnew\n{end}\nafter\n"
        )
        with self.assertRaises(claims.RegistryError):
            claims.splice("no markers", "x", ["new"], Path("f.md"))

    def test_the_latest_record_of_a_task_wins_across_run_directories(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            for name, day, status in (("a", "2026-11-17", "timeout"), ("b", "2026-11-18", "ok")):
                (Path(scratch) / name).mkdir()
                (Path(scratch) / name / "results.jsonl").write_text(
                    json.dumps(record("t", status=status, day=day)) + "\n"
                )
            latest = claims.latest_records(Path(scratch))
            self.assertEqual((latest["t"]["status"], latest["t"]["batch"]), ("ok", "b"))
            self.assertEqual(claims.latest_records(Path(scratch) / "absent"), {})


if __name__ == "__main__":
    unittest.main()
