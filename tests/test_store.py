"""The result file: whole records only, one writer at a time."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from taskbatch.store import ResultStore, StoreLocked


def record(task_id: str, status: str = "ok") -> dict[str, str]:
    return {"task_id": task_id, "status": status}


class Store(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.path = Path(scratch.name) / "run" / "results.jsonl"

    def test_records_come_back_in_the_order_written(self) -> None:
        with ResultStore(self.path) as store:
            store.append(record("a"))
            store.append(record("b", "timeout"))
            store.append(record("a", "error"))
        store = ResultStore(self.path)
        self.assertEqual([r["task_id"] for r in store.records()], ["a", "b", "a"])
        self.assertEqual(store.latest()["a"]["status"], "error")
        self.assertEqual(store.finished(), {"a", "b"})
        self.assertEqual(store.finished(retry={"timeout"}), {"a"})
        self.assertEqual(len(self.path.read_text().splitlines()), 3)

    def test_an_empty_or_missing_file_has_no_records(self) -> None:
        self.assertEqual(ResultStore(self.path).records(), [])
        self.assertEqual(ResultStore(self.path).finished(), set())

    def test_an_incomplete_last_line_is_ignored_and_closed_off(self) -> None:
        with ResultStore(self.path) as store:
            store.append(record("a"))
        whole = json.dumps(record("b"))
        with self.path.open("a") as handle:
            handle.write(whole[: len(whole) // 2])  # a writer that was killed in the middle of a record

        store = ResultStore(self.path)
        self.assertEqual(store.finished(), {"a"})
        self.assertEqual(store.unreadable_lines, 1)

        with store:
            store.append(record("c"))
        self.assertEqual(store.finished(), {"a", "c"})
        self.assertEqual(store.unreadable_lines, 1)

    def test_lines_that_are_not_records_are_counted_not_used(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text('{"task_id": "a", "status": "ok"}\n[1, 2]\n{"status": "ok"}\n\n')
        store = ResultStore(self.path)
        self.assertEqual(store.finished(), {"a"})
        self.assertEqual(store.unreadable_lines, 2)

    def test_a_second_writer_is_refused(self) -> None:
        with ResultStore(self.path), self.assertRaises(StoreLocked):
            ResultStore(self.path).open()
        with ResultStore(self.path) as store:
            store.append(record("a"))

    def test_writing_needs_an_open_store(self) -> None:
        with self.assertRaises(RuntimeError):
            ResultStore(self.path).append(record("a"))


if __name__ == "__main__":
    unittest.main()
