"""Review of note 20 (note 23): checks of Lemma 20.1, Proposition 20.2,
Proposition 20.3, the values of H(a) and Corollary 20.5, the region table of section 5.2,
and section 6.2.  Own code; see review23_n20_lib.py.  Python integers throughout.

Usage: python -I review23_n20_checks.py {lemma|lines|spiral|hvalues|region|forkless|all} [options]
"""
import fractions
import itertools
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
from review23_n20_lib import (mutate, height, is_fork, canon, Q_matrix, W_matrix, H_of,
                                from_upper, perms)  # noqa: E402


# ------------------------------------------------------------------ helpers

def canon_fast(B):
    """Invariant-sorted canonical form (lexicographic max over orders compatible with the
    per-vertex key (out-weight, in-weight, largest signed entry))."""
    n = len(B)
    inv = []
    for v in range(n):
        pos = sum(B[v][j] for j in range(n) if B[v][j] > 0)
        neg = -sum(B[v][j] for j in range(n) if B[v][j] < 0)
        mx = max(B[v][j] for j in range(n) if j != v)
        inv.append((pos, neg, mx))
    order = sorted(range(n), key=lambda v: inv[v], reverse=True)
    groups = []
    for v in order:
        if groups and inv[groups[-1][0]] == inv[v]:
            groups[-1].append(v)
        else:
            groups.append([v])
    best = None
    for choice in itertools.product(*[itertools.permutations(g) for g in groups]):
        t = [v for g in choice for v in g]
        tup = tuple(B[t[i]][t[j]] for i in range(n) for j in range(i + 1, n))
        if best is None or tup > best:
            best = tup
    return best


class Frame(dict):
    def swap(self, u, v):
        self[u], self[v] = self[v], self[u]


def state(B, f):
    return (B[f['p']][f['x']], B[f['q']][f['x']], B[f['x']][f['r']], B[f['x']][f['s']])


def four_part_is_W(B, f, m, j):
    W = W_matrix(m, j)
    lab = [f['p'], f['q'], f['r'], f['s']]
    return all(B[lab[i]][lab[k]] == W[i][k] for i in range(4) for k in range(4))


def build_route(a):
    """First half of the route of Theorem 18.4, built by integer mutation.
    Returns a list of records (turns_done, position, B, frame) and the table check."""
    m = 2 * a + 1
    c = (4 * a - 1) * (a - 1)
    tstar = c // 2 + 2 if a % 2 else (c + 3) // 2
    B = Q_matrix(a)
    f = Frame(x=0, p=4, q=1, r=2, s=3)
    pos = a + 1
    assert four_part_is_W(B, f, m, pos)
    recs = [(0, pos, B, Frame(f))]
    for _ in range(a):
        B = mutate(B, f['p'])
        f.swap('p', 'q')
        pos += 1
        recs.append((0, pos, B, Frame(f)))
    turns = 0
    nturns_total = 2 * a + 1 + tstar - 1   # turns made in the first half (lines need rounds up to T)
    table_bad = 0
    u = lambda i: a - 2 + i * (2 * a - 1)
    while True:
        # before turn n = turns + 1, at position m
        n = turns + 1
        A, Bq, U, V = state(B, f)
        if n == 1:
            exp = (2 * a * a - a + 1, -(2 * a * a - 3 * a + 3), a - 2, a + 1)
        elif n == 2:
            exp = (4 * a * a + 1, -(4 * a * a - a + 1), a + 1, -(a - 2))
        elif n <= 2 * a + 1:
            k = n - 2
            exp = (4 * a * a + 1 - k * m, -(4 * a * a + 2 - k * m), -u(k - 1), u(k - 2))
        else:
            t = n - 2 * a - 1
            exp = (2 * a - 3 + (t - 1) * m, -(2 * a - 4 + (t - 1) * m), -(c - 2 * (t - 1)), c + 2 - 2 * (t - 1))
        if (A, Bq, U, V) != exp:
            table_bad += 1
        if turns == nturns_total:
            break
        B = mutate(B, f['r'])
        f.swap('r', 's')
        turns += 1
        pos = 0
        assert four_part_is_W(B, f, m, 0)
        recs.append((turns, pos, B, Frame(f)))
        for _ in range(m):
            B = mutate(B, f['p'])
            f.swap('p', 'q')
            pos += 1
            assert four_part_is_W(B, f, m, pos)
            recs.append((turns, pos, B, Frame(f)))
    return recs, table_bad, tstar


