#!/usr/bin/env python
"""
review19.py -- independent checks for the review of notes 13, 14, 15 and 16.

Written for the review; it imports none of the scripts under review.  Quivers are skew-symmetric integer matrices,
stored as the tuple of entries above the diagonal in the order (01, 02, ..., 0n-1, 12, ...).  Every search here is
on LABELLED quivers (no canonical form during the search, so no relabelling bookkeeping can go wrong), with Python
integers (no overflow).  Isomorphism is tested only at the end, by the lexicographic MAXIMUM over all relabellings
(the scripts under review use the minimum).  No fork is ever pruned unless a subcommand says so.

Subcommands
  route16   the route of Theorem 16.4 for P+_t and P_t: every column, every height, the top identity, non-isomorphism
  search16  Theorem 16.5: all labelled quivers that P+_t (or P_t) reaches below H; the low ones; the join at exactly H
  bottleneck  least L at which a quiver reaches a non-isomorphic quiver of height <= its own (labelled minimax search)
  search15  Theorems 15.6 and 15.13: the same search for Q_t and R_b
  orbits    Theorem 15.1, Corollary 15.2 and Proposition 15.3 on random lines and exhaustively for small w
  vb        Proposition 15.8 (V_b)
  cor16     Corollary 16.7: the inequality and the least constant on 4 <= w < 4225
  prove16   re-evaluate the members and verdicts of np_corridor_prove.py at many integer points, including large t
"""
import argparse
import heapq
import itertools
import math
import random
import sys
from fractions import Fraction


# ----------------------------------------------------------------------------- labelled kernel
class Kernel:
    def __init__(self, n):
        self.n = n
        self.idx = {}
        c = 0
        for a in range(n):
            for b in range(a + 1, n):
                self.idx[(a, b)] = c
                c += 1
        self.m = c
        # for each vertex k: the index of b_{a k} with its sign, and the pairs (a, b) not containing k
        self.at = []
        for k in range(n):
            lst = []
            for a in range(n):
                if a == k:
                    continue
                if a < k:
                    lst.append((a, self.idx[(a, k)], 1))
                else:
                    lst.append((a, self.idx[(k, a)], -1))
            pairs = []
            for a in range(n):
                for b in range(a + 1, n):
                    if a != k and b != k:
                        pairs.append((a, b, self.idx[(a, b)]))
            self.at.append((lst, pairs))
        self.perms = list(itertools.permutations(range(n)))

    def entry(self, Q, a, b):
        if a == b:
            return 0
        return Q[self.idx[(a, b)]] if a < b else -Q[self.idx[(b, a)]]

    def mutate(self, Q, k):
        lst, pairs = self.at[k]
        bk = {}
        out = list(Q)
        for a, ix, s in lst:
            bk[a] = s * Q[ix]          # b_{a k}
            out[ix] = -Q[ix]
        for a, b, ix in pairs:
            x, y = bk[a], -bk[b]       # b_{ak}, b_{kb}
            if x > 0 and y > 0:
                out[ix] = Q[ix] + x * y
            elif x < 0 and y < 0:
                out[ix] = Q[ix] - x * y
        return tuple(out)

    def height(self, Q):
        return max(abs(e) for e in Q) if Q else 0

    def relabel(self, Q, p):
        # (p.Q)_{p(a) p(b)} = Q_{ab}
        out = [0] * self.m
        for (a, b), ix in self.idx.items():
            pa, pb = p[a], p[b]
            if pa < pb:
                out[self.idx[(pa, pb)]] = Q[ix]
            else:
                out[self.idx[(pb, pa)]] = -Q[ix]
        return tuple(out)

    def canon(self, Q):
        return max(self.relabel(Q, p) for p in self.perms)

    def neg(self, Q):
        return tuple(-e for e in Q)

    def from_matrix(self, B):
        return tuple(B[a][b] for a in range(self.n) for b in range(a + 1, self.n))

    def matrix(self, Q):
        return [[self.entry(Q, a, b) for b in range(self.n)] for a in range(self.n)]

    def is_acyclic(self, Q, vs=None):
        vs = set(range(self.n)) if vs is None else set(vs)
        while vs:
            src = [a for a in vs if not any(self.entry(Q, b, a) > 0 for b in vs if b != a)]
            if not src:
                return False
            vs -= set(src)
        return True

    def is_fork(self, Q):
        """Warkentin's fork (Ervin, Def. 2.5): abundant, not acyclic, a point of return r with
        b_ji > b_ir and b_ji > b_rj for every path i -> r -> j, and both sides of r acyclic."""
        n = self.n
        if any(abs(e) < 2 for e in Q):
            return False
        if self.is_acyclic(Q):
            return False
        for r in range(n):
            ins = [a for a in range(n) if a != r and self.entry(Q, a, r) > 0]
            outs = [b for b in range(n) if b != r and self.entry(Q, r, b) > 0]
            ok = all(self.entry(Q, j, i) > self.entry(Q, i, r) and self.entry(Q, j, i) > self.entry(Q, r, j)
                     for i in ins for j in outs)
            if ok and self.is_acyclic(Q, ins) and self.is_acyclic(Q, outs):
                return True
        return False


