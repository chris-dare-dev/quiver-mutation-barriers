"""The repository's settings: the default runner and the batch-file keys that belong to it."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from taskbatch.config import ConfigError, parse_config
from taskbatch.settings import Settings, SettingsError, load_settings


def minimal(**changes: object) -> dict[str, object]:
    data: dict[str, object] = {
        "scheduler": {"workers": 1, "memory_budget_mb": 100},
        "limits": {"time_seconds": 1, "memory_mb": 100},
        "tasks": [{"kind": "k"}],
    }
    return data | changes


class RepositorySettings(unittest.TestCase):
    def repository(self, pyproject: str | None) -> Path:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name)
        (root / "runners").mkdir()
        (root / "runners" / "run.py").write_text("")
        if pyproject is not None:
            (root / "pyproject.toml").write_text(pyproject)
        return root

    def test_a_repository_without_settings_has_no_default_runner(self) -> None:
        self.assertEqual(load_settings(self.repository(None)), Settings())
        self.assertEqual(load_settings(self.repository("[project]\nname = 'x'\n")), Settings())

    def test_the_runner_command_is_resolved_against_the_repository(self) -> None:
        root = self.repository(
            '[tool.taskbatch]\nrunner = ["{python}", "-I", "runners/run.py", "runners/absent.py"]\n'
            'description_keys = ["objects"]\n'
        )
        settings = load_settings(root)
        self.assertEqual(
            settings.runner, (sys.executable, "-I", str(root / "runners" / "run.py"), "runners/absent.py")
        )
        self.assertEqual(settings.description_keys, ("objects",))

    def test_settings_that_cannot_be_used_are_refused(self) -> None:
        refused = [
            "[tool.taskbatch]\nrunner = 'python3 run.py'\n",
            "[tool.taskbatch]\nrunner = []\n",
            "[tool.taskbatch]\ndescription_keys = ['tasks']\n",
            "[tool.taskbatch]\nworkers = 4\n",
            "[tool]\ntaskbatch = 3\n",
            "[tool.taskbatch\n",
        ]
        for text in refused:
            with self.subTest(text=text), self.assertRaises(SettingsError):
                load_settings(self.repository(text))


class DescriptionKeys(unittest.TestCase):
    def test_only_the_declared_keys_reach_the_runner(self) -> None:
        with self.assertRaises(ConfigError):
            parse_config(minimal(objects=[{"d": 2}]))
        config = parse_config(minimal(objects=[{"d": 2}]), description_keys=("objects", "fields"))
        self.assertEqual(config.description, {"objects": [{"d": 2}], "fields": [], "tasks": [{"kind": "k"}]})

    def test_without_declared_keys_the_runner_receives_the_task_sets(self) -> None:
        self.assertEqual(parse_config(minimal()).description, {"tasks": [{"kind": "k"}]})


if __name__ == "__main__":
    unittest.main()
