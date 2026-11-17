"""Check A of note 14, Theorem 14.2: the class of G_k recomputed with the independent library
review19_n14a_lib.py (own mutation, own fork/pre-fork predicates, own closure and sink-SCC core).

For each k: V'(G_k), its sink SCCs (the core), levels, strict up-exit steps (kinds, levels, weights),
balanced edges, the direct shape test on the core, persistence of the extended core, f(G_k, w), a
radius-limited exploration of every far region (least level met), and for small k a brute-force sublevel
enumeration of the component of G_k.

  python -I review19_n14a_gk.py KMIN KMAX
"""
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14a_lib as L


def G(k):
    B = [[0] * 4 for _ in range(4)]
    def arr(i, j, w):
        B[i][j] = w
        B[j][i] = -w
    arr(0, 1, k); arr(2, 0, k); arr(3, 0, k); arr(1, 3, k); arr(3, 2, k - 1)
    return tuple(tuple(r) for r in B)


def C4(k):
    """Oriented 4-cycle with weights k, k, k, k-1 (vertex order 0->1->2->3->0)."""
    B = [[0] * 4 for _ in range(4)]
    for (i, j), w in zip(((0, 1), (1, 2), (2, 3), (3, 0)), (k, k, k, k - 1)):
        B[i][j] = w
        B[j][i] = -w
    return tuple(tuple(r) for r in B)


def persistence(levels, g):
    order = sorted(levels, key=lambda x: (levels[x], x))
    parent, birth, pairs = {}, {}, []
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for x in order:
        parent[x] = x
        birth[x] = levels[x]
        for y in g[x]:
            if y in parent:
                ra, rb = find(x), find(y)
                if ra != rb:
                    if birth[ra] < birth[rb]:
                        ra, rb = rb, ra
                    if birth[ra] < levels[x]:
                        pairs.append((birth[ra], levels[x]))
                    parent[ra] = rb
    return sorted(pairs)


def minimax(levels, g, src):
    import heapq
    h = {src: levels[src]}
    pq = [(levels[src], src)]
    done = set()
    while pq:
        d, x = heapq.heappop(pq)
        if x in done:
            continue
        done.add(x)
        for y in g[x]:
            nd = max(d, levels[y])
            if nd < h.get(y, 1 << 200):
                h[y] = nd
                heapq.heappush(pq, (nd, y))
    return h


def explore_region(root, m, radius, cap=60000):
    """Labelled BFS from the root(s) of the far region of the exit (root, m), never crossing a bridge.
    Returns (least level, least weight, number of labelled quivers)."""
    roots = {root}
    lp = L.light_pairs(root)
    if lp and abs(root[lp[0][0]][lp[0][1]]) == 1:
        k, kp = lp[0]
        X = root
        for v in (k, kp, k, kp, k):
            X = L.mut(X, v)
        roots.add(X)
    seen = set(roots)
    front = list(roots)
    lo_lev, lo_w = min(L.level(x) for x in roots), min(L.weight(x) for x in roots)
    for _ in range(radius):
        nxt = []
        for z in front:
            for v in range(4):
                if z in roots and v == m:
                    continue
                y = L.mut(z, v)
                if y in seen:
                    continue
                seen.add(y)
                lo_lev = min(lo_lev, L.level(y))
                lo_w = min(lo_w, L.weight(y))
                if L.level(y) < 10 ** 40 and len(seen) < cap:
                    nxt.append(y)
        front = nxt
    return lo_lev, lo_w, len(seen)


def sublevel_component(B, bound, cap=200000):
    s = L.key(B)
    rep = {s: B}
    todo = [s]
    while todo:
        x = todo.pop()
        for v in range(4):
            Y = L.mut(rep[x], v)
            if L.level(Y) <= bound:
                y = L.key(Y)
                if y not in rep:
                    rep[y] = Y
                    todo.append(y)
                    if len(rep) > cap:
                        return rep, False
    return rep, True


