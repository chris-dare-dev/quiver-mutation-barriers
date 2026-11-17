"""Review 2 of note 14 (n14b): the single-quiver cores of section 3 (remark) and section 4, recounted with
my own code from my full-census run (review19_n14b_full.py output).  Run from experiments/ with python -I."""
import glob, gzip, json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L
st = Counter()
nv_other = Counter()
for fn in sorted(glob.glob(os.path.expanduser("~/.cache/qmb-review19/n14b_full_*.jsonl.gz"))):
    for l in gzip.open(fn, "rt"):
        r = json.loads(l)
        if not r["c"] or r.get("n") != 1:
            continue
        q = tuple(r["vid"])
        st["single-quiver cores"] += 1
        eq = L.exits(q)
        su = 0
        forks = 0
        selfloop = 0
        for m in range(4):
            y = L.mut(q, m)
            if m in L.exits(y) and m not in eq:
                su += 1
                forks += m in L.fork_points(L.mat(y), [0, 1, 2, 3])
            elif L.canon(y) == q:
                selfloop += 1
        st[f"strict up-exit mutations {su}"] += 1
        if su == 4:
            st["... all four forks"] += forks == 4
            st["... isomorphic to its opposite"] += L.canon(L.neg(q)) == q
        else:
            st["... other mutations return the same quiver (all)"] += selfloop == 4 - su
            nv_other[r["nv"]] += 1
print(dict(st))
print("|V'| of the single-quiver cores with fewer than four exits:", dict(sorted(nv_other.items())))
