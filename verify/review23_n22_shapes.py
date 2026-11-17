"""Review 3 of note 22, item 1: the tube shapes of note 14's certificates, with my own code.

Reads the regenerated certificates (~/.cache/qmb-review23/n14_certs.jsonl.gz, review23_n22_regen14.py) as data.
For every family (tau, Y(0), Y(1), Y(2)) the members Y(n), n <= NM, are rebuilt from the recurrence
e(n+3) = (tau+1) e(n+2) - (tau+1) e(n+1) + e(n), and:
  - the non-constant entries and the vertices common to them (the growing vertex g, if unique);
  - the triangle T opposite g: constant along the family?  its type (with orientation) and Markov constant C;
  - tau against C: tau = t_k (t_0 = 2, t_1 = C - 2, t_{k+1} = t_1 t_k - t_{k-1}), j = k; or, when C = a^2,
    tau = s_k (s_0 = 2, s_1 = a, s_{k+1} = a s_k - s_{k-1}), j = k/2;
  - (D1)-(D3) of Lemma 22.1 at g for n = 0..NM, and whether the step at g is a strict up-exit (my exit test)
    for n = 0..NM; every entry constant or of fixed sign with non-decreasing absolute value for n <= NM;
  - links: the step at m from Y(n), n = 3, 4, 5, lands on members G(n + d) of one family G (canonical forms);
    tubes = strongly connected sets of families under these links; walk = the vertices used inside the tube.
Usage: python -I review23_n22_shapes.py > review23_n22_shapes.log"""
import gzip
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L

IN = os.path.expanduser("~/.cache/qmb-review23/n14_certs.jsonl.gz")
NM = 12


def members(tau, Y, nm=NM):
    out = [tuple(Y[0]), tuple(Y[1]), tuple(Y[2])]
    while len(out) <= nm:
        a, b, c = out[-3], out[-2], out[-1]
        out.append(tuple((tau + 1) * (z - y) + x for x, y, z in zip(a, b, c)))
    return out


def group(tt):
    if tt.startswith("(0,1,a)") or tt.startswith("(1,a,a)"):
        return "(0,1,a)/(1,a,a)"
    if tt.startswith("(1,1,a)") or tt.startswith("(1,a,a+1)"):
        return "(1,1,a)/(1,a,a+1)"
    if tt.startswith("(2,m,m)"):
        return "(2,m,m) oriented"
    return tt


