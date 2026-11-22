"""certificate: the verdict of a certificate program of research/experiments/.

    names, audit_tmax

CERTIFICATES names each program with the verdict the article states for it, which is the predicted value.
`audit_tmax` (7 to 14) is how far the certificate of P+_t is audited by direct enumeration.  `parse_verdict`
reads the verdict from what a program printed.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterator
from typing import Any

from ..backends import program, scratch
from .base import Common, Kind, Result, Table, TaskError, known


class CertificateTask(Common):
    name: str  # a key of CERTIFICATES
    program: list[str]  # the script of research/experiments/ and its arguments
    article: str


CERTIFICATES: dict[str, dict[str, Any]] = {
    "R_b": {
        "program": ["n4_doors.py", "prove2"],
        "predicted": {"claims": 30, "certified": True},
        "article": "Theorem 7.2",
    },
    "Q_t": {
        "program": ["n4_doors.py", "prove"],
        "predicted": {"claims": 43, "certified": True},
        "article": "Section 7",
    },
    "P+_t": {
        "program": ["np_corridor_prove.py", "prove", "--T0", "8"],
        "predicted": {
            "claims": 938,
            "members": 149,
            "certified": True,
            "exits": {"fork": 54, "height": 428, "member": 161, "new": 123},
        },
        "article": "Theorem 9.1",
    },
}


def expand(table: Table, where: str) -> Iterator[CertificateTask]:
    known(table, where, "names", "audit_tmax")
    names = table.get("names", list(CERTIFICATES))
    audit = table.get("audit_tmax", 11)
    if not isinstance(names, list) or type(audit) is not int or not 7 <= audit <= 14:
        raise TaskError(f"{where}: names must be a list and audit_tmax a whole number from 7 to 14")
    for name in names:
        if name not in CERTIFICATES:
            raise TaskError(f"{where}: no certificate {name!r}; there are {', '.join(CERTIFICATES)}")
        spec = CERTIFICATES[name]
        audited = name == "P+_t"
        yield {
            "id": f"certificate/{name}" + (f"/audit-to-{audit}" if audited else ""),
            "group": "certificate",
            "cost": 3 * (audit - 7) if audited else 1,
            "name": name,
            "program": [*spec["program"], *(["--audit-tmax", str(audit)] if audited else [])],
            "article": spec["article"],
            "predicted": spec["predicted"],
        }


def parse_verdict(output: str) -> dict[str, Any] | None:
    """What a certificate program concluded: how many claims, whether all are certified and, where it
    prints them, the members and the exits by verdict.  None if it printed no verdict."""
    verdict = re.search(r"^(\d+) claims, (?:(\d+) members, )?(.+)$", output, re.MULTILINE)
    if verdict is None:
        return None
    found: dict[str, Any] = {"claims": int(verdict[1]), "certified": verdict[3].strip() == "ALL CERTIFIED"}
    if verdict[2] is not None:
        found["members"] = int(verdict[2])
    exits = re.search(r"^exits by verdict: (\{.*\})$", output, re.MULTILINE)
    if exits is not None:
        found["exits"] = ast.literal_eval(exits[1])
    return found


def run(task: CertificateTask) -> Result:
    script, *arguments = task["program"]
    with scratch(task["id"]) as work:
        output = program(script, *arguments, cwd=work)
    return {"value": parse_verdict(output), "method": " ".join(task["program"])}


KIND = Kind(expand, run)
