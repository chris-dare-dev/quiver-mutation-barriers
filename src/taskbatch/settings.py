"""What a repository tells the scheduler about itself: the `[tool.taskbatch]` table of its pyproject.toml.

    [tool.taskbatch]
    runner = ["{python}", "src/runners/task_runner.py"]   # the default runner command
    description_keys = ["objects"]                     # batch-file keys handed to the runner with "tasks"

`{python}` stands for the interpreter that runs the scheduler.  An argument that names a file of the
repository is made absolute.  Both keys are optional: without `runner` every command needs `--runner`,
and without `description_keys` a batch file may hold `name`, `scheduler`, `limits` and `tasks` only.
"""

from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]


class SettingsError(ValueError):
    """The `[tool.taskbatch]` table cannot be used."""


@dataclass(frozen=True)
class Settings:
    runner: tuple[str, ...] | None = None
    description_keys: tuple[str, ...] = ()


def _strings(value: object, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SettingsError(f"[tool.taskbatch] {where} must be an array of strings")
    return tuple(value)


def resolve_runner(runner: tuple[str, ...], repository: Path = REPOSITORY) -> tuple[str, ...]:
    """The runner command with `{python}` filled in and files of the repository as absolute paths."""
    resolved = []
    for index, argument in enumerate(runner):
        if argument == "{python}":
            argument = sys.executable
        elif index > 0 and not argument.startswith("-") and (repository / argument).is_file():
            argument = str(repository / argument)
        resolved.append(argument)
    return tuple(resolved)


def load_settings(repository: Path = REPOSITORY) -> Settings:
    """The settings of the repository that holds this package; the defaults if it declares none."""
    path = repository / "pyproject.toml"
    if not path.exists():
        return Settings()
    try:
        with path.open("rb") as handle:
            table = tomllib.load(handle).get("tool", {}).get("taskbatch", {})
    except tomllib.TOMLDecodeError as problem:
        raise SettingsError(f"{path}: {problem}") from None
    if not isinstance(table, dict):
        raise SettingsError("[tool.taskbatch] must be a table")
    unknown = set(table) - {"runner", "description_keys"}
    if unknown:
        raise SettingsError(f"[tool.taskbatch]: unknown key {sorted(unknown)[0]!r}")
    runner = _strings(table["runner"], "runner") if "runner" in table else None
    if runner is not None and not runner:
        raise SettingsError("[tool.taskbatch] runner must name a command")
    keys = _strings(table.get("description_keys", []), "description_keys")
    reserved = {"name", "scheduler", "limits", "tasks"} & set(keys)
    if reserved:
        raise SettingsError(f"[tool.taskbatch] description_keys cannot contain {sorted(reserved)[0]!r}")
    return Settings(
        runner=None if runner is None else resolve_runner(runner, repository), description_keys=keys
    )
