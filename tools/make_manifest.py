#!/usr/bin/env python3
"""make_manifest.py -- the manifest table of DATA.md: every stored result, its size, the script that wrote it and its note.

Usage:  python3 -I tools/make_manifest.py DIR      DIR is experiments/ with the archive unpacked (or the staging copy)

The script of a file is the longest script name that begins the file's name (n4_doors_prove2.log -> n4_doors.py),
with the exceptions listed in OWNER; the note is that of the file's family (FAMILY).
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# family prefix -> (default script, notes)
FAMILY = [
    ("mutation_", "mutation_path.py", "1"), ("bounded_profile_v2", "bounded_paths.py", "3"), ("bounded_", "bounded_paths.py", "2"),
    ("bp_sizing", "bounded_paths.py", "2"), ("rank3_profile", "rank3_paths.py", "3"), ("pockets_", "pockets.py", "4"),
    ("traps_", "traps.py", "5"), ("hunt_", "hunt.py", "6"), ("n4_all_", "n4_all.py", "7, 8, 10"), ("n4_family", "n4_family.py", "7"),
    ("n4_classes_", "n4_classes.py", "8, 10"), ("n4_mirror_proof", "n4_mirror_proof.py", "9"), ("n4_mirror_", "n4_mirror.py", "9"),
    ("n4_block_scan", "n4_block_scan.py", "10"), ("n4_triangle_patterns", "a one-off driver over n4_classes.py (note 10 §4)", "10"),
    ("n4_conj55_", "n4_conj55.py", "13"), ("n4_opposite_tubes", "n4_opposite_tubes.py", "14"), ("n4_opposite_gk", "n4_opposite_gk.py", "14"),
    ("n4_opposite_", "n4_opposite_run.py", "14"), ("n4_doors_prove2_readable", "n4_doors_readable.py", "15"),
    ("n4_doors_prove_readable", "n4_doors_readable.py", "15"), ("n4_doors_", "n4_doors.py", "15"), ("n4_tube_", "n4_tube_lemma.py", "22"),
    ("n4_", "n4_evidence.py", "11"), ("np_corridor_members", "np_corridor_members.py", "16"), ("np_corridor_prove", "np_corridor_prove.py", "16"),
    ("np_corridor_", "np_corridor.py", "16"), ("np_rowwalk_", "np_rowwalk.py", "18"), ("np_qa_core_", "np_qa_core.py", "20"),
    ("owf_barrier_", "owf_barrier.py", "21"), ("review12_", "verify/review12.py", "12"), ("review17_", "verify/review17.py", "17"),
    ("review19_", "verify/review19.py", "19"), ("review23_n20_search", "verify/review23_n20_runs.py, review23_n20_search.c", "23"),
    ("review23_n21_", "verify/review23_n21_review.py", "23"), ("review23_", "verify/review23_*.py", "23"),
]


def scripts():
    out = {}
    for d in ("experiments", "verify"):
        for f in os.listdir(os.path.join(ROOT, d)):
            if f.endswith(".py"):
                out[f[:-3]] = ("verify/" if d == "verify" else "") + f
    return out


def owner(name, sc):
    stem = name.split(".")[0]
    for pre, script, notes in FAMILY:
        if stem.startswith(pre):
            break
    else:
        return "?", "?"
    if script.startswith("verify/") and "," not in script:
        best = max((s for s in sc if stem.startswith(s) and sc[s].startswith("verify/")), key=len, default=None)
        if best:
            script = sc[best]
    return script, notes


def main():
    d = sys.argv[1]
    sc = scripts()
    files = sorted(os.listdir(d))
    files = [f for f in files if f.endswith((".log", ".json", ".jsonl", ".gz"))]
    print("| File | Bytes | Date | Written by | Note |")
    print("|---|---|---|---|---|")
    total = 0
    for f in files:
        st = os.stat(os.path.join(d, f))
        total += st.st_size
        script, notes = owner(f, sc)
        print("| `%s` | %d | %s | `%s` | %s |" % (f, st.st_size, datetime.date.fromtimestamp(st.st_mtime).isoformat(), script, notes))
    sys.stderr.write("%d files, %d bytes\n" % (len(files), total))


if __name__ == "__main__":
    main()
