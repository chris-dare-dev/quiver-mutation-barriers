"""Check A of note 14, item 1(d): compare n4_opposite.py's fork / pre-fork / exit / direct tests with an
independent implementation of Ervin's definitions (review19_n14a_lib.py) on many quivers; check
consequences (a), (b) and Ervin's structural lemmas with the independent predicates.

  python -I review19_n14a_preds.py [N_per_family] [seed]
"""
import os
import random
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14a_lib as L
import n4_opposite as O            # the code under review, only for comparison

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
rng = random.Random(SEED)


def rand_uniform(R):
    return L.from6([rng.randint(-R, R) for _ in range(6)])


def rand_one_light(R):
    t = [rng.choice([-1, 1]) * rng.randint(2, R) for _ in range(6)]
    t[rng.randrange(6)] = rng.choice([-1, 0, 1])
    return L.from6(t)


def rand_walk(R, steps):
    B = rand_uniform(R)
    for _ in range(steps):
        B = L.mut(B, rng.randrange(4))
    return B


def rand_prefork_from_key(R):
    """A key-like quiver (k, k' on the same side of every other vertex) mutated at a non-source/sink
    vertex: often a pre-fork (Ervin Lemma 4.10)."""
    while True:
        # acyclic order 0<1<2<3 with arrows i->j, then pick k, k' adjacent-ish and set k-k' light
        t = {}
        for i, j in L.UPPER:
            t[(i, j)] = rng.randint(2, R)
        k, kp = rng.sample(range(4), 2)
        a, b = min(k, kp), max(k, kp)
        t[(a, b)] = rng.choice([0, 1, -1])
        B = L.from6([t[p] for p in L.UPPER])
        perm = list(range(4))
        rng.shuffle(perm)
        B = L.relabel(B, perm)
        if not L.is_key(B):
            continue
        m = rng.randrange(4)
        B = L.mut(B, m)
        for _ in range(rng.randrange(4)):
            B = L.mut(B, rng.randrange(4))
        return B


FAMILIES = [
    ("uniform R=3", lambda: rand_uniform(3)),
    ("uniform R=6", lambda: rand_uniform(6)),
    ("uniform R=15", lambda: rand_uniform(15)),
    ("one light pair R=8", lambda: rand_one_light(8)),
    ("one light pair R=30", lambda: rand_one_light(30)),
    ("random walk 6 steps from R=3", lambda: rand_walk(3, 6)),
    ("random walk 10 steps from R=2", lambda: rand_walk(2, 10)),
    ("from a key, R=6", lambda: rand_prefork_from_key(6)),
    ("from a key, R=20", lambda: rand_prefork_from_key(20)),
]


