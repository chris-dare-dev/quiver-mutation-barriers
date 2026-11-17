"""
review19_n13_samples.py -- re-certify samples of note 13's stored outputs with the independent library.

  resolve  rows of n4_conj55_N18_resolve.json.gz with a representative of height 10..18, stratified by
           certificate.  For each row:
             (1) the representative fails: its component inside its own height (up to relabelling) is exhausted
                 without an acyclic quiver;
             (2) tri / vortex / markov rows: the recorded quiver carries the certificate (own code; markov = own
                 Lemma 2.4 test) and is reached from the representative with bottleneck <= the recorded one;
             (3) cor52 rows: X = K_quiver is reached from the representative within height K, own H(X) <= K, and
                 the LABELLED component of X inside height H(X) is exhausted with no acyclic quiver (Cor. 5.2
                 applied to X literally);
             (4) own bottleneck search from the representative: verdict, certificate, and (cor52) its K.
  run      the stored random failing / passing samples of n4_conj55_N18.json.gz at heights 10..18:
           failing: (1) and own search verdict; passing: a quiver inside its own height reached is acyclic.
  random   own uniform random labelled quivers of height exactly h (h = 11..18): pass/fail by own BFS inside
           height h; failing ones certified by own search; the orbit-weighted pass fraction is compared with
           note 13's table.
  family   own search on the representatives with the largest K per height and on the family
           (-h, 2, 0, -(h-1), -h, -h).
Usage: python -I review19_n13_samples.py MODE [--n N] [--seed S] [--workers W]
"""
import argparse
import gzip
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results


def fails_in_own_height(t, budget=3_000_000):
    found, size, exhausted = L.bfs_within(t, L.ht(t), labelled=False, budget=budget)
    return found is None and exhausted, size


def labelled_component_no_acyclic(X, H, budget=3_000_000):
    found, size, exhausted = L.bfs_within(X, H, labelled=True, budget=budget)
    return found is None and exhausted, size


def check_resolve_row(r):
    t = tuple(r["quiver"])
    out = {"quiver": r["quiver"], "height": r["height"], "cert": r["cert"]}
    ok_fail, size = fails_in_own_height(t)
    out["fails"] = ok_fail
    out["own_height_component"] = size
    cert = r["cert"]
    if cert in ("tri", "vortex", "markov"):
        x = tuple(r["at"])
        has = {"tri": L.cyclic_triangle, "vortex": L.is_vortex, "markov": L.lemma24_excluded}[cert](x)
        bn = L.bottleneck_to(t, x, r["bottleneck"])
        out["cert_holds"] = bool(has)
        out["reached"] = bn is not None and bn <= r["bottleneck"]
    elif cert == "cor52":
        X = tuple(r["K_quiver"])
        K = r["K"]
        H = L.H_of(X)
        bn = L.bottleneck_to(t, X, K)
        out["H_own"] = H
        out["H_le_K"] = H is not None and H <= K
        out["reached"] = bn is not None and bn <= K
        out["max_H_bn_eq_K"] = H is not None and bn is not None and max(H, bn) == K
        noac, lsize = labelled_component_no_acyclic(X, H) if H is not None else (False, 0)
        out["labelled_component_no_acyclic"] = noac
        out["labelled_component_size"] = lsize
        out["cert_holds"] = out["H_le_K"] and out["reached"] and noac
    else:
        out["cert_holds"] = None
        out["reached"] = None
    own = L.my_resolve(t, budget=500_000)
    out["own"] = [own[0], own[1], own[2]]
    if cert == "cor52":
        out["own_K_equal"] = own[1] == "cor52" and own[2] == r["K"]
    return out


