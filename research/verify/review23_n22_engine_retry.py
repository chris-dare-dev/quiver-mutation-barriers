"""Review 3 of note 22: rerun my own engine (review23_n22_engine) on the classes it failed on, with larger caps
(derived depth 8, 1,500 families, E cap 60,000, N = 8, time 1,200 s per attempt).
Usage: python -I review23_n22_engine_retry.py PROCS < ids > review23_n22_engine_retry.log"""
import gzip
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_engine as G

G.DERIV, G.FAMCAP, G.ECAP, G.N = 8, 1500, 60000, 8


def main():
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    ids = [int(s) for s in sys.stdin.read().split()]
    with gzip.open("n4_tube_certify2.jsonl.gz", "rt") as f:
        cert = {r["i"]: r for r in (json.loads(l) for l in f) if r["status"] == "certified"}
    t0 = time.time()
    tab = Counter()
    with Pool(procs) as pool:
        for o in pool.imap_unordered(G.job, [(cert[i], "retry") for i in ids]):
            r = cert[o["i"]]
            tab[o["status"]] += 1
            if o["status"] == "certified":
                same = (o["lo"] == r["bK"], o["kid"] == r["kid"], o["mkid"] == r["mkid"], o["nbot"] == r["nbot"])
                tab["certified: bottom equal"] += all(same)
                tab["certified: closure failures"] += o["closure_failures"] > 0
            print(json.dumps(o, separators=(",", ":")), flush=True)
    print(f"summary ({time.time() - t0:.0f}s): {dict(tab)}")


if __name__ == "__main__":
    main()
