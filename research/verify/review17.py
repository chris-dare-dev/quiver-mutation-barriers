#!/usr/bin/env python
"""
review17.py -- independent checks of note 16 (the 5-vertex family P+_t and F(5, w) >= 2w^{5/2} - 11w^2).

Written for the review of note 16.  It imports none of np_corridor.py, np_corridor_prove.py, n4_doors.py.
Its own pieces, chosen to differ from the code under review:
  * integer mutation on upper-triangle tuples, with the rule written through [x]_+;
  * a canonical form by sorted rows (vertices ordered by their sorted row, ties broken by the least tuple),
    where np_barrier.c and np_corridor.py take the least tuple over all 120 relabellings;
  * a fork test that uses the tournament structure (acyclic = no oriented triangle);
  * polynomials in PARI (cypari2) for everything symbolic.

Commands
  selftest     the two integer kernels against each other, the canonical form against brute force
  route        Theorem 16.4 on integers: columns, heights, length, the identity at the top, non-isomorphism
  lemmas       Lemmas 16.1-16.3 on random quivers with 5 to 7 vertices
  forks        Lemma 15.4 and Lemma 15.5 on random forks and random reduced routes, 5 and 6 vertices
  plain        Theorem 16.5: the set reached from P+_t (or P_t) below H, no pruning, against the stored counts
  closure      the argument of section 4.1 on integers: the set reached below H+ without passing a fork higher than t^2
  pendant      P_t with a path hung from x, on 6 and 7 vertices: the search below H(t), no pruning
  star         the star quivers of section 5 on 5 to 7 vertices: the search below the height of the route, no pruning
  anatomy      that set split into the route, the backward line, the ends of the first line and the rest
  closedforms  the closed forms of the lines, as polynomial identities (PARI) and on integers
  singles      the fourteen single quivers as polynomials in t
  replay       every claim of np_corridor_prove.log re-certified with PARI, and the bookkeeping of "member"
  negctl       sixteen logs with one line changed and one with a line removed: replay must reject each
  instances    the members of the replay at the true parameters of t, against the search of `closure`
  corollary    Corollary 16.7: the inequality, the least constant, the exceptions to H+ > 2w^2

Vertices: x = 0, p = 1, q = 2, c1 = 3, c = 4.  A quiver is the tuple (b01, b02, b03, b04, b12, b13, b14, b23, b24, b34);
b_ij > 0 means b_ij arrows i -> j.  Run from experiments/ with python -I.
"""
import argparse
import ast
import itertools
import json
import os
import random
import re
import struct
import sys
import time
from collections import Counter, defaultdict, deque
from multiprocessing import Pool

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results
X, PV, QV, C1, C = 0, 1, 2, 3, 4
VNAMES = ["x", "p", "q", "c1", "c"]
VIDX = {n: i for i, n in enumerate(VNAMES)}


# ============================================================================= integer kernel on tuples
class Kernel:
    """Mutation, canonical form and fork test for n-vertex quivers stored as upper-triangle tuples."""

    def __init__(self, n):
        self.n = n
        self.pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
        self.m = len(self.pairs)
        self.pidx = {ab: k for k, ab in enumerate(self.pairs)}
        # loc[a][b] = (index, sign) with b_ab = sign * u[index]
        self.loc = [[None] * n for _ in range(n)]
        for (a, b), k in self.pidx.items():
            self.loc[a][b] = (k, 1)
            self.loc[b][a] = (k, -1)
        self.rows = [[self.loc[a][b] for b in range(n) if b != a] for a in range(n)]
        self.mut_tab = []
        for k in range(n):
            tab = []
            for (a, b) in self.pairs:
                if a != k and b != k:
                    ia, sa = self.loc[a][k]
                    ib, sb = self.loc[k][b]
                    tab.append((self.pidx[(a, b)], ia, sa, ib, sb))
            at = [self.pidx[ab] for ab in self.pairs if k in ab]
            self.mut_tab.append((tab, at))

    def ent(self, u, a, b):
        k, s = self.loc[a][b]
        return s * u[k]

    def mut(self, u, k):
        """b'_ab = b_ab + [b_ak]_+ [b_kb]_+ - [-b_ak]_+ [-b_kb]_+ away from k; the entries at k change sign."""
        tab, at = self.mut_tab[k]
        v = list(u)
        for ab, ia, sa, ib, sb in tab:
            x = u[ia] * sa
            y = u[ib] * sb
            if x > 0:
                if y > 0:
                    v[ab] += x * y
            elif x < 0 and y < 0:
                v[ab] -= x * y
        for ab in at:
            v[ab] = -u[ab]
        return tuple(v)

    def relabel(self, u, perm):
        """The quiver with new vertex a = old vertex perm[a]."""
        out = []
        for (a, b) in self.pairs:
            k, s = self.loc[perm[a]][perm[b]]
            out.append(s * u[k])
        return tuple(out)

    def canon(self, u):
        """Vertices ordered by their sorted rows; ties broken by the least resulting tuple."""
        sig = [tuple(sorted(s * u[k] for k, s in row)) for row in self.rows]
        order = sorted(range(self.n), key=sig.__getitem__)
        if all(sig[order[a]] != sig[order[a + 1]] for a in range(self.n - 1)):
            return self.relabel(u, order)
        groups = [list(g) for _, g in itertools.groupby(order, key=sig.__getitem__)]
        best = None
        for choice in itertools.product(*(itertools.permutations(g) for g in groups)):
            perm = [a for g in choice for a in g]
            c = self.relabel(u, perm)
            if best is None or c < best:
                best = c
        return best

    def canon_brute(self, u):
        return max(self.relabel(u, p) for p in itertools.permutations(range(self.n)))

    def neg(self, u):
        return tuple(-a for a in u)

    @staticmethod
    def ht(u):
        return max(max(u), -min(u))

    def fork_points(self, u):
        """All points of return, for Warkentin's definition (thesis, Def. 2.1): every entry has absolute value >= 2,
        the quiver is not acyclic, and there is r with b_ji > b_ir and b_ji > b_rj whenever i -> r -> j, such that
        the in-neighbours and the out-neighbours of r each span an acyclic quiver.  Every pair is joined, so the
        orientation is a tournament, and a tournament is acyclic exactly when it has no oriented triangle."""
        n = self.n
        if min(abs(a) for a in u) < 2:
            return []
        e = lambda a, b: self.ent(u, a, b)

        def has_triangle(vs):
            for a, b, c in itertools.combinations(vs, 3):
                s = (e(a, b) > 0) + (e(b, c) > 0) + (e(c, a) > 0)
                if s == 0 or s == 3:
                    return True
            return False
        if not has_triangle(range(n)):
            return []
        out = []
        for r in range(n):
            ins = [a for a in range(n) if a != r and e(a, r) > 0]
            outs = [a for a in range(n) if a != r and e(r, a) > 0]
            if has_triangle(ins) or has_triangle(outs):
                continue
            if all(e(j, i) > e(i, r) and e(j, i) > e(r, j) for i in ins for j in outs):
                out.append(r)
        return out

    def is_fork(self, u):
        return bool(self.fork_points(u))


K5 = Kernel(5)


# ============================================================================= integer matrices (a second kernel)
def to_matrix(u, n=5):
    M = [[0] * n for _ in range(n)]
    k = 0
    for a in range(n):
        for b in range(a + 1, n):
            M[a][b] = u[k]
            M[b][a] = -u[k]
            k += 1
    return M


def to_tuple(M):
    n = len(M)
    return tuple(M[a][b] for a in range(n) for b in range(a + 1, n))


