#!/usr/bin/env python
"""
np_corridor_prove.py -- a symbolic certificate for the lower bound of note 16 (P+_t on 5 vertices).

Claim.  Let t >= T0.  Every route from P+_t to a quiver of height <= t^2 that is not isomorphic to P+_t has height
at least H+(t) = 2t^5 - t^4 + t^2 - 1.

Method (that of n4_doors.py prove, note 15).  By Lemma 15.5 a reduced route between two quivers of height <= t^2
passes no fork higher than t^2.  The script lists families of quivers with polynomial entries (the members), and
certifies for every member and every vertex that the mutation is
    another member (a polynomial identity, up to a relabelling of the vertices),
    or has an entry of absolute value >= H+ (height),
    or is a fork with an entry above t^2 (fork),
and that every member except P+_t itself has an entry above t^2.  A route below H+ that starts at P+_t then stays
among the members and can only end at P+_t.

A statement p >= 0 on an orthant {var >= bound} is certified by shifting every variable to its bound and checking
that no coefficient of the expanded polynomial is negative.  A sign that cannot be certified on an orthant is
retried on the two halves {var = bound} and {var >= bound + 1}.

Members.  Line coordinates: vertices x = 0, p = 1, q = 2, c1 = 3, c = 4, two arrows q -> p, columns (b_pe, b_qe).
A forward step mutates at p and exchanges the names p, q; a backward step mutates at q and exchanges them.
  K0            P+_t                                           variable t >= T0
  K(j)          j steps after K0, 1 <= j <= t - 2              variables j >= 1, v >= 1, t = j + v + 1
  L(i)          i steps after mu_c1 K(t-1), 2 <= i <= N        variables t, i >= 2, r >= 1 free; r stands for N + 1 - i
  L(N+1)        the top                                        variables t, i >= 2 (r = 0)
  M1(k)         k backward steps from L(0), 3 <= k <= t - 3    variables k >= 3, u >= 1, t = k + u + 2
  M2(m)         t + 1 + m backward steps from L(0), m >= 0     variables t, m
and fourteen single quivers in the variable t: K0, K(t-1), K(t), K(t+1), K(t+2), K(-1), K(-2), L(0), L(1), L(-1),
L(-2), M1(t-2), L(-(t-1)), L(-t), which the script derives by symbolic steps.  Every further member is found by
the script: an exit that is certified neither as height nor as fork, and is not recognised as a member, becomes
a new member with the same variables, up to a fixed depth (2).

Reading the verdict "member F(i+1)" and the like: the mutated quiver equals the formula of the family F at the
shifted index, as polynomials.  For the true parameters that is a member: inside the range of F by definition,
and at the ends of the ranges because the formulas of K at j = t-1, of L at i = 1 and at r = 0, of M1 at k = 2
and k = t-2, and of M2 at m = -1 are the single quivers K(t-1), L(1), L(N+1), L(-2), M1(t-2), L(-t) (certified
or by definition).  The verdict "the exit y of its base" says that the mutated quiver equals mu_y of the line
member it was derived from, an exit that is classified in its own right.

After the certificate the script runs three audits that the proof does not need: every height and fork verdict
re-evaluated with integers; the members against the core found by search (np_corridor.core); and the closure
property itself on integers, for T0 <= t <= --audit-tmax.

Run from experiments/ with python -I.  `check` compares the closed forms with integer mutation for small t.
"""
import argparse
import itertools
import sys

VARS = ("t", "j", "v", "i", "r", "k", "u", "m")
NV = len(VARS)
N5 = 5
PERMS = list(itertools.permutations(range(N5)))
X, PV, QV, C1, C = 0, 1, 2, 3, 4
NAMES = "x p q c1 c".split()


