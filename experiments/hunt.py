#!/usr/bin/env python
"""
hunt.py -- searching for traps with large escape ratios (note 6).

The census of note 5 measures escape heights by enumerating whole classes, which limits it to
small weights.  This script works locally.  For a local minimum x of total weight (no mutation
lowers the number of arrows), its *descent barrier* D(x) is the least L such that some path of
quivers with maximal entry <= L leads from x to a quiver of strictly smaller total weight.  It is
found by a bottleneck (minimax) Dijkstra search from x that stops at the first lighter quiver, so
it needs no enumeration of the class.  Whenever the class contains a quiver lighter than x (every
x but the lightest), every path from x to the bottom of the class passes such a quiver, so

    e(x) >= D(x)      and      e(x) / max(x) >= D(x) / max(x).

Large D/max therefore certifies large escape ratios.  Quivers are up to relabelling.

Subcommands:
  calibrate  D(x) for the traps of note 5's census files, against their escape heights e(x)
  hunt       random local minima at higher weights: random walk up to W_high, greedy descent
             on total weight, then D(x)
  climb      evolutionary search: from the worst traps found so far, short random walks and
             descent to nearby local minima, keeping those with the largest D/max
  summarize  tables from hunt / climb output

Run from experiments/ with python -I.
"""
import argparse
import gzip
import heapq
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT, all_mutations, max_entry_per_k, random_quiver  # noqa: E402
from bounded_paths import canonical, walk_until_high  # noqa: E402


# Entries stay below 2^31 everywhere, so that a mutation (|b| + |b|·|b| < 2^63) cannot overflow int64.
LIMIT = 2 ** 31 - 1


