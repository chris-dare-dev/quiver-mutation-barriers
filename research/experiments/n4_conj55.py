#!/usr/bin/env python
"""
n4_conj55.py -- Conjecture 5.5 of arXiv 2610.36179 on all 4-vertex quivers of small height (note 13).

Conjecture 5.5 (Armstrong-Williams, Hirst, Jackson, Lee).  Every mutation-acyclic four-vertex quiver Q
admits a mutation sequence to an acyclic quiver along which every arrow multiplicity is at most ht(Q),
where ht(Q) = max |b_ij(Q)|.

Let G_L be the mutation graph on 4-vertex quivers (up to relabelling) of height <= L, and a(Q) the least
L at which the component of Q in G_L contains an acyclic quiver.  Q satisfies the conjecture exactly
when a(Q) = ht(Q) or Q is mutation-cyclic.  One union-find over the levels L = 1..N of all quivers of
height <= N gives a(Q) (capped at N) for every Q of height <= H <= N at once.  A quiver Q with
a(Q) > ht(Q) "fails"; it is then
  a counterexample      if a(Q) <= N (its class contains an acyclic quiver), or
  certified cyclic      if the component of Q in G_N carries a certificate of mutation-cyclicity:
      tri     a member has a mutation-cyclic full triangle (BBH Thm 1.2 + Warkentin; paper Prop. 2.1)
      vortex  a member is a vortex = has no proper wiggle class (FN26 Prop. 13.2 + Thm 2.2; paper Lemma 2.7)
      markov  a connected member whose proper wiggle classes all have Markov value M < 3 or M <= 2|p|
              (paper Lemma 2.4, the simplest case of Markov exclusion, Lemma 2.6)
      closed  no member has a mutation of height > N, so the component is the whole class, and it has
              no acyclic quiver
      cor52   some member X has H(X) <= N, where H(X) = max(ht(X), Markov values of the proper wiggle
              classes of X) (paper (13)); X's component in G_{H(X)} lies in this one, which has no acyclic
              quiver, so X is mutation-cyclic by Corollary 5.2 (= Theorem 5.1)
  undetermined          otherwise (left to the subcommand resolve).

Subcommands:
  check    unit checks of the invariants against the paper's examples and slow references
  run      the global computation; one JSON file with per-height counts, counterexamples and the
           undetermined failing quivers
  verify   re-check of a sample of the verdicts of run with separate code (labelled BFS for passing
           quivers, BFS on review12's canonical form for failing ones)
  verify-resolve
           re-check of a sample of resolve's certificates by plain BFS (for cor52: Corollary 5.2 applied
           to the certified quiver directly, on labelled quivers)
  recount  separate recount of run's per-height pass/fail table for heights <= H (Python BFS per quiver,
           review12's canonical form)
  resolve  per-class searches for the undetermined failing quivers: least-height-first search of the class,
           stopping at an acyclic quiver, a certificate, or the Corollary 5.2 bound of the quivers reached
  census   the same decision for the census classes of notes 8 and 10 with a pocket born <= B/4 (note 12)
  summary  the per-height table of the note, from the outputs of run and resolve

Run from experiments/ with python -I.  N = 18 needs about 11 GB of memory and 25 minutes.
"""
import argparse
import gzip
import itertools
import json
import os
import random
import sys
import time
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "verify"))  # review12.py: canonical form and mutation used by the checks
from n4_plateaus import UP, to_full, to_upper, mutate_batch, is_acyclic  # noqa: E402
from n4_all import keys_of, decode, level_keys  # noqa: E402

# ----------------------------------------------------------------------------- invariants (vectorized)
# cyclic orderings <0, v2, v3, v4> of the vertices 0..3, read in the displayed linear order
ORDERS = [(0,) + p for p in itertools.permutations((1, 2, 3))]
ORDER_ID = {}
for _o, _w in enumerate(ORDERS):
    for _r in range(4):
        ORDER_ID[_w[_r:] + _w[:_r]] = _o
# wiggles: swap two neighbours on the circle; (ordering, neighbour pair, ordering after the swap)
WIGGLES = []
for _o, _w in enumerate(ORDERS):
    for _r in range(4):
        x, y = _w[_r], _w[(_r + 1) % 4]
        nw = list(_w)
        nw[_r], nw[(_r + 1) % 4] = y, x
        WIGGLES.append((_o, x, y, ORDER_ID[tuple(nw)]))
# for each ordering: the (i, k, j) with i, k, j distinct that are NOT in clockwise (= increasing cyclic) order
NOT_CW = []
for _w in ORDERS:
    pos = {v: t for t, v in enumerate(_w)}
    bad = []
    for i, k, j in itertools.permutations(range(4), 3):
        if not ((pos[k] - pos[i]) % 4 < (pos[j] - pos[i]) % 4):
            bad.append((i, k, j))
    NOT_CW.append(bad)
TRIPLES = list(itertools.combinations(range(4), 3))
BIG = 1 << 30


def markov(B, w):
    """M_omega(Q) of the paper, (4), for the linear representative w = (v1, v2, v3, v4)."""
    v1, v2, v3, v4 = w
    a, b, c = B[:, v1, v2], B[:, v1, v3], B[:, v1, v4]
    d, e, f = B[:, v2, v3], B[:, v2, v4], B[:, v3, v4]
    return a * a + b * b + c * c + d * d + e * e + f * f + a * b * d + a * c * e + b * c * f + d * e * f + a * c * d * f


def pfaffian(B):
    """p(Q) = af - be + cd for b(Q) = (b01, b02, b03, b12, b13, b23)."""
    return B[:, 0, 1] * B[:, 2, 3] - B[:, 0, 2] * B[:, 1, 3] + B[:, 0, 3] * B[:, 1, 2]


