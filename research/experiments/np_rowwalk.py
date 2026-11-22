#!/usr/bin/env python
"""
np_rowwalk.py -- a fifth vertex over the bounce cycle of a 4-vertex quiver: barriers of order w^3 (note 18).

A 5-vertex quiver is written (row | R): vertex 0 = x carries the row (b01, b02, b03, b04), the vertices 1..4
carry the 4-vertex quiver R = (b12, b13, b14, b23, b24, b34).  If x is never mutated, R moves in its own mutation
class and the row follows linearly (Lemma 16.8).

The bounce cycle.  W_m(j), 0 <= j <= m, on the vertices p, q, r, s:
    q -> p  2,   s -> r  2,   column of r  (b_pr, b_qr) = (m - j, -(m + 1 - j)),   column of s  (b_ps, b_qs) = (j, 1 - j).
A step (mutate at p, exchange the names p, q) takes W_m(j) to W_m(j + 1); the turn (mutate at r in W_m(m), exchange
the names r, s) gives W_m(0).  R_a = (-(a+1), -a, 2, -2, -a, -(a+1)) is W_{2a+1}(a+1) with (p, q, r, s) = (4, 1, 2, 3).
The fifth vertex is recorded by (A, B, U, V) = (b_px, b_qx, b_xr, b_xs).

The family.  Q_a = (-(a-3), a-2, a+1, -(a+1) | R_a), of height w = a + 1, is joined to its opposite at
    H(a) = 4a^3 - 3a^2 + (5a - 1)/2  (a odd),   4a^3 - 3a^2 + (3a - 4)/2  (a even).

Subcommands (run from experiments/ with python -I; `np_corridor.py build` first):
  blocks   a route of least height, cut into runs of steps on one pair and single mutations
  cycle    the bounce cycle, its mirror symmetry and the two rules for the fifth vertex, against integer mutation
  family   Q_a for a range of a: the route, its closed forms, and the search on both sides of H(a)
  pycheck  the set of quivers below H(a) by a pure-Python search, against np_barrier
  scan     every row with entries <= k over R_a, up to the flip: escape levels
  walks    every row over R_a walked along the cycle by the rules, against a stored scan
  allbases every cycle W_m, position and fifth vertex of height <= w, walked by the rules
  phases   the walk of one row, cut into stretches of constant slopes
  shape    the rows with the slopes of Q_a over R_a: escape levels
  sample   random isolated n-vertex quivers of height w: escape levels
  recheck  the quivers over budget in a stored sample, again with a larger budget
"""
import argparse
import collections
import gzip
import itertools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import np_corridor as nc
from np_corridor import mut, ht, canon, upper, from_upper, neg


def sub4(B):
    return tuple(tuple(B[i][j] for j in (1, 2, 3, 4)) for i in (1, 2, 3, 4))


def runs(seq):
    """Cut a mutation word into maximal alternating runs on a pair (length >= 3) and single mutations."""
    out = []
    i = 0
    while i < len(seq):
        j = i
        while j + 2 < len(seq) and seq[j + 2] == seq[j] and seq[j + 1] != seq[j]:
            j += 1
        L = j + 2 - i if j > i else 1
        if L >= 3:
            out.append((i, L, (seq[i], seq[i + 1])))
            i += L
        else:
            out.append((i, 1, (seq[i],)))
            i += 1
    return out


def cmd_blocks(args):
    B = from_upper(args.quiver, 5)
    r, seq, mats = nc.labelled_route(B, args.cap, budget=args.budget)
    print("status %s, escape level %s, %d quivers searched" % (r["status"], r.get("iso"), r["popped"]))
    if seq is None:
        return
    print("mutations (%d): %s" % (len(seq), "".join(map(str, seq))))
    print("mutations at x: %d" % seq.count(0))
    print("start %s  end %s" % (upper(mats[0]), upper(mats[-1])))
    print("end is the opposite of the start: %s; isomorphic to the start: %s"
          % (canon(mats[-1]) == canon(neg(mats[0])), canon(mats[-1]) == canon(mats[0])))
    h4 = [ht(sub4(M)) for M in mats]
    hx = [max(abs(v) for v in M[0]) for M in mats]
    print("largest entry away from x: %d; largest entry at x: %d" % (max(h4), max(hx)))
    for (i, L, vs) in runs(seq):
        M = mats[i + L]
        tag = "(%s)^%d" % ("".join(map(str, vs)), L) if L > 1 else "%d" % vs[0]
        print("%5d %-10s ht %4d  x: %s   R: %s" % (i + L, tag, ht(M), " ".join("%5d" % v for v in M[0][1:]),
                                                     " ".join("%4d" % v for v in upper(sub4(M)))))


