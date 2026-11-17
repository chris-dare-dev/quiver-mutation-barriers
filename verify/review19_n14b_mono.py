"""Review 2 of note 14 (n14b), item 1(c): attack on 'the growing vertex' step of the tube certificates with
synthetic families (independent code, review19_n14b_lib).  A family has every entry away from vertex 0
constant and the entries at 0 constant or of constant sign with non-decreasing absolute value (the
conditions the engine certifies), at least two of them growing and multiplied by the mutation at 0.
Question: if (Y(n), 0) is not an exit and (mu_0 Y(n), 0) is an exit for n = 0 (resp. n = 0, 1, 2), does
this hold for every n <= 40?  Also counted: whether an entry of mu_0 Y(n) changes sign with n.
Usage: python -I review19_n14b_mono.py SEED TRIALS"""
import random
import sys
from collections import Counter

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n14b_lib as L


def seq(rng, tau, s):
    e0 = s * rng.randint(1, 6)
    d0 = s * rng.randint(0, 4)
    d1 = d0 + s * rng.randint(0, 4)
    out = [e0, e0 + d0, e0 + d0 + d1]
    while len(out) < 44:
        out.append((tau + 1) * (out[-1] - out[-2]) + out[-3])
    return out


def main():
    seed, trials = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    st = Counter()
    ex = []
    for _ in range(trials):
        tau = rng.choice((2, 3, 4, 7, 34))
        at0 = []
        for a in range(3):
            if rng.random() < 0.7:
                s = rng.choice((-1, 1))
                v = seq(rng, tau, s)
                if v[0] == v[1] == v[2]:
                    v = [v[0]] * 44
                at0.append(v)
            else:
                c = rng.randint(-6, 6)
                at0.append([c] * 44)
        cst = [rng.randint(-12, 12) for _ in range(3)]          # b12, b13, b23
        Ys = [(at0[0][n], at0[1][n], at0[2][n], cst[0], cst[1], cst[2]) for n in range(44)]
        # two growing entries at 0 multiplied: i -> 0 -> j with both varying
        B0 = L.mat(Ys[0])
        var = [len(set(at0[a][:3])) > 1 for a in range(3)]
        nonlin = any(var[i - 1] and var[j - 1] and B0[i][0] * B0[0][j] > 0 for i in (1, 2, 3) for j in (1, 2, 3) if i != j)
        if not nonlin:
            continue
        st["families with a growing-vertex step at 0"] += 1
        good = []
        signs = set()
        for n in range(41):
            y = Ys[n]
            z = L.mut(y, 0)
            good.append(0 in L.exits(z) and 0 not in L.exits(y))
            signs.add(tuple((v > 0) - (v < 0) for v in z))
        if good[0]:
            st["strict up-exit at n = 0"] += 1
            if not all(good):
                st["... but not at some n <= 40  (the claim of section 8 with n = 0 only)"] += 1
                if len(ex) < 5:
                    ex.append(("n=0", Ys[0], Ys[1], Ys[2], tau, good.index(False)))
        if all(good[:3]):
            st["strict up-exit at n = 0, 1, 2 (what the engine tests)"] += 1
            if not all(good):
                st["... but not at some n <= 40  (VIOLATION of the engine's rule)"] += 1
                if len(ex) < 10:
                    ex.append(("n=0..2", Ys[0], Ys[1], Ys[2], tau, good.index(False)))
            if len(signs) > 1:
                st["... and an entry of mu_0 Y(n) changes sign with n"] += 1
        if not good[0] and any(good):
            st["not an exit at n = 0 but at a later n"] += 1
    for k in sorted(st):
        print(f"   {k}: {st[k]}")
    for e in ex:
        print("   example:", e)


if __name__ == "__main__":
    main()
