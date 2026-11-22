"""Tube certificates for the 4-vertex census classes whose core search does not stop (n4_opposite.py).

For a start quiver x that certainly lies in the core, the script tries to prove

    V'(x)  is contained in  E  union  R,

where E is a finite set of concrete quivers (reached from x by allowed steps through quivers of level <= L
that are not members of R) and R is a finite union of families {Y(n) : n >= 0}.  A family is a triple of
labelled quivers (Y(0), Y(1), Y(2)) and an integer tau >= 2; every entry is continued by

    e(n+3) = (tau+1) e(n+2) - (tau+1) e(n+1) + e(n),   i.e.  D(n+2) = tau D(n+1) - D(n) for D(n) = e(n+1) - e(n).

The families are sets defined by this rule.  Soundness comes only from the closure check: every allowed
step from a member of E or R is shown to land in E or R.  All facts "for all n" are certified by

    D(1) >= D(0) >= 0  implies  D(n+1) >= D(n) >= 0 for all n      (tau >= 2),

through the class Seq, on which the unchanged functions of n4_opposite.py (mutate, fork_return,
prefork_returns, exit_returns) are run.  A comparison that is not certified raises Undetermined and the
attempt is abandoned.

  run         all census classes with "ex": false in n4_opposite_cores.jsonl.gz
  validate    Seq unit tests, comparison with brute force, replay of the closure, broken certificates
  crosscheck  the certified classes against the census mirror map (needs n4_opposite_plateaus.jsonl.gz)
  summary     the tables of a finished run
  one         one quiver, verbose
Run from experiments/ with python -I.
"""
import argparse
import gzip
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n4_opposite as O


class Undetermined(Exception):
    pass


class Nonlinear(Exception):
    pass


class Abort(Exception):
    pass


# ----------------------------------------------------------------------------- certified facts on a triple
def _inc(e):
    return e[1] - e[0] >= 0 and e[2] - e[1] >= e[1] - e[0]


def _dec(e):
    return e[1] - e[0] <= 0 and e[2] - e[1] <= e[1] - e[0]


def t_pos(e):          # e(n) > 0 for all n >= 0, and non-decreasing
    return e[0] > 0 and _inc(e)


def t_nonneg(e):
    return e[0] >= 0 and _inc(e)


def t_neg(e):
    return e[0] < 0 and _dec(e)


def t_nonpos(e):
    return e[0] <= 0 and _dec(e)


def gt0(e):
    if t_pos(e):
        return True
    if t_nonpos(e):
        return False
    raise Undetermined()


def ge0(e):
    if t_nonneg(e):
        return True
    if t_neg(e):
        return False
    raise Undetermined()


def _tr(o):
    if isinstance(o, Seq):
        return o.e
    if isinstance(o, int):
        return (o, o, o)
    return None


class SignProduct:
    """The product of two non-constant sequences: only its sign (constant in n) is known."""
    __slots__ = ("s",)

    def __init__(self, s):
        self.s = s

    def _chk(self, o):
        if not (isinstance(o, int) and o == 0):
            raise Nonlinear()

    def __le__(self, o):
        self._chk(o)
        return self.s <= 0

    def __lt__(self, o):
        self._chk(o)
        return self.s < 0

    def __ge__(self, o):
        self._chk(o)
        return self.s >= 0

    def __gt__(self, o):
        self._chk(o)
        return self.s > 0

    def _bad(self, *a):
        raise Nonlinear()

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __neg__ = __abs__ = _bad