# ----------------------------------------------------------------------------- the bounce cycle and the rules
def Wm(m, j, lab=(4, 1, 2, 3), state=None):
    """W_m(j) on the vertices lab = (p, q, r, s) of 1..4, as a 5-vertex quiver with x = 0 given by state = (A, B, U, V).
    j = m + 1 is the quiver one step beyond W_m(m)."""
    p, q, r, s = lab
    B = [[0] * 5 for _ in range(5)]

    def setb(i, k, v):
        B[i][k] = v
        B[k][i] = -v
    setb(q, p, 2)
    setb(s, r, 2)
    setb(p, r, m - j)
    setb(q, r, -(m + 1 - j))
    setb(p, s, j)
    setb(q, s, 1 - j)
    if state:
        setb(p, 0, state[0])
        setb(q, 0, state[1])
        setb(0, r, state[2])
        setb(0, s, state[3])
    return tuple(tuple(row) for row in B)


def get_state(B, lab):
    p, q, r, s = lab
    return (B[p][0], B[q][0], B[0][r], B[0][s])


def rule_step(m, j, st):
    """The fifth vertex under the step from position j (0 <= j <= m) to j + 1 (rule S)."""
    A, B, U, V = st
    if A >= 0:
        return (2 * A + B, -A, U, V)
    return (B, -A, U - A * (m - j), V - A * j)


def rule_turn(st):
    """The fifth vertex under the turn at W_m(m), after the exchange of the names r, s (rule T)."""
    A, B, U, V = st
    if U >= 0:
        return (A, B - U, V, -U)
    return (A, B, V + 2 * U, -U)


def rule_turn_late(m, st):
    """The same turn made one step later, at position m + 1 (the other way round the commuting square): from the state
    at position m + 1 to the state at position 1."""
    A, B, U, V = st
    if U >= 0:
        return (A - U, B, V, -U)
    return (A, B, V + 2 * U, -U)


def mirror(st):
    """-W_m(j) with the names p <-> q, r <-> s exchanged is W_m(m + 1 - j); the fifth vertex becomes mirror(st)."""
    A, B, U, V = st
    return (-B, -A, -V, -U)


def cmd_cycle(args):
    import random
    rng = random.Random(7)
    n_cyc = n_mir = n_rule = n_sq = 0
    ok = True
    for m in range(3, args.mmax + 1):
        lab = (4, 1, 2, 3)
        p, q, r, s = lab
        for j in range(0, m + 1):
            for _ in range(args.rows):
                st = tuple(rng.randint(-3 * m, 3 * m) for _ in range(4))
                X = Wm(m, j, lab, st)
                if j < m:
                    Y = mut(X, p)                                   # step: names p, q exchanged
                    ok &= Y == Wm(m, j + 1, (q, p, r, s), rule_step(m, j, st))
                    n_rule += 1
                else:
                    Y = mut(X, r)                                   # turn: names r, s exchanged
                    ok &= Y == Wm(m, 0, (p, q, s, r), rule_turn(st))
                    Z = mut(X, p)                                   # one step beyond, then the turn: the commuting square
                    st1 = rule_step(m, m, st)
                    ok &= Z == Wm(m, m + 1, (q, p, r, s), st1)
                    ok &= mut(Z, r) == mut(Y, p) == Wm(m, 1, (q, p, s, r), rule_turn_late(m, st1))
                    ok &= rule_turn_late(m, st1) == rule_step(m, 0, rule_turn(st))
                    n_rule += 1
                    n_sq += 1
                ok &= neg(X) == Wm(m, m + 1 - j, (q, p, s, r), mirror(st))          # j = 0 gives the quiver one step beyond W_m(m)
                n_mir += 1
            n_cyc += 1
    print("bounce cycle W_m(j), 3 <= m <= %d: %d positions; step and turn rules for the fifth vertex on %d random states; "
          "the commuting square at W_m(m) on %d; -W_m(j) = W_m(m+1-j) with p<->q, r<->s and the mirrored state on %d: %s"
          % (args.mmax, n_cyc, n_rule, n_sq, n_mir, "all hold" if ok else "FAILED"))
    ok2 = all(upper(sub4(Wm(2 * a + 1, a + 1))) == Ra(a) for a in range(1, 200))
    print("R_a = W_{2a+1}(a+1) with (p, q, r, s) = (4, 1, 2, 3) for 1 <= a < 200: %s" % ok2)
    for a in range(2, args.amax + 1):
        m = 2 * a + 1
        seen = low_graph(a, 2 * a + 3)
        line = {canon(sub4(Wm(m, j))) for j in range(0, m + 2)}
        beyond = sub4(mut(Wm(m, m + 1), 4))                         # position m + 2: (p, q) = (1, 4) after m + 1 steps
        corner = sub4(mut(Wm(m, m - 1), 2))                         # the fifth quiver of the pentagon at W_m(m - 1)
        extra = {canon(beyond), canon(neg(beyond)), canon(corner), canon(neg(corner))}
        ok3 = len(seen) == 2 * a + 7 and len(line) == 2 * a + 3 and len(extra) == 4 and seen == line | extra
        print("a=%d: quivers of the class of R_a joined to it through height <= 2a + 3: %d (2a + 7 = %d), forks among them: %d, "
              "of height <= a + 1: %d; they are W_m(j), 0 <= j <= m + 1, the next quiver of the line at either end, and the fifth "
              "quiver of the pentagon at either end: %s"
              % (a, len(seen), 2 * a + 7, sum(1 for c in seen if nc.fork_return(from_upper(c, 4)) is not None),
                 sum(1 for c in seen if max(abs(v) for v in c) <= a + 1), ok3))


