"""Checks of note 22 (note 23, 2026-11-14).

Independent code: nothing is imported from n4_tube_lemma.py, n4_opposite*.py
or any other script of the notes under check.  Forks and pre-forks are
written from the definitions quoted in note 14 section 3 (Warkentin Def. 2.1,
Ervin Def. 4.5), on labelled 4x4 skew-symmetric integer matrices.

Subcommands:
  lemmas   random tests of Lemmas 22.1, 22.1', 22.2, 22.3, 22.6 and Prop. 22.4
  markov   Theorem 22.7: the columns v(z, n), their invariants, and the
           exhaustive cut of V'(X0) at levels 25, 50, 100, 200
  side     class 108970: the main tube Y_k and the side tubes
"""
import itertools
import random
import sys
from fractions import Fraction

N = 4
PERMS = list(itertools.permutations(range(N)))
PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def from6(t):
    B = [[0] * N for _ in range(N)]
    for (i, j), x in zip(PAIRS, t):
        B[i][j] = x
        B[j][i] = -x
    return B


def to6(B):
    return tuple(B[i][j] for i, j in PAIRS)


def mutate(B, k):
    n = len(B)
    C = [row[:] for row in B]
    for i in range(n):
        for j in range(n):
            if i == k or j == k:
                C[i][j] = -B[i][j]
            else:
                C[i][j] = B[i][j] + max(B[i][k], 0) * max(B[k][j], 0) - max(-B[i][k], 0) * max(-B[k][j], 0)
    return C


def canon(B):
    """Least 6-tuple over the 24 relabellings."""
    best = None
    for p in PERMS:
        t = tuple(B[p[i]][p[j]] for i, j in PAIRS)
        if best is None or t < best:
            best = t
    return best


def level(B):
    return max(abs(B[i][j]) for i in range(len(B)) for j in range(len(B)))


def acyclic_on(B, verts):
    """Is the full subquiver on verts acyclic?  (Kahn's algorithm.)"""
    verts = list(verts)
    indeg = {v: sum(1 for u in verts if B[u][v] > 0) for v in verts}
    left = set(verts)
    while True:
        src = [v for v in left if indeg[v] == 0]
        if not src:
            break
        v = src[0]
        left.remove(v)
        for w in left:
            if B[v][w] > 0:
                indeg[w] -= 1
    return not left


def is_fork(B, r, verts=None):
    """Warkentin Def. 2.1 on the full subquiver on verts, point of return r."""
    if verts is None:
        verts = list(range(len(B)))
    verts = list(verts)
    if r not in verts:
        return False
    for a, b in itertools.combinations(verts, 2):
        if abs(B[a][b]) < 2:
            return False          # not abundant
    if acyclic_on(B, verts):
        return False
    ins = [i for i in verts if i != r and B[i][r] > 0]
    outs = [j for j in verts if j != r and B[r][j] > 0]
    if not acyclic_on(B, ins) or not acyclic_on(B, outs):
        return False
    for i in ins:
        for j in outs:
            # need arrows j -> i, more than i -> r and r -> j
            if not (B[j][i] > B[i][r] and B[j][i] > B[r][j]):
                return False
    return True


def is_prefork(B, r):
    """Ervin Def. 4.5: two vertices k != k' such that B minus k and B minus k'
    are forks with common point of return r, and every other vertex has arrows
    to both k and k' or from both."""
    n = len(B)
    allv = list(range(n))
    for k, kk in itertools.combinations([v for v in allv if v != r], 2):
        if not is_fork(B, r, [v for v in allv if v != k]):
            continue
        if not is_fork(B, r, [v for v in allv if v != kk]):
            continue
        ok = True
        for i in allv:
            if i in (k, kk):
                continue
            if not ((B[i][k] > 0 and B[i][kk] > 0) or (B[i][k] < 0 and B[i][kk] < 0)):
                ok = False
                break
        if ok:
            return True
    return False


def is_exit(B, m):
    return is_fork(B, m) or is_prefork(B, m)


def allowed(B, m):
    """The step B -> mu_m(B) is allowed unless it is a strict up-exit step."""
    Y = mutate(B, m)
    return not (is_exit(Y, m) and not is_exit(B, m))


def pf(B):
    return B[0][1] * B[2][3] - B[0][2] * B[1][3] + B[0][3] * B[1][2]


# ---------------------------------------------------------------- lemmas

