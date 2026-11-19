"""The report: every task of the manifest is counted, and each kind of outcome has its table."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from taskbatch.report import render
from taskbatch.store import ResultStore

from . import helpers


def task(name: str, group: str = "pairs d2", **more: Any) -> dict[str, Any]:
    return {"id": name, "kind": "ext_pair", "group": group, "cost": 3} | more


def record(name: str, status: str, **more: Any) -> dict[str, Any]:
    fields = {"predicted": {"chi": 2}, "runner": {"version": "1.0"}} | more
    return dict(helpers.record(fields.pop("task", task(name)), status, **fields))


class Report(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.run_dir = Path(scratch.name) / "example"

    def write(self, tasks: list[dict[str, Any]], records: list[dict[str, Any]]) -> None:
        with ResultStore(self.run_dir / "results.jsonl") as store:
            for entry in records:
                store.append(entry)
        (self.run_dir / "manifest.json").write_text(json.dumps({"tasks": tasks}))

    def test_every_outcome_has_its_place(self) -> None:
        names = ["good", "bad", "slow", "big", "broken", "none", "waiting"]
        self.write(
            [task(name) for name in names] + [task("other", group="pairs d3")],
            [
                record(
                    "good",
                    "ok",
                    value={"dims": [1, 0, 1], "chi": 2},
                    agrees=True,
                    detail={"method": "direct"},
                ),
                record("bad", "mismatch", value={"dims": [1, 0, 0], "chi": 1}, agrees=False),
                record("slow", "timeout", wall_seconds=60.1),
                record("big", "memory", peak_rss_mb=499.0),
                record(
                    "broken", "error", error="tasks.py:1:1: error: no object named X", log="logs/broken.log"
                ),
                record("none", "unsupported"),
            ],
        )
        report = render(self.run_dir, full=True)

        self.assertIn("# Results in example", report)
        self.assertIn("- code: abc123", report)
        self.assertIn("- runner: version 1.0", report)
        self.assertIn(
            "| group | tasks | ok | mismatch | unsupported | timeout | memory | error | not run |", report
        )
        self.assertIn("| pairs d2 | 7 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |", report)
        self.assertIn("| pairs d3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |", report)
        self.assertIn("| `bad` | chi 1, dims (1, 0, 0) | chi 2 |", report)
        self.assertIn("| `slow` | timeout | 3 | 60 | 500 | 60.1 | 120 |", report)
        self.assertIn("| `big` | memory | 3 | 60 | 500 | 1.5 | 499 |", report)
        self.assertIn(
            "| `broken` | error | tasks.py:1:1: error: no object named X | logs/broken.log |", report
        )
        self.assertIn("| `none` | chi 2 |", report)
        self.assertIn("| `good` | chi 2, dims (1, 0, 1) | chi 2 | yes | direct | 1.5 | 120 |", report)

    def test_the_latest_record_of_a_task_counts(self) -> None:
        self.write([task("a")], [record("a", "timeout"), record("a", "ok", value=1, agrees=True)])
        report = render(self.run_dir)
        self.assertIn("| pairs d2 | 1 | 1 |", report)
        self.assertNotIn("Stopped at a limit", report)
        self.assertIn("## Slowest computed tasks", report)

    def test_records_from_uncommitted_code_and_unreadable_lines_are_pointed_out(self) -> None:
        self.write([task("a")], [record("a", "ok", value=1, code={"commit": "abc123", "dirty": True})])
        with (self.run_dir / "results.jsonl").open("a") as handle:
            handle.write('{"task_id": "b", "sta')
        report = render(self.run_dir)
        self.assertIn("uncommitted changes", report)
        self.assertIn("1 unreadable line(s)", report)

    def test_results_without_a_manifest_are_still_reported(self) -> None:
        with ResultStore(self.run_dir / "results.jsonl") as store:
            store.append(record("a", "ok", value=1))
        self.assertIn("| pairs d2 | 1 | 1 |", render(self.run_dir))


if __name__ == "__main__":
    unittest.main()
