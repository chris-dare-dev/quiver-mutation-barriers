#!/usr/bin/env python3
"""claims.py -- the claim tables, written from the registry, the batch files and the records.

Usage:  python3 tools/claims.py tables              write the generated parts of CLAIMS.md and README.md,
                                                     and claims/RECORDS.md
        python3 tools/claims.py check               fail if they are not what `tables` writes, or if the
                                                     registry and the batch files do not fit together
        python3 tools/claims.py headline DIRECTORY  print the headline table from the records under
                                                     DIRECTORY (for example results), and fail if it is
                                                     not the one in README.md
        python3 tools/claims.py adopt RUN_DIR ...   copy the records of finished runs (results/<batch>)
                                                     into records/<batch>

What is read:  claims/claims.toml (the claims and the tasks that compute them), batches/*.toml (which
tasks exist), claims/expected.json (predicted values and stored evidence), records/<batch>/results.jsonl
(what was computed here).  A task without a record reads "not re-run", whatever the stored results say.

`adopt` copies results.jsonl and manifest.json unchanged, and refuses records that were computed from a
working tree with uncommitted changes: a record must name the commit of the code that computed it.
"""

from __future__ import annotations

import fnmatch
import re
import shutil
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY))

from qmb.tasks import expand_batch, load_expected  # noqa: E402
from taskbatch.config import load_config  # noqa: E402
from taskbatch.store import ResultStore  # noqa: E402

REGISTRY = REPOSITORY / "claims" / "claims.toml"
RECORDS = REPOSITORY / "records"
DETAIL = REPOSITORY / "claims" / "RECORDS.md"
NOT_RERUN = "not re-run"
STATUSES = ["ok", "mismatch", "unsupported", "timeout", "memory", "error", "crashed", NOT_RERUN]


class RegistryError(ValueError):
    """The registry, the batch files and the records do not fit together."""


# ---------------------------------------------------------------------------------------------------
# reading


def load_registry() -> dict[str, Any]:
    with REGISTRY.open("rb") as handle:
        registry: dict[str, Any] = tomllib.load(handle)
    return registry


def batch_tasks() -> dict[str, dict[str, Any]]:
    """Every task of every batch file by id, each with the names of the batches that contain it."""
    expected = load_expected()
    tasks: dict[str, dict[str, Any]] = {}
    for path in sorted((REPOSITORY / "batches").glob("*.toml")):
        for task in expand_batch(load_config(path).description, expected):
            tasks.setdefault(task["id"], task | {"batches": []})["batches"].append(path.stem)
    return tasks


def latest_records(root: Path) -> dict[str, dict[str, Any]]:
    """The most recent record of each task over the run directories under `root`."""
    latest: dict[str, dict[str, Any]] = {}
    if not root.is_dir():
        return latest
    for run_dir in sorted(path for path in root.iterdir() if (path / "results.jsonl").is_file()):
        for task_id, record in ResultStore(run_dir / "results.jsonl").latest().items():
            known = latest.get(task_id)
            if known is None or record["started_at"] > known["started_at"]:
                latest[task_id] = record | {"batch": run_dir.name}
    return latest


def _natural(text: str) -> list[Any]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text)]


