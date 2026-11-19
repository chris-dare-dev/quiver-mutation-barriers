"""Back ends outside this package: the C search np_barrier, and the programs of experiments/.

The programs of experiments/ produced the stored results.  A task that runs one of them starts it in an
empty scratch directory, never in experiments/, because most of them overwrite their output files.  The
scratch directory is `$QMB_SCRATCH/<task>` if that variable is set, else `~/.cache/qmb-scratch/<task>`.
Some programs also keep caches of their own under `~/.cache/qmb-np/`.  The scratch directory is removed
when the task ends; with QMB_KEEP set to a directory, a stage of Section 13 first copies there what its
program wrote (keep_output).
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parent.parent
EXPERIMENTS = REPOSITORY / "experiments"
BUILD = REPOSITORY / "build"
INT_MAX = 2**31 - 1


class BackendError(RuntimeError):
    """A back end is missing or failed; the message says what to do."""


class Unsupported(Exception):
    """A back end cannot compute what a task asks; the message says why.  The task ends "unsupported"."""


def binary(name: str) -> Path:
    path = BUILD / name
    if not path.is_file():
        raise BackendError(f"build/{name} is not built: run `make build` (needs a C compiler)")
    return path


@dataclass(frozen=True)
class Search:
    """What one search of np_barrier.c found."""

    status: str  # "found"; "cap" or "closed" when no other low quiver is within the cap
    popped: int  # quivers taken from the queue
    plateau: int  # quivers of height at most `low` among them
    forks: int
    iso: int | None = None  # with "found": the height at which the other low quiver is reached
    target: tuple[int, ...] | None = None  # with "found": that quiver


def c_search(
    quiver: Sequence[int], *, low: int, cap: int, n: int, prune_forks: bool, budget: int
) -> dict[str, Any]:
    """The row that experiments/np_barrier.c prints for one search, as it prints it.

    This is all that is said to the C program and heard from it; `np_barrier` decides what may be asked
    of it and what its answer means.
    """
    line = f"{n} {low} {cap} {budget} {int(prune_forks)} {' '.join(map(str, quiver))}\n"
    done = subprocess.run(
        [str(binary("np_barrier"))], input=line, capture_output=True, text=True, check=False
    )
    rows = [row for row in done.stdout.splitlines() if row.strip().endswith("}")]
    if done.returncode != 0 or len(rows) != 1:
        raise BackendError(f"np_barrier failed (status {done.returncode}): {done.stderr.strip()[-300:]}")
    row: dict[str, Any] = json.loads(rows[0])
    return row


def np_barrier(
    quiver: Sequence[int],
    *,
    low: int,
    cap: int,
    n: int,
    barrier: int,
    prune_forks: bool = False,
    budget: int = 6_000_000,
) -> Search:
    """One search of experiments/np_barrier.c.

    From `quiver`, through quivers of height at most `cap`, lowest bottleneck first, until a quiver of
    height at most `low` outside the start's own component at that height is reached.

    `barrier` is the height up to which the caller relies on the search.  np_barrier.c holds every entry
    in 32 bits and discards a quiver with a larger one, so it sees the whole region below a barrier, and
    the join at it, only when the barrier is below 2^31: above that the search is Unsupported.  A `cap`
    above 2^31 - 1 is lowered to it, which only bounds the search.  A search that needs more than `budget`
    quivers is an error.
    """
    if barrier > INT_MAX:
        raise Unsupported(
            "np_barrier.c holds entries in 32 bits, and the barrier of this task, "
            f"{barrier}, is above 2^31 - 1"
        )
    result = c_search(quiver, low=low, cap=min(cap, INT_MAX), n=n, prune_forks=prune_forks, budget=budget)
    if result["status"] == "budget":
        raise BackendError(f"np_barrier needed more than its budget of {budget} quivers")
    return Search(
        status=result["status"],
        popped=result["popped"],
        plateau=result["plateau"],
        forks=result["forks"],
        iso=result.get("iso"),
        target=tuple(result["target"]) if "target" in result else None,
    )


@contextlib.contextmanager
def scratch(task_id: str) -> Iterator[Path]:
    """An empty directory for one task's files, removed when the task is done."""
    root = Path(os.environ.get("QMB_SCRATCH") or Path.home() / ".cache" / "qmb-scratch")
    readable = re.sub(r"[^A-Za-z0-9._-]+", "_", task_id).strip("_")[:60]
    path = root / f"{readable}-{hashlib.sha1(task_id.encode()).hexdigest()[:8]}"
    shutil.rmtree(path, ignore_errors=True)  # left behind by a task that was killed
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def keep_output(work: Path, inputs: Iterable[str]) -> dict[str, str]:
    """Copy what a program wrote in `work` to `$QMB_KEEP/<name of work>`: the SHA-256 of each file kept.

    The copies of the inputs are left out.  Without QMB_KEEP nothing is kept and the result is empty.
    """
    root = os.environ.get("QMB_KEEP")
    if not root:
        return {}
    kept = Path(root) / work.name
    kept.mkdir(parents=True, exist_ok=True)
    digests = {}
    for path in sorted(work.iterdir()):
        if path.is_file() and path.name not in inputs:
            shutil.copyfile(path, kept / path.name)
            digests[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def require(*modules: str) -> None:
    missing = [name for name in modules if importlib.util.find_spec(name) is None]
    if missing:
        raise BackendError(
            f"this task runs a program of experiments/ that needs {', '.join(missing)}: run the scheduler "
            "with an interpreter that has experiments/requirements.txt installed"
        )


def program(script: str, *arguments: object, cwd: Path, env: dict[str, str] | None = None) -> str:
    """Runs `python -I experiments/<script> <arguments>` in `cwd`; returns what it printed."""
    command = [sys.executable, "-I", str(EXPERIMENTS / script), *map(str, arguments)]
    done = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False, env=os.environ | (env or {}),
        stdin=subprocess.DEVNULL,
    )  # fmt: skip
    if done.returncode != 0:
        tail = "\n".join((done.stderr or done.stdout).strip().splitlines()[-6:])
        raise BackendError(
            f"{script} {' '.join(map(str, arguments))} ended with status {done.returncode}:\n{tail}"
        )
    return done.stdout


def versions() -> dict[str, str]:
    """What the runner reports about itself."""
    from . import __version__

    out = {"python": sys.version.split()[0], "qmb": __version__}
    spec = importlib.util.find_spec("numpy")
    if spec is not None:
        out["numpy"] = importlib.metadata.version("numpy")
    for name in ("np_barrier", "np_qa_core"):
        path = BUILD / name
        if path.is_file():
            out[name] = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return out
