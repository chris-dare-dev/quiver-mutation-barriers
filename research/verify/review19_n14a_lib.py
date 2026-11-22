"""Independent review of note 14 (check A): own implementation of 4-vertex quiver
mutation and of Ervin's (arXiv 2306.07502) forks, pre-forks, wings, tips, keys, written from the
definitions and NOT from experiments/n4_opposite.py.

A quiver is a 4x4 skew-symmetric integer matrix stored as a tuple of 4 row tuples; B[i][j] > 0 means
B[i][j] arrows i -> j.  Exact Python integers throughout.
"""
import itertools

V = (0, 1, 2, 3)
PERM24 = list(itertools.permutations(V))
UPPER = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


# ----------------------------------------------------------------------------- basic operations
def from6(t):
    B = [[0] * 4 for _ in V]
    for (i, j), x in zip(UPPER, t):
        B[i][j] = x
        B[j][i] = -x
    return tuple(tuple(r) for r in B)


def to6(B):
    return tuple(B[i][j] for i, j in UPPER)


def from_rows(rows):
    return tuple(tuple(int(x) for x in r) for r in rows)


def mut(B, k):
    """Fomin-Zelevinsky matrix mutation: b'_ij = -b_ij if k in {i,j}, else
    b_ij + (|b_ik| b_kj + b_ik |b_kj|) / 2."""
    out = []
    for i in V:
        row = []
        for j in V:
            if i == k or j == k:
                row.append(-B[i][j])
            else:
                row.append(B[i][j] + (abs(B[i][k]) * B[k][j] + B[i][k] * abs(B[k][j])) // 2)
        out.append(tuple(row))
    return tuple(out)


def neg(B):
    return tuple(tuple(-x for x in r) for r in B)


def relabel(B, p):
    """New vertex a is old vertex p[a]."""
    return tuple(tuple(B[p[a]][p[b]] for b in V) for a in V)


def key(B):
    """Canonical form up to relabelling: the lexicographically least upper-triangle tuple."""
    return min(tuple(B[p[i]][p[j]] for i, j in UPPER) for p in PERM24)


def level(B):
    return max(abs(B[i][j]) for i, j in UPPER)


def weight(B):
    return sum(abs(B[i][j]) for i, j in UPPER)


# ----------------------------------------------------------------------------- graph predicates
def has_cycle(B, S):
    """Oriented cycle inside the full subquiver on S, by transitive closure (Warshall)."""
    S = list(S)
    R = {(a, b): B[a][b] > 0 for a in S for b in S}
    for m in S:
        for a in S:
            if R[(a, m)]:
                for b in S:
                    if R[(m, b)]:
                        R[(a, b)] = True
    return any(R[(a, a)] for a in S)


def abundant(B, S):
    return all(abs(B[a][b]) >= 2 for a, b in itertools.combinations(sorted(S), 2))


def fork_returns(B, S=V):
    """All r in S such that the full subquiver on S is a fork with point of return r (Ervin Def. 2.5):
    abundant, not acyclic, for all i in F^-(r), j in F^+(r): f_ji > f_ir and f_ji > f_rj, and the full
    subquivers on F^-(r) and on F^+(r) are acyclic."""
    S = tuple(S)
    if not abundant(B, S) or not has_cycle(B, S):
        return set()
    out = set()
    for r in S:
        ins = [i for i in S if i != r and B[i][r] > 0]
        outs = [j for j in S if j != r and B[r][j] > 0]
        ok = all(B[j][i] > B[i][r] and B[j][i] > B[r][j] for i in ins for j in outs)
        if ok and not has_cycle(B, ins) and not has_cycle(B, outs):
            out.add(r)
    return out


def abundant_acyclic(B, S):
    return abundant(B, S) and not has_cycle(B, S)


def side_condition(B, k, kp):
    """Ervin Def. 4.5 (2) / Def. 4.1 (2): every other vertex i has arrows k -> i and k' -> i, or
    i -> k and i -> k' (the k k' edge is arbitrary)."""
    return all((B[k][i] > 0 and B[kp][i] > 0) or (B[i][k] > 0 and B[i][kp] > 0)
               for i in V if i not in (k, kp))


def prefork_triples(B):
    """All (r, k, k') with k < k' such that B is a pre-fork with vertices {r, k, k'} (Ervin Def. 4.5)."""
    out = set()
    for k, kp in itertools.combinations(V, 2):
        if not side_condition(B, k, kp):
            continue
        r1 = fork_returns(B, [v for v in V if v != k])
        r2 = fork_returns(B, [v for v in V if v != kp])
        for r in r1 & r2:
            out.add((r, k, kp))
    return out


def is_key(B):
    """(k, k') pairs with B a key (Ervin Def. 4.1)."""
    out = set()
    for k, kp in itertools.combinations(V, 2):
        if (side_condition(B, k, kp) and abundant_acyclic(B, [v for v in V if v != k])
                and abundant_acyclic(B, [v for v in V if v != kp])):
            out.add((k, kp))
    return out


def between(B, k, kp):
    """Q_{kk'} = [Q^+(k) cap Q^-(k')] cup [Q^+(k') cap Q^-(k)], as a set of the other vertices."""
    return {i for i in V if i not in (k, kp) and ((B[k][i] > 0 and B[i][kp] > 0) or (B[kp][i] > 0 and B[i][k] > 0))}


def _ab_condition(B, k, kp, variant):
    """The last bullet of Ervin Def. 4.14 / 4.18 ("b >= a + 2", with a the i-k edge and b the i-k' edge).
    The two pictures are lost in the text extraction; two readings are implemented:
      'oriented': whenever {i, k, k'} carries an oriented 3-cycle, |b_ik'| >= |b_ik| + 2;
      'none'    : the bullet is dropped (the weakest reading; a superset of every reading)."""
    if variant == "none":
        return True
    for i in V:
        if i in (k, kp):
            continue
        if has_cycle(B, (i, k, kp)) and not abs(B[i][kp]) >= abs(B[i][k]) + 2:
            return False
    return True


def wing_pairs(B, variant="oriented"):
    """All (k, k') (ordered: k is the point of return) such that B is a wing with point of return k
    (Ervin Def. 4.14)."""
    out = set()
    for k in V:
        for kp in V:
            if kp == k or abs(B[k][kp]) >= 2:
                continue
            others = {i for i in V if i not in (k, kp)}
            if between(B, k, kp) != others:
                continue
            if k not in fork_returns(B, [v for v in V if v != kp]):
                continue
            if not abundant_acyclic(B, [v for v in V if v != k]):
                continue
            if not _ab_condition(B, k, kp, variant):
                continue
            out.add((k, kp))
    return out


def tip_pairs(B, variant="oriented"):
    """All (k', k) such that B is a tip with point of return k' (Ervin Def. 4.18), k the other vertex of
    the light pair."""
    out = set()
    for kp in V:
        for k in V:
            if k == kp or abs(B[k][kp]) >= 2:
                continue
            if kp not in fork_returns(B, [v for v in V if v != k]):
                continue
            btw = between(B, k, kp)
            if B[kp][k] == 0:
                if btw:
                    continue
            elif B[kp][k] == 1:                      # t_{k'k} = 1: one arrow k' -> k
                if btw != {i for i in V if i not in (k, kp) and B[i][kp] > 0}:
                    continue
            else:                                    # t_{kk'} = 1: one arrow k -> k'
                if btw != {i for i in V if i not in (k, kp) and B[kp][i] > 0}:
                    continue
            rest = [v for v in V if v != kp]
            if B[k][kp] == 0:
                if k not in fork_returns(B, rest):
                    continue
            else:
                if not abundant_acyclic(B, rest):
                    continue
                if B[kp][k] == 1 and not all(B[k][i] > 0 for i in rest if i != k):
                    continue                          # k a source in T \ {k'}
                if B[k][kp] == 1 and not all(B[i][k] > 0 for i in rest if i != k):
                    continue                          # k a sink in T \ {k'}
            if not _ab_condition(B, k, kp, variant):
                continue
            out.add((kp, k))
    return out


def light_pairs(B):
    return [(i, j) for i, j in UPPER if abs(B[i][j]) < 2]


def exit_vertices(B):
    """m such that (B, m) is an exit: a fork with point of return m or a pre-fork with point of return m."""
    return fork_returns(B) | {r for r, k, kp in prefork_triples(B)}


def in_far_region_shape(B, variant="none"):
    """True if B is a fork, a pre-fork, a wing or a tip (necessary for lying in a far region)."""
    return bool(fork_returns(B) or prefork_triples(B) or wing_pairs(B, variant) or tip_pairs(B, variant))


# ----------------------------------------------------------------------------- allowed steps, V', core
def strict_up_exit(B, m, Bm=None):
    if Bm is None:
        Bm = mut(B, m)
    return (m in exit_vertices(Bm)) and (m not in exit_vertices(B))


def closure(B, cap=100000, level_cap=None):
    """V'(B) up to relabelling: dict key -> representative matrix, adjacency of allowed steps (keys),
    the strict up-exit steps found (source key, m, target matrix) and exhausted flag."""
    s = key(B)
    rep = {s: B}
    adj = {s: set()}
    ups = []
    todo = [s]
    while todo:
        x = todo.pop()
        X = rep[x]
        ex = exit_vertices(X)
        for m in V:
            Y = mut(X, m)
            if m not in ex and m in exit_vertices(Y):
                ups.append((x, m, Y))
                continue
            y = key(Y)
            if y not in rep:
                if len(rep) >= cap or (level_cap is not None and level(Y) > level_cap):
                    return rep, adj, ups, False
                rep[y] = Y
                adj[y] = set()
                todo.append(y)
            adj[x].add(y)
    return rep, adj, ups, True


def sink_sccs(adj):
    """Strongly connected components with no edge leaving them (Kosaraju, iterative)."""
    order = []
    seen = set()
    for s in adj:
        if s in seen:
            continue
        stack = [(s, iter(adj[s]))]
        seen.add(s)
        while stack:
            v, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                stack.pop()
                order.append(v)
            elif nxt not in seen:
                seen.add(nxt)
                stack.append((nxt, iter(adj[nxt])))
    radj = {v: set() for v in adj}
    for v in adj:
        for w in adj[v]:
            radj[w].add(v)
    comp = {}
    comps = []
    for s in reversed(order):
        if s in comp:
            continue
        c = len(comps)
        comps.append({s})
        comp[s] = c
        st = [s]
        while st:
            v = st.pop()
            for w in radj[v]:
                if w not in comp:
                    comp[w] = c
                    comps[c].add(w)
                    st.append(w)
    sinks = [C for i, C in enumerate(comps) if all(comp[w] == i for v in C for w in adj[v])]
    return sinks


def core_of(B, cap=100000, level_cap=None):
    rep, adj, ups, ex = closure(B, cap=cap, level_cap=level_cap)
    if not ex:
        return None
    sinks = sink_sccs(adj)
    return rep, adj, ups, sinks