# ----------------------------------------------------------------------------- polynomials
class P:
    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = {k: v for k, v in (c or {}).items() if v}

    @staticmethod
    def const(a):
        return P({(0,) * NV: a})

    @staticmethod
    def var(name):
        e = [0] * NV
        e[VARS.index(name)] = 1
        return P({tuple(e): 1})

    @staticmethod
    def lift(a):
        return a if isinstance(a, P) else P.const(a)

    def __add__(self, o):
        o = P.lift(o)
        c = dict(self.c)
        for k, v in o.c.items():
            c[k] = c.get(k, 0) + v
        return P(c)

    __radd__ = __add__

    def __neg__(self):
        return P({k: -v for k, v in self.c.items()})

    def __sub__(self, o):
        return self + (-P.lift(o))

    def __rsub__(self, o):
        return P.lift(o) - self

    def __mul__(self, o):
        o = P.lift(o)
        c = {}
        for k1, v1 in self.c.items():
            for k2, v2 in o.c.items():
                k = tuple(a + b for a, b in zip(k1, k2))
                c[k] = c.get(k, 0) + v1 * v2
        return P(c)

    __rmul__ = __mul__

    def __pow__(self, n):
        r = P.const(1)
        for _ in range(n):
            r = r * self
        return r

    def is_zero(self):
        return not self.c

    def subs(self, name, poly):
        i = VARS.index(name)
        poly = P.lift(poly)
        r = P()
        pw = {0: P.const(1)}
        for k, v in self.c.items():
            e = list(k)
            d, e[i] = e[i], 0
            if d not in pw:
                pw[d] = poly ** d
            r = r + P({tuple(e): v}) * pw[d]
        return r

    def subs_all(self, mapping):
        r = self
        # simultaneous substitution: go through fresh copies so that replaced variables do not interact
        r2 = P()
        for k, v in r.c.items():
            term = P.const(v)
            for name, e in zip(VARS, k):
                if e:
                    term = term * (P.lift(mapping[name]) if name in mapping else P.var(name)) ** e
            r2 = r2 + term
        return r2

    def value(self, env):
        s = 0
        for k, v in self.c.items():
            for name, e in zip(VARS, k):
                if e:
                    v *= env[name] ** e
            s += v
        return s

    def used(self):
        return {VARS[i] for k in self.c for i, e in enumerate(k) if e}

    def __repr__(self):
        if not self.c:
            return "0"
        out = []
        for k in sorted(self.c, reverse=True):
            mono = "*".join(n if e == 1 else "%s^%d" % (n, e) for n, e in zip(VARS, k) if e)
            v = self.c[k]
            out.append("%+d%s" % (v, "*" + mono if mono else ""))
        return " ".join(out)


def nonneg(p, dom):
    p = P.lift(p)
    if not p.used() <= set(dom):
        raise ValueError("no bound for %s" % sorted(p.used() - set(dom)))
    for name, lb in dom.items():
        if lb and name in p.used():
            p = p.subs(name, P.var(name) + lb)
    return all(v >= 0 for v in p.c.values())


def wsign(p, dom):
    """+1 if p >= 0 on dom, -1 if p <= 0, 0 if p is the zero polynomial; None if not certified."""
    p = P.lift(p)
    if p.is_zero():
        return 0
    if nonneg(p, dom):
        return 1
    if nonneg(-p, dom):
        return -1
    return None


def ssign(p, dom):
    """+1 if p >= 1 on dom, -1 if p <= -1; None otherwise."""
    p = P.lift(p)
    if nonneg(p - 1, dom):
        return 1
    if nonneg(-p - 1, dom):
        return -1
    return None


# ----------------------------------------------------------------------------- symbolic quivers
def smat(rows):
    return tuple(tuple(P.lift(a) for a in r) for r in rows)


def line(c1, c, x, scc1, sxc, sxc1):
    """Two arrows q -> p; columns (b_pe, b_qe) of c1, c, x; b_{c c1}, b_{x c}, b_{x c1}."""
    M = [[P.const(0)] * N5 for _ in range(N5)]

    def setb(a, b, val):
        M[a][b] = P.lift(val)
        M[b][a] = -P.lift(val)
    setb(QV, PV, 2)
    for e, col in ((C1, c1), (C, c), (X, x)):
        setb(PV, e, col[0])
        setb(QV, e, col[1])
    setb(C, C1, scc1)
    setb(X, C, sxc)
    setb(X, C1, sxc1)
    return smat(M)


def smutate(M, k, dom):
    """mu_k with certified signs of the entries at k on dom; None if some sign is not certified."""
    sg = {}
    for a in range(N5):
        if a != k:
            s = wsign(M[a][k], dom)
            if s is None:
                return None
            sg[a] = s
    out = [[None] * N5 for _ in range(N5)]
    for a in range(N5):
        for b in range(N5):
            if a == k or b == k:
                out[a][b] = -M[a][b]
            elif a == b:
                out[a][b] = P.const(0)
            else:
                e = M[a][b]
                if sg[a] > 0 and sg[b] < 0:        # b_ak >= 0 and b_kb = -b_bk >= 0
                    e = e + M[a][k] * M[k][b]
                elif sg[a] < 0 and sg[b] > 0:      # b_ak <= 0 and b_kb <= 0
                    e = e - M[a][k] * M[k][b]
                out[a][b] = e
    return smat(out)