def rand_with_column(g, rng, vgen, tgen):
    B = [[0] * N for _ in range(N)]
    others = [i for i in range(N) if i != g]
    for i in others:
        x = vgen(i)
        B[i][g] = x
        B[g][i] = -x
    for a, b in itertools.combinations(others, 2):
        x = tgen()
        B[a][b] = x
        B[b][a] = -x
    return B


def cmd_lemmas(seed=1):
    rng = random.Random(seed)
    out = []

    # Lemma 22.1: (D1)-(D3) => (X, g) not an exit, (mu_g X, g) an exit;
    # fork iff |b_kk'| >= 2, else pre-fork.
    tested = fail = forks = preforks = 0
    while tested < 20000:
        g = rng.randrange(N)
        W = rng.choice([4, 8, 30, 200])
        others = [i for i in range(N) if i != g]
        B = rand_with_column(g, rng, lambda i: rng.choice([-1, 1]) * rng.randint(2, W),
                             lambda: rng.randint(-W, W))
        v = {i: B[i][g] for i in others}
        if not (any(x > 0 for x in v.values()) and any(x < 0 for x in v.values())):
            continue
        if any(abs(B[a][b]) >= max(abs(v[a]), abs(v[b])) for a, b in itertools.combinations(others, 2)):
            continue
        tested += 1
        Y = mutate(B, g)
        I = [i for i in others if v[i] > 0]
        O = [i for i in others if v[i] < 0]
        pair = I if len(I) == 2 else O
        k, kk = pair
        if is_exit(B, g) or not is_exit(Y, g):
            fail += 1
            continue
        if abs(B[k][kk]) >= 2:
            forks += 1
            if not is_fork(Y, g):
                fail += 1
        else:
            preforks += 1
            if is_fork(Y, g) or not is_prefork(Y, g):
                fail += 1
    out.append(f"Lemma 22.1: {tested} random quivers with (D1)-(D3): {fail} failures "
               f"({forks} with |b_kk'| >= 2, all forks; {preforks} with |b_kk'| <= 1, all pre-forks not forks)")

    # Lemma 22.1': some |v_i| <= 1 => (mu_g X, g) is not an exit
    tested = fail = 0
    while tested < 20000:
        g = rng.randrange(N)
        W = rng.choice([3, 8, 50])
        others = [i for i in range(N) if i != g]
        small = rng.choice(others)
        B = rand_with_column(g, rng, lambda i: rng.randint(-1, 1) if i == small else rng.randint(-W, W),
                             lambda: rng.randint(-W, W))
        tested += 1
        if is_exit(mutate(B, g), g):
            fail += 1
    out.append(f"Lemma 22.1': {tested} random quivers with an entry |v_i| <= 1: (mu_g X, g) an exit in {fail}")

    # Lemma 22.2: mu_k X = (mu_k T, E v)
    tested = fail = 0
    for _ in range(20000):
        g = rng.randrange(N)
        W = rng.choice([3, 10, 100])
        B = from6([rng.randint(-W, W) for _ in range(6)])
        k = rng.choice([i for i in range(N) if i != g])
        Y = mutate(B, k)
        eps = 1 if B[k][g] > 0 else -1
        for j in range(N):
            if j in (g, k):
                continue
            pred = B[j][g] + max(eps * B[j][k], 0) * B[k][g]
            if Y[j][g] != pred:
                fail += 1
        if Y[k][g] != -B[k][g]:
            fail += 1
        tested += 1
    out.append(f"Lemma 22.2: {tested} random steps inside T: {fail} entries differ from E v")

    # Lemma 22.3(1): |Pf| = |<v, kappa(T)>|, and Pf changes sign at each mutation
    tested = fail = signfail = 0
    for _ in range(20000):
        W = rng.choice([3, 10, 100])
        B = from6([rng.randint(-W, W) for _ in range(6)])
        g = rng.randrange(N)
        a, b, c = [i for i in range(N) if i != g]
        v = [B[a][g], B[b][g], B[c][g]]
        kap = [B[b][c], -B[a][c], B[a][b]]
        if abs(pf(B)) != abs(sum(x * y for x, y in zip(v, kap))):
            fail += 1
        k = rng.randrange(N)
        if pf(mutate(B, k)) != -pf(B):
            signfail += 1
        tested += 1
    out.append(f"Lemma 22.3(1): {tested} random quivers: |Pf| != |<v,kappa>| in {fail}; "
               f"Pf(mu_k B) != -Pf(B) in {signfail}")

    # Lemma 22.3(2): Coxeter period, characteristic polynomial (x+1)(x^2-(C-2)x+1)
    tested = fail = 0
    for _ in range(2000):
        p, q, r = rng.randint(0, 12), rng.randint(0, 12), rng.randint(0, 12)
        # T on vertices 1, 2, 3 with 1 -> 2 (p), 1 -> 3 (q), 2 -> 3 (r); g = 0
        T = [[0] * N for _ in range(N)]
        for (i, j), x in (((1, 2), p), ((1, 3), q), ((2, 3), r)):
            T[i][j] = x
            T[j][i] = -x
        # monodromy on v = (v1, v2, v3) when every mutated entry is positive:
        # build M column by column from the linear rule of Lemma 22.2 with eps = +
        def period(Bm, v):
            Bm = [row[:] for row in Bm]
            v = list(v)
            done = set()
            for _ in range(3):
                # a sink of the current triangle on {1,2,3} not yet mutated (unique when T is
                # connected; with an isolated vertex there are two, and each vertex is taken once)
                sink = [k for k in (1, 2, 3) if k not in done and all(Bm[k][j] <= 0 for j in (1, 2, 3) if j != k)]
                if not sink:
                    return None, None
                k = sink[0]
                done.add(k)
                vk = v[k - 1]
                nv = list(v)
                nv[k - 1] = -vk
                for j in (1, 2, 3):
                    if j != k:
                        nv[j - 1] = v[j - 1] + max(Bm[j][k], 0) * vk
                v = nv
                Bm = mutate(Bm, k)
            return Bm, v
        Bend, _ = period(T, [1, 0, 0])
        if Bend is None or [Bend[i][j] for i in (1, 2, 3) for j in (1, 2, 3)] != [T[i][j] for i in (1, 2, 3) for j in (1, 2, 3)]:
            fail += 1
            continue
        M = [[0] * 3 for _ in range(3)]
        for col in range(3):
            e = [0, 0, 0]
            e[col] = 1
            _, w = period(T, e)
            for row in range(3):
                M[row][col] = w[row]
        tr = M[0][0] + M[1][1] + M[2][2]
        m2 = (M[0][0] * M[1][1] - M[0][1] * M[1][0] + M[0][0] * M[2][2] - M[0][2] * M[2][0]
              + M[1][1] * M[2][2] - M[1][2] * M[2][1])
        det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
               - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
               + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
        C = p * p + q * q + r * r + p * q * r
        # (x+1)(x^2-(C-2)x+1) = x^3 - (C-3) x^2 - (C-3) x + 1 ... expand:
        # x^3 + (1-(C-2)) x^2 + (1-(C-2)) x + 1
        want_tr, want_m2, want_det = (C - 2) - 1, 1 - (C - 2), -1
        if (tr, m2, det) != (want_tr, want_m2, want_det):
            fail += 1
        tested += 1
    out.append(f"Lemma 22.3(2): {tested} acyclic triangles (weights <= 12): three sink steps return T; "
               f"char. poly of M != (x+1)(x^2-(C-2)x+1) in {fail}")

    # Lemma 22.6: Markov triangle, (mu_k X, k) never an exit
    tested = fail = 0
    for _ in range(60000):
        g = rng.randrange(N)
        a, b, c = [i for i in range(N) if i != g]
        W = rng.choice([1, 3, 10, 1000])
        B = [[0] * N for _ in range(N)]
        for (i, j) in ((a, b), (b, c), (c, a)):
            B[i][j] = 2
            B[j][i] = -2
        for i in (a, b, c):
            x = rng.randint(-W, W)
            B[i][g] = x
            B[g][i] = -x
        k = rng.choice([a, b, c])
        if is_exit(mutate(B, k), k):
            fail += 1
        tested += 1
    out.append(f"Lemma 22.6: {tested} random quivers with a Markov triangle: (mu_k X, k) an exit in {fail}")

    # Proposition 22.4: mutation-cyclic triangles (x, y, z >= 2, C <= 4), weights <= 200
    flat2 = []
    flat3 = []
    for x in range(2, 201):
        for y in range(x, 201):
            for z in range(y, 201):
                if x * x + y * y + z * z - x * y * z > 4:
                    continue
                nflat = (y * z == 2 * x) + (x * z == 2 * y) + (x * y == 2 * z)
                if nflat >= 2:
                    flat2.append((x, y, z))
                if nflat >= 3:
                    flat3.append((x, y, z))
    bad = [t for t in flat2 if not (t[0] == 2 and t[1] == t[2])]
    out.append(f"Prop. 22.4: cyclic triangles with weights in [2, 200] and C <= 4 having >= 2 flat steps: "
               f"{len(flat2)} (all of shape (2, m, m): {not bad}); with 3 flat steps: {flat3}")
    print("\n".join(out))