class Seq:
    """An integer sequence given by three consecutive values, continued by the recurrence."""
    __slots__ = ("e",)

    def __init__(self, e0, e1, e2):
        self.e = (e0, e1, e2)

    def const(self):
        return self.e[0] == self.e[1] == self.e[2]

    def sign(self):
        if t_pos(self.e):
            return 1
        if t_neg(self.e):
            return -1
        if self.e == (0, 0, 0):
            return 0
        raise Undetermined()

    def __neg__(self):
        return Seq(-self.e[0], -self.e[1], -self.e[2])

    def __abs__(self):
        if t_nonneg(self.e):
            return self
        if t_nonpos(self.e):
            return -self
        raise Undetermined()

    def __add__(self, o):
        if isinstance(o, SignProduct):
            raise Nonlinear()
        t = _tr(o)
        return Seq(self.e[0] + t[0], self.e[1] + t[1], self.e[2] + t[2])

    __radd__ = __add__

    def __sub__(self, o):
        if isinstance(o, SignProduct):
            raise Nonlinear()
        t = _tr(o)
        return Seq(self.e[0] - t[0], self.e[1] - t[1], self.e[2] - t[2])

    def __rsub__(self, o):
        t = _tr(o)
        return Seq(t[0] - self.e[0], t[1] - self.e[1], t[2] - self.e[2])

    def __mul__(self, o):
        if isinstance(o, int):
            return Seq(o * self.e[0], o * self.e[1], o * self.e[2])
        if isinstance(o, Seq):
            if self.const():
                c = self.e[0]
                return Seq(c * o.e[0], c * o.e[1], c * o.e[2])
            if o.const():
                c = o.e[0]
                return Seq(c * self.e[0], c * self.e[1], c * self.e[2])
            return SignProduct(self.sign() * o.sign())
        raise Nonlinear()

    __rmul__ = __mul__

    def _d(self, o):
        t = _tr(o)
        return (self.e[0] - t[0], self.e[1] - t[1], self.e[2] - t[2])

    def __gt__(self, o):
        return gt0(self._d(o))

    def __lt__(self, o):
        d = self._d(o)
        return gt0((-d[0], -d[1], -d[2]))

    def __ge__(self, o):
        return ge0(self._d(o))

    def __le__(self, o):
        d = self._d(o)
        return ge0((-d[0], -d[1], -d[2]))

    def __eq__(self, o):
        d = self._d(o)
        if d == (0, 0, 0):
            return True
        if t_pos(d) or t_neg(d):
            return False
        raise Undetermined()

    def __ne__(self, o):
        return not self.__eq__(o)

    __hash__ = None

    def __repr__(self):
        return f"Seq{self.e}"


# ----------------------------------------------------------------------------- families
def relab(t, pi):
    return tuple(s * t[a] for a, s in O.RELAB[pi])


def canon_triple(Y):
    """The largest (Y(0), Y(1), Y(2)) over the 24 simultaneous relabellings (lexicographic order)."""
    y0, y1, y2 = Y
    best = None
    ties = []
    for pi, r in enumerate(O.RELAB):
        c = tuple(sg * y0[a] for a, sg in r)
        if best is None or c > best:
            best = c
            ties = [pi]
        elif c == best:
            ties.append(pi)
    return max((best, relab(y1, pi), relab(y2, pi)) for pi in ties)


# composition of relabellings: relab(relab(t, p), q) = relab(t, COMP[p][q])
_PIDX = {p: a for a, p in enumerate(O.PERMS)}
COMP = [[_PIDX[tuple(p[q[i]] for i in range(4))] for q in O.PERMS] for p in O.PERMS]


def nxt(Y, tau):
    return tuple((tau + 1) * (c - b) + a for a, b, c in zip(Y[0], Y[1], Y[2]))


def prv(Y, tau):
    return tuple((tau + 1) * (a - b) + c for a, b, c in zip(Y[0], Y[1], Y[2]))


def shift(Y, d, tau):
    """The triple (Y(d), Y(d+1), Y(d+2))."""
    Y = tuple(Y)
    while d > 0:
        Y = (Y[1], Y[2], nxt(Y, tau))
        d -= 1
    while d < 0:
        Y = (prv(Y, tau), Y[0], Y[1])
        d += 1
    return Y


def seqs(Y):
    return tuple(Seq(Y[0][a], Y[1][a], Y[2][a]) for a in range(6))


def definite(e):
    return e[0] == e[1] == e[2] or t_pos(e) or t_neg(e)


SHIFTS = (0, 1, 2, 3, -1, -2, -3)


