#!/usr/bin/env python
"""
np_corridor.py -- barriers above w^2 on five vertices (note 16).

The 5-vertex quiver P_t (t >= 2, D = floor(t^2 / 2)), on the vertices 0 = x, 1 = p, 2 = q, 3 = c1, 4 = c:

    q -> p      2            p -> c1   t(t - 1)       c1 -> q   t^2
    p -> c      t^2          q -> c    t^2 - 1        c -> c1   2t
    p -> x      t^2          x -> q    t^2 - D        x -> c    2D          (x and c1 are not joined)

has maximal entry t^2.  Its full subquiver on {p, q, c1, c} is the quiver Q_t of note 15.  P_t and its
opposite -P_t are joined at maximal entry

    H(t) = t^2 + (2t^3 - t^2 + 1) * D        ( = t^5 - t^4/2 + 3t^2/2 for even t )

and, for every t checked, by no lower route.  The lower bound is measured by an exhaustive bottleneck
search (np_barrier.c), which this script drives.

Subcommands (run from experiments/ with python -I):
  build       compile np_barrier.c into ~/.cache/qmb-np/np_barrier
  selftest    the search against known 4-vertex values; the Python kernel against mutation_path.mutate
  family      P_t for a range of t: the route, the identity at the top, and the search on both sides of H(t)
  family_plus the variant P+_t (x starts one step earlier), with H+(t) = 2t^5 - t^4 + t^2 - 1
  pycheck     the component below H by a pure-Python search, against np_barrier
  core        the quivers a reduced route from P_t can use below H(t) (no fork above t^2), and their branches
  grid        the same construction with free parameters (h, m, a0, D, Ax): where the formula holds
  star        several counters on one pair (n = k + 4 vertices)
  pendant     P_t with a path of extra vertices hung from x (connected quivers on n >= 6 vertices)
  census      every isolated n-vertex quiver of maximal entry w (all its mutations are higher): escape levels
  templates   5-vertex quivers with entries in {0, +-1, +-(k-1), +-k} whose every mutation is above 2k
  rows        a fixed 4-vertex quiver with a fifth vertex attached by every row of entries <= k
  path        a route of least height from a given quiver to another quiver of its starting height
"""
import argparse
import collections
import gzip
import itertools
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.expanduser("~/.cache/qmb-np/np_barrier")
INT_MAX = 2 ** 31 - 1


# ----------------------------------------------------------------------------- exact kernel (Python integers)
def mut(B, k):
    n = len(B)
    N = [list(r) for r in B]
    for i in range(n):
        if i == k or B[i][k] == 0:
            continue
        bik = B[i][k]
        for j in range(n):
            if j == k:
                continue
            bkj = B[k][j]
            if bik > 0 and bkj > 0:
                N[i][j] += bik * bkj
            elif bik < 0 and bkj < 0:
                N[i][j] -= bik * bkj
    for i in range(n):
        N[i][k] = -B[i][k]
        N[k][i] = -B[k][i]
    return tuple(tuple(r) for r in N)


def ht(B):
    return max(abs(x) for r in B for x in r)


def neg(B):
    return tuple(tuple(-x for x in r) for r in B)


_PERMS = {}


def canon(B):
    """Least upper triangle over all relabellings (the convention of np_barrier.c)."""
    n = len(B)
    if n not in _PERMS:
        _PERMS[n] = list(itertools.permutations(range(n)))
    return min(tuple(B[p[i]][p[j]] for i in range(n) for j in range(i + 1, n)) for p in _PERMS[n])


def upper(B):
    n = len(B)
    return [B[i][j] for i in range(n) for j in range(i + 1, n)]


def from_upper(u, n):
    B = [[0] * n for _ in range(n)]
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            B[i][j] = u[k]
            B[j][i] = -u[k]
            k += 1
    return tuple(tuple(r) for r in B)


