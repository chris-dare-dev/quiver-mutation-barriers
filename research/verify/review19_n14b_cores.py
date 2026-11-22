"""Review 2 of note 14 (n14b): recompute cores from scratch with independent code (review19_n14b_lib) for
a stratified random sample of finite-core census classes, and compare with n4_opposite_cores.jsonl.gz
(every stored field) and, as sets of canonical quivers, with n4_opposite.core (imported only for that
comparison, in the parent after the independent computation).  Also mirror pairs and self-mirror classes:
the cores of the two classes of a pair are mirror images and different; a self-mirror class has a
self-mirror core; the mirror class of the plateaus file contains the mirror image of the bottom quiver in a
bottom component (my own plateau search).  Collects the roots of pre-fork far regions hanging from the
cores for review19_n14b_prefork.py.
Usage: python -I review19_n14b_cores.py SEED PER_BOTTOM PAIRS SELF"""
import gzip
import json
import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L

ROOTS = os.path.expanduser("~/.cache/qmb-review19/n14b_prefork_roots.jsonl.gz")
os.makedirs(os.path.dirname(ROOTS), exist_ok=True)


def census():
    CENSUS = [("n4_classes_B512.jsonl", 1, 4), ("n4_classes_k5_B512.jsonl", 5, 5), ("n4_classes_k67_B256.jsonl", 6, 7),
              ("n4_classes_k8_B192.jsonl.gz", 8, 8), ("n4_classes_k9_B192.jsonl.gz", 9, 9)]
    qs = []
    for fn, lo, hi in CENSUS:
        op = gzip.open if fn.endswith(".gz") else open
        with op(fn, "rt") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if lo <= r["bottom"] <= hi:
                        B = r["bottom_quiver"]
                        qs.append(tuple(B[i][j] for (i, j) in L.PAIRS))
    return qs


def plateau_key(t):
    s = L.canon(t)
    m = L.level(s)
    seen = {s}
    todo = [s]
    while todo:
        x = todo.pop()
        for k in range(4):
            y = L.mut(x, k)
            if L.level(y) <= m:
                c = L.canon(y)
                if c not in seen:
                    seen.add(c)
                    todo.append(c)
    return min(seen)


def job(a):
    i, q = a
    t0 = time.time()
    lev, adj, complete, _ = L.vprime(q, cap=800, level_cap=10 ** 6)
    out = {"i": i, "complete": complete, "nv": len(lev)}
    if not complete:
        return out
    sinks = L.sink_sccs(adj)
    out["nsinks"] = len(sinks)
    K = sinks[0] if len(sinks) == 1 else set()
    out["K"] = sorted(K)
    if K:
        lo = min(lev[x] for x in K)
        out.update({"n": len(K), "vid": list(min(K)), "mvid": list(min(L.canon(L.neg(x)) for x in K)),
                    "top": max(lev[x] for x in K), "lo": lo, "nlo": sum(1 for x in K if lev[x] == lo),
                    "qin": L.canon(q) in K, "ncert": sum(1 for x in K if L.no_far_region(x)),
                    "zero": sum(1 for x in K if 0 in x), "vortex": sum(1 for x in K if L.is_vortex(x)),
                    "acyc": sum(1 for x in K if L.is_acyclic_q(x))})
        pre = 0
        roots = []
        for x in K:
            ex = L.exits(x)
            for m in range(4):
                y = L.mut(x, m)
                ey = L.exits(y)
                if m in ey and m not in ex:
                    if not L.fork_points(L.mat(y), [0, 1, 2, 3]):
                        pre += 1
                        roots.append((list(y), m))
        out["pre"] = pre
        out["roots"] = roots
        # balanced edges inside K (both ends exits for the same vertex)
        bal = 0
        for x in K:
            for m in L.exits(x):
                if L.canon(L.mut(x, m)) in K and m in L.exits(L.mut(x, m)):
                    bal += 1
        out["bal"] = bal
    out["t"] = round(time.time() - t0, 2)
    return out


