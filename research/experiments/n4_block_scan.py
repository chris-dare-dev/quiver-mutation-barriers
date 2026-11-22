#!/usr/bin/env python
"""n4_block_scan.py -- note 10: the heavy-block shape H(a, c, p, q); usage: n4_block_scan.py AMAX OUT.jsonl"""
# H(a, c, p, q): rows (0, -p, -a, c), (p, 0, c, -a), (a, -c, 0, -q), (-c, a, q, 0); scan for the join of the
# bottom pieces relative to the class bottom squared.
import os, sys, json
E = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, E)
import numpy as np
from multiprocessing import Pool
from mutation_path import DT
from bounded_paths import enumerate_component
from pockets import persistence

def H(a, c, p, q):
    return np.array([[0, -p, -a, c], [p, 0, c, -a], [a, -c, 0, -q], [-c, a, q, 0]], dtype=DT)

def task(t):
    a, c, p, q = t
    B = H(a, c, p, q)
    st, ex = enumerate_component(B, 3 * a * a, 400000, unlabelled=True)
    if not ex: return None
    pairs, lo, _, _ = persistence(st, 4)
    j = max([d for bb, d, _, _ in pairs if bb == lo], default=None)
    return {"a": a, "c": c, "p": p, "q": q, "bottom": lo, "join": j, "size": len(st)}

if __name__ == "__main__":
    amax = int(sys.argv[1])
    tasks = [(a, c, p, q) for a in range(3, amax + 1) for c in range(0, a + 1) for p in range(0, a + 1) for q in range(0, a + 1)]
    best = {}
    with Pool(12) as pool, open(sys.argv[2], "w") as f:
        for r in pool.imap_unordered(task, tasks, chunksize=16):
            if not r or not r["join"]: continue
            f.write(json.dumps(r) + "\n")
            q = r["join"] / r["bottom"] ** 2
            if q > best.get(r["bottom"], (0,))[0]: best[r["bottom"]] = (q, r)
    for b in sorted(best): print(f"bottom {b:>2}: max join/bottom^2 = {best[b][0]:.3f}  {best[b][1]}")