def close(base, tau, known, node_cap=80):
    """The closure check from the family `base`.  known: nodes already certified (key -> triple).
    Returns (new nodes, concrete 'downward' quivers that must lie in E or R).  Raises Abort."""
    new = {}
    D = []
    k0 = (tau, canon_triple(base))
    if k0 in known:
        return new, D
    new[k0] = k0[1]
    queue = [k0]
    while queue:
        key = queue.pop()
        Y = key[1]
        S = seqs(Y)
        for s in S:
            if not definite(s.e):
                raise Abort("an entry of a family is not certified constant or sign-definite")
        exY = None
        for m in range(4):
            Yp = tuple(O.mutate(y, m) for y in Y)
            try:
                Sp = O.mutate(S, m)
            except Undetermined:
                raise Abort("undetermined comparison: mutation of a family")
            except Nonlinear:
                # m is the big vertex: every other entry must be constant; the step is then a strict
                # up-exit for all n as soon as it is one at n = 0 (monotonicity)
                for a, (i, j) in enumerate(O.PAIRS):
                    if m not in (i, j) and not S[a].const():
                        raise Abort("nonlinear step with a varying entry away from the vertex")
                try:
                    if exY is None:
                        exY = O.exit_returns(S)
                except Undetermined:
                    raise Abort("undetermined comparison: exits of a family")
                if m in exY:
                    raise Abort("nonlinear step from an exit")
                if not all(m in O.exit_returns(y) for y in Yp):
                    raise Abort("nonlinear step that is not an exit")
                continue
            if any(Sp[a].e != (Yp[0][a], Yp[1][a], Yp[2][a]) for a in range(6)):
                raise Abort("internal: symbolic and concrete mutation differ")
            # the mutated family is linear in n, so it is the family of the triple Yp.  If it is a shift of
            # a known family, its members are in R whether or not the step is allowed.
            found = False
            for d in SHIFTS:
                kz = (tau, canon_triple(shift(Yp, -d, tau)))
                if kz in known or kz in new:
                    for j in range(-d if d < 0 else 0):     # Y'(0), ..., Y'(|d|-1) lie below the family
                        if not (m not in O.exit_returns(Y[j]) and m in O.exit_returns(Yp[j])):
                            D.append(Yp[j])                 # reached by an allowed step: must lie in E or R
                    found = True
                    break
            if found:
                continue
            try:
                if exY is None:
                    exY = O.exit_returns(S)
                exYp = O.exit_returns(Sp)
            except Undetermined:
                raise Abort("undetermined comparison: exits of a neighbour family")
            if m not in exY and m in exYp:
                continue                                    # strict up-exit step for every n
            kz = (tau, canon_triple(Yp))
            if len(new) >= node_cap:
                raise Abort("node cap")
            new[kz] = kz[1]
            queue.append(kz)
    return new, D


def _mat_mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


class Family:
    """One family {Y(n) : n >= 0}; Y(n) is computed directly for any n."""

    def __init__(self, tau, Y):
        self.tau = tau
        self.c = [Y[0], Y[1], Y[2]]
        self.const = Y[0] == Y[1] == Y[2]
        self.w0 = O.weight(Y[0])
        self.far = {}

    def get(self, n):
        c = self.c
        tau = self.tau
        if n < 2048:
            while len(c) <= n:
                c.append(tuple((tau + 1) * (c[-1][a] - c[-2][a]) + c[-3][a] for a in range(6)))
            return c[n]
        r = self.far.get(n)
        if r is None:
            # (e(n), e(n+1), e(n+2)) = C^n (e(0), e(1), e(2))
            P = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
            C = [[0, 1, 0], [0, 0, 1], [1, -(tau + 1), tau + 1]]
            k = n
            while k:
                if k & 1:
                    P = _mat_mul(P, C)
                C = _mat_mul(C, C)
                k >>= 1
            r = tuple(P[0][0] * c[0][a] + P[0][1] * c[1][a] + P[0][2] * c[2][a] for a in range(6))
            self.far[n] = r
        return r

    def contains(self, q, w):
        """Is the canonical quiver q (of total weight w) a member?  The total weight of Y(n) is
        non-decreasing in n, and increasing from n = 1 on unless the family is constant."""
        if w < self.w0:
            return False
        if self.const:
            return O.canon(self.c[0]) == q
        hi = 1
        while O.weight(self.get(hi)) < w:
            hi *= 2
            if hi > 1 << 60:
                return False
        lo = 0
        while lo < hi:                                  # least n with weight >= w
            mid = (lo + hi) // 2
            if O.weight(self.get(mid)) < w:
                lo = mid + 1
            else:
                hi = mid
        n = lo
        while O.weight(self.get(n)) == w:
            if O.canon(self.get(n)) == q:
                return True
            n += 1
            if n > lo + 3:
                break
        return False


