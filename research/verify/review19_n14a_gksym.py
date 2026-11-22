"""Check A of note 14, Theorem 14.2: three facts that n4_opposite_gk.py does not check, certified for
every integer k >= 3 with its Poly class (p > 0 iff p(j+3) has non-negative coefficients and positive
constant term; anything else raises Undetermined):
  (1) none of the seven core quivers is an exit (so no balanced edge; item 5 applies);
  (2) the seven are pairwise non-isomorphic for every k >= 3 (every relabelling leaves an entry whose
      difference is certified non-zero), and only C_k is isomorphic to its opposite;
  (3) the level of each of the seven and of each of the twelve roots, certified (an entry whose absolute
      value is >= every other absolute value), and the minimum weight of the pre-fork roots.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import n4_opposite as O
import n4_opposite_gk as GK

GK.K0 = 3
Poly = GK.Poly
k = Poly([0, 1])
Z = Poly([0])
G = (k, -k, -k, Z, k, -(k - 1))


def nonzero(p):
    return p.sign() in ("+", "-")


def certified_level(x):
    """Return the |entry| that is certified >= every |entry|, or raise."""
    absx = [abs(e) for e in x]
    for a in absx:
        if all((a - b).sign() in ("+", "0", ">=0") for b in absx):
            return a
    raise GK.Undetermined("no certified maximum")


def main():
    negG = tuple(-e for e in G)
    core = {"G": G, "mu1G": O.mutate(G, 1), "mu2G": O.mutate(G, 2), "-G": negG}
    core["-mu1G"] = tuple(-e for e in core["mu1G"])
    core["-mu2G"] = tuple(-e for e in core["mu2G"])
    core["C"] = O.mutate(core["mu1G"], 2)
    print("valid for every integer k >= 3")
    for n, x in core.items():
        ex = O.exit_returns(x)
        print(f"  {n:6s} {x}  exit vertices: {sorted(ex)}  level: {certified_level(x)}  weight: {sum((abs(e) for e in x), Z)}")
    names = list(core)
    clash = []
    for i, a in enumerate(names):
        for b in names[i:]:
            x, y = core[a], tuple(-e for e in core[b]) if False else core[b]
            for r in GK.relabellings(y):
                if not any(nonzero(p - q) for p, q in zip(x, r)):
                    if a != b:
                        clash.append((a, b))
                    break
    print("pairs of distinct names that are isomorphic for some k >= 3 (not excluded by a certified non-zero entry):", clash)
    selfopp = []
    for a in names:
        x = core[a]
        if any(not any(nonzero(p - q) for p, q in zip(x, r)) for r in GK.relabellings(tuple(-e for e in x))):
            selfopp.append(a)
    print("isomorphic to their opposite (not excluded):", selfopp)
    # is C really the oriented 4-cycle with weights k, k, k, k-1?  print its zero pattern
    print("C:", core["C"])
    # the twelve strict up-exit steps and their roots
    n = 0
    minw = None
    for nm, x in core.items():
        ex_x = O.exit_returns(x)
        for m in range(4):
            y = O.mutate(x, m)
            if m not in ex_x and m in O.exit_returns(y):
                n += 1
                kind = "fork" if O.fork_return(y) == m else "pre-fork"
                w = sum((abs(e) for e in y), Z)
                if kind == "pre-fork":
                    minw = w if minw is None or (w - minw).sign() == "-" else minw
                print(f"  up-exit from {nm} at {m}: {kind}, level {certified_level(y)}, weight {w}")
    print(f"strict up-exit steps: {n}; least pre-fork root weight {minw}; "
          f"minus (6(k^2-k)-6): {minw - (6 * (k * k - k) - 6)} sign {(minw - (6 * (k * k - k) - 6)).sign()}")


if __name__ == "__main__":
    main()
