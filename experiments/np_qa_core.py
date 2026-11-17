#!/usr/bin/env python
"""
np_qa_core.py -- the core of Q_a below H(a) (Conjecture 18.7a): which quivers a reduced route from Q_a can use.

Q_a = (-(a-3), a-2, a+1, -(a+1) | R_a) and H(a) are those of note 18 (np_rowwalk.py).  The core is the set of quivers,
up to relabelling, that Q_a reaches through quivers of height < H(a) without entering a fork; by Lemma 15.5 a reduced
route from Q_a to a quiver of height <= a + 1 below H(a) stays in it.

The search (np_qa_core.c) is grown from the whole first half of the route of Theorem 18.4 at once.  Each seed is
written in the frame x = 0, p = 1, q = 2, r = 3, s = 4 of its position on the bounce cycle: the seed (n, j) is
W_m(j) with the state (A, B, U, V) = (b_px, b_qx, b_xr, b_xs) it has before the n-th turn.  Every member of the core
then carries the seed it is nearest to, the word of mutations (in the names x, p, q, r, s of that seed) that leads to
it, and its matrix in that frame.

Subcommands (run from experiments/ with python -I):
  build       compile np_qa_core.c into ~/.cache/qmb-np/np_qa_core
  core        sizes of the core for a range of a, by first mutation off the route
  anatomy     the core in full: route, lines of steps beyond the ends of the rounds, the rest; exits along the lines
  lines       the closed forms of the two families of lines against integer mutation, and their counts
  branches    the members off the route and off the lines, by kind (stretch of the seed, skeleton of the word)
  region      where the mutation at r of a route quiver is a member: A + (m - j)|U| < H(a)
  kinds       kinds of the stored members in mode chain, for larger a
  ends        how far the core reaches into the 4-vertex quivers that are not forks, off the bounce cycle
  forkless    the quivers of the 4-vertex class of R_a that are not forks, below a cap; the spiral
  spiral      ten mutations at p, q, s return their triangle and multiply the row of r (the proposition on the spiral)
  prefork     the core without expanding heavy pre-forks
  crosscheck  the number of members against np_barrier and against mode plain
  family      the search from Q_a alone, with fork pruning (mode chain) or without (mode chain-nofork)
  compare18   the counts without pruning against those of Theorem 18.5
  rerun       part of the two family runs again, against their stored results
"""
import argparse
import collections
import itertools
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import np_rowwalk as rw
from np_corridor import mut, ht, canon, upper, from_upper, neg, fork_return

BIN = os.environ.get("NP_QA_CORE_BIN") or os.path.expanduser("~/.cache/qmb-np/np_qa_core")
CACHE = os.path.expanduser("~/.cache/qmb-np/qa_core")
NAMES = "xpqrs"
FRAME = (1, 2, 3, 4)                      # (p, q, r, s)
SWAP_PQ = (0, 2, 1, 3, 4)
SWAP_RS = (0, 1, 2, 4, 3)


def relabel(B, p):
    return tuple(tuple(B[p[i]][p[j]] for j in range(5)) for i in range(5))


def cmd_build(args):
    os.makedirs(os.path.dirname(BIN), exist_ok=True)
    subprocess.run(["gcc", "-O2", "-Wall", "-o", BIN, os.path.join(HERE, "np_qa_core.c")], check=True)
    print("built", BIN)


