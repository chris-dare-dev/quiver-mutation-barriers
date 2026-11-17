"""Review 3 of note 22, items 4 and 5: the disconnected classes by rank 3, the acyclic-bottom classes, and
the tau digits of note 14's certificates.  Own code (review23_n22_lib); data from the stored records.

  A. the 400 disconnected classes: component structure of every bottom quiver; for a triangle plus an isolated
     vertex, the rank-3 descent of note 3 (Step 1) to a root or an acyclic quiver, and BBH's criterion
     (oriented, weights >= 2, C <= 4) as a crosscheck; for a root, T ~ -T decided two ways:
       (i)  the criterion of note 22 §6.1: two equal weights or a flat step (2z = xy);
       (ii) directly from Theorem 3.1: the roots of the class are the closure of one root under flat steps
            (weight-keeping mutations); T ~ -T iff -R is among them up to relabelling;
     compared with the census mirror map.
  B. the 1,556 acyclic-bottom classes: an acyclic quiver is found by my own search from the bottom components
     (mutations through quivers of level <= b, the census bottom), for every class.
  C. note 14's certificates: the number of digits of the largest tau.
Usage: python -I review23_n22_rank3.py > review23_n22_rank3.log"""
import gzip
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L


def load(p):
    with gzip.open(p, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


plats = {r["i"]: r for r in load("n4_opposite_plateaus.jsonl.gz")}
cls = {r["i"]: r for r in load("n4_tube_classify.jsonl.gz")}
owner = {}
for i, p in plats.items():
    for c in p["comps"]:
        owner[tuple(c["k"])] = i
mirror = {i: owner[tuple(p["comps"][0]["mk"])] for i, p in plats.items()}


def tri_canon(T3):
    """3-vertex quiver (b_ab, b_bc, b_ca) up to relabelling: rotations and reflections (a reflection reverses
    the cycle and negates)."""
    x, y, z = T3
    cands = [(x, y, z), (y, z, x), (z, x, y), (-x, -z, -y), (-z, -y, -x), (-y, -x, -z)]
    return max(cands)


def tri_mutate(T3, v):
    """Mutate the triangle (b_ab, b_bc, b_ca) at vertex v in {0: a, 1: b, 2: c}; uses the 4-vertex mutation."""
    x, y, z = T3
    t = (0, 0, 0, x, -z, y)
    u = L.mutate(t, v + 1)
    return (L.e(u, 1, 2), L.e(u, 2, 3), L.e(u, 3, 1))


def flat_closure(R):
    seen = {tri_canon(R)}
    todo = [R]
    while todo:
        T = todo.pop()
        w = sorted(abs(a) for a in T)
        for v in range(3):
            U = tri_mutate(T, v)
            if sorted(abs(a) for a in U) == w:
                c = tri_canon(U)
                if c not in seen:
                    seen.add(c)
                    todo.append(U)
    return seen


# ---------------------------------------------------------------- A
print("A. disconnected classes")
dis = [i for i in cls if cls[i]["disc"]]
tab = Counter()
crit_vs_direct = Counter()
for i in sorted(dis):
    shapes = set()
    res = set()
    for c in plats[i]["comps"]:
        k = tuple(c["k"])
        comps = L.components(k)
        shape = tuple(sorted(len(cc) for cc in comps))
        shapes.add(shape)
        if shape == (1, 3):
            g = next(cc[0] for cc in comps if len(cc) == 1)
            T3 = L.tri_entries(k, g)
            kind, w = L.rank3_root(T3)
            bbh = L.tri_oriented(T3) and min(abs(a) for a in T3) >= 2 and L.markov_C(T3) <= 4
            # descent from the census bottom: T3 is minimal, so it should itself be a root or acyclic
            if kind == "root":
                # rebuild the root as signed entries: rank3_root returns weights around the cycle
                R = w
                x, y, z = R
                crit = len(set(R)) < 3 or 2 * z == x * y or 2 * x == y * z or 2 * y == x * z
                roots = flat_closure(R)
                # R as signed entries around its cycle is (x, y, z), -R is (-x, -y, -z); tri_canon handles relabelling
                direct = tri_canon((-x, -y, -z)) in roots
                res.add(("root", crit, direct, bbh))
            else:
                res.add((kind, None, None, bbh))
        else:
            res.add(("no triangle", None, None, False))
    if len(shapes) != 1 or len(res) != 1:
        tab["components of one class disagree"] += 1
        print("   disagree:", i, shapes, res)
        continue
    shape = shapes.pop()
    kind, crit, direct, bbh = res.pop()
    selfm = mirror[i] == i
    if kind == "root":
        tab[("mutation-cyclic triangle", "self-mirror" if selfm else "mirror pair", "criterion T~-T" if crit else "criterion T!~-T")] += 1
        crit_vs_direct[(crit, direct)] += 1
        tab["BBH criterion agrees with descent"] += bbh
    else:
        tab[("not mutation-cyclic", str(shape), kind, "self-mirror" if selfm else "mirror pair")] += 1
        tab["BBH criterion says cyclic for a non-root (should be 0)"] += bbh
for k, v in sorted(tab.items(), key=str):
    print(f"   {v:5d}  {k}")
print("   (criterion of §6.1, direct flat-step closure of Theorem 3.1):", dict(crit_vs_direct))
cyc_pairs = [i for i in dis if mirror[i] != i]
print(f"   disconnected classes in census mirror pairs: {len(cyc_pairs)}; acyc flag among the disconnected: "
      f"{sum(1 for i in dis if cls[i]['acyc'])}")

# ---------------------------------------------------------------- B
print("\nB. acyclic-bottom classes: an acyclic quiver by my own search")
acb = [i for i in cls if not cls[i]["disc"] and cls[i]["acyc"]]
found = Counter()
for i in acb:
    b = cls[i]["b"]
    hit = None
    for c in plats[i]["comps"]:
        k = tuple(c["k"])
        if L.is_acyclic(k):
            hit = ("bottom quiver itself", k)
            break
        seen = {k}
        todo = [k]
        while todo and hit is None and len(seen) < 20000:
            y = todo.pop()
            for m in range(4):
                z = L.mutate(y, m)
                if L.level(z) > b:
                    continue
                cz = L.canon(z)
                if cz in seen:
                    continue
                if L.is_acyclic(cz):
                    hit = ("on the plateau", cz)
                    break
                seen.add(cz)
                todo.append(cz)
        if hit:
            break
    found[hit[0] if hit else "NOT FOUND"] += 1
print(f"   {len(acb)} classes: {dict(found)}")

# ---------------------------------------------------------------- C
print("\nC. note 14 certificates: digits of the largest tau")
t50 = [r for r in load("n4_opposite_tubes.jsonl.gz") if r["status"] == "certified"]
dig = Counter(len(str(max(r["taus"]))) for r in t50)
print(f"   {len(t50)} certificates: {dict(sorted(dig.items()))}; largest tau: {max(max(r['taus']) for r in t50)}")
