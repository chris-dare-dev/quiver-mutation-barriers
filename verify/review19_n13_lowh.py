"""
review19_n13_lowh.py -- independent per-height recount for note 13, heights 1..Lmax, on LABELLED quivers.

For each L: build the labelled mutation graph on all (2L+1)^6 skew-symmetric 4x4 integer matrices with entries in
[-L, L] (edges = mutations, paper (2), that stay inside height L), find its components (hooking + pointer
jumping), mark components with an acyclic member.  A quiver of height exactly L "passes" when its labelled
component in this graph contains an acyclic quiver; by the paper's identity (3) this is the same as the
up-to-relabelling statement.  Orbits under S_4 are counted by an own canonical key (minimum code over the 24
relabellings).  Also: connected / acyclic counts, components of G_L (up to relabelling) meeting height L, a
consistency check (no labelled component with an acyclic member contains a tri / vortex / Lemma-2.4 quiver),
and the failing orbits are written to ~/.cache/qmb-review19/fail_h{L}.txt for review19_n13_lowcert.py.

Imports nothing from the scripts under review.  Usage:
  python -I review19_n13_lowh.py --Lmin 1 --Lmax 7
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as Lb  # noqa: E402

PAIRS = Lb.PAIRS
PIDX = {p: a for a, p in enumerate(PAIRS)}
CACHE = os.path.expanduser("~/.cache/qmb-review19")


def entry(C, i, j):
    """b_ij from the coordinate arrays C[0..5] (vectorized)."""
    if i == j:
        return np.zeros_like(C[0])
    if i < j:
        return C[PIDX[(i, j)]]
    return -C[PIDX[(j, i)]]


def mutate_vec(C, k):
    out = []
    for (i, j) in PAIRS:
        if i == k or j == k:
            out.append(-C[PIDX[(i, j)]])
        else:
            bik, bkj = entry(C, i, k), entry(C, k, j)
            out.append(C[PIDX[(i, j)]] + np.maximum(bik, 0) * np.maximum(bkj, 0)
                       - np.maximum(-bik, 0) * np.maximum(-bkj, 0))
    return out


def acyclic_vec(C):
    cyc = np.zeros(C[0].shape, dtype=bool)
    for a, b, c in Lb._TRI3:
        cyc |= (entry(C, a, b) > 0) & (entry(C, b, c) > 0) & (entry(C, c, a) > 0)
    for a, b, c, d in Lb._CYC4:
        cyc |= (entry(C, a, b) > 0) & (entry(C, b, c) > 0) & (entry(C, c, d) > 0) & (entry(C, d, a) > 0)
    return ~cyc


def connected_vec(C):
    b01, b02, b03, b12, b13, b23 = [(x != 0) for x in C]
    iso = (~b01 & ~b02 & ~b03) | (~b01 & ~b12 & ~b13) | (~b02 & ~b12 & ~b23) | (~b03 & ~b13 & ~b23)
    split = (~b02 & ~b03 & ~b12 & ~b13) | (~b01 & ~b03 & ~b12 & ~b23) | (~b01 & ~b02 & ~b13 & ~b23)
    return ~(iso | split)


def tri_vec(C):
    out = np.zeros(C[0].shape, dtype=bool)
    for a, b, c in itertools.combinations(range(4), 3):
        x, y, z = entry(C, a, b), entry(C, b, c), entry(C, c, a)
        orient = ((x > 0) & (y > 0) & (z > 0)) | ((x < 0) & (y < 0) & (z < 0))
        x, y, z = np.abs(x), np.abs(y), np.abs(z)
        out |= orient & (np.minimum(np.minimum(x, y), z) >= 2) & (x * x + y * y + z * z - x * y * z <= 4)
    return out


# proper wiggle classes by sign pattern (from the pure-Python library, which follows FN's definitions)
SP_N = np.zeros(729, dtype=np.int64)
SP_REP = np.zeros((729, 6, 4), dtype=np.int64)
SP_VORTEX = np.zeros(729, dtype=bool)
for _s, _pat in enumerate(itertools.product((-1, 0, 1), repeat=6)):
    _pcs = Lb.proper_class_reps(_pat)
    SP_N[_s] = len(_pcs)
    for _c, _cls in enumerate(_pcs):
        SP_REP[_s, _c] = _cls[0]
    SP_VORTEX[_s] = Lb.is_vortex(_pat)


def sign_index(C):
    s = np.zeros(C[0].shape, dtype=np.int64)
    for p in range(6):
        s = s * 3 + (np.sign(C[p]).astype(np.int64) + 1)
    return s


def markov_pfaff_vec(C):
    """Per quiver: number of proper classes, their Markov values (m, 6) padded, the Pfaffian."""
    m = C[0].shape[0]
    B = np.zeros((m, 4, 4), dtype=np.int64)
    for (i, j) in PAIRS:
        B[:, i, j] = C[PIDX[(i, j)]]
        B[:, j, i] = -C[PIDX[(i, j)]]
    s = sign_index(C)
    npc = SP_N[s]
    M = np.zeros((m, 6), dtype=np.int64)
    ar = np.arange(m)
    for c in range(6):
        w = SP_REP[s, c]                       # (m, 4)
        g = lambda x, y: B[ar, w[:, x], w[:, y]]
        a, b, cc, d, e, f = g(0, 1), g(0, 2), g(0, 3), g(1, 2), g(1, 3), g(2, 3)
        M[:, c] = a * a + b * b + cc * cc + d * d + e * e + f * f + a * b * d + a * cc * e + b * cc * f + d * e * f + a * cc * d * f
    p = C[0] * C[5] - C[1] * C[4] + C[2] * C[3]
    return npc, M, p, SP_VORTEX[s]


def certs_vec(C, conn):
    npc, M, p, vort = markov_pfaff_vec(C)
    valid = np.arange(6)[None, :] < npc[:, None]
    excl = (M < 3) | (2 * np.abs(p)[:, None] >= M)
    l24 = conn & (npc > 0) & np.where(valid, excl, True).all(axis=1)
    return tri_vec(C), vort, l24, npc


def decode(idx, L):
    base = 2 * L + 1
    C = []
    x = idx.copy()
    for p in range(6):
        C.append((x % base).astype(np.int64) - L)
        x //= base
    return C


def encode(C, L):
    base = 2 * L + 1
    k = np.zeros(C[0].shape, dtype=np.int64)
    for p in reversed(range(6)):
        k = k * base + (C[p] + L)
    return k


RL = Lb._RL


def canon_key(C, L):
    best = None
    for m in RL:
        U = [s * C[src] for src, s in m]
        k = encode(U, L)
        best = k if best is None else np.minimum(best, k)
    return best


def components(n, nbrs, log):
    parent = np.arange(n, dtype=np.int32)
    us, vs = [], []
    ids = np.arange(n, dtype=np.int32)
    for nb in nbrs:
        sel = (nb >= 0) & (nb > ids)
        us.append(ids[sel])
        vs.append(nb[sel])
    u = np.concatenate(us)
    v = np.concatenate(vs)
    del us, vs
    it = 0
    while u.size:
        it += 1
        ru, rv = parent[u], parent[v]
        d = ru != rv
        if not d.any():
            break
        u, v, ru, rv = u[d], v[d], ru[d], rv[d]
        np.minimum.at(parent, np.maximum(ru, rv), np.minimum(ru, rv))
        while True:
            pp = parent[parent]
            if np.array_equal(pp, parent):
                break
            parent = pp
    log(f"    components: {it} hooking rounds")
    return parent


def run_level(L, log, dump):
    t0 = time.time()
    base = 2 * L + 1
    n = base ** 6
    CH = 2_000_000
    nbrs = [np.full(n, -1, dtype=np.int32) for _ in range(4)]
    acyc = np.zeros(n, dtype=bool)
    conn = np.zeros(n, dtype=bool)
    exact = np.zeros(n, dtype=bool)
    cert = np.zeros(n, dtype=np.int8)       # 1 tri, 2 vortex, 3 l24 (first one)
    for s in range(0, n, CH):
        idx = np.arange(s, min(n, s + CH), dtype=np.int64)
        C = decode(idx, L)
        acyc[idx] = acyclic_vec(C)
        cn = connected_vec(C)
        conn[idx] = cn
        h = np.max(np.abs(np.stack(C)), axis=0)
        exact[idx] = h == L
        tr, vo, l24, npc = certs_vec(C, cn)
        assert np.array_equal(vo, npc == 0), "vortex <=> no proper class failed"
        cc = np.where(tr, 1, np.where(vo, 2, np.where(l24, 3, 0))).astype(np.int8)
        cert[idx] = cc
        for k in range(4):
            Nk = mutate_vec(C, k)
            hk = np.max(np.abs(np.stack(Nk)), axis=0)
            ok = hk <= L
            code = np.where(ok, encode([np.clip(x, -L, L) for x in Nk], L), -1)
            nbrs[k][idx] = code.astype(np.int32)
    log(f"  L={L}: {n} labelled quivers, graph built ({time.time() - t0:.0f}s)")
    # symmetry of the edge relation (mutation is an involution): nbr_k(nbr_k(x)) = x
    for k in range(4):
        ok = nbrs[k] >= 0
        back = nbrs[k][nbrs[k][ok]]
        assert np.array_equal(back, np.flatnonzero(ok).astype(np.int32)), "mutation not involutive"
    root = components(n, nbrs, log)
    del nbrs
    hasA = np.zeros(n, dtype=bool)
    hasA[root[acyc]] = True
    passing = hasA[root]
    hasC = np.zeros(n, dtype=bool)
    hasC[root[cert > 0]] = True
    both = int((hasA & hasC).sum())
    ncompA = int(hasA.sum())
    # canonical keys (for orbits and for components up to relabelling); component up to relabelling:
    # min canonical key over the labelled component
    ex = np.flatnonzero(exact)
    k_ex = np.empty(ex.size, dtype=np.int64)
    cmin = np.full(n, np.iinfo(np.int64).max, dtype=np.int64)
    accA = []
    for s in range(0, n, CH):
        idx = np.arange(s, min(n, s + CH), dtype=np.int64)
        ck = canon_key(decode(idx, L), L)
        np.minimum.at(cmin, root[idx], ck)
        lo, hi = np.searchsorted(ex, [s, s + idx.size])
        k_ex[lo:hi] = ck[ex[lo:hi] - s]
        accA.append(np.unique(ck[hasA[root[idx]]]))
    orbits_in_A = np.unique(np.concatenate(accA)).size
    roots = np.flatnonzero(root == np.arange(n))
    comps_all = np.unique(cmin[roots]).size
    comps_A = np.unique(cmin[roots[hasA[roots]]]).size
    orbits = np.unique(k_ex)
    pass_orb = np.unique(k_ex[passing[ex]])
    fail_orb = np.unique(k_ex[~passing[ex]])
    assert np.intersect1d(pass_orb, fail_orb).size == 0, "an orbit both passes and fails"
    assert pass_orb.size + fail_orb.size == orbits.size
    conn_orb = np.unique(k_ex[conn[ex]])
    pass_conn = np.unique(k_ex[conn[ex] & passing[ex]])
    acyc_orb = np.unique(k_ex[acyc[ex]])
    comp_meet = np.unique(cmin[root[ex]])
    comp_meet_pass = np.unique(cmin[root[ex[passing[ex]]]])
    row = {"L": L, "labelled": int(n), "labelled_exact": int(ex.size), "orbits": int(orbits.size),
           "connected": int(conn_orb.size), "acyclic": int(acyc_orb.size), "pass": int(pass_orb.size),
           "fail": int(fail_orb.size), "pass_connected": int(pass_conn.size),
           "fail_connected": int(conn_orb.size - pass_conn.size),
           "components_GL_meeting_L": int(comp_meet.size), "components_GL_meeting_L_with_acyclic": int(comp_meet_pass.size),
           "labelled_components_with_acyclic": ncompA, "labelled_components_with_acyclic_and_cert": both,
           "quivers_in_components_with_acyclic": int(hasA[root].sum()),
           "components_GL_all_heights": int(comps_all), "components_GL_with_acyclic_all_heights": int(comps_A),
           "orbits_in_components_GL_with_acyclic": int(orbits_in_A), "time": round(time.time() - t0, 1)}
    log(f"  L={L}: {json.dumps(row)}")
    if dump:
        fo = np.unique(k_ex[~passing[ex]])
        C = decode(fo, L)        # the canonical key is itself a code; decode it to the canonical quiver
        # the key encodes coordinates with p=5 most significant; decode() uses p=0 least significant: same order
        with open(os.path.join(CACHE, f"fail_h{L}.txt"), "w") as f:
            for i in range(fo.size):
                f.write(" ".join(str(int(C[p][i])) for p in range(6)) + "\n")
        log(f"  wrote {fo.size} failing orbits to {CACHE}/fail_h{L}.txt")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--Lmin", type=int, default=1)
    ap.add_argument("--Lmax", type=int, default=6)
    ap.add_argument("--dump-max", type=int, default=6)
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    log = lambda s: print(s, flush=True)
    rows = []
    for L in range(a.Lmin, a.Lmax + 1):
        rows.append(run_level(L, log, L <= a.dump_max))
    with open(os.path.join(CACHE, f"lowh_{a.Lmin}_{a.Lmax}.json"), "w") as f:
        json.dump(rows, f)
    print("h | orbits | connected | acyclic | pass | fail | pass_conn | fail_conn | comps G_h meeting h | with acyclic | "
          "labelled comps w/ acyclic AND cert")
    for r in rows:
        print(f"{r['L']} | {r['orbits']} | {r['connected']} | {r['acyclic']} | {r['pass']} | {r['fail']} | "
              f"{r['pass_connected']} | {r['fail_connected']} | {r['components_GL_meeting_L']} | "
              f"{r['components_GL_meeting_L_with_acyclic']} | {r['labelled_components_with_acyclic_and_cert']}")


if __name__ == "__main__":
    main()
