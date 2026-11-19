"""The record: how a status is decided from what the scheduler saw, and which fields a record has."""

from __future__ import annotations

import json
import re
import signal
import unittest
from typing import Any

from taskbatch import cli
from taskbatch.model import Limits, Status, Task
from taskbatch.record import Record, answers, classify, make_record
from taskbatch.settings import REPOSITORY


def printed(**result: Any) -> str:
    return "some output\n@result " + json.dumps(result) + "\n"


def never() -> bool:
    raise AssertionError("the memory guard is asked only about a process someone else killed")


class Classify(unittest.TestCase):
    def test_a_result_of_the_runner_gives_the_status(self) -> None:
        for status in ("ok", "mismatch", "unsupported"):
            found, result, error = classify(
                printed(status=status, value=3), 0, stopped=None, killed_for_memory=never
            )
            self.assertEqual((found, result, error), (Status(status), {"status": status, "value": 3}, None))

    def test_a_process_the_scheduler_stopped_has_the_status_of_its_limit(self) -> None:
        for stopped in (Status.TIMEOUT, Status.MEMORY):
            found = classify("", -signal.SIGKILL, stopped=stopped, killed_for_memory=never)
            self.assertEqual(found, (stopped, {}, None))

    def test_a_result_printed_before_the_limit_does_not_count(self) -> None:
        found = classify(printed(status="ok", value=3), 0, stopped=Status.TIMEOUT, killed_for_memory=never)
        self.assertEqual(found, (Status.TIMEOUT, {}, None))

    def test_a_kill_by_the_kernel_at_the_limit_is_a_memory_stop(self) -> None:
        found = classify("", -signal.SIGKILL, stopped=None, killed_for_memory=lambda: True)
        self.assertEqual(found, (Status.MEMORY, {}, None))

    def test_another_kill_is_a_crash(self) -> None:
        found = classify("", -signal.SIGKILL, stopped=None, killed_for_memory=lambda: False)
        self.assertEqual(found, (Status.CRASHED, {}, "ended by signal SIGKILL"))
        found = classify("", -signal.SIGSEGV, stopped=None, killed_for_memory=never)
        self.assertEqual(found, (Status.CRASHED, {}, "ended by signal SIGSEGV"))

    def test_a_failing_exit_status_is_an_error_with_the_lines_that_say_why(self) -> None:
        output = "starting\nlib.py:3: error: no object named X\n"
        found = classify(output, 1, stopped=None, killed_for_memory=never)
        self.assertEqual(found, (Status.ERROR, {}, "lib.py:3: error: no object named X"))
        self.assertEqual(classify("", 7, stopped=None, killed_for_memory=never)[2], "exit status 7")

    def test_a_result_is_not_read_after_a_failing_exit_status(self) -> None:
        found = classify(printed(status="ok", value=3), 1, stopped=None, killed_for_memory=never)
        self.assertEqual(found[0], Status.ERROR)

    def test_ending_well_without_a_result_is_a_crash(self) -> None:
        found = classify("no result line\n", 0, stopped=None, killed_for_memory=never)
        self.assertEqual(found, (Status.CRASHED, {}, "ended without a result"))

    def test_a_status_the_runner_may_not_report_is_a_crash_that_keeps_what_was_printed(self) -> None:
        found = classify(printed(status="timeout", value=3), 0, stopped=None, killed_for_memory=never)
        self.assertEqual(found, (Status.CRASHED, {"status": "timeout", "value": 3}, "ended without a result"))


