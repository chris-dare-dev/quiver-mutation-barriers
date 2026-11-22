#!/usr/bin/env python
"""
n4_plateaus.py -- every 4-vertex quiver, level by level: where can pockets be born? (note 7)

A pocket is born at level M exactly when some connected component of the *plateau graph* P_M
(quivers up to relabelling with maximal entry exactly M, joined by mutations that keep the
maximal entry equal to M) has no *exit*, i.e. no member with a mutation of maximal entry < M,
and is not the lowest component of its class.  Call such a component an isolated plateau
component (IPC).  An IPC is either the bottom of its mutation class or a pocket.

For each M this script builds P_M exhaustively (all skew-symmetric 4x4 integer matrices with
maximal entry M, up to relabelling), finds its components with numpy, and lists the IPCs.  Each
IPC is classified as
  acyclic       some member is acyclic (then, by Caldero-Keller, the class is mutation-acyclic and
                its acyclic members are related by sink/source mutations, which keep the weights);
  other         no member is acyclic.
For the IPCs it then runs a bottleneck search for a quiver of maximal entry < M (cap K*M): if one
is found the IPC is a pocket and the search height is its death; if none is found within the cap,
the IPC is reported as a candidate class bottom.

Subcommands:
  scan       levels M = lo..hi; one JSONL row per level
  summarize  table from the JSONL file

Run from experiments/ with python -I.
"""
import argparse
import heapq
import itertools
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT, all_mutations, max_entry_per_k  # noqa: E402
from bounded_paths import canonical  # noqa: E402

UP = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
PERMS = list(itertools.permutations(range(4)))
# for relabelling p (new vertex i is old vertex p[i]): new upper entry pos = sgn * old upper entry idx
IDX = np.zeros((24, 6), dtype=np.int64)
SGN = np.zeros((24, 6), dtype=np.int64)
for a, p in enumerate(PERMS):
    for pos, (i, j) in enumerate(UP):
        u, v = p[i], p[j]
        IDX[a, pos] = UP.index((min(u, v), max(u, v)))
        SGN[a, pos] = 1 if u < v else -1


def canon_keys(X, M):
    """X: (m, 6) upper-triangle entries with |entries| <= M.  Canonical key: least base-(2M+1)
    encoding over the 24 relabellings."""
    base = 2 * M + 1
    w = base ** np.arange(5, -1, -1, dtype=np.int64)
    best = None
    for a in range(24):
        k = ((X[:, IDX[a]] * SGN[a] + M) * w).sum(axis=1)
        best = k if best is None else np.minimum(best, k)
    return best


def decode(keys, M):
    base = 2 * M + 1
    out = np.zeros((keys.size, 6), dtype=np.int64)
    k = keys.copy()
    for pos in range(5, -1, -1):
        out[:, pos] = k % base - M
        k //= base
    return out


def to_full(X):
    B = np.zeros((X.shape[0], 4, 4), dtype=np.int64)
    for pos, (i, j) in enumerate(UP):
        B[:, i, j] = X[:, pos]
        B[:, j, i] = -X[:, pos]
    return B


def to_upper(B):
    return np.stack([B[:, i, j] for i, j in UP], axis=1)


def mutate_batch(B, k):
    col = B[:, :, k]
    row = B[:, k, :]
    add = (np.abs(col)[:, :, None] * row[:, None, :] + col[:, :, None] * np.abs(row)[:, None, :]) // 2
    N = B + add
    N[:, k, :] = -row
    N[:, :, k] = -col
    return N


def plateau_nodes(M, chunk_first=True):
    """Canonical keys of all quivers with maximal entry exactly M (generated with b01 = +M)."""
    r = np.arange(-M, M + 1, dtype=np.int64)
    rest = np.stack([x.ravel() for x in np.meshgrid(r, r, r, r, indexing="ij")], axis=1)   # b03 b12 b13 b23
    keys = []
    for b02 in r:
        X = np.concatenate([np.full((rest.shape[0], 1), M), np.full((rest.shape[0], 1), b02), rest], axis=1)
        keys.append(np.unique(canon_keys(X, M)))
    return np.unique(np.concatenate(keys))


def components(n, u, v):
    """Connected components by hooking and pointer jumping; returns the root of every node."""
    parent = np.arange(n, dtype=np.int64)
    while True:
        pu, pv = parent[u], parent[v]
        lo, hi = np.minimum(pu, pv), np.maximum(pu, pv)
        m = lo != hi
        if not m.any():
            return parent
        np.minimum.at(parent, hi[m], lo[m])
        while True:
            pp = parent[parent]
            if np.array_equal(pp, parent):
                break
            parent = pp


