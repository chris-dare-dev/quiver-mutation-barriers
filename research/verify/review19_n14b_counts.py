"""Review 2 of note 14 (n14b): recount the tables of sections 4 and 8 from the stored outputs
n4_opposite_cores.jsonl.gz, n4_opposite_plateaus.jsonl.gz, n4_opposite_tubes.jsonl.gz, and the census
files, with independent code (review19_n14b_lib).  Run from experiments/ with python -I."""
import gzip
import json
import os
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L

t0 = time.time()


def load(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---- the census, read directly (notes 8 and 10): which bottoms come from which file
CENSUS = [("n4_classes_B512.jsonl", 1, 4), ("n4_classes_k5_B512.jsonl", 5, 5), ("n4_classes_k67_B256.jsonl", 6, 7),
          ("n4_classes_k8_B192.jsonl.gz", 8, 8), ("n4_classes_k9_B192.jsonl.gz", 9, 9)]
census_q = []
census_b = []
for fn, lo, hi in CENSUS:
    op = gzip.open if fn.endswith(".gz") else open
    with op(fn, "rt") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if lo <= r["bottom"] <= hi:
                B = r["bottom_quiver"]
                t = tuple(B[i][j] for (i, j) in L.PAIRS)
                census_q.append(t)
                census_b.append(r["bottom"])
print(f"census rows read: {len(census_q)}", flush=True)

cores = load("n4_opposite_cores.jsonl.gz")
plats = load("n4_opposite_plateaus.jsonl.gz")
tubes = {r["i"]: r for r in load("n4_opposite_tubes.jsonl.gz")}
N = len(cores)
bad = Counter()
if N != len(census_q):
    bad["cores file and census differ in length"] += 1
for a, c in enumerate(cores):
    if c["i"] != a:
        bad["cores index out of order"] += 1
    if c["b"] != census_b[a]:
        bad["cores bottom differs from census"] += 1
    if tuple(c["q"]) != L.canon(census_q[a]):
        bad["cores q is not the canonical census bottom quiver"] += 1
    if L.level(census_q[a]) != census_b[a]:
        bad["census bottom quiver level != bottom"] += 1
for a, p in enumerate(plats):
    if p["i"] != a or p["b"] != census_b[a]:
        bad["plateaus index/bottom mismatch"] += 1
print(f"consistency of stored files with the census: {dict(bad)} ({time.time() - t0:.0f}s)", flush=True)

# ---- section 4, cores table
by = defaultdict(Counter)
for c in cores:
    by[c["b"]]["classes"] += 1
    by[c["b"]]["finite"] += c["ex"]
    by[c["b"]]["capped"] += not c["ex"]
tot = Counter()
print("bottom: classes / finite core / capped")
for b in sorted(by):
    tot.update(by[b])
    print(f"  {b}: {by[b]['classes']} / {by[b]['finite']} / {by[b]['capped']}")
print(f"  all: {tot['classes']} / {tot['finite']} / {tot['capped']}")
fin = [c for c in cores if c["ex"]]
sizes = Counter(c["n"] for c in fin)
maxn = max(c["n"] for c in fin)
maxtop = max(c["top"] for c in fin)
print(f"finite cores {len(fin)}; largest {maxn}; highest level {maxtop}; size 1: {sizes[1]}, size 2: {sizes[2]}, "
      f"size 4: {sizes[4]}; top > 192: {sum(1 for c in fin if c['top'] > 192)}; top > 512: {sum(1 for c in fin if c['top'] > 512)}")
print(f"  share with a finite core by bottom: " + ", ".join(f"{b}: {by[b]['finite'] / by[b]['classes']:.3f}" for b in sorted(by)))
vids = Counter(tuple(c["vid"]) for c in fin)
print(f"distinct vid among finite cores: {len(vids)}; shared: {sum(1 for v in vids.values() if v > 1)}")
print(f"finite cores containing an acyclic quiver: {sum(1 for c in fin if c['acyc'])}; census bottom quiver outside the core: "
      f"{sum(1 for c in fin if not c['qin'])}")
print(f"finite cores with a quiver passing the direct test (ncert > 0): {sum(1 for c in fin if c['ncert'] > 0)}")

# ---- separation of the capped classes
unres = [c for c in cores if not c["ex"]]
sep = Counter()
mine_in = Counter()
for c in unres:
    a = L.no_far_region(tuple(c["q"]))
    mine_in[(c["in"], a)] += 1
    if c["in"]:
        sep["in"] += 1
    elif c["hc"] > maxtop:
        sep["hc > maxtop"] += 1
    else:
        sep["other"] += 1
print(f"capped classes: {len(unres)}; split {dict(sep)}; stored 'in' vs my direct test on q: {dict(mine_in)}")
left51 = [c["i"] for c in unres if not c["in"] and c["hc"] <= maxtop]
print(f"  the leftover classes: {left51}")

# ---- mirror map from the plateaus file
owner = {}
clash = 0
for p in plats:
    for c in p["comps"]:
        k = tuple(c["k"])
        if k in owner and owner[k] != p["i"]:
            clash += 1
        owner.setdefault(k, p["i"])
mirror = []
incons = 0
for p in plats:
    js = {owner.get(tuple(c["mk"])) for c in p["comps"]}
    if len(js) != 1 or None in js:
        incons += 1
    mirror.append(sorted(js, key=lambda v: (v is None, v))[0])
invol = sum(1 for i in range(N) if mirror[i] is not None and mirror[mirror[i]] != i)
selfm = [i for i in range(N) if mirror[i] == i]
pairs = [(i, mirror[i]) for i in range(N) if mirror[i] is not None and i < mirror[i]]
ncomp = sum(len(p["comps"]) for p in plats)
print(f"bottom components {ncomp}; plateau keys in two classes: {clash}; classes without a single mirror class: {incons}; "
      f"mirror map not an involution: {invol}; self-mirror {len(selfm)}; pairs {len(pairs)}")
acyc = [any(c["acyc"] for c in p["comps"]) for p in plats]

tab = defaultdict(Counter)
pbad = Counter()
for i, j in pairs:
    b = cores[i]["b"]
    if cores[j]["b"] != b:
        pbad["pair with different bottoms"] += 1
    ci, cj = cores[i], cores[j]
    if ci["ex"] != cj["ex"]:
        pbad["finite core for one class only"] += 1
    byc = False
    if ci["ex"] and cj["ex"]:
        byc = ci["vid"] != cj["vid"]
        if ci["mvid"] != cj["vid"] or cj["mvid"] != ci["vid"]:
            pbad["mirror core is not the core of the mirror class"] += 1
    if acyc[i] != acyc[j]:
        pbad["acyclic in one class only"] += 1
    byk = acyc[i] or acyc[j]
    tab[b]["pairs"] += 1
    tab[b]["core"] += byc
    tab[b]["ck"] += byk
    tab[b]["either"] += byc or byk
    tab[b]["both"] += byc and byk
print("mirror pairs by bottom: pairs / by core / by acyclic / either / open / both")
tot = Counter()
for b in sorted(tab):
    t = tab[b]
    tot.update(t)
    print(f"  {b}: {t['pairs']} / {t['core']} / {t['ck']} / {t['either']} / {t['pairs'] - t['either']} / {t['both']}")
print(f"  all: {tot['pairs']} / {tot['core']} / {tot['ck']} / {tot['either']} / {tot['pairs'] - tot['either']} / {tot['both']}; "
      f"failures {dict(pbad)}")
sm_fin = [i for i in selfm if cores[i]["ex"]]
print(f"self-mirror classes with a finite core: {len(sm_fin)}; vid == mvid: {sum(1 for i in sm_fin if cores[i]['vid'] == cores[i]['mvid'])}")
print(f"classes with an acyclic quiver in a bottom plateau: {sum(acyc)}; of these capped: {sum(1 for c in unres if acyc[c['i']])}")

# ---- section 8, tube certificates
print(f"tube records: {len(tubes)}; keys equal the capped classes: {set(tubes) == {c['i'] for c in unres}}")
cert = {i: r for i, r in tubes.items() if r["status"] == "certified"}
nokid = sum(1 for r in cert.values() if r.get("kid") is None)
tb = defaultdict(Counter)
for i, r in tubes.items():
    tb[r["b"]]["classes"] += 1
    tb[r["b"]]["cert"] += r["status"] == "certified"
print("tubes by bottom: classes / certified / not: " + "; ".join(f"{b}: {tb[b]['classes']}/{tb[b]['cert']}/{tb[b]['classes'] - tb[b]['cert']}" for b in sorted(tb)))
print(f"certified {len(cert)}, without kid {nokid}")
reasons = Counter()
for r in tubes.values():
    if r["status"] != "certified":
        s = r["status"]
        reasons["E cap" if "E cap" in s else "no periodic" if "no periodic" in s else "families" if "families" in s
                else "undetermined" if "undetermined" in s else "time" if "time budget" in s else s] += 1
print(f"failure reasons (grouped): {dict(reasons)}")
tau2 = sum(1 for r in cert.values() if 2 in r["taus"])
print(f"certified classes with a tau = 2 family: {tau2}")
sep_ok = sum(1 for r in cert.values() if r["bK"] < r["lR3"])
print(f"certified with bK < lR3: {sep_ok}")
kids = Counter(tuple(r["kid"]) for r in cert.values())
print(f"distinct kid: {len(kids)}; shared: {sum(1 for v in kids.values() if v > 1)}")
# kid canonical?
noncanon = sum(1 for r in cert.values() if L.canon(tuple(r["kid"])) != tuple(r["kid"]) or L.canon(tuple(r["mkid"])) != tuple(r["mkid"]))
print(f"kid or mkid not canonical: {noncanon}")
# a tube kid equal to a quiver that is the vid of a finite core?  (should never happen)
print(f"tube kid equal to a finite-core vid: {sum(1 for k in kids if k in vids)}")
above = sum(1 for i, r in cert.items() if L.level(tuple(r["kid"])) != cores[i]["b"])
print(f"bottom of the core above the census bottom: {above}; at it: {len(cert) - above}")
mm = sum(1 for i, r in cert.items() if (r["kid"] == r["mkid"]) != (mirror[i] == i))
print(f"kid == mkid disagrees with the census mirror map: {mm}; self: {sum(1 for r in cert.values() if r['kid'] == r['mkid'])}")

ct = defaultdict(Counter)
cbad = Counter()
for i in range(N):
    b = cores[i]["b"]
    fc = cores[i]["ex"]
    tc = i in cert
    ct[b]["classes"] += 1
    ct[b]["fin"] += fc
    ct[b]["tube"] += tc
    j = mirror[i]
    if j == i:
        ct[b]["self"] += 1
        ct[b]["self known"] += fc or tc
        if tc and cert[i]["kid"] != cert[i]["mkid"]:
            cbad["self-mirror tube class with kid != mkid"] += 1
    elif j is not None and i < j:
        ct[b]["pairs"] += 1
        both_f = cores[i]["ex"] and cores[j]["ex"] and cores[i]["vid"] != cores[j]["vid"]
        both_t = i in cert and j in cert
        if both_t:
            ri, rj = cert[i], cert[j]
            if not (ri["kid"] == rj["mkid"] and rj["kid"] == ri["mkid"] and ri["kid"] != rj["kid"]):
                cbad["tube pair: bottoms not mirror images or equal"] += 1
        if (i in cert) != (j in cert):
            cbad["tube pair: one class certified only"] += 1
        byc = both_f or both_t
        ct[b]["by cores"] += byc
        ct[b]["with ck"] += byc or acyc[i] or acyc[j]
print("combined: bottom: classes / finite / tube / neither ; pairs / by cores / with CK / open ; self / known")
tot = Counter()
for b in sorted(ct):
    t = ct[b]
    tot.update(t)
    print(f"  {b}: {t['classes']} / {t['fin']} / {t['tube']} / {t['classes'] - t['fin'] - t['tube']} ; {t['pairs']} / "
          f"{t['by cores']} / {t['with ck']} / {t['pairs'] - t['with ck']} ; {t['self']} / {t['self known']}")
t = tot
print(f"  all: {t['classes']} / {t['fin']} / {t['tube']} / {t['classes'] - t['fin'] - t['tube']} ; {t['pairs']} / "
      f"{t['by cores']} / {t['with ck']} / {t['pairs'] - t['with ck']} ; {t['self']} / {t['self known']}; failures {dict(cbad)}")
print(f"pairwise certified different (finite + tube): {t['fin'] + t['tube']} = {(t['fin'] + t['tube']) / N:.4f}")
print(f"({time.time() - t0:.0f}s)")
