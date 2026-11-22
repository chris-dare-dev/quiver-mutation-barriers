#!/usr/bin/env python
"""
n4_classes.py -- per-class persistence for every 4-vertex class with a low bottom (note 8).

Input: the components born at levels <= L that survive to level N in n4_all.py (option
--keep-survivors), i.e. every class bottom at level <= L plus the low pockets still unmerged at N.
For each, the class (up to relabelling) is enumerated inside a larger bound B and its persistence
pairs are computed as in pockets.py.  Classes met several times are kept once (key: the least
canonical quiver at the class's lowest level).  This extends the n4_all census, which is exact only
for deaths <= N, to deaths <= B for the low classes.

Run from experiments/ with python -I.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT  # noqa: E402
from bounded_paths import enumerate_component  # noqa: E402
from pockets import persistence  # noqa: E402


def _task(task):
    q, bound, budget = task
    t0 = time.time()
    states, exhausted = enumerate_component(np.array(q, dtype=DT), bound, budget, unlabelled=True)
    pairs, lo, eldest, alive = persistence(states, 4)
    key = min(k for k, v in states.items() if v == lo)
    return {"key": key.hex(), "bottom": lo, "bottom_quiver": np.frombuffer(key, dtype=DT).reshape(4, 4).tolist(),
            "size": len(states), "exhausted": exhausted, "bottom_components": 1 + sum(1 for b, d, _, _ in pairs if b == lo),
            "pairs": [{"birth": b, "death": d, "size": sz, "quiver": np.frombuffer(rp, dtype=DT).reshape(4, 4).tolist()}
                      for b, d, rp, sz in pairs],
            "time": round(time.time() - t0, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("survivors", help="n4_all.py output with survivors")
    ap.add_argument("--B", type=int, default=128)
    ap.add_argument("--budget", type=int, default=2000000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-level", type=int, default=0, help="skip components born below this level")
    ap.add_argument("--max-level", type=int, default=10 ** 9, help="skip components born above this level")
    args = ap.parse_args()
    qs = [q for q in json.load(open(args.survivors))["survivors"] if args.min_level <= np.abs(np.array(q)).max() <= args.max_level]
    seen = set()
    n = 0
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_task, [(q, args.B, args.budget) for q in qs], chunksize=4):
            if r["key"] in seen:
                continue
            seen.add(r["key"])
            n += 1
            f.write(json.dumps(r) + "\n")
    rows = [json.loads(l) for l in open(args.out)]
    print(f"{len(qs)} components -> {len(rows)} classes, exhausted {sum(r['exhausted'] for r in rows)}")
    P = [(r, p) for r in rows if r["exhausted"] for p in r["pairs"] if p["birth"] <= args.B // 4]
    rat = [p["death"] / p["birth"] for _, p in P]
    print(f"pockets born <= B/4: {len(P)}; death/birth max {max(rat):.2f}" if P else "no pockets")
    for r, p in sorted(P, key=lambda x: -x[1]["death"] / x[1]["birth"])[:12]:
        print(f"  bottom {r['bottom']} ({r['bottom_components']} bottom components): birth {p['birth']} death {p['death']} ratio {p['death'] / p['birth']:.2f}")


if __name__ == "__main__":
    main()
