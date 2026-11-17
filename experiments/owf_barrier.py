#!/usr/bin/env python
"""
owf_barrier.py -- do the barriers of notes 15, 16 and 18 reopen the mutation-path one-way function of note 1? (note 21)

Note 1 killed the one-way function: iterative deepening on the entry bound (attack A3) inverts every planted
instance, and the planter pays more than the attacker.  Later notes then found explicit quivers Q whose opposite -Q is
joined to Q only far above the height w of Q: R_b (4 vertices, about 2w^2), Q_t (4 vertices, about 2w^2), P+_t
(5 vertices, about 2w^{5/2}) and Q_a (5 vertices, about 4w^3).  This script measures, for planted instances (Q, Q')
of that kind, three costs: the planter's, the generic attacker's and a structure-aware attacker's.

The structure-aware attacker
  1. descends out of fork regions (Warkentin, Def. 2.1 and Lemma 2.5: a fork has one way down, at its point of return);
  2. walks on pairs of weight 2.  A *step* mutates the sink p of the double arrow q -> p (Lemma 16.1); a *turn* mutates
     a vertex y of a chosen turn set whose column on the pair is (0, -eta), eta >= 1 (Lemma 16.2).  This is the walk of
     notes 16 and 18 (the bounce cycle W_m, Lemmas 18.1 and 18.2) written for any n;
  3. accelerates the walk, with a certificate:
       - a *run* of l steps on the pair, while every column has first entry >= 0, is the closed form
         (A, B) -> (A + l d, B - l d), d = A + B, with the entries between the other vertices unchanged (Lemma 16.1);
       - a *period*, the stretch of the walk between two turns at the same vertex with the same pair orientation, is
         replayed on the line X(k) = X + k (X - X_prev) with every entry an affine function of k.  Each decision of the
         walk (which run length, which turn, which sign in each product of the mutation rule) is turned into an affine
         inequality in k, each product must have one constant factor, and the output must be X(k + 1).  If so the period
         applies K times, for the largest K that satisfies every inequality, and the jump is exact;
  4. enumerates the pairs of weight 2, both directions (the backward walk is the forward walk of -X) and every turn set,
     from both ends, and matches the low quivers met on the way (height <= w) and the quivers at the ends of runs and
     periods, with their neighbours, up to relabelling.
It outputs a compressed route: runs, single mutations and repeated periods.

Subcommands (run from experiments/ with python -I; `np_corridor.py build` first):
  selftest  the run closed form, the symbolic period and the canonical form against integer mutation
  generic   the generic attacker: the minimax search of np_barrier (iterative deepening on the bound with exact levels)
  attack    the structure-aware attacker on R_b, Q_t, P+_t, Q_a, randomly relabelled, up to huge parameters
  rows      planter (a): random rows over the bounce cycle, n = 5 to 8, walked by the planter's own rule
  perturb   planter (b): every perturbation by +-1 of one entry of an explicit family member
  rwalk     planter (c): random walks inside a height bound, started at a family member
  mask      fork masking: random climbs from -Q, undone by fork descent
"""
import argparse
import itertools
import json
import math
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import np_corridor as nc
import np_rowwalk as nr
import n4_doors as nd
from np_corridor import mut, ht, neg, from_upper, upper, fork_return


def tup(B):
    return tuple(tuple(r) for r in B)


def lst(B):
    return [list(r) for r in B]


def relabel(B, perm):
    """The quiver with entry (i, j) = B[perm[i]][perm[j]]."""
    n = len(B)
    return tuple(tuple(B[perm[i]][perm[j]] for j in range(n)) for i in range(n))


# ----------------------------------------------------------------------------- canonical form, any n
def _classes(B):
    n = len(B)
    sig = [tuple(sorted(B[i])) for i in range(n)]
    sig2 = [(sig[i], tuple(sorted((B[i][j], sig[j]) for j in range(n) if j != i))) for i in range(n)]
    order = sorted(range(n), key=lambda i: sig2[i])
    groups = []
    for i in order:
        if groups and sig2[groups[-1][0]] == sig2[i]:
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups


def ckey(B):
    """Least upper triangle over the relabellings that sort the vertices by a relabelling-invariant signature.
    Equal keys if and only if the quivers are isomorphic."""
    n = len(B)
    groups = _classes(B)
    best = None
    for parts in itertools.product(*[itertools.permutations(g) for g in groups]):
        p = [v for part in parts for v in part]
        t = tuple(B[p[i]][p[j]] for i in range(n) for j in range(i + 1, n))
        if best is None or t < best:
            best = t
    return best


def iso_perm(X, Y):
    """A permutation perm with X = relabel(Y, perm), or None."""
    n = len(X)
    gx, gy = _classes(X), _classes(Y)
    if [len(g) for g in gx] != [len(g) for g in gy]:
        return None
    for parts in itertools.product(*[itertools.permutations(g) for g in gy]):
        py = [v for part in parts for v in part]
        px = [v for g in gx for v in g]
        perm = [0] * n
        for a, b in zip(px, py):
            perm[a] = b
        if all(X[i][j] == Y[perm[i]][perm[j]] for i in range(n) for j in range(n)):
            return perm
    return None


# ----------------------------------------------------------------------------- fork descent
def fork_descent(B, limit=10 ** 6):
    """While B is a fork, mutate at its point of return (the only way out of its far region).  Returns (B, word)."""
    word = []
    while len(word) < limit:
        r = fork_return(B)
        if r is None:
            break
        B = mut(B, r)
        word.append(r)
    return B, word


def weight(B):
    n = len(B)
    return sum(abs(B[i][j]) for i in range(n) for j in range(i + 1, n))


def descend(B, limit=10 ** 6):
    """Fork descent, and between fork steps the steepest descent on total arrow weight (note 1, attack A2), until
    neither applies.  Returns (B, word)."""
    word = []
    while len(word) < limit:
        r = fork_return(B)
        if r is not None:
            B = mut(B, r)
            word.append(r)
            continue
        wb = weight(B)
        best = None
        for v in range(len(B)):
            N = mut(B, v)
            wn = weight(N)
            if wn < wb and (best is None or wn < best[0]):
                best = (wn, v, N)
        if best is None:
            break
        B = best[2]
        word.append(best[1])
    return B, word


# ----------------------------------------------------------------------------- the walk: numeric decisions
INF = float("inf")


def floordiv(a, b):
    return a // b


