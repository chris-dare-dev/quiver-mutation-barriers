"""
review19_n13_soundness.py -- empirical soundness test of the certificates and of the Markov/properness
conventions on quivers KNOWN to be mutation-acyclic (random mutation walks from random acyclic quivers):
  - no tri / vortex / Lemma-2.4 certificate ever fires;
  - some proper wiggle class of Q carries the Markov value m of the start's topological class (the totally
    proper class is transported with its Markov value, paper Thm 2.2 and sec. 2.2), so m <= H(Q);
  - for connected Q, m >= 3 and 2|p(Q)| < m (Lemma 2.4).
Usage: python -I review19_n13_soundness.py
"""
import itertools
import os
import random
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

rng = random.Random(4905)
t0 = time.time()
stats = Counter()
maxh = 0
for trial in range(40000):
    e = rng.randint(1, 6)
    while True:
        A = tuple(rng.randint(-e, e) for _ in range(6))
        if L.is_acyclic(A) and any(A):
            break
    B = L.full(A)
    topo = next(w for w in itertools.permutations(range(4)) if all(B[w[j]][w[i]] <= 0 for i in range(4) for j in range(i + 1, 4)))
    m = L.markov_value(A, topo)
    conn = L.is_connected(A)
    Q = A
    last = -1
    for step in range(rng.randint(1, 10)):
        k = rng.choice([x for x in range(4) if x != last])
        Q = L.mutate(Q, k)
        last = k
        if L.ht(Q) > 400:
            break
    maxh = max(maxh, L.ht(Q))
    stats["walks"] += 1
    stats["cert fired (must be 0)"] += L.certificate(Q) is not None
    ms = [mm for mm, _ in L.proper_markov(Q)]
    stats["m among proper-class Markov values"] += m in ms
    stats["m <= H(Q)"] += (L.H_of(Q) is not None and m <= L.H_of(Q))
    if conn:
        stats["connected"] += 1
        stats["connected: m >= 3 and 2|p| < m"] += (m >= 3 and 2 * abs(L.pfaffian(Q)) < m)
print(dict(stats))
print(f"largest height reached {maxh} ({time.time() - t0:.0f}s)")
