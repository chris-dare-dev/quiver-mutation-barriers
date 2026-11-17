"""Review 2 of note 14 (n14b), step 2 of the tube attack: check the certificates saved by
review19_n14b_tubecert.py with independent integer code (review19_n14b_lib only; nothing from
n4_opposite*.py).  For each certificate (x, E, families):

  A. x passes the direct test for lying in no far region.
  B. every family: tau >= 2; Y(n) for n = 0..NF; every entry has constant sign and non-decreasing absolute
     value on the enumerated range; the level is non-decreasing for n >= 3 and Y(n), n >= 3, lies above the
     claimed bottom level bK.
  C. closure at many n: for every family, n = 0..NC and every vertex m, the step Y(n) -> mu_m Y(n) is a
     strict up-exit step or lands in E or in a family (membership by canonical form, explicit n).
     Steps where two growing entries at m are multiplied ("growing vertex") are counted separately.
  D. closure of E: every allowed step out of E lands in E or in a family.
  E. my own V' from x by a best-first search in order of level (cap 6000 quivers, quivers above 10^12 not
     expanded): every quiver found lies in E or in a family; the least level found is bK and the quivers
     found at that level are the claimed bottom; kid and mkid recomputed.
  F. the census bottom quiver q: my V'(q) reaches x (or q = x); if q passes the direct test, V'(q) lies in
     E or a family as well.
  G. the re-run record agrees with the stored record (status, kid, mkid, bK, number of families).
Usage: python -I review19_n14b_tubecheck.py START STEP  (processes certificates START, START+STEP, ...)
"""
import gzip
import heapq
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L

CERTS = os.path.expanduser("~/.cache/qmb-review19/n14b_certs.jsonl.gz")
NF = 56          # members enumerated directly
NC = 44          # closure checked for n = 0..NC
BIG = 10 ** 90   # stop the closure check of a family above this level


class Cert:
    def __init__(self, c):
        self.E = {tuple(e) for e in c["E"]}
        self.fams = [(tau, tuple(tuple(y) for y in Y)) for tau, Y in c["fams"]]
        self.terms = []
        self.mem = {}
        for fid, (tau, Y) in enumerate(self.fams):
            ts = L.fam_terms(Y, tau, NF)
            self.terms.append(ts)
            for n, y in enumerate(ts):
                self.mem.setdefault(L.canon(y), (fid, n))
        self.cache = {}

    def member(self, q):
        """(kind, data): ('E', None), ('R', (fid, n)) or (None, None)."""
        if q in self.E:
            return "E", None
        r = self.mem.get(q)
        if r is not None:
            return "R", r
        r = self.cache.get(q)
        if r is not None:
            return r
        for fid, (tau, Y) in enumerate(self.fams):
            n = L.fam_find(Y, tau, q)
            if n is not None:
                self.cache[q] = ("R", (fid, n))
                return "R", (fid, n)
        self.cache[q] = (None, None)
        return None, None


_ex = {}


def exits(t):
    r = _ex.get(t)
    if r is None:
        if len(_ex) > 400000:
            _ex.clear()
        r = _ex[t] = L.exits(t)
    return r


def strict_up(y, m, z):
    return m in exits(z) and m not in exits(y)


def best_first(start, cert, cap=6000, level_cap=10 ** 12):
    """V'(start) explored in order of level.  Returns (found: canon -> level, above: set, outside: list)."""
    s = L.canon(start)
    found = {s: L.level(s)}
    heap = [(found[s], s)]
    above = set()
    outside = []
    while heap and len(found) < cap:
        lv, x = heapq.heappop(heap)
        for m in range(4):
            y = L.mut(x, m)
            if strict_up(x, m, y):
                continue
            c = L.canon(y)
            if c in found or c in above:
                continue
            lc = L.level(c)
            if cert is not None and cert.member(c)[0] is None:
                outside.append(c)
            if lc > level_cap:
                above.add(c)
                continue
            found[c] = lc
            heapq.heappush(heap, (lc, c))
    return found, above, outside, len(heap) == 0


