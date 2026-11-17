"""
review19_n13_lib.py -- independent re-implementation for the second review of note 13.

Written from the definitions in arXiv 2610.36179 (paper) and arXiv 2406.03604 (Fomin-Neville, FN);
it imports nothing from the scripts under review (n4_conj55.py, n4_all.py, n4_plateaus.py, review12.py).

Conventions (paper section 2):
  b(Q) = (b01, b02, b03, b12, b13, b23)   (0-based labels; the paper's b12, b13, b14, b23, b24, b34)
  b_ij > 0 means b_ij arrows i -> j.
  mutation: paper (2):  b'_ij = -b_ij if k in {i, j}, else b_ij + [b_ik]_+ [b_kj]_+ - [-b_ik]_+ [-b_kj]_+.
  relabelling: b_ij(Q^pi) = b_{pi(i) pi(j)}(Q).
  height: max |b_ij|.
  cyclic ordering: a linear order (v1, v2, v3, v4) up to rotation; normalised to start with vertex 0.
  wiggle (FN Def. 2.3): swap two circle-neighbours not joined by an arrow.
  proper vertex k in an ordering (FN Def. 5.2): every path i -> k -> j makes a right turn, i.e. i, k, j are
     met in this order when going clockwise (= increasing position, cyclically) from i.
  proper wiggle class (FN Def. 5.4 / 11.1, paper 2.1): every vertex is proper in SOME ordering of the class.
  Markov value: paper (4), on the linear representative.  Pfaffian: paper (5).
  H(Q): paper (13).
  vortex (FN Def. 13.1, second form): complete, contains an oriented 3-cycle, contains no oriented 4-cycle.
"""
import heapq
import itertools
from collections import deque

PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
PERMS = list(itertools.permutations(range(4)))


def full(t):
    B = [[0] * 4 for _ in range(4)]
    for (i, j), x in zip(PAIRS, t):
        B[i][j] = x
        B[j][i] = -x
    return B


def pos_(x):
    return x if x > 0 else 0


def mutate(t, k):
    B = full(t)
    out = []
    for (i, j) in PAIRS:
        if i == k or j == k:
            out.append(-B[i][j])
        else:
            bik, bkj = B[i][k], B[k][j]
            out.append(B[i][j] + pos_(bik) * pos_(bkj) - pos_(-bik) * pos_(-bkj))
    return tuple(out)


# relabelling maps: new coordinate p = sign * old coordinate src
_RL = []
for pi in PERMS:
    m = []
    for (i, j) in PAIRS:
        a, b = pi[i], pi[j]
        if a < b:
            m.append((PAIRS.index((a, b)), 1))
        else:
            m.append((PAIRS.index((b, a)), -1))
    _RL.append(m)


def relabel(t, pi_index):
    return tuple(s * t[src] for src, s in _RL[pi_index])


def canon(t):
    """Canonical form up to relabelling: lexicographically smallest of the 24 relabellings, compared on the
    REVERSED tuple (b23 most significant).  Returned as an ordinary tuple."""
    best = None
    for m in _RL:
        u = tuple(s * t[src] for src, s in m)
        r = u[::-1]
        if best is None or r < best:
            best = r
    return best[::-1]


def ht(t):
    return max(abs(x) for x in t)


# ---------------------------------------------------------------- acyclicity, connectivity, triangles, vortices
_TRI3 = [(0, 1, 2), (0, 2, 1), (0, 1, 3), (0, 3, 1), (0, 2, 3), (0, 3, 2), (1, 2, 3), (1, 3, 2)]
_CYC4 = [(0,) + p for p in itertools.permutations((1, 2, 3))]


def has_3cycle(B):
    return any(B[a][b] > 0 and B[b][c] > 0 and B[c][a] > 0 for a, b, c in _TRI3)


def has_4cycle(B):
    return any(B[a][b] > 0 and B[b][c] > 0 and B[c][d] > 0 and B[d][a] > 0 for a, b, c, d in _CYC4)


def is_acyclic(t):
    """No directed cycle; on 4 vertices without 2-cycles a cycle has length 3 or 4."""
    B = full(t)
    return not has_3cycle(B) and not has_4cycle(B)


def is_connected(t):
    b01, b02, b03, b12, b13, b23 = t
    rows = [(b01, b02, b03), (b01, b12, b13), (b02, b12, b23), (b03, b13, b23)]
    if any(r == (0, 0, 0) for r in rows):
        return False
    if b02 == b03 == b12 == b13 == 0:      # {0,1} | {2,3}
        return False
    if b01 == b03 == b12 == b23 == 0:      # {0,2} | {1,3}
        return False
    if b01 == b02 == b13 == b23 == 0:      # {0,3} | {1,2}
        return False
    return True


