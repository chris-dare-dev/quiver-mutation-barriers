#!/usr/bin/env python
"""
traps.py -- local minima of total weight and their escape heights (note 5).

Work with one mutation class, quivers up to relabelling, enumerated inside an ambient bound B
on the maximal entry.  The total weight of a quiver is its number of arrows (sum of |b_ij|,
i < j).  A *local minimum* (LM) is a quiver none of whose mutations has smaller total weight;
greedy descent on total weight stops exactly at LMs.  The *escape height* e(x) of a quiver is
the least L such that x is joined to the root of the class (its lowest quiver: least maximal
entry, then least total weight) by a path of quivers of maximal entry <= L, i.e. the bottleneck
distance from the root.  A *trap* is an LM with e(x) > max(x): the pockets of note 4 that
greedy descent cannot leave.

For each LM the census records its maximal entry, total weight, escape height, the least
maximal entry among its mutations (a lower bound for e(x) when x is a strict local minimum of
the maximal entry), and the bottleneck path to the root: its length and where its highest
quiver (the *saddle*) sits on it.

Visibility: only LMs of total weight <= B and maximal entry <= B/4 are reported.  A mutation
outside the enumeration has maximal entry > B, hence total weight > B, so these LMs are exact.
Escape heights are exact (the enumeration is connected inside B, so every e(x) is <= B), and the
cap max <= B/4 keeps every escape ratio up to 4 visible: a quiver whose escape lies above B is
not in the enumeration at all.

Subcommands:
  census     one JSONL row per component
  summarize  tables from the JSONL files

Run from experiments/ with python -I.
"""
import argparse
import heapq
import json
import os
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT, all_mutations, max_entry_per_k  # noqa: E402
from bounded_paths import make_quiver, enumerate_component, canonical  # noqa: E402
from pockets import fork_return  # noqa: E402


def neighbours(k, n):
    """Canonical keys, maximal entries and total weights of the n mutations of state k."""
    N = all_mutations(np.frombuffer(k, dtype=DT).reshape(n, n))
    me = max_entry_per_k(N)
    tw = np.abs(N).reshape(n, -1).sum(axis=1) // 2
    return N, me, tw


def bottleneck_tree(states, n, root):
    """Minimax (bottleneck) Dijkstra from root over the enumerated states: e[x] and parent links."""
    e = {root: states[root]}
    parent = {root: None}
    heap = [(states[root], root)]
    done = set()
    while heap:
        h, k = heapq.heappop(heap)
        if k in done:
            continue
        done.add(k)
        N, me, _ = neighbours(k, n)
        for j in range(n):
            nb = canonical(N[j]).tobytes()
            if nb not in states or nb in done:
                continue
            v = max(h, states[nb])
            if v < e.get(nb, 1 << 62):
                e[nb] = v
                parent[nb] = k
                heapq.heappush(heap, (v, nb))
    return e, parent


def descend(k, states, tw, n):
    """Greedy descent on total weight from state k inside the enumeration: (path max, end)."""
    pm = states[k]
    while True:
        N, _, ntw = neighbours(k, n)
        j = int(np.argmin(ntw))
        if ntw[j] >= tw[k]:
            return pm, k
        k = canonical(N[j]).tobytes()
        if k not in states:
            return None, None
        pm = max(pm, states[k])


def lookahead(x, states, tw, e, n, kmax):
    """E_k(x) for k = 0..kmax: the least height of a walk of at most k mutations from x followed by
    greedy descent that ends at a harmless local minimum (escape height equal to its own maximal
    entry).  E_k(x) >= e(x) always; the least k with E_k(x) = e(x) measures how local the barrier is."""
    best = [None] * (kmax + 1)
    memo = {}
    frontier = {x: states[x]}                      # state -> least walk height reaching it
    for k in range(kmax + 1):
        for z, h in frontier.items():
            if z not in memo:
                memo[z] = descend(z, states, tw, n)
            pm, end = memo[z]
            if pm is None or e[end] != states[end]:
                continue
            v = max(h, pm)
            if best[k] is None or v < best[k]:
                best[k] = v
        if k > 0 and best[k - 1] is not None and (best[k] is None or best[k - 1] < best[k]):
            best[k] = best[k - 1]
        if k == kmax:
            break
        nxt = {}
        for z, h in frontier.items():
            N, _, _ = neighbours(z, n)
            for j in range(n):
                y = canonical(N[j]).tobytes()
                if y in states:
                    v = max(h, states[y])
                    if v < nxt.get(y, 1 << 62):
                        nxt[y] = v
        frontier = nxt
    return best


