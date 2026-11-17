"""
review19_n13_arith.py -- (1) own Burnside count of 4-vertex quivers per height 1..18; (2) own enumeration of the
disconnected quivers per height 1..18 with pass/fail inside their own height (own BFS) and their certificates;
(3) re-addition of note 13's tables from its logs (n4_conj55_N18.log, n4_conj55_N18_resolve.log,
n4_conj55_N18_summary.log) and from the stored resolve rows.
Usage: python -I review19_n13_arith.py
"""
import ast
import gzip
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results

# ------------------------------------------------------------------ (1) Burnside
def fixed(perm_index, h):
    """Labelled quivers with entries in [-h, h] fixed by the relabelling: product over cycles of the signed
    permutation of the 6 coordinates: (2h+1) for a cycle with sign product +1, 1 (only 0) for sign product -1."""
    m = L._RL[perm_index]
    seen = set()
    out = 1
    for p in range(6):
        if p in seen:
            continue
        sgn = 1
        q = p
        while q not in seen:
            seen.add(q)
            src, s = m[q]
            sgn *= s
            q = src
        out *= (2 * h + 1) if sgn == 1 else 1
    return out


def orbits_le(h):
    tot = sum(fixed(a, h) for a in range(24))
    assert tot % 24 == 0
    return tot // 24


# sanity: brute force for h <= 2
for h in (1, 2):
    bf = len({L.canon(t) for t in itertools.product(range(-h, h + 1), repeat=6)})
    assert bf == orbits_le(h), (h, bf, orbits_le(h))
burn = {h: orbits_le(h) - orbits_le(h - 1) for h in range(1, 19)}
print("(1) Burnside, quivers of height exactly h up to relabelling:", burn)
print("    total heights 1..18:", sum(burn.values()))

# ------------------------------------------------------------------ (2) disconnected quivers
N = 18
dis = set()
R = range(-N, N + 1)
for v in range(4):
    zero = [p for p, (i, j) in enumerate(L.PAIRS) if v in (i, j)]
    free = [p for p in range(6) if p not in zero]
    for vals in itertools.product(R, repeat=3):
        t = [0] * 6
        for p, x in zip(free, vals):
            t[p] = x
        dis.add(L.canon(tuple(t)))
for (a, b), (c, d) in [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]:
    pa, pb = L.PAIRS.index((a, b)), L.PAIRS.index((c, d))
    for x, y in itertools.product(R, repeat=2):
        t = [0] * 6
        t[pa], t[pb] = x, y
        dis.add(L.canon(tuple(t)))
dis.discard((0,) * 6)
assert all(not L.is_connected(t) for t in dis)
per = defaultdict(Counter)
for t in dis:
    h = L.ht(t)
    found, size, exh = L.bfs_within(t, h)
    if found is not None:
        per[h]["pass"] += 1
    else:
        assert exh
        per[h]["fail"] += 1
        per[h]["fail_with_cyclic_triangle"] += L.cyclic_triangle(t)
print("(2) disconnected quivers per height (pass / fail / fail with a cyclic triangle):")
for h in range(1, 19):
    print(f"    h={h}: {sum(per[h][k] for k in ('pass', 'fail'))} = {per[h]['pass']} + {per[h]['fail']}; "
          f"fail with cyclic triangle {per[h]['fail_with_cyclic_triangle']}")
print("    total disconnected, heights 1..18:", len(dis), "; failing:", sum(per[h]["fail"] for h in per),
      "; passing:", sum(per[h]["pass"] for h in per))

# ------------------------------------------------------------------ (3) note 13's tables, re-added
# run log table
run_rows = {}
for line in open(os.path.join(HERE, "n4_conj55_N18.log")):
    m = re.match(r"^(\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$", line.strip())
    if m:
        v = list(map(int, m.groups()))
        run_rows[v[0]] = dict(zip("h quivers connected pass fail cex tri vortex markov closed cor52 undet".split(), v))
