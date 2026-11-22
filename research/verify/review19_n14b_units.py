"""Review 2 of note 14 (n14b): unit checks of the independent library review19_n14b_lib.py, and a
comparison with n4_opposite.py on random quivers (the only place n4_opposite is imported here).
Run from experiments/ with python -I."""
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L

rng = random.Random(5050)
bad = Counter()

# mutation is an involution; relabelling commutes with mutation
for _ in range(20000):
    t = tuple(rng.randint(-9, 9) for _ in range(6))
    k = rng.randrange(4)
    if L.mut(L.mut(t, k), k) != t:
        bad["mutation not an involution"] += 1
    p = rng.choice(L.PERMS)
    # relabel by p: new vertex i is old p[i]; mutating the new quiver at i = mutating the old at p[i]
    i = rng.randrange(4)
    if L.relabel(L.mut(t, p[i]), p) != L.mut(L.relabel(t, p), i):
        bad["relabelling does not commute with mutation"] += 1
    if L.canon(L.relabel(t, p)) != L.canon(t):
        bad["canon not invariant"] += 1

# hand examples: the fork of Ervin's Definition 2.5 picture: r with i -> r (3), r -> j (4), j -> i (5)
# vertices i=0, r=1, j=2 and a fourth vertex 3 attached to make an abundant 4-vertex fork is not needed;
# the 3-vertex test:
B = [[0] * 4 for _ in range(4)]
def setb(B, i, j, x):
    B[i][j] = x; B[j][i] = -x
setb(B, 0, 1, 3); setb(B, 1, 2, 4); setb(B, 2, 0, 5)
if L.fork_points(B, [0, 1, 2]) != {1}:
    bad["Ervin's picture: point of return not r"] += 1
# a cyclic triangle (2, m, m): two equal largest weights -> not a fork
B = [[0] * 4 for _ in range(4)]
setb(B, 0, 1, 2); setb(B, 1, 2, 5); setb(B, 2, 0, 5)
if L.fork_points(B, [0, 1, 2]):
    bad["(2, m, m) is a fork"] += 1

# comparison with n4_opposite on random quivers and random-walk quivers
import n4_opposite as O
n = 0
kinds = Counter()
samples = []
for _ in range(60000):
    samples.append(tuple(rng.randint(-12, 12) for _ in range(6)))
for _ in range(3000):
    t = tuple(rng.randint(-3, 3) for _ in range(6))
    for _ in range(rng.randint(1, 25)):
        t = L.mut(t, rng.randrange(4))
        samples.append(t)
for t in samples:
    n += 1
    if L.mut(t, 0) != O.mutate(t, 0) or L.mut(t, 3) != O.mutate(t, 3):
        bad["mutation differs from n4_opposite"] += 1
    if L.canon(t) != O.canon(t):
        bad["canon differs from n4_opposite"] += 1
    e1 = L.exits(t)
    e2 = O.exit_returns(t)
    if e1 != e2:
        bad["exit set differs from n4_opposite"] += 1
        if bad["exit set differs from n4_opposite"] <= 5:
            print("  exit set differs:", t, e1, e2)
    fp = L.fork_points(L.mat(t), [0, 1, 2, 3])
    if len(fp) > 1:
        bad["fork with two points of return"] += 1
    if len(e1) > 1:
        bad["exit for two vertices"] += 1
    if L.no_far_region(t) != O.certainly_in_core(t):
        bad["direct test differs from n4_opposite.certainly_in_core"] += 1
    if L.is_vortex(t) != O.is_vortex(t):
        bad["vortex test differs"] += 1
    if L.is_acyclic_q(t) != O.is_acyclic(t):
        bad["acyclicity differs"] += 1
    kinds["fork" if fp else ("pre-fork" if e1 else "no exit")] += 1
print(f"units: {n} quivers compared with n4_opposite; kinds {dict(kinds)}; failures {dict(bad)}")
