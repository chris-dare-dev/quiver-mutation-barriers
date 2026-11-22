"""census, core, tube: one stage of Sections 8 and 13, by its own program, on the stored inputs.

    stages, procs, sample

STAGES names each program with its kind, the stored results it reads and the lines of its output that are
its counts.  `sample` runs the first command of a stage on a random sample of that many classes, where
its program can take one.  A task carries `stage`, `procs`, `sample` and `inputs`.

Predicted: the counts of the stored logs, which data/claims/expected.json holds; `parse_counts` reads them
from a program's output, here and when src/bookkeeping/expected.py reads a stored log.
"""

from __future__ import annotations

import os
import re
import shutil
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from ..backends import EXPERIMENTS, REPOSITORY, BackendError, keep_output, program, require, scratch
from .base import Common, Kind, Result, Table, TaskError, known


class StageTask(Common):
    stage: str  # a key of STAGES
    procs: int
    sample: int | None  # so many classes, drawn at random, instead of all of them
    inputs: list[str]
    article: str


CENSUS_FILES = [
    "n4_classes_B512.jsonl",
    "n4_classes_k5_B512.jsonl",
    "n4_classes_k67_B256.jsonl",
    "n4_classes_k8_B192.jsonl.gz",
    "n4_classes_k9_B192.jsonl.gz",
]


@dataclass(frozen=True)
class Stage:
    """One program of Sections 8 and 13, run on stored inputs, and the lines of its output that count."""

    kind: str
    commands: tuple[tuple[str, ...], ...]  # each: a script, relative to the repository, and its arguments
    inputs: tuple[str, ...]  # stored results the program reads, by the names it expects
    counts: tuple[tuple[str, str], ...]  # (key, pattern with one group) searched in the output
    modules: tuple[str, ...]
    cost: int
    article: str
    sample: bool = False  # the first command takes `--limit N`: a random sample of N classes


STAGES: dict[str, Stage] = {
    "finite-cores": Stage(
        kind="core",
        commands=(
            (
                "research/experiments/n4_opposite_run.py",
                "cores",
                "--cap",
                "800",
                "--level-cap",
                "1000000",
                "--procs",
                "{procs}",
                "--out",
                "n4_opposite_cores.jsonl.gz",
            ),
        ),
        inputs=tuple(CENSUS_FILES),
        counts=(
            ("classes", r"^(\d+) census classes read"),
            ("finite_cores", r"^total: core found (\d+),"),
            ("search_stopped_at_a_cap", r"^total: core found \d+, search stopped at a cap (\d+) "),
        ),
        modules=("numpy",),
        cost=600,
        article="Section 13",
    ),
    "tube-certificates-note-14": Stage(
        kind="tube",
        commands=(
            (
                "research/experiments/n4_opposite_tubes.py",
                "run",
                "--procs",
                "{procs}",
                "--cores",
                "n4_opposite_cores.jsonl.gz",
                "--out",
                "n4_opposite_tubes.jsonl.gz",
            ),
        ),
        inputs=("n4_opposite_cores.jsonl.gz",),
        # `run` ends with the summary of what it wrote
        counts=(("classes", r"^(\d+) classes$"), ("certified", r"^certified: (\d+);")),
        sample=True,
        modules=("numpy",),
        cost=3600,
        article="Section 13",
    ),
    "tube-certificates-note-22": Stage(
        kind="tube",
        commands=(
            (
                "research/experiments/n4_tube_lemma.py",
                "certify2",
                "--budget",
                "12",
                "--procs",
                "{procs}",
                "--out",
                "n4_tube_certify2.jsonl.gz",
            ),
        ),
        inputs=("n4_tube_classify.jsonl.gz", "n4_opposite_tubes.jsonl.gz", "n4_opposite_plateaus.jsonl.gz"),
        counts=(
            ("classes", r"^(\d+) classes; second-pass"),
            ("certified", r"^certified: (\d+); with a bottom"),
        ),
        sample=True,
        modules=("numpy",),
        cost=2700,
        article="Section 13",
    ),
    "decided-classes": Stage(
        kind="census",
        commands=(("research/verify/review23_n22_counts.py",),),
        inputs=(
            "n4_opposite_cores.jsonl.gz",
            "n4_opposite_plateaus.jsonl.gz",
            "n4_opposite_tubes.jsonl.gz",
            "n4_tube_certify2.jsonl.gz",
            "n4_tube_classify.jsonl.gz",
        ),
        counts=(
            ("classes", r"^census classes: (\d+);"),
            ("mirror_pairs", r"^mirror map: .* pairs (\d+)$"),
            ("finite_cores", r"^finite cores (\d+);"),
            ("tube_certificates_note_14", r"note-14 tube certificates (\d+);"),
            ("tube_certificates_note_22", r"note-22 certificates (\d+);"),
            ("disconnected", r"^\s+disconnected\s+\{'classes': (\d+),"),
            ("acyclic_bottom", r"^\s+acyclic bottom\s+\{'classes': (\d+),"),
            ("open_classes", r"open classes (\d+):"),
            (
                "settled_by_cores_and_tubes",
                r"pairwise distinct \(finite cores \+ tube certificates\): (\d+);",
            ),
            ("decided", r"covered: (\d+)$"),
        ),
        modules=(),
        cost=20,
        article="Section 13",
    ),
}


