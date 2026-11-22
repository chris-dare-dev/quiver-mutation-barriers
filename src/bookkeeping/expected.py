#!/usr/bin/env python3
"""expected.py -- the predicted values and the evidence of the tasks, read from the stored results.

Usage:  python3 src/bookkeeping/expected.py build DIRECTORY     write data/claims/expected.json
        python3 src/bookkeeping/expected.py check DIRECTORY     fail if data/claims/expected.json is not what `build` writes

DIRECTORY holds the files of the data archive (research/experiments/ after unpacking it, see data/README.md).

data/claims/expected.json maps a task id to its predicted value and to the stored results that carry the
original number, as file and line.  It has three kinds of entry:

  from the article   a value the article prints, typed in ARTICLE below, with the stored line that has it;
  stored counts      a number that exists only in a stored result (how many quivers a search reached, the
                     table of Conjecture 5.5, the counts of Section 13), copied from it;
  evidence only      for a task whose predicted value is a closed form (a barrier, a route): the stored
                     line where the original run found the same value.  The closed form is in
                     src/qmb/families.py, and this script stops if a stored value differs from it.

Nothing here is a record of a run.  A stored result says what an earlier program printed; a record
(data/records/) says what a task computed under the scheduler.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY / "src"))

from qmb.families import FAMILIES  # noqa: E402
from qmb.tasks import (  # noqa: E402
    EXPECTED,
    STAGES,
    np_qa_core_row,
    parse_conj55_summary,
    parse_counts,
    parse_review17,
)

# Values the article prints for its running example, R_8 = (-8, -8, 7, -2, 6, -8).
ARTICLE: dict[str, dict[str, Any]] = {
    "quiver/R/b=8": {"predicted": {"height": 8, "mutation_heights": [62, 24, 57, 48]}},
    "route/R/b=8": {"predicted": {"first_heights": [8, 24, 40, 56]}},
}


class Stored:
    """The files of the archive, read as lines."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def lines(self, name: str) -> list[str]:
        path = self.directory / name
        opener = gzip.open if name.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as handle:
            return handle.read().splitlines()

    def rows(self, name: str, key: str) -> dict[int, tuple[int, dict[str, Any]]]:
        """The JSON rows of a file by the value of `key`, each with its line number."""
        found = {}
        for number, line in enumerate(self.lines(name), start=1):
            if line.startswith("{"):
                row = json.loads(line)
                found[row[key]] = (number, row)
        return found


def _need(condition: bool, what: str) -> None:
    if not condition:
        raise SystemExit(f"expected.py: a stored result does not say what is expected: {what}")


