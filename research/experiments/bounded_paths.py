#!/usr/bin/env python
"""
bounded_paths.py -- a test of the bounded-path conjecture for quiver mutation (note 2).

Conjecture (suggested by note 1).  Let Q, Q' be mutation-equivalent quivers on n vertices
with all |entries| <= w.  Then some mutation path from Q to Q' keeps every intermediate
quiver at |entries| <= f(n, w), with f(n, w) close to w.  In words: high-weight excursions
are dead-end spikes, never bridges between low-weight regions.  If f is effective, iterative
deepening on the bound (note 1, attack A3) decides mutation equivalence.

Two measurements.
  profile     Exhaustively enumerate the component C of Q inside a large bound B_big.  For
              each w, let S_w = {X in C : maxentry(X) <= w}.  Adding states in order of
              increasing max entry with incremental union-find, record the least ambient
              bound w' at which S_w becomes connected.  That w' is f(n, w) for this
              component (exact when C is exhausted; a lower bound otherwise).
  excursions  From Q (weight <= 3), random-walk inside a huge bound until some entry
              exceeds W_high, then descend greedily on total weight to a local minimum Q'.
              Find the least bound at which Q and Q' connect (iterative deepening, node
              budget per level).  If the connecting bound stays near max(w_Q, w_Q')
              whatever W_high is, excursions are spikes; if it grows with W_high, bridges.

Correction (note 3).  Up to note 2, profile tested S_w only at levels >= w, so when no
quiver of the class has maximal entry in [w, f) it reported the next level present as f(w).
f(w) is now the least level >= m_w (the largest level <= w) at which S_w is connected, so
f(w) <= w means "no excess"; the old value is kept as f_note2.  --unlabelled runs the same
measurement on quivers up to relabelling of the vertices (canonical form under S_n).

Run from experiments/ with python -I.  Reuses the kernels of mutation_path.py.
"""
import argparse
import bisect
import itertools
import json
import os
import sys
import time
from collections import deque, defaultdict
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import (DT, all_mutations, mutate, random_quiver, weight, max_entry_per_k,  # noqa: E402
                           bidir_bfs, descend)


# ----------------------------------------------------------------------------- starting quivers
def random_sparse_quiver(n, rng, extra_edges=None):
    """Connected sparse quiver: a random spanning tree plus `extra_edges` further edges
    (default: 0, 1 or 2 at random), random orientations, all weights 1 except one edge of
    weight 3, which guarantees an infinite mutation class."""
    if extra_edges is None:
        extra_edges = int(rng.integers(0, 3))
    B = np.zeros((n, n), dtype=DT)
    order = rng.permutation(n)
    edges = []
    for i in range(1, n):
        j = int(order[int(rng.integers(0, i))])
        edges.append((int(order[i]), j))
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if (a, b) not in edges and (b, a) not in edges]
    for idx in rng.permutation(len(pairs))[:extra_edges]:
        edges.append(pairs[int(idx)])
    heavy = int(rng.integers(0, len(edges)))
    for e, (a, b) in enumerate(edges):
        w = 3 if e == heavy else 1
        if rng.integers(0, 2):
            a, b = b, a
        B[a, b] = w
        B[b, a] = -w
    return B


def make_quiver(n, rng, sparse):
    return random_sparse_quiver(n, rng) if sparse else random_quiver(n, rng)


# ----------------------------------------------------------------------------- union-find
class UF:
    def __init__(self):
        self.p = {}

    def add(self, x):
        if x not in self.p:
            self.p[x] = x

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb
        return ra != rb


# ----------------------------------------------------------------------------- relabelling
_PERM_INDEX = {}


def _perm_index(n):
    if n not in _PERM_INDEX:
        perms = np.array(list(itertools.permutations(range(n))), dtype=np.intp)
        _PERM_INDEX[n] = (perms, (perms[:, :, None] * n + perms[:, None, :]).reshape(len(perms), n * n))
    return _PERM_INDEX[n]


