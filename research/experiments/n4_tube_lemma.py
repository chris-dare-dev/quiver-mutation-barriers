"""Note 22: a general lemma for the tubes of note 14, and where a finite description by tubes fails.

Builds on n4_opposite.py (forks, pre-forks, exits, V') and n4_opposite_tubes.py (tube certificates).

  classify    the 6,990 classes without a finite core or a tube certificate: disconnected, acyclic bottom,
              Markov triangle, and the growth of V' cut at levels 32b and 128b
  shapes      every family of the note-14 certificates: growing vertex, the fixed triangle T, its type and
              Markov constant C(T), tau against C(T), hypotheses (D1)-(D3) of Lemma 22.1 at the growing
              vertex, and the tubes (strongly connected sets of families) with their walks
  lemma       random checks of Lemmas 22.1, 22.2, 22.3 and of Proposition 22.4
  markov      Lemma 22.6 and Theorem 22.7: the class of the Markov triangle with one pendant arrow
  side        the side tubes of census class 108970
  certify2    second-pass certificates: note 14's engine with polynomial families for tau = 2 (spikes),
              a corridor search on weight-2 pairs, and larger caps; crosschecks against the census mirror
              map and the bottoms of all certified classes
  verify2     exhaustive cuts of V' and a replay of the closure for a sample of second-pass certificates
  pairs       the 6,990 classes and the open mirror pairs, by kind, before and after the second pass
  sidesig     the side-tube signature of the connected cyclic classes the second pass leaves open
Run from experiments/ with python -I.  Quivers are 6-tuples (b01, b02, b03, b12, b13, b23).
"""
import argparse
import gzip
import itertools
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n4_opposite as O
import n4_opposite_tubes as TB


# ----------------------------------------------------------------------------- basic helpers
def components(t):
    adj = {i: set() for i in range(4)}
    for (i, j), x in zip(O.PAIRS, t):
        if x:
            adj[i].add(j)
            adj[j].add(i)
    seen, comps = set(), []
    for s in range(4):
        if s in seen:
            continue
        st, c = [s], {s}
        seen.add(s)
        while st:
            u = st.pop()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    c.add(w)
                    st.append(w)
        comps.append(len(c))
    return sorted(comps)


def triangle(t, g):
    """The three entries of the full subquiver on the vertices other than g, as (b_ab, b_ac, b_bc)."""
    a, b, c = [v for v in range(4) if v != g]
    return (O.entry(t, a, b), O.entry(t, a, c), O.entry(t, b, c))


def column(t, g):
    """v_i = b_ig for the vertices i != g, in increasing order."""
    return tuple(O.entry(t, i, g) for i in range(4) if i != g)


def tri_weights(t, g):
    return tuple(sorted(abs(x) for x in triangle(t, g)))


def is_markov(t, g):
    """The triangle on the vertices other than g is the Markov quiver: an oriented 3-cycle with weights 2, 2, 2."""
    a, b, c = [v for v in range(4) if v != g]
    e = (O.entry(t, a, b), O.entry(t, b, c), O.entry(t, c, a))
    return e in ((2, 2, 2), (-2, -2, -2))


def ball(x, L, cap=None):
    """V'(x) cut at level L: quivers reached from x by allowed steps through quivers of level <= L."""
    s = O.canon(x)
    lev = {s: O.level(s)}
    todo = [s]
    while todo:
        y = todo.pop()
        ey = O.exit_returns(y)
        for m in range(4):
            z = O.mutate(y, m)
            if m not in ey and m in O.exit_returns(z):
                continue
            c = O.canon(z)
            if c in lev or O.level(c) > L:
                continue
            if cap is not None and len(lev) >= cap:
                return lev, False
            lev[c] = O.level(c)
            todo.append(c)
    return lev, True


def start_quiver(q):
    """A quiver of the class that certainly lies in no far region (as in n4_opposite_tubes.certify)."""
    x = tuple(q)
    if O.certainly_in_core(x):
        return O.canon(x)
    lev, adj, ex = O.no_exit_closure(x, cap=800, level_cap=10 ** 6)
    cands = [y for y in lev if O.certainly_in_core(y)]
    if not cands:
        return None
    return O.canon(min(cands, key=lambda y: (lev[y], y)))


