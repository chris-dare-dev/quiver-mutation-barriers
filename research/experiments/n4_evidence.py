#!/usr/bin/env python
"""
n4_evidence.py -- evidence and proof material for Conjecture 10.1, F(4, w) <= 2w² (note 11).

Subcommands:
  bfz       numerical check of mu_k(B) = E B E^T (Berenstein-Fomin-Zelevinsky, Cluster algebras III,
            proof of Lemma 3.2, eq. (3.2)) on random mutation paths, and of the invariance of the gcd
            of the entries and of |Pf(B)| on 4 vertices.
  certify   apply (gcd, |Pf|) to the class files of notes 8 and 10.  A class is certified separate
            when no other class with the same invariants has a lower or equal bottom; only the others
            could be pockets of another class that join above the enumeration bound.
  rejoin    re-enumerate every uncertified class at bound max(B, c·bottom²) and look for joins (to a
            lower level, or between bottom components) that lie above the census bound.
  descent   Problem 6.1 on the census classes: for every quiver x of an enumerated class, D(x) = the
            least bound at which x reaches a quiver of smaller total weight; also the join level of the
            quivers of minimal total weight.  Option --gk runs the same on note 9's family G_k.
  joins     for the extreme pockets of notes 8-10, an optimal join path: its peak, its steps above the
            birth level, and whether the peak is a product of two entries.

Quivers are up to relabelling (canonical forms of bounded_paths.py).  Entries stay below 2^31 - 1
(see hunt.py), far above every bound used here.  Run from experiments/ with python -I.
"""
import argparse
import gzip
import heapq
import itertools
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict, deque
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT, all_mutations, max_entry_per_k, mutate  # noqa: E402
from bounded_paths import canonical, enumerate_component  # noqa: E402
from pockets import persistence  # noqa: E402

LIMIT = 2 ** 31 - 1
CLASS_FILES = [("n4_classes_B512.jsonl", 512), ("n4_classes_k5_B512.jsonl", 512), ("n4_classes_k67_B256.jsonl", 256),
               ("n4_classes_k8_B192.jsonl.gz", 192), ("n4_classes_k9_B192.jsonl.gz", 192)]


