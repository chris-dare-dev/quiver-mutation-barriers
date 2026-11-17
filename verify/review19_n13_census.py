"""
review19_n13_census.py -- own re-certification of note 12's census classes with a pocket born <= B/4
(note 13 sec. 6: "census certifies all 123,691").  Reads the stored class files of notes 8 and 10 directly
(rows whose bottom lies in the file's range; a class is selected when one of its (birth, death) pairs has
birth <= B // 4), takes the bottom quiver, and runs the independent bottleneck search of review19_n13_lib.
Usage: python -I review19_n13_census.py [--workers 8]
"""
import argparse
import gzip
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results
FILES = [("n4_classes_B512.jsonl", 1, 4, 512), ("n4_classes_k5_B512.jsonl", 5, 5, 512),
         ("n4_classes_k67_B256.jsonl", 6, 7, 256), ("n4_classes_k8_B192.jsonl.gz", 8, 8, 192),
         ("n4_classes_k9_B192.jsonl.gz", 9, 9, 192)]


def rows():
    for fn, lo, hi, B in FILES:
        op = gzip.open if fn.endswith(".gz") else open
        with op(os.path.join(HERE, fn), "rt") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if lo <= r["bottom"] <= hi and any(p["birth"] <= B // 4 for p in r["pairs"]):
                    M = r["bottom_quiver"]
                    yield tuple(M[i][j] for (i, j) in L.PAIRS)


def work(t):
    found, _, _ = L.bfs_within(t, L.ht(t))
    r = L.my_resolve(t, budget=500_000)
    return L.canon(t), found is not None, r[0], r[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    t0 = time.time()
    qs = list(rows())
    with Pool(a.workers) as pool:
        out = pool.map(work, qs, chunksize=256)
    tally = Counter((("bottom reaches acyclic within its height" if f else "bottom fails"), v, c) for _, f, v, c in out)
    print(f"{len(qs)} census classes with a pocket born <= B/4; {len({c for c, _, _, _ in out})} distinct bottoms "
          f"up to relabelling")
    for k, v in sorted(tally.items()):
        print(f"  {k}: {v}")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