def cyclic_triangle(t):
    """Paper Prop. 2.1: a full triangle that is oriented with x, y, z >= 2 and x^2+y^2+z^2-xyz <= 4."""
    B = full(t)
    for a, b, c in itertools.combinations(range(4), 3):
        x, y, z = B[a][b], B[b][c], B[c][a]
        if (x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0):
            x, y, z = abs(x), abs(y), abs(z)
            if min(x, y, z) >= 2 and x * x + y * y + z * z - x * y * z <= 4:
                return True
    return False


def is_vortex(t):
    """FN Def. 13.1, second form: complete, has an oriented 3-cycle, has no oriented 4-cycle."""
    if any(x == 0 for x in t):
        return False
    B = full(t)
    return has_3cycle(B) and not has_4cycle(B)


def is_vortex_first_form(t):
    """FN Def. 13.1, first form: complete, a vertex is a source or sink, the other three an oriented 3-cycle."""
    if any(x == 0 for x in t):
        return False
    B = full(t)
    for v in range(4):
        o = [u for u in range(4) if u != v]
        if all(B[v][u] > 0 for u in o) or all(B[u][v] > 0 for u in o):
            a, b, c = o
            if (B[a][b] > 0 and B[b][c] > 0 and B[c][a] > 0) or (B[a][b] < 0 and B[b][c] < 0 and B[c][a] < 0):
                return True
    return False


# ---------------------------------------------------------------- cyclic orderings, wiggles, properness
ORDS = [(0,) + p for p in itertools.permutations((1, 2, 3))]


def _norm(w):
    r = w.index(0)
    return tuple(w[r:] + w[:r])


def vertex_proper(B, w, k):
    """FN Def. 5.2: every path i -> k -> j makes a right turn at k (i, k, j clockwise)."""
    for i in range(4):
        if B[i][k] <= 0:
            continue
        for j in range(4):
            if B[k][j] <= 0:
                continue
            r = w.index(i)
            rot = w[r:] + w[:r]          # start the circle at i and go clockwise
            if rot.index(k) > rot.index(j):
                return False
    return True


def wiggle_classes(B):
    """Wiggle-equivalence classes of the 6 cyclic orderings (FN Def. 2.3, 2.5), via BFS."""
    seen = set()
    classes = []
    for w0 in ORDS:
        if w0 in seen:
            continue
        cls = [w0]
        seen.add(w0)
        q = deque([w0])
        while q:
            w = q.popleft()
            for r in range(4):
                s = (r + 1) % 4
                if B[w[r]][w[s]] == 0:
                    nw = list(w)
                    nw[r], nw[s] = nw[s], nw[r]
                    nw = _norm(nw)
                    if nw not in seen:
                        seen.add(nw)
                        cls.append(nw)
                        q.append(nw)
        classes.append(cls)
    return classes


def markov_value(t, w):
    """Paper (4) on the linear representative w = (v1, v2, v3, v4)."""
    B = full(t)
    v1, v2, v3, v4 = w
    a, b, c = B[v1][v2], B[v1][v3], B[v1][v4]
    d, e, f = B[v2][v3], B[v2][v4], B[v3][v4]
    return a * a + b * b + c * c + d * d + e * e + f * f + a * b * d + a * c * e + b * c * f + d * e * f + a * c * d * f


def pfaffian(t):
    b01, b02, b03, b12, b13, b23 = t
    return b01 * b23 - b02 * b13 + b03 * b12


def _sign(x):
    return (x > 0) - (x < 0)


_PC_CACHE = {}


def proper_class_reps(t):
    """Representative orderings (one per class) of the proper wiggle classes of t, and all classes.
    Depends only on the sign pattern; cached."""
    key = tuple(_sign(x) for x in t)
    if key in _PC_CACHE:
        return _PC_CACHE[key]
    B = full(key)
    out = []
    for cls in wiggle_classes(B):
        if all(any(vertex_proper(B, w, k) for w in cls) for k in range(4)):
            out.append(tuple(cls))
    _PC_CACHE[key] = out
    return out


def proper_markov(t):
    """[(M, class)] over the proper wiggle classes of t; asserts M constant on each class."""
    res = []
    for cls in proper_class_reps(t):
        vals = {markov_value(t, w) for w in cls}
        assert len(vals) == 1, (t, cls, vals)
        res.append((vals.pop(), cls))
    return res


