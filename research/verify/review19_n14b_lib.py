"""Independent library for the check of note 14 (n14b).  Written from Ervin arXiv 2306.07502,
Definitions 2.5 (fork), 4.5 (pre-fork), 4.14 (wing), 4.18 (tip), and note 14 section 3 (exits, allowed
steps, V').  Imports nothing from n4_opposite*.py.  Pure Python integers throughout (no numpy).

A quiver is stored as the 6-tuple (b01, b02, b03, b12, b13, b23) of the skew-symmetric exchange matrix;
b_ij > 0 means b_ij arrows i -> j.  All tests below work on the 4x4 matrix.
"""
import itertools

PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
PERMS = tuple(itertools.permutations(range(4)))


def mat(t):
    B = [[0] * 4 for _ in range(4)]
    for (i, j), x in zip(PAIRS, t):
        B[i][j] = x
        B[j][i] = -x
    return B


def vec(B):
    return tuple(B[i][j] for (i, j) in PAIRS)


def mut(t, k):
    """Fomin-Zelevinsky matrix mutation at k:
    B'_ij = -B_ij if k in {i, j};  B'_ij = B_ij + sgn(B_ik) max(B_ik B_kj, 0) otherwise."""
    B = mat(t)
    C = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            if i == k or j == k:
                C[i][j] = -B[i][j]
            else:
                p = B[i][k] * B[k][j]
                if p > 0:
                    s = 1 if B[i][k] > 0 else -1
                    C[i][j] = B[i][j] + s * p
                else:
                    C[i][j] = B[i][j]
    return vec(C)


def relabel(t, p):
    """Entry (i, j) of the new quiver is entry (p[i], p[j]) of the old one."""
    B = mat(t)
    return tuple(B[p[i]][p[j]] for (i, j) in PAIRS)


def canon(t):
    B = mat(t)
    return max(tuple(B[p[i]][p[j]] for (i, j) in PAIRS) for p in PERMS)


def neg(t):
    return tuple(-x for x in t)


def level(t):
    return max(abs(x) for x in t)


def weight(t):
    return sum(abs(x) for x in t)


# ----------------------------------------------------------------------------- definitions
def acyclic(B, V):
    """No oriented cycle in the full subquiver on V: peel off sinks."""
    rem = list(V)
    while rem:
        sinks = [i for i in rem if not any(B[i][j] > 0 for j in rem if j != i)]
        if not sinks:
            return False
        rem = [i for i in rem if i not in sinks]
    return True


def abundant(B, V):
    return all(abs(B[i][j]) >= 2 for i, j in itertools.combinations(V, 2))


def fork_points(B, V):
    """All r in V such that the full subquiver on V is a fork with point of return r (Ervin Def. 2.5):
    abundant, not acyclic, for all i in F^-(r), j in F^+(r): f_ji > f_ir and f_ji > f_rj, and the full
    subquivers on F^-(r) and on F^+(r) acyclic.  f_ji is the number of arrows j -> i (B[j][i] if positive)."""
    if not abundant(B, V) or acyclic(B, V):
        return set()
    out = set()
    for r in V:
        ins = [i for i in V if i != r and B[i][r] > 0]
        outs = [j for j in V if j != r and B[r][j] > 0]
        ok = True
        for i in ins:
            for j in outs:
                fji = B[j][i] if B[j][i] > 0 else 0
                if not (fji > B[i][r] and fji > B[r][j]):
                    ok = False
        if ok and acyclic(B, ins) and acyclic(B, outs):
            out.add(r)
    return out


def prefork_points(B):
    """All r such that the 4-vertex quiver is a pre-fork with vertices {r, k, k'} for some k != k'
    (Ervin Def. 4.5): Q minus k and Q minus k' are forks with the common point of return r, and every
    vertex i not in {k, k'} has arrows k -> i and k' -> i, or i -> k and i -> k'."""
    out = set()
    for k, kp in itertools.combinations(range(4), 2):
        rest = [i for i in range(4) if i not in (k, kp)]
        cond2 = all((B[k][i] > 0 and B[kp][i] > 0) or (B[i][k] > 0 and B[i][kp] > 0) for i in rest)
        if not cond2:
            continue
        f1 = fork_points(B, [v for v in range(4) if v != k])
        f2 = fork_points(B, [v for v in range(4) if v != kp])
        for r in f1 & f2:
            out.add(r)
    return out


def exits(t):
    """The set of m such that (t, m) is an exit: a fork with point of return m or a pre-fork with point of
    return m."""
    B = mat(t)
    return fork_points(B, [0, 1, 2, 3]) | prefork_points(B)


def is_fork(t):
    return bool(fork_points(mat(t), [0, 1, 2, 3]))


def is_acyclic_q(t):
    return acyclic(mat(t), [0, 1, 2, 3])


def no_far_region(t):
    """Sufficient test for lying in no far region, from the definitions: every quiver of a far region is a
    fork, a pre-fork, a wing or a tip (Ervin Cor. 4.25).  Forks are abundant.  A pre-fork that is not a
    fork has exactly one pair {k, k'} with |b| < 2 and both deletions forks.  A wing has |w_kk'| < 2,
    W - k' a fork, W - k abundant acyclic.  A tip has |t_kk'| < 2, T - k a fork, T - k' fork or abundant
    acyclic.  So in all cases: no light pair and a fork, or one light pair with both deletions forks or
    abundant acyclic and at least one a fork.  Returns True if t fails all of these."""
    B = mat(t)
    light = [(i, j) for (i, j) in PAIRS if abs(B[i][j]) < 2]
    if len(light) >= 2:
        return True
    if not light:
        return not fork_points(B, [0, 1, 2, 3])
    k, kp = light[0]
    kinds = []
    for v in (k, kp):
        V = [u for u in range(4) if u != v]
        if fork_points(B, V):
            kinds.append("fork")
        elif abundant(B, V) and acyclic(B, V):
            kinds.append("aa")
        else:
            kinds.append(None)
    return None in kinds or "fork" not in kinds


