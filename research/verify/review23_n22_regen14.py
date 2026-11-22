"""Review 3 of note 22, item 1, step 1: regenerate a sample of note 14's tube certificates as plain data.

Note 14 stored only a summary per class (n4_opposite_tubes.jsonl.gz: x, L, nE, nodes, taus, bK, kid, mkid, nbot);
the families themselves are not stored anywhere (note 19 §9 says the same), and ~/.cache/n4_tube_shapes.jsonl.gz
holds only note 22's per-family verdicts.  So the families are regenerated here by running note 14's engine
as a black box, through its own command line (`n4_opposite_tubes.py one QUIVER`, which prints the record and
every family triple), in a subprocess.  Nothing of the engine is imported, copied or adapted; its printed output
is parsed as data and checked by review23_n22_shapes.py with my own code.

Sample: R random certified classes (seed 7303) + the 150 with the largest tau + the 150 with the most families
+ the 150 with the largest L + note 14's extremes.  The census bottom quiver q (n4_opposite_cores) is passed,
so that b = level(q) is the census bottom, as in note 14's run.
Output: ~/.cache/qmb-review23/n14_certs.jsonl.gz.
Usage: python -I review23_n22_regen14.py [R] [PROCS]"""
import ast
import gzip
import json
import os
import random
import subprocess
import sys
import time
from multiprocessing import Pool

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results
PY = sys.executable
OUT = os.path.expanduser("~/.cache/qmb-review23/n14_certs.jsonl.gz")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
EXTREMES = [1063, 2880, 19829, 30671, 104171, 663398]


def job(a):
    i, q, why = a
    t0 = time.time()
    p = subprocess.run([PY, "-I", "n4_opposite_tubes.py", "one", json.dumps(q)], cwd=HERE,
                       capture_output=True, text=True, timeout=600)
    rec, fams = None, []
    for line in p.stdout.splitlines():
        s = line.strip()
        if s.startswith("{"):
            rec = ast.literal_eval(s)
        elif s.startswith("tau "):
            _, tau, rest = s.split(" ", 2)
            Y = ast.literal_eval(rest)
            fams.append([int(tau), [list(y) for y in Y]])
    return {"i": i, "q": q, "why": why, "rec": rec, "fams": fams, "err": p.stderr[-500:], "t": round(time.time() - t0, 2)}


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    os.chdir(HERE)
    with gzip.open("n4_opposite_tubes.jsonl.gz", "rt") as f:
        recs = [json.loads(l) for l in f]
    cert = {r["i"]: r for r in recs if r["status"] == "certified"}
    with gzip.open("n4_opposite_cores.jsonl.gz", "rt") as f:
        q = {}
        for l in f:
            r = json.loads(l)
            if r["i"] in cert:
                q[r["i"]] = r["q"]
    why = {}
    for i in random.Random(7303).sample(sorted(cert), R):
        why[i] = "random"
    for key, name in ((lambda r: max(r["taus"]), "largest tau"), (lambda r: r["nodes"], "most families"),
                      (lambda r: r["L"], "largest L")):
        for r in sorted(cert.values(), key=lambda r: -key(r))[:150]:
            why.setdefault(r["i"], name)
    for i in EXTREMES:
        if i in cert:
            why.setdefault(i, "extreme")
    jobs = [(i, q[i], why[i]) for i in sorted(why)]
    print(f"sample: {len(jobs)} certified classes", flush=True)
    t0 = time.time()
    n = 0
    with Pool(procs) as pool, gzip.open(OUT, "wt") as out:
        for res in pool.imap_unordered(job, jobs, chunksize=4):
            res["stored"] = cert[res["i"]]
            out.write(json.dumps(res, separators=(",", ":")) + "\n")
            n += 1
            if n % 1000 == 0:
                print(f"  {n} ({time.time() - t0:.0f}s)", flush=True)
    print(f"wrote {n} certificates to {OUT} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
