"""Review 3 of note 22: my own engine (review23_n22_engine) with E cut at a level LAM = 10 * L, L the level bound
stored in the second-pass record, for the classes where the default levels (64b, 512b, 4096b) failed.
Usage: python -I review23_n22_engine_highlam.py < ids > review23_n22_engine_highlam.log"""
import gzip, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_engine as G
G.DERIV, G.FAMCAP, G.ECAP = 8, 1500, 60000
ids = [int(s) for s in sys.stdin.read().split()]
with gzip.open("n4_tube_certify2.jsonl.gz", "rt") as f:
    cert = {r["i"]: r for r in (json.loads(l) for l in f) if r["status"] == "certified"}
for i in ids:
    r = cert[i]
    lam = 10 * r["L"]
    t0 = time.time()
    try:
        o = G.certify(tuple(r["x"]), r["b"], lam)
        o["status"] = "certified"
    except G.Fail as e:
        o = {"status": "failed: " + str(e)}
    o.update({"i": i, "lam_digits": len(str(lam))})
    same = o.get("lo") == r["bK"] and o.get("kid") == r["kid"] and o.get("mkid") == r["mkid"] and o.get("nbot") == r["nbot"]
    print(json.dumps(o, separators=(",", ":")), "| bottom equal to the stored one:", same, f"({time.time() - t0:.0f}s)", flush=True)
