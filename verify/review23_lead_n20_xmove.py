"""Check of the finding that Q_a reaches, below H(a)
and through quivers that are not forks, relabellings of itself that move the
fifth vertex x (vertex 0).  Own code (functions of review23_lead_n21_mask.py,
written for this check); labelled breadth-first search, no canonical form.

  python -I review23_lead_n20_xmove.py > review23_lead_n20_xmove.log
  python -I review23_lead_n20_xmove.py pentagon >> review23_lead_n20_xmove.log

The second command tests the pentagon relation that explains the moves: if
|b_ij| = 1, then mu_i mu_j mu_i mu_j mu_i (B) is B with i and j exchanged.
"""
import itertools
import sys
from collections import deque
sys.path.insert(0, __file__.rsplit("/", 1)[0])
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
from review23_lead_n21_mask import family, mutate, fork_return, height


def key(B):
    return tuple(x for row in B for x in row)


def search(a, bound):
    Q = family("Qa", a)
    n = 5
    perms = {}
    for p in itertools.permutations(range(n)):
        P = [[Q[p[i]][p[j]] for j in range(n)] for i in range(n)]  # vertex i of P is vertex p[i] of Q
        perms.setdefault(key(P), p)
    start = key(Q)
    prev = {start: None}
    dq = deque([Q])
    while dq:
        B = dq.popleft()
        kB = key(B)
        for k in range(n):
            C = mutate(B, k)
            if height(C) > bound or fork_return(C) is not None:
                continue
            kC = key(C)
            if kC not in prev:
                prev[kC] = (kB, k)
                dq.append(C)
    copies = [(perms[k], k) for k in perms if k in prev]
    return len(prev), copies, prev


def pentagon():
    import random
    rng = random.Random(5)
    bad = tested = 0
    for _ in range(20000):
        n = rng.randint(3, 7)
        B = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                x = rng.randint(-9, 9)
                B[i][j] = x
                B[j][i] = -x
        i, j = rng.sample(range(n), 2)
        s = rng.choice([1, -1])
        B[i][j] = s
        B[j][i] = -s
        C = B
        for k in (i, j, i, j, i):
            C = mutate(C, k)
        P = list(range(n))
        P[i], P[j] = j, i
        D = [[B[P[a]][P[b]] for b in range(n)] for a in range(n)]
        tested += 1
        bad += (C != D)
    print(f"pentagon: {tested} random quivers on 3-7 vertices with |b_ij| = 1: "
          f"mu_i mu_j mu_i mu_j mu_i (B) != B with i, j exchanged in {bad}")


if len(sys.argv) > 1 and sys.argv[1] == "pentagon":
    pentagon()
    sys.exit(0)

for a, bound in ((3, 26), (3, 25), (5, 234), (5, 233), (6, 407), (6, 406)):
    size, copies, prev = search(a, bound)
    moved = [p for p, _ in copies if p[0] != 0]
    line = f"a={a} bound {bound}: {size} labelled non-forks reached; copies of Q_a: {len(copies)}; copies moving x: {len(moved)}"
    if moved:
        p = moved[0]
        k = [kk for pp, kk in copies if pp == p][0]
        word = []
        while prev[k] is not None:
            k, m = prev[k]
            word.append(m)
        word.reverse()
        # replay with the word and record the height
        B = family("Qa", a)
        hmax = height(B)
        forks = 0
        for m in word:
            B = mutate(B, m)
            hmax = max(hmax, height(B))
            forks += fork_return(B) is not None
        line += f"; e.g. vertex i of the copy is vertex {p} [i] of Q_a, by {len(word)} mutations {word}, height {hmax}, forks {forks}"
    print(line, flush=True)
