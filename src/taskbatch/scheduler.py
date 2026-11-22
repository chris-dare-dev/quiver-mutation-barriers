"""Runs the tasks of a batch: one process per task, several at a time, within a memory budget.

A task process is never trusted to stop itself.  The scheduler measures its wall time and kills it at
the time limit; the memory guard stops it at the memory limit.  Whatever happens to one process, the
scheduler writes exactly one record for its task and carries on with the others.
"""

from __future__ import annotations

import contextlib
import ctypes
import hashlib
import os
import re
import signal
import subprocess
import time
from collections import Counter
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import BatchConfig, ConfigError
from .memory import MemoryGuard
from .model import RUNNER_STATUSES, Limits, Status, Task
from .record import Record, classify, make_record
from .runner import run_command
from .settings import REPOSITORY
from .store import ResultStore

_PR_SET_PDEATHSIG = 1
_libc = ctypes.CDLL(None, use_errno=True)


def _die_with_scheduler() -> None:
    # runs in the task process before the command starts: the kernel kills the process if the scheduler
    # goes away, so no computation outlives the program that enforces its limits
    _libc.prctl(_PR_SET_PDEATHSIG, signal.SIGKILL)


@dataclass
class _Running:
    task: Task
    limits: Limits
    process: subprocess.Popen[bytes]
    tag: str
    log: Path
    started: float
    started_at: str
    stopped: Status | None = None  # the limit at which the scheduler killed the process


Progress = Callable[[Record, int, int], None]


class Scheduler:
    def __init__(
        self,
        *,
        config: BatchConfig,
        tasks: Sequence[Task],
        store: ResultStore,
        run_dir: Path,
        runner: tuple[str, ...],
        guard: MemoryGuard,
        stamp: dict[str, Any] | None = None,
        retry: Collection[str] = (),
        progress: Progress | None = None,
        tick: float = 0.02,
    ) -> None:
        self.config = config
        self.tasks = list(tasks)
        self.store = store
        self.run_dir = run_dir
        self.runner = runner
        self.guard = guard
        self.stamp = stamp or {}
        self.retry = frozenset(retry)
        self.progress = progress
        self.tick = tick
        self._started = 0

    def pending(self) -> list[tuple[Task, Limits]]:
        """The tasks without a record that counts, cheapest first, each with its limits."""
        finished = self.store.finished(self.retry)
        todo = [(task, self.config.limits_for(task)) for task in self.tasks if task.id not in finished]
        for task, limits in todo:
            if limits.memory_mb > self.config.memory_budget_mb:
                raise ConfigError(
                    f"task {task.id} has a memory limit of {limits.memory_mb} MB, "
                    f"above the budget of {self.config.memory_budget_mb} MB"
                )
        order = {task.id: index for index, task in enumerate(self.tasks)}
        return sorted(todo, key=lambda item: (item[0].cost, order[item[0].id]))

    def run(self) -> Counter[str]:
        """Computes every pending task and returns how many ended with each status."""
        pending = self.pending()
        total = len(pending)
        outcome: Counter[str] = Counter()
        running: list[_Running] = []
        (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)
        # a terminated scheduler stops its task processes the same way an interrupted one does
        previous = signal.signal(signal.SIGTERM, _raise_interrupt)
        try:
            while pending or running:
                self._admit(pending, running)
                finished = self._collect(running)
                for record in finished:
                    self.store.append(record)
                    outcome[record["status"]] += 1
                    if self.progress is not None:
                        self.progress(record, outcome.total(), total)
                if not finished and running:
                    time.sleep(self.tick)
        finally:
            # an interrupted run leaves no record for the tasks in flight, so a rerun computes them
            for entry in running:
                self._kill(entry)
                self.guard.release(entry.tag)
            signal.signal(signal.SIGTERM, previous)
        return outcome

    # starting --------------------------------------------------------------------------------------

    def _admit(self, pending: list[tuple[Task, Limits]], running: list[_Running]) -> None:
        """Starts tasks, cheapest first, while a worker is free and the memory limits fit the budget."""
        while len(running) < self.config.workers:
            committed = sum(entry.limits.memory_mb for entry in running)
            room = self.config.memory_budget_mb - committed
            fits = next((i for i, (_, limits) in enumerate(pending) if limits.memory_mb <= room), None)
            if fits is None:
                return
            running.append(self._start(*pending.pop(fits)))

    def _start(self, task: Task, limits: Limits) -> _Running:
        self._started += 1
        tag = f"taskbatch-{os.getpid()}-{self._started}"
        log = self.run_dir / "logs" / f"{_slug(task.id)}.log"
        command = self.guard.wrap(run_command(self.runner, task), limits.memory_mb, tag)
        with log.open("wb") as output:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.STDOUT,
                cwd=REPOSITORY,
                start_new_session=True,
                preexec_fn=_die_with_scheduler,
            )
        return _Running(
            task=task,
            limits=limits,
            process=process,
            tag=tag,
            log=log,
            started=time.monotonic(),
            started_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )

    # ending ----------------------------------------------------------------------------------------

    def _collect(self, running: list[_Running]) -> list[Record]:
        """Records for the processes that ended or had to be stopped; removes them from `running`."""
        records = []
        for entry in list(running):
            pid, status, usage = os.wait4(entry.process.pid, os.WNOHANG)
            if pid == 0:
                if time.monotonic() - entry.started > entry.limits.time_seconds:
                    entry.stopped = Status.TIMEOUT
                elif self.guard.over_limit(entry.process.pid, entry.limits.memory_mb):
                    entry.stopped = Status.MEMORY
                else:
                    continue
                status, usage = self._kill(entry)
            wall = time.monotonic() - entry.started
            entry.process.returncode = os.waitstatus_to_exitcode(status)
            running.remove(entry)
            records.append(self._record(entry, entry.process.returncode, usage, wall))
        return records

    @staticmethod
    def _kill(entry: _Running) -> tuple[int, Any]:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(entry.process.pid, signal.SIGKILL)
        _, status, usage = os.wait4(entry.process.pid, 0)
        entry.process.returncode = os.waitstatus_to_exitcode(status)
        return status, usage

    def _record(self, entry: _Running, exit_code: int, usage: Any, wall: float) -> Record:
        output = entry.log.read_text(encoding="utf-8", errors="replace")
        status, result, error = classify(
            output,
            exit_code,
            stopped=entry.stopped,
            killed_for_memory=lambda: self.guard.killed_for_memory(entry.tag),
        )
        if exit_code != 0:
            self.guard.release(entry.tag)
        keep_log = status not in RUNNER_STATUSES
        if not keep_log:
            entry.log.unlink(missing_ok=True)
        return make_record(
            entry.task,
            entry.limits,
            status,
            result,
            error,
            wall_seconds=wall,
            cpu_seconds=usage.ru_utime + usage.ru_stime,
            peak_rss_mb=usage.ru_maxrss / 1024,
            memory_guard=self.guard.name,
            exit_code=exit_code,
            started_at=entry.started_at,
            log=str(entry.log.relative_to(self.run_dir)) if keep_log else None,
            stamp=self.stamp,
        )


def _raise_interrupt(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


def _slug(task_id: str) -> str:
    """A file name for a task id: readable, and unique through a hash of the id."""
    readable = re.sub(r"[^A-Za-z0-9._-]+", "_", task_id).strip("_")[:80]
    return f"{readable}-{hashlib.sha1(task_id.encode()).hexdigest()[:8]}"