class Members:
    """The union R of the families."""

    def __init__(self):
        self.fams = {}
        self.yes = set()
        self.no = set()

    def add(self, nodes):
        for key, Y in nodes.items():
            if key not in self.fams:
                self.fams[key] = Family(key[0], Y)
                self.no = set()

    def __contains__(self, q):
        if q in self.yes:
            return True
        if q in self.no:
            return False
        w = O.weight(q)
        for f in self.fams.values():
            if f.contains(q, w):
                self.yes.add(q)
                return True
        self.no.add(q)
        return False


def exits(t, cache):
    r = cache.get(t)
    if r is None:
        r = cache[t] = O.exit_returns(t)
    return r


def bfs_E(seeds, L, mem, cache, cap=1000):
    """Quivers reached from the seeds by allowed steps through quivers of level <= L that are not members
    of a family.  Returns (E: canonical quiver -> level, frontier: canonical quivers of level > L)."""
    E = {}
    frontier = {}
    todo = []
    for s in seeds:
        if s not in E:
            E[s] = O.level(s)
            todo.append(s)
    while todo:
        x = todo.pop()
        ex_x = exits(x, cache)
        for m in range(4):
            y = O.mutate(x, m)
            if m not in ex_x and m in exits(y, cache):
                continue
            c = O.canon(y)
            if c in E or c in frontier:
                continue
            if c in mem:
                continue
            lv = O.level(c)
            if lv > L:
                frontier[c] = lv
                continue
            if len(E) >= cap:
                raise Abort("E cap")
            E[c] = lv
            todo.append(c)
    return E, frontier


def forward_path(f, cache, steps=130, maxlev=10 ** 150):
    """Follow allowed steps from f, each time to the unvisited quiver of largest level."""
    ys = [f]
    seen = {O.canon(f)}
    y = f
    for _ in range(steps):
        best = None
        ex_y = exits(y, cache)
        for m in range(4):
            z = O.mutate(y, m)
            if m not in ex_y and m in exits(z, cache):
                continue
            c = O.canon(z)
            if c in seen:
                continue
            lz = O.level(z)
            if best is None or lz > best[0]:
                best = (lz, c, z)
        if best is None:
            break
        y = best[2]
        seen.add(best[1])
        ys.append(y)
        if best[0] > maxlev:
            break
    return ys


def _signs(t):
    return tuple((x > 0) - (x < 0) for x in t)


def base_candidates(ys, max_period=24, max_shift=3):
    """Triples (X(0), X(1), X(2)) read off a forward path: X(i) is y_{s+ip} relabelled i times by one
    permutation, with X(3) agreeing with the recurrence for one integer tau >= 2.  Yields (s, p, tau, X),
    smallest period first; for each period the offsets 0, 1, ..., then whole periods further up."""
    n = len(ys)
    rel = {}

    def R(i):
        r = rel.get(i)
        if r is None:
            r = rel[i] = [relab(ys[i], pi) for pi in range(24)]
        return r

    seen = set()
    for p in range(1, max_period + 1):
        if 3 * p >= n:
            break
        offs = []
        for k in range(max_shift + 1):
            for s0 in range(0, p):
                s = s0 + k * p
                if s + 3 * p < n:
                    offs.append(s)
        for s in offs:
            X0 = ys[s]
            sg0 = _signs(X0)
            r1, r2, r3 = R(s + p), R(s + 2 * p), R(s + 3 * p)
            for pi in range(24):
                X1 = r1[pi]
                if _signs(X1) != sg0:
                    continue
                p2 = COMP[pi][pi]
                X2 = r2[p2]
                X3 = r3[COMP[p2][pi]]
                tau = None
                ok = True
                for a in range(6):
                    e = (X0[a], X1[a], X2[a], X3[a])
                    if e[0] == e[1] == e[2] == e[3]:
                        continue
                    d0, d1, d2 = e[1] - e[0], e[2] - e[1], e[3] - e[2]
                    if d1 == 0 or (d2 + d0) % d1:
                        ok = False
                        break
                    ta = (d2 + d0) // d1
                    if ta < 2 or (tau is not None and ta != tau) or not definite(e[:3]):
                        ok = False
                        break
                    tau = ta
                if not ok or tau is None:
                    continue
                key = (tau, canon_triple((X0, X1, X2)))
                if key not in seen:
                    seen.add(key)
                    yield (s, p, tau, (X0, X1, X2))


def build_tube(f, nodes, cache, max_tries=8):
    ys = forward_path(f, cache)
    reason = "no periodic base on the forward path"
    tries = 0
    for s, p, tau, X in base_candidates(ys):
        try:
            new, D = close(X, tau, nodes)
            return new, D, (s, p, tau)
        except Abort as e:
            reason = str(e)
        tries += 1
        if tries >= max_tries:
            break
    raise Abort(reason)


