#!/usr/bin/env python3
"""smoke.py -- a few headline numbers of the article, recomputed from the definition in a few minutes.

Standard library only; it imports nothing from experiments/ or from the other scripts of verify/, and it reads
no stored result.  Everything is recomputed from three definitions: quiver mutation, relabelling of the
vertices, and the height (largest absolute entry).  The expected values are those printed in the article and
in the paper; a line ends with "ok" when the recomputed value equals the expected one.

A quiver on n vertices is the tuple of the entries b_ij, i < j, of its exchange matrix, row by row;
b_ij > 0 means b_ij arrows i -> j.  Quivers are compared up to relabelling of the vertices.

  barrier(Q)    the least H such that -Q can be reached from Q through quivers of height <= H, by a search
                that always expands a quiver of least height (so it is exact, with no pruning)
  below(Q, H)   every quiver reachable from Q through quivers of height < H, up to relabelling
  shortest(Q,H) the least number of mutations from Q to -Q through quivers of height <= H

Usage:  python3 -I verify/smoke.py            about 15 seconds, under 100 MB
        python3 -I verify/smoke.py --full     adds Q_7 (barrier 1,242), R_b to b = 20 and Conjecture 5.5 at heights 5 and 6; about 2.5 minutes, under 500 MB
"""
import heapq
import itertools
import sys
import time


class Rank:
    def __init__(self, n):
        self.n = n
        self.pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        idx = {p: a for a, p in enumerate(self.pairs)}
        self.idx = idx

        def at(i, j):                                     # (index, sign) of the entry b_ij
            return (idx[(i, j)], 1) if i < j else (idx[(j, i)], -1)
        self.mut = []
        for k in range(n):
            flip = [a for a, (i, j) in enumerate(self.pairs) if k in (i, j)]
            rest = [(a,) + at(i, k) + at(k, j) for a, (i, j) in enumerate(self.pairs) if k not in (i, j)]
            self.mut.append((flip, rest))
        self.perms = [tuple(at(p[i], p[j]) for (i, j) in self.pairs) for p in itertools.permutations(range(n))]

    def mutate(self, q, k):
        """Fomin-Zelevinsky mutation at k: b_ij -> -b_ij if k is i or j, else b_ij + (|b_ik| b_kj + b_ik |b_kj|) / 2."""
        out = list(q)
        flip, rest = self.mut[k]
        for a in flip:
            out[a] = -q[a]
        for a, i1, s1, i2, s2 in rest:
            x, y = s1 * q[i1], s2 * q[i2]                 # b_ik, b_kj
            if x > 0 and y > 0:
                out[a] = q[a] + x * y
            elif x < 0 and y < 0:
                out[a] = q[a] - x * y
        return tuple(out)

    def canon(self, q):
        return min(tuple(s * q[i] for i, s in p) for p in self.perms)

    def neighbours(self, q):
        return [self.canon(self.mutate(q, k)) for k in range(self.n)]

    def barrier(self, q):
        """(least H joining q to -q, number of quivers popped)."""
        start, target = self.canon(q), self.canon(neg(q))
        heap, seen, level, popped = [(ht(start), start)], {start}, 0, 0
        while heap:
            h, x = heapq.heappop(heap)
            level = max(level, h)
            popped += 1
            if x == target:
                return level, popped
            for y in self.neighbours(x):
                if y not in seen:
                    seen.add(y)
                    heapq.heappush(heap, (ht(y), y))
        return None, popped

    def below(self, q, H):
        start = self.canon(q)
        seen, todo = {start}, [start]
        while todo:
            x = todo.pop()
            for y in self.neighbours(x):
                if ht(y) < H and y not in seen:
                    seen.add(y)
                    todo.append(y)
        return seen

    def shortest(self, q, H):
        """(least number of mutations from q to -q through heights <= H, heights along one such route)."""
        start, target = self.canon(q), self.canon(neg(q))
        prev, layer = {start: None}, [start]
        while layer and target not in prev:
            nxt = []
            for x in layer:
                for y in self.neighbours(x):
                    if ht(y) <= H and y not in prev:
                        prev[y] = x
                        nxt.append(y)
            layer = nxt
        if target not in prev:
            return None, []
        route, x = [], target
        while x is not None:
            route.append(ht(x))
            x = prev[x]
        return len(route) - 1, route[::-1]


