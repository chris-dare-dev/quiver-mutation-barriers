#!/usr/bin/env python
"""
n4_all.py -- persistence of the maximal-entry filtration over ALL 4-vertex quivers (note 7).

Every skew-symmetric 4x4 integer matrix with maximal entry <= N is enumerated up to relabelling
(numpy, canonical keys over the 24 relabellings).  Edges are mutations between them.  Processing
the levels L = 1..N in order with vectorized union-find, a component is born at L when all its
quivers have maximal entry L, and dies when it merges into an older component (elder rule; ties
broken by node order).  Every class of 4-vertex quivers whose bottom has maximal entry <= N is
covered at once, so the pockets found (birth b, death D <= N) are all pockets of all such classes
with death <= N.  Components still alive at N are class bottoms or pockets with death > N.

Subcommands:
  run   one JSON file with the persistence pairs, the pocket quivers and per-level counts

Run from experiments/ with python -I.  Needs a few GB of memory for N = 16.
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n4_plateaus import IDX, SGN, to_full, to_upper, mutate_batch, is_acyclic  # noqa: E402


def keys_of(X, N):
    base = 2 * N + 1
    w = base ** np.arange(5, -1, -1, dtype=np.int64)
    best = None
    for a in range(24):
        k = ((X[:, IDX[a]] * SGN[a] + N) * w).sum(axis=1)
        best = k if best is None else np.minimum(best, k)
    return best


def decode(keys, N):
    base = 2 * N + 1
    out = np.zeros((keys.size, 6), dtype=np.int64)
    k = keys.copy()
    for pos in range(5, -1, -1):
        out[:, pos] = k % base - N
        k //= base
    return out


def level_keys(M, N):
    """Canonical keys (global base 2N+1) of all quivers with maximal entry exactly M."""
    r = np.arange(-M, M + 1, dtype=np.int64)
    rest = np.stack([x.ravel() for x in np.meshgrid(r, r, r, r, indexing="ij")], axis=1)
    out = []
    for b02 in r:
        X = np.concatenate([np.full((rest.shape[0], 1), M), np.full((rest.shape[0], 1), b02), rest], axis=1)
        out.append(np.unique(keys_of(X, N)))
    return np.unique(np.concatenate(out))


def run(N, log, keep_survivors=0):
    t0 = time.time()
    keys, lev = [], []
    for M in range(1, N + 1):
        k = level_keys(M, N)
        keys.append(k)
        lev.append(np.full(k.size, M, dtype=np.int16))
        log(f"  level {M}: {k.size} quivers ({time.time() - t0:.0f}s)")
    keys = np.concatenate(keys)
    lev = np.concatenate(lev)
    order = np.argsort(keys)
    keys, lev = keys[order], lev[order]
    nV = keys.size
    log(f"{nV} quivers with maximal entry <= {N}")
    # edges, by level
    eu, ev, el = [], [], []
    CH = 2_000_000
    for s in range(0, nV, CH):
        X = decode(keys[s:s + CH], N)
        B = to_full(X)
        idx = np.arange(s, min(s + CH, nV))
        for k in range(4):
            Nk = mutate_batch(B, k)
            me = np.abs(Nk).reshape(Nk.shape[0], -1).max(axis=1)
            sel = np.flatnonzero(me <= N)
            nk = keys_of(to_upper(Nk[sel]), N)
            j = np.searchsorted(keys, nk)
            assert np.all(keys[j] == nk)
            keep = j > idx[sel]                       # each undirected edge once
            eu.append(idx[sel][keep].astype(np.int64))
            ev.append(j[keep].astype(np.int64))
            el.append(np.maximum(lev[idx[sel][keep]], me[sel][keep]).astype(np.int16))
        log(f"  edges for quivers {s}..{min(s + CH, nV)} ({time.time() - t0:.0f}s)")
    eu, ev, el = np.concatenate(eu), np.concatenate(ev), np.concatenate(el)
    log(f"{eu.size} edges")
    # incremental union-find by level, elder rule on tracked components
    parent = np.arange(nV, dtype=np.int64)
    rep = np.zeros(0, dtype=np.int64)
    birth = np.zeros(0, dtype=np.int16)
    alive = np.zeros(0, dtype=bool)
    pairs = []
    per_level = []
    for L in range(1, N + 1):
        m = el == L
        u, v = eu[m], ev[m]
        while u.size:
            pu, pv = parent[u], parent[v]
            lo, hi = np.minimum(pu, pv), np.maximum(pu, pv)
            d = lo != hi
            if not d.any():
                break
            np.minimum.at(parent, hi[d], lo[d])
            while True:
                pp = parent[parent]
                if np.array_equal(pp, parent):
                    break
                parent = pp
        active = np.flatnonzero(lev <= L)
        root = parent[active]
        minlev = np.full(nV, 1 << 14, dtype=np.int64)
        np.minimum.at(minlev, root, lev[active])
        new_roots = np.unique(root[minlev[root] == L])
        rep = np.concatenate([rep, new_roots])
        birth = np.concatenate([birth, np.full(new_roots.size, L, dtype=np.int16)])
        alive = np.concatenate([alive, np.ones(new_roots.size, dtype=bool)])
        ai = np.flatnonzero(alive)
        r = parent[rep[ai]]
        o = np.lexsort((rep[ai], birth[ai], r))
        rs = r[o]
        first = np.ones(o.size, dtype=bool)
        first[1:] = rs[1:] != rs[:-1]
        dead = ai[o[~first]]
        for t in dead:
            if birth[t] < L:
                pairs.append((int(birth[t]), L, int(rep[t])))
        alive[dead] = False
        per_level.append({"L": L, "quivers": int((lev == L).sum()), "born": int(new_roots.size),
                          "alive_components": int(alive.sum()), "pockets_dying": int(sum(1 for t in dead if birth[t] < L))})
        log(f"  L={L}: born {new_roots.size}, pockets dying {per_level[-1]['pockets_dying']}, alive {alive.sum()} ({time.time() - t0:.0f}s)")
    # the bottom of each pocket's class (within N): the lowest level in its final component
    final_min = np.full(nV, 1 << 14, dtype=np.int64)
    np.minimum.at(final_min, parent, lev)
    pockets = []
    for b, d, rp in pairs:
        Bq = to_full(decode(keys[rp:rp + 1], N))[0]
        pockets.append({"birth": b, "death": d, "bottom": int(final_min[parent[rp]]), "quiver": Bq.tolist(),
                        "acyclic": is_acyclic(Bq)})
    surv = birth[alive]
    kept = [to_full(decode(keys[rp:rp + 1], N))[0].tolist()
            for rp, b in zip(rep[alive], birth[alive]) if b <= keep_survivors]
    return {"N": N, "quivers": int(nV), "edges": int(eu.size), "per_level": per_level, "pockets": pockets,
            "survivors_by_birth": np.bincount(surv, minlength=N + 1).tolist(), "survivors": kept,
            "time": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--N", type=int, required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--keep-survivors", type=int, default=0, help="store the components born at levels <= this that survive to N")
    args = ap.parse_args()
    res = run(args.N, lambda s: print(s, flush=True), args.keep_survivors)
    with open(args.out, "w") as f:
        json.dump(res, f)
    pk = res["pockets"]
    print(f"pockets (death <= {args.N}): {len(pk)}; births {sorted(set(p['birth'] for p in pk))}; "
          f"max death/birth {max([p['death'] / p['birth'] for p in pk] or [0]):.2f}")


if __name__ == "__main__":
    main()
