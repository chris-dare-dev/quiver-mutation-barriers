#!/usr/bin/env python
"""
mutation_path.py -- planted mutation-path one-way function test (note 1).

Problem.  Q is a quiver on n vertices, encoded as a skew-symmetric integer
matrix (b_ij = #arrows i->j minus #arrows j->i).  The secret is a sequence
(i_1, ..., i_L) with no immediate repeats.  Q' = mu_{i_L} ... mu_{i_1}(Q), and
every intermediate quiver has all |entries| <= B.  Public: (Q, Q', n, B).
Inversion: find ANY mutation sequence Q -> Q' staying inside the bound.

Attacks implemented (the attacker sees only Q, Q', n, B):
  A0  bounded-component enumeration from Q (BFS with a node budget).  If the
      component inside the bound is exhausted, the function is trivially
      invertible for that (n, B).
  A1  bidirectional BFS inside the bound, node budget.
  A2  greedy weight descent from both ends, then bidirectional BFS between the
      two local minima.
Walk statistics recorded for the planted walk: fraction of candidate vertices
blocked by the bound, fraction of sink/source (orientation-only) steps, whether
Q' has the same underlying weighted graph as Q, max entry seen, early stop.

Subcommands:
  grid     run the planted experiment over (n, B, L, strategy) x trials
  growth   measure how fast entries grow along UNBOUNDED random walks
  summarize  print tables from a JSONL results file

Everything is toy-sized.  Run from inside experiments/ with `python -I`.
"""
import argparse
import json
import sys
import time
from collections import deque
from multiprocessing import Pool

import numpy as np

DT = np.int64


# ----------------------------------------------------------------------------
# mutation kernel
# ----------------------------------------------------------------------------
def all_mutations(B):
    """N[k] = mu_k(B) for every vertex k, shape (n, n, n)."""
    A = np.abs(B)
    add = (A.T[:, :, None] * B[:, None, :] + B.T[:, :, None] * A[:, None, :]) // 2
    N = B[None, :, :] + add
    idx = np.arange(B.shape[0])
    N[idx, idx, :] = -B
    N[idx, :, idx] = -B.T
    return N


def mutate(B, k):
    col = B[:, k]
    row = B[k, :]
    add = (np.abs(col)[:, None] * row[None, :] + col[:, None] * np.abs(row)[None, :]) // 2
    N = B + add
    N[k, :] = -row
    N[:, k] = -col
    return N


def apply_seq(B, seq):
    for k in seq:
        B = mutate(B, k)
    return B


def is_sink_or_source(B, k):
    row = B[k]
    nz = row[row != 0]
    return nz.size == 0 or bool((nz > 0).all()) or bool((nz < 0).all())


