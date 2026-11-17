"""Check A of note 14, §2 "A test": independent re-run of the cosquare / ideal-class test with own code.

For a quiver and a cyclic ordering: own unipotent companion U (FN Def. 4.2, -B = U - U^T), cosquare
C = U^{-T} U (FN Def. 4.7) computed in PARI with exact rationals, characteristic polynomial f.
Own GP code: eigenvectors by matker over Q[y]/(f) (right eigenvector of C and right eigenvector of C^T),
ideals in the maximal order, bnfisprincipal with generator.  When the quotient ideal is principal, an
explicit G in GL_4(Z) with G^{-1} C G = C^T is constructed from the generator and checked in exact
integer arithmetic: an unconditional (GRH-free) certificate of conjugacy.  Optionally bnfcertify.

Reads n4_opposite_fn.jsonl.gz (verdicts of the code under review), n4_opposite_cores.jsonl.gz (vid, mvid)
and n4_opposite_plateaus.jsonl.gz (acyclic bottom components); recomputes everything else.

  python -I review19_n14a_cosq.py [n_different] [n_undecided] [n_certify] [seed]
"""
import gzip
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14a_lib as L

import cypari2

pari = cypari2.Pari()
pari.allocatemem(64 * 10 ** 6, 2 * 10 ** 9, silent=True)
pari("""rv_test(C, docert, tryG) = {
  my(f, nf, bnf, th, Kr, Kl, w, u, Iw, Iu, Q, e, idx, G, W, Vm, lam, ok, cert, same);
  f = charpoly(C, 'y);
  if(!polisirreducible(f), return([0, f]));
  nf = nfinit(f);
  idx = sqrtint(abs(poldisc(f) / nf.disc));
  bnf = bnfinit(nf, 1);
  th = Mod('y, f);
  Kr = matker(th*matid(4) - C);  w = Kr[,1];
  Kl = matker(th*matid(4) - C~); u = Kl[,1];
  if(C*w != th*w || C~*u != th*u, error("eigenvector"));
  Iw = idealhnf(nf, w[1]); for(i = 2, 4, Iw = idealadd(nf, Iw, w[i]));
  Iu = idealhnf(nf, u[1]); for(i = 2, 4, Iu = idealadd(nf, Iu, u[i]));
  Q = idealdiv(nf, Iw, Iu);
  e = bnfisprincipal(bnf, Q, 0);
  same = (e == 0*e);
  ok = 0; G = 0;
  if(same && tryG,
     e = bnfisprincipal(bnf, Q, 1 + 2);
     if(e === 0, return([1, f, same, idx, bnf.no, -2, -1, 0]));
     lam = nfbasistoalg(nf, e[2]);
     if(idealhnf(nf, lam) != Q, error("generator"));
     W = matrix(4, 4, i, j, nfalgtobasis(nf, w[i])[j]);
     Vm = matrix(4, 4, i, j, nfalgtobasis(nf, lam*u[i])[j]);
     G = W * Vm^(-1);
     if(denominator(G) == 1 && abs(matdet(G)) == 1 && G^(-1)*C*G == C~, ok = 1));
  cert = -1;
  if(docert, cert = bnfcertify(bnf));
  return([1, f, same, idx, bnf.no, ok, cert, G]);
}""")


def unipotent(B, order):
    n = 4
    return [[1 if a == b else (-B[order[a]][order[b]] if a < b else 0) for b in range(n)] for a in range(n)]


def cosquare_pari(B, order):
    U = pari.matrix(4, 4, [x for row in unipotent(B, order) for x in row])
    C = pari("(U) -> (U~)^(-1) * U")(U)
    return C


def proper_cyclic_orders(B):
    """Cyclic orders (as tuples starting with vertex 0) in which every vertex is proper (FN Defs. 5.1, 5.2),
    for a complete quiver (no wiggles possible)."""
    out = []
    for p in L.PERM24:
        if p[0] != 0:
            continue
        pos = {v: a for a, v in enumerate(p)}
        good = True
        for j in range(4):
            for i in range(4):
                for k in range(4):
                    if len({i, j, k}) < 3 or not (B[i][j] > 0 and B[j][k] > 0):
                        continue
                    # right turn at j: going cyclically forward from i one meets j before k
                    if not ((pos[j] - pos[i]) % 4 < (pos[k] - pos[i]) % 4):
                        good = False
        if good:
            out.append(p)
    return out


