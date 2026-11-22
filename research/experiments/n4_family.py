#!/usr/bin/env python
"""
n4_family.py -- an infinite family of pockets on 4 vertices (note 7).

P_k has rows (0, -k, -(k-1), k), (k, 0, -2, 1), (k-1, 2, 0, -2), (-k, -1, 2, 0).  For each k the
script checks, by exact computation up to relabelling:
  1. the plateau component of P_k at level k (quivers of maximal entry exactly k joined by
     mutations that keep it) has no exit, i.e. no member has a mutation of maximal entry < k;
  2. the least bound at which P_k reaches a quiver of maximal entry < k (bottleneck search) is D_k;
  3. P_k and P_{k-1} are joined inside bound k + 2 (so all P_k lie in one class).
Together: P_k is born at level k and dies at D_k, in the class of P_5.

Run from experiments/ with python -I.
"""
import argparse
import heapq
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT, all_mutations, max_entry_per_k  # noqa: E402
from bounded_paths import canonical  # noqa: E402


def P(k):
    return np.array([[0, -k, -(k - 1), k], [k, 0, -2, 1], [k - 1, 2, 0, -2], [-k, -1, 2, 0]], dtype=DT)


def plateau(x, M):
    """Plateau component of x at level M; returns (size, has_exit)."""
    start = canonical(x).tobytes()
    seen, todo, exit_ = {start}, [start], False
    while todo:
        k = todo.pop()
        B = np.frombuffer(k, dtype=DT).reshape(4, 4)
        N = all_mutations(B)
        me = max_entry_per_k(N)
        if (me < M).any():
            exit_ = True
        for j in np.flatnonzero(me == M):
            nb = canonical(N[j]).tobytes()
            if nb not in seen:
                seen.add(nb)
                todo.append(nb)
    return len(seen), exit_


def bottleneck(x, target, cap):
    """Least height of a path from x to a quiver satisfying target (bound cap)."""
    start = canonical(x).tobytes()
    best = {start: int(np.abs(x).max())}
    heap = [(best[start], start)]
    done = set()
    while heap:
        h, k = heapq.heappop(heap)
        if k in done:
            continue
        done.add(k)
        B = np.frombuffer(k, dtype=DT).reshape(4, 4)
        if target(B, k):
            return h
        N = all_mutations(B)
        me = max_entry_per_k(N)
        for j in np.flatnonzero(me <= cap):
            nb = canonical(N[j]).tobytes()
            v = max(h, int(me[j]))
            if nb not in done and v < best.get(nb, 1 << 62):
                best[nb] = v
                heapq.heappush(heap, (v, nb))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kmin", type=int, default=5)
    ap.add_argument("--kmax", type=int, default=200)
    args = ap.parse_args()
    bottom = bottleneck(P(args.kmin), lambda B, k: np.abs(B).max() <= 4, 4 * args.kmin)
    print(f"P_{args.kmin} reaches maximal entry <= 4 at bound {bottom}")
    for k in range(args.kmin, args.kmax + 1):
        size, ex = plateau(P(k), k)
        D = bottleneck(P(k), lambda B, kk: np.abs(B).max() < k, 2 * k)
        prev = canonical(P(k - 1)).tobytes()
        link = bottleneck(P(k), lambda B, kk: kk == prev, k + 2) if k > args.kmin else None
        print(f"k={k}: plateau component size {size}, exit {ex}, death {D}, joined to P_{k-1} at bound {link}", flush=True)


if __name__ == "__main__":
    main()
