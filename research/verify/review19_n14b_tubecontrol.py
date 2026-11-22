"""Review 2 of note 14 (n14b): positive control for review19_n14b_tubecheck.py.  The same checks on
certificates with ONE family broken (tau + 1; one entry of Y(2) changed by +-1; the family deleted).  A
useful checker must flag (nearly) all of them.  Only certificates with at least two families are used.
Run from experiments/ with python -I."""
import gzip, json, os, random, sys
from collections import Counter
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_tubecheck as TC

def run(a):
    c, kind, seed = a
    rng = random.Random(seed)
    c = json.loads(json.dumps(c))
    k = rng.randrange(len(c["fams"]))
    if kind == "tau+1":
        c["fams"][k][0] += 1
    elif kind == "Y2":
        a_ = rng.randrange(6)
        c["fams"][k][1][2][a_] += rng.choice((-1, 1))
    else:
        del c["fams"][k]
    out, st, bad = TC.check(c)
    kinds = sorted({b.split(":")[0] for b in bad})
    return kind, bool(bad), kinds

cs = [json.loads(l) for l in gzip.open(TC.CERTS, "rt") if l.strip()]
rng = random.Random(4)
cs = [c for c in cs if len(c.get("fams", [])) >= 2]
cs = rng.sample(cs, 40)
jobs = [(c, kind, rng.randrange(10 ** 9)) for c in cs for kind in ("tau+1", "Y2", "delete")]
st = Counter()
with Pool(6) as pool:
    for kind, flagged, kinds in pool.imap_unordered(run, jobs):
        st[(kind, "flagged" if flagged else "NOT flagged")] += 1
        for k in kinds:
            st[(kind, "by check " + k)] += 1
for k in sorted(st):
    print("  ", k, st[k])

# ---- why were some broken certificates not flagged?  (same jobs, same seeds)
def why(a):
    c, kind, seed = a
    rng = random.Random(seed)
    k = rng.randrange(len(c["fams"]))
    tau, Y = c["fams"][k]
    const = Y[0] == Y[1] == Y[2]
    out, st, bad = run(a)[1], None, None
    if out:
        return None
    # is the family covered by the other families / E?  (members n = 0..12 by canonical form)
    import review19_n14b_lib as L
    cert = TC.Cert({"E": c["E"], "fams": [f for j, f in enumerate(c["fams"]) if j != k]})
    ts = L.fam_terms(tuple(tuple(y) for y in Y), tau, 12)
    covered = all(cert.member(L.canon(y))[0] is not None for y in ts)
    return kind, c["i"], k, "constant family" if const else "non-constant", "members covered by E and the other families" if covered else "not covered"

with Pool(6) as pool:
    for r in pool.imap_unordered(why, jobs):
        if r:
            print("   not flagged:", r)