def member(B, H):
    return height(B) < H and not is_fork(B)


# ------------------------------------------------------------------ item 1

def cmd_lemma(rng, ntests=200000):
    bad = 0
    tested = [0, 0]
    for _ in range(ntests):
        n = rng.choice([3, 4, 5, 6])
        ups = [rng.randint(-40, 40) for _ in range(n * (n - 1) // 2)]
        B = from_upper(n, ups)
        p, q = 0, 1
        B[q][p], B[p][q] = 2, -2
        e = rng.randrange(2, n)
        L = rng.randint(1, 3000)
        case = rng.randrange(2)
        if case == 0:
            Ae = rng.randint(1, 80)
            Be = -rng.randint(1, 80)
        else:
            Ae = -rng.randint(1, 80)
            Be = rng.randint(1, 80)
        B[p][e], B[e][p] = Ae, -Ae
        B[q][e], B[e][q] = Be, -Be
        C = mutate(B, e)
        h = height(C)
        if case == 0:
            tested[0] += 1
            if C[p][q] != -2 + Ae * (-Be):
                bad += 1
            if Ae * abs(Be) >= L + 2 and h < L:
                bad += 1
        else:
            tested[1] += 1
            if C[q][p] != 2 + abs(Ae) * Be or h < abs(Ae) * Be + 2:
                bad += 1
    print('Lemma 20.1: %d random quivers on 3 to 6 vertices (%d of case 1, %d of case 2): %d failures'
          % (ntests, tested[0], tested[1], bad))


# ------------------------------------------------------------------ item 2

def lines_for(a, lemma_count=False, verbose=False, collect=None):
    m = 2 * a + 1
    c = (4 * a - 1) * (a - 1)
    H = H_of(a)
    recs, table_bad, tstar = build_route(a)
    T = tstar - 1
    idx = {(r[0], r[1]): r for r in recs}
    out = {'a': a, 'H': H, 'T': T, 'table_bad': table_bad}
    # backward lines: position 0 after turn 2a+1+t
    bl = []
    closed_bad = 0
    forks_in_closed_range = 0
    lemma_ok = 0
    bl_total = 0
    for t in range(1, T + 1):
        turns, pos, B, f = idx[(2 * a + 1 + t, 0)]
        f = Frame(f)
        A, Bq, U, V = state(B, f)
        At = 2 * a - 3 + (t - 1) * m
        if (A, Bq, U, V) != (At, -(At - 1), -(c - 2 * t), c - 2 * t + 2):
            closed_bad += 1
        k = 0
        while True:
            B = mutate(B, f['q'])
            f.swap('p', 'q')
            k += 1
            if 2 <= k <= A:
                p_, q_, r_, s_, x_ = f['p'], f['q'], f['r'], f['s'], f['x']
                ok = (B[q_][p_] == 2 and (B[p_][r_], B[q_][r_]) == (m + k, -(m + k + 1))
                      and (B[p_][s_], B[q_][s_]) == (k - 2, -(k - 1))
                      and (B[p_][x_], B[q_][x_]) == (A - k, -(A - k - 1))
                      and B[r_][s_] == m - 1 and B[x_][r_] == U and B[x_][s_] == V + A - 1)
                if not ok:
                    closed_bad += 1
                if is_fork(B):
                    forks_in_closed_range += 1
            h = height(B)
            if h >= H:
                end = 'high'
                break
            if is_fork(B):
                end = 'fork'
                break
            bl_total += 1
            if collect is not None:
                collect.append(('BL', canon_fast(B)))
            if lemma_count:
                good = True
                for e in ('r', 's', 'x'):
                    Ae, Be = B[f['p']][f[e]], B[f['q']][f[e]]
                    if Ae > 0 > Be and Ae * (-Be) >= H + 2:
                        continue
                    if Ae < 0 < Be and (-Ae) * Be + 2 >= H:
                        continue
                    good = False
                    break
                if good:
                    lemma_ok += 1
                    for e in ('r', 's', 'x'):
                        assert height(mutate(B, f[e])) >= H
        bl.append((t, A, k - 1, end))
    fl = []
    fl_total = 0
    for kp in range(1, 2 * a):
        turns, pos, B, f = idx[(2 + kp - 1, m)]
        f = Frame(f)
        A, Bq, U, V = state(B, f)
        u = lambda i: a - 2 + i * (2 * a - 1)
        Ak = 4 * a * a + 1 - kp * m
        if (A, Bq, U, V) != (Ak, -(Ak + 1), -u(kp - 1), u(kp - 2)):
            closed_bad += 1
        k = 0
        while True:
            B = mutate(B, f['p'])
            f.swap('p', 'q')
            k += 1
            if 2 <= k <= A + 1:
                p_, q_, r_, s_, x_ = f['p'], f['q'], f['r'], f['s'], f['x']
                ok = (B[q_][p_] == 2 and (B[p_][r_], B[q_][r_]) == (k - 2, -(k - 3))
                      and (B[p_][s_], B[q_][s_]) == (m + k, -(m + k - 1))
                      and (B[p_][x_], B[q_][x_]) == (A - k, -(A - k + 1))
                      and B[r_][s_] == m - 1 and B[x_][r_] == U - (A - 1) and B[x_][s_] == V)
                if not ok:
                    closed_bad += 1
                if is_fork(B):
                    forks_in_closed_range += 1
            h = height(B)
            if h >= H:
                end = 'high'
                break
            if is_fork(B):
                end = 'fork'
                break
            fl_total += 1
            if collect is not None:
                collect.append(('FL', canon_fast(B)))
        fl.append((kp, A, k - 1, end))
    out.update(bl=bl, fl=fl, bl_total=bl_total, fl_total=fl_total, closed_bad=closed_bad,
               forks_in_closed_range=forks_in_closed_range, lemma_ok=lemma_ok)
    return out


def cmd_distinct(alist):
    for a in alist:
        H = H_of(a)
        col = []
        r = lines_for(a, collect=col)
        recs, _, _ = build_route(a)
        route = set(canon_fast(B) for (_, _, B, _) in recs if height(B) < H)
        bl = [k for (t, k) in col if t == 'BL']
        fl = [k for (t, k) in col if t == 'FL']
        print('a=%d: backward-line quivers %d, distinct classes %d; forward-line quivers %d, distinct %d; '
              'line classes also on the first half of the route %d; backward and forward lines sharing a class %d'
              % (a, len(bl), len(set(bl)), len(fl), len(set(fl)), len((set(bl) | set(fl)) & route),
                 len(set(bl) & set(fl))))
        sys.stdout.flush()


def cmd_exits(a):
    """Backward lines of S4 (t = 1..T, and the line of the bottom round, after turn 2a+1): members whose
    three exits at x, r, s all have height >= H."""
    H = H_of(a)
    recs, _, tstar = build_route(a)
    T = tstar - 1
    idx = {(r[0], r[1]): r for r in recs}
    tot = hhh = 0
    for t in range(0, T + 1):
        turns, pos, B, f = idx[(2 * a + 1 + t, 0)]
        f = Frame(f)
        while True:
            B = mutate(B, f['q'])
            f.swap('p', 'q')
            if height(B) >= H or is_fork(B):
                break
            tot += 1
            if all(height(mutate(B, f[e])) >= H for e in ('x', 'r', 's')):
                hhh += 1
    print('a=%d: members of the backward lines of S4 (bottom round included): %d; with all three exits at x, r, s '
          'of height >= H: %d' % (a, tot, hhh))


def cmd_lines(amin, amax, lemma_upto):
    print('# Proposition 20.2: route of Theorem 18.4 rebuilt by integer mutation; lines continued until '
          'the first quiver that is a fork or has height >= H(a).')
    for a in range(amin, amax + 1):
        r = lines_for(a, lemma_count=(a <= lemma_upto))
        m = 2 * a + 1
        T = r['T']
        bl_dev = [(t, A, L - (A + 3), end) for (t, A, L, end) in r['bl'] if L != A + 3 or end != 'fork']
        fl_dev = [(k, A, L - (A + 4), end) for (k, A, L, end) in r['fl'] if L != A + 4 or end != 'fork']
        f_bl = 2 * a * T + m * T * (T - 1) // 2
        f_fl = (2 * a - 1) * (2 * a * a - a + 5)
        print('a=%d H=%d: table of Thm 18.4 mismatches %d; T=%d backward lines, %d quivers (formula 2aT+mT(T-1)/2 = %d, '
              'difference %d); %d forward lines, %d quivers (formula (2a-1)(2a^2-a+5) = %d); closed-form mismatches %d; '
              'forks inside the closed-form ranges %d' % (
                  a, r['H'], r['table_bad'], T, r['bl_total'], f_bl, f_bl - r['bl_total'], len(r['fl']), r['fl_total'],
                  f_fl, r['closed_bad'], r['forks_in_closed_range']))
        print('    backward lines not of length A+3 ending at a fork (t, A, length-(A+3), end): %s' % bl_dev)
        print('    forward lines not of length A+4 ending at a fork (k, A, length-(A+4), end): %s' % fl_dev)
        if a <= lemma_upto:
            print('    backward-line quivers whose three exits at r, s, x are high by Lemma 20.1 alone: %d of %d (%.2f %%)'
                  % (r['lemma_ok'], r['bl_total'], 100.0 * r['lemma_ok'] / r['bl_total']))
        sys.stdout.flush()


# ------------------------------------------------------------------ item 3

TABLE = [  # (vertex, b_rk before, entries of r after (b_rp, b_rq, b_rs), triangle after (b_pq, b_ps, b_qs))
    ('q', lambda A, Bt, G: Bt, lambda A, Bt, G: (2 * Bt - A, -Bt, Bt - G), (2, 0, -1)),
    ('p', lambda A, Bt, G: 2 * Bt - A, lambda A, Bt, G: (A - 2 * Bt, 3 * Bt - 2 * A, Bt - G), (-2, 0, -1)),
    ('q', lambda A, Bt, G: 3 * Bt - 2 * A, lambda A, Bt, G: (4 * Bt - 3 * A, 2 * A - 3 * Bt, Bt - G), (2, -2, 1)),
    ('s', lambda A, Bt, G: Bt - G, lambda A, Bt, G: (6 * Bt - 3 * A - 2 * G, 2 * A - 3 * Bt, G - Bt), (0, 2, -1)),
    ('p', lambda A, Bt, G: 6 * Bt - 3 * A - 2 * G,
     lambda A, Bt, G: (-(6 * Bt - 3 * A - 2 * G), 2 * A - 3 * Bt, 11 * Bt - 6 * A - 3 * G), (0, -2, -1)),
    ('s', lambda A, Bt, G: 11 * Bt - 6 * A - 3 * G,
     lambda A, Bt, G: (16 * Bt - 9 * A - 4 * G, 8 * Bt - 4 * A - 3 * G, -(11 * Bt - 6 * A - 3 * G)), (0, 2, 1)),
    ('p', lambda A, Bt, G: 16 * Bt - 9 * A - 4 * G,
     lambda A, Bt, G: (-(16 * Bt - 9 * A - 4 * G), 8 * Bt - 4 * A - 3 * G, 21 * Bt - 12 * A - 5 * G), (0, -2, 1)),
    ('s', lambda A, Bt, G: 21 * Bt - 12 * A - 5 * G,
     lambda A, Bt, G: (26 * Bt - 15 * A - 6 * G, 8 * Bt - 4 * A - 3 * G, -(21 * Bt - 12 * A - 5 * G)), (-2, 2, -1)),
    ('q', lambda A, Bt, G: 8 * Bt - 4 * A - 3 * G,
     lambda A, Bt, G: (42 * Bt - 23 * A - 12 * G, -(8 * Bt - 4 * A - 3 * G), -(21 * Bt - 12 * A - 5 * G)), (2, 0, 1)),
    ('p', lambda A, Bt, G: 42 * Bt - 23 * A - 12 * G,
     lambda A, Bt, G: (-(42 * Bt - 23 * A - 12 * G), 76 * Bt - 42 * A - 21 * G, -(21 * Bt - 12 * A - 5 * G)), (-2, 0, 1)),
]
LAB = {'p': 0, 'q': 1, 'r': 2, 's': 3}
WORD = 'qpqspspsqp'


def spiral_quiver(al, be, ga):
    B = [[0] * 4 for _ in range(4)]

    def put(i, k, v):
        B[i][k] = v
        B[k][i] = -v
    put(1, 0, 2)      # two arrows q -> p
    put(1, 3, 1)      # one arrow q -> s
    put(2, 0, -al)    # b_rp = -alpha
    put(2, 1, be)     # b_rq = beta
    put(2, 3, -ga)    # b_rs = -gamma
    return B


def det3(M):
    return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
            + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))