def ht(q):
    return max(abs(e) for e in q)


def neg(q):
    return tuple(-e for e in q)


def acyclic4(q, R):
    arrows = {(i, j) if q[a] > 0 else (j, i) for a, (i, j) in enumerate(R.pairs) if q[a]}
    rem = set(range(4))
    while rem:
        src = [v for v in rem if not any((u, v) in arrows for u in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


# ------------------------------------------------------------------ the families, as the article defines them
def G(k):                      # Section 5: rows (0, k, -k, -k), (-k, 0, 0, k), (k, 0, 0, -(k-1)), (k, -k, k-1, 0)
    return (k, -k, -k, 0, k, -(k - 1))


def R_(b):                     # Section 7
    return (-b, -b, b - 1, -2, b - 2, -b)


def Qt(t):                     # Section 7, the second four-vertex family; vertices p, q, c1, c in the order below
    # two arrows q -> p; t(t-1) arrows p -> c1; t^2 arrows c1 -> q; t^2 arrows p -> c; t^2 - 1 arrows q -> c; 2t arrows c -> c1
    return from_arrows(4, {("q", "p"): 2, ("p", "c1"): t * (t - 1), ("c1", "q"): t * t, ("p", "c"): t * t,
                           ("q", "c"): t * t - 1, ("c", "c1"): 2 * t}, ["p", "q", "c1", "c"])


def Pplus(t):                  # Section 9: Q_t on p, q, c1, c and the fifth vertex x
    return from_arrows(5, {("q", "p"): 2, ("p", "c1"): t * (t - 1), ("c1", "q"): t * t, ("p", "c"): t * t,
                           ("q", "c"): t * t - 1, ("c", "c1"): 2 * t, ("x", "p"): 1, ("q", "x"): t * t - 1,
                           ("x", "c"): t * t, ("c1", "x"): t * (t - 1)}, ["x", "p", "q", "c1", "c"])


def Qa(a):                     # Section 10, as a tuple
    return (-(a - 3), a - 2, a + 1, -(a + 1), -(a + 1), -a, 2, -2, -a, -(a + 1))


def from_arrows(n, arrows, names):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    q = [0] * len(pairs)
    for (u, v), w in arrows.items():
        i, j = names.index(u), names.index(v)
        if i < j:
            q[pairs.index((i, j))] = w
        else:
            q[pairs.index((j, i))] = -w
    return tuple(q)


def H_R(b):
    return 2 * b * b - 3 * b - 3


def H_Qt(t):
    return 2 * t ** 4 - t ** 3 - t * t + 2 * t


def H_P(t):
    return 2 * t ** 5 - t ** 4 + t * t - 1


def H_Qa(a):
    return 4 * a ** 3 - 3 * a * a + ((5 * a - 1) // 2 if a % 2 else (3 * a - 4) // 2)


FAIL = []


def check(label, got, want):
    ok = got == want
    if not ok:
        FAIL.append(label)
    print("%-78s %-28s %s" % (label, got, "ok" if ok else "MISMATCH, expected %s" % (want,)))
    sys.stdout.flush()


def main():
    full = "--full" in sys.argv
    t0 = time.time()
    R4, R5 = Rank(4), Rank(5)

    print("== R_8 = (-8, -8, 7, -2, 6, -8), the running example (article, opening and Section 7)")
    r8 = R_(8)
    check("height of R_8", ht(r8), 8)
    check("heights of the four mutations of R_8", [ht(R4.mutate(r8, k)) for k in range(4)], [62, 24, 57, 48])
    check("barrier between R_8 and -R_8", R4.barrier(r8)[0], 101)
    reg = R4.below(r8, 101)
    check("quivers reachable from R_8 below height 101, up to relabelling", len(reg), 35)
    check("  of these, of height <= 8", sum(1 for x in reg if ht(x) <= 8), 1)
    check("  -R_8 among them", R4.canon(neg(r8)) in reg, False)
    n, route = R4.shortest(r8, 101)
    check("fewest mutations from R_8 to -R_8 at bound 101", n, 37)
    check("  quivers at height 101 on that route", route.count(101), 28)
    check("  heights on the climb", route[:5], [8, 24, 40, 56, 56])

    print("== G_k, the first barrier (Theorem 5.1)")
    g8 = G(8)
    hs, x = [8], g8
    for k in (1, 2, 3, 0):
        x = R4.mutate(x, k)
        hs.append(ht(x))
    check("heights along mu_1, mu_2, mu_3, mu_0 from G_8", hs, [8, 56, 8, 56, 8])
    check("  the route ends at -G_8 up to relabelling", R4.canon(x) == R4.canon(neg(g8)), True)
    check("barrier between G_k and -G_k, k = 3..12", [R4.barrier(G(k))[0] for k in range(3, 13)], [k * (k - 1) for k in range(3, 13)])
    check("quivers reachable from G_8 below height 56", len(R4.below(g8, 56)), 1)

    print("== R_b (Theorem 7.2: even b >= 6; odd b is computational) and Q_t (Section 7)")
    bs = list(range(5, 21 if full else 15))
    check("barrier of R_b, b = %d..%d, against 2b^2 - 3b - 3" % (bs[0], bs[-1]), [R4.barrier(R_(b))[0] for b in bs], [H_R(b) for b in bs])
    ev = [b for b in bs if b % 2 == 0 and b >= 6]
    check("fewest mutations at the barrier, even b, against b(b-1)/2 + b + 1", [R4.shortest(R_(b), H_R(b))[0] for b in ev], [b * (b - 1) // 2 + b + 1 for b in ev])
    check("barrier of Q_t, t = 3, 4, against 2t^4 - t^3 - t^2 + 2t", [R4.barrier(Qt(t))[0] for t in (3, 4)], [H_Qt(3), H_Qt(4)])

    print("== P+_t on five vertices (Theorem 9.1)")
    for t in (2, 3):
        p = Pplus(t)
        check("height of P+_%d" % t, ht(p), t * t)
        check("barrier of P+_%d against 2t^5 - t^4 + t^2 - 1" % t, R5.barrier(p)[0], H_P(t))
        reg = R5.below(p, H_P(t))
        check("  quivers of height <= t^2 reachable below the barrier", sum(1 for x in reg if ht(x) <= t * t), 1)
        n, route = R5.shortest(p, H_P(t))
        check("  fewest mutations at the barrier, against 4t^3 - 2t^2 + 4", n, 4 * t ** 3 - 2 * t * t + 4)
        check("  quivers at the top height on that route", route.count(H_P(t)), 1)

    print("== Q_a on five vertices (Theorem 10.1, Proposition 10.2)")
    for a in (2, 3, 4, 7) if full else (2, 3, 4):
        q = Qa(a)
        check("height of Q_%d" % a, ht(q), a + 1)
        b, popped = R5.barrier(q)
        check("barrier of Q_%d against H(a)" % a, b, H_Qa(a))
        if a <= 3:
            n, route = R5.shortest(q, H_Qa(a))
            check("  fewest mutations at the barrier, against (2a+2)(4a^2 - a + 6)", n, (2 * a + 2) * (4 * a * a - a + 6))
    check("H(7), the top rung of the ladder at height 8", H_Qa(7), 1242)
    check("length of the route of Theorem 10.1 at a = 7 and a = 12", [(2 * a + 2) * (4 * a * a - a + 6) for a in (7, 12)], [3120, 14820])

    print("== Conjecture 5.5 at small height (Proposition 12.1): quivers of height exactly h, up to relabelling,")
    print("   and those that reach an acyclic quiver through quivers of height <= h")
    want = {1: (41, 39), 2: (653, 521), 3: (4317, 2916), 4: (17353, 10415), 5: (51841, 28523), 6: (127541, 66393)}
    for h in range(1, 7 if full else 5):
        reps = set()
        for q in itertools.product(range(-h, h + 1), repeat=6):
            if any(q):
                reps.add(R4.canon(q))
        good = set()                                      # quivers of height <= h that reach an acyclic one within h
        todo = [x for x in reps if acyclic4(x, R4)]
        good.update(todo)
        while todo:
            x = todo.pop()
            for y in R4.neighbours(x):
                if ht(y) <= h and y not in good:
                    good.add(y)
                    todo.append(y)
        exact = [x for x in reps if ht(x) == h]
        check("h = %d: (quivers, reach an acyclic quiver within h)" % h, (len(exact), sum(1 for x in exact if x in good)), want[h])

    print()
    print("%d mismatches; %.0f s" % (len(FAIL), time.time() - t0))
    if FAIL:
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