def weight(B):
    return int(np.abs(B).sum() // 2)


def max_entry_per_k(N):
    return np.abs(N).reshape(N.shape[0], -1).max(axis=1)


def connected(B):
    n = B.shape[0]
    seen = {0}
    dq = deque([0])
    while dq:
        i = dq.popleft()
        for j in np.flatnonzero(B[i]):
            if j not in seen:
                seen.add(int(j))
                dq.append(int(j))
    return len(seen) == n


def random_quiver(n, rng, wmax=3, need_big=3):
    """Random connected skew-symmetric matrix with entries in [-wmax, wmax] and
    at least one |entry| >= need_big.  For n >= 3 an entry >= 3 guarantees an
    infinite mutation class (mutation-finite quivers have all weights <= 2)."""
    while True:
        U = rng.integers(-wmax, wmax + 1, size=(n, n), dtype=DT)
        B = np.triu(U, 1)
        B = B - B.T
        if np.abs(B).max() >= need_big and connected(B):
            return B


# ----------------------------------------------------------------------------
# planted walk
# ----------------------------------------------------------------------------
def plant_walk(Q, L, bound, rng, strategy):
    n = Q.shape[0]
    cur = Q.copy()
    prev = -1
    seq = []
    blocked = 0
    offered = 0
    ss_steps = 0
    maxent = int(np.abs(Q).max())
    stuck = False
    backtracks = 0
    for _ in range(L):
        N = all_mutations(cur)
        ok = max_entry_per_k(N) <= bound
        cands = [k for k in range(n) if k != prev]
        offered += len(cands)
        allowed = [k for k in cands if ok[k]]
        blocked += len(cands) - len(allowed)
        if strategy == "cyclic":
            cyc = [k for k in allowed if not is_sink_or_source(cur, k)]
            if cyc:
                allowed = cyc
        if not allowed:
            if strategy == "backtrack" and prev >= 0:
                # step back along the edge we came from (always inside the bound)
                allowed = [prev]
                backtracks += 1
            else:
                stuck = True
                break
        k = int(rng.choice(allowed))
        if is_sink_or_source(cur, k):
            ss_steps += 1
        cur = N[k]
        seq.append(k)
        prev = k
        maxent = max(maxent, int(np.abs(cur).max()))
    stats = {
        "steps": len(seq),
        "stuck": stuck,
        "backtracks": backtracks,
        "blocked_frac": blocked / offered if offered else 0.0,
        "sinksource_frac": ss_steps / len(seq) if seq else 0.0,
        "max_entry": maxent,
        "same_underlying": bool((np.abs(cur) == np.abs(Q)).all()),
        "weight_start": weight(Q),
        "weight_end": weight(cur),
    }
    return cur, seq, stats


def plant_deepest(Q, bound, budget, rng):
    """Adversarial planting: BFS inside the bound (node budget) and return a
    random quiver at the maximal depth reached.  The planted distance is that
    depth (exact if the component was exhausted, else a lower bound on the
    attacker-visible radius)."""
    n = Q.shape[0]
    seen = {Q.tobytes()}
    dq = deque([(Q.tobytes(), 0)])
    maxd = 0
    deepest = [Q.tobytes()]
    while dq and len(seen) < budget:
        ck, d = dq.popleft()
        cur = np.frombuffer(ck, dtype=DT).reshape(n, n)
        N = all_mutations(cur)
        ok = max_entry_per_k(N) <= bound
        for k in np.flatnonzero(ok):
            kb = N[k].tobytes()
            if kb not in seen:
                seen.add(kb)
                dq.append((kb, d + 1))
                if d + 1 > maxd:
                    maxd = d + 1
                    deepest = [kb]
                elif d + 1 == maxd:
                    deepest.append(kb)
    kb = deepest[int(rng.integers(len(deepest)))]
    Qp = np.frombuffer(kb, dtype=DT).reshape(n, n).copy()
    return Qp, maxd, len(seen), not dq


# ----------------------------------------------------------------------------
# attacks
# ----------------------------------------------------------------------------
def bfs_component(Q, bound, budget, return_profile=False):
    """Size of the mutation component of Q inside the bound, capped at budget.
    Also returns the depth profile (number of states at each BFS depth)."""
    n = Q.shape[0]
    seen = {Q.tobytes()}
    dq = deque([(Q.tobytes(), 0)])
    maxd = 0
    profile = [1]
    while dq and len(seen) < budget:
        ck, d = dq.popleft()
        cur = np.frombuffer(ck, dtype=DT).reshape(n, n)
        N = all_mutations(cur)
        ok = max_entry_per_k(N) <= bound
        for k in np.flatnonzero(ok):
            kb = N[k].tobytes()
            if kb not in seen:
                seen.add(kb)
                dq.append((kb, d + 1))
                if d + 1 > maxd:
                    maxd = d + 1
                    profile.append(0)
                profile[d + 1] += 1
    exhausted = not dq
    if return_profile:
        return len(seen), exhausted, maxd, profile
    return len(seen), exhausted, maxd


def _trace(parents, key):
    path = []
    while parents[key] is not None:
        pk, k = parents[key]
        path.append(k)
        key = pk
    path.reverse()
    return path


def bidir_bfs(Q, Qp, bound, budget):
    """Returns (found, path, nodes). path is a list of vertices taking Q to Qp."""
    if Q.shape == Qp.shape and (Q == Qp).all():
        return True, [], 0
    n = Q.shape[0]
    fwd = {Q.tobytes(): None}
    bwd = {Qp.tobytes(): None}
    fq = [Q]
    bq = [Qp]
    nodes = 0
    while fq and bq and nodes < budget:
        forward = len(fq) <= len(bq)
        frontier = fq if forward else bq
        seen = fwd if forward else bwd
        other = bwd if forward else fwd
        nxt = []
        for cur in frontier:
            ck = cur.tobytes()
            N = all_mutations(cur)
            ok = max_entry_per_k(N) <= bound
            for k in np.flatnonzero(ok):
                kb = N[k].tobytes()
                if kb in seen:
                    continue
                seen[kb] = (ck, int(k))
                nodes += 1
                if kb in other:
                    pf = _trace(fwd, kb)
                    pb = _trace(bwd, kb)
                    # mutation is an involution: from the meeting point back to
                    # Qp, apply the backward path in reverse order.
                    path = pf + pb[::-1]
                    return True, path, nodes
                nxt.append(N[k])
        if forward:
            fq = nxt
        else:
            bq = nxt
    return False, None, nodes


def descend(Q, bound, rng, max_steps=10000):
    """Greedy steepest descent on arrow weight inside the bound."""
    n = Q.shape[0]
    cur = Q
    path = []
    w0 = weight(cur)
    for _ in range(max_steps):
        N = all_mutations(cur)
        ok = max_entry_per_k(N) <= bound
        w = np.abs(N).reshape(n, -1).sum(axis=1) // 2
        cand = [k for k in np.flatnonzero(ok) if w[k] < w0]
        if not cand:
            break
        best = min(int(w[k]) for k in cand)
        ks = [k for k in cand if w[k] == best]
        k = int(rng.choice(ks))
        cur = N[k]
        w0 = best
        path.append(k)
    return cur, path


def attack_descent(Q, Qp, bound, rng, budget):
    m1, p1 = descend(Q, bound, rng)
    m2, p2 = descend(Qp, bound, rng)
    if (m1 == m2).all():
        return True, p1 + p2[::-1], 0, weight(m1), weight(m2)
    found, mid, nodes = bidir_bfs(m1, m2, bound, budget)
    if found:
        return True, p1 + mid + p2[::-1], nodes, weight(m1), weight(m2)
    return False, None, nodes, weight(m1), weight(m2)


# ----------------------------------------------------------------------------
# one instance
# ----------------------------------------------------------------------------
def attack_deepening(Q, Qp, bound, budget_per_level):
    """Iterative deepening on the entry bound: search inside B' = 4, 16, 64, ...
    up to the public bound.  Returns (found, path, B'_found, total_nodes)."""
    total = 0
    bp = 4
    levels = []
    while True:
        bp = min(bp, bound)
        levels.append(bp)
        found, path, nodes = bidir_bfs(Q, Qp, bp, budget_per_level)
        total += nodes
        if found:
            return True, path, bp, total
        if bp >= bound:
            return False, None, None, total
        bp *= 4


def run_instance(task):
    n, bound, L, strategy, trial, seed, comp_budget, bfs_budget, plant_bound, a3_budget = task
    if plant_bound is None:
        plant_bound = bound
    rng = np.random.default_rng(seed)
    t0 = time.time()
    Q = random_quiver(n, rng)
    row = {"n": n, "B": bound, "L": L, "strategy": strategy, "trial": trial, "seed": seed}
    row["plant_bound"] = plant_bound
    if strategy == "deepest":
        t = time.time()
        Qp, depth, size, exhausted = plant_deepest(Q, plant_bound, comp_budget, rng)
        row.update({"steps": depth, "stuck": False, "backtracks": 0, "blocked_frac": None,
                    "sinksource_frac": None, "max_entry": int(np.abs(Qp).max()),
                    "same_underlying": bool((np.abs(Qp) == np.abs(Q)).all()),
                    "weight_start": weight(Q), "weight_end": weight(Qp), "planted_len": depth,
                    "comp_size": size, "comp_exhausted": exhausted, "comp_maxdepth": depth,
                    "comp_time": round(time.time() - t, 3)})
    else:
        Qp, seq, stats = plant_walk(Q, L, plant_bound, rng, strategy)
        row.update(stats)
        row["planted_len"] = len(seq)
        # A0 component size
        t = time.time()
        size, exhausted, maxd = bfs_component(Q, bound, comp_budget)
        row.update({"comp_size": size, "comp_exhausted": exhausted, "comp_maxdepth": maxd,
                    "comp_time": round(time.time() - t, 3)})

    # A1 bidirectional BFS
    t = time.time()
    found, path, nodes = bidir_bfs(Q, Qp, bound, bfs_budget)
    ok = bool(found and (apply_seq(Q, path) == Qp).all())
    row.update({"a1_found": ok, "a1_dist": len(path) if ok else None, "a1_nodes": nodes,
                "a1_time": round(time.time() - t, 3)})

    # A2 descent + BFS between minima
    t = time.time()
    found2, path2, nodes2, wm1, wm2 = attack_descent(Q, Qp, bound, rng, bfs_budget)
    ok2 = bool(found2 and (apply_seq(Q, path2) == Qp).all())
    row.update({"a2_found": ok2, "a2_len": len(path2) if ok2 else None, "a2_nodes": nodes2,
                "a2_minima_equal": bool(found2 and nodes2 == 0),
                "a2_minw_Q": wm1, "a2_minw_Qp": wm2, "a2_time": round(time.time() - t, 3)})

    # A3 iterative deepening on the bound
    t = time.time()
    found3, path3, bfound, nodes3 = attack_deepening(Q, Qp, bound, a3_budget)
    ok3 = bool(found3 and (apply_seq(Q, path3) == Qp).all())
    row.update({"a3_found": ok3, "a3_len": len(path3) if ok3 else None, "a3_bound": bfound,
                "a3_nodes": nodes3, "a3_time": round(time.time() - t, 3)})
    row["time"] = round(time.time() - t0, 3)
    return row


# ----------------------------------------------------------------------------
# growth without a bound
# ----------------------------------------------------------------------------
def growth(args):
    rng = np.random.default_rng(args.seed)
    thresholds = [2 ** e for e in args.log2_thresholds]
    out = {}
    for n in args.n:
        hits = {th: [] for th in thresholds}
        for _ in range(args.walks):
            Q = random_quiver(n, rng).astype(object)
            cur = Q
            prev = -1
            first = {th: None for th in thresholds}
            for t in range(1, args.steps + 1):
                k = int(rng.choice([j for j in range(n) if j != prev]))
                cur = mutate(cur, k)
                prev = k
                m = max(abs(int(x)) for x in cur.flat)
                for th in thresholds:
                    if first[th] is None and m > th:
                        first[th] = t
            for th in thresholds:
                hits[th].append(first[th] if first[th] is not None else args.steps + 1)
        out[n] = {str(th): {"median_steps_to_exceed": float(np.median(hits[th])),
                            "frac_never_within_T": float(np.mean([h > args.steps for h in hits[th]]))}
                  for th in thresholds}
        print(f"n={n}:")
        for th in thresholds:
            d = out[n][str(th)]
            print(f"  B=2^{th.bit_length() - 1:<3d} median steps to exceed: {d['median_steps_to_exceed']:>6.1f}"
                  f"   never exceeded within T={args.steps}: {d['frac_never_within_T']:.2f}")
    with open(args.out, "w") as f:
        json.dump({"args": {k: v for k, v in vars(args).items() if k != "func"}, "results": out}, f, indent=1)


# ----------------------------------------------------------------------------
# grid
# ----------------------------------------------------------------------------
def grid(args):
    assert max(args.B) <= 2 ** 30, "int64 safety: products of two entries must fit"
    tasks = []
    s = args.seed
    for n in args.n:
        for bound in args.B:
            for L in args.L:
                for strategy in args.strategies:
                    for pb in (args.plant_bound or [None]):
                        for trial in range(args.trials):
                            s += 1
                            tasks.append((n, bound, L, strategy, trial, s, args.comp_budget, args.bfs_budget,
                                          pb, args.a3_budget))
    print(f"{len(tasks)} instances, {args.workers} workers", flush=True)
    t0 = time.time()
    done = 0
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for row in pool.imap_unordered(run_instance, tasks, chunksize=1):
            f.write(json.dumps(row) + "\n")
            f.flush()
            done += 1
            if done % 20 == 0 or done == len(tasks):
                print(f"  {done}/{len(tasks)}  elapsed {time.time() - t0:.0f}s", flush=True)


def _component_task(task):
    n, bound, trial, seed, budget = task
    rng = np.random.default_rng(seed)
    Q = random_quiver(n, rng)
    t = time.time()
    size, exhausted, maxd, profile = bfs_component(Q, bound, budget, return_profile=True)
    return {"n": n, "B": bound, "trial": trial, "seed": seed, "budget": budget,
            "comp_size": size, "comp_exhausted": exhausted, "comp_maxdepth": maxd,
            "profile": profile, "weight_start": weight(Q), "time": round(time.time() - t, 2)}


def component(args):
    tasks = []
    s = args.seed
    for n in args.n:
        for bound in args.B:
            for trial in range(args.trials):
                s += 1
                tasks.append((n, bound, trial, s, args.budget))
    print(f"{len(tasks)} component measurements, {args.workers} workers", flush=True)
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for row in pool.imap_unordered(_component_task, tasks, chunksize=1):
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"  n={row['n']} B={row['B']} trial={row['trial']}: size={row['comp_size']} "
                  f"exhausted={row['comp_exhausted']} maxdepth={row['comp_maxdepth']} "
                  f"({row['time']}s)", flush=True)


