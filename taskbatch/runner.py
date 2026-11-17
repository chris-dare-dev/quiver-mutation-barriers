"""The protocol between the scheduler and the program that does the computing (PROTOCOL.md).

A runner is a command.  `<runner> expand <JSON>` prints one line `@task <JSON>` per task and a last
line `@meta <JSON>` with the number of tasks and the versions in use.  `<runner> run <JSON>` computes
one task and prints one line `@result <JSON>`; on an error it exits with a non-zero status and the
message on its standard error.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .model import Task
from .settings import REPOSITORY

TASK_MARK = "@task "
META_MARK = "@meta "
RESULT_MARK = "@result "


class RunnerError(RuntimeError):
    """The runner failed or did not follow the protocol."""


def error_lines(output: str, limit: int = 5) -> str:
    """The lines of a runner's output that say what went wrong, without the lines of a backtrace."""
    lines = [line.strip() for line in output.splitlines()]
    lines = [line for line in lines if line and "--back trace--" not in line and not line.startswith("@")]
    errors = [line for line in lines if "error" in line.lower()]
    return "\n".join((errors or lines)[-limit:])


def expand(
    runner: tuple[str, ...], description: dict[str, Any], *, timeout: float = 600
) -> tuple[list[Task], dict[str, Any]]:
    """Asks the runner for the tasks of a batch description and for its versions."""
    command = [*runner, "expand", json.dumps(description)]
    try:
        done = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, check=False
        )
    except FileNotFoundError:
        raise RunnerError(f"cannot start the runner: {runner[0]} not found") from None
    except subprocess.TimeoutExpired:
        raise RunnerError(f"the runner did not expand the batch within {timeout:g} s") from None
    if done.returncode != 0:
        raise RunnerError(
            f"the runner could not expand the batch (status {done.returncode}):\n"
            + error_lines(done.stderr + done.stdout)
        )
    tasks: list[Task] = []
    meta: dict[str, Any] | None = None
    for line in done.stdout.splitlines():
        try:
            if line.startswith(TASK_MARK):
                tasks.append(Task.from_payload(json.loads(line[len(TASK_MARK) :])))
            elif line.startswith(META_MARK):
                meta = json.loads(line[len(META_MARK) :])
        except (json.JSONDecodeError, ValueError) as problem:
            raise RunnerError(f"the runner printed a line that cannot be read: {problem}") from None
    if meta is None or meta.get("tasks") != len(tasks):
        raise RunnerError("the runner's list of tasks is incomplete")
    if len({task.id for task in tasks}) != len(tasks):
        raise RunnerError("the runner produced two tasks with the same id")
    meta.pop("tasks")
    return tasks, meta


def run_command(runner: tuple[str, ...], task: Task) -> list[str]:
    """The command that computes one task."""
    return [*runner, "run", json.dumps(task.payload)]


def parse_result(output: str) -> dict[str, Any] | None:
    """The result a task printed, or None if it printed none that can be read."""
    for line in reversed(output.splitlines()):
        if line.startswith(RESULT_MARK):
            try:
                result = json.loads(line[len(RESULT_MARK) :])
            except json.JSONDecodeError:
                return None
            return result if isinstance(result, dict) else None
    return None


def code_version(repository: Path = REPOSITORY) -> dict[str, Any]:
    """The git commit of the code and whether the working tree differs from it."""

    def git(*arguments: str) -> str | None:
        try:
            done = subprocess.run(
                ["git", "-C", str(repository), *arguments],
                capture_output=True, text=True, timeout=30, check=False,
            )  # fmt: skip
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
        return done.stdout.strip() if done.returncode == 0 else None

    commit = git("rev-parse", "HEAD")
    changes = git("status", "--porcelain")
    return {"commit": commit, "dirty": None if commit is None or changes is None else bool(changes)}
