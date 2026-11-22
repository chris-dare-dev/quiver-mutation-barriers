"""synthetic: no mathematics; a task that sleeps, holds memory or fails, to try the scheduler's limits.

items   each a table with name and, optionally, cost, sleep_seconds, allocate_mb, fail, value, predicted
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

from ..backends import BackendError
from .base import Common, Kind, Result, Table, TaskError, known


class SyntheticTask(Common):
    sleep_seconds: float
    allocate_mb: float
    fail: bool
    value: Any  # what the task reports instead of the megabytes it held


ITEM_KEYS = {"name", "cost", "sleep_seconds", "allocate_mb", "fail", "value", "predicted"}


def expand(table: Table, where: str) -> Iterator[SyntheticTask]:
    known(table, where, "items")
    items = table.get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) and "name" in item for item in items):
        raise TaskError(f"{where}: items must be a list of tables with a name")
    for item in items:
        unknown = set(item) - ITEM_KEYS
        if unknown:
            raise TaskError(f"{where}: unknown key {sorted(unknown)[0]!r} in an item")
        yield {
            "id": f"synthetic/{item['name']}",
            "group": "synthetic",
            "cost": item.get("cost", 0),
            "sleep_seconds": item.get("sleep_seconds", 0),
            "allocate_mb": item.get("allocate_mb", 0),
            "fail": bool(item.get("fail", False)),
            "value": item.get("value"),
            "predicted": item.get("predicted"),
        }


def run(task: SyntheticTask) -> Result:
    if task["fail"]:
        raise BackendError("synthetic task asked to fail")
    held = bytearray(b"x") * (int(task["allocate_mb"]) << 20)
    time.sleep(float(task["sleep_seconds"]))
    return {"value": len(held) >> 20 if task["value"] is None else task["value"], "method": "synthetic"}


KIND = Kind(expand, run)