class Fields(unittest.TestCase):
    def make(self, result: dict[str, Any], exit_code: int = 0, **payload: Any) -> Record:
        return make_record(
            Task.from_payload({"id": "t", "kind": "k"} | payload),
            Limits(time_seconds=60, memory_mb=500),
            Status.OK,
            result,
            None,
            wall_seconds=1.23456,
            cpu_seconds=2.00049,
            peak_rss_mb=120.04,
            memory_guard="poll",
            exit_code=exit_code,
            started_at="2026-01-01T00:00:00+00:00",
            log=None,
            stamp={"run_id": "r", "runner": {}, "code": {"commit": "0" * 40, "dirty": False}},
        )

    def test_a_record_has_the_fields_of_the_type_and_no_other(self) -> None:
        self.assertEqual(set(self.make({})), set(Record.__annotations__))

    def test_the_protocol_names_every_field(self) -> None:
        protocol = (REPOSITORY / "taskbatch" / "PROTOCOL.md").read_text(encoding="utf-8")
        section = protocol.split("## Records", 1)[1].split("\n## ", 1)[0]
        first_paragraph = section.strip().split("\n\n", 1)[0]
        self.assertEqual(set(re.findall(r"`([a-z_]+)`", first_paragraph)), set(Record.__annotations__))

    def test_the_other_keys_of_a_result_go_under_detail(self) -> None:
        record = self.make({"status": "ok", "value": 3, "predicted": 3, "agrees": True, "method": "direct"})
        self.assertEqual(record["detail"], {"method": "direct"})
        self.assertEqual((record["value"], record["predicted"], record["agrees"]), (3, 3, True))

    def test_the_predicted_value_of_the_task_is_kept_when_the_result_gives_none(self) -> None:
        self.assertEqual(self.make({"value": 3}, predicted=4)["predicted"], 4)
        self.assertEqual(self.make({"value": 3, "predicted": 5}, predicted=4)["predicted"], 5)

    def test_measurements_are_rounded(self) -> None:
        record = self.make({})
        self.assertEqual(
            (record["wall_seconds"], record["cpu_seconds"], record["peak_rss_mb"]), (1.235, 2.0, 120.0)
        )

    def test_a_signal_is_named_and_leaves_no_exit_code(self) -> None:
        record = self.make({}, exit_code=-signal.SIGKILL)
        self.assertEqual((record["exit_code"], record["exit_signal"]), (None, "SIGKILL"))
        record = self.make({}, exit_code=2)
        self.assertEqual((record["exit_code"], record["exit_signal"]), (2, None))


TASK: dict[str, Any] = {"id": "t", "kind": "k", "bound": 3, "predicted": {"n": 7}, "pair": ["a", "b"]}


class Answers(unittest.TestCase):
    task = TASK

    def test_a_record_answers_the_task_it_was_computed_for(self) -> None:
        self.assertTrue(answers({"task": dict(self.task)}, self.task))
        self.assertTrue(answers({"task": self.task | {"pair": ["a", "b"]}}, self.task | {"pair": ("a", "b")}))

    def test_the_place_of_a_task_in_its_batch_does_not_count(self) -> None:
        moved = self.task | {"set": 4, "group": "other", "cost": 9.5}
        self.assertTrue(answers({"task": self.task | {"set": 0, "group": "k", "cost": 1}}, moved))

    def test_a_key_without_a_value_is_as_good_as_absent(self) -> None:
        self.assertTrue(answers({"task": dict(self.task)}, self.task | {"sample": None}))

    def test_another_predicted_value_or_another_computation_is_another_task(self) -> None:
        self.assertFalse(answers({"task": dict(self.task)}, self.task | {"predicted": {"n": 8}}))
        self.assertFalse(answers({"task": dict(self.task)}, self.task | {"bound": 4}))
        self.assertFalse(answers({"task": self.task | {"method": "direct"}}, self.task))


class ExitStatus(unittest.TestCase):
    def test_a_run_ends_with_the_worst_of_its_statuses(self) -> None:
        self.assertEqual(cli.exit_status([]), cli.EXIT_OK)
        self.assertEqual(cli.exit_status(["ok", "unsupported"]), cli.EXIT_OK)
        self.assertEqual(cli.exit_status(["ok", "timeout"]), cli.EXIT_LIMITS)
        self.assertEqual(cli.exit_status(["ok", "memory"]), cli.EXIT_LIMITS)
        for failed in ("mismatch", "error", "crashed"):
            self.assertEqual(cli.exit_status(["ok", "timeout", failed]), cli.EXIT_FAILED)


if __name__ == "__main__":
    unittest.main()
