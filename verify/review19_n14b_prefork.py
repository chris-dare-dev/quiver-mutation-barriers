"""Review 2 of note 14 (n14b), item 3: do levels drop inside far regions rooted at pre-forks?
Independent code (review19_n14b_lib).  Roots: pre-forks that are not forks, (a) hanging from the cores
recomputed by review19_n14b_cores.py (strict up-exit steps out of a core), (b) met on random walks from
census bottom quivers.  For a root P with return vertex m and light pair {k, k'}: the second root is
P~ = mu_k mu_k' mu_k mu_k' mu_k (P) when |p_kk'| = 1 (checked to be P with k, k' exchanged), and P itself
when p_kk' = 0.  The region is explored as a labelled breadth-first ball of radius R from the roots,
never mutating a root at m (the bridges).  Measured:
  foot     the ball contains mu_m(P) or mu_m(P~)
  below    a quiver of the ball has level < level(P)
  edge     an edge z -> y with dist(y) = dist(z) + 1 and level(y) < level(z)  (a step away from the root
           lowers the level; all such edges, not only a BFS tree)
  minimax  a quiver y of the ball with no path from the roots inside the ball through levels <= level(y)
  lighter  a quiver other than the roots with weight <= weight(P)
  direct   a quiver of the ball that passes the direct test (so is no fork, pre-fork, wing or tip)
Usage: python -I review19_n14b_prefork.py SEED N_CORE N_WALK RADIUS"""
import gzip
import heapq
import json
import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L

ROOTS = os.path.expanduser("~/.cache/qmb-review19/n14b_prefork_roots.jsonl.gz")
os.makedirs(os.path.dirname(ROOTS), exist_ok=True)


def light_pair(t):
    lp = [(i, j) for (i, j) in L.PAIRS if abs(L.mat(t)[i][j]) < 2]
    return lp


def region(a):
    P, m, R, src = a
    P = tuple(P)
    st = Counter()
    lp = light_pair(P)
    if len(lp) != 1 or L.is_fork(P) or m not in L.exits(P):
        st["root is not a pre-fork with one light pair (skipped)"] += 1
        return src, None, st
    k, kp = lp[0]
    bkk = L.mat(P)[k][kp]
    kind = "kk' not joined" if bkk == 0 else "kk' one arrow"
    roots = {P}
    if bkk != 0:
        y = P
        for v in (k, kp, k, kp, k):
            y = L.mut(y, v)
        p = list(range(4))
        p[k], p[kp] = kp, k
        if y != L.relabel(P, p):
            st["second root is not the swap of k, k'"] += 1
        roots.add(y)
    feet = {L.mut(r, m) for r in roots}
    dist = {r: 0 for r in roots}
    frontier = list(roots)
    edges = []
    for d in range(R):
        nxt = []
        for z in frontier:
            for v in range(4):
                if z in roots and v == m:
                    continue
                y = L.mut(z, v)
                if y not in dist:
                    dist[y] = d + 1
                    nxt.append(y)
                edges.append((z, y))
        frontier = nxt
    l0, w0 = L.level(P), L.weight(P)
    lev = {y: L.level(y) for y in dist}
    st["regions"] += 1
    st[f"regions, {kind}"] += 1
    st["labelled quivers"] += len(dist)
    st["edges"] += len(edges)
    flags = Counter()
    if set(dist) & feet:
        flags["foot"] += 1
    nb = sum(1 for y in dist if lev[y] < l0)
    if nb:
        flags["below"] += nb
    ne = sum(1 for z, y in edges if dist[y] == dist[z] + 1 and lev[y] < lev[z])
    if ne:
        flags["edge"] += ne
    st["edges away from the root"] += sum(1 for z, y in edges if dist[y] == dist[z] + 1)
    nl = sum(1 for y in dist if y not in roots and L.weight(y) <= w0)
    if nl:
        flags["lighter"] += nl
    nd = sum(1 for y in dist if L.no_far_region(y))
    if nd:
        flags["direct"] += nd
    # minimax path level from the roots inside the ball (undirected adjacency)
    adj = {}
    for z, y in edges:
        adj.setdefault(z, set()).add(y)
        adj.setdefault(y, set()).add(z)
    best = {r: lev[r] for r in roots}
    h = [(lev[r], r) for r in roots]
    heapq.heapify(h)
    while h:
        b, z = heapq.heappop(h)
        if b > best.get(z, b):
            continue
        for y in adj.get(z, ()):
            nb2 = max(b, lev[y])
            if nb2 < best.get(y, 10 ** 10000):
                best[y] = nb2
                heapq.heappush(h, (nb2, y))
    nm = sum(1 for y in dist if best[y] > max(lev[y], l0))
    if nm:
        flags["minimax"] += nm
    for f, v in flags.items():
        st[f"{kind}: regions with {f}"] += 1
        st[f"{kind}: quivers/edges with {f}"] += v
    example = None
    if flags:
        example = {"P": list(P), "m": m, "flags": dict(flags), "src": src}
    return src, example, st


def walk_roots(rng, qs, n):
    out = []
    tries = 0
    while len(out) < n and tries < 200 * n:
        tries += 1
        x = rng.choice(qs)
        for _ in range(rng.randint(1, 30)):
            m = rng.randrange(4)
            y = L.mut(x, m)
            if L.level(y) > 10 ** 15:
                break
            ey = L.exits(y)
            if m in ey and not L.is_fork(y) and m not in L.exits(x):
                out.append((y, m))
                break
            x = y
    return out


def main():
    seed, ncore, nwalk, R = (int(v) for v in sys.argv[1:5])
    rng = random.Random(seed)
    t0 = time.time()
    with gzip.open(ROOTS, "rt") as f:
        croots = [json.loads(l) for l in f if l.strip()]
    # stratify the core roots by the type of the pair k k'
    by = {0: [], 1: []}
    for r in croots:
        y = tuple(r["y"])
        lp = light_pair(y)
        if len(lp) == 1:
            by[abs(L.mat(y)[lp[0][0]][lp[0][1]])].append((y, r["m"]))
    jobs = []
    for key in (0, 1):
        for y, m in rng.sample(by[key], min(ncore // 2, len(by[key]))):
            jobs.append((y, m, R, "core"))
    from review19_n14b_cores import census
    qs = census()
    for y, m in walk_roots(rng, qs, nwalk):
        jobs.append((y, m, R, "walk"))
    print(f"core roots available: kk' not joined {len(by[0])}, one arrow {len(by[1])}; jobs {len(jobs)} radius {R} "
          f"({time.time() - t0:.0f}s)", flush=True)
    tot = {"core": Counter(), "walk": Counter()}
    ex = []
    with Pool(6) as pool:
        for src, example, st in pool.imap_unordered(region, jobs, chunksize=4):
            tot[src].update(st)
            if example and len(ex) < 10:
                ex.append(example)
    for src in ("core", "walk"):
        print(f"roots {src}:")
        for k in sorted(tot[src]):
            print(f"   {k}: {tot[src][k]}")
    for e in ex:
        print("   example:", e)
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
