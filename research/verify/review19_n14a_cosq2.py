"""Check A of note 14, §2: how often is the cosquare conjugate to its transpose in the classes that the
part calls "undecided" (equal ideal classes, Z[x] not maximal)?  For a sample of undecided mirror pairs,
look for an explicit G in GL_4(Z) with C G = G C^T (from the generator of I_w / I_u, see
review19_n14a_cosq.py), re-checked here in exact Python integers.  For acyclic pairs, re-certify that
Q and -Q are different classes with an own sink/source orbit (Caldero-Keller, Cor. 4).

  python -I review19_n14a_cosq2.py KIND N SEED      (KIND = acyclic or complete)
"""
import gzip
import json
import os
import random
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14a_lib as L
import review19_n14a_cosq as CQ
from cysignals.alarm import alarm, cancel_alarm

pari = CQ.pari


def int_cosquare(B, order):
    """U^{-T} U in exact integers (U unipotent)."""
    U = CQ.unipotent(B, order)
    n = 4
    N = [[U[i][j] - (i == j) for j in range(n)] for i in range(n)]
    Ui = [[int(i == j) for j in range(n)] for i in range(n)]
    P = [[int(i == j) for j in range(n)] for i in range(n)]
    for e in range(1, n):
        P = [[sum(P[i][k] * N[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                Ui[i][j] += (-1) ** e * P[i][j]
    UiT = [[Ui[j][i] for j in range(n)] for i in range(n)]
    return [[sum(UiT[i][k] * U[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def det(M):
    if len(M) == 1:
        return M[0][0]
    return sum((-1) ** j * M[0][j] * det([r[:j] + r[j + 1:] for r in M[1:]]) for j in range(len(M)))


def check_G(C, G):
    n = 4
    CG = [[sum(C[i][k] * G[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    GCt = [[sum(G[i][k] * C[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
    return CG == GCt and abs(det(G)) == 1


def sink_source_orbit(B):
    seen = {L.key(B)}
    todo = [B]
    while todo:
        X = todo.pop()
        for v in range(4):
            col = [X[v][j] for j in range(4) if j != v]
            if all(c >= 0 for c in col) or all(c <= 0 for c in col):
                Y = L.mut(X, v)
                ky = L.key(Y)
                if ky not in seen:
                    seen.add(ky)
                    todo.append(Y)
    return seen


def main():
    kind, N, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    t0 = time.time()
    fn = {}
    with gzip.open("n4_opposite_fn.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if (r["kind"] == kind and "error" not in r and r.get("irreducible") and r["same"] and r["index"] > 1):
                fn[r["i"]] = r
    info = {}
    if kind == "complete":
        with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
            for line in f:
                r = json.loads(line)
                if r["i"] in fn:
                    info[r["i"]] = (r["vid"] == r["mvid"], tuple(r["vid"]))
    else:
        with gzip.open("n4_opposite_plateaus.jsonl.gz", "rt") as f:
            for line in f:
                r = json.loads(line)
                if r["i"] in fn:
                    keys = {tuple(c["k"]) for c in r["comps"]}
                    ac = [c["k"] for c in r["comps"] if c["acyc"]]
                    info[r["i"]] = (tuple(r["comps"][0]["mk"]) in keys, tuple(ac[0]))
    pairs = sorted(i for i in fn if not info[i][0])
    print(f"{kind}: undecided records {len(fn)}, of which mirror pairs {len(pairs)}; sample {min(N, len(pairs))}", flush=True)
    sample = rng.sample(pairs, min(N, len(pairs)))
    st = Counter()
    found = []
    for cnt, i in enumerate(sample):
        if cnt % 250 == 0:
            print(f"  [{cnt}] {time.time() - t0:.0f}s {dict(st)}", flush=True)
        if kind == "complete":
            B = L.from6(info[i][1])
            po = CQ.proper_cyclic_orders(B)
            if len(po) != 1:
                st["not one proper order"] += 1
                continue
            order = po[0]
        else:
            B = CQ.acyclic_in_plateau(info[i][1])
            order = CQ.topo_order(B)
        C = CQ.cosquare_pari(B, order)
        try:
            alarm(30)
            r = pari("rv_test")(C, 0, 1)
            cancel_alarm()
        except BaseException:
            cancel_alarm()
            st["timeout or PARI error"] += 1
            continue
        st["tested"] += 1
        if int(r[0]) != 1 or not bool(r[2]) or int(r[3]) == 1:
            st["verdict changed (not undecided)"] += 1
            continue
        if int(r[5]) != 1:
            st["no explicit G from the generator"] += 1
            continue
        G = [[int(r[7][a, b]) for b in range(4)] for a in range(4)]
        Ci = int_cosquare(B, order)
        if not check_G(Ci, G):
            st["G fails the integer re-check"] += 1
            continue
        st["explicit G: cosquare conjugate to its transpose (unconditional)"] += 1
        if kind == "acyclic":
            if L.key(L.neg(B)) in sink_source_orbit(B):
                st["   ... but -Q in the sink/source orbit of Q (not a mirror pair!)"] += 1
                continue
            st["   ... and -Q not in the sink/source orbit of Q: different classes (Caldero-Keller)"] += 1
        found.append((L.level(B), L.weight(B), i, L.to6(B), order, int(r[3]), 4 - sum(Ci[a][a] for a in range(4)), G))
    print(f"{kind}: {dict(st)}")
    found.sort()
    for x in found[:5]:
        print(f"  example (level, weight, class, quiver b01..b23, ordering, index, Markov M, G): {x}")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
