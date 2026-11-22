"""Review 2 of note 14 (n14b): the core search of section 4 for EVERY census class, with independent code
(review19_n14b_lib; nothing from n4_opposite*.py), same caps as n4_opposite_run.py cores (800 quivers,
stop at the first quiver above level 10^6), but breadth-first.  For a class whose search stops, the
separation argument of section 4 is redone with my own searches:
  in      the bottom quiver passes the direct test (the stopped search then has > 77 quivers or level > 1312);
  hc      a quiver of V'(q) that passes the direct test has level > 1312 (BFS, up to 3000 quivers,
          quivers above 10^6 not expanded);
  closure V'(y) of the lowest quiver y found that passes the direct test has > 77 quivers or level > 1312;
  none    not separated by these searches.
Also the keys (least canonical quiver) of the plateaus of q and of -q at the bottom level.
Usage: python -I review19_n14b_full.py CHUNK NCHUNKS  -> ~/.cache/qmb-review19/n14b_full_CHUNK.jsonl.gz"""
import gzip
import json
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L
from review19_n14b_cores import census, plateau_key

MAXN, MAXTOP = 77, 1312      # largest finite core and highest core level (checked against my own run later)


def job(a):
    i, q = a
    lev, adj, complete, _ = L.vprime(q, cap=800, level_cap=10 ** 6)
    out = {"i": i, "c": complete, "nv": len(lev), "pk": list(plateau_key(q)), "mpk": list(plateau_key(L.neg(q)))}
    if complete:
        sinks = L.sink_sccs(adj)
        out["ns"] = len(sinks)
        if len(sinks) == 1:
            K = sinks[0]
            out.update({"n": len(K), "vid": list(min(K)), "mvid": list(min(L.canon(L.neg(x)) for x in K)),
                        "top": max(lev[x] for x in K), "acyc": sum(1 for x in K if L.is_acyclic_q(x))})
        return out
    if L.no_far_region(q):
        out["sep"] = "in"
        out["why"] = "cap" if len(lev) >= 800 else "level"
        return out
    ys = [y for y in lev if L.no_far_region(y)]
    hi = [y for y in ys if lev[y] > MAXTOP]
    if not hi:
        lev2, adj2, comp2, above2 = L.vprime(q, cap=3000, level_cap=10 ** 6, skip_above=True)
        ys2 = [y for y in lev2 if L.no_far_region(y)] + [y for y in above2 if L.no_far_region(y)]
        hi = [y for y in ys2 if L.level(y) > MAXTOP]
        ys = ys2 or ys
    if hi:
        out["sep"] = "hc"
        out["hc"] = min(L.level(y) for y in hi)
        return out
    if not ys:
        out["sep"] = "none"
        return out
    y = min(ys, key=lambda y: (L.level(y), y))
    lev3, adj3, comp3, _ = L.vprime(y, cap=MAXN + 1, level_cap=MAXTOP)
    out["sep"] = "closure" if not comp3 else "none"
    out["y"] = list(y)
    return out


def main():
    chunk, nch = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    qs = census()
    jobs = [(i, qs[i]) for i in range(chunk, len(qs), nch)]
    path = os.path.expanduser(f"~/.cache/qmb-review19/n14b_full_{chunk}.jsonl.gz")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = 0
    with Pool(6) as pool, gzip.open(path, "wt") as f:
        for out in pool.imap_unordered(job, jobs, chunksize=200):
            f.write(json.dumps(out, separators=(",", ":")) + "\n")
            n += 1
    print(f"chunk {chunk}/{nch}: {n} classes written to {path} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
