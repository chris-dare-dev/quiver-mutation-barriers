"""Note 14 drivers for n4_opposite.py.  Run from experiments/ with python -I.

  cores      the core of every census class (forks and pre-forks as exits), in parallel
  plateaus   the bottom components of every census class and their mirror images
  mirror     mirror pairs certified distinct; self-mirror classes; barriers and mirror joins
  summary    separation of the classes without a finite core; balanced edges; total properness
  corecheck  deaths recomputed in the core graph; the map x -> -x on the cores of self-mirror classes
  pockets    every pocket of every class with a finite core
  fn         the Fomin-Neville cosquare test on the classes with a certified totally proper ordering
  extremes   G_k for a range of k, and the census extremes
  lemmas     numerical checks of the quoted lemmas on forks and pre-forks
  walks      the core recomputed from the end of random mutation walks
  tubeshapes the shapes of the infinite families in classes without a finite core
  combined   finite cores and the tube certificates of n4_opposite_tubes.py together
"""
import argparse
import gzip
import itertools
import json
import os
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n4_opposite as O


def cmd_cores(args):
    t0 = time.time()
    jobs = []
    for fn, B, r in O.census_rows():
        jobs.append((len(jobs), r["bottom"], O.from_matrix(r["bottom_quiver"]), args.cap, args.level_cap))
    print(f"{len(jobs)} census classes read ({time.time() - t0:.0f}s)", flush=True)
    stats = Counter()
    with Pool(args.procs) as pool, gzip.open(args.out, "wt") as out:
        for rec in pool.imap(O.core_record, jobs, chunksize=500):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            stats[(rec["b"], rec["ex"])] += 1
            if rec["i"] % 50000 == 0:
                print(f"  {rec['i']} ({time.time() - t0:.0f}s)", flush=True)
    for b in sorted({k[0] for k in stats}):
        print(f"  bottom {b}: core found {stats[(b, True)]}, search stopped at a cap {stats[(b, False)]}")
    print(f"total: core found {sum(v for k, v in stats.items() if k[1])}, search stopped at a cap "
          f"{sum(v for k, v in stats.items() if not k[1])} (caps: {args.cap} quivers, level {args.level_cap}) "
          f"({time.time() - t0:.0f}s)")


def cmd_plateaus(args):
    t0 = time.time()
    jobs = [(i, B, r) for i, (fn, B, r) in enumerate(O.census_rows())]
    n = 0
    with Pool(args.procs) as pool, gzip.open(args.out, "wt") as out:
        for rec in pool.imap(O.plateau_record, jobs, chunksize=500):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            n += 1
    print(f"{n} census classes, bottom plateaus written to {args.out} ({time.time() - t0:.0f}s)")


