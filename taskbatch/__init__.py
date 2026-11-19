"""Runs batches of tasks: one process per task, under time and memory limits.

The computation lives in a runner, a command of the repository that uses this package.  This package
knows only that a runner can expand a batch description into tasks and compute one task (PROTOCOL.md);
it schedules the tasks, enforces the limits, and keeps one structured record per task.
"""

__version__ = "0.4"