def is_acyclic(B):
    rem = set(range(B.shape[0]))
    while rem:
        src = [i for i in rem if not any(B[j, i] > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def lower_search(x, M, cap, budget):
    """Bottleneck search from x for a quiver of maximal entry < M through quivers of maximal entry
    <= cap.  Returns the search height (the death of x's pocket) or None."""
    n = 4
    start = canonical(x).tobytes()
    best = {start: M}
    heap = [(M, start)]
    done = set()
    while heap and len(done) < budget:
        h, k = heapq.heappop(heap)
        if k in done:
            continue
        done.add(k)
        B = np.frombuffer(k, dtype=DT).reshape(n, n)
        if np.abs(B).max() < M:
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


def scan_level(M, cap_ratio, budget, max_search):
    t0 = time.time()
    keys = plateau_nodes(M)
    nV = keys.size
    X = decode(keys, M)
    B = to_full(X)
    exit_ = np.zeros(nV, dtype=bool)
    us, vs = [], []
    for k in range(4):
        N = mutate_batch(B, k)
        me = np.abs(N).reshape(nV, -1).max(axis=1)
        exit_ |= me < M
        sel = np.flatnonzero(me == M)
        if sel.size:
            nk = canon_keys(to_upper(N[sel]), M)
            idx = np.searchsorted(keys, nk)
            assert np.all(keys[idx] == nk)
            us.append(sel)
            vs.append(idx)
    u = np.concatenate(us) if us else np.zeros(0, dtype=np.int64)
    v = np.concatenate(vs) if vs else np.zeros(0, dtype=np.int64)
    root = components(nV, u, v)
    roots, inv = np.unique(root, return_inverse=True)
    has_exit = np.zeros(roots.size, dtype=bool)
    np.logical_or.at(has_exit, inv, exit_)
    sizes = np.bincount(inv)
    ipc = np.flatnonzero(~has_exit)
    rows = []
    for c in ipc:
        members = np.flatnonzero(inv == c)
        Bs = B[members]
        acyc = any(is_acyclic(b) for b in Bs[:64])
        rows.append({"size": int(sizes[c]), "acyclic": bool(acyc), "rep": Bs[0].tolist()})
    # bottleneck searches for the non-acyclic IPCs (and a sample of acyclic ones)
    others = [r for r in rows if not r["acyclic"]]
    acyc = [r for r in rows if r["acyclic"]]
    rng = np.random.default_rng(M)
    sample = list(rng.choice(len(acyc), size=min(len(acyc), max_search), replace=False)) if acyc else []
    for r in others[:max_search] + [acyc[i] for i in sample]:
        d = lower_search(np.array(r["rep"], dtype=DT), M, cap_ratio * M, budget)
        r["death"] = d
    return {"M": M, "plateau_quivers": int(nV), "components": int(roots.size), "ipc": len(rows),
            "ipc_acyclic": len(acyc), "ipc_other": len(others),
            "searched_other": min(len(others), max_search), "searched_acyclic": len(sample),
            "pockets_other": [r for r in others if r.get("death")],
            "pockets_acyclic": [r for r in acyc if r.get("death")],
            "unresolved_other": [r for r in others[:max_search] if "death" in r and r["death"] is None][:50],
            "time": round(time.time() - t0, 1)}


def cmd_scan(args):
    with open(args.out, "a" if args.append else "w") as f:
        for M in range(args.lo, args.hi + 1):
            r = scan_level(M, args.cap_ratio, args.budget, args.max_search)
            f.write(json.dumps(r) + "\n")
            f.flush()
            print(f"M={M}: {r['plateau_quivers']} quivers, {r['components']} plateau components, IPCs {r['ipc']} "
                  f"(acyclic {r['ipc_acyclic']}, other {r['ipc_other']}); pockets among searched: other "
                  f"{len(r['pockets_other'])}/{r['searched_other']}, acyclic {len(r['pockets_acyclic'])}/{r['searched_acyclic']} ({r['time']}s)",
                  flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    sc.add_argument("--lo", type=int, default=3)
    sc.add_argument("--hi", type=int, default=12)
    sc.add_argument("--cap-ratio", type=int, default=4)
    sc.add_argument("--budget", type=int, default=200000)
    sc.add_argument("--max-search", type=int, default=400)
    sc.add_argument("--out", required=True)
    sc.add_argument("--append", action="store_true")
    sc.set_defaults(func=cmd_scan)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