def build(directory: Path) -> dict[str, Any]:
    stored = Stored(directory)
    tasks: dict[str, dict[str, Any]] = {}

    def add(task_id: str, evidence: list[dict[str, Any]], predicted: Any = None) -> None:
        entry = tasks.setdefault(task_id, {"evidence": []})
        entry["evidence"] += evidence
        if predicted is not None:
            entry["predicted"] = (
                entry.get("predicted", {}) | predicted if isinstance(predicted, dict) else predicted
            )

    def at(name: str, line: int, field: str | None = None) -> dict[str, Any]:
        return {"file": name, "line": line} | ({"field": field} if field else {})

    r, qt, pp, qa = (FAMILIES[key] for key in ("R", "Qt", "P+", "Qa"))

    # G_k: the symbolic rerun of the hand proof covers every k >= 3 at once
    for k in range(3, 61):
        for kind in ("quiver", "barrier", "reach", "route"):
            add(f"{kind}/G/k={k}", [{"file": "review12_handproof.log"}])

    # R_b: the searches of note 15 for 5 <= b <= 60
    name = "n4_doors_family3.log"
    for b, (line, row) in stored.rows(name, "b").items():
        _need(row["H"] == r.barrier(b) == row["escape"] and row["escape_reaches_mirror"], f"{name}:{line}")
        add(f"barrier/R/b={b}", [at(name, line, "escape")])
        if b % 2 == 0 and b >= 6:
            _need(row["route_ok"] and row["plateau_quivers"] == b * (b - 1) // 2, f"{name}:{line} route")
            add(f"route/R/b={b}", [at(name, line, "route_ok, plateau_quivers")])
    name = "owf_barrier_summary.log"
    tables = 0
    for line, text in enumerate(stored.lines(name), start=1):
        tables += text.startswith("## ")
        cells = [cell.strip() for cell in text.split("|")]
        head = cells[0].split()
        if tables == 1 and len(head) == 4 and head[0] == "R" and int(head[1]) <= 60:  # the generic attacker
            b = int(head[1])
            _need(
                int(head[3]) == r.barrier(b) and int(cells[1]) == b * (b - 1) // 2 + b + 1, f"{name}:{line}"
            )
            add(f"reach/R/b={b}", [at(name, line, "below H")], {"quivers": int(cells[4]), "low": 1})
            add(f"route/R/b={b}", [at(name, line, "L")])

    # Q_t: the searches of note 15 for 3 <= t <= 30
    name = "n4_doors_family.log"
    for t, (line, row) in stored.rows(name, "t").items():
        _need(row["H"] == qt.barrier(t) == row["escape"] and row["escape_reaches_mirror"], f"{name}:{line}")
        add(f"barrier/Qt/t={t}", [at(name, line, "escape")])

    # P+_t: the searches of note 16 for 2 <= t <= 64, and the second enumerator for 65 <= t <= 80
    name = "np_corridor_family_plus.jsonl"
    for t, (line, row) in stored.rows(name, "t").items():
        _need(
            row["H"] == pp.barrier(t) == row["at_H"]["iso"] and row["joined_to_opposite_at_exactly_H"],
            f"{name}:{line}",
        )
        _need(
            2 * row["route_steps_to_top"] + 2 == 4 * t**3 - 2 * t * t + 4 and row["top_height_is_H"],
            f"{name}:{line} route",
        )
        _need(row["no_other_low_quiver_below_H"], f"{name}:{line} region")
        count = {"quivers": row["below_H"]["popped"], "low": row["below_H"]["plateau"]}
        for suffix in ("", "@np_barrier"):
            add(f"barrier/P+/t={t}{suffix}", [at(name, line, "at_H.iso")])
            add(f"reach/P+/t={t}{suffix}", [at(name, line, "below_H.popped")], count)
        add(f"route/P+/t={t}", [at(name, line, "route_steps_to_top")])
        add(f"reach/P+/t={t}@review17", [at(name, line, "below_H.popped")], count)
    # the second enumerator of note 17: its own log for t <= 64, and the only source for 65 <= t <= 80
    for name in ("review17_plain.log", "review17_plain_65_80.log"):
        for line, text in enumerate(stored.lines(name), start=1):
            plain = parse_review17(text)
            if plain is not None:
                t = plain.t
                count = {"quivers": plain.quivers, "low": plain.low}
                _need(plain.barrier == pp.barrier(t), f"{name}:{line}")
                known = tasks.get(f"reach/P+/t={t}@review17", {}).get("predicted")
                _need(known is None or known == count, f"{name}:{line} against np_corridor_family_plus.jsonl")
                add(f"reach/P+/t={t}@review17", [at(name, line)], count)
                if t > 64:
                    add(f"reach/P+/t={t}@np_barrier", [at(name, line)], count)

    # Q_a: the route and the searches of note 18 (a <= 22), and the searches of note 20 (a <= 48, a <= 64)
    name = "np_rowwalk_family.jsonl"
    for a, (line, row) in stored.rows(name, "a").items():
        _need(
            row["H"] == qa.barrier(a) == row["at_H"]["iso"] and row["joined_to_opposite_at_exactly_H"],
            f"{name}:{line}",
        )
        _need(
            row["mutations"] == (2 * a + 2) * (4 * a * a - a + 6) and row["no_mutation_at_x"],
            f"{name}:{line} route",
        )
        _need(
            row["largest_entry_away_from_x"] <= 2 * a + 2 and row["route_height_is_H"], f"{name}:{line} route"
        )
        _need(row["quivers_at_H"] == (1 if a % 2 else 2 * a + 5), f"{name}:{line} top")
        count = {"quivers": row["below_H"]["popped"], "low": row["below_H"]["plateau"]}
        for suffix in ("", "@np_barrier"):
            add(f"barrier/Qa/a={a}{suffix}", [at(name, line, "at_H.iso")])
            add(f"reach/Qa/a={a}{suffix}", [at(name, line, "below_H.popped")], count)
        add(f"route/Qa/a={a}", [at(name, line, "mutations, quivers_at_H")])
    for name, pruned in (
        ("np_qa_core_family_nofork.jsonl", ""),
        ("np_qa_core_family.jsonl", "/forks-pruned"),
    ):
        for a, (line, row) in stored.rows(name, "a").items():
            core = np_qa_core_row(row)
            _need(core.barrier == qa.barrier(a) and core.ok and core.status == "closed", f"{name}:{line}")
            count = {"quivers": core.members, "low": core.low}
            add(f"reach/Qa/a={a}{pruned}@np_qa_core", [at(name, line, "members")], count)
            add(f"reach/Qa/a={a}{pruned}", [at(name, line, "members")], count)

    # Conjecture 5.5: the table of the run to height 18
    name = "n4_conj55_N18_summary.log"
    lines = stored.lines(name)
    summary = parse_conj55_summary("\n".join(lines))
    row_line = {
        cells[1].strip(): n
        for n, text in enumerate(lines, start=1)
        if (cells := text.split("|"))[0] == "" and len(cells) > 2
    }
    for h, counted in summary["heights"].items():
        add(
            f"conj55/h={h}",
            [at(name, row_line[h])],
            {"quivers": counted["quivers"], "reach_acyclic": counted["reach_acyclic"]},
        )
    for bound in range(2, 18):
        rows = {h: counted for h, counted in summary["heights"].items() if int(h) <= bound}
        add(f"conj55_program/N={bound}", [{"file": name, "lines": [3, bound + 2]}], {"heights": rows})
    add("conj55_program/N=18", [{"file": name}], summary)

    # Sections 8 and 13: the counts in the logs of the stages
    for stage_name, log in (
        ("finite-cores", "n4_opposite_cores.log"),
        ("tube-certificates-note-14", "n4_opposite_tubes.log"),
        ("tube-certificates-note-22", "n4_tube_certify2.log"),
        ("decided-classes", "review23_n22_counts.log"),
    ):
        stage = STAGES[stage_name]
        counts = parse_counts(stage, "\n".join(stored.lines(log)))
        _need(counts is not None, f"{log}: a count of the stage {stage_name} is missing")
        add(f"{stage.kind}/{stage_name}", [{"file": log}], counts)

    for task_id, entry in ARTICLE.items():
        add(task_id, [], entry["predicted"])
        tasks[task_id]["typed_from_the_article"] = sorted(entry["predicted"])

    # the checksum of the archive as data/README.md states it (dist/ is not in git)
    stated = re.search(
        r"^\| SHA-256 \| `([0-9a-f]{64})` \|$", (REPOSITORY / "data" / "README.md").read_text(), re.MULTILINE
    )
    archive = stated[1] if stated else None
    return {"archive_sha256": archive, "tasks": dict(sorted(tasks.items()))}


def render(content: dict[str, Any]) -> str:
    lines = ["{", f' "archive_sha256": {json.dumps(content["archive_sha256"])},', ' "tasks": {']
    entries = [
        f"  {json.dumps(key)}: {json.dumps(entry, sort_keys=True)}" for key, entry in content["tasks"].items()
    ]
    return "\n".join([*lines, ",\n".join(entries), " }", "}"]) + "\n"


def main(arguments: list[str]) -> int:
    if len(arguments) != 2 or arguments[0] not in {"build", "check"}:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    text = render(build(Path(arguments[1])))
    if arguments[0] == "build":
        EXPECTED.parent.mkdir(exist_ok=True)
        EXPECTED.write_text(text, encoding="utf-8")
        print(
            f"wrote {EXPECTED.relative_to(REPOSITORY)}: {text.count(chr(10)) - 4} tasks, sha256 {hashlib.sha256(text.encode()).hexdigest()[:12]}"
        )
        return 0
    if not EXPECTED.exists() or EXPECTED.read_text(encoding="utf-8") != text:
        print(
            "data/claims/expected.json differs from what the stored results give: run src/bookkeeping/expected.py build",
            file=sys.stderr,
        )
        return 1
    print("data/claims/expected.json agrees with the stored results")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
