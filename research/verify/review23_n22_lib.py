"""Review 3 of note 22 (review23_n22): an independent library for 4-vertex quivers.

Written from the definitions in note 14 §3 (forks, pre-forks, exits, allowed steps, V'), note 22 §2 and
note 3 §4 (rank 3).  Nothing here is imported, copied or adapted from n4_opposite*.py or n4_tube_lemma.py.

Quivers are 6-tuples (b01, b02, b03, b12, b13, b23) of ints; b_ji = -b_ij; b_ij > 0 means arrows i -> j.
level = max |b_ij|, weight = sum |b_ij|, canonical form = the largest tuple over the 24 relabellings
(the convention of the stored files, checked against them in review23_n22_selftest).
"""
import itertools

PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
IDX = {}
for _a, (_i, _j) in enumerate(PAIRS):
    IDX[(_i, _j)] = (_a, 1)
    IDX[(_j, _i)] = (_a, -1)

# relabelling p (vertex i goes to p[i]): new entry at pair (p[i], p[j]) is b_ij
PERMS = list(itertools.permutations(range(4)))
RELAB = []
for _p in PERMS:
    # new tuple position a' = pair (p[i],p[j]) sorted; we record, for every new position, (old position, sign)
    src = [None] * 6
    for a, (i, j) in enumerate(PAIRS):
        pi, pj = _p[i], _p[j]
        if pi < pj:
            src[IDX[(pi, pj)][0]] = (a, 1)
        else:
            src[IDX[(pj, pi)][0]] = (a, -1)
    RELAB.append(tuple(src))


def relabel(t, k):
    return tuple(s * t[a] for a, s in RELAB[k])


def canon(t):
    return max(tuple(s * t[a] for a, s in r) for r in RELAB)


def canon_with_perm(t):
    best, bk = None, None
    for k, r in enumerate(RELAB):
        c = tuple(s * t[a] for a, s in r)
        if best is None or c > best:
            best, bk = c, k
    return best, bk


def neg(t):
    return tuple(-x for x in t)


def level(t):
    return max(abs(x) for x in t)


def weight(t):
    return sum(abs(x) for x in t)


def e(t, i, j):
    if i == j:
        return 0
    a, s = IDX[(i, j)]
    return s * t[a]


def mutate(t, k):
    out = []
    for (i, j), x in zip(PAIRS, t):
        if i == k or j == k:
            out.append(-x)
        else:
            bik, bkj = e(t, i, k), e(t, k, j)
            # b'_ij = b_ij + [b_ik]_+ [b_kj]_+ - [-b_ik]_+ [-b_kj]_+
            if bik > 0 and bkj > 0:
                x = x + bik * bkj
            elif bik < 0 and bkj < 0:
                x = x - bik * bkj
            out.append(x)
    return tuple(out)


def acyclic_on(t, verts):
    """The full subquiver on verts has no oriented cycle (verts has at most 4 vertices)."""
    verts = list(verts)
    rem = set(verts)
    while rem:
        src = [v for v in rem if all(e(t, u, v) <= 0 for u in rem if u != v)]
        if not src:
            return False
        rem.discard(src[0])
    return True


def is_acyclic(t):
    return acyclic_on(t, range(4))


def fork_with_return(t, r, verts=(0, 1, 2, 3)):
    """Ervin Def. 2.5 / Warkentin Def. 2.1 on the full subquiver on verts: abundant, not acyclic, and r is a
    point of return: for every path i -> r -> j, b_ji > b_ir and b_ji > b_rj (arrows j -> i, more of them);
    in- and out-neighbourhoods of r acyclic."""
    vs = list(verts)
    if r not in vs:
        return False
    for a in range(len(vs)):
        for b in range(a + 1, len(vs)):
            if abs(e(t, vs[a], vs[b])) < 2:
                return False
    if acyclic_on(t, vs):
        return False
    ins = [i for i in vs if i != r and e(t, i, r) > 0]
    outs = [j for j in vs if j != r and e(t, r, j) > 0]
    for i in ins:
        for j in outs:
            bji = e(t, j, i)
            if not (bji > e(t, i, r) and bji > e(t, r, j)):
                return False
    return acyclic_on(t, ins) and acyclic_on(t, outs)


def prefork_with_return(t, r):
    """Ervin Def. 4.5: two vertices k != k' (both != r) with P - {k}, P - {k'} forks with point of return r,
    and every other vertex has arrows to both k and k' or from both."""
    others = [v for v in range(4) if v != r]
    for k, kp in itertools.combinations(others, 2):
        rest_k = [v for v in range(4) if v != k]
        rest_kp = [v for v in range(4) if v != kp]
        if not (fork_with_return(t, r, rest_k) and fork_with_return(t, r, rest_kp)):
            continue
        ok = True
        for i in range(4):
            if i in (k, kp):
                continue
            a, b = e(t, i, k), e(t, i, kp)
            if not ((a > 0 and b > 0) or (a < 0 and b < 0)):
                ok = False
                break
        if ok:
            return True
    return False


def is_exit(t, m):
    return fork_with_return(t, m) or prefork_with_return(t, m)


def exits(t):
    return frozenset(m for m in range(4) if is_exit(t, m))


def strict_up_exit(t, m, z=None):
    if z is None:
        z = mutate(t, m)
    return is_exit(z, m) and not is_exit(t, m)


def allowed(t, m, z=None):
    return not strict_up_exit(t, m, z)


def light_pairs(t):
    return sum(1 for x in t if abs(x) < 2)


