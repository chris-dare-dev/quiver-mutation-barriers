#!/usr/bin/env python
"""
pockets.py -- the pockets of note 3, measured as 0-dimensional persistence (note 4).

Filter the mutation graph of one class (quivers up to relabelling) by maximal entry: X_L is the
set of quivers with all |entries| <= L, with the mutations between them.  As L grows, components
of X_L are born at their lowest quiver and die when they merge into an older one (elder rule).
A *pocket* is a component that dies at a level D above its birth level b: its quivers have
maximal entry >= b, and the first path out of it to an older component climbs to D.  The
profile of note 3 is recovered as

    f(w) = max(m_w, max{ D : b <= m_w < D })        (m_w = largest level <= w),

so the persistence pairs (b, D) carry all of the bounded-path data; the barrier ratio D/b is
the quantity a bound F(n, w) has to control.

For every pocket the script also records its lowest quiver (canonical form), whether it is a
fork (Warkentin, Definition 2.1), how many entries attain its maximum, the lowest maximal entry
among its mutations, and where greedy descent on total weight (sum of |entries| / 2) takes it:
the maximal entry met on the way, and whether it ends at the class minimum.

Subcommands:
  diagram    one JSONL row per component, with its persistence pairs
  summarize  tables from the JSONL file

Run from experiments/ with python -I.  Reuses bounded_paths.py and mutation_path.py.
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT, all_mutations, max_entry_per_k  # noqa: E402
from bounded_paths import make_quiver, enumerate_component, canonical  # noqa: E402


# ----------------------------------------------------------------------------- forks
def _acyclic(B, idx):
    rem = set(idx)
    while rem:
        src = [i for i in rem if not any(B[j, i] > 0 for j in rem)]
        if not src:
            return False
        rem -= set(src)
    return True


def fork_return(B):
    """Point of return if B is a fork (Warkentin, Def. 2.1: abundant, not acyclic, and a vertex
    r with q_ji > q_ir, q_rj for all i -> r -> j, and Q^-(r), Q^+(r) acyclic); else None."""
    n = B.shape[0]
    if np.abs(B[~np.eye(n, dtype=bool)]).min() < 2 or _acyclic(B, range(n)):
        return None
    for r in range(n):
        Qm = [i for i in range(n) if B[i, r] > 0]
        Qp = [j for j in range(n) if B[r, j] > 0]
        if all(B[j, i] > B[i, r] and B[j, i] > B[r, j] for i in Qm for j in Qp) and _acyclic(B, Qm) and _acyclic(B, Qp):
            return r
    return None


# ----------------------------------------------------------------------------- persistence
def persistence(states, n):
    """Elder-rule persistence pairs of the max-entry filtration on the quotient graph.
    states: canonical bytes -> maximal entry.  Returns pairs (birth, death, rep, size) with
    death > birth, the global minimum level, and the representative of the eldest component."""
    by_level = defaultdict(list)
    for k, v in states.items():
        by_level[v].append(k)
    parent, birth, rep, size = {}, {}, {}, {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = []
    for lvl in sorted(by_level):
        new = by_level[lvl]
        for k in new:
            parent[k] = k
            birth[k], rep[k], size[k] = lvl, k, 1
        for k in new:
            N = all_mutations(np.frombuffer(k, dtype=DT).reshape(n, n))
            me = max_entry_per_k(N)
            for j in np.flatnonzero(me <= lvl):
                nb = canonical(N[j]).tobytes()
                if nb not in parent:
                    continue
                ra, rb = find(k), find(nb)
                if ra == rb:
                    continue
                # elder rule: the component born later dies; ties broken by size, then key
                if (birth[ra], -size[ra], rep[ra]) > (birth[rb], -size[rb], rep[rb]):
                    ra, rb = rb, ra
                if birth[rb] < lvl:
                    pairs.append((birth[rb], lvl, rep[rb], size[rb]))
                parent[rb] = ra
                size[ra] += size[rb]
    roots = {find(k) for k in parent}
    eldest = min(roots, key=lambda r: (birth[r], -size[r], rep[r]))
    alive = sorted((birth[r], size[r]) for r in roots if r != eldest)    # not merged inside the bound
    return pairs, min(by_level), rep[eldest], alive


def f_from_pairs(pairs, levels, w):
    """f(w) recovered from the persistence pairs (see the module docstring)."""
    m = max(l for l in levels if l <= w)
    return max([m] + [d for b, d, _, _ in pairs if b <= m < d])


# ----------------------------------------------------------------------------- pocket descriptors
def total_weight(B):
    return int(np.abs(B).sum() // 2)


def sum_descent(B, states, n):
    """Greedy descent on total weight inside the enumerated component; returns the maximal entry
    met, and the end quiver's level and total weight."""
    cur, path_max = B, int(np.abs(B).max())
    while True:
        N = all_mutations(cur)
        tw = np.abs(N).reshape(n, -1).sum(axis=1) // 2
        k = int(np.argmin(tw))
        if tw[k] >= total_weight(cur):
            return path_max, int(np.abs(cur).max()), total_weight(cur)
        nxt = canonical(N[k])
        if nxt.tobytes() not in states:      # left the enumerated part: report as escaped
            return None, None, None
        cur = nxt
        path_max = max(path_max, int(np.abs(cur).max()))


