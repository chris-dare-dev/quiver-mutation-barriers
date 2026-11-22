#!/usr/bin/env python
"""
review12.py -- independent checks of notes 3-10 (note 12, 2026-11-11).

Written from the statements in the notes, without reusing the code under review (mutation_path,
bounded_paths, pockets, n4_*).  Quivers are 4x4 (or 3x3) skew-symmetric integer matrices; mutation is
the Fomin-Zelevinsky rule b'_ij = -b_ij if k in {i, j}, else b_ij + (|b_ik| b_kj + b_ik |b_kj|) / 2.

Subcommands:
  burnside   number of 4-vertex quivers up to relabelling with maximal entry exactly M (Burnside)
  n4slow     persistence of the maximal-entry filtration over all 4-vertex quivers with entries <= N,
             computed on LABELLED matrices with relabelling edges added (no canonical forms), with a
             plain Python union-find; compared with n4_all.py's stored pockets
  rank3      the same over all 3-vertex quivers (Theorem 3.1: no pockets), and the labelled
             weight-1 triangles of Theorem 3.1(3)
  classes    per-class persistence with an own enumerator, own canonical form (lexicographic maximum) and
             components recomputed level by level (no union-find); spot-checks of the stored census of
             notes 8 and 10 and of the formula of note 4 against the definition of f
  extremes   the two census extremes and G_k, enumerated above the census bounds
  mirror     the census under B -> -B: which classes are their own mirror, the mirror structure of the
             bottom components, and a search at a higher bound for joins between mirror classes
  cyclic     whether pocket classes contain a mutation-cyclic full triangle (so are not mutation-acyclic)
  cyclic2    the same, searching upwards from the bottom for such a triangle or for an acyclic quiver
  symbolic   Theorem 9.1 again, with PARI polynomials (cypari2), exact real-root thresholds and
             equality-up-to-relabelling tests instead of a canonical key
  handproof  the short proof of Theorem 9.1, checked with PARI for every k >= 3
  pendant    G_k with a path of extra vertices: the barrier on connected quivers with n >= 5 vertices

Run from experiments/ with python -I.
"""
import argparse
import gzip
import itertools
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict

import numpy as np

PERMS4 = list(itertools.permutations(range(4)))
PAIRS4 = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