def props(B):
    """Vectorized invariants of a batch of 4x4 exchange matrices (m, 4, 4).  Returns a dict of arrays:
    acyc, conn, tri, vortex, noproper, markov_excl, Hm (max Markov value over proper wiggle classes,
    -BIG if none), H (= max(ht, Hm), BIG if no proper class), p."""
    m = B.shape[0]
    A = (B > 0).astype(np.int64)
    A2 = A @ A
    acyc = ~((A2 @ A2).reshape(m, -1) != 0).any(axis=1)          # nilpotent adjacency <=> no directed cycle
    U = ((B != 0) | np.eye(4, dtype=bool)[None]).astype(np.int64)
    conn = ((U @ U @ U) > 0).reshape(m, -1).all(axis=1)
    tri = np.zeros(m, dtype=bool)
    for a, b, c in TRIPLES:
        x, y, z = B[:, a, b], B[:, b, c], B[:, c, a]
        orient = ((x > 0) & (y > 0) & (z > 0)) | ((x < 0) & (y < 0) & (z < 0))
        ax, ay, az = np.abs(x), np.abs(y), np.abs(z)
        tri |= orient & (np.minimum(np.minimum(ax, ay), az) >= 2) & (ax * ax + ay * ay + az * az - ax * ay * az <= 4)
    complete = (B[:, [0, 0, 0, 1, 1, 2], [1, 2, 3, 2, 3, 3]] != 0).all(axis=1)
    srcsink = np.zeros(m, dtype=bool)
    for v in range(4):
        others = [u for u in range(4) if u != v]
        row = B[:, v, others]
        src = (row > 0).all(axis=1) | (row < 0).all(axis=1)
        a, b, c = others
        x, y, z = B[:, a, b], B[:, b, c], B[:, c, a]
        orient = ((x > 0) & (y > 0) & (z > 0)) | ((x < 0) & (y < 0) & (z < 0))
        srcsink |= src & orient
    vortex = complete & srcsink
    # proper vertices per ordering
    pos = B > 0
    proper = np.ones((m, 6, 4), dtype=bool)
    for o in range(6):
        for (i, k, j) in NOT_CW[o]:
            proper[:, o, k] &= ~(pos[:, i, k] & pos[:, k, j])
    # wiggle classes: label propagation over the 6 orderings
    lab = np.tile(np.arange(6), (m, 1))
    for _ in range(6):
        for (o, x, y, o2) in WIGGLES:
            ok = B[:, x, y] == 0
            mn = np.minimum(lab[:, o], lab[:, o2])
            lab[:, o] = np.where(ok, mn, lab[:, o])
            lab[:, o2] = np.where(ok, mn, lab[:, o2])
    M = np.stack([markov(B, w) for w in ORDERS], axis=1)
    cls_proper = np.zeros((m, 6), dtype=bool)                   # indexed by class label
    for r in range(6):
        inr = lab == r
        cls_proper[:, r] = ((proper & inr[:, :, None]).any(axis=1)).all(axis=1) & inr.any(axis=1)
        has = inr.any(axis=1)
        mx = np.where(inr, M, -BIG).max(axis=1)
        mnv = np.where(inr, M, BIG).min(axis=1)
        assert np.all(~has | (mx == mnv)), "Markov value not constant on a wiggle class"
    op = np.take_along_axis(cls_proper, lab, axis=1)            # ordering lies in a proper class
    noproper = ~op.any(axis=1)
    Hm = np.where(op, M, -BIG).max(axis=1)
    ht = np.abs(B).reshape(m, -1).max(axis=1)
    H = np.where(noproper, BIG, np.maximum(ht, Hm))
    p = pfaffian(B)
    excl_o = (M < 3) | (M <= 2 * np.abs(p)[:, None])
    markov_excl = conn & ~noproper & np.where(op, excl_o, True).all(axis=1)
    return {"acyc": acyc, "conn": conn, "tri": tri, "vortex": vortex, "noproper": noproper,
            "markov_excl": markov_excl, "Hm": Hm, "H": H, "p": p, "M": M, "op": op, "lab": lab}


# ----------------------------------------------------------------------------- check
def mat(t):
    return to_full(np.array([t], dtype=np.int64))


def cmd_check(args):
    ok = True

    def expect(name, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"  {'ok ' if good else 'BAD'} {name}: got {got}, expected {want}")

    # Example 5.4: single proper wiggle class, Markov value 41, p^2 = 225, H = 41
    P = props(mat((-3, -2, 2, 0, 3, -3)))
    cls = sorted(set(P["lab"][0][P["op"][0]].tolist()))
    expect("Example 5.4 proper classes", len(cls), 1)
    expect("Example 5.4 H", int(P["H"][0]), 41)
    expect("Example 5.4 p^2", int(P["p"][0]) ** 2, 225)
    # Example 5.4: the acyclic quiver (0, 0, 3, 5, 1, 1) realises (41, 225) in the ordering 1 < 2 < 3 < 4
    P = props(mat((0, 0, 3, 5, 1, 1)))
    expect("(0,0,3,5,1,1) acyclic", bool(P["acyc"][0]), True)
    expect("(0,0,3,5,1,1) M<1234>, p^2", (int(P["M"][0][ORDER_ID[(0, 1, 2, 3)]]), int(P["p"][0]) ** 2), (41, 225))
    # Example 5.4: the component of Q inside height 41 has 238 quivers, none acyclic
    from review12 import canon4, mutations4
    for unl in (False, True):
        q = (-3, -2, 2, 0, 3, -3)
        q = canon4(q) if unl else q
        seen, todo = {q}, [q]
        while todo:
            x = todo.pop()
            for y in mutations4(x):
                if max(map(abs, y)) <= 41:
                    y = canon4(y) if unl else y
                    if y not in seen:
                        seen.add(y)
                        todo.append(y)
        expect(f"Example 5.4 component inside height 41 ({'up to relabelling' if unl else 'labelled'}): size, acyclic members",
               (len(seen), sum(map(sc_acyclic, seen))), (119 if unl else 238, 0))
    # Remark 5.6: G_x = (x, x, 0, 1, x, -1), acyclic with order 1 < 2 < 4 < 3 and m = x^3 + 4x^2 + x + 2
    for x in range(1, 9):
        P = props(mat((x, x, 0, 1, x, -1)))
        o = ORDER_ID[(0, 1, 3, 2)]
        expect(f"G_{x} acyclic, M<1243>, proper", (bool(P["acyc"][0]), int(P["M"][0][o]), bool(P["op"][0][o])),
               (True, x ** 3 + 4 * x * x + x + 2, True))
    # Remark 2.5: L_k = (k, 0, 0, 1, 0, k): M = 2k^2 + 1, p = k^2
    for k in range(1, 6):
        P = props(mat((k, 0, 0, 1, 0, k)))
        expect(f"L_{k} M<1234>, p", (int(P["M"][0][ORDER_ID[(0, 1, 2, 3)]]), int(P["p"][0])), (2 * k * k + 1, k * k))
    # Proposition 6.1: mu_1 of the double-arrow box, (2, 0, -2, -2, 4, -2): one proper class, M = 0
    P = props(mat((2, 0, -2, -2, 4, -2)))
    expect("mu_1(box) Markov-excluded", bool(P["markov_excl"][0]), True)
    expect("mu_1(box) H", int(P["H"][0]), 4)
    # the dreaded torus (-2, 1, 1, -1, -1, -1): each mutation is a relabelling of it
    T = mat((-2, 1, 1, -1, -1, -1))
    kT = keys_of(to_upper(T), 4)
    expect("dreaded torus closed under mutation", all(keys_of(to_upper(mutate_batch(T, k)), 4)[0] == kT[0] for k in range(4)), True)
    # slow references on every labelled quiver with entries in [-2, 2] and a random sample at height <= 9
    from review12 import has_cyclic_triangle
    r = np.arange(-2, 3)
    X = np.stack([g.ravel() for g in np.meshgrid(r, r, r, r, r, r, indexing="ij")], axis=1)
    rng = np.random.default_rng(55)
    X = np.concatenate([X, rng.integers(-9, 10, size=(20000, 6))])
    B = to_full(X)
    P = props(B)
    bad = Counter()
    for t in range(B.shape[0]):
        b = B[t]
        bad["acyclic"] += P["acyc"][t] != is_acyclic(b)
        bad["triangle"] += P["tri"][t] != has_cyclic_triangle(tuple(int(b[i, j]) for i, j in UP))
        # slow vortex: complete, and a vertex is a source or sink whose complement is an oriented triangle
        comp = all(b[i, j] != 0 for i, j in UP)
        vt = False
        for v in range(4):
            o = [u for u in range(4) if u != v]
            if all(b[v, u] > 0 for u in o) or all(b[v, u] < 0 for u in o):
                x, y, z = b[o[0], o[1]], b[o[1], o[2]], b[o[2], o[0]]
                vt |= (x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0)
        bad["vortex"] += P["vortex"][t] != (comp and vt)
        # slow connectivity
        seen, todo = {0}, [0]
        while todo:
            u = todo.pop()
            for v in range(4):
                if b[u, v] != 0 and v not in seen:
                    seen.add(v)
                    todo.append(v)
        bad["connected"] += P["conn"][t] != (len(seen) == 4)
    bad["vortex vs no proper class (FN26 Prop. 13.2)"] = int((P["vortex"] != P["noproper"]).sum())
    for k in ["acyclic", "triangle", "vortex", "connected", "vortex vs no proper class (FN26 Prop. 13.2)"]:
        expect(f"{B.shape[0]} quivers: disagreements, {k}", int(bad[k]), 0)
    # reversal B -> -B and relabelling preserve H and the certificates
    Pm = props(-B)
    expect("H(-Q) = H(Q)", bool(np.array_equal(Pm["H"], P["H"])), True)
    perm = (2, 0, 3, 1)
    Bp = B[:, perm][:, :, perm]
    Pp = props(Bp)
    expect("H invariant under relabelling", bool(np.array_equal(Pp["H"], P["H"])), True)
    expect("Markov exclusion invariant under relabelling", bool(np.array_equal(Pp["markov_excl"], P["markov_excl"])), True)
    # the scalar invariants used by verify and resolve, against the vectorized ones
    dis = Counter()
    for t in range(B.shape[0]):
        u = tuple(int(B[t][i, j]) for i, j in UP)
        hs, mx = sc_H(u), sc_markov_excl(u)
        dis["acyclic"] += sc_acyclic(u) != bool(P["acyc"][t])
        dis["triangle"] += sc_tri(u) != bool(P["tri"][t])
        dis["vortex"] += sc_vortex(u) != bool(P["vortex"][t])
        dis["H"] += (BIG if hs is None else hs) != int(P["H"][t])
        dis["markov exclusion"] += mx != bool(P["markov_excl"][t])
    for k in ["acyclic", "triangle", "vortex", "H", "markov exclusion"]:
        expect(f"{B.shape[0]} quivers: scalar vs vectorized, {k}", int(dis[k]), 0)
    print("all checks passed" if ok else "SOME CHECKS FAILED")


