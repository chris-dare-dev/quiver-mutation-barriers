"""Review 3 of note 22: is the Markov constant of note 22 §2 a mutation invariant?  The weight form
x^2 + y^2 + z^2 - xyz (oriented 3-cycle) / + xyz (otherwise) against the signed form
b12^2 + b23^2 + b31^2 - b12 b23 b31 written in §2, on random 3-vertex quivers.
Usage: python -I review23_n22_markovC.py > review23_n22_markovC.log"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L
rng = random.Random(1)
bad_true = bad_signed = n = 0
for _ in range(20000):
    t = (0, 0, 0, rng.randint(-6, 6), rng.randint(-6, 6), rng.randint(-6, 6))
    T = L.tri_entries(t, 0)
    for k in (1, 2, 3):
        U = L.tri_entries(L.mutate(t, k), 0)
        n += 1
        bad_true += L.markov_C(T) != L.markov_C(U)
        bad_signed += L.markov_C_signed(T) != L.markov_C_signed(U)
print('mutations', n, 'weight form not invariant', bad_true, 'signed form of note 22 s2 not invariant', bad_signed)
t = (0, 0, 0, 1, 0, 1)
u = L.mutate(t, 2)
print('example: path 1 -> 2 -> 3, (b12, b23, b31) =', L.tri_entries(t, 0), 'signed C', L.markov_C_signed(L.tri_entries(t, 0)),
      '; after mu_2:', L.tri_entries(u, 0), 'signed C', L.markov_C_signed(L.tri_entries(u, 0)), '; weight form', L.markov_C(L.tri_entries(t, 0)), L.markov_C(L.tri_entries(u, 0)))
