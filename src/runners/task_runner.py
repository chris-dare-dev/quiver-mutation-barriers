#!/usr/bin/env python3
"""The entry point the scheduler calls (src/taskbatch/PROTOCOL.md): expands a batch, or computes one task.

    python3 -I src/runners/task_runner.py expand '<batch description as JSON>'
    python3 -I src/runners/task_runner.py run '<task as JSON>'

"expand" prints one line "@task <JSON>" per task and a last line "@meta <JSON>" with the number of tasks
and the versions in use.  "run" prints one line "@result <JSON>".  An error ends the process with status 1
and one line on the standard error.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # src/, which holds the packages

from qmb.backends import BackendError, versions
from qmb.tasks import EXPECTED, expand_batch, run_task


def emit(mark: str, content: object) -> None:
    print(mark, json.dumps(content, ensure_ascii=False), flush=True)


def main(arguments: list[str]) -> int:
    if len(arguments) != 2 or arguments[0] not in {"expand", "run"}:
        print("usage: task_runner.py (expand|run) '<JSON>'", file=sys.stderr)
        return 2
    try:
        request = json.loads(arguments[1])
        if arguments[0] == "run":
            emit("@result", run_task(request))
        else:
            tasks = expand_batch(request)
            for task in tasks:
                emit("@task", task)
            expected = hashlib.sha256(EXPECTED.read_bytes()).hexdigest()[:12] if EXPECTED.exists() else None
            emit("@meta", {"tasks": len(tasks)} | versions() | {"expected": expected})
    except (BackendError, ValueError, KeyError) as problem:
        message = str(problem) if not isinstance(problem, KeyError) else f"missing key {problem}"
        print(f"task_runner.py: error: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