def certify(idx, b, q, full=False, verbose=False, L0=None, max_iter=40, max_raise=3, budget=6.0, max_nodes=240):
    t0 = time.time()
    rec = {"i": idx, "b": b}

    def done(status, **kw):
        rec["status"] = status
        rec.update(kw)
        rec["t"] = round(time.time() - t0, 3)
        return (rec, None) if full else rec

    x = tuple(q)
    if not O.certainly_in_core(x):
        lev, adj, ex = O.no_exit_closure(x, cap=800, level_cap=10 ** 6)
        cands = [y for y in lev if O.certainly_in_core(y)]
        if not cands:
            return done("failed: no start that certainly lies in the core")
        x = min(cands, key=lambda y: (lev[y], y))
    x = O.canon(x)
    rec["x"] = list(x)
    L = L0 if L0 is not None else max(O.level(x), 2 * b * b + 20)
    nodes = {}
    D = []
    seeds = [x]
    cache = {}
    members = Members()
    reason = "iteration cap"
    raises = 0
    try:
        for it in range(max_iter):
            if time.time() - t0 > budget:
                return done("failed: time budget (" + reason + ")", L=L, nodes=len(nodes))
            E, frontier = bfs_E(seeds, L, members, cache)
            unc = sorted((lv, f) for f, lv in frontier.items())
            if verbose:
                print(f"  it {it}: L {L}, |E| {len(E)}, frontier {len(unc)}, nodes {len(nodes)}")
            if unc:
                progress = False
                fails = 0
                for lv, f in unc:
                    if f in members:
                        continue
                    if fails >= 6 or time.time() - t0 > budget:
                        break
                    try:
                        new, newD, info = build_tube(f, nodes, cache)
                    except Abort as e:
                        reason = str(e)
                        fails += 1
                        continue
                    if verbose:
                        print(f"     tube from level {lv}: offset {info[0]}, period {info[1]}, tau {info[2]}, {len(new)} families")
                    if new:
                        progress = True
                        nodes.update(new)
                        D.extend(newD)
                        members.add(new)
                        if len(nodes) > max_nodes:
                            return done("failed: more than %d families" % max_nodes, L=L, nodes=len(nodes))
                rest = [lv for lv, f in unc if f not in members]
                newL = max([L] + [O.level(Y[0]) for Y in nodes.values()])
                if rest and newL == L:
                    if progress or raises >= max_raise:
                        # absorb the lowest uncovered frontier quiver into E
                        newL = min(rest)
                        if not progress:
                            raises += 1
                            if raises > max_raise + 6:
                                return done("failed: " + reason, L=L, nE=len(E), nodes=len(nodes))
                    else:
                        raises += 1
                        newL = L * 8
                L = newL
                if L > 10 ** 60:
                    return done("failed: level bound (" + reason + ")", L=L, nodes=len(nodes))
                continue
            missing = [d for d in {O.canon(d) for d in D} if d not in E and d not in members]
            if not missing:
                break
            for c in missing:
                if O.level(c) <= L:
                    if c not in seeds:
                        seeds.append(c)
                else:
                    L = max(L, O.level(c))
            reason = "downward quivers outside E and R"
        else:
            return done("failed: " + reason, L=L, nodes=len(nodes))
    except Abort as e:
        return done("failed: " + str(e), L=L, nodes=len(nodes))
    # the bottom of the core: E and the first three members of every family are quivers of V'(x); every
    # other member has level >= that of the fourth member of its family
    low = dict(E)
    for key, Y in nodes.items():
        for y in Y:
            low[O.canon(y)] = O.level(y)
    bK = min(low.values())
    lR = min((O.level(Y[0]) for Y in nodes.values()), default=None)
    lR3 = min((O.level(members.fams[key].get(3)) for key in nodes), default=None)
    out = {"L": L, "nE": len(E), "nodes": len(nodes), "taus": sorted({k[0] for k in nodes}), "lR": lR, "lR3": lR3,
           "bK": bK, "it": it}
    if lR3 is None or bK < lR3:
        bot = [y for y in low if low[y] == bK]
        out["kid"] = list(min(bot))
        out["mkid"] = list(min(O.canon(O.neg(y)) for y in bot))
        out["nbot"] = len(bot)
    rec.update(out)
    rec["status"] = "certified"
    rec["t"] = round(time.time() - t0, 3)
    if full:
        return rec, (x, E, nodes, members, D)
    return rec


