"""
review19_n13_units.py -- unit checks of the independent library review19_n13_lib against the
paper's (arXiv 2610.36179) worked examples and against Fomin-Neville's definitions.
Run: python -I ../verify/review19_n13_units.py > review19_n13_units.log
"""
import itertools
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review19_n13_lib as L  # noqa: E402

ok_all = True


def check(name, cond, info=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {info}", flush=True)


t0 = time.time()
# 1. Example 5.4
Q = (-3, -2, 2, 0, 3, -3)
pm = L.proper_markov(Q)
check("Ex 5.4: one proper wiggle class", len(pm) == 1, f"{[(m, c) for m, c in pm]}")
check("Ex 5.4: Markov value 41", pm[0][0] == 41)
check("Ex 5.4: p^2 = 225", L.pfaffian(Q) ** 2 == 225)
check("Ex 5.4: H = 41", L.H_of(Q) == 41)
A = (0, 0, 3, 5, 1, 1)
check("Ex 5.4: (0,0,3,5,1,1) acyclic", L.is_acyclic(A))
check("Ex 5.4: (0,0,3,5,1,1) has (M,p^2) = (41,225) in 1<2<3<4",
      (L.markov_value(A, (0, 1, 2, 3)), L.pfaffian(A) ** 2) == (41, 225))
# labelled component inside height 41
seen = {Q}
todo = [Q]
while todo:
    x = todo.pop()
    for y in L.neighbours(x):
        if L.ht(y) <= 41 and y not in seen:
            seen.add(y)
            todo.append(y)
check("Ex 5.4: labelled component inside height 41 has 238 quivers", len(seen) == 238, f"got {len(seen)}")
check("Ex 5.4: none acyclic", not any(L.is_acyclic(x) for x in seen))
check("Ex 5.4: none has tri / vortex / Lemma-2.4 exclusion", not any(L.certificate(x) for x in seen))
check("Ex 5.4: up to relabelling 119", len({L.canon(x) for x in seen}) == 119, f"got {len({L.canon(x) for x in seen})}")
check("Ex 5.4: oriented 4-cycle (3,-2,0,0,9,-1) is in the class (bottleneck search, cap 200)",
      L.bottleneck_to(Q, (3, -2, 0, 0, 9, -1), 200) is not None, f"bottleneck {L.bottleneck_to(Q, (3, -2, 0, 0, 9, -1), 200)}")
r = L.my_resolve(Q)
check("Ex 5.4: own resolve gives cor52 with K = 41", r[0] == "cyclic" and r[1] == "cor52" and r[2] == 41, f"{r[:3]}")

# 2. Remark 2.5
for k in range(1, 9):
    Lk = (k, 0, 0, 1, 0, k)
    check(f"Rem 2.5 k={k}: M = 2k^2+1, p = k^2",
          L.markov_value(Lk, (0, 1, 2, 3)) == 2 * k * k + 1 and L.pfaffian(Lk) == k * k and L.is_acyclic(Lk))

# 3. Remark 5.6
for x in range(1, 11):
    G = (x, x, 0, 1, x, -1)
    m = L.markov_value(G, (0, 1, 3, 2))
    mu4 = L.mutate(G, 3)
    pcs = [c for _, c in L.proper_markov(G)]
    topo_in_proper = any((0, 1, 3, 2) in c for c in pcs)
    check(f"Rem 5.6 x={x}: acyclic, m = x^3+4x^2+x+2 on 1<2<4<3, mu4 = (x,x,0,x+1,-x,1), topo class proper",
          L.is_acyclic(G) and m == x ** 3 + 4 * x * x + x + 2 and mu4 == (x, x, 0, x + 1, -x, 1) and topo_in_proper,
          f"m={m}")

# 4. Proposition 6.1
box = (-2, 0, 2, -2, 0, -2)
mb = L.mutate(box, 0)
pmb = L.proper_markov(mb)
check("Prop 6.1: mu1(box) = (2,0,-2,-2,4,-2)", mb == (2, 0, -2, -2, 4, -2))
check("Prop 6.1: mu1(box) has one proper class with M = 0", len(pmb) == 1 and pmb[0][0] == 0, f"{pmb}")
check("Prop 6.1: mu1(box) is Lemma-2.4 excluded", L.lemma24_excluded(mb))

# 5. dreaded torus
QT = (-2, 1, 1, -1, -1, -1)
check("dreaded torus: each mutation is a relabelling", all(L.canon(L.mutate(QT, k)) == L.canon(QT) for k in range(4)))
check("dreaded torus: not acyclic, no tri/vortex/l24", (not L.is_acyclic(QT)) and L.certificate(QT) is None)

# 6. FN Prop 13.2 on all 729 sign patterns; the two forms of FN Def 13.1
bad = 0
nv = 0
for s in itertools.product((-1, 0, 1), repeat=6):
    v1, v2 = L.is_vortex(s), L.is_vortex_first_form(s)
    nopc = len(L.proper_class_reps(s)) == 0
    nv += v1
    if not (v1 == v2 == nopc):
        bad += 1
        print("   mismatch", s, v1, v2, nopc)
check("FN Prop 13.2: vortex <=> no proper wiggle class, both forms of Def 13.1 agree, all 729 sign patterns",
      bad == 0, f"{nv} vortex sign patterns")

# 7. algebraic sanity on random quivers
rng = random.Random(49)
n_ok = 0
N = 20000
for _ in range(N):
    h = rng.randint(1, 18)
    t = tuple(rng.randint(-h, h) for _ in range(6))
    good = True
    # rotation invariance of M over all 24 linear orders
    for w in L.ORDS:
        vals = {L.markov_value(t, w[r:] + w[:r]) for r in range(4)}
        good &= len(vals) == 1
    # involution and relabelling equivariance (paper (3)): mu_{pi^-1(k)}(Q^pi) = (mu_k Q)^pi
    for k in range(4):
        good &= L.mutate(L.mutate(t, k), k) == t
        good &= abs(L.pfaffian(L.mutate(t, k))) == abs(L.pfaffian(t))
    a = rng.randrange(24)
    pi = L.PERMS[a]
    inv = [pi.index(i) for i in range(4)]
    for k in range(4):
        good &= L.mutate(L.relabel(t, a), inv[k]) == L.relabel(L.mutate(t, k), a)
    # invariants under relabelling
    u = L.relabel(t, a)
    good &= L.is_acyclic(u) == L.is_acyclic(t) and L.is_connected(u) == L.is_connected(t)
    good &= L.cyclic_triangle(u) == L.cyclic_triangle(t) and L.is_vortex(u) == L.is_vortex(t)
    good &= L.H_of(u) == L.H_of(t) and L.lemma24_excluded(u) == L.lemma24_excluded(t)
    good &= sorted(m for m, _ in L.proper_markov(u)) == sorted(m for m, _ in L.proper_markov(t))
    # reversal keeps H (paper: reversing arrows and ordering keeps M)
    rv = tuple(-x for x in t)
    good &= L.H_of(rv) == L.H_of(t)
    n_ok += good
check("random height<=18: M rotation-invariant; mu involutive; |p| invariant; (3) holds; invariants relabelling-"
      "invariant; H reversal-invariant", n_ok == N, f"{n_ok}/{N}")

# 8. acyclic quivers: topological class proper, entries >= 0, Lemma 2.4 inequalities for connected ones
n_ok = n_ac = 0
for _ in range(200000):
    h = rng.randint(1, 18)
    t = tuple(rng.randint(-h, h) for _ in range(6))
    if not L.is_acyclic(t):
        continue
    n_ac += 1
    B = L.full(t)
    topo = [w for w in itertools.permutations(range(4)) if all(B[w[j]][w[i]] <= 0 for i in range(4) for j in range(i + 1, 4))]
    w = topo[0]
    pcs = L.proper_markov(t)
    cls = [c for _, c in pcs if L._norm(list(w)) in c]
    m = L.markov_value(t, w)
    good = len(cls) == 1 and [mm for mm, c in pcs if L._norm(list(w)) in c][0] == m
    if L.is_connected(t):
        good &= m >= 3 and 2 * abs(L.pfaffian(t)) < m
        good &= not L.lemma24_excluded(t)
    good &= not L.cyclic_triangle(t) and not L.is_vortex(t)
    n_ok += good
check("random acyclic quivers: topological class is proper, its M satisfies Lemma 2.4; no cert", n_ok == n_ac,
      f"{n_ok}/{n_ac}")

# 9. Prop 2.1 triangle criterion versus brute force on 3-vertex quivers: the oriented triangles with
#    x,y,z>=2 and Markov <= 4 never reach an acyclic triangle within a generous height bound, and the others do.
def mut3(t, k):
    B = [[0] * 3 for _ in range(3)]
    (B[0][1], B[0][2], B[1][2]) = t
    for i, j in ((0, 1), (0, 2), (1, 2)):
        B[j][i] = -B[i][j]
    out = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        if k in (i, j):
            out.append(-B[i][j])
        else:
            out.append(B[i][j] + max(B[i][k], 0) * max(B[k][j], 0) - max(-B[i][k], 0) * max(-B[k][j], 0))
    return tuple(out)


def acyc3(t):
    x, y, z = t[0], t[2], -t[1]       # 0->1, 1->2, 2->0
    return not ((x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0))


bad = 0
for t in itertools.product(range(-8, 9), repeat=3):
    x, y, z = t[0], t[2], -t[1]
    crit = ((x > 0 and y > 0 and z > 0) or (x < 0 and y < 0 and z < 0)) and min(abs(x), abs(y), abs(z)) >= 2 and \
        x * x + y * y + z * z - abs(x * y * z) <= 4
    seen = {t}
    q = [t]
    found = acyc3(t)
    while q and not found:
        u = q.pop()
        for k in range(3):
            v = mut3(u, k)
            if max(map(abs, v)) <= 400 and v not in seen:
                seen.add(v)
                q.append(v)
                if acyc3(v):
                    found = True
                    break
    if crit == found:
        bad += 1
check("Prop 2.1 on all 3-vertex quivers with entries in [-8,8]: criterion <=> no acyclic quiver within height 400",
      bad == 0, f"{bad} mismatches")
print(f"ALL {'PASS' if ok_all else 'FAIL'} ({time.time() - t0:.0f}s)")