def acyclic_on(B, vs):
    rem = set(vs)
    while rem:
        src = [i for i in rem if not any(B[j][i] > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def fork_return(B):
    """Point of return if B is a fork (Warkentin, Def. 2.1), else None."""
    n = len(B)
    if any(abs(B[i][j]) < 2 for i in range(n) for j in range(i + 1, n)) or acyclic_on(B, range(n)):
        return None
    for r in range(n):
        ins = [i for i in range(n) if B[i][r] > 0]
        outs = [j for j in range(n) if B[r][j] > 0]
        if all(B[j][i] > B[i][r] and B[j][i] > B[r][j] for i in ins for j in outs) and acyclic_on(B, ins) and acyclic_on(B, outs):
            return r
    return None


# ----------------------------------------------------------------------------- the C search
def task_line(B, cap, budget, prune, w=None):
    return "%d %d %d %d %d %s" % (len(B), ht(B) if w is None else w, cap, budget, prune, " ".join(map(str, upper(B))))


def _run_chunk(arg):
    lines, flag = arg
    cmd = [BIN] + ([flag] if flag else [])
    return subprocess.run(cmd, input="\n".join(lines) + "\n", capture_output=True, text=True).stdout


def search(lines, workers=1, chunk=100, flag=None):
    """Run task lines through np_barrier; returns the parsed JSON rows (order not kept when workers > 1)."""
    chunks = [(lines[i:i + chunk], flag) for i in range(0, len(lines), chunk)]
    out = []
    if workers <= 1:
        for c in chunks:
            out += [json.loads(l) for l in _run_chunk(c).splitlines() if l.strip().endswith("}")]
    else:
        with Pool(workers) as pool:
            for res in pool.imap_unordered(_run_chunk, chunks):
                out += [json.loads(l) for l in res.splitlines() if l.strip().endswith("}")]
    return out


def escape(B, cap, budget=6_000_000, prune=0):
    return search([task_line(B, min(cap, INT_MAX), budget, prune)])[0]


def cmd_build(args):
    os.makedirs(os.path.dirname(BIN), exist_ok=True)
    subprocess.run(["gcc", "-O2", "-Wall", "-o", BIN, os.path.join(HERE, "np_barrier.c")], check=True)
    print("built", BIN)


# ----------------------------------------------------------------------------- the family P_t
X, Pv, Qv, C1, C = 0, 1, 2, 3, 4


def two_counter(h, m, a0, D, Ax, tail=0, tail_sign=1):
    """Vertices x, p, q, c1, c (and a path of `tail` further vertices hung from x by arrows of weight 1).
    q -> p has weight 2.  In the coordinates A_e = b_pe, B_e = b_qe:
      c1 = (m h, -(m + 1) h)      descends by h per step and is exhausted after m steps;
      c  = (a0, 2h^2 - 1 - a0)    climbs by 2h^2 - 1 per step, and by -1 after the mutation at c1;
      x  = (Ax, D - Ax)           climbs by D per step;
    c -> c1 has weight 2h, x -> c has weight 2D, x and c1 are not joined."""
    n = 5 + tail
    B = [[0] * n for _ in range(n)]

    def setb(i, j, v):
        B[i][j] = v
        B[j][i] = -v
    setb(Qv, Pv, 2)
    setb(Pv, C1, m * h)
    setb(Qv, C1, -(m + 1) * h)
    setb(Pv, C, a0)
    setb(Qv, C, 2 * h * h - 1 - a0)
    setb(Pv, X, Ax)
    setb(Qv, X, D - Ax)
    setb(X, C, 2 * D)
    setb(C, C1, 2 * h)
    prev = X
    for v in range(5, n):
        setb(prev, v, tail_sign)
        prev = v
    return tuple(tuple(r) for r in B)


def Dt(t):
    return t * t // 2


def Pt(t, tail=0, tail_sign=1):
    return two_counter(t, t - 1, t * t, Dt(t), t * t, tail, tail_sign)


def Ht(t):
    return t * t + (2 * t ** 3 - t * t + 1) * Dt(t)


def route(h, m, a0, D, Ax, tail=0, tail_sign=1):
    """The first half of the route: m steps on the pair, the mutation at c1, a0 + m(2h^2 - 1) further steps.
    Returns the quivers passed, the last one L, and mu_p(L), mu_c(L)."""
    B = two_counter(h, m, a0, D, Ax, tail, tail_sign)
    hist = [B]
    cur = Pv
    for _ in range(m):
        B = mut(B, cur)
        cur = Pv + Qv - cur
        hist.append(B)
    B = mut(B, C1)
    hist.append(B)
    for _ in range(a0 + m * (2 * h * h - 1)):
        B = mut(B, cur)
        cur = Pv + Qv - cur
        hist.append(B)
    return hist, mut(B, cur), mut(B, C)


def closed_forms_ok(t, hist):
    """The columns and the three entries between x, c1, c at every quiver of the route, against Lemma 16.1/53.2."""
    D = Dt(t)
    N = 2 * t ** 3 - t * t - t
    cur = Pv
    for idx, B in enumerate(hist):
        if idx <= t - 1:                       # K(j)
            j = idx
            c1 = ((t - 1 - j) * t, -(t - j) * t)
            c = (t * t + j * (2 * t * t - 1), -(t * t + (j - 1) * (2 * t * t - 1)))
            x = (t * t + j * D, -(t * t + (j - 1) * D))
            z = 2 * t
            steps = j
        else:                                  # L(i)
            i = idx - t
            c1 = (i * t, -(i - 1) * t)
            c = (N + 1 - i, -(N + 2 - i))
            x = (t * t + (t - 1 + i) * D, -(t * t + (t - 2 + i) * D))
            z = -2 * t
            steps = t - 1 + i
        p = Pv if steps % 2 == 0 else Qv
        q = Pv + Qv - p
        got = (B[q][p], (B[p][C1], B[q][C1]), (B[p][C], B[q][C]), (B[p][X], B[q][X]), B[C][C1], B[X][C], B[X][C1])
        if got != (2, c1, c, x, z, 2 * D, 0):
            return False
    return True


def cmd_family(args):
    print("# P_t: route, identity at the top, and exhaustive search on both sides of H(t); prune = %d" % args.prune)
    rows = []
    for t in range(args.tmin, args.tmax + 1):
        t0 = time.time()
        Q = Pt(t)
        w = ht(Q)
        H = Ht(t)
        N = 2 * t ** 3 - t * t - t
        hist, up, turn = route(t, t - 1, t * t, Dt(t), t * t)
        heights = [ht(B) for B in hist]
        r = {"t": t, "w": w, "D": Dt(t), "H": H, "H/w^2": round(H / w ** 2, 4), "H/w^2.5": round(H / w ** 2.5, 4),
             "route_steps_to_top": len(hist) - 1,
             "height_is_t2": w == t * t,
             "closed_forms": closed_forms_ok(t, hist),
             "identity_mu_c_eq_minus_mu_p": turn == neg(up),
             "route_below_H": max(heights) == H - Dt(t) and max(heights) < H,
             "top_height_is_H": ht(up) == H == ht(turn),
             "not_isomorphic_to_opposite": canon(Q) != canon(neg(Q)),
             "subquiver_is_Q_t_of_note_15": upper(tuple(tuple(Q[i][j] for j in (1, 2, 3, 4)) for i in (1, 2, 3, 4))) ==
             [-2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t]}
        below = escape(Q, H - 1, prune=args.prune)
        at = escape(Q, H, prune=args.prune)
        r["below_H"] = {k: below[k] for k in ("status", "popped", "plateau", "lowest", "forks", "capped")}
        r["no_other_low_quiver_below_H"] = below["status"] in ("cap", "closed") and below["plateau"] == 1 and below["lowest"] == w
        r["at_H"] = {k: at.get(k) for k in ("status", "iso", "popped", "path_len")}
        r["joined_to_opposite_at_exactly_H"] = at["status"] == "found" and at["iso"] == H and tuple(at["target"]) == canon(neg(Q))
        r["seconds"] = round(time.time() - t0, 1)
        rows.append(r)
        ok = all(v for k, v in r.items() if isinstance(v, bool))
        print("t=%d w=%d D=%d H=%d H/w^2=%.3f H/w^2.5=%.3f steps=%d | component below H: %d quivers, only P_t at height <= w: %s | "
              "first other quiver of height <= w at %s, it is -P_t: %s | all checks %s (%.1fs)"
              % (t, w, Dt(t), H, H / w ** 2, H / w ** 2.5, len(hist) - 1, below["popped"], r["no_other_low_quiver_below_H"],
                 at.get("iso"), r["joined_to_opposite_at_exactly_H"], "ok" if ok else "FAILED", r["seconds"]), flush=True)
    bad = [r["t"] for r in rows if not all(v for v in r.values() if isinstance(v, bool))]
    print("# t = %d..%d: %d values, failures: %s" % (args.tmin, args.tmax, len(rows), bad or "none"))
    even = [r for r in rows if r["t"] % 2 == 0]
    print("# even t: H = t^5 - t^4/2 + 3t^2/2 in all: %s; odd t: H = t^5 - t^4/2 - t^3 + 2t^2 - 1/2 in all: %s"
          % (all(2 * r["H"] == 2 * r["t"] ** 5 - r["t"] ** 4 + 3 * r["t"] ** 2 for r in even),
             all(2 * r["H"] == 2 * r["t"] ** 5 - r["t"] ** 4 - 2 * r["t"] ** 3 + 4 * r["t"] ** 2 - 1 for r in rows if r["t"] % 2)))
    if args.out:
        with open(args.out, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")


# ----------------------------------------------------------------------------- the variant P+_t
def Pplus(t):
    """P+_t: as P_t, but x starts one step earlier, as an in-neighbour of p: x -> p of weight 1, q -> x of weight
    t^2 - 1, x -> c of weight t^2 and c1 -> x of weight t(t - 1).  After the first step on the pair, x is the column
    (t^2 - 1, 1), which climbs by t^2 per step, x -> c has weight 2t^2 and x, c1 are not joined."""
    B = [list(r) for r in two_counter(t, t - 1, t * t, 0, 0)]

    def setb(i, j, v):
        B[i][j] = v
        B[j][i] = -v
    setb(Pv, X, -1)
    setb(Qv, X, t * t - 1)
    setb(X, C, t * t)
    setb(X, C1, -t * (t - 1))
    return tuple(tuple(r) for r in B)


def Hplus(t):
    return 2 * t ** 5 - t ** 4 + t * t - 1


def route_from(Q, m, L2):
    B = Q
    hist = [B]
    cur = Pv
    for _ in range(m):
        B = mut(B, cur)
        cur = Pv + Qv - cur
        hist.append(B)
    B = mut(B, C1)
    hist.append(B)
    for _ in range(L2):
        B = mut(B, cur)
        cur = Pv + Qv - cur
        hist.append(B)
    return hist, mut(B, cur), mut(B, C)


def closed_forms_plus_ok(t, hist):
    N = 2 * t ** 3 - t * t - t
    ax = lambda s: t * t - 1 + (s - 1) * t * t          # the entry of x at the vertex to be mutated, after s >= 1 steps
    for idx, B in enumerate(hist):
        if idx <= t - 1:
            j = idx
            c1 = ((t - 1 - j) * t, -(t - j) * t)
            c = (t * t + j * (2 * t * t - 1), -(t * t + (j - 1) * (2 * t * t - 1)))
            z, steps = 2 * t, j
        else:
            i = idx - t
            c1 = (i * t, -(i - 1) * t)
            c = (N + 1 - i, -(N + 2 - i))
            z, steps = -2 * t, t - 1 + i
        if steps == 0:
            x, sxc, sxc1 = (-1, t * t - 1), t * t, -t * (t - 1)
        else:
            x, sxc, sxc1 = (ax(steps), -ax(steps - 1) if steps >= 2 else 1), 2 * t * t, 0
        p = Pv if steps % 2 == 0 else Qv
        q = Pv + Qv - p
        got = (B[q][p], (B[p][C1], B[q][C1]), (B[p][C], B[q][C]), (B[p][X], B[q][X]), B[C][C1], B[X][C], B[X][C1])
        if got != (2, c1, c, x, z, sxc, sxc1):
            return False
    return True


def cmd_family_plus(args):
    print("# P+_t: route, identity at the top, and exhaustive search on both sides of H+(t) = 2t^5 - t^4 + t^2 - 1; prune = %d" % args.prune)
    rows = []
    for t in range(args.tmin, args.tmax + 1):
        t0 = time.time()
        Q = Pplus(t)
        w = ht(Q)
        H = Hplus(t)
        hist, up, turn = route_from(Q, t - 1, 2 * t ** 3 - t * t - t + 1)
        heights = [ht(B) for B in hist]
        r = {"t": t, "w": w, "H": H, "H/w^2": round(H / w ** 2, 4), "H/w^2.5": round(H / w ** 2.5, 4),
             "route_steps_to_top": len(hist) - 1,
             "height_is_t2": w == t * t,
             "closed_forms": closed_forms_plus_ok(t, hist),
             "identity_mu_c_eq_minus_mu_p": turn == neg(up),
             "route_below_H": max(heights) == H - t * t,
             "top_height_is_H": ht(up) == H == ht(turn),
             "not_isomorphic_to_opposite": canon(Q) != canon(neg(Q))}
        below = escape(Q, H - 1, prune=args.prune)
        at = escape(Q, H, prune=args.prune)
        r["below_H"] = {k: below[k] for k in ("status", "popped", "plateau", "lowest", "forks", "capped")}
        r["no_other_low_quiver_below_H"] = below["status"] in ("cap", "closed") and below["plateau"] == 1 and below["lowest"] == w
        r["at_H"] = {k: at.get(k) for k in ("status", "iso", "popped", "path_len")}
        r["joined_to_opposite_at_exactly_H"] = at["status"] == "found" and at["iso"] == H and tuple(at["target"]) == canon(neg(Q))
        r["seconds"] = round(time.time() - t0, 1)
        rows.append(r)
        ok = all(v for k, v in r.items() if isinstance(v, bool))
        print("t=%d w=%d H+=%d H/w^2=%.3f H/w^2.5=%.3f steps=%d | component below H+: %d quivers, only P+_t at height <= w: %s | "
              "first other quiver of height <= w at %s, it is -P+_t: %s | all checks %s (%.1fs)"
              % (t, w, H, H / w ** 2, H / w ** 2.5, len(hist) - 1, below["popped"], r["no_other_low_quiver_below_H"],
                 at.get("iso"), r["joined_to_opposite_at_exactly_H"], "ok" if ok else "FAILED", r["seconds"]), flush=True)
    bad = [r["t"] for r in rows if not all(v for v in r.values() if isinstance(v, bool))]
    print("# t = %d..%d: %d values, failures: %s" % (args.tmin, args.tmax, len(rows), bad or "none"))
    import math
    T = args.tmax
    worst = max((2 * w ** 2.5 - Hplus(math.isqrt(w))) / w ** 2 for w in range(4, (T + 1) ** 2))
    print("# for 4 <= w < %d: H+(floor(sqrt(w))) >= 2w^2.5 - c*w^2 with least c = %.4f; H+(t) > 2t^4 for all 2 <= t <= %d: %s"
          % ((T + 1) ** 2, worst, T, all(Hplus(t) > 2 * t ** 4 for t in range(2, T + 1))))
    if args.out:
        with open(args.out, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")


def cmd_pycheck(args):
    """The component of P_t and of P+_t among quivers of height < H, by a breadth-first search in pure Python
    (Python integers, no fork pruning, own canonical form), against the count of np_barrier."""
    for t in range(args.tmin, args.tmax + 1):
        for name, Q, H in (("P_t", Pt(t), Ht(t)), ("P+_t", Pplus(t), Hplus(t))):
            w = ht(Q)
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
            cnt = escape(Q, H - 1, prune=0)["popped"]
            print("t=%d %s: %d quivers of height < %d reachable below that height, %d of them of height <= %d; np_barrier counts %d: %s"
                  % (t, name, len(seen), H, low, w, cnt, cnt == len(seen)), flush=True)


# ----------------------------------------------------------------------------- the core
def core(t, plus=False):
    """Labelled search from P_t (or P+_t) through non-forks of height < H(t).  A fork of height <= t^2 would be
    recorded as a low quiver; none occurs."""
    Q = Pplus(t) if plus else Pt(t)
    H = Hplus(t) if plus else Ht(t)
    w = ht(Q)
    seen = {canon(Q): (Q, None, None)}
    todo = collections.deque([Q])
    exits = collections.Counter()
    low_forks = 0
    while todo:
        B = todo.popleft()
        for v in range(5):
            N = mut(B, v)
            lv = ht(N)
            if lv >= H:
                exits["height >= H"] += 1
                continue
            if fork_return(N) is not None:
                low_forks += lv <= w
                exits["fork"] += 1
                continue
            c = canon(N)
            if c in seen:
                exits["member"] += 1
                continue
            seen[c] = (N, canon(B), v)
            todo.append(N)
    return seen, exits, low_forks


def _rle(word):
    out = []
    i = 0
    while i < len(word):
        j = i
        while j + 2 < len(word) and word[j + 2] == word[j]:
            j += 1
        if j - i >= 3:
            reps = (j + 2 - i) // 2
            out.append("(%d %d)^%d%s" % (word[i], word[i + 1], reps, " %d" % word[i] if (j + 2 - i) % 2 else ""))
            i = j + 2
        else:
            out.append(str(word[i]))
            i += 1
    return " ".join(out)


def cmd_core(args):
    for t in args.t:
        seen, exits, low_forks = core(t, args.plus)
        if args.plus:
            hist, _, _ = route_from(Pplus(t), t - 1, 2 * t ** 3 - t * t - t + 1)
        else:
            hist, _, _ = route(t, t - 1, t * t, Dt(t), t * t)
        idx = {canon(B): j for j, B in enumerate(hist)}
        w, H = t * t, (Hplus(t) if args.plus else Ht(t))
        low = sum(1 for B, _, _ in seen.values() if ht(B) <= w)
        print("t=%d w=%d H=%d: core %d quivers (%d on the route, core of Q_t in note 15: %d); exits: %s; forks of height <= w: %d; "
              "members of height <= w: %d" % (t, w, H, len(seen), sum(1 for c in seen if c in idx), 2 * t ** 3 - t * t + 5,
                                               dict(exits), low_forks, low))
        if not args.branches:
            continue
        br = collections.defaultdict(list)
        for c, (B, par, v) in seen.items():
            if c in idx:
                continue
            word = [v]
            p = par
            while p not in idx:
                _, pp, vv = seen[p]
                word.append(vv)
                p = pp
            word.reverse()
            br[(idx[p], word[0])].append((len(word), tuple(word), ht(B)))
        for key in sorted(br):
            lst = sorted(br[key])
            name = "K(%d)" % key[0] if key[0] <= t - 1 else "L(%d)" % (key[0] - t)
            print("   branch at %s by the mutation at %s: %d quivers, heights %d..%d, longest word %s"
                  % (name, "x p q c1 c".split()[key[1]], len(lst), min(l[2] for l in lst), max(l[2] for l in lst), _rle(lst[-1][1])))


# ----------------------------------------------------------------------------- free parameters
def cmd_grid(args):
    tasks = []
    for h in range(1, 6):
        for m in range(1, 6):
            for a0 in (0, 1, 2, 3, 5, 8, 13):
                for D in (1, 2, 3, 5, 8):
                    for Ax in (0, 1, 2, 5, 9, 16):
                        B = two_counter(h, m, a0, D, Ax)
                        if ht(B) > 40:
                            continue
                        hist, up, turn = route(h, m, a0, D, Ax)
                        H = max(max(ht(Y) for Y in hist), ht(up))
                        tasks.append(((h, m, a0, D, Ax), ht(B), H, turn == neg(up), task_line(B, 3 * H, 400000, 1)))
    rows = {tuple(r["start"]): r for r in search([t[4] for t in tasks], workers=args.workers)}
    res = collections.Counter()
    byh = collections.Counter()
    generic = collections.Counter()
    for par, w, H, ident, _ in tasks:
        r = rows[tuple(upper(two_counter(*par)))]
        if r["status"] == "found" and r["iso"] == H:
            kind = "escape level = height of the route"
        elif r["status"] == "found":
            kind = "escape level below the route"
        else:
            kind = "no other quiver of height <= w found below 3H (%s)" % r["status"]
        res[kind] += 1
        byh[(par[0], kind)] += 1
        h, m, a0, D, Ax = par
        if h >= 2 and a0 >= h * h and Ax >= h * h and D >= h:
            generic[kind] += 1
    print("parameter sets: %d; identity mu_c = -mu_p at the top in all: %s" % (len(tasks), all(t[3] for t in tasks)))
    for k, v in sorted(res.items()):
        print("  %-70s %d" % (k, v))
    for (h, k), v in sorted(byh.items()):
        print("  h=%d  %-64s %d" % (h, k, v))
    print("  with h >= 2, a0 >= h^2, Ax >= h^2, D >= h: %s" % dict(generic))


def cmd_pendant(args):
    for n in args.n:
        for t in args.t:
            for sign in (1, -1):
                Q = Pt(t, tail=n - 5, tail_sign=sign)
                H = Ht(t)
                hist, up, turn = route(t, t - 1, t * t, Dt(t), t * t, tail=n - 5, tail_sign=sign)
                below = escape(Q, H - 1, prune=args.prune, budget=args.budget)
                at = escape(Q, H, prune=args.prune, budget=args.budget)
                print("n=%d t=%d tail %+d: height %d; route to the quiver with the block reversed and the tail kept has height %d = H: %s; "
                      "below H: %s, %d quivers, %d of height <= w; first other quiver of height <= w at %s"
                      % (n, t, sign, ht(Q), max(max(ht(Y) for Y in hist), ht(up)), max(max(ht(Y) for Y in hist), ht(up)) == H,
                         below["status"], below["popped"], below["plateau"], at.get("iso")), flush=True)


def star(k, h, m, a0, D, Ax):
    """k counters z_1..z_k (vertices 3..k+2), each (m h, -(m + 1) h) and joined to c (last vertex) by c -> z_i of
    weight 2h; c = (a0, 2k h^2 - 1 - a0); x = (Ax, D - Ax) with x -> c of weight 2D.  For k = 1 this is two_counter."""
    n = k + 4
    B = [[0] * n for _ in range(n)]

    def setb(i, j, v):
        B[i][j] = v
        B[j][i] = -v
    c = n - 1
    setb(Qv, Pv, 2)
    for z in range(3, 3 + k):
        setb(Pv, z, m * h)
        setb(Qv, z, -(m + 1) * h)
        setb(c, z, 2 * h)
    setb(Pv, c, a0)
    setb(Qv, c, 2 * k * h * h - 1 - a0)
    setb(Pv, X, Ax)
    setb(Qv, X, D - Ax)
    setb(X, c, 2 * D)
    return tuple(tuple(r) for r in B)


def cmd_star(args):
    """Several counters on one pair, on n = k + 4 vertices: route, identity at the top, and the search (with fork
    pruning) on both sides of the height of the route."""
    for spec in args.spec:
        k, h, m, a0, D, Ax = [int(v) for v in spec.split(",")]
        B = star(k, h, m, a0, D, Ax)
        Q = B
        n = len(B)
        w = ht(B)
        cur = Pv
        top = w
        for _ in range(m):
            B = mut(B, cur)
            cur = Pv + Qv - cur
            top = max(top, ht(B))
        for z in range(3, 3 + k):
            B = mut(B, z)
            top = max(top, ht(B))
        for _ in range(a0 + m * (2 * k * h * h - 1)):
            B = mut(B, cur)
            cur = Pv + Qv - cur
            top = max(top, ht(B))
        up, turn = mut(B, cur), mut(B, n - 1)
        H = max(top, ht(up))
        below = escape(Q, H - 1, prune=1)
        at = escape(Q, H, prune=1)
        print("k=%d n=%d h=%d m=%d a0=%d D=%d Ax=%d: height %d, route of height H=%d (H/w^2=%.2f, H/w^2.5=%.2f), identity at the top %s; "
              "below H: %s, %d quivers, %d of height <= w; first other quiver of height <= w at %s"
              % (k, n, h, m, a0, D, Ax, w, H, H / w ** 2, H / w ** 2.5, turn == neg(up), below["status"], below["popped"], below["plateau"],
                 at.get("iso")), flush=True)


# ----------------------------------------------------------------------------- censuses and scans
def isolated(n, vals, thr, need):
    """Labelled n-vertex quivers with entries in vals, maximal entry `need`, vertices in non-decreasing order of
    total weight, and every mutation of maximal entry > thr.  Returns the upper triangles."""
    import numpy as np
    V = np.array(vals, dtype=np.int32)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = len(pairs)
    ni = min(m, 6)
    no = m - ni
    inner = V[np.array(list(itertools.product(range(len(V)), repeat=ni)), dtype=np.int16)]
    kept = []
    for outer in itertools.product(range(len(V)), repeat=no):
        U = np.empty((inner.shape[0], m), dtype=np.int32)
        if no:
            U[:, :no] = V[list(outer)]
        U[:, no:] = inner
        U = U[np.abs(U).max(axis=1) == need]
        B = np.zeros((U.shape[0], n, n), dtype=np.int32)
        for k, (i, j) in enumerate(pairs):
            B[:, i, j] = U[:, k]
            B[:, j, i] = -U[:, k]
        deg = np.abs(B).sum(axis=2)
        ok = (deg[:, :-1] <= deg[:, 1:]).all(axis=1)
        B, U = B[ok], U[ok]
        if B.shape[0] == 0:
            continue
        good = np.ones(B.shape[0], dtype=bool)
        for v in range(n):
            col, row = B[:, :, v], B[:, v, :]
            add = (np.abs(col)[:, :, None] * row[:, None, :] + col[:, :, None] * np.abs(row)[:, None, :]) // 2
            N = B + add
            N[:, v, :] = -row
            N[:, :, v] = -col
            good &= np.abs(N).reshape(N.shape[0], n * n).max(axis=1) > thr
        kept.append(U[good])
    return np.concatenate(kept)


def dedupe(U, n):
    """One representative per class under relabelling and reversal of all arrows."""
    import numpy as np
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pos = {p: k for k, p in enumerate(pairs)}
    base = int(np.abs(U).max()) * 2 + 1
    off = base // 2
    best = None
    bestU = None
    for sgn in (1, -1):
        for p in itertools.permutations(range(n)):
            cols, signs = [], []
            for (i, j) in pairs:
                a, b = p[i], p[j]
                cols.append(pos[(min(a, b), max(a, b))])
                signs.append(sgn if a < b else -sgn)
            W = U[:, cols] * np.array(signs, dtype=U.dtype)
            code = np.zeros(U.shape[0], dtype=np.int64)
            for k in range(len(pairs)):
                code = code * base + (W[:, k].astype(np.int64) + off)
            if best is None:
                best, bestU = code, W.copy()
            else:
                upd = code < best
                best = np.where(upd, code, best)
                bestU[upd] = W[upd]
    _, idx = np.unique(best, return_index=True)
    return bestU[idx]


def summarize_scan(rows, label, out=None, top=12):
    st = collections.Counter(r["status"] for r in rows)
    found = sorted((r for r in rows if r["status"] == "found"), key=lambda r: -r["iso"])
    print("%s: %d quivers; another quiver of height <= w found for %d; search closed below the cap for %d "
          "(of these %d met no cap at all); over budget %d"
          % (label, len(rows), st["found"], st["cap"] + st["closed"], st["closed"], st["budget"]))
    if found:
        hist = collections.Counter(r["iso"] for r in found)
        print("   escape levels (level: count): %s" % " ".join("%d:%d" % kv for kv in sorted(hist.items())))
        for r in found[:top]:
            print("   %d  %s  route of %d steps, %d quivers searched" % (r["iso"], r["start"], r["path_len"], r["popped"]))
    if out:
        with gzip.open(out, "wt") as f:
            for r in rows:
                if r["status"] != "cap":
                    f.write(json.dumps(r) + "\n")
            f.write(json.dumps({"summary": dict(st), "label": label}) + "\n")


def cmd_census(args):
    import numpy as np
    n, w = args.n, args.w
    U = isolated(n, list(range(-w, w + 1)), w, w)
    if args.min_twos:
        U = U[(np.abs(U) == 2).sum(axis=1) >= args.min_twos]
    CU = dedupe(U, n)
    cap = args.cap or 16 * w ** (n - 2)
    lines = ["%d %d %d %d %d %s" % (n, w, cap, args.budget, args.prune, " ".join(str(int(x)) for x in row)) for row in CU]
    rows = search(lines, workers=args.workers, chunk=200)
    label = "n=%d w=%d isolated quivers%s, cap %d, budget %d" % (n, w, " with at least %d entries +-2" % args.min_twos if args.min_twos else "",
                                                                cap, args.budget)
    summarize_scan(rows, label, args.out)
    if args.recheck_cap:
        todo = [r for r in rows if r["status"] != "found"]
        if args.recheck_sample and len(todo) > args.recheck_sample:
            import random
            random.Random(1).shuffle(todo)
            todo = todo[:args.recheck_sample]
        lines = ["%d %d %d %d %d %s" % (n, w, args.recheck_cap, args.recheck_budget, args.prune, " ".join(map(str, r["start"]))) for r in todo]
        summarize_scan(search(lines, workers=args.workers, chunk=50), "   recheck of %d unresolved quivers at cap %d, budget %d"
                       % (len(todo), args.recheck_cap, args.recheck_budget))


def cmd_census_summary(args):
    """Summary of stored census rows (.jsonl or .jsonl.gz), and the largest escape level by the number of entries +-2."""
    op = gzip.open if args.file.endswith(".gz") else open
    rows = []
    stored = None
    with op(args.file, "rt") as f:
        for line in f:
            line = line.strip()
            if not line.endswith("}"):
                continue
            r = json.loads(line)
            if "summary" in r:
                stored = r
            else:
                rows.append(r)
    if stored:
        print("stored summary: %s" % stored)
    summarize_scan(rows, args.label or args.file, args.out)
    by = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "found":
            by[sum(1 for v in r["start"] if abs(v) == 2)].append(r["iso"])
    for k in sorted(by):
        print("   entries +-2: %d  quivers with an escape: %d  largest escape levels: %s" % (k, len(by[k]), sorted(by[k])[-4:]))


def cmd_templates(args):
    k = args.k
    U = isolated(5, [-k, -(k - 1), -1, 0, 1, k - 1, k], 2 * k, k)
    CU = dedupe(U, 5)
    lines = ["5 %d %d %d 1 %s" % (k, args.cap, args.budget, " ".join(str(int(x)) for x in row)) for row in CU]
    rows = search(lines, workers=args.workers, chunk=200)
    summarize_scan(rows, "templates k=%d (entries 0, +-1, +-%d, +-%d; every mutation above %d), cap %d" % (k, k - 1, k, 2 * k, args.cap), args.out)
    todo = [r for r in rows if r["status"] != "found"]
    lines = ["5 %d %d %d 1 %s" % (k, args.cap2, args.budget, " ".join(map(str, r["start"]))) for r in todo]
    summarize_scan(search(lines, workers=args.workers, chunk=100), "   the %d unresolved templates again at cap %d" % (len(todo), args.cap2))


FIXED = {
    # (b12, b13, b14, b23, b24, b34) of the 4-vertex quiver on the vertices 1..4
    "rstar": lambda a: [-3, -2, 2, -2, -2, -3],                      # a square of weight-2 arrows with two diagonals of weight 3
    "square": lambda a: [-a, -2, 2, -2, -2, -a],                     # the same square with diagonals of weight a
    "db1": lambda a: [-(a + 1), -2, a, -a, -2, -(a + 1)],
    "db2": lambda a: [-(a + 1), -a, 2, -2, -a, -(a + 1)],
    "bounce": lambda a: [-2, 0, a, 1, -(a + 1), 2],                  # one weight-2 pair with two walls of slope 1 (a = bounce length)
}


def cmd_rows(args):
    R = FIXED[args.kind](args.a)
    k = args.k
    w = max(k, max(abs(x) for x in R))
    cap = args.capf * w ** 3
    lines = ["5 %d %d %d 1 %s" % (w, cap, args.budget, " ".join(map(str, list(r) + R))) for r in itertools.product(range(-k, k + 1), repeat=4)]
    rows = search(lines, workers=args.workers, chunk=50)
    summarize_scan(rows, "fixed quiver %s(a=%d) = %s with every row of entries <= %d (w = %d), cap %d, budget %d"
                   % (args.kind, args.a, R, k, w, cap, args.budget), args.out, top=6)


def labelled_route(B, cap, budget=5_000_000, prune=1):
    r = search([task_line(B, cap, budget, prune)], flag="--path")[0]
    if r["status"] != "found":
        return r, None, None
    seq, mats = [], [B]
    for key in r["path"][1:]:
        for v in range(len(B)):
            N = mut(B, v)
            if canon(N) == tuple(key):
                seq.append(v)
                B = N
                mats.append(B)
                break
        else:
            raise RuntimeError("route step not found")
    return r, seq, mats


def cmd_path(args):
    B = from_upper(args.quiver, args.n)
    r, seq, mats = labelled_route(B, args.cap)
    print("status %s, escape level %s, %d quivers searched" % (r["status"], r.get("iso"), r["popped"]))
    if seq is None:
        return
    print("mutations:", "".join(map(str, seq)))
    print("heights:", r["levels"])
    if args.full:
        for i, M in enumerate(mats):
            print(i, "-" if i == 0 else seq[i - 1], ht(M), " | ".join(" ".join("%4d" % x for x in row) for row in M))


def cmd_selftest(args):
    import random
    import numpy as np
    sys.path.insert(0, HERE)
    from mutation_path import mutate as ref_mutate
    rng = random.Random(5)
    ok = True
    for _ in range(20000):
        n = rng.choice((4, 5, 6))
        u = [rng.randint(-6, 6) for _ in range(n * (n - 1) // 2)]
        B = from_upper(u, n)
        k = rng.randrange(n)
        ok &= mut(B, k) == tuple(map(tuple, ref_mutate(np.array(B, dtype=np.int64), k).tolist()))
    print("Python kernel against mutation_path.mutate on 20,000 random mutations (n = 4, 5, 6): %s" % ok)
    G = lambda k: from_upper([k, -k, -k, 0, k, -(k - 1)], 4)
    gk = [escape(G(k), 4 * k ** 3, prune=p).get("iso") for p in (0, 1) for k in range(3, 13)]
    print("G_k, k = 3..12, escape level k(k - 1) with and without fork pruning: %s" % (gk == [k * (k - 1) for k in range(3, 13)] * 2))
    ext = {3: [-1, -3, 2, 3, -3, 2], 4: [-3, 4, -4, -2, -4, 4], 5: [-5, -2, 4, -5, 0, -5], 6: [6, -6, -6, -2, 5, -6],
           7: [-7, -6, 5, -7, 2, -6], 8: [2, -6, -8, 8, -8, 7], 9: [-2, -9, 8, 8, -9, -4]}
    want = {3: 12, 4: 28, 5: 45, 6: 66, 7: 79, 8: 101, 9: 144}
    got = {b: [escape(from_upper(u, 4), 2000, prune=p).get("iso") for p in (0, 1)] for b, u in ext.items()}
    print("census extremes of note 10 (births 3..9), escape levels with and without pruning: %s  -> %s"
          % (got, all(v == [want[b]] * 2 for b, v in got.items())))
    Qt = lambda t: from_upper([-t * t, -(t * t - 1), 2 * t, -2, t * (t - 1), -t * t], 4)
    Hq = lambda t: 2 * t ** 4 - t ** 3 - t * t + 2 * t
    q52 = [escape(Qt(t), 2 * Hq(t), prune=0).get("iso") for t in range(3, 11)]
    print("Q_t of note 15, t = 3..10, escape level H_t = 2t^4 - t^3 - t^2 + 2t: %s" % (q52 == [Hq(t) for t in range(3, 11)]))
    nf = 0
    okf = True
    while nf < 20000:
        n = rng.choice((4, 5))
        B = from_upper([rng.choice((-1, 1)) * rng.randint(2, 12) for _ in range(n * (n - 1) // 2)], n)
        r = fork_return(B)
        if r is None:
            continue
        nf += 1
        for k in range(n):
            if k != r:
                N = mut(B, k)
                okf &= fork_return(N) == k and all(abs(N[i][j]) >= abs(B[i][j]) for i in range(n) for j in range(n))
    print("Warkentin's Lemma 2.5 on %d random forks (n = 4, 5): the mutation away from the point of return is a fork "
          "with that point of return and no smaller entry: %s" % (nf, okf))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sub.add_parser("selftest")
    s = sub.add_parser("family")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=16)
    s.add_argument("--prune", type=int, default=0)
    s.add_argument("--out", default=None)
    s = sub.add_parser("family_plus")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=16)
    s.add_argument("--prune", type=int, default=0)
    s.add_argument("--out", default=None)
    s = sub.add_parser("pycheck")
    s.add_argument("--tmin", type=int, default=2)
    s.add_argument("--tmax", type=int, default=8)
    s = sub.add_parser("core")
    s.add_argument("--t", type=int, nargs="+", default=[2, 3, 4, 5, 6, 7, 8])
    s.add_argument("--branches", action="store_true")
    s.add_argument("--plus", action="store_true")
    s = sub.add_parser("grid")
    s.add_argument("--workers", type=int, default=6)
    s = sub.add_parser("pendant")
    s.add_argument("--n", type=int, nargs="+", default=[6, 7])
    s.add_argument("--t", type=int, nargs="+", default=[2, 3, 4])
    s.add_argument("--prune", type=int, default=0)
    s.add_argument("--budget", type=int, default=6_000_000)
    s = sub.add_parser("star")
    s.add_argument("--spec", nargs="+", default=["1,2,3,8,4,8", "2,2,3,8,4,8", "2,3,5,18,9,18", "2,4,7,32,16,32", "3,2,5,12,6,12", "3,4,11,48,24,48"])
    s = sub.add_parser("census")
    s.add_argument("--n", type=int, required=True)
    s.add_argument("--w", type=int, required=True)
    s.add_argument("--cap", type=int, default=0)
    s.add_argument("--budget", type=int, default=20000)
    s.add_argument("--prune", type=int, default=1)
    s.add_argument("--min-twos", type=int, default=0)
    s.add_argument("--workers", type=int, default=6)
    s.add_argument("--recheck-cap", type=int, default=0)
    s.add_argument("--recheck-budget", type=int, default=200000)
    s.add_argument("--recheck-sample", type=int, default=0)
    s.add_argument("--out", default=None)
    s = sub.add_parser("census_summary")
    s.add_argument("--file", required=True)
    s.add_argument("--label", default=None)
    s.add_argument("--out", default=None)
    s = sub.add_parser("templates")
    s.add_argument("--k", type=int, default=7)
    s.add_argument("--cap", type=int, default=5000)
    s.add_argument("--cap2", type=int, default=1000000)
    s.add_argument("--budget", type=int, default=5000)
    s.add_argument("--workers", type=int, default=6)
    s.add_argument("--out", default=None)
    s = sub.add_parser("rows")
    s.add_argument("--kind", choices=sorted(FIXED), required=True)
    s.add_argument("--a", type=int, default=2)
    s.add_argument("--k", type=int, required=True)
    s.add_argument("--capf", type=int, default=16)
    s.add_argument("--budget", type=int, default=100000)
    s.add_argument("--workers", type=int, default=6)
    s.add_argument("--out", default=None)
    s = sub.add_parser("path")
    s.add_argument("--n", type=int, required=True)
    s.add_argument("--quiver", type=int, nargs="+", required=True)
    s.add_argument("--cap", type=int, default=100000)
    s.add_argument("--full", action="store_true")
    args = ap.parse_args()
    globals()["cmd_" + args.cmd](args)


if __name__ == "__main__":
    main()
