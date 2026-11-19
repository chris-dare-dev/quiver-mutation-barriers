"""Adoption: which records of a run may be committed, and what happens to them on the way."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from taskbatch.settings import REPOSITORY

from . import helpers

sys.path.insert(0, str(REPOSITORY / "tools"))

import adopt


def record(task_id: str, commit: str = "a" * 40, dirty: bool = False, **fields: Any) -> dict[str, Any]:
    code = {"commit": commit, "dirty": dirty}
    return dict(helpers.record({"id": task_id, "kind": "k"}, "ok", code=code, **fields))


def run_directory(scratch: str, *rows: dict[str, Any]) -> Path:
    run_dir = Path(scratch) / "results" / "trial"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "manifest.json").write_text("{}")
    (run_dir / "results.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    return run_dir


class Adoption(unittest.TestCase):
    def test_only_records_of_committed_code_are_adopted(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            records = Path(scratch) / "records"
            run_dir = run_directory(scratch, record("t", dirty=True))
            with self.assertRaisesRegex(adopt.AdoptError, "uncommitted changes"):
                adopt.adopt(run_dir, records, REPOSITORY)
            run_dir = run_directory(scratch)
            with self.assertRaisesRegex(adopt.AdoptError, "no records"):
                adopt.adopt(run_dir, records, REPOSITORY)
            self.assertFalse(records.exists())

    def test_a_record_that_names_this_machine_is_not_adopted(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            row = record("t", error=f"work directory kept at {Path.home()}/somewhere")
            run_dir = run_directory(scratch, row)
            with self.assertRaisesRegex(adopt.AdoptError, "names this machine or a directory outside"):
                adopt.adopt(run_dir, Path(scratch) / "records", REPOSITORY)
            self.assertFalse((Path(scratch) / "records").exists())

    def test_a_record_follows_its_commit_through_a_rewrite_of_the_messages(self) -> None:
        def git(*arguments: str) -> str:
            identity = ["-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false"]
            done = subprocess.run(
                ["git", "-C", str(root), *identity, *arguments], capture_output=True, text=True
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            return done.stdout.strip()

        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / "repository"
            root.mkdir()
            git("init", "-q")
            (root / "code.py").write_text("1\n")
            git("add", "code.py")
            git("commit", "-q", "-m", "first, with a trailer")
            before = git("rev-parse", "HEAD")
            git("commit", "-q", "--amend", "-m", "first")  # the same tree under a new number
            after = git("rev-parse", "HEAD")
            (root / "code.py").write_text("2\n")
            git("commit", "-q", "-am", "second")
            head = git("rev-parse", "HEAD")
            self.assertNotEqual(before, after)
            rows = [record("old", commit=before), record("new", commit=head)]
            run_dir = run_directory(scratch, *rows)
            text = (run_dir / "results.jsonl").read_text()

            done = adopt.adopt(run_dir, root / "records", root)
            self.assertEqual([row["task_id"] for row in done.records], ["old", "new"])
            self.assertEqual(dict(done.moved), {(before, after): 1})
            adopted = (root / "records" / "trial" / "results.jsonl").read_text().splitlines()
            self.assertEqual(json.loads(adopted[0])["code"]["commit"], after)
            self.assertEqual(json.loads(adopted[0]) | {"code": None}, rows[0] | {"code": None})
            self.assertEqual(adopted[1], text.splitlines()[1])  # untouched, byte for byte
            # next to the records: the tree of each commit they name
            trees = json.loads((root / "records" / "trial" / "adopted.json").read_text())["trees"]
            self.assertEqual(trees, {c: git("rev-parse", f"{c}^{{tree}}") for c in (after, head)})
            # a commit that is nowhere in the repository cannot be placed
            run_dir = run_directory(scratch, record("lost"))
            with self.assertRaisesRegex(adopt.AdoptError, "not in this repository"):
                adopt.adopt(run_dir, root / "records", root)


if __name__ == "__main__":
    unittest.main()
