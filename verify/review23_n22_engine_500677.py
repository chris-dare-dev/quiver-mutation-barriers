"""Review 3 of note 22: class 500677, the one sampled class my engine did not certify at the default levels:
retries at further levels LAM with larger caps.
Usage: python -I review23_n22_engine_500677.py > review23_n22_engine_500677.log"""
import gzip, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_engine as G
G.DERIV, G.FAMCAP, G.ECAP, G.WALK = 10, 3000, 150000, 12
with gzip.open("n4_tube_certify2.jsonl.gz", "rt") as f:
    r = next(r for r in (json.loads(l) for l in f) if r["i"] == 500677)
print("stored:", r, flush=True)
for lam in (2000, 8000, 30000, 100000, 300000, 10 ** 6):
    t0 = time.time()
    try:
        o = G.certify(tuple(r["x"]), r["b"], lam)
        o["status"] = "certified"
    except G.Fail as e:
        o = {"status": "failed: " + str(e)}
    same = o.get("lo") == r["bK"] and o.get("kid") == r["kid"] and o.get("mkid") == r["mkid"] and o.get("nbot") == r["nbot"]
    print("LAM", lam, json.dumps(o, separators=(",", ":"))[:700], "| bottom equal:", same, f"({time.time() - t0:.0f}s)", flush=True)
    if o["status"] == "certified":
        break
