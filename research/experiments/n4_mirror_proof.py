#!/usr/bin/env python
"""
n4_mirror_proof.py -- a symbolic proof that f(Q, w)/w is unbounded on 4 vertices (note 9).

G_k has rows (0, k, -k, -k), (-k, 0, 0, k), (k, 0, 0, -(k-1)), (k, -k, k-1, 0).  This script runs the
note-9 computation with entries that are polynomials in k (integer coefficients):

  1. Breadth-first search from G_k, up to relabelling, keeping every mutation whose maximal entry
     is <= k^2 + 4k.  Every sign and every comparison is decided by the sign of a polynomial at large
     k, and each such polynomial is recorded together with a bound beyond which its sign is that of
     its leading coefficient (Cauchy's root bound).
  2. On the closed set S found, the maximal-entry filtration: its bottom level, the components there,
     and the level at which they join.

If the search closes (every mutation of a member of S is in S or exceeds the bound), then for every
k > k0 (the largest recorded root bound) the class of G_k contains exactly the quivers of S with
maximal entry <= k^2 + 4k, and the statements of step 2 hold for that k.  The finitely many k <= k0
are checked numerically with the exact integer code (n4_mirror.py).

Run from experiments/ with python -I.
"""
import itertools
import sys
from fractions import Fraction

THRESH = []          # Cauchy bounds of every polynomial whose sign was used


def norm(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return tuple(p)


def add(p, q):
    n = max(len(p), len(q))
    return norm([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])


def neg(p):
    return tuple(-c for c in p)


def mul(p, q):
    if not p or not q:
        return ()
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return norm(r)


def sign(p):
    """Sign of p(k) for all large k; records the bound beyond which it holds."""
    if not p:
        return 0
    lead = p[-1]
    bound = 1 + max([Fraction(abs(c), abs(lead)) for c in p[:-1]] or [0])
    THRESH.append(bound)
    return 1 if lead > 0 else -1


def absp(p):
    return neg(p) if sign(p) < 0 else p


def less_eq(p, q):
    return sign(add(q, neg(p))) >= 0


def pmax(ps):
    best = ps[0]
    for p in ps[1:]:
        if sign(add(p, neg(best))) > 0:
            best = p
    return best


def mutate(B, k):
    n = len(B)
    N = [[B[i][j] for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i == k or j == k:
                N[i][j] = neg(B[i][j])
            else:
                prod = mul(B[i][k], B[k][j])
                if sign(prod) > 0:
                    s = sign(B[i][k])
                    N[i][j] = add(B[i][j], prod if s > 0 else neg(prod))
    return N


def maxentry(B):
    return pmax([absp(B[i][j]) for i in range(4) for j in range(4) if i != j])


def key(B):
    """Canonical form up to relabelling: least tuple over the 24 relabellings."""
    best = None
    for p in itertools.permutations(range(4)):
        t = tuple(B[p[i]][p[j]] for i in range(4) for j in range(4))
        if best is None or t < best:
            best = t
    return best


def main():
    K = (0, 1)                       # the polynomial k
    one = (1,)
    Gk = [[(), K, neg(K), neg(K)],
          [neg(K), (), (), K],
          [K, (), (), neg(add(K, neg(one)))],
          [K, neg(K), add(K, neg(one)), ()]]
    bound = (0, 4, 1)                # k^2 + 4k
    S = {key(Gk): Gk}
    edges = []
    todo = [Gk]
    exceed = 0
    while todo:
        X = todo.pop()
        kx = key(X)
        for v in range(4):
            Y = mutate(X, v)
            if not less_eq(maxentry(Y), bound):
                exceed += 1
                continue
            ky = key(Y)
            if ky not in S:
                S[ky] = Y
                todo.append(Y)
            edges.append((kx, ky))
    print(f"closed set S: {len(S)} quivers up to relabelling (mutations leaving the bound: {exceed})")
    mirror = [[neg(Gk[i][j]) for j in range(4)] for i in range(4)]
    print(f"the opposite -G_k is in S: {key(mirror) in S}")
    lv = {k: maxentry(B) for k, B in S.items()}
    # order the levels at infinity
    levels = []
    for p in lv.values():
        if p not in levels:
            levels.append(p)
    import functools
    levels.sort(key=functools.cmp_to_key(lambda a, b: sign(add(a, neg(b)))))
    fmt = lambda p: " + ".join(f"{c}k^{i}" for i, c in enumerate(p) if c) or "0"
    print("levels present:", [fmt(p) for p in levels])
    parent = {k: k for k in S}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    lo = levels[0]
    bottom = [k for k in S if lv[k] == lo]
    for L in levels:
        for a, b in edges:
            if sign(add(L, neg(lv[a]))) >= 0 and sign(add(L, neg(lv[b]))) >= 0:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
        comps = {find(k) for k in bottom}
        print(f"  at level {fmt(L)}: the {len(bottom)} bottom quivers lie in {len(comps)} component(s)")
        if len(comps) == 1:
            print(f"bottom level {fmt(lo)}; the bottom components first join at level {fmt(L)}")
            break
    # distinct members of S must stay distinct (up to relabelling) at the k considered: for every pair
    # and relabelling, some entry differs by a nonzero polynomial, nonzero beyond its Cauchy bound
    members = list(S.values())
    for a in range(len(members)):
        for b in range(a + 1, len(members)):
            X, Y = members[a], members[b]
            for p in itertools.permutations(range(4)):
                diffs = [add(X[p[i]][p[j]], neg(Y[i][j])) for i in range(4) for j in range(4)]
                nz = [d for d in diffs if d]
                assert nz, "two members of S are equal up to relabelling"
                bounds = [1 + max([Fraction(abs(c), abs(d[-1])) for c in d[:-1]] or [0]) for d in nz]
                THRESH.append(min(bounds))
    k0 = max(THRESH)
    print(f"every sign, comparison and distinctness used is valid for k > {float(k0):.2f} (largest Cauchy bound over {len(THRESH)} polynomials)")


if __name__ == "__main__":
    sys.exit(main())
