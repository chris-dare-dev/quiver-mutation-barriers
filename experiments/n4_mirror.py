#!/usr/bin/env python
"""
n4_mirror.py -- families of 4-vertex classes whose two bottom components are mirror images (note 9).

G(b, T): vertex 0 with arrows 0 -> 1, 2 -> 0, 3 -> 0 of weight b, attached to a triangle T on the
vertices 1, 2, 3 given by (b12, b13, b23).  For each (b, T) the script enumerates the class (up to
relabelling) inside bound K*b, computes its persistence pairs, and reports the class bottom, the
number of bottom components, whether G and its opposite -G are both at the bottom in different
components, and the death of the younger bottom component (the level at which the two join).

Run from experiments/ with python -I.
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT  # noqa: E402
from bounded_paths import enumerate_component, canonical  # noqa: E402
from pockets import persistence  # noqa: E402


def G(b, T):
    b12, b13, b23 = T
    B = np.zeros((4, 4), dtype=DT)
    B[0, 1], B[2, 0], B[3, 0] = b, b, b
    B[1, 2], B[1, 3], B[2, 3] = b12, b13, b23
    return B - B.T


def measure(task):
    b, T, K, budget = task
    x = G(b, T)
    states, ex = enumerate_component(x, K * b, budget, unlabelled=True)
    pairs, lo, eldest, _ = persistence(states, 4)
    bottom_pairs = [(bb, d) for bb, d, _, _ in pairs if bb == lo]
    kx, km = canonical(x).tobytes(), canonical(-x).tobytes()
    return {"b": b, "T": list(T), "K": K, "size": len(states), "exhausted": ex, "bottom": lo,
            "x_at_bottom": states[kx] == lo, "mirror_in_class": km in states,
            "bottom_components": 1 + len(bottom_pairs),
            "join": max([d for _, d in bottom_pairs], default=None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=int, nargs=3, action="append", required=True, help="triangle (b12 b13 b23); repeatable")
    ap.add_argument("--b", type=int, nargs="+", required=True)
    ap.add_argument("--K", type=int, default=24)
    ap.add_argument("--budget", type=int, default=3000000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    tasks = [(b, tuple(T), args.K, args.budget) for T in args.T for b in args.b if b >= max(abs(t) for t in T)]
    with Pool(args.workers) as pool, open(args.out, "w") as f:
        for r in pool.imap(measure, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            j = r["join"]
            print(f"T={tuple(r['T'])} b={r['b']}: class bottom {r['bottom']} (G at bottom: {r['x_at_bottom']}), bottom components "
                  f"{r['bottom_components']}, mirror in class {r['mirror_in_class']}, join {j}"
                  + (f" = {j / r['b']:.2f} b" if j else "") + f", size {r['size']}, exhausted {r['exhausted']}", flush=True)


if __name__ == "__main__":
    main()
