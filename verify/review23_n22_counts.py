"""Review 3 of note 22: recompute the counts of §6.1, §6.2, §6.3 and §7 from the stored records only
(n4_opposite_cores / _plateaus / _tubes, n4_tube_classify, n4_tube_certify2).  Own code; the mirror map is
rebuilt from the bottom components of n4_opposite_plateaus.jsonl.gz.
Usage: python -I review23_n22_counts.py > review23_n22_counts.log"""
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L


def load(p):
    with gzip.open(p, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


cores = {r["i"]: r for r in load("n4_opposite_cores.jsonl.gz")}
plats = {r["i"]: r for r in load("n4_opposite_plateaus.jsonl.gz")}
tubes = {r["i"]: r for r in load("n4_opposite_tubes.jsonl.gz")}
cls = {r["i"]: r for r in load("n4_tube_classify.jsonl.gz")}
c2 = {r["i"]: r for r in load("n4_tube_certify2.jsonl.gz")}
N = len(cores)
print(f"census classes: {N}; plateau records {len(plats)}")

# ---- mirror map from bottom components
owner = {}
for i, p in plats.items():
    for c in p["comps"]:
        k = tuple(c["k"])
        if k in owner and owner[k] != i:
            print("   component shared by two classes:", k, owner[k], i)
        owner[k] = i
mirror = {}
incons = 0
for i, p in plats.items():
    js = {owner.get(tuple(c["mk"])) for c in p["comps"]}
    if len(js) != 1 or None in js:
        incons += 1
    mirror[i] = owner.get(tuple(p["comps"][0]["mk"]))
invol = sum(1 for i in mirror if mirror[mirror[i]] != i)
selfm = [i for i in mirror if mirror[i] == i]
pairs = [(i, mirror[i]) for i in mirror if mirror[i] > i]
print(f"mirror map: inconsistent components {incons}; not an involution {invol}; self-mirror {len(selfm)}; pairs {len(pairs)}")
acyc = {i: any(c["acyc"] for c in plats[i]["comps"]) for i in plats}

fin = {i for i, r in cores.items() if r["ex"]}
t50 = {i for i, r in tubes.items() if r["status"] == "certified" and "kid" in r}
t73 = {i for i, r in c2.items() if r["status"] == "certified" and "kid" in r}
print(f"finite cores {len(fin)}; note-14 tube certificates {len(t50)}; note-22 certificates {len(t73)}; overlap 50/73 {len(t50 & t73)}")
unc = set(cls)
print(f"classify records {len(unc)}; = census minus finite core minus note-14 certified: {unc == set(cores) - fin - t50}")

# ---- note 14 pair status
def n14_status(i, j):
    a, b = i in fin or i in t50, j in fin or j in t50
    if a and b:
        return "both certified (note 14)"
    if acyc[i] or acyc[j]:
        return "Caldero-Keller"
    if a or b:
        return "OPEN in note 14 but one class certified"
    return "open"
st50 = Counter(n14_status(i, j) for i, j in pairs)
print("note 14 mirror pairs:", dict(st50))
# both certified: bottoms/cores mirror images?
bad = 0
for i, j in pairs:
    if i in t50 and j in t50:
        if tubes[i]["kid"] != tubes[j]["mkid"] or tubes[i]["kid"] == tubes[j]["kid"]:
            bad += 1
    elif i in fin and j in fin:
        if cores[i]["vid"] != cores[j]["mvid"] or cores[i]["vid"] == cores[j]["vid"]:
            bad += 1
mixed = sum(1 for i, j in pairs if (i in fin and j in t50) or (i in t50 and j in fin))
print(f"   both-certified pairs whose two invariants are not mirror images and different: {bad}; pairs with one finite core and one tube certificate: {mixed}")
both14 = sum(1 for i, j in pairs if (i in fin or i in t50) and (j in fin or j in t50))
ck_extra = sum(1 for i, j in pairs if not ((i in fin or i in t50) and (j in fin or j in t50)) and (acyc[i] or acyc[j]))
print(f"   certified by cores {both14}; with Caldero-Keller {both14 + ck_extra}; open {len(pairs) - both14 - ck_extra}")
selfcert14 = sum(1 for i in selfm if i in fin or i in t50)
print(f"   self-mirror classes with a finite core or note-14 certificate: {selfcert14}")

# ---- §6.1 table
def growth(r):
    if not r["ok2"]:
        return "cap"
    q = r["n2"] / max(1, r["n1"])
    return "quadratic" if q >= 8 else "linear" if q >= 2.5 else "slow"


def kind(i):
    r = cls[i]
    if r["disc"]:
        return "disconnected"
    if r["acyc"]:
        return "acyclic bottom"
    if r["markov"]:
        return "Markov triangle"
    return "cyclic " + growth(r)


# independent recomputation of the disconnected flag and the acyclic flag
disc_bad = sum(1 for i in cls if cls[i]["disc"] != (len(L.components(tuple(plats[i]["comps"][0]["k"]))) > 1))
acyc_bad = sum(1 for i in cls if cls[i]["acyc"] != acyc[i])
# a class is disconnected if ANY bottom quiver is: check all components agree
disc_mixed = sum(1 for i in cls if len({len(L.components(tuple(c["k"]))) > 1 for c in plats[i]["comps"]}) > 1)
print(f"\n§6.1: classify 'disc' against my component count of the first bottom component: {disc_bad} differ; "
      f"classes whose bottom components disagree on connectedness: {disc_mixed}; 'acyc' flag differs from plateaus: {acyc_bad}")
tab = defaultdict(Counter)
for i in cls:
    k = kind(i)
    j = mirror[i]
    tab[k]["classes"] += 1
    tab[k]["self"] += j == i
    tab[k]["pair"] += j != i
    tab[k]["mirror also in the 6,990"] += (j != i and j in cls)
    tab[k]["mirror in the same kind"] += (j != i and j in cls and kind(j) == k)
    if j != i and j < i:
        continue
    if j != i and n14_status(i, j) in ("open", "OPEN in note 14 but one class certified"):
        tab[k]["open pairs (note 14)"] += 1
for k in sorted(tab):
    print(f"   {k:22s} {dict(tab[k])}")
print("   growth kinds by base:", dict(Counter((('disc' if cls[i]['disc'] else 'acyc' if cls[i]['acyc'] else 'cyc'), bool(cls[i]['markov']), growth(cls[i])) for i in cls)))

# ---- §6.2 table
def reason(s):
    if s == "certified":
        return "certified"
    for key in ("E cap", "level bound", "no periodic base", "time budget", "more than", "no start"):
        if key in s:
            return key
    return s


print("\n§6.2: certify2 status by kind (level bound includes 'level bound (no periodic base ...)')")
t62 = defaultdict(Counter)
for i in cls:
    s = c2[i]["status"] if i in c2 else "missing"
    t62[kind(i)][reason(s)] += 1
    t62[kind(i)]["raw: " + s] += 0
for k in sorted(t62):
    print(f"   {k:22s} {dict((a, b) for a, b in t62[k].items() if b)}")
print("   raw statuses:", dict(Counter(c2[i]["status"] for i in cls)))
npoly = Counter(c2[i].get("npoly", 0) > 0 for i in t73)
print(f"   new certificates with at least one polynomial family: {npoly[True]} of {len(t73)}")
sep = sum(1 for i in t73 if c2[i]["bK"] < c2[i]["lR3"])
print(f"   bottom bK below lR3 (the least level of a fourth member): {sep} of {len(t73)}")

# ---- note 22 pairs
print("\nnote 22 mirror pairs among the note-14 open pairs:")
cert = lambda i: i in fin or i in t50 or i in t73
op = Counter()
contra = 0
for i, j in pairs:
    s = n14_status(i, j)
    if s not in ("open", "OPEN in note 14 but one class certified"):
        continue
    k = kind(i) if i in cls else kind(j)
    ci, cj = i in t73, j in t73
    if k == "disconnected":
        how = "disconnected"
    elif ci and cj:
        ok = c2[i]["kid"] == c2[j]["mkid"] and c2[i]["kid"] != c2[j]["kid"]
        how = "both certified by note 22" if ok else "CONTRADICTION"
    elif ci or cj or cert(i) or cert(j):
        how = "EXACTLY ONE class certified"
    else:
        how = "neither certified"
    op[(k, how)] += 1
for k, v in sorted(op.items()):
    print(f"   {v:6d}  {k[0]} | {k[1]}")
# self-mirror and pair consistency of the new certificates
s_new = sum(1 for i in t73 if mirror[i] == i)
s_ok = sum(1 for i in t73 if mirror[i] == i and c2[i]["kid"] == c2[i]["mkid"])
p_bad = sum(1 for i in t73 if mirror[i] != i and c2[i]["kid"] == c2[i]["mkid"])
p_new = sum(1 for i in t73 if mirror[i] != i)
p_mirror_cert = sum(1 for i in t73 if mirror[i] != i and mirror[i] in t73)
print(f"   new certificates: self-mirror {s_new} (kid == mkid in {s_ok}); in census pairs {p_new} "
      f"(kid == mkid, a contradiction, in {p_bad}; mirror class also newly certified in {p_mirror_cert})")

# ---- distinct bottoms
allk = Counter(tuple(tubes[i]["kid"]) for i in t50) + Counter(tuple(c2[i]["kid"]) for i in t73)
dup = sum(1 for k, v in allk.items() if v > 1)
oldk = {tuple(tubes[i]["kid"]) for i in t50}
new_eq_old = sum(1 for i in t73 if tuple(c2[i]["kid"]) in oldk)
# a new kid equal to the mkid of another class (the mirror of another bottom) other than its census mirror
mk_owner = defaultdict(set)
for i in t50:
    mk_owner[tuple(tubes[i]["mkid"])].add(i)
for i in t73:
    mk_owner[tuple(c2[i]["mkid"])].add(i)
crossm = 0
for i in t73:
    for j in mk_owner.get(tuple(c2[i]["kid"]), ()):
        if j != mirror[i]:
            crossm += 1
vids = {tuple(r["vid"]) for i, r in cores.items() if r["ex"]}
new_eq_vid = sum(1 for i in t73 if tuple(c2[i]["kid"]) in vids)
print(f"\ndistinct bottoms: {len(allk)} kids for {len(t50) + len(t73)} certificates; kids shared: {dup}; new kid equal to an old kid: {new_eq_old}; "
      f"new kid equal to the mkid of a class other than its census mirror: {crossm}; new kid equal to a finite core's vid: {new_eq_vid}")

# ---- §6.3 and §7
dis = [i for i in cls if kind(i) == "disconnected"]
acb = [i for i in cls if kind(i) == "acyclic bottom"]
openc = [i for i in cls if i not in t73 and kind(i) not in ("disconnected", "acyclic bottom")]
print(f"\n§6.3: open classes {len(openc)}: {dict(Counter(kind(i) for i in openc))}")
print(f"   pairwise distinct (finite cores + tube certificates): {len(fin) + len(t50) + len(t73)}; covered: {len(fin) + len(t50) + len(t73) + len(dis) + len(acb)}")
print(f"   newly certified self-mirror classes: {sum(1 for i in t73 if mirror[i] == i)}; newly certified pairs (both classes): {sum(1 for i, j in pairs if i in t73 and j in t73)}")