def bfs_below(K, start, L, limit=50_000_000, prune=None):
    """All labelled quivers reached from start through quivers of height <= L (start included)."""
    seen = {start}
    frontier = [start]
    while frontier:
        nxt = []
        for Q in frontier:
            for k in range(K.n):
                R = K.mutate(Q, k)
                if R in seen:
                    continue
                if max(abs(e) for e in R) > L:
                    continue
                if prune is not None and prune(R):
                    continue
                seen.add(R)
                nxt.append(R)
                if len(seen) > limit:
                    raise RuntimeError("limit")
        frontier = nxt
    return seen


def bottleneck_join(K, start, w, cap, budget=5_000_000, prune=None):
    """Least L such that start reaches, through heights <= L, a quiver of height <= w not isomorphic to start.
    Labelled minimax (Dijkstra on the maximum).  Returns (L, quiver) or (None, None) if nothing below cap."""
    c0 = K.canon(start)
    best = {start: K.height(start)}
    pq = [(K.height(start), start)]
    iso_cache = {}
    popped = 0
    while pq:
        d, Q = heapq.heappop(pq)
        if best.get(Q, None) != d:
            continue
        popped += 1
        if popped > budget:
            return ("budget", None)
        if K.height(Q) <= w and Q != start:
            c = iso_cache.get(Q)
            if c is None:
                c = K.canon(Q)
                iso_cache[Q] = c
            if c != c0:
                return (d, Q)
        for k in range(K.n):
            R = K.mutate(Q, k)
            h = K.height(R)
            if h > cap:
                continue
            if prune is not None and prune(R):
                continue
            nd = max(d, h)
            if nd < best.get(R, 1 << 200):
                best[R] = nd
                heapq.heappush(pq, (nd, R))
    return (None, None)


# ----------------------------------------------------------------------------- note 16 quivers
K5 = None
X, PV, QV, C1, C = 0, 1, 2, 3, 4


def k5():
    global K5
    if K5 is None:
        K5 = Kernel(5)
    return K5


def p_plus(t):
    # (b01, b02, b03, b04, b12, b13, b14, b23, b24, b34)
    return (1, -(t * t - 1), -t * (t - 1), t * t, -2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t)


def p_t(t):
    D = t * t // 2
    return (-t * t, t * t - D, 0, 2 * D, -2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t)


def Hplus(t):
    return 2 * t ** 5 - t ** 4 + t * t - 1


