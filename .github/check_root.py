"""Every tracked entry at the repository root is on the allow-list.

Invariant: the root holds the code (src/), its tests (tests/), the data this
repository publishes (data/) and the research trail behind it (research/), with
the standard files beside them. A new entry needs its reason in a comment
beside it here.

Usage: python3 .github/check_root.py
Standard library only, so CI needs no install. Reads `git ls-files`, so
untracked and ignored files (results/, build/, dist/) do not count.
"""


from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys

ALLOWED_DIRS = frozenset({
    "src",
    "tests",
    # the data release: batches, records, claims and the example batch, which the article cites
    "data",
    # the research trail: the numbered notes, the scripts behind them, the checks, the paper
    "research",
    ".github",
})

# Patterns, matched with fnmatch. Dotfiles are allowed by the first one.
ALLOWED_FILES = (
    ".*",
    "README.md", "LICENSE", "CITATION.cff", "Dockerfile", "Makefile", "pyproject.toml",
    # the CC BY 4.0 licence of the prose, the paper and the data; LICENSE is the MIT licence of the code
    "LICENSE-TEXT.md",
    # the claims and their tables, which the article links to
    "CLAIMS.md",
    # the full reference the README points to
    "GUIDE.md",
)

WHERE_TO = {
    "docker": "deploy/", "infra": "deploy/", "k8s": "deploy/", "chart": "deploy/",
    "charts": "deploy/", "helm": "deploy/", "terraform": "deploy/",
    "apps": "a box under src/, or its own repository",
    "cmd": "a box under src/",
    "internal": "src/",
    "cli": "a box under src/", "server": "a box under src/",
    "scripts": "a box under src/, a Makefile target, or deletion",
    "tools": "a box under src/, a Makefile target, or deletion",
    "bin": "a box under src/, a Makefile target, or deletion",
    "runners": "a box under src/",
    "docs": "research/ if these are research notes, else a README.md inside a box or the wiki",
    "plans": "the issue or pull request", "notes": "the wiki, or research/",
    "design": "the wiki",
    "experiments": "research/", "verify": "research/", "notebooks": "research/",
    "paper": "research/",
    "batches": "data/", "records": "data/", "claims": "data/",
    "results": "gitignore it (scratch runs), or data/records/ through `make record`",
    "var": "gitignore; regenerate it",
    "out": "gitignore", "build": "gitignore", "dist": "gitignore",
    "examples": "tests/ if a test reads them, data/ if a reader runs them, else the wiki",
    "samples": "tests/ if a test reads them, data/ if a reader runs them, else the wiki",
    "fixtures": "tests/",
    "binder": ".binder/",
}


def root_entries(repo: str, rev: str | None) -> tuple[dict[str, bool], set[str]]:
    """Each tracked top-level name mapped to whether it is a directory, and the
    top-level directories that are Python packages."""
    cmd = ["ls-tree", "-r", "--name-only", "-z", rev] if rev else ["ls-files", "-z"]
    out = subprocess.run(
        ["git", "-C", repo, *cmd], check=True, capture_output=True, text=True,
    ).stdout
    entries: dict[str, bool] = {}
    packages: set[str] = set()
    for path in filter(None, out.split("\0")):
        head, sep, rest = path.partition("/")
        entries[head] = entries.get(head, False) or bool(sep)
        if rest == "__init__.py":
            packages.add(head)
    return entries, packages


def file_allowed(name: str) -> bool:
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in ALLOWED_FILES)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", help="check this commit's tree instead of the index")
    args = parser.parse_args()

    entries, packages = root_entries(args.repo, args.rev)

    bad = []
    for name, is_dir in sorted(entries.items()):
        if is_dir and name not in ALLOWED_DIRS:
            fallback = "a box under src/" if name in packages else (
                "src/, tests/, data/ or research/, or out of the tree")
            hint = WHERE_TO.get(name.lower(), fallback)
            bad.append(f"  {name}/  -> {hint}")
        elif not is_dir and not file_allowed(name):
            if name.startswith(("docker-compose", "compose.")):
                hint = "deploy/"
            elif name.lower().endswith(".md"):
                hint = "README.md of the folder it describes, or the wiki"
            else:
                hint = "a box under src/, a tool's config file, or out of the tree"
            bad.append(f"  {name}  -> {hint}")

    if bad:
        print("Root entries not on the allow-list:")
        print("\n".join(bad))
        print("Move each one, or add it to the allow-list with its reason beside it.")
        return 1
    print("Root is on the allow-list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