def is_fork_any(t):
    return any(fork_with_return(t, r) for r in range(4))


def direct_no_far_region(t):
    """Sufficient test (note 14 §3 consequence (b)): two light pairs, or abundant and not a fork."""
    lp = light_pairs(t)
    if lp >= 2:
        return True
    if lp == 0 and not is_fork_any(t):
        return True
    return False


def cut(x, L, cap=None, keep_frontier=False):
    """V'(x) cut at level L: quivers (canonical) reached from x by allowed steps through quivers of level <= L.
    Returns (dict canon -> level, complete flag, frontier count)."""
    s = canon(x)
    seen = {s: level(s)}
    todo = [s]
    nfront = 0
    while todo:
        y = todo.pop()
        ey = exits(y)
        for m in range(4):
            z = mutate(y, m)
            lz = level(z)
            if lz > L:
                if keep_frontier and (m in ey or not is_exit(z, m)):
                    nfront += 1
                continue
            if m not in ey and is_exit(z, m):
                continue
            c = canon(z)
            if c in seen:
                continue
            if cap is not None and len(seen) >= cap:
                return seen, False, nfront
            seen[c] = lz
            todo.append(c)
    return seen, True, nfront


def components(t):
    adj = {i: set() for i in range(4)}
    for (i, j), x in zip(PAIRS, t):
        if x:
            adj[i].add(j)
            adj[j].add(i)
    seen, comps = set(), []
    for s in range(4):
        if s in seen:
            continue
        st, c = [s], {s}
        seen.add(s)
        while st:
            u = st.pop()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    c.add(w)
                    st.append(w)
        comps.append(sorted(c))
    return comps


# ----------------------------------------------------------------------------- triangles (rank 3)
def tri_entries(t, g):
    """Signed entries of the triangle opposite g around the cycle a -> b -> c -> a: (b_ab, b_bc, b_ca),
    a < b < c the other vertices."""
    a, b, c = [v for v in range(4) if v != g]
    return (e(t, a, b), e(t, b, c), e(t, c, a))


def column(t, g):
    return tuple(e(t, i, g) for i in range(4) if i != g)


def markov_C(T3):
    """T3 = (b_ab, b_bc, b_ca): C = x^2 + y^2 + z^2 - xyz for an oriented 3-cycle (either orientation) and
    + xyz otherwise, x, y, z the weights (BBH).  NB: the signed form b_ab^2 + b_bc^2 + b_ca^2 - b_ab b_bc b_ca
    of note 22 §2 agrees with this only when the cycle is a -> b -> c -> a (all three entries >= 0 or the
    triangle acyclic with the right signs); it is not a mutation invariant (see markov_C_signed)."""
    x, y, z = T3
    p = abs(x * y * z)
    return x * x + y * y + z * z + (-p if tri_oriented(T3) else p)


def markov_C_signed(T3):
    """The signed form of note 22 §2, kept to test its invariance."""
    x, y, z = T3
    return x * x + y * y + z * z - x * y * z


def tri_oriented(T3):
    x, y, z = T3
    return (x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0)


def tri_type(T3):
    w = tuple(sorted(abs(v) for v in T3))
    cyc = tri_oriented(T3)
    if w[0] == 0 and w[1] == 0:
        return "(0,0,a)"
    if w[0] == 0 and w[1] == 1:
        return "(0,1,a)"
    if w[0] == 1 and w[1] == w[2] and w[1] >= 2:
        return "(1,a,a)" + (" oriented" if cyc else " acyclic")
    if w[0] == 1 and w[1] == 1:
        return "(1,1,a)" + (" oriented" if cyc else " acyclic")
    if w[0] == 1 and w[2] == w[1] + 1:
        return "(1,a,a+1)" + (" oriented" if cyc else " acyclic")
    if w == (2, 2, 2) and cyc:
        return "Markov"
    if w[0] == 2 and w[1] == w[2] and cyc:
        return "(2,m,m) oriented"
    return ("other oriented " if cyc else "other acyclic ") + str(w)


def rank3_root(T3):
    """Descent of note 3 Step 1 on a 3-vertex quiver with signed cyclic entries (x, y, z) = (b_ab, b_bc, b_ca).
    Returns ('acyclic', weights) or ('root', (x, y, z) as positive weights around the oriented cycle, in the
    cyclic order a -> b -> c -> a of the result)."""
    t = (0, 0, 0, T3[0], -T3[2], T3[1])     # vertex 0 isolated; b12 = x, b23 = y, b31 = z
    for _ in range(100000):
        x, y, z = e(t, 1, 2), e(t, 2, 3), e(t, 3, 1)
        if not tri_oriented((x, y, z)):
            return ("acyclic", tuple(sorted(abs(v) for v in (x, y, z))))
        ax, ay, az = abs(x), abs(y), abs(z)
        if min(ax, ay, az) >= 2 and 2 * az <= ax * ay and 2 * ax <= ay * az and 2 * ay <= ax * az:
            return ("root", (ax, ay, az) if x > 0 else (ax, az, ay))
        # a lowering move: vertex opposite the weight that drops.  vertex 3 is opposite b12 = x, etc.
        best = None
        for m, opp in ((3, ax), (1, ay), (2, az)):
            z2 = mutate(t, m)
            if weight(z2) < weight(t):
                if best is None or weight(z2) < weight(best):
                    best = z2
        if best is None:
            return ("stuck", (ax, ay, az))
        t = best
    return ("loop", None)