def _expander(kind: str) -> Callable[[Table, str], Iterator[StageTask]]:
    def expand(table: Table, where: str) -> Iterator[StageTask]:
        known(table, where, "stages", "procs", "sample")
        procs, sample = table.get("procs", 4), table.get("sample")
        names = table.get("stages")
        if not isinstance(names, list) or not names or type(procs) is not int or procs < 1:
            raise TaskError(f"{where} needs a list of stages, and procs at least 1")
        if sample is not None and (type(sample) is not int or sample < 1):
            raise TaskError(f"{where}: sample must be a whole number of classes")
        for name in names:
            stage = STAGES.get(name)
            if stage is None or stage.kind != kind:
                own = [key for key, value in STAGES.items() if value.kind == kind]
                raise TaskError(f"{where}: no {kind} stage {name!r}; there are {', '.join(own)}")
            if sample is not None and not stage.sample:
                raise TaskError(f"{where}: the program of the stage {name} cannot take a sample")
            yield {
                "id": f"{kind}/{name}" + (f"/sample-of-{sample}" if sample else ""),
                "group": kind,
                "cost": stage.cost if sample is None else 1,
                "stage": name,
                "procs": procs,
                "sample": sample,
                "inputs": list(stage.inputs),
                "article": stage.article,
                "predicted": None,
            }

    return expand


def data_directory() -> Path:
    return Path(os.environ.get("QMB_DATA") or EXPERIMENTS)


def parse_counts(stage: Stage, output: str) -> dict[str, int] | None:
    """The counts of a stage in what its program printed; None if one is missing."""
    found = {}
    for key, pattern in stage.counts:
        match = re.search(pattern, output, re.MULTILINE)
        if match is None:
            return None
        found[key] = int(match[1])
    return found


def run(task: StageTask) -> Result:
    stage = STAGES[task["stage"]]
    require(*stage.modules)
    data = data_directory()
    missing = [name for name in stage.inputs if not (data / name).is_file()]
    if missing:
        raise BackendError(
            f"the stored result {missing[0]} is not in {data}: unpack the data archive (data/README.md), "
            "or set QMB_DATA to the directory that holds its files"
        )
    output = ""
    with scratch(task["id"]) as work:
        for name in stage.inputs:
            # a copy, not a link: whatever the program does to the file, the stored result is not touched
            shutil.copyfile(data / name, work / name)
        for number, (script, *arguments) in enumerate(stage.commands):
            filled = [argument.replace("{procs}", str(task["procs"])) for argument in arguments]
            if number == 0 and task.get("sample"):
                filled += ["--limit", str(task["sample"])]
            output += program(os.path.relpath(REPOSITORY / script, EXPERIMENTS), *filled, cwd=work)
        kept = keep_output(work, stage.inputs)
    counts = parse_counts(stage, output)
    if counts is None:
        raise BackendError(
            f"the programs of the stage {task['stage']} did not print every count of the stage"
        )
    return {
        "value": counts,
        "method": "; ".join(" ".join(command) for command in stage.commands).replace(
            "{procs}", str(task["procs"])
        ),
        "inputs": "stored results of the data archive",
        **({"kept_output": kept} if kept else {}),
    }


def kind(name: str) -> Kind[StageTask]:
    """The kind of the stages of one of the three sorts: "census", "core" or "tube"."""
    return Kind(_expander(name), run)