def main():
    kmin, kmax = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    bad = Counter()
    for k in range(kmin, kmax + 1):
        Gk = G(k)
        res = L.core_of(Gk, cap=10000)
        if res is None:
            print(f"k={k}: V' search did not stop")
            bad["V' not finite"] += 1
            continue
        rep, adj, ups, sinks = res
        nV = len(rep)
        if len(sinks) != 1:
            bad["not exactly one sink SCC"] += 1
        K = sinks[0]
        levs = sorted(L.level(rep[x]) for x in K)
        names = {L.key(Gk): "G", L.key(L.neg(Gk)): "-G", L.key(C4(k)): "C",
                 L.key(L.mut(Gk, 1)): "mu1G", L.key(L.neg(L.mut(Gk, 1))): "-mu1G",
                 L.key(L.mut(Gk, 2)): "mu2G", L.key(L.neg(L.mut(Gk, 2))): "-mu2G"}
        expect = set(names)
        if len(expect) != 7:
            bad["the seven named quivers are not pairwise non-isomorphic"] += 1
        if set(K) != expect:
            bad["core differs from the seven named quivers"] += 1
        if levs != sorted([k, k, k, k * k - k, k * k - k, k * k, k * k]):
            bad["core levels differ"] += 1
        # every quiver of V' is in the core? (V' = core)
        if nV != len(K):
            bad["V' larger than the core"] += 1
        # self-opposite quivers in the core
        selfopp = sorted(names[x] for x in K if L.key(L.neg(rep[x])) == x)
        if selfopp != ["C"]:
            bad["self-opposite core quivers are not exactly C"] += 1
        # edges inside the core (all mutation edges, up to relabelling)
        g = {x: set() for x in K}
        for x in K:
            for v in range(4):
                y = L.key(L.mut(rep[x], v))
                if y in K and y != x:
                    g[x].add(y)
                    g[y].add(x)
        edges = sorted({tuple(sorted((names[x], names[y]))) for x in K for y in g[x]})
        want = sorted({tuple(sorted(e)) for e in (("G", "mu1G"), ("mu1G", "C"), ("C", "-mu1G"), ("-mu1G", "-G"),
                                                  ("G", "mu2G"), ("mu2G", "C"), ("C", "-mu2G"), ("-mu2G", "-G"))})
        if edges != want:
            bad["core graph is not the two paths G - mu_iG - C - (-mu_iG) - (-G)"] += 1
        # exits in the core, balanced edges, direct shape test
        n_exit_core = sum(1 for x in K if L.exit_vertices(rep[x]))
        balanced = sum(1 for x in K for m in L.exit_vertices(rep[x])
                       if L.key(L.mut(rep[x], m)) in K and m in L.exit_vertices(L.mut(rep[x], m)))
        shape = sum(1 for x in K if L.in_far_region_shape(rep[x], "none"))
        if balanced:
            bad["balanced edge in the core"] += 1
        # strict up-exit steps from the core
        U = [(x, m, Y) for x, m, Y in ups if x in K]
        kinds = Counter("fork" if L.fork_returns(Y) == {m} else "pre-fork" for x, m, Y in U)
        rootlev = sorted((("F" if L.fork_returns(Y) == {m} else "P"), L.level(Y), L.weight(Y)) for x, m, Y in U)
        if len(U) != 12 or kinds != Counter({"fork": 4, "pre-fork": 8}):
            bad["not 4 fork + 8 pre-fork exits"] += 1
        flev = sorted(l for t, l, w in rootlev if t == "F")
        if flev != sorted([k * k, k * k, k * k - k, k * k - k]):
            bad["fork root levels differ from k^2, k^2-k"] += 1
        pw = [w for t, l, w in rootlev if t == "P"]
        if not all(w > 6 * (k * k - k) - 6 for w in pw):
            bad["pre-fork root weight <= 6(k^2-k)-6"] += 1
        plev = sorted(l for t, l, w in rootlev if t == "P")
        if min(plev) < k ** 3 - k * k - k:
            bad["pre-fork root level below k^3-k^2-k"] += 1
        # pre-fork roots: light pair value
        qv = sorted(abs(Y[a][b]) for x, m, Y in U if L.fork_returns(Y) != {m} for a, b in L.light_pairs(Y))
        # extended core and persistence
        levels = {x: L.level(rep[x]) for x in K}
        gg = {x: set(g[x]) for x in K}
        for x, m, Y in U:
            y = L.key(Y)
            if y in K:
                bad["root inside the core"] += 1
            if y not in levels:
                levels[y] = L.level(Y)
                gg[y] = set()
            gg[y].add(x)
            gg[x].add(y)
        pairs = persistence(levels, gg)
        if pairs != [(k, k * k - k), (k, k * k - k)]:
            bad["pockets differ from two (k, k^2-k)"] += 1
        # f(G_k, w) for k <= w < k^2 - k: join heights between the three level-k quivers inside the core
        low = [x for x in K if levels[x] == k]
        jh = max(minimax(levels, gg, a)[b] for a in low for b in low)
        if jh != k * k - k:
            bad["join of the level-k quivers is not k^2-k"] += 1
        # far regions explored to a radius (numerical): least level and weight met
        rad = 5 if k <= 12 else 3
        reg_lo = min(explore_region(Y, m, rad)[0] for x, m, Y in U)
        if reg_lo < k * k - k:
            bad["a far region contains a quiver below k^2 - k"] += 1
        # brute force for small k: component of G_k at levels < k^2-k, and at <= k^2-k
        extra = ""
        if k <= 9:
            c1, ok1 = sublevel_component(Gk, k * k - k - 1)
            c2, ok2 = sublevel_component(Gk, k * k - k)
            n2 = Counter(L.level(Y) for Y in c2.values())
            if not (ok1 and set(c1) == {L.key(Gk)}):
                bad["G_k not alone below k^2-k in its component"] += 1
            if L.key(L.neg(Gk)) not in c2 or L.key(C4(k)) not in c2:
                bad["G_k not joined to -G_k, C_k at k^2-k"] += 1
            extra = f"; brute force: component of G_k below k^2-k = {len(c1)} quiver, at <= k^2-k: {len(c2)} quivers {dict(sorted(n2.items()))}"
        print(f"k={k}: V' {nV}, sink SCCs {len(sinks)}, core {len(K)} levels {levs}; self-opposite {selfopp}; "
              f"core exits {n_exit_core}, balanced {balanced}, fork/pre-fork/wing/tip shapes in core {shape}; "
              f"up-exits {len(U)} {dict(kinds)}; fork roots lev {flev}; pre-fork roots lev {plev} "
              f"min weight {min(pw)} > {6 * (k * k - k) - 6}; pre-fork light-pair values {qv}; pockets {pairs}; "
              f"join of level-k quivers {jh}; least level in far regions (radius {rad}) {reg_lo}{extra}", flush=True)
    print("failures:", dict(bad) if bad else "none")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
