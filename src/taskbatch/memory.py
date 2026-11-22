"""Memory limits for task processes.

Two guards enforce a limit.  `CgroupGuard` starts each task in its own systemd scope with a hard limit:
the kernel kills the process the moment it exceeds it, and systemd records why.  `PollingGuard` needs
nothing but /proc: the scheduler reads the resident size of each task process on every tick and kills it
when it is over the limit, so a process can overshoot by what it allocates within one tick.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path


class MemoryGuard:
    """How the memory limit of a task process is enforced."""

    name = "none"

    def wrap(self, command: list[str], limit_mb: int, tag: str) -> list[str]:
        """The command that runs `command` under the limit; `tag` names the task process."""
        return command

    def over_limit(self, pid: int, limit_mb: int) -> bool:
        """Whether the scheduler must kill the process now."""
        return False

    def killed_for_memory(self, tag: str) -> bool:
        """Whether a process that was killed by someone other than the scheduler died at its limit."""
        return False

    def release(self, tag: str) -> None:
        """Forgets a task process that ended abnormally."""


class PollingGuard(MemoryGuard):
    name = "poll"

    def over_limit(self, pid: int, limit_mb: int) -> bool:
        return resident_mb(pid) > limit_mb


class CgroupGuard(MemoryGuard):
    name = "cgroup"

    @staticmethod
    def available() -> bool:
        if shutil.which("systemd-run") is None or shutil.which("systemctl") is None:
            return False
        try:
            probe = subprocess.run(
                ["systemd-run", "--user", "--scope", "--quiet", "true"],
                capture_output=True, timeout=20, check=False,
            )  # fmt: skip
        except (OSError, subprocess.TimeoutExpired):
            return False
        return probe.returncode == 0

    def wrap(self, command: list[str], limit_mb: int, tag: str) -> list[str]:
        # systemd-run moves itself into the new scope and then becomes the command, so the process the
        # scheduler started is the task process itself
        return [
            "systemd-run", "--user", "--scope", "--quiet", f"--unit={tag}",
            "-p", f"MemoryMax={limit_mb}M", "-p", "MemorySwapMax=0", "--", *command,
        ]  # fmt: skip

    def killed_for_memory(self, tag: str) -> bool:
        # systemd learns of the kill from the kernel a moment after the process is gone
        for _ in range(20):
            result = self._systemctl("show", f"{tag}.scope", "--property=Result", "--value")
            if result == "oom-kill":
                return True
            time.sleep(0.05)
        return False

    def release(self, tag: str) -> None:
        # a scope whose process was killed stays listed as failed until it is reset
        self._systemctl("reset-failed", f"{tag}.scope")

    @staticmethod
    def _systemctl(*arguments: str) -> str:
        try:
            done = subprocess.run(
                ["systemctl", "--user", *arguments], capture_output=True, text=True, timeout=20, check=False
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return done.stdout.strip()


def resident_mb(pid: int) -> float:
    """Resident memory of a process in megabytes; 0 if it is gone."""
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        pass
    return 0.0


def available_mb() -> int | None:
    """Memory the kernel estimates can be used without swapping, in megabytes."""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def choose_guard(name: str) -> MemoryGuard:
    """The guard called `name`; "auto" is the cgroup guard where systemd offers it, else polling."""
    if name == "poll":
        return PollingGuard()
    if name == "cgroup":
        if not CgroupGuard.available():
            raise RuntimeError("systemd-run --user --scope is not available here; use the poll guard")
        return CgroupGuard()
    if name == "auto":
        return CgroupGuard() if CgroupGuard.available() else PollingGuard()
    raise ValueError(f"unknown memory guard {name!r}")