def ceildiv(a, b):
    return -((-a) // b)


def decide(X, p, q, T, bound):
    """One decision of the walk at X with the double arrow q -> p.  Returns ('turn', y), ('step',), ('square', y),
    ('run', l, why) or ('stop', why).

    A vertex y of T whose column is (-eta, 0) is turned at once (the late turn).  One whose column is (0, -eta) is
    turned now, or, if the step is lower, the walk steps first and turns late: the two ways round the commuting square
    of Lemma 18.2(Q) end at the same quiver."""
    n = len(X)
    for y in T:
        if X[q][y] == 0 and X[p][y] < 0:
            return ("turn", y)
    for y in T:
        if X[p][y] == 0 and X[q][y] < 0:
            if ht(mut(X, y)) <= ht(mut(X, p)):
                return ("turn", y)
            return ("square", y)
    others = [e for e in range(n) if e != p and e != q]
    if any(X[p][e] < 0 for e in others):
        return ("step",)
    lreg = lbot = lturn = lh = INF
    for e in others:
        A, B = X[p][e], X[q][e]
        d = A + B
        if d < 0:
            lreg = min(lreg, A // (-d) + 1)                       # first i with A + i d < 0
            if A // (-d) >= 1:
                lbot = min(lbot, A // (-d))                       # the bottom: last i with A + i d >= 0
            if e in T and A % (-d) == 0:
                lturn = min(lturn, A // (-d))                     # A + i d = 0 with d < 0: a turn (i >= 1 here)
        elif d > 0:
            lh = min(lh, (bound - A) // d)                        # A + i d <= bound
    l = min(lreg, lbot, lturn, lh)
    if l == INF:
        return ("stop", "cycle")
    if l <= 0:
        return ("stop", "bound")
    why = "turn" if l == lturn else ("bottom" if l == lbot else ("regime" if l == lreg else "bound"))
    return ("run", l, why)


def apply_run(X, p, q, l):
    """l steps on the pair (sink p, source q) in closed form; valid while every column has first entry >= 0."""
    n = len(X)
    Y = lst(X)
    P, Qv = (p, q) if l % 2 == 0 else (q, p)
    for e in range(n):
        if e == p or e == q:
            continue
        A, B = X[p][e], X[q][e]
        d = A + B
        A2, B2 = A + l * d, B - l * d
        Y[P][e], Y[e][P] = A2, -A2
        Y[Qv][e], Y[e][Qv] = B2, -B2
    Y[Qv][P], Y[P][Qv] = 2, -2
    return tup(Y), P, Qv


def run_low_points(X, p, q, l, wlow):
    """Positions 1 <= i <= l on the run from X whose quiver has height <= wlow (an interval)."""
    n = len(X)
    lo, hi = 1, l
    for i in range(n):
        for j in range(i + 1, n):
            if {i, j} & {p, q}:
                continue
            if abs(X[i][j]) > wlow:
                return []
    for e in range(n):
        if e == p or e == q:
            continue
        A, B = X[p][e], X[q][e]
        d = A + B
        # entries A + i d and B - i d at position i
        for c0, c1 in ((A, d), (B, -d)):
            if c1 == 0:
                if abs(c0) > wlow:
                    return []
            elif c1 > 0:
                lo, hi = max(lo, ceildiv(-wlow - c0, c1)), min(hi, floordiv(wlow - c0, c1))
            else:
                lo, hi = max(lo, ceildiv(c0 - wlow, -c1)), min(hi, floordiv(c0 + wlow, -c1))
    return list(range(lo, hi + 1)) if lo <= hi else []


# ----------------------------------------------------------------------------- the walk: symbolic period
class Fail(Exception):
    pass


class Cons:
    """Affine functions c0 + c1 k on k in [0, kmax]; each requirement lowers kmax or fails."""

    def __init__(self, bound):
        self.kmax = INF
        self.bound = bound

    def cap(self, v):
        if v < 0:
            raise Fail("k")
        self.kmax = min(self.kmax, v)

    def nonneg(self, f):
        c0, c1 = f
        if c0 < 0:
            raise Fail("nonneg")
        if c1 < 0:
            self.cap(c0 // (-c1))

    def nonpos(self, f):
        self.nonneg((-f[0], -f[1]))

    def pos(self, f):
        c0, c1 = f
        if c0 <= 0:
            raise Fail("pos")
        if c1 < 0:
            self.cap(ceildiv(c0, -c1) - 1)

    def neg(self, f):
        self.pos((-f[0], -f[1]))

    def zero(self, f):
        if f != (0, 0):
            raise Fail("zero")

    def nonzero(self, f):
        c0, c1 = f
        if c0 == 0:
            raise Fail("nonzero")
        if c1 != 0 and (-c0) % c1 == 0 and (-c0) // c1 > 0:
            self.cap((-c0) // c1 - 1)

    def absle(self, f):
        c0, c1 = f
        b = self.bound
        if abs(c0) > b:
            raise Fail("height")
        if c1 > 0:
            self.cap((b - c0) // c1)
        elif c1 < 0:
            self.cap((b + c0) // (-c1))


def a_add(f, g):
    return (f[0] + g[0], f[1] + g[1])


def a_mul(f, g):
    if f[1] != 0 and g[1] != 0:
        raise Fail("quadratic")
    return (f[0] * g[0], f[0] * g[1] + f[1] * g[0])


def a_neg(f):
    return (-f[0], -f[1])


def sym_sign_class(f, cons):
    """+1 if f >= 0 on the range, -1 if f <= 0, decided at k = 0 and required on the range."""
    c0, c1 = f
    if c0 > 0 or (c0 == 0 and c1 >= 0):
        cons.nonneg(f)
        return 1
    cons.nonpos(f)
    return -1


def sym_mut(S, v, cons):
    n = len(S)
    sg = {}
    for i in range(n):
        if i != v:
            sg[i] = sym_sign_class(S[i][v], cons)
    N = [row[:] for row in S]
    for i in range(n):
        if i == v or S[i][v] == (0, 0):
            continue
        for j in range(n):
            if j == v or j == i or S[v][j] == (0, 0):
                continue
            si, sj = sg[i], -sg[j]                                 # sign of b_iv and of b_vj = -b_jv
            if si > 0 and sj > 0:
                N[i][j] = a_add(N[i][j], a_mul(S[i][v], S[v][j]))
            elif si < 0 and sj < 0:
                N[i][j] = a_add(N[i][j], a_neg(a_mul(S[i][v], S[v][j])))
    for i in range(n):
        N[i][v] = a_neg(S[i][v])
        N[v][i] = a_neg(S[v][i])
    for i in range(n):
        for j in range(i + 1, n):
            cons.absle(N[i][j])
    return N


def sym_not_turn(S, p, q, T, cons, late_upto=None, early_upto=None, early=True):
    """Require that no vertex of T is a late turn (before late_upto in the order of T) and, if early, that none is an
    early turn (before early_upto), on the whole range."""
    for y in T:
        if y == late_upto:
            break
        A, B = S[p][y], S[q][y]
        if B[0] != 0:
            cons.nonzero(B)
        else:
            cons.nonneg(A)
    if late_upto is not None or not early:
        return
    for y in T:
        if y == early_upto:
            break
        A, B = S[p][y], S[q][y]
        if A[0] != 0:
            cons.nonzero(A)
        else:
            cons.nonneg(B)


def sym_apply(S, p, q, op, T, cons):
    """Replay one recorded op on the symbolic quiver S, requiring that the walk makes the same decision on the range."""
    n = len(S)
    others = [e for e in range(n) if e != p and e != q]
    if op[0] == "turn" and S[q][op[1]][0] == 0 and S[p][op[1]][0] < 0:          # late turn
        y = op[1]
        sym_not_turn(S, p, q, T, cons, late_upto=y)
        cons.zero(S[q][y])
        cons.neg(S[p][y])
        return sym_mut(S, y, cons), p, q
    if op[0] in ("turn", "square"):                                            # early turn, or the step before a late one
        y = op[1]
        sym_not_turn(S, p, q, T, cons, early_upto=y)
        cons.zero(S[p][y])
        cons.neg(S[q][y])
        if op[0] == "turn":
            return sym_mut(S, y, cons), p, q
        return sym_mut(S, p, cons), q, p
    sym_not_turn(S, p, q, T, cons)
    if op[0] == "step":
        e = next((e for e in others if S[p][e][0] < 0), None)
        if e is None:
            raise Fail("step")
        cons.neg(S[p][e])
        N = sym_mut(S, p, cons)
        return N, q, p
    if op[0] == "run":
        l, why = op[1], op[2]
        if why == "bound":
            raise Fail("bound")
        N = [row[:] for row in S]
        P, Qv = (p, q) if l % 2 == 0 else (q, p)
        stop_ok = False
        for e in others:
            A, B = S[p][e], S[q][e]
            d = a_add(A, B)
            Al = (A[0] + l * d[0], A[1] + l * d[1])                     # first entry at position l
            Alm1 = (A[0] + (l - 1) * d[0], A[1] + (l - 1) * d[1])
            cons.nonneg(A)
            cons.nonneg(Alm1)                                           # first entries >= 0 at positions 0..l-1
            if d[0] < 0 and l >= 2:
                cons.neg(d)
                cons.nonneg(Al)                                         # no bottom before position l
            elif l >= 2:
                cons.nonneg(d)
            if e in T and l >= 2:                                       # no turn at positions 1..l-1
                if d[0] >= 0:
                    cons.nonneg(d)
                else:
                    cons.pos((A[0] + d[0], A[1] + d[1]))
                    cons.pos(Alm1)
            if why == "turn" and e in T and Al == (0, 0):
                cons.neg(d)
                stop_ok = True
            if why == "regime" and Al[0] < 0 and not stop_ok:
                cons.neg(Al)
                stop_ok = True
            if why == "bottom" and d[0] < 0 and Al[0] >= 0 and Al[0] + d[0] < 0 and not stop_ok:
                cons.nonneg(Al)
                cons.neg(a_add(Al, d))
                stop_ok = True
            Bl = (B[0] - l * d[0], B[1] - l * d[1])
            for f in (A, B, Al, Bl):
                cons.absle(f)
            N[P][e], N[e][P] = Al, a_neg(Al)
            N[Qv][e], N[e][Qv] = Bl, a_neg(Bl)
        if not stop_ok:
            raise Fail("stop")
        N[Qv][P], N[P][Qv] = (2, 0), (-2, 0)
        return N, P, Qv
    raise Fail("op")


def try_period(Xprev, X, p, q, ops, T, bound):
    """X = ops(Xprev).  If ops applies to X + k (X - Xprev) for 0 <= k < K and gives X + (k + 1)(X - Xprev), return K
    (the largest such, >= 1) and the symbolic snapshots after each op; else None."""
    n = len(X)
    S = [[(X[i][j], X[i][j] - Xprev[i][j]) for j in range(n)] for i in range(n)]
    if all(S[i][j][1] == 0 for i in range(n) for j in range(n)):
        return "cycle"
    cons = Cons(bound)
    snaps = []
    try:
        cur, pp, qq = S, p, q
        for op in ops:
            cur, pp, qq = sym_apply(cur, pp, qq, op, T, cons)
            snaps.append((cur, pp, qq, op))
    except Fail:
        return None
    if (pp, qq) != (p, q):
        return None
    for i in range(n):
        for j in range(n):
            if cur[i][j] != (S[i][j][0] + S[i][j][1], S[i][j][1]):
                return None
    K = cons.kmax + 1 if cons.kmax != INF else INF
    return K, snaps


def affine_low_ks(S, wlow, K):
    """The k in [0, K] at which every entry of the symbolic quiver S has absolute value <= wlow (an interval)."""
    n = len(S)
    lo, hi = 0, K
    for i in range(n):
        for j in range(i + 1, n):
            c0, c1 = S[i][j]
            if c1 == 0:
                if abs(c0) > wlow:
                    return None
            elif c1 > 0:
                lo, hi = max(lo, ceildiv(-wlow - c0, c1)), min(hi, floordiv(wlow - c0, c1))
            else:
                lo, hi = max(lo, ceildiv(c0 - wlow, -c1)), min(hi, floordiv(c0 + wlow, -c1))
    return (lo, hi) if lo <= hi else None


def _aff_le(c0, c1, w, K):
    """The k in [0, K] with |c0 + c1 k| <= w, as an interval or None."""
    if c1 == 0:
        return (0, K) if abs(c0) <= w else None
    if c1 > 0:
        lo, hi = ceildiv(-w - c0, c1), floordiv(w - c0, c1)
    else:
        lo, hi = ceildiv(c0 - w, -c1), floordiv(c0 + w, -c1)
    lo, hi = max(lo, 0), min(hi, K)
    return (lo, hi) if lo <= hi else None


def _iv_and(A, B):
    out = []
    for (a0, a1) in A:
        for (b0, b1) in B:
            lo, hi = max(a0, b0), min(a1, b1)
            if lo <= hi:
                out.append((lo, hi))
    return out


def run_low_ks(S, p, q, l, w, K):
    """A superset of the k in [0, K] at which the run of l steps from S(k) passes a quiver of height <= w.  Along the run
    every first entry A_e + i d_e is >= 0 and affine in i, and the second entries are earlier first entries, so a
    column can be low somewhere only if it is low at position 0 or l; the other entries are constant."""
    n = len(S)
    ivs = [(0, K)]
    for i in range(n):
        for j in range(i + 1, n):
            if {i, j} & {p, q}:
                continue
            r = _aff_le(S[i][j][0], S[i][j][1], w, K)
            if r is None:
                return []
            ivs = _iv_and(ivs, [r])
    for e in range(n):
        if e == p or e == q:
            continue
        A, B = S[p][e], S[q][e]
        d = (A[0] + B[0], A[1] + B[1])
        Al = (A[0] + l * d[0], A[1] + l * d[1])
        Alm1 = (A[0] + (l - 1) * d[0], A[1] + (l - 1) * d[1])
        u = [r for r in (_aff_le(A[0], A[1], w, K), _aff_le(Al[0], Al[1], w, K)) if r]
        ivs = _iv_and(ivs, u)
        u = [r for r in (_aff_le(-B[0], -B[1], w, K), _aff_le(Alm1[0], Alm1[1], w, K)) if r]
        ivs = _iv_and(ivs, u)
        if not ivs:
            return []
    return ivs


def at_k(S, k):
    return tuple(tuple(c0 + c1 * k for (c0, c1) in row) for row in S)


# ----------------------------------------------------------------------------- the walk
class Walk:
    """The walk from X on the pair with sink p, source q and turn set T, inside the height bound, with certified
    acceleration.  Records the compressed route (ops), the quivers at the ends of ops ('nodes'), and the quivers of
    height <= wlow met anywhere on the way ('lows'), each with the position on the route that reaches it."""

    def __init__(self, X, p, q, T, bound, wlow, max_ops=4000, accelerate=True, low_cap=20000):
        self.X0, self.p0, self.q0 = X, p, q
        self.T = tuple(sorted(T))
        self.bound, self.wlow = bound, wlow
        self.ops = []              # compressed route: ('m', v) | ('run', p, q, l) | ('rep', [ops], K)
        self.nodes = []            # (quiver, index into ops: the quiver after ops[:index])
        self.turns = []            # the quivers right after a turn, as nodes
        self.lows = []             # (quiver, route prefix as a list of ops)
        self.end = None
        self.n_ops = 0
        self.n_sym = 0
        self.length = 0            # number of mutations of the literal route
        self.maxh = ht(X)
        self.low_unchecked = 0
        self.max_ops = max_ops
        self.accelerate = accelerate
        self.low_cap = low_cap
        self.run()

    def _low(self, Y, prefix):
        if ht(Y) <= self.wlow:
            self.lows.append((Y, prefix))

    def run(self):
        X, p, q = self.X0, self.p0, self.q0
        markers = {}               # (y, p, q) -> (X after the turn, index in local op list)
        local = []                 # the decisions since the start, as ('turn', y) / ('step',) / ('run', l, why)
        self.nodes.append((X, 0))
        while self.n_ops < self.max_ops:
            dec = decide(X, p, q, self.T, self.bound)
            self.n_ops += 1
            if dec[0] == "stop":
                self.end = dec[1]
                break
            if dec[0] == "turn":
                Y = mut(X, dec[1])
                if ht(Y) > self.bound:
                    self.end = "bound"
                    break
                self.ops.append(("m", dec[1]))
                self.length += 1
                X = Y
                self._low(X, list(self.ops))
                self.turns.append((X, len(self.ops)))
            elif dec[0] in ("step", "square"):
                Y = mut(X, p)
                if ht(Y) > self.bound:
                    self.end = "bound"
                    break
                self.ops.append(("m", p))
                self.length += 1
                X, p, q = Y, q, p
                self._low(X, list(self.ops))
            else:
                l = dec[1]
                for i in run_low_points(X, p, q, l, self.wlow)[:self.low_cap]:
                    Y, _, _ = apply_run(X, p, q, i)
                    self.lows.append((Y, list(self.ops) + [("run", p, q, i)]))
                self.ops.append(("run", p, q, l))
                self.length += l
                X, p, q = apply_run(X, p, q, l)
            self.maxh = max(self.maxh, ht(X))
            local.append(dec)
            self.nodes.append((X, len(self.ops)))
            if dec[0] == "turn" and self.accelerate:
                key = (dec[1], p, q)
                if key in markers:
                    Xprev, i0, j0 = markers[key]
                    period = local[i0:]
                    res = try_period(Xprev, X, p, q, period, self.T, self.bound)
                    self.n_sym += 1
                    if res == "cycle":
                        self.end = "cycle"
                        break
                    if res is not None and res[0] >= 2:
                        K, snaps = res
                        if K == INF:
                            self.end = "unbounded"
                            break
                        jumped = self._jump(X, p, q, Xprev, period, K, snaps, j0)
                        X = jumped
                        markers = {}
                        local = []
                        self.nodes.append((X, len(self.ops)))
                        self.maxh = max(self.maxh, ht(X))
                        continue
                markers[key] = (X, len(local), len(self.ops))
        self.final = (X, p, q)
        if self.end is None:
            self.end = "budget"

    def _jump(self, X, p, q, Xprev, period, K, snaps, j0):
        """Apply the period K times from X; record low quivers inside the jump; return the end quiver."""
        n = len(X)
        rec = self.ops[j0:]                       # the period as compressed ops (one copy)
        plen = sum(op[3] if op[0] == "run" else 1 for op in rec)
        base = list(self.ops)
        S0 = [[(X[i][j], X[i][j] - Xprev[i][j]) for j in range(n)] for i in range(n)]
        # low quivers: at the start of each period, after each op of it, and inside its runs
        states = [(S0, p, q, None)] + [(s, pp, qq, op) for (s, pp, qq, op) in snaps]
        cand = set()
        for idx in range(len(states) - 1):
            S, pp, qq, _ = states[idx]
            op = snaps[idx][3]
            if op[0] == "run":
                rngs = run_low_ks(S, pp, qq, op[1], self.wlow, K - 1)
            else:
                r = affine_low_ks(snaps[idx][0], self.wlow, K - 1)
                rngs = [r] if r else []
            for (lo, hi) in rngs:
                if hi - lo > self.low_cap:
                    self.low_unchecked += hi - lo - self.low_cap
                    hi = lo + self.low_cap
                for k in range(lo, hi + 1):
                    cand.add((k, idx))
        for (k, idx) in sorted(cand):
            S, pp, qq, _ = states[idx]
            op = snaps[idx][3]
            Xk = at_k(S, k)
            prefix = base + [("rep", rec, k)] + rec[:idx]
            if op[0] == "run":
                for i in run_low_points(Xk, pp, qq, op[1], self.wlow):
                    Y, _, _ = apply_run(Xk, pp, qq, i)
                    self.lows.append((Y, prefix + [("run", pp, qq, i)]))
            else:
                Y = at_k(snaps[idx][0], k)
                if ht(Y) <= self.wlow:
                    self.lows.append((Y, prefix + [rec[idx]]))
        self.ops.append(("rep", rec, K))
        self.length += K * plen
        Xend = tuple(tuple(c0 + c1 * K for (c0, c1) in row) for row in S0)
        for S, _, _, _ in snaps:                  # heights inside the jump are certified <= bound; record the largest
            self.maxh = max(self.maxh, max(max(abs(c0), abs(c0 + c1 * (K - 1))) for row in S for (c0, c1) in row))
        return Xend


# ----------------------------------------------------------------------------- literal replay of a compressed route
def expand(ops):
    """The literal mutation word of a compressed route."""
    out = []
    for op in ops:
        if op[0] == "m":
            out.append(op[1])
        elif op[0] == "run":
            _, p, q, l = op
            out.extend(p if i % 2 == 0 else q for i in range(l))
        else:
            _, rec, K = op
            w = expand(rec)
            for _ in range(K):
                out.extend(w)
    return out


def replay(X, word):
    h = ht(X)
    for v in word:
        X = mut(X, v)
        h = max(h, ht(X))
    return X, h


def compressed_size(ops):
    return sum(1 + (compressed_size(op[1]) if op[0] == "rep" else 0) for op in ops)


# ----------------------------------------------------------------------------- the structure-aware attacker
def weight2_pairs(X):
    """Ordered pairs (p, q) with two arrows q -> p."""
    n = len(X)
    return [(p, q) for p in range(n) for q in range(n) if X[q][p] == 2]


def turn_sets(n, p, q, mode="all"):
    rest = [v for v in range(n) if v != p and v != q]
    if mode == "all":
        return [c for r in range(len(rest), -1, -1) for c in itertools.combinations(rest, r)]
    return [tuple(rest)]


class Attack:
    """Inverts (Q, Q') inside the public bound by fork descent and accelerated walks from both ends.

    Depth 0 walks from the two ends; the quivers right after the turns of depth-d walks are the seeds of depth d + 1,
    from which walks start again in every direction (this is how a walk reverses: R_b crosses its plateau backwards).
    A match is a quiver met from both ends, up to relabelling: a low quiver on a walk, a quiver at the end of a run or
    period, or one of its neighbours."""

    def __init__(self, Q, Qp, bound, wlow=None, max_ops=4000, tmode="all", neighbours=True, accelerate=True,
                 depth=2, max_seeds=400):
        t0 = time.time()
        self.bound = bound
        self.Q, self.Qp = Q, Qp
        self.Q0, self.wq = fork_descent(Q)
        self.Qp0, self.wqp = fork_descent(Qp)
        self.wlow = wlow if wlow is not None else max(ht(self.Q0), ht(self.Qp0))
        self.walks = self.ops = self.sym = self.keys = 0
        self.literal_steps = 0
        self.unchecked = 0
        self.depth_used = None
        self.found = None
        self.index = [{}, {}]
        starts = [self.Q0, self.Qp0]
        seeds = [[(starts[0], [])], [(starts[1], [])]]
        seen = [{ckey(starts[0])}, {ckey(starts[1])}]
        for side in (0, 1):
            if self._add(side, starts[side], (starts[side], [], None)):
                break
        self.weight_descent = [0, 0]
        for side in (0, 1):                      # the weight descent of each end is a second seed of depth 0
            if self.found:
                break
            D, dw = descend(starts[side])
            self.weight_descent[side] = len(dw)
            if dw and ckey(D) not in seen[side]:
                seen[side].add(ckey(D))
                seeds[side].append((D, [[("m", v) for v in dw]]))
                self._add(side, D, (D, [[("m", v) for v in dw]], None))
        for d in range(depth + 1):
            if self.found:
                break
            new = [[], []]
            for side in (0, 1):
                for (Y, segs) in seeds[side]:
                    if self.found:
                        break
                    self._walks_from(side, Y, segs, new, max_ops, tmode, neighbours, accelerate, seen, max_seeds)
            if self.found:
                self.depth_used = d
            seeds = [sorted(s, key=lambda t: ht(t[0]))[:max_seeds] for s in new]
        self.time = time.time() - t0

    def _walks_from(self, side, Y, segs, new, max_ops, tmode, neighbours, accelerate, seen, max_seeds):
        for sign in (1, -1):
            X = Y if sign == 1 else neg(Y)
            for (p, q) in weight2_pairs(X):
                for T in turn_sets(len(X), p, q, tmode):
                    if self.found:
                        return
                    W = Walk(X, p, q, T, self.bound, self.wlow, max_ops=max_ops, accelerate=accelerate)
                    self.walks += 1
                    self.ops += W.n_ops
                    self.sym += W.n_sym
                    self.literal_steps += W.length
                    self.unchecked += W.low_unchecked
                    sg = (lambda Z: Z) if sign == 1 else neg
                    for (L, prefix) in W.lows:
                        if self._add(side, sg(L), (sg(L), segs + [prefix], None)):
                            return
                    if neighbours:
                        for (N, idx) in W.nodes:
                            N2, pre = sg(N), W.ops[:idx]
                            if self._add(side, N2, (N2, segs + [pre], None)):
                                return
                            for v in range(len(N2)):
                                Z = mut(N2, v)
                                if ht(Z) <= self.bound and self._add(side, Z, (Z, segs + [pre], v)):
                                    return
                    for (N, idx) in W.nodes:
                        N2, pre = sg(N), W.ops[:idx]
                        cands = [(N2, segs + [pre])] + [(mut(N2, v), segs + [pre + [("m", v)]]) for v in range(len(N2))]
                        for (Z, sz) in cands:
                            if ht(Z) > self.bound:
                                continue
                            k = ckey(Z)
                            if k not in seen[side]:
                                seen[side].add(k)
                                new[side].append((Z, sz))

    def _add(self, side, Y, info):
        k = ckey(Y)
        self.keys += 1
        other = self.index[1 - side]
        if k in other:
            self.found = (info, other[k]) if side == 0 else (other[k], info)
            return True
        self.index[side].setdefault(k, info)
        return False

    def word(self):
        """The literal route from Q to a relabelling of Q', and that relabelling (only for moderate sizes)."""
        (Y0, segs0, v0), (Y1, segs1, v1) = self.found
        perm = iso_perm(Y0, Y1)                  # Y0 = relabel(Y1, perm)
        inv = [0] * len(perm)
        for i, j in enumerate(perm):
            inv[j] = i
        a = list(self.wq) + [v for s in segs0 for v in expand(s)] + ([] if v0 is None else [v0])
        b = list(self.wqp) + [v for s in segs1 for v in expand(s)] + ([] if v1 is None else [v1])
        return a + [inv[v] for v in reversed(b)], perm

    def summary(self):
        size = None
        if self.found:
            (Y0, segs0, v0), (Y1, segs1, v1) = self.found
            size = (sum(compressed_size(s) for s in segs0 + segs1) + len(self.wq) + len(self.wqp)
                    + (v0 is not None) + (v1 is not None))
        return {"found": self.found is not None, "depth": self.depth_used, "walks": self.walks, "ops": self.ops,
                "sym_periods": self.sym, "keys": self.keys, "route_ops": size,
                "fork_descent": [len(self.wq), len(self.wqp)], "weight_descent": self.weight_descent,
                "low_unchecked": self.unchecked, "time": round(self.time, 3)}


def route_length(ops):
    return sum(op[3] if op[0] == "run" else (1 if op[0] == "m" else op[2] * route_length(op[1])) for op in ops)


def found_length(A):
    (Y0, segs0, v0), (Y1, segs1, v1) = A.found
    return (len(A.wq) + len(A.wqp) + sum(route_length(s) for s in segs0 + segs1) + (v0 is not None) + (v1 is not None))


# ----------------------------------------------------------------------------- the families
def fam_R(b):
    return from_upper(list(nd.Rb(b)), 4), nd.HRb(b), b


def fam_Qt(t):
    return from_upper(list(nd.Qt(t)), 4), nd.Ht(t), t * t


def fam_Pplus(t):
    return nc.Pplus(t), nc.Hplus(t), t * t


def fam_Qa(a):
    return nr.Qa(a), nr.Hfam(a), a + 1


FAMILIES = {"R": fam_R, "Qt": fam_Qt, "P+": fam_Pplus, "Qa": fam_Qa}
NVERT = {"R": 4, "Qt": 4, "P+": 5, "Qa": 5}


def random_relabel(B, rng):
    perm = list(range(len(B)))
    rng.shuffle(perm)
    return relabel(B, perm)


# ----------------------------------------------------------------------------- selftest
def cmd_selftest(args):
    rng = random.Random(1)
    ok = True
    # run closed form against integer mutation
    nrun = 0
    for _ in range(3000):
        n = rng.choice([4, 5, 6, 7])
        B = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                v = rng.randint(-9, 9)
                B[i][j], B[j][i] = v, -v
        p, q = rng.sample(range(n), 2)
        B[q][p], B[p][q] = 2, -2
        for e in range(n):
            if e not in (p, q):
                A = rng.randint(0, 30)
                B[p][e], B[e][p] = A, -A
        B = tup(B)
        dec = decide(B, p, q, (), 10 ** 9)
        if dec[0] != "run":
            continue
        l = min(dec[1], 40)
        Y, P, Qv = apply_run(B, p, q, l)
        Z = B
        cur = p
        for i in range(l):
            Z = mut(Z, cur)
            cur = p + q - cur
        ok &= Y == Z and P == cur
        nrun += 1
    print("run closed form against integer mutation on %d random runs: %s" % (nrun, ok))
    # canonical form
    ok2 = True
    for _ in range(300):
        n = rng.choice([4, 5, 6])
        B = from_upper([rng.randint(-3, 3) for _ in range(n * (n - 1) // 2)], n)
        C = random_relabel(B, rng)
        ok2 &= ckey(B) == ckey(C) and relabel(C, iso_perm(B, C)) == B or (relabel(C, iso_perm(B, C)) == B)
        ok2 &= (ckey(B) == ckey(neg(B))) == (nc.canon(B) == nc.canon(neg(B)))
    print("canonical form: invariant under relabelling, agrees with np_corridor.canon on B vs -B, iso_perm: %s" % ok2)
    # the walk with and without acceleration on Q_a: same quivers at the end
    ok3 = True
    for a in range(2, 9):
        Q, H, w = fam_Qa(a)
        for T in [(2, 3)]:
            W1 = Walk(Q, 4, 1, T, H, w, max_ops=10 ** 6, accelerate=False)
            W2 = Walk(Q, 4, 1, T, H, w, max_ops=10 ** 6, accelerate=True)
            X1, _ = replay(Q, expand(W2.ops))
            ok3 &= X1 == W2.final[0] and W1.length == W2.length and W1.final[0] == W2.final[0]
            l1 = sorted(ckey(Y) for Y, _ in W1.lows)
            l2 = sorted(ckey(Y) for Y, _ in W2.lows)
            ok3 &= l1 == l2
            for Y, pre in W2.lows:
                ok3 &= replay(Q, expand(pre))[0] == Y
            print("  a=%d: walk of %d mutations, %d ops plain, %d ops accelerated (%d periods tried), end %s; low quivers %d/%d"
                  % (a, W2.length, W1.n_ops, W2.n_ops, W2.n_sym, W2.end, len(W1.lows), len(W2.lows)))
    print("accelerated walk = plain walk on Q_a, a = 2..8 (end quiver, length, low quivers, replay of every prefix): %s" % ok3)
    print("ALL OK" if ok and ok2 and ok3 else "FAILED")


def parse_params(s):
    """'2-8,16,1e6,2^40' -> list of ints."""
    out = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part[1:]:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif "^" in part:
            a, b = part.split("^")
            out.append(int(a) ** int(b))
        elif "e" in part:
            a, b = part.split("e")
            out.append(int(a) * 10 ** int(b))
        else:
            out.append(int(part))
    return out


def cmd_attack(args):
    """The structure-aware attacker against Q' = -Q, both randomly relabelled, public bound = the barrier H (or larger)."""
    rng = random.Random(args.seed)
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for fam in args.families:
        for par in parse_params(args.params):
            Q, H, w = FAMILIES[fam](par)
            bound = H * args.bound_factor
            for trial in range(args.trials):
                Qr = random_relabel(Q, rng)
                Qpr = random_relabel(neg(Q), rng)
                A = Attack(Qr, Qpr, bound, wlow=w, max_ops=args.max_ops, tmode=args.tmode, depth=args.depth)
                r = {"family": fam, "param": par, "n": len(Q), "w": w, "H": H, "bound": bound, "trial": trial}
                r.update(A.summary())
                if A.found:
                    r["route_mutations"] = found_length(A)
                    if args.verify and r["route_mutations"] <= args.verify:
                        word, perm = A.word()
                        Z, h = replay(Qr, word)
                        r["verified"] = Z == relabel(Qpr, perm) and h <= bound
                        r["route_height"] = h
                print(json.dumps(r), flush=True)
                if out:
                    out.write(json.dumps(r) + "\n")
                    out.flush()
    if out:
        out.close()


# ----------------------------------------------------------------------------- the generic attacker
def route_len_closed(fam, par):
    """The number of mutations of the published route (Theorems 15.13, 15.6, 16.4, 18.4); None if not in closed form."""
    if fam == "Qa":
        return nr.Lfam(par)
    if fam == "P+":
        return 4 * par ** 3 - 2 * par ** 2 + 4
    return None


def cmd_generic(args):
    """np_barrier on each family member: (1) the minimax search from Q at the bound H, which stops when it reaches
    another quiver of height <= w (that is -Q): the cost of iterative deepening with exact levels; (2) the whole
    component below H (the quivers a bounded search must sweep before the barrier opens); (3) the component at the
    first level 4^k >= H, the level at which note 1's attack A3 (bounds 4, 16, 64, ...) succeeds."""
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for fam in args.families:
        for par in parse_params(getattr(args, "p_" + fam.replace("+", "plus"))):
            Q, H, w = FAMILIES[fam](par)
            if H >= nc.INT_MAX:
                continue
            L4 = 4
            while L4 < H:
                L4 *= 4
            t0 = time.time()
            rows = {}
            for prune in args.prune:
                lines = [nc.task_line(Q, H, args.budget, prune, w=w),
                         nc.task_line(Q, H - 1, args.budget, prune, w=H - 1)]
                if args.l4 and L4 < nc.INT_MAX:
                    lines.append(nc.task_line(Q, L4, args.budget, prune, w=L4))
                res = nc.search(lines)
                mm = res[0]
                r = {"family": fam, "param": par, "n": len(Q), "w": w, "H": H, "prune": prune,
                     "minimax": {k: mm.get(k) for k in ("status", "iso", "popped", "nodes", "path_len", "forks")},
                     "target_is_opposite": mm.get("target") is not None and tuple(mm["target"]) == nc.canon(neg(Q)),
                     "below_H": {k: res[1].get(k) for k in ("status", "popped", "plateau", "forks")}}
                if len(res) > 2:
                    r["at_L4"] = {"L4": L4, **{k: res[2].get(k) for k in ("status", "popped", "forks")}}
                r["route_closed_form"] = route_len_closed(fam, par)
                r["time"] = round(time.time() - t0, 2)
                print(json.dumps(r), flush=True)
                if out:
                    out.write(json.dumps(r) + "\n")
                    out.flush()
    if out:
        out.close()


# ----------------------------------------------------------------------------- planter (a): rows over the bounce cycle
BIN8 = os.path.expanduser("~/.cache/qmb-np/np_barrier8")


def barrier_search(B, w, cap, budget, prune=0):
    """np_barrier (np_barrier8 for n = 8): the minimax search from B, stopping at the first quiver of height <= w
    outside the component of B at height w."""
    line = nc.task_line(B, min(cap, nc.INT_MAX), budget, prune, w=w)
    binary = BIN8 if len(B) == 8 else nc.BIN
    out = subprocess.run([binary], input=line + "\n", capture_output=True, text=True).stdout
    return json.loads(out.strip().splitlines()[-1])


def cycle_quiver(m, j, states, extra=None):
    """W_m(j) on (p, q, r, s) = (0, 1, 2, 3), with vertices 4, 5, ... in the states (A, B, U, V) = (b_px, b_qx, b_xr,
    b_xs), and the entries extra[(x, y)] between them."""
    k = len(states)
    n = 4 + k
    B = [[0] * n for _ in range(n)]

    def setb(i, j2, v):
        B[i][j2], B[j2][i] = v, -v
    setb(1, 0, 2)
    setb(3, 2, 2)
    setb(0, 2, m - j)
    setb(1, 2, -(m + 1 - j))
    setb(0, 3, j)
    setb(1, 3, 1 - j)
    for t, (A, Bx, U, V) in enumerate(states):
        x = 4 + t
        setb(0, x, A)
        setb(1, x, Bx)
        setb(x, 2, U)
        setb(x, 3, V)
    for (x, y), v in (extra or {}).items():
        setb(x, y, v)
    return tup(B)


def first_low(W, Q):
    """The first quiver of height <= w on the walk that is not isomorphic to Q, with its route prefix."""
    kq = ckey(Q)
    best = None
    for (Y, prefix) in W.lows:
        if ckey(Y) != kq:
            L = route_length(prefix)
            if best is None or L < best[2]:
                best = (Y, prefix, L)
    return best


def cmd_rows(args):
    """Planter (a).  Q = W_m(j) at its lowest position (m = 2w - 1, j = w, height w) with n - 4 random rows of height
    <= w.  The planter walks Q by the bounce-cycle rule (pair (p, q), turns at r and s), forwards and backwards, inside
    the cap, and plants (Q, Y) for the first quiver Y of height <= w not isomorphic to Q.  Its route and the height h of
    that route are the secret.  Then: the generic attacker (np_barrier from Q at height w up to h) and the
    structure-aware attacker on (Q, Y) relabelled at random, with public bound h."""
    rng = random.Random(args.seed)
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for n in args.n:
        for w in args.w:
            m, j = 2 * w - 1, w
            cap = args.cap_factor * w ** (n - 2)
            stats = {"rows": 0, "planted": 0}
            for trial in range(args.rows):
                k = n - 4
                states = [tuple(rng.randint(-w, w) for _ in range(4)) for _ in range(k)]
                extra = {}
                if args.mode == "dense":
                    for x in range(4, n):
                        for y in range(x + 1, n):
                            extra[(x, y)] = rng.randint(-w, w)
                Q = cycle_quiver(m, j, states, extra)
                stats["rows"] += 1
                t0 = time.time()
                best = None
                walk_ops = 0
                for sign in (1, -1):
                    X = Q if sign == 1 else neg(Q)
                    p, q = (0, 1) if X[1][0] == 2 else (1, 0)
                    W = Walk(X, p, q, (2, 3), cap, w, max_ops=args.max_ops)
                    walk_ops += W.n_ops
                    fl = first_low(W, X)
                    if fl and (best is None or fl[2] < best[2]):
                        Y = fl[0] if sign == 1 else neg(fl[0])
                        best = (Y, fl[1], fl[2], sign)
                r = {"n": n, "w": w, "m": m, "mode": args.mode, "states": states, "extra": sorted(extra.items()),
                     "planter_walk_ops": walk_ops, "planter_time": round(time.time() - t0, 4), "planted": best is not None}
                if best is not None:
                    Y, prefix, L, sign = best
                    word = expand(prefix)
                    _, h = replay(Q, word)
                    stats["planted"] += 1
                    r.update({"route_mutations": L, "route_ops": compressed_size(prefix), "h": h,
                              "h_over_w^(n-2)": round(h / w ** (n - 2), 3), "Y_is_opposite": ckey(Y) == ckey(neg(Q)),
                              "Y": upper(Y)})
                    if args.generic and n <= 8:
                        g = barrier_search(Q, w, h, args.budget)
                        r["generic"] = {kk: g.get(kk) for kk in ("status", "iso", "popped", "path_len")}
                        r["generic"]["target_is_Y"] = g.get("target") is not None and \
                            ckey(from_upper(g["target"], n)) == ckey(Y)
                    Qr, Yr = random_relabel(Q, rng), random_relabel(Y, rng)
                    A = Attack(Qr, Yr, h, wlow=w, max_ops=args.max_ops, depth=args.depth)
                    r["structure"] = A.summary()
                    if A.found and found_length(A) <= 2_000_000:
                        wd, perm = A.word()
                        Z, hh = replay(Qr, wd)
                        r["structure"]["verified"] = Z == relabel(Yr, perm) and hh <= h
                print(json.dumps(r), flush=True)
                if out:
                    out.write(json.dumps(r) + "\n")
                    out.flush()
            print("# n=%d w=%d mode=%s: %d rows, %d planted" % (n, w, args.mode, stats["rows"], stats["planted"]), flush=True)
    if out:
        out.close()


# ----------------------------------------------------------------------------- planter (b): perturbations
def cmd_perturb(args):
    """Planter (b).  Every quiver obtained from a family member Q of height w by changing one entry by +-1 or +-2,
    keeping the height <= w.  For each: the generic escape level (np_barrier up to cap_factor * H, the first quiver of
    height <= w outside the start component, and its cost), and the structure-aware attacker on (Q~, that quiver)
    relabelled, with public bound the escape level."""
    rng = random.Random(args.seed)
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for spec in args.members:
        fam, par = spec.split(":")
        par = int(par)
        Q, H, w = FAMILIES[fam](par)
        n = len(Q)
        u = upper(Q)
        seen = {ckey(Q)}
        rows = []
        for i in range(len(u)):
            for dlt in args.deltas:
                v = list(u)
                v[i] += dlt
                if abs(v[i]) > w:
                    continue
                P = from_upper(v, n)
                k = ckey(P)
                if k in seen:
                    continue
                seen.add(k)
                # the planter's walks: every pair of weight 2, both directions, every turn set, up to 64 H
                t0 = time.time()
                best, wops = None, 0
                for sign in (1, -1):
                    X = P if sign == 1 else neg(P)
                    for (p, q) in weight2_pairs(X):
                        for T in turn_sets(n, p, q):
                            W = Walk(X, p, q, T, 64 * H, w, max_ops=args.max_ops)
                            wops += W.n_ops
                            fl = first_low(W, X)
                            if fl:
                                _, hh = replay(P, expand(fl[1]))
                                if best is None or hh < best[1]:
                                    best = (fl[0] if sign == 1 else neg(fl[0]), hh, fl[2])
                r = {"family": fam, "param": par, "n": n, "w": w, "H": H, "entry": i, "delta": dlt, "quiver": v,
                     "planter": {"found": best is not None, "h": best[1] if best else None,
                                 "route_mutations": best[2] if best else None, "walk_ops": wops,
                                 "time": round(time.time() - t0, 3)}}
                cap = max(args.cap_factor * H, best[1] if best else 0)
                g = barrier_search(P, w, cap, args.budget)
                r["generic"] = {kk: g.get(kk) for kk in ("status", "iso", "popped", "path_len")}
                r["generic"]["cap"] = cap
                target = None
                if g.get("status") == "found":
                    target, bnd = from_upper(g["target"], n), g["iso"]
                    r["generic"]["target_is_opposite"] = ckey(target) == ckey(neg(P))
                elif best is not None:
                    target, bnd = best[0], best[1]
                if target is not None:
                    A = Attack(random_relabel(P, rng), random_relabel(target, rng), bnd, wlow=w, max_ops=args.max_ops, depth=args.depth)
                    r["structure"] = A.summary()
                print(json.dumps(r), flush=True)
                if out:
                    out.write(json.dumps(r) + "\n")
                    out.flush()
    if out:
        out.close()


# ----------------------------------------------------------------------------- planter (c): height-restricted walks
def component_graph(Q, bound, budget):
    """The component of Q among quivers of height <= bound, up to relabelling: keys, levels, neighbour lists (a
    mutation that leaves the bound is a loop)."""
    line = nc.task_line(Q, bound, budget, 0, w=bound)
    out = subprocess.run([nc.BIN, "--dump"], input=line + "\n", capture_output=True, text=True).stdout
    data = json.loads(out.strip().splitlines()[-1].replace("],\"n\"", "],\"n\"", 1)) if False else None
    txt = out.strip().splitlines()[-1]
    head, tail = txt.split("],\"n\":", 1)
    dump = json.loads(head[len('{"dump":'):] + "]")
    meta = json.loads('{"n":' + tail)
    n = len(Q)
    keys = [tuple(k) for k, lv, h in dump]
    level = [lv for k, lv, h in dump]
    idx = {k: i for i, k in enumerate(keys)}
    nbr = []
    for k in keys:
        B = from_upper(list(k), n)
        row = []
        for v in range(n):
            N = mut(B, v)
            row.append(idx.get(nc.canon(N), -1) if ht(N) <= bound else -1)
        nbr.append(row)
    return keys, level, nbr, meta


def cmd_rwalk(args):
    """Planter (c).  The planter walks at random inside the height bound h (a random vertex at each step; a mutation
    that would leave the bound is refused and counts as a step), starting at Q, until it first meets a quiver of
    height <= w that is not Q.  Hitting times against the size of the bounded component (the generic attacker's sweep)
    and the length of the shortest route (the honest planter's)."""
    rng = random.Random(args.seed)
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for spec in args.members:
        fam, par = spec.split(":")
        par = int(par)
        Q, H, w = FAMILIES[fam](par)
        n = len(Q)
        for bf in args.bound_factors:
            h = int(H * bf)
            t0 = time.time()
            keys, level, nbr, meta = component_graph(Q, h, args.budget)
            if meta.get("status") == "budget":
                print(json.dumps({"family": fam, "param": par, "h": h, "status": "budget"}), flush=True)
                continue
            start = keys.index(nc.canon(Q))
            low_far = {i for i in range(len(keys)) if level[i] <= w and keys[i] != keys[start]}
            times = []
            for trial in range(args.trials):
                x, steps = start, 0
                while steps < args.max_steps:
                    y = nbr[x][rng.randrange(n)]
                    steps += 1
                    if y >= 0:
                        x = y
                        if x in low_far:
                            break
                times.append(steps if x in low_far else None)
            hit = sorted(t for t in times if t is not None)
            r = {"family": fam, "param": par, "n": n, "w": w, "H": H, "h": h, "component": len(keys),
                 "low_targets": len(low_far), "trials": args.trials, "hit": len(hit),
                 "median_steps": hit[len(hit) // 2] if hit else None, "min_steps": hit[0] if hit else None,
                 "max_steps_cap": args.max_steps, "time": round(time.time() - t0, 2)}
            print(json.dumps(r), flush=True)
            if out:
                out.write(json.dumps(r) + "\n")
                out.flush()
    if out:
        out.close()


# ----------------------------------------------------------------------------- fork masking
def cmd_mask(args):
    """Q' = a random climb of l mutations (no immediate repeat) from -Q, Q a family member.  Fork descent from Q', then
    the structure-aware attacker with public bound max(H, height of the climb)."""
    rng = random.Random(args.seed)
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for spec in args.members:
        fam, par = spec.split(":")
        par = int(par)
        Q, H, w = FAMILIES[fam](par)
        n = len(Q)
        for l in args.lengths:
            for trial in range(args.trials):
                X = neg(Q)
                word, last, hmax, forks = [], None, H, 0
                for _ in range(l):
                    v = rng.choice([u for u in range(n) if u != last])
                    X = mut(X, v)
                    word.append(v)
                    last = v
                    hmax = max(hmax, ht(X))
                    forks += fork_return(X) is not None
                D, dw = fork_descent(X)
                # how much of the climb did the descent undo?
                undone = 0
                while undone < len(dw) and undone < l and dw[undone] == word[l - 1 - undone]:
                    undone += 1
                A = Attack(random_relabel(Q, rng), random_relabel(X, rng), hmax, wlow=w, max_ops=args.max_ops, depth=args.depth)
                r = {"family": fam, "param": par, "l": l, "trial": trial, "log10_height": round(math.log10(max(hmax, 1)), 1),
                     "forks_on_climb": forks, "end_is_fork": fork_return(X) is not None, "descent": len(dw),
                     "descent_undoes_climb": undone, "residual_climb": l - undone, "climb": word, "structure": A.summary()}
                print(json.dumps(r), flush=True)
                if out:
                    out.write(json.dumps(r) + "\n")
                    out.flush()
    if out:
        out.close()


# ----------------------------------------------------------------------------- short literal routes above the barrier
def bibfs(A, B, bound, budget, prune_w=None):
    """Bidirectional breadth-first search between A and B (up to relabelling) among quivers of height <= bound.
    With prune_w, forks higher than prune_w are skipped: by Lemma 15.5 a reduced route between quivers of height
    <= prune_w passes none, and a shortest route is reduced.  Returns (distance or None, nodes, lower bound)."""
    ka, kb = ckey(A), ckey(B)
    if ka == kb:
        return 0, 1, 0
    dist = [{ka: 0}, {kb: 0}]
    front = [[A], [B]]
    depth = [0, 0]
    nodes = 2
    while front[0] and front[1] and nodes < budget:
        s = 0 if len(front[0]) <= len(front[1]) else 1
        nxt = []
        for X in front[s]:
            for v in range(len(X)):
                Y = mut(X, v)
                if ht(Y) > bound:
                    continue
                if prune_w is not None and ht(Y) > prune_w and fork_return(Y) is not None:
                    continue
                k = ckey(Y)
                if k in dist[s]:
                    continue
                dist[s][k] = depth[s] + 1
                nodes += 1
                if k in dist[1 - s]:
                    return depth[s] + 1 + dist[1 - s][k], nodes, None
                nxt.append(Y)
        front[s] = nxt
        depth[s] += 1
    closed = not front[0] or not front[1]
    return None, nodes, (None if closed else depth[0] + depth[1] + 1)


def cmd_shortest(args):
    """The fewest mutations from Q to -Q inside the bound B, for B from the barrier H upwards."""
    out = open(args.out, "a" if args.append else "w") if args.out else None
    for spec in args.members:
        fam, par = spec.split(":")
        par = int(par)
        Q, H, w = FAMILIES[fam](par)
        for bnd in args.bounds:
            B = H * int(bnd[1:]) if bnd.startswith("x") else 2 ** int(bnd[2:]) if bnd.startswith("2^") else int(bnd)
            if B < H:
                continue
            t0 = time.time()
            d, nodes, lb = bibfs(Q, neg(Q), B, args.budget, prune_w=w if args.prune else None)
            r = {"family": fam, "param": par, "w": w, "H": H, "bound": B, "prune": args.prune, "distance": d, "lower_bound": lb,
                 "nodes": nodes, "time": round(time.time() - t0, 1)}
            print(json.dumps(r), flush=True)
            if out:
                out.write(json.dumps(r) + "\n")
                out.flush()
    if out:
        out.close()


# ----------------------------------------------------------------------------- summary
def _load(path):
    p = os.path.join(HERE, path)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def _fmt(x):
    if x is None:
        return "-"
    if isinstance(x, int) and x >= 10 ** 7:
        return "%.3g" % x if x < 2 ** 63 else "2^%.1f" % math.log2(x)
    return str(x)


def cmd_summarize(args):
    print("# owf_barrier.py summarize: the tables of note 21 from the stored results")
    gen = _load("owf_barrier_generic.jsonl")
    print("\n## Generic attacker (np_barrier).  L = length of the minimax route; sweep = quivers popped before -Q is reached")
    print("family param w H | L | sweep | sweep, forks pruned | below H | component at the A3 level 4^k >= H | sweep/L | log sweep / log L")
    for r in gen:
        if r["prune"] != 0:
            continue
        r1 = next((s for s in gen if s["family"] == r["family"] and s["param"] == r["param"] and s["prune"] == 1), None)
        L, P = r["minimax"]["path_len"], r["minimax"]["popped"]
        l4 = r.get("at_L4", {})
        print("%s %s %d %d | %d | %d | %s | %d | %s (%s, 4^k = %s) | %.2f | %.3f" % (
            r["family"], r["param"], r["w"], r["H"], L, P, r1["minimax"]["popped"] if r1 else "-", r["below_H"]["popped"],
            l4.get("popped"), l4.get("status"), l4.get("L4"), P / L, math.log(P) / math.log(L)))
    att = _load("owf_barrier_attack.jsonl") + _load("owf_barrier_attack_bigbound.jsonl")
    print("\n## Structure-aware attacker (max over the trials)")
    print("family param bound/H | found | depth | walks | ops | iso keys | route ops | route mutations | time s | literal replay")
    groups = {}
    for r in att:
        groups.setdefault((r["family"], r["param"], r["bound"] // r["H"]), []).append(r)
    for (f, p, bf), rs in groups.items():
        ver = [r.get("verified") for r in rs]
        print("%s %s %s | %d/%d | %s | %d | %d | %d | %d | %s | %.3f | %s" % (
            f, _fmt(p), bf, sum(r["found"] for r in rs), len(rs), max(r["depth"] or 0 for r in rs), max(r["walks"] for r in rs),
            max(r["ops"] for r in rs), max(r["keys"] for r in rs), max(r["route_ops"] or 0 for r in rs),
            _fmt(rs[0].get("route_mutations")), max(r["time"] for r in rs),
            "all %d verified" % len(rs) if all(v is True for v in ver) else ("not run (too long)" if all(v is None for v in ver) else str(ver))))
    print("total: %d instances, %d found, %d literal routes verified, %d failed verification" % (
        len(att), sum(r["found"] for r in att), sum(r.get("verified") is True for r in att), sum(r.get("verified") is False for r in att)))
    rows = []
    for f in ("owf_barrier_rows_n5.jsonl", "owf_barrier_rows_n6.jsonl", "owf_barrier_rows_n6_dense.jsonl",
              "owf_barrier_rows_n7.jsonl", "owf_barrier_rows_n8.jsonl"):
        rows += _load(f)
    print("\n## Planter (a): random rows over the bounce cycle")
    print("n w mode | rows | planted | h >= w^(n-2)/2 | h >= w^(n-2) | largest h (h/w^(n-2)) | its route | planter walk ops (median) | "
          "generic sweep, largest | generic reaches Y at h | structure found / verified | structure iso keys median, max")
    grp = {}
    for r in rows:
        grp.setdefault((r["n"], r["w"], r["mode"]), []).append(r)
    for (n, w, mode), rs in sorted(grp.items()):
        pl = [r for r in rs if r["planted"]]
        W = w ** (n - 2)
        top = max(pl, key=lambda r: r["h"]) if pl else None
        po = sorted(r["planter_walk_ops"] for r in rs)
        sk = sorted(r["structure"]["keys"] for r in pl)
        print("%d %d %s | %d | %d | %d | %d | %s | %s | %d | %s | %d | %d / %d | %s, %s" % (
            n, w, mode, len(rs), len(pl), sum(r["h"] >= W / 2 for r in pl), sum(r["h"] >= W for r in pl),
            "%d (%.2f)" % (top["h"], top["h"] / W) if top else "-", top["route_mutations"] if top else "-", po[len(po) // 2],
            max((r["generic"]["popped"] for r in pl if "generic" in r), default="-"),
            sum(1 for r in pl if r.get("generic", {}).get("iso") == r["h"] and r["generic"].get("target_is_Y")),
            sum(r["structure"]["found"] for r in pl), sum(r["structure"].get("verified") is True for r in pl),
            sk[len(sk) // 2] if sk else "-", sk[-1] if sk else "-"))
    pts = [(r["h"], r["generic"]["popped"], r["route_mutations"]) for r in rows if r["planted"] and r["n"] == 5
           and r.get("generic", {}).get("iso") == r["h"] and r["h"] >= 50]
    if len(pts) > 2:
        xs, ys = [math.log(h) for h, _, _ in pts], [math.log(p) for _, p, _ in pts]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        rat = sorted(p / L for _, p, L in pts)
        print("n = 5, rows whose generic escape equals h >= 50: %d; sweep ~ h^%.2f; sweep / route median %.1f, max %.1f"
              % (len(pts), a, rat[len(rat) // 2], rat[-1]))
    per = _load("owf_barrier_perturb.jsonl")
    print("\n## Planter (b): perturbations by +-1, +-2 of one entry")
    print("member H | perturbed quivers | another quiver of height <= w below cap = 4H (generic) | largest escape (/H) | "
          "planter walk finds one with h > w | structure found / instances")
    grp = {}
    for r in per:
        grp.setdefault((r["family"], r["param"]), []).append(r)
    for (f, p), rs in grp.items():
        gf = [r for r in rs if r["generic"]["status"] == "found"]
        iso = max((r["generic"]["iso"] for r in gf), default=None)
        att2 = [r for r in rs if "structure" in r]
        print("%s %s %d | %d | %d | %s | %d | %d / %d" % (
            f, p, rs[0]["H"], len(rs), len(gf), "%d (%.2f)" % (iso, iso / rs[0]["H"]) if iso else "-",
            sum(1 for r in rs if r["planter"]["found"] and r["planter"]["h"] > r["w"]),
            sum(r["structure"]["found"] for r in att2), len(att2)))
    rw = _load("owf_barrier_rwalk.jsonl") + _load("owf_barrier_rwalk_qa.jsonl")
    print("\n## Planter (c): random walks inside the bound h, from Q until another quiver of height <= w")
    print("member H h | component (generic sweep) | trials hit | median steps | min steps | median / component")
    for r in rw:
        if r.get("status") == "budget":
            continue
        print("%s %s %d %d | %d | %d/%d | %s | %s | %s" % (
            r["family"], r["param"], r["H"], r["h"], r["component"], r["hit"], r["trials"], r["median_steps"], r["min_steps"],
            "%.0f" % (r["median_steps"] / r["component"]) if r["median_steps"] else "-"))
    sh = _load("owf_barrier_shortest.jsonl") + _load("owf_barrier_shortest_pruned.jsonl")
    print("\n## The fewest mutations from Q to -Q inside the bound (pruned: forks higher than w skipped, Lemma 15.5)")
    print("member H | pruned | bound | distance | quivers searched")
    for r in sh:
        print("%s %s %d | %s | %s | %s | %d" % (r["family"], r["param"], r["H"], "yes" if r.get("prune") else "no", _fmt(r["bound"]),
                                               r["distance"] if r["distance"] is not None else ">= %s (budget)" % r["lower_bound"],
                                               r["nodes"]))
    mk = _load("owf_barrier_mask.jsonl")
    print("\n## Fork masking: Q' = a random climb of l mutations from -Q")
    print("member l | trials | end is a fork | descent undoes the whole climb | largest log10 height | structure found | depth | max time s")
    grp = {}
    for r in mk:
        grp.setdefault((r["family"], r["param"], r["l"]), []).append(r)
    for (f, p, l), rs in sorted(grp.items(), key=lambda t: (t[0][0], t[0][1], t[0][2])):
        print("%s %s %d | %d | %d | %d | %.1f | %d | %s | %.2f" % (
            f, p, l, len(rs), sum(r["end_is_fork"] for r in rs), sum(r["residual_climb"] == 0 for r in rs),
            max(r["log10_height"] for r in rs), sum(r["structure"]["found"] for r in rs),
            sorted(set(r["structure"]["depth"] for r in rs if r["structure"]["depth"] is not None)), max(r["structure"]["time"] for r in rs)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    s = sub.add_parser("generic")
    s.add_argument("--families", nargs="+", default=["R", "Qt", "P+", "Qa"])
    s.add_argument("--p-R", default="6,8,10,16,20,30,40,60,100,200")
    s.add_argument("--p-Qt", default="3-14")
    s.add_argument("--p-Pplus", default="2-10,16,32,64")
    s.add_argument("--p-Qa", default="2-12")
    s.add_argument("--prune", type=int, nargs="+", default=[0, 1])
    s.add_argument("--budget", type=int, default=10_000_000)
    s.add_argument("--l4", action="store_true")
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    s = sub.add_parser("rows")
    s.add_argument("--depth", type=int, default=4)
    s.add_argument("--n", type=int, nargs="+", default=[5])
    s.add_argument("--w", type=int, nargs="+", default=[3, 4])
    s.add_argument("--rows", type=int, default=200)
    s.add_argument("--mode", default="star", choices=["star", "dense"])
    s.add_argument("--cap-factor", type=int, default=64)
    s.add_argument("--max-ops", type=int, default=4000)
    s.add_argument("--generic", action="store_true")
    s.add_argument("--budget", type=int, default=5_000_000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    s = sub.add_parser("perturb")
    s.add_argument("--depth", type=int, default=4)
    s.add_argument("--members", nargs="+", default=["R:6", "R:7", "R:8", "R:10", "Qt:3", "Qt:4", "P+:2", "P+:3", "Qa:3", "Qa:4", "Qa:5", "Qa:6"])
    s.add_argument("--deltas", type=int, nargs="+", default=[-2, -1, 1, 2])
    s.add_argument("--cap-factor", type=int, default=4)
    s.add_argument("--budget", type=int, default=5_000_000)
    s.add_argument("--max-ops", type=int, default=4000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    s = sub.add_parser("rwalk")
    s.add_argument("--members", nargs="+", default=["R:8", "R:10", "R:12", "Qt:3", "Qt:4", "P+:2", "P+:3", "P+:4", "Qa:2", "Qa:3", "Qa:4"])
    s.add_argument("--bound-factors", type=float, nargs="+", default=[1.0, 2.0])
    s.add_argument("--trials", type=int, default=100)
    s.add_argument("--max-steps", type=int, default=50_000_000)
    s.add_argument("--budget", type=int, default=2_000_000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    s = sub.add_parser("mask")
    s.add_argument("--depth", type=int, default=4)
    s.add_argument("--members", nargs="+", default=["R:8", "R:9", "Qt:4", "P+:4", "Qa:5", "Qa:6"])
    s.add_argument("--lengths", type=int, nargs="+", default=[5, 10, 20, 40])
    s.add_argument("--trials", type=int, default=10)
    s.add_argument("--max-ops", type=int, default=4000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    s = sub.add_parser("shortest")
    s.add_argument("--members", nargs="+", default=["R:6", "R:8", "Qt:3", "P+:2", "P+:3", "Qa:2", "Qa:3"])
    s.add_argument("--bounds", nargs="+", default=["x1", "x4", "x16", "x256", "2^20", "2^40"])
    s.add_argument("--prune", action="store_true", help="skip forks higher than w (Lemma 15.5)")
    s.add_argument("--budget", type=int, default=3_000_000)
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    sub.add_parser("summarize")
    s = sub.add_parser("attack")
    s.add_argument("--depth", type=int, default=4)
    s.add_argument("--families", nargs="+", default=["R", "Qt", "P+", "Qa"])
    s.add_argument("--params", default="6-8")
    s.add_argument("--trials", type=int, default=1)
    s.add_argument("--bound-factor", type=int, default=1)
    s.add_argument("--max-ops", type=int, default=4000)
    s.add_argument("--tmode", default="all")
    s.add_argument("--verify", type=int, default=2_000_000, help="replay the literal route when it has at most this many mutations")
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--out")
    s.add_argument("--append", action="store_true")
    args = ap.parse_args()
    globals()["cmd_" + args.cmd](args)


if __name__ == "__main__":
    main()