def H_of(t):
    """Paper (13); None if t has no proper wiggle class."""
    pm = proper_markov(t)
    if not pm:
        return None
    return max([ht(t)] + [m for m, _ in pm])


def lemma24_excluded(t):
    """Paper Lemma 2.4 contrapositive: connected, has a proper class, and EVERY proper class has
    M < 3 or 2|p| >= M.  Then t is mutation-cyclic."""
    if not is_connected(t):
        return False
    pm = proper_markov(t)
    if not pm:
        return False
    p = abs(pfaffian(t))
    return all(m < 3 or 2 * p >= m for m, _ in pm)


def certificate(t):
    """First of tri / vortex / l24 that t carries, or None."""
    if cyclic_triangle(t):
        return "tri"
    if is_vortex(t):
        return "vortex"
    if lemma24_excluded(t):
        return "l24"
    return None


# ---------------------------------------------------------------- searches
def neighbours(t):
    return [mutate(t, k) for k in range(4)]


def bfs_within(t, L, labelled=False, budget=10 ** 7, want_acyclic=True):
    """Component of t in the mutation graph on quivers of height <= L (labelled, or up to relabelling via
    canon).  Returns (acyclic member found or None, number of states visited, exhausted?)."""
    f = (lambda x: x) if labelled else canon
    s = f(t)
    assert ht(s) <= L
    seen = {s}
    q = deque([s])
    while q:
        x = q.popleft()
        if want_acyclic and is_acyclic(x):
            return x, len(seen), False
        for y in neighbours(x):
            if ht(y) <= L:
                fy = f(y)
                if fy not in seen:
                    seen.add(fy)
                    if len(seen) > budget:
                        return None, len(seen), False
                    q.append(fy)
    return None, len(seen), True


def bottleneck_to(t, target, cap, budget=10 ** 6):
    """Least bottleneck (max height along a path) from t to the relabelling class of target, searching
    only through quivers of height <= cap.  None if not found."""
    tc = canon(target)
    s = canon(t)
    best = {s: ht(s)}
    heap = [(best[s], s)]
    done = set()
    while heap:
        b, x = heapq.heappop(heap)
        if x in done:
            continue
        done.add(x)
        if x == tc:
            return b
        if len(done) > budget:
            return None
        for y in neighbours(x):
            hy = ht(y)
            if hy > cap:
                continue
            cy = canon(y)
            nb = max(b, hy)
            if cy not in done and nb < best.get(cy, 1 << 62):
                best[cy] = nb
                heapq.heappush(heap, (nb, cy))
    return None


def my_resolve(t, budget=500_000):
    """Own bottleneck search of the class of t, up to relabelling.  Stops at
      - an acyclic quiver               -> ('acyclic', bottleneck, quiver)
      - a tri / vortex / l24 member      -> ('cyclic', cert, bottleneck, quiver)
      - the Cor. 5.2 bound: K = min over popped X of max(H(X), bn(X)); when the next bottleneck exceeds K,
        every quiver of bottleneck <= K (the whole component of t in G_K) was popped and none is acyclic; the X*
        attaining K has its G_{H(X*)}-component inside, so X* is mutation-cyclic (Cor. 5.2).
                                         -> ('cyclic', 'cor52', K, X*)
      - class exhausted                  -> ('cyclic', 'closed', None, None)
    """
    s = canon(t)
    best = {s: ht(s)}
    heap = [(best[s], s)]
    done = set()
    K, KX = None, None
    while heap:
        b, x = heapq.heappop(heap)
        if x in done:
            continue
        if K is not None and b > K:
            return ("cyclic", "cor52", K, KX, len(done))
        done.add(x)
        if is_acyclic(x):
            return ("acyclic", "acyclic", b, x, len(done))
        c = certificate(x)
        if c is not None:
            return ("cyclic", c, b, x, len(done))
        h = H_of(x)
        if h is not None and (K is None or max(h, b) < K):
            K, KX = max(h, b), x
        if len(done) >= budget:
            return ("undetermined", None, K, KX, len(done))
        for y in neighbours(x):
            cy = canon(y)
            nb = max(b, ht(y))
            if cy not in done and nb < best.get(cy, 1 << 62):
                best[cy] = nb
                heapq.heappush(heap, (nb, cy))
    return ("cyclic", "closed", None, None, len(done))
