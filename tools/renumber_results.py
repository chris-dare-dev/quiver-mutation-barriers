#!/usr/bin/env python3
"""renumber_results.py -- the one rewrite applied to the stored results before they were archived.

The notes of this repository were first written under a working numbering that differs from the numbers of
docs/.  Scripts, logs and records referred to notes and to their numbered statements by the working numbers,
and some logs recorded absolute paths of the machine they ran on.  This script is the complete specification
of how those references were rewritten.  It was run once, on a copy of the original outputs, before the
archive of DATA.md was built; the same text rules were applied to the scripts and to the notes, so that a
script, its stored output and the note that quotes them agree.

Rules, applied to every line of every text file (gzip files are unpacked, rewritten and repacked only if a
line changes):

  1. working note number -> note number of docs/        ("note 15", "notes 3 to 10"); and one printed line of
     n4_tube_lemma.py, "the 6,990 classes after this ...:", which named the note by a common noun
  2. numbered statements, N.k with N a working number   ("Theorem 15.13"); only statements that the notes
     define are touched, so labels of cited papers (for example Definition 14.1 of Fomin-Neville) stay
  3. file-name tags of the checking scripts              (review12, review17, review19_n13_..., review23_n20_...)
  4. absolute paths: the interpreter becomes "python", the experiments directory becomes relative, a home
     directory becomes "~", scratch directories are dropped; cache directories get the names the scripts use

No number, count, quiver or timing is changed by any rule.  The script is not idempotent (rule 2 would map
a new label again), so it must not be run on the unpacked archive.

Usage:  python3 -I renumber_results.py DIR [--dry-run]     rewrites DIR in place and prints what changed
"""
import gzip
import os
import re
import sys

# working number -> note number in docs/
NOTE = {12: 1, 14: 2, 15: 3, 16: 4, 17: 5, 18: 6, 19: 7, 20: 8, 21: 9, 22: 10, 44: 11, 46: 12, 49: 13, 50: 14, 52: 15,
        53: 16, 65: 17, 66: 18, 69: 19, 71: 20, 72: 21, 73: 22, 77: 23}

# statements N.k defined by the notes (working numbers); everything else of the form "Lemma 12.5" is a citation
LABELS = set()          # filled below from LABEL_TABLE
LABEL_TABLE = "15:1 17:1,2 18:1 21:1 22:1 44:1,2 46:1 49:1 50:1,2,3 52:1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 53:1,2,3,4,5,6,7,8,9,10 66:1,2,3,4,5,6,7,8 71:1,2,3,4,5 73:1,2,3,4,5,6,7"
for _item in LABEL_TABLE.split():
    _n, _ks = _item.split(":")
    for _k in _ks.split(","):
        LABELS.add((int(_n), _k))
# one script and its log used the label of note 22's lemmas under an older number
STALE = {(72, "1"): 73, (72, "6"): 73}

LAB = (r"(?:Theorems?|Thms?|Lemmas?|Propositions?|Props?|Corollar(?:y|ies)|Cors?|Conjectures?|Conjs?|Observations?|Obs|"
       r"Questions?|Remarks?|Problems?|Definitions?|Defs?)\.?")
NUM = r"\d+\.\d+"
SEP = r"(?:\s*(?:,\s*and|,|–|-|—|to|and|or)\s*)"
LABEL_CHAIN = re.compile(r"\b(" + LAB + r")(\s+)(" + NUM + r"(?:[^\s\w]{0,4}?" + SEP + NUM + r")*)")
LABEL_ONE = re.compile(r"(?<![\d.])(\d+)\.(\d+)")
# after "class" and after "level as" the word is followed by a count, not by a note number (four logs, see DATA.md)
PART_CHAIN = re.compile(r"(?<!class )(?<!level as )\b([Pp])art(s?)([ -])(\d+)((?:" + SEP + r"\d+(?!\d|\.\d))*)")
INT = re.compile(r"(?<![\d.])\d+(?![\d]|\.\d)")
TRACE = None            # set to a dict to collect every distinct replacement of rules 1 and 2


def _label_one(m):
    n, k = int(m.group(1)), m.group(2)
    if (n, k) in STALE:
        n = STALE[(n, k)]
    elif (n, k) not in LABELS:
        return m.group(0)
    return "%d.%s" % (NOTE[n], k)


def _label_chain(m):
    out = m.group(1) + m.group(2) + LABEL_ONE.sub(_label_one, m.group(3))
    if TRACE is not None and out != m.group(0):
        TRACE[(m.group(0), out)] = TRACE.get((m.group(0), out), 0) + 1
    return out


def _part_chain(m):
    head = int(m.group(4))
    if head not in NOTE:
        return m.group(0)                      # a note that is not in this repository: left as it is
    tail = m.group(5)
    if m.group(2):                             # plural: the whole list of numbers is mapped; singular: only the first number
        tail = INT.sub(lambda x: str(NOTE.get(int(x.group(0)), int(x.group(0)))), tail)
    out = ("N" if m.group(1) == "P" else "n") + "ote" + m.group(2) + m.group(3) + str(NOTE[head]) + tail
    if TRACE is not None:
        TRACE[(m.group(0), out)] = TRACE.get((m.group(0), out), 0) + 1
    return out