def _job(a):
    try:
        return certify(*a)
    except Exception as e:                                  # never lose the run to one class
        return {"i": a[0], "b": a[1], "status": "error: " + repr(e)[:200]}


# ----------------------------------------------------------------------------- commands
def unresolved(path):
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if not r["ex"]:
                    yield r


def summarize(recs, out=sys.stdout):
    by = defaultdict(Counter)
    for r in recs:
        by[r["b"]]["certified" if r["status"] == "certified" else "failed"] += 1
    print("bottom: classes / certified / failed", file=out)
    tot = Counter()
    for b in sorted(by):
        c = by[b]
        tot.update(c)
        print(f"  {b}: {c['certified'] + c['failed']} / {c['certified']} / {c['failed']}", file=out)
    print(f"  all: {tot['certified'] + tot['failed']} / {tot['certified']} / {tot['failed']}", file=out)
    reasons = Counter(r["status"] for r in recs if r["status"] != "certified")
    print("failure reasons:", file=out)
    for k, v in reasons.most_common():
        print(f"   {v}: {k}", file=out)
    cert = [r for r in recs if r["status"] == "certified"]
    if cert:
        nokid = sum(1 for r in cert if "kid" not in r)
        selfm = sum(1 for r in cert if "kid" in r and r["kid"] == r["mkid"])
        print(f"certified: {len(cert)}; bottom not separated from the fourth members: {nokid}; "
              f"equal to their mirror (kid == mkid): {selfm}; different from their mirror: {len(cert) - nokid - selfm}",
              file=out)
        print(f"  families per class: {dict(sorted(Counter(r['nodes'] for r in cert).items()))}", file=out)
        print(f"  tau values: {dict(sorted(Counter(t for r in cert for t in r['taus']).items())[:40])}", file=out)
        print(f"  largest |E|: {max(r['nE'] for r in cert)}; largest L: {max(r['L'] for r in cert)}; "
              f"classes with a family starting at the bottom level (l_R = b_K): {sum(1 for r in cert if r['lR'] == r['bK'])}", file=out)
    print(f"cpu time: {sum(r.get('t', 0) for r in recs):.0f}s", file=out)


def cmd_run(args):
    t0 = time.time()
    jobs = [(r["i"], r["b"], r["q"]) for r in unresolved(args.cores)]
    if args.limit:
        random.Random(args.seed).shuffle(jobs)
        jobs = jobs[:args.limit]
        jobs.sort()
    print(f"{len(jobs)} classes", flush=True)
    recs = []
    with Pool(args.procs) as pool, gzip.open(args.out, "wt") as out:
        for rec in pool.imap_unordered(_job, jobs, chunksize=20):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            recs.append(rec)
            if len(recs) % 20000 == 0:
                print(f"  {len(recs)} ({time.time() - t0:.0f}s)", flush=True)
    summarize(recs)
    print(f"wall time: {time.time() - t0:.0f}s")


def explicit(e, tau, n):
    out = list(e)
    while len(out) < n:
        out.append((tau + 1) * (out[-1] - out[-2]) + out[-3])
    return out