def is_vortex(t):
    if any(x == 0 for x in t):
        return False
    B = mat(t)
    for a in range(4):
        col = [B[a][j] for j in range(4) if j != a]
        if all(c > 0 for c in col) or all(c < 0 for c in col):
            if not acyclic(B, [i for i in range(4) if i != a]):
                return True
    return False


# ----------------------------------------------------------------------------- V' and the core
def allowed_steps(x, ex_cache=None):
    """Targets (labelled) of the allowed steps out of the labelled quiver x: m -> mu_m(x) unless
    (mu_m(x), m) is an exit and (x, m) is not."""
    ex = exits(x) if ex_cache is None else ex_cache(x)
    out = []
    for m in range(4):
        y = mut(x, m)
        ey = exits(y) if ex_cache is None else ex_cache(y)
        if m in ey and m not in ex:
            continue
        out.append((m, y))
    return out


def vprime(t, cap=5000, level_cap=None, skip_above=False):
    """V'(t) up to relabelling by BFS.  Returns (levels dict, adjacency dict, complete flag).
    With skip_above=True quivers above level_cap are recorded in 'above' and not expanded (search goes on);
    otherwise the search stops at the first one (complete = False)."""
    s = canon(t)
    lev = {s: level(s)}
    adj = {s: set()}
    above = set()
    queue = [s]
    qi = 0
    complete = True
    while qi < len(queue):
        x = queue[qi]
        qi += 1
        for m, y in allowed_steps(x):
            c = canon(y)
            if c not in lev:
                lc = level(c)
                if level_cap is not None and lc > level_cap:
                    if skip_above:
                        above.add(c)
                        complete = False
                        continue
                    return lev, adj, False, above
                if len(lev) >= cap:
                    return lev, adj, False, above
                lev[c] = lc
                adj[c] = set()
                queue.append(c)
            if c != x:
                adj[x].add(c)
    return lev, adj, complete, above


def sink_sccs(adj):
    """Strongly connected components of a finite digraph with no edge leaving them (iterative Tarjan)."""
    index = {}
    low = {}
    onstack = set()
    stack = []
    comps = []
    counter = [0]
    for v0 in adj:
        if v0 in index:
            continue
        work = [(v0, iter(adj[v0]))]
        index[v0] = low[v0] = counter[0]
        counter[0] += 1
        stack.append(v0)
        onstack.add(v0)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    onstack.add(w)
                    work.append((w, iter(adj[w])))
                    advanced = True
                    break
                elif w in onstack:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                u = work[-1][0]
                low[u] = min(low[u], low[v])
            if low[v] == index[v]:
                comp = set()
                while True:
                    w = stack.pop()
                    onstack.discard(w)
                    comp.add(w)
                    if w == v:
                        break
                comps.append(comp)
    sinks = []
    for c in comps:
        if all(w in c for v in c for w in adj[v]):
            sinks.append(c)
    return sinks


def core_of(t, cap=800, level_cap=10 ** 6):
    """(core as a frozenset or None, |V'|, number of sink components).  None when the search hit a cap."""
    lev, adj, complete, _ = vprime(t, cap=cap, level_cap=level_cap)
    if not complete:
        return None, len(lev), None
    sinks = sink_sccs(adj)
    if len(sinks) != 1:
        return frozenset(), len(lev), len(sinks)
    return frozenset(sinks[0]), len(lev), 1


# ----------------------------------------------------------------------------- families (tube certificates)
def fam_terms(Y, tau, n_max):
    """Y(0..n_max) of the family (Y0, Y1, Y2, tau): e(n+3) = (tau+1) e(n+2) - (tau+1) e(n+1) + e(n)."""
    out = [tuple(Y[0]), tuple(Y[1]), tuple(Y[2])]
    while len(out) <= n_max:
        a, b, c = out[-3], out[-2], out[-1]
        out.append(tuple((tau + 1) * c[i] - (tau + 1) * b[i] + a[i] for i in range(6)))
    return out[:n_max + 1]


def _mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def fam_term(Y, tau, n):
    """Y(n) for large n by the companion matrix power."""
    if n <= 2:
        return tuple(Y[n])
    C = [[0, 1, 0], [0, 0, 1], [1, -(tau + 1), tau + 1]]
    P = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    k = n
    while k:
        if k & 1:
            P = _mm(P, C)
        C = _mm(C, C)
        k >>= 1
    return tuple(P[0][0] * Y[0][a] + P[0][1] * Y[1][a] + P[0][2] * Y[2][a] for a in range(6))


def fam_find(Y, tau, q):
    """Least n >= 0 with canon(Y(n)) == q, searched among the n with weight(Y(n)) == weight(q), assuming the
    weight is non-decreasing in n (checked by the caller on the enumerated part).  None if not found."""
    w = weight(q)
    if weight(Y[0]) > w:
        return None
    if Y[0] == Y[1] == Y[2]:
        return 0 if canon(Y[0]) == q else None
    hi = 1
    while weight(fam_term(Y, tau, hi)) < w:
        hi *= 2
        if hi > 1 << 80:
            return None
    lo = 0
    while lo < hi:
        mid = (lo + hi) // 2
        if weight(fam_term(Y, tau, mid)) < w:
            lo = mid + 1
        else:
            hi = mid
    n = lo
    while True:
        y = fam_term(Y, tau, n)
        if weight(y) != w:
            return None
        if canon(y) == q:
            return n
        n += 1
        if n > lo + 50:
            return None