def load_gz(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


# ----------------------------------------------------------------------------- classify the uncertified classes
def classify_record(a):
    i, b, q0, acyc, x = a
    t0 = time.time()
    rec = {"i": i, "b": b}
    rec["disc"] = components(q0) != [4]
    rec["acyc"] = acyc
    if x is None:
        x = start_quiver(q0)
    if x is None:
        rec["kind"] = "no start"
        return rec
    rec["x"] = list(x)
    L1 = 32 * b
    L2 = 4 * L1
    lev1, ok1 = ball(x, L1, cap=6000)
    lev2, ok2 = ball(x, L2, cap=24000)
    rec["n1"], rec["n2"], rec["ok2"] = len(lev1), len(lev2), ok2
    mk = [y for y in lev2 if any(is_markov(y, g) for g in range(4))]
    rec["markov"] = len(mk)
    if mk:
        rec["mq"] = list(min(mk, key=lambda y: (O.level(y), y)))
    shapes = Counter()
    for y, l in lev2.items():
        if l <= L1:
            continue
        g = min(range(4), key=lambda g: (max(tri_weights(y, g)), g))
        shapes[tri_weights(y, g)] += 1
    rec["nshapes"] = len(shapes)
    rec["shapes"] = [[list(k), v] for k, v in shapes.most_common(6)]
    rec["t"] = round(time.time() - t0, 2)
    return rec


def cmd_classify(args):
    plats = {p["i"]: p for p in load_gz(args.plateaus)}
    cores = {c["i"]: c for c in load_gz(args.cores) if not c["ex"]}
    jobs = []
    for r in load_gz(args.tubes):
        if r["status"] == "certified":
            continue
        p = plats[r["i"]]
        jobs.append((r["i"], r["b"], tuple(p["comps"][0]["k"]), any(c["acyc"] for c in p["comps"]),
                     tuple(r["x"]) if "x" in r else None))
    if args.limit:
        random.Random(args.seed).shuffle(jobs)
        jobs = sorted(jobs[:args.limit])
    t0 = time.time()
    recs = []
    with Pool(args.procs) as pool, gzip.open(args.out, "wt") as out:
        for rec in pool.imap_unordered(classify_record, jobs, chunksize=4):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            recs.append(rec)
    summarize_classify(recs)
    print(f"wall time {time.time() - t0:.0f}s")


def growth_kind(r):
    if not r["ok2"]:
        return "cap"
    ratio = r["n2"] / max(1, r["n1"])
    if ratio >= 8:
        return "quadratic"
    if ratio >= 2.5:
        return "linear"
    return "slow"


def summarize_classify(recs):
    tab = Counter()
    for r in recs:
        if r.get("kind") == "no start":
            tab[("no start",)] += 1
            continue
        base = "disconnected" if r["disc"] else ("acyclic bottom" if r["acyc"] else "cyclic bottom")
        tab[(base, "Markov" if r["markov"] else "no Markov", growth_kind(r))] += 1
    print(f"{len(recs)} uncertified classes")
    for k, v in sorted(tab.items()):
        print(f"   {v:6d}  {' / '.join(k)}")



# ----------------------------------------------------------------------------- step 1: tube shapes
def tri_type(T):
    """Type of a 3-vertex quiver given by its entries (b_ab, b_ac, b_bc)."""
    w = tuple(sorted(abs(x) for x in T))
    a, b, c = T
    cyc = (a > 0 and c > 0 and b < 0) or (a < 0 and c < 0 and b > 0)   # a->b->c->a or reverse
    if w == (2, 2, 2) and cyc:
        return "Markov"
    if w[0] == 0 and w[1] == 0:
        return "(0,0,a)"
    if w[0] == 2 and w[1] == w[2] and cyc:
        return "(2,m,m) cyclic"
    if w[:2] == (0, 1) or (w[0] == 1 and w[1] == w[2] and w[1] >= 2):
        return "(0,1,a)/(1,a,a)"
    if w[:2] == (1, 1) or (w[0] == 1 and w[2] == w[1] + 1):
        return "(1,1,a)/(1,a,a+1)"
    if w[0] == 0:
        return "(0,p,q) other"
    return ("cyclic " if cyc else "acyclic ") + ("abundant" if w[0] >= 2 else "with a light pair")


def markov_constant(T):
    """C(T) = x^2 + y^2 + z^2 - |xyz| for an oriented 3-cycle, + |xyz| otherwise: a mutation invariant of
    3-vertex quivers (Beineke-Bruestle-Hille)."""
    a, b, c = T
    cyc = (a > 0 and c > 0 and b < 0) or (a < 0 and c < 0 and b > 0)
    p = abs(a * b * c)
    return a * a + b * b + c * c + (-p if cyc else p)


def tau_from_C(C, tau, kmax=8):
    """Is tau = lambda^k + lambda^-k for lambda + 1/lambda = C - 2 and some k >= 1 (or its square root
    for a half period: tau^2 - 2 = C - 2)?"""
    t1 = C - 2
    if t1 < 2:
        return None
    prev, cur = 2, t1
    for k in range(1, kmax + 1):
        if tau == cur:
            return "C - 2" if k == 1 else "k = %d" % k
        prev, cur = cur, t1 * cur - prev
    # half periods (the pair walk on (0, 0, a)): tau = mu^j + mu^-j with mu + 1/mu = sqrt(C), j odd
    a = math.isqrt(C)
    if a * a == C:
        prev, cur = 2, a
        for j in range(1, 2 * kmax + 2):
            if tau == cur and j % 2 == 1:
                return "half" if j == 1 else "half x %d" % j
            prev, cur = cur, a * cur - prev
    return None


def growing_vertex(Y):
    """The vertex g common to all non-constant entries of the family, or None."""
    S = TB.seqs(Y)
    var = [a for a in range(6) if not S[a].const()]
    if not var:
        return None
    common = set(range(4))
    for a in var:
        common &= set(O.PAIRS[a])
    return min(common) if len(common) == 1 else None


def dominant(t, g):
    """Hypotheses (D1)-(D3) of Lemma 22.1 for the vertex g of t."""
    v = {i: O.entry(t, i, g) for i in range(4) if i != g}
    if not (any(x > 0 for x in v.values()) and any(x < 0 for x in v.values())):
        return False
    if any(abs(x) < 2 for x in v.values()):
        return False
    return all(abs(O.entry(t, i, j)) < max(abs(v[i]), abs(v[j])) for i, j in itertools.combinations(sorted(v), 2))


def family_graph(nodes):
    """For every family and vertex: ('g', None) for the step at the growing vertex, ('exit', None) for a
    strict up-exit, ('fam', key) for a step into a family of the certificate."""
    out = {}
    for key, Y in nodes.items():
        tau = key[0]
        S = TB.seqs(Y)
        exY = O.exit_returns(S)
        row = {}
        for m in range(4):
            Yp = tuple(O.mutate(y, m) for y in Y)
            try:
                Sp = O.mutate(S, m)
            except TB.Nonlinear:
                row[m] = ("g", None)
                continue
            hit = None
            for d in TB.SHIFTS:
                kz = (tau, TB.canon_triple(TB.shift(Yp, -d, tau)))
                if kz in nodes:
                    hit = kz
                    break
            if hit is not None:
                row[m] = ("fam", hit)
            elif m not in exY and m in O.exit_returns(Sp):
                row[m] = ("exit", None)
            else:
                row[m] = ("?", None)
        out[key] = row
    return out


def sccs(adj):
    """Strongly connected components (Tarjan, iterative)."""
    index, low, on, st, comps, cnt = {}, {}, set(), [], [], [0]
    for v0 in adj:
        if v0 in index:
            continue
        work = [(v0, iter(adj[v0]))]
        index[v0] = low[v0] = cnt[0]
        cnt[0] += 1
        st.append(v0)
        on.add(v0)
        while work:
            v, it = work[-1]
            nxt_ = next(it, None)
            if nxt_ is None:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    comp = []
                    while True:
                        w = st.pop()
                        on.discard(w)
                        comp.append(w)
                        if w == v:
                            break
                    comps.append(comp)
            elif nxt_ not in index:
                index[nxt_] = low[nxt_] = cnt[0]
                cnt[0] += 1
                st.append(nxt_)
                on.add(nxt_)
                work.append((nxt_, iter(adj[nxt_])))
            elif nxt_ in on:
                low[v] = min(low[v], index[nxt_])
    return comps


def shapes_record(a):
    i, b, x = a
    rec, obj = TB.certify(i, b, x, full=True)
    out = {"i": i, "b": b, "status": rec["status"]}
    if obj is None:
        return out
    _, E, nodes, members, D = obj
    G = family_graph(nodes)
    fams = []
    lemma = Counter()
    for key, Y in nodes.items():
        g = growing_vertex(Y)
        T = triangle(Y[0], g) if g is not None else None
        Tconst = g is not None and all(triangle(y, g) == T for y in Y)
        f = {"tau": key[0], "g": g, "Tconst": Tconst, "type": tri_type(T) if T else "no single growing vertex"}
        if T:
            f["C"] = markov_constant(T)
            f["tauC"] = tau_from_C(f["C"], key[0])
        # Lemma 22.1 at the growing-vertex steps: (D1)-(D3) at n = 0, else at the first n <= 12 where they hold
        if g is not None and G[key][g][0] == "g":
            fam = TB.Family(key[0], Y)
            first = next((n for n in range(13) if dominant(fam.get(n), g)), None)
            lemma["g-steps"] += 1
            lemma["(D1)-(D3) at n = 0" if first == 0 else ("(D1)-(D3) from n = %s" % first if first is not None else "(D1)-(D3) fail up to n = 12")] += 1
        fams.append(f)
    adj = {k: [t for (kind, t) in G[k].values() if kind == "fam" and t != k] for k in nodes}
    tubes = []
    for comp in sccs(adj):
        cs = set(comp)
        if len(comp) == 1 and comp[0] not in adj[comp[0]] and not any(
                kind == "fam" and t == comp[0] for (kind, t) in G[comp[0]].values()):
            pass
        # vertices whose steps stay in the component, per family
        used = []
        for k in comp:
            ms = sorted(m for m, (kind, t) in G[k].items() if kind == "fam" and t in cs)
            used.append(ms)
        g0 = growing_vertex(nodes[comp[0]])
        if all(len(ms) <= 2 for ms in used):
            ws = set()
            for k, ms in zip(comp, used):
                if len(ms) == 2:
                    ws.add(abs(O.entry(nodes[k][0], ms[0], ms[1])))
            walk = "pair, c = %s" % sorted(ws) if ws else "pair"
        else:
            walk = "three vertices"
        tubes.append({"n": len(comp), "tau": comp[0][0], "walk": walk,
                      "types": sorted({tri_type(triangle(nodes[k][0], growing_vertex(nodes[k]))) if growing_vertex(nodes[k]) is not None else "none" for k in comp})})
    out.update({"fams": fams, "tubes": tubes, "lemma": dict(lemma),
                "unknown_steps": sum(1 for r in G.values() for kind, _ in r.values() if kind == "?")})
    return out


def cmd_shapes(args):
    t0 = time.time()
    if args.summary:
        res = load_gz(args.out)
        for r in res:                                   # tau against C(T) with the current classification
            for f in r.get("fams", []):
                if "C" in f:
                    f["tauC"] = tau_from_C(f["C"], f["tau"])
    else:
        recs = [r for r in load_gz(args.tubes) if r["status"] == "certified"]
        random.Random(args.seed).shuffle(recs)
        jobs = [(r["i"], r["b"], r["x"]) for r in recs[:args.classes]]
        with Pool(args.procs) as pool:
            res = pool.map(shapes_record, jobs, chunksize=4)
        with gzip.open(args.out, "wt") as f:
            for r in res:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
    ok = [r for r in res if r["status"] == "certified"]
    print(f"{len(res)} certified classes re-run, {len(ok)} certified again ({time.time() - t0:.0f}s)")
    nf = sum(len(r["fams"]) for r in ok)
    print(f"families: {nf}; with a single growing vertex: {sum(1 for r in ok for f in r['fams'] if f['g'] is not None)}; "
          f"with T constant along the family: {sum(1 for r in ok for f in r['fams'] if f['Tconst'])}")
    print("families by the type of T:")
    for k, v in Counter(f["type"] for r in ok for f in r["fams"]).most_common():
        print(f"   {v:7d}  {k}")
    print("tau against the Markov constant C(T) (tau = t_k with t_1 = C - 2, or half: tau^2 - 2 = C - 2):")
    for k, v in Counter((f["type"], f.get("tauC")) for r in ok for f in r["fams"]).most_common():
        print(f"   {v:7d}  {k[0]}: {k[1]}")
    print("   C(T) values by type:", {t: sorted(Counter(f["C"] for r in ok for f in r["fams"] if f["type"] == t))[:12]
                                       for t in sorted({f["type"] for r in ok for f in r["fams"]})})
    lem = Counter()
    for r in ok:
        lem.update(r["lemma"])
    print("steps at the growing vertex (Lemma 22.1):", dict(lem))
    print("steps not classified (should be 0):", sum(r["unknown_steps"] for r in ok))
    tubes = [t for r in ok for t in r["tubes"]]
    print(f"tubes (strongly connected sets of families): {len(tubes)}")
    tab = Counter()
    for t in tubes:
        w = t["walk"]
        if w.startswith("pair, c = "):
            cs = json.loads(w[len("pair, c = "):])
            c = cs[0] if len(cs) == 1 else None
            rel = ("tau = c" if t["tau"] == c else "tau = c^2 - 2" if c is not None and t["tau"] == c * c - 2 else
                   "tau other") if c is not None else "several c"
            w = "pair walk (rank-2 orbit), c = 2" if c == 2 else "pair walk (rank-2 orbit), c >= 3, " + rel
        tab[(w, " + ".join(t["types"]))] += 1
    for k, v in tab.most_common():
        print(f"   {v:7d}  {k[0]} | {k[1]}")
    cl = Counter()
    for r in ok:
        kinds = set()
        for t in r["tubes"]:
            kinds.add("pair c=2" if t["walk"] == "pair, c = [2]" else "pair c>=3" if t["walk"].startswith("pair") else "three")
        cl[" + ".join(sorted(kinds))] += 1
    print("classes by the kinds of their tubes:")
    for k, v in cl.most_common():
        print(f"   {v:7d}  {k}")



# ----------------------------------------------------------------------------- the Markov obstruction
# vertex 0 = g; the Markov triangle 1 -> 2 -> 3 -> 1 with weight 2; v_i = b_i0
def markov_quiver(v):
    return (-v[0], -v[1], -v[2], 2, -2, 2)


def markov_coords(t):
    """All v with t isomorphic to markov_quiver(v) by a relabelling fixing 0 (empty if T is not Markov)."""
    out = set()
    for p in itertools.permutations((1, 2, 3)):
        perm = (0,) + p
        r = tuple(O.entry(t, perm[i], perm[j]) for (i, j) in O.PAIRS)
        if r[3:] == (2, -2, 2):
            out.add((-r[0], -r[1], -r[2]))
    return out


def allowed(x, m):
    """The step x -> mu_m(x) is not a strict up-exit step."""
    return not (m not in O.exit_returns(x) and m in O.exit_returns(O.mutate(x, m)))


def cmd_markov(args):
    rng = random.Random(args.seed)
    # Lemma 22.6: no step at a vertex of a Markov triangle is a strict up-exit, and (mu_k X, k) is never an exit
    bad = n = 0
    for _ in range(args.random):
        v = tuple(rng.randint(-args.vmax, args.vmax) for _ in range(3))
        x = markov_quiver(v)
        for k in (1, 2, 3):
            n += 1
            bad += k in O.exit_returns(O.mutate(x, k))
    print(f"Lemma 22.6: {n} steps mu_k, k in the Markov triangle, from random columns |v_i| <= {args.vmax}: "
          f"(mu_k X, k) an exit in {bad}")
    # the corridors P_z = (1 - z, 0, z), C^n(P_z) = (-(z-1)(n+1), (z-1) n, z), reached by real mutations
    x0 = markov_quiver((1, 0, 0))
    seen = set()
    steps = fails = 0
    cur = x0
    a = 1
    points = 0
    for z in range(2, args.zmax + 1):
        # (a, 0, 1 - a) -> (a + 1, 0, -a): one step at vertex 1 (allowed), up to a rotation of T
        while a < z:
            assert (a, 0, 1 - a) in {w for w in markov_coords(cur)} or (0, 1 - a, a) in markov_coords(cur) or (1 - a, a, 0) in markov_coords(cur)
            # find the label of the vertex carrying v = a > 0 and step there
            k = next(k for k in (1, 2, 3) if O.entry(cur, k, 0) == a)
            steps += 1
            fails += not allowed(cur, k)
            cur = O.mutate(cur, k)
            a += 1
        # now cur has column (a, 0, 1 - a) up to rotation with a = z; step at the zero entry gives P_z
        k = next(k for k in (1, 2, 3) if O.entry(cur, k, 0) == 0)
        steps += 1
        fails += not allowed(cur, k)
        y = O.mutate(cur, k)
        if not any(w in markov_coords(y) for w in [(1 - z, 0, z), (0, z, 1 - z), (z, 1 - z, 0)]):
            print("  P_z not reached at z =", z)
            fails += 1
        # the corridor: step at the vertex with v = -(z-1)(n+1) < 0
        for nn in range(args.nmax + 1):
            target = (-(z - 1) * (nn + 1), (z - 1) * nn, z)
            rots_ = {target, target[1:] + target[:1], target[2:] + target[:2]}
            if not (rots_ & markov_coords(y)):
                print("  corridor point missing", z, nn, target)
                fails += 1
                break
            seen.add(O.canon(y))
            points += 1
            k = next(k for k in (1, 2, 3) if O.entry(y, k, 0) == -(z - 1) * (nn + 1))
            steps += 1
            fails += not allowed(y, k)
            y = O.mutate(y, k)
    print(f"corridors z = 2..{args.zmax}, n = 0..{args.nmax}: {points} points, {len(seen)} distinct quivers up to "
          f"relabelling, {steps} steps by real mutations, steps that are strict up-exits or misses: {fails}")
    # counts below level L against the bound for finitely many families
    for L in (100, 1000, 10000):
        cnt = sum(1 for z in range(3, L + 2) for nn in range(1, L + 1) if (z - 1) * (nn + 1) <= L and z <= L)
        print(f"   L = {L}: corridor pairs (z >= 3, n >= 1) of level <= L: {cnt} (L ln L / 2 = {L * math.log(L) / 2:.0f})")
    # V' cut at level L from X0 (exhaustive)
    for L in args.levels:
        lev, ok = ball(x0, L, cap=400000)
        mk = sum(1 for y in lev if any(is_markov(y, g) for g in range(4)))
        print(f"   V'(X0) cut at level {L}: {len(lev)} quivers ({'complete' if ok else 'cap'}), {mk} with a Markov triangle")



# ----------------------------------------------------------------------------- the side-tube obstruction (class 108970)
def cmd_side(args):
    x = (8, 0, -7, -7, 2, 1)                       # a quiver of census class 108970 in no far region
    print("start", x, "certainly in no far region:", O.certainly_in_core(x))
    lev, ok = ball(x, 10 ** args.cut)
    print(f"V'(x) cut at level 10^{args.cut}: {len(lev)} quivers ({'complete' if ok else 'cap'})")
    # the (0,0,57) tube with a pendant vertex: Y_k = (A_{k+1}, 0, -57, -1, A_k, 0)
    A = [49, 2791]
    while len(A) < args.kmax + 2:
        A.append(57 * A[-1] - A[-2])
    inV = sum(1 for k in range(1, args.kmax + 1) if O.level((A[k], 0, -57, -1, A[k - 1], 0)) <= 10 ** args.cut
              and O.canon((A[k], 0, -57, -1, A[k - 1], 0)) in lev)
    cnt = sum(1 for k in range(1, args.kmax + 1) if O.level((A[k], 0, -57, -1, A[k - 1], 0)) <= 10 ** args.cut)
    print(f"members Y_k of the (0,0,57) tube below the cut: {cnt}, found in V'(x): {inV}")
    # Y_k is a member of the (0,0,57) tube (growing vertex 1) by a step at vertex 3 or 0 ...
    steps_ok = 0
    for k in range(1, args.kmax):
        Y = (A[k], 0, -57, -1, A[k - 1], 0)
        nxt_ = O.canon((A[k + 1], 0, -57, -1, A[k], 0))
        hit = [m for m in range(4) if O.canon(O.mutate(Y, m)) == nxt_ and allowed(Y, m)]
        steps_ok += bool(hit)
    print(f"Y_k -> Y_(k+1) by one allowed step: {steps_ok} of {args.kmax - 1}")
    # ... and the base of a side tube: allowed steps at 0, 1, 2 keep the triangle {0,1,2} = (0, 1, A_k)
    print("side tubes: allowed steps at vertices 0, 1, 2 that keep the triangle on {0, 1, 2} of shape (0,1,a) or (1,a,a), a = A_k:")
    for k in range(1, args.kmax + 1):
        Y = (A[k], 0, -57, -1, A[k - 1], 0)
        a = A[k]
        shapes_ = {(0, 1, a), (1, a, a)}
        frontier, seen, tops = [Y], {Y}, []
        for d in range(args.depth):
            new = []
            for y in frontier:
                for m in (0, 1, 2):
                    if not allowed(y, m):
                        continue
                    z = O.mutate(y, m)
                    if tri_weights(z, 3) in shapes_ and z not in seen:
                        seen.add(z)
                        new.append(z)
            frontier = new
            if not frontier:
                break
            tops.append(max(abs(O.entry(z, 3, u)) for z in frontier for u in range(3)))
        digits = [len(str(t)) for t in tops]
        if k <= 6 or k == args.kmax:
            print(f"   k = {k:2d}: a = A_k has {len(str(a))} digits; depth reached {len(tops)}; digits of the largest "
                  f"entry at vertex 3 by depth: {digits}; tau of the side tube = (a^2 - 1)^2 - 2 has {len(str((a * a - 1) ** 2 - 2))} digits")
        if len(tops) < args.depth:
            print(f"   k = {k}: side walk stopped at depth {len(tops)}")



# ----------------------------------------------------------------------------- polynomial families (tau = 2 and spikes)
PD = 8          # degree bound: a polynomial family is given by its values at n = 0, ..., PD


def _diffs(v):
    """Forward differences at 0: v(0), D v(0), D^2 v(0), ..."""
    out = []
    v = list(v)
    while v:
        out.append(v[0])
        v = [b - a for a, b in zip(v, v[1:])]
    return out


class PSeq:
    """A polynomial in n of degree <= PD, given by its values at 0..PD.  Certified facts for all n >= 0 come
    from the Newton expansion p(n) = sum_j D^j p(0) C(n, j): if p(0) > 0 and D^j p(0) >= 0 for j >= 1, then p
    is positive and non-decreasing on n >= 0."""
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = tuple(v)

    def const(self):
        return all(x == self.v[0] for x in self.v)

    def degree(self):
        d = _diffs(self.v)
        return max((j for j, x in enumerate(d) if x), default=-1)

    def _pos(self):
        d = _diffs(self.v)
        return d[0] > 0 and all(x >= 0 for x in d[1:])

    def _nonneg(self):
        d = _diffs(self.v)
        return d[0] >= 0 and all(x >= 0 for x in d[1:])

    def sign(self):
        if all(x == 0 for x in self.v):
            return 0
        if self._pos():
            return 1
        if (-self)._pos():
            return -1
        raise TB.Undetermined()

    def __neg__(self):
        return PSeq(-x for x in self.v)

    def __abs__(self):
        if self._nonneg():
            return self
        if (-self)._nonneg():
            return -self
        raise TB.Undetermined()

    def _o(self, o):
        return o.v if isinstance(o, PSeq) else (o,) * len(self.v)

    def __add__(self, o):
        return PSeq(a + b for a, b in zip(self.v, self._o(o)))

    __radd__ = __add__

    def __sub__(self, o):
        return PSeq(a - b for a, b in zip(self.v, self._o(o)))

    def __rsub__(self, o):
        return PSeq(b - a for a, b in zip(self.v, self._o(o)))

    def __mul__(self, o):
        if isinstance(o, int):
            return PSeq(o * a for a in self.v)
        if self.degree() + o.degree() > PD:
            raise TB.Nonlinear()
        return PSeq(a * b for a, b in zip(self.v, o.v))

    __rmul__ = __mul__

    def __gt__(self, o):
        return (self - o).sign() > 0 if not (self - o)._nonneg() or (self - o)._pos() else _gt_slow(self - o)

    def __lt__(self, o):
        return (o - self) > 0 if isinstance(o, PSeq) else PSeq(o - a for a in self.v) > 0

    def __ge__(self, o):
        return not (self < o)

    def __le__(self, o):
        return not (self > o)

    def __eq__(self, o):
        d = self - o
        if all(x == 0 for x in d.v):
            return True
        d.sign()
        return False

    def __ne__(self, o):
        return not self.__eq__(o)

    __hash__ = None


def _gt_slow(d):
    """d > 0 for all n, where d is certified non-negative: true if d(0) > 0, false if d is identically 0."""
    if all(x == 0 for x in d.v):
        return False
    if d.v[0] > 0:
        return True
    raise TB.Undetermined()


def _pseq_gt(self, o):
    d = self - o
    sg = d.sign()
    return sg > 0


PSeq.__gt__ = _pseq_gt


def pvals(Y):
    """Family of polynomial values -> six PSeq."""
    return tuple(PSeq(Y[k][a] for k in range(PD + 1)) for a in range(6))


def p_from_triple(Y, tau):
    """A tau = 2 family of note 14 as values at 0..PD."""
    vals = [Y[0], Y[1], Y[2]]
    while len(vals) < PD + 1:
        vals.append(TB.nxt(vals[-3:], tau))
    return tuple(vals)


def p_shift(V, d):
    """Values at d..d+PD of the polynomial family with values V at 0..PD (d may be negative)."""
    out = []
    for a in range(6):
        dif = _diffs([v[a] for v in V])
        vals = []
        for n in range(d, d + PD + 1):
            # Newton: sum_j dif[j] * C(n, j), valid for negative n with the generalised binomial
            tot, c = 0, 1
            for j, x in enumerate(dif):
                tot += x * c
                c = c * (n - j) // (j + 1) if j + 1 <= PD else c
            vals.append(tot)
        out.append(vals)
    return tuple(tuple(out[a][k] for a in range(6)) for k in range(PD + 1))


def _binom_eval(dif, n):
    tot, c = 0, 1
    for j, x in enumerate(dif):
        tot += x * c
        c = c * (n - j) // (j + 1)
    return tot


def p_canon(V):
    """Canonical form of a polynomial family up to simultaneous relabelling."""
    best = None
    for pi in range(24):
        c = tuple(TB.relab(v, pi) for v in V)
        if best is None or c > best:
            best = c
    return best


class PFamily:
    def __init__(self, V):
        self.dif = [_diffs([v[a] for v in V]) for a in range(6)]
        self.V = V
        self.const = all(len(set(v[a] for v in V)) == 1 for a in range(6))
        self.w0 = O.weight(V[0])
        self.cache = {}

    def get(self, n):
        r = self.cache.get(n)
        if r is None:
            r = self.cache[n] = tuple(_binom_eval(self.dif[a], n) for a in range(6))
        return r

    def contains(self, q, w):
        if w < self.w0:
            return False
        if self.const:
            return O.canon(self.V[0]) == q
        hi = 1
        while O.weight(self.get(hi)) < w:
            hi *= 2
            if hi > 1 << 62:
                return False
        lo = 0
        while lo < hi:
            mid = (lo + hi) // 2
            if O.weight(self.get(mid)) < w:
                lo = mid + 1
            else:
                hi = mid
        n = lo
        while O.weight(self.get(n)) == w:
            if O.canon(self.get(n)) == q:
                return True
            n += 1
            if n > lo + 3:
                break
        return False


def close_poly(base, known, node_cap=200):
    """Closure of a polynomial family: every step from a family is a strict up-exit for all n, or lands in a
    known family (up to a shift by -3..3), or gives a new family that is closed in turn.  A step whose image
    is constant in n gives one concrete quiver, which must lie in E (returned in D)."""
    new, D = {}, []
    k0 = ("p", p_canon(base))
    if k0 in known:
        return new, D
    new[k0] = k0[1]
    queue = [k0]
    while queue:
        key = queue.pop()
        V = key[1]
        S = pvals(V)
        for x in S:
            if not x.const():
                try:
                    x.sign()                            # every entry constant or sign-definite
                except TB.Undetermined:
                    raise TB.Abort("an entry of a polynomial family is not sign-definite")
        exY = None
        for m in range(4):
            try:
                Sp = O.mutate(S, m)
            except TB.Undetermined:
                raise TB.Abort("undetermined comparison: mutation of a polynomial family")
            except TB.Nonlinear:
                raise TB.Abort("degree bound")
            Vp = tuple(tuple(Sp[a].v[k] for a in range(6)) for k in range(PD + 1))
            if any(O.mutate(V[k], m) != Vp[k] for k in range(PD + 1)):
                raise TB.Abort("internal: symbolic and concrete mutation differ")
            if all(len(set(v[a] for v in Vp)) == 1 for a in range(6)):
                raise TB.Abort("internal: constant image of a non-constant family")
            found = False
            for d in TB.SHIFTS:
                kz = ("p", p_canon(p_shift(Vp, -d)))
                if kz in known or kz in new:
                    for j in range(-d if d < 0 else 0):      # Y'(0), ..., Y'(|d|-1) lie below the family
                        if not (m not in O.exit_returns(V[j]) and m in O.exit_returns(Vp[j])):
                            D.append(Vp[j])                 # reached by an allowed step: must lie in E or R
                    found = True
                    break
            if found:
                continue
            try:
                if exY is None:
                    exY = O.exit_returns(S)
                exYp = O.exit_returns(Sp)
            except (TB.Undetermined, TB.Nonlinear):
                raise TB.Abort("undetermined comparison: exits of a polynomial family")
            if m not in exY and m in exYp:
                continue
            for x in Sp:
                try:
                    x.sign() if not x.const() else None
                except TB.Undetermined:
                    raise TB.Abort("a new polynomial family is not sign-definite")
            kz = ("p", p_canon(Vp))
            if len(new) >= node_cap:
                raise TB.Abort("node cap")
            new[kz] = kz[1]
            queue.append(kz)
    return new, D


class Members2(TB.Members):
    def add(self, nodes):
        for key, Y in nodes.items():
            if key not in self.fams:
                self.fams[key] = PFamily(Y) if key[0] == "p" else TB.Family(key[0], Y)
                self.no = set()


def corridor_paths(f, steps=40):
    """Rank-2 walks with c = 2 from f: for each pair {i, j} with |b_ij| = 2, mutate alternately at i and j,
    in the direction in which the level grows (note 15, Theorem 15.1).  The walk stops at the first step that
    is not allowed, so every quiver on it lies in V' when f does: the first members of a family read off it,
    which enter the bottom of the core, are then quivers of V'."""
    out = []
    for i, j in O.PAIRS:
        if abs(O.entry(f, i, j)) != 2:
            continue
        for first, second in ((i, j), (j, i)):
            ys = [f]
            y = f
            for k in range(steps):
                m = first if k % 2 == 0 else second
                if not allowed(y, m):
                    break
                y = O.mutate(y, m)
                ys.append(y)
            if len(ys) > 4 and O.level(ys[-1]) > O.level(f):
                out.append(ys)
    return out


def _candidates2(f, cache):
    yield from TB.base_candidates(TB.forward_path(f, cache))
    for ys in corridor_paths(f):
        yield from TB.base_candidates(ys, max_period=4)


def build_tube2(f, nodes, cache, max_tries=12):
    reason = "no periodic base on the forward path"
    tries = 0
    for s_, p_, tau, X in _candidates2(f, cache):
        try:
            if tau == 2:
                new, D = close_poly(p_from_triple(X, 2), nodes)
            else:
                new, D = TB.close(X, tau, {k: v for k, v in nodes.items() if k[0] != "p"})
            return new, D, (s_, p_, tau)
        except TB.Abort as e:
            reason = str(e)
        tries += 1
        if tries >= max_tries:
            break
    raise TB.Abort(reason)


def certify2(idx, b, q, budget=30.0, max_nodes=1200, ecap=6000, max_iter=60, max_raise=3, full=False):
    """n4_opposite_tubes.certify with polynomial families for tau = 2 (so that steps at the growing vertex
    of a corridor that are not exits are followed), larger caps, and the same closure logic."""
    t0 = time.time()
    rec = {"i": idx, "b": b}
    nodes = {}

    def done(status, **kw):
        rec["status"] = status
        rec.update(kw)
        rec["t"] = round(time.time() - t0, 3)
        taus = sorted({k[0] for k in nodes if k[0] != "p"})
        rec["ntau"] = len(taus)                         # distinct tau > 2 found before giving up
        rec["maxtau_digits"] = len(str(taus[-1])) if taus else 0
        return (rec, None) if full else rec

    x = start_quiver(q)
    if x is None:
        return done("failed: no start that certainly lies in the core")
    rec["x"] = list(x)
    L = max(O.level(x), 2 * b * b + 20)
    D, seeds, cache = [], [x], {}
    members = Members2()
    reason, raises = "iteration cap", 0
    orig_bfs = TB.bfs_E
    try:
        for it in range(max_iter):
            if time.time() - t0 > budget:
                return done("failed: time budget (" + reason + ")", L=L, nodes=len(nodes))
            E, frontier = orig_bfs(seeds, L, members, cache, cap=ecap)
            unc = sorted((lv, f) for f, lv in frontier.items())
            if unc:
                progress, fails = False, 0
                for lv, f in unc:
                    if f in members:
                        continue
                    if fails >= 6 or time.time() - t0 > budget:
                        break
                    try:
                        new, newD, info = build_tube2(f, nodes, cache)
                    except TB.Abort as e:
                        reason = str(e)
                        fails += 1
                        continue
                    if new:
                        progress = True
                        nodes.update(new)
                        D.extend(newD)
                        members.add(new)
                        if len(nodes) > max_nodes:
                            return done("failed: more than %d families" % max_nodes, L=L, nodes=len(nodes))
                rest = [lv for lv, f in unc if f not in members]
                newL = max([L] + [O.level(Y[0]) for Y in nodes.values()])
                if rest and newL == L:
                    if progress or raises >= max_raise:
                        newL = min(rest)
                        if not progress:
                            raises += 1
                            if raises > max_raise + 6:
                                return done("failed: " + reason, L=L, nE=len(E), nodes=len(nodes))
                    else:
                        raises += 1
                        newL = L * 8
                L = newL
                if L > 10 ** 60:
                    return done("failed: level bound (" + reason + ")", L=L, nodes=len(nodes))
                continue
            missing = [d for d in {O.canon(d) for d in D} if d not in E and d not in members]
            if not missing:
                break
            for c in missing:
                if O.level(c) <= L:
                    if c not in seeds:
                        seeds.append(c)
                else:
                    L = max(L, O.level(c))
            reason = "downward quivers outside E and R"
        else:
            return done("failed: " + reason, L=L, nodes=len(nodes))
    except TB.Abort as e:
        return done("failed: " + str(e), L=L, nodes=len(nodes))
    low = dict(E)
    for key, Y in nodes.items():
        for y in Y[:3]:
            low[O.canon(y)] = O.level(y)
    bK = min(low.values())
    lR3 = min((O.level(members.fams[key].get(3)) for key in nodes), default=None)
    out = {"L": L, "nE": len(E), "nodes": len(nodes), "npoly": sum(1 for k in nodes if k[0] == "p"), "bK": bK,
           "lR3": lR3}
    if lR3 is None or bK < lR3:
        bot = [y for y in low if low[y] == bK]
        out["kid"] = list(min(bot))
        out["mkid"] = list(min(O.canon(O.neg(y)) for y in bot))
        out["nbot"] = len(bot)
    rec.update(out)
    rec["status"] = "certified"
    rec["t"] = round(time.time() - t0, 3)
    if full:
        return rec, (x, E, nodes, members)
    return rec



def _job2(a):
    try:
        return certify2(*a)
    except Exception as e:                                  # never lose the run to one class
        return {"i": a[0], "b": a[1], "status": "error: " + repr(e)[:200]}


def cmd_certify2(args):
    cls = load_gz(args.classify)
    jobs = [(r["i"], r["b"], tuple(r["x"])) for r in cls if "x" in r]
    if args.limit:
        random.Random(args.seed).shuffle(jobs)
        jobs = sorted(jobs[:args.limit])
    t0 = time.time()
    recs = []
    with Pool(args.procs) as pool, gzip.open(args.out, "wt") as out:
        for rec in pool.imap_unordered(_job2, [(i, b, x, args.budget) for i, b, x in jobs], chunksize=2):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            recs.append(rec)
    summarize_certify2(recs, cls, args)
    print(f"wall time {time.time() - t0:.0f}s")


def summarize_certify2(recs, cls, args):
    import n4_opposite_run as R
    kinds = {}
    for r in cls:
        kinds[r["i"]] = ("disconnected" if r["disc"] else "acyclic bottom" if r["acyc"] else
                         "Markov" if r["markov"] else "cyclic, " + growth_kind(r))
    tab = Counter((kinds[r["i"]], "certified" if r["status"] == "certified" else r["status"].split(" (")[0]) for r in recs)
    print(f"{len(recs)} classes; second-pass certificates (polynomial families for tau = 2):")
    for k, v in sorted(tab.items()):
        print(f"   {v:6d}  {k[0]} | {k[1]}")
    cert = {r["i"]: r for r in recs if r["status"] == "certified" and "kid" in r}
    nokid = sum(1 for r in recs if r["status"] == "certified" and "kid" not in r)
    print(f"certified: {sum(1 for r in recs if r['status'] == 'certified')}; with a bottom of the core: {len(cert)}; "
          f"bottom not separated from the fourth members: {nokid}; polynomial families used in {sum(1 for r in cert.values() if r.get('npoly'))}")
    # crosscheck: against the census mirror map, and against the bottoms of note 14's certificates
    plats = R.load_gz(args.plateaus)
    mirror = R.mirror_map(plats)
    old = {t["i"]: t for t in R.load_gz(args.tubes) if t["status"] == "certified" and t.get("kid") is not None}
    kids = Counter(tuple(t["kid"]) for t in old.values())
    kids.update(tuple(r["kid"]) for r in cert.values())
    st = Counter()
    for i, r in cert.items():
        j = mirror[i]
        if (r["kid"] == r["mkid"]) != (j == i):
            st["kid == mkid disagrees with the census mirror map (CONTRADICTION)"] += 1
        else:
            st["kid == mkid agrees with the census mirror map"] += 1
        if kids[tuple(r["kid"])] > 1:
            st["bottom of the core shared with another certified class (hidden join)"] += 1
        if j != i and j in cert:
            rj = cert[j]
            st["mirror pair, both certified: " + ("cores are mirror images and different" if r["kid"] == rj["mkid"] and r["mkid"] == rj["kid"] and r["kid"] != rj["kid"] else "CONTRADICTION")] += 1
    for k, v in sorted(st.items()):
        print(f"   {v:6d}  {k}")
    shared = sum(1 for r in cert.values() if kids[tuple(r["kid"])] > 1)
    print(f"check: new certificates whose bottom quiver kid equals that of another certified class, old or new: "
          f"{shared} of {len(cert)}; distinct kids among all {len(old) + len(cert)} certificates: {len(kids)}")
    # open mirror pairs before and after
    acyc = [any(c["acyc"] for c in p["comps"]) for p in plats]
    unc = {r["i"] for r in cls}
    before = after = 0
    by = Counter()
    for i in unc:
        j = mirror[i]
        if j is None or j == i or j < i and j in unc:
            continue
        if acyc[i] or acyc[j]:
            continue
        before += 1
        if i in cert and j in cert:
            by[kinds[i]] += 1
        else:
            after += 1
    print(f"open mirror pairs: {before} before, {after} after; newly certified pairs by kind: {dict(by)}")
    selfm = sum(1 for i in cert if mirror[i] == i)
    print(f"self-mirror classes newly certified (core known, equal to its mirror): {selfm}")



# ----------------------------------------------------------------------------- checks of Lemmas 22.1-22.3 and Proposition 22.4
def quiver_from(T, v, g):
    """The quiver with triangle T = (b_ab, b_ac, b_bc) on the vertices a < b < c other than g and column v
    (v_i = b_ig, in increasing order of i)."""
    a, b, c = [u for u in range(4) if u != g]
    B = [[0] * 4 for _ in range(4)]

    def put(i, j, x):
        B[i][j], B[j][i] = x, -x
    put(a, b, T[0])
    put(a, c, T[1])
    put(b, c, T[2])
    for i, x in zip((a, b, c), v):
        put(i, g, x)
    return O.from_matrix(B)


def E_matrix(T, g, k, eps):
    """The matrix of Lemma 22.2 on the column (v_a, v_b, v_c)."""
    vs = [u for u in range(4) if u != g]
    t = quiver_from(T, (0, 0, 0), g)
    M = [[int(i == j) for j in range(3)] for i in range(3)]
    kk = vs.index(k)
    M[kk][kk] = -1
    for jj, j in enumerate(vs):
        if j != k:
            M[jj][kk] = max(eps * O.entry(t, j, k), 0)
    return M


def charpoly3(M):
    (a, b, c), (d, e, f), (g_, h, i) = M
    tr = a + e + i
    m2 = (a * e - b * d) + (a * i - c * g_) + (e * i - f * h)
    det = a * (e * i - f * h) - b * (d * i - f * g_) + c * (d * h - e * g_)
    return (1, -tr, m2, -det)


def cmd_lemma(args):
    rng = random.Random(args.seed)
    # Lemma 22.1
    n = bad = 0
    while n < args.n:
        g = rng.randrange(4)
        T = tuple(rng.randint(-args.tmax, args.tmax) for _ in range(3))
        v = tuple(rng.choice((-1, 1)) * rng.randint(2, args.vmax) for _ in range(3))
        x = quiver_from(T, v, g)
        if not dominant(x, g):
            continue
        n += 1
        bad += not (g not in O.exit_returns(x) and g in O.exit_returns(O.mutate(x, g)))
    print(f"Lemma 22.1: {n} random quivers with (D1)-(D3) at g; step at g not a strict up-exit: {bad}")
    # necessity: drop one hypothesis at a time
    for name, cond in (("(D2) fails", lambda v, T: min(abs(a) for a in v) <= 1),
                       ("(D3) fails", lambda v, T: True)):
        tot = ok = 0
        tries = 0
        while tot < 2000 and tries < 10 ** 6:
            tries += 1
            g = rng.randrange(4)
            T = tuple(rng.randint(-args.tmax, args.tmax) for _ in range(3))
            v = tuple(rng.choice((-1, 1)) * rng.randint(0 if name.startswith("(D2)") else 2, args.vmax) for _ in range(3))
            x = quiver_from(T, v, g)
            vv = column(x, g)
            if not (any(a > 0 for a in vv) and any(a < 0 for a in vv)):
                continue
            if name.startswith("(D2)") and not (cond(vv, T) and all(abs(O.entry(x, i, j)) < max(abs(O.entry(x, i, g)), abs(O.entry(x, j, g))) for i, j in itertools.combinations([u for u in range(4) if u != g], 2))):
                continue
            if name.startswith("(D3)") and (min(abs(a) for a in vv) < 2 or dominant(x, g)):
                continue
            tot += 1
            ok += (g not in O.exit_returns(x) and g in O.exit_returns(O.mutate(x, g)))
        print(f"   with {name} (other hypotheses kept): {tot} quivers, step at g a strict up-exit in {ok}")
    # Lemma 22.2 and Lemma 22.3(1)
    n = bad = badpf = 0
    for _ in range(args.n):
        g = rng.randrange(4)
        T = tuple(rng.randint(-args.tmax, args.tmax) for _ in range(3))
        v = tuple(rng.randint(-args.vmax, args.vmax) for _ in range(3))
        x = quiver_from(T, v, g)
        k = rng.choice([u for u in range(4) if u != g])
        vs = [u for u in range(4) if u != g]
        eps = 1 if O.entry(x, k, g) >= 0 else -1
        E = E_matrix(T, g, k, eps)
        pred = tuple(sum(E[i][j] * v[j] for j in range(3)) for i in range(3))
        y = O.mutate(x, k)
        n += 1
        bad += column(y, g) != pred
        a, b, c = vs
        kap = (O.entry(x, b, c), -O.entry(x, a, c), O.entry(x, a, b))
        badpf += abs(O.pfaffian(x)) != abs(sum(p * q for p, q in zip(v, kap)))
    print(f"Lemma 22.2: {n} random steps inside T, column differs from E v: {bad}; Lemma 22.3(1): |Pf| != |<v, kappa>|: {badpf}")
    # Lemma 22.3(2): Coxeter walks with positive mutated entries
    n = bad = 0
    for _ in range(args.n // 10):
        p_, q_, r_ = (rng.randint(0, 12) for _ in range(3))
        # vertices 1 (source), 2 (middle), 3 (sink); g = 0
        T = (p_, q_, r_)                                   # b12 = p, b13 = q, b23 = r
        C = p_ * p_ + q_ * q_ + r_ * r_ + p_ * q_ * r_
        M = [[int(i == j) for j in range(3)] for i in range(3)]
        cur = T
        order = (3, 2, 1)                                   # sink, then the new sink, then the last
        for k in order:
            E = E_matrix(cur, 0, k, 1)
            M = [[sum(E[i][l] * M[l][j] for l in range(3)) for j in range(3)] for i in range(3)]
            t = O.mutate(quiver_from(cur, (0, 0, 0), 0), k)
            cur = triangle(t, 0)
        n += 1
        bad += cur != T or charpoly3(M) != (1, 3 - C, 3 - C, 1)
    print(f"Lemma 22.3(2): {n} acyclic triangles, three sink steps: back to T with characteristic polynomial "
          f"(x + 1)(x^2 - (C - 2)x + 1) in all but {bad}")
    # Proposition 22.4: flat steps of mutation-cyclic triangles
    flat = Counter()
    for x_ in range(2, args.wmax + 1):
        for y_ in range(x_, args.wmax + 1):
            for z_ in range(y_, args.wmax + 1):
                if x_ * x_ + y_ * y_ + z_ * z_ - x_ * y_ * z_ > 4:
                    continue
                w = (x_, y_, z_)
                nf = sum(1 for i in range(3) if w[i] * w[(i + 1) % 3] == 2 * w[(i + 2) % 3])
                if nf >= 2:
                    flat[w] = nf
    print(f"Proposition 22.4: mutation-cyclic triangles with weights <= {args.wmax} and two or more flat steps: "
          f"{len(flat)}; all of the form (2, m, m): {all(w[0] == 2 and w[1] == w[2] for w in flat)}; "
          f"three flat steps only at {[w for w, c in flat.items() if c == 3]}")



# ----------------------------------------------------------------------------- step 3: the 6,990 classes and the open mirror pairs
def rank3_root(w):
    """Strict descent on an oriented triangle given by its weights read around the cycle (BBH Theorem 5.1):
    the step at the vertex between the edges x and y changes the third weight z to xy - z and reverses the
    cyclic order."""
    w = tuple(w)
    while True:
        for i in range(3):
            x, y, z = w[i], w[(i + 1) % 3], w[(i + 2) % 3]
            if x * y - z < z:
                w = (x, x * y - z, y)
                break
        else:
            return w


def cyclic_weights(T):
    """Weights read around the cycle if T = (b_ab, b_ac, b_bc) is an oriented 3-cycle, else None."""
    ab, ac, bc = T
    if ab > 0 and bc > 0 and ac < 0:            # a -> b -> c -> a
        return (ab, bc, -ac)
    if ab < 0 and bc < 0 and ac > 0:            # a -> c -> b -> a
        return (ac, -bc, -ab)
    return None


def disconnected_status(q):
    for g in range(4):
        if all(O.entry(q, g, u) == 0 for u in range(4) if u != g):
            cw = cyclic_weights(triangle(q, g))
            if cw is None or min(cw) < 2 or sum(x * x for x in cw) - cw[0] * cw[1] * cw[2] > 4:
                return "mutation-acyclic"
            r = rank3_root(cw)
            flat = any(r[i] * r[(i + 1) % 3] == 2 * r[(i + 2) % 3] for i in range(3))
            rev = r[::-1]
            return "rank 3: T ~ -T" if flat or rev in {r, r[1:] + r[:1], r[2:] + r[:2]} else "rank 3: T not ~ -T"
    return "mutation-acyclic"                   # two components on two vertices


def cmd_pairs(args):
    import n4_opposite_run as R
    plats = R.load_gz(args.plateaus)
    mirror = R.mirror_map(plats)
    cls = {r["i"]: r for r in load_gz(args.classify)}
    c2 = {}
    if os.path.exists(args.certify2):
        c2 = {r["i"]: r for r in load_gz(args.certify2)}
    acyc = [any(c["acyc"] for c in p["comps"]) for p in plats]

    def kind(i):
        r = cls[i]
        if r["disc"]:
            return "disconnected"
        if r["acyc"]:
            return "acyclic bottom"
        if r["markov"]:
            return "Markov triangle"
        return "cyclic, V' " + {"linear": "linear", "slow": "slow", "quadratic": "quadratic", "cap": "cap"}[growth_kind(r)]

    def cert(i):
        r = c2.get(i)
        return r is not None and r["status"] == "certified" and "kid" in r

    print(f"{len(cls)} classes without a finite core or a tube certificate (note 14)")
    print("kind | classes | of which certified by certify2 | census self-mirror | in census mirror pairs")
    tab = defaultdict(Counter)
    for i in cls:
        k = kind(i)
        tab[k]["classes"] += 1
        tab[k]["cert"] += cert(i)
        tab[k]["self"] += mirror[i] == i
        tab[k]["pair"] += mirror[i] != i
    for k in sorted(tab):
        t = tab[k]
        print(f"   {k:28s} {t['classes']:6d} {t['cert']:6d} {t['self']:6d} {t['pair']:6d}")
    # disconnected classes: rank 3
    dst = Counter()
    for i in cls:
        if cls[i]["disc"]:
            st_ = disconnected_status(tuple(plats[i]["comps"][0]["k"]))
            dst[(st_, "self-mirror" if mirror[i] == i else "mirror pair")] += 1
    print("disconnected classes by rank 3 (BBH Theorem 5.1):", dict(dst))
    # open mirror pairs
    op = Counter()
    for i in cls:
        j = mirror[i]
        if j is None or j == i or (j < i and j in cls):
            continue
        if acyc[i] or acyc[j]:
            continue
        k = kind(i)
        if k == "disconnected":
            how = "settled by rank 3" if disconnected_status(tuple(plats[i]["comps"][0]["k"])) == "rank 3: T not ~ -T" else "open"
        elif cert(i) and j in cls and cert(j):
            how = "certified by certify2" if c2[i]["kid"] == c2[j]["mkid"] and c2[i]["kid"] != c2[j]["kid"] else "CONTRADICTION"
        else:
            how = "open"
        op[(k, how)] += 1
    print(f"mirror pairs with no acyclic quiver in a bottom component and not certified by note 14: {sum(op.values())}")
    for k, v in sorted(op.items()):
        print(f"   {v:6d}  {k[0]} | {k[1]}")
    print(f"   still open: {sum(v for k, v in op.items() if k[1] == 'open')}")
    # classes: decided (certified, disconnected, or with an acyclic bottom quiver) and open
    dec = Counter()
    for i in cls:
        k = kind(i)
        if cert(i):
            dec["certified by certify2"] += 1
        elif k == "disconnected":
            dec["disconnected (rank 3)"] += 1
        elif k == "acyclic bottom":
            dec["acyclic bottom (arXiv 2610.36179)"] += 1
        else:
            dec["open: " + k] += 1
    print("the 6,990 classes after this note:")
    for k, v in sorted(dec.items()):
        print(f"   {v:6d}  {k}")
    print(f"   decided: {sum(v for k, v in dec.items() if not k.startswith('open'))}; "
          f"open: {sum(v for k, v in dec.items() if k.startswith('open'))}")



def cmd_verify2(args):
    """Checks of second-pass certificates: an exhaustive cut of V' lies in E and the families, its bottom is
    the certified bottom, and the allowed steps out of members Y(n), n = 3..10, land in E or a family."""
    recs = [r for r in load_gz(args.certify2) if r["status"] == "certified" and "kid" in r]
    random.Random(args.seed).shuffle(recs)
    tot = Counter()
    for r in recs[:args.classes]:
        rec, obj = certify2(r["i"], r["b"], tuple(r["x"]), budget=60.0, full=True)
        if rec["status"] != "certified":
            tot["not certified again"] += 1
            continue
        x, E, nodes, members = obj
        tot["classes"] += 1
        tot["same bottom as the run"] += rec.get("kid") == r["kid"]
        Lc = min(args.cut, 4 * rec["L"])
        lev, ok = ball(x, Lc, cap=args.cap)
        tot["cut complete"] += ok
        tot["quivers in the cuts"] += len(lev)
        tot["quivers of the cut outside E and the families"] += sum(1 for y in lev if y not in E and y not in members)
        if ok:
            bl = min(lev.values())
            tot["cut bottom = certified bottom"] += bl == rec["bK"] and min(y for y in lev if lev[y] == bl) == tuple(rec["kid"])
        for key, Y in nodes.items():
            fam = members.fams[key]
            for nn in range(3, 11):
                y = fam.get(nn)
                if O.level(y) > 10 ** 200:
                    break
                ey = O.exit_returns(y)
                for m in range(4):
                    z = O.mutate(y, m)
                    if m not in ey and m in O.exit_returns(z):
                        continue
                    c = O.canon(z)
                    tot["replayed allowed steps"] += 1
                    tot["replayed steps landing outside E and the families"] += c not in E and c not in members
    for k, v in tot.items():
        print(f"   {k}: {v}")



def cmd_sidesig(args):
    """The side-tube signature: digits of the largest tau found by certify2 before it gives up, for the
    connected cyclic classes that the second pass leaves open, against the largest tau of every note-14
    certificate."""
    import n4_opposite_run as R
    c2 = {r["i"]: r for r in load_gz(args.certify2)}
    cls = load_gz(args.classify)
    jobs = [(r["i"], r["b"], tuple(r["x"]), args.budget) for r in cls
            if not r["disc"] and not r["acyc"] and not r["markov"] and r["i"] in c2 and c2[r["i"]]["status"] != "certified"]
    old = Counter(len(str(max(t["taus"]))) for t in R.load_gz(args.tubes) if t["status"] == "certified")
    print(f"note 14 certificates by digits of the largest tau: {dict(sorted(old.items()))}")
    with Pool(args.procs) as pool:
        res = pool.map(_job2, jobs, chunksize=2)
    kinds = {r["i"]: growth_kind(r) for r in cls}
    tab = defaultdict(Counter)
    for r in res:
        if r["status"] == "certified":
            tab[kinds[r["i"]]]["certified on the rerun"] += 1
            continue
        d = r.get("maxtau_digits", 0)
        tab[kinds[r["i"]]]["largest tau above 15 digits" if d > 15 else "largest tau of at most 15 digits" if d else "no tau > 2 found"] += 1
    for k in sorted(tab):
        print(f"   V' {k}: {dict(tab[k])}")
    print(f"   digits of the largest tau at failure: {dict(sorted(Counter(r.get('maxtau_digits', 0) for r in res if r['status'] != 'certified').items()))}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("classify")
    s.add_argument("--tubes", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--out", default="n4_tube_classify.jsonl.gz")
    s.add_argument("--procs", type=int, default=6)
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--seed", type=int, default=1)
    s = sub.add_parser("shapes")
    s.add_argument("--tubes", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--out", default="n4_tube_shapes.jsonl.gz")
    s.add_argument("--classes", type=int, default=3000)
    s.add_argument("--procs", type=int, default=6)
    s.add_argument("--seed", type=int, default=72)
    s.add_argument("--summary", action="store_true", help="only summarise an existing --out file")
    s = sub.add_parser("markov")
    s.add_argument("--random", type=int, default=20000)
    s.add_argument("--vmax", type=int, default=40)
    s.add_argument("--zmax", type=int, default=40)
    s.add_argument("--nmax", type=int, default=40)
    s.add_argument("--levels", type=int, nargs="*", default=[25, 50, 100, 200])
    s.add_argument("--seed", type=int, default=6)
    s = sub.add_parser("side")
    s.add_argument("--cut", type=int, default=12)
    s.add_argument("--kmax", type=int, default=25)
    s.add_argument("--depth", type=int, default=12)
    s = sub.add_parser("certify2")
    s.add_argument("--classify", default="n4_tube_classify.jsonl.gz")
    s.add_argument("--tubes", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--out", default="n4_tube_certify2.jsonl.gz")
    s.add_argument("--procs", type=int, default=6)
    s.add_argument("--budget", type=float, default=20.0)
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--seed", type=int, default=1)
    s = sub.add_parser("lemma")
    s.add_argument("--n", type=int, default=20000)
    s.add_argument("--tmax", type=int, default=12)
    s.add_argument("--vmax", type=int, default=60)
    s.add_argument("--wmax", type=int, default=200)
    s.add_argument("--seed", type=int, default=73)
    s = sub.add_parser("pairs")
    s.add_argument("--classify", default="n4_tube_classify.jsonl.gz")
    s.add_argument("--certify2", default="n4_tube_certify2.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s = sub.add_parser("verify2")
    s.add_argument("--certify2", default="n4_tube_certify2.jsonl.gz")
    s.add_argument("--classes", type=int, default=200)
    s.add_argument("--cut", type=int, default=20000)
    s.add_argument("--cap", type=int, default=60000)
    s.add_argument("--seed", type=int, default=9)
    s = sub.add_parser("sidesig")
    s.add_argument("--certify2", default="n4_tube_certify2.jsonl.gz")
    s.add_argument("--classify", default="n4_tube_classify.jsonl.gz")
    s.add_argument("--tubes", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--budget", type=float, default=12.0)
    s.add_argument("--procs", type=int, default=6)
    args = ap.parse_args()
    {"classify": cmd_classify, "shapes": cmd_shapes, "markov": cmd_markov, "side": cmd_side,
     "certify2": cmd_certify2, "lemma": cmd_lemma, "pairs": cmd_pairs, "verify2": cmd_verify2,
     "sidesig": cmd_sidesig}[args.cmd](args)


if __name__ == "__main__":
    main()