def srelabel(M, p):
    return tuple(tuple(M[p[a]][p[b]] for b in range(N5)) for a in range(N5))


SWAP = (0, 2, 1, 3, 4)


def sfwd(M, dom):
    m = smutate(M, PV, dom)
    return None if m is None else srelabel(m, SWAP)


def sback(M, dom):
    m = smutate(M, QV, dom)
    return None if m is None else srelabel(m, SWAP)


def ssubs(M, mapping):
    return tuple(tuple(e.subs_all(mapping) for e in r) for r in M)


def sequal(M1, M2):
    return all((a - b).is_zero() for r1, r2 in zip(M1, M2) for a, b in zip(r1, r2))


def same_up_to_relabelling(M1, M2):
    for p in PERMS:
        if sequal(srelabel(M1, p), M2):
            return p
    return None


def cert_height(M, H, dom):
    for a in range(N5):
        for b in range(a + 1, N5):
            s = wsign(M[a][b], dom)
            if s and nonneg(s * M[a][b] - H, dom):
                return (a, b)
    return None


def cert_above(M, W, dom):
    """Some entry has absolute value >= W + 1 on dom."""
    for a in range(N5):
        for b in range(a + 1, N5):
            s = wsign(M[a][b], dom)
            if s and nonneg(s * M[a][b] - W - 1, dom):
                return (a, b)
    return None


def cert_fork(M, W, dom):
    """M is a fork on dom with an entry above W.  Returns the point of return, or None."""
    sg = {}
    for a in range(N5):
        for b in range(N5):
            if a != b:
                s = ssign(M[a][b], dom)
                if s is None:
                    return None
                sg[(a, b)] = s
    wt = lambda a, b: sg[(a, b)] * M[a][b]
    if not all(nonneg(wt(a, b) - 2, dom) for a in range(N5) for b in range(a + 1, N5)):
        return None
    arrow = lambda a, b: sg[(a, b)] > 0

    def acyc(vs):
        rem = set(vs)
        while rem:
            src = [a for a in rem if not any(arrow(b, a) for b in rem if b != a)]
            if not src:
                return False
            rem -= set(src)
        return True
    if acyc(range(N5)) or cert_above(M, W, dom) is None:
        return None
    for r in range(N5):
        ins = [a for a in range(N5) if a != r and arrow(a, r)]
        outs = [b for b in range(N5) if b != r and arrow(r, b)]
        if not (acyc(ins) and acyc(outs)):
            continue
        if all(arrow(b, a) and nonneg(wt(b, a) - wt(a, r) - 1, dom) and nonneg(wt(b, a) - wt(r, b) - 1, dom)
               for a in ins for b in outs):
            return r
    return None


# ----------------------------------------------------------------------------- integer kernel for `check`
def imut(B, k):
    n = len(B)
    Nn = [list(r) for r in B]
    for a in range(n):
        if a == k or B[a][k] == 0:
            continue
        for b in range(n):
            if b == k:
                continue
            if B[a][k] > 0 and B[k][b] > 0:
                Nn[a][b] += B[a][k] * B[k][b]
            elif B[a][k] < 0 and B[k][b] < 0:
                Nn[a][b] -= B[a][k] * B[k][b]
    for a in range(n):
        Nn[a][k] = -B[a][k]
        Nn[k][a] = -B[k][a]
    return tuple(tuple(r) for r in Nn)


def ieval(M, env):
    return tuple(tuple(e.value(env) for e in r) for r in M)


def irel(B, p):
    return tuple(tuple(B[p[a]][p[b]] for b in range(N5)) for a in range(N5))


def icanon(B):
    return min(tuple(B[p[a]][p[b]] for a in range(N5) for b in range(a + 1, N5)) for p in PERMS)


# ----------------------------------------------------------------------------- the members
t, j, v, i, r, k, u, m = (P.var(n) for n in VARS)


def Nof(tt):
    return 2 * tt ** 3 - tt * tt - tt


def Hof(tt):
    return 2 * tt ** 5 - tt ** 4 + tt * tt - 1


def K0f(tt):
    return line(((tt - 1) * tt, -tt * tt), (tt * tt, tt * tt - 1), (P.const(-1), tt * tt - 1), 2 * tt, tt * tt, -tt * (tt - 1))


def Kf(tt, jj):
    d = 2 * tt * tt - 1
    return line(((tt - 1 - jj) * tt, -(tt - jj) * tt), (tt * tt + jj * d, -(tt * tt + (jj - 1) * d)),
                (jj * tt * tt - 1, -((jj - 1) * tt * tt - 1)), 2 * tt, 2 * tt * tt, 0)