def canonical(B):
    """Lexicographically least P B P^T over the permutations that list the vertices in
    increasing order of a vertex invariant (the sorted row): the quiver up to relabelling of
    its vertices.  The admissible set is equivariant, so the result is a canonical form.
    Mutation commutes with relabelling, so the mutation graph descends to canonical forms."""
    n = B.shape[0]
    perms, idx = _perm_index(n)
    _, inv = np.unique(np.sort(B, axis=1), axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    ok = (inv[perms[:, :-1]] <= inv[perms[:, 1:]]).all(axis=1)
    X = B.reshape(-1)[idx[ok]]
    return X[np.lexsort(X.T[::-1])[0]].reshape(n, n)


def _key(B, unlabelled):
    return canonical(B).tobytes() if unlabelled else B.tobytes()


# ----------------------------------------------------------------------------- profile
def enumerate_component(Q, bound, budget, unlabelled=False):
    """BFS inside the bound; returns dict state_bytes -> max entry, and exhausted flag.
    With unlabelled=True the states are canonical forms (quivers up to relabelling)."""
    n = Q.shape[0]
    start = _key(Q, unlabelled)
    seen = {start: int(np.abs(Q).max())}
    dq = deque([start])
    while dq and len(seen) < budget:
        ck = dq.popleft()
        cur = np.frombuffer(ck, dtype=DT).reshape(n, n)
        N = all_mutations(cur)
        me = max_entry_per_k(N)
        for k in np.flatnonzero(me <= bound):
            kb = _key(N[k], unlabelled)
            if kb not in seen:
                seen[kb] = int(me[k])
                dq.append(kb)
    return seen, not dq


def merging_profile(Q, bound, budget, w_list, unlabelled=False):
    n = Q.shape[0]
    t0 = time.time()
    states, exhausted = enumerate_component(Q, bound, budget, unlabelled)
    t_enum = time.time() - t0
    by_level = defaultdict(list)
    for kb, me in states.items():
        by_level[me].append(kb)
    levels = sorted(by_level)
    # S_w is complete once the largest level m_w <= w has been added; connectivity can only
    # change at a level that is present, so f(w) is the least present level >= m_w at which
    # S_w is connected (f(w) <= w: no excess).
    # S_w = S_{m_w} and f(w) = f(m_w).  Components only merge, so the prefix of `order` known to
    # lie in the component of order[0] only grows; S_m is connected once that prefix covers it.
    m_of_w = {w: levels[bisect.bisect_right(levels, w) - 1] for w in w_list if w >= levels[0]}
    ms = sorted(set(m_of_w.values()))
    uf = UF()
    present = set()
    order = []              # states in order of addition; S_m is a prefix
    prefix = {}
    f_of_m = {}
    classes_at_m = {}
    pos = 0
    joined = 0              # order[:joined] all lie in the component of order[0]
    n_comp = 0              # components among the states present (= of S_lvl at bound lvl)
    for lvl in levels:
        new = by_level[lvl]
        for kb in new:
            uf.add(kb)
            present.add(kb)
        n_comp += len(new)
        for kb in new:
            cur = np.frombuffer(kb, dtype=DT).reshape(n, n)
            N = all_mutations(cur)
            me = max_entry_per_k(N)
            for k in np.flatnonzero(me <= lvl):
                nb = _key(N[k], unlabelled)
                if nb in present and uf.union(kb, nb):
                    n_comp -= 1
        order.extend(new)
        prefix[lvl] = len(order)
        if lvl in ms:
            classes_at_m[lvl] = n_comp                    # components of S_m at ambient bound m
        root0 = uf.find(order[0])
        while joined < len(order) and uf.find(order[joined]) == root0:
            joined += 1
        while pos < len(ms) and ms[pos] <= lvl and joined >= prefix[ms[pos]]:
            f_of_m[ms[pos]] = lvl
            pos += 1
        if pos == len(ms):
            break
    f_of_w = {w: f_of_m[m] for w, m in m_of_w.items() if m in f_of_m}
    # the value the note-2 code reported: S_w was first tested at the least level >= w
    f_note2 = {}
    for w, fw in f_of_w.items():
        i = bisect.bisect_left(levels, w)
        f_note2[w] = fw if fw >= w else (levels[i] if i < len(levels) else None)
    return {"comp_size": len(states), "exhausted": exhausted, "levels": len(levels),
            "max_level": levels[-1], "enum_time": round(t_enum, 2), "unlabelled": bool(unlabelled),
            "S_size": {w: prefix[m] for w, m in m_of_w.items()},
            "classes_at_w": {w: classes_at_m[m] for w, m in m_of_w.items() if m in classes_at_m},
            "m": m_of_w, "f": f_of_w, "f_note2": f_note2,
            "unconnected_w": [w for w in m_of_w if w not in f_of_w]}


def _profile_task(task):
    n, bound, trial, seed, budget, w_list, sparse, unlabelled = task
    rng = np.random.default_rng(seed)
    Q = make_quiver(n, rng, sparse)
    r = merging_profile(Q, bound, budget, w_list, unlabelled)
    r.update({"n": n, "B_big": bound, "trial": trial, "seed": seed, "wQ": int(np.abs(Q).max()),
              "sparse": bool(sparse), "edges": int((Q != 0).sum() // 2)})
    return r


def cmd_profile(args):
    tasks = []
    s = args.seed
    for n in args.n:
        for trial in range(args.trials):
            s += 1
            tasks.append((n, args.B_big, trial, s, args.budget, args.w, args.sparse, args.unlabelled))
    print(f"{len(tasks)} profiles, {args.workers} workers", flush=True)
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_profile_task, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            fs = ", ".join(f"f({w})={r['f'].get(w, '>' + str(r['max_level']))}" for w in args.w if w in r["S_size"])
            print(f"  n={r['n']} trial={r['trial']}: comp {r['comp_size']} exhausted={r['exhausted']} "
                  f"maxlevel={r['max_level']}; {fs}", flush=True)


# ----------------------------------------------------------------------------- excursions
def walk_until_high(Q, W_high, B_walk, rng, max_steps=400):
    cur = Q.copy()
    prev = -1
    n = Q.shape[0]
    wmax = int(np.abs(Q).max())
    for t in range(max_steps):
        N = all_mutations(cur)
        me = max_entry_per_k(N)
        allowed = [k for k in range(n) if k != prev and me[k] <= B_walk]
        if not allowed:
            return None, t, wmax
        k = int(rng.choice(allowed))
        cur = N[k]
        prev = k
        wmax = max(wmax, int(me[k]))
        if me[k] >= W_high:
            return cur, t + 1, wmax
    return None, max_steps, wmax


def connection_bound(Q, Qp, start_bound, budget, caps):
    bounds = sorted(set([start_bound + d for d in range(0, 9)] + [c for c in caps if c > start_bound]))
    total = 0
    for b in bounds:
        found, path, nodes = bidir_bfs(Q, Qp, b, budget)
        total += nodes
        if found:
            return b, len(path), total, bounds
    return None, None, total, bounds


def _excursion_task(task):
    n, W_high, trial, seed, B_walk, budget, sparse = task
    rng = np.random.default_rng(seed)
    Q = make_quiver(n, rng, sparse)
    wQ = int(np.abs(Q).max())
    t0 = time.time()
    high, steps, wmax = walk_until_high(Q, W_high, B_walk, rng)
    row = {"n": n, "W_high": W_high, "trial": trial, "seed": seed, "wQ": wQ, "walk_steps": steps,
           "walk_max_entry": wmax, "reached_high": high is not None, "sparse": bool(sparse)}
    if high is None:
        row["time"] = round(time.time() - t0, 2)
        return row
    Qp, dpath = descend(high, B_walk, rng)
    wQp = int(np.abs(Qp).max())
    row.update({"descent_steps": len(dpath), "wQp": wQp, "weight_Qp": weight(Qp), "Qp_equals_Q": bool((Qp == Q).all())})
    start = max(wQ, wQp)
    b, plen, nodes, bounds = connection_bound(Q, Qp, start, budget, caps=[16, 32, 64, 128, 256, 1024])
    row.update({"start_bound": start, "connect_bound": b, "connect_excess": (b - start) if b is not None else None,
                "path_len": plen, "search_nodes": nodes, "bounds_tried": bounds, "time": round(time.time() - t0, 2)})
    return row


def cmd_excursions(args):
    tasks = []
    s = args.seed
    for n in args.n:
        for W in args.W_high:
            for trial in range(args.trials):
                s += 1
                tasks.append((n, W, trial, s, args.B_walk, args.budget, args.sparse))
    print(f"{len(tasks)} excursions, {args.workers} workers", flush=True)
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_excursion_task, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            if r.get("reached_high"):
                print(f"  n={r['n']} W_high={r['W_high']} trial={r['trial']}: walk {r['walk_steps']} steps to {r['walk_max_entry']}, "
                      f"descent {r['descent_steps']} steps to max entry {r['wQp']}, connect at bound {r['connect_bound']} "
                      f"(start {r['start_bound']}), path {r['path_len']}, nodes {r['search_nodes']}, {r['time']}s", flush=True)
            else:
                print(f"  n={r['n']} W_high={r['W_high']} trial={r['trial']}: walk stuck after {r['walk_steps']} steps (max {r['walk_max_entry']})", flush=True)


def cmd_summarize(args):
    rows = [json.loads(l) for l in open(args.file) if l.strip()]
    if rows and "W_high" in rows[0]:
        cells = defaultdict(list)
        for r in rows:
            cells[(r["n"], r["W_high"])].append(r)
        print(f"{'n':>2} {'W_high':>9} {'trials':>6} {'reached':>7} {'Qp==Q':>5} {'connected':>9} {'excess 0':>8} {'excess<=2':>9} {'max excess':>10} {'median path':>11} {'median nodes':>12}")
        for k in sorted(cells):
            rs = cells[k]
            re_ = [r for r in rs if r.get("reached_high")]
            con = [r for r in re_ if r.get("connect_bound") is not None]
            ex = [r["connect_excess"] for r in con]
            print(f"{k[0]:>2} {k[1]:>9} {len(rs):>6} {len(re_):>7} {sum(r.get('Qp_equals_Q', False) for r in re_):>5} {len(con):>9} "
                  f"{sum(e == 0 for e in ex):>8} {sum(e <= 2 for e in ex):>9} {max(ex) if ex else '-':>10} "
                  f"{int(np.median([r['path_len'] for r in con])) if con else '-':>11} {int(np.median([r['search_nodes'] for r in con])) if con else '-':>12}")
    else:
        cells = defaultdict(list)
        for r in rows:
            cells[r["n"]].append(r)
        for n in sorted(cells):
            rs = cells[n]
            ws = sorted({int(w) for r in rs for w in r["S_size"]})
            print(f"n={n}: {len(rs)} components, exhausted {sum(r['exhausted'] for r in rs)}/{len(rs)}, sizes {min(r['comp_size'] for r in rs)}..{max(r['comp_size'] for r in rs)}")
            print(f"  {'w':>3} {'#comps with S_w':>15} {'median |S_w|':>12} {'f(w)<=w':>8} {'f(w)<=w+1':>9} {'f(w)<=w+2':>9} {'max f(w)-w':>10} {'unconnected':>11}")
            for w in ws:
                have = [r for r in rs if str(w) in r["S_size"] or w in r["S_size"]]
                get = lambda d, w: d.get(str(w), d.get(w))
                fs = [get(r["f"], w) for r in have if get(r["f"], w) is not None]
                un = sum(1 for r in have if get(r["f"], w) is None)
                sz = [get(r["S_size"], w) for r in have]
                print(f"  {w:>3} {len(have):>15} {int(np.median(sz)) if sz else '-':>12} {sum(f <= w for f in fs):>8} {sum(f <= w + 1 for f in fs):>9} {sum(f <= w + 2 for f in fs):>9} {max(f - w for f in fs) if fs else '-':>10} {un:>11}")


def cmd_compare(args):
    """Labelled against unlabelled corrected profiles (note 3), components exhausted in both."""
    def load(p):
        return {(r["n"], r["trial"]): r for r in map(json.loads, open(p)) if r.get("exhausted")}
    lab, unl = load(args.labelled), load(args.unlabelled)
    keys = sorted(set(lab) & set(unl))
    print(f"{len(keys)} components exhausted in both runs ({len(lab)} labelled, {len(unl)} unlabelled)")
    ws = sorted({int(w) for k in keys for w in lab[k]["f"]})
    print(f"  {'w':>4} {'comps':>5} {'note2 f<=w':>11} {'lab f<=w':>8} {'unl f<=w':>8} {'note2 max f-w':>14} "
          f"{'lab max f-w':>11} {'unl max f-w':>11} {'lab max f/w':>11} {'unl max f/w':>11}")
    for w in ws:
        rows = [k for k in keys if str(w) in lab[k]["f"] and str(w) in unl[k]["f"]]
        if not rows:
            continue
        old = [lab[k]["f_note2"][str(w)] for k in rows if lab[k]["f_note2"][str(w)] is not None]
        fl = [lab[k]["f"][str(w)] for k in rows]
        fu = [unl[k]["f"][str(w)] for k in rows]
        print(f"  {w:>4} {len(rows):>5} {sum(f <= w for f in old):>11} {sum(f <= w for f in fl):>8} {sum(f <= w for f in fu):>8} "
              f"{max(f - w for f in old):>14} {max(f - w for f in fl):>11} {max(f - w for f in fu):>11} "
              f"{max(f / w for f in fl):>11.2f} {max(f / w for f in fu):>11.2f}")
    pairs = [(k, w) for k in keys for w in lab[k]["f"] if w in unl[k]["f"]]
    count = lambda d, key: sum(1 for k, w in pairs if d[k][key][w] is not None and d[k][key][w] > int(w))
    print(f"  (component, w) pairs with f(w) > w: note-2 rule {count(lab, 'f_note2')}/{len(pairs)}, "
          f"labelled {count(lab, 'f')}/{len(pairs)}, unlabelled {count(unl, 'f')}/{len(pairs)}")
    only = sorted(set(unl) - set(lab))
    if only:
        ex = sum(1 for k in only for w, v in unl[k]["f"].items() if v > int(w))
        print(f"  {len(only)} further components exhausted only up to relabelling: {ex} pairs with excess")
    print("  per component: threshold = largest f(w) with f(w) > w (none: '-'); islands at the smallest w")
    for k in keys:
        def thr(r):
            ex = [v for w, v in r["f"].items() if v > int(w)]
            return max(ex) if ex else "-"
        w0 = min(lab[k]["classes_at_w"], key=int)
        print(f"    n={k[0]} trial={k[1]:>2}: size lab {lab[k]['comp_size']:>8} unl {unl[k]['comp_size']:>7}; threshold lab {thr(lab[k])!s:>3} "
              f"unl {thr(unl[k])!s:>3}; islands at w={w0}: lab {lab[k]['classes_at_w'][w0]:>3} unl {unl[k]['classes_at_w'].get(w0, '-')!s:>3}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("profile")
    pr.add_argument("--n", type=int, nargs="+", default=[4, 5])
    pr.add_argument("--B-big", type=int, default=2 ** 16)
    pr.add_argument("--budget", type=int, default=3000000)
    pr.add_argument("--w", type=int, nargs="+", default=[3, 4, 5, 6, 8, 12, 16, 24, 32, 64])
    pr.add_argument("--trials", type=int, default=10)
    pr.add_argument("--workers", type=int, default=8)
    pr.add_argument("--seed", type=int, default=20261108)
    pr.add_argument("--out", default="bounded_profile.jsonl")
    pr.add_argument("--append", action="store_true")
    pr.add_argument("--sparse", action="store_true", help="sparse starting quivers (tree + 0-2 edges, one weight-3 edge)")
    pr.add_argument("--unlabelled", action="store_true", help="quivers up to relabelling of the vertices")
    pr.set_defaults(func=cmd_profile)
    ex = sub.add_parser("excursions")
    ex.add_argument("--n", type=int, nargs="+", default=[4, 5, 6])
    ex.add_argument("--W-high", type=int, nargs="+", default=[100, 10000, 1000000, 100000000])
    ex.add_argument("--B-walk", type=int, default=2 ** 29)
    ex.add_argument("--budget", type=int, default=300000)
    ex.add_argument("--trials", type=int, default=15)
    ex.add_argument("--workers", type=int, default=8)
    ex.add_argument("--seed", type=int, default=20261109)
    ex.add_argument("--out", default="bounded_excursions.jsonl")
    ex.add_argument("--append", action="store_true")
    ex.add_argument("--sparse", action="store_true")
    ex.set_defaults(func=cmd_excursions)
    sm = sub.add_parser("summarize")
    sm.add_argument("file")
    sm.set_defaults(func=cmd_summarize)
    cp = sub.add_parser("compare")
    cp.add_argument("labelled")
    cp.add_argument("unlabelled")
    cp.set_defaults(func=cmd_compare)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
