"""One quiver from the command line, without a batch file.

    python3 -m qmb explore -8 -8 7 -2 6 -8
    python3 -m qmb explore 3 -2 1 -3 -1 -3 --cap 500
    python3 -m qmb explore 2 -2 2 --json

The numbers are the entries b_ij, i < j, of the exchange matrix, row by row.  The command prints the
height of the quiver, the height at which it is joined to its opposite if the search reaches it, and what
lies below; src/qmb/kinds/explore.py says what each number is and where the search stops.  The same
computation is the task kind "explore" of a batch file, which runs it under time and memory limits.
"""

from __future__ import annotations

import argparse
import json
import sys

from .kinds import explore
from .kinds.base import TaskError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m qmb", description="Searches on one quiver.")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser(
        "explore", help="the height at which a quiver is joined to its opposite, and what lies below"
    )
    entries = "the entries b_ij, i < j, row by row"
    command.add_argument("entries", type=int, nargs="+", metavar="B", help=entries)
    command.add_argument("--cap", type=int, metavar="H", help="leave out every quiver above this height")
    command.add_argument(
        "--budget",
        type=int,
        default=explore.BUDGET,
        metavar="N",
        help=f"stop a search after this many quivers (default {explore.BUDGET})",
    )
    command.add_argument("--json", action="store_true", help="print the result as JSON")
    return parser


def main(arguments: list[str]) -> int:
    asked = _parser().parse_args(arguments)
    try:
        quiver = explore.check(asked.entries, asked.cap, asked.budget, "explore")
    except TaskError as problem:
        print(f"python3 -m qmb: error: {problem}", file=sys.stderr)
        return 2
    result = explore.survey(quiver, cap=asked.cap, budget=asked.budget)
    print(json.dumps(result, ensure_ascii=False) if asked.json else "\n".join(explore.lines(result)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