def Hp(t):
    return t * t + (2 * t ** 3 - t * t + 1) * (t * t // 2)


def Nof(t):
    return 2 * t ** 3 - t * t - t


def swap_pq(K, Q):
    return K.relabel(Q, (0, 2, 1, 3, 4))


def col(K, Q, e):
    return (K.entry(Q, PV, e), K.entry(Q, QV, e))


def cmd_route16(args):
    K = k5()
    bad = 0
    for t in range(args.tmin, args.tmax + 1):
        N = Nof(t)
        H = Hplus(t)
        for name, Q0, Htop in (("P+", p_plus(t), H), ("P", p_t(t), Hp(t))):
            if K.height(Q0) != t * t:
                bad += 1
                print("t=%d %s: height %d" % (t, name, K.height(Q0)))
            route = [Q0]
            Q = Q0
            for _ in range(t - 1):
                Q = swap_pq(K, K.mutate(Q, PV))
                route.append(Q)
            # check the column formulas of the table for P+
            if name == "P+":
                for jj, R in enumerate(route):
                    if jj == 0:
                        continue
                    exp_c1 = ((t - 1 - jj) * t, -(t - jj) * t)
                    exp_c = (t * t + jj * (2 * t * t - 1), -(t * t + (jj - 1) * (2 * t * t - 1)))
                    exp_x = (jj * t * t - 1, -((jj - 1) * t * t - 1))
                    if (col(K, R, C1), col(K, R, C), col(K, R, X)) != (exp_c1, exp_c, exp_x) or \
                            K.entry(R, C, C1) != 2 * t or K.entry(R, X, C) != 2 * t * t or K.entry(R, X, C1) != 0:
                        bad += 1
                        print("t=%d K(%d) mismatch" % (t, jj))
            Q = K.mutate(Q, C1)
            route.append(Q)
            for ii in range(N + 1):
                if name == "P+" and (ii < 3 or ii > N - 3 or ii % 997 == 0):
                    exp_c1 = (ii * t, -(ii - 1) * t)
                    exp_c = (N + 1 - ii, -(N + 2 - ii))
                    exp_x = ((t - 1 + ii) * t * t - 1, -((t - 2 + ii) * t * t - 1))
                    if (col(K, Q, C1), col(K, Q, C), col(K, Q, X)) != (exp_c1, exp_c, exp_x) or \
                            K.entry(Q, C1, C) != 2 * t or K.entry(Q, X, C) != 2 * t * t or K.entry(Q, X, C1) != 0:
                        bad += 1
                        print("t=%d L(%d) mismatch" % (t, ii))
                Q = swap_pq(K, K.mutate(Q, PV))
                route.append(Q)
            T = Q
            if name == "P+":
                if (col(K, T, C1), col(K, T, C), col(K, T, X)) != (((N + 1) * t, -N * t), (0, -1), ((t + N) * t * t - 1, -((t + N - 1) * t * t - 1))):
                    bad += 1
                    print("t=%d top mismatch" % t)
            mc, mp = K.mutate(T, C), K.mutate(T, PV)
            if mc != K.neg(mp):
                bad += 1
                print("t=%d %s: mu_c(T) != -mu_p(T)" % (t, name))
            hs = [K.height(R) for R in route]
            top = K.height(mc)
            if top != Htop or max(hs) > Htop - (t * t if name == "P+" else t * t // 2):
                bad += 1
                print("t=%d %s: top %d (expected %d), max on route %d" % (t, name, top, Htop, max(hs)))
            # full route to -Q0 by mirror
            full = route + [mc] + [K.neg(R) for R in reversed(route)]
            # verify consecutive quivers differ by one mutation (up to the name exchange)
            nm = 0
            for A, B in zip(full, full[1:]):
                ok = any(K.mutate(A, k) == B or swap_pq(K, K.mutate(A, k)) == B for k in range(5))
                if not ok:
                    bad += 1
                    print("t=%d %s: route break" % (t, name))
                    break
                nm += 1
            if name == "P+" and nm != 4 * t ** 3 - 2 * t * t + 4:
                bad += 1
                print("t=%d: %d mutations" % (t, nm))
            # heights: exactly one quiver at Htop
            allh = [K.height(R) for R in full]
            if allh.count(Htop) != 1 or max(allh) != Htop:
                bad += 1
                print("t=%d %s: %d quivers at the top" % (t, name, allh.count(Htop)))
            # not isomorphic to the opposite
            if K.canon(Q0) == K.canon(K.neg(Q0)):
                bad += 1
                print("t=%d %s: isomorphic to opposite" % (t, name))
            # in-weights / out-weights argument of the proof
            if name == "P+":
                inw = sum(max(K.entry(Q0, a, PV), 0) for a in range(5))
                outs = sorted(sum(max(K.entry(Q0, a, b), 0) for b in range(5)) for a in range(5))
                if inw != 3 or 3 in outs:
                    bad += 1
                    print("t=%d: in-weight of p %d, out-weights %s" % (t, inw, outs))
        if args.verbose:
            print("t=%d ok so far (bad=%d)" % (t, bad), flush=True)
    print("route16: t = %d..%d, failures: %d" % (args.tmin, args.tmax, bad))
    return 0 if bad == 0 else 1


def _search16_task(task):
    t, name = task
    K = k5()
    Q0 = p_plus(t) if name == "P+" else p_t(t)
    H = Hplus(t) if name == "P+" else Hp(t)
    S = bfs_below(K, Q0, H - 1)
    low = [Q for Q in S if K.height(Q) <= t * t]
    c0 = K.canon(Q0)
    lowc = {K.canon(Q) for Q in low}
    other = len([c for c in lowc if c != c0])
    return (t, name, H, len(S), len(low), len(lowc), other, max(K.height(Q) for Q in S))


def cmd_search16(args):
    if args.procs > 1:
        import multiprocessing as mp
        tasks = sorted(((t, f) for t in args.t for f in args.fam), key=lambda x: -x[0])
        tot = 0
        with mp.Pool(args.procs) as pool:
            for res in pool.imap_unordered(_search16_task, tasks):
                t, name, H, nS, nlow, nlowc, other, hmax = res
                tot += other
                print("t=%d %s H=%d: labelled quivers below H: %d; labelled of height <= t^2: %d; iso classes among them: %d; "
                      "other than start: %d; highest reached %d" % res, flush=True)
        print("search16: other low quivers found below H: %d" % tot)
        return 0 if tot == 0 else 1
    K = k5()
    tot = 0
    for t in args.t:
        for name in args.fam:
            Q0 = p_plus(t) if name == "P+" else p_t(t)
            H = Hplus(t) if name == "P+" else Hp(t)
            S = bfs_below(K, Q0, H - 1)
            low = [Q for Q in S if K.height(Q) <= t * t]
            c0 = K.canon(Q0)
            lowc = {K.canon(Q) for Q in low}
            other = [c for c in lowc if c != c0]
            msg = "t=%d %s H=%d: labelled quivers below H: %d; labelled of height <= t^2: %d; iso classes among them: %d; other than start: %d" % (
                t, name, H, len(S), len(low), len(lowc), len(other))
            if args.classes:
                msg += "; iso classes below H: %d" % len({K.canon(Q) for Q in S})
            print(msg, flush=True)
            tot += len(other)
            if args.at_H:
                S2 = bfs_below(K, Q0, H)
                low2 = {K.canon(Q) for Q in S2 if K.height(Q) <= t * t}
                print("   at bound H: classes of height <= t^2: %d; opposite reached: %s" % (
                    len(low2), K.canon(K.neg(Q0)) in low2), flush=True)
    print("search16: other low quivers found below H: %d" % tot)
    return 0 if tot == 0 else 1


# ----------------------------------------------------------------------------- note 15 quivers
def q_t(t):
    return (-t * t, -(t * t - 1), 2 * t, -2, t * (t - 1), -t * t)


def r_b(b):
    return (-b, -b, b - 1, -2, b - 2, -b)


def H_t(t):
    return 2 * t ** 4 - t ** 3 - t * t + 2 * t


def H_b(b):
    return 2 * b * b - 3 * b - 3


def cmd_search15(args):
    K = Kernel(4)
    bad = 0
    for t in args.t:
        Q0 = q_t(t)
        H = H_t(t)
        S = bfs_below(K, Q0, H - 1)
        lowc = {K.canon(Q) for Q in S if K.height(Q) <= t * t}
        S2 = bfs_below(K, Q0, H)
        low2 = {K.canon(Q) for Q in S2 if K.height(Q) <= t * t}
        ok = len(lowc) == 1 and K.canon(K.neg(Q0)) in low2 and K.canon(Q0) != K.canon(K.neg(Q0))
        bad += not ok
        print("Q_%d: height %d, H_t = %d; labelled below H: %d (classes %d); low classes below H: %d; at H: %d, opposite reached %s; %s" % (
            t, K.height(Q0), H, len(S), len({K.canon(Q) for Q in S}), len(lowc), len(low2), K.canon(K.neg(Q0)) in low2,
            "ok" if ok else "FAIL"), flush=True)
    for b in args.b:
        Q0 = r_b(b)
        H = H_b(b)
        S = bfs_below(K, Q0, H - 1)
        lowc = {K.canon(Q) for Q in S if K.height(Q) <= b}
        S2 = bfs_below(K, Q0, H)
        low2 = {K.canon(Q) for Q in S2 if K.height(Q) <= b}
        ok = len(lowc) == 1 and K.canon(K.neg(Q0)) in low2 and K.canon(Q0) != K.canon(K.neg(Q0)) and K.height(Q0) == b
        bad += not ok
        print("R_%d: height %d, 2b^2-3b-3 = %d; labelled below H: %d (classes %d); low classes below H: %d; at H: %d, opposite reached %s; %s" % (
            b, K.height(Q0), H, len(S), len({K.canon(Q) for Q in S}), len(lowc), len(low2), K.canon(K.neg(Q0)) in low2,
            "ok" if ok else "FAIL"), flush=True)
    print("search15: failures %d" % bad)
    return 0 if bad == 0 else 1


def cmd_bottleneck(args):
    n = args.n
    K = Kernel(n)
    Q = tuple(int(x) for x in args.quiver.split(","))
    w = K.height(Q) if args.w is None else args.w
    iso = all(K.height(K.mutate(Q, k)) > w for k in range(n))
    L, R = bottleneck_join(K, Q, w, args.cap, args.budget)
    print("quiver %s, n=%d, w=%d, isolated=%s: least join level %s, reached %s; opposite? %s" % (
        Q, n, w, iso, L, R, (R is not None and K.canon(R) == K.canon(K.neg(Q)))), flush=True)
    return 0


# ----------------------------------------------------------------------------- Theorem 15.1 and friends
def lam(c, xk, yk, xl, yl, z):
    """Lambda_c(x_k, y_k; x_l, y_l; z) in the vertex order (i, j, k, l): (c, -x_k, -x_l, -y_k, -y_l, z)."""
    return (c, -xk, -xl, -yk, -yl, z)


def coords(Q):
    c, mxk, mxl, myk, myl, z = Q
    return c, -mxk, -myk, -mxl, -myl, z


def cmd_orbits(args):
    K = Kernel(4)
    rng = random.Random(args.seed)
    bad = 0
    pos = lambda a: max(a, 0)
    # (1) step formula and inverse, (2) invariant, on random quivers with b_ij = c >= 0
    for trial in range(args.samples):
        c = rng.randint(0, 6)
        xk, yk, xl, yl, z = (rng.randint(-40, 40) for _ in range(5))
        Q = lam(c, xk, yk, xl, yl, z)
        R = K.mutate(Q, 0)                      # mutate at i = 0
        R = K.relabel(R, (1, 0, 2, 3))          # exchange the names of i and j
        sx = lambda x, y: (y + c * pos(x), -x)
        nk, nl = sx(xk, yk), sx(xl, yl)
        nz = z + pos(xk) * pos(-xl) - pos(-xk) * pos(xl)
        if R != lam(c, nk[0], nk[1], nl[0], nl[1], nz):
            bad += 1
            if bad < 5:
                print("step mismatch", Q, R)
        Pinv = lambda q: q[0] * q[5] - (coords(q)[1] * coords(q)[4] - coords(q)[3] * coords(q)[2])
        if Pinv(Q) != Pinv(R):
            bad += 1
        pf = lambda q: q[0] * q[5] - q[1] * q[4] + q[2] * q[3]
        if abs(Pinv(Q)) != abs(pf(Q)):
            bad += 1
        # backward step is the inverse
        Bk = K.relabel(K.mutate(R, 1), (1, 0, 2, 3))
        if Bk != Q:
            bad += 1
    print("orbits: %d random steps: step formula, inverse, P invariant and |P| = |Pf|: failures %d" % (args.samples, bad), flush=True)

    # (3) column types and (4) valley, for c = 2..6: closed forms for columns with a bottom
    bad3 = 0
    ncol = 0
    for c in range(2, 7):
        for x0 in range(-12, 13):
            for y0 in range(-12, 13):
                if (x0, y0) == (0, 0):
                    continue
                ncol += 1
                sx = lambda x, y: (y + c * pos(x), -x)
                sinv = lambda x, y: (-y, x - c * pos(-y))
                seq = {0: (x0, y0)}
                for s in range(1, 30):
                    seq[s] = sx(*seq[s - 1])
                    seq[-s] = sinv(*seq[-(s - 1)])
                xs = {n: seq[n][0] for n in seq}
                neg = [n for n in sorted(seq) if xs[n] < 0]
                if neg:
                    # with a bottom: the bottom t is the position after the first negative x
                    tb = neg[0] + 1
                    if tb not in seq or tb + 12 not in seq or tb - 12 not in seq:
                        continue
                    e = -xs[tb]
                    a = seq[tb][1]
                    if not (a >= 1 and e >= 0):
                        bad3 += 1
                        continue
                    p = [-e, a]
                    q = [-a, e]
                    for _ in range(30):
                        p.append(c * p[-1] - p[-2])
                        q.append(c * q[-1] - q[-2])
                    for mm in range(1, 12):
                        if seq[tb + mm] != (p[mm], -p[mm - 1]):
                            bad3 += 1
                        if seq[tb - mm] != (q[mm - 1], -q[mm]):
                            bad3 += 1
                    # x negative at t-1, non-positive at t, non-negative elsewhere
                    if not (xs[tb - 1] < 0 and xs[tb] <= 0):
                        bad3 += 1
                    for nn in seq:
                        if nn not in (tb - 1, tb) and xs[nn] < 0:
                            bad3 += 1
                else:
                    # always cyclic: x > 0 > y everywhere
                    if not all(seq[nn][0] > 0 > seq[nn][1] for nn in seq):
                        bad3 += 1
                # valley: W is non-increasing and then non-decreasing
                W = [max(abs(seq[nn][0]), abs(seq[nn][1])) for nn in range(-29, 30)]
                up = [s_ for s_ in range(len(W) - 1) if W[s_ + 1] > W[s_]]
                down = [s_ for s_ in range(len(W) - 1) if W[s_ + 1] < W[s_]]
                if up and down and min(up) < max(down):
                    bad3 += 1
    print("orbits: %d columns with c = 2..6: closed forms, sign pattern, valley: failures %d" % (ncol, bad3), flush=True)

    # Corollary 15.2 on random weight-2 lines
    bad2 = 0
    ntest = 0
    for trial in range(args.samples):
        c = 2
        xk, yk, xl, yl, z = (rng.randint(-15, 15) for _ in range(5))
        Q = lam(c, xk, yk, xl, yl, z)
        line = {0: Q}
        cur = Q
        for s in range(1, 60):
            cur = K.relabel(K.mutate(cur, 0), (1, 0, 2, 3))
            line[s] = cur
        cur = Q
        for s in range(1, 60):
            cur = K.relabel(K.mutate(cur, 1), (1, 0, 2, 3))
            line[-s] = cur
        # find bottoms: first position where x < 0, plus one
        def bottom(which):
            xsn = [(n, coords(line[n])[1 if which == 'k' else 3]) for n in sorted(line)]
            negs = [n for n, xv in xsn if xv < 0]
            if not negs:
                return None
            tb = negs[0] + 1
            return tb if tb in line else None
        tk, tl = bottom('k'), bottom('l')
        if tk is None or tl is None or tl - tk < 2 or tl > 55 or tk < -55:
            continue
        D = tl - tk
        cc = coords(line[tk])
        ak, ek = coords(line[tk])[2], -coords(line[tk])[1]
        al, el = coords(line[tl])[4], -coords(line[tl])[3]
        sk, sl = ak + ek, al + el
        zs = {line[nn][5] for nn in range(tk + 1, tl)}
        if len(zs) != 1:
            bad2 += 1
            continue
        zeta = zs.pop()
        P_ = Q[0] * Q[5] - (coords(Q)[1] * coords(Q)[4] - coords(Q)[3] * coords(Q)[2])
        ntest += 1
        if sk * sl * (D - 3) + sl * ak + sk * el != P_ - 2 * zeta:
            bad2 += 1
    print("orbits: Corollary 15.2 on %d random weight-2 lines with D >= 2: failures %d" % (ntest, bad2), flush=True)

    # Proposition 15.3, exhaustively for small w and c = |b_ij| >= 2 (labelled lines, forward walks)
    for w in range(2, args.wmax + 1):
        worst = {}
        over = 0
        for c in range(2, w + 1):
            worst[c] = (0, None)
            for vals in itertools.product(range(-w, w + 1), repeat=5):
                Q = lam(c, *vals)
                if K.height(Q) != w:
                    continue
                cur = Q
                mx = 0
                for s_ in range(1, 4 * w * w + 40):
                    cur = K.relabel(K.mutate(cur, 0), (1, 0, 2, 3))
                    h = K.height(cur)
                    if h <= w:
                        if mx > worst[c][0]:
                            worst[c] = (mx, Q)
                        if mx > w * w + w:
                            over += 1
                        break
                    mx = max(mx, h)
                    if h > 10 ** 12:
                        break
        print("orbits: w=%d: largest height strictly between consecutive positions of height <= w, from a start of height w, by c: %s; above w^2+w: %d" % (
            w, {c_: v_[0] for c_, v_ in worst.items()}, over), flush=True)
        if w >= 4:
            print("        extremes: %s" % {c_: v_[1] for c_, v_ in worst.items()})
        bad += over
    return 0 if bad == bad2 == bad3 == 0 else 1


# ----------------------------------------------------------------------------- Proposition 15.8
def cyclic_orders(n):
    out = []
    for p in itertools.permutations(range(1, n)):
        out.append((0,) + p)
    return out


def proper_vertex(B, order, j):
    """FN: j is proper if every path i -> j -> k turns right: clockwise from i, j is met before k."""
    n = len(order)
    posn = {v: s for s, v in enumerate(order)}

    def cw(a, b):  # clockwise distance from a to b
        return (posn[b] - posn[a]) % n
    for i in range(n):
        for k in range(n):
            if i in (j, k) or k == j:
                continue
            if B[i][j] > 0 and B[j][k] > 0:
                if not (cw(i, j) < cw(i, k)):
                    return False
    return True


def unipotent(B, order):
    n = len(order)
    U = [[Fraction(0)] * n for _ in range(n)]
    for a in range(n):
        U[a][a] = Fraction(1)
        for b in range(a + 1, n):
            U[a][b] = Fraction(-B[order[a]][order[b]])
    return U


def matinv(Mx):
    n = len(Mx)
    A = [list(r) + [Fraction(int(i == j)) for j in range(n)] for i, r in enumerate(Mx)]
    for col_ in range(n):
        piv = next(r for r in range(col_, n) if A[r][col_] != 0)
        A[col_], A[piv] = A[piv], A[col_]
        pv = A[col_][col_]
        A[col_] = [x / pv for x in A[col_]]
        for r in range(n):
            if r != col_ and A[r][col_] != 0:
                f = A[r][col_]
                A[r] = [x - f * y for x, y in zip(A[r], A[col_])]
    return [r[n:] for r in A]


def markov_value(B, order):
    """M = n - tr(U^{-T} U) (Fomin-Neville)."""
    U = unipotent(B, order)
    n = len(U)
    Ui = matinv(U)
    UiT = [[Ui[j][i] for j in range(n)] for i in range(n)]
    tr = sum(sum(UiT[a][s] * U[s][a] for s in range(n)) for a in range(n))
    return n - tr


def cmd_vb(args):
    K = Kernel(4)
    bad = 0
    for b in range(3, args.bmax + 1):
        V = (-b, 2, -1, -b, 1, 1)
        c0 = K.canon(V)
        hs = [K.height(K.mutate(V, k)) for k in range(4)]
        rel = [K.canon(K.mutate(V, k)) == c0 for k in range(4)]
        if not (rel[0] and rel[2] and hs[3] == b + 1 and hs[1] == b * b - 2):
            bad += 1
            print("b=%d: heights %s, relabellings %s" % (b, hs, rel))
        X1 = K.mutate(V, 3)
        X2 = K.mutate(X1, 0)
        X3 = K.mutate(X2, 2)
        path = [K.height(X1), K.height(X2), K.height(X3)]
        if K.canon(X3) != K.canon(K.neg(V)) or path != [b + 1, b + 1, b] or c0 == K.canon(K.neg(V)):
            bad += 1
            print("b=%d: path heights %s, end is -V %s, V iso -V %s" % (b, path, K.canon(X3) == K.canon(K.neg(V)), c0 == K.canon(K.neg(V))))
        # the only quivers of height <= b reachable at height <= b are relabellings of V
        S = bfs_below(K, V, b)
        if {K.canon(Q) for Q in S} != {c0}:
            bad += 1
        B = K.matrix(V)
        props = [o for o in cyclic_orders(4) if all(proper_vertex(B, o, j) for j in range(4))]
        Ms = [markov_value(B, o) for o in props]
        pf = V[0] * V[5] - V[1] * V[4] + V[2] * V[3]
        if b <= args.show or len(props) != 1 or Ms != [5] or pf != -2:
            print("b=%d: proper cyclic orders %s, Markov values %s, Pf %d" % (b, props, Ms, pf))
            if len(props) != 1 or Ms != [5] or pf != -2:
                bad += 1
    print("vb: b = 3..%d, failures %d" % (args.bmax, bad))
    return 0 if bad == 0 else 1


# ----------------------------------------------------------------------------- Corollary 16.7
def cmd_cor16(args):
    bad = 0
    worst = 0
    exc = []
    for w in range(4, args.wmax):
        t = math.isqrt(w)
        Hv = Hplus(t)
        # least constant C with Hv >= 2 w^{5/2} - C w^2  <=>  C >= (2 w^{5/2} - Hv) / w^2
        Cw = (2 * w ** 2.5 - Hv) / w ** 2
        worst = max(worst, Cw)
        if not (Hv >= 2 * w ** 2.5 - 11 * w * w):
            bad += 1
        if not (Hv > 2 * w * w):
            exc.append(w)
    print("cor16: 4 <= w < %d: H+(floor sqrt w) >= 2 w^{5/2} - 11 w^2 fails %d times; least constant %.4f; H+ <= 2w^2 at w in %s" % (
        args.wmax, bad, worst, exc[:20]))
    # the polynomial inequality 2(s-1)^5 - (s-1)^4 >= 2 s^5 - 11 s^4 for s >= 2: difference 24s^3 - 26s^2 + 14s - 3
    diff = lambda s: 2 * (s - 1) ** 5 - (s - 1) ** 4 - (2 * s ** 5 - 11 * s ** 4)
    print("cor16: difference at s = 2, 3, 10: %s (closed form 24s^3 - 26s^2 + 14s - 3: %s)" % (
        [diff(s) for s in (2, 3, 10)], [24 * s ** 3 - 26 * s * s + 14 * s - 3 for s in (2, 3, 10)]))
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("route16")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=40)
    s.add_argument("--verbose", action="store_true")
    s = sub.add_parser("search16")
    s.add_argument("--t", type=int, nargs="+", default=[2, 3, 4, 5])
    s.add_argument("--fam", nargs="+", default=["P+", "P"])
    s.add_argument("--classes", action="store_true")
    s.add_argument("--at-H", action="store_true")
    s.add_argument("--procs", type=int, default=1)
    s = sub.add_parser("search15")
    s.add_argument("--t", type=int, nargs="*", default=[3, 4, 5])
    s.add_argument("--b", type=int, nargs="*", default=[5, 6, 7, 8])
    s = sub.add_parser("bottleneck")
    s.add_argument("--n", type=int, default=5)
    s.add_argument("--quiver", required=True)
    s.add_argument("--w", type=int, default=None)
    s.add_argument("--cap", type=int, default=2000)
    s.add_argument("--budget", type=int, default=3_000_000)
    s = sub.add_parser("orbits")
    s.add_argument("--samples", type=int, default=50000)
    s.add_argument("--seed", type=int, default=11)
    s.add_argument("--wmax", type=int, default=5)
    s = sub.add_parser("vb")
    s.add_argument("--bmax", type=int, default=60)
    s.add_argument("--show", type=int, default=4)
    s = sub.add_parser("cor16")
    s.add_argument("--wmax", type=int, default=4225)
    args = ap.parse_args()
    sys.exit(globals()["cmd_" + args.cmd](args))


if __name__ == "__main__":
    main()