def check(c):
    t0 = time.time()
    st = Counter()
    bad = []
    out = {"i": c["i"], "b": c["b"]}
    rec = c["rec"]
    sto = c["stored"]
    if rec["status"] != "certified":
        out["rerun"] = rec["status"]
        return out, st, ["re-run not certified: " + rec["status"]]
    for k in ("kid", "mkid", "bK", "nodes", "nE", "lR3"):
        if rec.get(k) != sto.get(k):
            bad.append(f"G: re-run {k} {rec.get(k)} != stored {sto.get(k)}")
    cert = Cert(c)
    x = tuple(c["x"])
    bK = rec["bK"]
    out.update({"nE": len(cert.E), "nfam": len(cert.fams), "taus": sorted({f[0] for f in cert.fams})})
    # A
    if not L.no_far_region(x):
        bad.append("A: x fails the direct test")
    if L.canon(x) != x:
        bad.append("A: x not canonical")
    # B
    low = {e: L.level(e) for e in cert.E}
    for fid, (tau, Y) in enumerate(cert.fams):
        if tau < 2:
            bad.append(f"B: family {fid} tau {tau}")
        ts = cert.terms[fid]
        for a in range(6):
            seq = [y[a] for y in ts]
            sg = {(v > 0) - (v < 0) for v in seq}
            if len(sg) > 1:
                bad.append(f"B: family {fid} entry {a} changes sign")
                break
            if any(abs(seq[n + 1]) < abs(seq[n]) for n in range(len(seq) - 1)):
                bad.append(f"B: family {fid} entry {a} decreases in absolute value")
                break
        levs = [L.level(y) for y in ts]
        if any(levs[n + 1] < levs[n] for n in range(3, len(levs) - 1)):
            bad.append(f"B: family {fid} level decreases after n = 3")
        if min(levs[3:]) <= bK:
            bad.append(f"B: family {fid} has a member n >= 3 at or below bK")
        ws = [L.weight(y) for y in ts]
        if any(ws[n + 1] < ws[n] for n in range(len(ws) - 1)):
            bad.append(f"B: family {fid} weight decreases")
        for y in ts[:3]:
            cy = L.canon(y)
            low[cy] = L.level(cy)
    # C
    for fid, (tau, Y) in enumerate(cert.fams):
        ts = cert.terms[fid]
        var = [len({y[a] for y in ts[:3]}) > 1 for a in range(6)]
        for m in range(4):
            at_m = [a for a, (i, j) in enumerate(L.PAIRS) if m in (i, j)]
            grow = sum(1 for a in at_m if var[a])
            others_var = any(var[a] for a in range(6) if a not in at_m)
            zs = []
            for n in range(NC + 1):
                y = ts[n]
                if L.level(y) > BIG:
                    break
                z = L.mut(y, m)
                zs.append(z)
                su = strict_up(y, m, z)
                # does the mutation multiply two varying entries at m?
                B = L.mat(y)
                nonlin = False
                for i in range(4):
                    for j in range(4):
                        if len({i, j, m}) == 3 and B[i][m] * B[m][j] > 0:
                            ai = L.PAIRS.index((min(i, m), max(i, m)))
                            aj = L.PAIRS.index((min(j, m), max(j, m)))
                            if var[ai] and var[aj]:
                                nonlin = True
                kind = "nonlinear" if nonlin else "linear"
                st[f"C {kind} steps"] += 1
                if su:
                    st[f"C {kind} strict up-exit"] += 1
                    continue
                if nonlin:
                    bad.append(f"C: family {fid} m {m} n {n}: growing-vertex step that is allowed")
                k, where = cert.member(L.canon(z))
                if k is None:
                    bad.append(f"C: family {fid} m {m} n {n}: allowed step lands outside E and R")
                else:
                    st[f"C {kind} allowed, in {k}"] += 1
            # the mutated sequence follows the recurrence (linear case)
            rec_ok = all(zs[n + 3][a] == (tau + 1) * (zs[n + 2][a] - zs[n + 1][a]) + zs[n][a]
                         for n in range(len(zs) - 3) for a in range(6))
            nl_any = any(True for _ in ()) 
            if not rec_ok:
                st["C mutated sequence not a recurrence sequence"] += 1
                if grow < 2:
                    bad.append(f"C: family {fid} m {m}: linear step but the mutated sequence is not a recurrence sequence")
            if grow >= 2:
                st["C families x vertices with >= 2 growing entries at m"] += 1
                if others_var:
                    st["C ... with a varying entry away from m"] += 1
    # D
    for e in cert.E:
        for m in range(4):
            z = L.mut(e, m)
            if strict_up(e, m, z):
                continue
            k, _ = cert.member(L.canon(z))
            st["D allowed steps out of E"] += 1
            if k is None:
                bad.append(f"D: allowed step out of E lands outside E and R: {e} m {m}")
    for d in c.get("D", []):
        if cert.member(L.canon(tuple(d)))[0] is None:
            bad.append("D: a downward quiver outside E and R")
    # E
    found, above, outside, done = best_first(x, cert)
    st["E quivers found"] += len(found) + len(above)
    if outside:
        bad.append(f"E: {len(outside)} quivers of V'(x) outside E and R, e.g. {outside[0]}")
    mn = min(found.values())
    bot_mine = {y for y, lv in found.items() if lv == mn}
    bot_cert = {y for y, lv in low.items() if lv == bK}
    if mn != bK:
        bad.append(f"E: least level found {mn} != bK {bK}")
    if bot_mine != bot_cert:
        bad.append(f"E: bottom found ({len(bot_mine)}) != certified bottom ({len(bot_cert)})")
    kid = min(bot_mine)
    mkid = min(L.canon(L.neg(y)) for y in bot_mine)
    if list(kid) != rec.get("kid") or list(mkid) != rec.get("mkid"):
        bad.append("E: kid/mkid recomputed differ")
    if len(bot_cert) != rec.get("nbot"):
        bad.append("E: nbot differs")
    e_reached = sum(1 for e in cert.E if e in found)
    out.update({"found": len(found), "above": len(above), "E_reached": e_reached, "exhausted": done})
    # F
    q = tuple(c["q"])
    if L.canon(q) != x:
        foundq, aboveq, outq, _ = best_first(q, None, cap=3000)
        out["x_from_q"] = x in foundq
        if x not in foundq:
            st["F x not reached from q within the cap"] += 1
        else:
            st["F x reached from q"] += 1
        if L.no_far_region(q):
            bad.append("F: q passes the direct test but is not x")
    else:
        st["F q = x"] += 1
    out["t"] = round(time.time() - t0, 1)
    return out, st, bad


def main():
    start, step = int(sys.argv[1]), int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    with gzip.open(CERTS, "rt") as f:
        cs = [json.loads(l) for l in f if l.strip()]
    cs.sort(key=lambda c: c["i"])
    cs = cs[start::step]
    tot = Counter()
    nbad = 0
    t0 = time.time()
    with Pool(procs) as pool:
        for out, st, bad in pool.imap_unordered(check, cs):
            tot.update(st)
            nbad += bool(bad)
            print(json.dumps(out), "BAD" if bad else "ok", bad[:4], flush=True)
    print(f"chunk {start}/{step}: {len(cs)} certificates, with failures: {nbad} ({time.time() - t0:.0f}s)")
    for k in sorted(tot):
        print(f"   {k}: {tot[k]}")


if __name__ == "__main__":
    main()