def imut(M, k):
    n = len(M)
    out = [[0] * n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            if a == k or b == k:
                out[a][b] = -M[a][b]
            else:
                out[a][b] = M[a][b] + max(M[a][k], 0) * max(M[k][b], 0) - max(-M[a][k], 0) * max(-M[k][b], 0)
    return out


def swap_pq(M):
    s = [0, 2, 1] + list(range(3, len(M)))
    return [[M[s[a]][s[b]] for b in range(len(M))] for a in range(len(M))]


def istep(M):
    """A step on the pair: mutate at p, then exchange the names p and q."""
    return swap_pq(imut(M, PV))


def iback(M):
    return swap_pq(imut(M, QV))


# ============================================================================= the families, over any ring
def line_matrix(c1, c, x, s_c_c1, s_x_c, s_x_c1, zero=0):
    """Two arrows q -> p; the columns (b_pe, b_qe) of c1, c, x; then b_{c,c1}, b_{x,c}, b_{x,c1}."""
    M = [[zero] * 5 for _ in range(5)]

    def put(a, b, val):
        M[a][b] = val + zero
        M[b][a] = -val + zero
    put(QV, PV, 2)
    put(PV, C1, c1[0])
    put(QV, C1, c1[1])
    put(PV, C, c[0])
    put(QV, C, c[1])
    put(PV, X, x[0])
    put(QV, X, x[1])
    put(C, C1, s_c_c1)
    put(X, C, s_x_c)
    put(X, C1, s_x_c1)
    return M


def Nof(t):
    return 2 * t ** 3 - t * t - t


def Hplus(t):
    return 2 * t ** 5 - t ** 4 + t * t - 1


def F_K0(t, zero=0):
    return line_matrix((t * (t - 1), -t * t), (t * t, t * t - 1), (-1 + 0 * t, t * t - 1), 2 * t, t * t, -t * (t - 1), zero)


def F_K(t, j, zero=0):
    d = 2 * t * t - 1
    return line_matrix(((t - 1 - j) * t, -(t - j) * t), (t * t + j * d, -(t * t + (j - 1) * d)),
                       (j * t * t - 1, -((j - 1) * t * t - 1)), 2 * t, 2 * t * t, 0 * t, zero)


def F_L(t, i, r, zero=0):
    return line_matrix((i * t, -(i - 1) * t), (r, -(r + 1)),
                       ((t - 1 + i) * t * t - 1, -((t - 2 + i) * t * t - 1)), -2 * t, 2 * t * t, 0 * t, zero)


def F_M1(t, k, zero=0):
    N = Nof(t)
    return line_matrix(((k - 2) * t, -(k - 1) * t), (N + 1 + k, -(N + 2 + k)),
                       ((t - 1 - k) * t * t - 1, -((t - 2 - k) * t * t - 1)), t * N, 2 * t * t, t * ((t - 2) * t * t - 1), zero)


def F_M2(t, m, zero=0):
    N = Nof(t)
    return line_matrix(((t - 1 + m) * t, -(t + m) * t), (N + t + 2 + m, -(N + t + 3 + m)),
                       (m * t * t + 1, -((m + 1) * t * t + 1)), t * N, -(Hplus(t) - 2 * t * t), 0 * t, zero)


def Pplus(t):
    return to_tuple(F_K0(t))


def Pt_matrix(t):
    """P_t of note 16 section 3.1, from its table: p -> x (t^2), x -> q (t^2 - D), x -> c (2D), D = floor(t^2 / 2)."""
    D = t * t // 2
    return line_matrix((t * (t - 1), -t * t), (t * t, t * t - 1), (t * t, -(t * t - D)), 2 * t, 2 * D, 0)


def Hpt(t):
    return t * t + (2 * t ** 3 - t * t + 1) * (t * t // 2)


# ============================================================================= selftest
def cmd_selftest(args):
    rng = random.Random(53)
    bad = 0
    for n in (4, 5, 6):
        ker = Kernel(n)
        trials, sample = (4000, 20000) if n < 6 else (500, 3000)
        for _ in range(trials):
            u = tuple(rng.randint(-9, 9) for _ in range(ker.m))
            k = rng.randrange(n)
            bad += ker.mut(u, k) != to_tuple(imut(to_matrix(u, n), k))
            bad += ker.mut(ker.mut(u, k), k) != u
            p = list(range(n))
            rng.shuffle(p)
            v = ker.relabel(u, p)
            bad += ker.canon(u) != ker.canon(v)
            a1 = tuple(rng.randint(-1, 1) for _ in range(ker.m))
            a2 = tuple(rng.randint(-1, 1) for _ in range(ker.m))
            bad += (ker.canon(a1) == ker.canon(a2)) != (ker.canon_brute(a1) == ker.canon_brute(a2))
            bad += ker.canon_brute(ker.canon(u)) != ker.canon_brute(u)
            bad += ker.mut(v, p.index(k)) != ker.relabel(ker.mut(u, k), p)
        # canonical form is complete: on small entries, classes by canon = classes by brute force
        seen1, seen2 = set(), set()
        for _ in range(sample):
            u = tuple(rng.randint(-2, 2) for _ in range(ker.m))
            seen1.add(ker.canon(u))
            seen2.add(ker.canon_brute(u))
        bad += len(seen1) != len(seen2)
        print("n=%d: %d random mutations and relabellings, and %d classes of %d random small quivers: the two kernels and the two "
              "canonical forms agree: %s" % (n, trials, len(seen1), sample, bad == 0))
    # the sign certificate: nonneg(g) must say exactly whether every coefficient of g is >= 0, in any number of variables
    names = ["zt", "zi", "zr", "zj", "zv"]
    wrong = 0
    for trial in range(4000):
        nv = rng.randint(1, 4)
        vs = rng.sample(names, nv)
        coef = {}
        for _ in range(rng.randint(1, 8)):
            coef[tuple(rng.randint(0, 3) for _ in vs)] = rng.randint(-2, 9) if trial % 2 else rng.randint(0, 9)
        g = G(0)
        for e, c in coef.items():
            term = G(c)
            for name, k in zip(vs, e):
                term = term * G(name) ** k
            g = g + term
        wrong += nonneg(g) != all(c >= 0 for c in coef.values())
        wrong += iszero(g) != all(c == 0 for c in coef.values())
        pt = {name: rng.randint(0, 5) for name in vs}
        val = sum(c * __import__("math").prod(pt[name] ** k for name, k in zip(vs, e)) for e, c in coef.items())
        h = g
        for name in vs:
            h = h.subst(name, pt[name])
        wrong += int(h) != val
    print("PARI: nonneg, iszero and evaluation on 4000 random polynomials in 1 to 4 variables with known coefficients: %d wrong" % wrong)
    bad += wrong
    print("selftest %s" % ("ok" if bad == 0 else "FAILED (%d)" % bad))
    return 0 if bad == 0 else 1


# ============================================================================= Theorem 16.4 on integers
def cmd_route(args):
    ok_all = True
    for t in range(args.tmin, args.tmax + 1):
        N, H = Nof(t), Hplus(t)
        ok = True
        M = F_K0(t)
        start = to_tuple(M)
        ok &= start == (1, -(t * t - 1), -t * (t - 1), t * t, -2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t)
        ok &= K5.ht(start) == t * t
        heights = [K5.ht(start)]
        nmut = 0
        for j in range(1, t):                                  # K(1) .. K(t-1)
            M = istep(M)
            nmut += 1
            ok &= M == F_K(t, j)
            heights.append(K5.ht(to_tuple(M)))
        M = imut(M, C1)                                        # L(0)
        nmut += 1
        ok &= M == F_L(t, 0, N + 1)
        heights.append(K5.ht(to_tuple(M)))
        for i in range(1, N + 2):                              # L(1) .. L(N+1)
            M = istep(M)
            nmut += 1
            if i <= 50 or i >= N - 50 or i % 997 == 0:
                ok &= M == F_L(t, i, N + 1 - i)
            heights.append(K5.ht(to_tuple(M)))
        top = M
        up, turn = imut(top, PV), imut(top, C)
        ok &= turn == [[-a for a in row] for row in up]        # mu_c(T) = -mu_p(T), same labels
        ok &= K5.ht(to_tuple(up)) == H
        ok &= max(heights) == H - t * t                        # every quiver before the top
        ok &= sum(1 for a in to_tuple(up) if abs(a) == H) == 1
        total = 2 * nmut + 2                                   # up to T, mu_c, mu_p, and back
        ok &= total == 4 * t ** 3 - 2 * t * t + 4
        ok &= K5.canon(start) != K5.canon(K5.neg(start))
        inw = sorted(sum(max(K5.ent(start, a, b), 0) for a in range(5) if a != b) for b in range(5))
        outw = sorted(sum(max(K5.ent(start, b, a), 0) for a in range(5) if a != b) for b in range(5))
        ok &= outw == sorted([t * t + 1, 2 * t * t - t, 2 * t * t, 2 * t * t - t, 2 * t]) and 3 in inw and 3 not in outw
        # P_t (item 3 of the theorem)
        D = t * t // 2
        Mp = Pt_matrix(t)
        okp = to_tuple(Mp) == (-t * t, t * t - D, 0, 2 * D, -2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t)
        hp = [K5.ht(to_tuple(Mp))]
        cnt = 0
        for j in range(1, t):
            Mp = istep(Mp)
            cnt += 1
            hp.append(K5.ht(to_tuple(Mp)))
        Mp = imut(Mp, C1)
        cnt += 1
        hp.append(K5.ht(to_tuple(Mp)))
        for i in range(1, N + 2):
            Mp = istep(Mp)
            cnt += 1
            hp.append(K5.ht(to_tuple(Mp)))
        upp, turnp = imut(Mp, PV), imut(Mp, C)
        okp &= turnp == [[-a for a in row] for row in upp] and K5.ht(to_tuple(upp)) == Hpt(t)
        okp &= max(hp) == Hpt(t) - D and 2 * cnt + 2 == 4 * t ** 3 - 2 * t * t + 4
        s0 = to_tuple(Pt_matrix(t))
        okp &= K5.canon(s0) != K5.canon(K5.neg(s0)) and K5.ht(s0) == t * t
        ok_all &= ok and okp
        if t <= 8 or t % 8 == 0 or not (ok and okp):
            print("t=%d: P+_t route of %d mutations, heights before the top <= %d = H+ - t^2, top %d = H+, mu_c = -mu_p, "
                  "P+_t not isomorphic to -P+_t: %s | P_t: top %d = H, before the top <= H - D, same length: %s"
                  % (t, total, max(heights), H, ok, Hpt(t), okp), flush=True)
    print("# t = %d..%d: all checks %s" % (args.tmin, args.tmax, "ok" if ok_all else "FAILED"))
    return 0 if ok_all else 1


# ============================================================================= Lemmas 16.1-16.3 on random quivers
def cmd_lemmas(args):
    rng = random.Random(531)
    bad1 = bad2 = bad3 = 0
    n1 = n2 = n3 = 0
    for trial in range(args.trials):
        n = rng.choice((5, 6, 7))
        others = list(range(3, n)) + [0]
        # Lemma 16.1: any quiver with two arrows q -> p
        M = [[0] * n for _ in range(n)]

        def put(a, b, val):
            M[a][b] = val
            M[b][a] = -val
        for a in range(n):
            for b in range(a + 1, n):
                put(a, b, rng.randint(-6, 6))
        put(QV, PV, 2)
        A = {e: M[PV][e] for e in others}
        Bc = {e: M[QV][e] for e in others}
        S = {(e, f): M[e][f] for e in others for f in others if e != f}
        Y = imut(M, PV)
        n1 += 1
        good = Y[PV][QV] == 2
        for e in others:
            good &= Y[PV][e] == -A[e] and Y[QV][e] == Bc[e] + 2 * max(A[e], 0)
            for f in others:
                if e != f:
                    good &= Y[e][f] == S[(e, f)] + max(-A[e], 0) * max(A[f], 0) - max(A[e], 0) * max(-A[f], 0)
        Z = swap_pq(Y)
        good &= Z[QV][PV] == 2
        for e in others:
            col = (2 * A[e] + Bc[e], -A[e]) if A[e] >= 0 else (Bc[e], -A[e])
            good &= (Z[PV][e], Z[QV][e]) == col
        bad1 += not good
        # Lemma 16.2: y = (0, -eta), S_ey >= 0
        y = rng.choice(others)
        eta = rng.randint(1, 5)
        put(PV, y, 0)
        put(QV, y, -eta)
        for e in others:
            if e != y:
                put(e, y, rng.randint(0, 6))
        Y = imut(M, y)
        n2 += 1
        good = Y[PV][y] == 0 and Y[QV][y] == eta and Y[QV][PV] == 2
        for e in others:
            if e == y:
                continue
            good &= Y[PV][e] == M[PV][e] and Y[QV][e] == M[QV][e] - eta * M[e][y] and Y[e][y] == -M[e][y]
            for f in others:
                if f not in (e, y):
                    good &= Y[e][f] == M[e][f]
        bad2 += not good
        # Lemma 16.3: also A_e >= 0, eta * S_ey = 2 (A_e + B_e), S_ef = 0
        eta = rng.choice((1, 2))
        put(QV, y, -eta)
        for e in others:
            if e == y:
                continue
            a = rng.randint(0, 6)
            s = rng.randint(0, 5)
            put(e, y, 2 * s)                       # eta * 2s = 2 (A + B)  =>  A + B = eta * s
            put(PV, e, a)
            put(QV, e, eta * s - a)
            for f in others:
                if f not in (e, y):
                    put(e, f, 0)
        n3 += 1
        bad3 += imut(M, y) != [[-a for a in row] for row in imut(M, PV)]
    print("Lemma 16.1 (step): %d random quivers on 5 to 7 vertices, %d wrong" % (n1, bad1))
    print("Lemma 16.2 (turn): %d random quivers, %d wrong" % (n2, bad2))
    print("Lemma 16.3 (top):  %d random quivers, %d wrong" % (n3, bad3))
    return 0 if bad1 + bad2 + bad3 == 0 else 1


# ============================================================================= Lemmas 15.4 and 15.5
def random_fork(ker, rng, big):
    """A random fork, by construction: r, an acyclic order on each side, arrows from the out-side to the in-side
    that are heavier than the arrows at r they have to beat."""
    n = ker.n
    while True:
        r = rng.randrange(n)
        rest = [a for a in range(n) if a != r]
        rng.shuffle(rest)
        cut = rng.randint(1, n - 2)
        ins, outs = rest[:cut], rest[cut:]
        M = [[0] * n for _ in range(n)]

        def put(a, b, val):
            M[a][b] = val
            M[b][a] = -val
        for a in ins:
            put(a, r, rng.randint(2, big))
        for b in outs:
            put(r, b, rng.randint(2, big))
        for side in (ins, outs):
            for a, b in itertools.combinations(side, 2):
                put(a, b, rng.randint(2, big))
        for a in ins:
            for b in outs:
                put(b, a, max(M[a][r], M[r][b]) + rng.randint(1, big))
        u = to_tuple(M)
        if r in ker.fork_points(u):
            return u, r


def cmd_forks(args):
    rng = random.Random(524)
    worst = 0
    for n in (5, 6):
        ker = Kernel(n)
        bad = cnt = multi = 0
        for _ in range(args.forks):
            u, r = random_fork(ker, rng, rng.choice((3, 9, 40)))
            pts = ker.fork_points(u)
            multi += len(pts) > 1
            tot = sum(abs(a) for a in u)
            for k in range(n):
                if k in pts:
                    continue
                v = ker.mut(u, k)
                cnt += 1
                good = ker.fork_points(v) == [k]
                good &= all(abs(b) >= abs(a) for a, b in zip(u, v))
                good &= sum(abs(a) for a in v) > tot
                bad += not good
        print("Lemma 15.4, n=%d: %d forks built at random (%d with more than one point of return), %d mutations away from a "
              "point of return: %d are not forks with point of return the mutated vertex, with no entry smaller and larger total weight"
              % (n, args.forks, multi, cnt, bad))
        worst += bad
        # Lemma 15.5 on reduced routes
        bad = routes = forks_seen = high = 0
        for _ in range(args.routes):
            if rng.random() < 0.5:
                u = tuple(rng.randint(-4, 4) for _ in range(ker.m))
            else:
                u, _ = random_fork(ker, rng, 4)
                for _ in range(rng.randint(0, 2)):          # start near a fork, not always on one
                    u = ker.mut(u, rng.randrange(n))
            path = [u]
            last = -1
            for _ in range(rng.randint(2, 9)):
                k = rng.choice([a for a in range(n) if a != last])
                u = ker.mut(u, k)
                last = k
                if ker.ht(u) > 10 ** 30:
                    break
                path.append(u)
            routes += 1
            bound = max(ker.ht(path[0]), ker.ht(path[-1]))
            for v in path:
                if ker.is_fork(v):
                    forks_seen += 1
                    high += ker.ht(v) > bound
                    bad += ker.ht(v) > bound
        print("Lemma 15.5, n=%d: %d random reduced routes, %d forks on them, %d of them higher than both ends" % (n, routes, forks_seen, high))
        worst += bad
    return 0 if worst == 0 else 1


# ============================================================================= searches on integers
PACK = struct.Struct("<10q")


def reach(start, H, w, nofork):
    """The quivers of height < H, up to relabelling, that `start` reaches through quivers of height < H.
    With nofork, forks higher than w are not entered (Lemma 15.5: a reduced route between quivers of height <= w
    passes none).  Returns (number reached, number of height <= w, exits of height >= H, exits to high forks,
    forks of height <= w met)."""
    ker = K5
    c0 = ker.canon(start)
    seen = {PACK.pack(*c0)}
    todo = deque([c0])
    low = 1 if ker.ht(c0) <= w else 0
    high = forks = lowforks = 0
    while todo:
        u = todo.popleft()
        for k in range(5):
            v = ker.mut(u, k)
            h = ker.ht(v)
            if h >= H:
                high += 1
                continue
            if nofork and h > w and ker.is_fork(v):
                forks += 1
                continue
            c = ker.canon(v)
            key = PACK.pack(*c)
            if key in seen:
                continue
            seen.add(key)
            if h <= w:
                low += 1
                if nofork and ker.is_fork(v):
                    lowforks += 1
            todo.append(c)
    return len(seen), low, high, forks, lowforks


def _plain_task(arg):
    fam, t = arg
    t0 = time.time()
    if fam == "plus":
        start, H = Pplus(t), Hplus(t)
    else:
        start, H = to_tuple(Pt_matrix(t)), Hpt(t)
    n, low, high, _, _ = reach(start, H, t * t, False)
    return fam, t, H, n, low, high, time.time() - t0


def cmd_plain(args):
    stored = {}
    for fam, fn in (("plus", "np_corridor_family_plus.jsonl"), ("pt", "np_corridor_family.jsonl")):
        path = os.path.join(HERE, fn)
        if os.path.exists(path):
            for line in open(path):
                r = json.loads(line)
                stored[(fam, r["t"])] = r
    fams = ["plus", "pt"] if args.family == "both" else [args.family]
    tasks = [(fam, t) for fam in fams for t in range(args.tmin, args.tmax + 1)]
    tasks.sort(key=lambda a: -a[1])
    res = {}
    with Pool(args.workers) as pool:
        for fam, t, H, n, low, high, sec in pool.imap_unordered(_plain_task, tasks):
            res[(fam, t)] = (H, n, low, high, sec)
    bad = 0
    tot = Counter()
    for fam in fams:
        name = "P+_t" if fam == "plus" else "P_t"
        for t in range(args.tmin, args.tmax + 1):
            H, n, low, high, sec = res[(fam, t)]
            st = stored.get((fam, t))
            cmp_ = "no stored row"
            good = low == 1
            if st is not None:
                same = st["H"] == H and st["below_H"]["popped"] == n and st["below_H"]["capped"] == high
                good &= same
                cmp_ = "stored: H %d, reached %d, exits above %d: %s" % (st["H"], st["below_H"]["popped"], st["below_H"]["capped"],
                                                                         "same" if same else "DIFFERENT")
            bad += not good
            tot[fam] += n
            print("%s t=%d w=%d H=%d: %d quivers reached below H, %d of height <= w, %d mutations lead to height >= H | %s (%.1fs)"
                  % (name, t, t * t, H, n, low, high, cmp_, sec))
        print("# %s, t = %d..%d: %d quivers in all" % (name, args.tmin, args.tmax, tot[fam]))
    print("# failures: %d" % bad)
    return 0 if bad == 0 else 1


def _closure_task(t):
    t0 = time.time()
    n, low, high, forks, lowforks = reach(Pplus(t), Hplus(t), t * t, True)
    return t, n, low, high, forks, lowforks, time.time() - t0


def cmd_closure(args):
    ts = sorted(range(args.tmin, args.tmax + 1), reverse=True)
    res = {}
    with Pool(args.workers) as pool:
        for row in pool.imap_unordered(_closure_task, ts):
            res[row[0]] = row[1:]
    bad = 0
    for t in range(args.tmin, args.tmax + 1):
        n, low, high, forks, lowforks, sec = res[t]
        bad += low != 1
        print("t=%d w=%d H+=%d: %d quivers reached below H+ without entering a fork higher than w; of height <= w: %d; "
              "exits: %d to height >= H+, %d to forks higher than w; forks of height <= w met: %d (%.1fs)"
              % (t, t * t, Hplus(t), n, low, high, forks, lowforks, sec))
    ref = {2: 120, 3: 125, 4: 263, 5: 492, 6: 840, 7: 1331, 8: 1985, 9: 2827, 10: 3882, 11: 5174}   # note 16, section 4.2
    both = [t for t in sorted(res) if t in ref]
    diff = [t for t in both if res[t][0] != ref[t]]
    print("# note 16 gives the core for t = 2..11 (np_corridor_core_plus.log, np_corridor_prove.log); compared here for t = %s: "
          "%s" % (both, "all equal" if not diff else "DIFFERENT at %s" % diff))
    bad += len(diff)
    print("# failures (another quiver of height <= w): %d" % bad)
    return 0 if bad == 0 else 1


# ============================================================================= what the closure set consists of
def reach_set(start, H, w):
    """As reach(..., nofork=True), but returns the set of canonical forms."""
    ker = K5
    c0 = ker.canon(start)
    seen = {c0}
    todo = deque([c0])
    while todo:
        u = todo.popleft()
        for k in range(5):
            v = ker.mut(u, k)
            h = ker.ht(v)
            if h >= H or (h > w and ker.is_fork(v)):
                continue
            c = ker.canon(v)
            if c not in seen:
                seen.add(c)
                todo.append(c)
    return seen


def cmd_anatomy(args):
    for t in args.t:
        N, H, w = Nof(t), Hplus(t), t * t
        core = reach_set(Pplus(t), H, w)
        M = F_K0(t)
        route = {K5.canon(to_tuple(M))}
        for _ in range(1, t):
            M = istep(M)
            route.add(K5.canon(to_tuple(M)))
        M = imut(M, C1)
        L0 = M
        route.add(K5.canon(to_tuple(M)))
        for _ in range(N + 1):
            M = istep(M)
            route.add(K5.canon(to_tuple(M)))
        back = set()
        M = L0
        n = 0
        while True:                                   # the backward line, as long as it stays below H+
            M = iback(M)
            n += 1
            if K5.ht(to_tuple(M)) >= H:
                break
            back.add(K5.canon(to_tuple(M)))
        later = 0
        for _ in range(50):                           # it does not come back below H+
            M = iback(M)
            later += K5.ht(to_tuple(M)) < H
        fwd = set()                                   # K(t), K(t+1), ... and K(-1), K(-2), ... while below H+ and no high fork
        for start, step in ((F_K(t, t - 1), istep), (F_K0(t), iback)):
            M = start
            while True:
                M = step(M)
                u = to_tuple(M)
                if K5.ht(u) >= H or (K5.ht(u) > w and K5.is_fork(u)):
                    break
                fwd.add(K5.canon(u))
        lines = route | back | fwd
        print("t=%d: %d quivers below H+ = %d can be reached without entering a fork higher than %d: %d on the route "
              "(all of them: %s), %d on the backward line from L(0) (it leaves at step %d and stays out: %s), %d beyond the ends "
              "of the first line, %d others; all line quivers are in the set: %s"
              % (t, len(core), H, w, len(route & core), len(route) == t + N + 2 and route <= core, len(back & core), n, later == 0,
                 len(fwd & core), len(core - lines), lines <= core))
    return 0


# ============================================================================= 6 and 7 vertices (measured statements)
def reach_n(ker, start, bound, w):
    """All quivers of height <= bound, up to relabelling, reached through such quivers; no pruning.
    Returns (number, number of height <= w)."""
    c0 = ker.canon(start)
    seen = {c0}
    todo = deque([c0])
    low = 1 if ker.ht(c0) <= w else 0
    while todo:
        u = todo.popleft()
        for k in range(ker.n):
            v = ker.mut(u, k)
            h = ker.ht(v)
            if h > bound:
                continue
            c = ker.canon(v)
            if c not in seen:
                seen.add(c)
                low += h <= w
                todo.append(c)
    return len(seen), low


def with_tail(M, tail, sign):
    n = len(M) + tail
    B = [[0] * n for _ in range(n)]
    for a in range(len(M)):
        for b in range(len(M)):
            B[a][b] = M[a][b]
    prev = X
    for v in range(len(M), n):
        B[prev][v] = sign
        B[v][prev] = -sign
        prev = v
    return B


def cmd_pendant(args):
    """P_t with a path of weight-1 arrows hung from x (note 16, section 3.3, 'More vertices'), no pruning."""
    for n in args.n:
        ker = Kernel(n)
        for t in args.t:
            for sign in (1, -1):
                Q = with_tail(Pt_matrix(t), n - 5, sign)
                H, w = Hpt(t), t * t
                # the route never mutates x or the tail; it ends at the block reversed with the tail kept
                M = Q
                top = 0
                for _ in range(t - 1):
                    M = istep(M)
                    top = max(top, ker.ht(to_tuple(M)))
                M = imut(M, C1)
                for _ in range(Nof(t) + 1):
                    M = istep(M)
                    top = max(top, ker.ht(to_tuple(M)))
                up = imut(M, PV)
                target = with_tail([[-a for a in row] for row in Pt_matrix(t)], n - 5, sign)
                turn = imut(M, C)
                ident = all(turn[a][b] == -up[a][b] for a in range(5) for b in range(5))
                n0, _ = reach_n(ker, to_tuple(Q), w, w)
                n1, low1 = reach_n(ker, to_tuple(Q), H - 1, w)
                n2, low2 = reach_n(ker, to_tuple(Q), H, w)
                print("n=%d t=%d tail %+d: height %d; route below the top <= %d, top %d = H: %s; block identity at the top: %s; "
                      "plateau (reached at height <= w): %d quivers; below H: %d quivers, %d of height <= w; up to H: %d quivers, "
                      "%d of height <= w; the block-reversed quiver is not isomorphic to the start: %s"
                      % (n, t, sign, ker.ht(to_tuple(Q)), top, ker.ht(to_tuple(up)), ker.ht(to_tuple(up)) == H, ident, n0, n1, low1, n2, low2,
                         ker.canon(to_tuple(target)) != ker.canon(to_tuple(Q))), flush=True)
    return 0


def star_matrix(k, h, m, a0, D, Ax):
    """k equal counters z_1..z_k = (m h, -(m+1) h), each with 2h arrows c -> z_i; c = (a0, 2k h^2 - 1 - a0);
    x = (Ax, D - Ax) with 2D arrows x -> c (note 16, section 5).  Vertices x, p, q, z_1..z_k, c."""
    n = k + 4
    B = [[0] * n for _ in range(n)]

    def put(a, b, val):
        B[a][b] = val
        B[b][a] = -val
    c = n - 1
    put(QV, PV, 2)
    for z in range(3, 3 + k):
        put(PV, z, m * h)
        put(QV, z, -(m + 1) * h)
        put(c, z, 2 * h)
    put(PV, c, a0)
    put(QV, c, 2 * k * h * h - 1 - a0)
    put(PV, X, Ax)
    put(QV, X, D - Ax)
    put(X, c, 2 * D)
    return B


def cmd_star(args):
    for spec in args.spec:
        k, h, m, a0, D, Ax = [int(a) for a in spec.split(",")]
        Q = star_matrix(k, h, m, a0, D, Ax)
        n = k + 4
        ker = Kernel(n)
        w = ker.ht(to_tuple(Q))
        M = Q
        top = w
        for _ in range(m):
            M = istep(M)
            top = max(top, ker.ht(to_tuple(M)))
        for z in range(3, 3 + k):
            M = imut(M, z)
            top = max(top, ker.ht(to_tuple(M)))
        for _ in range(a0 + m * (2 * k * h * h - 1)):
            M = istep(M)
            top = max(top, ker.ht(to_tuple(M)))
        up, turn = imut(M, PV), imut(M, n - 1)
        H = max(top, ker.ht(to_tuple(up)))
        ident = turn == [[-a for a in row] for row in up]
        t0 = time.time()
        n1, low1 = reach_n(ker, to_tuple(Q), H - 1, w)
        n2, low2 = reach_n(ker, to_tuple(Q), H, w)
        print("k=%d n=%d (h, m, a0, D, Ax) = (%d, %d, %d, %d, %d): height %d, route of height H = %d (H/w^2.5 = %.2f), identity at the "
              "top: %s; no pruning: below H %d quivers, %d of height <= w; up to H %d quivers, %d of height <= w (%.0f s)"
              % (k, n, h, m, a0, D, Ax, w, H, H / w ** 2.5, ident, n1, low1, n2, low2, time.time() - t0), flush=True)
    return 0


# ============================================================================= PARI polynomials
_pari = None


def PARI():
    global _pari
    if _pari is None:
        import cypari2
        _pari = cypari2.Pari()
        _pari.allocatemem(512 * 10 ** 6, silent=True)
    return _pari


def G(a):
    return PARI()(a)


def iszero(g):
    return bool(G(g) == 0)


def nonneg(g):
    """g >= 0 wherever all its variables are >= 0: no coefficient of g is negative."""
    g = G(g)
    ty = g.type()
    if ty == "t_INT":
        return int(g) >= 0
    if ty == "t_POL":
        return all(nonneg(c) for c in g.Vec())
    raise TypeError(ty)


def wsign(g):
    """+1: g >= 0 on the region and g is not the zero polynomial; -1: g <= 0; 0: g = 0; None: not certified."""
    if iszero(g):
        return 0
    if nonneg(g):
        return 1
    if nonneg(-G(g)):
        return -1
    return None


def ssign(g):
    """+1: g >= 1 on the region; -1: g <= -1; None otherwise."""
    if nonneg(G(g) - 1):
        return 1
    if nonneg(-G(g) - 1):
        return -1
    return None


def smut(M, k):
    """mu_k of a matrix of polynomials, valid on the whole region; None if the sign of an entry at k is not certified."""
    pos, neg = {}, {}
    for a in range(5):
        if a == k:
            continue
        s = wsign(M[a][k])
        if s is None:
            return None
        pos[a] = M[a][k] if s > 0 else G(0)          # [b_ak]_+
        neg[a] = -M[a][k] if s < 0 else G(0)         # [-b_ak]_+
    out = [[G(0)] * 5 for _ in range(5)]
    for a in range(5):
        for b in range(5):
            if a == b:
                continue
            if a == k or b == k:
                out[a][b] = -M[a][b]
            else:                                    # b_kb = -b_bk, so [b_kb]_+ = neg[b] and [-b_kb]_+ = pos[b]
                out[a][b] = M[a][b] + pos[a] * neg[b] - neg[a] * pos[b]
    return out


def sstep(M):
    Y = smut(M, PV)
    return None if Y is None else swap_pq(Y)


def sback(M):
    Y = smut(M, QV)
    return None if Y is None else swap_pq(Y)


def sequal(A, B):
    return all(iszero(A[a][b] - B[a][b]) for a in range(5) for b in range(a + 1, 5))


PERMS5 = list(itertools.permutations(range(5)))


def siso(A, B):
    """A relabelling perm with A[perm[a]][perm[b]] = B[a][b] as polynomials, or None."""
    for p in PERMS5:
        if all(iszero(A[p[a]][p[b]] - B[a][b]) for a in range(5) for b in range(a + 1, 5)):
            return p
    return None


def sfork(M, r, W):
    """M is a fork with point of return r on the whole region, and has an entry above W.  Returns a reason on failure."""
    sg = {}
    for a in range(5):
        for b in range(a + 1, 5):
            s = ssign(M[a][b])
            if s is None:
                return "entry %s-%s has no strict sign" % (VNAMES[a], VNAMES[b])
            sg[(a, b)] = s
            sg[(b, a)] = -s
    wt = lambda a, b: sg[(a, b)] * M[a][b]             # |b_ab|
    arrow = lambda a, b: sg[(a, b)] > 0                # a -> b
    for a in range(5):
        for b in range(a + 1, 5):
            if not nonneg(wt(a, b) - 2):
                return "entry %s-%s not >= 2" % (VNAMES[a], VNAMES[b])

    def has_triangle(vs):
        for a, b, c in itertools.combinations(vs, 3):
            s = arrow(a, b) + arrow(b, c) + arrow(c, a)
            if s == 0 or s == 3:
                return True
        return False
    if not has_triangle(range(5)):
        return "acyclic"
    ins = [a for a in range(5) if a != r and arrow(a, r)]
    outs = [a for a in range(5) if a != r and arrow(r, a)]
    if has_triangle(ins) or has_triangle(outs):
        return "a side of the point of return is not acyclic"
    for i in ins:
        for j in outs:
            if not arrow(j, i):
                return "no arrow %s -> %s" % (VNAMES[j], VNAMES[i])
            if not (nonneg(wt(j, i) - wt(i, r) - 1) and nonneg(wt(j, i) - wt(r, j) - 1)):
                return "inequality at %s -> r -> %s not certified" % (VNAMES[i], VNAMES[j])
    if not any(nonneg(wt(a, b) - W - 1) for a in range(5) for b in range(a + 1, 5)):
        return "no entry certified above t^2"
    return None


# ============================================================================= charts, boxes and members
# A chart has coordinates; a box gives each coordinate as ('eq', c) or ('ge', c).  A point of a box is written with
# one fresh variable z<coord> >= 0 for each 'ge' coordinate, so that a box is the orthant of its fresh variables.
CHARTS = {"T": ("t",), "K": ("j", "v"), "L": ("t", "i", "r"), "Ltop": ("t", "i"), "M1": ("k", "u"), "M2": ("t", "m")}
SPOR = ["K0", "K(t-1)", "K(t)", "K(t+1)", "K(t+2)", "K(-1)", "K(-2)", "L(0)", "L(1)", "L(-1)", "L(-2)", "M1(t-2)", "L(-(t-1))", "L(-t)"]
LINE_BASES = {"K(j), 1<=j<=t-2": "K", "L(i), 2<=i<=N": "L", "L(N+1)": "Ltop", "M1(k), 3<=k<=t-3": "M1", "M2(m), m>=0": "M2"}
CHART_OF = dict({s: "T" for s in SPOR}, **LINE_BASES)
T0 = 8


def box_point(chart, box):
    pt = {}
    for cname in CHARTS[chart]:
        kind, c = box[cname]
        pt[cname] = G(c) if kind == "eq" else G(c) + G("z" + cname)
    if chart == "K":
        pt["t"] = pt["j"] + pt["v"] + 1
    elif chart == "M1":
        pt["t"] = pt["k"] + pt["u"] + 2
    elif chart == "Ltop":
        pt["r"] = G(0)
    return pt


def int_points(chart, box, cmax):
    """The integer points of a box with every coordinate cut off at cmax.  Sets given by conditions x = c and x >= c
    with all c < cmax cannot tell a coordinate x > cmax from x = cmax, so these points decide every inclusion."""
    axes = []
    for cname in CHARTS[chart]:
        kind, c = box[cname]
        axes.append([c] if kind == "eq" else list(range(c, cmax + 1)))
    return itertools.product(*axes)


def in_box(chart, box, point):
    for cname, val in zip(CHARTS[chart], point):
        kind, c = box[cname]
        if (kind == "eq" and val != c) or (kind == "ge" and val < c):
            return False
    return True


def H_of(chart, pt):
    t = pt["t"]
    if chart in ("L", "Ltop"):                     # r stands for N + 1 - i; there H+ = (t + i + r) t^2 - 1
        return (t + pt["i"] + pt["r"]) * t * t - 1
    return Hplus(t)


_spor_cache = {}


def spor_matrix(name, t):
    """The fourteen single quivers, by symbolic steps from the closed forms, at a value of t (a polynomial or an integer)."""
    key = (name, str(t))
    if key in _spor_cache:
        return _spor_cache[key]
    z = G(0)
    N = Nof(t)
    if name == "K0":
        M = F_K0(t, z)
    elif name == "K(t-1)":
        M = F_K(t, t - 1, z)
    elif name in ("K(t)", "K(t+1)", "K(t+2)"):
        M = sstep(spor_matrix({"K(t)": "K(t-1)", "K(t+1)": "K(t)", "K(t+2)": "K(t+1)"}[name], t))
    elif name in ("K(-1)", "K(-2)"):
        M = sback(spor_matrix({"K(-1)": "K0", "K(-2)": "K(-1)"}[name], t))
    elif name == "L(0)":
        M = F_L(t, 0 * t, N + 1, z)
    elif name == "L(1)":
        M = F_L(t, 0 * t + 1, N, z)
    elif name in ("L(-1)", "L(-2)"):
        M = sback(spor_matrix({"L(-1)": "L(0)", "L(-2)": "L(-1)"}[name], t))
    elif name == "M1(t-2)":
        M = F_M1(t, t - 2, z)
    elif name in ("L(-(t-1))", "L(-t)"):
        M = sback(spor_matrix({"L(-(t-1))": "M1(t-2)", "L(-t)": "L(-(t-1))"}[name], t))
    else:
        raise KeyError(name)
    if M is None:
        raise ValueError("signs not certified on the way to %s at t = %s" % (name, t))
    _spor_cache[key] = M
    return M


def base_matrix(base, pt):
    z = G(0)
    ch = CHART_OF[base]
    if ch == "T":
        return spor_matrix(base, pt["t"])
    if ch == "K":
        return F_K(pt["t"], pt["j"], z)
    if ch in ("L", "Ltop"):
        return F_L(pt["t"], pt["i"], pt["r"], z)
    if ch == "M1":
        return F_M1(pt["t"], pt["k"], z)
    return F_M2(pt["t"], pt["m"], z)


def member_matrix(base, word, pt):
    M = base_matrix(base, pt)
    for k in word:
        M = smut(M, k)
        if M is None:
            return None
    return M


def parse_name(name):
    word = []
    while name.startswith("mu_"):
        head, name = name.split(" ", 1)
        word.append(VIDX[head[3:]])
    word.reverse()                                  # "mu_c1 mu_x B" is mu_c1(mu_x(B)): mutate at x first
    slices = [(a, int(b)) for a, b in re.findall(r" \[(\w+)=(-?\d+)\]", name)]
    base = re.sub(r" \[\w+=-?\d+\]", "", name).strip()
    if base not in CHART_OF:
        raise ValueError("unknown base %r" % base)
    return base, tuple(word), slices


def make_box(chart, slices, dom):
    cons = {}
    for var, val in slices:
        if var in cons:
            raise ValueError("variable sliced twice")
        cons[var] = ("eq", val)
    for var, lb in dom.items():
        if var in cons:
            raise ValueError("variable both sliced and free")
        cons[var] = ("ge", lb)
    if chart == "Ltop":
        if cons.pop("r", ("eq", 0)) != ("eq", 0):
            raise ValueError("L(N+1) with r != 0")
    if chart in ("K", "M1"):
        a, b, c = ("j", "v", 1) if chart == "K" else ("k", "u", 2)
        if "t" in cons:                             # a slice that np_corridor_prove.py rewrote in t
            other = [z for z in (a, b) if z in cons]
            if len(other) != 1 or cons[other[0]][0] != "eq":
                raise ValueError("cannot place %r in the chart %s" % (cons, chart))
            free = b if other[0] == a else a
            kind, val = cons.pop("t")
            cons[free] = (kind, val - cons[other[0]][1] - c)
    if set(cons) != set(CHARTS[chart]):
        raise ValueError("box %r does not fit the chart %s" % (cons, chart))
    return cons


def line_boxes():
    """The members that are given, not derived: fourteen single quivers and the five lines, for t >= T0."""
    out = {}
    for s in SPOR:
        out[(s, ())] = [{"t": ("ge", T0)}]
    # K(j), 1 <= j <= t-2, t = j + v + 1 >= 8: the six quarter-planes of the certificate
    out[("K(j), 1<=j<=t-2", ())] = [{"j": ("ge", a), "v": ("ge", T0 - 1 - a)} for a in range(1, T0 - 1)]
    out[("L(i), 2<=i<=N", ())] = [{"t": ("ge", T0), "i": ("ge", 2), "r": ("ge", 1)}]
    out[("L(N+1)", ())] = [{"t": ("ge", T0), "i": ("ge", 2)}]
    out[("M1(k), 3<=k<=t-3", ())] = [{"k": ("ge", a), "u": ("ge", T0 - 2 - a)} for a in range(3, T0 - 2)]
    out[("M2(m), m>=0", ())] = [{"t": ("ge", T0), "m": ("ge", 0)}]
    return out


def covered(chart, boxes, cover, extra=()):
    """Every integer point of every box of `boxes` lies in a box of `cover`.  Returns the first point that does not."""
    consts = [c for bx in list(boxes) + list(cover) + list(extra) for _, c in bx.values()]
    cmax = max(consts) + 1
    for bx in boxes:
        for pnt in int_points(chart, bx, cmax):
            if not any(in_box(chart, cb, pnt) for cb in cover):
                return pnt
    return None


LOG_RE = re.compile(r"^exit (\w+)\s+of (.*?)\s+on (\{[^}]*\})\s+ok\s*(.*?)\s*$")


def read_claims(path):
    claims = []
    other = []
    for ln, line in enumerate(open(path), 1):
        line = line.rstrip("\n")
        m = LOG_RE.match(line)
        if m:
            base, word, slices = parse_name(m.group(2))
            dom = ast.literal_eval(m.group(3))
            chart = CHART_OF[base]
            claims.append({"ln": ln, "vtx": VIDX[m.group(1)], "name": m.group(2), "base": base, "word": word,
                           "chart": chart, "box": make_box(chart, slices, dom), "verdict": m.group(4)})
        else:
            other.append((ln, line))
    return claims, other


def range_ok(lo, val, hi):
    return nonneg(val - lo) and (hi is None or nonneg(hi - val))


def resolve_target(target, cl, pt, members):
    """The quiver that a verdict "member <target>" names at the point pt of the claim cl, with the reason why it is a
    member there.  Returns (matrix, reason) or raises ValueError."""
    z = G(0)
    t = pt["t"]
    N = Nof(t)
    plain = cl["word"] == ()
    ch = cl["chart"]
    # ---- the neighbours on a line
    if target in ("K(j+1)", "K(j-1)"):
        if not (plain and ch == "K"):
            raise ValueError("shift on a non-line member")
        j2 = pt["j"] + (1 if target == "K(j+1)" else -1)
        if not range_ok(1, j2, t - 1):
            raise ValueError("index outside 1..t-1")
        return F_K(t, j2, z), "K(j'), 1 <= j' <= t-1 (the formula at j' = t-1 is K(t-1) by definition)"
    if target in ("M1(k+1)", "M1(k-1)"):
        if not (plain and ch == "M1"):
            raise ValueError("shift on a non-line member")
        k2 = pt["k"] + (1 if target == "M1(k+1)" else -1)
        if not range_ok(2, k2, t - 2):
            raise ValueError("index outside 2..t-2")
        return F_M1(t, k2, z), "M1(k'), 2 <= k' <= t-2 (the formula at k' = 2 is L(-2), identity I8; at t-2 it is M1(t-2))"
    if target in ("M2(m+1)", "M2(m-1)"):
        if not (plain and ch == "M2"):
            raise ValueError("shift on a non-line member")
        m2 = pt["m"] + (1 if target == "M2(m+1)" else -1)
        if not range_ok(-1, m2, None):
            raise ValueError("index below -1")
        return F_M2(t, m2, z), "M2(m'), m' >= -1 (the formula at m' = -1 is L(-t), identity I9)"
    if target == "L(i+1)":
        if not (plain and ch == "L"):
            raise ValueError("shift on a non-line member")
        if not (nonneg(pt["r"] - 1) and nonneg(pt["i"] - 0)):
            raise ValueError("needs r >= 1")
        return F_L(t, pt["i"] + 1, pt["r"] - 1, z), "L(i+1) with r-1 >= 0; at the true points i+1 <= N+1"
    if target == "L(i-1)":
        if not (plain and ch == "L"):
            raise ValueError("shift on a non-line member")
        if not nonneg(pt["i"] - 2):
            raise ValueError("needs i >= 2")
        return F_L(t, pt["i"] - 1, pt["r"] + 1, z), "L(i-1) with i-1 >= 1; at the true points r+1 = N+1-(i-1), and L(1) is the formula at i = 1"
    if target == "L(i-1) with {'r': '0'}":
        if not (plain and ch == "Ltop"):
            raise ValueError("shift on a non-line member")
        if not nonneg(pt["i"] - 2):
            raise ValueError("needs i >= 2")
        return F_L(t, pt["i"] - 1, G(1), z), "L(N) = the formula at (i-1, r = 1); at the true point i = N+1"
    # ---- single quivers and instances of the lines at a fixed distance from an end
    if target in SPOR:
        return spor_matrix(target, t), "single quiver %s" % target
    m = re.match(r"^(K|L|M1|M2)\((t-)?(\d+)\)$", target)
    if m:
        fam, rel, c = m.group(1), bool(m.group(2)), int(m.group(3))
        idx = (t - c) if rel else (G(c) + 0 * t)
        if fam == "K":
            if not range_ok(1, idx, t - 1):
                raise ValueError("K index outside 1..t-1")
            return F_K(t, idx, z), "K(j'), 1 <= j' <= t-1"
        if fam == "L":
            if not range_ok(0, idx, N + 1):
                raise ValueError("L index outside 0..N+1")
            return F_L(t, idx, N + 1 - idx, z), "L(i'), 0 <= i' <= N+1, r = N+1-i'"
        if fam == "M1":
            if not range_ok(2, idx, t - 2):
                raise ValueError("M1 index outside 2..t-2")
            return F_M1(t, idx, z), "M1(k'), 2 <= k' <= t-2"
        if not range_ok(-1, idx, None):
            raise ValueError("M2 index below -1")
        return F_M2(t, idx, z), "M2(m'), m' >= -1"
    # ---- a derived member: the same word on the same base, at the point with the same t
    if target.startswith("mu_"):
        tbase, tword, tslices = parse_name(target)
        tch = CHART_OF[tbase]
        sl = dict(tslices)
        if tch == "T":
            tp = {"t": t}
        elif tch == "K":
            if "j" in sl:
                j2 = G(sl["j"]) + 0 * t
                v2 = t - 1 - j2
            elif "v" in sl:
                v2 = G(sl["v"]) + 0 * t
                j2 = t - 1 - v2
            elif ch == "K":
                j2, v2 = pt["j"], pt["v"]
            else:
                raise ValueError("no way to place the target on the K chart")
            tp = {"j": j2, "v": v2, "t": j2 + v2 + 1}
        elif tch == ch:
            tp = dict(pt)
        else:
            raise ValueError("target on another chart")
        for var, val in tslices:
            if not iszero(tp[var] - val):
                raise ValueError("the target's slice %s = %d does not hold at this point" % (var, val))
        home = None
        for bx in members.get((tbase, tword), []):
            good = True
            for cname in CHARTS[tch]:
                kind, c = bx[cname]
                good &= iszero(tp[cname] - c) if kind == "eq" else nonneg(tp[cname] - c)
            if good:
                home = bx
                break
        if home is None:
            raise ValueError("the point is in no box where %r was made a member" % target)
        M = member_matrix(tbase, tword, tp)
        if M is None:
            raise ValueError("signs of the target not certified")
        return M, "derived member (%s; word %s) on its box %s" % (tbase, [VNAMES[a] for a in tword], home)
    raise ValueError("verdict not understood: %r" % target)


def int_env(chart, box, rng, first):
    env = {}
    for cname in CHARTS[chart]:
        kind, c = box[cname]
        env[cname] = c if (kind == "eq" or first) else c + rng.randint(0, 6)
    if chart == "K":
        env["t"] = env["j"] + env["v"] + 1
    elif chart == "M1":
        env["t"] = env["k"] + env["u"] + 2
    elif chart == "Ltop":
        env["r"] = 0
    return env


def pari_eval(M, chart, box, env):
    """A matrix of polynomials in the fresh variables of a box, at the integer point env of that box."""
    vars_ = [(G("z" + c), env[c] - box[c][1]) for c in CHARTS[chart] if box[c][0] == "ge"]
    out = [[0] * 5 for _ in range(5)]
    for a in range(5):
        for b in range(5):
            g = G(M[a][b])
            for var, val in vars_:
                g = g.subst(var, val)
            out[a][b] = int(g)
    return out


def label(base, word):
    return "".join("mu_%s " % VNAMES[a] for a in reversed(word)) + base.split(",")[0]


def build_members(claims):
    """The given members and one box for every verdict "new member": (members, given keys, created)."""
    members = line_boxes()
    given = set(members)
    created = defaultdict(list)
    for cl in claims:
        if cl["verdict"] == "new member":
            created[(cl["base"], cl["word"] + (cl["vtx"],))].append(cl["box"])
    for key, boxes in created.items():
        if key in members:
            raise ValueError("a derived member with an empty word")
        members[key] = boxes
    return members, given, created


def cmd_replay(args):
    path = os.path.join(HERE, args.log)
    claims, other = read_claims(path)
    counts = Counter()
    fails = []

    def fail(cl, why):
        fails.append((cl["ln"], cl["name"], VNAMES[cl["vtx"]], cl["verdict"], why))

    print("# %s: %d exit claims read, %d other lines" % (args.log, len(claims), len(other)))
    # ---- the members: the given ones, and one box for every verdict "new member"
    members, given, created = build_members(claims)
    nmem = sum(len(b) for b in members.values())
    kinds = sorted({k for k in members if k[1]}, key=lambda k: (SPOR + list(LINE_BASES)).index(k[0]) * 100 + len(k[1]))
    print("# members: %d given boxes (14 single quivers, 5 lines) and %d boxes of derived members; %d boxes in all"
          % (sum(len(members[k]) for k in given), sum(len(b) for b in created.values()), nmem))
    print("# kinds of derived members (%d): %s" % (len(kinds), "; ".join(label(b, w) for b, w in kinds)))

    # ---- (A) every claim
    table = defaultdict(lambda: defaultdict(set))
    rng = random.Random(53)
    numeric = 0
    t_start = time.time()
    for cl in claims:
        ch, box, vtx = cl["chart"], cl["box"], cl["vtx"]
        pt = box_point(ch, box)
        H = H_of(ch, pt)
        W = pt["t"] * pt["t"]
        try:
            M = member_matrix(cl["base"], cl["word"], pt)
        except ValueError as exc:
            fail(cl, str(exc))
            continue
        if M is None:
            fail(cl, "the member itself: signs not certified on this box")
            continue
        Mx = smut(M, vtx)
        if Mx is None:
            fail(cl, "signs at the mutated vertex not certified")
            continue
        vd = cl["verdict"]
        target = None
        if vd.startswith("height (entry "):
            a, b = (VIDX[s] for s in vd[len("height (entry "):-1].split("-"))
            s = wsign(Mx[a][b])
            if not (s and nonneg(s * Mx[a][b] - H)):
                fail(cl, "|entry| - H+ >= 0 not certified")
                continue
            counts["height"] += 1
            table[(cl["base"], cl["word"])][vtx].add("height")
        elif vd.startswith("fork, point of return "):
            r = VIDX[vd.split()[-1]]
            why = sfork(Mx, r, W)
            if why:
                fail(cl, "fork: " + why)
                continue
            counts["fork"] += 1
            table[(cl["base"], cl["word"])][vtx].add("fork at %s" % VNAMES[r])
        elif vd == "new member":
            counts["new member"] += 1
            table[(cl["base"], cl["word"])][vtx].add(label(cl["base"], cl["word"] + (vtx,)))
        elif vd.startswith("member "):
            try:
                target, reason = resolve_target(vd[len("member "):], cl, pt, members)
            except ValueError as exc:
                fail(cl, "member: %s" % exc)
                continue
            if siso(Mx, target) is None:
                fail(cl, "member: not equal to the target up to relabelling")
                continue
            counts["member"] += 1
            counts["member: " + reason.split(" on its box")[0].split(" (")[0].split(";")[0]] += 1
            tg = vd[len("member "):]
            if tg.startswith("mu_"):
                tb, tw, _ = parse_name(tg)
                tg = label(tb, tw)
            table[(cl["base"], cl["word"])][vtx].add(tg.split(" with ")[0])
        else:
            fail(cl, "verdict not understood")
            continue
        # the same verdict on integers, with the integer kernel: the corner of the box and two random points
        for trial in range(3):
            env = int_env(ch, box, rng, trial == 0)
            if ch == "L" and trial == 2:               # a true point of the L chart when the box has one
                tt, ii = env["t"], env["i"]
                rr = Nof(tt) + 1 - ii
                if in_box(ch, box, (tt, ii, rr)):
                    env["r"] = rr
            u = K5.mut(to_tuple(pari_eval(M, ch, box, env)), vtx)
            Hn = env["t"] ** 2 * (env["t"] + env["i"] + env["r"]) - 1 if ch in ("L", "Ltop") else Hplus(env["t"])
            numeric += 1
            if u != to_tuple(pari_eval(Mx, ch, box, env)):
                fail(cl, "integer mutation differs from the symbolic one at %s" % env)
            elif vd.startswith("height") and K5.ht(u) < Hn:
                fail(cl, "integer check: height %d < %d at %s" % (K5.ht(u), Hn, env))
            elif vd.startswith("fork") and not (r in K5.fork_points(u) and K5.ht(u) > env["t"] ** 2):
                fail(cl, "integer check: not a fork higher than t^2 at %s" % env)
            elif target is not None and K5.canon(u) != K5.canon(to_tuple(pari_eval(target, ch, box, env))):
                fail(cl, "integer check: not the target at %s" % env)
    print("# (A) claims re-certified with PARI: %s; failed: %d  (%.0f s; %d integer evaluations agree)"
          % (dict(sorted((k, v) for k, v in counts.items() if ":" not in k)), len(fails), time.time() - t_start, numeric - 0))
    for k in sorted(k for k in counts if ":" in k):
        print("#     %-70s %d" % (k, counts[k]))

    if not fails:
        print("#\n# The exits, by kind of member (every verdict that occurs on some box; 'back' is the vertex the member was made by):")
        order = SPOR + list(LINE_BASES)
        for key in sorted(table, key=lambda k: (len(k[1]), order.index(k[0]), k[1])):
            cells = []
            for vtx in range(5):
                if key[1] and vtx == key[1][-1]:
                    cells.append("back")
                else:
                    cells.append(" / ".join(sorted(table[key][vtx])) or "-")
            print("#   %-22s | %s" % (label(*key), " | ".join("%s: %s" % (VNAMES[a], c) for a, c in enumerate(cells))))
        print("#")
    # ---- (B) coverage: for every member box and every vertex but the one it was made by, the claims cover the box
    by_exit = defaultdict(list)
    for cl in claims:
        by_exit[(cl["base"], cl["word"], cl["vtx"])].append(cl["box"])
    holes = 0
    checked = 0
    for (base, word), boxes in members.items():
        ch = CHART_OF[base]
        for vtx in range(5):
            if word and vtx == word[-1]:
                continue
            checked += len(boxes)
            miss = covered(ch, boxes, by_exit.get((base, word, vtx), []))
            if miss is not None:
                holes += 1
                print("HOLE: exit %s of (%s, word %s) has no claim at the point %s of %s" % (VNAMES[vtx], base, word, miss, CHARTS[ch]))
    print("# (B) coverage: %d (member box, vertex) pairs; every integer point of each box is under a claim for that vertex: %s"
          % (checked, "yes" if holes == 0 else "NO, %d holes" % holes))
    # the given boxes cover the true parameters
    gaps = 0
    for t in range(T0, 60):
        gaps += any(not any(in_box("K", b, (j, t - 1 - j)) for b in members[("K(j), 1<=j<=t-2", ())]) for j in range(1, t - 1))
        gaps += any(not any(in_box("M1", b, (k, t - 2 - k)) for b in members[("M1(k), 3<=k<=t-3", ())]) for k in range(3, t - 2))
    print("# (B) the six boxes of K and the three of M1 contain every (j, t-1-j), 1 <= j <= t-2, and (k, t-2-k), 3 <= k <= t-3, "
          "for 8 <= t < 60: %s" % ("yes" if gaps == 0 else "NO"))
    # a derived member is made on a box that lies in the boxes of its parent
    orphans = 0
    for (base, word), boxes in created.items():
        ch = CHART_OF[base]
        if covered(ch, boxes, members[(base, word[:-1])]) is not None:
            orphans += 1
            print("ORPHAN: (%s, %s)" % (base, word))
    print("# (B) every box of a derived member lies in the boxes of the member it was derived from: %s" % ("yes" if orphans == 0 else "NO"))

    # ---- (C) every member but K0 has an entry above t^2 on its whole box
    lowm = 0
    nabove = 0
    for (base, word), boxes in members.items():
        if (base, word) == ("K0", ()):
            continue
        ch = CHART_OF[base]
        for bx in boxes:
            pt = box_point(ch, bx)
            M = member_matrix(base, word, pt)
            W = pt["t"] * pt["t"]
            good = M is not None and any((s := wsign(M[a][b])) and nonneg(s * M[a][b] - W - 1) for a in range(5) for b in range(a + 1, 5))
            nabove += 1
            if not good:
                lowm += 1
                print("LOW: (%s, %s) on %s" % (base, word, bx))
    print("# (C) members other than K0 with an entry certified above t^2 on the whole box: %d of %d" % (nabove - lowm, nabove))

    # ---- (D) the lines of other lines of the log, for the record
    idn = [l for _, l in other if re.search(r"\s(ok|FAILED)\s*", l) and not l.startswith("above")]
    above = [l for _, l in other if l.startswith("above")]
    print("# (D) the log also has %d identity lines (checked here by `closedforms`) and %d lines 'above t^2' (re-derived in C)"
          % (len(idn), len(above)))
    if fails:
        print("\nFAILED CLAIMS (%d)" % len(fails))
        for f in fails[:args.show]:
            print("  line %d: exit %s of %s => %s | %s" % (f[0], f[2], f[1], f[3], f[4]))
    ok = not fails and holes == 0 and gaps == 0 and orphans == 0 and lowm == 0
    print("\nreplay: %s" % ("ALL %d CLAIMS RE-CERTIFIED, COVERAGE COMPLETE" % len(claims) if ok else "PROBLEMS FOUND"))
    return 0 if ok else 1


# ============================================================================= the members on integers
def ispor(name, t):
    N = Nof(t)
    if name == "K0":
        return F_K0(t)
    if name == "K(t-1)":
        return F_K(t, t - 1)
    if name in ("K(t)", "K(t+1)", "K(t+2)"):
        return istep(ispor({"K(t)": "K(t-1)", "K(t+1)": "K(t)", "K(t+2)": "K(t+1)"}[name], t))
    if name in ("K(-1)", "K(-2)"):
        return iback(ispor({"K(-1)": "K0", "K(-2)": "K(-1)"}[name], t))
    if name == "L(0)":
        return F_L(t, 0, N + 1)
    if name == "L(1)":
        return F_L(t, 1, N)
    if name in ("L(-1)", "L(-2)"):
        return iback(ispor({"L(-1)": "L(0)", "L(-2)": "L(-1)"}[name], t))
    if name == "M1(t-2)":
        return F_M1(t, t - 2)
    if name in ("L(-(t-1))", "L(-t)"):
        return iback(ispor({"L(-(t-1))": "M1(t-2)", "L(-t)": "L(-(t-1))"}[name], t))
    raise KeyError(name)


def true_points(chart, t):
    """The points of a chart that belong to the given t (for L: r = N + 1 - i)."""
    N = Nof(t)
    if chart == "T":
        return [(t,)]
    if chart == "K":
        return [(j, t - 1 - j) for j in range(1, t - 1)]
    if chart == "L":
        return [(t, i, N + 1 - i) for i in range(2, N + 1)]
    if chart == "Ltop":
        return [(t, N + 1)]
    if chart == "M1":
        return [(k, t - 2 - k) for k in range(3, t - 2)]
    return [(t, m) for m in range(0, 2 * N + 2 * t + 8)]


def cmd_instances(args):
    """The members of the replay, at the true parameters of a given t, against the search of `closure`."""
    claims, _ = read_claims(os.path.join(HERE, args.log))
    members, given, created = build_members(claims)
    bad = 0
    for t in args.t:
        N, H, w = Nof(t), Hplus(t), t * t
        inst = {}
        for (base, word), boxes in members.items():
            ch = CHART_OF[base]
            for pnt in true_points(ch, t):
                if not any(in_box(ch, bx, pnt) for bx in boxes):
                    continue
                env = dict(zip(CHARTS[ch], pnt))
                if ch == "T":
                    M = ispor(base, t)
                elif ch == "K":
                    M = F_K(t, env["j"])
                elif ch == "L":
                    M = F_L(t, env["i"], env["r"])
                elif ch == "Ltop":
                    M = F_L(t, env["i"], 0)
                elif ch == "M1":
                    M = F_M1(t, env["k"])
                else:
                    M = F_M2(t, env["m"])
                for k in word:
                    M = imut(M, k)
                u = to_tuple(M)
                inst.setdefault(K5.canon(u), (base, word, pnt))
        below = {c for c in inst if K5.ht(c) < H}
        core = reach_set(Pplus(t), H, w)
        low = [c for c in inst if K5.ht(c) <= w]
        # closure on integers, from the instances: every mutation of an instance below H+ is an instance, is high, or is a high fork
        viol = 0
        for c in below:
            for k in range(5):
                v = K5.mut(c, k)
                if not (K5.ht(v) >= H or K5.canon(v) in inst or (K5.ht(v) > w and K5.is_fork(v))):
                    viol += 1
        good = below == core and len(low) == 1 and viol == 0
        bad += not good
        print("t=%d: %d instances of members at the true parameters, %d of them below H+; the search of `closure` finds %d quivers; "
              "the two sets are equal: %s; instances of height <= t^2: %d; mutations of instances below H+ that are neither an instance, "
              "nor of height >= H+, nor a fork higher than t^2: %d" % (t, len(inst), len(below), len(core), below == core, len(low), viol))
    return 0 if bad == 0 else 1


# ============================================================================= negative controls for `replay`
def cmd_negctl(args):
    """Change one line of the log at a time; `replay` must reject every changed log."""
    import contextlib
    import io
    src = open(os.path.join(HERE, args.log)).read().split("\n")
    tmpdir = os.path.expanduser("~/.cache/qmb-review17")
    os.makedirs(tmpdir, exist_ok=True)
    tmp = os.path.join(tmpdir, "negctl.log")

    def run(lines):
        with open(tmp, "w") as f:
            f.write("\n".join(lines))
        buf = io.StringIO()
        ns = argparse.Namespace(log=tmp, show=2)
        with contextlib.redirect_stdout(buf):
            rc = cmd_replay(ns)
        out = buf.getvalue().split("\n")
        why = [l.strip() for l in out if l.startswith(("  line", "HOLE", "ORPHAN", "LOW"))][:1]
        return rc, why

    def find(*needles):
        return next(i for i, l in enumerate(src) if all(n in l for n in needles))

    tests = [
        ("height: another entry named", ("exit x  of K(t-1)",), ("entry p-q", "entry x-c")),
        ("height on L: another entry named", ("exit c  of L(i), 2<=i<=N",), ("entry x-q", "entry x-p")),
        ("fork: another point of return", ("exit c1 of K0 ", "fork"), ("return c1", "return p")),
        ("fork: box widened to j >= 0", ("exit c  of K(j), 1<=j<=t-2", "fork"), ("'j': 1, 'v': 6", "'j': 0, 'v': 6")),
        ("member: K(j-1) written for K(j+1)", ("exit p  of K(j), 1<=j<=t-2",), ("K(j+1)", "K(j-1)")),
        ("member K(j-1): box widened to j >= 1", ("exit q  of K(j), 1<=j<=t-2  ", "'j': 2, 'v': 6"), ("'j': 2, 'v': 6", "'j': 1, 'v': 6")),
        ("member M1(k-1): box widened to k >= 2", ("exit p  of M1(k)",), ("'k': 3, 'u': 3", "'k': 2, 'u': 3")),
        ("member M1(k+1): box widened to u >= 0", ("exit q  of M1(k)", "'k': 5, 'u': 1"), ("'k': 5, 'u': 1", "'k': 5, 'u': 0")),
        ("member L(i+1): box widened to r >= 0", ("exit p  of L(i), 2<=i<=N",), ("'r': 1}", "'r': 0}")),
        ("member M2(m-1): box widened to m >= -1", ("exit p  of M2(m)",), ("'m': 0}", "'m': -1}")),
        ("derived target: another slice", ("exit x  of mu_c1 K(j), 1<=j<=t-2 [j=3] [t=9]",), ("[v=5] [t=9]", "[v=6] [t=9]")),
        ("derived target: box larger than the target's", ("exit x  of mu_c1 K(j), 1<=j<=t-2  ", "'j': 3, 'v': 8"), ("'j': 3, 'v': 8", "'j': 2, 'v': 8")),
        ("new member turned into height", ("exit x  of K(j), 1<=j<=t-2 [j=4] [t=8]",), ("new member", "height (entry p-q)")),
        ("slice moved from t = 9 to t = 10", ("exit c1 of mu_x K(j), 1<=j<=t-2 [j=4] [t=9]",), ("[t=9]  ", "[t=10] ")),
        ("box shrunk from t >= 10 to t >= 11", ("exit x  of K0  ", "'t': 10"), ("'t': 10", "'t': 11")),
        ("single quiver: K(t) written for K(t-2)", ("exit q  of K(t-1)",), ("member K(t-2)", "member K(t)")),
    ]
    rc, _ = run(src)
    print("%-52s -> %s" % ("the log as it is", "accepted" if rc == 0 else "REJECTED"))
    bad = rc != 0
    for label, needles, (a, b) in tests:
        i = find(*needles)
        lines = list(src)
        assert a in lines[i]
        lines[i] = lines[i].replace(a, b)
        rc, why = run(lines)
        bad |= rc == 0
        print("%-52s -> %s  %s" % (label + " (line %d)" % (i + 1), "rejected" if rc else "ACCEPTED", why[0][:150] if why else ""))
    i = find("exit q  of mu_x K0 [t=9]")
    rc, why = run(src[:i] + src[i + 1:])
    bad |= rc == 0
    print("%-52s -> %s  %s" % ("one claim removed (line %d)" % (i + 1), "rejected" if rc else "ACCEPTED", why[0][:150] if why else ""))
    print("negative controls: %s" % ("all %d changed logs rejected" % (len(tests) + 1) if not bad else "SOME ACCEPTED"))
    return 1 if bad else 0


# ============================================================================= closed forms
def cmd_closedforms(args):
    bad = 0

    def claim(label, good):
        nonlocal bad
        bad += not good
        print("%-110s %s" % (label, "ok" if good else "FAILED"), flush=True)

    z = G(0)
    # ---- polynomial identities.  Regions: all fresh variables >= 0.
    a, b, d = G("za"), G("zb"), G("zd")
    for tmin, tag in ((2, "t >= 2"),):
        t = tmin + a
        N = Nof(t)
        claim("I1  H+ = (t + N + 1) t^2 - 1", iszero(Hplus(t) - ((t + N + 1) * t * t - 1)))
        K0 = F_K0(t, z)
        K1 = sstep(K0)
        claim("I2  the step of K0 is the formula of K at j = 1  (%s)" % tag, K1 is not None and sequal(K1, F_K(t, 1 + 0 * t, z)))
        Kt = F_K(t, t - 1, z)
        L0 = smut(Kt, C1)
        claim("I4  mu_c1 of K(t-1) is the formula of L at i = 0, r = N + 1  (%s)" % tag, L0 is not None and sequal(L0, F_L(t, 0 * t, N + 1, z)))
    j, v = 1 + a, 1 + b                                   # 1 <= j <= t-2, t = j + v + 1 >= 3
    t = j + v + 1
    Kj = F_K(t, j, z)
    S = sstep(Kj)
    claim("I3  the step of K(j) is K(j+1) for 1 <= j <= t-2, t >= 3", S is not None and sequal(S, F_K(t, j + 1, z)))
    S = sback(F_K(t, j + 1, z))
    claim("I3' the backward step of K(j+1) is K(j) for 1 <= j <= t-2", S is not None and sequal(S, Kj))
    t, i, r = 2 + a, b, 1 + d                             # L(i) -> L(i+1) for i >= 0, r >= 1, t >= 2, r free
    S = sstep(F_L(t, i, r, z))
    claim("I5  the step of L(i) is L(i+1), with r - 1 for r, for i >= 0, r >= 1, t >= 2 and free r", S is not None and sequal(S, F_L(t, i + 1, r - 1, z)))
    S = sback(F_L(t, i + 1, r - 1, z))
    claim("I5' the backward step of L(i+1) is L(i) for i >= 0, r >= 1, t >= 2", S is not None and sequal(S, F_L(t, i, r, z)))
    t, i = 2 + a, b                                       # the top, with r = 0 and free i
    T = F_L(t, i, 0 * t, z)
    up, turn = smut(T, PV), smut(T, C)
    good = up is not None and turn is not None and all(iszero(up[x][y] + turn[x][y]) for x in range(5) for y in range(5))
    claim("I6  at the top (r = 0, any i >= 0, t >= 2): mu_c = -mu_p with the same labels", good)
    i = 1 + b                                              # from here on the top has index i >= 1
    T = F_L(t, i, 0 * t, z)
    up = smut(T, PV)
    Htop = (t + i) * t * t - 1
    good = up is not None and iszero(up[QV][X] - Htop) and all(nonneg(Htop - up[x][y]) and nonneg(Htop + up[x][y]) for x in range(5) for y in range(5))
    claim("I6' ... and mu_p(T) has the entry q -> x equal to (t + i) t^2 - 1 = H+ at i = N + 1, and no entry larger  (i >= 1)", good)
    T1 = F_L(t, i + 1, 0 * t, z)
    Hbelow = (t + i + 1) * t * t - 1 - t * t
    good = all(nonneg(Hbelow - T1[x][y]) and nonneg(Hbelow + T1[x][y]) for x in range(5) for y in range(5)) and iszero(T1[PV][X] - Hbelow)
    claim("I6'' every entry of the top L(N+1) is at most H+ - t^2 in absolute value, with equality at p -> x  (top index >= 2)", good)
    # entries along K(j) and L(i) against H+ - t^2 (r free: H+ - t^2 = (t + i + r - 1) t^2 - 1 at the true points)
    t, i, r = 2 + a, b, d
    Li = F_L(t, i, r, z)
    Hb = (t + i + r - 1) * t * t - 1
    xs = [Li[PV][X], Li[QV][X]]
    good = all(nonneg(Hb - e) and nonneg(Hb + e) for e in xs)
    claim("I7  on L(i), 0 <= i <= N+1: the column of x is at most H+ - t^2 in absolute value (t >= 2, r >= 0 free)", good)
    t = 8 + a                                              # the backward line, t >= 8 as in the certificate
    N = Nof(t)
    L0 = F_L(t, 0 * t, N + 1, z)
    B1 = sback(L0)
    B2 = sback(B1) if B1 is not None else None
    B3 = sback(B2) if B2 is not None else None
    claim("I8  two backward steps from L(0) give the formula of M1 at k = 2, and three give M1(3)  (t >= 8)",
          B3 is not None and sequal(B2, F_M1(t, 2 + 0 * t, z)) and sequal(B3, F_M1(t, 3 + 0 * t, z)))
    Mt = F_M1(t, t - 2, z)
    D1 = sback(Mt)
    D2 = sback(D1) if D1 is not None else None
    D3 = sback(D2) if D2 is not None else None
    claim("I9  two backward steps from M1(t-2) give the formula of M2 at m = -1, and three give M2(0)  (t >= 8)",
          D3 is not None and sequal(D2, F_M2(t, -1 + 0 * t, z)) and sequal(D3, F_M2(t, 0 * t, z)))
    k, u = 2 + a, 1 + b                                    # M1(k) -> M1(k+1) for 2 <= k <= t-3
    t = k + u + 2
    S = sback(F_M1(t, k, z))
    claim("I10 the backward step of M1(k) is M1(k+1) for 2 <= k <= t-3", S is not None and sequal(S, F_M1(t, k + 1, z)))
    t, m = 2 + a, -1 + b
    S = sback(F_M2(t, m, z))
    claim("I11 the backward step of M2(m) is M2(m+1) for m >= -1, t >= 2", S is not None and sequal(S, F_M2(t, m + 1, z)))
    t = 8 + a
    names = []
    for nm in SPOR:
        try:
            spor_matrix(nm, t)
            names.append(nm)
        except ValueError:
            pass
    claim("I12 signs certified on the way to the 14 single quivers (t >= 8): %d" % len(names), len(names) == 14)
    K0 = spor_matrix("K0", t)
    A = smut(smut(F_K(t, 1 + 0 * t, z), X), QV)
    B = smut(smut(K0, X), PV)
    claim("I13 mu_q mu_x K(1) is mu_p mu_x K(0) up to relabelling (the pentagon of the single arrow x -> p), t >= 8",
          A is not None and B is not None and siso(A, B) is not None)
    # ---- the same on integers, by mutation only
    good = True
    for tt in range(args.tmin, args.tmax + 1):
        N = Nof(tt)
        M = F_K0(tt)
        for jj in range(1, tt):
            M = istep(M)
            good &= M == F_K(tt, jj)
        M = imut(M, C1)
        L0 = M
        for ii in range(0, min(N + 1, args.imax) + 1):
            good &= M == F_L(tt, ii, N + 1 - ii)
            M = istep(M)
        M = L0
        for n in range(1, tt + args.mmax + 2):
            M = iback(M)
            if 2 <= n <= tt - 2:
                good &= M == F_M1(tt, n)
            if n >= tt:
                good &= M == F_M2(tt, n - tt - 1)
    claim("    integers, t = %d..%d: K(j), L(i) (i <= %d), M1(k), M2(m) (m <= %d) equal the quivers obtained by mutation"
          % (args.tmin, args.tmax, args.imax, args.mmax), good)
    print("\nclosed forms: %s" % ("all ok" if bad == 0 else "%d FAILED" % bad))
    return 0 if bad == 0 else 1


def cmd_singles(args):
    """The fourteen single quivers as polynomials in t (valid for t >= 8), in the coordinates of note 16, section 2."""
    zt = G("zt")
    t = 8 + zt
    tv = G("t")
    show = lambda g: str(G(g).subst("zt", tv - 8))
    print("%-10s | %-34s | %-30s | %-46s | %-14s | %-24s | %s" % ("quiver", "c1 = (b_p,c1, b_q,c1)", "c", "x", "b_c,c1", "b_x,c", "b_x,c1"))
    for nm in SPOR:
        M = spor_matrix(nm, t)
        cols = ["(%s, %s)" % (show(M[PV][e]), show(M[QV][e])) for e in (C1, C, X)]
        print("%-10s | %-34s | %-30s | %-46s | %-14s | %-24s | %s" % (nm, cols[0], cols[1], cols[2], show(M[C][C1]), show(M[X][C]), show(M[X][C1])))
        assert iszero(M[QV][PV] - 2)
    N = Nof(tv)
    print("N = %s, H+ = %s, H+ - 2t^2 = %s, t(t-2)(t^2-1) = %s" % (N, Hplus(tv), Hplus(tv) - 2 * tv * tv, tv * (tv - 2) * (tv * tv - 1)))
    return 0


# ============================================================================= Corollary 16.7
def cmd_corollary(args):
    import math
    pari = PARI()
    s = G("s")
    lhs = 2 * (s - 1) ** 5 - (s - 1) ** 4
    rhs = 2 * s ** 5 - 11 * s ** 4
    diff = lhs - rhs
    print("2(s-1)^5 - (s-1)^4 - (2s^5 - 11s^4) = %s" % diff)
    shifted = diff.subst("s", s + 1)
    print("  in s = 1 + y: %s ; no negative coefficient: %s, so the inequality holds for s >= 1" % (shifted, nonneg(shifted)))
    print("  real roots of the difference: %s" % [float(x) for x in pari.polrootsreal(diff)])
    d = (2 * s ** 5 - s ** 4).deriv()
    print("  d/ds (2s^5 - s^4) = %s, positive for s > 2/5, so 2s^5 - s^4 increases on [1, oo)" % d)
    T = args.tmax
    worst, at = max(((2 * w ** 2.5 - Hplus(math.isqrt(w))) / w ** 2, w) for w in range(4, (T + 1) ** 2))
    print("for 4 <= w < %d: the least c with H+(floor(sqrt w)) >= 2w^2.5 - c w^2 is %.4f, attained at w = %d" % ((T + 1) ** 2, worst, at))
    for t in (64, 1000, 100000):
        w = (t + 1) ** 2 - 1
        print("  at the worst w = (t+1)^2 - 1 with t = %d the constant is %.4f; as t grows it tends to 11 from below (11 - 29/t + ...)"
              % (t, (2 * w ** 2.5 - Hplus(t)) / w ** 2))
    exc = [w for w in range(4, (T + 1) ** 2) if Hplus(math.isqrt(w)) <= 2 * w * w]
    print("w in [4, %d) with H+(floor(sqrt w)) <= 2w^2: %s" % ((T + 1) ** 2, exc))
    print("H+(t) < (t+1)^2 never for t >= 2 (needed for t^2 <= w < H+): %s" % all(Hplus(t) >= (t + 1) ** 2 for t in range(2, 1000)))
    # exact: 2 w^{5/2} <= H+ + 11 w^2  <=>  4 w^5 <= (H+ + 11 w^2)^2
    bad = [w for w in range(4, 2000000) if 4 * w ** 5 > (Hplus(math.isqrt(w)) + 11 * w * w) ** 2]
    print("H+(floor(sqrt w)) >= 2w^2.5 - 11w^2 for every 4 <= w < 2,000,000, in exact integers: %s" % (not bad))
    bad10 = next(w for w in range(4, 10 ** 7) if 4 * w ** 5 > (Hplus(math.isqrt(w)) + 10 * w * w) ** 2)
    print("with 10 in place of 11 the inequality first fails at w = %d" % bad10)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    s = sub.add_parser("route")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=64)
    s = sub.add_parser("lemmas")
    s.add_argument("--trials", type=int, default=20000)
    s = sub.add_parser("forks")
    s.add_argument("--forks", type=int, default=20000)
    s.add_argument("--routes", type=int, default=200000)
    s = sub.add_parser("plain")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=64)
    s.add_argument("--family", choices=("plus", "pt", "both"), default="plus")
    s.add_argument("--workers", type=int, default=8)
    s = sub.add_parser("closure")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=40)
    s.add_argument("--workers", type=int, default=8)
    s = sub.add_parser("pendant")
    s.add_argument("--n", type=int, nargs="+", default=[6, 7])
    s.add_argument("--t", type=int, nargs="+", default=[2, 3, 4])
    s = sub.add_parser("star")
    s.add_argument("--spec", nargs="+", default=["1,2,3,8,4,8", "2,2,3,8,4,8", "2,3,5,18,9,18", "2,4,7,32,16,32", "3,2,5,12,6,12", "3,4,11,48,24,48"])
    s = sub.add_parser("anatomy")
    s.add_argument("--t", type=int, nargs="+", default=[5, 8, 12])
    s = sub.add_parser("closedforms")
    s.add_argument("--tmin", type=int, default=3)
    s.add_argument("--tmax", type=int, default=14)
    s.add_argument("--imax", type=int, default=600)
    s.add_argument("--mmax", type=int, default=60)
    s = sub.add_parser("replay")
    s.add_argument("--log", default="np_corridor_prove.log")
    s.add_argument("--show", type=int, default=40)
    s = sub.add_parser("instances")
    s.add_argument("--log", default="np_corridor_prove.log")
    s.add_argument("--t", type=int, nargs="+", default=[8, 9, 10, 11, 12, 13, 14, 16, 20])
    s = sub.add_parser("negctl")
    s.add_argument("--log", default="np_corridor_prove.log")
    sub.add_parser("singles")
    s = sub.add_parser("corollary")
    s.add_argument("--tmax", type=int, default=64)
    args = ap.parse_args()
    sys.exit(globals()["cmd_" + args.cmd](args))


if __name__ == "__main__":
    main()
