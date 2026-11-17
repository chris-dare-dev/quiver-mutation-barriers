"""A runner without mathematics, for testing the scheduler.

It follows the runner protocol (taskbatch/PROTOCOL.md).  A batch description lists items; each becomes one
task, and its keys say how the task behaves:

    cost         the task's cost
    sleep        seconds to sleep
    allocate_mb  megabytes to hold while it sleeps
    exit         exit with this status and an error message instead of a result
    signal       end by this signal instead of printing a result
    silent       exit with status 0 without printing a result
    value, predicted   reported in the result; "mismatch" when both are given and differ

With `--journal FILE` every run appends "start <pid> <time> <id>" and "end <pid> <time> <id>" lines.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import time


def expand(description: dict) -> None:
    count = 0
    for index, task_set in enumerate(description.get("tasks", [])):
        for item in task_set.get("items", []):
            task = dict(item) | {
                "id": f"fake/{item['name']}",
                "kind": "fake",
                "set": index,
                "group": task_set.get("group", "fake"),
                "cost": item.get("cost", 0),
            }
            print("@task " + json.dumps(task))
            count += 1
    print("@meta " + json.dumps({"tasks": count, "fake_version": "1"}))


def note(journal: str | None, word: str, task: dict) -> None:
    if journal:
        line = f"{word} {os.getpid()} {time.time():.6f} {task['id']}\n"
        fd = os.open(journal, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        os.write(fd, line.encode())
        os.close(fd)


def run(task: dict, journal: str | None) -> None:
    note(journal, "start", task)
    held = bytearray(b"x") * (int(task.get("allocate_mb", 0)) << 20)
    time.sleep(float(task.get("sleep", 0)))
    note(journal, "end", task)
    if "exit" in task:
        print("fake_runner.py:1:1: error: asked to fail", file=sys.stderr)
        sys.exit(int(task["exit"]))
    if "signal" in task:
        os.kill(os.getpid(), getattr(signal, task["signal"]))
    if task.get("silent"):
        return
    value = task.get("value", len(held))
    predicted = task.get("predicted")
    agrees = None if predicted is None else value == predicted
    if task.get("unsupported"):
        status, value = "unsupported", None
    else:
        status = "mismatch" if agrees is False else "ok"
    result = {"status": status, "value": value, "predicted": predicted, "agrees": agrees, "method": "fake"}
    print("@result " + json.dumps(result))


def main(argv: list[str]) -> int:
    journal = None
    if argv[:1] == ["--journal"]:
        journal, argv = argv[1], argv[2:]
    if len(argv) != 2 or argv[0] not in {"expand", "run"}:
        print("usage: fake_runner.py [--journal FILE] (expand|run) JSON", file=sys.stderr)
        return 2
    request = json.loads(argv[1])
    if argv[0] == "expand":
        expand(request)
    else:
        run(request, journal)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