def load_gz(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def salvage(path):
    """The complete records of an interrupted run (a truncated .gz file), by class index."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    try:
        with gzip.open(path, "rt") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    break
                out[rec["i"]] = rec
    except EOFError:
        pass
    return out


def cmd_mirror(args):
    """The census under B -> -B: which mirror pairs of classes are certified distinct, by the core
    (forks and pre-forks) or by an acyclic quiver (Caldero-Keller); the self-mirror classes; the barrier
    between bottom components and mirror joins."""
    t0 = time.time()
    cores = load_gz(args.cores)
    plats = load_gz(args.plateaus)
    assert len(cores) == len(plats) and all(c["i"] == a for a, c in enumerate(cores))
    N = len(cores)
    owner = {}
    clash = 0
    for p in plats:
        for c in p["comps"]:
            k = tuple(c["k"])
            if owner.setdefault(k, p["i"]) != p["i"]:
                clash += 1
    mirror = []
    incons = 0
    for p in plats:
        js = {owner.get(tuple(c["mk"])) for c in p["comps"]}
        if len(js) != 1 or None in js:
            incons += 1
        mirror.append(next(iter(js)))
    selfm = [i for i in range(N) if mirror[i] == i]
    pairs = [(i, mirror[i]) for i in range(N) if mirror[i] is not None and i < mirror[i]]
    print(f"{N} census classes, {len(owner)} bottom plateaus (plateau in two classes: {clash}; classes whose "
          f"bottom plateaus have no single mirror class: {incons})")
    print(f"census self-mirror classes: {len(selfm)}; mirror pairs of distinct census classes: {len(pairs)} "
          f"({time.time() - t0:.0f}s)")

    # ---- cores
    fin = [c for c in cores if c["ex"]]
    byvid = defaultdict(list)
    for c in fin:
        byvid[tuple(c["vid"])].append(c["i"])
    hidden = [v for v in byvid.values() if len(v) > 1]
    print(f"classes with a finite core: {len(fin)} of {N}; distinct cores: {len(byvid)}; "
          f"cores shared by two or more census classes (hidden joins): {len(hidden)}")
    for v in hidden[:10]:
        print("   shared core:", [(i, cores[i]["b"], cores[i]["q"]) for i in v])
    maxtop = max(c["top"] for c in fin)
    maxn = max(c["n"] for c in fin)
    print(f"largest core: {maxn} quivers; highest level in a core: {maxtop}; "
          f"cores containing an acyclic quiver: {sum(1 for c in fin if c['acyc'])}; "
          f"census bottom quiver outside the core: {sum(1 for c in fin if not c['qin'])}")
    sizes = Counter(c["n"] for c in fin)
    print("  core sizes (size: classes):", dict(sorted(sizes.items())[:40]))
    unres = [c for c in cores if not c["ex"]]
    sep = Counter()
    for c in unres:
        sep["bottom quiver certainly in the core" if c["in"] else
            ("a core quiver above every finite core" if c["hc"] > maxtop else "not separated from the finite cores")] += 1
    print(f"classes whose search stopped at a cap: {len(unres)}; separated from every finite-core class by: {dict(sep)}")

    # ---- acyclic classes
    acyc = [any(c["acyc"] for c in p["comps"]) for p in plats]
    print(f"classes with an acyclic quiver in a bottom plateau: {sum(acyc)}")

    # ---- mirror pairs
    tab = defaultdict(Counter)
    bad = Counter()
    for i, j in pairs:
        b = cores[i]["b"]
        ci, cj = cores[i], cores[j]
        by_core = False
        if ci["ex"] != cj["ex"]:
            bad["core found for one class of a pair only"] += 1
        if ci["ex"] and cj["ex"]:
            if ci["vid"] == cj["vid"]:
                bad["mirror pair with the same core: the two classes are one class"] += 1
            else:
                by_core = True
            if ci["mvid"] != cj["vid"]:
                bad["mirror core is not the core of the mirror class"] += 1
        by_ck = acyc[i] or acyc[j]
        if acyc[i] != acyc[j]:
            bad["acyclic quiver in one class of a pair only"] += 1
        tab[b]["pairs"] += 1
        tab[b]["core"] += by_core
        tab[b]["acyclic"] += by_ck
        tab[b]["either"] += (by_core or by_ck)
        tab[b]["both"] += (by_core and by_ck)
    print("mirror pairs certified distinct, by bottom: pairs / by the core / by an acyclic quiver / by either / open")
    tot = Counter()
    for b in sorted(tab):
        t = tab[b]
        tot.update(t)
        print(f"  bottom {b}: {t['pairs']} / {t['core']} / {t['acyclic']} / {t['either']} / {t['pairs'] - t['either']}")
    print(f"  all: {tot['pairs']} / {tot['core']} / {tot['acyclic']} / {tot['either']} / {tot['pairs'] - tot['either']}")
    print(f"  consistency failures: {dict(bad)}")

    # ---- self-mirror classes
    st = Counter()
    for i in selfm:
        c, p = cores[i], plats[i]
        if c["ex"]:
            st["core found"] += 1
            if c["mvid"] != c["vid"]:
                st["core found but not equal to its mirror (inconsistent)"] += 1
        keys = {tuple(x["k"]) for x in p["comps"]}
        selfc = [x for x in p["comps"] if x["k"] == x["mk"]]
        swapped = [x for x in p["comps"] if x["k"] != x["mk"]]
        if selfc and not swapped:
            kind = "every bottom component is its own mirror"
        elif selfc and swapped:
            kind = "some bottom components are their own mirror, others are exchanged"
        else:
            kind = "the bottom components are exchanged in pairs"
        st[kind] += 1
        if selfc:
            st["... a bottom component that is its own mirror contains a quiver isomorphic to its opposite"
               if any(x["fix"] for x in selfc) else
               "... no quiver of a self-mirror bottom component is isomorphic to its opposite"] += 1
    print("census self-mirror classes:")
    for k in sorted(st):
        print(f"   {k}: {st[k]}")

    # ---- the barrier between bottom components and mirror joins
    print("classes with several bottom components: is the last death the death of a component whose mirror "
          "is another bottom component of the class?")
    print("  bottom: classes / last death at a mirror pair / largest death/b^2 at a mirror pair / elsewhere")
    worst = defaultdict(list)
    for p in plats:
        dead = [x for x in p["comps"] if x["d"] is not None]
        if not dead:
            continue
        b = p["b"]
        keys = {tuple(x["k"]) for x in p["comps"]}
        x = max(dead, key=lambda x: x["d"])
        is_mirror = x["mk"] != x["k"] and tuple(x["mk"]) in keys
        worst[b].append((x["d"], is_mirror, p["i"]))
    for b in sorted(worst):
        w = worst[b]
        m = [d for d, im, i in w if im]
        o = [d for d, im, i in w if not im]
        top = sorted(w, reverse=True)[:10]
        print(f"  {b}: {len(w)} / {len(m)} / {max(m, default=0) / b / b:.3f} / {max(o, default=0) / b / b:.3f}"
              f"   ten largest deaths: {[(d, 'mirror' if im else 'other') for d, im, i in top]}")
    print(f"({time.time() - t0:.0f}s)")


def mirror_map(plats):
    owner = {}
    for p in plats:
        for c in p["comps"]:
            owner.setdefault(tuple(c["k"]), p["i"])
    return [owner.get(tuple(p["comps"][0]["mk"])) for p in plats]


def cmd_fn(args):
    """The Fomin-Neville invariant on the census: for every class with a certified totally proper cyclic
    ordering, is the cosquare of its unipotent companion conjugate to its transpose in GL_4(Z)?  (Necessary
    for the class to equal its mirror; tested through ideal classes in the maximal order.)"""
    t0 = time.time()
    pool = Pool(args.procs)                             # before the data is loaded: small workers
    done = salvage(args.resume)
    cores = load_gz(args.cores)
    plats = load_gz(args.plateaus)
    mirror = mirror_map(plats)
    jobs = []
    for c, p in zip(cores, plats):
        if mirror[c["i"]] < c["i"]:
            continue                      # one class of each mirror pair: the mirror has the transposed cosquare
        ac = [x for x in p["comps"] if x["acyc"]]
        if ac:
            jobs.append((c["i"], "acyclic", ac[0]["k"]))
        elif c["ex"] and c["pre"] == 0 and c["zero"] == 0 and c["vortex"] == 0:
            jobs.append((c["i"], "complete", c["vid"]))
    if args.limit:
        import random
        random.Random(1).shuffle(jobs)
        jobs = jobs[:args.limit]
    print(f"classes with a certified totally proper ordering, one of each mirror pair: {len(jobs)} "
          f"({Counter(j[1] for j in jobs)})", flush=True)
    res = {}
    with gzip.open(args.out, "wt") as out:
        for j in jobs:
            if j[0] in done:
                res[j[0]] = done[j[0]]
                out.write(json.dumps(done[j[0]], separators=(",", ":")) + "\n")
        print(f"  taken from {args.resume}: {len(res)}", flush=True)
        todo = [j for j in jobs if j[0] not in res]
        for rec in pool.imap_unordered(O.fn_record, todo, chunksize=20):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            res[rec["i"]] = rec
            if len(res) % 10000 == 0:
                print(f"  {len(res)} ({time.time() - t0:.0f}s)", flush=True)
    pool.close()
    tab = defaultdict(Counter)
    for i, rec in res.items():
        kind = rec["kind"]
        selfm = mirror[i] == i
        key = (kind, "self-mirror class" if selfm else "class of a mirror pair")
        if "error" in rec:
            tab[key]["error: " + rec["error"]] += 1
        elif not rec["irreducible"]:
            tab[key]["Alexander polynomial reducible: not tested"] += 1
        elif not rec["same"]:
            tab[key]["cosquare not conjugate to its transpose: certified different from its mirror"] += 1
        elif rec["index"] == 1:
            tab[key]["same ideal class, Z[x] maximal: cosquare conjugate to its transpose"] += 1
        else:
            tab[key]["same ideal class in the maximal order, Z[x] not maximal: undecided"] += 1
    for key in sorted(tab):
        print(f"  {key[0]}, {key[1]}: {sum(tab[key].values())}")
        for k, v in sorted(tab[key].items()):
            print(f"      {k}: {v}")
    print(f"({time.time() - t0:.0f}s)")


def cmd_corecheck(args):
    """Finite-core classes: the deaths of the bottom components recomputed in the core graph against the
    census; the action of x -> -x on the cores of self-mirror classes."""
    t0 = time.time()
    cores = load_gz(args.cores)
    plats = load_gz(args.plateaus)
    mirror = mirror_map(plats)
    jobs = []
    for c, p in zip(cores, plats):
        if not c["ex"]:
            continue
        selfm = mirror[c["i"]] == c["i"]
        deaths = [x["d"] for x in p["comps"] if x["d"] is not None]
        if selfm or deaths:
            jobs.append((c["i"], c["vid"], deaths, selfm))
    print(f"finite-core classes that are self-mirror or have several bottom components: {len(jobs)}", flush=True)
    st = Counter()
    act = Counter()
    worst = []
    ex = []
    with Pool(args.procs) as pool:
        for rec in pool.imap_unordered(O.corecheck_record, jobs, chunksize=200):
            b = cores[rec["i"]]["b"]
            if rec["census_deaths"]:
                st["classes with several bottom components"] += 1
                if rec["lo"] != b:
                    st["   lowest level of the core differs from the census bottom"] += 1
                elif rec["core_deaths"] == rec["census_deaths"]:
                    st["   deaths in the core graph equal the census deaths"] += 1
                else:
                    st["   deaths differ"] += 1
                    if len(ex) < 8:
                        ex.append((rec["i"], b, cores[rec["i"]]["q"], rec["core_deaths"], rec["census_deaths"]))
            if "fix" in rec:
                kind = ("contains a quiver isomorphic to its opposite" if rec["fix"] else
                        ("no such quiver, but an edge x - (-x)" if rec["inv"] else "neither"))
                act[kind] += 1
                act[f"core size {'odd' if rec['n'] % 2 else 'even'}, {kind}"] += 1
                if rec["mirror_join"] is not None and rec["mirror_join"] > b:
                    act["bottom quiver joined to its mirror only above the bottom"] += 1
                    worst.append((rec["mirror_join"] / b / b, b, rec["mirror_join"], rec["fix"], rec["fixlo"], rec["i"]))
    for k in sorted(st):
        print(f"  {k}: {st[k]}")
    for e in ex:
        print("     differ:", e)
    print("self-mirror classes with a finite core: the map x -> -x on the core")
    for k in sorted(act):
        print(f"  {k}: {act[k]}")
    worst.sort(reverse=True)
    print("  largest mirror joins (join/b^2, b, join, quivers isomorphic to their opposite, their lowest level, class):")
    for w in worst[:12]:
        print("    ", (round(w[0], 3),) + w[1:], cores[w[5]]["q"])
    print(f"({time.time() - t0:.0f}s)")


def cmd_pockets(args):
    """Every pocket of every class with a finite core: the persistence pairs of the core together with the
    roots of its far regions.  Compared with the census deaths of the bottom components."""
    t0 = time.time()
    pool = Pool(args.procs)                              # before the data is loaded: small workers
    done = salvage(args.resume)
    cores = load_gz(args.cores)
    plats = load_gz(args.plateaus)
    jobs = [(c["i"], c["vid"]) for c in cores if c["ex"]]
    print(f"classes with a finite core: {len(jobs)}; taken from an interrupted run: {len(done)}", flush=True)
    by_birth = defaultdict(lambda: [0, 0.0, None])          # birth -> [pairs, largest death/birth^2, example]
    by_birth_forkonly = defaultdict(lambda: [0, 0.0, None])
    st = Counter()
    worst = []
    import itertools
    todo = [j for j in jobs if j[0] not in done]
    with gzip.open(args.out, "wt") as out:
        for rec in itertools.chain(done.values(), pool.imap_unordered(O.pockets_record, todo, chunksize=500)):
            out.write(json.dumps(rec, separators=(",", ":")) + "\n")
            i = rec["i"]
            b = cores[i]["b"]
            st["classes"] += 1
            st["classes whose far regions are all rooted at forks"] += rec["npre"] == 0
            st["pockets"] += len(rec["pairs"])
            st["roots of far regions"] += rec["nroots"]
            census = sorted(x["d"] for x in plats[i]["comps"] if x["d"] is not None)
            mine = sorted(d for bb, d in rec["pairs"] if bb == b)
            if rec["lo"] != b:
                st["lowest level differs from the census bottom"] += 1
            elif census == mine:
                st["deaths of the bottom components equal the census"] += 1
            else:
                st["deaths of the bottom components differ from the census"] += 1
                if st["deaths of the bottom components differ from the census"] <= 5:
                    print("   differ:", i, b, cores[i]["q"], mine, census, flush=True)
            for bb, d in rec["pairs"]:
                for tab in ((by_birth, by_birth_forkonly) if rec["npre"] == 0 else (by_birth,)):
                    e = tab[bb]
                    e[0] += 1
                    if d / bb / bb > e[1]:
                        e[1] = d / bb / bb
                        e[2] = (d, i)
                if bb >= 2 and d > 2 * bb * bb:
                    worst.append((d / bb / bb, bb, d, i, rec["npre"]))
    for k in sorted(st):
        print(f"  {k}: {st[k]}")
    for name, tab in (("all finite-core classes", by_birth), ("classes whose far regions are all rooted at forks", by_birth_forkonly)):
        print(f"pockets by birth level, {name}: birth: pockets, largest death/birth^2 (death, class)")
        for bb in sorted(tab):
            if bb <= 40 or tab[bb][1] > 1.0:
                print(f"   {bb}: {tab[bb][0]}, {tab[bb][1]:.3f} {tab[bb][2]}")
        births = [bb for bb in tab if bb >= 2]
        print(f"   births from {min(births)} to {max(births)}; largest death/birth^2 over births >= 2: "
              f"{max(tab[bb][1] for bb in births):.3f}; over births >= 10: "
              f"{max((tab[bb][1] for bb in births if bb >= 10), default=0):.3f}")
    print(f"pockets with death > 2 birth^2 (birth >= 2): {len(worst)}")
    for w in sorted(worst, reverse=True)[:20]:
        print("    ", (round(w[0], 3),) + w[1:], cores[w[3]]["q"])
    print(f"({time.time() - t0:.0f}s)")


def cmd_summary(args):
    t0 = time.time()
    pool = Pool(args.procs)
    cores = load_gz(args.cores)
    plats = load_gz(args.plateaus)
    fin = [c for c in cores if c["ex"]]
    maxtop = max(c["top"] for c in fin)
    maxn = max(c["n"] for c in fin)
    # classes without a finite core that the two cheap arguments do not separate from the finite cores
    res = Counter()
    for u in cores:
        if u["ex"] or u["in"] or u["hc"] > maxtop:
            continue
        lev, adj, ex = O.no_exit_closure(tuple(u["q"]), cap=800, level_cap=10 ** 6)
        ys = [y for y in lev if O.certainly_in_core(y)]
        if not ys:
            res["no quiver certainly outside the far regions found"] += 1
            continue
        y = min(ys, key=lambda y: lev[y])
        lev2, adj2, ex2 = O.no_exit_closure(y, cap=800, level_cap=10 ** 6)
        res["closure of a quiver outside the far regions larger or higher than every finite core"
            if (not ex2 or len(lev2) > maxn or max(lev2.values()) > maxtop) else "finite closure (not separated)"] += 1
    print(f"classes without a finite core left over by the two direct arguments: {dict(res)}")
    # balanced edges
    jobs = [(c["i"], c["vid"]) for c in fin if c["ncert"] == 0]
    bal = {}
    for idx, n, size in pool.imap_unordered(O.balanced_record, jobs, chunksize=500):
        if n:
            bal[idx] = size
    pool.close()
    near = [c for c in fin if c["i"] not in bal]
    print(f"finite cores: {len(fin)}; with a quiver that passes the direct test for lying in no far region: "
          f"{sum(1 for c in fin if c['ncert'] > 0)}; of the other {len(jobs)}, cores with a balanced edge: {len(bal)} "
          f"(sizes {dict(Counter(bal.values()))})")
    print(f"cores certified to lie in no far region: {len(near)}; of these, far regions all rooted at forks: "
          f"{sum(1 for c in near if c['pre'] == 0)}")
    print(f"core of one quiver: {sum(1 for c in fin if c['n'] == 1)}; cores reaching above level 192: "
          f"{sum(1 for c in fin if c['top'] > 192)}; above 512: {sum(1 for c in fin if c['top'] > 512)}; highest: {maxtop}")
    # cores of one quiver: how many of its four mutations are strict up-exit steps
    c4 = Counter()
    selfop = forks4 = 0
    for c in fin:
        if c["n"] != 1:
            continue
        x = tuple(c["vid"])
        ex_x = O.exit_returns(x)
        n = sum(1 for m in range(4) if m not in ex_x and m in O.exit_returns(O.mutate(x, m)))
        c4[n] += 1
        if n == 4:
            selfop += c["vid"] == c["mvid"]
            forks4 += all(O.fork_return(O.mutate(x, m)) == m for m in range(4))
    print(f"cores of one quiver, by the number of mutations that are strict up-exit steps: {dict(sorted(c4.items()))}; "
          f"with four: all four are forks in {forks4}, the quiver is isomorphic to its opposite in {selfop}")
    # total properness
    acyc = [any(x["acyc"] for x in p["comps"]) for p in plats]
    tpb = [bool(c["ex"] and c["pre"] == 0 and c["zero"] == 0 and c["vortex"] == 0) for c in cores]
    print(f"classes with an acyclic quiver in a bottom plateau: {sum(acyc)} (of these without a finite core: "
          f"{sum(1 for c in cores if not c['ex'] and acyc[c['i']])})")
    print(f"finite cores, complete and vortex-free, all exits forks: {sum(tpb)}; either: "
          f"{sum(1 for a, b in zip(acyc, tpb) if a or b)}; both: {sum(1 for a, b in zip(acyc, tpb) if a and b)}")
    print(f"finite cores containing a vortex: {sum(1 for c in fin if c['vortex'])}")
    print(f"({time.time() - t0:.0f}s)")


def cmd_extremes(args):
    def Gk(k):
        return O.from_matrix([[0, k, -k, -k], [-k, 0, 0, k], [k, 0, 0, -(k - 1)], [k, -k, k - 1, 0]])
    ok = 0
    ks = range(args.kmin, args.kmax + 1)
    for k in ks:
        K, lev, adj, ex = O.core(Gk(k))
        levels, g, roots, npre = O.extended_core(Gk(k))
        ok += (ex and sorted(K.values()) == [k, k, k, k * k - k, k * k - k, k * k, k * k] and len(roots) == 12
               and npre == 8 and O.persistence_pairs(levels, g) == [(k, k * k - k), (k, k * k - k)]
               and O.canon(O.neg(Gk(k))) in K)
    print(f"G_k, k = {args.kmin}..{args.kmax}: core of 7 quivers at levels k, k, k, k^2-k, k^2-k, k^2, k^2 containing "
          f"-G_k; 12 roots of far regions (8 pre-forks); pockets (k, k^2-k) twice and no other: {ok} of {len(ks)}")
    print("G_k: proper cyclic orderings and proper mutations to a COQ that is not proper (None: none found among 3000 COQs)")
    for k in (3, 4, 5, 8, 12):
        print(f"   k = {k}: {O.proper_orderings(Gk(k))} {O.not_totally_proper(Gk(k))}")
    print("the bottom component with the largest death at each bottom:")
    best = {}
    for fn, B, r in O.census_rows():
        for p in r["pairs"]:
            if p["birth"] == r["bottom"] and p["death"] > best.get(r["bottom"], (0,))[0]:
                best[r["bottom"]] = (p["death"], r["bottom_quiver"])
    for b in sorted(best):
        d, q = best[b]
        t = O.from_matrix(q)
        K, lev, adj, ex = O.core(t, cap=800, level_cap=10 ** 6)
        print(f"   bottom {b}: death {d}, {q}: " + (f"core of {len(K)} quivers up to level {max(K.values())}" if ex
              else "no finite core within the caps") + f"; proper orderings {len(O.proper_orderings(t))}, "
              f"non-proper COQ after {O.not_totally_proper(t)}")


def _plateau_key(q):
    return min(O.plateau(tuple(q)))


def cmd_combined(args):
    """Finite cores and tube certificates together: mirror pairs certified, classes pairwise distinct,
    and a check of every tube certificate's bottom against the census bottom components."""
    t0 = time.time()
    pool = Pool(args.procs)
    cores = load_gz(args.cores)
    plats = load_gz(args.plateaus)
    tubes = {t["i"]: t for t in load_gz(args.tubes)}
    mirror = mirror_map(plats)
    cert = {i: t for i, t in tubes.items() if t["status"] == "certified" and t.get("kid") is not None}
    print(f"classes without a finite core: {len(tubes)}; with a tube certificate and a bottom of the core: {len(cert)}")
    # the bottom of the core against the census: kid lies in a bottom component of its class, mkid in the mirror class
    idx = sorted(cert)
    keys = pool.map(_plateau_key, [cert[i]["kid"] for i in idx], chunksize=2000)
    mkeys = pool.map(_plateau_key, [cert[i]["mkid"] for i in idx], chunksize=2000)
    pool.close()
    bad = Counter()
    st = Counter()
    for i, k, mk in zip(idx, keys, mkeys):
        own = {tuple(c["k"]) for c in plats[i]["comps"]}
        mown = {tuple(c["k"]) for c in plats[mirror[i]]["comps"]}
        if (cert[i]["kid"] == cert[i]["mkid"]) != (mirror[i] == i):
            bad["kid == mkid disagrees with the census mirror map"] += 1
        if O.level(tuple(cert[i]["kid"])) != cores[i]["b"]:
            # the census bottom component lies in a far region; the core starts higher
            st["bottom of the core above the census bottom"] += 1
            if cores[i]["in"]:
                bad["core above the census bottom although the bottom quiver is certainly in no far region"] += 1
            continue
        st["bottom of the core at the census bottom"] += 1
        if k not in own:
            bad["kid outside the bottom components of its class"] += 1
        if mk not in mown:
            bad["mkid outside the bottom components of the mirror class"] += 1
    print(f"tube certificates checked against the census: {len(idx)}; {dict(st)}; failures: {dict(bad)}")
    ids = Counter(tuple(t["kid"]) for t in cert.values())
    print(f"bottoms of cores shared by two certified classes: {sum(1 for v in ids.values() if v > 1)}")
    acyc = [any(x["acyc"] for x in p["comps"]) for p in plats]
    known = [c["ex"] or c["i"] in cert for c in cores]
    tab = defaultdict(Counter)
    for i in range(len(cores)):
        b = cores[i]["b"]
        tab[b]["classes"] += 1
        tab[b]["finite core"] += cores[i]["ex"]
        tab[b]["tube certificate"] += i in cert
        j = mirror[i]
        if j == i:
            tab[b]["self-mirror"] += 1
            tab[b]["self-mirror, core known"] += known[i]
        elif i < j:
            tab[b]["pairs"] += 1
            by_core = (cores[i]["ex"] and cores[j]["ex"]) or (i in cert and j in cert)
            tab[b]["pairs by a core"] += by_core
            tab[b]["pairs by either"] += by_core or acyc[i] or acyc[j]
    print("bottom: classes / finite core / tube certificate / neither ; mirror pairs / certified by cores / "
          "by cores or an acyclic quiver / open ; self-mirror classes / core known")
    tot = Counter()
    for b in sorted(tab):
        t = tab[b]
        tot.update(t)
        print(f"  {b}: {t['classes']} / {t['finite core']} / {t['tube certificate']} / "
              f"{t['classes'] - t['finite core'] - t['tube certificate']} ; {t['pairs']} / {t['pairs by a core']} / "
              f"{t['pairs by either']} / {t['pairs'] - t['pairs by either']} ; {t['self-mirror']} / {t['self-mirror, core known']}")
    t = tot
    print(f"  all: {t['classes']} / {t['finite core']} / {t['tube certificate']} / "
          f"{t['classes'] - t['finite core'] - t['tube certificate']} ; {t['pairs']} / {t['pairs by a core']} / "
          f"{t['pairs by either']} / {t['pairs'] - t['pairs by either']} ; {t['self-mirror']} / {t['self-mirror, core known']}")
    # the census extremes
    best = {}
    for p in plats:
        for c in p["comps"]:
            if c["d"] is not None and c["d"] > best.get(p["b"], (0,))[0]:
                best[p["b"]] = (c["d"], p["i"])
    print("the class with the largest death of a bottom component, by bottom:")
    for b in sorted(best):
        d, i = best[b]
        how = "finite core" if cores[i]["ex"] else (f"tube certificate ({cert[i].get('nodes', '?')} families)" if i in cert
                                                    else tubes[i]["status"])
        print(f"   bottom {b}: death {d}, class {i}: {how}")
    print(f"({time.time() - t0:.0f}s)")


def cmd_tubeshapes(args):
    """Classes without a finite core: the shape of the quivers found high up in the closure V'.
    For each such quiver, the lightest of its four triangles, as a sorted triple of weights."""
    import random
    rng = random.Random(args.seed)
    cores = load_gz(args.cores)
    unres = [c for c in cores if not c["ex"]]
    st = Counter()
    for c in rng.sample(unres, args.classes):
        lev, adj, ex = O.no_exit_closure(tuple(c["q"]), cap=args.cap)
        hi = [x for x in lev if lev[x] > args.high]
        if not hi:
            # slow growth: take the highest tenth
            cut = sorted(lev.values())[-max(1, len(lev) // 10)]
            hi = [x for x in lev if lev[x] >= cut]
        tris = set()
        for x in hi:
            tris.add(min(tuple(sorted(abs(O.entry(x, a, b)) for a, b in itertools.combinations([i for i in range(4) if i != v], 2)))
                         for v in range(4)))
        def shape(t):
            if t[0] >= 2:
                return "D"
            if t[:2] == (0, 0):
                return "C"
            if t[:2] == (0, 1) or (t[0] == 1 and t[1] == t[2] and t[1] >= 2):
                return "A"
            if t[:2] == (1, 1) or (t[0] == 1 and t[2] == t[1] + 1):
                return "B"
            return "?"
        shapes = {shape(t) for t in tris}
        if shapes == {"D"}:
            kind = ("no light pair; a cyclic triangle (2, m, m) in every quiver" if all(
                any(_is_2mm(x, v) for v in range(4)) for x in hi) else "no light pair; other")
        elif shapes == {"A"}:
            kind = "lightest triangles (0, 1, a) and (1, a, a)"
        elif shapes == {"B"}:
            kind = "lightest triangles (1, 1, a), (1, 1, a + 1) and (1, a, a + 1)"
        elif shapes == {"C"}:
            kind = "lightest triangle (0, 0, a)"
        elif "?" in shapes:
            kind = "other"
        else:
            kind = "several of these shapes"
        st[kind] += 1
    print(f"{args.classes} classes without a finite core, closure searched to {args.cap} quivers:")
    for k, v in st.most_common():
        print(f"   {k}: {v}")


def _is_2mm(x, v):
    a, b, c = [i for i in range(4) if i != v]
    e = (O.entry(x, a, b), O.entry(x, b, c), O.entry(x, c, a))
    if not (all(t > 0 for t in e) or all(t < 0 for t in e)):
        return False
    w = sorted(abs(t) for t in e)
    return w[0] == 2 and w[1] == w[2]


def cmd_walks(args):
    """The core is the same from every quiver of the class: random mutation walks out of classes with a
    finite core, then the core recomputed from the end of the walk."""
    import random
    rng = random.Random(args.seed)
    cores = load_gz(args.cores)
    fin = [c for c in cores if c["ex"]]
    st = Counter()
    longest = 0
    for c in rng.sample(fin, args.classes):
        for _ in range(args.walks):
            x = tuple(c["q"])
            last = None
            steps = 0
            for _ in range(args.length):
                m = rng.choice([v for v in range(4) if v != last])
                y = O.mutate(x, m)
                if O.level(y) > 10 ** args.digits:
                    break
                x, last, steps = y, m, steps + 1
            K, lev, adj, ex = O.core(x, cap=20000)
            st["walks"] += 1
            longest = max(longest, O.level(x))
            if not ex:
                st["search from the end of the walk did not stop"] += 1
            elif list(min(K)) == c["vid"] and len(K) == c["n"]:
                st["same core"] += 1
            else:
                st["different core"] += 1
            st["end of the walk outside the core"] += canon_not_in(K, x) if ex else 0
    print(f"{dict(st)}; highest level at the end of a walk: about 10^{len(str(longest)) - 1}")


def canon_not_in(K, x):
    return O.canon(x) not in K


def cmd_lemmas(args):
    """Numerical checks of the quoted lemmas against this implementation of forks and pre-forks:
    Ervin arXiv 2306.07502, Lemma 2.7 (forks), Lemma 4.6 (pre-forks), uniqueness of the return vertex,
    and the bridge property of Lemma 2.8 and Corollary 4.25 inside a ball."""
    import random
    rng = random.Random(args.seed)
    rows = [r for fn, B, r in O.census_rows()]
    starts = rng.sample(rows, args.classes)
    exits = {}                                    # labelled quiver -> return vertex
    seen = 0
    multi = 0
    for r in starts:
        t = O.from_matrix(r["bottom_quiver"])
        for _ in range(args.walks):
            x = t
            for _ in range(args.length):
                x = O.mutate(x, rng.randrange(4))
                if O.level(x) > 10 ** 12:
                    break
                seen += 1
                e = O.exit_returns(x)
                if len(e) > 1:
                    multi += 1
                if e and len(exits) < args.max_exits:
                    exits[x] = min(e)
    kinds = Counter()
    for x, m in exits.items():
        kinds["fork" if O.fork_return(x) == m else "pre-fork, not a fork"] += 1
    print(f"{seen} quivers visited on random walks from {len(starts)} census classes; {len(exits)} distinct exits kept: {dict(kinds)}")
    print(f"quivers with more than one return vertex: {multi}")
    # one step up from an exit
    bad = Counter()
    n_steps = 0
    for x, m in exits.items():
        isfork = O.fork_return(x) == m
        sp = O.small_pairs(x)
        for k in range(4):
            if k == m:
                continue
            y = O.mutate(x, k)
            if isfork:
                n_steps += 1
                if O.fork_return(y) != k:
                    bad["fork: mu_k is not a fork with return k"] += 1
                if O.weight(y) <= O.weight(x):
                    bad["fork: weight does not increase"] += 1
            elif k not in sp[0]:
                n_steps += 1
                if k not in O.prefork_returns(y):
                    bad["pre-fork: mu_m is not a pre-fork with return m"] += 1
                if O.weight(y) <= O.weight(x):
                    bad["pre-fork: weight does not increase"] += 1
                if O.entry(y, *sp[0]) != O.entry(x, *sp[0]):
                    bad["pre-fork: the entry k k' changes"] += 1
    print(f"steps away from the return vertex checked: {n_steps}; failures: {dict(bad)}")
    # the far region inside a ball: never crosses back, weights >= the root's, levels do not drop
    bad = Counter()
    n_balls = Counter()
    n_nodes = 0
    forks = [(x, m) for x, m in exits.items() if O.fork_return(x) == m]
    pre0 = [(x, m) for x, m in exits.items() if O.fork_return(x) != m and O.entry(x, *O.small_pairs(x)[0]) == 0]
    pre1 = [(x, m) for x, m in exits.items() if O.fork_return(x) != m and O.entry(x, *O.small_pairs(x)[0]) != 0]
    for name, lst in (("fork", forks), ("pre-fork, k k' not joined", pre0), ("pre-fork, k k' joined by one arrow", pre1)):
        for x, m in lst[:args.balls]:
            sp = O.small_pairs(x)
            roots = {x}
            if sp and abs(O.entry(x, *sp[0])) == 1:
                k, kp = sp[0]
                y = x
                for v in (k, kp, k, kp, k):
                    y = O.mutate(y, v)
                roots.add(y)                           # the second root, x with k and k' exchanged
                p = list(range(4)); p[k], p[kp] = kp, k
                sw = tuple(s * x[a] for a, s in O.RELAB[O.PERMS.index(tuple(p))])
                if sw != y:
                    bad["mu_[k,k',k,k',k] is not the swap of k and k'"] += 1
            foot = {O.mutate(z, m) for z in roots}
            parent = {z: None for z in roots}
            frontier = list(roots)
            for _ in range(args.radius):
                nxt = []
                for z in frontier:
                    for k in range(4):
                        if z in roots and k == m:
                            continue
                        y = O.mutate(z, k)
                        if O.level(y) > 10 ** 30:
                            continue
                        if y not in parent:
                            parent[y] = z
                            nxt.append(y)
                frontier = nxt
            n_balls[name] += 1
            n_nodes += len(parent)
            if set(parent) & foot:
                bad["the far region reaches the foot of the bridge"] += 1
            w0, l0 = O.weight(x), O.level(x)
            if any(O.weight(y) < w0 or (O.weight(y) == w0 and y not in roots) for y in parent):
                bad["a quiver of the far region is not heavier than the root"] += 1
            if any(len(O.small_pairs(y)) > 1 for y in parent):
                bad["a quiver of the far region has two pairs of weight < 2"] += 1
            if any(O.level(y) < l0 for y in parent):
                bad[f"{name}: a quiver of the far region lies below the level of the root"] += 1
            if any(z is not None and O.level(z) > O.level(y) for y, z in parent.items()):
                bad[f"{name}: a step away from the root lowers the level"] += 1
    print(f"far regions explored to radius {args.radius}: {dict(n_balls)} ({n_nodes} labelled quivers); failures: {dict(bad)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("cores")
    s.add_argument("--cap", type=int, default=800)
    s.add_argument("--level-cap", type=int, default=10**6)
    s.add_argument("--procs", type=int, default=12)
    s.add_argument("--out", default="n4_opposite_cores.jsonl.gz")
    s = sub.add_parser("plateaus")
    s.add_argument("--procs", type=int, default=4)
    s.add_argument("--out", default="n4_opposite_plateaus.jsonl.gz")
    s = sub.add_parser("mirror")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s = sub.add_parser("fn")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--out", default="n4_opposite_fn.jsonl.gz")
    s.add_argument("--resume", default="")
    s.add_argument("--procs", type=int, default=4)
    s.add_argument("--limit", type=int, default=0)
    s = sub.add_parser("corecheck")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--procs", type=int, default=3)
    s = sub.add_parser("pockets")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--out", default="n4_opposite_pockets.jsonl.gz")
    s.add_argument("--resume", default="")
    s.add_argument("--procs", type=int, default=4)
    s = sub.add_parser("summary")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--procs", type=int, default=3)
    s = sub.add_parser("extremes")
    s.add_argument("--kmin", type=int, default=3)
    s.add_argument("--kmax", type=int, default=200)
    s = sub.add_parser("combined")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--plateaus", default="n4_opposite_plateaus.jsonl.gz")
    s.add_argument("--tubes", default="n4_opposite_tubes.jsonl.gz")
    s.add_argument("--procs", type=int, default=4)
    s = sub.add_parser("tubeshapes")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--classes", type=int, default=600)
    s.add_argument("--cap", type=int, default=1200)
    s.add_argument("--high", type=int, default=10 ** 5)
    s.add_argument("--seed", type=int, default=50)
    s = sub.add_parser("walks")
    s.add_argument("--cores", default="n4_opposite_cores.jsonl.gz")
    s.add_argument("--classes", type=int, default=3000)
    s.add_argument("--walks", type=int, default=3)
    s.add_argument("--length", type=int, default=40)
    s.add_argument("--digits", type=int, default=300)
    s.add_argument("--seed", type=int, default=50)
    s = sub.add_parser("lemmas")
    s.add_argument("--classes", type=int, default=3000)
    s.add_argument("--walks", type=int, default=6)
    s.add_argument("--length", type=int, default=8)
    s.add_argument("--max-exits", type=int, default=200000)
    s.add_argument("--balls", type=int, default=3000)
    s.add_argument("--radius", type=int, default=7)
    s.add_argument("--seed", type=int, default=48)
    args = ap.parse_args()
    {"cores": cmd_cores, "lemmas": cmd_lemmas, "plateaus": cmd_plateaus, "mirror": cmd_mirror, "fn": cmd_fn, "corecheck": cmd_corecheck, "pockets": cmd_pockets, "summary": cmd_summary, "extremes": cmd_extremes, "walks": cmd_walks, "tubeshapes": cmd_tubeshapes, "combined": cmd_combined}[args.cmd](args)


if __name__ == "__main__":
    main()
