"""Review 2 of note 14 (n14b): for the 322 re-run tube certificates, the claimed bottom of the core against the
census bottom components, with my own plateau search (review19_n14b_cores.plateau_key): when the bottom
level is the census bottom, kid lies in a bottom component of its class and mkid in one of the mirror class;
when it is higher, the census bottom quiver fails my direct test.  Run from experiments/ with python -I."""
import gzip, json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L
from review19_n14b_cores import plateau_key
plats = [json.loads(l) for l in gzip.open("n4_opposite_plateaus.jsonl.gz", "rt") if l.strip()]
owner = {}
for p in plats:
    for x in p["comps"]:
        owner.setdefault(tuple(x["k"]), p["i"])
mirror = [owner.get(tuple(p["comps"][0]["mk"])) for p in plats]
st = Counter()
for l in gzip.open(os.path.expanduser("~/.cache/qmb-review19/n14b_certs.jsonl.gz"), "rt"):
    c = json.loads(l)
    i, b, rec = c["i"], c["b"], c["rec"]
    kid, mkid = tuple(rec["kid"]), tuple(rec["mkid"])
    if L.level(kid) == b:
        st["bottom at the census bottom"] += 1
        st["kid in a bottom component of its class"] += owner.get(plateau_key(kid)) == i
        st["mkid in a bottom component of the mirror class"] += owner.get(plateau_key(mkid)) == mirror[i]
    else:
        st["bottom above the census bottom"] += 1
        st["... census bottom quiver fails my direct test"] += not L.no_far_region(tuple(c["q"]))
    st["kid == mkid iff census self-mirror"] += (kid == mkid) == (mirror[i] == i)
print(dict(st))
