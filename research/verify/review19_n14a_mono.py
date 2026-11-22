"""Check A of note 14, item 4: is the level monotone in pre-fork far regions?  A search for
counterexamples with the independent library.

For many pre-fork roots (k k' not joined, or joined by one arrow), the far region is explored to a radius
(labelled BFS from the root and, if |q_kk'| = 1, its twin, never crossing the two bridges).  Checked:
 (1) no quiver of the region has level below the root;
 (2) the property Proposition 14.3 needs: every explored quiver X is joined to a root, inside the explored
     ball, through quivers of level <= level(X) (minimax path, Dijkstra);
 (3) "outward" steps never lower the level: fork or pre-fork at a vertex other than its return, wing at a
     vertex other than its return, tip at a vertex outside its light pair (Ervin's classification, own
     predicates); and which entries can shrink on such steps;
 (4) every non-root quiver whose neighbours were all explored has a strictly lighter neighbour in the
     region of no larger level (the local property that gives (2) by induction on the weight).
Roots: pre-forks built from random keys (small and lopsided entries), random one-light-pair quivers, and
the pre-fork roots hanging from the finite cores of sampled census classes.

  python -I review19_n14a_mono.py N_KEY N_RAND N_CENSUS RADIUS SEED
"""
import gzip
import heapq
import json
import os
import random
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14a_lib as L


def from_key(rng, lo, hi):
    while True:
        t = [rng.randint(lo, hi) for _ in range(6)]
        k, kp = rng.sample(range(4), 2)
        a, b = min(k, kp), max(k, kp)
        t[L.UPPER.index((a, b))] = rng.choice([0, 1, -1])
        B = L.from6(t)
        perm = list(range(4))
        rng.shuffle(perm)
        B = L.relabel(B, perm)
        if not L.is_key(B):
            continue
        B = L.mut(B, rng.randrange(4))
        # optionally walk outward along pre-forks (Lemma 4.6) to get deeper roots
        for _ in range(rng.randrange(3)):
            pt = L.prefork_triples(B)
            if not pt:
                break
            r, k1, k2 = next(iter(pt))
            ms = [m for m in range(4) if m not in (r, k1, k2)]
            B = L.mut(B, ms[0])
        pt = L.prefork_triples(B)
        if pt and not L.fork_returns(B):
            return B


def from_rand(rng, R):
    while True:
        t = [rng.choice([-1, 1]) * rng.randint(2, R) for _ in range(6)]
        t[rng.randrange(6)] = rng.choice([-1, 0, 1])
        B = L.from6(t)
        if L.prefork_triples(B) and not L.fork_returns(B):
            return B


def census_roots(rng, n_classes):
    """Pre-fork roots hanging from the finite cores of sampled census classes (cores recomputed with the
    independent library from the bottom quiver recorded in n4_opposite_cores.jsonl.gz)."""
    recs = []
    with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["ex"] and r.get("pre", 0) > 0:
                recs.append((r["i"], tuple(r["q"])))
    rng.shuffle(recs)
    out = []
    for i, q in recs[:n_classes]:
        res = L.core_of(L.from6(q), cap=3000)
        if res is None:
            continue
        rep, adj, ups, sinks = res
        K = sinks[0]
        for x, m, Y in ups:
            if x in K and not L.fork_returns(Y):
                out.append((Y, m, i))
    return out


def outward_vertices(X):
    """Vertices v such that the step X -> mu_v(X) is 'outward' by Ervin's classification of X."""
    out = {}
    fr = L.fork_returns(X)
    if fr:
        out["fork"] = {v for v in range(4) if v not in fr}
    pt = L.prefork_triples(X)
    if pt and not fr:
        rs = {r for r, k, kp in pt}
        out["pre-fork"] = {v for v in range(4) if v not in rs}
    w = L.wing_pairs(X, "oriented")
    if w:
        out["wing"] = {v for v in range(4) if all(v != kk for kk, kp in w)}
    tp = L.tip_pairs(X, "oriented")
    if tp:
        out["tip"] = {v for v in range(4) if all(v not in (a, b) for a, b in tp)}
    return out