TAG = {"46": "12", "49": "13", "50": "14", "53": "16", "71": "20", "72": "21", "73": "22"}
TOKENS = [
    (re.compile(r"(?<![A-Za-z0-9])p1_review3_lead_p(7[123])"), lambda m: "review23_lead_n" + TAG[m.group(1)]),
    (re.compile(r"(?<![A-Za-z0-9])p1_review3_p(7[123])"), lambda m: "review23_n" + TAG[m.group(1)]),
    (re.compile(r"(?<![A-Za-z0-9])p1_review2_p(49|50)"), lambda m: "review19_n" + TAG[m.group(1)]),
    (re.compile(r"(?<![A-Za-z0-9])p1_review53"), lambda m: "review17"),
    (re.compile(r"(?<![A-Za-z0-9])p1_review2"), lambda m: "review19"),
    (re.compile(r"(?<![A-Za-z0-9])p1_review3"), lambda m: "review23"),
    (re.compile(r"(?<![A-Za-z0-9])p1_review"), lambda m: "review12"),
    (re.compile(r"(?<![A-Za-z0-9])p(46|49|50|53|71|72|73)(?=[ab]?(?![A-Za-z0-9]))"), lambda m: "n" + TAG[m.group(1)]),
    (re.compile(r"(?<![A-Za-z0-9])(compare|stored|search|route|lemmas|core|records|pf|markov|review|prove|regen|cor|lem|"
                r"tally|seen|both|selfcert)(46|50|52|53|66|71)(?![A-Za-z0-9])"),
     lambda m: m.group(0) if m.group(0) in ("cor52",) else m.group(1) + str(NOTE[int(m.group(2))])),
    (re.compile(r"(?<![A-Za-z0-9])part(_?)(14|52|53|66|71)(?![0-9])"), lambda m: "note" + m.group(1) + str(NOTE[int(m.group(2))])),
]
PATHS = [
    (re.compile(r"(?:/home/[^/\s\"']+|~)/\.cache/k3-exp-venv/bin/python"), "python"),
    (re.compile(r"/home/[^/\s\"']+/Documents/[^\"'\n]*?/experiments/"), ""),
    (re.compile(r"/?tmp/[^\s\"']*?/scratchpad/"), ""),
    (re.compile(r"/home/[^/\s\"']+/"), "~/"),
    (re.compile(r"k3-p1-review2\b"), "qmb-review19"),
    (re.compile(r"k3-p1-review\b"), "qmb-review12"),
    (re.compile(r"k3-review53\b"), "qmb-review17"),
    (re.compile(r"k3-review3\b"), "qmb-review23"),
    (re.compile(r"k3-np\b"), "qmb-np"),
    (re.compile(r"classes after this part:"), "classes after this note:"),      # one printed line of n4_tube_lemma.py pairs
]
# a cheap gate: every rule above needs one of these substrings in the line
QUICK = re.compile(r"[Pp]art|\d\.\d|p1_|/home/|tmp/|k3-|(?<![A-Za-z0-9])p\d\d|"
                   r"(?:compare|stored|search|route|lemmas|core|records|pf|markov|review|prove|regen|cor|lem|tally|seen|both|selfcert)\d\d")


def rewrite(line):
    """One line of text -> the rewritten line."""
    if not QUICK.search(line):
        return line
    for rx, rep in PATHS:
        line = rx.sub(rep, line)
    for rx, fn in TOKENS:
        line = rx.sub(fn, line)
    line = PART_CHAIN.sub(_part_chain, line)
    line = LABEL_CHAIN.sub(_label_chain, line)
    return line


def rename(name):
    for rx, fn in TOKENS:
        name = rx.sub(fn, name)
    return name


def process(path, dry):
    gz = path.endswith(".gz")
    op = gzip.open if gz else open
    with op(path, "rt", encoding="utf-8", errors="surrogateescape", newline="") as f:
        lines = f.readlines()
    out = [rewrite(x) for x in lines]
    changed = sum(1 for a, b in zip(lines, out) if a != b)
    if changed and not dry:
        st = os.stat(path)
        if gz:
            with open(path, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as g:
                g.write("".join(out).encode("utf-8", errors="surrogateescape"))
        else:
            with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                f.writelines(out)
        os.utime(path, (st.st_atime, st.st_mtime))
    return changed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    total = 0
    for dp, _, files in os.walk(args[0]):
        for f in sorted(files):
            if not f.endswith((".log", ".json", ".jsonl", ".gz", ".txt")):
                continue
            p = os.path.join(dp, f)
            n = process(p, dry)
            new = rename(f)
            if new != f and not dry:
                os.rename(p, os.path.join(dp, new))
            if n or new != f:
                total += 1
                print("%-58s %6d lines%s" % (new, n, "" if new == f else "   (was %s)" % f))
    print("%d files rewritten or renamed" % total)


if __name__ == "__main__":
    main()
