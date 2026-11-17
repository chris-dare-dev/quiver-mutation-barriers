"""Review of note 20, section 6.3: 4-vertex parts of stored members of K(a).

K(a) is grown breadth-first from the seeds = quivers of the first half of the route of
Theorem 18.4 below H(a) (labelled, x = vertex 0, built by own integer mutation), through
non-forks of height < H(a).  Each class keeps the first labelled representative found, and its
"x" is vertex 0 of that representative.  A member is "stored" in the sense of note 20 section 2.2
if it is a seed, has height <= a+1, or does not have exactly two of its five mutations in K(a).
For the stored members the 4-vertex part (vertex 0 deleted) is classified: fork or not, on the
cycle W_m(0..m) or not, and distance from the cycle in the 4-vertex search of section 6.2.

Usage: python -I review23_n20_ends.py a [a ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
from review23_n20_lib import mutate, height, is_fork, H_of, W_matrix  # noqa: E402
from review23_n20_checks import build_route, canon_fast, canon4  # noqa: E402


def forkless4(a, cap):
    m = 2 * a + 1
    seeds = {}
    for j in range(0, m + 1):
        W = W_matrix(m, j)
        seeds[canon4(W)] = W
    dist = {k: 0 for k in seeds}
    rep = dict(seeds)
    frontier = list(seeds)
    d = 0
    while frontier:
        d += 1
        nxt = []
        for key in frontier:
            X = rep[key]
            for k in range(4):
                Y = mutate(X, k)
                if height(Y) >= cap or is_fork(Y):
                    continue
                ky = canon4(Y)
                if ky not in dist:
                    dist[ky] = d
                    rep[ky] = Y
                    nxt.append(ky)
        frontier = nxt
    return dist, set(seeds)


def part4(B):
    return [[B[i][j] for j in range(1, 5)] for i in range(1, 5)]


def run(a):
    H = H_of(a)
    w = a + 1
    recs, _, _ = build_route(a)
    rep = {}
    order = []
    seedkeys = set()
    for (turns, pos, B, f) in recs:
        if height(B) >= H:
            continue
        assert not is_fork(B)
        k = canon_fast(B)
        seedkeys.add(k)
        if k not in rep:
            rep[k] = B
            order.append(k)
    i = 0
    deg = {}
    while i < len(order):
        key = order[i]
        i += 1
        X = rep[key]
        dcount = 0
        for v in range(5):
            Y = mutate(X, v)
            if height(Y) >= H or is_fork(Y):
                continue
            dcount += 1
            ky = canon_fast(Y)
            if ky not in rep:
                rep[ky] = Y
                order.append(ky)
        deg[key] = dcount
    stored = [k for k in order if k in seedkeys or height(rep[k]) <= w or deg[k] != 2]
    dist4, cyc = forkless4(a, H)
    parts = {}
    for k in stored:
        P = part4(rep[k])
        if is_fork(P):
            continue
        c4 = canon4(P)
        if c4 in cyc:
            continue
        parts.setdefault(c4, 0)
        parts[c4] += 1
    in_first = [c for c in parts if c in dist4]
    far = max((dist4[c] for c in in_first), default=0)
    print('a=%d H=%d: core %d classes, %d seeds, stored (sense of note 20) %d; 4-vertex parts of stored members, '
          'not forks, off W_m(0..m): %d; of these in the 4-vertex search of section 6.2: %d, largest distance %d; '
          'stored members over such parts: %d; 4-vertex search: %d off the cycle'
          % (a, H, len(order), len(seedkeys), len(stored), len(parts), len(in_first), far, sum(parts.values()),
             len([c for c in dist4 if c not in cyc])))
    sys.stdout.flush()


if __name__ == '__main__':
    for tok in sys.argv[1:]:
        run(int(tok))