def seeds(a, check=True):
    """The first half of the route of Theorem 18.4 below H(a): a list of (n, j, state, matrix in the frame x p q r s).
    n is the number of the next turn, j the position on W_m."""
    m, H = 2 * a + 1, rw.Hfam(a)
    c = 4 * a * a - 5 * a + 1
    nturn = 2 * a + 1 + (c // 2 + 2 if a % 2 else (c + 3) // 2)
    st = (a + 1, a - 3, a - 2, a + 1)
    j = a + 1
    out = []
    X = rw.Wm(m, j, FRAME, st)
    if check:
        assert canon(X) == canon(rw.Qa(a))
    for n in range(1, nturn + 1):
        while True:
            if check:
                assert X == rw.Wm(m, j, FRAME, st)
            out.append((n, j, st, X))
            if j == m:
                break
            st = rw.rule_step(m, j, st)
            X = relabel(mut(X, 1), SWAP_PQ)
            j += 1
        st = rw.rule_turn(st)
        X = relabel(mut(X, 3), SWAP_RS)
        j = 0
    return [s for s in out if ht(s[3]) < H]


def dtype(n=5):
    mm = n * (n - 1) // 2
    return np.dtype([("lab", "<i4", (mm,)), ("parent", "<i4"), ("root", "<i4"), ("depth", "<i4"), ("move", "<i4"),
                     ("second", "<i4"), ("chain", "<i4"), ("code", "<i4", (n,)), ("target", "<i4", (n,)), ("clen", "<i4", (n,))])


def run_core(a, budget=None, keep=True, seedlist=None, H=None, w=None, tag="", mode="plain", store=True):
    """Returns (seeds, stored members, summary).  mode "chain" stores only the members that are seeds, have height
    <= w, or do not have exactly two neighbours in the core; the others are counted (np_qa_core.c)."""
    sd = seeds(a) if seedlist is None else seedlist
    H = rw.Hfam(a) if H is None else H
    w = a + 1 if w is None else w
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "core_a%d%s%s.bin" % (a, "" if mode == "plain" else "_" + mode, tag))
    if budget is None:
        budget = int(6 * a ** 5 + 200000) if mode == "plain" else int(40 * a ** 3 + 200000)
    if not (keep and os.path.exists(path + ".json") and (os.path.exists(path) or not store)):
        inp = "5 %d %d %d %d\n" % (H, w, len(sd), budget) + "\n".join(" ".join(map(str, upper(s[3]))) for s in sd) + "\n"
        res = subprocess.run([BIN, path if store else "-", mode], input=inp, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError("np_qa_core failed: %s %s" % (res.stdout, res.stderr))
        with open(path + ".json", "w") as f:
            f.write(res.stdout)
    with open(path + ".json") as f:
        summary = json.loads(f.read())
    if not store:
        return sd, None, summary
    with open(path, "rb") as f:
        cnt = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        arr = np.frombuffer(f.read(), dtype=dtype())
    assert cnt == len(arr) == summary["stored"]
    return sd, arr, summary


def _extend(prev, c):
    if prev:
        y, z, L = prev[-1]
        if z is None and c != y:
            return prev[:-1] + ((y, c, 2),)
        if z is not None and c == (y if L % 2 == 0 else z):
            return prev[:-1] + ((y, z, L + 1),)
    return prev + ((c, None, 1),)


def words(arr):
    """For every stored member the word from its root in the names x p q r s, as a tuple of runs (y, z, L): the L
    letters y z y z ... (z is None for a single letter).  Long lines of steps are one run.  In chain mode the members
    passed through on the way from the parent are part of the word."""
    out = [()] * len(arr)
    par, mv, sec, ch = arr["parent"].tolist(), arr["move"].tolist(), arr["second"].tolist(), arr["chain"].tolist()
    for u in range(len(arr)):                       # parents come first
        if par[u] < 0:
            continue
        c1 = NAMES[mv[u]]
        w = _extend(out[par[u]], c1)
        k = abs(ch[u])
        if k:
            c2 = NAMES[sec[u]]
            w = _extend(w, c2)
            if k > 1:
                y, z, L = w[-1]
                if z is not None and {y, z} == {c1, c2}:
                    w = w[:-1] + ((y, z, L + k - 1),)
                else:                               # c2 went into a run on another pair: the rest starts a new one
                    w = w + ((c1, c2, k - 1),) if k > 2 else w + ((c1, None, 1),)
        out[u] = w
    return out


def word_str(runs, k=None):
    """The word as a string; with k, runs of length >= k are written (yz)^L."""
    out = []
    for y, z, L in runs:
        if z is None:
            out.append(y)
        elif k is not None and L >= k:
            out.append("(%s%s)^%d" % (y, z, L))
        else:
            out.append("".join(y if i % 2 == 0 else z for i in range(L)))
    return "".join(out)


def pattern(runs, k=4):
    """The word with every run of length >= k written (yz)^k: the kind of a branch."""
    return "".join(y if z is None else "(%s%s)^k" % (y, z) if L >= k else "".join(y if i % 2 == 0 else z for i in range(L))
                   for y, z, L in runs)


def is_line(runs):
    """A word of steps on the pair (p, q) only."""
    return len(runs) == 1 and runs[0][0] in "pq" and (runs[0][1] is None or runs[0][1] in "pq")


def cmd_core(args):
    for a in range(args.amin, args.amax + 1):
        sd, arr, summ = run_core(a, keep=not args.fresh, mode=args.mode)
        H, w = rw.Hfam(a), a + 1
        wd = words(arr)
        first = collections.Counter(x[0][0] for x in wd if x)
        print("a=%d w=%d H=%d: core %d quivers (%d stored, %d passed through), %d on the route (seeds); members of height <= w: %d; "
              "forks of height <= w among the exits: %d; exits of the stored members: member %d, height >= H %d, fork %d"
              % (a, w, H, summ["members"], summ["stored"], summ["passed_through"], summ["seeds"], summ["members_of_height_le_w"],
                 summ["forks_of_height_le_w"], summ["exits_member"], summ["exits_high"], summ["exits_fork"]), flush=True)
        print("   stored members by first mutation off the route: %s" % " ".join("%s:%d" % (k, first[k]) for k in NAMES))


def _family_one(arg):
    a, mode = arg
    t0 = time.time()
    Q = rw.Qa(a)
    budget = 12 * a ** 3 + 100000 if mode == "chain" else 24 * a ** 3 + 200000
    _, _, summ = run_core(a, seedlist=[(1, a + 1, None, Q)], mode=mode, store=False, tag="_single", budget=budget)
    summ["a"] = a
    summ["seconds"] = round(time.time() - t0, 1)
    return summ


def cmd_family(args):
    """The search of Theorem 18.5, with fork pruning (mode chain) or without (mode chain-nofork), without storing the
    members that have exactly two neighbours."""
    print("# Q_a, the set of quivers reached from Q_a through quivers of height < H(a), %s (np_qa_core.c, mode %s, one seed).  "
          "ok = the set is closed, Q_a is its only member of height <= a + 1%s."
          % ("forks not expanded" if args.mode == "chain" else "no pruning", args.mode,
             ", and no fork of height <= a + 1 is met" if args.mode == "chain" else ""))
    todo = [(a, args.mode) for a in range(args.amax, args.amin - 1, -1)]
    assert rw.Hfam(args.amax) < 2 ** 31
    rows = {}
    with Pool(args.workers) as pool:
        for r in pool.imap_unordered(_family_one, todo, chunksize=1):
            rows[r["a"]] = r
            a = r["a"]
            ok = r["status"] == "closed" and r["members_of_height_le_w"] == 1 and r["forks_of_height_le_w"] == 0 and r["chain_sum_is_even"]
            r["ok"] = ok
            print("a=%d w=%d H=%d: %d quivers below H (%d stored, %d passed through, longest chain %d), of height <= w: %d, forks of "
                  "height <= w met: %d, %s (%.1fs)" % (a, a + 1, r["H"], r["members"], r["stored"], r["passed_through"], r["longest_chain"],
                                                       r["members_of_height_le_w"], r["forks_of_height_le_w"], "ok" if ok else "FAILED",
                                                       r["seconds"]), flush=True)
    bad = [a for a in sorted(rows) if not rows[a]["ok"]]
    print("# a = %d..%d: %d values, failures: %s" % (args.amin, args.amax, len(rows), bad or "none"))
    if args.out:
        with open(args.out, "w") as f:
            for a in sorted(rows):
                f.write(json.dumps(rows[a]) + "\n")


P4 = list(itertools.permutations(range(4)))


def canon4(u):
    """Canonical form of the 4-vertex quiver with upper triangle u = (b12, b13, b14, b23, b24, b34)."""
    B = from_upper(list(u), 4)
    return min(tuple(B[p[i]][p[j]] for i in range(4) for j in range(i + 1, 4)) for p in P4)


def skeleton(runs):
    """The word with the lengths of its runs dropped: the pairs of vertices it steps on, in order."""
    return " ".join(y if z is None else "".join(sorted(y + z)) for y, z, L in runs)


def stretch(a, n):
    """The four stretches of the first half (Theorem 18.4): turns 1, 2, 3..2a+1 and those after the bottom."""
    return "S1" if n == 1 else "S2" if n == 2 else "S3" if n <= 2 * a + 1 else "S4"


def cmd_kinds(args):
    """The stored members of the core (chain mode, grown from the route) sorted by stretch of the root and skeleton of
    the word: how many kinds there are, and how that number moves with a."""
    print("# kinds of the members of the core that are not passed through (np_qa_core.c, mode chain, seeds = the first half of "
          "the route).  A kind is (stretch of the root, skeleton of the word).  4-vertex parts: the quiver without x.")
    prev = {}
    for a in args.a:
        t0 = time.time()
        m = 2 * a + 1
        sd, arr, summ = run_core(a, mode="chain", keep=not args.fresh)
        wd = words(arr)
        roots = arr["root"].tolist()
        kinds = collections.Counter()
        nruns = collections.Counter()
        for u, w in enumerate(wd):
            if w:
                kinds[(stretch(a, sd[roots[u]][0]), skeleton(w))] += 1
                nruns[len(w)] += 1
        sub = np.ascontiguousarray(arr["lab"][:, 4:])
        uniq = np.unique(sub, axis=0)
        parts = {canon4(tuple(int(v) for v in u)) for u in uniq}
        nonfork = [c for c in parts if fork_return(from_upper(list(c), 4)) is None]
        cyc = {canon4(upper(rw.sub4(rw.Wm(m, j)))) for j in range(0, m + 1)}
        off = [c for c in nonfork if c not in cyc]
        line = ("a=%d: core %d, stored %d (route %d); kinds %d, with >= a members %d; runs in the longest word %d; words by number "
                "of runs %s; 4-vertex parts of the stored members that are not forks: %d, of these off the cycle: %d (%.0fs)"
                % (a, summ["members"], summ["stored"], summ["seeds"], len(kinds), sum(1 for v in kinds.values() if v >= a), max(nruns),
                   " ".join("%d:%d" % (k, nruns[k]) for k in sorted(nruns)), len(nonfork), len(off), time.time() - t0))
        print(line, flush=True)
        old = prev.get(a % 2)
        if old is not None:
            new = sorted(set(kinds) - set(old[1]))
            gone = sorted(set(old[1]) - set(kinds))
            print("   against a=%d: %d new kinds%s; %d kinds gone%s"
                  % (old[0], len(new), (": " + "; ".join("%s %s (%d)" % (k[0], k[1], kinds[k]) for k in new[:args.show])) if new else "",
                     len(gone), (": " + "; ".join("%s %s" % k for k in gone[:args.show])) if gone else ""), flush=True)
        prev[a % 2] = (a, kinds)


def cmd_anatomy(args):
    """The core in full (mode plain), sorted into the route, the lines of steps beyond the two ends of each round, and
    the rest; the lengths of the lines against their closed forms; the exits at x, r, s along the lines."""
    print("# anatomy of the core of Q_a below H(a) (np_qa_core.c, mode plain, seeds = the first half of the route).")
    print("# backward line of a round: steps q, p, q, ... from its position 0; forward line: steps p, q, p, ... from its position m.")
    C = "MHFf"
    for a in args.a:
        m, H = 2 * a + 1, rw.Hfam(a)
        sd, arr, summ = run_core(a, keep=not args.fresh)
        wd = words(arr)
        roots = arr["root"].tolist()
        codes = arr["code"]
        cat = collections.Counter()
        blen, flen = collections.Counter(), collections.Counter()
        ex = collections.Counter()
        withx = 0
        for u, w in enumerate(wd):
            n, j, st, _ = sd[roots[u]]
            S = stretch(a, n)
            if not w:
                cat["route"] += 1
                continue
            withx += any("x" in (y, z) for y, z, L in w)
            if is_line(w):
                back = w[0][0] == "q"
                cat[("backward line " if back else "forward line ") + S] += 1
                (blen if back else flen)[(n, j)] = max((blen if back else flen)[(n, j)], w[0][2])
                if S == ("S4" if back else "S3"):
                    ex[("backward S4 " if back else "forward S3 ") + C[codes[u][0]] + C[codes[u][3]] + C[codes[u][4]]] += 1
            else:
                cat["other, first mutation " + w[0][0]] += 1
        sub = np.ascontiguousarray(arr["lab"][:, 4:])
        uniq, inv = np.unique(sub, axis=0, return_inverse=True)
        isfork = np.array([fork_return(from_upper([int(v) for v in u], 4)) is not None for u in uniq])
        over_forks = int(isfork[inv].sum())
        print("a=%d w=%d H=%d: core %d = route %d + backward lines %d + forward lines %d + others %d; members whose word has a mutation "
              "at x: %d; members whose 4-vertex part is a fork: %d; of height <= w: %d"
              % (a, a + 1, H, len(arr), cat["route"], sum(v for k, v in cat.items() if k.startswith("backward")),
                 sum(v for k, v in cat.items() if k.startswith("forward")), sum(v for k, v in cat.items() if k.startswith("other")),
                 withx, over_forks, summ["members_of_height_le_w"]), flush=True)
        print("   " + "; ".join("%s %d" % (k, cat[k]) for k in sorted(cat) if k != "route"))
        # lengths against the closed forms: A + 3 backward in S4, A + 4 forward in S3, A the entry b_px of the root
        okb = [(n, L, sd_state(sd, n, 0)[0] + 3) for (n, j), L in sorted(blen.items()) if stretch(a, n) == "S4"]
        okf = [(n, L, sd_state(sd, n, m)[0] + 4) for (n, j), L in sorted(flen.items()) if stretch(a, n) == "S3"]
        badb = [(n, L, e) for n, L, e in okb if L != e]
        badf = [(n, L, e) for n, L, e in okf if L != e]
        print("   backward lines in S4: %d, of length A + 3: %d, others (turn, length, A + 3): %s" % (len(okb), len(okb) - len(badb), badb[:6]))
        print("   forward lines in S3: %d, of length A + 4: %d, others (turn, length, A + 4): %s" % (len(okf), len(okf) - len(badf), badf[:6]))
        print("   exits at x, r, s of the members of these lines (M member, H height >= H, F fork): %s"
              % "; ".join("%s %d" % (k, ex[k]) for k in sorted(ex)))


def sd_state(sd, n, j):
    for nn, jj, st, _ in sd:
        if nn == n and jj == j:
            return st
    raise KeyError((n, j))


def BLform(m, k, st):
    """The quiver k backward steps from position 0 of a round with state st = (A, B, U, V), B = -(A - 1), for 2 <= k <= A
    (Proposition on the lines).  Frame x p q r s."""
    A, B, U, V = st
    M = [[0] * 5 for _ in range(5)]

    def setb(i, j, v):
        M[i][j] = v
        M[j][i] = -v
    setb(2, 1, 2)
    setb(1, 3, m + k), setb(2, 3, -(m + k + 1))
    setb(1, 4, k - 2), setb(2, 4, -(k - 1))
    setb(1, 0, A - k), setb(2, 0, -(A - k - 1))
    setb(3, 4, m - 1), setb(0, 3, U), setb(0, 4, V + A - 1)
    return tuple(tuple(r) for r in M)


def FLform(m, k, st):
    """The quiver k forward steps from position m of a round with state st = (A, B, U, V), B = -(A + 1), for 2 <= k <= A + 1."""
    A, B, U, V = st
    M = [[0] * 5 for _ in range(5)]

    def setb(i, j, v):
        M[i][j] = v
        M[j][i] = -v
    setb(2, 1, 2)
    setb(1, 3, k - 2), setb(2, 3, -(k - 3))
    setb(1, 4, m + k), setb(2, 4, -(m + k - 1))
    setb(1, 0, A - k), setb(2, 0, -(A - k + 1))
    setb(3, 4, m - 1), setb(0, 3, U - (A - 1)), setb(0, 4, V)
    return tuple(tuple(r) for r in M)


def cmd_lines(args):
    """The closed forms of the two families of lines against integer mutation, and the count of their members."""
    print("# the lines beyond the ends of the rounds: closed forms BL (backward from position 0, rounds with slopes (1, 2)) and "
          "FL (forward from position m, rounds with slopes (-1, -(2a-1))) against integer mutation; frame x p q r s.")
    for a in range(args.amin, args.amax + 1):
        m, H = 2 * a + 1, rw.Hfam(a)
        sd = seeds(a)
        ok = True
        nb = nf = 0
        cb = cf = 0
        endb, endf = collections.Counter(), collections.Counter()
        prodb = 0
        for n, j, st, X in sd:
            A, B, U, V = st
            if j == 0 and B == -(A - 1) and n > m + 1:           # a round with slopes (1, 2), after the bottom
                nb += 1
                Y = X
                k = 0
                while True:
                    Y = relabel(mut(Y, 2), SWAP_PQ)
                    k += 1
                    if ht(Y) >= H:
                        endb["height >= H after %s steps" % ("A + %d" % (k - A) if k > A else "fewer than A")] += 1
                        break
                    if fork_return(Y) is not None:
                        endb["fork after A + %d steps" % (k - A)] += 1
                        break
                    cb += 1
                    if 2 <= k <= A:
                        ok &= Y == BLform(m, k, st)
                        prodb += (m + k) * (m + k + 1) >= H + 2 and (k - 2) * (k - 1) >= H + 2 and (A - k) * (A - k - 1) >= H + 2
            if j == m and B == -(A + 1) and 3 <= n <= m:          # a round with slopes (-1, -(2a-1))
                nf += 1
                Y = X
                k = 0
                while True:
                    Y = relabel(mut(Y, 1), SWAP_PQ)
                    k += 1
                    if ht(Y) >= H:
                        endf["height >= H"] += 1
                        break
                    if fork_return(Y) is not None:
                        endf["fork after A + %d steps" % (k - A)] += 1
                        break
                    cf += 1
                    if 2 <= k <= A + 1:
                        ok &= Y == FLform(m, k, st)
        print("a=%d: %d backward lines with %d quivers below H before the first fork, %d forward lines with %d; closed forms %s; "
              "backward lines end: %s; forward lines end: %s; members of backward lines with all three products >= H + 2 (Lemma on "
              "exits off a line): %d" % (a, nb, cb, nf, cf, "agree" if ok else "FAILED", dict(endb), dict(endf), prodb), flush=True)


def W4(m, j):
    return rw.sub4(rw.Wm(m, j, FRAME))


def forkless4(a, cap):
    """The quivers of the 4-vertex class of R_a reached from the cycle W_m(j), 0 <= j <= m, through quivers of height
    < cap that are not forks.  Returns {canonical form: (position of the root, word in p q r s, quiver)}."""
    m = 2 * a + 1
    seen = {}
    todo = collections.deque()
    for j in range(0, m + 1):
        B = W4(m, j)
        seen[canon(B)] = (j, "", B)
        todo.append((B, j, ""))
    while todo:
        B, j, w = todo.popleft()
        for v in range(4):
            N = mut(B, v)
            if ht(N) >= cap or fork_return(N) is not None:
                continue
            c = canon(N)
            if c not in seen:
                seen[c] = (j, w + "pqrs"[v], N)
                todo.append((N, j, w + "pqrs"[v]))
    return seen


def cmd_forkless(args):
    """The 4-vertex quivers of the class of R_a that are not forks: how many lie below a cap, and the spiral."""
    print("# the class of R_a on four vertices: quivers that are not forks, reached from the bounce cycle through such quivers "
          "of height < cap.  Entries: number off the cycle / largest distance from the cycle.")
    caps = [("4a^2", lambda a, H: 4 * a * a), ("H", lambda a, H: H), ("4H", lambda a, H: 4 * H), ("16H", lambda a, H: 16 * H),
            ("256H", lambda a, H: 256 * H), ("H^2", lambda a, H: H * H), ("H^3", lambda a, H: H ** 3)]
    print("# caps: %s" % ", ".join(c[0] for c in caps))
    for a in args.a:
        H = rw.Hfam(a)
        row = []
        for name, f in caps:
            seen = forkless4(a, f(a, H))
            off = [v for v in seen.values() if v[1]]
            row.append("%d/%d" % (len(off), max(len(v[1]) for v in off)))
        print("a=%d H=%d: %s" % (a, H, "  ".join(row)), flush=True)
    for a, capname, capf in [(args.a[0], "H^3", lambda H: H ** 3), (args.a[-1], "H", lambda H: H)]:
        m, H = 2 * a + 1, rw.Hfam(a)
        seen = forkless4(a, capf(H))
        off = [v for v in seen.values() if v[1]]
        byj = collections.Counter(v[0] for v in off)
        print("a=%d, cap %s: %d quivers off the cycle, by position of the root: %s" % (a, capname, len(off), dict(sorted(byj.items()))))
        j, w, _ = max(off, key=lambda v: (len(v[1]), v[0] == 0))
        X = W4(m, j)
        hts, light = [ht(X)], []
        for c in w:
            X = mut(X, "pqrs".index(c))
            hts.append(ht(X))
            light.append(sum(1 for i in range(4) for k in range(i + 1, 4) if abs(X[i][k]) < 2))
        print("   the longest word, from position %d: %s" % (j, word_str(tuple(_runs(w)), 3)))
        print("   heights along it: %s" % hts)
        print("   pairs with fewer than two arrows along it: %s" % light)
        d = [hts[i + 1] - hts[i] for i in range(len(hts) - 1)]
        steps = []
        for i in range(1, len(d)):
            if d[i] == d[i - 1] and (not steps or steps[-1] != d[i]):
                steps.append(d[i])
        print("   common differences of the runs: %s; ratios: %s" % (steps, " ".join("%.4f" % (steps[i + 1] / steps[i]) for i in range(len(steps) - 1))))
        print("   d(k+1) - 7 d(k) + d(k-1) for the differences from the second on: %s (m - 4 = %d); d(2) = 2m + 3 = %d, d(3) = 15m + 16 = %d"
              % ([steps[i + 1] - 7 * steps[i] + steps[i - 1] for i in range(2, len(steps) - 1)], m - 4, 2 * m + 3, 15 * m + 16))


def _runs(w):
    out = ()
    for c in w:
        out = _extend(out, c)
    return out


def cmd_region(args):
    """Where the mutation at r of a route quiver is a member of the core: after the bottom, with U < 0, exactly where
    A + (m - j)|U| < H(a)."""
    print("# route quivers (t, j) after the bottom with U < 0: is mu_r a member of the core, against the inequality "
          "A + (m - j)|U| < H(a) for its entry b_px (np_qa_core.c, mode chain).")
    for a in args.a:
        m, H = 2 * a + 1, rw.Hfam(a)
        sd, arr, summ = run_core(a, mode="chain", keep=not args.fresh)
        assert summ["seeds"] == len(sd) and summ["duplicate_seeds"] == 0      # the seeds are the first stored members, in order
        code = arr["code"]
        tab = collections.Counter()
        for u, (n, j, st, X) in enumerate(sd):
            A, B, U, V = st
            if n <= m or U >= 0:
                continue
            Y = mut(X, 3)
            tab[(bool(code[u][3] == 0), ht(Y) < H, fork_return(Y) is not None, A + (m - j) * (-U) < H, Y[1][0] == A + (m - j) * (-U))] += 1
        tot = sum(tab.values())
        yes = tab[(True, True, False, True, True)]
        no = tab[(False, False, False, False, True)]
        print("a=%d: %d route quivers; mu_r is a member and A + (m-j)|U| < H: %d; mu_r has height >= H and A + (m-j)|U| >= H: %d; "
              "other cases: %d; forks among the mu_r: %d" % (a, tot, yes, no, tot - yes - no, sum(v for k, v in tab.items() if k[2])), flush=True)


def cmd_ends(args):
    """How far the core reaches into the part of the class of R_a that is not forks, off the bounce cycle."""
    print("# 4-vertex parts (the quiver without x) of the stored members of the core (mode chain) that are not forks and not on "
          "the bounce cycle, against the fork-less part of the 4-vertex class of R_a below H(a) (forkless4).")
    for a in args.a:
        m, H = 2 * a + 1, rw.Hfam(a)
        sd, arr, summ = run_core(a, mode="chain", keep=not args.fresh)
        g4 = forkless4(a, H)
        dist = {c: len(v[1]) for c, v in g4.items()}
        sub = np.ascontiguousarray(arr["lab"][:, 4:])
        uniq, cnt = np.unique(sub, axis=0, return_counts=True)
        parts = collections.Counter()
        for u, c in zip(uniq, cnt):
            parts[canon4(tuple(int(v) for v in u))] += int(c)
        off = {c: k for c, k in parts.items() if dist.get(c, -1) != 0 and fork_return(from_upper(list(c), 4)) is None}
        ing = [c for c in off if c in dist]
        print("a=%d: fork-less part of the class of R_a below H, off the cycle: %d quivers, largest distance from the cycle %d; "
              "4-vertex parts of stored core members that are not forks, off the cycle: %d (%d stored members), of these in the "
              "fork-less part reached from the cycle: %d, largest distance %d"
              % (a, sum(1 for c in dist if dist[c] > 0), max(dist.values()), len(off), sum(off.values()), len(ing),
                 max(dist[c] for c in ing)), flush=True)


def cmd_crosscheck(args):
    """The number of members against np_barrier (note 16), which stores every quiver: popped - forks."""
    import np_corridor as nc
    print("# members of the core: np_qa_core.c (mode chain, one seed; mode plain where a <= %d) against np_barrier with fork pruning "
          "and cap H - 1 (quivers popped minus forks)." % args.plain_amax)
    bad = 0
    for a in args.a:
        Q, H = rw.Qa(a), rw.Hfam(a)
        _, _, summ = run_core(a, seedlist=[(1, a + 1, None, Q)], mode="chain", store=False, tag="_single", budget=12 * a ** 3 + 100000)
        r = nc.escape(Q, H - 1, budget=int(4.2 * a ** 5 + 500000), prune=1)
        ref = r["popped"] - r["forks"]
        line = "a=%d: chain %d, np_barrier %d - %d = %d (status %s, lowest %d, plateau %d)" % (
            a, summ["members"], r["popped"], r["forks"], ref, r["status"], r["lowest"], r["plateau"])
        good = summ["members"] == ref and r["status"] == "cap" and r["plateau"] == 1
        if a <= args.plain_amax:
            _, _, sp = run_core(a)
            line += ", plain %d" % sp["members"]
            good &= sp["members"] == ref
        bad += not good
        print(line + (": equal" if good else ": DIFFERENT"), flush=True)
    print("# %d values, %d differences" % (len(args.a), bad))


def cmd_branches(args):
    """The members of the core off the route and off the lines of steps on (p, q), by kind (mode plain)."""
    print("# members of the core that are neither on the route nor reached from it by steps on the pair (p, q) alone, by kind = "
          "(stretch of the root, skeleton of the word); np_qa_core.c, mode plain.  Last columns, for the largest a: turns n and "
          "positions j of the roots, and the longest runs of the word.")
    res = {}
    for a in args.a:
        sd, arr, summ = run_core(a, keep=not args.fresh)
        wd = words(arr)
        roots = arr["root"].tolist()
        sk = collections.defaultdict(list)
        for u, w in enumerate(wd):
            if w and not is_line(w):
                n, j, st, _ = sd[roots[u]]
                sk[(stretch(a, n), skeleton(w))].append((n, j, tuple(L for y, z, L in w)))
        res[a] = sk
        runs = collections.Counter(len(x[2]) for lst in sk.values() for x in lst)
        print("a=%d: %d members in %d kinds, %d kinds with >= a members (%d members); words by number of runs: %s"
              % (a, sum(len(v) for v in sk.values()), len(sk), sum(1 for v in sk.values() if len(v) >= a),
                 sum(len(v) for v in sk.values() if len(v) >= a), " ".join("%d:%d" % (k, runs[k]) for k in sorted(runs))), flush=True)
    A = list(args.a)
    last = res[A[-1]]
    keys = sorted(set().union(*[set(res[a]) for a in A]), key=lambda k: (-len(last.get(k, [])), k))
    print("%-3s %-18s %s | at a=%d" % ("", "skeleton", " ".join("a=%-6d" % a for a in A), A[-1]))
    for k in keys:
        lst = last.get(k, [])
        info = ""
        if lst:
            ns = sorted(set(x[0] for x in lst))
            js = sorted(set(x[1] for x in lst))
            mx = tuple(max(x[2][i] for x in lst if len(x[2]) > i) for i in range(max(len(x[2]) for x in lst)))
            info = "n %d..%d (%d), j %s, runs <= %s" % (ns[0], ns[-1], len(ns), "%d..%d" % (js[0], js[-1]) if len(js) > 2 else js, mx)
        print("%-3s %-18s %s | %s" % (k[0], k[1], " ".join("%-8d" % len(res[a].get(k, [])) for a in A), info))


SPIRAL = "qpqspspsqp"
SPIRAL_M = ((-23, 42, -12), (-42, 76, -21), (-12, 21, -5))      # (alpha, beta, gamma) after one period


def spiral_quiver(al, be, ga):
    """Frame p q r s: two arrows q -> p, one arrow q -> s, p and s not joined, and the row of r
    (b_rp, b_rq, b_rs) = (-alpha, beta, -gamma).  W_m(0) is spiral_quiver(m, m + 1, 2)."""
    B = [[0] * 4 for _ in range(4)]

    def setb(i, j, v):
        B[i][j] = v
        B[j][i] = -v
    setb(1, 0, 2), setb(1, 3, 1), setb(2, 0, -al), setb(2, 1, be), setb(2, 3, -ga)
    return tuple(tuple(r) for r in B)


def cmd_spiral(args):
    """Proposition on the spiral: ten mutations at p, q, s return the triangle on p, q, s and multiply the row of r."""
    import random
    rng = random.Random(11)
    ok = W4(7, 0) == spiral_quiver(7, 8, 2) and all(W4(m, 0) == spiral_quiver(m, m + 1, 2) for m in range(3, 200))
    print("W_m(0) = spiral_quiver(m, m + 1, 2) for 3 <= m < 200: %s" % ok)
    # the cone I = {0 <= alpha <= beta, 0 <= gamma <= beta / 2}: its four rays
    rays = [(0, 1, 0), (1, 1, 0), (0, 2, 1), (2, 2, 1)]
    conds = [(0, 1, 0), (-1, 2, 0), (-2, 3, 0), (0, 1, -1), (-3, 6, -2), (-6, 11, -3), (-9, 16, -4), (-12, 21, -5), (-4, 8, -3), (-23, 42, -12)]
    dot = lambda c, v: sum(x * y for x, y in zip(c, v))
    img = lambda v: tuple(dot(row, v) for row in SPIRAL_M)
    inI = lambda v: v[1] > 0 and 0 <= v[0] <= v[1] and 0 <= 2 * v[2] <= v[1]
    print("on the four rays of the cone I: the ten entries b_rk at the mutated vertices are > 0: %s; the image lies in I: %s; "
          "beta' >= 23.5 beta: %s" % (all(dot(c, v) > 0 for c in conds for v in rays), all(inI(img(v)) for v in rays),
                                      all(2 * img(v)[1] >= 47 * v[1] for v in rays)))
    n = 0
    good = True
    light = set()
    for trial in range(args.trials):
        be = rng.randint(1, 10 ** rng.randint(1, 12))
        al = rng.randint(0, be)
        ga = rng.randint(0, be // 2)
        X = spiral_quiver(al, be, ga)
        v = (al, be, ga)
        for i, c in enumerate(SPIRAL):
            k = "pqrs".index(c)
            good &= X[2][k] == dot(conds[i], v) > 0            # r -> k, with the predicted number of arrows
            X = mut(X, k)
            tri = (X[0][1], X[0][3], X[1][3])
            light.add(tri)
            good &= min(abs(t) for t in tri) < 2 and fork_return(X) is None
            n += 1
        good &= X == spiral_quiver(*img(v))
    print("%d random points of I, %d mutations: the predicted entries, a pair with fewer than two arrows among p, q, s after every "
          "mutation, no fork, and the image after ten mutations: %s" % (args.trials, n, "all hold" if good else "FAILED"))
    print("the triangles (b_pq, b_ps, b_qs) met: %s" % sorted(light))
    tr = sum(SPIRAL_M[i][i] for i in range(3))
    M = SPIRAL_M
    det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
           + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    print("the matrix of one period: %s, trace %d, determinant %d; characteristic polynomial (t - 1)(t^2 - 47t + 1)" % (M, tr, det))
    for m in (5, 13, 193):
        v = (m, m + 1, 2)
        hs = []
        for _ in range(6):
            hs.append(v[1])
            v = img(v)
        print("m=%d: beta after 0..5 periods: %s; ratios %s" % (m, hs, " ".join("%.4f" % (hs[i + 1] / hs[i]) for i in range(5))))


def cmd_compare18(args):
    """The counts of the search without pruning against those of Theorem 18.5 (np_rowwalk_family.jsonl, np_barrier)."""
    old = {}
    with open(os.path.join(HERE, "np_rowwalk_family.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if "below_H" in r:
                old[r["a"]] = r["below_H"]["popped"]
    new = {}
    with open(os.path.join(HERE, args.file)) as f:
        for line in f:
            r = json.loads(line)
            new[r["a"]] = r["members"]
    both = sorted(set(old) & set(new))
    diff = [a for a in both if old[a] != new[a]]
    print("quivers reached below H(a) without pruning: np_barrier (Theorem 18.5, every quiver stored) against np_qa_core.c mode "
          "chain-nofork: a = %d..%d, %d values compared, differences: %s" % (both[0], both[-1], len(both), diff or "none"))
    print("   " + " ".join("%d:%d" % (a, new[a]) for a in both))


def prefork(B):
    """(r, k, k') if B is a pre-fork (Ervin, arXiv 2306.07502, Def. 4.5, as quoted in note 14, section 3), else None."""
    n = len(B)
    for k in range(n):
        for k2 in range(k + 1, n):
            if not all((B[i][k] > 0 and B[i][k2] > 0) or (B[i][k] < 0 and B[i][k2] < 0) for i in range(n) if i not in (k, k2)):
                continue
            i1 = [i for i in range(n) if i != k]
            i2 = [i for i in range(n) if i != k2]
            r1 = fork_return(tuple(tuple(B[i][j] for j in i1) for i in i1))
            r2 = fork_return(tuple(tuple(B[i][j] for j in i2) for i in i2))
            if r1 is not None and r2 is not None and i1[r1] == i2[r2]:
                return (i1[r1], k, k2)
    return None


def cmd_prefork(args):
    """How much of the core lies behind pre-forks: the core again, without expanding the pre-forks of total weight
    above 10(a + 1) (no quiver of height <= a + 1 has that many arrows)."""
    print("# the core (mode plain) and the part of it reached from the route without expanding a pre-fork of total weight > 10(a + 1).")
    for a in args.a:
        sd, arr, summ = run_core(a, keep=not args.fresh)
        labs = arr["lab"]
        cand = np.nonzero((np.abs(labs) < 2).sum(axis=1) >= 1)[0]      # a pre-fork that is not a fork has a pair with < 2 arrows
        heavy = set()
        for u in cand:
            if int(np.abs(labs[u]).sum()) > 10 * (a + 1) and prefork(from_upper([int(v) for v in labs[u]], 5)) is not None:
                heavy.add(int(u))
        code, targ = arr["code"], arr["target"]
        alive = np.zeros(len(arr), dtype=bool)
        todo = collections.deque(np.nonzero(arr["depth"] == 0)[0].tolist())
        for u in todo:
            alive[u] = True
        while todo:
            u = todo.popleft()
            if u in heavy:
                continue
            for v in range(5):
                if code[u][v] == 0 and not alive[targ[u][v]]:
                    alive[targ[u][v]] = True
                    todo.append(int(targ[u][v]))
        print("a=%d: core %d; members with a pair joined by fewer than two arrows: %d; pre-forks of weight > 10(a + 1) among them: %d, "
              "on the route: %d; core without expanding these: %d (%d fewer)"
              % (a, len(arr), len(cand), len(heavy), sum(1 for u in heavy if arr["depth"][u] == 0), int(alive.sum()),
                 len(arr) - int(alive.sum())), flush=True)


def _rerun_one(arg):
    a, mode = arg
    budget = 12 * a ** 3 + 100000 if mode == "chain" else 24 * a ** 3 + 200000
    _, _, summ = run_core(a, seedlist=[(1, a + 1, None, rw.Qa(a))], mode=mode, store=False, tag="_rerun", keep=False, budget=budget)
    return a, mode, summ


def cmd_rerun(args):
    """Part of the two family runs again, against their stored results."""
    ref = {}
    for mode, name in (("chain", "np_qa_core_family.jsonl"), ("chain-nofork", "np_qa_core_family_nofork.jsonl")):
        with open(os.path.join(HERE, name)) as f:
            ref[mode] = {r["a"]: r for r in map(json.loads, f)}
    todo = [(a, "chain") for a in range(args.amax, 1, -1)] + [(a, "chain-nofork") for a in range(args.amax_nofork, 1, -1)]
    bad = 0
    keys = ("members", "stored", "passed_through", "members_of_height_le_w", "forks_of_height_le_w", "status")
    with Pool(args.workers) as pool:
        for a, mode, summ in pool.imap_unordered(_rerun_one, todo, chunksize=1):
            bad += any(summ[k] != ref[mode][a][k] for k in keys)
    print("searches repeated with the binary built from np_qa_core.c as it stands: mode chain for a = 2..%d, mode chain-nofork for "
          "a = 2..%d, %d searches; compared with np_qa_core_family.jsonl and np_qa_core_family_nofork.jsonl in %s: %d differences"
          % (args.amax, args.amax_nofork, len(todo), ", ".join(keys), bad))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    s = sub.add_parser("core")
    s.add_argument("--amin", type=int, default=6)
    s.add_argument("--amax", type=int, default=12)
    s.add_argument("--fresh", action="store_true")
    s.add_argument("--mode", default="plain", choices=("plain", "chain"))
    s = sub.add_parser("kinds")
    s.add_argument("--a", type=int, nargs="+", default=[6, 8, 10, 12])
    s.add_argument("--fresh", action="store_true")
    s.add_argument("--show", type=int, default=8)
    s = sub.add_parser("anatomy")
    s.add_argument("--a", type=int, nargs="+", default=[6, 7, 8, 9, 10, 11, 12])
    s.add_argument("--fresh", action="store_true")
    s = sub.add_parser("lines")
    s.add_argument("--amin", type=int, default=3)
    s.add_argument("--amax", type=int, default=12)
    s = sub.add_parser("forkless")
    s.add_argument("--a", type=int, nargs="+", default=[6, 8, 12, 16, 24, 32, 48, 64, 96])
    s = sub.add_parser("region")
    s.add_argument("--a", type=int, nargs="+", default=[8, 12, 16])
    s.add_argument("--fresh", action="store_true")
    s = sub.add_parser("ends")
    s.add_argument("--a", type=int, nargs="+", default=[6, 8, 12, 16])
    s.add_argument("--fresh", action="store_true")
    s = sub.add_parser("crosscheck")
    s.add_argument("--a", type=int, nargs="+", default=list(range(2, 17)))
    s.add_argument("--plain-amax", type=int, default=16)
    s = sub.add_parser("branches")
    s.add_argument("--a", type=int, nargs="+", default=[10, 11, 12, 13, 14, 15, 16])
    s.add_argument("--fresh", action="store_true")
    s = sub.add_parser("spiral")
    s.add_argument("--trials", type=int, default=20000)
    s = sub.add_parser("compare18")
    s.add_argument("--file", default="np_qa_core_family_nofork.jsonl")
    s = sub.add_parser("prefork")
    s.add_argument("--a", type=int, nargs="+", default=[6, 8, 10, 12, 14])
    s.add_argument("--fresh", action="store_true")
    s = sub.add_parser("rerun")
    s.add_argument("--amax", type=int, default=36)
    s.add_argument("--amax-nofork", type=int, default=26)
    s.add_argument("--workers", type=int, default=14)
    s = sub.add_parser("family")
    s.add_argument("--amin", type=int, default=2)
    s.add_argument("--amax", type=int, default=32)
    s.add_argument("--workers", type=int, default=8)
    s.add_argument("--mode", default="chain", choices=("chain", "chain-nofork"))
    s.add_argument("--out", default="")
    args = ap.parse_args()
    sys.exit(globals()["cmd_" + args.cmd](args))


if __name__ == "__main__":
    main()
