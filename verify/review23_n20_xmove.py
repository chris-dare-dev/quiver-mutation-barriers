"""Review of note 20: the fifth vertex x is not determined by the class of a member of K(a).

Labelled breadth-first search from Q_a (x = vertex 0) through non-forks of height < H(a), in
Python, with parent pointers.  Lists the labelled copies of Q_a that are reached, and prints, for
one copy in which vertex 0 no longer plays the part of x, the route that reaches it (its length,
height, and the number of mutations at each label).

Usage: python -I review23_n20_xmove.py a [a ...]
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
from review23_n20_lib import mutate, height, is_fork, H_of, Q_matrix, perms, upper, from_upper  # noqa: E402


def run(a):
    H = H_of(a)
    w = a + 1
    Q = Q_matrix(a)
    start = upper(Q)
    parent = {start: None}
    order = [start]
    i = 0
    while i < len(order):
        key = order[i]
        i += 1
        X = from_upper(5, key)
        for v in range(5):
            Y = mutate(X, v)
            if height(Y) >= H or is_fork(Y):
                continue
            ky = upper(Y)
            if ky not in parent:
                parent[ky] = (key, v)
                order.append(ky)
    copies = []
    for t in perms(5):
        C = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                C[t[x]][t[y]] = Q[x][y]
        if upper(C) in parent:
            copies.append(t)
    print('a=%d H=%d: %d labelled non-fork quivers reached; labelled copies of Q_a reached: %d; '
          'images of x (vertex 0) under them: %s'
          % (a, H, len(order), len(copies), sorted(set(t[0] for t in copies))))
    moved = [t for t in copies if t[0] != 0]
    if moved:
        t = moved[0]
        C = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                C[t[x]][t[y]] = Q[x][y]
        key = upper(C)
        word = []
        hmax = 0
        while parent[key] is not None:
            hmax = max(hmax, height(from_upper(5, key)))
            key, v = parent[key]
            word.append(v)
        word.reverse()
        print('   copy with vertex i of Q_a at label t[i], t = %s: reached by %d mutations of height %d '
              '(H = %d); mutations per label: %s' % (t, len(word), hmax, H, dict(sorted(Counter(word).items()))))
    sys.stdout.flush()


if __name__ == '__main__':
    for tok in sys.argv[1:]:
        run(int(tok))