# ---------------------------------------------------------------- markov

def column_quiver(v):
    """Markov triangle 1 -> 2 -> 3 -> 1 (two arrows each), column v_i = b_i0."""
    B = [[0] * N for _ in range(N)]
    for (i, j) in ((1, 2), (2, 3), (3, 1)):
        B[i][j] = 2
        B[j][i] = -2
    for i, x in zip((1, 2, 3), v):
        B[i][0] = x
        B[0][i] = -x
    return B


def cut(start, L, cap=None):
    """Exhaustive cut of V'(start) at level L: allowed steps, quivers of level <= L,
    up to relabelling (labelled representatives are kept)."""
    seen = {canon(start): start}
    stack = [start]
    while stack:
        B = stack.pop()
        for m in range(N):
            Y = mutate(B, m)
            if level(Y) > L:
                continue
            if not allowed(B, m):
                continue
            key = canon(Y)
            if key not in seen:
                seen[key] = Y
                stack.append(Y)
                if cap and len(seen) > cap:
                    return seen, False
    return seen, True


def markov_triangles(B):
    cnt = 0
    for tri in itertools.combinations(range(N), 3):
        a, b, c = tri
        ws = [B[a][b], B[b][c], B[c][a]]
        if all(w == 2 for w in ws) or all(w == -2 for w in ws):
            cnt += 1
    return cnt


