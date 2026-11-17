"""The command line with fake tasks: planning, running, reporting, exit statuses, interruption."""

from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from taskbatch.cli import EXIT_FAILED, EXIT_INTERRUPTED, EXIT_LIMITS, EXIT_OK, EXIT_USAGE
from taskbatch.runner import REPOSITORY, code_version

from .helpers import FAKE_RUNNER, Journal

HEADER = """
name = "cli"
[scheduler]
workers = 4
memory_budget_mb = 400
[limits]
time_seconds = 20
memory_mb = 100
"""


def items(*entries: str, limits: str = "") -> str:
    return f'[[tasks]]\nkind = "fake"\n{limits}\nitems = [{", ".join(entries)}]\n'


AGREEING = items('{ name = "a", value = 1, predicted = 1 }', '{ name = "b", cost = 3 }')
DIFFERING = items('{ name = "differs", value = 1, predicted = 2 }')
SLEEPING = items('{ name = "sleeper", sleep = 60 }', limits="limits = { time_seconds = 0.3 }")


def still_runs(pid: int) -> bool:
    """Whether a process is running.  A killed process stays listed as a zombie until its parent
    collects it, which the first process of a container may never do; a zombie does not run."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return False
    return stat.rpartition(")")[2].split()[0] != "Z"


class CommandLine(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        self.run_dir = self.scratch / "run"
        self.journal = Journal(self.scratch / "journal")
        self.runner = shlex.join([sys.executable, str(FAKE_RUNNER), "--journal", str(self.journal.path)])

    def batch(self, *task_sets: str) -> Path:
        path = self.scratch / "cli.toml"
        path.write_text(HEADER + "\n".join(task_sets))
        return path

    def command(self, verb: str, *arguments: object) -> list[str]:
        command = [sys.executable, "-m", "taskbatch", verb, *map(str, arguments)]
        if verb != "report":
            command += ["--runner", self.runner, "--out", str(self.run_dir)]
        return command

    def taskbatch(self, verb: str, *arguments: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            self.command(verb, *arguments), capture_output=True, text=True, cwd=REPOSITORY, timeout=120
        )

    def records(self) -> list[dict]:
        path = self.run_dir / "results.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_run_then_rerun_then_report(self) -> None:
        batch = self.batch(AGREEING)
        plan = self.taskbatch("plan", batch)
        self.assertEqual(plan.returncode, EXIT_OK, plan.stderr)
        self.assertIn("2 tasks, 2 to compute, 0 already recorded", plan.stdout)
        self.assertEqual(self.journal.started(), [])
        self.assertFalse(self.run_dir.exists())

        first = self.taskbatch("run", batch)
        self.assertEqual(first.returncode, EXIT_OK, first.stderr)
        self.assertIn("this run: 2 ok", first.stderr)
        self.assertEqual(len(self.records()), 2)

        second = self.taskbatch("run", batch)
        self.assertEqual(second.returncode, EXIT_OK, second.stderr)
        self.assertIn("this run: nothing to do", second.stderr)
        self.assertEqual(len(self.journal.started()), 2)
        self.assertEqual(len(self.records()), 2)
        self.assertIn("2 tasks, 0 to compute, 2 already recorded", self.taskbatch("plan", batch).stdout)

        report = self.taskbatch("report", self.run_dir, "--full")
        self.assertEqual(report.returncode, EXIT_OK, report.stderr)
        self.assertIn("| fake | 2 | 2 |", report.stdout)
        self.assertIn("| `fake/a` | 1 | 1 | yes | fake |", report.stdout)

    def test_the_configuration_of_each_run_is_recorded_with_the_results(self) -> None:
        batch = self.batch(AGREEING)
        self.taskbatch("run", batch, "--workers", 2, "--time-limit", 7)
        self.taskbatch("run", batch)
        runs = [json.loads(line) for line in (self.run_dir / "runs.jsonl").read_text().splitlines()]
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0]["config"]["scheduler"], {"workers": 2, "memory_budget_mb": 400})
        self.assertEqual(runs[0]["config"]["limits"]["time_seconds"], 7)
        self.assertEqual((runs[0]["tasks"], runs[0]["pending"], runs[1]["pending"]), (2, 2, 0))
        self.assertEqual(runs[0]["runner"], {"fake_version": "1"})
        self.assertEqual(runs[0]["code"], code_version())
        self.assertIn(runs[0]["memory_guard"], ("cgroup", "poll"))
        for record in self.records():
            self.assertEqual(record["run_id"], runs[0]["run_id"])
            self.assertEqual(record["limits"]["time_seconds"], 7)
            self.assertEqual(record["code"], runs[0]["code"])
        manifest = json.loads((self.run_dir / "manifest.json").read_text())
        self.assertEqual([task["id"] for task in manifest["tasks"]], ["fake/a", "fake/b"])

    def test_exit_status_tells_failures_from_limits(self) -> None:
        stopped = self.taskbatch("run", self.batch(AGREEING, SLEEPING))
        self.assertEqual(stopped.returncode, EXIT_LIMITS, stopped.stderr)
        self.assertIn("1 timeout", stopped.stderr)

        failed = self.taskbatch("run", self.batch(AGREEING, SLEEPING, DIFFERING))
        self.assertEqual(failed.returncode, EXIT_FAILED, failed.stderr)
        self.assertIn("computed 1, predicted 2", failed.stderr)

        report = self.taskbatch("report", self.run_dir).stdout
        self.assertIn("## Computed values that differ from the predicted ones", report)
        self.assertIn("| `fake/differs` | 1 | 2 |", report)
        self.assertIn("## Stopped at a limit", report)
        self.assertIn("| `fake/sleeper` | timeout | 0 | 0.3 | 100 |", report)

    def test_retry_runs_stopped_tasks_again(self) -> None:
        batch = self.batch(AGREEING, SLEEPING)
        self.taskbatch("run", batch)
        again = self.taskbatch("run", batch, "--retry", "timeout,memory")
        self.assertEqual(again.returncode, EXIT_LIMITS, again.stderr)
        self.assertEqual(self.journal.started().count("fake/sleeper"), 2)
        self.assertEqual(len(self.journal.started()), 4)

    def test_what_cannot_run_is_refused_before_any_task_starts(self) -> None:
        batch = self.batch(AGREEING)
        refused = [
            self.taskbatch("run", batch, "--memory-budget", 10**9),  # more than the machine has
            self.taskbatch("run", batch, "--memory-limit", 500),  # a task limit above the budget
            self.taskbatch("run", batch, "--retry", "sometimes"),
            self.taskbatch("run", batch, "--workers", 0),
            self.taskbatch("run", self.scratch / "missing.toml"),
            self.taskbatch("report", self.scratch / "nothing-here"),
        ]
        for done in refused:
            self.assertEqual(done.returncode, EXIT_USAGE, done.stderr)
            self.assertIn("taskbatch:", done.stderr)
        self.assertEqual(self.journal.started(), [])
        self.assertEqual(self.records(), [])

    def test_two_runs_cannot_write_to_the_same_results(self) -> None:
        batch = self.batch(items('{ name = "slow", sleep = 2 }'))
        first = subprocess.Popen(self.command("run", batch), cwd=REPOSITORY, stderr=subprocess.DEVNULL)
        self.addCleanup(first.wait)
        self.wait_for(lambda: len(self.journal.started()) == 1)
        second = self.taskbatch("run", batch)
        self.assertEqual(second.returncode, EXIT_USAGE)
        self.assertIn("another run is writing", second.stderr)
        self.assertEqual(first.wait(), EXIT_OK)
        self.assertEqual(len(self.journal.started()), 1)

    def wait_for(self, condition: object, seconds: float = 20) -> None:
        deadline = time.monotonic() + seconds
        while not condition():  # type: ignore[operator]
            if time.monotonic() > deadline:
                self.fail("timed out waiting")
            time.sleep(0.02)

    def start_long_run(self) -> subprocess.Popen[bytes]:
        long = items(*(f'{{ name = "long-{i}", sleep = 60 }}' for i in range(3)))
        quick = items('{ name = "quick", cost = -1 }')
        process = subprocess.Popen(
            self.command("run", self.batch(quick, long)), cwd=REPOSITORY, stderr=subprocess.DEVNULL
        )
        self.wait_for(lambda: len(self.journal.started()) == 4 and len(self.records()) == 1)
        return process

    def assert_gone(self, pids: list[int]) -> None:
        self.wait_for(lambda: not any(still_runs(pid) for pid in pids), seconds=5)

    def test_an_interrupted_run_stops_its_tasks_and_a_rerun_computes_them(self) -> None:
        for stop in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=stop.name):
                process = self.start_long_run()
                process.send_signal(stop)
                self.assertEqual(process.wait(timeout=20), EXIT_INTERRUPTED)
                self.assert_gone(self.journal.pids())
                # the finished task keeps its record; the three in flight have none
                self.assertEqual([record["task_id"] for record in self.records()], ["fake/quick"])
                plan = self.taskbatch("plan", self.scratch / "cli.toml").stdout
                self.assertIn("4 tasks, 3 to compute, 1 already recorded", plan)
                self.journal.path.unlink()
                (self.run_dir / "results.jsonl").unlink()

    def test_tasks_do_not_outlive_a_killed_scheduler(self) -> None:
        process = self.start_long_run()
        os.kill(process.pid, signal.SIGKILL)
        process.wait(timeout=20)
        self.assert_gone(self.journal.pids())
        self.assertEqual([record["task_id"] for record in self.records()], ["fake/quick"])


if __name__ == "__main__":
    unittest.main()