def claim_tasks(claim: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> list[str]:
    """The ids of the tasks of a claim, negative controls left out."""
    chosen = {
        task_id
        for pattern in claim["tasks"]
        for task_id in fnmatch.filter(tasks, pattern)
        if not tasks[task_id].get("control")
    }
    return sorted(chosen, key=_natural)


def validate(registry: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> None:
    problems = []
    ids = [claim["id"] for claim in registry["claim"]]
    problems += [f"two claims have the id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    claimed: set[str] = set()
    for claim in registry["claim"]:
        table = registry["table"].get(claim["table"])
        if table is None:
            problems.append(f"{claim['id']}: no table {claim['table']!r}")
        elif len(claim["cells"]) != len(table["columns"]):
            problems.append(f"{claim['id']}: {len(claim['cells'])} cells for {len(table['columns'])} columns")
        if bool(claim["tasks"]) == ("no_task" in claim):
            problems.append(f"{claim['id']}: a claim has either tasks or a reason under no_task")
        for pattern in claim["tasks"]:
            if not fnmatch.filter(tasks, pattern):
                problems.append(f"{claim['id']}: no task of any batch matches {pattern!r}")
        claimed.update(claim_tasks(claim, tasks))
    for task_id, task in tasks.items():
        if task["kind"] != "synthetic" and not task.get("control") and task_id not in claimed:
            problems.append(f"the task {task_id} ({', '.join(task['batches'])}) belongs to no claim")
    for row in registry["headline"]:
        if "smoke" not in tasks.get(row["task"], {}).get("batches", []):
            problems.append(f"headline: {row['task']} is not a task of batches/smoke.toml")
    if problems:
        raise RegistryError("\n".join(problems))


# ---------------------------------------------------------------------------------------------------
# writing


def cell(value: Any, limit: int = 160) -> str:
    """A value as it appears in a table cell."""
    if value is None:
        text = ""
    elif isinstance(value, bool):
        text = "yes" if value else "no"
    elif isinstance(value, dict):
        text = ", ".join(f"{key} {cell(item, 10**9)}" for key, item in value.items())
    elif isinstance(value, list):
        text = "(" + ", ".join(cell(item, 10**9) for item in value) + ")"
    elif isinstance(value, int):
        text = f"{value:,}"
    else:
        text = str(value)
    text = text.replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def table(header: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
        *("| " + " | ".join(row) + " |" for row in rows),
    ]


def anchor(claim_id: str) -> str:
    return "claim-" + re.sub(r"[^a-z0-9]+", "-", claim_id.lower()).strip("-")


def stamp(records: list[dict[str, Any]]) -> str:
    """When and from which commits a set of records comes."""
    days = sorted({record["started_at"][:10] for record in records})
    commits = sorted({(record.get("code") or {}).get("commit") or "unknown commit" for record in records})
    when = days[0] if len(days) == 1 else f"{days[0]} to {days[-1]}"
    return f"{when}, " + ", ".join(f"`{commit[:7]}`" for commit in commits)


def summary(
    claim: dict[str, Any], tasks: dict[str, dict[str, Any]], latest: dict[str, dict[str, Any]]
) -> str:
    """The last cell of a claim's row: what the scheduler's records say about it."""
    chosen = claim_tasks(claim, tasks)
    if not chosen:
        return f"no task: {claim['no_task']}"
    recorded = [latest[task_id] for task_id in chosen if task_id in latest]
    counts = Counter(record["status"] for record in recorded)
    counts[NOT_RERUN] = len(chosen) - len(recorded)
    link = f"[tasks](claims/RECORDS.md#{anchor(claim['id'])})"
    if not recorded:
        batches = sorted({batch for task_id in chosen for batch in tasks[task_id]["batches"]})
        where = ", ".join(f"`{batch}`" for batch in batches)
        return f"**{NOT_RERUN}**: {len(chosen)} {_plural(len(chosen), 'task')} in {where}, no record; {link}"
    parts = [f"{status} {counts[status]}" for status in STATUSES if counts[status]]
    lead = (
        f"**ok**, all {len(chosen)} tasks"
        if counts["ok"] == len(chosen)
        else "; ".join(parts) + f" (of {len(chosen)} tasks)"
    )
    return f"{lead}; {stamp(recorded)}; {link}"


def _plural(count: int, word: str) -> str:
    return word if count == 1 else word + "s"


def claims_table(
    slug: str, registry: dict[str, Any], tasks: dict[str, dict[str, Any]], latest: dict[str, dict[str, Any]]
) -> list[str]:
    spec = registry["table"][slug]
    rows = [
        [*claim["cells"], summary(claim, tasks, latest)]
        for claim in registry["claim"]
        if claim["table"] == slug
    ]
    return table([*spec["columns"], "Re-run under the scheduler"], rows)


def evidence_cell(task: dict[str, Any]) -> str:
    parts = []
    for item in task.get("evidence", []):
        where = f"`{item['file']}`"
        if "line" in item:
            where += f", line {item['line']}"
        elif "lines" in item:
            where += f", lines {item['lines'][0]} to {item['lines'][1]}"
        if "field" in item:
            where += f" ({item['field']})"
        parts.append(where)
    return "; ".join(parts)


def detail(
    registry: dict[str, Any], tasks: dict[str, dict[str, Any]], latest: dict[str, dict[str, Any]]
) -> str:
    """claims/RECORDS.md: every claim with its tasks, one row per task."""
    lines = [
        "# Tasks and records, claim by claim",
        "",
        "Generated by `tools/claims.py tables`; do not edit. For every claim of [CLAIMS.md](../CLAIMS.md) that has tasks: "
        "each task with its predicted value, the stored result that carries the original number (a file of the data "
        "archive, [DATA.md](../DATA.md)), and the latest record of the task under the scheduler, if there is one. "
        f'A task without a record reads "{NOT_RERUN}": the stored result is then the only support, and it is the '
        "original output, not a run of this repository.",
        "",
        "A predicted value is a closed form of the article, a number the article prints, or a count copied from a "
        'stored result ([expected.json](expected.json) says which). "Computed" is what the task found; the status is '
        "`ok` when the two agree. A record names the day it was computed and the commit of the code.",
        "",
    ]
    for claim in registry["claim"]:
        chosen = claim_tasks(claim, tasks)
        if not chosen:
            continue
        lines += [f'<a name="{anchor(claim["id"])}"></a>', "", f"## {claim['id']}", "", claim["cells"][0], ""]
        rows = []
        for task_id in chosen:
            task, record = tasks[task_id], latest.get(task_id)
            if record is None:
                state, computed = NOT_RERUN, ""
            else:
                state = f"{record['status']}, {record['started_at'][:10]}, `{((record.get('code') or {}).get('commit') or 'unknown')[:7]}`, {record['wall_seconds']:g} s"
                computed = cell(record["value"])
            rows.append([
                f"`{task_id}`", ", ".join(task["batches"]), cell(task.get("predicted")), evidence_cell(task), state, computed,
            ])  # fmt: skip
        lines += table(["Task", "Batches", "Predicted", "Stored evidence", "Record", "Computed"], rows)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def headline(
    registry: dict[str, Any], tasks: dict[str, dict[str, Any]], latest: dict[str, dict[str, Any]]
) -> list[str]:
    rows = []
    for row in registry["headline"]:
        task, record = tasks[row["task"]], latest.get(row["task"])
        key = row.get("key")

        def pick(value: Any, key: str | None = key) -> Any:
            return value.get(key) if key and isinstance(value, dict) else value

        rows.append([
            row["label"], cell(pick(task.get("predicted"))),
            "" if record is None else cell(pick(record["value"])),
            NOT_RERUN if record is None else record["status"], f"`{row['task']}`",
        ])  # fmt: skip
    return table(["Quantity", "Predicted", "Computed", "Status", "Task"], rows)


def blocks(
    registry: dict[str, Any], tasks: dict[str, dict[str, Any]], latest: dict[str, dict[str, Any]]
) -> dict[Path, dict[str, list[str]]]:
    """The generated parts of the hand-written files, by file and name."""
    return {
        REPOSITORY / "CLAIMS.md": {
            slug: claims_table(slug, registry, tasks, latest) for slug in registry["table"]
        },
        REPOSITORY / "README.md": {"headline": headline(registry, tasks, latest)},
    }


def splice(text: str, name: str, lines: list[str], path: Path) -> str:
    begin, end = f"<!-- BEGIN GENERATED {name}: tools/claims.py tables -->", f"<!-- END GENERATED {name} -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise RegistryError(f"{path.name} needs exactly one pair of markers for the generated part {name!r}")
    head, rest = text.split(begin)
    _, tail = rest.split(end)
    return head + begin + "\n" + "\n".join(lines) + "\n" + end + tail


def outputs() -> dict[Path, str]:
    registry, tasks, latest = load_registry(), batch_tasks(), latest_records(RECORDS)
    validate(registry, tasks)
    written = {DETAIL: detail(registry, tasks, latest)}
    for path, parts in blocks(registry, tasks, latest).items():
        text = path.read_text(encoding="utf-8")
        for name, lines in parts.items():
            text = splice(text, name, lines, path)
        written[path] = text
    return written


# ---------------------------------------------------------------------------------------------------
# commands


def command_tables() -> int:
    for path, text in outputs().items():
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(REPOSITORY)}")
    return 0


def command_check() -> int:
    stale = [
        path
        for path, text in outputs().items()
        if not path.exists() or path.read_text(encoding="utf-8") != text
    ]
    for path in stale:
        print(
            f"{path.relative_to(REPOSITORY)} is not what the registry and the records give: run `make tables`",
            file=sys.stderr,
        )
    if not stale:
        print("the generated tables agree with the registry, the batch files and the records")
    return 1 if stale else 0


def command_headline(root: Path) -> int:
    registry, tasks = load_registry(), batch_tasks()
    lines = headline(registry, tasks, latest_records(root))
    print("\n".join(lines))
    readme = (REPOSITORY / "README.md").read_text(encoding="utf-8")
    if splice(readme, "headline", lines, REPOSITORY / "README.md") != readme:
        print("\nthis is NOT the headline table of README.md", file=sys.stderr)
        return 1
    print("\nthis is the headline table of README.md")
    return 0


def command_adopt(run_dirs: list[Path]) -> int:
    for run_dir in run_dirs:
        records = list(ResultStore(run_dir / "results.jsonl").latest().values())
        if not records:
            raise RegistryError(f"no records in {run_dir}")
        dirty = [r["task_id"] for r in records if (r.get("code") or {}).get("dirty") is not False]
        if dirty:
            raise RegistryError(
                f"{run_dir}: {len(dirty)} records, among them {dirty[0]}, were computed from a working tree with "
                "uncommitted changes or outside a checkout; commit the code and run the batch again"
            )
        target = RECORDS / run_dir.name
        target.mkdir(parents=True, exist_ok=True)
        for name in ("results.jsonl", "manifest.json"):
            shutil.copyfile(run_dir / name, target / name)
        print(f"records/{run_dir.name}: {len(records)} records, {stamp(records)}")
    return 0


def main(arguments: list[str]) -> int:
    try:
        if arguments == ["tables"]:
            return command_tables()
        if arguments == ["check"]:
            return command_check()
        if len(arguments) == 2 and arguments[0] == "headline":
            return command_headline(Path(arguments[1]))
        if len(arguments) >= 2 and arguments[0] == "adopt":
            return command_adopt([Path(argument) for argument in arguments[1:]])
    except (RegistryError, ValueError, OSError) as problem:
        print(f"claims.py: {problem}", file=sys.stderr)
        return 1
    print((__doc__ or "").split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