def open_text(path):
    """Open a JSONL result file, gzip-compressed (.gz) or not."""
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def total(B):
    return int(np.abs(B).sum() // 2)


def descend(B):
    """Greedy descent on total weight (labelled); returns the canonical local minimum and the
    largest maximal entry met on the way."""
    n = B.shape[0]
    pm = int(np.abs(B).max())
    while True:
        N = all_mutations(B)
        tw = np.abs(N).reshape(n, -1).sum(axis=1) // 2
        k = int(np.argmin(tw))
        if tw[k] >= total(B):
            return canonical(B), pm
        B = N[k]
        pm = max(pm, int(np.abs(B).max()))


def is_local_min(B):
    n = B.shape[0]
    return bool((np.abs(all_mutations(B)).reshape(n, -1).sum(axis=1) // 2).min() >= total(B))


def barrier(x, cap, budget):
    """Bottleneck search from x for the first quiver of smaller total weight, through quivers of
    maximal entry <= cap.  Returns (D, popped, path length, total of the lighter quiver); D is None
    when nothing lighter is reachable inside the cap and budget."""
    n = x.shape[0]
    T0 = total(x)
    start = x.tobytes()
    best = {start: int(np.abs(x).max())}
    depth = {start: 0}
    heap = [(best[start], start)]
    done = set()
    while heap and len(done) < budget:
        h, k = heapq.heappop(heap)
        if k in done:
            continue
        done.add(k)
        B = np.frombuffer(k, dtype=DT).reshape(n, n)
        if total(B) < T0:
            return h, len(done), depth[k], total(B)
        N = all_mutations(B)
        me = max_entry_per_k(N)
        for j in np.flatnonzero(me <= cap):
            nb = canonical(N[j]).tobytes()
            v = max(h, int(me[j]))
            if nb not in done and v < best.get(nb, 1 << 62):
                best[nb] = v
                depth[nb] = depth[k] + 1
                heapq.heappush(heap, (v, nb))
    return None, len(done), None, None


def measure(x, cap_ratio, budget):
    m = int(np.abs(x).max())
    cap = min(cap_ratio * m, LIMIT)
    D, popped, plen, lt = barrier(x, cap, budget)
    return {"quiver": x.tolist(), "max": m, "total": total(x), "D": D, "ratio": (D / m) if D else None, "cap": cap,
            "popped": popped, "path_len": plen, "lighter_total": lt, "capped": D is None}


# ----------------------------------------------------------------------------- calibrate
def _cal_task(task):
    x, e, cap_ratio, budget = task
    r = measure(np.array(x, dtype=DT), cap_ratio, budget)
    r["e"] = e
    return r


def cmd_calibrate(args):
    tasks = []
    for f in args.files:
        for row in map(json.loads, open_text(f)):
            for t in row["lms"]:
                if t["trap"]:
                    tasks.append((t["quiver"], t["e"], args.cap_ratio, args.budget))
    with Pool(args.workers) as pool:
        res = pool.map(_cal_task, tasks, chunksize=1)
    eq = sum(r["D"] == r["e"] for r in res)
    lo = sum(r["D"] is not None and r["D"] < r["e"] for r in res)
    hi = sum(r["D"] is not None and r["D"] > r["e"] for r in res)
    print(f"{len(res)} traps: D == e {eq}, D < e {lo}, D > e {hi} (should be 0), not found {sum(r['capped'] for r in res)}")
    with open(args.out, "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")


# ----------------------------------------------------------------------------- hunt
def _hunt_task(task):
    n, W_high, trial, seed, wmax, cap_ratio, budget = task
    rng = np.random.default_rng(seed)
    Q = random_quiver(n, rng, wmax=wmax, need_big=3)
    t0 = time.time()
    if W_high > 0:
        high, steps, _ = walk_until_high(Q, W_high, LIMIT, rng)
        if high is None:
            return {"n": n, "W_high": W_high, "trial": trial, "seed": seed, "reached": False}
    else:
        high = Q
    if total(high) > LIMIT:
        return {"n": n, "W_high": W_high, "trial": trial, "seed": seed, "reached": False}
    x, pm = descend(high)
    r = measure(x, cap_ratio, budget)
    r.update({"n": n, "W_high": W_high, "trial": trial, "seed": seed, "wmax": wmax, "reached": True,
              "descent_path_max": pm, "time": round(time.time() - t0, 2)})
    return r


def cmd_hunt(args):
    tasks = []
    s = args.seed
    for W in args.W_high:
        for trial in range(args.trials):
            s += 1
            tasks.append((args.n, W, trial, s, args.wmax, args.cap_ratio, args.budget))
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_hunt_task, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
    summarize([args.out])


# ----------------------------------------------------------------------------- bounded walks
def _bwalk_task(task):
    """Random walk inside the bound W (no immediate reversal, moves above W rejected), collecting
    the local minima of total weight it visits with maximal entry >= W/frac, then D for each."""
    n, W, trial, seed, steps, frac, cap_ratio, budget = task
    rng = np.random.default_rng(seed)
    B = random_quiver(n, rng, wmax=3, need_big=3)
    prev = -1
    cands = {}
    t0 = time.time()
    for _ in range(steps):
        N = all_mutations(B)
        me = max_entry_per_k(N)
        tw = np.abs(N).reshape(n, -1).sum(axis=1) // 2
        m = int(np.abs(B).max())
        if m * frac >= W and tw.min() >= total(B):
            c = canonical(B)
            cands.setdefault(c.tobytes(), c)
        ok = [k for k in range(n) if k != prev and me[k] <= W]
        if not ok:
            ok = [prev]
        k = int(rng.choice(ok))
        B, prev = N[k], k
    out = []
    for c in cands.values():
        r = measure(c, cap_ratio, budget)
        r.update({"n": n, "W": W, "trial": trial, "seed": seed})
        out.append(r)
    return {"n": n, "W": W, "trial": trial, "seed": seed, "steps": steps, "candidates": len(cands),
            "time": round(time.time() - t0, 1), "minima": out}


def cmd_bwalk(args):
    tasks = []
    s = args.seed
    for W in args.W:
        for trial in range(args.trials):
            s += 1
            tasks.append((args.n, W, trial, s, args.steps, args.frac, args.cap_ratio, args.budget))
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_bwalk_task, tasks, chunksize=1):
            for x in r.pop("minima"):
                f.write(json.dumps(x) + "\n")
            f.flush()
            print(f"  n={r['n']} W={r['W']} trial={r['trial']}: {r['candidates']} local minima ({r['time']}s)", flush=True)
    summarize([args.out])


# ----------------------------------------------------------------------------- climb
def _children_task(task):
    x, seed, kids, cap_ratio, budget = task
    rng = np.random.default_rng(seed)
    x = np.array(x, dtype=DT)
    n = x.shape[0]
    out = []
    for _ in range(kids):
        B, prev = x.copy(), -1
        for _ in range(int(rng.integers(1, 7))):
            k = int(rng.choice([v for v in range(n) if v != prev]))
            B, prev = all_mutations(B)[k], k
            if total(B) > LIMIT:
                break
        if total(B) > LIMIT:          # descent then stays below LIMIT: max <= total only falls
            continue
        y, _ = descend(B)
        out.append(y.tolist())
    return out


def _measure_task(task):
    y, cap_ratio, budget = task
    return measure(np.array(y, dtype=DT), cap_ratio, budget)


def cmd_climb(args):
    pop = []
    for f in args.seeds:
        for r in map(json.loads, open_text(f)):
            if r.get("ratio"):
                pop.append(r)
    pop = sorted(pop, key=lambda r: -r["ratio"])[: args.keep]
    seen = {np.array(r["quiver"], dtype=DT).tobytes() for r in pop}
    rng = np.random.default_rng(args.seed)
    log = open(args.out, "w")
    with Pool(args.workers) as pool:
        for rnd in range(args.rounds):
            tasks = [(r["quiver"], int(rng.integers(1 << 31)), args.kids, args.cap_ratio, args.budget) for r in pop]
            kids = [y for ys in pool.map(_children_task, tasks, chunksize=1) for y in ys]
            fresh = []
            for y in kids:
                kb = np.array(y, dtype=DT).tobytes()
                if kb not in seen:
                    seen.add(kb)
                    fresh.append(y)
            res = pool.map(_measure_task, [(y, args.cap_ratio, args.budget) for y in fresh], chunksize=1)
            for r in res:
                r["round"] = rnd
                log.write(json.dumps(r) + "\n")
            log.flush()
            pop = sorted(pop + [r for r in res if r["ratio"]], key=lambda r: -r["ratio"])[: args.keep]
            print(f"round {rnd}: {len(fresh)} new local minima, {sum(1 for r in res if r['ratio'] and r['ratio'] > 1)} with D > max, "
                  f"{sum(r['capped'] for r in res)} capped; best ratios {[round(r['ratio'], 2) for r in pop[:6]]} "
                  f"(max {pop[0]['max']}, D {pop[0]['D']})", flush=True)
    log.close()


# ----------------------------------------------------------------------------- summary
def summarize(files):
    rows = [json.loads(l) for f in files for l in open_text(f) if l.strip()]
    rows = [r for r in rows if r.get("reached", True) and "max" in r]
    traps = [r for r in rows if r["ratio"] and r["ratio"] > 1]
    print(f"{len(rows)} local minima; with D > max (certified traps) {len(traps)}; capped (nothing lighter inside the cap) {sum(r['capped'] for r in rows)}")
    for lo, hi in [(1, 16), (17, 64), (65, 256), (257, 1024), (1025, 4096), (4097, 10 ** 12)]:
        sel = [r for r in rows if lo <= r["max"] <= hi]
        tr = [r["ratio"] for r in sel if r["ratio"] and r["ratio"] > 1]
        if sel:
            print(f"  max {lo:>5}-{hi if hi < 10 ** 12 else 'inf':>5}: {len(sel):>5} minima, certified traps {len(tr):>4}"
                  + (f", D/max median {np.median(tr):.2f}, 90% {np.percentile(tr, 90):.2f}, max {max(tr):.2f}" if tr else "")
                  + f", capped {sum(r['capped'] for r in sel)}")


def cmd_summarize(args):
    summarize(args.files)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ca = sub.add_parser("calibrate")
    ca.add_argument("files", nargs="+")
    ca.add_argument("--cap-ratio", type=int, default=12)
    ca.add_argument("--budget", type=int, default=2000000)
    ca.add_argument("--workers", type=int, default=8)
    ca.add_argument("--out", required=True)
    ca.set_defaults(func=cmd_calibrate)
    hu = sub.add_parser("hunt")
    hu.add_argument("--n", type=int, required=True)
    hu.add_argument("--W-high", type=int, nargs="+", required=True)
    hu.add_argument("--trials", type=int, default=100)
    hu.add_argument("--wmax", type=int, default=3)
    hu.add_argument("--cap-ratio", type=int, default=12)
    hu.add_argument("--budget", type=int, default=2000000)
    hu.add_argument("--workers", type=int, default=8)
    hu.add_argument("--seed", type=int, required=True)
    hu.add_argument("--out", required=True)
    hu.add_argument("--append", action="store_true")
    hu.set_defaults(func=cmd_hunt)
    bw = sub.add_parser("bwalk")
    bw.add_argument("--n", type=int, required=True)
    bw.add_argument("--W", type=int, nargs="+", required=True)
    bw.add_argument("--trials", type=int, default=16)
    bw.add_argument("--steps", type=int, default=200000)
    bw.add_argument("--frac", type=int, default=8)
    bw.add_argument("--cap-ratio", type=int, default=12)
    bw.add_argument("--budget", type=int, default=300000)
    bw.add_argument("--workers", type=int, default=8)
    bw.add_argument("--seed", type=int, required=True)
    bw.add_argument("--out", required=True)
    bw.add_argument("--append", action="store_true")
    bw.set_defaults(func=cmd_bwalk)
    cl = sub.add_parser("climb")
    cl.add_argument("seeds", nargs="+")
    cl.add_argument("--keep", type=int, default=24)
    cl.add_argument("--kids", type=int, default=20)
    cl.add_argument("--rounds", type=int, default=10)
    cl.add_argument("--cap-ratio", type=int, default=12)
    cl.add_argument("--budget", type=int, default=2000000)
    cl.add_argument("--workers", type=int, default=8)
    cl.add_argument("--seed", type=int, default=1)
    cl.add_argument("--out", required=True)
    cl.set_defaults(func=cmd_climb)
    sm = sub.add_parser("summarize")
    sm.add_argument("files", nargs="+")
    sm.set_defaults(func=cmd_summarize)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