def low_graph(a, hmax):
    """The 4-vertex quivers joined to R_a through quivers of height <= hmax, up to relabelling."""
    R = from_upper(Ra(a), 4)
    seen = {canon(R)}
    todo = [R]
    while todo:
        B = todo.pop()
        for v in range(4):
            N = mut(B, v)
            c = canon(N)
            if ht(N) <= hmax and c not in seen:
                seen.add(c)
                todo.append(N)
    return seen


# ----------------------------------------------------------------------------- the family Q_a
def Qrow(a):
    return (-(a - 3), a - 2, a + 1, -(a + 1))


def Qa(a):
    return from_upper(list(Qrow(a)) + Ra(a), 5)


def Hfam(a):
    return (8 * a ** 3 - 6 * a * a + 5 * a - 1) // 2 if a % 2 else (8 * a ** 3 - 6 * a * a + 3 * a - 4) // 2


def Lfam(a):
    return (2 * a + 2) * (4 * a * a - a + 6)


def closed_state(a, n):
    """(A, B, U, V) at W_m(m) before the n-th turn of the first half of the route of Q_a (Theorem 18.4)."""
    m = 2 * a + 1
    c = 4 * a * a - 5 * a + 1
    if n == 1:
        return (2 * a * a - a + 1, -(2 * a * a - 3 * a + 3), a - 2, a + 1)
    if n == 2:
        return (4 * a * a + 1, -(4 * a * a - a + 1), a + 1, -(a - 2))
    if n <= 2 * a + 1:
        k = n - 2
        u = lambda i: a - 2 + i * (2 * a - 1)
        return (4 * a * a + 1 - k * m, -(4 * a * a + 2 - k * m), -u(k - 1), u(k - 2))
    t = n - (2 * a + 1)
    return (2 * a - 3 + (t - 1) * m, -(2 * a - 4 + (t - 1) * m), -(c - 2 * (t - 1)), c + 2 - 2 * (t - 1))


