"""The results of a batch: one JSON object per line, one line per task that ended."""

from __future__ import annotations

import fcntl
import json
import os
from collections.abc import Collection, Mapping
from pathlib import Path
from typing import Any, cast

from .record import Record


class StoreLocked(RuntimeError):
    """Another scheduler is writing to the same results."""


class ResultStore:
    """An append-only file of records, written by one scheduler at a time.

    Each record is written with a single `write` on a file opened for appending and then synced, so a
    record is either whole or absent.  A scheduler that is killed in the middle of a write leaves at most
    one incomplete last line, which is ignored when the file is read and closed off by the next writer.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.unreadable_lines = 0
        self._fd: int | None = None
        self._lock_fd: int | None = None

    # reading ---------------------------------------------------------------------------------------

    def records(self) -> list[Record]:
        """Every record in the file, oldest first."""
        self.unreadable_lines = 0
        if not self.path.exists():
            return []
        records: list[Record] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    self.unreadable_lines += 1
                    continue
                if isinstance(record, dict) and "task_id" in record and "status" in record:
                    records.append(cast(Record, record))
                else:
                    self.unreadable_lines += 1
        return records

    def latest(self) -> dict[str, Record]:
        """The most recent record of each task."""
        return {record["task_id"]: record for record in self.records()}

    def finished(self, retry: Collection[str] = ()) -> set[str]:
        """Ids of the tasks a run must not compute again: those whose latest status is not in `retry`."""
        return {task_id for task_id, record in self.latest().items() if record["status"] not in retry}

    # writing ---------------------------------------------------------------------------------------

    def open(self) -> None:
        """Takes the lock and opens the file for appending."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_fd = os.open(self.path.with_name(self.path.name + ".lock"), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self._lock_fd)
            self._lock_fd = None
            raise StoreLocked(f"another run is writing to {self.path}") from None
        self._fd = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        if self._ends_mid_line():
            os.write(self._fd, b"\n")

    def _ends_mid_line(self) -> bool:
        size = self.path.stat().st_size
        if size == 0:
            return False
        with self.path.open("rb") as handle:
            handle.seek(size - 1)
            return handle.read(1) != b"\n"

    def append(self, record: Mapping[str, Any]) -> None:
        if self._fd is None:
            raise RuntimeError("the store is not open for writing")
        line = json.dumps(record, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
        os.write(self._fd, line.encode("utf-8"))
        os.fsync(self._fd)

    def close(self) -> None:
        for fd in (self._fd, self._lock_fd):
            if fd is not None:
                os.close(fd)
        self._fd = None
        self._lock_fd = None

    def __enter__(self) -> ResultStore:
        self.open()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