def summarize(args):
    rows = [json.loads(l) for l in open(args.file) if l.strip()]
    cells = {}
    for r in rows:
        cells.setdefault((r["n"], r["B"], r.get("plant_bound") or r["B"], r["strategy"], r["L"]), []).append(r)
    hdr = ("n", "B", "pB", "strat", "L", "trials", "stuck", "len", "blocked", "comp", "exh",
           "A1", "dist", "A1nodes", "A2", "A2nodes", "min=", "A3", "A3B'", "A3nodes", "any", "t(s)")
    print(" ".join(f"{h:>7}" for h in hdr))
    for key in sorted(cells):
        rs = cells[key]
        n, B, pB, strat, L = key
        med = lambda xs: float(np.median(xs)) if xs else float("nan")
        a1 = np.mean([r["a1_found"] for r in rs])
        a2 = np.mean([r["a2_found"] for r in rs])
        anyf = np.mean([r["a1_found"] or r["a2_found"] or r.get("a3_found", False) for r in rs])
        a3 = np.mean([r.get("a3_found", False) for r in rs])
        a3b = [r["a3_bound"] for r in rs if r.get("a3_bound") is not None]
        a3n = [r["a3_nodes"] for r in rs if "a3_nodes" in r]
        mineq = np.mean([r.get("a2_minima_equal", False) for r in rs])
        d = [r["a1_dist"] for r in rs if r["a1_dist"] is not None]
        l2 = [r["a2_len"] for r in rs if r["a2_len"] is not None]
        comp = med([r["comp_size"] for r in rs])
        exh = np.mean([r["comp_exhausted"] for r in rs])
        bf = [r['blocked_frac'] for r in rs if r['blocked_frac'] is not None]
        sf = [r['sinksource_frac'] for r in rs if r['sinksource_frac'] is not None]
        print(f"{n:>7} {B:>7} {pB:>7} {strat:>7} {L:>7} {len(rs):>7} {np.mean([r['stuck'] for r in rs]):>7.2f} "
              f"{med([r['planted_len'] for r in rs]):>7.0f} {(np.mean(bf) if bf else float('nan')):>7.2f} "
              f"{comp:>7.0f} {exh:>7.2f} {a1:>7.2f} {med(d):>7.1f} {med([r['a1_nodes'] for r in rs]):>7.0f} "
              f"{a2:>7.2f} {med([r['a2_nodes'] for r in rs]):>7.0f} {mineq:>7.2f} {a3:>7.2f} {med(a3b):>7.0f} {med(a3n):>7.0f} "
              f"{anyf:>7.2f} {med([r['time'] for r in rs]):>7.2f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("grid")
    g.add_argument("--n", type=int, nargs="+", default=[6, 8, 10])
    g.add_argument("--B", type=int, nargs="+", default=[4, 16, 256, 65536, 2 ** 30])
    g.add_argument("--L", type=int, nargs="+", default=[10, 30, 100])
    g.add_argument("--strategies", nargs="+", default=["uniform", "cyclic", "backtrack"])
    g.add_argument("--trials", type=int, default=10)
    g.add_argument("--comp-budget", type=int, default=50000)
    g.add_argument("--bfs-budget", type=int, default=200000)
    g.add_argument("--workers", type=int, default=8)
    g.add_argument("--seed", type=int, default=20261108)
    g.add_argument("--plant-bound", type=int, nargs="+", default=None,
                   help="plant inside this smaller bound (attacker still uses --B)")
    g.add_argument("--a3-budget", type=int, default=100000, help="A3 node budget per bound level")
    g.add_argument("--out", default="mutation_path.jsonl")
    g.add_argument("--append", action="store_true")
    g.set_defaults(func=grid)

    gr = sub.add_parser("growth")
    gr.add_argument("--n", type=int, nargs="+", default=[6, 8, 10])
    gr.add_argument("--walks", type=int, default=200)
    gr.add_argument("--steps", type=int, default=60)
    gr.add_argument("--log2-thresholds", type=int, nargs="+", default=[2, 4, 8, 16, 32, 64])
    gr.add_argument("--seed", type=int, default=20261108)
    gr.add_argument("--out", default="mutation_growth.json")
    gr.set_defaults(func=growth)

    c = sub.add_parser("component")
    c.add_argument("--n", type=int, nargs="+", default=[6, 8, 10])
    c.add_argument("--B", type=int, nargs="+", default=[4, 16, 256, 65536, 2 ** 30])
    c.add_argument("--trials", type=int, default=3)
    c.add_argument("--budget", type=int, default=1000000)
    c.add_argument("--workers", type=int, default=4)
    c.add_argument("--seed", type=int, default=20261109)
    c.add_argument("--out", default="mutation_component.jsonl")
    c.set_defaults(func=component)

    sm = sub.add_parser("summarize")
    sm.add_argument("file", nargs="?", default="mutation_path.jsonl")
    sm.set_defaults(func=summarize)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
