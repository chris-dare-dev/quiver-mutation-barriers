"""The batch file: what to compute, with which limits, on how much of the machine."""

from __future__ import annotations

import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .model import Limits, Task


class ConfigError(ValueError):
    """The batch file or the command line asks for something that cannot be run."""


@dataclass(frozen=True)
class Tier:
    """Limits for tasks whose cost is at least `min_cost`; a missing limit is inherited."""

    min_cost: float
    time_seconds: float | None = None
    memory_mb: int | None = None


@dataclass(frozen=True)
class BatchConfig:
    name: str
    workers: int
    memory_budget_mb: int
    default_limits: Limits
    tiers: tuple[Tier, ...]
    # one entry per [[tasks]] table: the limits written in that table, if any
    set_limits: tuple[dict[str, Any], ...]
    # what the runner expands: the repository's description keys and {"tasks": [...]}
    description: dict[str, Any]

    def limits_for(self, task: Task) -> Limits:
        """Limits of a task: its set's own, else those of the highest tier it reaches, else the defaults."""
        time_seconds: float = self.default_limits.time_seconds
        memory_mb: int = self.default_limits.memory_mb
        for tier in sorted(self.tiers, key=lambda t: t.min_cost):
            if task.cost >= tier.min_cost:
                if tier.time_seconds is not None:
                    time_seconds = tier.time_seconds
                if tier.memory_mb is not None:
                    memory_mb = tier.memory_mb
        own = self.set_limits[task.set] if task.set < len(self.set_limits) else {}
        return Limits(
            time_seconds=own.get("time_seconds", time_seconds),
            memory_mb=own.get("memory_mb", memory_mb),
        )

    def with_overrides(
        self,
        *,
        workers: int | None = None,
        memory_budget_mb: int | None = None,
        time_seconds: float | None = None,
        memory_mb: int | None = None,
    ) -> BatchConfig:
        """The configuration with command-line values for the scheduler settings and the default limits."""
        config = replace(
            self,
            workers=self.workers if workers is None else workers,
            memory_budget_mb=self.memory_budget_mb if memory_budget_mb is None else memory_budget_mb,
            default_limits=Limits(
                time_seconds=self.default_limits.time_seconds if time_seconds is None else time_seconds,
                memory_mb=self.default_limits.memory_mb if memory_mb is None else memory_mb,
            ),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.workers < 1:
            raise ConfigError("workers must be at least 1")
        if self.memory_budget_mb < 1:
            raise ConfigError("memory_budget_mb must be positive")
        _check_limits("limits", self.default_limits.as_dict())
        for tier in self.tiers:
            _check_limits(f"tier min_cost = {tier.min_cost}", _present(tier.time_seconds, tier.memory_mb))
        for index, own in enumerate(self.set_limits):
            _check_limits(f"tasks[{index}].limits", own)

    def as_dict(self) -> dict[str, Any]:
        """The resolved configuration, as written to the run's record."""
        return {
            "name": self.name,
            "scheduler": {"workers": self.workers, "memory_budget_mb": self.memory_budget_mb},
            "limits": self.default_limits.as_dict()
            | {
                "tier": [{"min_cost": t.min_cost} | _present(t.time_seconds, t.memory_mb) for t in self.tiers]
            },
            "set_limits": list(self.set_limits),
            "description": self.description,
        }


def _present(time_seconds: float | None, memory_mb: int | None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if time_seconds is not None:
        out["time_seconds"] = time_seconds
    if memory_mb is not None:
        out["memory_mb"] = memory_mb
    return out


def _check_limits(where: str, limits: dict[str, Any]) -> None:
    unknown = set(limits) - {"time_seconds", "memory_mb"}
    if unknown:
        raise ConfigError(f"{where}: unknown key {sorted(unknown)[0]!r}")
    for key, value in limits.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ConfigError(f"{where}: {key} must be a positive number")
    if "memory_mb" in limits and not isinstance(limits["memory_mb"], int):
        raise ConfigError(f"{where}: memory_mb must be a whole number of megabytes")


def _table(data: dict[str, Any], key: str, where: str) -> dict[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError(f"{where}{key} must be a table")
    return value


def _require(table: dict[str, Any], key: str, where: str) -> Any:
    if key not in table:
        raise ConfigError(f"{where} needs {key}")
    return table[key]


def parse_config(
    data: dict[str, Any], *, default_name: str = "batch", description_keys: Sequence[str] = ()
) -> BatchConfig:
    """Builds the configuration from the content of a batch file.

    `description_keys` are the keys of the batch file, next to `tasks`, that belong to the runner: they
    are handed to it unread, and an absent one is handed over as an empty array.
    """
    known = {"name", "scheduler", "limits", "tasks", *description_keys}
    unknown = set(data) - known
    if unknown:
        raise ConfigError(f"unknown key {sorted(unknown)[0]!r}; expected {', '.join(sorted(known))}")

    scheduler = _table(data, "scheduler", "")
    limits = dict(_table(data, "limits", ""))
    tiers_data = limits.pop("tier", [])
    if not isinstance(tiers_data, list):
        raise ConfigError("limits.tier must be an array of tables")
    tiers = []
    for entry in tiers_data:
        entry = dict(entry)
        min_cost = entry.pop("min_cost", None)
        if not isinstance(min_cost, (int, float)) or isinstance(min_cost, bool):
            raise ConfigError("every [[limits.tier]] needs a number min_cost")
        _check_limits(f"tier min_cost = {min_cost}", entry)
        tiers.append(Tier(min_cost, entry.get("time_seconds"), entry.get("memory_mb")))

    task_sets = data.get("tasks", [])
    if not isinstance(task_sets, list) or not task_sets:
        raise ConfigError("the batch needs at least one [[tasks]] table")
    set_limits = []
    described_sets = []
    for index, task_set in enumerate(task_sets):
        if not isinstance(task_set, dict) or "kind" not in task_set:
            raise ConfigError(f"tasks[{index}] needs a kind")
        task_set = dict(task_set)
        own = task_set.pop("limits", {})
        if not isinstance(own, dict):
            raise ConfigError(f"tasks[{index}].limits must be a table")
        set_limits.append(dict(own))
        described_sets.append(task_set)

    _check_limits("limits", limits)
    config = BatchConfig(
        name=str(data.get("name", default_name)),
        workers=_require(scheduler, "workers", "[scheduler]"),
        memory_budget_mb=_require(scheduler, "memory_budget_mb", "[scheduler]"),
        default_limits=Limits(
            time_seconds=_require(limits, "time_seconds", "[limits]"),
            memory_mb=_require(limits, "memory_mb", "[limits]"),
        ),
        tiers=tuple(tiers),
        set_limits=tuple(set_limits),
        description={key: data.get(key, []) for key in description_keys} | {"tasks": described_sets},
    )
    if not isinstance(config.workers, int) or not isinstance(config.memory_budget_mb, int):
        raise ConfigError("[scheduler] workers and memory_budget_mb must be whole numbers")
    config.validate()
    return config


def load_config(path: Path, *, description_keys: Sequence[str] = ()) -> BatchConfig:
    """Reads a batch file (TOML)."""
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as problem:
        raise ConfigError(f"{path}: {problem}") from None
    try:
        return parse_config(data, default_name=path.stem, description_keys=description_keys)
    except ConfigError as problem:
        raise ConfigError(f"{path}: {problem}") from None