def cmd_validate(args):
    rng = random.Random(args.seed)
    # (3) Seq against explicit sequences
    n_true = n_false = n_und = bad = 0
    for _ in range(args.seq_tests):
        tau = rng.randint(2, 9)
        a = tuple(rng.randint(-6, 6) for _ in range(3)) if rng.random() < 0.5 else (lambda c: (c, c, c))(rng.randint(-3, 3))
        bb = tuple(rng.randint(-6, 6) for _ in range(3)) if rng.random() < 0.5 else (lambda c: (c, c, c))(rng.randint(-3, 3))
        A, B = explicit(a, tau, 50), explicit(bb, tau, 50)
        sa, sb = Seq(*a), Seq(*bb)
        tests = [("gt", lambda u, v: u > v), ("ge", lambda u, v: u >= v), ("lt", lambda u, v: u < v),
                 ("le", lambda u, v: u <= v), ("eq", lambda u, v: u == v)]
        for name, f in tests:
            for (u, U), (v, V) in (((sa, A), (sb, B)), ((sa, A), (rng.randint(-3, 3),) * 2)):
                if isinstance(v, int):
                    V = [v] * 50
                try:
                    r = f(u, v)
                except Undetermined:
                    n_und += 1
                    continue
                truth = [f(p, q) for p, q in zip(U, V)]
                if r:
                    n_true += 1
                    bad += not all(truth)
                else:
                    n_false += 1
                    bad += any(truth)
        try:
            ab = abs(sa)
            bad += explicit(ab.e, tau, 50) != [abs(v) for v in A]
        except Undetermined:
            pass
        try:
            s = sa.sign()
            bad += any((v > 0) - (v < 0) != s for v in A)
        except Undetermined:
            pass
        c = rng.randint(-4, 4)
        bad += explicit((sa * c + sb).e, tau, 50) != [c * p + q for p, q in zip(A, B)]
    print(f"Seq: {args.seq_tests} random pairs, comparisons certified true {n_true}, certified false {n_false}, "
          f"undetermined {n_und}; contradicted by 50 explicit terms: {bad}")

    # (1) brute force and replay
    jobs = [(r["i"], r["b"], r["q"]) for r in unresolved(args.cores)]
    rng.shuffle(jobs)
    n_cert = n_fail = 0
    miss = 0
    n_brute = 0
    replay_steps = replay_bad = 0
    broken_tau = broken_tau_rej = broken_tri = broken_tri_rej = 0
    t0 = time.time()
    for a in jobs:
        if n_cert >= args.classes:
            break
        rec, obj = certify(*a, full=True)
        if rec["status"] != "certified":
            n_fail += 1
            continue
        n_cert += 1
        x, E, nodes, members, D = obj
        lev, adj, ex = O.no_exit_closure(x, cap=args.brute_cap, level_cap=10 ** 12)
        n_brute += len(lev)
        miss += sum(1 for y in lev if y not in E and y not in members)
        # replay: the neighbours of Y(n), n = 3..10, concretely
        for key, Y in nodes.items():
            tau = key[0]
            T = shift(Y, 3, tau)
            for n in range(3, 11):
                y = T[0]
                if O.level(y) > 10 ** 200:
                    break
                ex_y = O.exit_returns(y)
                for m in range(4):
                    z = O.mutate(y, m)
                    if m not in ex_y and m in O.exit_returns(z):
                        continue
                    replay_steps += 1
                    c = O.canon(z)
                    if c not in E and c not in members:
                        replay_bad += 1
                T = (T[1], T[2], nxt(T, tau))
        # (2) broken certificates: the same bases with a wrong tau, or with one entry of Y(2) changed
        if nodes and broken_tau < args.broken:
            key = rng.choice(sorted(nodes))
            tau, Y = key
            for kind in ("tau", "triple"):
                if kind == "tau":
                    t2, Y2 = tau + 1, Y
                else:
                    a_ = rng.randrange(6)
                    y2 = list(Y[2])
                    y2[a_] += rng.choice((-1, 1))
                    t2, Y2 = tau, (Y[0], Y[1], tuple(y2))
                rejected = False
                try:
                    new, D2 = close(Y2, t2, {})
                    mem2 = Members()
                    mem2.add(new)
                    E3, fr3 = bfs_E([x], rec["L"], mem2, {})
                    if fr3 or any(O.canon(d) not in E3 and O.canon(d) not in mem2 for d in D2):
                        rejected = True
                except Abort:
                    rejected = True
                if kind == "tau":
                    broken_tau += 1
                    broken_tau_rej += rejected
                else:
                    broken_tri += 1
                    broken_tri_rej += rejected
    print(f"classes tried {n_cert + n_fail}: certified {n_cert}, failed {n_fail} ({time.time() - t0:.0f}s)")
    print(f"brute force (no_exit_closure, cap {args.brute_cap}, level cap 10^12): {n_brute} quivers of V', "
          f"outside E and R: {miss}")
    print(f"replay of the closure at n = 3..10: {replay_steps} allowed steps, landing outside E and R: {replay_bad}")
    print(f"broken certificates: wrong tau {broken_tau}, rejected {broken_tau_rej}; "
          f"one entry of Y(2) changed {broken_tri}, rejected {broken_tri_rej}")


def cmd_one(args):
    q = tuple(json.loads(args.q))
    rec, obj = certify(0, O.level(q), q, full=True, verbose=True)
    print(rec)
    if obj:
        x, E, nodes, members, D = obj
        for key, Y in sorted(nodes.items()):
            print("  tau", key[0], Y)


