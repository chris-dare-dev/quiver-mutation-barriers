"""Check of note 21 section 4.4 (masking by a climb).

Independent code: nothing is imported from owf_barrier.py or the scripts it
uses.  The climbs are read from owf_barrier_mask.jsonl as data.  For each row:
build -Q, apply the recorded climb to get Q', and then, without using the
climb, run (1) fork descent (mutate a fork at its point of return, Warkentin
Def. 2.1), (2) steepest descent on total arrow weight, and (3) a breadth-first
search of radius <= 4 from the end, inside the public bound, for a relabelling
of -Q.  Reports the counts of section 4.4.

  python -I review23_lead_n21_mask.py > review23_lead_n21_mask.log
"""
import itertools
import json
import math
import os
import sys
from collections import Counter

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results


def from_tuple(t, n):
    B = [[0] * n for _ in range(n)]
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            B[i][j] = t[k]
            B[j][i] = -t[k]
            k += 1
    return B


def family(name, p):
    if name == "R":            # note 15: R_b = (-b, -b, b-1, -2, b-2, -b)
        b = p
        return from_tuple((-b, -b, b - 1, -2, b - 2, -b), 4)
    if name == "Qt":           # note 15: Q_t
        t = p
        return from_tuple((-t * t, -(t * t - 1), 2 * t, -2, t * (t - 1), -t * t), 4)
    if name in ("P+", "Pp"):   # note 16: P+_t
        t = p
        return from_tuple((1, -(t * t - 1), -t * (t - 1), t * t, -2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t), 5)
    if name == "Qa":           # note 18: Q_a = (-(a-3), a-2, a+1, -(a+1) | R_a)
        a = p
        return from_tuple((-(a - 3), a - 2, a + 1, -(a + 1),
                           -(a + 1), -a, 2, -2, -a, -(a + 1)), 5)
    raise ValueError(name)


def mutate(B, k):
    n = len(B)
    C = [row[:] for row in B]
    for i in range(n):
        for j in range(n):
            if i == k or j == k:
                C[i][j] = -B[i][j]
            else:
                C[i][j] = B[i][j] + max(B[i][k], 0) * max(B[k][j], 0) - max(-B[i][k], 0) * max(-B[k][j], 0)
    return C


def acyclic_on(B, verts):
    verts = list(verts)
    indeg = {v: sum(1 for u in verts if B[u][v] > 0) for v in verts}
    left = set(verts)
    while True:
        src = [v for v in left if indeg[v] == 0]
        if not src:
            break
        v = src[0]
        left.remove(v)
        for w in left:
            if B[v][w] > 0:
                indeg[w] -= 1
    return not left


def fork_return(B):
    """Point of return if B is a fork (Warkentin Def. 2.1), else None."""
    n = len(B)
    for a, b in itertools.combinations(range(n), 2):
        if abs(B[a][b]) < 2:
            return None
    if acyclic_on(B, range(n)):
        return None
    for r in range(n):
        ins = [i for i in range(n) if B[i][r] > 0]
        outs = [j for j in range(n) if B[r][j] > 0]
        if not acyclic_on(B, ins) or not acyclic_on(B, outs):
            continue
        if all(B[j][i] > B[i][r] and B[j][i] > B[r][j] for i in ins for j in outs):
            return r
    return None


def weight(B):
    n = len(B)
    return sum(abs(B[i][j]) for i in range(n) for j in range(i + 1, n))


def height(B):
    return max(abs(x) for row in B for x in row)


def canon(B):
    n = len(B)
    best = None
    for p in itertools.permutations(range(n)):
        t = tuple(B[p[i]][p[j]] for i in range(n) for j in range(i + 1, n))
        if best is None or t < best:
            best = t
    return best


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "owf_barrier_mask.jsonl"))]
    stats = Counter()
    per = Counter()
    maxlog = 0.0
    for row in rows:
        fam, p, climb = row["family"], row["param"], row["climb"]
        Q = family(fam, p)
        target = [[-x for x in r] for r in Q]
        tkey = canon(target)
        X = target
        forks_on = 0
        for k in climb:
            X = mutate(X, k)
            if fork_return(X) is not None:
                forks_on += 1
        bound = height(X)
        maxlog = max(maxlog, math.log10(bound))
        stats["rows"] += 1
        endfork = fork_return(X) is not None
        stats["end_is_fork"] += endfork
        # fork descent
        Y = X
        nfd = 0
        while True:
            r = fork_return(Y)
            if r is None:
                break
            Y = mutate(Y, r)
            nfd += 1
        undone_by_fd = canon(Y) == tkey
        stats["fork_descent_alone"] += undone_by_fd
        # steepest descent on total weight
        nwd = 0
        while True:
            best = None
            for k in range(len(Y)):
                Z = mutate(Y, k)
                if weight(Z) < weight(Y) and (best is None or weight(Z) < weight(best[1])):
                    best = (k, Z)
            if best is None:
                break
            Y = best[1]
            nwd += 1
            r = fork_return(Y)
            while r is not None:
                Y = mutate(Y, r)
                nfd += 1
                r = fork_return(Y)
        hit_after_descent = canon(Y) == tkey
        stats["fork_and_weight_descent"] += hit_after_descent
        # small BFS inside the public bound
        dist = None
        if hit_after_descent:
            dist = 0
        else:
            front = {canon(Y): Y}
            seen = set(front)
            for d in range(1, 5):
                nxt = {}
                for Z in front.values():
                    for k in range(len(Z)):
                        W = mutate(Z, k)
                        if height(W) > bound:
                            continue
                        key = canon(W)
                        if key in seen:
                            continue
                        seen.add(key)
                        nxt[key] = W
                if tkey in nxt:
                    dist = d
                    break
                front = nxt
        stats["inverted_within_radius_4"] += dist is not None
        per[(fam, p, row["l"], endfork, undone_by_fd, hit_after_descent, dist)] += 1
        agree = (row["end_is_fork"] == endfork and row["forks_on_climb"] == forks_on)
        stats["agree_with_jsonl_on_forks"] += agree
        stats["jsonl_descent_undoes_whole_climb"] += row["descent_undoes_climb"] == len(climb)
    print(f"rows {stats['rows']}; largest log10 height of a climb {maxlog:.1f}")
    print(f"Q' is a fork (end of climb): {stats['end_is_fork']}")
    print(f"agreement with the jsonl on 'end_is_fork' and 'forks_on_climb': {stats['agree_with_jsonl_on_forks']}")
    print(f"fork descent alone reaches -Q up to relabelling: {stats['fork_descent_alone']} "
          f"(jsonl: descent_undoes_climb = l in {stats['jsonl_descent_undoes_whole_climb']})")
    print(f"fork descent + steepest weight descent reach -Q: {stats['fork_and_weight_descent']}")
    print(f"-Q within 4 mutations of the end of the descents, inside the bound: {stats['inverted_within_radius_4']}")
    print("by family, parameter, climb length, end fork, fork descent alone, both descents, BFS distance: count")
    for k in sorted(per, key=str):
        print("  ", k, per[k])


if __name__ == "__main__":
    main()
