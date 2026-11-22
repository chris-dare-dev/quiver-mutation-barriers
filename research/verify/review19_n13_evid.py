"""
review19_n13_evid.py -- the paper's evidence (i) for Conjecture 5.5 (arXiv 2610.36179, after Conj. 5.5):
"the mutation-cyclic ones [connected, height <= 3] are certified by a mutation-cyclic full triangle, a vortex or
a Markov exclusion within three mutations, except for the dreaded torus at height two and four quivers at height
three, which are certified by Corollary 5.2."  Recomputed with the independent library: for every connected
failing orbit of height 1..3 (from review19_n13_lowh.py), all mutation words of length <= 3 (no height limit)
are tried for (a) tri, (b) vortex, (c) Markov exclusion (connected, a proper class, and for every proper class
no connected acyclic A in a topological order with (M_A, p_A^2) = (M, p^2)).  The table of pairs (M_A, p_A^2) is
complete for M_A <= CAP; a class with M > CAP is treated as NOT excluded (conservative).
Usage: python -I review19_n13_evid.py [--cap 1500]
"""
import argparse
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

CACHE = os.path.expanduser("~/.cache/qmb-review19")


def acyclic_pairs(cap):
    """{M: set of p^2} over nonnegative tuples (a..f) (topological order 1<2<3<4), connected, M <= cap."""
    out = {}
    n = 0
    a = 0
    while a * a <= cap:
        b = 0
        while a * a + b * b <= cap:
            d = 0
            while True:
                s1 = a * a + b * b + d * d + a * b * d
                if s1 > cap:
                    break
                c = 0
                while True:
                    s2 = s1 + c * c
                    if s2 > cap:
                        break
                    e = 0
                    while True:
                        s3 = s2 + e * e + a * c * e
                        if s3 > cap:
                            break
                        f = 0
                        while True:
                            M = s3 + f * f + b * c * f + d * e * f + a * c * d * f
                            if M > cap:
                                break
                            t = (a, b, c, d, e, f)
                            n += 1
                            if L.is_connected(t):
                                out.setdefault(M, set()).add(L.pfaffian(t) ** 2)
                            f += 1
                        e += 1
                    c += 1
                d += 1
            b += 1
        a += 1
    return out, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=1500)
    a = ap.parse_args()
    t0 = time.time()
    table, n = acyclic_pairs(a.cap)
    print(f"table of connected acyclic (M, p^2) for M <= {a.cap}: {n} tuples, {sum(len(v) for v in table.values())} pairs "
          f"({time.time() - t0:.0f}s)", flush=True)
    assert (41, 225) in {(m, p) for m, s in table.items() for p in s}

    over_cap = Counter()

    def mexcl(x):
        if not L.is_connected(x):
            return False
        pm = L.proper_markov(x)
        if not pm:
            return False
        p2 = L.pfaffian(x) ** 2
        for m, _ in pm:
            if m > a.cap:
                over_cap["proper class with M above the table"] += 1
                return False
            if p2 in table.get(m, ()):
                return False
        return True

    def cert(x):
        if L.cyclic_triangle(x):
            return "a"
        if L.is_vortex(x):
            return "b"
        if mexcl(x):
            return "c"
        return None

    torus = L.canon((-2, 1, 1, -1, -1, -1))
    for h in (1, 2, 3):
        fails = [tuple(int(v) for v in line.split()) for line in open(os.path.join(CACHE, f"fail_h{h}.txt"))]
        conn = [t for t in fails if L.is_connected(t)]
        found = Counter()
        exceptions = []
        for t in conn:
            frontier = [t]
            got = None
            for depth in range(4):
                cs = [cert(x) for x in frontier]
                cs = [c for c in cs if c]
                if cs:
                    got = (min(cs), depth)
                    break
                frontier = [L.mutate(x, k) for x in frontier for k in range(4)]
            if got is None:
                exceptions.append(t)
            else:
                found[got] += 1
        print(f"height {h}: {len(conn)} connected failing orbits; certificate (type, mutations): {dict(sorted(found.items()))}; "
              f"no certificate within 3 mutations: {len(exceptions)}")
        for t in exceptions:
            r = L.my_resolve(t)
            print(f"   {t}{'  (dreaded torus)' if t == torus else ''}: own search {r[0]} {r[1]} K={r[2]}; "
                  f"bottleneck to Example 5.4 (or its reversal), cap 41: "
                  f"{L.bottleneck_to(t, (-3, -2, 2, 0, 3, -3), 41)}, {L.bottleneck_to(t, (3, 2, -2, 0, -3, 3), 41)}")
    print(f"over-cap events: {dict(over_cap)} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