def family_route(a):
    """The route of Theorem 18.4 by integer mutation.  Returns the word, the quivers, the states before the turns of the
    first half, and the index of the first and last quiver of the middle part."""
    m = 2 * a + 1
    c = 4 * a * a - 5 * a + 1
    nturn = 2 * a + 1 + (c // 2 + 2 if a % 2 else (c + 3) // 2)       # the turn at the top
    B = Qa(a)
    p, q, r, s = 4, 1, 2, 3
    word, mats, states = [], [B], []

    def do(v):
        nonlocal B
        B = mut(B, v)
        word.append(v)
        mats.append(B)
    j = a + 1
    for n in range(1, nturn + 1):
        while j < m:
            do(p)
            p, q = q, p
            j += 1
        states.append(get_state(B, (p, q, r, s)))
        if n == nturn and a % 2 == 1:
            break                                  # odd a: the first half ends before the turn at the top
        do(r)
        r, s = s, r
        j = 0
    i1 = len(mats) - 1
    T1 = B
    half = list(word)
    if a % 2 == 1:                                 # the turn and one step
        do(r)
        r, s = s, r
        do(p)
        p, q = q, p
    else:                                          # m + 1 steps
        for _ in range(m + 1):
            do(p)
            p, q = q, p
    i2 = len(mats) - 1
    pi = None
    for perm in itertools.permutations(range(1, 5)):
        pm = (0,) + perm
        if all(B[pm[i]][pm[k]] == -T1[i][k] for i in range(5) for k in range(5)):
            pi = pm
            break
    if pi is None:
        return word, mats, states, i1, i2, None
    for v in reversed(half):
        do(pi[v])
    return word, mats, states, i1, i2, pi


def cmd_family(args):
    print("# Q_a = (-(a-3), a-2, a+1, -(a+1) | R_a): the route of Theorem 18.4 by integer mutation, and the search of np_barrier "
          "on both sides of H(a); prune = %d" % args.prune)
    rows = []
    for a in range(args.amin, args.amax + 1):
        t0 = time.time()
        Q = Qa(a)
        w, H, m = a + 1, Hfam(a), 2 * a + 1
        word, mats, states, i1, i2, pi = family_route(a)
        hts = [ht(M) for M in mats]
        top = [i for i, h in enumerate(hts) if h == H]
        r = {"a": a, "w": w, "H": H, "H/w^3": round(H / w ** 3, 4), "H/w^2.5": round(H / w ** 2.5, 4), "mutations": len(word),
             "height_is_a+1": ht(Q) == w,
             "no_mutation_at_x": 0 not in word,
             "length_is_L": len(word) == Lfam(a),
             "closed_forms_at_every_turn": all(st == closed_state(a, n + 1) for n, st in enumerate(states)),
             "turns_in_first_half": len(states),
             "mirror_found": pi is not None,
             "ends_at_opposite": pi is not None and mats[-1] == tuple(tuple(-Q[pi.index(i)][pi.index(k)] for k in range(5)) for i in range(5))
             and canon(mats[-1]) == canon(neg(Q)),
             "route_height_is_H": max(hts) == H,
             "quivers_at_H": len(top),
             "top_is_the_middle": top == (list(range(i1 + 1, i2)) if a % 2 else list(range(i1 - 1, i2 + 2))),
             "largest_entry_away_from_x": max(ht(sub4(M)) for M in mats),
             "not_isomorphic_to_opposite": canon(Q) != canon(neg(Q))}
        if a <= args.search_amax:
            below = nc.escape(Q, H - 1, budget=args.budget, prune=args.prune)
            at = nc.escape(Q, H, budget=args.budget, prune=args.prune)
            r["below_H"] = {k: below[k] for k in ("status", "popped", "plateau", "lowest", "forks", "capped")}
            r["no_other_low_quiver_below_H"] = below["status"] in ("cap", "closed") and below["plateau"] == 1 and below["lowest"] == w
            r["at_H"] = {k: at.get(k) for k in ("status", "iso", "popped", "path_len")}
            r["joined_to_opposite_at_exactly_H"] = at["status"] == "found" and at["iso"] == H and tuple(at["target"]) == canon(neg(Q))
        r["seconds"] = round(time.time() - t0, 1)
        rows.append(r)
        ok = all(v for v in r.values() if isinstance(v, bool))
        srch = ""
        if "below_H" in r:
            srch = " | below H: %s, %d quivers, only Q_a at height <= w: %s | first other quiver of height <= w at %s, it is -Q_a: %s" % (
                r["below_H"]["status"], r["below_H"]["popped"], r["no_other_low_quiver_below_H"], r["at_H"].get("iso"),
                r["joined_to_opposite_at_exactly_H"])
        print("a=%d w=%d H=%d H/w^3=%.3f H/w^2.5=%.3f | route: %d mutations, height %d, %d quivers at H, closed forms at %d turns %s%s | "
              "all checks %s (%.1fs)" % (a, w, H, H / w ** 3, H / w ** 2.5, len(word), max(hts), len(top), len(states),
                                         "ok" if r["closed_forms_at_every_turn"] else "FAILED", srch, "ok" if ok else "FAILED",
                                         r["seconds"]), flush=True)
    bad = [r["a"] for r in rows if not all(v for v in r.values() if isinstance(v, bool))]
    print("# a = %d..%d: %d values, failures: %s" % (args.amin, args.amax, len(rows), bad or "none"))
    if args.out:
        with open(args.out, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")


def Ra(a):
    """R_a = (b12, b13, b14, b23, b24, b34) = (-(a+1), -a, 2, -2, -a, -(a+1)): the fourth family of note 16, 6.2."""
    return [-(a + 1), -a, 2, -2, -a, -(a + 1)]


def flip(row):
    """(row | R_a) and (flip(row) | R_a) are opposite quivers up to the relabelling 1 <-> 4, 2 <-> 3."""
    return (-row[3], -row[2], -row[1], -row[0])


def cmd_scan(args):
    """Every row with entries <= k over R_a, one of each pair {row, flip(row)} (opposite quivers have equal escape levels)."""
    a = args.a
    k = args.k or a + 1
    w = max(k, a + 1)
    cap = args.capf * w ** 3
    rows = [r for r in itertools.product(range(-k, k + 1), repeat=4) if r <= flip(r)]
    lines = ["5 %d %d %d 1 %s" % (w, cap, args.budget, " ".join(map(str, list(r) + Ra(a)))) for r in rows]
    t0 = time.time()
    res = nc.search(lines, workers=args.workers, chunk=20)
    nc.summarize_scan(res, "R_%d = %s with every row of entries <= %d up to the flip (w = %d), cap %d, budget %d"
                      % (a, Ra(a), k, w, cap, args.budget), args.out, top=12)
    print("   %.0f s with %d workers" % (time.time() - t0, args.workers))


def cmd_pycheck(args):
    """The set of quivers that Q_a reaches through quivers of height < H(a), by a breadth-first search in pure Python
    (Python integers, no fork pruning, the canonical form of np_corridor.canon), against the count of np_barrier."""
    for a in range(args.amin, args.amax + 1):
        Q, H, w = Qa(a), Hfam(a), a + 1
        seen = {canon(Q): ht(Q)}
        todo = collections.deque([Q])
        while todo:
            B = todo.popleft()
            for v in range(5):
                N = mut(B, v)
                if ht(N) < H:
                    c = canon(N)
                    if c not in seen:
                        seen[c] = ht(N)
                        todo.append(N)
        low = sum(1 for v in seen.values() if v <= w)
        cnt = nc.escape(Q, H - 1, prune=0)["popped"]
        print("a=%d: %d quivers reachable through height < %d, %d of them of height <= %d; np_barrier counts %d: %s"
              % (a, len(seen), H, low, w, cnt, cnt == len(seen)), flush=True)


# ----------------------------------------------------------------------------- every row over R_a, by the rules
def base_height(m, j):
    return m + 1 if j in (0, m + 1) else max(2, m + 1 - j, j)


def row_over_Ra(X, a):
    """The row r with X isomorphic to (r | R_a) by a relabelling that fixes x."""
    target = tuple(Ra(a))
    for perm in itertools.permutations(range(1, 5)):
        if tuple(X[perm[i]][perm[k]] for i in range(4) for k in range(i + 1, 4)) == target:
            return tuple(X[0][perm[i]] for i in range(4))
    return None


def walk_by_rules(a, row, cap, slopes=False):
    """Walk forward from (row | R_a) along the bounce cycle (steps, and at W_m(m) the lower of the two ways round the
    commuting square).  Returns (status, height, half-periods, row reached, slopes): status 'low' if another quiver of
    height <= a + 1 is reached, 'self' if the first such quiver is isomorphic to the start, 'high' if the cap is passed."""
    m, w = 2 * a + 1, a + 1
    st = (-row[3], -row[0], row[1], row[2])
    p, q, r, s = 4, 1, 2, 3
    j, top, n = a + 1, 0, 0
    trace = []
    while True:
        while j < m:
            st = rule_step(m, j, st)
            p, q = q, p
            j += 1
            top = max(top, base_height(m, j), max(abs(v) for v in st))
            if top > cap:
                return ("high", top, n, None, trace)
            if j == a + 1 and max(abs(v) for v in st) <= w:
                X = Wm(m, j, (p, q, r, s), st)
                if canon(X) == canon(from_upper(list(row) + Ra(a), 5)):
                    return ("self", top, n, tuple(row), trace)
                return ("low", top, n, row_over_Ra(X, a), trace)
        if slopes:
            trace.append((st[0] + st[1], st[2] + st[3]))
        early = rule_turn(st)
        late = rule_step(m, m, st)
        top = max(top, m + 1, min(max(abs(v) for v in early), max(abs(v) for v in late)))
        st = early
        r, s = s, r
        j = 0
        n += 1


def walk_general(m, j0, st, w, cap, maxrounds):
    """Walk forward from the quiver at position j0 of the cycle W_m with state st, of height <= w, until another
    quiver of height <= w is met ('low'), the start is met again ('self'), the cap is passed ('high') or maxrounds
    rounds are done ('long').  Returns (status, height, rounds)."""
    cs = canon(Wm(m, j0, (1, 2, 3, 4), st))
    p, q, r, s = 1, 2, 3, 4
    j, top, n = j0, 0, 0
    while n <= maxrounds:
        while j < m:
            st = rule_step(m, j, st)
            p, q = q, p
            j += 1
            hx = max(abs(v) for v in st)
            top = max(top, base_height(m, j), hx)
            if top > cap:
                return ("high", top, n)
            if hx <= w and base_height(m, j) <= w:
                return ("low" if canon(Wm(m, j, (p, q, r, s), st)) != cs else "self", top, n)
        early = rule_turn(st)
        late = rule_step(m, m, st)
        top = max(top, m + 1, min(max(abs(v) for v in early), max(abs(v) for v in late)))
        st = early
        r, s = s, r
        j = 0
        n += 1
    return ("long", top, n)


def cmd_allbases(args):
    """Every quiver of height <= w that is a position of a cycle W_m with a fifth vertex: the height of its walk.
    The mirror image of a backward walk is a forward walk from another quiver of the list, so forward walks suffice."""
    w = args.w
    cap = args.capf * w ** 3
    best = []
    for m in range(3, 2 * w):
        cnt = ret = 0
        top_m = (0, None)
        for j0 in range(1, m + 1):
            if base_height(m, j0) > w:
                continue
            for st in itertools.product(range(-w, w + 1), repeat=4):
                cnt += 1
                status, top, n = walk_general(m, j0, st, w, cap, 40 * w * w)
                if status == "low":
                    ret += 1
                    best.append((top, m, j0, st, n))
                    if top > top_m[0]:
                        top_m = (top, (j0, st, n))
        print("w=%d m=%d: %d quivers, the walk reaches another quiver of height <= w for %d, largest walk height %d %s"
              % (w, m, cnt, ret, top_m[0], top_m[1]), flush=True)
    best.sort(reverse=True)
    lines, keys = [], []
    for top, m, j0, st, n in best[:args.verify]:
        Q = Wm(m, j0, (1, 2, 3, 4), st)
        lines.append("5 %d %d %d 1 %s" % (w, cap, args.budget, " ".join(map(str, upper(Q)))))
        keys.append((tuple(upper(Q)), top, m, j0, st, n))
    out = {tuple(q["start"]): q for q in nc.search(lines, workers=args.workers, chunk=1)}
    for key, top, m, j0, st, n in keys:
        q = out[key]
        print("   m=%d position %d state %s, %d rounds: walk height %d, escape level %s (%s)  quiver %s"
              % (m, j0, st, n, top, q.get("iso"), q["status"], list(key)))


def cmd_walks(args):
    a = args.a
    w, m = a + 1, 2 * a + 1
    cap = args.capf * w ** 3
    rows = [r for r in itertools.product(range(-w, w + 1), repeat=4) if r <= flip(r)]
    res = {}
    for r in rows:
        best = None
        for d, rr in (("forward", r), ("backward", flip(r))):
            st, top, n, end, _ = walk_by_rules(a, rr, cap)
            if st == "low" and (best is None or top < best[0]):
                best = (top, n, d, end)
        res[r] = best
    ret = {r: v for r, v in res.items() if v}
    print("R_%d, w = %d: %d rows up to the flip; the walk along the cycle reaches another quiver of height <= w below %d for %d of them"
          % (a, w, len(rows), cap, len(ret)))
    order = sorted(ret, key=lambda r: -ret[r][0])
    for r in order[:args.top]:
        top, n, d, end = ret[r]
        print("   walk height %d  row %s  %s, %d half-periods, reaches the row %s (slopes x1+x4 = %d, x2+x3 = %d)"
              % (top, list(r), d, n, list(end), r[0] + r[3], r[1] + r[2]))
    if args.scan:
        found, over = {}, set()
        with gzip.open(args.scan, "rt") as f:
            for line in f:
                if not line.strip().endswith("}"):
                    continue
                q = json.loads(line)
                if "summary" in q:
                    continue
                r = tuple(q["start"][:4])
                r = min(r, flip(r))
                if q["status"] == "found":
                    found[r] = q["iso"]
                else:
                    over.add(r)
        closed = [r for r in rows if r not in found and r not in over]
        diff = collections.Counter()
        for r, iso in found.items():
            diff["no return by the walk" if r not in ret else ("equal" if ret[r][0] == iso else
                                                              ("walk higher by %d" % (ret[r][0] - iso) if ret[r][0] - iso <= 3 else
                                                               ("walk higher by more than 3" if ret[r][0] > iso else "walk lower")))] += 1
        print("   against the scan %s:" % os.path.basename(args.scan))
        print("   rows with an escape found: %d; walk height against escape level: %s" % (len(found), dict(sorted(diff.items()))))
        big = [r for r in found if found[r] > args.level]
        print("   rows with escape level above %d: %d; the walk gives the same height for %d and a height within 3 for %d"
              % (args.level, len(big), sum(1 for r in big if r in ret and ret[r][0] == found[r]),
                 sum(1 for r in big if r in ret and 0 <= ret[r][0] - found[r] <= 3)))
        print("   rows closed below the cap by the search: %d; the walk returns below the cap for %d of them"
              % (len(closed), sum(1 for r in closed if r in ret)))
        ob = sorted((r for r in over if r in ret), key=lambda r: -ret[r][0])
        print("   rows over budget in the scan: %d; the walk returns for %d of them, largest walk heights: %s"
              % (len(over), len(ob), [(ret[r][0], list(r)) for r in ob[:6]]))
    if args.verify:
        lines, keys = [], []
        for r in order[:args.verify]:
            lines.append("5 %d %d %d 1 %s" % (w, cap, args.budget, " ".join(map(str, list(r) + Ra(a)))))
            keys.append(r)
        out = {tuple(q["start"][:4]): q for q in nc.search(lines, workers=args.workers, chunk=1)}
        agree = 0
        for r in keys:
            q = out[r]
            agree += q["status"] == "found" and q["iso"] == ret[r][0]
            print("   search: row %s  walk height %d  escape level %s (%s, %d quivers)" % (list(r), ret[r][0], q.get("iso"), q["status"], q["popped"]))
        print("   the %d rows of largest walk height: escape level equal to the walk height for %d" % (len(keys), agree))


def cmd_phases(args):
    """The walk of (row | R_a) along the cycle, cut into phases: maximal stretches of half-periods with constant slopes
    d = A + B (of x on the pair p, q, per step) and e = U + V (of x on the pair r, s, per turn)."""
    for spec in args.rows:
        a, *row = [int(v) for v in spec.split(",")]
        m, w = 2 * a + 1, a + 1
        st = (-row[3], -row[0], row[1], row[2])
        j, n, top = a + 1, 0, 0
        ph = []                                       # [d, e, first turn, last turn, state before the first, state before the last]
        done = False
        while not done and n < args.maxhalf:
            while j < m:
                st = rule_step(m, j, st)
                j += 1
                top = max(top, max(abs(v) for v in st))
                if j == a + 1 and max(abs(v) for v in st) <= w:
                    done = True
                    break
            if done:
                break
            n += 1
            key = (st[0] + st[1], st[2] + st[3])
            if ph and ph[-1][0] == key:
                ph[-1][2], ph[-1][4] = n, st
            else:
                ph.append([key, n, n, st, st])
            early, late = rule_turn(st), rule_step(m, m, st)
            top = max(top, min(max(abs(v) for v in early), max(abs(v) for v in late)))
            st = early
            j = 0
        r = nc.escape(from_upper(list(row) + Ra(a), 5), args.capf * w ** 3, budget=args.budget, prune=1)
        print("a=%d m=%d row %s: walk of %d half-periods, height %d, ends at a quiver of height <= %d: %s; escape level by search: %s"
              % (a, m, row, n, top, w, done, r.get("iso")))
        for key, n1, n2, s1, s2 in ph:
            print("   turns %4d..%4d  slopes (d, e) = (%3d, %3d)   (A, B, U, V) before the first %s, before the last %s"
                  % (n1, n2, key[0], key[1], s1, s2))


def cmd_shape(args):
    """Rows over R_a with x1 + x4 = -(2a - 2), x2 + x3 = 2a - 1, x2 >= 0, x3 >= 0 (the slopes of Q_a): escape levels."""
    for a in range(args.amin, args.amax + 1):
        w = a + 1
        rows = [(x1, x2, 2 * a - 1 - x2, -(2 * a - 2) - x1) for x1 in range(-w, w + 1) for x2 in range(0, w + 1)
                if abs(-(2 * a - 2) - x1) <= w and 0 <= 2 * a - 1 - x2 <= w]
        lines = ["5 %d %d %d 1 %s" % (w, args.capf * w ** 3, args.budget, " ".join(map(str, list(r) + Ra(a)))) for r in rows]
        out = {tuple(q["start"][:4]): q for q in nc.search(lines, workers=args.workers, chunk=1)}
        vals = sorted(((out[r].get("iso") or 0, r, out[r]["status"]) for r in rows), reverse=True)
        print("a=%d w=%d: %d rows with the slopes of Q_a; escape levels: %s; Q_a: %s, H(a) = %d"
              % (a, w, len(rows), " ".join("%d%s:%s" % (v, "" if stt == "found" else "(" + stt + ")", ",".join(map(str, r))) for v, r, stt in vals[:args.top]),
                 out[Qrow(a)].get("iso"), Hfam(a)), flush=True)


# ----------------------------------------------------------------------------- a sample of isolated 6-vertex quivers
def cmd_sample(args):
    """Random n-vertex quivers of height w whose every mutation is higher than w (isolated, as in note 16, 6.1), up to
    relabelling and reversal: escape levels.  Entries are drawn independently: +-w with probability --pw, 0 with
    probability --p0, the other values uniformly."""
    import numpy as np
    n, w = args.n, args.w
    rng = np.random.default_rng(args.seed)
    vals = list(range(-w, w + 1))
    rest = [v for v in vals if v != 0 and abs(v) != w]
    prob = [args.pw / 2 if abs(v) == w else (args.p0 if v == 0 else (1 - args.pw - args.p0) / len(rest)) for v in vals]
    pairs = [(i, k) for i in range(n) for k in range(i + 1, n)]
    U = rng.choice(np.array(vals, dtype=np.int32), size=(args.draws, len(pairs)), p=prob)
    U = U[np.abs(U).max(axis=1) == w]
    B = np.zeros((U.shape[0], n, n), dtype=np.int32)
    for k, (i, j) in enumerate(pairs):
        B[:, i, j] = U[:, k]
        B[:, j, i] = -U[:, k]
    good = np.ones(B.shape[0], dtype=bool)
    for v in range(n):
        col, row = B[:, :, v], B[:, v, :]
        N = B + (np.abs(col)[:, :, None] * row[:, None, :] + col[:, :, None] * np.abs(row)[:, None, :]) // 2
        N[:, v, :] = -row
        N[:, :, v] = -col
        good &= np.abs(N).reshape(N.shape[0], n * n).max(axis=1) > w
    U = U[good]
    CU = nc.dedupe(U, n)
    print("n=%d w=%d: %d draws (P(+-%d) = %.2f, P(0) = %.2f, seed %d), %d isolated, %d up to relabelling and reversal"
          % (n, w, args.draws, w, args.pw, args.p0, args.seed, U.shape[0], CU.shape[0]), flush=True)
    lines = ["%d %d %d %d 1 %s" % (n, w, args.cap, args.budget, " ".join(str(int(x)) for x in row)) for row in CU]
    t0 = time.time()
    rows = nc.search(lines, workers=args.workers, chunk=20)
    nc.summarize_scan(rows, "n=%d w=%d sample of isolated quivers, cap %d, budget %d" % (n, w, args.cap, args.budget), args.out, top=10)
    by = collections.defaultdict(list)
    for r in rows:
        by[sum(1 for v in r["start"] if abs(v) == w)].append(r["iso"] if r["status"] == "found" else 0)
    for k in sorted(by):
        print("   entries +-%d: %2d  quivers %5d  with an escape %5d  largest escape levels %s"
              % (w, k, len(by[k]), sum(1 for v in by[k] if v), sorted(by[k])[-3:]))
    print("   %.0f s with %d workers" % (time.time() - t0, args.workers))


def cmd_recheck(args):
    """Search again, with a larger budget, a random part of the quivers that ran over the budget in a stored sample."""
    import random
    todo = []
    with gzip.open(args.file, "rt") as f:
        for line in f:
            if line.strip().endswith("}"):
                q = json.loads(line)
                if q.get("status") == "budget":
                    todo.append(q)
    random.Random(args.seed).shuffle(todo)
    total = len(todo)
    todo = todo[:args.take]
    lines = ["%d %d %d %d 1 %s" % (q["n"], q["w"], args.cap, args.budget, " ".join(map(str, q["start"]))) for q in todo]
    t0 = time.time()
    rows = nc.search(lines, workers=args.workers, chunk=5)
    nc.summarize_scan(rows, "recheck of %d of the %d quivers over budget in %s, cap %d, budget %d"
                      % (len(todo), total, os.path.basename(args.file), args.cap, args.budget), args.out, top=10)
    print("   %.0f s with %d workers" % (time.time() - t0, args.workers))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("blocks")
    s.add_argument("--quiver", type=int, nargs="+", required=True)
    s.add_argument("--cap", type=int, default=100000)
    s.add_argument("--budget", type=int, default=5_000_000)
    s = sub.add_parser("cycle")
    s.add_argument("--mmax", type=int, default=41)
    s.add_argument("--rows", type=int, default=40)
    s.add_argument("--amax", type=int, default=20)
    s = sub.add_parser("family")
    s.add_argument("--amin", type=int, default=2)
    s.add_argument("--amax", type=int, default=12)
    s.add_argument("--search-amax", type=int, default=12)
    s.add_argument("--prune", type=int, default=1)
    s.add_argument("--budget", type=int, default=30_000_000)
    s.add_argument("--out", default=None)
    s = sub.add_parser("pycheck")
    s.add_argument("--amin", type=int, default=2)
    s.add_argument("--amax", type=int, default=6)
    s = sub.add_parser("scan")
    s.add_argument("--a", type=int, required=True)
    s.add_argument("--k", type=int, default=0)
    s.add_argument("--capf", type=int, default=16)
    s.add_argument("--budget", type=int, default=300000)
    s.add_argument("--workers", type=int, default=12)
    s.add_argument("--out", default=None)
    s = sub.add_parser("walks")
    s.add_argument("--a", type=int, required=True)
    s.add_argument("--capf", type=int, default=16)
    s.add_argument("--scan", default=None)
    s.add_argument("--level", type=int, default=0)
    s.add_argument("--top", type=int, default=8)
    s.add_argument("--verify", type=int, default=0)
    s.add_argument("--budget", type=int, default=3_000_000)
    s.add_argument("--workers", type=int, default=4)
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=6)
    s.add_argument("--w", type=int, default=2)
    s.add_argument("--draws", type=int, default=200000)
    s.add_argument("--pw", type=float, default=0.5)
    s.add_argument("--p0", type=float, default=0.15)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--cap", type=int, default=1024)
    s.add_argument("--budget", type=int, default=50000)
    s.add_argument("--workers", type=int, default=12)
    s.add_argument("--out", default=None)
    s = sub.add_parser("recheck")
    s.add_argument("--file", required=True)
    s.add_argument("--take", type=int, default=500)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--cap", type=int, default=1024)
    s.add_argument("--budget", type=int, default=300000)
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--out", default=None)
    s = sub.add_parser("allbases")
    s.add_argument("--w", type=int, required=True)
    s.add_argument("--capf", type=int, default=8)
    s.add_argument("--verify", type=int, default=6)
    s.add_argument("--budget", type=int, default=3_000_000)
    s.add_argument("--workers", type=int, default=2)
    s = sub.add_parser("phases")
    s.add_argument("--rows", nargs="+", required=True, help="a,x1,x2,x3,x4")
    s.add_argument("--maxhalf", type=int, default=100000)
    s.add_argument("--capf", type=int, default=16)
    s.add_argument("--budget", type=int, default=3_000_000)
    s = sub.add_parser("shape")
    s.add_argument("--amin", type=int, default=3)
    s.add_argument("--amax", type=int, default=10)
    s.add_argument("--capf", type=int, default=16)
    s.add_argument("--budget", type=int, default=3_000_000)
    s.add_argument("--top", type=int, default=6)
    s.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    globals()["cmd_" + args.cmd](args)


if __name__ == "__main__":
    main()