def describe(rep, states, n, global_min_rep):
    B = np.frombuffer(rep, dtype=DT).reshape(n, n).copy()
    M = int(np.abs(B).max())
    me = max_entry_per_k(all_mutations(B))
    sd_max, sd_level, sd_tw = sum_descent(B, states, n)
    gm = np.frombuffer(global_min_rep, dtype=DT).reshape(n, n)
    return {"quiver": B.tolist(), "max": M, "total": total_weight(B), "n_max_entries": int((np.abs(B) == M).sum() // 2),
            "fork_return": fork_return(B), "zeros": int((B == 0).sum() - n) // 2,
            "nb_max": sorted(int(x) for x in me), "sd_path_max": sd_max, "sd_end_level": sd_level, "sd_end_total": sd_tw,
            "sd_end_is_class_min": sd_tw is not None and sd_tw == total_weight(gm) and sd_level == int(np.abs(gm).max())}


def _diagram_task(task):
    n, bound, trial, seed, budget, sparse = task
    t0 = time.time()
    Q = make_quiver(n, np.random.default_rng(seed), sparse)
    states, exhausted = enumerate_component(Q, bound, budget, unlabelled=True)
    pairs, lo, eldest, alive = persistence(states, n)
    out = []
    for b, d, rep, sz in sorted(pairs, key=lambda p: (p[0], p[1])):
        row = {"birth": b, "death": d, "size": sz}
        row.update(describe(rep, states, n, eldest))
        out.append(row)
    return {"n": n, "trial": trial, "seed": seed, "sparse": bool(sparse), "B_big": bound, "comp_size": len(states),
            "exhausted": exhausted, "min_level": lo, "levels": sorted(set(states.values())),
            "unmerged": [{"birth": b, "size": sz} for b, sz in alive],
            "pairs": out, "time": round(time.time() - t0, 1)}


def cmd_diagram(args):
    tasks = []
    s = args.seed
    for trial in range(args.trials):
        s += 1
        if args.only is None or trial in args.only:
            tasks.append((args.n, args.B_big, trial, s, args.budget, args.sparse))
    print(f"{len(tasks)} components, n={args.n}, bound {args.B_big}, {args.workers} workers", flush=True)
    with open(args.out, "a" if args.append else "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_diagram_task, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n")
            f.flush()
            pk = [(p["birth"], p["death"]) for p in r["pairs"]]
            print(f"  n={r['n']} trial={r['trial']}: comp {r['comp_size']} exhausted={r['exhausted']} "
                  f"pockets {len(pk)} {pk[:8]}{' ...' if len(pk) > 8 else ''} ({r['time']}s)", flush=True)


# ----------------------------------------------------------------------------- summary
def cmd_summarize(args):
    rows = [json.loads(l) for f in args.files for l in open(f) if l.strip()]
    rows = [r for r in rows if r["exhausted"]]
    by_n = defaultdict(list)
    for r in rows:
        by_n[(r["n"], r["sparse"])].append(r)
    for (n, sparse), rs in sorted(by_n.items()):
        P = [(r, p) for r in rs for p in r["pairs"] if p["birth"] <= r["B_big"] // args.frac]
        U = [u for r in rs for u in r["unmerged"] if u["birth"] <= r["B_big"] // args.frac]
        print(f"\nn={n}{' sparse' if sparse else ''}: {len(rs)} exhausted components, "
              f"{sum(1 for r in rs if any(p['birth'] <= r['B_big'] // args.frac for p in r['pairs']))} with pockets born <= B/{args.frac}, "
              f"{len(P)} pockets ({len(U)} unmerged inside the bound; 0 expected, the enumeration is connected by construction)")
        if not P:
            continue
        ratio = [p["death"] / p["birth"] for _, p in P]
        print(f"  death/birth: max {max(ratio):.2f}, median {np.median(ratio):.2f}; death - birth: max {max(p['death'] - p['birth'] for _, p in P)}")
        for lo, hi in [(1, 8), (9, 16), (17, 32), (33, 64), (65, 128), (129, 256), (257, 10 ** 9)]:
            sel = [p for _, p in P if lo <= p["birth"] <= hi]
            if sel:
                rr = [p["death"] / p["birth"] for p in sel]
                print(f"    birth {lo:>3}-{hi if hi < 10 ** 9 else 'inf':>4}: {len(sel):>4} pockets, death/birth max {max(rr):.2f} "
                      f"median {np.median(rr):.2f} 90% {np.percentile(rr, 90):.2f}, death-birth max {max(p['death'] - p['birth'] for p in sel)}, "
                      f"size median {int(np.median([p['size'] for p in sel]))} max {max(p['size'] for p in sel)}")
        forks = sum(p["fork_return"] is not None for _, p in P)
        strict = sum(min(p["nb_max"]) > p["max"] for _, p in P)
        uniq = sum(p["n_max_entries"] == 1 for _, p in P)
        sd = [p for _, p in P if p["sd_path_max"] is not None]
        print(f"  lowest quiver: fork {forks}/{len(P)}, strict local min of max entry {strict}/{len(P)}, "
              f"maximum attained once {uniq}/{len(P)}, with a zero entry {sum(p['zeros'] > 0 for _, p in P)}/{len(P)}")
        trap = [p for p in sd if p["sd_end_total"] == p["total"]]
        moving = [p for p in sd if p["sd_end_total"] != p["total"]]
        print(f"  greedy total-weight descent: left the enumeration {len(P) - len(sd)}; "
              f"stuck at once (lowest quiver is a local min of total weight) {len(trap)}/{len(sd)}")
        if moving:
            print(f"    the other {len(moving)}: end at the class minimum {sum(p['sd_end_is_class_min'] for p in moving)}, "
                  f"path max == death {sum(p['sd_path_max'] == p['death'] for p in moving)}, path max > death {sum(p['sd_path_max'] > p['death'] for p in moving)}, "
                  f"path max < death {sum(p['sd_path_max'] < p['death'] for p in moving)}")
        if trap:
            rr = [p["death"] / p["birth"] for p in trap]
            print(f"    traps: death/birth max {max(rr):.2f} median {np.median(rr):.2f}; non-traps: "
                  f"max {max([p['death'] / p['birth'] for p in moving] or [0]):.2f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    dg = sub.add_parser("diagram")
    dg.add_argument("--n", type=int, required=True)
    dg.add_argument("--B-big", type=int, required=True)
    dg.add_argument("--budget", type=int, default=3000000)
    dg.add_argument("--trials", type=int, default=12)
    dg.add_argument("--workers", type=int, default=4)
    dg.add_argument("--seed", type=int, required=True)
    dg.add_argument("--sparse", action="store_true")
    dg.add_argument("--out", required=True)
    dg.add_argument("--append", action="store_true")
    dg.add_argument("--only", type=int, nargs="+", help="run only these trial indices (same seeds)")
    dg.set_defaults(func=cmd_diagram)
    sm = sub.add_parser("summarize")
    sm.add_argument("files", nargs="+")
    sm.add_argument("--frac", type=int, default=2, help="only pockets born at most B_big / frac")
    sm.set_defaults(func=cmd_summarize)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
