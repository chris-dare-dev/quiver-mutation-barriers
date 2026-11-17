"""Review of note 20 (note 23): independent helpers.

Written from the definitions only; nothing is imported or copied from the
scripts under review (np_qa_core*, np_barrier.c, np_rowwalk.py, np_corridor.py).

Conventions: a quiver on n vertices is an n x n skew-symmetric integer matrix B
(list of lists), b_ij > 0 meaning b_ij arrows i -> j.  Mutation at k:
  b'_ij = -b_ij                                   if k in {i, j}
  b'_ij = b_ij + [b_ik]+[b_kj]+ - [-b_ik]+[-b_kj]+ otherwise.
Height = largest |b_ij|.

Fork (Warkentin, thesis 2014, Def. 2.1, as quoted verbatim in note 19 section 4):
an abundant quiver (every pair joined by >= 2 arrows) that is not acyclic and
has a vertex r with
 (F1) q_ji > q_ir and q_ji > q_rj for all i in Q^-(r) (i -> r), j in Q^+(r) (r -> j),
 (F2) the full subquivers on Q^-(r) and on Q^+(r) are acyclic.
Valid for any number of vertices.
"""
import itertools


def mutate(B, k):
    n = len(B)
    C = [row[:] for row in B]
    for i in range(n):
        if i == k:
            continue
        bik = B[i][k]
        for j in range(n):
            if j == k or j == i:
                continue
            bkj = B[k][j]
            if bik > 0 and bkj > 0:
                C[i][j] = B[i][j] + bik * bkj
            elif bik < 0 and bkj < 0:
                C[i][j] = B[i][j] - bik * bkj
    for i in range(n):
        if i != k:
            C[i][k] = -B[i][k]
            C[k][i] = -B[k][i]
    return C


def height(B):
    n = len(B)
    return max(abs(B[i][j]) for i in range(n) for j in range(i + 1, n))


def from_upper(n, ups):
    """ups = (b01, b02, ..., b0n-1, b12, ...) row by row."""
    B = [[0] * n for _ in range(n)]
    it = iter(ups)
    for i in range(n):
        for j in range(i + 1, n):
            v = next(it)
            B[i][j] = v
            B[j][i] = -v
    return B


def upper(B):
    n = len(B)
    return tuple(B[i][j] for i in range(n) for j in range(i + 1, n))


def acyclic_on(B, verts):
    """True if the full subquiver on verts has no oriented cycle."""
    rem = set(verts)
    while rem:
        src = None
        for v in rem:
            if all(not (B[u][v] > 0) for u in rem if u != v):
                src = v
                break
        if src is None:
            return False
        rem.remove(src)
    return True


def is_fork(B):
    n = len(B)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(B[i][j]) < 2:
                return False
    if acyclic_on(B, range(n)):
        return False
    for r in range(n):
        qin = [i for i in range(n) if i != r and B[i][r] > 0]
        qout = [j for j in range(n) if j != r and B[r][j] > 0]
        ok = True
        for i in qin:
            for j in qout:
                if not (B[j][i] > B[i][r] and B[j][i] > B[r][j]):
                    ok = False
                    break
            if not ok:
                break
        if ok and acyclic_on(B, qin) and acyclic_on(B, qout):
            return True
    return False


_PERMS = {}


def perms(n):
    if n not in _PERMS:
        _PERMS[n] = list(itertools.permutations(range(n)))
    return _PERMS[n]


def relabel(B, s):
    """vertex i of B becomes vertex s[i]."""
    n = len(B)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            C[s[i]][s[j]] = B[i][j]
    return C


def canon(B):
    """Lexicographic maximum of the upper triangle over all relabellings."""
    n = len(B)
    best = None
    for s in perms(n):
        # C[i][j] = B[s^-1 i][s^-1 j]; enumerate t = s^-1 directly
        t = s
        tup = tuple(B[t[i]][t[j]] for i in range(n) for j in range(i + 1, n))
        if best is None or tup > best:
            best = tup
    return best


def aut_order(B):
    n = len(B)
    c = 0
    for t in perms(n):
        if all(B[t[i]][t[j]] == B[i][j] for i in range(n) for j in range(i + 1, n)):
            c += 1
    return c


def negate(B):
    return [[-v for v in row] for row in B]


# ---------------------------------------------------------------- note 18 data

def H_of(a):
    if a % 2:
        return 4 * a**3 - 3 * a**2 + (5 * a - 1) // 2
    return 4 * a**3 - 3 * a**2 + (3 * a - 4) // 2


def Q_matrix(a):
    """Q_a = (-(a-3), a-2, a+1, -(a+1) | -(a+1), -a, 2, -2, -a, -(a+1)); x = vertex 0."""
    return from_upper(5, (-(a - 3), a - 2, a + 1, -(a + 1),
                          -(a + 1), -a, 2, -2, -a, -(a + 1)))


def W_matrix(m, j):
    """W_m(j) on labels p, q, r, s = 0, 1, 2, 3."""
    B = [[0] * 4 for _ in range(4)]
    p, q, r, s = 0, 1, 2, 3

    def put(i, k, v):
        B[i][k] = v
        B[k][i] = -v
    put(q, p, 2)
    put(s, r, 2)
    put(p, r, m - j)
    put(q, r, -(m + 1 - j))
    put(p, s, j)
    put(q, s, -(j - 1))
    return B
