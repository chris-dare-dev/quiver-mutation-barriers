"""Check A of note 14, §2: (1) numerical check of the opposite-invariance proof (U_opp = w U^T w, same
Alexander polynomial, Markov invariant and minors of tU - U^T up to sign); (2) the acyclic mirror pair
whose cosquare is conjugate to its transpose, re-verified in plain Python integers.

  python -I review19_n14a_example.py
"""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14a_lib as L
from review19_n14a_cosq2 import int_cosquare, check_G, sink_source_orbit, det


def U_of(B, order):
    return [[1 if a == b else (-B[order[a]][order[b]] if a < b else 0) for b in range(4)] for a in range(4)]


# polynomials in t as tuples of coefficients (constant first)
def padd(p, q):
    n = max(len(p), len(q))
    r = [(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)]
    while r and r[-1] == 0:
        r.pop()
    return tuple(r)


def pmul(p, q):
    if not p or not q:
        return ()
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    while r and r[-1] == 0:
        r.pop()
    return tuple(r)


def pneg(p):
    return tuple(-a for a in p)


def pdet(M):
    if len(M) == 1:
        return M[0][0]
    out = ()
    for j in range(len(M)):
        sub = [r[:j] + r[j + 1:] for r in M[1:]]
        term = pmul(M[0][j], pdet(sub))
        out = padd(out, term if j % 2 == 0 else pneg(term))
    return out


def alexander_matrix(U):
    n = len(U)
    return [[padd((0, U[i][j]) if U[i][j] else (), (-U[j][i],) if U[j][i] else ()) for j in range(n)] for i in range(n)]


def minors(M, k):
    out = Counter()
    for rows in itertools.combinations(range(4), k):
        for cols in itertools.combinations(range(4), k):
            d = pdet([[M[r][c] for c in cols] for r in rows])
            # up to sign: normalise so that the leading coefficient is positive
            if d and d[-1] < 0:
                d = pneg(d)
            out[d] += 1
    return out


from collections import Counter


def main():
    rng = random.Random(50)
    bad = Counter()
    n = 0
    for _ in range(300):
        B = L.from6([rng.randint(-9, 9) for _ in range(6)])
        order = list(range(4))
        rng.shuffle(order)
        U = U_of(B, order)
        Uo = U_of(L.neg(B), order[::-1])
        w = [[int(i + j == 3) for j in range(4)] for i in range(4)]
        UT = [[U[j][i] for j in range(4)] for i in range(4)]
        wUTw = [[sum(w[i][a] * UT[a][b] * w[b][j] for a in range(4) for b in range(4)) for j in range(4)] for i in range(4)]
        n += 1
        if Uo != wUTw:
            bad["U_opp != w U^T w"] += 1
        A, Ao = alexander_matrix(U), alexander_matrix(Uo)
        if pdet(A) != pdet(Ao):
            bad["Alexander polynomial differs"] += 1
        for k in range(1, 5):
            if minors(A, k) != minors(Ao, k):
                bad[f"{k}x{k} minors differ up to sign"] += 1
        C, Co = int_cosquare(B, order), int_cosquare(L.neg(B), order[::-1])
        if sum(C[i][i] for i in range(4)) != sum(Co[i][i] for i in range(4)):
            bad["Markov invariant differs"] += 1
    print(f"opposite invariance: {n} random quivers and orderings; failures: {dict(bad) if bad else 'none'}")
    # the acyclic example
    Q = L.from6((3, 1, 0, 1, 1, -3))
    order = (0, 1, 3, 2)
    print("Q rows:", Q, "acyclic:", not L.has_cycle(Q, range(4)), "topological order:", order)
    orb = sink_source_orbit(Q)
    print(f"sink/source orbit of Q up to relabelling: {len(orb)} quivers; contains -Q: {L.key(L.neg(Q)) in orb}; "
          f"orbit of -Q: {len(sink_source_orbit(L.neg(Q)))} quivers")
    C = int_cosquare(Q, order)
    G = [[-2, -3, 4, 3], [-3, -2, 3, 1], [4, 3, -4, -2], [3, 1, -2, 0]]
    print("cosquare C =", C, "Markov M =", 4 - sum(C[i][i] for i in range(4)))
    print("G =", G, "det G =", det(G), "C G == G C^T:", check_G(C, G))
    Co = int_cosquare(L.neg(Q), order[::-1])
    print("cosquare of the opposite COQ (-Q, reversed order):", Co)


if __name__ == "__main__":
    main()