def open_text(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def upper(q):
    return [q[0][1], q[0][2], q[0][3], q[1][2], q[1][3], q[2][3]]


def invariants(q):
    """(gcd of the entries, |Pf|) of a 4-vertex quiver; Python integers, so no overflow."""
    u = [int(x) for x in upper(q)]
    g = 0
    for x in u:
        g = math.gcd(g, abs(x))
    return g, abs(u[0] * u[5] - u[1] * u[4] + u[2] * u[3])


def total(B):
    return int(np.abs(B).sum() // 2)


def load_classes(folder):
    """One record per class (keyed as in n4_classes.py), with the largest bound it was enumerated at."""
    rows = {}
    seen_lower = 0
    for fn, B in CLASS_FILES:
        for line in open_text(os.path.join(folder, fn)):
            r = json.loads(line)
            k = r["key"]
            if k in rows:
                assert rows[k]["bottom"] == r["bottom"], k
                seen_lower += 1
                if B <= rows[k]["B"]:
                    continue
            rows[k] = {"key": k, "bottom": r["bottom"], "B": B, "q": r["bottom_quiver"], "size": r["size"],
                       "pairs": [(p["birth"], p["death"], p["quiver"]) for p in r["pairs"]], "file": fn}
    return rows, seen_lower


# ----------------------------------------------------------------------------- bfz
def bfz_matrix(B, k, eps):
    """J + E_k of BFZ (3.2): identity with -1 at (k, k) and e_ik = max(0, -eps·b_ik) for i != k."""
    n = len(B)
    E = [[int(i == j) for j in range(n)] for i in range(n)]
    E[k][k] = -1
    for i in range(n):
        if i != k:
            E[i][k] = max(0, -eps * B[i][k])
    return E


def matmul(X, Y):
    return [[sum(X[i][l] * Y[l][j] for l in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]


def transpose(X):
    return [list(r) for r in zip(*X)]


def det(M):
    """Exact determinant by fraction-free elimination (Bareiss)."""
    M = [list(r) for r in M]
    n, sign, prev = len(M), 1, 1
    for c in range(n - 1):
        if M[c][c] == 0:
            sw = next((r for r in range(c + 1, n) if M[r][c] != 0), None)
            if sw is None:
                return 0
            M[c], M[sw] = M[sw], M[c]
            sign = -sign
        for r in range(c + 1, n):
            for j in range(c + 1, n):
                M[r][j] = (M[r][j] * M[c][c] - M[r][c] * M[c][j]) // prev
        prev = M[c][c]
    return sign * M[n - 1][n - 1]


def cmd_bfz(args):
    rng = np.random.default_rng(args.seed)
    stats = Counter()
    for t in range(args.paths):
        n = args.n[t % len(args.n)]
        U = np.triu(rng.integers(-args.wmax, args.wmax + 1, size=(n, n)), 1)
        B = (U - U.T).astype(DT)
        prev = -1
        inv0 = invariants(B.tolist()) if n == 4 else None
        for step in range(args.length):
            k = int(rng.integers(0, n))
            if k == prev:
                k = (k + 1) % n
            prev = k
            N = mutate(B, k)
            if np.abs(N).max() > LIMIT:
                stats["stopped_at_limit"] += 1
                break
            Bl, Nl = B.tolist(), N.tolist()
            for eps in (1, -1):
                E = bfz_matrix(Bl, k, eps)
                stats["checks"] += 1
                stats["E_B_Et_equal"] += matmul(matmul(E, Bl), transpose(E)) == Nl
                stats["E_squared_identity"] += matmul(E, E) == [[int(i == j) for j in range(n)] for i in range(n)]
                stats["det_E_minus_one"] += det(E) == -1
            if n == 4:
                stats["n4_steps"] += 1
                stats["n4_invariants_kept"] += invariants(Nl) == inv0
            stats["steps"] += 1
            stats["max_entry_seen"] = max(stats["max_entry_seen"], int(np.abs(N).max()))
            B = N
    out = dict(stats, paths=args.paths, length=args.length, n=args.n, seed=args.seed)
    print(json.dumps(out))
    if args.out:
        json.dump(out, open(args.out, "w"))


# ----------------------------------------------------------------------------- certify
def classify(rows):
    """For each class: 'certified', 'lower' (a class with the same invariants has a lower bottom) or
    'equal' (only classes with the same bottom share its invariants)."""
    by_inv = defaultdict(list)
    for r in rows.values():
        r["inv"] = invariants(r["q"])
        by_inv[r["inv"]].append(r)
    for grp in by_inv.values():
        bottoms = Counter(r["bottom"] for r in grp)
        lowest = min(bottoms)
        # census bounds of the other classes with a lower or equal bottom: a hidden pocket's own class is
        # one of them, and the pocket's join lies above that class's bound
        bounds = defaultdict(Counter)
        for r in grp:
            bounds[r["bottom"]][r["B"]] += 1
        for r in grp:
            if r["bottom"] > lowest:
                r["status"] = "lower"
            elif bottoms[r["bottom"]] > 1:
                r["status"] = "equal"
            else:
                r["status"] = "certified"
            cand = [B for b, cnt in bounds.items() if b < r["bottom"] for B in cnt]
            cand += [B for B, m in bounds[r["bottom"]].items() if m - (B == r["B"]) > 0]
            r["partner_bound"] = min(cand, default=None)
    return by_inv


def acyclic(q):
    rem = set(range(len(q)))
    while rem:
        src = [i for i in rem if not any(q[j][i] > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def cyclic_triangle(q):
    """Has q a full subquiver on three vertices that is mutation-cyclic: an oriented 3-cycle with all weights
    >= 2 and Markov constant x² + y² + z² - xyz <= 4 (Beineke-Brustle-Hille, Thm 1.2)?"""
    for a, b, c in itertools.combinations(range(4), 3):
        x, y, z = q[a][b], q[b][c], q[c][a]
        if (x > 0) == (y > 0) == (z > 0) and x * y * z != 0:
            x, y, z = abs(x), abs(y), abs(z)
            if min(x, y, z) >= 2 and x * x + y * y + z * z - x * y * z <= 4:
                return True
    return False


def cmd_certify(args):
    rows, seen_lower = load_classes(args.folder)
    by_inv = classify(rows)
    # Mutation-acyclicity status of the bottom quiver: 'A' acyclic, so the class is mutation-acyclic; 'N' it
    # has a full triangle that is mutation-cyclic by Beineke-Brustle-Hille (cyclic, weights >= 2, Markov
    # constant <= 4), so the class is not mutation-acyclic, because full subquivers of mutation-acyclic
    # quivers are mutation-acyclic (Warkentin); 'U' neither.  An A class differs from every N class.  Two
    # A classes differ too: by Caldero-Keller (Cor. 4; FWZ Thm 2.6.11) their acyclic quivers would be joined
    # by sink/source mutations, which keep the maximal entry, so the census would have joined them at
    # their common bottom level.
    status = {k: "A" if acyclic(r["q"]) else "N" if cyclic_triangle(r["q"]) else "U" for k, r in rows.items()}
    ck, extra = 0, 0
    for grp in by_inv.values():
        cnt = defaultdict(Counter)
        for r in grp:
            cnt[r["bottom"]][status[r["key"]]] += 1
        for r in grp:
            if r["status"] == "certified":
                continue
            st = status[r["key"]]
            others = sum((c for b, c in cnt.items() if b <= r["bottom"]), Counter())
            others[st] -= 1
            if st == "A" and others["U"] == 0 and others["N"] == 0:
                ck += 1
            elif st == "A" and others["U"] == 0 or st == "N" and others["U"] == 0 and others["N"] == 0:
                extra += 1
    table = defaultdict(Counter)
    for r in rows.values():
        table[r["bottom"]][r["status"]] += 1
        table[r["bottom"]]["classes"] += 1
    thresholds = defaultdict(lambda: math.inf)
    for r in rows.values():
        if r["status"] != "certified":
            t = max(r["B"], r["partner_bound"]) / r["bottom"] ** 2
            thresholds[r["bottom"]] = min(thresholds[r["bottom"]], t)
    out = {"classes": len(rows), "rows_met_again": seen_lower, "distinct_invariants": len(by_inv),
           "gcd_values": dict(Counter(r["inv"][0] for r in rows.values())),
           "pf_zero": sum(r["inv"][1] == 0 for r in rows.values()),
           "acyclic_bottom": sum(acyclic(r["q"]) for r in rows.values()),
           "bottom_status": dict(Counter(status.values())),
           "certified_by_caldero_keller_in_addition": ck,
           "certified_by_acyclicity_status_in_addition": extra,
           "by_bottom": {b: dict(table[b]) for b in sorted(table)},
           "hidden_ratio_threshold_census": {b: thresholds[b] for b in sorted(thresholds)}}
    print(json.dumps(out, indent=1))
    json.dump(out, open(args.out, "w"), indent=1)


# ----------------------------------------------------------------------------- rejoin
def _rejoin_task(task):
    q, b, B0, B1 = task
    t0 = time.time()
    states, exhausted = enumerate_component(np.array(q, dtype=DT), B1, 10 ** 8, unlabelled=True)
    pairs, lo, _, _ = persistence(states, 4)
    # every pair dying above the census bound is new; keep the quiver of those born <= 9 or above 2·birth²
    new = [(pb, pd, np.frombuffer(rp, dtype=DT).reshape(4, 4).tolist() if pb <= 9 or pd > 2 * pb * pb else None, sz)
           for pb, pd, rp, sz in pairs if pd > B0]
    low = [(pd / pb ** 2, pb, pd) for pb, pd, _, _ in pairs if 3 <= pb <= 9]
    return {"q": q, "bottom": b, "B0": B0, "B1": B1, "size": len(states), "exhausted": exhausted, "lo": lo,
            "new_pairs": new, "max_low": max(low) if low else None, "time": time.time() - t0}


def cmd_rejoin(args):
    rows, _ = load_classes(args.folder)
    classify(rows)
    todo = []
    for r in rows.values():
        if r["status"] == "certified" or r["bottom"] < args.min_bottom:
            continue
        B1 = max(r["B"], args.c * r["bottom"] ** 2)
        if B1 > r["B"]:
            todo.append((r["q"], r["bottom"], r["B"], B1))
    todo.sort(key=lambda t: -t[3])
    del rows                # the workers fork after this; keep their copy small
    print(f"{len(todo)} classes to re-enumerate", flush=True)
    stats = defaultdict(Counter)
    t0 = time.time()
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(_rejoin_task, todo, chunksize=16)):
            s = stats[r["bottom"]]
            s["classes"] += 1
            s["states"] += r["size"]
            s["not_exhausted"] += not r["exhausted"]
            s["reached_lower"] += r["lo"] < r["bottom"]
            s["new_pairs"] += len(r["new_pairs"])
            s["new_pairs_born_le_9"] += sum(pb <= 9 for pb, _, _, _ in r["new_pairs"])
            s["new_pairs_above_2b2"] += sum(pd > 2 * pb * pb for pb, pd, _, _ in r["new_pairs"])
            s["B1"] = r["B1"]
            if r["max_low"] and r["max_low"][0] > s.get("max_low_ratio", (0,))[0]:
                s["max_low_ratio"] = r["max_low"]
            for pb, pd, _, _ in r["new_pairs"]:
                if pd / pb ** 2 > s.get("max_new_ratio", (0,))[0]:
                    s["max_new_ratio"] = (pd / pb ** 2, pb, pd)
            if r["lo"] < r["bottom"] or not r["exhausted"] or any(x[2] is not None for x in r["new_pairs"]):
                f.write(json.dumps(r) + "\n")
                f.flush()
            if (i + 1) % 50000 == 0:
                print(f"  {i + 1} done, {time.time() - t0:.0f} s", flush=True)
    summary = {"c": args.c, "by_bottom": {b: dict(stats[b]) for b in sorted(stats)}, "time": round(time.time() - t0)}
    print(json.dumps(summary, indent=1))
    json.dump(summary, open(args.out.replace(".jsonl", "_summary.json"), "w"), indent=1)


# ----------------------------------------------------------------------------- graphs with edges
def enumerate_graph(Q, bound, budget=10 ** 8):
    """Component of Q (up to relabelling) inside the bound, with its edges.
    Returns keys, levels, total weights, edges (i, j) with i < j, exhausted flag."""
    start = canonical(np.array(Q, dtype=DT)).tobytes()
    index = {start: 0}
    keys, level, tw = [start], [], []
    edges = set()
    dq = deque([0])
    B0 = np.frombuffer(start, dtype=DT).reshape(4, 4)
    level.append(int(np.abs(B0).max()))
    tw.append(total(B0))
    while dq and len(keys) < budget:
        i = dq.popleft()
        cur = np.frombuffer(keys[i], dtype=DT).reshape(4, 4)
        N = all_mutations(cur)
        me = max_entry_per_k(N)
        for k in np.flatnonzero(me <= bound):
            kb = canonical(N[k]).tobytes()
            j = index.get(kb)
            if j is None:
                j = len(keys)
                index[kb] = j
                keys.append(kb)
                level.append(int(me[k]))
                tw.append(total(N[k]))
                dq.append(j)
            if j != i:
                edges.add((min(i, j), max(i, j)))
    return keys, level, tw, sorted(edges), not dq


def quiver_of(key):
    return np.frombuffer(key, dtype=DT).reshape(4, 4).tolist()


def descent_barriers(level, tw, edges):
    """D[i] = least L >= level[i] such that i reaches a quiver of smaller total weight through quivers
    of level <= L (None if none in the component).  Also the level at which all quivers of minimal total
    weight are joined.  Union-find over levels; each component keeps a max-heap of unresolved quivers."""
    n = len(level)
    by_level = defaultdict(list)
    for i in range(n):
        by_level[level[i]].append(i)
    e_by_level = defaultdict(list)
    for i, j in edges:
        e_by_level[max(level[i], level[j])].append((i, j))
    parent = list(range(n))
    minT = list(tw)
    heaps = {}
    D = [None] * n
    tmin = min(tw)
    mins = [i for i in range(n) if tw[i] == tmin]
    min_join = None

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for L in sorted(by_level):
        touched = []
        for i in by_level[L]:
            heaps[i] = [(-tw[i], i)]
            touched.append(i)
        for i, j in e_by_level[L]:
            ri, rj = find(i), find(j)
            if ri == rj:
                continue
            if len(heaps[ri]) < len(heaps[rj]):
                ri, rj = rj, ri
            parent[rj] = ri
            minT[ri] = min(minT[ri], minT[rj])
            for item in heaps.pop(rj):
                heapq.heappush(heaps[ri], item)
            touched.append(ri)
        for r in {find(x) for x in touched}:
            h = heaps[r]
            while h and -h[0][0] > minT[r]:
                D[heapq.heappop(h)[1]] = L
        if min_join is None and all(level[m] <= L for m in mins) and len({find(m) for m in mins}) == 1:
            min_join = L
    return D, mins, min_join


def _descent_task(task):
    q, bound, label = task
    keys, level, tw, edges, ex = enumerate_graph(q, bound)
    D, mins, min_join = descent_barriers(level, tw, edges)
    lo = min(level)
    worst = None          # largest D/max over quivers that are not of minimal total weight
    worst_low = None      # the same over quivers at level <= 2·bottom
    worst_sq = None       # largest D/max² over those of level >= 3
    n_above = 0           # quivers with D > max (descent needs a detour above their own maximal entry)
    for i in range(len(keys)):
        if D[i] is None:
            continue
        n_above += D[i] > level[i]
        rec = (D[i] / level[i], D[i], level[i], tw[i], i)
        if worst is None or rec > worst:
            worst = rec
        if level[i] <= 2 * lo and (worst_low is None or rec > worst_low):
            worst_low = rec
        if level[i] >= 3 and (worst_sq is None or D[i] / level[i] ** 2 > worst_sq[0]):
            worst_sq = (D[i] / level[i] ** 2, D[i], level[i], tw[i], i)
    unresolved = [i for i in range(len(keys)) if D[i] is None and tw[i] != tw[mins[0]]]
    res = {"label": label, "bottom": lo, "bound": bound, "size": len(keys), "exhausted": ex,
           "min_total": tw[mins[0]], "n_min": len(mins), "min_levels": sorted({level[m] for m in mins}),
           "min_join": min_join, "n_detour": n_above, "unresolved_nonmin": len(unresolved)}
    for name, w in (("worst", worst), ("worst_low", worst_low), ("worst_sq", worst_sq)):
        if w is not None:
            res[name] = {"ratio": w[0], "D": w[1], "max": w[2], "total": w[3], "quiver": quiver_of(keys[w[4]])}
    if label is not None and label.startswith("G"):
        res["bottom_quivers"] = [{"quiver": quiver_of(keys[i]), "total": tw[i], "D": D[i]}
                                 for i in range(len(keys)) if level[i] == lo]
    return res


def cmd_descent(args):
    if args.gk:
        tasks = []
        for k in args.gk:
            G = [[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]]
            tasks.append((G, (k + 4) * k, f"G{k}"))
    else:
        rows, _ = load_classes(args.folder)
        tasks = [(r["q"], min(r["B"], args.bound_cap), None) for r in rows.values()
                 if args.min_bottom <= r["bottom"] <= args.max_bottom]
        tasks.sort(key=lambda t: -t[1])
        del rows
    print(f"{len(tasks)} classes", flush=True)
    t0 = time.time()
    n = 0
    agg = defaultdict(Counter)
    best = defaultdict(dict)
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_descent_task, tasks, chunksize=8):
            n += 1
            if n % 50000 == 0:
                print(f"  {n} done, {time.time() - t0:.0f} s", flush=True)
            if args.gk:
                f.write(json.dumps(r) + "\n")
                continue
            g, bb = agg[r["bottom"]], best[r["bottom"]]
            g["classes"] += 1
            g["states"] += r["size"]
            g["not_exhausted"] += not r["exhausted"]
            g["unresolved_nonmin"] += r["unresolved_nonmin"]
            g["detour_quivers"] += r["n_detour"]
            g["classes_with_detour"] += r["n_detour"] > 0
            g["classes_several_min"] += r["n_min"] > 1
            top = max(r["min_levels"])
            g["classes_min_not_joined_at_own_level"] += r["min_join"] > top
            w = r.get("worst", {}).get("ratio", 0)
            for c in (2, 4, 8):
                g[f"classes_worst_ge_{c}"] += w >= c
            notable = False
            for name, val in (("worst", w), ("worst_sq", r.get("worst_sq", {}).get("ratio", 0)),
                              ("min_join_ratio", r["min_join"] / top), ("min_join_sq", r["min_join"] / top ** 2)):
                if val > bb.get(name, (0,))[0]:
                    bb[name] = (val, r)
                    notable = True
            if notable or w >= 8 or r["min_join"] > 4 * top:
                f.write(json.dumps(r) + "\n")
    if not args.gk:
        out = {"bound_cap": args.bound_cap, "by_bottom": {}}
        for b in sorted(agg):
            out["by_bottom"][b] = dict(agg[b])
            for name, (val, r) in best[b].items():
                ex = {"value": round(val, 4), "class_bottom_quiver": None, "min_join": r["min_join"],
                      "min_levels": r["min_levels"], "n_min": r["n_min"]}
                if name in ("worst", "worst_sq"):
                    ex.update(r[name])
                out["by_bottom"][b][name] = ex
        print(json.dumps(out, indent=1))
        json.dump(out, open(args.out.replace(".jsonl", "_summary.json"), "w"), indent=1)
    print(f"done in {time.time() - t0:.0f} s")


def cmd_gk_symbolic(args):
    """Note 9's closed set S, with entries polynomials in k, extended by total weights: which members
    are lighter than G_k, and the least level at which G_k reaches one (D(G_k) of Problem 6.1)."""
    import functools
    import n4_mirror_proof as mp
    K, one = (0, 1), (1,)
    Gk = [[(), K, mp.neg(K), mp.neg(K)], [mp.neg(K), (), (), K], [K, (), (), mp.neg(mp.add(K, mp.neg(one)))],
          [K, mp.neg(K), mp.add(K, mp.neg(one)), ()]]
    bound = (0, 4, 1)
    S, edges, todo = {mp.key(Gk): Gk}, [], [Gk]
    while todo:
        X = todo.pop()
        for v in range(4):
            Y = mp.mutate(X, v)
            if mp.less_eq(mp.maxentry(Y), bound):
                if mp.key(Y) not in S:
                    S[mp.key(Y)] = Y
                    todo.append(Y)
                edges.append((mp.key(X), mp.key(Y)))
    lv = {k: mp.maxentry(B) for k, B in S.items()}
    tw = {k: functools.reduce(mp.add, [mp.absp(B[i][j]) for i in range(4) for j in range(i + 1, 4)], ()) for k, B in S.items()}
    cmp = functools.cmp_to_key(lambda a, b: mp.sign(mp.add(a, mp.neg(b))))
    fmt = lambda p: " + ".join(f"{c}k^{i}" for i, c in enumerate(p) if c) or "0"
    g = mp.key(Gk)
    lighter = [k for k in S if mp.sign(mp.add(tw[g], mp.neg(tw[k]))) > 0]
    tmin = min(tw.values(), key=cmp)
    print(f"closed set S: {len(S)} quivers; G_k has level {fmt(lv[g])} and total weight {fmt(tw[g])}")
    for k in sorted(S, key=lambda k: (cmp(lv[k]), cmp(tw[k]))):
        print(f"  level {fmt(lv[k]):>14}  total {fmt(tw[k]):>16}  lighter than G_k: {k in lighter}")
    print(f"minimal total weight in S: {fmt(tmin)}, attained by {sum(1 for k in S if tw[k] == tmin)} member(s)")
    levels = sorted(set(lv.values()), key=cmp)
    parent = {k: k for k in S}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for L in levels:
        for a, b in edges:
            if mp.less_eq(lv[a], L) and mp.less_eq(lv[b], L) and find(a) != find(b):
                parent[find(a)] = find(b)
        if any(find(x) == find(g) for x in lighter if mp.less_eq(lv[x], L)):
            print(f"D(G_k) = {fmt(L)}: the first level at which G_k reaches a lighter member of S")
            break
    print(f"all signs used are valid for k > {float(max(mp.THRESH)):.2f} (largest Cauchy bound over {len(mp.THRESH)} polynomials)")


# ----------------------------------------------------------------------------- joins
def products(q):
    """Absolute products of two entries of q (upper triangle, any two positions, repeats allowed)."""
    u = [abs(x) for x in upper(q) if x != 0]
    return {a * c for a, c in itertools.combinations_with_replacement(u, 2)}


def one_step_values(q):
    """|b_ij + sgn(b_ik)·|b_ik·b_kj|| for every mutation of q: the entries a single mutation can create."""
    B = np.array(q, dtype=DT)
    return {int(x) for x in np.abs(all_mutations(B)).reshape(-1)}


def join_path(keys, level, edges, rep, b, death):
    """Optimal join of the pocket born at b whose quiver is keys[rep] and which dies at `death` (elder rule):
    the targets are the quivers of level <= b outside the pocket's component at bound death - 1 (so a merger
    with a sibling born at the same level, which the pocket survives, is passed over).  d is the least
    bound at which rep reaches a target; then, among paths of peak d, one with the fewest quivers above b
    (then the fewest steps)."""
    adj = defaultdict(list)
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    plateau = {rep}
    dq = deque([rep])
    while dq:
        i = dq.popleft()
        for j in adj[i]:
            if level[j] <= death - 1 and j not in plateau:
                plateau.add(j)
                dq.append(j)
    assert min(level[i] for i in plateau) == b
    plateau = {i for i in plateau if level[i] <= b}     # not targets: low quivers joined below the death
    # bottleneck Dijkstra from rep
    best = {rep: b}
    heap = [(b, rep)]
    done = set()
    d = None
    while heap:
        h, i = heapq.heappop(heap)
        if i in done:
            continue
        done.add(i)
        if level[i] <= b and i not in plateau:
            d = h
            break
        for j in adj[i]:
            v = max(h, level[j])
            if v < best.get(j, 1 << 62):
                best[j] = v
                heapq.heappush(heap, (v, j))
    if d is None:
        return None
    # fewest quivers above b, then fewest steps, inside level <= d, from rep to any target
    cost = {rep: (0, 0)}
    prev = {rep: None}
    heap = [((0, 0), rep)]
    done = set()
    end = None
    while heap:
        c, i = heapq.heappop(heap)
        if i in done:
            continue
        done.add(i)
        if level[i] <= b and i not in plateau:
            end = i
            break
        for j in adj[i]:
            if level[j] > d:
                continue
            cj = (c[0] + (level[j] > b), c[1] + 1)
            if cj < cost.get(j, (1 << 62, 0)):
                cost[j] = cj
                prev[j] = i
                heapq.heappush(heap, (cj, j))
    path = []
    i = end
    while i is not None:
        path.append(i)
        i = prev[i]
    return d, path[::-1]


def _joins_task(task):
    q_bottom, bound, rep_q, b, death, meta = task
    keys, level, tw, edges, ex = enumerate_graph(q_bottom, bound)
    index = {k: i for i, k in enumerate(keys)}
    rep = index[canonical(np.array(rep_q, dtype=DT)).tobytes()]
    d, path = join_path(keys, level, edges, rep, b, death)
    levels = [level[i] for i in path]
    high = [i for i, i_ in enumerate(path) if level[i_] > b]
    excursions = sum(1 for i in range(len(path)) if level[path[i]] > b and (i == 0 or level[path[i - 1]] <= b))
    first_peak = levels.index(d)
    launch = path[high[0] - 1]                     # last quiver at level <= b before the excursion
    pre_peak = path[first_peak - 1]
    q_rep, q_launch, q_pre = quiver_of(keys[rep]), quiver_of(keys[launch]), quiver_of(keys[pre_peak])
    return dict(meta, birth=b, death=death, d=d, bound=bound, size=len(keys), path_len=len(path) - 1,
                levels=levels, steps_above_birth=len(high), excursions=excursions,
                peak_index=first_peak, peak_count=levels.count(d), pre_peak_level=level[pre_peak],
                one_step_climb=level[pre_peak] <= b,
                peak_is_product_of_rep=d in products(q_rep), peak_is_product_of_launch=d in products(q_launch),
                peak_one_step_from_launch=d in one_step_values(q_launch),
                peak_one_step_from_pre=d in one_step_values(q_pre),
                rep=q_rep, launch=q_launch, pre_peak=q_pre, peak=quiver_of(keys[path[first_peak]]),
                path=[quiver_of(keys[i]) for i in path] if len(path) <= 400 else None)


def cmd_joins(args):
    rows, _ = load_classes(args.folder)
    cand = []
    for r in rows.values():
        for pb, pd, pq in r["pairs"]:
            if 3 <= pb <= 9:
                cand.append((pd / pb ** 2, pb, pd, pq, r))
    tasks = []
    for b in range(3, 10):
        for kind in ("bottom", "above"):
            c = sorted((x for x in cand if x[1] == b and (x[4]["bottom"] == b) == (kind == "bottom")),
                       key=lambda x: (-x[0], str(x[3])))
            pick = [x for x in c if x[0] >= args.min_ratio] or c[:1]
            for x in pick[:args.top]:
                ratio, pb, pd, pq, r = x
                tasks.append((r["q"], pd, pq, pb, pd, {"kind": kind, "class_bottom": r["bottom"],
                                                       "ratio_b2": round(ratio, 4)}))
    for k in range(4, 13):          # note 9's family, for comparison: G_k joins C_k at k(k - 1)
        G = [[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]]
        tasks.append((G, (k + 4) * k, G, k, k * (k - 1), {"kind": "G_k", "class_bottom": k,
                                                          "ratio_b2": round((k - 1) / k, 4)}))
    print(f"{len(tasks)} pockets", flush=True)
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_joins_task, tasks):
            f.write(json.dumps(r) + "\n")
            f.flush()


def ascent(r):
    """The climb of a join path from the launch quiver to the first peak: the first level above the
    birth (one mutation from the launch), then the increments up to the peak."""
    lv, b = r["levels"], r["birth"]
    i0 = next(i for i, x in enumerate(lv) if x > b)
    up = lv[i0:r["peak_index"] + 1]
    inc = [y - x for x, y in zip(up, up[1:]) if y > x]
    tail = inc[1:]                         # increments after the first rise of the ladder
    return {"J": up[0], "rises": len(inc), "increments": inc,
            "ladder": len(tail) >= 2 and len(set(tail)) == 1, "delta": tail[0] if tail else None}


def labelled_vertices(path):
    """Rebuild a labelled mutation sequence along a path of canonical forms: the vertex mutated at each
    step, and the weight of the arrow between the last two vertices mutated (None at the first step)."""
    X = np.array(path[0], dtype=DT)
    seq = []
    for nxt in path[1:]:
        target = canonical(np.array(nxt, dtype=DT)).tobytes()
        k = next(k for k in range(4) if canonical(mutate(X, k)).tobytes() == target)
        pair_w = int(abs(X[seq[-1][0], k])) if seq else None
        seq.append((k, pair_w))
        X = mutate(X, k)
    return seq


def corridor(r):
    """The longest run, on the climb from the first level above the birth to the first peak, of steps
    that alternate between the two ends of an arrow of weight 2 (an affine Kronecker corridor, along which
    entries grow linearly).  Returns its length in steps, the level gained before it (from J), along it,
    and after it up to the peak, so that d = J + before + gain + after; None if the path was not stored."""
    if not r["path"]:
        return None
    seq = labelled_vertices(r["path"])
    lv, b, pk = r["levels"], r["birth"], r["peak_index"]
    i0 = next(i for i, x in enumerate(lv) if x > b)        # step t takes path[t] to path[t + 1]
    best, t = (0, None, None), i0
    while t < pk:
        if t > i0 - 1 and seq[t][1] == 2:
            s0, e = t, t
            while e + 1 < pk and seq[e + 1][1] == 2 and seq[e + 1][0] == seq[e - 1][0] if e >= 1 else False:
                e += 1
            if e - s0 + 1 > best[0]:
                best = (e - s0 + 1, s0, e)
            t = e + 1
        else:
            t += 1
    n, s0, e = best
    if not n:
        return {"steps": 0, "before": 0, "gain": 0, "after": lv[pk] - lv[i0], "J": lv[i0]}
    return {"steps": n, "before": lv[s0] - lv[i0], "gain": lv[e + 1] - lv[s0], "after": lv[pk] - lv[e + 1], "J": lv[i0]}


def cmd_joins_summary(args):
    R = [json.loads(l) for l in open(args.joins)]
    R.sort(key=lambda r: (r["kind"] == "G_k", r["birth"], r["kind"], -r["ratio_b2"]))
    agg = defaultdict(Counter)
    print("kind   b  bottom death  d/b²   J   J/b²  rises  ladder δ  above-b  steps  peak=product  J=product  corridor(steps, before, gain, after)")
    for r in R:
        a = ascent(r)
        J_prod = a["J"] in products(r["launch"])
        print(f"{r['kind']:6} {r['birth']:2} {r['class_bottom']:4} {r['d']:5} {r['d'] / r['birth'] ** 2:5.2f} {a['J']:4} "
              f"{a['J'] / r['birth'] ** 2:5.2f} {a['rises']:5}  {str(a['ladder']):6} {str(a['delta']):>3} "
              f"{r['steps_above_birth']:6} {r['path_len']:6}  {str(r['peak_is_product_of_rep']):12} {str(J_prod):5}  "
              f"{tuple(corridor(r).values())[:4] if r['path'] else None}")
        g = agg[r["kind"]]
        g["pockets"] += 1
        g["death_equals_bottleneck"] += r["d"] == r["death"]
        g["one_excursion"] += r["excursions"] == 1
        g["peak_in_one_step_from_birth_level"] += r["one_step_climb"]
        g["ladder"] += a["ladder"]
        g["peak_is_product_of_two_entries"] += r["peak_is_product_of_rep"]
        g["first_jump_is_product"] += J_prod
        g["max_J_over_b2"] = max(g["max_J_over_b2"], round(a["J"] / r["birth"] ** 2, 3))
        g["max_ladder_gain_over_b2"] = max(g["max_ladder_gain_over_b2"], round((r["d"] - a["J"]) / r["birth"] ** 2, 3))
        c = corridor(r)
        if c is None:
            g["path_not_stored"] += 1
        else:
            g["corridor_ge_2_steps"] += c["steps"] >= 2
            g["max_corridor_steps"] = max(g["max_corridor_steps"], c["steps"])
            g["max_corridor_gain_over_b2"] = max(g["max_corridor_gain_over_b2"], round(c["gain"] / r["birth"] ** 2, 3))
            g["max_after_corridor_over_b2"] = max(g["max_after_corridor_over_b2"], round(c["after"] / r["birth"] ** 2, 3))
            g["max_before_corridor_over_b2"] = max(g["max_before_corridor_over_b2"], round(c["before"] / r["birth"] ** 2, 3))
            assert c["J"] + c["before"] + c["gain"] + c["after"] == r["d"]
            r["corridor"] = c
        if a["ladder"]:
            g["max_ladder_delta_over_b"] = max(g["max_ladder_delta_over_b"], round(a["delta"] / r["birth"], 3))
            g["max_ladder_rises"] = max(g["max_ladder_rises"], a["rises"])
        g["max_rises"] = max(g["max_rises"], a["rises"])
        g["max_steps_above_birth"] = max(g["max_steps_above_birth"], r["steps_above_birth"])
        g["sum_steps_above_birth"] += r["steps_above_birth"]
    print(json.dumps({k: dict(v) for k, v in agg.items()}, indent=1))


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("bfz")
    p.add_argument("--paths", type=int, default=2000)
    p.add_argument("--length", type=int, default=40)
    p.add_argument("--n", type=int, nargs="+", default=[4, 5, 6])
    p.add_argument("--wmax", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out")
    sub.add_parser("gk-symbolic")
    p = sub.add_parser("joins-summary")
    p.add_argument("joins")
    for name in ("certify", "rejoin", "descent", "joins"):
        p = sub.add_parser(name)
        p.add_argument("--folder", default=".")
        p.add_argument("--out", required=True)
        p.add_argument("--workers", type=int, default=12)
        if name == "rejoin":
            p.add_argument("--c", type=float, default=8)
            p.add_argument("--min-bottom", type=int, default=1)
        if name == "descent":
            p.add_argument("--min-bottom", type=int, default=1)
            p.add_argument("--max-bottom", type=int, default=7)
            p.add_argument("--bound-cap", type=int, default=256)
            p.add_argument("--gk", type=int, nargs="*")
        if name == "joins":
            p.add_argument("--min-ratio", type=float, default=1.5)
            p.add_argument("--top", type=int, default=12)
    args = ap.parse_args()
    {"bfz": cmd_bfz, "gk-symbolic": cmd_gk_symbolic, "certify": cmd_certify, "rejoin": cmd_rejoin, "descent": cmd_descent, "joins": cmd_joins,
     "joins-summary": cmd_joins_summary}[args.cmd](args)


if __name__ == "__main__":
    main()