# ----------------------------------------------------------------------------- scalar invariants (pure Python)
# written separately from props(): explicit two-paths, wiggle classes by search over the orderings
def sc_full(t):
    B = [[0] * 4 for _ in range(4)]
    for (i, j), x in zip(UP, t):
        B[i][j], B[j][i] = x, -x
    return B


def sc_acyclic(t):
    B = sc_full(t)
    rem = set(range(4))
    while rem:
        src = [i for i in rem if not any(B[j][i] > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def sc_tri(t):
    B = sc_full(t)
    for a, b, c in TRIPLES:
        x, y, z = B[a][b], B[b][c], B[c][a]
        if (x > 0) == (y > 0) == (z > 0) and x * y * z != 0:
            x, y, z = abs(x), abs(y), abs(z)
            if min(x, y, z) >= 2 and x * x + y * y + z * z - x * y * z <= 4:
                return True
    return False


def sc_conn(t):
    B = sc_full(t)
    seen, todo = {0}, [0]
    while todo:
        u = todo.pop()
        for v in range(4):
            if B[u][v] and v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == 4


def sc_vortex(t):
    if any(x == 0 for x in t):
        return False
    B = sc_full(t)
    for v in range(4):
        o = [u for u in range(4) if u != v]
        if all(B[v][u] > 0 for u in o) or all(B[v][u] < 0 for u in o):
            x, y, z = B[o[0]][o[1]], B[o[1]][o[2]], B[o[2]][o[0]]
            if (x > 0) == (y > 0) == (z > 0):
                return True
    return False


def _rot0(w):
    r = w.index(0)
    return w[r:] + w[:r]


def sc_proper_classes(t):
    """[(Markov value, class)] for the proper wiggle classes of t, and p(t)."""
    B = sc_full(t)

    def proper(w, k):
        pos = {v: i for i, v in enumerate(w)}
        for i in range(4):
            for j in range(4):
                if B[i][k] > 0 and B[k][j] > 0 and not ((pos[k] - pos[i]) % 4 < (pos[j] - pos[i]) % 4):
                    return False
        return True

    def M(w):
        v1, v2, v3, v4 = w
        a, b, c, d, e, f = B[v1][v2], B[v1][v3], B[v1][v4], B[v2][v3], B[v2][v4], B[v3][v4]
        return a * a + b * b + c * c + d * d + e * e + f * f + a * b * d + a * c * e + b * c * f + d * e * f + a * c * d * f

    left = {(0,) + p for p in itertools.permutations((1, 2, 3))}
    out = []
    while left:
        w0 = left.pop()
        cls, todo = {w0}, [w0]
        while todo:
            w = todo.pop()
            for r in range(4):
                x, y = w[r], w[(r + 1) % 4]
                if B[x][y] == 0:
                    nw = list(w)
                    nw[r], nw[(r + 1) % 4] = y, x
                    nw = _rot0(tuple(nw))
                    if nw not in cls:
                        cls.add(nw)
                        todo.append(nw)
        left -= cls
        vals = {M(w) for w in cls}
        assert len(vals) == 1
        if all(any(proper(w, k) for w in cls) for k in range(4)):
            out.append((vals.pop(), sorted(cls)))
    p = t[0] * t[5] - t[1] * t[4] + t[2] * t[3]
    return out, p


def sc_H(t):
    pc, _ = sc_proper_classes(t)
    if not pc:
        return None
    return max([max(abs(x) for x in t)] + [m for m, _ in pc])


def sc_markov_excl(t):
    pc, p = sc_proper_classes(t)
    return bool(pc) and sc_conn(t) and all(m < 3 or m <= 2 * abs(p) for m, _ in pc)


# ----------------------------------------------------------------------------- verify
def cmd_verify(args):
    """Re-check stored verdicts with separate code: labelled BFS (no canonical forms) for passing quivers,
    and BFS on review12's canonical form (lexicographic maximum) for failing ones."""
    from review12 import canon4, mutations4
    op = gzip.open if args.inp.endswith(".gz") else open
    res = json.load(op(args.inp, "rt"))
    rng = random.Random(7)
    sp = res["sample_pass"]
    sf = res["sample_fail"]
    sp = rng.sample(sp, min(args.n, len(sp)))
    sf = rng.sample(sf, min(args.n, len(sf)))
    t0 = time.time()
    cnt = Counter()
    worst = Counter()
    for q in sp:
        q = tuple(q)
        h = max(map(abs, q))
        seen = {q: None}
        todo = [q]
        found = None
        it = 0
        while it < len(todo) and len(seen) < args.budget:
            x = todo[it]
            it += 1
            if sc_acyclic(x):
                found = x
                break
            for k, y in enumerate(mutations4(x)):
                if max(map(abs, y)) <= h and y not in seen:
                    seen[y] = (x, k)
                    todo.append(y)
        if found is None:
            cnt[("pass", "NOT CONFIRMED" if it >= len(todo) else "budget")] += 1
            continue
        # replay the labelled path and check every height
        path = []
        y = found
        while seen[y] is not None:
            x, k = seen[y]
            path.append(k)
            y = x
        path.reverse()
        z = q
        for k in path:
            z = mutations4(z)[k]
            assert max(map(abs, z)) <= h
        assert z == found and sc_acyclic(z)
        cnt[("pass", "confirmed, labelled path replayed")] += 1
        worst[len(path)] += 1
    print(f"passing sample: {dict(cnt)}; labelled path lengths {sorted(worst.items())} ({time.time() - t0:.0f}s)", flush=True)
    cnt = Counter()
    for q in sf:
        h = max(map(abs, q))
        c0 = canon4(q)
        seen = {c0}
        todo = [c0]
        it = 0
        acyc = False
        while it < len(todo) and len(seen) < args.budget:
            x = todo[it]
            it += 1
            if sc_acyclic(x):
                acyc = True
                break
            for y in mutations4(x):
                if max(map(abs, y)) <= h:
                    cy = canon4(y)
                    if cy not in seen:
                        seen.add(cy)
                        todo.append(cy)
        if acyc:
            cnt["fail: CONTRADICTED (acyclic within height)"] += 1
        elif it >= len(todo):
            cnt["fail: confirmed (component exhausted, no acyclic)"] += 1
        else:
            cnt["fail: budget"] += 1
    print(f"failing sample: {dict(cnt)} ({time.time() - t0:.0f}s)")


def cmd_verify_resolve(args):
    """Re-check a sample of the certificates found by resolve, by plain BFS: the certified quiver X is
    reached from the representative within the stated height; X carries the certificate; for cor52,
    H(X) <= K and the LABELLED component of X inside height H(X) is exhausted without an acyclic quiver
    (Corollary 5.2 applied to X directly)."""
    from review12 import canon4, mutations4
    rows = json.load(gzip.open(args.inp, "rt"))["rows"]
    rows = [r for r in rows if r["verdict"] == "cyclic" and not r["cert"].startswith("same class")]
    rng = random.Random(11)
    by = {}
    for r in rows:
        by.setdefault(r["cert"], []).append(r)
    t0 = time.time()
    for cert, rs in sorted(by.items()):
        cnt = Counter()
        pick = (sorted(rs, key=lambda r: -(r.get("K") or 0))[:args.n] if args.largest
                else rng.sample(rs, min(args.n, len(rs))))
        for r in pick:
            t = canon4(tuple(r["quiver"]))
            X = tuple(r["K_quiver"] if cert == "cor52" else r["at"])
            lim = r["K"] if cert == "cor52" else r["bottleneck"]
            cX = canon4(X)
            seen, todo, it = {t}, [t], 0
            while it < len(todo) and cX not in seen:
                x = todo[it]
                it += 1
                for y in mutations4(x):
                    if max(map(abs, y)) <= lim:
                        cy = canon4(y)
                        if cy not in seen:
                            seen.add(cy)
                            todo.append(cy)
            reached = cX in seen
            if cert == "tri":
                ok = sc_tri(X)
            elif cert == "vortex":
                ok = sc_vortex(X)
            elif cert == "markov":
                ok = sc_markov_excl(X)
            else:
                hX = sc_H(X)
                ok = hX is not None and hX <= lim
                if ok:
                    seen2, todo2, it2 = {X}, [X], 0
                    while it2 < len(todo2) and len(seen2) < args.budget:
                        x = todo2[it2]
                        it2 += 1
                        if sc_acyclic(x):
                            ok = False
                            break
                        for y in mutations4(x):
                            if max(map(abs, y)) <= hX and y not in seen2:
                                seen2.add(y)
                                todo2.append(y)
                    ok = ok and it2 >= len(todo2)
                    cnt["max labelled component"] = max(cnt["max labelled component"], len(seen2))
            cnt[("reached" if reached else "NOT REACHED", "certificate holds" if ok else "CERTIFICATE FAILS")] += 1
        print(f"  {cert}: {dict(cnt)} ({time.time() - t0:.0f}s)", flush=True)


def cmd_recount(args):
    """Independent recount of the per-height table of run: quivers of height h up to relabelling from
    review12's canonical form (lexicographic maximum) over the tuples with b01 = h, and for each one a
    BFS inside height h for an acyclic quiver.  Quivers of height h met by one search share its verdict."""
    from review12 import canon4, mutations4
    op = gzip.open if args.inp.endswith(".gz") else open
    ref = json.load(op(args.inp, "rt"))["per_height"]
    t0 = time.time()
    for h in range(args.hmin, args.H + 1):
        r = range(-h, h + 1)
        reps = {canon4((h,) + rest) for rest in itertools.product(r, repeat=5)}
        verdict = {}
        for q in reps:
            if q in verdict:
                continue
            seen, todo, it, acyc = {q}, [q], 0, False
            while it < len(todo):
                x = todo[it]
                it += 1
                if sc_acyclic(x):
                    acyc = True
                    break
                for y in mutations4(x):
                    if max(map(abs, y)) <= h:
                        cy = canon4(y)
                        if cy not in seen:
                            seen.add(cy)
                            todo.append(cy)
            for x in seen:
                if max(map(abs, x)) == h:
                    verdict[x] = acyc
        n = len(reps)
        conn = sum(map(sc_conn, reps))
        npass = sum(verdict[q] for q in reps)
        nfail_conn = sum(1 for q in reps if not verdict[q] and sc_conn(q))
        R = ref[str(h)]
        same = (n, conn, npass, nfail_conn) == (R["quivers"], R["connected"], R["pass"], R["fail_connected"])
        print(f"height {h}: quivers {n}, connected {conn}, pass {npass}, fail {n - npass} (connected {nfail_conn}); "
              f"run: {R['quivers']}, {R['connected']}, {R['pass']}, {R['fail']} ({R['fail_connected']}) -> "
              f"{'agree' if same else 'DISAGREE'} ({time.time() - t0:.0f}s)", flush=True)


# ----------------------------------------------------------------------------- resolve
def resolve_one(t, budget, known):
    """Bottleneck search (least maximal height first) over the class of t, up to relabelling.
    Stops at: an acyclic quiver (mutation-acyclic; a(t) = its bottleneck height); a certificate of
    mutation-cyclicity (tri, vortex, markov) on a reached quiver; or the Corollary 5.2 bound: with
    K = min over reached X of max(H(X), bottleneck(X)), once every quiver of bottleneck <= K has been
    reached without an acyclic one, the X attaining K is mutation-cyclic.  `known` maps canonical forms
    of already settled classes to their verdict."""
    import heapq
    from review12 import canon4, mutations4
    c0 = canon4(t)
    best = {c0: max(map(abs, c0))}
    pred = {c0: None}
    heap = [(best[c0], c0)]
    done = set()
    K, Kx = None, None
    while heap:
        b, x = heapq.heappop(heap)
        if x in done:
            continue
        if K is not None and b > K:
            return {"verdict": "cyclic", "cert": "cor52", "K": K, "K_quiver": list(Kx), "popped": len(done)}, done
        done.add(x)
        if x in known:
            v = dict(known[x])
            v.update({"cert": "same class as " + v.get("cert", ""), "popped": len(done)})
            if v["verdict"] == "cyclic":
                return v, done
        if sc_acyclic(x):
            path = []
            y = x
            while pred[y] is not None:
                path.append(y)
                y = pred[y]
            path.append(y)
            path.reverse()
            return {"verdict": "acyclic", "a": b, "acyclic_quiver": list(x),
                    "path": [list(p) for p in path], "path_heights": [max(map(abs, p)) for p in path], "popped": len(done)}, done
        if sc_tri(x):
            return {"verdict": "cyclic", "cert": "tri", "at": list(x), "bottleneck": b, "popped": len(done)}, done
        if sc_vortex(x):
            return {"verdict": "cyclic", "cert": "vortex", "at": list(x), "bottleneck": b, "popped": len(done)}, done
        if sc_markov_excl(x):
            return {"verdict": "cyclic", "cert": "markov", "at": list(x), "bottleneck": b, "popped": len(done)}, done
        hx = sc_H(x)
        if hx is not None and (K is None or max(hx, b) < K):
            K, Kx = max(hx, b), x
        if len(done) >= budget:
            return {"verdict": "undetermined", "K": K, "popped": len(done), "bottleneck_reached": b}, done
        for y in mutations4(x):
            cy = canon4(y)
            nb = max(b, max(map(abs, y)))
            if cy not in done and nb < best.get(cy, 1 << 62):
                best[cy] = nb
                pred[cy] = x
                heapq.heappush(heap, (nb, cy))
    return {"verdict": "cyclic", "cert": "class finite and exhausted", "popped": len(done)}, done


def _resolve_slice(task):
    rows, budget, cache, every, wid = task
    known = {}
    out = []
    t0 = time.time()
    tally = Counter()
    for i, u in enumerate(rows):
        v, done = resolve_one(tuple(u["quiver"]), budget, known)
        if v["verdict"] == "cyclic" and len(known) < cache:
            for x in done:
                known[x] = {"verdict": "cyclic", "cert": v["cert"].replace("same class as ", "")}
        row = dict(u)
        row.update(v)
        out.append(row)
        tally[(v["verdict"], v.get("cert", "").replace("same class as ", ""))] += 1
        if v["verdict"] == "acyclic":
            print(f"  COUNTEREXAMPLE? {u} -> {v}", flush=True)
        if (i + 1) % every == 0:
            print(f"  worker {wid}: {i + 1}/{len(rows)}: {dict(tally)} ({time.time() - t0:.0f}s)", flush=True)
    return out


def cmd_resolve(args):
    op = gzip.open if args.inp.endswith(".gz") else open
    res = json.load(op(args.inp, "rt"))
    rows = [u for u in res["undetermined"] if u["height"] <= args.H]
    rows.sort(key=lambda u: (u["height"], u["minH_component"]))
    print(f"{len(rows)} undetermined components of G_{res['N']} with a failing quiver of height <= {args.H}", flush=True)
    t0 = time.time()
    W = max(1, args.workers)
    tasks = [(rows[w::W], args.budget, args.cache // W, args.every, w) for w in range(W)]
    if W == 1:
        parts = [_resolve_slice(tasks[0])]
    else:
        from multiprocessing import Pool
        with Pool(W) as pool:
            parts = pool.map(_resolve_slice, tasks)
    out = [r for p in parts for r in p]
    tally = Counter((r["verdict"], r.get("cert", "").replace("same class as ", "")) for r in out)
    print(f"done: {dict(tally)} ({time.time() - t0:.0f}s)")
    # per height: failing quivers settled
    per = {}
    for r in out:
        for h, c in r["fail_by_height"].items():
            key = (int(h), r["verdict"])
            per[key] = per.get(key, 0) + c
    for key in sorted(per):
        print(f"  height {key[0]}: {key[1]}: {per[key]} undetermined failing quivers")
    with gzip.open(args.out, "wt") as f:
        json.dump({"input": args.inp, "H": args.H, "budget": args.budget, "rows": out}, f)


# ----------------------------------------------------------------------------- run
F_ACYC, F_CONN, F_TRI, F_VORTEX, F_MEXCL, F_EXIT = 1, 2, 4, 8, 16, 32


def _sample(arr, k, seed):
    return np.random.default_rng(seed).choice(arr, size=min(k, arr.size), replace=False)


def run(H, N, log, store_h):
    t0 = time.time()
    keys, lev = [], []
    for M in range(1, N + 1):
        k = level_keys(M, N)
        keys.append(k)
        lev.append(np.full(k.size, M, dtype=np.int8))
        log(f"  level {M}: {k.size} quivers ({time.time() - t0:.0f}s)")
    keys = np.concatenate(keys)
    lev = np.concatenate(lev)
    order = np.argsort(keys)
    keys, lev = keys[order], lev[order]
    del order
    nV = keys.size
    log(f"{nV} quivers with height <= {N}")
    flags = np.zeros(nV, dtype=np.uint8)
    Hx = np.zeros(nV, dtype=np.int32)
    eu, ev, el = [], [], []
    CH = 1_000_000
    for s in range(0, nV, CH):
        X = decode(keys[s:s + CH], N)
        B = to_full(X)
        idx = np.arange(s, min(s + CH, nV), dtype=np.int64)
        P = props(B)
        f = (P["acyc"] * F_ACYC + P["conn"] * F_CONN + P["tri"] * F_TRI + P["vortex"] * F_VORTEX
             + P["markov_excl"] * F_MEXCL).astype(np.uint8)
        assert np.array_equal(P["vortex"], P["noproper"])
        Hx[s:s + CH] = np.minimum(P["H"], BIG).astype(np.int32)
        for k in range(4):
            Nk = mutate_batch(B, k)
            me = np.abs(Nk).reshape(Nk.shape[0], -1).max(axis=1)
            f |= np.where(me > N, F_EXIT, 0).astype(np.uint8)
            sel = np.flatnonzero(me <= N)
            nk = keys_of(to_upper(Nk[sel]), N)
            j = np.searchsorted(keys, nk)
            assert np.all(keys[j] == nk)
            keep = j > idx[sel]
            eu.append(idx[sel][keep].astype(np.int32))
            ev.append(j[keep].astype(np.int32))
            el.append(np.maximum(lev[idx[sel][keep]], me[sel][keep]).astype(np.int8))
        flags[s:s + CH] = f
        if (s // CH) % 10 == 0:
            log(f"  nodes {s}..{min(s + CH, nV)} ({time.time() - t0:.0f}s)")
    eu, ev, el = np.concatenate(eu), np.concatenate(ev), np.concatenate(el)
    log(f"{eu.size} edges ({time.time() - t0:.0f}s)")
    acyc_idx = np.flatnonzero(flags & F_ACYC)
    parent = np.arange(nV, dtype=np.int32)
    a = np.zeros(nV, dtype=np.int8)               # a(Q); 0 = not reached yet
    per_h = {}
    for L in range(1, N + 1):
        m = el == L
        u, v = eu[m], ev[m]
        while u.size:
            pu, pv = parent[u], parent[v]
            lo, hi = np.minimum(pu, pv), np.maximum(pu, pv)
            d = lo != hi
            if not d.any():
                break
            np.minimum.at(parent, hi[d], lo[d])
            while True:
                pp = parent[parent]
                if np.array_equal(pp, parent):
                    break
                parent = pp
            u, v = u[d], v[d]
        hasA = np.zeros(nV, dtype=bool)
        hasA[parent[acyc_idx[lev[acyc_idx] <= L]]] = True
        cand = np.flatnonzero((a == 0) & (lev <= min(L, H)))
        a[cand[hasA[parent[cand]]]] = L
        if L <= H:
            at = np.flatnonzero(lev == L)
            ro = parent[at]
            ps = a[at] == L
            per_h[L] = {"quivers": int(at.size), "connected": int((flags[at] & F_CONN).astype(bool).sum()),
                        "acyclic": int((flags[at] & F_ACYC).astype(bool).sum()),
                        "components_GL": int(np.unique(ro).size),
                        "components_GL_with_acyclic": int(np.unique(ro[ps]).size),
                        "pass": int(ps.sum()), "pass_connected": int((ps & (flags[at] & F_CONN).astype(bool)).sum())}
        log(f"  L={L}: union done, {int((a == L).sum())} quivers first meet an acyclic quiver at L ({time.time() - t0:.0f}s)")
    del eu, ev, el
    # component certificates on G_N
    root = parent
    def any_on_root(mask_nodes):
        out = np.zeros(nV, dtype=bool)
        out[root[mask_nodes]] = True
        return out
    r_tri = any_on_root(np.flatnonzero(flags & F_TRI))
    r_vor = any_on_root(np.flatnonzero(flags & F_VORTEX))
    r_mex = any_on_root(np.flatnonzero(flags & F_MEXCL))
    r_exit = any_on_root(np.flatnonzero(flags & F_EXIT))
    minH = np.full(nV, BIG, dtype=np.int64)
    np.minimum.at(minH, root, Hx.astype(np.int64))
    r_c52 = minH <= N
    # consistency: a component of G_N with an acyclic member is mutation-acyclic, so none of its members
    # may carry a certificate of mutation-cyclicity
    r_acyc = any_on_root(acyc_idx)
    comps = np.flatnonzero(root == np.arange(nV))
    consistency = {"components_GN": int(comps.size), "components_with_acyclic": int(r_acyc[comps].sum()),
                   "quivers_in_components_with_acyclic": int(r_acyc[root].sum()),
                   "acyclic_and_tri": int((r_acyc & r_tri)[comps].sum()),
                   "acyclic_and_vortex": int((r_acyc & r_vor)[comps].sum()),
                   "acyclic_and_markov": int((r_acyc & r_mex)[comps].sum())}
    log(f"consistency: {consistency}")
    fail = np.flatnonzero((lev <= H) & (a != lev))
    fr = root[fail]
    order_c = [("tri", r_tri), ("vortex", r_vor), ("markov", r_mex), ("closed", ~r_exit), ("cor52", r_c52)]
    first = np.full(fail.size, -1, dtype=np.int64)
    for c, (name, arr) in enumerate(order_c):
        hit = arr[fr] & (first < 0) & (a[fail] == 0)
        first[hit] = c
    names = [n for n, _ in order_c]
    for h in range(1, H + 1):
        sel = lev[fail] == h
        fh, frh, ah, firsth = fail[sel], fr[sel], a[fail][sel], first[sel]
        conn = (flags[fh] & F_CONN).astype(bool)
        row = per_h[h]
        row["fail"] = int(fh.size)
        row["fail_connected"] = int(conn.sum())
        row["counterexamples"] = int((ah > 0).sum())
        row["cert"] = {names[c]: int((firsth == c).sum()) for c in range(len(names))}
        row["cert_connected"] = {names[c]: int(((firsth == c) & conn).sum()) for c in range(len(names))}
        row["cert_each"] = {n: int(arr[frh][ah == 0].sum()) for n, arr in order_c}
        row["certified"] = int((firsth >= 0).sum())
        row["undetermined"] = int(((firsth < 0) & (ah == 0)).sum())
        row["undetermined_connected"] = int(((firsth < 0) & (ah == 0) & conn).sum())
        row["fail_components_GN"] = int(np.unique(frh).size)
        row["undetermined_components_GN"] = int(np.unique(frh[(firsth < 0) & (ah == 0)]).size)
        row["classical_only"] = int((r_tri[frh] | r_vor[frh] | ~r_exit[frh])[ah == 0].sum())
        row["minH_of_fail_components"] = Counter(int(min(x, N + 1)) for x in minH[np.unique(frh[ah == 0])]).most_common()
    # all components of G_N meeting height <= h (each lies in one mutation class)
    for h in range(1, H + 1):
        per_h[h]["components_GN_meeting_le_h"] = int(np.unique(root[lev <= h]).size)
    cex = fail[a[fail] > 0]
    und = fail[(first < 0) & (a[fail] == 0)]
    # one representative per undetermined component: its lowest-height failing member, then smallest key
    uo = und[np.lexsort((keys[und], lev[und], root[und]))]
    und_reps = uo[np.r_[True, root[uo][1:] != root[uo][:-1]]] if uo.size else uo
    und_reps = und_reps[lev[und_reps] <= store_h]
    # undetermined failing quivers per (component, height), for the stored components
    us = und[lev[und] <= store_h]
    k2 = root[us].astype(np.int64) * 128 + lev[us]
    uq, uc = np.unique(k2, return_counts=True)
    by_root = {}
    for kk, cc in zip(uq.tolist(), uc.tolist()):
        by_root.setdefault(kk // 128, {})[kk % 128] = cc
    return {
        "H": H, "N": N, "quivers": int(nV), "time": round(time.time() - t0, 1), "per_height": per_h,
        "consistency": consistency,
        "counterexamples": [{"quiver": decode(keys[x:x + 1], N)[0].tolist(), "height": int(lev[x]), "a": int(a[x])}
                            for x in cex[:1000]],
        "undetermined": [{"quiver": decode(keys[x:x + 1], N)[0].tolist(), "height": int(lev[x]),
                          "minH_component": int(minH[root[x]]), "fail_by_height": by_root[int(root[x])]}
                         for x in und_reps],
        "undetermined_count": int(und.size),
        "sample_pass": [decode(keys[x:x + 1], N)[0].tolist() for x in
                        _sample(np.flatnonzero((lev <= H) & (a == lev)), 4000, 1)],
        "sample_fail": [decode(keys[x:x + 1], N)[0].tolist() for x in
                        _sample(fail, 4000, 2)],
    }


def cmd_run(args):
    res = run(args.H, args.N, lambda s: print(s, flush=True), args.store_h)
    op = gzip.open if args.out.endswith(".gz") else open
    with op(args.out, "wt") as f:
        json.dump(res, f)
    print(f"total time {res['time']}s")
    hdr = "h  quivers  connected  pass  fail  cex  tri  vortex  markov  closed  cor52  undet"
    print(hdr)
    for h, r in res["per_height"].items():
        c = r["cert"]
        print(f"{h} {r['quivers']} {r['connected']} {r['pass']} {r['fail']} {r['counterexamples']} {c['tri']} {c['vortex']} "
              f"{c['markov']} {c['closed']} {c['cor52']} {r['undetermined']}")
    print(f"counterexamples: {len(res['counterexamples'])}; undetermined quivers {res['undetermined_count']}; "
          f"{len(res['undetermined'])} undetermined components of G_N stored (height <= {args.store_h})")


def cmd_census(args):
    """The census classes of notes 8 and 10 with a pocket born <= B/4 (note 12 sec. 6): for each, the
    bottom quiver's search inside its own height for an acyclic quiver, then resolve_one on it."""
    from review12 import census_rows, canon4, mutations4
    t0 = time.time()
    tally, tally12 = Counter(), Counter()
    known = {}
    for fn, B, r in census_rows():
        if not any(p["birth"] <= B // 4 for p in r["pairs"]):
            continue
        t = canon4(np.array(r["bottom_quiver"]))
        h = max(map(abs, t))
        seen, todo, it, acyc = {t}, [t], 0, False
        while it < len(todo):
            x = todo[it]
            it += 1
            if sc_acyclic(x):
                acyc = True
                break
            for y in mutations4(x):
                if max(map(abs, y)) <= h:
                    cy = canon4(y)
                    if cy not in seen:
                        seen.add(cy)
                        todo.append(cy)
        # note 12's status (review12.py cyclic2): triangle at the bottom, or found by an upward search
        # inside the census bound B (budget 200,000), or undecided
        if sc_tri(t):
            n12 = "note 12: triangle at the bottom quiver"
        else:
            import heapq
            seen12, pq, n12 = {t}, [(h, t)], "note 12: undecided"
            while pq and len(seen12) < 200_000:
                m, x = heapq.heappop(pq)
                if sc_acyclic(x):
                    n12 = "note 12: ACYCLIC inside the bound"
                    break
                if sc_tri(x):
                    n12 = "note 12: triangle found upwards"
                    break
                for y in mutations4(x):
                    mm = max(map(abs, y))
                    if mm <= B:
                        cy = canon4(y)
                        if cy not in seen12:
                            seen12.add(cy)
                            heapq.heappush(pq, (mm, cy))
        v, done = resolve_one(t, args.budget, known)
        if v["verdict"] == "cyclic" and len(known) < 20_000_000:
            for x in done:
                known[x] = {"verdict": "cyclic", "cert": v["cert"].replace("same class as ", "")}
        tally[(f"bottom height {h}" if h > 9 else "bottom height <= 9",
               "bottom reaches acyclic within its height" if acyc else "bottom fails",
               v["verdict"], v.get("cert", "").replace("same class as ", ""))] += 1
        tally12[(n12, v["verdict"], v.get("cert", "").replace("same class as ", ""))] += 1
    for k in sorted(tally):
        print(f"  {k}: {tally[k]}")
    print("by note 12's status:")
    for k in sorted(tally12):
        print(f"  {k}: {tally12[k]}")
    print(f"{sum(tally.values())} classes ({time.time() - t0:.0f}s)")


def cmd_summary(args):
    """Per-height table from the outputs of run and resolve (markdown)."""
    op = gzip.open if args.run.endswith(".gz") else open
    run_ = json.load(op(args.run, "rt"))
    res = json.load(gzip.open(args.resolve, "rt"))
    settled = Counter()
    for r in res["rows"]:
        cert = r.get("cert", "").replace("same class as ", "")
        for h, c in r["fail_by_height"].items():
            settled[(int(h), r["verdict"], cert)] += c
    H = max(int(h) for h in run_["per_height"])
    print(f"run: N = {run_['N']}, {run_['quivers']} quivers, {run_['time']} s; resolve: heights <= {res['H']}, "
          f"budget {res['budget']}, {len(res['rows'])} components")
    print("| h | quivers | connected | acyclic | components of G_h | reach acyclic within h | fail | certified in G_N "
          "(tri / vortex / markov / closed / cor52) | settled by resolve (tri / vortex / markov / cor52 / other) | "
          "counterexamples | undetermined |")
    print("|" + "---|" * 11)
    tot = Counter()
    for h in range(1, H + 1):
        r = run_["per_height"][str(h)]
        c = r["cert"]
        res_c = {k: settled[(h, "cyclic", k)] for k in ("tri", "vortex", "markov", "cor52")}
        other = sum(v for (hh, vv, k), v in settled.items() if hh == h and vv == "cyclic" and k not in res_c)
        acyc_res = sum(v for (hh, vv, k), v in settled.items() if hh == h and vv == "acyclic")
        und_res = sum(v for (hh, vv, k), v in settled.items() if hh == h and vv == "undetermined")
        left = r["undetermined"] - sum(res_c.values()) - other - acyc_res
        assert h > res["H"] or und_res == left, (h, und_res, left)
        print(f"| {h} | {r['quivers']:,} | {r['connected']:,} | {r['acyclic']:,} | {r['components_GL']:,} | {r['pass']:,} | "
              f"{r['fail']:,} | {r['certified']:,} ({c['tri']:,} / {c['vortex']:,} / {c['markov']:,} / {c['closed']:,} / "
              f"{c['cor52']:,}) | {sum(res_c.values()) + other:,} ({res_c['tri']:,} / {res_c['vortex']:,} / "
              f"{res_c['markov']:,} / {res_c['cor52']:,} / {other:,}) | {r['counterexamples'] + acyc_res:,} | {left:,} |")
        for k in ("quivers", "connected", "pass", "fail", "certified", "counterexamples"):
            tot[k] += r[k]
        tot["resolved"] += sum(res_c.values()) + other
        tot["acyc_res"] += acyc_res
        tot["left"] += left
        tot["cor52_run"] += c["cor52"]
        tot["cor52_res"] += res_c["cor52"]
        tot["markov"] += c["markov"] + res_c["markov"]
    print(f"totals: {dict(tot)}")
    # by certificate, over all heights: first certificate in G_N (run) plus resolve's certificate
    bycert = Counter()
    for h in range(1, H + 1):
        for k, v in run_["per_height"][str(h)]["cert"].items():
            bycert[k] += v
    for (hh, vv, k), v in settled.items():
        if hh <= H and vv == "cyclic":
            bycert[k] += v
    print(f"failing quivers by certificate (run's first certificate, else resolve's): {dict(bycert)}")
    cl_run = sum(run_["per_height"][str(h)]["classical_only"] for h in range(1, H + 1))
    cl_res = sum(v for (hh, vv, k), v in settled.items() if vv == "cyclic" and k in ("tri", "vortex", "class finite and exhausted"))
    tri_any = sum(run_["per_height"][str(h)]["cert_each"]["tri"] for h in range(1, H + 1))
    clo_any = sum(run_["per_height"][str(h)]["cert_each"]["closed"] for h in range(1, H + 1))
    tri_res = sum(v for (hh, vv, k), v in settled.items() if vv == "cyclic" and k == "tri")
    print(f"failing quivers with a triangle in their component of G_N: {tri_any}; closed components: {clo_any}; "
          f"triangle found by resolve: {tri_res}; certified by triangles or a closed class alone (at most this many "
          f"overlap): <= {tri_any + clo_any + tri_res}, so >= {tot['fail'] - tri_any - clo_any - tri_res} rely on a vortex, "
          f"Lemma 2.4 or Corollary 5.2 as found")
    print(f"failing quivers with a classical certificate (tri, vortex or closed in G_N, or tri / vortex from resolve): "
          f"{cl_run + cl_res} = {cl_run} + {cl_res}; relying on Lemma 2.4 or Corollary 5.2: {tot['fail'] - cl_run - cl_res}")
    print("connected quivers reaching an acyclic quiver within h / failing:",
          {h: (run_["per_height"][str(h)]["pass_connected"], run_["per_height"][str(h)]["fail_connected"]) for h in range(1, H + 1)})
    print("components of G_N meeting height <= h:", {h: run_["per_height"][str(h)]["components_GN_meeting_le_h"] for h in range(1, H + 1)})
    print("components of G_h with an acyclic quiver:", {h: run_["per_height"][str(h)]["components_GL_with_acyclic"] for h in range(1, H + 1)})
    print("failing components of G_N:", {h: run_["per_height"][str(h)]["fail_components_GN"] for h in range(1, H + 1)})
    print("failing quivers certified by tri, vortex or closed alone (G_N):", {h: run_["per_height"][str(h)]["classical_only"] for h in range(1, H + 1)})
    big = sorted(res["rows"], key=lambda r: -r.get("popped", 0))[:5]
    print("largest resolve searches:", [(r["quiver"], r["height"], r["verdict"], r.get("cert"), r.get("K"), r["popped"]) for r in big])
    mk = {}
    for r in res["rows"]:
        if r.get("cert") == "cor52":
            mk[r["height"]] = max(mk.get(r["height"], 0), r["K"])
    print("resolve, largest cor52 bound K per height of the representative:",
          {h: (k, h ** 3 + h ** 2 + 5) for h, k in sorted(mk.items())}, "(second entry: h^3 + h^2 + 5)")
    ks = Counter(r.get("K") for r in res["rows"] if r.get("cert") == "cor52")
    print("resolve, cor52 bound K: max", max(ks) if ks else None, "; distribution", sorted(ks.items())[-10:])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    r = sub.add_parser("run")
    r.add_argument("--H", type=int, required=True)
    r.add_argument("--N", type=int, required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--store-h", type=int, default=12, help="store the undetermined components with a failing quiver of height <= this")
    v = sub.add_parser("verify")
    v.add_argument("--inp", required=True)
    v.add_argument("--n", type=int, default=2000, help="quivers per sample (passing, failing)")
    v.add_argument("--budget", type=int, default=2_000_000)
    vr = sub.add_parser("verify-resolve")
    vr.add_argument("--inp", required=True)
    vr.add_argument("--n", type=int, default=300, help="rows per certificate kind")
    vr.add_argument("--budget", type=int, default=5_000_000)
    vr.add_argument("--largest", action="store_true", help="take the rows with the largest bound K instead of a random sample")
    c = sub.add_parser("recount")
    c.add_argument("--inp", required=True)
    c.add_argument("--H", type=int, required=True)
    c.add_argument("--hmin", type=int, default=1)
    e = sub.add_parser("census")
    e.add_argument("--budget", type=int, default=2_000_000)
    m = sub.add_parser("summary")
    m.add_argument("--run", required=True)
    m.add_argument("--resolve", required=True)
    s = sub.add_parser("resolve")
    s.add_argument("--inp", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--H", type=int, required=True, help="resolve the components with a failing quiver of height <= H")
    s.add_argument("--budget", type=int, default=2_000_000, help="quivers reached per class")
    s.add_argument("--cache", type=int, default=20_000_000, help="canonical forms of settled classes kept")
    s.add_argument("--every", type=int, default=500)
    s.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    if args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "run":
        assert args.H <= args.N
        cmd_run(args)
    elif args.cmd == "verify":
        cmd_verify(args)
    elif args.cmd == "verify-resolve":
        cmd_verify_resolve(args)
    elif args.cmd == "recount":
        cmd_recount(args)
    elif args.cmd == "summary":
        cmd_summary(args)
    elif args.cmd == "census":
        cmd_census(args)
    elif args.cmd == "resolve":
        cmd_resolve(args)


if __name__ == "__main__":
    main()
