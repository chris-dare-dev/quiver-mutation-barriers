"""The registry of claims and the tables generated from it."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from typing import Any

from taskbatch.settings import REPOSITORY

sys.path.insert(0, str(REPOSITORY / "tools"))

import claims


def record(
    task_id: str, status: str = "ok", value: Any = 1, dirty: bool = False, day: str = "2026-11-17"
) -> dict[str, Any]:
    return {
        "task_id": task_id, "task": {"id": task_id}, "status": status, "value": value, "predicted": value,
        "agrees": status == "ok", "wall_seconds": 0.5, "started_at": f"{day}T10:00:00+00:00",
        "code": {"commit": "a" * 40, "dirty": dirty},
    }  # fmt: skip


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

    def test_only_records_of_committed_code_are_adopted(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            run_dir = Path(scratch) / "trial"
            run_dir.mkdir()
            (run_dir / "manifest.json").write_text("{}")
            (run_dir / "results.jsonl").write_text(json.dumps(record("t", dirty=True)) + "\n")
            with self.assertRaisesRegex(claims.RegistryError, "uncommitted changes"):
                claims.command_adopt([run_dir])
            (run_dir / "results.jsonl").write_text("")
            with self.assertRaisesRegex(claims.RegistryError, "no records"):
                claims.command_adopt([run_dir])

    def test_a_record_follows_its_commit_through_a_rewrite_of_the_messages(self) -> None:
        def git(*arguments: str) -> str:
            identity = ["-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false"]
            done = subprocess.run(
                ["git", "-C", str(root), *identity, *arguments], capture_output=True, text=True
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            return done.stdout.strip()

        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            git("init", "-q")
            (root / "code.py").write_text("1\n")
            git("add", "code.py")
            git("commit", "-q", "-m", "first, with a trailer")
            before = git("rev-parse", "HEAD")
            git("commit", "-q", "--amend", "-m", "first")  # the same tree under a new number
            after = git("rev-parse", "HEAD")
            (root / "code.py").write_text("2\n")
            git("commit", "-q", "-am", "second")
            self.assertNotEqual(before, after)
            run_dir = root / "results" / "trial"
            run_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text("{}")
            rows = [record("old") | {"code": {"commit": before, "dirty": False}}]
            rows.append(record("new") | {"code": {"commit": git("rev-parse", "HEAD"), "dirty": False}})
            text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
            (run_dir / "results.jsonl").write_text(text)
            with unittest.mock.patch.multiple(claims, REPOSITORY=root, RECORDS=root / "records"):
                claims.command_adopt([run_dir])
                adopted = (root / "records" / "trial" / "results.jsonl").read_text().splitlines()
                self.assertEqual(json.loads(adopted[0])["code"]["commit"], after)
                self.assertEqual(json.loads(adopted[0]) | {"code": None}, rows[0] | {"code": None})
                self.assertEqual(adopted[1], text.splitlines()[1])  # untouched, byte for byte
                # a commit that is nowhere in the repository cannot be placed
                (run_dir / "results.jsonl").write_text(json.dumps(record("lost")) + "\n")
                with self.assertRaisesRegex(claims.RegistryError, "not in this repository"):
                    claims.command_adopt([run_dir])

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
