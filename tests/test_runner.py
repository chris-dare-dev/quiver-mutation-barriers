"""The protocol with the runner: reading its tasks and results, refusing what is incomplete."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from taskbatch.model import Task
from taskbatch.runner import RunnerError, code_version, error_lines, expand, parse_result, run_command

from .helpers import FAKE_RUNNER


def printing(*lines: str, status: int = 0) -> tuple[str, ...]:
    """A runner that prints the given lines whatever it is asked."""
    program = f"import sys\nfor line in {list(lines)!r}: print(line)\nsys.exit({status})"
    return (sys.executable, "-c", program)


class Expansion(unittest.TestCase):
    def test_tasks_and_versions_are_read(self) -> None:
        description = {"tasks": [{"items": [{"name": "a", "cost": 2}, {"name": "b"}]}]}
        tasks, versions = expand((sys.executable, str(FAKE_RUNNER)), description)
        self.assertEqual([task.id for task in tasks], ["fake/a", "fake/b"])
        self.assertEqual((tasks[0].kind, tasks[0].cost, tasks[0].set, tasks[0].group), ("fake", 2, 0, "fake"))
        self.assertEqual(tasks[0].payload["name"], "a")
        self.assertEqual(versions, {"fake_version": "1"})

    def test_other_output_is_ignored(self) -> None:
        runner = printing(
            " -- setting random seed to 1", '@task {"id": "a", "kind": "k"}', '@meta {"tasks": 1}'
        )
        tasks, _ = expand(runner, {})
        self.assertEqual(
            tasks, [Task(id="a", kind="k", cost=0, set=0, group="k", payload={"id": "a", "kind": "k"})]
        )

    def test_an_incomplete_list_is_refused(self) -> None:
        one = '@task {"id": "a", "kind": "k"}'
        for runner in (
            printing(one),  # no closing line
            printing(one, '@meta {"tasks": 2}'),  # a task is missing
            printing(one, one, '@meta {"tasks": 2}'),  # the same task twice
            printing('@task {"kind": "k"}', '@meta {"tasks": 1}'),  # a task without an id
            printing("@task {not json", '@meta {"tasks": 1}'),
        ):
            with self.subTest(runner=runner[-1]), self.assertRaises(RunnerError):
                expand(runner, {})

    def test_a_failing_runner_is_reported_with_its_message(self) -> None:
        with self.assertRaisesRegex(RunnerError, "status 2"):
            expand((sys.executable, str(FAKE_RUNNER), "nonsense"), {})
        with self.assertRaisesRegex(RunnerError, "not found"):
            expand(("no-such-program-anywhere",), {})


class Results(unittest.TestCase):
    def test_the_command_hands_the_task_back_unchanged(self) -> None:
        payload = {"id": "a", "kind": "k", "source": "a^dual(1)"}
        command = run_command(("prog", "--script", "runner.x"), Task.from_payload(payload))
        self.assertEqual(command[:4], ["prog", "--script", "runner.x", "run"])
        self.assertEqual(json.loads(command[4]), payload)

    def test_the_last_result_line_is_the_result(self) -> None:
        output = ' -- noise\n@result {"status": "ok", "value": 1}\n@result {"status": "ok", "value": 2}\n'
        self.assertEqual(parse_result(output), {"status": "ok", "value": 2})
        self.assertIsNone(parse_result("no result here\n"))
        self.assertIsNone(parse_result("@result {broken\n"))
        self.assertIsNone(parse_result("@result [1, 2]\n"))

    def test_error_messages_come_without_the_backtrace(self) -> None:
        output = (
            " -- setting random seed to 1\n"
            "lib/tasks.x:153:60:(2):[8]: error: no object named X\n"
            "lib/tasks.x:173:29:(2):[7]: --back trace--\n"
        )
        self.assertEqual(error_lines(output), "lib/tasks.x:153:60:(2):[8]: error: no object named X")
        self.assertEqual(error_lines("something odd\n"), "something odd")


class CodeVersion(unittest.TestCase):
    def test_a_checkout_has_a_commit(self) -> None:
        version = code_version()
        if version["commit"] is None:
            self.skipTest("the code is not in a git checkout")
        self.assertRegex(version["commit"], "^[0-9a-f]{40}$")
        self.assertIn(version["dirty"], (True, False))

    def test_outside_a_repository_the_commit_is_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            self.assertEqual(code_version(Path(scratch)), {"commit": None, "dirty": None})


if __name__ == "__main__":
    unittest.main()
