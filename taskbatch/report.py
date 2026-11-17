"""Tables from the records of a batch: computed against predicted, mismatches, timeouts, kills."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .model import Status
from .store import ResultStore

NOT_RUN = "not run"
COLUMNS = [str(status) for status in Status] + [NOT_RUN]


def _cell(value: Any) -> str:
    """A value as it appears in a table cell."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, dict):
        return ", ".join(f"{key} {_cell(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "(" + ", ".join(_cell(item) for item in value) + ")"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value).replace("|", "\\|")


def _table(header: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(_cell(item) for item in row) + " |" for row in rows]
    return [*lines, ""]


def _name(record: dict[str, Any]) -> str:
    return f"`{record['task_id']}`"


def load_manifest(run_dir: Path) -> list[dict[str, Any]]:
    """The tasks of the run's latest expansion; empty if the run has no manifest."""
    path = run_dir / "manifest.json"
    if not path.exists():
        return []
    tasks: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8")).get("tasks", [])
    return tasks


def render(run_dir: Path, *, full: bool = False) -> str:
    """The report of a run directory, as Markdown."""
    store = ResultStore(run_dir / "results.jsonl")
    latest = store.latest()
    manifest = load_manifest(run_dir)
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    known = set()
    for task in manifest:
        known.add(task["id"])
        record = latest.get(task["id"])
        groups[task.get("group", task["kind"])][record["status"] if record else NOT_RUN] += 1
    for task_id, record in latest.items():
        if task_id not in known:
            groups[record["task"].get("group", record["task"].get("kind", "?"))][record["status"]] += 1
    records = sorted(latest.values(), key=lambda r: (r["task"].get("group", ""), r["task_id"]))

    lines = [f"# Results in {run_dir.name}", ""]
    lines += _provenance(records, store.unreadable_lines)

    lines += ["## Summary", ""]
    used = [column for column in COLUMNS if any(counts[column] for counts in groups.values())]
    lines += _table(
        ["group", "tasks", *used],
        [
            [group, counts.total(), *(counts[column] for column in used)]
            for group, counts in sorted(groups.items())
        ],
    )

    def section(title: str, statuses: set[str], header: list[str], row: Any) -> None:
        chosen = [record for record in records if record["status"] in statuses]
        if chosen:
            lines.extend([f"## {title}", ""])
            lines.extend(_table(header, [row(record) for record in chosen]))

    section(
        "Computed values that differ from the predicted ones",
        {Status.MISMATCH},
        ["task", "computed", "predicted"],
        lambda r: [_name(r), r["value"], r["predicted"]],
    )
    section(
        "Stopped at a limit",
        {Status.TIMEOUT, Status.MEMORY},
        ["task", "status", "cost", "time limit (s)", "memory limit (MB)", "wall (s)", "peak (MB)"],
        lambda r: [
            _name(r),
            r["status"],
            r["task"].get("cost"),
            r["limits"]["time_seconds"],
            r["limits"]["memory_mb"],
            r["wall_seconds"],
            r["peak_rss_mb"],
        ],
    )
    section(
        "Errors and crashes",
        {Status.ERROR, Status.CRASHED},
        ["task", "status", "message", "log"],
        lambda r: [_name(r), r["status"], (r["error"] or "").replace("\n", "; "), r["log"]],
    )
    section(
        "No method",
        {Status.UNSUPPORTED},
        ["task", "predicted"],
        lambda r: [_name(r), r["predicted"]],
    )
    if full:
        section(
            "Computed against predicted",
            {Status.OK, Status.MISMATCH},
            ["task", "computed", "predicted", "agrees", "method", "wall (s)", "peak (MB)"],
            lambda r: [
                _name(r),
                r["value"],
                r["predicted"],
                r["agrees"],
                r["detail"].get("method"),
                r["wall_seconds"],
                r["peak_rss_mb"],
            ],
        )
    else:
        slowest = sorted(
            (r for r in records if r["status"] in {Status.OK, Status.MISMATCH}),
            key=lambda r: -r["wall_seconds"],
        )[:10]
        if slowest:
            lines += ["## Slowest computed tasks", ""]
            lines += _table(
                ["task", "cost", "wall (s)", "peak (MB)"],
                [[_name(r), r["task"].get("cost"), r["wall_seconds"], r["peak_rss_mb"]] for r in slowest],
            )
    return "\n".join(lines).rstrip() + "\n"


def _provenance(records: list[dict[str, Any]], unreadable: int) -> list[str]:
    def distinct(pick: Any) -> str:
        values = sorted({str(value) for value in map(pick, records) if value is not None})
        return ", ".join(values) if values else "unknown"

    lines = [
        f"- records: {len(records)}",
        f"- code: {distinct(lambda r: r.get('code', {}).get('commit'))}",
        f"- runner: {distinct(lambda r: _cell(r.get('runner')) or None)}",
        f"- wall time of all tasks: {sum(r['wall_seconds'] for r in records):.0f} s",
    ]
    if any(r.get("code", {}).get("dirty") for r in records):
        lines.append("- some records come from a working tree with uncommitted changes")
    if unreadable:
        lines.append(f"- {unreadable} unreadable line(s) in results.jsonl were ignored")
    return [*lines, ""]
