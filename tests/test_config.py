"""The batch file: what is accepted, and which limits a task gets."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from taskbatch.config import ConfigError, load_config, parse_config
from taskbatch.model import Limits, Task

BATCH = """
name = "example"

[scheduler]
workers = 3
memory_budget_mb = 6000

[limits]
time_seconds = 600
memory_mb = 1000

[[limits.tier]]
min_cost = 9
time_seconds = 3600

[[limits.tier]]
min_cost = 100
memory_mb = 4000

[[objects]]
d = 2

[[objects]]
d = 3
special = true

[[tasks]]
kind = "pair"
names = ["a", "b"]

[[tasks]]
kind = "synthetic"
limits = { time_seconds = 5 }
items = [{ name = "idle" }]
"""


def task(cost: float, task_set: int = 0) -> Task:
    return Task(id="t", kind="k", cost=cost, set=task_set, group="g", payload={})


def minimal(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "scheduler": {"workers": 1, "memory_budget_mb": 100},
        "limits": {"time_seconds": 1, "memory_mb": 100},
        "tasks": [{"kind": "k"}],
    }
    return data | changes


class BatchFile(unittest.TestCase):
    def load(self, text: str) -> Any:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        path = Path(scratch.name) / "example-batch.toml"
        path.write_text(text)
        return load_config(path, description_keys=("objects",))

    def test_a_batch_file_is_read(self) -> None:
        config = self.load(BATCH)
        self.assertEqual(config.name, "example")
        self.assertEqual((config.workers, config.memory_budget_mb), (3, 6000))
        self.assertEqual(config.default_limits, Limits(600, 1000))
        # the runner receives its own keys and the task sets, without the limits
        self.assertEqual(
            config.description,
            {
                "objects": [{"d": 2}, {"d": 3, "special": True}],
                "tasks": [
                    {"kind": "pair", "names": ["a", "b"]},
                    {"kind": "synthetic", "items": [{"name": "idle"}]},
                ],
            },
        )

    def test_the_name_defaults_to_the_file_name(self) -> None:
        self.assertEqual(self.load(BATCH.replace('name = "example"', "")).name, "example-batch")

    def test_limits_come_from_the_set_then_the_tiers_then_the_defaults(self) -> None:
        config = self.load(BATCH)
        self.assertEqual(config.limits_for(task(1)), Limits(600, 1000))
        self.assertEqual(config.limits_for(task(9)), Limits(3600, 1000))
        self.assertEqual(config.limits_for(task(121)), Limits(3600, 4000))
        self.assertEqual(config.limits_for(task(121, task_set=1)), Limits(5, 4000))

    def test_command_line_values_replace_scheduler_settings_and_default_limits(self) -> None:
        config = self.load(BATCH).with_overrides(workers=8, memory_budget_mb=9000, time_seconds=60)
        self.assertEqual((config.workers, config.memory_budget_mb), (8, 9000))
        self.assertEqual(config.limits_for(task(1)), Limits(60, 1000))
        self.assertEqual(config.limits_for(task(9)), Limits(3600, 1000))

    def test_the_resolved_configuration_can_be_recorded(self) -> None:
        recorded = self.load(BATCH).as_dict()
        self.assertEqual(recorded["scheduler"], {"workers": 3, "memory_budget_mb": 6000})
        self.assertEqual(recorded["limits"]["tier"][0], {"min_cost": 9, "time_seconds": 3600})
        self.assertEqual(recorded["set_limits"], [{}, {"time_seconds": 5}])

    def test_what_cannot_be_run_is_refused(self) -> None:
        refused = [
            minimal(scheduler={"workers": 0, "memory_budget_mb": 100}),
            minimal(scheduler={"workers": 1}),
            minimal(scheduler={"workers": 1.5, "memory_budget_mb": 100}),
            minimal(limits={"time_seconds": 1}),
            minimal(limits={"time_seconds": -1, "memory_mb": 100}),
            minimal(limits={"time_seconds": 1, "memory_mb": 0.5}),
            minimal(limits={"time_seconds": 1, "memory_mb": 100, "cores": 2}),
            minimal(limits={"time_seconds": 1, "memory_mb": 100, "tier": [{"time_seconds": 5}]}),
            minimal(tasks=[]),
            minimal(tasks=[{"sheaves": "all"}]),
            minimal(tasks=[{"kind": "k", "limits": {"time": 5}}]),
            minimal(workers=4),
        ]
        for data in refused:
            with self.subTest(data=data), self.assertRaises(ConfigError):
                parse_config(data)
        with self.assertRaises(ConfigError):
            self.load("name = ")
        with self.assertRaises(ConfigError):
            parse_config(minimal()).with_overrides(workers=0)


if __name__ == "__main__":
    unittest.main()