assert sorted(run_rows) == list(range(1, 19))
summ = open(os.path.join(HERE, "n4_conj55_N18_summary.log")).read()
pc = ast.literal_eval(re.search(r"connected quivers reaching an acyclic quiver within h / failing: (\{.*\})", summ).group(1))
bad = []
for h, r in run_rows.items():
    if burn[h] != r["quivers"]:
        bad.append(("quivers vs Burnside", h, burn[h], r["quivers"]))
    if r["pass"] + r["fail"] != r["quivers"]:
        bad.append(("pass+fail", h))
    if r["tri"] + r["vortex"] + r["markov"] + r["closed"] + r["cor52"] + r["undet"] + r["cex"] != r["fail"]:
        bad.append(("cert sum", h))
    dconn = r["quivers"] - r["connected"]
    if dconn != per[h]["pass"] + per[h]["fail"]:
        bad.append(("disconnected count", h, dconn, per[h]["pass"] + per[h]["fail"]))
    if r["pass"] - pc[h][0] != per[h]["pass"] or r["fail"] - pc[h][1] != per[h]["fail"]:
        bad.append(("disconnected pass/fail", h, r["pass"] - pc[h][0], per[h]["pass"], r["fail"] - pc[h][1], per[h]["fail"]))
print("(3) run-log table vs own Burnside / disconnected counts; internal sums: problems:", bad)
tot = Counter()
for r in run_rows.values():
    for k in ("quivers", "connected", "pass", "fail", "tri", "vortex", "markov", "closed", "cor52", "undet", "cex"):
        tot[k] += r[k]
print("    run totals:", dict(tot))
# resolve rows
res = json.load(gzip.open(os.path.join(HERE, "n4_conj55_N18_resolve.json.gz"), "rt"))["rows"]
q_by = Counter()
q_by_h = defaultdict(Counter)
rows_by = Counter()
for r in res:
    c = r["cert"].replace("same class as ", "")
    rows_by[r["cert"]] += 1
    for h, n in r["fail_by_height"].items():
        q_by[c] += n
        q_by_h[int(h)][c] += n
print("    resolve rows by recorded cert:", dict(rows_by), "; total rows", len(res))
print("    resolve failing quivers by cert (cache rows merged):", dict(q_by), "; total", sum(q_by.values()))
undet_ok = all(sum(q_by_h[h].values()) == run_rows[h]["undet"] for h in range(1, 19))
print("    resolve quivers per height == run 'undet' column at every height:", undet_ok)
bycert = Counter()
for r in run_rows.values():
    for k in ("tri", "vortex", "markov", "closed", "cor52"):
        bycert[k] += r[k]
for k, v in q_by.items():
    bycert[k] += v
print("    failing quivers by first certificate (run + resolve):", dict(bycert), "; total", sum(bycert.values()))
# the two bounds of section 4
m1 = re.search(r"failing quivers with a triangle in their component of G_N: (\d+); closed components: (\d+)", summ)
tri_any, clo_any = int(m1.group(1)), int(m1.group(2))
m2 = re.search(r"\(tri, vortex or closed in G_N, or tri / vortex from resolve\): (\d+) = (\d+) \+ (\d+)", summ)
cl_all, cl_run, cl_res = map(int, m2.groups())
print(f"    'at least ... no triangle': {tot['fail']} - {tri_any} - {clo_any} - {q_by['tri']} = "
      f"{tot['fail'] - tri_any - clo_any - q_by['tri']}")
print(f"    classical from resolve recomputed = tri + vortex quivers = {q_by['tri'] + q_by['vortex']} (log: {cl_res}); "
      f"'at most ... Lemma 2.4 or Cor 5.2' = {tot['fail']} - {cl_run} - {q_by['tri'] + q_by['vortex']} = "
      f"{tot['fail'] - cl_run - q_by['tri'] - q_by['vortex']}")
print(f"    markov + cor52 first certificates = {bycert['markov'] + bycert['cor52']}")
# resolve stop counts
stops = Counter(r["cert"].replace("same class as ", "") for r in res)
print("    resolve stops (cache merged):", dict(stops), "; cache rows:", sum(v for k, v in rows_by.items() if k.startswith("same")))
big = max(res, key=lambda r: r.get("popped", 0))
kmax = max((r for r in res if r["cert"] == "cor52"), key=lambda r: r["K"])
print(f"    largest search: {big['quiver']} popped {big['popped']} K {big.get('K')}; largest K: {kmax['K']} at {kmax['quiver']} "
      f"popped {kmax['popped']}")
kh = {}
for r in res:
    if r["cert"] == "cor52":
        kh[r["height"]] = max(kh.get(r["height"], 0), r["K"])
print("    largest K per representative height == h^3+h^2+5:", {h: (k, k == h ** 3 + h ** 2 + 5) for h, k in sorted(kh.items())})
nonfail_K = sorted(Counter(r["K"] for r in res if r["cert"] == "cor52").items())[-3:]
print("    top K values:", nonfail_K)