def mode_resolve(a):
    res = json.load(gzip.open(os.path.join(HERE, "n4_conj55_N18_resolve.json.gz"), "rt"))["rows"]
    rng = random.Random(a.seed)
    by = defaultdict(list)
    for r in res:
        if 10 <= r["height"] <= 18:
            by[r["cert"]].append(r)
    print({k: len(v) for k, v in by.items()}, flush=True)
    want = {"tri": a.n, "vortex": a.n, "markov": 10 ** 9, "cor52": 2 * a.n,
            "same class as cor52": a.n // 2, "same class as vortex": a.n // 2}
    rows = []
    for k, v in by.items():
        rows += rng.sample(v, min(len(v), want.get(k, 0)))
    # the cor52 rows with the largest K at heights 10..18
    top = sorted(by["cor52"], key=lambda r: -r["K"])[:a.n // 4]
    seen = {tuple(r["quiver"]) for r in rows}
    rows += [r for r in top if tuple(r["quiver"]) not in seen]
    print(f"{len(rows)} rows sampled: {dict(Counter(r['cert'] for r in rows))}", flush=True)
    t0 = time.time()
    with Pool(a.workers) as pool:
        outs = pool.map(check_resolve_row, rows, chunksize=4)
    tally = defaultdict(Counter)
    for o in outs:
        c = o["cert"]
        tally[c]["rows"] += 1
        tally[c]["rep fails in own height"] += o["fails"]
        if o["cert_holds"] is not None:
            tally[c]["certificate re-verified"] += bool(o["cert_holds"])
            tally[c]["certified quiver reached within recorded height"] += bool(o["reached"])
        tally[c]["own search: cyclic"] += o["own"][0] == "cyclic"
        tally[c][f"own search cert {o['own'][1]}"] += 1
        if c == "cor52":
            tally[c]["own K == recorded K"] += bool(o["own_K_equal"])
            tally[c]["max(H_own(X), bottleneck(X)) == K"] += bool(o["max_H_bn_eq_K"])
    for c, t in tally.items():
        print(f"{c}: {dict(t)}")
    cor = [o for o in outs if o["cert"] == "cor52"]
    if cor:
        print(f"cor52: largest K re-verified {max(o['own'][2] for o in cor if o['own'][1] == 'cor52')}, "
              f"largest labelled component inside H(X) {max(o['labelled_component_size'] for o in cor)}")
    bad = [o for o in outs if not o["fails"] or o["own"][0] != "cyclic" or o["cert_holds"] is False
           or (o["cert"] == "cor52" and not o["own_K_equal"])]
    print(f"rows with any failed check: {len(bad)}")
    for o in bad[:20]:
        print("   ", o)
    print(f"({time.time() - t0:.0f}s)")


def check_fail(t):
    ok, size = fails_in_own_height(t)
    own = L.my_resolve(t, budget=500_000)
    return t, ok, size, own[:3]


def check_pass(t):
    found, size, _ = L.bfs_within(t, L.ht(t), labelled=False)
    return t, found is not None, size


def mode_run(a):
    res = json.load(gzip.open(os.path.join(HERE, "n4_conj55_N18.json.gz"), "rt"))
    rng = random.Random(a.seed)
    fails = defaultdict(list)
    for t in res["sample_fail"]:
        if 10 <= L.ht(t) <= 18:
            fails[L.ht(t)].append(tuple(t))
    passes = [tuple(t) for t in res["sample_pass"] if 10 <= L.ht(t) <= 18 and not L.is_acyclic(tuple(t))]
    fs = []
    for h in sorted(fails):
        fs += rng.sample(fails[h], min(len(fails[h]), a.n))
    print(f"failing sample: {len(fs)} of {sum(len(v) for v in fails.values())} stored at heights 10..18; "
          f"passing non-acyclic: {len(passes)}", flush=True)
    t0 = time.time()
    with Pool(a.workers) as pool:
        fo = pool.map(check_fail, fs, chunksize=4)
        po = pool.map(check_pass, passes, chunksize=4)
    tally = Counter()
    for t, ok, size, own in fo:
        tally["fails in own height"] += ok
        tally[f"own: {own[0]} {own[1]}"] += 1
    print(f"failing: {dict(tally)}; largest own-height component {max(s for _, _, s, _ in fo)}")
    print(f"passing non-acyclic: {sum(ok for _, ok, _ in po)} of {len(po)} reach an acyclic quiver inside their height")
    print(f"({time.time() - t0:.0f}s)")


def rand_quiver(rng, h):
    while True:
        t = tuple(rng.randint(-h, h) for _ in range(6))
        if L.ht(t) == h:
            return t


def stab_size(t):
    return sum(1 for a in range(24) if L.relabel(t, a) == t)


def check_random(t):
    found, size, exhausted = L.bfs_within(t, L.ht(t), labelled=False, budget=3_000_000)
    if found is not None:
        return t, "pass", None, size
    if not exhausted:
        return t, "undecided", None, size
    own = L.my_resolve(t, budget=500_000)
    return t, "fail", own[:3], size


TABLE = {11: (2595341, 1166783), 12: (4005273, 1776593), 13: (5971057, 2611703), 14: (8643013, 3740365),
         15: (12196421, 5229234), 16: (16833441, 7159350), 17: (22785033, 9612933), 18: (30312877, 12711219)}


def mode_random(a):
    rng = random.Random(a.seed)
    qs = []
    for h in range(11, 19):
        qs += [rand_quiver(rng, h) for _ in range(a.n)]
    t0 = time.time()
    with Pool(a.workers) as pool:
        outs = pool.map(check_random, qs, chunksize=4)
    per = defaultdict(Counter)
    w = defaultdict(lambda: [0.0, 0.0])
    for t, v, own, size in outs:
        h = L.ht(t)
        per[h][v] += 1
        if own is not None:
            per[h][f"own {own[0]} {own[1]}"] += 1
        # labelled uniform sampling -> orbit fraction: weight 1/|orbit| = |Stab|/24
        wt = stab_size(t) / 24
        w[h][0] += wt * (v == "pass")
        w[h][1] += wt
    import math
    for h in sorted(per):
        q, p = TABLE[h]
        est = w[h][0] / w[h][1]
        n = sum(per[h][k] for k in ("pass", "fail", "undecided"))
        se = math.sqrt(est * (1 - est) / n)
        print(f"h={h}: {dict(per[h])}; orbit-weighted pass fraction {est:.4f} +- {se:.4f} (1 s.e.); "
              f"note 13 table {p / q:.4f}; z = {(est - p / q) / se:+.2f}")
    print(f"({time.time() - t0:.0f}s)")


def fam(t):
    r = L.my_resolve(t, budget=500_000)
    return t, r[0], r[1], r[2], r[4]


def mode_family(a):
    res = json.load(gzip.open(os.path.join(HERE, "n4_conj55_N18_resolve.json.gz"), "rt"))["rows"]
    top = {}
    for r in res:
        if r["cert"] == "cor52" and (r["height"] not in top or r["K"] > top[r["height"]]["K"]):
            top[r["height"]] = r
    qs = [tuple(top[h]["quiver"]) for h in sorted(top)]
    qs += [(-h, 2, 0, -(h - 1), -h, -h) for h in range(2, 19)]
    big = max(res, key=lambda r: r.get("popped", 0))
    qs.append(tuple(big["quiver"]))
    with Pool(a.workers) as pool:
        outs = pool.map(fam, qs, chunksize=1)
    for (t, v, c, K, popped) in outs:
        h = L.ht(t)
        rec = next((top[h] for _ in [0] if h in top and tuple(top[h]["quiver"]) == t), None)
        extra = f"; recorded K {rec['K']}, popped {rec['popped']}" if rec else ""
        if t == tuple(big["quiver"]):
            extra += f"; largest recorded search: K {big.get('K')}, popped {big['popped']}"
        print(f"{t} h={h}: own {v} {c} K={K} popped={popped}; h^3+h^2+5={h ** 3 + h ** 2 + 5}{extra}")


def check_row_light(r):
    t = tuple(r["quiver"])
    ok, size = fails_in_own_height(t)
    own = L.my_resolve(t, budget=500_000)
    return (r["height"], r["cert"], r.get("K"), sum(r["fail_by_height"].values()), ok, own[0], own[1], own[2], own[4])


def mode_allrows(a):
    """Every row of the resolve output (or a slice): representative fails in own height, own search verdict, and
    for cor52 rows equality of K.  Also re-sums the failing quivers per certificate."""
    res = json.load(gzip.open(os.path.join(HERE, "n4_conj55_N18_resolve.json.gz"), "rt"))["rows"]
    rows = res[a.part::a.of]
    t0 = time.time()
    with Pool(a.workers) as pool:
        outs = pool.map(check_row_light, rows, chunksize=64)
    tally = Counter()
    quivers = Counter()
    bad = []
    for (h, cert, K, nf, ok, v, c, k, popped) in outs:
        tally[(cert, "own " + str(c))] += 1
        quivers[cert] += nf
        if not ok or v != "cyclic" or (cert == "cor52" and (c != "cor52" or k != K)):
            bad.append((h, cert, K, ok, v, c, k))
    print(f"slice {a.part}/{a.of}: {len(rows)} rows; failing quivers held: {sum(quivers.values())} {dict(quivers)}")
    print(f"  (recorded cert, own cert): {dict(tally)}")
    print(f"  rows failing a check: {len(bad)} {bad[:10]}")
    print(f"  ({time.time() - t0:.0f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["resolve", "run", "random", "family", "allrows"])
    ap.add_argument("--part", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--n", type=int, default=80)
    ap.add_argument("--seed", type=int, default=4902)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    {"resolve": mode_resolve, "run": mode_run, "random": mode_random, "family": mode_family,
     "allrows": mode_allrows}[a.mode](a)


if __name__ == "__main__":
    main()
