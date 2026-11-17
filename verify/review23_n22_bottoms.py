"""Review 3 of note 22, item 2 (bottoms): an exhaustive cut of V'(x), with my own code, for every one of the
2,206 second-pass certificates (n4_tube_certify2.jsonl.gz), against the claimed bottom of N.

For each certified class with start x:
  a. x lies in no far region: by the direct test (two light pairs, or abundant and not a fork); otherwise via a
     quiver x' of V'(x) that passes it and whose V' reaches x again (then x lies in N = V'(x'));
  b. V'(x) cut at level LC = FACTOR * b (allowed steps, up to relabelling, cap CAP): least level, the quivers
     there, their least canonical form and least mirrored form, against bK, kid, nbot, mkid;
  c. separation from the finite cores (note 14 §4): the cut has more than 77 quivers or reaches above level 1,312.
Usage: python -I review23_n22_bottoms.py FACTOR CAP PROCS > review23_n22_bottoms.log"""
import gzip
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L

FACTOR = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 400000
PROCS = int(sys.argv[3]) if len(sys.argv) > 3 else 4


def job(r):
    t0 = time.time()
    x = tuple(r["x"])
    out = {"i": r["i"], "b": r["b"]}
    LC = FACTOR * r["b"]
    cutx, ok, _ = L.cut(x, LC, cap=CAP)
    out["n"] = len(cutx)
    out["complete"] = ok
    if L.direct_no_far_region(x):
        out["x_in_N"] = "direct"
    else:
        xs = [y for y in cutx if L.direct_no_far_region(y)]
        if xs:
            xp = min(xs, key=lambda y: (cutx[y], y))
            back, _, _ = L.cut(xp, LC, cap=CAP)
            out["x_in_N"] = "via x'" if L.canon(x) in back else "x' found but x not reached back"
        else:
            out["x_in_N"] = "unknown"
    lo = min(cutx.values())
    bot = sorted(y for y, l in cutx.items() if l == lo)
    out["lo"] = lo
    out["nbot"] = len(bot)
    out["kid"] = list(bot[0])
    out["mkid"] = list(min(L.canon(L.neg(y)) for y in bot))
    out["top"] = max(cutx.values())
    out["t"] = round(time.time() - t0, 2)
    return out


def main():
    with gzip.open("n4_tube_certify2.jsonl.gz", "rt") as f:
        recs = [json.loads(l) for l in f]
    cert = {r["i"]: r for r in recs if r["status"] == "certified"}
    jobs = sorted(cert.values(), key=lambda r: -r["b"])
    t0 = time.time()
    tab = Counter()
    bad = []
    with Pool(PROCS) as pool:
        for o in pool.imap_unordered(job, jobs, chunksize=2):
            r = cert[o["i"]]
            tab["classes"] += 1
            tab["cut complete"] += o["complete"]
            tab["x in N: " + o["x_in_N"]] += 1
            same_lo = o["lo"] == r["bK"]
            tab["least level of the cut = bK"] += same_lo
            tab["least level of the cut < bK (CONTRADICTION)"] += o["lo"] < r["bK"]
            tab["least level of the cut > bK (bottom not reached)"] += o["lo"] > r["bK"]
            if same_lo:
                tab["kid equal"] += o["kid"] == r["kid"]
                tab["mkid equal"] += o["mkid"] == r["mkid"]
                tab["nbot equal"] += o["nbot"] == r["nbot"]
                tab["nbot of the cut < claimed"] += o["nbot"] < r["nbot"]
                tab["nbot of the cut > claimed (CONTRADICTION)"] += o["nbot"] > r["nbot"]
            if not (same_lo and o["kid"] == r["kid"] and o["mkid"] == r["mkid"] and o["nbot"] == r["nbot"]):
                bad.append((o, {k: r[k] for k in ("bK", "kid", "mkid", "nbot", "x")}))
            tab["separated from finite cores (> 77 quivers or level > 1312)"] += o["n"] > 77 or o["top"] > 1312
            tab["quivers in the cuts"] += o["n"]
    print(f"cut of V'(x) at level {FACTOR} b, cap {CAP}, for the {len(cert)} certify2 certificates ({time.time() - t0:.0f}s)")
    for k, v in tab.items():
        print(f"   {k}: {v}")
    for o, r in bad[:40]:
        print("   differs:", o, r)


if __name__ == "__main__":
    main()
