"""Note 14: when is a 4-vertex quiver mutation-equivalent to its opposite?

Tools (pure Python, exact integers, no bound on the entries):
  forks (Warkentin), the forkless part of a mutation class, vortices and proper cyclic orderings
  (Fomin-Neville), unipotent companions and cosquares.

A quiver is a 6-tuple t = (b01, b02, b03, b12, b13, b23) of the entries above the diagonal of its
exchange matrix; b_ij > 0 means b_ij arrows i -> j.
"""
import itertools

PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
PIDX = {p: a for a, p in enumerate(PAIRS)}
PERMS = list(itertools.permutations(range(4)))
# relabelling by p: new entry (i, j) is the old entry (p[i], p[j])
RELAB = [[(PIDX[(min(p[i], p[j]), max(p[i], p[j]))], 1 if p[i] < p[j] else -1) for (i, j) in PAIRS] for p in PERMS]
# for mutation at k: the two pairs (i, k), (k, j) for each pair (i, j) not containing k
_OTHER = []
for k in range(4):
    row = []
    for (i, j) in PAIRS:
        if i == k or j == k:
            row.append(None)
        else:
            a = (PIDX[(min(i, k), max(i, k))], 1 if i < k else -1)      # b_ik
            b = (PIDX[(min(k, j), max(k, j))], 1 if k < j else -1)      # b_kj
            row.append((a, b))
    _OTHER.append(row)


def from_matrix(B):
    return tuple(int(B[i][j]) for (i, j) in PAIRS)


def to_matrix(t):
    B = [[0] * 4 for _ in range(4)]
    for (i, j), x in zip(PAIRS, t):
        B[i][j], B[j][i] = x, -x
    return B


def mutate(t, k):
    out = []
    for a, x in enumerate(t):
        o = _OTHER[k][a]
        if o is None:
            out.append(-x)
        else:
            (ia, sa), (ib, sb) = o
            p, q = sa * t[ia], sb * t[ib]
            if p > 0 and q > 0:
                out.append(x + p * q)
            elif p < 0 and q < 0:
                out.append(x - p * q)
            else:
                out.append(x)
    return tuple(out)


def canon(t):
    """Canonical form up to relabelling: the largest tuple over the 24 relabellings."""
    return max(tuple(s * t[a] for a, s in r) for r in RELAB)


def neg(t):
    return tuple(-x for x in t)


def level(t):
    return max(abs(x) for x in t)


def weight(t):
    return sum(abs(x) for x in t)


def entry(t, i, j):
    if i == j:
        return 0
    return t[PIDX[(i, j)]] if i < j else -t[PIDX[(j, i)]]


