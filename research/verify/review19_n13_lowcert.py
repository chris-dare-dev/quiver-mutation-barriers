"""
review19_n13_lowcert.py -- certify EVERY failing orbit of a given height (from review19_n13_lowh.py's
~/.cache/qmb-review19/fail_h{h}.txt) with the independent library: own bottleneck search of the class,
stopping at an acyclic quiver (counterexample), a tri / vortex / Lemma-2.4 quiver, or the Cor. 5.2 bound.
Also, for h <= 2, the classification of paper Theorem 6.2 (connected / disconnected, mutation-acyclic /
mutation-cyclic, the zero quiver included).
Usage: python -I review19_n13_lowcert.py --h 3 [--workers 6]
"""
import argparse
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

CACHE = os.path.expanduser("~/.cache/qmb-review19")


def work(t):
    r = L.my_resolve(t, budget=300_000)
    return t, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h", type=int, required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    t0 = time.time()
    rows = [tuple(int(x) for x in line.split()) for line in open(os.path.join(CACHE, f"fail_h{a.h}.txt"))]
    assert all(L.ht(t) == a.h for t in rows) and len(set(L.canon(t) for t in rows)) == len(rows)
    # each listed orbit must really fail: its component inside its own height has no acyclic quiver
    with Pool(a.workers) as pool:
        res = pool.map(work, rows, chunksize=64)
    tally = Counter()
    tally_conn = Counter()
    Kmax = 0
    Kmax_rows = []
    bad = []
    for t, r in res:
        tally[(r[0], r[1])] += 1
        tally_conn[(L.is_connected(t), r[0])] += 1
        if r[0] != "cyclic":
            bad.append((t, r))
        if r[1] == "cor52":
            if r[2] > Kmax:
                Kmax, Kmax_rows = r[2], [t]
            elif r[2] == Kmax:
                Kmax_rows.append(t)
    print(f"height {a.h}: {len(rows)} failing orbits; own search verdicts: {dict(tally)}")
    print(f"  (connected?, verdict): {dict(tally_conn)}")
    print(f"  not certified cyclic: {len(bad)} {bad[:5]}")
    print(f"  largest Cor 5.2 bound K among own cor52 stops: {Kmax} (h^3+h^2+5 = {a.h ** 3 + a.h ** 2 + 5}); "
          f"attained by {len(Kmax_rows)} orbits, e.g. {Kmax_rows[:4]}")
    if a.h <= 2:
        # Theorem 6.2: all quivers of height <= 2 (incl. the zero quiver and height 1), up to relabelling
        import itertools
        orbits = {}
        for t in itertools.product(range(-2, 3), repeat=6):
            orbits.setdefault(L.canon(t), None)
        failing = set()
        for hh in (1, 2):
            failing |= {tuple(int(x) for x in line.split()) for line in open(os.path.join(CACHE, f"fail_h{hh}.txt"))}
        verdict = {}
        for c in orbits:
            if c in failing:
                v = L.my_resolve(c)[0]
            else:
                found, _, _ = L.bfs_within(c, max(L.ht(c), 0) if L.ht(c) > 0 else 0)
                v = "acyclic" if found is not None else "??"
            verdict[c] = v
        tab = Counter((L.is_connected(c), verdict[c]) for c in orbits)
        print(f"  Theorem 6.2 table (all {len(orbits)} orbits with entries in [-2,2], zero quiver included): "
              f"connected acyclic {tab[(True, 'acyclic')]}, connected cyclic {tab[(True, 'cyclic')]}, "
              f"disconnected acyclic {tab[(False, 'acyclic')]}, disconnected cyclic {tab[(False, 'cyclic')]}, "
              f"other {sum(v for k, v in tab.items() if k[1] not in ('acyclic', 'cyclic'))}")
        # paper's Theorem 6.2 (ii): certificates within <= 2 mutations through height-<= 2... the paper allows any
        # height for the 2 mutations; count which orbits get a tri / vortex / l24 within <= 2 mutations
        cyc = [c for c in orbits if verdict[c] == "cyclic"]
        # Markov exclusion (paper, before Lemma 2.6): connected, has a proper class, and for every proper class
        # no connected acyclic A in a topological ordering has (M_A, p_A^2) = (M, p^2).  Table of the pairs
        # realised by connected acyclic tuples (a..f) >= 0 read in the topological order 1<2<3<4.
        MMAX = 400
        pairs = set()
        import math
        r = int(math.isqrt(MMAX))
        for tt in itertools.product(range(r + 1), repeat=6):
            if sum(x * x for x in tt) > MMAX:
                continue
            if not L.is_connected(tt):
                continue
            pairs.add((L.markov_value(tt, (0, 1, 2, 3)), L.pfaffian(tt) ** 2))
        def markov_excluded(x):
            if not L.is_connected(x):
                return False
            pm = L.proper_markov(x)
            if not pm:
                return False
            p2 = L.pfaffian(x) ** 2
            for m, _ in pm:
                if m > MMAX:
                    return False          # outside the table: treat as not excluded (conservative)
                if (m, p2) in pairs:
                    return False
            return True
        def cert2(x):
            if L.cyclic_triangle(x):
                return "a:tri"
            if L.is_vortex(x):
                return "b:vortex"
            if markov_excluded(x):
                return "c:markov-excluded"
            return None
        def short_cert(c):
            if c == L.canon((-2, 1, 1, -1, -1, -1)):
                return ("torus", 0)
            frontier = [c]
            for depth in range(3):
                found = [cert2(x) for x in frontier if cert2(x) is not None]
                if found:
                    return (min(found), depth)
                frontier = [L.mutate(x, k) for x in frontier for k in range(4)]
            return (None, None)
        sc = Counter()
        dep = Counter()
        for c in cyc:
            if not L.is_connected(c):
                sc[("disconnected",) + short_cert(c)[:1]] += 1
                continue
            k, d = short_cert(c)
            sc[k] += 1
            dep[d] += 1
        print(f"  Theorem 6.2 (ii) shortest certificate within <= 2 mutations, preferring (a) tri, (b) vortex, "
              f"(c) Markov-excluded: {dict(sc)}; lengths (connected, torus incl.): {dict(dep)}")
    print(f"  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