def topo_order(B):
    rem = set(range(4))
    out = []
    while rem:
        s = sorted(i for i in rem if not any(B[j][i] > 0 for j in rem))
        if not s:
            return None
        out.append(s[0])
        rem.discard(s[0])
    return tuple(out)


def acyclic_in_plateau(q):
    """An acyclic quiver in the plateau (component at level <= level(q)) of q, own BFS."""
    B0 = L.from6(q)
    lv = L.level(B0)
    seen = {L.key(B0): B0}
    todo = [B0]
    best = None
    while todo:
        X = todo.pop()
        if not L.has_cycle(X, range(4)):
            if best is None or L.key(X) < L.key(best):
                best = X
        for v in range(4):
            Y = L.mut(X, v)
            if L.level(Y) <= lv:
                ky = L.key(Y)
                if ky not in seen:
                    seen[ky] = Y
                    todo.append(Y)
    return best


def run_one(B, order, docert=False):
    C = cosquare_pari(B, order)
    from cysignals.alarm import alarm, cancel_alarm
    try:
        alarm(60)
        r = pari("rv_test")(C, 0, 1)
        cancel_alarm()
    except BaseException as ex:                # cysignals.AlarmInterrupt or a PARI error
        cancel_alarm()
        r = pari("rv_test")(C, 0, 0)
        r[5] = -2
    if docert and int(r[0]) == 1:
        try:
            alarm(45)
            c = pari("rv_test")(C, 1, 0)
            cancel_alarm()
            r[6] = c[6]
        except BaseException as ex:
            cancel_alarm()
            r[6] = -3
    tr = int(sum(int(C[i, i]) for i in range(4))) if False else int(pari("trace")(C))
    M = 4 - tr
    if int(r[0]) == 0:
        return {"irr": False, "M": M}
    return {"irr": True, "same": bool(r[2]), "index": int(r[3]), "h": int(r[4]), "G_ok": int(r[5]) == 1, "G_timeout": int(r[5]) == -2,
            "cert": int(r[6]), "M": M, "f": str(r[1])}