def cmd_spiral(rng, ntriples=20000):
    bad_table = bad_pos = bad_cone = bad_fork = 0
    nsteps = 0
    min_ratio = None
    for it in range(ntriples):
        be = rng.randint(1, 10**6) if it % 2 else rng.randint(1, 60)
        al = rng.randint(0, be)
        ga = rng.randint(0, be // 2)
        B = spiral_quiver(al, be, ga)
        for step, (v, before, after, tri) in enumerate(TABLE):
            k = LAB[v]
            if B[2][k] != before(al, be, ga) or B[2][k] <= 0:
                bad_pos += 1
            B = mutate(B, k)
            nsteps += 1
            if (B[2][0], B[2][1], B[2][3]) != after(al, be, ga) or (B[0][1], B[0][3], B[1][3]) != tri:
                bad_table += 1
            if is_fork(B) or min(abs(B[0][1]), abs(B[0][3]), abs(B[1][3])) >= 2:
                bad_fork += 1
        a2, b2, g2 = -B[2][0], B[2][1], -B[2][3]
        if (a2, b2, g2) != (-23 * al + 42 * be - 12 * ga, -42 * al + 76 * be - 21 * ga, -12 * al + 21 * be - 5 * ga):
            bad_table += 1
        if not (b2 > 0 and 0 <= a2 <= b2 and 0 <= 2 * g2 <= b2 and 2 * b2 >= 47 * be):
            bad_cone += 1
        r = fractions.Fraction(b2, be)
        min_ratio = r if min_ratio is None or r < min_ratio else min_ratio
    print('Proposition 20.3: %d random triples in the cone (%d mutations): table mismatches %d, '
          'b_rk <= 0 before a mutation %d, statement (3) failures %d, quivers with all three p,q,s pairs >= 2 '
          'arrows or forks %d; least beta\'/beta seen %.4f' % (ntriples, nsteps, bad_table, bad_pos, bad_cone,
                                                               bad_fork, float(min_ratio)))
    # the four rays (vertices of the cone section beta = 2)
    for al, be, ga in [(0, 2, 0), (2, 2, 0), (0, 2, 1), (2, 2, 1)]:
        a2, b2, g2 = -23 * al + 42 * be - 12 * ga, -42 * al + 76 * be - 21 * ga, -12 * al + 21 * be - 5 * ga
        print('   ray (alpha, beta, gamma) = (%d, %d, %d) -> (%d, %d, %d), beta\'/beta = %s'
              % (al, be, ga, a2, b2, g2, fractions.Fraction(b2, be)))
    M = [[-23, 42, -12], [-42, 76, -21], [-12, 21, -5]]
    tr = M[0][0] + M[1][1] + M[2][2]
    s2 = sum(M[i][i] * M[j][j] - M[i][j] * M[j][i] for i in range(3) for j in range(i + 1, 3))
    print('   matrix: det %d, trace %d, sum of principal 2x2 minors %d -> char poly t^3 - %d t^2 + %d t - %d; '
          '(t-1)(t^2-47t+1) = t^3 - 48t^2 + 48t - 1; phi^8 = %.6f, (47+21*sqrt5)/2 = %.6f'
          % (det3(M), tr, s2, tr, s2, det3(M), ((1 + 5 ** 0.5) / 2) ** 8, (47 + 21 * 5 ** 0.5) / 2))
    # five vertices: from W_m(0) with the fifth vertex of a route quiver at position 0
    for a in (2, 3, 6, 12):
        m = 2 * a + 1
        recs, _, _ = build_route(a)
        seen = set()
        for (turns, pos, B0, f) in recs:
            if pos != 0 or turns not in (1, 2, 2 * a + 2, 2 * a + 10):
                continue
            B = [row[:] for row in B0]
            heights = []
            ok = True
            for rnd in range(4):
                for v in WORD:
                    B = mutate(B, f[v])
                    if is_fork(B):
                        ok = False
                    lab = [f['p'], f['q'], f['s']]
                    if min(abs(B[lab[0]][lab[1]]), abs(B[lab[0]][lab[2]]), abs(B[lab[1]][lab[2]])) >= 2:
                        ok = False
                heights.append(height(B))
                seen.add(canon_fast(B))
            print('   5 vertices, a=%d, route quiver at position 0 after turn %d: 4 rounds, heights %s, '
                  'no fork and a light pair among p,q,s throughout: %s' % (a, turns, heights, ok))
        print('   a=%d: %d distinct classes among these end-of-round quivers (expected 4 x number of starts)'
              % (a, len(seen)))
    # four vertices, from W_m(0): heights after every mutation, runs of five
    for a in (6, 96):
        m = 2 * a + 1
        B = W_matrix(m, 0)
        hs = [height(B)]
        for rnd in range(4):
            for v in WORD:
                B = mutate(B, LAB[v])
                hs.append(height(B))
        print('   4 vertices, a=%d, m=%d: heights along (q p q s p s p s q p)^4 from W_m(0): %s' % (a, m, hs[:26]))
        # runs: mutations 4..8, 9..13, ... (1-based); increments inside each run
        runs = []
        i = 3
        while i + 5 <= len(hs) - 1:
            seg = hs[i:i + 6]
            runs.append([seg[j + 1] - seg[j] for j in range(5)])
            i += 5
        print('     increments inside the runs of five after q p q: %s' % runs)
        d = [r[-1] for r in runs]
        pred = [2 * m + 3, 15 * m + 16]
        while len(pred) < len(d):
            pred.append(7 * pred[-1] - pred[-2] + (m - 4))
        print('     last increment of each run: %s; claimed d_1 = 2m+3, d_2 = 15m+16, d_{i+1} = 7d_i - d_{i-1} + (m-4): %s'
              % (d, pred))


# ------------------------------------------------------------------ item 4 (formulas)

def cmd_hvalues():
    bad = 0
    for a in range(2, 200):
        H = H_of(a)
        recs = None
        w = a + 1
        rhs = 4 * w**3 - 15 * w**2 + 19 * w - 11
        if 3 <= w <= 65 and H < rhs:
            bad += 1
        # closed forms of Corollary 18.6
        if w % 2 == 0:
            alt = fractions.Fraction(4 * w**3 - 15 * w**2) + fractions.Fraction(41 * w - 20, 2)
        else:
            alt = fractions.Fraction(4 * w**3 - 15 * w**2) + fractions.Fraction(39 * w - 21, 2)
        if alt != H:
            bad += 1
    print('H(w-1) >= 4w^3-15w^2+19w-11 for 3 <= w <= 65 and H(w-1) = the closed forms of Corollary 18.6 for w < 201: '
          '%d failures' % bad)
    print('   H(w-1) - (4w^3-15w^2+19w-11) = (3w+2)/2 for even w, (w+1)/2 for odd w (by the closed forms)')
    print('   a     H(a)   H/w^3  H/w^2.5   (A_1 from c: odd a: 2a-3+(c/2+1)m+1, even a: 2a-3+((c+1)/2)m)')
    for a in (22, 26, 32, 40, 48, 56, 64):
        w = a + 1
        m = 2 * a + 1
        c = (4 * a - 1) * (a - 1)
        A1 = 2 * a - 3 + (c // 2 + 1) * m + 1 if a % 2 else 2 * a - 3 + ((c + 1) // 2) * m
        print('   %d  %d  %.2f  %.1f  %d' % (a, H_of(a), H_of(a) / w**3, H_of(a) / w**2.5, A1))
    a = 64
    print('   H(64) < 2^20: %s' % (H_of(64) < 2**20))


# ------------------------------------------------------------------ item 5

def cmd_region(alist):
    print('# section 5.2: route quivers in the rounds from the one after turn 2a+1 on, with U < 0; mu_r member '
          '(height < H, not a fork) against A + (m-j)|U| < H')
    for a in alist:
        m = 2 * a + 1
        H = H_of(a)
        recs, _, tstar = build_route(a)
        tab = {}
        for strict in (False, True):
            n = mem_in = high_out = other = forks = 0
            for (turns, pos, B, f) in recs:
                if turns < 2 * a + 1:
                    continue
                if strict and turns == 2 * a + 1 and pos <= 3:
                    continue
                A, Bq, U, V = state(B, f)
                if U >= 0:
                    continue
                n += 1
                C = mutate(B, f['r'])
                pred = A + (m - pos) * abs(U) < H
                if C[f['p']][f['x']] != A + (m - pos) * abs(U):
                    other += 1
                    continue
                if is_fork(C):
                    forks += 1
                    continue
                ism = height(C) < H
                if ism and pred:
                    mem_in += 1
                elif (not ism) and (not pred):
                    high_out += 1
                else:
                    other += 1
            tab[strict] = (n, mem_in, high_out, other, forks)
        print('a=%d H=%d: including the bottom round from position 0: %s; only after the bottom step: %s '
              '(route quivers, member & below, high & not below, other, forks)' % (a, H, tab[False], tab[True]))


# ------------------------------------------------------------------ item 6 (section 6.2)

def canon4(B):
    best = None
    for t in perms(4):
        tup = tuple(B[t[i]][t[j]] for i in range(4) for j in range(i + 1, 4))
        if best is None or tup > best:
            best = tup
    return best


def cmd_forkless(cases):
    print('# section 6.2: 4-vertex classes reached from the cycle W_m(j), 0 <= j <= m+1, through non-forks below the cap')
    for a, capname in cases:
        m = 2 * a + 1
        H = H_of(a)
        cap = {'4a2': 4 * a * a, 'H': H, '4H': 4 * H, '16H': 16 * H, '256H': 256 * H, 'H2': H * H}[capname]
        seeds = {}
        for j in range(0, m + 2):
            W = W_matrix(m, j)
            assert not is_fork(W) and height(W) < cap
            seeds[canon4(W)] = W
        dist = {k: 0 for k in seeds}
        rep = dict(seeds)
        frontier = list(seeds)
        d = 0
        while frontier:
            d += 1
            nxt = []
            for key in frontier:
                X = rep[key]
                for k in range(4):
                    Y = mutate(X, k)
                    if height(Y) >= cap or is_fork(Y):
                        continue
                    ky = canon4(Y)
                    if ky not in dist:
                        dist[ky] = d
                        rep[ky] = Y
                        nxt.append(ky)
            frontier = nxt
        off = [k for k in dist if k not in seeds]
        cyc0m = set(canon4(W_matrix(m, j)) for j in range(0, m + 1))
        off2 = [k for k in dist if k not in cyc0m]
        print('a=%d cap=%s=%d: %d cycle classes W_m(0..m+1), %d classes off them, largest distance %d; '
              'with the cycle taken as W_m(0..m): %d off it'
              % (a, capname, cap, len(seeds), len(off), max(dist[k] for k in off) if off else 0, len(off2)))


def main():
    cmd = sys.argv[1]
    rng = random.Random(71)
    if cmd in ('lemma', 'all'):
        cmd_lemma(rng)
    if cmd in ('spiral', 'all'):
        cmd_spiral(rng)
    if cmd in ('hvalues', 'all'):
        cmd_hvalues()
    if cmd == 'lines':
        cmd_lines(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    if cmd == 'distinct':
        cmd_distinct([int(x) for x in sys.argv[2:]])
    if cmd == 'exits':
        cmd_exits(int(sys.argv[2]))
    if cmd == 'region':
        cmd_region([int(x) for x in sys.argv[2:]])
    if cmd == 'forkless':
        cases = []
        for tok in sys.argv[2:]:
            a, cn = tok.split(':')
            cases.append((int(a), cn))
        cmd_forkless(cases)


if __name__ == '__main__':
    main()
