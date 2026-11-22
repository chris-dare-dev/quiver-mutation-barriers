"""Review 2 of note 14 (n14b): is the 'broken certificate' test of n4_opposite_tubes.py validate informative?
It closes ONE family of a certificate (wrong tau or one entry of Y(2) changed), rebuilds E from x with only
that closure as R, and calls the certificate rejected if E has a frontier or a downward quiver is missing.
Control: the same procedure with the family left UNCHANGED.  If the control is also 'rejected', the test
cannot tell a broken certificate from a correct one.  Also: how far no_exit_closure(x, cap=4000,
level_cap=10**12) (the brute-force check of validate) gets before it stops.
Imports the code under review on purpose.  Run from experiments/ with python -I."""
import gzip
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import n4_opposite as O
import n4_opposite_tubes as T

CERTS = os.path.expanduser("~/.cache/qmb-review19/n14b_certs.jsonl.gz")
rng = random.Random(77)
with gzip.open(CERTS, "rt") as f:
    cs = [json.loads(l) for l in f if l.strip()]
rng.shuffle(cs)
st = Counter()
bf = []
for c in cs[:120]:
    x = tuple(c["x"])
    fams = [(tau, tuple(tuple(y) for y in Y)) for tau, Y in c["fams"]]
    tau, Y = rng.choice(sorted(fams))
    for kind in ("unchanged", "tau+1", "Y2 entry +-1"):
        if kind == "unchanged":
            t2, Y2 = tau, Y
        elif kind == "tau+1":
            t2, Y2 = tau + 1, Y
        else:
            a = rng.randrange(6)
            y2 = list(Y[2]); y2[a] += rng.choice((-1, 1))
            t2, Y2 = tau, (Y[0], Y[1], tuple(y2))
        rejected = False
        why = ""
        try:
            new, D2 = T.close(Y2, t2, {})
            mem2 = T.Members()
            mem2.add(new)
            E3, fr3 = T.bfs_E([x], c["rec"]["L"], mem2, {})
            if fr3:
                rejected, why = True, "frontier"
            elif any(O.canon(d) not in E3 and O.canon(d) not in mem2 for d in D2):
                rejected, why = True, "downward"
        except T.Abort as e:
            rejected, why = True, "abort"
        st[(kind, rejected, why)] += 1
    if len(bf) < 60:
        lev, adj, ex = O.no_exit_closure(x, cap=4000, level_cap=10 ** 12)
        bf.append(len(lev))
for k in sorted(st):
    print(f"   {k}: {st[k]}")
print(f"no_exit_closure(x, cap=4000, level_cap=10^12) on {len(bf)} certificates: quivers before it stops: "
      f"min {min(bf)}, median {sorted(bf)[len(bf) // 2]}, max {max(bf)}; reached the 4000 cap: {sum(1 for v in bf if v >= 4000)}")