def Lf(tt, ii, rr):
    return line((ii * tt, -(ii - 1) * tt), (rr, -(rr + 1)),
                ((tt - 1 + ii) * tt * tt - 1, -((tt - 2 + ii) * tt * tt - 1)), -2 * tt, 2 * tt * tt, 0)


def M1f(tt, kk):
    Nn = Nof(tt)
    s = tt - 1 - kk
    return line(((kk - 2) * tt, -(kk - 1) * tt), (Nn + 1 + kk, -(Nn + 2 + kk)),
                (s * tt * tt - 1, -((s - 1) * tt * tt - 1)), tt * Nn, 2 * tt * tt, tt * ((tt - 2) * tt * tt - 1))


def M2f(tt, mm):
    Nn = Nof(tt)
    return line(((tt - 1 + mm) * tt, -(tt + mm) * tt), (Nn + tt + 2 + mm, -(Nn + tt + 3 + mm)),
                (mm * tt * tt + 1, -((mm + 1) * tt * tt + 1)), tt * Nn, -(Hof(tt) - 2 * tt * tt), 0)


def orthants(names, lbs, total):
    """Orthants whose union is {x_a >= lb_a, x_1 + x_2 >= total} for two variables."""
    (n1, n2), (l1, l2) = names, lbs
    out = []
    a = l1
    while a < total - l2:
        out.append({n1: a, n2: total - a})
        a += 1
    out.append({n1: max(l1, total - l2), n2: l2})
    return out


class Fam:
    """A formal family: a matrix in chart variables, with the shifts of its line variable."""
    def __init__(self, name, M, H, W, shifts, tsum=None):
        self.name, self.M, self.H, self.W, self.shifts, self.tsum = name, M, H, W, shifts, tsum


class Member:
    def __init__(self, name, M, dom, H, W, fam=None, sub=None, parent=None, via=None, depth=0, low=False, base=None, word=()):
        self.name, self.M, self.dom, self.H, self.W = name, M, dict(dom), H, W
        self.fam, self.sub = fam, dict(sub or {})
        self.parent, self.via, self.depth, self.low = parent, via, depth, low
        self.fixed = {}                                # variables fixed by slicing, in the current variables
        self.base = M if base is None else base        # the member of a line this one was derived from, in the same variables
        self.word = tuple(word)                        # the mutations that lead from base to M


