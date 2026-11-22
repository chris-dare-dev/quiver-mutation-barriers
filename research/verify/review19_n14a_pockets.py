"""Check A of note 14, Proposition 14.3: spot-check of the pocket listing on sampled finite-core classes.

For each sampled class: own core (independent library, from the recorded bottom quiver), own extended core
K^ (core + roots of the far regions hanging from it, joined to their feet), own elder-rule persistence
pairs; compared with n4_opposite_pockets.jsonl.gz and with the census pairs of notes 8/22 (all pairs with
death <= the census bound).  Also: balanced edges, root kinds, and whether any hanging far region
contains a core quiver (checked by exploring each region to a radius).

  python -I review19_n14a_pockets.py N SEED
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
from review19_n14a_gk import persistence

CENSUS = [("n4_classes_B512.jsonl", 1, 4, 512), ("n4_classes_k5_B512.jsonl", 5, 5, 512),
          ("n4_classes_k67_B256.jsonl", 6, 7, 256), ("n4_classes_k8_B192.jsonl.gz", 8, 8, 192),
          ("n4_classes_k9_B192.jsonl.gz", 9, 9, 192)]


def census_iter():
    for fn, lo, hi, B in CENSUS:
        op = gzip.open if fn.endswith(".gz") else open
        with op(fn, "rt") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if lo <= r["bottom"] <= hi:
                    yield B, r


def own_khat(q):
    res = L.core_of(L.from6(q), cap=5000)
    if res is None:
        return None
    rep, adj, ups, sinks = res
    if len(sinks) != 1:
        return "several sinks"
    K = sinks[0]
    levels = {x: L.level(rep[x]) for x in K}
    g = {x: set() for x in K}
    for x in K:
        for v in range(4):
            y = L.key(L.mut(rep[x], v))
            if y in K and y != x:
                g[x].add(y)
                g[y].add(x)
    roots = {}
    for x, m, Y in ups:
        if x not in K:
            continue
        y = L.key(Y)
        if y in K:
            return "root inside the core"
        if y not in levels:
            levels[y] = L.level(Y)
            g[y] = set()
            roots[y] = (Y, m, "fork" if L.fork_returns(Y) == {m} else "pre-fork")
        g[y].add(x)
        g[x].add(y)
    balanced = sum(1 for x in K for m in L.exit_vertices(rep[x])
                   if L.key(L.mut(rep[x], m)) in K and m in L.exit_vertices(L.mut(rep[x], m)))
    return K, rep, levels, g, roots, balanced


def region_hits_core(Y, m, K, radius):
    roots = [Y]
    lp = L.light_pairs(Y)
    if lp and abs(Y[lp[0][0]][lp[0][1]]) == 1:
        k, kp = lp[0]
        X = Y
        for v in (k, kp, k, kp, k):
            X = L.mut(X, v)
        roots.append(X)
    seen = set(roots)
    front = list(roots)
    for _ in range(radius):
        nxt = []
        for z in front:
            for v in range(4):
                if z in roots and v == m:
                    continue
                y = L.mut(z, v)
                if y not in seen:
                    seen.add(y)
                    if L.key(y) in K:
                        return True
                    nxt.append(y)
        front = nxt
    return False


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    t0 = time.time()
    pk = {}
    with gzip.open("n4_opposite_pockets.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            pk[r["i"]] = r
    cats = {"pre-fork roots, pocket born above the bottom": [], "pre-fork roots, pockets at the bottom only": [],
            "fork roots only, with pockets": [], "any": list(pk)}
    for i, r in pk.items():
        if r["npre"] > 0 and any(b > r["lo"] for b, d in r["pairs"]):
            cats["pre-fork roots, pocket born above the bottom"].append(i)
        elif r["npre"] > 0 and r["pairs"]:
            cats["pre-fork roots, pockets at the bottom only"].append(i)
        elif r["npre"] == 0 and r["pairs"]:
            cats["fork roots only, with pockets"].append(i)
    nc0 = []
    with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["ex"] and r["ncert"] == 0:
                nc0.append(r["i"])
    cats["no core quiver passes the direct test (balanced-edge candidates)"] = nc0
    picks = {}
    for c, lst in cats.items():
        for i in rng.sample(sorted(lst), min(N, len(lst))):
            picks.setdefault(i, c)
    for i, c in ((199416, "extreme 101/64"), (193314, "fork-only extreme 0.703")):
        picks[i] = c
    print(f"sampled classes: {Counter(picks.values())}", flush=True)
    rows = {}
    for idx, (B, r) in enumerate(census_iter()):
        if idx in picks:
            rows[idx] = (B, r)
    st = Counter()
    bad = []
    for i, c in sorted(picks.items()):
        B, r = rows[i]
        q = L.to6(L.from_rows(r["bottom_quiver"]))
        res = own_khat(q)
        if not isinstance(res, tuple):
            st[f"own core: {res}"] += 1
            bad.append((i, c, res))
            continue
        K, rep, levels, g, roots, balanced = res
        mine = persistence(levels, g)
        theirs = sorted(tuple(p) for p in pk[i]["pairs"])
        cen = sorted((p["birth"], p["death"]) for p in r["pairs"] if p["death"] is not None and p["birth"] < p["death"])
        mine_le_B = [p for p in mine if p[1] <= B]
        kinds = Counter(v[2] for v in roots.values())
        hit = any(region_hits_core(Y, m, K, 4) for Y, m, kd in roots.values())
        st["classes"] += 1
        st[f"{c}"] += 1
        st["own pairs == pockets file"] += mine == theirs
        st["own pairs (death <= census bound) == census pairs"] += mine_le_B == cen
        st["own number of roots == pockets file nroots"] += len(roots) == pk[i]["nroots"]
        st["cores with a balanced edge"] += balanced > 0
        st["a hanging far region meets the core within radius 4"] += hit
        if mine != theirs or mine_le_B != cen:
            bad.append((i, c, mine, theirs, cen, B))
        print(f"  class {i} ({c}): bottom {r['bottom']}, core {len(K)}, roots {dict(kinds)}, balanced {balanced}; "
              f"pairs {mine}; file {theirs}; census {cen}", flush=True)
    for k in sorted(st):
        print(f"  {k}: {st[k]}")
    print("mismatches:", bad if bad else "none")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
