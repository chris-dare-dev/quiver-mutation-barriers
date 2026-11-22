"""Review 3 of note 22, item 2 (closure): an independent certificate search for second-pass classes.

Note 22's certificates (families, E) are not stored: n4_tube_certify2.jsonl.gz keeps only a summary per class,
and the engine has no command that prints them.  So instead of re-checking those certificates, this builds its own
certificate for each sampled class with my own code (review23_n22_lib only), checks its closure explicitly for
n <= N, and compares its bottom of N with the stored one.

A certificate here is a finite set E and a list of families, every member of which is a quiver of V'(x):
  - base family: a frontier quiver z (reached from E by an allowed step, above the level LAM) and a map
    Phi(y) = pi(mu_u(y)), u a word of allowed steps at vertices other than a vertex g, pi a relabelling fixing g,
    such that pi(mu_u(z)) has the same labelled triangle opposite g, the same column signs and a higher level;
    members F(n) = Phi^n(z), computed by explicit mutation (every step checked allowed for n <= N);
  - derived family: D(n) = mu_m(P(n)) for a family P, kept for the n where that step is allowed (spikes, and
    the intermediate quivers of a walk).
Closure (explicit): every allowed step out of E lands in E or on a member of a family; for every family and
n <= N, every allowed step out of the member lands in E or on a member of a family (any index; members are indexed
by level as far as needed).  A frontier quiver for which no base family is found is added to E (a finite part above
LAM); E is capped.
Usage: python -I review23_n22_engine.py SAMPLE_SIZE PROCS > review23_n22_engine.log"""
import gzip
import json
import os
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L

N = 10                  # closure checked for members n = 0..N
CAPN = 4000             # members indexed per family at most
ECAP = 30000
FAMCAP = 600
DERIV = 5               # derived depth
WALK = 10               # depth of the walk search
GFIX = {g: [k for k, p in enumerate(L.PERMS) if p[g] == g] for g in range(4)}


class Fail(Exception):
    pass


def sgn(a):
    return (a > 0) - (a < 0)


class Fam:
    def __init__(self, kind, depth, z0=None, g=None, word=None, perm=None, parent=None, m=None):
        self.kind, self.depth = kind, depth
        self.z0, self.g, self.word, self.perm = z0, g, word, perm
        self.parent, self.m = parent, m
        self.mem = []           # labelled members, None where not a member
        self.nidx = 0
        self.top = 0

    def phi(self, y):
        for v in self.word:
            if not L.allowed(y, v):
                return None
            y = L.mutate(y, v)
        return L.relabel(y, self.perm)

    def get(self, n):
        while len(self.mem) <= n:
            k = len(self.mem)
            if self.kind == "base":
                if k == 0:
                    y = self.z0
                else:
                    prev = self.mem[k - 1]
                    y = self.phi(prev) if prev is not None else None
            else:
                p = self.parent.get(k)
                y = None
                if p is not None:
                    z = L.mutate(p, self.m)
                    if L.allowed(p, self.m, z):
                        y = z
            self.mem.append(y)
        return self.mem[n]


def find_tube(z):
    """A base family through z: (g, word, perm) or None."""
    gs = sorted(range(4), key=lambda g: (max(abs(a) for a in L.tri_entries(z, g)), g))
    for g in gs[:2]:
        T0 = L.tri_entries(z, g)
        col0 = L.column(z, g)
        if max(abs(a) for a in col0) <= max(abs(a) for a in T0):
            continue
        s0 = tuple(sgn(a) for a in col0)
        lz = L.level(z)
        frontier = [(z, (), None)]
        cands = []
        for depth in range(1, WALK + 1):
            nxt = []
            for y, w, last in frontier:
                for v in range(4):
                    if v == g or v == last:
                        continue
                    yz = L.mutate(y, v)
                    if not L.allowed(y, v, yz):
                        continue
                    w2 = w + (v,)
                    nxt.append((yz, w2, v))
                    for k in GFIX[g]:
                        p = L.relabel(yz, k)
                        if L.tri_entries(p, g) != T0:
                            continue
                        col = L.column(p, g)
                        if tuple(sgn(a) for a in col) != s0 or L.level(p) <= lz:
                            continue
                        if any(abs(a) < abs(b) for a, b in zip(col, col0)):
                            continue
                        cands.append((L.level(p), w2, k))
            if cands:
                break
            frontier = nxt
        for _, w2, k in sorted(cands):
            F = Fam("base", 0, z0=z, g=g, word=w2, perm=k)
            ok = True
            prevl = lz
            for n in range(1, N + 2):
                y = F.get(n)
                if y is None or L.tri_entries(y, g) != T0 or tuple(sgn(a) for a in L.column(y, g)) != s0 or L.level(y) <= prevl:
                    ok = False
                    break
                prevl = L.level(y)
            if ok:
                return g, w2, k
    return None


