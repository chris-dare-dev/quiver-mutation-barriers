"""Review 2 of note 14 (n14b), step 1 of the tube attack: choose a stratified sample of certified tube
classes and re-run n4_opposite_tubes.certify on them, saving the certificates (E and the families) as
plain data to ~/.cache/qmb-review19/n14b_certs.jsonl.gz.  This is the only script of the attack that
imports the code under review; the checks (review19_n14b_tubecheck.py) use only review19_n14b_lib.
Run from experiments/ with python -I."""
import gzip
import json
import os
import random
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review

OUT = os.path.expanduser("~/.cache/qmb-review19/n14b_certs.jsonl.gz")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
EXTREMES = [1063, 2880, 19829, 30671, 104171, 663398]


def job(a):
    import n4_opposite_tubes as T
    i, b, q = a
    t0 = time.time()
    rec, obj = T.certify(i, b, q, full=True)
    out = {"i": i, "b": b, "q": q, "rec": rec, "t": round(time.time() - t0, 2)}
    if obj is not None:
        x, E, nodes, members, D = obj
        out["x"] = list(x)
        out["E"] = [list(e) for e in E]
        out["fams"] = [[key[0], [list(y) for y in Y]] for key, Y in nodes.items()]
        out["D"] = [list(d) for d in D]
    return out


def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 2026)
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 18
    with gzip.open("n4_opposite_tubes.jsonl.gz", "rt") as f:
        recs = [json.loads(l) for l in f if l.strip()]
    with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
        q = {}
        for l in f:
            r = json.loads(l)
            if not r["ex"]:
                q[r["i"]] = r["q"]
    cert = [r for r in recs if r["status"] == "certified"]
    strata = defaultdict(list)
    for r in cert:
        kind = "tau2" if 2 in r["taus"] else "tau>2"
        above = r["bK"] != r["b"]
        strata[(r["b"], kind, above)].append(r)
    chosen = {}
    for b in range(2, 10):
        for kind in ("tau2", "tau>2"):
            pool = strata[(b, kind, False)]
            for r in rng.sample(pool, min(per, len(pool))):
                chosen[r["i"]] = r
            pool = strata[(b, kind, True)]
            for r in rng.sample(pool, min(2, len(pool))):
                chosen[r["i"]] = r
    for i in EXTREMES:
        chosen[i] = next(r for r in cert if r["i"] == i)
    # a few with the most families
    for r in sorted(cert, key=lambda r: -r["nodes"])[:6]:
        chosen[r["i"]] = r
    jobs = [(i, chosen[i]["b"], q[i]) for i in sorted(chosen)]
    print(f"sample: {len(jobs)} certified classes", flush=True)
    t0 = time.time()
    n = 0
    with Pool(6) as pool, gzip.open(OUT, "wt") as out:
        for res in pool.imap_unordered(job, jobs):
            res["stored"] = chosen[res["i"]]
            out.write(json.dumps(res, separators=(",", ":")) + "\n")
            n += 1
    print(f"wrote {n} certificates to {OUT} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