# ----------------------------------------------------------------------------- Burnside
def burnside_count(N, n=4):
    """Orbits of S_n on skew-symmetric n x n matrices with entries in [-N, N]."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    total = 0
    perms = list(itertools.permutations(range(n)))
    for s in perms:
        # signed permutation of the pairs: {i, j} -> {s(i), s(j)}, sign -1 if the order flips
        img = {}
        for (i, j) in pairs:
            a, b = s[i], s[j]
            img[(i, j)] = ((min(a, b), max(a, b)), 1 if a < b else -1)
        seen, fix = set(), 1
        for p in pairs:
            if p in seen:
                continue
            q, sgn = p, 1
            while True:
                seen.add(q)
                q2, s2 = img[q]
                sgn *= s2
                q = q2
                if q == p:
                    break
            fix *= (2 * N + 1) if sgn == 1 else 1
        total += fix
    assert total % len(perms) == 0
    return total // len(perms)


def cmd_burnside(args):
    tot = 0
    for M in range(1, args.N + 1):
        c = burnside_count(M) - burnside_count(M - 1)
        tot += c
        print(f"level {M}: {c} quivers up to relabelling (cumulative {tot})")


# ----------------------------------------------------------------------------- labelled 4-vertex graph
def decode_all(N, n=4):
    base = 2 * N + 1
    m = n * (n - 1) // 2
    idx = np.arange(base ** m, dtype=np.int64)
    up = np.empty((idx.size, m), dtype=np.int16)
    t = idx.copy()
    for pos in range(m):
        up[:, pos] = t % base - N
        t //= base
    return up


def encode(up, N):
    base = 2 * N + 1
    m = up.shape[1]
    w = base ** np.arange(m, dtype=np.int64)
    return ((up.astype(np.int64) + N) * w).sum(axis=1)


def full_from_up(up, n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    B = np.zeros((up.shape[0], n, n), dtype=np.int64)
    for pos, (i, j) in enumerate(pairs):
        B[:, i, j] = up[:, pos]
        B[:, j, i] = -up[:, pos]
    return B


def up_from_full(B):
    n = B.shape[1]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return np.stack([B[:, i, j] for (i, j) in pairs], axis=1)


def mutate_np(B, k):
    """FZ mutation at k of a stack of matrices (exact, int64)."""
    bik = B[:, :, k][:, :, None]
    bkj = B[:, k, :][:, None, :]
    C = B + (np.abs(bik) * bkj + bik * np.abs(bkj)) // 2
    C[:, k, :] = -B[:, k, :]
    C[:, :, k] = -B[:, :, k]
    return C


def labelled_persistence(N, n, log):
    """Persistence pairs of the max-entry filtration on quivers up to relabelling, computed on the
    labelled graph plus relabelling edges.  Returns Counter of (birth, death) and survivors by birth."""
    t0 = time.time()
    up = decode_all(N, n)
    V = up.shape[0]
    lev = np.abs(up).max(axis=1).astype(np.int64)
    B = full_from_up(up, n)
    del up
    eu, ev, el = [], [], []
    for k in range(n):
        C = mutate_np(B, k)
        me = np.abs(C).reshape(V, -1).max(axis=1)
        ok = np.flatnonzero(me <= N)
        tgt = encode(up_from_full(C[ok]), N)
        keep = tgt > ok
        eu.append(ok[keep]); ev.append(tgt[keep]); el.append(np.maximum(lev[ok[keep]], me[ok[keep]]))
        del C
    # relabelling edges: a transposition and an n-cycle generate S_n
    for s in [(1, 0) + tuple(range(2, n)), tuple(range(1, n)) + (0,)]:
        P = np.zeros((n, n), dtype=np.int64)
        for i in range(n):
            P[s[i], i] = 1
        C = np.einsum("ab,vbc,dc->vad", P, B, P)
        tgt = encode(up_from_full(C), N)
        src = np.arange(V, dtype=np.int64)
        keep = tgt != src
        eu.append(src[keep]); ev.append(tgt[keep]); el.append(lev[keep])
        del C
    eu, ev, el = np.concatenate(eu), np.concatenate(ev), np.concatenate(el)
    order = np.argsort(el, kind="stable")
    eu, ev, el = eu[order], ev[order], el[order]
    log(f"  N={N} n={n}: {V} labelled matrices, {eu.size} edges (mutation + relabelling), built in {time.time() - t0:.0f}s")
    levl = lev.tolist()
    parent = list(range(V))
    birth = levl[:]                      # birth of the component whose root is this node

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = Counter()
    bounds = np.searchsorted(el, np.arange(N + 2))
    for L in range(1, N + 1):
        a, b = bounds[L], bounds[L + 1]
        U, W = eu[a:b].tolist(), ev[a:b].tolist()
        for x, y in zip(U, W):
            rx, ry = find(x), find(y)
            if rx == ry:
                continue
            if birth[rx] > birth[ry]:
                rx, ry = ry, rx
            if birth[ry] < L:
                pairs[(birth[ry], L)] += 1
            parent[ry] = rx
        log(f"  level {L} done ({time.time() - t0:.0f}s)")
    roots = Counter(birth[find(x)] for x in range(V) if parent[x] == x)
    # roots counts labelled components = unlabelled components (relabelling edges included)
    return pairs, roots


def cmd_n4slow(args):
    log = lambda s: print(s, flush=True)
    pairs, roots = labelled_persistence(args.N, 4, log)
    print(f"slow: {sum(pairs.values())} pockets with death <= {args.N}")
    print(f"slow: survivors by birth {[roots.get(b, 0) for b in range(args.N + 1)]}")
    ref = json.load(open(args.ref))
    rp = Counter((p["birth"], p["death"]) for p in ref["pockets"] if p["death"] <= args.N)
    print(f"{args.ref}: {sum(rp.values())} pockets with death <= {args.N}")
    diff = {k: (pairs.get(k, 0), rp.get(k, 0)) for k in set(pairs) | set(rp) if pairs.get(k, 0) != rp.get(k, 0)}
    print("pairs (birth, death) -> count, slow:", dict(sorted(pairs.items())))
    print("identical multisets of (birth, death):", not diff, diff if diff else "")
    if args.ref_same_N:
        r2 = json.load(open(args.ref_same_N))
        print(f"{args.ref_same_N}: survivors by birth {r2['survivors_by_birth']}")
        print("survivors identical:", r2["survivors_by_birth"] == [roots.get(b, 0) for b in range(args.N + 1)])


# ----------------------------------------------------------------------------- rank 3
def cmd_rank3(args):
    log = lambda s: print(s, flush=True)
    pairs, roots = labelled_persistence(args.N, 3, log)
    print(f"rank 3, all quivers with entries <= {args.N}: {sum(pairs.values())} pockets; components alive at N by birth: "
          f"{sum(roots.values())}")
    # labelled part (3): acyclic triangles with an edge of weight 1, labelled
    bad = tested = 0
    for p in range(1, args.W + 1):
        for q in range(1, args.W + 1):
            for l in range(1, args.W + 1):
                if 1 not in (p, q, l):
                    continue
                tested += 1
                j = min(p * q + l, q * l + p, l * p + q)
                ws = max(p, q, l)
                lev, adj = tri_component((p, l, q), 3 * j + 3)       # (b01, b02, b12): 0->1 p, 0->2 l, 1->2 q
                levels = sorted(set(lev.values()))
                low = lambda w: [x for x in lev if lev[x] <= w]
                n_isl = n_islands(lev, adj, ws)
                fs = {w: f_labelled(lev, adj, w) for w in range(ws, 2 * j + 1)}
                ok = (min(levels) == ws and n_isl >= 2 and all(fs[w] == j for w in range(ws, j))
                      and all(fs[w] <= w for w in range(j, 2 * j + 1)))
                cyc_min = min(lev[x] for x in lev if tri_cyclic(x))
                expect = 6 if (p, q, l).count(1) >= 2 else 2
                if not ok or cyc_min != j or n_isl != expect:
                    bad += 1
                    print(f"  ({p},{q},{l}): bottom {min(levels)}, islands {n_isl} (note 3: {expect}), "
                          f"f on [w*, j) {sorted(set(fs[w] for w in range(ws, j)))}, j {j}, least cyclic {cyc_min}")
    print(f"labelled acyclic triangles with a weight-1 edge, weights <= {args.W}: {tested} tested, {bad} deviating "
          f"(checks: bottom = w*, islands 2 or 6, f = j on [w*, j), f(w) <= w on [j, 2j], least cyclic level = j)")


def tri_mut(t, k):
    b = [[0, t[0], t[1]], [-t[0], 0, t[2]], [-t[1], -t[2], 0]]
    c = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if i == k or j == k:
                c[i][j] = -b[i][j]
            else:
                c[i][j] = b[i][j] + (abs(b[i][k]) * b[k][j] + b[i][k] * abs(b[k][j])) // 2
    return (c[0][1], c[0][2], c[1][2])


def tri_cyclic(t):
    a, b, c = t                       # 0->1 a, 0->2 b, 1->2 c: cyclic iff a, c > 0 > b or a, c < 0 < b
    return (a > 0 and c > 0 and b < 0) or (a < 0 and c < 0 and b > 0)


def tri_component(t0, bound):
    lev = {t0: max(map(abs, t0))}
    adj = defaultdict(set)
    todo = [t0]
    while todo:
        t = todo.pop()
        for k in range(3):
            u = tri_mut(t, k)
            m = max(map(abs, u))
            if m > bound:
                continue
            if u not in lev:
                lev[u] = m
                todo.append(u)
            if u != t:
                adj[t].add(u); adj[u].add(t)
    return lev, adj


def n_islands(lev, adj, w):
    low = [x for x in lev if lev[x] <= w]
    comp = _uf_components(low, [(a, b) for a in low for b in adj[a] if lev[b] <= w])
    return len(set(comp.values()))


def f_labelled(lev, adj, w):
    low = [x for x in lev if lev[x] <= w]
    h = bottleneck(lev, adj, low[0])
    m = max(l for l in set(lev.values()) if l <= w)
    return max([m] + [h[x] for x in low])


def _uf_components(nodes, edges):
    parent = {x: x for x in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return {x: find(x) for x in nodes}


# ----------------------------------------------------------------------------- per-class tools (n = 4)
# relabelling of an upper-triangle tuple: entry (i, j) of P B P^T is +-t[pair of (p[i], p[j])]
_RELAB = []
for _p in PERMS4:
    _RELAB.append([(PAIRS4.index((min(_p[i], _p[j]), max(_p[i], _p[j]))), 1 if _p[i] < _p[j] else -1) for (i, j) in PAIRS4])


def canon4(B):
    """Own canonical form: the lexicographically LARGEST upper-triangle tuple over the 24 relabellings.
    B is a 4x4 array/list or an upper-triangle 6-tuple."""
    if len(B) == 6 and not hasattr(B[0], "__len__"):
        t = tuple(int(x) for x in B)
    else:
        t = tuple(int(B[i][j]) for (i, j) in PAIRS4)
    return max(tuple(s * t[a] for a, s in r) for r in _RELAB)


def mat4(t):
    B = [[0] * 4 for _ in range(4)]
    for (i, j), x in zip(PAIRS4, t):
        B[i][j], B[j][i] = x, -x
    return np.array(B, dtype=np.int64)


def mutations4(t):
    """The four mutations of the quiver with upper-triangle tuple t, as upper-triangle tuples."""
    B = [[0] * 4 for _ in range(4)]
    for (i, j), x in zip(PAIRS4, t):
        B[i][j], B[j][i] = x, -x
    out = []
    for k in range(4):
        u = []
        for (i, j) in PAIRS4:
            if i == k or j == k:
                u.append(-B[i][j])
            else:
                u.append(B[i][j] + (abs(B[i][k]) * B[k][j] + B[i][k] * abs(B[k][j])) // 2)
        out.append(tuple(u))
    return out


def class_graph(t0, bound, budget=3_000_000):
    """BFS of the class of t0 (canonical tuple) up to relabelling inside the bound.
    Returns (levels: canon -> max entry, adjacency: canon -> set of canon, exhausted)."""
    lev = {t0: max(abs(x) for x in t0)}
    adj = defaultdict(set)
    todo = [t0]
    while todo:
        t = todo.pop()
        for C in mutations4(t):
            m = max(map(abs, C))
            if m > bound:
                continue
            c = canon4(C)
            if c not in lev:
                if len(lev) >= budget:
                    return lev, adj, False
                lev[c] = m
                todo.append(c)
            if c != t:
                adj[t].add(c)
                adj[c].add(t)
    return lev, adj, True


def bottleneck(lev, adj, src):
    """Minimax path heights from src: h[x] = least L such that x is joined to src through quivers
    of maximal entry <= L (Dijkstra with max instead of +)."""
    import heapq
    h = {src: lev[src]}
    pq = [(lev[src], src)]
    done = set()
    while pq:
        d, x = heapq.heappop(pq)
        if x in done:
            continue
        done.add(x)
        for y in adj[x]:
            nd = max(d, lev[y])
            if nd < h.get(y, 1 << 62):
                h[y] = nd
                heapq.heappush(pq, (nd, y))
    return h


def pairs_by_merge_tree(lev, adj):
    """Persistence pairs (birth, death) by recomputing the components of every X_L from scratch
    (BFS), then applying the elder rule level by level.  Slow but independent of union-find."""
    levels = sorted(set(lev.values()))
    prev = None                       # list of (birth, set of nodes) at the previous level
    pairs = []
    for L in levels:
        nodes = [x for x in lev if lev[x] <= L]
        seen = {}
        comps = []
        for s in nodes:
            if s in seen:
                continue
            cid = len(comps)
            stack = [s]
            seen[s] = cid
            members = [s]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if lev[y] <= L and y not in seen:
                        seen[y] = cid
                        stack.append(y)
                        members.append(y)
            comps.append(min(lev[m] for m in members))
        if prev is not None:
            groups = defaultdict(list)
            for b, rep in prev:
                groups[seen[rep]].append(b)
            for cid, bs in groups.items():
                bs.sort()
                for b in bs[1:]:
                    if b < L:
                        pairs.append((b, L))
        # representatives of the components at this level
        rep_of = {}
        for x in nodes:
            rep_of.setdefault(seen[x], x)
        prev = [(comps[cid], rep_of[cid]) for cid in range(len(comps))]
    return sorted(pairs)


def f_direct(lev, adj, w):
    """f(w) by definition: least level L >= m_w at which S_w lies in one component of X_L."""
    levels = sorted(set(lev.values()))
    low = [x for x in lev if lev[x] <= w]
    if not low:
        return None
    m = max(l for l in levels if l <= w)
    for L in levels:
        if L < m:
            continue
        src = low[0]
        seen = {src}
        stack = [src]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if lev[y] <= L and y not in seen:
                    seen.add(y)
                    stack.append(y)
        if all(x in seen for x in low):
            return L
    return None


def f_formula(pairs, levels, w):
    m = max(l for l in levels if l <= w)
    return max([m] + [d for b, d in pairs if b <= m < d])


def read_rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def cmd_classes(args):
    rng = random.Random(args.seed)
    files = {"n4_classes_B512.jsonl": 512, "n4_classes_k5_B512.jsonl": 512, "n4_classes_k67_B256.jsonl": 256,
             "n4_classes_k8_B192.jsonl.gz": 192, "n4_classes_k9_B192.jsonl.gz": 192}
    # 1. re-summarize the stored census (own reading of the stored rows)
    allrows = {}
    for fn, B in files.items():
        rows = list(read_rows(fn))
        allrows[fn] = rows
        byb = Counter(r["bottom"] for r in rows)
        ex = sum(1 for r in rows if r["exhausted"])
        print(f"{fn}: {len(rows)} rows, exhausted {ex}, by bottom {dict(sorted(byb.items()))}")
    best = {}
    best_above = (0, None)
    for fn, rows in allrows.items():
        for r in rows:
            for p in r["pairs"]:
                b, d = p["birth"], p["death"]
                if b > 9:
                    continue
                q = d / b ** 2
                if b == r["bottom"]:
                    if q > best.get(b, (0,))[0]:
                        best[b] = (q, d, fn, r["bottom_quiver"])
                elif q > best_above[0]:
                    best_above = (q, (b, d, r["bottom"], fn))
    for b in sorted(best):
        q, d, fn, bq = best[b]
        print(f"  birth {b} at the class bottom: largest death {d}, death/b^2 = {q:.4f} ({fn}) bottom quiver {bq}")
    print(f"  births above the class bottom: largest death/b^2 = {best_above[0]:.4f} {best_above[1]}")
    # rows whose class bottom lies below the file's range: are they classes already listed, with the same pairs?
    prev = {}
    for fn, lo_, hi_, B_ in CENSUS:
        dup = same = missing = 0
        for r in allrows[fn]:
            if r["bottom"] < lo_:
                if r["key"] in prev:
                    dup += 1
                    p0 = sorted((p["birth"], p["death"]) for p in prev[r["key"]]["pairs"] if p["death"] <= B_)
                    same += p0 == sorted((p["birth"], p["death"]) for p in r["pairs"])
                else:
                    missing += 1
            else:
                prev.setdefault(r["key"], r)
        print(f"  {fn}: {dup + missing} rows with a bottom below {lo_}: {dup} repeat a listed class "
              f"({same} with the same pairs up to {B_}), {missing} not listed before")
    # the table of note 8 (and its continuation to bottoms 8, 9), from the rows of each class once
    st = defaultdict(lambda: {"classes": 0, "several": 0, "latest": 0, "above": 0.0, "ratios": []})
    for fn, B, r in census_rows():
        d = st[r["bottom"]]
        d["classes"] += 1
        d["several"] += r["bottom_components"] >= 2
        for p in r["pairs"]:
            if p["birth"] > B // 4:
                continue
            d["ratios"].append(p["death"] / p["birth"])
            if p["birth"] == r["bottom"]:
                d["latest"] = max(d["latest"], p["death"])
            else:
                d["above"] = max(d["above"], p["death"] / p["birth"])
    for lo in sorted(st):
        d = st[lo]
        rs = sorted(d["ratios"])
        p99 = f"{rs[int(0.99 * (len(rs) - 1))]:.2f}" if rs else "-"
        print(f"  bottom {lo}: {d['classes']} classes, {d['several']} with several bottom components, latest death of a "
              f"bottom component {d['latest']} (ratio {d['latest'] / lo:.2f}), worst ratio above the bottom {d['above']:.2f}, "
              f"99th percentile of all ratios (nearest rank) {p99}")
    bs = sorted((json.loads(l) for l in open("n4_block_scan.jsonl")), key=lambda r: -r["join"] / r["bottom"] ** 2)
    print("  n4_block_scan.jsonl, largest join/bottom^2:",
          [(round(r["join"] / r["bottom"] ** 2, 3), (r["a"], r["c"], r["p"], r["q"]), r["bottom"], r["join"]) for r in bs[:4]])
    # 2. spot-check a random sample of classes with the own enumerator
    sample = []
    for fn, rows in allrows.items():
        rs = [r for r in rows if r["exhausted"]]
        with_pairs = [r for r in rs if r["pairs"]]
        k = args.per_file
        sample += [(fn, files[fn], r) for r in rng.sample(rs, min(k, len(rs)))]
        sample += [(fn, files[fn], r) for r in rng.sample(with_pairs, min(k, len(with_pairs)))]
    t0 = time.time()
    agree = 0
    fchecks = fbad = 0
    for i, (fn, B, r) in enumerate(sample):
        t = canon4(np.array(r["bottom_quiver"]))
        lev, adj, ex = class_graph(t, B)
        mine = pairs_by_merge_tree(lev, adj) if len(lev) <= args.slow_max else None
        if mine is None:
            continue
        theirs = sorted((p["birth"], p["death"]) for p in r["pairs"])
        same = (mine == theirs and ex == r["exhausted"] and len(lev) == r["size"] and min(lev.values()) == r["bottom"])
        agree += same
        if not same:
            print(f"  MISMATCH {fn} bottom {r['bottom']}: size {len(lev)} vs {r['size']}, pairs {mine[:6]} vs {theirs[:6]}")
        # formula of note 4 against the definition, at every w up to B/4
        levels = sorted(set(lev.values()))
        if i % args.f_every == 0:
            for w in range(min(levels), B // 4 + 1):
                fd, ff = f_direct(lev, adj, w), f_formula(mine, levels, w)
                fchecks += 1
                if fd != ff:
                    fbad += 1
                    print(f"  f mismatch at w={w}: direct {fd}, formula {ff}")
    checked = sum(1 for (fn, B, r) in sample if r["size"] <= args.slow_max)
    print(f"spot-check: {agree} of {checked} sampled classes agree (size, exhaustion, bottom, pairs) ({time.time() - t0:.0f}s)")
    print(f"formula f(w) = max(m_w, max D : b <= m_w < D) vs definition: {fchecks - fbad} of {fchecks} values agree")


def cmd_extremes(args):
    def show(name, Bq, bound):
        t = canon4(np.array(Bq))
        lev, adj, ex = class_graph(t, bound)
        lo = min(lev.values())
        bottoms = [x for x in lev if lev[x] == lo]
        h = bottleneck(lev, adj, bottoms[0])
        joins = sorted(h[x] for x in bottoms)
        opp = canon4(-mat4(t))
        print(f"{name}: class part {len(lev)} quivers inside {bound} (exhausted {ex}), bottom {lo}, "
              f"{len(bottoms)} bottom quivers, minimax heights from the first: {joins}; opposite in class: {opp in lev}, "
              f"opposite's height {h.get(opp)}")
        return lev, adj
    # note 8/22 extreme: G(6, T) with T = (-2, 5, -6): arrows 0->1, 2->0, 3->0 of weight 6
    b, (b12, b13, b23) = 6, (-2, 5, -6)
    G = np.zeros((4, 4), dtype=np.int64)
    G[0, 1], G[2, 0], G[3, 0] = b, b, b
    G[1, 2], G[1, 3], G[2, 3] = b12, b13, b23
    G = G - G.T
    show("bottom-6 mirror pair G(6, (-2,5,-6))", G, args.B)
    a, c, p, q = 9, 8, 4, 2
    H = [[0, -p, -a, c], [p, 0, c, -a], [a, -c, 0, -q], [-c, a, q, 0]]
    show("H(9, 8, 4, 2)", H, args.B)
    for k in args.k:
        Gk = [[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]]
        show(f"G_{k}", Gk, max(args.B, 2 * k * k + 10))
    # note 7's P_k: plateau at level k, first level at which a quiver below k is reached, lowest level within 2k
    for k in args.pk:
        t = canon4([[0, -k, -(k - 1), k], [k, 0, -2, 1], [k - 1, 2, 0, -2], [-k, -1, 2, 0]])
        lev, adj, ex = class_graph(t, 2 * k)
        h = bottleneck(lev, adj, t)
        print(f"P_{k}: plateau of {len(plateau(t))} quivers, first reaches a quiver below {k} at "
              f"{min(h[x] for x in lev if lev[x] < k)}, lowest level within {2 * k}: {min(lev.values())} (exhausted {ex})")


# ----------------------------------------------------------------------------- mirror test on the census
CENSUS = [("n4_classes_B512.jsonl", 1, 4, 512), ("n4_classes_k5_B512.jsonl", 5, 5, 512),
          ("n4_classes_k67_B256.jsonl", 6, 7, 256), ("n4_classes_k8_B192.jsonl.gz", 8, 8, 192),
          ("n4_classes_k9_B192.jsonl.gz", 9, 9, 192)]


def census_rows():
    """The 788,026 classes of notes 8 and 10, each once (rows whose bottom lies outside the file's
    range are duplicates of classes in an earlier file)."""
    for fn, lo, hi, B in CENSUS:
        for r in read_rows(fn):
            if lo <= r["bottom"] <= hi:
                yield fn, B, r


def plateau(t):
    """Component of the quiver t (canonical) among quivers of maximal entry <= max(t)."""
    m = max(map(abs, t))
    seen = {t}
    todo = [t]
    while todo:
        x = todo.pop()
        for C in mutations4(x):
            if max(map(abs, C)) <= m:
                c = canon4(C)
                if c not in seen:
                    seen.add(c)
                    todo.append(c)
    return seen


def cmd_mirror(args):
    t0 = time.time()
    rows = []
    owner = {}                         # plateau key -> row index
    stats_fill = Counter()
    for fn, B, r in census_rows():
        i = len(rows)
        lo = r["bottom"]
        main = plateau(canon4(np.array(r["bottom_quiver"])))
        pk = [max(main)]
        for p in r["pairs"]:
            if p["birth"] == lo:
                pk.append(max(plateau(canon4(np.array(p["quiver"])))))
        if len(set(pk)) < r["bottom_components"]:
            # the stored bottom quiver lies in a younger bottom component, so the eldest bottom plateau
            # is not among pk: enumerate the class to list every bottom plateau
            lev, adj, ex = class_graph(canon4(np.array(r["bottom_quiver"])), B)
            plateaus = []
            for x in lev:
                if lev[x] == lo and not any(x in P for P in plateaus):
                    plateaus.append(plateau(x))
            pk = [max(P) for P in plateaus]
            stats_fill[len(pk) == r["bottom_components"]] += 1
        for k in pk:
            owner.setdefault(k, i)
        rows.append((fn, B, lo, main, pk, len([p for p in r["pairs"] if p["birth"] == lo])))
    print(f"{len(rows)} classes, {len(owner)} bottom plateaus; classes re-enumerated to list their bottom plateaus "
          f"(count matched: {stats_fill[True]}, not matched: {stats_fill[False]}) ({time.time() - t0:.0f}s)", flush=True)
    stats = Counter()
    struct = Counter()
    flagged = []
    neg_key = lambda key: max(canon4(mat4(tuple(-x for x in t))) for t in plateau(key))
    for i, (fn, B, lo, main, pk, nb) in enumerate(rows):
        mk = max(canon4(mat4(tuple(-x for x in t))) for t in main)
        j = owner.get(mk)
        if j is None:
            stats[(lo, "mirror plateau in no census class")] += 1
        elif j == i:
            stats[(lo, "self-mirror class")] += 1
        else:
            stats[(lo, "mirror is another census class")] += 1
            if i < j:
                flagged.append((lo, i, j))
        if len(pk) >= 2:
            # all bottom plateaus of the class are known: classify them under the mirror map
            ks = set(pk)
            mir = [neg_key(k) for k in pk]
            n_self = sum(1 for k, m in zip(pk, mir) if m == k)
            n_pair = sum(1 for k, m in zip(pk, mir) if m != k and m in ks)
            struct[(lo, len(pk), n_pair, n_self)] += 1
    for key in sorted(stats):
        print(f"  bottom {key[0]}: {key[1]}: {stats[key]}")
    print("  classes with several bottom components: (bottom, components, components whose mirror is another bottom "
          "component, self-mirror components) -> classes")
    for key in sorted(struct):
        print(f"    {key}: {struct[key]}")
    mp = Counter()
    for (lo, nc, npair, nself), v in struct.items():
        mp[(lo, npair > 0)] += v
    print("  classes with a mirror pair among their bottom components, by bottom:",
          {lo: mp[(lo, True)] for lo in sorted({k[0] for k in mp})})
    rng = random.Random(args.seed)
    by_lo = defaultdict(list)
    for lo, i, j in flagged:
        by_lo[lo].append((i, j))
    print(f"pairs of distinct census classes that are mirror images: {len(flagged)}")
    for lo in sorted(by_lo):
        if args.bottoms and lo not in args.bottoms:
            continue
        sample = rng.sample(by_lo[lo], min(args.sample, len(by_lo[lo])))
        joined = big = 0
        for i, j in sample:
            a = max(rows[i][3])
            bound = args.factor * lo * lo
            lev, adj, ex = class_graph(a, bound, budget=args.budget)
            if not ex:
                big += 1
                continue
            if any(x in lev for x in rows[j][3]):          # the bottom plateau of the mirror class is reached
                joined += 1
                print(f"   bottom {lo}: classes {i} and {j} JOIN inside {bound}")
        print(f"  bottom {lo}: {len(by_lo[lo])} mirror pairs of classes; {len(sample)} sampled, searched to {args.factor}*b^2: "
              f"{joined} joined, {big} not exhausted within the budget", flush=True)


def tri_mutation_cyclic(x, y, z):
    """Cyclic triangle with weights x, y, z: mutation-cyclic iff all >= 2 and x^2 + y^2 + z^2 - xyz <= 4 (BBH)."""
    return min(x, y, z) >= 2 and x * x + y * y + z * z - x * y * z <= 4


def has_cyclic_triangle(t):
    B = mat4(t)
    for a, b, c in itertools.combinations(range(4), 3):
        x, y, z = B[a, b], B[b, c], B[c, a]
        if (x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0):
            if tri_mutation_cyclic(abs(x), abs(y), abs(z)):
                return True
    return False


def cmd_cyclic(args):
    """Certificate that a pocket's class is not mutation-acyclic: a full sub-triangle of the pocket quiver
    or of the class's bottom quiver is mutation-cyclic (Warkentin: full subquivers of mutation-acyclic
    quivers are mutation-acyclic)."""
    cnt = Counter()
    uncert = []
    for fn, B, r in census_rows():
        if not r["pairs"]:
            continue
        cls = has_cyclic_triangle(canon4(np.array(r["bottom_quiver"])))
        for p in r["pairs"]:
            if p["birth"] > B // 4:
                continue
            c = cls or has_cyclic_triangle(canon4(np.array(p["quiver"])))
            cnt[("bottom pocket" if p["birth"] == r["bottom"] else "pocket above bottom", c)] += 1
            if not c and len(uncert) < 10:
                uncert.append((fn, r["bottom_quiver"], p))
    for k in sorted(cnt):
        print(f"  {k[0]}: certified mutation-cyclic class {k[1]}: {cnt[k]}")
    N18 = json.load(open("n4_all_N18.json"))["pockets"]
    c18 = Counter(has_cyclic_triangle(canon4(np.array(p["quiver"]))) for p in N18)
    print(f"  n4_all_N18 pockets (death <= 18): lowest quiver has a mutation-cyclic full triangle: {dict(c18)}")
    for u in uncert[:5]:
        print("   uncertified:", u[0], u[1], u[2]["birth"], u[2]["death"], u[2]["quiver"])


def is_acyclic4(t):
    B = mat4(t)
    rem = set(range(4))
    while rem:
        src = [i for i in rem if not any(B[j, i] > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def cmd_cyclic2(args):
    """For census classes with a pocket born <= B/4 whose bottom quiver has no mutation-cyclic full triangle:
    search the class upwards from its bottom (lowest maximal entry first) for a quiver with such a
    triangle (the class is then not mutation-acyclic) or an acyclic quiver (the class is mutation-acyclic)."""
    import heapq
    res = Counter()
    examples = []
    t0 = time.time()
    for fn, B, r in census_rows():
        if not any(p["birth"] <= B // 4 for p in r["pairs"]):
            continue
        t = canon4(np.array(r["bottom_quiver"]))
        if has_cyclic_triangle(t):
            res["certified at the bottom quiver"] += 1
            continue
        seen = {t}
        pq = [(max(map(abs, t)), t)]
        out = None
        while pq and len(seen) < args.budget:
            m, x = heapq.heappop(pq)
            if is_acyclic4(x):
                out = ("contains an acyclic quiver", m)
                break
            if has_cyclic_triangle(x):
                out = ("certified mutation-cyclic", m)
                break
            for C in mutations4(x):
                mm = max(map(abs, C))
                if mm > B:
                    continue
                c = canon4(C)
                if c not in seen:
                    seen.add(c)
                    heapq.heappush(pq, (mm, c))
        if out is None:
            out = ("undecided within the bound", None)
        res[out[0]] += 1
        if out[0] == "contains an acyclic quiver" and len(examples) < 10:
            examples.append((fn, r["bottom"], r["bottom_quiver"], [(p["birth"], p["death"]) for p in r["pairs"]], out[1]))
    for k, v in sorted(res.items()):
        print(f"  {k}: {v}")
    for e in examples:
        print("   acyclic class with pockets:", e)
    print(f"({time.time() - t0:.0f}s)")


# ----------------------------------------------------------------------------- symbolic (PARI)
def cmd_symbolic(args):
    import cypari2
    pari = cypari2.Pari()
    k = pari("k")
    thresholds = []

    def sgn(p):
        """Sign of the polynomial p(k) for all integers k beyond its largest real root (recorded)."""
        p = pari(p)
        if p == 0:
            return 0
        lc = pari.pollead(p, k)
        if pari.poldegree(p, k) > 0:
            rr = pari.polrootsreal(p)
            if len(rr) > 0:
                thresholds.append(float(max(rr)))
        return 1 if lc > 0 else -1

    def mutate(B, v):
        C = [[B[i][j] for j in range(4)] for i in range(4)]
        for i in range(4):
            for j in range(4):
                if i == v or j == v:
                    C[i][j] = -B[i][j]
                else:
                    s1, s2 = sgn(B[i][v]), sgn(B[v][j])
                    # b_ij + (|b_iv| b_vj + b_iv |b_vj|) / 2
                    C[i][j] = B[i][j] + (s1 * B[i][v] * B[v][j] + B[i][v] * s2 * B[v][j]) / 2
        return C

    def maxent(B):
        es = [s * e for e in (B[i][j] for i in range(4) for j in range(i + 1, 4)) for s in [sgn(e) or 1]]
        best = es[0]
        for e in es[1:]:
            if sgn(e - best) > 0:
                best = e
        return best

    def equal_up_to_relabelling(X, Y):
        for p in PERMS4:
            if all(X[p[i]][p[j]] == Y[i][j] for i in range(4) for j in range(4)):
                return True
        return False

    def distinct_threshold(X, Y):
        """Every relabelling of X differs from Y at some entry; returns the largest real root of the
        differing entry with the smallest such root, over all relabellings (so X(k), Y(k) differ beyond it)."""
        worst = -1e18
        for p in PERMS4:
            best = None
            for i in range(4):
                for j in range(4):
                    d = pari(X[p[i]][p[j]] - Y[i][j])
                    if d == 0:
                        continue
                    if pari.poldegree(d, k) <= 0:
                        r = -1e18
                    else:
                        rr = pari.polrootsreal(d)
                        r = float(max(rr)) if len(rr) else -1e18
                    best = r if best is None else min(best, r)
            assert best is not None
            worst = max(worst, best)
        return worst

    Gk = [[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]]
    Gk = [[pari(x) for x in row] for row in Gk]
    for bound_s in args.bounds:
        thresholds.clear()
        bound = pari(bound_s)
        S = [Gk]
        edges = []
        exits = 0
        i = 0
        while i < len(S):
            X = S[i]
            for v in range(4):
                Y = mutate(X, v)
                if sgn(bound - maxent(Y)) < 0:
                    exits += 1
                    continue
                for jdx, Z in enumerate(S):
                    if equal_up_to_relabelling(Y, Z):
                        break
                else:
                    jdx = len(S)
                    S.append(Y)
                edges.append((i, jdx))
            i += 1
        levels = [maxent(X) for X in S]
        dist = [distinct_threshold(S[a], S[b]) for a in range(len(S)) for b in range(a + 1, len(S))]
        # levels in increasing order at large k
        import functools
        uniq = []
        for L in levels:
            if not any(L == U for U in uniq):
                uniq.append(L)
        uniq.sort(key=functools.cmp_to_key(lambda a, b: sgn(a - b)))
        lo = uniq[0]
        bottom = [a for a in range(len(S)) if levels[a] == lo]
        opp = [[-x for x in row] for row in Gk]
        opp_in = [a for a in range(len(S)) if equal_up_to_relabelling(opp, S[a])]
        print(f"bound {bound_s}: closed set of {len(S)} quivers, {exits} mutations leave the bound")
        print(f"  levels: {[str(U) for U in uniq]}; quivers per level {[sum(1 for L in levels if L == U) for U in uniq]}")
        print(f"  bottom quivers: {bottom}; -G_k is member {opp_in}")
        for U in uniq:
            parent = list(range(len(S)))

            def find(x):
                while parent[x] != x:
                    x = parent[x]
                return x
            for a, b in edges:
                if sgn(U - levels[a]) >= 0 and sgn(U - levels[b]) >= 0:
                    ra, rb = find(a), find(b)
                    if ra != rb:
                        parent[ra] = rb
            print(f"  at level {U}: bottom quivers in {len({find(a) for a in bottom})} component(s)")
        print(f"  largest real root of any polynomial whose sign was used: {max(thresholds):.4f} ({len(thresholds)} sign calls with real roots)")
        print(f"  members stay pairwise distinct up to relabelling for k > {max(dist):.4f}")
        if args.show:
            for a, X in enumerate(S):
                print(f"   [{a}] level {levels[a]}: {[[str(x) for x in row] for row in X]}")


def cmd_handproof(args):
    """The short proof of Theorem 9.1 (note 12), checked with PARI polynomials in k:
    (a) every mutation of G_k, and of the 4-cycle C_k = mu_2 mu_1 G_k, has an entry of absolute value >= k^2 - k;
    (b) mu_0 mu_3 mu_2 mu_1 (G_k) = P (-G_k) P^T for the relabelling 0<->1, 2<->3, with maximal entries
        k^2 - k, k, k^2 - k, k along the way;
    (c) G_k and -G_k are not isomorphic: their (out-weight, in-weight) multisets differ.
    Every sign and comparison used is checked to hold for every integer k >= 3."""
    import cypari2
    pari = cypari2.Pari()
    k = pari("k")
    K = 3                                     # all signs below are checked to hold for every integer k >= K

    def pos(p):
        """p(k) > 0 for every integer k >= K: leading coefficient positive and no real root >= K."""
        p = pari(p)
        if pari.poldegree(p, k) <= 0:
            return p != 0 and pari.pollead(p, k) > 0
        return pari.pollead(p, k) > 0 and all(float(r) < K for r in pari.polrootsreal(p)) and pari.subst(p, k, K) > 0

    def sgn(p):
        p = pari(p)
        if p == 0:
            return 0
        if pos(p):
            return 1
        assert pos(-p), f"sign of {p} not constant for k >= {K}"
        return -1

    def mutate(B, v):
        C = [[B[i][j] for j in range(4)] for i in range(4)]
        for i in range(4):
            for j in range(4):
                if i == v or j == v:
                    C[i][j] = -B[i][j]
                elif sgn(B[i][v]) * sgn(B[v][j]) > 0:
                    C[i][j] = B[i][j] + sgn(B[i][v]) * B[i][v] * B[v][j]
        return C

    def absmax(B):
        es = [sgn(B[i][j]) * B[i][j] for i in range(4) for j in range(i + 1, 4) if B[i][j] != 0]
        best = es[0]
        for e in es[1:]:
            if sgn(e - best) > 0:
                best = e
        return best

    G = [[pari(x) for x in row] for row in [[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]]]
    neg = lambda B: [[-x for x in row] for row in B]
    print("(a) maximal entries of the four mutations (valid for k >= 3):")
    for name, X in [("G_k", G), ("C_k = mu_2 mu_1 G_k", mutate(mutate(G, 1), 2))]:
        ms = [absmax(mutate(X, v)) for v in range(4)]
        ok = all(sgn(m - (k * k - k)) >= 0 for m in ms)
        print(f"    {name}: {[str(m) for m in ms]}  all >= k^2 - k: {ok}")
    X = G
    path = []
    for v in [1, 2, 3, 0]:
        X = mutate(X, v)
        path.append(str(absmax(X)))
    p = [1, 0, 3, 2]
    target = [[-G[p[i]][p[j]] for j in range(4)] for i in range(4)]
    print(f"(b) mu_0 mu_3 mu_2 mu_1 (G_k): maximal entries {path}; equals the relabelled -G_k: "
          f"{all(X[i][j] == target[i][j] for i in range(4) for j in range(4))}")
    C = mutate(mutate(G, 1), 2)
    print(f"    C_k = {[[str(x) for x in row] for row in C]}")

    def degs(B):
        return sorted((str(sum(B[i][j] for j in range(4) if sgn(B[i][j]) > 0)),
                       str(sum(-B[i][j] for j in range(4) if sgn(B[i][j]) < 0))) for i in range(4))
    print(f"(c) (out, in) weights of G_k: {degs(G)}; of -G_k: {degs(neg(G))}; different: {degs(G) != degs(neg(G))}")


def cmd_pendant(args):
    """G_k with a path of n - 4 extra vertices hanging from vertex 0 (a connected n-vertex quiver Q).
    Checks: Q is a local minimum of total weight; every quiver reachable from Q through maximal entry
    < k^2 - k keeps the block G_k on vertices 0..3 and has exactly four entries of absolute value k;
    X = mu_0 mu_3 mu_2 mu_1 Q has maximal entry k and five entries of absolute value k (so X is not
    isomorphic to any of them), with k^2 - k the highest point on the way; mu_2 mu_1 Q is lighter than Q."""
    def Gk(k):
        return np.array([[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]], dtype=np.int64)
    tw = lambda B: int(np.abs(B).sum() // 2)
    for n in args.n:
        for k in args.k:
            for orient in (1, -1):
                Q = np.zeros((n, n), dtype=np.int64)
                Q[:4, :4] = Gk(k)
                prev = 0
                for v in range(4, n):
                    Q[v, prev], Q[prev, v] = orient, -orient
                    prev = v
                local_min = all(tw(mutate_np(Q[None], v)[0]) >= tw(Q) for v in range(n))
                L = k * k - k - 1
                seen = {Q.tobytes(): Q}
                todo = [Q]
                while todo:
                    Y = todo.pop()
                    for v in range(n):
                        Z = mutate_np(Y[None], v)[0]
                        if np.abs(Z).max() <= L and Z.tobytes() not in seen:
                            seen[Z.tobytes()] = Z
                            todo.append(Z)
                block_ok = all((Y[:4, :4] == Gk(k)).all() for Y in seen.values())
                nk = {int((np.abs(Y[np.triu_indices(n, 1)]) == k).sum()) for Y in seen.values()}
                X = Q.copy()
                hi = 0
                for v in [1, 2, 3, 0]:
                    X = mutate_np(X[None], v)[0]
                    hi = max(hi, int(np.abs(X).max()))
                nkX = int((np.abs(X[np.triu_indices(n, 1)]) == k).sum())
                lighter = tw(mutate_np(mutate_np(Q[None], 1), 2)[0]) < tw(Q)
                print(f"n={n} k={k} orientation {orient:+d}: local min {local_min}; {len(seen)} labelled quivers below k^2-k, "
                      f"block G_k in all {block_ok}, entries = k: {sorted(nk)}; X: max {int(np.abs(X).max())}, entries = k: {nkX}, "
                      f"highest point {hi} = k^2-k {hi == k * k - k}; mu2 mu1 Q lighter {lighter}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("burnside"); s.add_argument("--N", type=int, default=18)
    s = sub.add_parser("n4slow"); s.add_argument("--N", type=int, default=6)
    s.add_argument("--ref", default="n4_all_N18.json"); s.add_argument("--ref-same-N", default=None)
    s = sub.add_parser("rank3"); s.add_argument("--N", type=int, default=40); s.add_argument("--W", type=int, default=8)
    s = sub.add_parser("classes"); s.add_argument("--per-file", type=int, default=40); s.add_argument("--seed", type=int, default=42)
    s.add_argument("--slow-max", type=int, default=20000); s.add_argument("--f-every", type=int, default=5)
    s = sub.add_parser("extremes"); s.add_argument("--B", type=int, default=400); s.add_argument("--k", type=int, nargs="*", default=[])
    s.add_argument("--pk", type=int, nargs="*", default=[])
    s = sub.add_parser("mirror"); s.add_argument("--sample", type=int, default=30); s.add_argument("--seed", type=int, default=7)
    s.add_argument("--factor", type=int, default=4); s.add_argument("--budget", type=int, default=400000)
    s.add_argument("--bottoms", type=int, nargs="*", default=[])
    s = sub.add_parser("handproof")
    s = sub.add_parser("pendant"); s.add_argument("--n", type=int, nargs="+", default=[5, 6, 7]); s.add_argument("--k", type=int, nargs="+", default=[3, 4, 5, 6, 8])
    s = sub.add_parser("cyclic")
    s = sub.add_parser("cyclic2"); s.add_argument("--budget", type=int, default=200000)
    s = sub.add_parser("symbolic"); s.add_argument("--bounds", nargs="+", default=["k^2+4*k", "2*k^2"])
    s.add_argument("--show", action="store_true")
    args = ap.parse_args()
    {"burnside": cmd_burnside, "n4slow": cmd_n4slow, "rank3": cmd_rank3, "classes": cmd_classes,
     "extremes": cmd_extremes, "mirror": cmd_mirror, "cyclic": cmd_cyclic, "handproof": cmd_handproof, "pendant": cmd_pendant, "cyclic2": cmd_cyclic2, "symbolic": cmd_symbolic}[args.cmd](args)


if __name__ == "__main__":
    main()