def tau_of(F):
    """tau of the recurrence e(n+3) = (tau+1)(e(n+2) - e(n+1)) + e(n) satisfied by F(0..7), or of F(2n)."""
    for step in (1, 2):
        ms = [F.get(step * n) for n in range(8)]
        if any(y is None for y in ms):
            return None
        taus = set()
        ok = True
        for a in range(6):
            s = [y[a] for y in ms]
            if len(set(s)) == 1:
                continue
            for n in range(5):
                d = s[n + 2] - s[n + 1]
                if d == 0:
                    if s[n + 3] != s[n]:
                        ok = False
                    continue
                q, r = divmod(s[n + 3] - s[n], d)
                if r:
                    ok = False
                taus.add(q - 1)
        if ok and len(taus) == 1:
            return (taus.pop(), step)
    return None


def certify(x, b, lam):
    t0 = time.time()
    fams = []
    index = {}
    E = {}
    stats = Counter()

    def index_to(level_target):
        for fid, F in enumerate(fams):
            while F.nidx <= N + 6 or (F.top < level_target and F.nidx < CAPN):
                y = F.get(F.nidx)
                if y is not None:
                    c = L.canon(y)
                    index.setdefault(c, (fid, F.nidx))
                    F.top = max(F.top, L.level(y))
                F.nidx += 1

    def lookup(c, lev):
        r = index.get(c)
        if r is None:
            index_to(lev)
            r = index.get(c)
        return r

    queue = []

    def add_fam(F):
        if len(fams) >= FAMCAP:
            raise Fail("family cap")
        fams.append(F)
        queue.append(len(fams) - 1)
        index_to(0)

    def add_base(z):
        tub = find_tube(z)
        if tub is None:
            return False
        g, w, k = tub
        B = Fam("base", 0, z0=z, g=g, word=w, perm=k)
        add_fam(B)
        # the intermediate quivers of the walk: derived families
        P = B
        for s in range(len(w) - 1):
            P = Fam("derived", 1, parent=P, m=w[s])
            add_fam(P)
        stats["base families"] += 1
        return True

    xs = L.canon(x)
    E[xs] = L.level(xs)
    stack = [xs]
    while True:
        while stack:
            if time.time() - t0 > 600:
                raise Fail("time")
            y = stack.pop()
            for m in range(4):
                z = L.mutate(y, m)
                if not L.allowed(y, m, z):
                    continue
                c = L.canon(z)
                lz = L.level(c)
                if c in E or lookup(c, lz) is not None:
                    continue
                if lz > lam and add_base(c):
                    stats["frontier quivers from E made bases"] += 1
                    continue
                if lz > lam:
                    stats["quivers above LAM put in E"] += 1
                if len(E) >= ECAP:
                    raise Fail("E cap")
                E[c] = lz
                stack.append(c)
        if not queue:
            break
        while queue:
            fid = queue.pop()
            F = fams[fid]
            for m in range(4):
                out = []
                for n in range(N + 1):
                    y = F.get(n)
                    if y is None:
                        continue
                    z = L.mutate(y, m)
                    if not L.allowed(y, m, z):
                        stats["family steps: strict up-exits"] += 1
                        continue
                    c = L.canon(z)
                    lz = L.level(c)
                    if c in E or lookup(c, lz) is not None:
                        stats["family steps: into E or a family"] += 1
                        continue
                    if lz <= lam:
                        if len(E) >= ECAP:
                            raise Fail("E cap")
                        E[c] = lz
                        stack.append(c)
                        stats["family steps: new quivers of E"] += 1
                        continue
                    out.append(n)
                if out:
                    if F.depth >= DERIV:
                        raise Fail("derived depth")
                    add_fam(Fam("derived", F.depth + 1, parent=F, m=m))
                    stats["derived families"] += 1
            if stack:
                break
    # final explicit recheck of the closure, independent of the order above
    bad = 0
    nchk = 0
    def inU(c):
        return c in E or index.get(c) is not None
    for c in list(E):
        for m in range(4):
            z = L.mutate(c, m)
            if L.allowed(c, m, z):
                nchk += 1
                cz = L.canon(z)
                if not (cz in E or lookup(cz, L.level(cz)) is not None):
                    bad += 1
    for F in fams:
        for n in range(N + 1):
            y = F.get(n)
            if y is None:
                continue
            for m in range(4):
                z = L.mutate(y, m)
                if L.allowed(y, m, z):
                    nchk += 1
                    cz = L.canon(z)
                    if not (cz in E or lookup(cz, L.level(cz)) is not None):
                        bad += 1
    lo = min(E.values())
    mem_lo = min((L.level(F.get(n)) for F in fams for n in range(N + 1) if F.get(n) is not None), default=None)
    bot = sorted(c for c, l in E.items() if l == lo)
    taus = Counter()
    for F in fams:
        if F.kind == "base":
            taus[tau_of(F)] += 1
    return {"E": len(E), "fams": len(fams), "lo": lo, "mem_lo": mem_lo, "kid": list(bot[0]), "nbot": len(bot),
            "mkid": list(min(L.canon(L.neg(c)) for c in bot)), "closure_steps": nchk, "closure_failures": bad,
            "taus": sorted((str(k), v) for k, v in taus.items()), "stats": dict(stats), "t": round(time.time() - t0, 1)}


