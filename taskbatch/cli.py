"""Command line: plan a batch, run it, report on its results."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import socket
import sys
from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__, report
from .config import BatchConfig, ConfigError, load_config
from .memory import available_mb, choose_guard
from .model import COMPLETED_STATUSES, Limits, Status, Task
from .runner import RunnerError, code_version, expand
from .scheduler import Scheduler
from .settings import REPOSITORY, SettingsError, load_settings
from .store import ResultStore, StoreLocked

EXIT_OK = 0
EXIT_FAILED = 1  # a mismatch, an error or a crash
EXIT_USAGE = 2
EXIT_LIMITS = 3  # nothing failed, but some tasks were stopped at a limit
EXIT_INTERRUPTED = 130


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="taskbatch", description="Run batches of tasks under time and memory limits."
    )
    parser.add_argument("--version", action="version", version=f"taskbatch {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    def batch_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("batch", type=Path, help="the batch file (TOML)")
        command.add_argument("--out", type=Path, help="run directory (default: results/<name of the batch>)")
        command.add_argument("--workers", type=int, help="task processes at a time")
        command.add_argument(
            "--memory-budget", type=int, metavar="MB", help="sum of the memory limits allowed at a time"
        )
        command.add_argument("--time-limit", type=float, metavar="S", help="default time limit of a task")
        command.add_argument("--memory-limit", type=int, metavar="MB", help="default memory limit of a task")
        command.add_argument(
            "--retry", default="", metavar="STATUS[,STATUS]",
            help="compute again the tasks whose latest record has one of these statuses",
        )  # fmt: skip
        command.add_argument(
            "--runner", help="command that expands batches and runs tasks (default: the repository's runner)"
        )

    plan = commands.add_parser("plan", help="list what a run would compute, without computing")
    batch_arguments(plan)

    run = commands.add_parser("run", help="compute the tasks of a batch that have no record yet")
    batch_arguments(run)
    run.add_argument(
        "--memory-guard", choices=["auto", "cgroup", "poll"], default="auto",
        help="how memory limits are enforced (default: cgroup where systemd offers it, else poll)",
    )  # fmt: skip
    run.add_argument(
        "--overcommit", action="store_true",
        help="run even if the memory budget is above the memory now available",
    )  # fmt: skip
    run.add_argument("--quiet", action="store_true", help="do not print a line per task")

    rep = commands.add_parser("report", help="print tables from the records of a run directory")
    rep.add_argument("run_dir", type=Path)
    rep.add_argument(
        "--full", action="store_true", help="list every computed value against its predicted value"
    )
    return parser


def _prepare(arguments: argparse.Namespace) -> tuple[BatchConfig, tuple[str, ...], Path, frozenset[str]]:
    settings = load_settings()
    config = load_config(arguments.batch, description_keys=settings.description_keys).with_overrides(
        workers=arguments.workers,
        memory_budget_mb=arguments.memory_budget,
        time_seconds=arguments.time_limit,
        memory_mb=arguments.memory_limit,
    )
    runner = tuple(shlex.split(arguments.runner)) if arguments.runner else settings.runner
    if runner is None:
        raise ConfigError("no runner: pass --runner, or set runner in [tool.taskbatch] of pyproject.toml")
    run_dir = arguments.out or REPOSITORY / "results" / config.name
    retry = frozenset(name for name in arguments.retry.split(",") if name)
    unknown = retry - {str(status) for status in Status}
    if unknown:
        raise ConfigError(f"--retry: unknown status {sorted(unknown)[0]!r}")
    return config, runner, run_dir, retry


def _plan_lines(
    config: BatchConfig, tasks: Sequence[Task], pending: Sequence[tuple[Task, Limits]]
) -> list[str]:
    recorded = len(tasks) - len(pending)
    lines = [
        f"batch {config.name}: {len(tasks)} tasks, {len(pending)} to compute, {recorded} already recorded",
        f"workers {config.workers}, memory budget {config.memory_budget_mb} MB",
    ]
    classes: Counter[tuple[float, int]] = Counter(
        (limits.time_seconds, limits.memory_mb) for _, limits in pending
    )
    for (time_seconds, memory_mb), count in sorted(classes.items()):
        alone = " (one at a time)" if 2 * memory_mb > config.memory_budget_mb else ""
        lines.append(f"  {count:5d} tasks with limits {time_seconds:g} s, {memory_mb} MB{alone}")
    return lines


def _command_plan(arguments: argparse.Namespace) -> int:
    config, runner, run_dir, retry = _prepare(arguments)
    tasks, _ = expand(runner, config.description)
    scheduler = Scheduler(
        config=config, tasks=tasks, store=ResultStore(run_dir / "results.jsonl"),
        run_dir=run_dir, runner=runner, guard=choose_guard("poll"), retry=retry,
    )  # fmt: skip
    pending = scheduler.pending()
    print("\n".join(_plan_lines(config, tasks, pending)))
    for task, limits in pending:
        print(f"{task.cost:8g}  {limits.time_seconds:8g} s  {limits.memory_mb:7d} MB  {task.id}")
    return EXIT_OK


def _command_run(arguments: argparse.Namespace) -> int:
    config, runner, run_dir, retry = _prepare(arguments)
    free = available_mb()
    if free is not None and config.memory_budget_mb > free and not arguments.overcommit:
        raise ConfigError(
            f"the memory budget is {config.memory_budget_mb} MB but only {free} MB is available now; "
            "lower --memory-budget, or pass --overcommit to run anyway"
        )
    guard = choose_guard(arguments.memory_guard)
    tasks, runner_versions = expand(runner, config.description)

    started_at = datetime.now(UTC)
    run_id = f"{started_at:%Y%m%dT%H%M%SZ}-{os.getpid()}"
    code = code_version()
    store = ResultStore(run_dir / "results.jsonl")
    with store:
        scheduler = Scheduler(
            config=config, tasks=tasks, store=store, run_dir=run_dir, runner=runner, guard=guard,
            stamp={"run_id": run_id, "runner": runner_versions, "code": code},
            retry=retry, progress=None if arguments.quiet else _print_progress,
        )  # fmt: skip
        pending = scheduler.pending()
        _write_json(
            run_dir / "manifest.json",
            {
                "batch": config.name,
                "tasks": [task.payload | {"limits": config.limits_for(task).as_dict()} for task in tasks],
            },
        )
        _append_json(
            run_dir / "runs.jsonl",
            {
                "run_id": run_id,
                "started_at": started_at.isoformat(timespec="seconds"),
                "command": sys.argv,
                "batch_file": str(arguments.batch),
                "config": config.as_dict(),
                "retry": sorted(retry),
                "runner_command": list(runner),
                "runner": runner_versions,
                "code": code,
                "memory_guard": guard.name,
                "memory_available_mb": free,
                "host": socket.gethostname(),
                "cpus": os.cpu_count(),
                "tasks": len(tasks),
                "pending": len(pending),
            },
        )
        print("\n".join(_plan_lines(config, tasks, pending)), file=sys.stderr)
        print(f"memory guard: {guard.name}; results in {run_dir}", file=sys.stderr)
        try:
            outcome = scheduler.run()
        except KeyboardInterrupt:
            print("interrupted: tasks in flight were stopped and have no record", file=sys.stderr)
            return EXIT_INTERRUPTED

    summary = ", ".join(f"{count} {status}" for status, count in sorted(outcome.items())) or "nothing to do"
    print(f"this run: {summary}", file=sys.stderr)
    latest = store.latest()
    statuses = Counter(latest[task.id]["status"] for task in tasks if task.id in latest)
    if statuses[Status.MISMATCH] or statuses[Status.ERROR] or statuses[Status.CRASHED]:
        return EXIT_FAILED
    if any(count for status, count in statuses.items() if status not in COMPLETED_STATUSES):
        return EXIT_LIMITS
    return EXIT_OK


def _print_progress(record: dict[str, Any], done: int, total: int) -> None:
    note = ""
    if record["status"] == Status.MISMATCH:
        note = f"  computed {report._cell(record['value'])}, predicted {report._cell(record['predicted'])}"
    elif record["error"]:
        note = "  " + record["error"].splitlines()[-1]
    print(
        f"[{done}/{total}] {record['status']:<11} {record['wall_seconds']:8.1f} s "
        f"{record['peak_rss_mb']:7.0f} MB  {record['task_id']}{note}",
        file=sys.stderr, flush=True,
    )  # fmt: skip


def _write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_text(json.dumps(content, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _append_json(path: Path, content: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(content, sort_keys=True) + "\n")


def _command_report(arguments: argparse.Namespace) -> int:
    if not (arguments.run_dir / "results.jsonl").exists():
        raise ConfigError(f"no results.jsonl in {arguments.run_dir}")
    sys.stdout.write(report.render(arguments.run_dir, full=arguments.full))
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    commands = {"plan": _command_plan, "run": _command_run, "report": _command_report}
    try:
        return commands[arguments.command](arguments)
    except (ConfigError, SettingsError, RunnerError, StoreLocked, RuntimeError, FileNotFoundError) as problem:
        print(f"taskbatch: {problem}", file=sys.stderr)
        return EXIT_USAGE