def region(root, m, radius, cap=40000):
    roots = [root]
    lp = L.light_pairs(root)
    if lp and abs(root[lp[0][0]][lp[0][1]]) == 1:
        k, kp = lp[0]
        X = root
        for v in (k, kp, k, kp, k):
            X = L.mut(X, v)
        roots.append(X)
    dist = {x: 0 for x in roots}
    nbr = {}
    front = list(roots)
    for d in range(radius):
        nxt = []
        for z in front:
            nbr[z] = []
            for v in range(4):
                if z in roots and v == m:
                    continue
                y = L.mut(z, v)
                nbr[z].append((v, y))
                if y not in dist and L.level(y) < 10 ** 30 and len(dist) < cap:
                    dist[y] = d + 1
                    nxt.append(y)
        front = nxt
    return roots, dist, nbr


def main():
    n_key, n_rand, n_cen, radius, seed = (int(a) for a in sys.argv[1:6])
    rng = random.Random(seed)
    t0 = time.time()
    jobs = []
    for _ in range(n_key // 2):
        jobs.append(("key, entries 2..4", from_key(rng, 2, 4)))
    for _ in range(n_key - n_key // 2):
        jobs.append(("key, entries 2..12", from_key(rng, 2, 12)))
    for _ in range(n_rand):
        jobs.append(("random one light pair, entries 2..9", from_rand(rng, 9)))
    jobs = [(name, B, next(iter({r for r, k, kp in L.prefork_triples(B)}))) for name, B in jobs]
    cr = census_roots(rng, n_cen)
    jobs += [("census core root", Y, m) for Y, m, i in cr]
    print(f"regions: {Counter(n for n, B, m in jobs)} ({time.time() - t0:.0f}s)", flush=True)
    st = Counter()
    bad = Counter()
    ex = {}
    shrink = Counter()
    for name, root, m in jobs:
        q = min(abs(root[a][b]) for a, b in L.light_pairs(root))
        tag = f"{name}, |q_kk'|={q}"
        st[tag] += 1
        roots, dist, nbr = region(root, m, radius)
        st["labelled quivers explored"] += len(dist)
        l0 = L.level(root)
        lev = {x: L.level(x) for x in dist}
        if min(lev.values()) < l0:
            bad["(1) a quiver below the root level"] += 1
            ex.setdefault("(1)", (L.to6(root), m))
        # (2) minimax inside the ball
        h = {x: lev[x] for x in roots}
        pq = [(lev[x], i, x) for i, x in enumerate(roots)]
        cnt = len(pq)
        done = set()
        while pq:
            d, _, x = heapq.heappop(pq)
            if x in done:
                continue
            done.add(x)
            for v, y in nbr.get(x, []):
                if y in dist:
                    nd = max(d, lev[y])
                    if nd < h.get(y, 1 << 400):
                        h[y] = nd
                        cnt += 1
                        heapq.heappush(pq, (nd, cnt, y))
        viol = [x for x in dist if h.get(x, 1 << 400) > lev[x]]
        if viol:
            bad["(2) a quiver joined to the root only above its own level (inside the ball)"] += 1
            ex.setdefault("(2)", (L.to6(root), m, L.to6(viol[0])))
        # (3) and (4)
        for x, ns in nbr.items():
            ow = outward_vertices(x)
            if not ow:
                bad["(3) explored quiver that is none of fork/pre-fork/wing/tip"] += 1
                ex.setdefault("(3) none", (L.to6(root), m, L.to6(x)))
            for typ, vs in ow.items():
                for v, y in ns:
                    if v in vs:
                        st[f"(3) outward steps from a {typ}"] += 1
                        if lev[y] < lev[x] if y in lev else L.level(y) < lev[x]:
                            bad[f"(3) outward step from a {typ} lowers the level"] += 1
                            ex.setdefault(f"(3) {typ}", (L.to6(root), m, L.to6(x), v))
                        if any(abs(y[i][j]) < abs(x[i][j]) for i, j in L.UPPER):
                            shrink[typ] += 1
            if x in roots:
                continue
            if len(ns) == 4 and all(y in dist for v, y in ns):
                st["(4) non-root quivers with all neighbours explored"] += 1
                if not any(L.weight(y) < L.weight(x) and lev[y] <= lev[x] for v, y in ns):
                    bad["(4) no lighter neighbour of no larger level"] += 1
                    ex.setdefault("(4)", (L.to6(root), m, L.to6(x)))
    print(f"radius {radius}, seed {seed}")
    for k in sorted(st):
        print(f"  {k}: {st[k]}")
    print("  outward steps on which some entry shrinks (by type of the source quiver):", dict(shrink))
    print("failures:", dict(bad) if bad else "none")
    for k, v in ex.items():
        print(f"  first example {k}: {v}")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