def job(a):
    r, why = a
    x = tuple(r["x"])
    out = {"i": r["i"], "b": r["b"], "why": why}
    for lam in (64 * r["b"], 512 * r["b"], 4096 * r["b"]):
        try:
            res = certify(x, r["b"], lam)
            res["lam"] = lam
            out.update(res)
            out["status"] = "certified"
            break
        except Fail as e:
            out["status"] = "failed: " + str(e)
            out["lam"] = lam
    return out


def main():
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with gzip.open("n4_tube_certify2.jsonl.gz", "rt") as f:
        recs = [json.loads(l) for l in f]
    cert = {r["i"]: r for r in recs if r["status"] == "certified"}
    with gzip.open("n4_tube_classify.jsonl.gz", "rt") as f:
        cls = {r["i"]: r for r in (json.loads(l) for l in f)}
    why = {}
    if 1034 in cert:
        why[1034] = "class 1034"
    for key, name in ((lambda r: r["nodes"], "most families"), (lambda r: r["npoly"], "most polynomial families"),
                      (lambda r: r["nE"], "largest E"), (lambda r: r["L"], "largest L"), (lambda r: -r["bK"] + r["b"], "bottom above census")):
        for r in sorted(cert.values(), key=lambda r: (-key(r), r["i"]))[:8]:
            why.setdefault(r["i"], name)
    slow = [i for i in cert if cls[i]["n2"] / max(1, cls[i]["n1"]) < 2.5]
    for i in random.Random(5).sample(sorted(slow), min(10, len(slow))):
        why.setdefault(i, "slow")
    rest = [i for i in sorted(cert) if i not in why]
    for i in random.Random(73).sample(rest, max(0, size - len(why))):
        why[i] = "random"
    jobs = [(cert[i], why[i]) for i in sorted(why)]
    print(f"sample: {len(jobs)} classes: {dict(Counter(why.values()))}", flush=True)
    t0 = time.time()
    tab = Counter()
    lines = []
    with Pool(procs) as pool:
        for o in pool.imap_unordered(job, jobs):
            r = cert[o["i"]]
            tab[o["status"]] += 1
            if o["status"] == "certified":
                same = (o["lo"] == r["bK"], o["kid"] == r["kid"], o["mkid"] == r["mkid"], o["nbot"] == r["nbot"])
                tab["certified: bottom level, kid, mkid, nbot all equal"] += all(same)
                tab["certified: closure failures (should be 0)"] += o["closure_failures"] > 0
                tab["certified: a family member below the bottom of E"] += o["mem_lo"] is not None and o["mem_lo"] < o["lo"]
                tab["closure steps checked"] += o["closure_steps"]
                if not all(same):
                    lines.append(("DIFFERENT BOTTOM", o, {k: r[k] for k in ("bK", "kid", "mkid", "nbot")}))
            print(json.dumps(o, separators=(",", ":")), flush=True)
    print(f"\nsummary ({time.time() - t0:.0f}s):")
    for k, v in tab.items():
        print(f"   {k}: {v}")
    for l in lines:
        print("  ", l)


if __name__ == "__main__":
    main()