def _census_task(task):
    n, bound, trial, seed, budget, sparse = task
    t0 = time.time()
    Q = make_quiver(n, np.random.default_rng(seed), sparse)
    states, exhausted = enumerate_component(Q, bound, budget, unlabelled=True)
    tw = {k: int(np.abs(np.frombuffer(k, dtype=DT)).sum() // 2) for k in states}
    root = min(states, key=lambda k: (states[k], tw[k], k))
    e, parent = bottleneck_tree(states, n, root)
    lms = []
    for k, t in tw.items():
        if t > bound or states[k] > bound // 4:
            continue
        N, me, ntw = neighbours(k, n)
        if ntw.min() < t:
            continue
        B = np.frombuffer(k, dtype=DT).reshape(n, n)
        path = [k]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        heights = [states[p] for p in path]
        s = int(np.argmax(heights))
        row = {"max": states[k], "total": t, "e": e[k], "trap": e[k] > states[k], "strict_total": bool(ntw.min() > t),
               "first_step_min": int(me.min()), "path_len": len(path) - 1, "saddle_at": s,
               "path_monotone_after_saddle": all(heights[i] >= heights[i + 1] for i in range(s, len(heights) - 1)),
               "path_monotone_to_saddle": all(heights[i] <= heights[i + 1] for i in range(s)),
               "n_max_entries": int((np.abs(B) == states[k]).sum() // 2), "zeros": int((B == 0).sum() - n) // 2,
               "fork_return": fork_return(B)}
        if row["trap"]:
            S = np.frombuffer(path[s], dtype=DT).reshape(n, n)
            E = lookahead(k, states, tw, e, n, 3)
            row.update({"quiver": B.tolist(), "saddle": S.tolist(), "saddle_total": tw[path[s]], "lookahead": E,
                        "k_local": next((i for i, v in enumerate(E) if v == e[k]), None)})
        lms.append(row)
    return {"n": n, "trial": trial, "seed": seed, "sparse": bool(sparse), "B_big": bound, "comp_size": len(states),
            "exhausted": exhausted, "root_max": states[root], "root_total": tw[root],
            "states_by_total": np.bincount([t for k, t in tw.items() if t <= bound and states[k] <= bound // 4]).tolist(),
            "lms": lms, "time": round(time.time() - t0, 1)}


def cmd_census(args):
    tasks = []
    s = args.seed
    for trial in range(args.trials):
        s += 1
        if args.only is None or trial in args.only:
            tasks.append((args.n, args.B_big, trial, s, args.budget, args.sparse))
    print(f"{len(tasks)} components, n={args.n}, bound {args.B_big}, {args.workers} workers", flush=True)
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_census_task, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            tr = [(x["max"], x["e"]) for x in r["lms"] if x["trap"]]
            print(f"  n={r['n']} trial={r['trial']}: comp {r['comp_size']} exhausted={r['exhausted']} "
                  f"LMs {len(r['lms'])}, traps {len(tr)} {tr[:6]}{' ...' if len(tr) > 6 else ''} ({r['time']}s)", flush=True)


def _pairs_task(task):
    """Random pairs in one class: the bound plain search needs (the level at which the two quivers
    first connect) against the bound needed after greedy descent from both ends."""
    n, bound, trial, seed, budget, npairs = task
    rng = np.random.default_rng(seed + 7919)
    Q = make_quiver(n, np.random.default_rng(seed), False)
    states, exhausted = enumerate_component(Q, bound, budget, unlabelled=True)
    tw = {k: int(np.abs(np.frombuffer(k, dtype=DT)).sum() // 2) for k in states}
    pool = sorted(k for k, v in states.items() if v <= bound // 4)
    pick = [pool[i] for i in rng.integers(0, len(pool), size=(npairs, 2)).ravel()]
    ends = {k: descend(k, states, tw, n) for k in set(pick)}
    pairs = [(pick[2 * i], pick[2 * i + 1]) for i in range(npairs)]
    queries = {(a, b) for a, b in pairs} | {(ends[a][1], ends[b][1]) for a, b in pairs}
    by_level = defaultdict(list)
    for k, v in states.items():
        by_level[v].append(k)
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    conn = {}
    pending = set(queries)
    for lvl in sorted(by_level):
        for k in by_level[lvl]:
            parent[k] = k
        for k in by_level[lvl]:
            N, me, _ = neighbours(k, n)
            for j in np.flatnonzero(me <= lvl):
                nb = canonical(N[j]).tobytes()
                if nb in parent:
                    ra, rb = find(k), find(nb)
                    if ra != rb:
                        parent[ra] = rb
        done = {q for q in pending if q[0] in parent and q[1] in parent and find(q[0]) == find(q[1])}
        for q in done:
            conn[q] = lvl
        pending -= done
        if not pending:
            break
    out = []
    for a, b in pairs:
        (pa, ea), (pb, eb) = ends[a], ends[b]
        out.append({"mx": states[a], "my": states[b], "conn": conn[(a, b)], "dx": pa, "dy": pb,
                    "mx_end": states[ea], "my_end": states[eb], "conn_end": conn[(ea, eb)],
                    "same_end": ea == eb})
    return {"n": n, "trial": trial, "seed": seed, "B_big": bound, "exhausted": exhausted, "comp_size": len(states), "pairs": out}


def cmd_pairs(args):
    tasks = []
    s = args.seed
    for trial in range(args.trials):
        s += 1
        if args.only is None or trial in args.only:
            tasks.append((args.n, args.B_big, trial, s, args.budget, args.npairs))
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_pairs_task, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
    rows = [json.loads(l) for l in open(args.out)]
    P = [p for r in rows if r["exhausted"] for p in r["pairs"]]
    plain = np.array([p["conn"] / max(p["mx"], p["my"]) for p in P])
    two = np.array([p["conn_end"] / max(p["mx_end"], p["my_end"]) for p in P])
    two_rel = np.array([p["conn_end"] / max(p["mx"], p["my"]) for p in P])
    print(f"n={args.n}, bound {args.B_big}: {len(P)} pairs in {sum(r['exhausted'] for r in rows)} classes")
    print(f"  plain search: bound needed <= max weight in {np.mean(plain <= 1):.3f} of pairs; ratio 90% {np.percentile(plain, 90):.2f}, max {plain.max():.2f}")
    print(f"  after greedy descent: same end point {np.mean([p['same_end'] for p in P]):.3f}; bound needed <= max end weight in {np.mean(two <= 1):.3f}; "
          f"ratio 90% {np.percentile(two, 90):.2f}, max {two.max():.2f}; relative to the original weights: <= 1 in {np.mean(two_rel <= 1):.3f}, max {two_rel.max():.2f}")


def cmd_summarize(args):
    rows = [json.loads(l) for f in args.files for l in open(f) if l.strip()]
    rows = [r for r in rows if r["exhausted"]]
    by = defaultdict(list)
    for r in rows:
        by[(r["n"], r["sparse"], r["B_big"])].append(r)
    for (n, sparse, _), rs in sorted(by.items()):
        L = [x for r in rs for x in r["lms"]]
        T = [x for x in L if x["trap"]]
        print(f"\nn={n}{' sparse' if sparse else ''}, bound {sorted({r['B_big'] for r in rs})}: {len(rs)} exhausted components; local minima of total weight "
              f"(total <= B, max <= B/4): {len(L)}, of which traps {len(T)} in {sum(any(x['trap'] for x in r['lms']) for r in rs)} components")
        if not T:
            continue
        ratio = np.array([x["e"] / x["max"] for x in T])
        print(f"  trap escape ratio e/max: median {np.median(ratio):.2f}, 90% {np.percentile(ratio, 90):.2f}, max {ratio.max():.2f}")
        fs = [x for x in T]
        print(f"  e == least maximal entry of a single mutation: {sum(x['e'] == x['first_step_min'] for x in fs)}/{len(fs)}; "
              f"e > it: {sum(x['e'] > x['first_step_min'] for x in fs)}")
        print(f"  bottleneck path: length median {int(np.median([x['path_len'] for x in T]))}, saddle position median "
              f"{int(np.median([x['saddle_at'] for x in T]))}, saddle at step 1: {sum(x['saddle_at'] == 1 for x in T)}, "
              f"rises monotonically to the saddle {sum(x['path_monotone_to_saddle'] for x in T)}, "
              f"falls monotonically after it {sum(x['path_monotone_after_saddle'] for x in T)}")
        print(f"  shape: strict local min of total {sum(x['strict_total'] for x in T)}/{len(T)}, max attained once "
              f"{sum(x['n_max_entries'] == 1 for x in T)}, with a zero entry {sum(x['zeros'] > 0 for x in T)}, forks "
              f"{sum(x['fork_return'] is not None for x in T)}")
        kl = [x.get("k_local") for x in T]
        print(f"  lookahead (k mutations, then greedy descent to a harmless minimum) reaches e exactly with k = "
              + ", ".join(f"{k}: {kl.count(k)}" for k in range(4)) + f"; not within 3: {kl.count(None)}")
        harmless = [x for x in L if not x["trap"]]
        print(f"  harmless local minima (e == max): {len(harmless)}; class roots counted among them: {len(rs)}")
        # density: LMs and traps per state, by total weight
        for lo, hi in [(1, 32), (33, 128), (129, 512), (513, 10 ** 9)]:
            nl = sum(1 for x in L if lo <= x["total"] <= hi)
            nt = sum(1 for x in T if lo <= x["total"] <= hi)
            ns = sum(sum(r["states_by_total"][lo:hi + 1]) for r in rs)
            if ns:
                print(f"    total {lo:>3}-{hi if hi < 10 ** 9 else 'inf':>4}: states {ns:>8}, local minima {nl:>5} ({nl / ns:.4f} per state), traps {nt:>4}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    cs = sub.add_parser("census")
    cs.add_argument("--n", type=int, required=True)
    cs.add_argument("--B-big", type=int, required=True)
    cs.add_argument("--budget", type=int, default=3000000)
    cs.add_argument("--trials", type=int, default=12)
    cs.add_argument("--only", type=int, nargs="+")
    cs.add_argument("--workers", type=int, default=4)
    cs.add_argument("--seed", type=int, required=True)
    cs.add_argument("--sparse", action="store_true")
    cs.add_argument("--out", required=True)
    cs.add_argument("--append", action="store_true")
    cs.set_defaults(func=cmd_census)
    pr = sub.add_parser("pairs")
    pr.add_argument("--n", type=int, required=True)
    pr.add_argument("--B-big", type=int, required=True)
    pr.add_argument("--budget", type=int, default=3000000)
    pr.add_argument("--trials", type=int, default=12)
    pr.add_argument("--only", type=int, nargs="+")
    pr.add_argument("--npairs", type=int, default=200)
    pr.add_argument("--workers", type=int, default=4)
    pr.add_argument("--seed", type=int, required=True)
    pr.add_argument("--out", required=True)
    pr.set_defaults(func=cmd_pairs)
    sm = sub.add_parser("summarize")
    sm.add_argument("files", nargs="+")
    sm.set_defaults(func=cmd_summarize)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
