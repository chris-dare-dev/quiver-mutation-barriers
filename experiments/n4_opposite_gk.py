"""The core of the class of G_k for every k >= K0, with polynomial entries (note 14).

A quiver is a 6-tuple of polynomials in k.  Comparisons are decided for all integers k >= K0 at once:
p > 0 for all k >= K0 when p(j + K0) has non-negative coefficients and a positive constant term.  Any
comparison that cannot be decided this way raises Undetermined.  The functions of n4_opposite.py
(mutate, fork_return, prefork_returns, exit_returns) run unchanged on these tuples.

  python -I n4_opposite_gk.py [K0]
"""
import os
import sys
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n4_opposite as O

K0 = 3


class Undetermined(Exception):
    pass


class Poly:
    __slots__ = ("c",)

    def __init__(self, c):
        c = list(c)
        while c and c[-1] == 0:
            c.pop()
        self.c = tuple(c)

    @staticmethod
    def lift(x):
        return x if isinstance(x, Poly) else Poly([x])

    def __add__(self, o):
        o = Poly.lift(o)
        n = max(len(self.c), len(o.c))
        return Poly([(self.c[i] if i < len(self.c) else 0) + (o.c[i] if i < len(o.c) else 0) for i in range(n)])
    __radd__ = __add__

    def __neg__(self):
        return Poly([-x for x in self.c])

    def __sub__(self, o):
        return self + (-Poly.lift(o))

    def __rsub__(self, o):
        return Poly.lift(o) - self

    def __mul__(self, o):
        o = Poly.lift(o)
        out = [0] * (len(self.c) + len(o.c))
        for i, a in enumerate(self.c):
            for j, b in enumerate(o.c):
                out[i + j] += a * b
        return Poly(out)
    __rmul__ = __mul__

    def sign(self):
        """'+', '-', '0', '>=0' or '<=0': what is known of the sign for every integer k >= K0."""
        if not self.c:
            return "0"
        sh = [sum(self.c[i] * comb(i, j) * K0 ** (i - j) for i in range(j, len(self.c))) for j in range(len(self.c))]
        if all(x >= 0 for x in sh):
            return "+" if sh[0] > 0 else ">=0"
        if all(x <= 0 for x in sh):
            return "-" if sh[0] < 0 else "<=0"
        raise Undetermined(f"sign of {self} for k >= {K0}")

    def _decide(self, o, true_if, false_if, what):
        s = (self - o).sign()
        if s in true_if:
            return True
        if s in false_if:
            return False
        raise Undetermined(f"{self} {what} {o} for k >= {K0}")

    def __abs__(self):
        return self if self.sign() in ("+", "0", ">=0") else -self

    def __eq__(self, o):
        return self._decide(o, ("0",), ("+", "-"), "==")

    def __ne__(self, o):
        return not self.__eq__(o)

    def __lt__(self, o):
        return self._decide(o, ("-",), ("+", "0", ">=0"), "<")

    def __gt__(self, o):
        return self._decide(o, ("+",), ("-", "0", "<=0"), ">")

    def __le__(self, o):
        return self._decide(o, ("-", "0", "<=0"), ("+",), "<=")

    def __ge__(self, o):
        return self._decide(o, ("+", "0", ">=0"), ("-",), ">=")

    def __hash__(self):
        return hash(self.c)

    def __call__(self, k):
        return sum(a * k ** i for i, a in enumerate(self.c))

    def __repr__(self):
        return "+".join(f"{a}k^{i}" if i else f"{a}" for i, a in enumerate(self.c) if a) or "0"


def relabellings(t):
    return [tuple(s * t[a] for a, s in r) for r in O.RELAB]


def same_up_to_relabelling(x, y):
    return any(all((a - b).c == () for a, b in zip(x, r)) for r in relabellings(y))


def main():
    global K0
    if len(sys.argv) > 1:
        K0 = int(sys.argv[1])
    k = Poly([0, 1])
    G = (k, -k, -k, Poly([0]), k, -(k - 1))          # rows (0,k,-k,-k), (-k,0,0,k), (k,0,0,-(k-1)), (k,-k,k-1,0)
    core = [G]
    names = ["G_k"]
    edges = []
    exits = []
    i = 0
    while i < len(core):
        x = core[i]
        ex_x = O.exit_returns(x)
        for m in range(4):
            y = O.mutate(x, m)
            if m not in ex_x and m in O.exit_returns(y):
                kind = "fork" if O.fork_return(y) == m else "pre-fork"
                exits.append((i, m, kind, y))
                continue
            for j, z in enumerate(core):
                if same_up_to_relabelling(y, z):
                    break
            else:
                core.append(y)
                names.append(f"X{len(core) - 1}")
                j = len(core) - 1
            edges.append((i, m, j))
        i += 1
        if len(core) > 50:
            raise SystemExit("more than 50 quivers")
    for j, x in enumerate(core):
        if same_up_to_relabelling(x, tuple(-a for a in G)):
            names[j] = "-G_k"
    print(f"valid for every integer k >= {K0}")
    print(f"core: {len(core)} quivers")
    for j, x in enumerate(core):
        lv = max((abs(a) for a in x), key=lambda p: p(10 ** 6))
        fixed = same_up_to_relabelling(x, tuple(-a for a in x))
        print(f"  {names[j]:5s} {x}   level {lv}   isomorphic to its opposite: {fixed}")
    print("steps inside the core (quiver, vertex, quiver):", [(names[a], m, names[b]) for a, m, b in edges])
    print(f"strict up-exit steps from the core: {len(exits)}")
    for a, m, kind, y in exits:
        lv = max((abs(e) for e in y), key=lambda p: p(10 ** 6))
        print(f"  from {names[a]} at vertex {m}: {kind} with return vertex {m}, level {lv}, {y}")
    # every quiver of a far region has at least as many arrows as its root (Ervin, Corollary 4.25), so its
    # level is at least a sixth of the root's weight; for a fork root the level itself does not drop
    k = Poly([0, 1])
    target = k * k - k
    ok_fork = all(max((abs(e) for e in y), key=lambda p: p(10 ** 6)) >= target for a, m, kind, y in exits if kind == "fork")
    ok_pre = all(sum((abs(e) for e in y), Poly([0])) + 6 > 6 * target for a, m, kind, y in exits if kind == "pre-fork")
    print(f"every fork root has level >= k^2 - k: {ok_fork}; every pre-fork root has weight > 6(k^2 - k) - 6: {ok_pre}")
    # strongly connected: every quiver reaches every other inside the core
    reach = {a: {a} for a in range(len(core))}
    changed = True
    while changed:
        changed = False
        for a, m, b in edges:
            for s in reach.values():
                if a in s and b not in s:
                    s.add(b)
                    changed = True
    print("every quiver of the core reaches every other by steps inside it:", all(len(s) == len(core) for s in reach.values()))


if __name__ == "__main__":
    main()