def cmd_summary(args):
    with gzip.open(args.out, "rt") as f:
        recs = [json.loads(line) for line in f if line.strip()]
    summarize(recs)


def cmd_crosscheck(args):
    """Compare the certified classes with the census mirror map (bottom plateaus, n4_opposite_run.py
    plateaus): a census class that is its own mirror must have kid == mkid; the two classes of a census
    mirror pair must have kid of one == mkid of the other; two census classes with the same kid are one
    mutation class."""
    with gzip.open(args.out, "rt") as f:
        recs = {r["i"]: r for r in (json.loads(line) for line in f if line.strip())}
    owner = {}
    plats = []
    with gzip.open(args.plateaus, "rt") as f:
        for line in f:
            p = json.loads(line)
            plats.append(p)
            for c in p["comps"]:
                owner.setdefault(tuple(c["k"]), p["i"])
    mirror = {p["i"]: owner.get(tuple(p["comps"][0]["mk"])) for p in plats}
    cert = {i: r for i, r in recs.items() if r["status"] == "certified" and "kid" in r}
    bykid = defaultdict(list)
    for i, r in cert.items():
        bykid[tuple(r["kid"])].append(i)
    shared = [v for v in bykid.values() if len(v) > 1]
    print(f"classes in the run: {len(recs)}; certified with a bottom of the core: {len(cert)}; distinct kid: {len(bykid)}; "
          f"kid shared by several census classes: {len(shared)}")
    for v in shared[:10]:
        print("   shared:", [(i, recs[i]["b"], recs[i]["x"]) for i in v])
    st = Counter()
    tab = defaultdict(Counter)
    for i, r in recs.items():
        j = mirror[i]
        b = r["b"]
        if j == i:
            tab[b]["self-mirror classes"] += 1
            if i in cert:
                tab[b]["self-mirror certified"] += 1
                st["census self-mirror class: kid == mkid" if r["kid"] == r["mkid"] else
                   "census self-mirror class: kid != mkid (CONTRADICTION)"] += 1
        elif j is not None and i < j:
            tab[b]["mirror pairs"] += 1
            if j not in recs:
                st["mirror class is not in the run"] += 1
                continue
            if (i in cert) != (j in cert):
                st["mirror pair: one class certified, the other not"] += 1
            if i in cert and j in cert:
                tab[b]["mirror pairs certified"] += 1
                ri, rj = cert[i], cert[j]
                if ri["kid"] == rj["kid"]:
                    st["mirror pair with the same kid: one mutation class (hidden join)"] += 1
                elif ri["kid"] == rj["mkid"] and ri["mkid"] == rj["kid"]:
                    st["mirror pair: cores are mirror images and different"] += 1
                else:
                    st["mirror pair: cores are not mirror images (CONTRADICTION)"] += 1
    for k in sorted(st):
        print(f"   {k}: {st[k]}")
    print("bottom: self-mirror classes / certified ; mirror pairs / both certified")
    tot = Counter()
    for b in sorted(tab):
        t = tab[b]
        tot.update(t)
        print(f"  {b}: {t['self-mirror classes']} / {t['self-mirror certified']} ; {t['mirror pairs']} / {t['mirror pairs certified']}")
    print(f"  all: {tot['self-mirror classes']} / {tot['self-mirror certified']} ; {tot['mirror pairs']} / {tot['mirror pairs certified']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("run")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--out", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--procs", type=int, default=8)
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--seed", type=int, default=1)
    s = sub.add_parser("validate")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--classes", type=int, default=300)
    s.add_argument("--brute-cap", type=int, default=4000)
    s.add_argument("--seq-tests", type=int, default=20000)
    s.add_argument("--broken", type=int, default=100)
    s.add_argument("--seed", type=int, default=48)
    s = sub.add_parser("one")
    s.add_argument("q")
    s = sub.add_parser("summary")
    s.add_argument("--out", default="n4_opposite_tubes.jsonl.gz")
    s = sub.add_parser("crosscheck")
    s.add_argument("--out", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    args = ap.parse_args()
    {"run": cmd_run, "validate": cmd_validate, "one": cmd_one, "summary": cmd_summary, "crosscheck": cmd_crosscheck}[args.cmd](args)


if __name__ == "__main__":
    main()
