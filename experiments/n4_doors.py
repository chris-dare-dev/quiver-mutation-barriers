"""Note 15: rank-2 orbits ("lines"), mirror doors, and the families R_b (barrier 2b^2 - 3b - 3) and Q_t
(barrier 2t^4 - t^3 - t^2 + 2t).

Pure Python, exact integers, no packages.  A 4-vertex quiver is the 6-tuple
(b01, b02, b03, b12, b13, b23) of the entries above the diagonal of its exchange matrix; b_ij > 0 means
b_ij arrows i -> j.  Height = maximal entry.  Quivers are compared up to relabelling by `canon`.

Subcommands
  selftest   the toolkit against mutation_path.mutate / bounded_paths.canonical and the census extremes
  orbit      Theorem 15.1 (profile of a rank-2 orbit) and Proposition 15.3 (joins inside an orbit), by brute force
  orbit01    Proposition 15.3 for the finite orbits (squares and pentagons), by brute force
  forks      Lemma 15.4 (Warkentin) and Lemma 15.5 (fork exclusion) on random forks and on the stored join paths
  family     Theorem 15.6 numerically: the region of Q_t below H_t is {K(j)} u {L(n)}, it is closed, the barrier is H_t
  prove      Theorem 15.6 for every t >= 3: polynomial certificates for each exit of the region
  family2    the two-parameter family Q_{t,b} (numerical)
  family3    Theorem 15.13 numerically: R_b = (-b, -b, b-1, -2, b-2, -b), barrier 2b^2 - 3b - 3 (all b; structure for even b)
  prove2     Theorem 15.13 for every even b >= 6: polynomial certificates
  doors      scan of mirror doors D(p, q, r, s)
  coq        proper cyclic orderings, total properness to a given depth, Markov invariants (section 7)
  ahjl       the local lemmas of arXiv 2610.36179 on mutation-cyclic examples (section 7)
  markov-census   the Markov value of every census class with a pocket, against the latest death (section 7)
  thin       the joins of all census pockets when quivers above the birth level must have a small entry (section 8)
  scan2      every quiver of height b with an entry +-2, beyond the census (section 6)
"""
import argparse
import heapq
import itertools
import json
import random
import sys
import time
from collections import Counter, defaultdict, deque
from multiprocessing import Pool

# ----------------------------------------------------------------------------- toolkit
PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
IDX = {p: a for a, p in enumerate(PAIRS)}
PERMS = list(itertools.permutations(range(4)))
# relabelling by p: the new entry (i, j) is the old entry (p[i], p[j])
PTAB = [tuple((IDX[(min(p[i], p[j]), max(p[i], p[j]))], 1 if p[i] < p[j] else -1) for (i, j) in PAIRS) for p in PERMS]


def ent(q, i, j):
    if i == j:
        return 0
    return q[IDX[(i, j)]] if i < j else -q[IDX[(j, i)]]


def mutate(q, k):
    out = []
    for (i, j) in PAIRS:
        b = q[IDX[(i, j)]]
        if i == k or j == k:
            out.append(-b)
        else:
            bik, bkj = ent(q, i, k), ent(q, k, j)
            if bik > 0 and bkj > 0:
                b += bik * bkj
            elif bik < 0 and bkj < 0:
                b -= bik * bkj
            out.append(b)
    return tuple(out)


def relabel(q, p):
    return tuple(s * q[i] for i, s in PTAB[PERMS.index(tuple(p))])


def canon(q):
    best = None
    for row in PTAB:
        t = (row[0][1] * q[row[0][0]], row[1][1] * q[row[1][0]], row[2][1] * q[row[2][0]],
             row[3][1] * q[row[3][0]], row[4][1] * q[row[4][0]], row[5][1] * q[row[5][0]])
        if best is None or t < best:
            best = t
    return best


def ht(q):
    return max(abs(x) for x in q)


def neg(q):
    return tuple(-x for x in q)


def pf(q):
    return q[0] * q[5] - q[1] * q[4] + q[2] * q[3]


def escape(q, bound, budget=10 ** 7):
    """Least L <= bound such that q reaches, through quivers of height <= L, a quiver of height <= ht(q)
    outside the component of q in the graph of quivers of height <= ht(q).  Lazy bottleneck search.
    Returns (L or None, the quiver reached, number of quivers seen)."""
    s = canon(q)
    b = ht(s)
    plateau = {s}
    dq = deque([s])
    while dq:
        c = dq.popleft()
        for k in range(4):
            m = mutate(c, k)
            if ht(m) <= b:
                m = canon(m)
                if m not in plateau:
                    plateau.add(m)
                    dq.append(m)
    best = {x: b for x in plateau}
    heap = [(b, x) for x in plateau]
    heapq.heapify(heap)
    done = set()
    while heap:
        h, c = heapq.heappop(heap)
        if c in done:
            continue
        done.add(c)
        if c not in plateau and ht(c) <= b:
            return h, c, len(best)
        if len(best) > budget:
            break
        for k in range(4):
            m = mutate(c, k)
            hm = ht(m)
            if hm > bound:
                continue
            m = canon(m)
            v = h if h > hm else hm
            if v < best.get(m, 1 << 62):
                best[m] = v
                heapq.heappush(heap, (v, m))
    return None, None, len(best)