def main():
    n_diff = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    n_und = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    n_cert = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    rng = random.Random(seed)
    t0 = time.time()
    fn = {}
    with gzip.open("n4_opposite_fn.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            fn[r["i"]] = r
    print(f"fn records: {len(fn)}", flush=True)
    need_c = {i for i, r in fn.items() if r["kind"] == "complete"}
    need_a = {i for i, r in fn.items() if r["kind"] == "acyclic"}
    cores = {}
    with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["i"] in need_c:
                cores[r["i"]] = (tuple(r["vid"]), tuple(r["mvid"]), r["n"])
    plats = {}
    with gzip.open("n4_opposite_plateaus.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["i"] in need_a:
                keys = {tuple(c["k"]) for c in r["comps"]}
                selfm = tuple(r["comps"][0]["mk"]) in keys
                ac = [c["k"] for c in r["comps"] if c["acyc"]]
                plats[r["i"]] = (selfm, tuple(ac[0]) if ac else None)
    # re-tabulate the published table from the raw records
    tab = defaultdict(Counter)
    selfmirror = {}
    for i, r in fn.items():
        if r["kind"] == "complete":
            vid, mvid, n = cores[i]
            sm = vid == mvid
        else:
            sm = plats[i][0]
        selfmirror[i] = sm
        col = (r["kind"], "self-mirror" if sm else "mirror pair")
        if "error" in r:
            v = "error"
        elif not r["irreducible"]:
            v = "reducible"
        elif not r["same"]:
            v = "different"
        elif r["index"] == 1:
            v = "conjugate"
        else:
            v = "undecided"
        tab[col][v] += 1
    print("re-tabulated verdicts of n4_opposite_fn.jsonl.gz:")
    for col in sorted(tab):
        print(f"  {col}: {sum(tab[col].values())} {dict(sorted(tab[col].items()))}")
    # choose the sample
    def verdict(r):
        if "error" in r or not r.get("irreducible"):
            return None
        return "different" if not r["same"] else ("conjugate" if r["index"] == 1 else "undecided")
    conj = sorted(i for i, r in fn.items() if verdict(r) == "conjugate")
    diff = [i for i, r in fn.items() if verdict(r) == "different"]
    und = [i for i, r in fn.items() if verdict(r) == "undecided"]
    sample = [("conjugate", i) for i in conj]
    sample += [("different", i) for i in rng.sample(diff, n_diff)]
    sample += [("undecided", i) for i in rng.sample(und, n_und)]
    cert_set = set(rng.sample([i for v, i in sample if v == "different"], min(n_cert, n_diff)))
    n_cert_conj = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    cert_set |= set(rng.sample([i for i in conj if fn[i]["kind"] == "complete" and not selfmirror[i]], n_cert_conj))
    res = Counter()
    mism = []
    smallest = None
    certtimes = []
    for cnt, (v, i) in enumerate(sample):
        if cnt % 50 == 0:
            print(f"  [{cnt}/{len(sample)}] {time.time() - t0:.0f}s", flush=True)
        r = fn[i]
        if r["kind"] == "complete":
            vid = cores[i][0]
            B = L.from6(vid)
            po = proper_cyclic_orders(B)
            if len(po) != 1:
                res["complete: not exactly one proper cyclic order"] += 1
                continue
            order = po[0]
        else:
            B = acyclic_in_plateau(plats[i][1])
            order = topo_order(B)
        docert = i in cert_set
        tc = time.time()
        mine = run_one(B, order, docert)
        if docert:
            certtimes.append(time.time() - tc)
        if time.time() - tc > 20:
            print(f"    slow: class {i} {v} {r['kind']} {time.time() - tc:.0f}s cert={mine.get('cert')}", flush=True)
        myv = None if not mine["irr"] else ("different" if not mine["same"] else ("conjugate" if mine["index"] == 1 else "undecided"))
        key = (v, r["kind"], "self-mirror" if selfmirror[i] else "mirror pair")
        res[key + ("agree" if myv == v else f"MINE={myv}",)] += 1
        if myv != v:
            mism.append((i, v, myv, L.to6(B)))
        if mine.get("markov") is None and mine["M"] != r["markov"]:
            res["Markov invariant differs from the record"] += 1
        if mine["irr"]:
            if mine["h"] != r["h"] or mine["index"] != r["index"]:
                res["h or index differs from the record"] += 1
            if mine["same"] and mine["G_ok"]:
                res[key + ("explicit G in GL_4(Z) with G^-1 C G = C^T found",)] += 1
            if mine["same"] and mine["G_timeout"]:
                res[key + ("generator: timeout or PARI error",)] += 1
            if docert:
                res[key + (f"bnfcertify = {mine['cert']}",)] += 1
        if v == "conjugate" and r["kind"] == "complete" and not selfmirror[i]:
            t = L.to6(B)
            sz = (L.level(B), L.weight(B))
            if smallest is None or sz < smallest[0]:
                smallest = (sz, i, t, mine)
    for k in sorted(res, key=str):
        print(f"  {k}: {res[k]}")
    print("mismatches:", mism[:10])
    if certtimes:
        print(f"bnfcertify: {len(certtimes)} runs, max {max(certtimes):.1f}s, total {sum(certtimes):.1f}s")
    # the smallest of the 301 and the quiver quoted in the note
    quoted = L.from_rows([(0, 5, 4, -3), (-5, 0, 2, 5), (-4, -2, 0, 5), (3, -5, -5, 0)])
    print("smallest (level, weight) among the 'conjugate, complete, mirror pair' records:", smallest[0], "class", smallest[1], smallest[2])
    print("quoted quiver canonical key:", L.key(quoted), "same class rep as the smallest:", L.key(quoted) == L.key(L.from6(smallest[2])))
    for name, B in (("quoted", quoted),):
        fr = [sorted(L.fork_returns(L.mut(B, m))) for m in range(4)]
        po = proper_cyclic_orders(B)
        mine = run_one(B, po[0], True)
        pf = B[0][1] * B[2][3] - B[0][2] * B[1][3] + B[0][3] * B[1][2]
        print(f"  {name}: mutations' fork return sets {fr}; isomorphic to its opposite: {L.key(L.neg(B)) == L.key(B)}; "
              f"exit vertices of B itself: {sorted(L.exit_vertices(B))}; proper cyclic orders {po}; "
              f"M = {mine['M']}, Pf = {pf}, det B = {pf * pf}; f = {mine['f']}; index {mine['index']}, h = {mine['h']}, "
              f"same class {mine['same']}, explicit G found {mine['G_ok']}, bnfcertify {mine['cert']}")
        # V'(B) with the independent library: the core is {B}?
        rc = L.core_of(B, cap=1000)
        print(f"  {name}: V' size {len(rc[0])}, sink SCCs {[len(s) for s in rc[3]]}")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
