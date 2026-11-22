"""What the checking code shares with the code it checks: the statements of research/verify/README.md, kept
true."""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

from taskbatch.settings import REPOSITORY

SOURCE = REPOSITORY / "src"
RESEARCH = REPOSITORY / "research"

NEW_CODE = {"qmb", "taskbatch", "runners", "adopt", "claims", "expected", "task_runner"}


def imports(path: Path) -> set[str]:
    """The top-level modules a script imports, anywhere in its source."""
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return found


class Independence(unittest.TestCase):
    def test_the_smoke_script_uses_the_standard_library_only(self) -> None:
        self.assertLessEqual(imports(RESEARCH / "verify" / "smoke.py"), sys.stdlib_module_names)

    def test_no_checking_script_imports_the_core_or_the_scheduler(self) -> None:
        scripts = sorted((RESEARCH / "verify").glob("*.py"))
        self.assertGreater(len(scripts), 50)
        for script in scripts:
            self.assertFalse(imports(script) & NEW_CODE, script.name)

    def test_the_scripts_of_experiments_do_not_use_the_core(self) -> None:
        for script in sorted((RESEARCH / "experiments").glob("*.py")):
            self.assertFalse(imports(script) & NEW_CODE, script.name)

    def test_the_core_and_the_scheduler_use_the_standard_library_only(self) -> None:
        for package in ("qmb", "taskbatch"):
            for module in sorted((SOURCE / package).rglob("*.py")):
                self.assertLessEqual(imports(module), sys.stdlib_module_names | {package}, module.name)

    def test_the_core_does_not_import_the_scripts_it_runs(self) -> None:
        names = {
            path.stem for folder in ("experiments", "verify") for path in (RESEARCH / folder).glob("*.py")
        }
        modules = sorted((SOURCE / "qmb").rglob("*.py"))
        self.assertGreater(len(modules), 15)  # the kinds, one module each, are among them
        for module in modules:
            self.assertFalse(imports(module) & names, module.name)


if __name__ == "__main__":
    unittest.main()