def cmd_markov(levels=(25, 50, 100, 200)):
    out = []
    X0 = from6((-1, 0, 0, 2, -2, 2))
    out.append(f"X0 = {to6(X0)}; column at 0 = {[X0[i][0] for i in (1, 2, 3)]}")
    light = [(i, j) for i, j in PAIRS if abs(X0[i][j]) < 2]
    out.append(f"light pairs of X0: {light} (a far region allows at most one)")
    exits = [m for m in range(N) if is_exit(X0, m)]
    out.append(f"(X0, m) is an exit for m in {exits}")

    # v(z, n) is reached by allowed steps: replay the moves of the proof with real mutations
    # and check that every step is allowed.  Moves on the column (v1, v2, v3):
    def step1(B):
        """mutate at vertex 1, then exchange the names 2 and 3"""
        Y = mutate(B, 1)
        P = [0, 1, 3, 2]
        return [[Y[P[i]][P[j]] for j in range(N)] for i in range(N)], allowed(B, 1)

    def rot(B):
        """relabel so that (v1, v2, v3) -> (v2, v3, v1): new vertex 1 is old 2, etc."""
        P = [0, 2, 3, 1]
        return [[B[P[i]][P[j]] for j in range(N)] for i in range(N)]

    def col(B):
        return tuple(B[i][0] for i in (1, 2, 3))

    nsteps = 0
    notallowed = 0
    reached = {}
    Zmax, Nmax = 40, 40
    # (a, 0, 1-a) for a = 1 .. Zmax
    B = X0
    ladder = {1: B}
    for a in range(1, Zmax):
        assert col(B) == (a, 0, 1 - a), col(B)
        B2, ok = step1(B)
        nsteps += 1
        notallowed += (not ok)
        # B2 has column (-a, 1+a, 0); rotate to (1+a, 0, -a)
        B2 = rot(B2)
        assert col(B2) == (1 + a, 0, -a), col(B2)
        B = B2
        ladder[a + 1] = B
    for z in range(2, Zmax + 1):
        B = ladder[z]                         # column (z, 0, 1 - z)
        B = rot(rot(B))                       # (0, 1 - z, z)... rotate twice: (1-z, z, 0)? fix below
        # we want the zero entry at vertex 1: rotations of (z, 0, 1-z) are (0, 1-z, z) and (1-z, z, 0)
        while col(B)[0] != 0:
            B = rot(B)
        assert col(B) == (0, 1 - z, z), col(B)
        B, ok = step1(B)                      # (0, z, 1 - z)
        nsteps += 1
        notallowed += (not ok)
        while col(B) != (1 - z, 0, z):
            B = rot(B)
        for n in range(0, Nmax + 1):
            want = (-(z - 1) * (n + 1), (z - 1) * n, z)
            assert col(B) == want, (z, n, col(B), want)
            assert markov_triangles(B) >= 1
            reached[(z, n)] = B
            if n == Nmax:
                break
            B, ok = step1(B)                  # step at the negative entry (vertex 1)
            nsteps += 1
            notallowed += (not ok)
            while col(B)[0] >= 0 or col(B)[2] != z:
                B = rot(B)
    out.append(f"v(z, n) for 2 <= z <= {Zmax}, 0 <= n <= {Nmax}: reached by {nsteps} real mutations, "
               f"{notallowed} of them not allowed")
    keys = {}
    for (z, n), B in reached.items():
        if z >= 3 and n >= 1:
            keys.setdefault(canon(B), []).append((z, n))
            assert level(B) == (z - 1) * (n + 1)
    dup = [v for v in keys.values() if len(v) > 1]
    out.append(f"z >= 3, n >= 1: {sum(len(v) for v in keys.values())} quivers, {len(keys)} classes "
               f"up to relabelling, duplicates {dup[:3]}; level = (z-1)(n+1) in all")
    # the count bound of Theorem 22.7(3)
    import math
    for L in (100, 1000, 10000, 100000):
        cntp = sum(L // m - 1 for m in range(2, L // 2 + 1))
        out.append(f"  L = {L}: pairs (z >= 3, n >= 1) with (z-1)(n+1) <= L: {cntp}; "
                   f"L ln L - 3L = {L * math.log(L) - 3 * L:.0f}")
    # exhaustive cuts
    for L in levels:
        seen, complete = cut(X0, L)
        mk = sum(1 for B in seen.values() if markov_triangles(B) >= 1)
        out.append(f"cut of V'(X0) at level {L}: {len(seen)} quivers ({'complete' if complete else 'capped'}), "
                   f"{mk} with a Markov triangle")
        print(out[-1], flush=True)
    print("\n".join(out))


# ---------------------------------------------------------------- side

def cmd_side(K=12):
    out = []
    x = from6((8, 0, -7, -7, 2, 1))
    out.append(f"x = {to6(x)}: light pairs {[(i, j) for i, j in PAIRS if abs(x[i][j]) < 2]}")
    A = [2, 49]
    while len(A) < K + 4:
        A.append(57 * A[-1] - A[-2])
    # Y_k = (A_{k+1}, 0, -57, -1, A_k, 0), with A_0 = 49 = A[1]
    def Y(k):
        return from6((A[k + 2], 0, -57, -1, A[k + 1], 0))
    for k in range(K):
        Yk, Yk1 = Y(k), Y(k + 1)
        hits = [m for m in range(N) if canon(mutate(Yk, m)) == canon(Yk1)]
        al = [allowed(Yk, m) for m in hits]
        out.append(f"k = {k}: A_k = {A[k + 1]}, Y_k -> Y_(k+1) by mutation at {hits}, allowed {al}")
    # is Y_0 in V'(x)?  search allowed steps from x up to level 3 * A_1
    seen, complete = cut(x, 3000)
    out.append(f"cut of V'(x) at level 3000: {len(seen)} quivers ({'complete' if complete else 'capped'}); "
               f"contains Y_0: {canon(Y(0)) in seen}")
    # side tube at Y_k: walk of allowed steps at vertices 0, 1, 2, never repeating a vertex
    for k in range(4):
        B = Y(k)
        a = A[k + 2]
        trail = []
        prev = None
        for s in range(12):
            opts = []
            for m in (0, 1, 2):
                if m == prev:
                    continue
                if not allowed(B, m):
                    continue
                Z = mutate(B, m)
                opts.append((sum(abs(Z[i][3]) for i in range(3)), m, Z))
            if not opts:
                trail.append("stuck")
                break
            # the side tube grows: take the step that increases the column of vertex 3 most
            opts.sort(key=lambda t: -t[0])
            _, m, B = opts[0]
            prev = m
            tri = sorted(abs(B[i][j]) for i, j in ((0, 1), (0, 2), (1, 2)))
            trail.append((m, tuple(tri), max(abs(B[i][3]) for i in range(3))))
        out.append(f"side tube from Y_{k} (a = {a}, a^2 - 1 = {a * a - 1}):")
        last = None
        for t in trail:
            if t == "stuck":
                out.append("   stuck")
                break
            m, tri, top = t
            ratio = f"{Fraction(top, last):.4g}" if last else ""
            out.append(f"   step at {m}: triangle {tri}, max |column of 3| = {top}  {ratio}")
            last = top
    print("\n".join(out))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lemmas"
    if cmd == "lemmas":
        cmd_lemmas()
    elif cmd == "markov":
        lv = tuple(int(s) for s in sys.argv[2:]) or (25, 50, 100, 200)
        cmd_markov(lv)
    elif cmd == "side":
        cmd_side()