def is_acyclic(t, verts=(0, 1, 2, 3)):
    rem = set(verts)
    while rem:
        src = [i for i in rem if not any(entry(t, j, i) > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def fork_return(t):
    """The point of return r if t is a fork (Warkentin; Ervin arXiv 2306.07502, Definition 2.5), else None.
    Fork: abundant, not acyclic, and for all i -> r -> j: b_ji > b_ir and b_ji > b_rj, with the full
    subquivers on the in-neighbours and on the out-neighbours of r acyclic."""
    if any(abs(x) < 2 for x in t):
        return None
    if is_acyclic(t):
        return None
    for r in range(4):
        ins = [i for i in range(4) if i != r and entry(t, i, r) > 0]
        outs = [j for j in range(4) if j != r and entry(t, r, j) > 0]
        ok = True
        for i in ins:
            for j in outs:
                bji = entry(t, j, i)
                if not (bji > entry(t, i, r) and bji > entry(t, r, j)):
                    ok = False
                    break
            if not ok:
                break
        if ok and is_acyclic(t, ins) and is_acyclic(t, outs):
            return r
    return None


def descend(t, max_steps=100000):
    """Follow points of return down from t.  Returns (kind, quivers):
       ('nonfork', [x])      x is a non-fork reached from t by mutating at points of return;
       ('balanced', [x, y])  x and y = mu_r(x) are both forks with point of return r (class of forks only)."""
    for _ in range(max_steps):
        r = fork_return(t)
        if r is None:
            return "nonfork", [t]
        u = mutate(t, r)
        if fork_return(u) == r:
            return "balanced", [t, u]
        t = u
    raise RuntimeError("descent did not stop")


def forkless_part(t, cap=5000):
    """The forkless part of the class of t up to relabelling, by a search through non-forks only.
    Returns (kind, core, adjacency, exhausted); core is a dict canonical quiver -> level.
    kind = 'balanced' when the class has no non-fork: the core is then the two ends of the balanced edge."""
    kind, start = descend(t)
    if kind == "balanced":
        a, b = canon(start[0]), canon(start[1])
        return kind, {a: level(a), b: level(b)}, {a: {b}, b: {a}}, True
    s = canon(start[0])
    core = {s: level(s)}
    adj = {s: set()}
    todo = [s]
    while todo:
        x = todo.pop()
        for k in range(4):
            y = mutate(x, k)
            if fork_return(y) is not None:
                continue
            c = canon(y)
            if c not in core:
                if len(core) >= cap:
                    return kind, core, adj, False
                core[c] = level(c)
                adj[c] = set()
                todo.append(c)
            if c != x:
                adj[x].add(c)
                adj[c].add(x)
    return kind, core, adj, True


# ----------------------------------------------------------------------------- pre-forks and exits
def _tri_fork_return(t, tri):
    """Point of return of the full 3-vertex subquiver on tri if it is a fork, else None.
    A 3-vertex fork is a cyclic triangle with all weights >= 2 whose largest weight is attained once;
    the point of return is the vertex opposite the largest edge."""
    a, b, c = tri
    x, y, z = entry(t, a, b), entry(t, b, c), entry(t, c, a)
    if not ((x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0)):
        return None
    x, y, z = abs(x), abs(y), abs(z)
    if min(x, y, z) < 2:
        return None
    m = max(x, y, z)
    if (x == m) + (y == m) + (z == m) != 1:
        return None
    return c if x == m else (a if y == m else b)


def prefork_returns(t):
    """Vertices r such that t is a pre-fork with vertices {r, k, k'} for some k, k'
    (Warkentin; Ervin arXiv 2306.07502, Definition 4.5): both t minus k and t minus k' are forks with the
    common point of return r, and every other vertex i has k -> i and k' -> i, or i -> k and i -> k'."""
    out = set()
    for k, kp in itertools.combinations(range(4), 2):
        rest = [i for i in range(4) if i not in (k, kp)]
        if any(entry(t, k, i) * entry(t, kp, i) <= 0 for i in rest):
            continue
        r1 = _tri_fork_return(t, (rest[0], rest[1], kp))      # t minus k
        if r1 is None or r1 == kp:
            continue
        if _tri_fork_return(t, (rest[0], rest[1], k)) == r1:  # t minus k'
            out.add(r1)
    return out


def exit_returns(t):
    """Vertices m such that (t, m) is an exit: t is a fork with point of return m, or a pre-fork with
    point of return m."""
    out = prefork_returns(t)
    r = fork_return(t)
    if r is not None:
        out.add(r)
    return out


def no_exit_closure(t, cap=5000, level_cap=None):
    """V'(t): the quivers, up to relabelling, reached from t by mutation paths with no strict up-exit step.
    A step x -> y = mu_m(x) is a strict up-exit step if (y, m) is an exit and (x, m) is not.
    Returns (levels: canonical quiver -> level, allowed steps: canonical quiver -> set of canonical quivers,
    exhausted).  The search gives up (exhausted = False) after cap quivers, or at the first quiver of level
    above level_cap."""
    s = canon(t)
    lev = {s: level(s)}
    adj = {s: set()}
    todo = [s]
    while todo:
        x = todo.pop()
        ex_x = exit_returns(x)
        for m in range(4):
            y = mutate(x, m)
            if m not in ex_x and m in exit_returns(y):
                continue
            c = canon(y)
            if c not in lev:
                if len(lev) >= cap or (level_cap is not None and level(c) > level_cap):
                    return lev, adj, False
                lev[c] = level(c)
                adj[c] = set()
                todo.append(c)
            if c != x:
                adj[x].add(c)
    return lev, adj, True


def _reach(adj, x):
    seen = {x}
    todo = [x]
    while todo:
        for y in adj[todo.pop()]:
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return seen


def core(t, cap=5000, level_cap=None):
    """The core of the class of t: the least non-empty set of quivers (up to relabelling) closed under the
    steps that are not strict up-exit steps.  It is the same for every quiver of the class whose closure
    V' is finite (note 14, Theorem 14.1).  Returns (core: canonical quiver -> level, closure V', allowed
    steps, exhausted); the core is None when the search did not stop."""
    lev, adj, ex = no_exit_closure(t, cap=cap, level_cap=level_cap)
    if not ex:
        return None, lev, adj, False
    R = set(lev)
    shrunk = True
    while shrunk:
        shrunk = False
        for y in R:
            Ry = _reach(adj, y)
            if len(Ry) < len(R):
                R = Ry
                shrunk = True
                break
    return {x: lev[x] for x in R}, lev, adj, True


def small_pairs(t):
    return [PAIRS[a] for a, x in enumerate(t) if abs(x) < 2]


def tri_kind(t, tri):
    """'fork', 'aa' (abundant acyclic) or None for the full subquiver on three vertices."""
    a, b, c = tri
    if min(abs(entry(t, a, b)), abs(entry(t, b, c)), abs(entry(t, c, a))) < 2:
        return None
    if _tri_fork_return(t, tri) is not None:
        return "fork"
    return "aa" if is_acyclic(t, tri) else None


def certainly_in_core(t):
    """True if t lies in no far region, by a sufficient test.  Every quiver of a far region is a fork, a
    pre-fork, a wing or a tip (Ervin, Corollary 4.25).  Each of these has at most one pair {k, k'} of
    weight < 2; if it has one, t minus k and t minus k' are forks or abundant acyclic and at least one is
    a fork; if it has none, it is a fork."""
    sp = small_pairs(t)
    if len(sp) >= 2:
        return True
    if not sp:
        return fork_return(t) is None
    k, kp = sp[0]
    kinds = [tri_kind(t, tuple(i for i in range(4) if i != v)) for v in (k, kp)]
    return None in kinds or "fork" not in kinds


# ----------------------------------------------------------------------------- the census of notes 8 and 10
CENSUS = [("n4_classes_B512.jsonl", 1, 4, 512), ("n4_classes_k5_B512.jsonl", 5, 5, 512),
          ("n4_classes_k67_B256.jsonl", 6, 7, 256), ("n4_classes_k8_B192.jsonl.gz", 8, 8, 192),
          ("n4_classes_k9_B192.jsonl.gz", 9, 9, 192)]


def read_rows(path):
    import gzip, json
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def census_rows():
    """The 788,026 classes of notes 8 and 10, each once (as in review12.census_rows)."""
    for fn, lo, hi, B in CENSUS:
        for r in read_rows(fn):
            if lo <= r["bottom"] <= hi:
                yield fn, B, r


def core_record(args):
    """One census class: its core when the search stops inside the caps."""
    idx, bottom, t, cap, level_cap = args
    K, lev, adj, ex = core(t, cap=cap, level_cap=level_cap)
    rec = {"i": idx, "b": bottom, "q": list(canon(t)), "ex": ex, "nv": len(lev), "in": certainly_in_core(t)}
    if not ex:
        # the highest quiver found that certainly lies in no far region
        rec["hc"] = max((lev[x] for x in lev if certainly_in_core(x)), default=0)
        return rec
    lo = min(K.values())
    rec.update({"n": len(K), "vid": list(min(K)), "mvid": list(min(canon(neg(x)) for x in K)),
                "top": max(K.values()), "lo": lo, "nlo": sum(1 for x in K if K[x] == lo),
                "qin": canon(t) in K, "ncert": sum(1 for x in K if certainly_in_core(x)),
                "zero": sum(1 for x in K if 0 in x), "vortex": sum(1 for x in K if is_vortex(x)),
                "acyc": sum(1 for x in K if is_acyclic(x))})
    # exits met at the boundary of the core: forks only, or pre-forks that are not forks as well
    pre = 0
    for x in K:
        ex_x = exit_returns(x)
        for m in range(4):
            y = mutate(x, m)
            if m not in ex_x and m in exit_returns(y) and fork_return(y) != m:
                pre += 1
    rec["pre"] = pre
    return rec


# ----------------------------------------------------------------------------- acyclic classes (Caldero-Keller)
def sink_source_orbit(t):
    """The acyclic quivers obtained from the acyclic quiver t by sink and source mutations, up to relabelling."""
    s = canon(t)
    seen = {s}
    todo = [s]
    while todo:
        x = todo.pop()
        for k in range(4):
            col = [entry(x, k, j) for j in range(4) if j != k]
            if all(c >= 0 for c in col) or all(c <= 0 for c in col):
                c = canon(mutate(x, k))
                if c not in seen:
                    seen.add(c)
                    todo.append(c)
    return seen


def find_acyclic(t, bound, budget=20000):
    """An acyclic quiver in the class of t found by a search inside the bound, or None."""
    s = canon(t)
    seen = {s}
    todo = [s]
    while todo:
        x = todo.pop()
        if is_acyclic(x):
            return x
        for k in range(4):
            y = mutate(x, k)
            if level(y) <= bound:
                c = canon(y)
                if c not in seen and len(seen) < budget:
                    seen.add(c)
                    todo.append(c)
    return None


# ----------------------------------------------------------------------------- cyclically ordered quivers (Fomin-Neville)
CYCLIC_ORDERS = [(0,) + p for p in itertools.permutations((1, 2, 3))]


def _norm_cyc(s):
    i = s.index(0)
    return tuple(s[i:] + s[:i])


def wiggle_class(t, sigma):
    """All cyclic orderings wiggle-equivalent to sigma: swaps of cyclically consecutive vertices that are
    not joined by an arrow (arXiv 2406.03604, Definition 2.3)."""
    s0 = _norm_cyc(tuple(sigma))
    seen = {s0}
    todo = [s0]
    while todo:
        s = todo.pop()
        for a in range(4):
            u, v = s[a], s[(a + 1) % 4]
            if entry(t, u, v) == 0:
                w = list(s)
                w[a], w[(a + 1) % 4] = v, u
                w = _norm_cyc(tuple(w))
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
    return seen


def vertex_proper(t, sigma, j):
    """No-left-turn rule at j (Definition 5.2): for every path i -> j -> k, going clockwise from i one meets
    j before k."""
    pos = {v: a for a, v in enumerate(sigma)}
    for i in range(4):
        if i == j or entry(t, i, j) <= 0:
            continue
        for k in range(4):
            if k == j or entry(t, j, k) <= 0:
                continue
            if (pos[j] - pos[i]) % 4 > (pos[k] - pos[i]) % 4:
                return False
    return True


def coq_proper(t, sigma):
    """(Q, sigma) is proper: every vertex is proper in some ordering of the wiggle class (Definition 11.1)."""
    cls = wiggle_class(t, sigma)
    return all(any(vertex_proper(t, s, j) for s in cls) for j in range(4))


def proper_orderings(t):
    """The proper cyclic orderings of t, one representative (the least) of each wiggle class."""
    out = []
    done = set()
    for s in CYCLIC_ORDERS:
        if s in done:
            continue
        cls = wiggle_class(t, s)
        done |= cls
        if all(any(vertex_proper(t, x, j) for x in cls) for j in range(4)):
            out.append(min(cls))
    return out


def proper_mutate(t, sigma, j):
    """Proper mutation of the COQ (t, sigma) at j (Definition 6.1), or None if j is proper in no ordering
    of the wiggle class.  Returns (mu_j(t), new cyclic ordering)."""
    for s in sorted(wiggle_class(t, sigma)):
        if not vertex_proper(t, s, j):
            continue
        a = s.index(j)
        rest = [s[(a + d) % 4] for d in (1, 2, 3)]            # clockwise from j
        first_in = next((b for b, x in enumerate(rest) if entry(t, x, j) > 0), 3)
        new = (j,) + tuple(rest[first_in:]) + tuple(rest[:first_in])
        return mutate(t, j), _norm_cyc(new)
    return None


def unipotent_companion(t, order):
    """U for the linear ordering `order` of the vertices (Definition 4.2): 1 on the diagonal and -b_ij above."""
    return [[1 if a == b else (-entry(t, order[a], order[b]) if a < b else 0) for b in range(4)] for a in range(4)]


def _matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def _transpose(A):
    return [list(r) for r in zip(*A)]


def _unipotent_inverse(U):
    n = len(U)
    N = [[U[i][j] - (i == j) for j in range(n)] for i in range(n)]
    out = [[int(i == j) for j in range(n)] for i in range(n)]
    P = [[int(i == j) for j in range(n)] for i in range(n)]
    for e in range(1, n):
        P = _matmul(P, N)
        for i in range(n):
            for j in range(n):
                out[i][j] += (-1) ** e * P[i][j]
    return out


def cosquare(t, sigma):
    """The cosquare U^{-T} U of the unipotent companion for the linear ordering that reads sigma from its
    first entry (Definition 4.7); its GL_4(Z) conjugacy class depends only on the wiggle class of sigma."""
    U = unipotent_companion(t, sigma)
    return _matmul(_transpose(_unipotent_inverse(U)), U)


def markov_invariant(t, sigma):
    C = cosquare(t, sigma)
    return 4 - sum(C[i][i] for i in range(4))


def pfaffian(t):
    return t[0] * t[5] - t[1] * t[4] + t[2] * t[3]


def is_vortex(t):
    """A complete 4-vertex quiver with a source or sink whose other three vertices carry an oriented 3-cycle
    (Definition 13.1)."""
    if any(x == 0 for x in t):
        return False
    for a in range(4):
        col = [entry(t, a, j) for j in range(4) if j != a]
        if all(c > 0 for c in col) or all(c < 0 for c in col):
            r = [i for i in range(4) if i != a]
            if not is_acyclic(t, r):
                return True
    return False


# ----------------------------------------------------------------------------- bottom plateaus and the mirror map
def plateau(t):
    """The component of t among the quivers of its class with level <= level(t), up to relabelling."""
    s = canon(t)
    m = level(s)
    seen = {s}
    todo = [s]
    while todo:
        x = todo.pop()
        for k in range(4):
            y = mutate(x, k)
            if level(y) <= m:
                c = canon(y)
                if c not in seen:
                    seen.add(c)
                    todo.append(c)
    return seen


def enumerate_within(t, bound, budget=3_000_000):
    s = canon(t)
    lev = {s: level(s)}
    todo = [s]
    while todo:
        x = todo.pop()
        for k in range(4):
            y = mutate(x, k)
            m = level(y)
            if m <= bound:
                c = canon(y)
                if c not in lev:
                    if len(lev) >= budget:
                        return lev, False
                    lev[c] = m
                    todo.append(c)
    return lev, True


def plateau_record(args):
    """One census class: its bottom components.  For each: the least quiver of the plateau (its key), the
    key of the mirror plateau, the death of the component (None for the eldest), the number of quivers
    isomorphic to their own opposite, and whether it contains an acyclic quiver."""
    idx, B, r = args
    lo = r["bottom"]
    comps = {}
    def add(q, death):
        P = plateau(q)
        k = min(P)
        if k not in comps:
            comps[k] = [death, P]
        elif death is not None and comps[k][0] is None:
            comps[k][0] = death
    add(from_matrix(r["bottom_quiver"]), None)
    for p in r["pairs"]:
        if p["birth"] == lo:
            add(from_matrix(p["quiver"]), p["death"])
    filled = False
    if len(comps) < r["bottom_components"]:
        lev, ex = enumerate_within(from_matrix(r["bottom_quiver"]), B)
        for x in lev:
            if lev[x] == lo and not any(x in c[1] for c in comps.values()):
                add(x, None)
        filled = True
    out = []
    for k, (death, P) in comps.items():
        mk = min(canon(neg(x)) for x in P)
        out.append({"k": list(k), "mk": list(mk), "d": death, "size": len(P),
                    "fix": sum(1 for x in P if canon(neg(x)) == x), "acyc": any(is_acyclic(x) for x in P)})
    return {"i": idx, "b": lo, "nc": r["bottom_components"], "filled": filled, "comps": out}


# ----------------------------------------------------------------------------- is the cosquare conjugate to its transpose?
_GP_READY = False


def transpose_test(C):
    """Necessary condition for a 4x4 integer matrix C to be conjugate to its transpose in GL_4(Z), when its
    characteristic polynomial f is irreducible.  Let L = Q[x]/(f).  The Z-span of the entries of an
    eigenvector of C for the eigenvalue x is a lattice in L determined by the GL_4(Z)-class of C up to a
    factor in L (Latimer-MacDuffee); so the ideal classes in the maximal order of the lattices of C and of
    C^T agree when C and C^T are conjugate.  Returns a dict: irreducible; same (the two ideal classes
    agree); index of Z[x] in the maximal order; class number.  PARI's bnfinit assumes GRH."""
    global _GP_READY
    import cypari2
    pari = cypari2.Pari()
    if not _GP_READY:
        pari.allocatemem(64 * 10 ** 6, 4 * 10 ** 9, silent=True)
        pari("""ttest(C) = { my(f = charpoly(C, 'x), bnf, th, A, B, w, u, Iw, Iu, e);
            if(!polisirreducible(f), return([0, f]));
            bnf = bnfinit(f, 1); th = Mod('x, f);
            A = matadjoint(th*matid(4) - C); B = matadjoint(th*matid(4) - C~);
            w = 0; for(j = 1, 4, if(A[,j] != 0, w = A[,j]; break));
            u = 0; for(j = 1, 4, if(B[,j] != 0, u = B[,j]; break));
            Iw = 0; for(i = 1, 4, if(w[i] != 0, Iw = if(Iw === 0, idealhnf(bnf, w[i]), idealadd(bnf, Iw, w[i]))));
            Iu = 0; for(i = 1, 4, if(u[i] != 0, Iu = if(Iu === 0, idealhnf(bnf, u[i]), idealadd(bnf, Iu, u[i]))));
            e = bnfisprincipal(bnf, idealdiv(bnf, Iw, Iu), 0);
            return([1, f, e == 0*e, sqrtint(abs(poldisc(f) / bnf.disc)), bnf.no]); }""")
        _GP_READY = True
    M = pari.matrix(4, 4, [C[i][j] for i in range(4) for j in range(4)])
    r = pari("ttest")(M)
    if int(r[0]) == 0:
        return {"irreducible": False, "f": str(r[1])}
    return {"irreducible": True, "f": str(r[1]), "same": bool(r[2]), "index": int(r[3]), "h": int(r[4])}


def topological_order(t):
    """A linear ordering of the vertices of an acyclic quiver with u before v whenever u -> v."""
    rem = set(range(4))
    out = []
    while rem:
        src = sorted(i for i in rem if not any(entry(t, j, i) > 0 for j in rem))
        out.append(src[0])
        rem.discard(src[0])
    return tuple(out)


def fn_record(args):
    """The Fomin-Neville test for one class with a totally proper cyclic ordering.
    kind 'acyclic': q is a bottom quiver whose plateau contains an acyclic quiver (totally proper by Neville,
    arXiv 2409.17832, with the ordering of Observation 11.6).  kind 'complete': q lies in a finite core all
    of whose quivers are complete and vortex-free and whose exits are forks (Theorem 15.7)."""
    idx, kind, q = args
    try:
        return _fn_record(idx, kind, tuple(q))
    except Exception as e:                       # a PARI error must not travel through the pool
        return {"i": idx, "kind": kind, "error": f"{type(e).__name__}: {str(e)[:80]}"}


def _fn_record(idx, kind, q):
    if kind == "acyclic":
        t = min(x for x in plateau(q) if is_acyclic(x))
        sigma = topological_order(t)
    else:
        t = q
        po = proper_orderings(t)
        if len(po) != 1:
            return {"i": idx, "kind": kind, "error": f"{len(po)} proper orderings"}
        sigma = po[0]
    if not coq_proper(t, sigma):
        return {"i": idx, "kind": kind, "error": "ordering not proper"}
    C = cosquare(t, sigma)
    r = transpose_test(C)
    r.update({"i": idx, "kind": kind, "markov": 4 - sum(C[a][a] for a in range(4)), "pf": abs(pfaffian(t))})
    r.pop("f", None)
    return r


# ----------------------------------------------------------------------------- the core graph: joins and the mirror map
def core_graph(K):
    """Undirected mutation edges between the quivers of a core K (canonical quivers)."""
    adj = {x: set() for x in K}
    for x in K:
        for m in range(4):
            c = canon(mutate(x, m))
            if c in K and c != x:
                adj[x].add(c)
                adj[c].add(x)
    return adj


def join_heights(lev, adj, src):
    """Least L such that each quiver is joined to src through quivers of level <= L, inside the graph."""
    import heapq
    h = {src: lev[src]}
    pq = [(lev[src], src)]
    done = set()
    while pq:
        d, x = heapq.heappop(pq)
        if x in done:
            continue
        done.add(x)
        for y in adj[x]:
            nd = max(d, lev[y])
            if nd < h.get(y, 1 << 62):
                h[y] = nd
                heapq.heappush(pq, (nd, y))
    return h


def corecheck_record(args):
    """A census class with a finite core: (1) the deaths of its bottom components recomputed inside the core
    graph; (2) how the map x -> -x acts on the core."""
    idx, q, census_deaths, selfm = args
    K, lev, adj, ex = core(tuple(q), cap=2000, level_cap=10 ** 7)
    g = core_graph(K)
    lo = min(K.values())
    rec = {"i": idx, "n": len(K), "lo": lo}
    # bottom components of the core at its lowest level, and elder-rule deaths
    bots = [x for x in K if K[x] == lo]
    comp = {}
    for x in bots:
        if x in comp:
            continue
        comp[x] = x
        todo = [x]
        while todo:
            y = todo.pop()
            for z in g[y]:
                if K[z] == lo and z not in comp:
                    comp[z] = x
                    todo.append(z)
    reps = sorted(set(comp.values()))
    deaths = []
    if len(reps) > 1:
        # single-linkage merge heights between the bottom components: deaths are the merge heights
        import itertools as it
        h = {r: join_heights(K, g, r) for r in reps}
        edges = sorted((h[a][b], a, b) for a, b in it.combinations(reps, 2))
        parent = {r: r for r in reps}
        def find(a):
            while parent[a] != a:
                a = parent[a]
            return a
        for d, a, b in edges:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                deaths.append(d)
    rec["core_deaths"] = sorted(deaths)
    rec["census_deaths"] = sorted(census_deaths)
    if selfm:
        fixed = [x for x in K if canon(neg(x)) == x]
        inverted = sum(1 for x in K for y in g[x] if canon(neg(x)) == y) // 2
        rec["fix"] = len(fixed)
        rec["inv"] = inverted
        rec["fixlo"] = min((K[x] for x in fixed), default=None)
        a = bots[0]
        ma = canon(neg(a))
        rec["mirror_join"] = join_heights(K, g, a).get(ma) if ma in K else None
    return rec


# ----------------------------------------------------------------------------- all pockets of a class with a finite core
def extended_core(t, cap=2000, level_cap=10 ** 7):
    """The core K of the class of t together with the roots of the far regions that hang from it.
    Returns (levels of the nodes, undirected edges as adjacency, set of root nodes, number of roots that
    are pre-forks and not forks), or None if the core search does not stop."""
    K, lev, adj, ex = core(t, cap=cap, level_cap=level_cap)
    if not ex:
        return None
    g = core_graph(K)
    levels = dict(K)
    roots = set()
    npre = 0
    for x in K:
        ex_x = exit_returns(x)
        for m in range(4):
            y = mutate(x, m)
            if m not in ex_x and m in exit_returns(y):
                c = canon(y)
                if c in K:
                    continue
                if c not in levels:
                    levels[c] = level(c)
                    g[c] = set()
                    roots.add(c)
                    if fork_return(y) != m:
                        npre += 1
                g[c].add(x)
                g[x].add(c)
    return levels, g, roots, npre


def persistence_pairs(levels, g):
    """Elder-rule pairs (birth, death) of the filtration of the graph by level; a node enters at its level."""
    order = sorted(levels, key=lambda x: levels[x])
    parent = {}
    birth = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    pairs = []
    for x in order:
        parent[x] = x
        birth[x] = levels[x]
        for y in g[x]:
            if y in parent:
                ra, rb = find(x), find(y)
                if ra != rb:
                    if birth[ra] < birth[rb]:
                        ra, rb = rb, ra            # ra is the younger
                    if birth[ra] < levels[x]:
                        pairs.append((birth[ra], levels[x]))
                    parent[ra] = rb
    return sorted(pairs)


def pockets_record(args):
    idx, q = args
    r = extended_core(tuple(q))
    if r is None:
        return {"i": idx, "error": "core search did not stop"}
    levels, g, roots, npre = r
    return {"i": idx, "pairs": persistence_pairs(levels, g), "nroots": len(roots), "npre": npre,
            "lo": min(levels.values()), "top": max(levels.values())}


def not_totally_proper(t, budget=3000):
    """Search the proper mutation classes of all proper cyclic orderings of t for a COQ that is not proper.
    Returns a list with, for each proper ordering of t, the number of proper mutations after which a
    non-proper COQ is reached (None if none was found within the budget).  If the list is empty or has no
    None, t has no totally proper cyclic ordering (arXiv 2406.03604, Definition 14.1)."""
    out = []
    for s0 in proper_orderings(t):
        seen = {(t, s0): 0}
        todo = [(t, s0)]
        found = None
        while todo and found is None and len(seen) < budget:
            nxt = []
            for (x, s) in todo:
                for j in range(4):
                    r = proper_mutate(x, s, j)
                    y, s2 = r
                    s2 = min(wiggle_class(y, s2))
                    if (y, s2) in seen:
                        continue
                    seen[(y, s2)] = seen[(x, s)] + 1
                    if not coq_proper(y, s2):
                        found = seen[(y, s2)]
                        break
                    nxt.append((y, s2))
                if found is not None:
                    break
            todo = nxt
        out.append(found)
    return out


def balanced_record(args):
    """Number of balanced edges in the core of the class of q: pairs x, mu_m(x) of core quivers that are
    both exits for the vertex m.  If there is none, no quiver of the core lies in a far region."""
    idx, q = args
    K, lev, adj, ex = core(tuple(q), cap=2000, level_cap=10 ** 7)
    n = 0
    for x in K:
        for m in exit_returns(x):
            y = mutate(x, m)
            if canon(y) in K and m in exit_returns(y):
                n += 1
    return idx, n, len(K)