def main():
    t0 = time.time()
    stat = Counter()
    bad = Counter()
    examples = {}

    def fail(name, B):
        bad[name] += 1
        examples.setdefault(name, L.to6(B))

    for fam, gen in FAMILIES:
        for _ in range(N):
            B = gen()
            t = L.to6(B)
            stat["quivers"] += 1
            fr = L.fork_returns(B)
            pt = L.prefork_triples(B)
            pr = {r for r, k, kp in pt}
            ex = fr | pr
            # comparison with the code under review
            ofr = O.fork_return(t)
            if (ofr is None) != (not fr) or (ofr is not None and ofr not in fr):
                fail("fork_return differs", B)
            if O.prefork_returns(t) != pr:
                fail("prefork_returns differs", B)
            if O.exit_returns(t) != ex:
                fail("exit_returns differs", B)
            # consequence (a) and Warkentin Lemma 2.3.e
            if len(fr) > 1:
                fail("fork with two points of return", B)
            if len(ex) > 1:
                fail("two exit vertices (consequence (a))", B)
            if fr:
                stat["forks"] += 1
            if pr and not fr:
                stat["pre-forks that are not forks"] += 1
                stat[f"   ... with |q_kk'| = {min(abs(B[k][kp]) for r, k, kp in pt)}"] += 1
            for r, k, kp in pt:
                if abs(B[k][kp]) >= 2 and r not in fr:
                    fail("pre-fork with |q_kk'| >= 2 that is not a fork with return r (Lemma 6.1)", B)
                if abs(B[k][kp]) < 2 and fr:
                    fail("pre-fork with a light pair that is a fork", B)
            # wings and tips: shapes and light pairs (consequence (b))
            for var in ("oriented", "none"):
                w = L.wing_pairs(B, var)
                tp = L.tip_pairs(B, var)
                if w:
                    stat[f"wings ({var})"] += 1
                if tp:
                    stat[f"tips ({var})"] += 1
                if (w or tp) and len(L.light_pairs(B)) != 1:
                    fail(f"wing or tip ({var}) without exactly one light pair", B)
                if (w or tp) and ex:
                    fail(f"wing or tip ({var}) that is also an exit", B)
            if pt and len(L.light_pairs(B)) > 1:
                fail("pre-fork with two light pairs", B)
            # the direct test of n4_opposite.certainly_in_core
            shape = L.in_far_region_shape(B, "none")
            cic = O.certainly_in_core(t)
            if cic:
                stat["certainly_in_core True"] += 1
                if shape:
                    fail("certainly_in_core True but B is a fork/pre-fork/wing/tip (weakest reading)", B)
            else:
                stat["certainly_in_core False"] += 1
                if not shape:
                    stat["   ... although B is none of fork/pre-fork/wing/tip (test conservative)"] += 1
            # Ervin's structural lemmas, with the independent predicates
            for r, k, kp in pt:
                if abs(B[k][kp]) >= 2:
                    continue
                for a, b in ((k, kp), (kp, k)):
                    W = L.mut(B, a)
                    stat["pre-fork -> mu_k (Cor. 4.15)"] += 1
                    if (a, b) not in L.wing_pairs(W, "oriented"):
                        fail("mu_k(pre-fork) not a wing with return k, oriented reading", B)
                    if (a, b) not in L.wing_pairs(W, "none"):
                        fail("mu_k(pre-fork) not a wing with return k, weakest reading", B)
                    T = L.mut(W, b)
                    stat["wing -> mu_k' (Cor. 4.19)"] += 1
                    if (b, a) not in L.tip_pairs(T, "oriented"):
                        fail("mu_k' mu_k(pre-fork) not a tip with return k', oriented reading", B)
                    if (b, a) not in L.tip_pairs(T, "none"):
                        fail("mu_k' mu_k(pre-fork) not a tip with return k', weakest reading", B)
                    if L.weight(W) <= L.weight(B) or L.weight(T) <= L.weight(W):
                        fail("weight does not increase pre-fork -> wing -> tip", B)
                    for m in range(4):
                        if m in (k, kp):
                            continue
                        F = L.mut(W, m)
                        stat["wing -> mu_r, r not in {k,k'} (Lemmas 4.16, 4.17)"] += 1
                        if L.fork_returns(F) != {m}:
                            fail("mu_r(wing) not a fork with return r", B)
                        P2 = L.mut(T, m)
                        stat["tip -> mu_r (Cor. 4.20)"] += 1
                        if L.exit_vertices(P2) != {m}:
                            fail("mu_r(tip) not a fork or pre-fork with return r", B)
                        if L.weight(P2) <= L.weight(T):
                            fail("mu_r(tip) not heavier", B)
                for m in range(4):
                    if m in (r, k, kp):
                        continue
                    P2 = L.mut(B, m)
                    stat["pre-fork -> mu_m, m not in {r,k,k'} (Lemma 4.6)"] += 1
                    if (m, k, kp) not in L.prefork_triples(P2) or P2[k][kp] != B[k][kp] or L.weight(P2) <= L.weight(B):
                        fail("Lemma 4.6 fails", B)
                if abs(B[k][kp]) == 1:
                    X = B
                    for v in (k, kp, k, kp, k):
                        X = L.mut(X, v)
                    p = list(range(4))
                    p[k], p[kp] = kp, k
                    stat["q_kk' = 1: mu_[k,k',k,k',k] (Lemma 4.23 b)"] += 1
                    if X != L.relabel(B, p):
                        fail("mu_[k,k',k,k',k](P) is not P with k, k' exchanged", B)
                else:
                    X = B
                    for v in (k, kp, k, kp):
                        X = L.mut(X, v)
                    X5 = L.mut(X, k)
                    stat["q_kk' = 0: mu_[k,k',k,k'] (Lemma 4.23 a)"] += 1
                    if X != B:
                        fail("mu_[k,k',k,k'](P) != P", B)
                    if X5 == B:
                        fail("mu_[k,k',k,k',k](P) == P when q_kk' = 0", B)
            # (F1): mutation of a fork away from its return, entries never shrink (consequence (c))
            for r in fr:
                for m in range(4):
                    if m == r:
                        continue
                    F = L.mut(B, m)
                    stat["fork -> mu_k, k != r"] += 1
                    if L.fork_returns(F) != {m} or L.weight(F) <= L.weight(B):
                        fail("(F1) fails", B)
                    if any(abs(F[i][j]) < abs(B[i][j]) for i, j in L.UPPER):
                        fail("consequence (c): an entry shrinks", B)
        print(f"  {fam}: done ({time.time() - t0:.0f}s)", flush=True)
    print(f"seed {SEED}, {N} quivers per family, {len(FAMILIES)} families")
    for k in sorted(stat):
        print(f"  {k}: {stat[k]}")
    print("failures:", dict(bad) if bad else "none")
    for k, v in examples.items():
        print(f"  first example of '{k}': {v}")
    print(f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