# ----------------------------------------------------------------------------- forks (Warkentin)
def acyclic_on(q, verts):
    rem = set(verts)
    while rem:
        src = [i for i in rem if not any(ent(q, j, i) > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def fork_return(q):
    """Point of return if q is a fork (Warkentin, Def. 2.1), else None."""
    if min(abs(x) for x in q) < 2 or acyclic_on(q, range(4)):
        return None
    for r in range(4):
        Qm = [i for i in range(4) if ent(q, i, r) > 0]
        Qp = [j for j in range(4) if ent(q, r, j) > 0]
        if all(ent(q, j, i) > ent(q, i, r) and ent(q, j, i) > ent(q, r, j) for i in Qm for j in Qp) \
                and acyclic_on(q, Qm) and acyclic_on(q, Qp):
            return r
    return None


# ----------------------------------------------------------------------------- lines (rank-2 orbits)
def Lam(xk, yk, xl, yl, z, c=2):
    """The quiver with vertices (0, 1, 2, 3) = (i, j, k, l): c arrows i -> j, x_u = b_{u,i}, y_u = b_{u,j}
    for u = k, l, and z = b_kl."""
    return (c, -xk, -xl, -yk, -yl, z)


def lam_coords(q):
    return (-q[1], -q[3], -q[2], -q[4], q[5], q[0])


def fwd(q):
    """Forward step on the line of the pair (0, 1): mutate at the source 0 of the arrow, swap the labels 0, 1."""
    return relabel(mutate(q, 0), (1, 0, 2, 3))


def bwd(q):
    return relabel(mutate(q, 1), (1, 0, 2, 3))


def sigma(c, x, y):
    return (y + c * max(x, 0), -x)


def tri(c, x, y):
    """Markov constant of the triangle {u, i, j}: c^2 + x^2 + y^2 - c|xy| if it is an oriented cycle
    (x > 0 > y), and + c|xy| otherwise."""
    return c * c + x * x + y * y + (-c * abs(x * y) if x > 0 > y else c * abs(x * y))


def line_step(c, s):
    xk, yk, xl, yl, z = s
    return sigma(c, xk, yk) + sigma(c, xl, yl) + (z + max(xk, 0) * max(-xl, 0) - max(-xk, 0) * max(xl, 0),)


def line_back(c, s):
    xk2, yk2, xl2, yl2, z2 = s
    xk, yk = -yk2, xk2 - c * max(-yk2, 0)
    xl, yl = -yl2, xl2 - c * max(-yl2, 0)
    return (xk, yk, xl, yl, z2 - (max(xk, 0) * max(-xl, 0) - max(-xk, 0) * max(xl, 0)))


# ----------------------------------------------------------------------------- the family Q_t
def Nt(t):
    return 2 * t ** 3 - t * t - t


def Ht(t):
    return 2 * t ** 4 - t ** 3 - t * t + 2 * t


def Qt(t, b=None):
    if b is None:
        b = t * t
    return (-b, -(2 * t * t - 1 - b), 2 * t, -2, b - t, -b)


def Ht2(t, b):
    return (2 * t * t + t - 1) * b - 2 * t ** 3 + 2 * t


def qseq(t, m):
    return t * t + (m - 1) * (2 * t * t - 1)


def Kq(t, j):
    """First line of the region, 0 <= j <= t, in line coordinates."""
    if j == 0:
        return Lam(-(t * t - 1), -t * t, t * t, -t * (t - 1), 2 * t)
    if j <= t - 1:
        return Lam(qseq(t, j), -qseq(t, j + 1), t * (t - j), -t * (t - j - 1), 2 * t)
    if j == t:
        return Lam(qseq(t, t), -qseq(t, t + 1), 0, t, 2 * t)
    raise ValueError(j)


def Lq(t, n):
    """Second line of the region, -2 <= n <= N + 1."""
    N = Nt(t)
    u = N + 1 - n
    if n >= 1:
        return Lam(t * (n - 1), -t * n, u + 1, -u, 2 * t)
    if n == 0:
        return Lam(-t, 0, N + 2, -(N + 1), 2 * t)
    if n == -1:
        return Lam(0, t, N + 3, -(N + 2), -t * N)
    if n == -2:
        return Lam(t, 0, N + 4, -(N + 3), -t * N)
    raise ValueError(n)


def region(q, H, b):
    """Quivers reached from q through non-forks of height < H and forks of height <= b."""
    s = canon(q)
    seen = {s}
    dq = deque([s])
    while dq:
        c = dq.popleft()
        for k in range(4):
            m = mutate(c, k)
            h = ht(m)
            if h >= H or (h > b and fork_return(m) is not None):
                continue
            m = canon(m)
            if m not in seen:
                seen.add(m)
                dq.append(m)
    return seen


def family_check(t):
    b, H, N = t * t, Ht(t), Nt(t)
    assert canon(Kq(t, 0)) == canon(Qt(t))
    members = {}
    for j in range(0, t + 1):
        members[canon(Kq(t, j))] = ("K", j)
    for n in range(-2, N + 2):
        members[canon(Lq(t, n))] = ("L", n)
    assert len(members) == N + t + 5
    for j in range(0, t):
        assert bwd(Kq(t, j)) == Kq(t, j + 1)
    for n in range(-2, N + 1):
        assert bwd(Lq(t, n)) == Lq(t, n + 1)
    table = defaultdict(list)
    for c, (fam, idx) in members.items():
        X = Kq(t, idx) if fam == "K" else Lq(t, idx)
        for v in range(4):
            m = mutate(X, v)
            cm, h = canon(m), ht(m)
            if cm in members:
                f2, i2 = members[cm]
                kind = "%s(%+d)" % (f2, i2 - idx) if f2 == fam else "%s(%d)" % (f2, i2)
            elif h >= H:
                kind = "height = H" if h == H else "height > H"
            elif h > b and fork_return(m) is not None:
                kind = "fork"
            else:
                kind = "LEAK"
            table[(fam, v, kind)].append(idx)
    S = region(Qt(t), H, b)
    e = escape(Qt(t), H + 1)
    return {"t": t, "b": b, "N": N, "H": H, "members": len(members), "region_equals_members": S == set(members),
            "leaks": sum(len(v) for k, v in table.items() if k[2] == "LEAK"),
            "mirror_in_region": canon(neg(Qt(t))) in members, "max_height_in_region": max(ht(x) for x in members),
            "only_Q_at_or_below_b": [members[x] for x in members if ht(x) <= b] == [("K", 0)],
            "escape": e[0], "escape_reaches_mirror": e[1] == canon(neg(Qt(t))), "seen": e[2], "pfaffian": pf(Qt(t)),
            "table": {"%s mu_%d %s" % k: _ranges(v) for k, v in sorted(table.items())}}


def _ranges(ix):
    ix = sorted(ix)
    out, s, p = [], ix[0], ix[0]
    for x in ix[1:]:
        if x != p + 1:
            out.append([s, p])
            s = x
        p = x
    out.append([s, p])
    return out


def cmd_family(args):
    ok = True
    for t in range(3, args.tmax + 1):
        r = family_check(t)
        good = (r["region_equals_members"] and r["leaks"] == 0 and not r["mirror_in_region"] and r["escape"] == r["H"]
                and r["escape_reaches_mirror"] and r["max_height_in_region"] < r["H"] and r["only_Q_at_or_below_b"]
                and r["members"] == 2 * t ** 3 - t * t + 5)
        ok &= good
        print(json.dumps({k: v for k, v in r.items() if k != "table" or t in args.show}))
        sys.stdout.flush()
    print("ALL OK" if ok else "FAILED")
    # remark after Theorem 15.6: H_t with t = floor(sqrt(w)) is at least 2 w^2 - 9 w^(3/2), i.e. (2w^2 - H)^2 <= 81 w^3
    import math
    good = all((2 * w * w - Ht(math.isqrt(w))) ** 2 <= 81 * w ** 3 and 2 * w * w >= Ht(math.isqrt(w))
               for w in range(9, 200001))
    print("H_floor(sqrt(w)) >= 2w^2 - 9w^(3/2) for 9 <= w <= 200000: %s" % good)
    print("t, t^2, H_t, H_t/t^4: %s" % [(t, t * t, Ht(t), round(Ht(t) / t ** 4, 4)) for t in (3, 4, 5, 6, 8, 10, 15, 20, 30, 100)])


# ----------------------------------------------------------------------------- polynomials
class P:
    """Integer polynomial in the variables VARS, as a dict exponent-tuple -> coefficient."""
    VARS = ("t", "n", "u", "j", "v")
    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = {k: v for k, v in (c or {}).items() if v}

    @staticmethod
    def const(a):
        return P({(0,) * len(P.VARS): a})

    @staticmethod
    def var(name):
        e = [0] * len(P.VARS)
        e[P.VARS.index(name)] = 1
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

    def __pow__(self, m):
        r = P.const(1)
        for _ in range(m):
            r = r * self
        return r

    def __eq__(self, o):
        return self.c == P.lift(o).c

    def __hash__(self):
        return hash(frozenset(self.c.items()))

    def is_zero(self):
        return not self.c

    def subs(self, name, poly):
        """Substitute the polynomial `poly` for the variable `name`."""
        i = P.VARS.index(name)
        poly = P.lift(poly)
        r = P()
        for k, v in self.c.items():
            e = list(k)
            d, e[i] = e[i], 0
            r = r + P({tuple(e): v}) * poly ** d
        return r

    def value(self, **kw):
        s = 0
        for k, v in self.c.items():
            for name, e in zip(P.VARS, k):
                if e:
                    v *= kw[name] ** e
            s += v
        return s

    def __repr__(self):
        if not self.c:
            return "0"
        out = []
        for k in sorted(self.c, reverse=True):
            mono = "*".join(n if e == 1 else "%s^%d" % (n, e) for n, e in zip(P.VARS, k) if e)
            v = self.c[k]
            out.append(("%+d" % v) + ("*" + mono if mono else "") if (abs(v) != 1 or not mono) else ("+" if v > 0 else "-") + mono)
        return " ".join(out)


def nonneg(p, dom):
    """Certificate that p >= 0 on the orthant {var >= dom[var]}: after the shift var = dom[var] + var',
    every coefficient is >= 0.  Every variable of p must have a lower bound in dom."""
    p = P.lift(p)
    used = {P.VARS[i] for k in p.c for i, e in enumerate(k) if e}
    if not used <= set(dom):
        raise ValueError("no lower bound for %s" % sorted(used - set(dom)))
    for name, lb in dom.items():
        if lb:
            p = p.subs(name, P.var(name) + lb)
    return all(v >= 0 for v in p.c.values())


def wsign(p, dom):
    """+1 if p >= 0 on dom, -1 if p <= 0 on dom (certified); raises if neither certificate is found."""
    if nonneg(p, dom):
        return 1
    if nonneg(-P.lift(p), dom):
        return -1
    raise ValueError("sign not certified: %r on %r" % (p, dom))


def ssign(p, dom):
    """+1 if p >= 1 on dom, -1 if p <= -1 on dom (certified); raises otherwise."""
    if nonneg(P.lift(p) - 1, dom):
        return 1
    if nonneg(-P.lift(p) - 1, dom):
        return -1
    raise ValueError("strict sign not certified: %r on %r" % (p, dom))


def sent(q, i, j):
    if i == j:
        return P.const(0)
    return P.lift(q[IDX[(i, j)]]) if i < j else -P.lift(q[IDX[(j, i)]])


def smutate(q, k, dom):
    """Mutation of a quiver with polynomial entries; the signs of the three entries at k are certified on dom."""
    sg = {i: wsign(sent(q, i, k), dom) for i in range(4) if i != k}       # sign of b_ik
    out = []
    for (i, j) in PAIRS:
        b = P.lift(q[IDX[(i, j)]])
        if i == k or j == k:
            out.append(-b)
        else:
            bik, bkj = sent(q, i, k), sent(q, k, j)
            if sg[i] > 0 and sg[j] < 0:          # b_ik >= 0 and b_kj = -b_jk >= 0
                b = b + bik * bkj
            elif sg[i] < 0 and sg[j] > 0:        # b_ik <= 0 and b_kj <= 0
                b = b - bik * bkj
            out.append(b)
    return tuple(out)


def srelabel(q, p):
    return tuple(s * P.lift(q[i]) for i, s in PTAB[PERMS.index(tuple(p))])


def sLam(xk, yk, xl, yl, z):
    return tuple(P.lift(x) for x in (2, -P.lift(xk), -P.lift(xl), -P.lift(yk), -P.lift(yl), z))


def cert_height(q, H, dom):
    """Some entry e of q has |e| >= H on dom.  Returns the index of the entry, or None."""
    for a, e in enumerate(q):
        try:
            s = wsign(e, dom)
        except ValueError:
            continue
        if nonneg(s * P.lift(e) - H, dom):
            return a
    return None


def cert_fork(q, dom, b):
    """q is a fork on dom (every sign strict, every entry >= 2 in absolute value, a point of return r with
    the strict inequalities, Q^-(r) and Q^+(r) acyclic, q not acyclic) and some entry exceeds b.
    Returns r, or None."""
    try:
        sg = {(i, j): ssign(sent(q, i, j), dom) for i in range(4) for j in range(4) if i != j}
    except ValueError:
        return None
    if not all(nonneg(sg[p] * sent(q, *p) - 2, dom) for p in PAIRS):
        return None
    w = lambda i, j: sg[(i, j)] * sent(q, i, j)                 # weight of the arrow between i and j
    arrow = lambda i, j: sg[(i, j)] > 0                         # i -> j

    def acyc(vs):
        rem = set(vs)
        while rem:
            src = [i for i in rem if not any(arrow(j, i) for j in rem if j != i)]
            if not src:
                return False
            rem -= set(src)
        return True
    if acyc(range(4)):
        return None
    if not any(nonneg(sg[p] * sent(q, *p) - b - 1, dom) for p in PAIRS):
        return None
    for r in range(4):
        Qm = [i for i in range(4) if i != r and arrow(i, r)]
        Qp = [j for j in range(4) if j != r and arrow(r, j)]
        if not (acyc(Qm) and acyc(Qp)):
            continue
        if all(arrow(j, i) and nonneg(w(j, i) - w(i, r) - 1, dom) and nonneg(w(j, i) - w(r, j) - 1, dom)
               for i in Qm for j in Qp):
            return r
    return None


def same_up_to_relabelling(q1, q2):
    for p in PERMS:
        if all((P.lift(a) - P.lift(b)).is_zero() for a, b in zip(srelabel(q1, p), q2)):
            return p
    return None


def cmd_prove(args):
    """Theorem 15.6: every exit of the region is a member, has height >= H_t, or is a fork higher than t^2."""
    t, n, u, j, v = (P.var(x) for x in P.VARS)
    one = P.const(1)
    results = []
    ok = True

    def claim(label, good, detail=""):
        nonlocal ok
        ok &= bool(good)
        results.append((label, bool(good), detail))
        print("%-58s %-6s %s" % (label, "ok" if good else "FAILED", detail))

    def exit_claim(label, q, k, dom, H, b, expect, target=None):
        """The mutation of q at k on dom: 'height', 'fork', or 'member' (equal to target up to relabelling)."""
        m = smutate(q, k, dom)
        if expect == "member":
            p = same_up_to_relabelling(m, target)
            claim(label, p is not None, "equals the target after the relabelling %s" % (p,))
        elif expect == "height":
            a = cert_height(m, H, dom)
            claim(label, a is not None, "entry b%d%d has absolute value >= H" % PAIRS[a] if a is not None else "")
        elif expect == "fork":
            r = cert_fork(m, dom, b)
            claim(label, r is not None, "fork with point of return %s, higher than t^2" % r)
        return m

    # ---- the first line K(j), with t = j + v + 1 for the general member
    D_t = {"t": 3}
    N1 = 2 * t ** 3 - t * t - t
    H1 = t * (N1 + 2)
    b1 = t * t
    q1 = lambda m: t * t + (m - 1) * (2 * t * t - 1)                    # q_m in terms of t and a polynomial m
    K0 = sLam(-(t * t - 1), -t * t, t * t, -t * (t - 1), 2 * t)
    Kt = sLam(q1(t), -q1(t + 1), 0, t, 2 * t)
    Ktm1 = sLam(q1(t - 1), -q1(t), t, 0, 2 * t)
    L0 = sLam(-t, 0, N1 + 2, -(N1 + 1), 2 * t)
    L1 = sLam(0, -t, N1 + 1, -N1, 2 * t)
    Lm1 = sLam(0, t, N1 + 3, -(N1 + 2), -t * N1)
    Lm2 = sLam(t, 0, N1 + 4, -(N1 + 3), -t * N1)
    claim("H_t = t(N+2) = 2t^4 - t^3 - t^2 + 2t", (H1 - (2 * t ** 4 - t ** 3 - t * t + 2 * t)).is_zero())
    claim("Pf(Q_t) = 2t^4 - t^3 - t^2 - 3t = H_t - 5t",
          (K0[0] * K0[5] - K0[1] * K0[4] + K0[2] * K0[3] + (H1 - 5 * t)).is_zero() or
          (K0[0] * K0[5] - K0[1] * K0[4] + K0[2] * K0[3] - (H1 - 5 * t)).is_zero())
    Qt_s = (-t * t, -(t * t - 1), 2 * t, P.const(-2), t * t - t, -t * t)
    claim("K(0) is Q_t relabelled", same_up_to_relabelling(K0, Qt_s) is not None)

    # general member K(j), 1 <= j <= t - 1, in the variables j, v with t = j + v + 1
    tt = j + v + 1
    qg = lambda m: tt * tt + (m - 1) * (2 * tt * tt - 1)
    Kj = sLam(qg(j), -qg(j + 1), tt * (tt - j), -tt * (tt - j - 1), 2 * tt)
    Kj_next = sLam(qg(j + 1), -qg(j + 2), tt * (tt - j - 1), -tt * (tt - j - 2), 2 * tt)
    Ng = 2 * tt ** 3 - tt * tt - tt
    Hg = tt * (Ng + 2)
    bg = tt * tt
    doms_K = [{"j": 1, "v": 1}, {"j": 2, "v": 0}]                       # together: 1 <= j <= t - 1, t >= 3
    for d in doms_K:
        tag = " [j>=%d, v>=%d]" % (d["j"], d["v"])
        if d["v"] >= 1:
            m = srelabel(smutate(Kj, 1, d), (1, 0, 2, 3))
            claim("K(j) backward step is K(j+1), j <= t-2" + tag, all((a - c).is_zero() for a, c in zip(m, Kj_next)))
        exit_claim("mu_k K(j), 1 <= j <= t-1: height >= H" + tag, Kj, 2, d, Hg, bg, "height")
    exit_claim("mu_l K(j), 1 <= j <= t-2: fork", Kj, 3, {"j": 1, "v": 1}, Hg, bg, "fork")
    # j = 0
    m = srelabel(smutate(K0, 1, D_t), (1, 0, 2, 3))
    K1 = sLam(q1(one), -q1(one * 2), t * (t - 1), -t * (t - 2), 2 * t)
    claim("K(0) backward step is K(1)", all((a - c).is_zero() for a, c in zip(m, K1)))
    exit_claim("K(0) forward step (K(-1)): fork", K0, 0, D_t, H1, b1, "fork")
    exit_claim("mu_k K(0): fork", K0, 2, D_t, H1, b1, "fork")
    exit_claim("mu_l K(0): fork", K0, 3, D_t, H1, b1, "fork")
    # j = t - 1 and j = t
    m = srelabel(smutate(Ktm1, 1, D_t), (1, 0, 2, 3))
    claim("K(t-1) backward step is K(t)", all((a - c).is_zero() for a, c in zip(m, Kt)))
    exit_claim("mu_l K(t-1) = L(0)", Ktm1, 3, D_t, H1, b1, "member", L0)
    exit_claim("mu_k K(t-1): height >= H", Ktm1, 2, D_t, H1, b1, "height")
    exit_claim("mu_l K(t) = L(1)", Kt, 3, D_t, H1, b1, "member", L1)
    exit_claim("mu_k K(t): height >= H", Kt, 2, D_t, H1, b1, "height")
    exit_claim("K(t) backward step (K(t+1)): height >= H", Kt, 1, D_t, H1, b1, "height")

    # ---- the second line L(n) = Lam(t(n-1), -tn, u+1, -u, 2t), n + u = N + 1; here n, u, t are free
    Ln = sLam(t * (n - 1), -t * n, u + 1, -u, 2 * t)
    Hf = t * (n + u + 1)                                                 # H = t(N + 2) with N + 1 = n + u
    bf = t * t
    d = {"t": 3, "n": 1, "u": 1}
    m = srelabel(smutate(Ln, 1, d), (1, 0, 2, 3))
    Ln_next = sLam(t * n, -t * (n + 1), u, -(u - 1), 2 * t)
    claim("L(n) backward step is L(n+1), 1 <= n <= N", all((a - c).is_zero() for a, c in zip(m, Ln_next)))
    exit_claim("mu_l L(n), 1 <= n <= N+1: height >= H", Ln, 3, {"t": 3, "n": 1, "u": 0}, Hf, bf, "height")
    exit_claim("mu_k L(n), 2 <= n <= N: fork", Ln, 2, {"t": 3, "n": 2, "u": 1}, Hf, bf, "fork")
    Lend = tuple(P.lift(e).subs("u", P.const(0)) for e in Ln)            # n = N + 1
    Hend = t * (n + 1)
    exit_claim("mu_k L(N+1): height >= H", Lend, 2, {"t": 3, "n": 1}, Hend, bf, "height")
    exit_claim("L(N+1) backward step: height >= H", Lend, 1, {"t": 3, "n": 1}, Hend, bf, "height")
    md = smutate(smutate(Lend, 1, {"t": 3, "n": 1}), 3, {"t": 3, "n": 1})
    claim("mu_l mu_j L(N+1) = -L(N+1) (the door)", all((a + c).is_zero() for a, c in zip(md, Lend)))
    for k_, name in ((1, "mu_j"), (3, "mu_l")):
        m = smutate(Lend, k_, {"t": 3, "n": 1})
        claim("%s L(N+1) has height exactly H" % name,
              cert_height(m, Hend, {"t": 3, "n": 1}) is not None and
              all(nonneg(Hend - s * P.lift(e), {"t": 3, "n": 1}) for e in m for s in (1, -1)))
    # the end n <= 1 of the second line: polynomials in t
    m = srelabel(smutate(L1, 0, D_t), (1, 0, 2, 3))
    claim("L(1) forward step is L(0)", all((a - c).is_zero() for a, c in zip(m, L0)))
    m = srelabel(smutate(L0, 0, D_t), (1, 0, 2, 3))
    claim("L(0) forward step is L(-1)", all((a - c).is_zero() for a, c in zip(m, Lm1)))
    m = srelabel(smutate(Lm1, 0, D_t), (1, 0, 2, 3))
    claim("L(-1) forward step is L(-2)", all((a - c).is_zero() for a, c in zip(m, Lm2)))
    exit_claim("L(-2) forward step (L(-3)): fork", Lm2, 0, D_t, H1, b1, "fork")
    L1n = tuple(P.lift(e).subs("n", one).subs("u", N1) for e in Ln)
    claim("L(1) is the member n = 1 of the general formula", all((a - c).is_zero() for a, c in zip(L1n, L1)))
    exit_claim("mu_k L(1) = K(t)", L1, 2, D_t, H1, b1, "member", Kt)
    exit_claim("mu_k L(0) = K(t-1)", L0, 2, D_t, H1, b1, "member", Ktm1)
    exit_claim("mu_l L(0): height >= H", L0, 3, D_t, H1, b1, "height")
    exit_claim("mu_k L(-1): height >= H", Lm1, 2, D_t, H1, b1, "height")
    exit_claim("mu_l L(-1): height >= H", Lm1, 3, D_t, H1, b1, "height")
    exit_claim("mu_k L(-2): height >= H", Lm2, 2, D_t, H1, b1, "height")
    exit_claim("mu_l L(-2): height >= H", Lm2, 3, D_t, H1, b1, "height")

    # ---- heights of the members: all below H; only K(0) is at or below t^2
    below = lambda q, H, dom: all(nonneg(H - 1 - s * P.lift(e), dom) for e in q for s in (1, -1))
    claim("K(0), K(t-1), K(t), L(0), L(-1), L(-2) are below H",
          all(below(q, H1, D_t) for q in (K0, Ktm1, Kt, L0, Lm1, Lm2)))
    claim("K(j), 1 <= j <= t-1, is below H", all(below(Kj, Hg, d) for d in doms_K))
    # n + u = N + 1 >= 2, so n >= 2 or u >= 1
    claim("L(n), 1 <= n <= N+1, is below H",
          all(below(Ln, Hf, d) for d in ({"t": 3, "n": 2, "u": 0}, {"t": 3, "n": 1, "u": 1})))
    claim("K(j), 1 <= j <= t-1, has an entry above t^2", all(nonneg(qg(j + 1) - bg - 1, d) for d in doms_K))
    claim("K(t), L(0), L(-1), L(-2) have an entry above t^2",
          all(nonneg(e - b1 - 1, D_t) for e in (q1(t + 1), N1 + 2, N1 + 3, N1 + 4)))
    # L(n): n + u = N + 1 > 2 t^2, so t n > t^2 or u + 1 > t^2
    claim("N + 1 - t - t^2 >= 1 (so L(n), n >= 1, has an entry above t^2)", nonneg(N1 + 1 - t - t * t - 1, D_t))
    print("\n%d claims, %s" % (len(results), "ALL CERTIFIED" if ok else "SOME FAILED"))


# ----------------------------------------------------------------------------- the family R_b (plateau type)
def Rb(b):
    return (-b, -b, b - 1, -2, b - 2, -b)


def HRb(b):
    return 2 * b * b - 3 * b - 3


def Aq(b, j):
    """The line of R_b for even b = 2c: A(0) = R_b, ..., A(c)."""
    c = b // 2
    if j == 0:
        return Lam(-b, -b, b, -(b - 2), b - 1)
    if j <= c - 1:
        return Lam((2 * j - 1) * b, -(2 * j + 1) * b, 2 * (c - j), -2 * (c - j - 1), b - 1)
    if j == c:
        return Lam((2 * c - 1) * b, -(2 * c + 1) * b, 0, 2, b - 1)
    raise ValueError(j)


def Pq(b, m):
    """The plateau of R_b, 1 <= m <= T = b(b-1)/2, in the labels of B; all of height H."""
    T, H = b * (b - 1) // 2, HRb(b)
    if m == 1:
        return Lam(2 * (T - 2), -2 * (T - 1), 0, 2, H)
    if m <= T - 1:
        return Lam(2 * (T - 1 - m), -2 * (T - m), 2 * (m - 1), -2 * (m - 2), H)
    if m == T:
        return Lam(-2, 0, 2 * (T - 1), -2 * (T - 2), H)
    raise ValueError(m)


def family3_check(b):
    H = HRb(b)
    q = Rb(b)
    e = escape(q, H + 1)
    r = {"b": b, "H": H, "escape": e[0], "escape_reaches_mirror": e[1] == canon(neg(q)), "seen": e[2], "pfaffian": pf(q),
         "region": len(region(q, H, b))}
    if b % 2 == 0 and b >= 6:
        c, T = b // 2, b * (b - 1) // 2
        assert canon(Aq(b, 0)) == canon(q)
        for j in range(c):
            assert bwd(Aq(b, j)) == Aq(b, j + 1)
        B, B2 = mutate(Aq(b, c - 1), 3), mutate(Aq(b, c), 3)
        members = {canon(Aq(b, j)): "A(%d)" % j for j in range(c + 1)}
        members[canon(B)] = "B"
        members[canon(B2)] = "B'"
        table = {}
        for name, X in [("A(%d)" % j, Aq(b, j)) for j in range(c + 1)] + [("B", B), ("B'", B2)]:
            row = []
            for v in range(4):
                m = mutate(X, v)
                cm, h = canon(m), ht(m)
                row.append(members[cm] if cm in members else ("height = H" if h == H else "height > H") if h >= H
                           else "fork" if (h > b and fork_return(m) is not None) else "LEAK")
            table[name] = row
        x = B
        route_ok = fwd(B) == Pq(b, 1)
        for m in range(1, T):
            route_ok &= fwd(Pq(b, m)) == Pq(b, m + 1) and ht(Pq(b, m)) == H
        end = fwd(Pq(b, T))
        route_ok &= ht(Pq(b, T)) == H and canon(end) == canon(neg(B)) and ht(B) < H
        r.update({"members": len(members), "region_equals_members": region(q, H, b) == set(members),
                  "leaks": sum(row.count("LEAK") for row in table.values()), "plateau_quivers": T, "route_ok": bool(route_ok),
                  "only_R_at_or_below_b": [members[x] for x in members if ht(x) <= b] == ["A(0)"],
                  "max_height_in_region": max(ht(x) for x in members), "table": table})
    return r


def cmd_family3(args):
    ok = True
    for b in range(5, args.bmax + 1):
        r = family3_check(b)
        good = r["escape"] == r["H"] and r["escape_reaches_mirror"]
        if "members" in r:
            good &= (r["region_equals_members"] and r["leaks"] == 0 and r["route_ok"] and r["only_R_at_or_below_b"]
                     and r["members"] == b // 2 + 3 and r["max_height_in_region"] < r["H"])
        ok &= bool(good)
        print(json.dumps({k: v for k, v in r.items() if k != "table" or b in args.show}))
        sys.stdout.flush()
    print("ALL OK" if ok else "FAILED")
    good = all(2 * w * w - 7 * w + 2 <= HRb(w if w % 2 == 0 else w - 1) for w in range(6, 100001))
    print("H(R_b) with b the largest even number <= w is at least 2w^2 - 7w + 2 for 6 <= w <= 100000: %s" % good)


def cmd_prove2(args):
    """Theorem 15.13 for b = 2c, c >= 3.  The polynomial variable t stands for c."""
    c, n, u, j, v = (P.var(x) for x in P.VARS)
    ok = True
    count = 0

    def claim(label, good, detail=""):
        nonlocal ok, count
        ok &= bool(good)
        count += 1
        print("%-62s %-6s %s" % (label, "ok" if good else "FAILED", detail))

    def exit_claim(label, q, k, dom, H, b, expect, target=None):
        m = smutate(q, k, dom)
        if expect == "member":
            p = same_up_to_relabelling(m, target)
            claim(label, p is not None, "equals the target after the relabelling %s" % (p,))
        elif expect == "height":
            a = cert_height(m, H, dom)
            claim(label, a is not None, "entry b%d%d has absolute value >= H" % PAIRS[a] if a is not None else "")
        elif expect == "fork":
            r = cert_fork(m, dom, b)
            claim(label, r is not None, "fork with point of return %s, higher than b" % r)
        return m

    D = {"t": 3}
    b = 2 * c
    H = 2 * b * b - 3 * b - 3
    T = c * (2 * c - 1)                                                  # b(b-1)/2
    A0 = sLam(-b, -b, b, -(b - 2), b - 1)
    Ac1 = sLam((2 * c - 3) * b, -(2 * c - 1) * b, 2, 0, b - 1)           # A(c-1)
    Ac = sLam((2 * c - 1) * b, -(2 * c + 1) * b, 0, 2, b - 1)            # A(c)
    Rs = (-b, -b, b - 1, P.const(-2), b - 2, -b)
    claim("A(0) is R_b relabelled", same_up_to_relabelling(A0, Rs) is not None)
    claim("Pf(R_b) = 2(b-1)^2 = H - (b-5)", (Rs[0] * Rs[5] - Rs[1] * Rs[4] + Rs[2] * Rs[3] - 2 * (b - 1) * (b - 1)).is_zero()
          and (H - (b - 5) - 2 * (b - 1) * (b - 1)).is_zero())
    # general member A(j), 1 <= j <= c - 2, with c = j + v + 1
    cc = j + v + 1
    bb = 2 * cc
    Hg = 2 * bb * bb - 3 * bb - 3
    Aj = sLam((2 * j - 1) * bb, -(2 * j + 1) * bb, 2 * (cc - j), -2 * (cc - j - 1), bb - 1)
    Aj_next = sLam((2 * j + 1) * bb, -(2 * j + 3) * bb, 2 * (cc - j - 1), -2 * (cc - j - 2), bb - 1)
    dj = {"j": 1, "v": 1}                                                # 1 <= j <= c - 2, hence c >= 3
    m_ = srelabel(smutate(Aj, 1, dj), (1, 0, 2, 3))
    claim("A(j) backward step is A(j+1), 1 <= j <= c-2", all((a - e).is_zero() for a, e in zip(m_, Aj_next)))
    exit_claim("mu_k A(j), 1 <= j <= c-2: height >= H", Aj, 2, dj, Hg, bb, "height")
    exit_claim("mu_l A(j), 1 <= j <= c-2: fork", Aj, 3, dj, Hg, bb, "fork")
    A1 = sLam(b, -3 * b, 2 * (c - 1), -2 * (c - 2), b - 1)
    m_ = srelabel(smutate(A0, 1, D), (1, 0, 2, 3))
    claim("A(0) backward step is A(1)", all((a - e).is_zero() for a, e in zip(m_, A1)))
    A1g = tuple(P.lift(e).subs("j", P.const(1)).subs("v", c - 2) for e in Aj)
    claim("A(1) is the member j = 1 of the general formula", all((a - e).is_zero() for a, e in zip(A1g, A1)))
    Ac1g = tuple(P.lift(e).subs("v", P.const(0)).subs("j", c - 1) for e in Aj)
    claim("A(c-1) is the member j = c-1 of the general formula", all((a - e).is_zero() for a, e in zip(Ac1g, Ac1)))
    exit_claim("A(0) forward step: fork", A0, 0, D, H, b, "fork")
    exit_claim("mu_k A(0): fork", A0, 2, D, H, b, "fork")
    exit_claim("mu_l A(0): fork", A0, 3, D, H, b, "fork")
    m_ = srelabel(smutate(Ac1, 1, D), (1, 0, 2, 3))
    claim("A(c-1) backward step is A(c)", all((a - e).is_zero() for a, e in zip(m_, Ac)))
    # A(c-2) -> A(c-1): the general step at j = c - 2 has v = 1, covered above
    exit_claim("mu_k A(c-1): height >= H", Ac1, 2, D, H, b, "height")
    Bq = (P.const(2), -(b * b - b - 2), P.const(2), b * b - b, P.const(0), -(b - 1))
    B2 = (P.const(2), -(b * b - b), P.const(0), b * b - b + 2, P.const(2), -(b - 1))
    m_ = smutate(Ac1, 3, D)
    claim("mu_l A(c-1) = B", all((a - e).is_zero() for a, e in zip(m_, Bq)))
    exit_claim("A(c) backward step: height >= H", Ac, 1, D, H, b, "height")
    exit_claim("mu_k A(c): height >= H", Ac, 2, D, H, b, "height")
    m_ = smutate(Ac, 3, D)
    claim("mu_l A(c) = B'", all((a - e).is_zero() for a, e in zip(m_, B2)))
    m_ = srelabel(smutate(Bq, 1, D), (1, 0, 2, 3))
    claim("B backward step is B'", all((a - e).is_zero() for a, e in zip(m_, B2)))
    exit_claim("mu_k B: height >= H", Bq, 2, D, H, b, "height")
    exit_claim("B' backward step: fork", B2, 1, D, H, b, "fork")
    exit_claim("mu_k B': height >= H", B2, 2, D, H, b, "height")
    # the plateau, in the labels of B: P(m) = Lam(2u, -2(u+1); 2(m-1), -2(m-2); H) with u = T - 1 - m
    P1 = sLam(2 * (T - 2), -2 * (T - 1), 0, 2, H)
    m_ = srelabel(smutate(Bq, 0, D), (1, 0, 2, 3))
    claim("B forward step is P(1), of height exactly H", all((a - e).is_zero() for a, e in zip(m_, P1))
          and all(nonneg(H - s * P.lift(e), D) for e in P1 for s in (1, -1)))
    P2 = sLam(2 * (T - 3), -2 * (T - 2), 2, 0, H)
    m_ = srelabel(smutate(P1, 0, D), (1, 0, 2, 3))
    claim("P(1) forward step is P(2)", all((a - e).is_zero() for a, e in zip(m_, P2)))
    Hf = P.var("t")                                                      # in the general step H is a free symbol >= 0
    Pm = sLam(2 * u, -2 * (u + 1), 2 * (n - 1), -2 * (n - 2), Hf)
    Pm_next = sLam(2 * (u - 1), -2 * u, 2 * n, -2 * (n - 1), Hf)
    m_ = srelabel(smutate(Pm, 0, {"n": 2, "u": 1, "t": 0}), (1, 0, 2, 3))
    claim("P(m) forward step is P(m+1), 2 <= m <= T-2", all((a - e).is_zero() for a, e in zip(m_, Pm_next)))
    PT1 = sLam(0, -2, 2 * (T - 2), -2 * (T - 3), H)                      # P(T-1): u = 0
    PT = sLam(-2, 0, 2 * (T - 1), -2 * (T - 2), H)
    m_ = srelabel(smutate(PT1, 0, D), (1, 0, 2, 3))
    claim("P(T-1) forward step is P(T)", all((a - e).is_zero() for a, e in zip(m_, PT)))
    E = srelabel(smutate(PT, 0, D), (1, 0, 2, 3))
    negB = tuple(-P.lift(e) for e in Bq)
    claim("P(T) forward step is -B relabelled", same_up_to_relabelling(E, negB) is not None)
    claim("2T = b^2 - b <= H - 1 (the columns of the plateau stay below H)", nonneg(H - 1 - 2 * T, D))
    below = lambda q, dom, HH: all(nonneg(HH - 1 - s * P.lift(e), dom) for e in q for s in (1, -1))
    claim("A(0), A(c-1), A(c), B, B' are below H", all(below(q, D, H) for q in (A0, Ac1, Ac, Bq, B2)))
    claim("A(j), 1 <= j <= c-2, is below H", below(Aj, dj, Hg))
    claim("A(j), 1 <= j <= c-1, A(c), B, B' have an entry above b",
          nonneg((2 * j + 1) * bb - bb - 1, {"j": 1, "v": 0}) and all(nonneg(e - b - 1, D) for e in ((2 * c + 1) * b, b * b - b, b * b - b + 2)))
    print("\n%d claims, %s" % (count, "ALL CERTIFIED" if ok else "SOME FAILED"))



# ----------------------------------------------------------------------------- family2, doors
def cmd_family2(args):
    print("t  b  H predicted  escape  reaches mirror  H/b^2")
    bad = 0
    for t in range(3, args.tmax + 1):
        for b in range(t * t, 2 * t * t):
            q = Qt(t, b)
            H = Ht2(t, b)
            e = escape(q, H + 1)
            good = e[0] == H and e[1] == canon(neg(q))
            if b == t * t or not good or b == (t + 1) ** 2 - 1:
                print(t, b, H, e[0], e[1] == canon(neg(q)), round(H / b / b, 4))
            if not good:
                bad += 1
                break
    print("first failures listed above" if bad else "all agree")


def door(p, q, r, s):
    """Oriented 4-cycle 0 -> 1 (p), 1 -> 2 (q), 2 -> 3 (r), 3 -> 0 (s) with the diagonal b02 = (rs - pq)/2:
    mu_1 mu_3 D = -D, and both corners of the square have height (pq + rs)/2 when that exceeds p, q, r, s."""
    return (p, (r * s - p * q) // 2, -s, q, 0, r)


def door_side(D, H, budget=100000):
    """Component of D among quivers of height < H: (least height, size, a lowest quiver), or None if it
    contains -D or the budget is exceeded."""
    s0, tgt = canon(D), canon(neg(D))
    if s0 == tgt:
        return None
    seen = {s0}
    dq = deque([s0])
    lo, arg = ht(s0), s0
    while dq:
        c = dq.popleft()
        for k in range(4):
            m = mutate(c, k)
            h = ht(m)
            if h < H:
                m = canon(m)
                if m not in seen:
                    if m == tgt or len(seen) > budget:
                        return None
                    seen.add(m)
                    dq.append(m)
                    if h < lo:
                        lo, arg = h, m
    return lo, len(seen), arg


def _door_task(task):
    p, q, r, smax = task
    out = []
    for s in range(1, smax + 1):
        if (r * s - p * q) % 2 or p * q > r * s:
            continue
        D = door(p, q, r, s)
        H = (r * s + p * q) // 2
        if ht(mutate(D, 1)) != H or ht(mutate(D, 3)) != H:
            continue
        res = door_side(D, H)
        if res is None:
            continue
        out.append((res[0], H, p, q, r, s, res[1], res[2]))
    return out


def cmd_doors(args):
    t0 = time.time()
    tasks = [(p, q, r, args.smax) for q in range(1, args.qmax + 1) for r in range(1, args.rmax + 1)
             for p in range(1, args.pmax + 1)]
    best, total, by_qr = {}, 0, Counter()
    with Pool(args.workers) as pool:
        for out in pool.imap_unordered(_door_task, tasks, chunksize=2):
            for x in out:
                total += 1
                b = x[0]
                if b not in best or x[1] > best[b][1]:
                    best[b] = x
    print("doors D(p,q,r,s) with q <= %d, r <= %d, p <= %d, s <= %d, pq <= rs, whose two sides are not joined "
          "below H = (pq+rs)/2: %d" % (args.qmax, args.rmax, args.pmax, args.smax, total))
    print("bottom b  largest H  H/b^2  door (p,q,r,s)  size of the side  a lowest quiver")
    top = 0
    for b in sorted(best):
        x = best[b]
        if b <= args.bmax:
            print(b, x[1], round(x[1] / b / b, 4), x[2:6], x[6], x[7])
            by_qr[(x[3], x[4])] += 1
            top = max(top, x[1] / b / b)
    print("largest H/b^2 for b <= %d: %.4f; (q, r) of the best door per b: %s; %.0f s"
          % (args.bmax, top, dict(by_qr), time.time() - t0))


# ----------------------------------------------------------------------------- orbit checks
def cmd_orbit(args):
    rng = random.Random(args.seed)
    # (a) the line coordinates: forward step = sigma on both columns, z-rule, and P = c z - Delta
    steps = 0
    for _ in range(args.samples):
        c = rng.randint(2, 6)
        s = tuple(rng.randint(-12, 12) for _ in range(5))
        q = Lam(*s, c=c)
        Pinv = c * s[4] - (s[0] * s[3] - s[2] * s[1])
        assert abs(Pinv) == abs(pf(q))
        for _ in range(8):
            s2 = line_step(c, s)
            q2 = fwd(q)
            assert q2 == Lam(*s2, c=c), (q, s)
            assert line_back(c, s2) == s and bwd(q2) == q
            assert c * s2[4] - (s2[0] * s2[3] - s2[2] * s2[1]) == Pinv
            # Markov constants of the two triangles through the pair are constant on the line
            for (x, y), (x2, y2) in (((s[0], s[1]), (s2[0], s2[1])), ((s[2], s[3]), (s2[2], s2[3]))):
                assert tri(c, x, y) == tri(c, x2, y2)
            s, q = s2, q2
            steps += 1
            if ht(q) > 10 ** 12:
                break
    print("line coordinates, the z-rule, P = c z - Delta and the triangle constants: %d steps, no failure" % steps)
    # (b) bottoms and the valley: closed formulas for one external vertex
    checked = 0
    for c in range(2, 6):
        for a in range(0, 8):
            for e in range(0, 8):
                if a == 0 and e == 0:
                    continue
                p = [-e, a]
                qq = [-a, e]
                for _ in range(12):
                    p.append(c * p[-1] - p[-2])
                    qq.append(c * qq[-1] - qq[-2])
                st = (-e, a)                                   # S_0
                states = {0: st}
                for m in range(1, 12):
                    st = sigma(c, *st)
                    states[m] = st
                    assert st == (p[m], -p[m - 1]), (c, a, e, m)
                st = (-e, a)
                for m in range(1, 12):
                    st = (-st[1], st[0] - c * max(-st[1], 0))
                    states[-m] = st
                    assert st == (qq[m - 1], -qq[m]), (c, a, e, m)
                W = [max(abs(states[m][0]), abs(states[m][1])) for m in range(-11, 12)]
                lo = min(W)
                i0, i1 = W.index(lo), len(W) - 1 - W[::-1].index(lo)
                assert all(W[i] >= W[i + 1] for i in range(i0)) and all(W[i] <= W[i + 1] for i in range(i1, len(W) - 1))
                assert all(w == lo for w in W[i0:i1 + 1])
                checked += 1
    print("bottom states S_n = (p_n, -p_{n-1}), S_{-m} = (q_{m-1}, -q_m) and the valley: %d cases" % checked)
    # (d) the first corridor (section 3.2): a descending column reaches its least height within w - 1 steps,
    #     and until then the other column stays at or below 2w^2 - w
    worst_steps = worst_other = cases = 0
    tight = True
    for w in range(2, 7):
        rr = range(-w, w + 1)
        for xk, yk, xl, yl in itertools.product(rr, repeat=4):
            if not (xk > 0 > yk and -yk > xk) or max(abs(xl), abs(yl)) > w:      # column k descends forward
                continue
            cases += 1
            st = (xk, yk, xl, yl, 0)
            W = max(abs(xk), abs(yk))
            n = other = 0
            while True:
                other = max(other, abs(st[2]), abs(st[3]))
                nxt = line_step(2, st)
                W2 = max(abs(nxt[0]), abs(nxt[1]))
                if W2 >= W:
                    break
                st, W, n = nxt, W2, n + 1
            assert n <= w - 1 and other <= 2 * w * w - w, (w, xk, yk, xl, yl, n, other)
            worst_steps, worst_other = max(worst_steps, n), max(worst_other, other)
    for w in range(2, 41):
        st = (w - 1, -w, w, w, 0)
        for _ in range(w - 1):
            st = line_step(2, st)
        a = max(abs(st[2]), abs(st[3]))
        st = line_step(2, line_step(2, st))
        tight &= a == 2 * w * w - w and (st[0], st[1]) == (0, 1) and max(abs(st[2]), abs(st[3])) == 2 * w * w + 3 * w
    print("first corridor: %d descending columns with w <= 6, never more than w - 1 steps to the least height, other "
          "column never above 2w^2 - w (largest seen: %d steps, %d); Lam(w-1, -w; w, w): 2w^2 - w after w - 1 steps "
          "and 2w^2 + 3w at the bottom position, two steps later, for 2 <= w <= 40: %s" % (cases, worst_steps, worst_other, tight))
    # (c) joins inside a line: largest height strictly between two consecutive positions of height <= w
    for c in args.c:
        for w in range(max(c, 2), args.wmax + 1):
            best = (0, None, 0)
            lines = 0
            rr = range(-w, w + 1)
            for xk, yk, xl, yl, z in itertools.product(rr, repeat=5):
                s0 = (xk, yk, xl, yl, z)
                if max(c, *(abs(x) for x in s0)) != w or (xk == 0 and yk == 0) or (xl == 0 and yl == 0):
                    continue
                lines += 1
                s, gap, n = s0, 0, 0
                while True:
                    s = line_step(c, s)
                    n += 1
                    h = max(c, *(abs(x) for x in s))
                    if h <= w:
                        if gap > best[0]:
                            best = (gap, s0, n)
                        break
                    gap = max(gap, h)
                    if max(abs(s[0]), abs(s[1]), abs(s[2]), abs(s[3])) > w and n > 4 * w + 8:
                        break                                   # both columns past their bottoms: no return
            print("c = %d, w = %d: %d starting points; largest barrier between consecutive low positions %d "
                  "(w^2 = %d) at %s after %d steps" % (c, w, lines, best[0], w * w, best[1], best[2]))
            sys.stdout.flush()


def finite_orbit_barrier(q):
    """For a quiver q with |b01| <= 1: the largest, over the quivers Y of height <= ht(q) in the orbit of
    mu_0, mu_1 that are not isomorphic to q, of the least height of a path from q to a copy of Y inside
    the orbit (0 if there is none, or if no such path leaves height ht(q))."""
    w = ht(q)
    cyc, k = [q], 0
    for _ in range(12):
        nxt = mutate(cyc[-1], k)
        k = 1 - k
        if nxt == q:
            break
        cyc.append(nxt)
    hs = [ht(x) for x in cyc]
    best = {}
    for m in range(1, len(cyc)):
        if hs[m] <= w and canon(cyc[m]) != canon(q):
            via = min(max(hs[1:m], default=0), max(hs[m + 1:], default=0))
            y = canon(cyc[m])
            best[y] = min(best.get(y, 1 << 62), via)
    return max(best.values(), default=0)


def cmd_orbit01(args):
    """Proposition 15.3 for the finite orbits: the square (b01 = 0) and the pentagon (b01 = 1)."""
    for c in (0, 1):
        for w in range(2, args.wmax + 1):
            best = (0, None)
            n = 0
            rr = range(-w, w + 1)
            for rest in itertools.product(rr, repeat=5):
                q = (c,) + rest
                if ht(q) != w:
                    continue
                n += 1
                v = finite_orbit_barrier(q)
                if v > best[0]:
                    best = (v, q)
            print("b01 = %d, w = %d: %d quivers; largest barrier inside the orbit %d (w^2 + w = %d) at %s"
                  % (c, w, n, best[0], w * w + w, best[1]))
            sys.stdout.flush()


# ----------------------------------------------------------------------------- forks
def cmd_forks(args):
    rng = random.Random(args.seed)
    found = steps = 0
    while found < args.samples:
        q = tuple(rng.choice((-1, 1)) * rng.randint(2, 40) for _ in range(6))
        r = fork_return(q)
        if r is None:
            continue
        found += 1
        x, rx = q, r
        for _ in range(6):
            k = rng.choice([v for v in range(4) if v != rx])
            y = mutate(x, k)
            assert fork_return(y) == k, (x, k)
            assert all(abs(b) >= abs(a) for a, b in zip(x, y)) and sum(map(abs, y)) > sum(map(abs, x))
            x, rx = y, k
            steps += 1
            if ht(x) > 10 ** 30:
                break
    print("Lemma 15.4 on %d random forks, %d mutations away from the point of return: no failure" % (found, steps))
    # Lemma 15.5 on the stored optimal join paths of note 11
    try:
        rows = [json.loads(l) for l in open(args.joins)]
    except OSError:
        print("no file %s; skipped the join paths" % args.joins)
        return
    n_paths = n_high = n_forks = 0
    types = Counter()
    for r in rows:
        if not r.get("path"):
            continue
        n_paths += 1
        path = [tuple(M[i][j] for (i, j) in PAIRS) for M in r["path"]]
        w = max(ht(path[0]), ht(path[-1]))
        for x in path:
            if ht(x) > w:
                n_high += 1
                if fork_return(x) is not None:
                    n_forks += 1
                else:
                    m = min(abs(e) for e in x)
                    types["least entry %s" % (m if m <= 2 else ">= 3")] += 1
    print("note 11's %d join paths: %d quivers above the endpoints, %d of them forks; non-forks by least entry: %s"
          % (n_paths, n_high, n_forks, dict(sorted(types.items()))))


# ----------------------------------------------------------------------------- cyclic orderings
ORDS = [(0,) + p for p in itertools.permutations((1, 2, 3))]


def _norm(w):
    i = w.index(0)
    return tuple(w[i:] + w[:i])


def proper_at(q, w, k):
    pos = {v: i for i, v in enumerate(w)}
    ins = [i for i in range(4) if ent(q, i, k) > 0]
    outs = [j for j in range(4) if ent(q, k, j) > 0]
    return all((pos[k] - pos[i]) % 4 < (pos[j] - pos[i]) % 4 for i in ins for j in outs)


def wiggle_class(q, w):
    w = _norm(tuple(w))
    cls, st = {w}, [w]
    while st:
        c = st.pop()
        for a in range(4):
            x, y = c[a], c[(a + 1) % 4]
            if ent(q, x, y) == 0:
                l = list(c)
                l[a], l[(a + 1) % 4] = y, x
                m = _norm(tuple(l))
                if m not in cls:
                    cls.add(m)
                    st.append(m)
    return frozenset(cls)


def proper_classes(q):
    seen, out = set(), []
    for w in ORDS:
        if w in seen:
            continue
        c = wiggle_class(q, w)
        seen |= c
        if all(any(proper_at(q, x, k) for x in c) for k in range(4)):
            out.append(c)
    return out


def markov(q, w):
    v1, v2, v3, v4 = w
    a, b, c = ent(q, v1, v2), ent(q, v1, v3), ent(q, v1, v4)
    d, e, f = ent(q, v2, v3), ent(q, v2, v4), ent(q, v3, v4)
    return a * a + b * b + c * c + d * d + e * e + f * f + a * b * d + a * c * e + b * c * f + d * e * f + a * c * d * f


def proper_mutation(q, cls, k):
    for w in sorted(cls):
        if proper_at(q, w, k):
            outs = {j for j in range(4) if ent(q, k, j) > 0}
            i = w.index(k)
            rest = [w[(i + a) % 4] for a in range(1, 4)]
            last = max([a for a, x in enumerate(rest) if x in outs], default=-1)
            q2 = mutate(q, k)
            return q2, wiggle_class(q2, tuple(rest[:last + 1] + [k] + rest[last + 1:]))
    return None


def totally_proper_to_depth(q, cls, depth):
    """Breadth-first search over proper mutations.  Returns (survives, states, Markov values seen)."""
    seen = {(q, cls)}
    frontier = [(q, cls)]
    vals = set()
    for d in range(depth + 1):
        nxt = []
        for (x, c) in frontier:
            if not all(any(proper_at(x, w, k) for w in c) for k in range(4)):
                return False, len(seen), vals
            vals.add(markov(x, min(c)))
            if d == depth:
                continue
            for k in range(4):
                r = proper_mutation(x, c, k)
                if r not in seen:
                    seen.add(r)
                    nxt.append(r)
        frontier = nxt
    return True, len(seen), vals


def Gk(k):
    return (k, -k, -k, 0, k, -(k - 1))


def cmd_coq(args):
    tests = [("acyclic (1,1,-1,1,0,0), m = 5 in 2610.36179 Remark 4.8", (1, 1, -1, 1, 0, 0)),
             ("2610.36179 Example 5.4, M = 41", (-3, -2, 2, 0, 3, -3))]
    tests += [("G_%d" % k, Gk(k)) for k in (3, 4, 5, 6, 7, 8)]
    tests += [("census extreme b=4 (death 28)", (-3, 4, -4, -2, -4, 4)), ("census extreme b=5 (45)", (-5, -2, 4, -5, 0, -5)),
              ("census extreme b=6 (66)", (6, -6, -6, -2, 5, -6)), ("census extreme b=7 (79)", (-7, -6, 5, -7, 2, -6)),
              ("census extreme b=8 (101)", (2, -6, -8, 8, -8, 7)), ("census extreme b=9 (144)", (-2, -9, 8, 8, -9, -4))]
    tests += [("Q_%d" % t, Qt(t)) for t in (3, 4, 5, 6)]
    tests += [("R_%d" % b, Rb(b)) for b in range(5, 13)]
    print("quiver | height | Pf | proper wiggle classes | Markov value | survives proper mutations to depth %d | states" % args.depth)
    for name, q in tests:
        pcs = proper_classes(q)
        if not pcs:
            print("%s | %d | %d | 0 | - | - | -" % (name, ht(q), pf(q)))
        for c in pcs:
            ok, n, vals = totally_proper_to_depth(q, c, args.depth)
            print("%s | %d | %d | %d | %s | %s | %d" % (name, ht(q), pf(q), len(pcs), sorted(vals), ok, n))
    print("G_k: M = -k^4 + k^3 + 4k^2 - 2k + 1:",
          all(markov(Gk(x), (0, 1, 3, 2)) == -x ** 4 + x ** 3 + 4 * x * x - 2 * x + 1 for x in range(3, 60)))
    # symbolic Markov values (the proper orderings depend only on the signs of the entries)
    t = P.var("t")

    def smarkov(q, w):
        v1, v2, v3, v4 = w
        a, b, c = sent(q, v1, v2), sent(q, v1, v3), sent(q, v1, v4)
        d, e, f = sent(q, v2, v3), sent(q, v2, v4), sent(q, v3, v4)
        return a * a + b * b + c * c + d * d + e * e + f * f + a * b * d + a * c * e + b * c * f + d * e * f + a * c * d * f
    Qs = (-t * t, -(t * t - 1), 2 * t, P.const(-2), t * t - t, -t * t)
    Vs = (-t, P.const(2), P.const(-1), -t, P.const(1), P.const(1))
    Rs = (-t, -t, t - 1, P.const(-2), t - 2, -t)
    print("R_b (b written t): proper class of %s, M = %r, Pf = %r"
          % (min(proper_classes(Rb(9))[0]), smarkov(Rs, min(proper_classes(Rb(9))[0])),
             Rs[0] * Rs[5] - Rs[1] * Rs[4] + Rs[2] * Rs[3]))
    e8 = (2, -6, -8, 8, -8, 7)
    print("R_8 is the bottom-8 extreme of note 10 up to relabelling and reversal: %s"
          % (canon(Rb(8)) in (canon(e8), canon(neg(e8)))))
    print("Q_t: proper class of %s, M = %r" % (min(proper_classes(Qt(5))[0]), smarkov(Qs, min(proper_classes(Qt(5))[0]))))
    print("V_b (b written t): proper class of %s, M = %r" % (min(proper_classes((-7, 2, -1, -7, 1, 1))[0]),
                                                            smarkov(Vs, min(proper_classes((-7, 2, -1, -7, 1, 1))[0]))))
    pats = [q for q in itertools.product((-1, 1), repeat=6)]
    print("complete sign patterns: %d with |Pf| = 3, %d without a proper cyclic ordering (vortices), %d with both"
          % (sum(1 for q in pats if abs(pf(q)) == 3), sum(1 for q in pats if not proper_classes(q)),
             sum(1 for q in pats if abs(pf(q)) == 3 and not proper_classes(q))))
    # the stored join paths: is the class of each worst pocket totally proper to the given depth?
    try:
        rows = [json.loads(l) for l in open(args.joins)]
    except OSError:
        return
    res = Counter()
    for r in rows:
        q = tuple(r["rep"][i][j] for (i, j) in PAIRS)
        pcs = proper_classes(q)
        surv = [c for c in pcs if totally_proper_to_depth(q, c, args.depth_joins)[0]]
        sgn = "no surviving class" if not surv else ("M < 0" if markov(q, min(surv[0])) < 0 else "M >= 0")
        res[(r["kind"], len(pcs), sgn)] += 1
    print("note 11's %d worst pockets (kind, proper classes, surviving class to depth %d): %s"
          % (len(rows), args.depth_joins, dict(sorted(res.items()))))


def cmd_ahjl(args):
    """Where the local lemmas of arXiv 2610.36179 fail in mutation-cyclic classes."""
    print("Lemma 4.2, second assertion (commuting square): corners of the square at two non-adjacent vertices")
    for name, q, pair in [("C_5 (class of G_5)", mutate(mutate(Gk(5), 1), 2), None),
                          ("door of the b=6 extreme", (42, -54, 24, 2, -1, 0), (2, 3)),
                          ("door L(N+1) of Q_3", Lq(3, Nt(3) + 1), (1, 3))]:
        pairs = [pair] if pair else [(a, b) for (a, b) in PAIRS if ent(q, a, b) == 0]
        for (a, b) in pairs:
            hs = [ht(q), ht(mutate(q, a)), ht(mutate(q, b)), ht(mutate(mutate(q, a), b))]
            pcs = proper_classes(q)
            print("   %s %s: vertices %d, %d: heights of the corners q, mu_a q, mu_b q, mu_a mu_b q = %s; Pf %d; "
                  "Markov %s" % (name, q, a, b, hs, pf(q), [markov(q, min(c)) for c in pcs]))
    print("Lemma 4.5 (double arrow): the b=8 extreme, low C -> high P = mu_0 C, then alternating at 1, 0")
    C = (-2, -2, 54, 0, -56, -7)
    x = mutate(C, 0)
    hs = [ht(C), ht(x)]
    k = 1
    while ht(x) >= 101:
        x = mutate(x, k)
        hs.append(ht(x))
        k = 1 - k
    print("   heights: %s ... %s (%d quivers at 101), Pf %d, |b01| = 2" % (hs[:4], hs[-3:], hs.count(101), pf(C)))
    print("The square of Appendix A.1 with (b, c, d, e, f) = (T, 1, T, 2, T+1): m = b^2+c^2+d^2+e^2+f^2-f(bc+de)")
    for T in (10, 20, 40, 100):
        q = (0, T, -1, T, -2, T + 1)
        C, C2 = mutate(q, 0), mutate(q, 1)
        pcs = proper_classes(q)
        e = escape(C, 4 * T * T)
        print("   T = %d: P = %s; proper classes %d, Markov %s, Pf %d; corners of the square %s; "
              "C = mu_0 P and C' = mu_1 P have height %d, %d; C reaches another quiver of height <= %d only at %s"
              % (T, q, len(pcs), [markov(q, min(c)) for c in pcs], pf(q),
                 [ent(x, 2, 3) for x in (q, C, C2, mutate(C, 1))], ht(C), ht(C2), ht(C), e[0]))
    print("V_b = (-b, 2, -1, -b, 1, 1): bounded invariants, a pocket at every level")
    good = True
    for b in range(3, 201):
        q = (-b, 2, -1, -b, 1, 1)
        pcs = proper_classes(q)
        good &= (canon(mutate(q, 0)) == canon(q) and canon(mutate(q, 2)) == canon(q) and ht(mutate(q, 1)) == b * b - 2
                 and ht(mutate(q, 3)) == b + 1 and canon(q) != canon(neg(q)) and len(pcs) == 1
                 and markov(q, min(pcs[0])) == 5 and pf(q) == -2
                 and canon(mutate(mutate(mutate(q, 3), 0), 2)) == canon(neg(q))
                 and ht(mutate(mutate(q, 3), 0)) == b + 1)
    print("   for 3 <= b <= 200: mu_0 V_b and mu_2 V_b are V_b relabelled, ht(mu_1 V_b) = b^2 - 2, ht(mu_3 V_b) = b + 1,")
    print("   mu_2 mu_0 mu_3 V_b = -V_b relabelled through heights b+1, b+1, b; V_b is not -V_b; one proper wiggle class,")
    print("   Markov value 5, Pf = -2: %s" % good)
    print("   that class survives proper mutations to depth 6 for b = 3..40: %s"
          % all(totally_proper_to_depth((-b, 2, -1, -b, 1, 1), proper_classes((-b, 2, -1, -b, 1, 1))[0], 6)[0]
                for b in range(3, 41)))


# ----------------------------------------------------------------------------- Markov invariant on the census
CENSUS = ["n4_classes_B512.jsonl", "n4_classes_k5_B512.jsonl", "n4_classes_k67_B256.jsonl",
          "n4_classes_k8_B192.jsonl.gz", "n4_classes_k9_B192.jsonl.gz"]


def _open(path):
    import gzip
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def _markov_task(task):
    q, depth = task
    pcs = proper_classes(q)
    surv = [c for c in pcs if totally_proper_to_depth(q, c, depth)[0]]
    return len(pcs), len(surv), (markov(q, min(surv[0])) if len(surv) == 1 else None), pf(q)


def cmd_markov_census(args):
    """Every census class with a pocket: proper wiggle classes of its bottom quiver, survival under proper
    mutations to the given depth, the Markov value M, and the latest death of a pocket against |M| and |Pf|."""
    seen, rows = set(), []
    for path in CENSUS:
        for line in _open(path):
            r = json.loads(line)
            if r["key"] in seen:
                continue
            seen.add(r["key"])
            pairs = [(p["birth"], p["death"]) for p in r["pairs"] if p["death"] > p["birth"] and p["birth"] <= 9]
            if pairs:
                q = tuple(r["bottom_quiver"][i][j] for (i, j) in PAIRS)
                rows.append((q, r["bottom"], max(d for _, d in pairs), max(d / b / b for b, d in pairs)))
    print("census classes: %d; with a pocket born at <= 9: %d" % (len(seen), len(rows)))
    with Pool(args.workers) as pool:
        res = pool.map(_markov_task, [(r[0], args.depth) for r in rows], chunksize=200)
    kinds = Counter()
    worst = defaultdict(lambda: (0, None, 0))
    sign = Counter()
    bounds = (("|M|", lambda M, p: abs(M)), ("max(|M|, 2|Pf|)", lambda M, p: max(abs(M), 2 * abs(p))),
              ("|M| + 2|Pf|", lambda M, p: abs(M) + 2 * abs(p)))
    viol = {name: [] for name, _ in bounds}
    for (q, bottom, dmax, ratio), (npc, ns, M, p) in zip(rows, res):
        kind = "no proper class" if npc == 0 else ("no class survives" if ns == 0 else
                                                    ("one class survives" if ns == 1 else "several survive"))
        kinds[kind] += 1
        if ratio > worst[kind][0]:
            worst[kind] = (ratio, q, dmax)
        if M is not None:
            sign["M < 0" if M < 0 else ("M = 0" if M == 0 else "M > 0")] += 1
            for name, fn in bounds:
                if dmax > fn(M, p):
                    viol[name].append((dmax - fn(M, p), dmax, q, M, p))
    print("bottom quiver of the class, proper wiggle classes surviving proper mutations to depth %d: %s"
          % (args.depth, dict(kinds)))
    for k, (ratio, q, dmax) in worst.items():
        print("   %s: largest death/birth^2 = %.4f (latest death %d) at %s" % (k, ratio, dmax, q))
    print("pocket classes whose bottom quiver has no proper wiggle class (a vortex): %d" % kinds["no proper class"])
    print("sign of M when exactly one class survives: %s" % dict(sign))
    for name, _ in bounds:
        v = sorted(viol[name], reverse=True)
        print("latest death > %s in %d classes; largest excess %s; largest death among them %s"
              % (name, len(v), v[0][0] if v else "-", max(x[1] for x in v) if v else "-"))
        for x in v[:args.show]:
            print("   excess %d: latest death %d, bottom quiver %s, M = %d, Pf = %d" % x)


# ----------------------------------------------------------------------------- thin summits on the census
def escape_thin(q, bound, cut, floor):
    """As escape(), but a quiver of height >= floor is used only if its least entry is at most `cut` in
    absolute value (floor must exceed ht(q))."""
    s = canon(q)
    b = ht(s)
    plateau = {s}
    dq = deque([s])
    while dq:
        c = dq.popleft()
        for k in range(4):
            m = mutate(c, k)
            if ht(m) <= b:
                m = canon(m)
                if m not in plateau:
                    plateau.add(m)
                    dq.append(m)
    best = {x: b for x in plateau}
    heap = [(b, x) for x in plateau]
    heapq.heapify(heap)
    done = set()
    while heap:
        h, c = heapq.heappop(heap)
        if c in done:
            continue
        done.add(c)
        if c not in plateau and ht(c) <= b:
            return h
        for k in range(4):
            m = mutate(c, k)
            hm = ht(m)
            if hm > bound or (hm >= floor and min(abs(x) for x in m) > cut):
                continue
            m = canon(m)
            v = h if h > hm else hm
            if v < best.get(m, 1 << 62):
                best[m] = v
                heapq.heappush(heap, (v, m))
    return None


def _thin_task(task):
    q, death = task
    e = escape(q, death)[0]
    if e is None:
        return None, None, None
    above = [escape_thin(q, e, cut, ht(q) + 1) for cut in (2, 1, 0)]
    summit = [escape_thin(q, e, cut, e) for cut in (2, 1, 0)]
    return e, above, summit


def cmd_thin(args):
    """For every census pocket born at <= 9, with join height e: is there still a join at height e when
    (a) every quiver above the birth level, (b) every quiver of height e, must have an entry of absolute
    value <= 2 (<= 1, = 0)?"""
    seen, tasks = set(), []
    for path in CENSUS:
        for line in _open(path):
            r = json.loads(line)
            if r["key"] in seen:
                continue
            seen.add(r["key"])
            for p in r["pairs"]:
                if p["death"] > p["birth"] and p["birth"] <= 9:
                    tasks.append((tuple(p["quiver"][i][j] for (i, j) in PAIRS), p["death"]))
    with Pool(args.workers) as pool:
        res = pool.map(_thin_task, tasks, chunksize=200)
    n = len(tasks)
    print("pockets born at <= 9: %d; escape() equals the stored death in %d"
          % (n, sum(1 for (q, d), r in zip(tasks, res) if r[0] == d)))
    for which, name in ((1, "every quiver above the birth level"), (2, "every quiver at the join height")):
        for a, cut in enumerate((2, 1, 0)):
            fails = sorted(((e / ht(q) ** 2, ht(q), e, q) for (q, d), (e, *rest) in zip(tasks, res)
                            if rest[which - 1][a] != e), reverse=True)
            print("%s has least entry <= %d: a join at the same height exists for %d of %d pockets"
                  % (name, cut, n - len(fails), n))
            for x in fails[:args.show]:
                print("   no such join: join/b^2 %.3f, birth %d, join %d, quiver %s" % x)


# ----------------------------------------------------------------------------- beyond the census: one entry equal to 2
def component_pairs(q, cap, budget=400000):
    """All quivers reached from q inside height <= cap, and the persistence pairs (birth, death) of the
    height filtration on them (elder rule).  Returns (levels, pairs, exhausted)."""
    s = canon(q)
    level = {s: ht(s)}
    adj = {}
    dq = deque([s])
    while dq:
        c = dq.popleft()
        nb = []
        for k in range(4):
            m = mutate(c, k)
            h = ht(m)
            if h <= cap:
                m = canon(m)
                nb.append(m)
                if m not in level:
                    if len(level) >= budget:
                        return level, [], False
                    level[m] = h
                    dq.append(m)
        adj[c] = nb
    parent, birth = {}, {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    pairs = []
    for x in sorted(level, key=level.get):
        parent[x] = x
        birth[x] = level[x]
        for y in adj[x]:
            if y in parent:
                rx, ry = find(x), find(y)
                if rx != ry:
                    if birth[rx] < birth[ry]:
                        rx, ry = ry, rx                      # rx is the younger one and dies
                    if birth[rx] < level[x]:
                        pairs.append((birth[rx], level[x]))
                    parent[rx] = ry
    return level, pairs, True


def _scan2_task(task):
    b, x2, cap = task
    seen = set()
    best = []
    n = unexhausted = 0
    rng = range(-b, b + 1)
    for y2 in rng:
        for x3 in rng:
            for y3 in rng:
                for z in range(0, b + 1):
                    q = (2, x2, x3, y2, y3, z)
                    if ht(q) != b:
                        continue
                    c = min(canon(q), canon(neg(q)))
                    if c in seen:
                        continue
                    level, pairs, ex = component_pairs(q, cap)
                    n += 1
                    unexhausted += not ex
                    for x, h in level.items():
                        if h == b and (2 in x or -2 in x):
                            seen.add(min(x, canon(neg(x))))
                    d = max((dd for bb, dd in pairs if bb == b), default=0)
                    if d:
                        best.append((d, c))
    best.sort(reverse=True)
    return n, unexhausted, best[:20]


def cmd_scan2(args):
    """Every quiver of height exactly b with an entry of absolute value 2: the component inside height
    <= cap and the pockets born at b in it.  A pocket that dies above the cap is not seen."""
    t0 = time.time()
    for b in args.b:
        cap = int(args.factor * b * b)
        with Pool(args.workers) as pool:
            res = pool.map(_scan2_task, [(b, x2, cap) for x2 in range(-b, b + 1)], chunksize=1)
        tops = {}
        for n, un, best in res:
            for d, c in best:
                tops[c] = max(d, tops.get(c, 0))
        top = sorted(((d, c) for c, d in tops.items()), reverse=True)[:args.show]
        print("b = %d, cap %d: %d components enumerated (with repeats between workers), %d over budget; "
              "largest death of a pocket born at b: %s (ratio %.4f); %.0f s"
              % (b, cap, sum(r[0] for r in res), sum(r[1] for r in res), top[0][0] if top else None,
                 top[0][0] / b / b if top else 0, time.time() - t0))
        for d, c in top:
            print("   death %d (%.4f): %s" % (d, d / b / b, c))
        sys.stdout.flush()



def cmd_selftest(args):
    import numpy as np
    sys.path.insert(0, ".")
    from mutation_path import DT, mutate as np_mutate
    from bounded_paths import canonical
    rng = random.Random(1)
    for _ in range(20000):
        q = tuple(rng.randint(-9, 9) for _ in range(6))
        B = np.zeros((4, 4), dtype=DT)
        for (i, j), x in zip(PAIRS, q):
            B[i, j], B[j, i] = x, -x
        k = rng.randrange(4)
        M = np_mutate(B, k)
        assert tuple(int(M[i, j]) for (i, j) in PAIRS) == mutate(q, k)
        p = rng.choice(PERMS)
        assert canon(relabel(q, p)) == canon(q)
        Bp = B[np.ix_(p, p)]
        assert (canonical(Bp) == canonical(B)).all()
        assert abs(pf(mutate(q, k))) == abs(pf(q))
    print("mutate, relabel, canon and |Pf| agree with mutation_path / bounded_paths on 20,000 random quivers")
    for q, d in [((-2, -9, 8, 8, -9, -4), 144), ((6, -6, -6, -2, 5, -6), 66), ((2, -6, -8, 8, -8, 7), 101),
                 ((-7, -6, 5, -7, 2, -6), 79), ((-5, -2, 4, -5, 0, -5), 45), ((-3, 4, -4, -2, -4, 4), 28)]:
        e = escape(q, 8 * ht(q) ** 2)
        assert e[0] == d, (q, e)
    for k in range(3, 13):
        assert escape(Gk(k), 2 * k * k)[0] == k * (k - 1)
    print("escape() reproduces the census extremes 28, 45, 66, 79, 101, 144 and k(k-1) for G_3..G_12")
    # polynomial arithmetic
    t, n = P.var("t"), P.var("n")
    assert ((t + n) ** 3).value(t=3, n=5) == 512 and (t * t - 1).subs("t", t + 1) == t * t + 2 * t
    assert nonneg(t * t - 9, {"t": 3}) and not nonneg(t * t - 10, {"t": 3})
    print("polynomial class: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    a = sub.add_parser("orbit")
    a.add_argument("--samples", type=int, default=20000)
    a.add_argument("--seed", type=int, default=7)
    a.add_argument("--c", type=int, nargs="+", default=[2, 3])
    a.add_argument("--wmax", type=int, default=6)
    a.set_defaults(fn=cmd_orbit)
    a = sub.add_parser("orbit01")
    a.add_argument("--wmax", type=int, default=8)
    a.set_defaults(fn=cmd_orbit01)
    a = sub.add_parser("forks")
    a.add_argument("--samples", type=int, default=20000)
    a.add_argument("--seed", type=int, default=7)
    a.add_argument("--joins", default="n4_joins.jsonl")
    a.set_defaults(fn=cmd_forks)
    a = sub.add_parser("family")
    a.add_argument("--tmax", type=int, default=30)
    a.add_argument("--show", type=int, nargs="*", default=[3, 7])
    a.set_defaults(fn=cmd_family)
    sub.add_parser("prove").set_defaults(fn=cmd_prove)
    a = sub.add_parser("family3")
    a.add_argument("--bmax", type=int, default=60)
    a.add_argument("--show", type=int, nargs="*", default=[8])
    a.set_defaults(fn=cmd_family3)
    sub.add_parser("prove2").set_defaults(fn=cmd_prove2)
    a = sub.add_parser("family2")
    a.add_argument("--tmax", type=int, default=8)
    a.set_defaults(fn=cmd_family2)
    a = sub.add_parser("doors")
    a.add_argument("--qmax", type=int, default=5)
    a.add_argument("--rmax", type=int, default=5)
    a.add_argument("--pmax", type=int, default=40)
    a.add_argument("--smax", type=int, default=1500)
    a.add_argument("--bmax", type=int, default=26)
    a.add_argument("--workers", type=int, default=8)
    a.set_defaults(fn=cmd_doors)
    a = sub.add_parser("coq")
    a.add_argument("--depth", type=int, default=7)
    a.add_argument("--depth-joins", type=int, default=5)
    a.add_argument("--joins", default="n4_joins.jsonl")
    a.set_defaults(fn=cmd_coq)
    sub.add_parser("ahjl").set_defaults(fn=cmd_ahjl)
    a = sub.add_parser("scan2")
    a.add_argument("--b", type=int, nargs="+", default=[10])
    a.add_argument("--factor", type=float, default=2.5)
    a.add_argument("--workers", type=int, default=8)
    a.add_argument("--show", type=int, default=8)
    a.set_defaults(fn=cmd_scan2)
    a = sub.add_parser("thin")
    a.add_argument("--workers", type=int, default=8)
    a.add_argument("--show", type=int, default=5)
    a.set_defaults(fn=cmd_thin)
    a = sub.add_parser("markov-census")
    a.add_argument("--depth", type=int, default=4)
    a.add_argument("--workers", type=int, default=8)
    a.add_argument("--show", type=int, default=6)
    a.set_defaults(fn=cmd_markov_census)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