def cmd_prove(args):
    T0 = args.T0
    results = []
    state = {"ok": True}

    def claim(label, good, detail=""):
        state["ok"] &= bool(good)
        results.append((label, bool(good)))
        if not good or not args.quiet:
            print("%-86s %-6s %s" % (label, "ok" if good else "FAILED", detail), flush=True)

    # ---- formal families
    tK = j + v + 1
    tM = k + u + 2
    FK = Fam("K", Kf(tK, j), Hof(tK), tK * tK, [({"j": j + 1, "v": v - 1}, "(j+1)"), ({"j": j - 1, "v": v + 1}, "(j-1)")], ("j", "v", 1))
    FL = Fam("L", Lf(t, i, r), (t + i + r) * t * t - 1, t * t, [({"i": i + 1, "r": r - 1}, "(i+1)"), ({"i": i - 1, "r": r + 1}, "(i-1)")])
    FM1 = Fam("M1", M1f(tM, k), Hof(tM), tM * tM, [({"k": k + 1, "u": u - 1}, "(k+1)"), ({"k": k - 1, "u": u + 1}, "(k-1)")], ("k", "u", 2))
    FM2 = Fam("M2", M2f(t, m), Hof(t), t * t, [({"m": m + 1}, "(m+1)"), ({"m": m - 1}, "(m-1)")])
    DT = {"t": T0}
    Nt = Nof(t)

    # ---- identities along the lines and derived quivers (all in the variable t)
    K0 = K0f(t)
    K1 = ssubs(FK.M, {"j": P.const(1), "v": t - 2})
    Ktop = ssubs(FK.M, {"j": t - 1, "v": P.const(0)})
    L0 = ssubs(FL.M, {"i": P.const(0), "r": Nt + 1})
    L1 = ssubs(FL.M, {"i": P.const(1), "r": Nt})
    claim("H+ = (t + N + 1) t^2 - 1", (Hof(t) - ((t + Nt + 1) * t * t - 1)).is_zero())
    eq = lambda A, B: A is not None and sequal(A, B)
    claim("K0 forward step = K(1)", eq(sfwd(K0, DT), K1))
    claim("mu_c1 K(t-1) = L(0)", eq(smutate(Ktop, C1, DT), L0))
    Ltop = ssubs(FL.M, {"r": P.const(0)})
    Htop = (t + i) * t * t - 1
    dtop = {"t": T0, "i": 2}
    mc, mp = smutate(Ltop, C, dtop), smutate(Ltop, PV, dtop)
    claim("at the top L(N+1): mu_c = -mu_p", mc is not None and mp is not None and
          all((a_ + b_).is_zero() for r1, r2 in zip(mc, mp) for a_, b_ in zip(r1, r2)))
    claim("at the top: mu_p has height exactly H+", mp is not None and cert_height(mp, Htop, dtop) is not None and
          all(nonneg(Htop - s_ * e, dtop) for row in mp for e in row for s_ in (1, -1)))

    def chain(M0, step, nsteps):
        out = []
        cur = M0
        for _ in range(nsteps):
            cur = step(cur, DT) if cur is not None else None
            out.append(cur)
        return out
    Ma1, Ma2, Ma3 = chain(L0, sback, 3)
    M13 = ssubs(FM1.M, {"k": P.const(3), "u": t - 5})
    claim("L(0), three backward steps = M1(3)", eq(Ma3, M13))
    M1top = ssubs(FM1.M, {"k": t - 2, "u": P.const(0)})
    Mb1, Mb2, Mb3 = chain(M1top, sback, 3)
    M20 = ssubs(FM2.M, {"m": P.const(0)})
    claim("M1(t-2), three backward steps = M2(0)", eq(Mb3, M20))
    Kf1, Kf2, Kf3 = chain(Ktop, sfwd, 3)
    Kb1, Kb2 = chain(K0, sback, 2)
    spor = [("K0", K0), ("K(t-1)", Ktop), ("K(t)", Kf1), ("K(t+1)", Kf2), ("K(t+2)", Kf3), ("K(-1)", Kb1), ("K(-2)", Kb2),
            ("L(0)", L0), ("L(1)", L1), ("L(-1)", Ma1), ("L(-2)", Ma2), ("M1(t-2)", M1top), ("L(-(t-1))", Mb1), ("L(-t)", Mb2)]
    for nm, mm in spor:
        claim("signs certified on the way to %s" % nm, mm is not None)
    claim("the formula of M1 at k = 2 is L(-2)", eq(Ma2, ssubs(FM1.M, {"k": P.const(2), "u": t - 4})))
    claim("the formula of M2 at m = -1 is L(-t)", eq(Mb2, ssubs(FM2.M, {"m": P.const(-1)})))
    claim("the formula of K at j = t-1 is K(t-1), and of L at i = 0, 1 with r = N+1-i is L(0), L(1)", True, "(definitions)")
    if not state["ok"]:
        print("\nclosed forms or derived members failed; stopping")
        return 1

    # ---- members
    members = []
    for nm, mm in spor:
        members.append(Member(nm, mm, DT, Hof(t), t * t, low=(nm == "K0")))
    for d in orthants(("j", "v"), (1, 1), T0 - 1):
        members.append(Member("K(j), 1<=j<=t-2", FK.M, d, FK.H, FK.W, fam=FK))
    members.append(Member("L(i), 2<=i<=N", FL.M, {"t": T0, "i": 2, "r": 1}, FL.H, FL.W, fam=FL))
    members.append(Member("L(N+1)", Ltop, dtop, Htop, t * t, fam=FL, sub={"r": P.const(0)}))
    members[-1].fixed = {"r": 0}
    for d in orthants(("k", "u"), (3, 1), T0 - 2):
        members.append(Member("M1(k), 3<=k<=t-3", FM1.M, d, FM1.H, FM1.W, fam=FM1))
    members.append(Member("M2(m), m>=0", FM2.M, {"t": T0, "m": 0}, FM2.H, FM2.W, fam=FM2))

    # instances of the formal families in the variable t, to recognise quivers across charts
    tinst = list(spor)
    for c_ in range(0, 4):
        tinst.append(("K(t-%d)" % (c_ + 1), ssubs(FK.M, {"j": t - 1 - c_, "v": P.const(c_)})))
        tinst.append(("K(%d)" % (c_ + 1), ssubs(FK.M, {"j": P.const(c_ + 1), "v": t - 2 - c_})))
        tinst.append(("L(%d)" % c_, ssubs(FL.M, {"i": P.const(c_), "r": Nt + 1 - c_})))
        tinst.append(("M1(t-%d)" % (c_ + 2), ssubs(FM1.M, {"k": t - 2 - c_, "u": P.const(c_)})))
        tinst.append(("M1(%d)" % (c_ + 3), ssubs(FM1.M, {"k": P.const(c_ + 3), "u": t - 5 - c_})))
        tinst.append(("M2(%d)" % c_, ssubs(FM2.M, {"m": P.const(c_)})))
    derived = []                                   # (name, matrix, variables) of new members, for recognition

    def recognise(Mx, mem):
        vars_ = frozenset(mem.dom)
        fx = {n_: P.const(b_) for n_, b_ in mem.fixed.items()}
        if vars_ | set(fx) == {"t"}:
            for nm, T in tinst:
                if same_up_to_relabelling(Mx, ssubs(T, fx) if fx else T) is not None:
                    return nm
        if mem.fam is not None:
            for mp_, tag in [({}, "")] + mem.fam.shifts:
                T = ssubs(ssubs(mem.fam.M, mp_), mem.sub) if (mp_ or mem.sub) else mem.fam.M
                if same_up_to_relabelling(Mx, T) is not None:
                    return mem.fam.name + tag + (" with %s" % {a_: repr(b_) for a_, b_ in mem.sub.items()} if mem.sub else "")
        for nm, T, dT, fT in derived:
            if set(dT) | set(fT) != vars_ | set(fx):
                continue
            if any(n_ in vars_ or mem.fixed[n_] != b_ for n_, b_ in fT.items()):
                continue
            if all(mem.fixed[n_] >= dT[n_] for n_ in fx if n_ in dT) and all(mem.dom[n_] >= dT[n_] for n_ in vars_):
                sub_ = {n_: b_ for n_, b_ in fx.items() if n_ in dT}
                if same_up_to_relabelling(Mx, ssubs(T, sub_) if sub_ else T) is not None:
                    return nm
        if mem.word:                                   # a quiver one mutation away from the base is an exit of the base
            if same_up_to_relabelling(Mx, mem.base) is not None:
                return "the base %s" % mem.word.__repr__()
            for y in range(N5):
                T = smutate(mem.base, y, mem.dom)
                if T is not None and same_up_to_relabelling(Mx, T) is not None:
                    return "the exit %s of its base (classified there)" % NAMES[y]
        return None

    def to_t(mem, name, val):
        """The slice {name = val} of mem.  A chart with t = sum of two variables + c is rewritten in t."""
        sub = {name: P.const(val)}
        M2_, H2, W2 = ssubs(mem.M, sub), mem.H.subs_all(sub), mem.W.subs_all(sub)
        B2 = ssubs(mem.base, sub)
        dom = {n_: b_ for n_, b_ in mem.dom.items() if n_ != name}
        fam, fsub = mem.fam, {**mem.sub, **sub}
        if mem.fam is not None and mem.fam.tsum and name in mem.fam.tsum[:2] and len(dom) == 1:
            a_, b_, c_ = mem.fam.tsum
            other = b_ if name == a_ else a_
            rep = {other: t - val - c_}
            M2_, H2, W2 = ssubs(M2_, rep), H2.subs_all(rep), W2.subs_all(rep)
            B2 = ssubs(B2, rep)
            dom = {"t": dom[other] + val + c_}
            fam, fsub = None, {}
        out = Member("%s [%s=%d]" % (mem.name, name, val), M2_, dom, H2, W2, fam=fam, sub=fsub, parent=mem.parent, via=mem.via,
                     depth=mem.depth, low=mem.low, base=B2, word=mem.word)
        out.fixed = {} if (fam is None and mem.fam is not None) else {**mem.fixed, name: val}
        return out

    def classify(mem, vtx, sd):
        """List of (member-slice, verdict, mutated matrix)."""
        Mx = smutate(mem.M, vtx, mem.dom)
        if Mx is not None:
            e = cert_height(Mx, mem.H, mem.dom)
            if e is not None:
                return [(mem, "height (entry %s-%s)" % (NAMES[e[0]], NAMES[e[1]]), Mx)]
            rr = cert_fork(Mx, mem.W, mem.dom)
            if rr is not None:
                return [(mem, "fork, point of return %s" % NAMES[rr], Mx)]
            fm = recognise(Mx, mem)
            if fm is not None:
                return [(mem, "member %s" % fm, Mx)]
        if sd < args.split and mem.dom:
            names = sorted(mem.dom)
            name = names[sd % len(names)]
            hi = Member(mem.name, mem.M, {**mem.dom, name: mem.dom[name] + 1}, mem.H, mem.W, fam=mem.fam, sub=mem.sub, parent=mem.parent,
                        via=mem.via, depth=mem.depth, low=mem.low, base=mem.base, word=mem.word)
            hi.fixed = dict(mem.fixed)
            lo = to_t(mem, name, mem.dom[name])
            return classify(lo, vtx, sd + 1) + classify(hi, vtx, sd + 1)
        return [(mem, None, Mx)]

    records = []
    todo = list(members)
    while todo:
        mem = todo.pop(0)
        for vtx in range(N5):
            if mem.via == vtx:
                continue
            for sl, verdict, Mx in classify(mem, vtx, 0):
                if verdict is None and Mx is not None and sl.depth < args.depth:
                    nm = "mu_%s %s" % (NAMES[vtx], sl.name)
                    new = Member(nm, Mx, sl.dom, sl.H, sl.W, parent=sl, via=vtx, depth=sl.depth + 1, base=sl.base, word=sl.word + (vtx,))
                    new.fixed = dict(sl.fixed)
                    members.append(new)
                    derived.append((nm, Mx, dict(sl.dom), dict(sl.fixed)))
                    todo.append(new)
                    verdict = "new member"
                records.append((sl, vtx, verdict))
                claim("exit %-2s of %-44s on %s" % (NAMES[vtx], sl.name, sl.dom), verdict is not None,
                      verdict or ("NOT CLASSIFIED" if Mx is not None else "SIGNS NOT CERTIFIED"))
    for mem in members:
        if not mem.low:
            claim("above t^2: %-52s on %s" % (mem.name, mem.dom), cert_above(mem.M, mem.W, mem.dom) is not None)
    print("\n%d claims, %d members, %s" % (len(results), len(members), "ALL CERTIFIED" if state["ok"] else "SOME FAILED"))
    print("failed: %d" % sum(1 for _, g in results if not g))
    kinds = {}
    for _, _, vd in records:
        key = (vd or "none").split(" ")[0].rstrip(",")
        kinds[key] = kinds.get(key, 0) + 1
    print("exits by verdict: %s" % dict(sorted(kinds.items())))
    if not state["ok"]:
        return 1

    # ---- audit 1: every height and fork verdict, re-evaluated with integers at sample points of its domain
    import random
    rng = random.Random(7)

    def ifork(B):
        n = len(B)
        if any(abs(B[a][b]) < 2 for a in range(n) for b in range(a + 1, n)):
            return False

        def acyc(vs):
            rem = set(vs)
            while rem:
                src = [a for a in rem if not any(B[b][a] > 0 for b in rem)]
                if not src:
                    return False
                rem -= set(src)
            return True
        if acyc(range(n)):
            return False
        for rr in range(n):
            ins = [a for a in range(n) if B[a][rr] > 0]
            outs = [b for b in range(n) if B[rr][b] > 0]
            if all(B[b][a] > B[a][rr] and B[b][a] > B[rr][b] for a in ins for b in outs) and acyc(ins) and acyc(outs):
                return True
        return False
    iht = lambda B: max(abs(e) for row in B for e in row)
    bad = 0
    checked = 0
    for sl, vtx, vd in records:
        for trial in range(4):
            env = {n_: b_ + (0 if trial == 0 else rng.randint(0, 6)) for n_, b_ in sl.dom.items()}
            B = ieval(sl.M, env)
            Nx = imut(B, vtx)
            Hn, Wn = sl.H.value(env), sl.W.value(env)
            if vd.startswith("height"):
                checked += 1
                bad += not (iht(Nx) >= Hn)
            elif vd.startswith("fork"):
                checked += 1
                bad += not (ifork(Nx) and iht(Nx) > Wn)
    print("audit 1: %d height and fork verdicts re-evaluated at integer points of their domains, %d wrong" % (checked, bad))

    # ---- audit 2: for small t, the core computed by search (np_corridor.core) lies in the list of members
    try:
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import np_corridor as npc
    except Exception as exc:                       # the certificate does not depend on this
        print("audit 2 skipped: %s" % exc)
        return 0 if bad == 0 else 1
    for tt in range(T0, args.audit_tmax + 1):
        Nn = 2 * tt ** 3 - tt * tt - tt
        Hn = 2 * tt ** 5 - tt ** 4 + tt * tt - 1
        inst = set()
        allinst = {}
        owner = {}
        for mem in members:
            vs = set(mem.dom) | set(mem.fixed)
            envs = []
            if vs & {"j", "v"}:
                envs = [{"j": jj, "v": tt - 1 - jj} for jj in range(1, tt - 1)]
            elif vs & {"k", "u"}:
                envs = [{"k": kk, "u": tt - 2 - kk} for kk in range(3, tt - 2)]
            elif vs & {"i", "r"}:
                envs = [{"t": tt, "i": ii, "r": Nn + 1 - ii} for ii in range(2, Nn + 2)]
            elif "m" in vs:
                envs = [{"t": tt, "m": mm} for mm in range(0, 2 * Nn)]
            else:
                envs = [{"t": tt}]
            for env in envs:
                if any(env.get(n_, None) is None or env[n_] < b_ for n_, b_ in mem.dom.items()):
                    continue
                if any(env.get(n_, b_) != b_ for n_, b_ in mem.fixed.items()):
                    continue
                B = ieval(mem.M, env)
                allinst[icanon(B)] = B
                owner.setdefault(icanon(B), "%s at %s fixed %s" % (mem.name, env, mem.fixed))
                if iht(B) < Hn:
                    inst.add(icanon(B))
        seen, exits, low_forks = npc.core(tt, plus=True)
        missing = [c_ for c_ in seen if c_ not in inst]
        print("audit 2, t = %d: the search finds a core of %d quivers; %d of them are not instances of a listed member; "
              "instances of members below H+: %d" % (tt, len(seen), len(missing), len(inst)), flush=True)
        bad += len(missing)
        # audit 3: the closure itself, on integers: every mutation of an instance below H+ is an instance, or has
        # height >= H+, or is a fork higher than t^2; and only P+_t has height <= t^2
        viol = 0
        nex = 0
        lowinst = 0
        for c_ in inst:
            B = allinst[c_]
            lowinst += iht(B) <= tt * tt
            for vtx in range(N5):
                Nx = imut(B, vtx)
                nex += 1
                if not (iht(Nx) >= Hn or icanon(Nx) in allinst or (ifork(Nx) and iht(Nx) > tt * tt)):
                    viol += 1
                    if args.debug and viol <= args.debug:
                        print("   violation: instance of %s, exit %s: height %d, fork %s" % (owner[c_], NAMES[vtx], iht(Nx), ifork(Nx)))
        print("audit 3, t = %d: %d mutations of the %d instances below H+: %d are neither an instance, nor of height >= H+, "
              "nor a fork higher than t^2; instances of height <= t^2: %d" % (tt, nex, len(inst), viol, lowinst), flush=True)
        bad += viol + (lowinst != 1)
    return 0 if bad == 0 else 1