def tau_j(C, tau, kmax=14):
    t1 = C - 2
    if t1 == 2:
        return "tau = 2 (C = 4)" if tau == 2 else "C = 4 but tau != 2"
    prev, cur = 2, t1
    for k in range(1, kmax + 1):
        if cur == tau:
            return "j = %d" % k
        prev, cur = cur, t1 * cur - prev
    a = math.isqrt(C)
    if a * a == C:
        prev, cur = 2, a
        for k in range(1, 2 * kmax + 1):
            if cur == tau:
                return "j = %d/2" % k if k % 2 else "j = %d" % (k // 2)
            prev, cur = cur, a * cur - prev
    return "NOT A CHEBYSHEV VALUE"


def dominant(t, g):
    v = {i: L.e(t, i, g) for i in range(4) if i != g}
    if not (any(x > 0 for x in v.values()) and any(x < 0 for x in v.values())):
        return False
    if any(abs(x) < 2 for x in v.values()):
        return False
    return all(abs(L.e(t, i, j)) < max(abs(v[i]), abs(v[j])) for i, j in itertools.combinations(sorted(v), 2))


def tarjan(adj):
    index, low, on, st, comps, cnt = {}, {}, set(), [], [], [0]

    def strong(v0):
        stack = [(v0, iter(adj[v0]))]
        index[v0] = low[v0] = cnt[0]
        cnt[0] += 1
        st.append(v0)
        on.add(v0)
        while stack:
            v, it = stack[-1]
            w = next(it, None)
            if w is None:
                stack.pop()
                if stack:
                    low[stack[-1][0]] = min(low[stack[-1][0]], low[v])
                if low[v] == index[v]:
                    comp = []
                    while True:
                        x = st.pop()
                        on.discard(x)
                        comp.append(x)
                        if x == v:
                            break
                    comps.append(comp)
            elif w not in index:
                index[w] = low[w] = cnt[0]
                cnt[0] += 1
                st.append(w)
                on.add(w)
                stack.append((w, iter(adj[w])))
            elif w in on:
                low[v] = min(low[v], index[w])

    for v in adj:
        if v not in index:
            strong(v)
    return comps


def main():
    S = Counter()
    fam_type = Counter()
    fam_type_rand = Counter()
    cls_type = Counter()
    cls_type_rand = Counter()
    Cvals = defaultdict(set)
    jdist = defaultdict(Counter)
    jdist_rand = defaultdict(Counter)
    dom = Counter()
    tubes = Counter()
    tubes_rand = Counter()
    cls_tubekinds = Counter()
    cls_tubekinds_rand = Counter()
    ntubes = ntubes_rand = 0
    trivial = Counter()
    nrand = 0
    why = Counter()
    examples = []
    with gzip.open(IN, "rt") as f:
        for line in f:
            c = json.loads(line)
            st = c["stored"]
            rec = c["rec"]
            why[c["why"]] += 1
            S["classes"] += 1
            if rec is None or rec.get("status") != "certified":
                S["not certified on the rerun"] += 1
                continue
            S["same kid as stored"] += rec.get("kid") == st["kid"]
            S["same number of families as stored"] += rec.get("nodes") == st["nodes"] == len(c["fams"])
            rnd = c["why"] == "random"
            nrand += rnd
            fams = []
            types_here = set()
            for tau, Y in c["fams"]:
                S["families"] += 1
                S["families with tau >= 2"] += tau >= 2
                M = members(tau, Y)
                var = [a for a in range(6) if not (Y[0][a] == Y[1][a] == Y[2][a])]
                common = set(range(4))
                for a in var:
                    common &= set(L.PAIRS[a])
                if len(common) != 1:
                    S["families without a single growing vertex"] += 1
                    if len(examples) < 5:
                        examples.append(("no single g", tau, Y))
                    fams.append((tau, M, None))
                    continue
                g = common.pop()
                T = L.tri_entries(M[0], g)
                if any(L.tri_entries(y, g) != T for y in M):
                    S["T not constant"] += 1
                tt = L.tri_type(T)
                gr = group(tt)
                C = L.markov_C(T)
                fam_type[tt] += 1
                if rnd:
                    fam_type_rand[gr] += 1
                types_here.add(gr)
                Cvals[gr].add(C)
                j = tau_j(C, tau)
                jdist[gr][j] += 1
                if rnd:
                    jdist_rand[gr][j] += 1
                if j == "NOT A CHEBYSHEV VALUE" and len(examples) < 10:
                    examples.append(("tau not Chebyshev", tau, C, tt, Y))
                # monotone entries
                mono = True
                for a in range(6):
                    sq = [y[a] for y in M]
                    if len(set(sq)) == 1:
                        continue
                    if not (all(x > 0 for x in sq) or all(x < 0 for x in sq)):
                        mono = False
                    if any(abs(sq[k + 1]) < abs(sq[k]) for k in range(len(sq) - 1)):
                        mono = False
                S["families with monotone entries (n <= 12)"] += mono
                # growing vertex step
                ds = [dominant(M[n], g) for n in range(NM + 1)]
                up = [L.strict_up_exit(M[n], g) for n in range(min(NM, 8) + 1)]
                first = next((n for n in range(NM + 1) if ds[n]), None)
                if first is None:
                    dom["(D1)-(D3) fail for all n <= 12"] += 1
                else:
                    dom["(D1)-(D3) from n = %d" % first] += 1
                    if not all(ds[first:]):
                        dom["(D1)-(D3) hold at some n and fail later"] += 1
                dom["step at g a strict up-exit for every n <= 8"] += all(up)
                dom["(D1)-(D3) hold but the step at g is not a strict up-exit"] += sum(1 for n in range(len(up)) if ds[n] and not up[n])
                if not all(up):
                    dom["step at g NOT a strict up-exit at some n <= 8: n = " + ",".join(str(n) for n in range(len(up)) if not up[n])] += 1
                fams.append((tau, M, g))
            for gr in types_here:
                cls_type[gr] += 1
                if rnd:
                    cls_type_rand[gr] += 1
            # links and tubes
            idx = {}
            for fid, (tau, M, g) in enumerate(fams):
                for n, y in enumerate(M):
                    idx.setdefault(L.canon(y), (fid, n))
            adj = {fid: set() for fid in range(len(fams))}
            used = {fid: set() for fid in range(len(fams))}
            linkto = {fid: {} for fid in range(len(fams))}
            for fid, (tau, M, g) in enumerate(fams):
                for m in range(4):
                    if m == g:
                        continue
                    hits = [idx.get(L.canon(L.mutate(M[n], m))) for n in (3, 4, 5)]
                    if all(h is not None for h in hits) and len({h[0] for h in hits}) == 1 and \
                            len({h[1] - n for h, n in zip(hits, (3, 4, 5))}) == 1:
                        adj[fid].add(hits[0][0])
                        linkto[fid][m] = hits[0][0]
                    else:
                        allup = all(L.strict_up_exit(M[n], m) for n in (3, 4, 5))
                        S["steps inside T that are strict up-exits"] += allup
                        S["steps inside T unresolved (not a family, not an exit)"] += not allup
                        if not allup:
                            lv = max(L.level(L.mutate(M[n], m)) for n in (3, 4, 5) if not L.strict_up_exit(M[n], m))
                            S["   of these: target level <= L of the certificate (E region)"] += lv <= rec["L"]
                            S["   of these: some n in 3..5 lands on a family member (shift varies)"] += any(h is not None for h in hits)
            comps = tarjan({k: sorted(v) for k, v in adj.items()})
            kinds_here = set()
            for comp in comps:
                cs = set(comp)
                if len(comp) == 1 and comp[0] not in adj[comp[0]]:
                    f0 = fams[comp[0]]
                    tr = group(L.tri_type(L.tri_entries(f0[1][0], f0[2]))) if f0[2] is not None else "none"
                    nin = sum(1 for k2 in adj if comp[0] in adj[k2])
                    dupl = any(idx.get(L.canon(f0[1][n]), (comp[0],))[0] != comp[0] for n in (3, 4, 5, 6))
                    trivial[(tr, "with links out" if adj[comp[0]] else "no links out", "with links in" if nin else "no links in",
                             "its members are indexed under another family (duplicate)" if dupl else "not a duplicate")] += 1
                    continue                                         # not a tube: no cycle
                per = []
                ws = set()
                for fid in comp:
                    ms = sorted(m for m, t in linkto[fid].items() if t in cs)
                    per.append(len(ms))
                    if len(ms) == 2:
                        ws.add(abs(L.e(fams[fid][1][0], ms[0], ms[1])))
                walk = "three vertices" if max(per) >= 3 else ("pair, c = %s" % sorted(ws) if ws else "one vertex per family")
                trs = sorted({group(L.tri_type(L.tri_entries(fams[fid][1][0], fams[fid][2]))) for fid in comp if fams[fid][2] is not None})
                key = (walk, " + ".join(trs))
                tubes[key] += 1
                ntubes += 1
                kinds_here.add(" + ".join(trs))
                if rnd:
                    tubes_rand[key] += 1
                    ntubes_rand += 1
            k = "only " + kinds_here.pop() if len(kinds_here) == 1 else ("two or three types" if kinds_here else "no tube")
            cls_tubekinds[k] += 1
            if rnd:
                cls_tubekinds_rand[k] += 1
    print("sample:", dict(why))
    for k, v in S.items():
        print(f"   {k}: {v}")
    F = sum(fam_type.values())
    Fr = sum(fam_type_rand.values())
    print(f"\nfamilies by the type of T (all {F}; random sample {Fr}, share of the random sample in brackets):")
    for k, v in sorted(fam_type.items(), key=lambda kv: -kv[1]):
        print(f"   {v:8d}  {k}")
    for k, v in sorted(fam_type_rand.items(), key=lambda kv: -kv[1]):
        print(f"   random: {v:8d} ({100 * v / Fr:.3f} %)  {k}")
    print(f"\nclasses with a family of the type (random sample of {nrand} classes):")
    for k, v in sorted(cls_type_rand.items(), key=lambda kv: -kv[1]):
        print(f"   {v:6d} ({100 * v / nrand:.2f} %)  {k}")
    print("   all sampled classes:", dict(cls_type))
    print("\nMarkov constants by type (min, max, number of values):")
    for k, v in sorted(Cvals.items()):
        print(f"   {k}: {min(v)} .. {max(v)}, {len(v)} values; smallest: {sorted(v)[:12]}")
    print("\ntau against C (all; random in brackets):")
    for k in sorted(jdist):
        tot = sum(jdist_rand[k].values()) or 1
        print(f"   {k}: " + "; ".join(f"{j}: {v} ({jdist_rand[k][j]}, {100 * jdist_rand[k][j] / tot:.3f} %)" for j, v in jdist[k].most_common()))
    print("\nthe growing-vertex step:")
    for k, v in sorted(dom.items()):
        print(f"   {v:8d}  {k}")
    print(f"\ntubes (strongly connected sets of families with a cycle): {ntubes} in all, {ntubes_rand} in the random sample "
          f"({ntubes_rand / max(1, nrand):.3f} per class; note 22: 650,334 / 225,208 = 2.888)")
    for k, v in sorted(tubes.items(), key=lambda kv: -kv[1]):
        print(f"   {v:7d} ({tubes_rand[k]:6d}, {100 * tubes_rand[k] / max(1, ntubes_rand):.2f} %)  {k[0]} | {k[1]}")
    print("\nsingle families on no cycle of families (trivial strongly connected components, not counted as tubes above):")
    for k, v in sorted(trivial.items(), key=lambda kv: -kv[1]):
        print(f"   {v:7d}  {k}")
    print("\nclasses by the triangles of their tubes (random sample):")
    for k, v in sorted(cls_tubekinds_rand.items(), key=lambda kv: -kv[1]):
        print(f"   {v:6d} ({100 * v / max(1, nrand):.2f} %)  {k}")
    print("   all sampled:", dict(cls_tubekinds))
    for ex in examples:
        print("   example:", ex)


if __name__ == "__main__":
    main()