def main():
    seed, per, npairs, nself = (int(v) for v in sys.argv[1:5])
    rng = random.Random(seed)
    t0 = time.time()
    qs = census()
    with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
        cores = [json.loads(l) for l in f if l.strip()]
    with gzip.open("n4_opposite_plateaus.jsonl.gz", "rt") as f:
        plats = [json.loads(l) for l in f if l.strip()]
    owner = {}
    for p in plats:
        for c in p["comps"]:
            owner.setdefault(tuple(c["k"]), p["i"])
    mirror = [owner.get(tuple(p["comps"][0]["mk"])) for p in plats]
    fin = [c for c in cores if c["ex"]]
    byb = {}
    for c in fin:
        byb.setdefault(c["b"], []).append(c["i"])
    sample = set(byb[1])
    for b in range(2, 10):
        sample.update(rng.sample(byb[b], min(per, len(byb[b]))))
    # extremes of the stored statistics
    for key in ("n", "top"):
        sample.add(max(fin, key=lambda c: c[key])["i"])
    sample.update(c["i"] for c in rng.sample([c for c in fin if c["pre"] > 0], 100))
    pairs = [(i, mirror[i]) for i in range(len(cores)) if mirror[i] is not None and i < mirror[i]
             and cores[i]["ex"] and cores[mirror[i]]["ex"]]
    pairs = rng.sample(pairs, npairs)
    selfm = rng.sample([i for i in range(len(cores)) if mirror[i] == i and cores[i]["ex"]], nself)
    todo = sorted(sample | {i for p in pairs for i in p} | set(selfm))
    print(f"classes to recompute: {len(todo)} (sample {len(sample)}, pairs {len(pairs)}, self-mirror {len(selfm)}) "
          f"({time.time() - t0:.0f}s)", flush=True)
    res = {}
    with Pool(6) as pool:
        for out in pool.imap_unordered(job, [(i, qs[i]) for i in todo], chunksize=4):
            res[out["i"]] = out
    print(f"recomputed ({time.time() - t0:.0f}s)", flush=True)
    bad = Counter()
    st = Counter()
    for i in todo:
        r, c = res[i], cores[i]
        if not r["complete"]:
            bad["my V' search hit a cap"] += 1
            continue
        if r["nsinks"] != 1:
            bad["not exactly one minimal closed set"] += 1
            continue
        for k in ("nv", "n", "vid", "mvid", "top", "lo", "nlo", "qin", "ncert", "zero", "vortex", "acyc", "pre"):
            if r[k] != c[k]:
                bad[f"field {k} differs"] += 1
        st["classes compared"] += 1
        st["cores with a balanced edge"] += r["bal"] > 0
    # full sets against n4_opposite.core
    import n4_opposite as O
    for i in todo:
        r = res[i]
        if not r.get("K"):
            continue
        K2, lev2, adj2, ex2 = O.core(qs[i], cap=800, level_cap=10 ** 6)
        if set(map(tuple, r["K"])) != set(K2):
            bad["core set differs from n4_opposite.core"] += 1
        st["core sets compared"] += 1
    # mirror pairs and self-mirror classes
    for i, j in pairs:
        Ki = {tuple(x) for x in res[i]["K"]}
        Kj = {tuple(x) for x in res[j]["K"]}
        if {L.canon(L.neg(x)) for x in Ki} != Kj:
            bad["pair: core of the mirror class is not the mirror of the core"] += 1
        if Ki == Kj or Ki & Kj:
            bad["pair: the two cores meet"] += 1
        mk = plateau_key(L.neg(qs[i]))
        if mk not in {tuple(x["k"]) for x in plats[j]["comps"]}:
            bad["pair: mirror of the bottom quiver not in a bottom component of the mirror class"] += 1
        st["pairs checked"] += 1
    for i in selfm:
        Ki = {tuple(x) for x in res[i]["K"]}
        if {L.canon(L.neg(x)) for x in Ki} != Ki:
            bad["self-mirror class with a core that is not self-mirror"] += 1
        mk = plateau_key(L.neg(qs[i]))
        if mk not in {tuple(x["k"]) for x in plats[i]["comps"]}:
            bad["self-mirror: mirror of the bottom quiver not in a bottom component of the class"] += 1
        st["self-mirror checked"] += 1
    byb_s = Counter(cores[i]["b"] for i in todo)
    print(f"by bottom: {dict(sorted(byb_s.items()))}")
    print(f"stats: {dict(st)}")
    print(f"failures: {dict(bad)}")
    sizes = Counter(res[i]["n"] for i in todo if res[i].get("K"))
    print(f"core sizes in the sample: largest {max(sizes)}; size counts {dict(sorted(sizes.items())[:12])}")
    nroots = 0
    with gzip.open(ROOTS, "wt") as f:
        for i in todo:
            for y, m in res[i].get("roots", []):
                f.write(json.dumps({"i": i, "y": y, "m": m}) + "\n")
                nroots += 1
    print(f"pre-fork roots hanging from the recomputed cores: {nroots} written to {ROOTS} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