def cmd_check(args):
    """The closed forms against integer mutation, for t in a range."""
    good = True
    for tt in range(args.tmin, args.tmax + 1):
        Nn = 2 * tt ** 3 - tt * tt - tt
        B = ieval(K0f(t), {"t": tt})
        P0 = B
        for jj in range(1, tt):
            B = irel(imut(B, PV), SWAP)
            good &= B == ieval(Kf(t, j), {"t": tt, "j": jj})
        B = imut(B, C1)
        L0 = B
        for ii in range(0, min(Nn + 1, 400) + 1):
            good &= B == ieval(Lf(t, i, r), {"t": tt, "i": ii, "r": Nn + 1 - ii})
            B = irel(imut(B, PV), SWAP)
        B = L0
        for kk in range(1, tt + 40):
            B = irel(imut(B, QV), SWAP)
            if 3 <= kk <= tt - 2:
                good &= B == ieval(M1f(t, k), {"t": tt, "k": kk})
            if kk >= tt + 1:
                good &= B == ieval(M2f(t, m), {"t": tt, "m": kk - tt - 1})
        print("t=%d: closed forms of K(j), L(i) (i <= 400), M1(k), M2(m) (m <= 38) agree with integer mutation: %s" % (tt, good))
    return 0 if good else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prove")
    s.add_argument("--T0", type=int, default=8)
    s.add_argument("--depth", type=int, default=2)
    s.add_argument("--split", type=int, default=2)
    s.add_argument("--quiet", action="store_true")
    s.add_argument("--audit-tmax", type=int, default=10)
    s.add_argument("--debug", type=int, default=0)
    s = sub.add_parser("check")
    s.add_argument("--tmin", type=int, default=5)
    s.add_argument("--tmax", type=int, default=12)
    args = ap.parse_args()
    sys.exit(globals()["cmd_" + args.cmd](args))


if __name__ == "__main__":
    main()
