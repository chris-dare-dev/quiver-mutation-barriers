"""Review 2 of note 14 (n14b): summarise the full-census run of review19_n14b_full.py (my own code) and
compare it class by class with n4_opposite_cores.jsonl.gz and n4_opposite_plateaus.jsonl.gz.
Run from experiments/ with python -I."""
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L

files = sorted(glob.glob(os.path.expanduser("~/.cache/qmb-review19/n14b_full_*.jsonl.gz")))
mine = {}
for fn in files:
    with gzip.open(fn, "rt") as f:
        for l in f:
            if l.strip():
                r = json.loads(l)
                mine[r["i"]] = r
with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
    cores = [json.loads(l) for l in f if l.strip()]
with gzip.open("n4_opposite_plateaus.jsonl.gz", "rt") as f:
    plats = [json.loads(l) for l in f if l.strip()]
N = len(cores)
print(f"files {len(files)}; classes in my run: {len(mine)} of {N}; missing: {N - len(mine)}")
bad = Counter()
by = defaultdict(Counter)
for i, c in enumerate(cores):
    r = mine.get(i)
    if r is None:
        continue
    b = c["b"]
    by[b]["classes"] += 1
    by[b]["finite"] += r["c"]
    if r["c"] != c["ex"]:
        bad["finite/capped differs from stored"] += 1
        continue
    if r["c"]:
        if r.get("ns") != 1:
            bad["not exactly one minimal closed set"] += 1
            continue
        for k in ("n", "vid", "mvid", "top", "acyc", "nv"):
            if r[k] != c[k]:
                bad[f"field {k} differs from stored"] += 1
    if r["pk"] not in [x["k"] for x in plats[i]["comps"]]:
        bad["plateau key of q not among the stored bottom components"] += 1
tot = Counter()
print("my run, bottom: classes / finite core / capped")
for b in sorted(by):
    tot.update(by[b])
    print(f"  {b}: {by[b]['classes']} / {by[b]['finite']} / {by[b]['classes'] - by[b]['finite']}")
print(f"  all: {tot['classes']} / {tot['finite']} / {tot['classes'] - tot['finite']}")
fin = [r for r in mine.values() if r["c"] and r.get("ns") == 1]
sizes = Counter(r["n"] for r in fin)
maxn = max(r["n"] for r in fin)
maxtop = max(r["top"] for r in fin)
vids = Counter(tuple(r["vid"]) for r in fin)
print(f"finite cores {len(fin)}; largest {maxn}; highest level {maxtop}; size1 {sizes[1]} size2 {sizes[2]} size4 {sizes[4]}; "
      f"top>192 {sum(1 for r in fin if r['top'] > 192)}; top>512 {sum(1 for r in fin if r['top'] > 512)}; "
      f"distinct vid {len(vids)}; with an acyclic quiver {sum(1 for r in fin if r['acyc'])}")
sep = Counter(r.get("sep") for r in mine.values() if not r["c"])
why = Counter(r.get("why") for r in mine.values() if r.get("sep") == "in")
print(f"separation of the capped classes (my searches): {dict(sep)}; 'in' stopped by: {dict(why)}")
cmp = Counter()
for r in mine.values():
    if r["c"]:
        continue
    c = cores[r["i"]]
    stored = "in" if c["in"] else ("hc" if c["hc"] > 1312 else "closure")
    cmp[(stored, r["sep"])] += 1
print(f"stored separation reason vs mine: {dict(cmp)}")
none = [r["i"] for r in mine.values() if r.get("sep") == "none"]
print(f"not separated by my searches: {none[:20]}")
# mirror map from my plateau keys of q and -q, against the stored bottom components
owner = {}
for p in plats:
    for x in p["comps"]:
        owner.setdefault(tuple(x["k"]), p["i"])
stored_mirror = [owner.get(tuple(p["comps"][0]["mk"])) for p in plats]
mm = Counter()
for i, r in mine.items():
    j = owner.get(tuple(r["mpk"]))
    mm["mirror class from my plateau of -q equals the stored mirror" if j == stored_mirror[i] else "differs"] += 1
print(f"mirror map: {dict(mm)}")
# pairs certified by the core, recounted from my run
pairs = [(i, stored_mirror[i]) for i in range(N) if stored_mirror[i] is not None and i < stored_mirror[i]]
pc = Counter()
for i, j in pairs:
    ri, rj = mine.get(i), mine.get(j)
    if ri is None or rj is None:
        pc["pair not in my run"] += 1
        continue
    if ri["c"] and rj["c"]:
        pc["both finite"] += 1
        if ri["vid"] != rj["vid"]:
            pc["by the core (different cores)"] += 1
        if ri["mvid"] != rj["vid"]:
            pc["mirror core is not the core of the mirror class"] += 1
    elif ri["c"] != rj["c"]:
        pc["finite for one class only"] += 1
print(f"mirror pairs (my cores): {dict(pc)}")
sm = [i for i in range(N) if stored_mirror[i] == i and mine[i]["c"]]
print(f"self-mirror with a finite core (mine): {len(sm)}; core self-mirror: {sum(1 for i in sm if mine[i]['vid'] == mine[i]['mvid'])}")
print(f"failures: {dict(bad)}")
