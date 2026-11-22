#!/usr/bin/env python
"""
review23_n21_review.py -- independent review of note 21 (barriers and the mutation-path one-way function).

Own code.  It does not import, copy or adapt owf_barrier.py, np_corridor.py, np_rowwalk.py, n4_doors.py or
np_barrier.c.  The searches run in review23_n21_search.c (also own code, compiled to ~/.cache/qmb-review23/n21/).
The note's .jsonl files are read as data only.  The one exception is item 3: owf_barrier.py is CALLED AS A BLACK BOX
by the separate driver review23_n21_blackbox.py (a subprocess), which hands it instances built here and writes the
routes it returns to ~/.cache/qmb-review23/n21/; this script then replays those routes with its own mutation.

Subcommands: selftest, generic, shortest, jsonl (recount the note's files), attack, rows, perturb, rwalk.
Quiver tuples are upper triangles in row order (b01, b02, ..., b12, ...).  [x]_+ = max(x, 0).
"""
import itertools
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results
CACHE = os.path.expanduser("~/.cache/qmb-review23/n21")
os.makedirs(CACHE, exist_ok=True)
BIN = os.path.join(CACHE, "p72search")
PY = sys.executable


# ----------------------------------------------------------------------------- quivers (Python integers)
def full(u, n):
    B = [[0] * n for _ in range(n)]
    t = 0
    for i in range(n):
        for j in range(i + 1, n):
            B[i][j], B[j][i] = u[t], -u[t]
            t += 1
    return B


def upper(B):
    n = len(B)
    return [B[i][j] for i in range(n) for j in range(i + 1, n)]


def nverts(u):
    m = len(u)
    n = 2
    while n * (n - 1) // 2 < m:
        n += 1
    return n


def mutate(B, k):
    """b'_ij = -b_ij if k in {i, j}; else b_ij + [b_ik]_+ [b_kj]_+ - [-b_ik]_+ [-b_kj]_+."""
    n = len(B)
    C = [row[:] for row in B]
    for i in range(n):
        for j in range(n):
            if i == k or j == k:
                C[i][j] = -B[i][j]
            else:
                x, y = B[i][k], B[k][j]
                if x > 0 and y > 0:
                    C[i][j] = B[i][j] + x * y
                elif x < 0 and y < 0:
                    C[i][j] = B[i][j] - x * y
    return C


def height(B):
    return max(abs(v) for row in B for v in row)


def negq(B):
    return [[-v for v in row] for row in B]


def relabel(B, perm):
    """entry (i, j) of the result is B[perm[i]][perm[j]]"""
    n = len(B)
    return [[B[perm[i]][perm[j]] for j in range(n)] for i in range(n)]


def brute_canon(B):
    n = len(B)
    return min(tuple(B[p[i]][p[j]] for i in range(n) for j in range(i + 1, n)) for p in itertools.permutations(range(n)))


def isomorphic(X, Y):
    return brute_canon(X) == brute_canon(Y)


# ----------------------------------------------------------------------------- families, from the notes' statements
def fam(name, par):
    """(upper tuple, H, w, closed-form route length or None)."""
    if name == "R":            # note 15, Theorem 15.13
        b = par
        return [-b, -b, b - 1, -2, b - 2, -b], 2 * b * b - 3 * b - 3, b, (b * (b - 1) // 2 + b + 1 if b % 2 == 0 else None)
    if name == "Qt":           # note 15, Theorem 15.6
        t = par
        return [-t * t, -(t * t - 1), 2 * t, -2, t * (t - 1), -t * t], 2 * t ** 4 - t ** 3 - t * t + 2 * t, t * t, 4 * t ** 3 - 2 * t * t + 4
    if name == "P+":           # note 16, Theorem 16.4
        t = par
        return ([1, -(t * t - 1), -t * (t - 1), t * t, -2, t * (t - 1), t * t, -t * t, t * t - 1, -2 * t],
                2 * t ** 5 - t ** 4 + t * t - 1, t * t, 4 * t ** 3 - 2 * t * t + 4)
    if name == "Qa":           # note 18, Theorem 18.4
        a = par
        H = 4 * a ** 3 - 3 * a * a + ((5 * a - 1) // 2 if a % 2 else (3 * a - 4) // 2)
        return ([-(a - 3), a - 2, a + 1, -(a + 1), -(a + 1), -a, 2, -2, -a, -(a + 1)], H, a + 1,
                (2 * a + 2) * (4 * a * a - a + 6))
    raise ValueError(name)


# ----------------------------------------------------------------------------- the C engine
def run_c(lines, seed=1):
    out = subprocess.run([BIN, str(seed)], input="\n".join(lines) + "\n", capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return [json.loads(l) if l.startswith("{") else l for l in out.stdout.strip().splitlines()]


def c_minimax(u, w, cap, tie=0, prune=0, budget=20_000_000, seed=1):
    n = nverts(u)
    return run_c(["minimax %d %d %d %d %d %d %s" % (n, w, cap, tie, prune, budget, " ".join(map(str, u)))], seed)[0]


def c_comp(u, bound, budget=20_000_000, prune=0, w=0):
    n = nverts(u)
    return run_c(["comp %d %d %d %d %d %s" % (n, bound, budget, prune, w, " ".join(map(str, u)))])[0]


def c_bibfs(ua, ub, bound, budget, prunew=0):
    n = nverts(ua)
    return run_c(["bibfs %d %d %d %d %s %s" % (n, bound, budget, prunew, " ".join(map(str, ua)), " ".join(map(str, ub)))])[0]


def c_canon(u):
    n = nverts(u)
    return run_c(["canon %d %s" % (n, " ".join(map(str, u)))])[0]


def c_isfork(us):
    lines = ["isfork %d %s" % (nverts(u), " ".join(map(str, u))) for u in us]
    return [int(x) for x in run_c(lines)]


# ----------------------------------------------------------------------------- own fork test in Python (cross-check)
def acyclic(B, vs):
    vs = list(vs)
    while vs:
        src = [v for v in vs if not any(B[u][v] > 0 for u in vs)]
        if not src:
            return False
        vs = [v for v in vs if v not in src]
    return True


def py_fork(B):
    n = len(B)
    if any(abs(B[i][j]) < 2 for i in range(n) for j in range(i + 1, n)):
        return -1
    if acyclic(B, range(n)):
        return -1
    for r in range(n):
        ins = [v for v in range(n) if v != r and B[v][r] > 0]
        outs = [v for v in range(n) if v != r and B[r][v] > 0]
        if all(B[j][i] > B[i][r] and B[j][i] > B[r][j] for i in ins for j in outs) and acyclic(B, ins) and acyclic(B, outs):
            return r
    return -1


# ----------------------------------------------------------------------------- selftest
def cmd_selftest():
    rng = random.Random(7)
    ok = True
    # 1. mutation: the C engine is exercised through replay files; here, Python mutation is an involution and
    #    commutes with relabelling and with negation
    bad = 0
    for _ in range(3000):
        n = rng.choice([4, 5, 6])
        B = full([rng.randint(-6, 6) for _ in range(n * (n - 1) // 2)], n)
        k = rng.randrange(n)
        C = mutate(B, k)
        perm = list(range(n)); rng.shuffle(perm)
        inv = [0] * n
        for i, p in enumerate(perm):
            inv[p] = i
        bad += mutate(C, k) != B
        bad += relabel(C, perm) != mutate(relabel(B, perm), inv[k])
        bad += negq(C) != mutate(negq(B), k)
    print("python mutation: involution, relabelling, negation on 3000 random quivers: %d failures" % bad)
    ok &= bad == 0
    # 2. canonical form of the C engine against brute force (equal iff isomorphic), n = 4, 5, 6
    bad = 0
    pairs = 0
    for _ in range(400):
        n = rng.choice([4, 5, 6])
        u = [rng.choice([-2, -1, 0, 1, 2]) for _ in range(n * (n - 1) // 2)]
        B = full(u, n)
        perm = list(range(n)); rng.shuffle(perm)
        v = upper(relabel(B, perm))
        # a near-copy: change one entry; often isomorphic, often not
        u2 = list(u); u2[rng.randrange(len(u2))] *= -1
        k1, k2, k3 = c_canon(u), c_canon(v), c_canon(u2)
        bad += k1 != k2
        bad += (k1 == k3) != (brute_canon(B) == brute_canon(full(u2, n)))
        pairs += 2
    print("C canonical form: relabelling-invariant and exact on %d pairs: %d failures" % (pairs, bad))
    ok &= bad == 0
    # 3. fork test: C against Python, and Warkentin's Lemma 2.5 on random forks (mu_k of a fork, k != r, is a fork
    #    with point of return k and no smaller entry)
    bad = cnt = 0
    us = []
    for _ in range(4000):
        n = rng.choice([4, 5])
        us.append([rng.choice([-1, 1]) * rng.randint(2, 9) for _ in range(n * (n - 1) // 2)])
    cf = c_isfork(us)
    for u, r in zip(us, cf):
        B = full(u, len(full(u, nverts(u))))
        pr = py_fork(B)
        bad += (r >= 0) != (pr >= 0) or (r >= 0 and r != pr)
        if pr >= 0:
            cnt += 1
            for k in range(len(B)):
                if k == pr:
                    continue
                C = mutate(B, k)
                bad += py_fork(C) != k
                bad += any(abs(C[i][j]) < abs(B[i][j]) for i in range(len(B)) for j in range(len(B)))
    print("fork test: C = Python on 4000 random abundant quivers (%d forks); Lemma 2.5 on their mutations: %d failures" % (cnt, bad))
    ok &= bad == 0 and cnt > 50
    # 4. known values from notes 15, 16 and 18 (own searches)
    checks = []
    for name, par, below_known in [("R", 6, None), ("R", 8, None), ("Qt", 3, 100), ("Qt", 4, 235), ("Qt", 5, 463),
                                   ("Qt", 6, 806), ("P+", 2, 157), ("P+", 3, 173), ("P+", 4, 381), ("Qa", 2, 525),
                                   ("Qa", 3, 3907), ("Qa", 4, 13645)]:
        u, H, w, _ = fam(name, par)
        r = c_minimax(u, w, 10 * H)
        c = c_comp(u, H - 1, w=w)
        good = r["status"] == "found" and r["level"] == H and r["target_is_neg"] == 1 and c["low"] == 1
        if below_known is not None:
            good &= c["size"] == below_known
        checks.append(good)
        print("  %s %d: escape level %s (H = %d), target -Q: %s, component below H %d (part: %s), low quivers in it %d"
              % (name, par, r["level"], H, r["target_is_neg"], c["size"], below_known, c["low"]))
    ok &= all(checks)
    # 5. own replay of the closed-form routes is not available; instead the C replay against Python replay
    bad = 0
    for _ in range(200):
        n = rng.choice([4, 5])
        u = [rng.randint(-3, 3) for _ in range(n * (n - 1) // 2)]
        word = [rng.randrange(n) for _ in range(rng.randint(1, 12))]
        B = full(u, n)
        hmax = height(B)
        for v in word:
            B = mutate(B, v)
            hmax = max(hmax, height(B))
        res = c_replay(u, upper(B), [("m", v) for v in word], bound=10 ** 18)
        bad += not (res["end_equals_target"] == 1 and res["max_height"] == hmax and res["length"] == len(word))
    print("C literal replay = Python replay on 200 random words: %d failures" % bad)
    ok &= bad == 0
    print("ALL OK" if ok else "FAILED")


def write_prog(path, u, target, ops, bound):
    n = nverts(u)
    with open(path, "w") as f:
        f.write("%d %d\n%s\n%s\n" % (n, bound, " ".join(map(str, u)), " ".join(map(str, target))))

        def emit(ops):
            for op in ops:
                if op[0] == "m":
                    f.write("m %d\n" % op[1])
                elif op[0] == "run":
                    f.write("run %d %d %d\n" % (op[1], op[2], op[3]))
                elif op[0] == "rep":
                    f.write("rep %d\n" % op[2])
                    emit(op[1])
                    f.write("end\n")
                else:
                    raise ValueError(op)
        emit(ops)
        f.write("end\n")


def c_replay(u, target, ops, bound, tag="tmp"):
    path = os.path.join(CACHE, "prog_%s_%d.txt" % (tag, os.getpid()))
    write_prog(path, u, target, ops, bound)
    r = run_c(["replayfile " + path])[0]
    os.remove(path)
    return r




# ----------------------------------------------------------------------------- item 1: the generic attacker
def cmd_generic(*members):
    """For each member: the component strictly below H (bound H - 1), the component at bound H (every quiver of
    bottleneck <= H: the most a minimax search can pop before it must have popped -Q), the minimax search with four
    tie-breaks at the last level, with and without fork pruning, and the component at the A3 level 4^k >= H."""
    members = members or ["R:20", "Qt:6", "P+:8", "Qa:6", "Qa:12"]
    for spec in members:
        name, par = spec.split(":")
        par = int(par)
        u, H, w, Lcf = fam(name, par)
        L4 = 4
        while L4 < H:
            L4 *= 4
        t0 = time.time()
        row = {"member": spec, "w": w, "H": H, "L_closed_form": Lcf, "L4": L4}
        for prune in (0, 1):
            below = c_comp(u, H - 1, budget=40_000_000, prune=prune, w=w)
            atH = c_comp(u, H, budget=40_000_000, prune=prune, w=w)
            runs = []
            for tie, seed in [(0, 1), (1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]:
                r = c_minimax(u, w, H, tie=tie, prune=prune, budget=40_000_000, seed=seed)
                runs.append({"tie": tie, "seed": seed, "status": r["status"], "level": r["level"], "popped": r["popped"],
                             "below": r["below"], "forks_popped": r["forks_popped"], "path_len": r["path_len"],
                             "target_is_neg": r["target_is_neg"]})
            row["prune%d" % prune] = {"below_H": below, "at_H": atH, "minimax": runs}
        if L4 <= 16384:
            row["comp_L4"] = c_comp(u, L4, budget=40_000_000, prune=0, w=w)
        row["time"] = round(time.time() - t0, 1)
        print(json.dumps(row), flush=True)


# ----------------------------------------------------------------------------- item 2: fewest mutations above H
def cmd_shortest(budget_pruned="30000000", budget_all="6000000", *members):
    """Bidirectional BFS for the fewest mutations from Q to a relabelling of -Q inside a bound, with forks higher
    than w skipped (exact by Lemma 15.5: a shortest route has no immediate repeat, so it is reduced) and over every
    quiver."""
    members = members or ["R:6", "R:8", "Qt:3", "P+:2", "P+:3", "Qa:3", "Qa:2"]
    for spec in members:
        name, par = spec.split(":")
        par = int(par)
        u, H, w, _ = fam(name, par)
        nu = upper(negq(full(u, nverts(u))))
        for label, B in [("H", H), ("4H", 4 * H), ("16H", 16 * H), ("256H", 256 * H), ("2^20", 2 ** 20), ("2^40", 2 ** 40)]:
            if B < H:
                continue
            row = {"member": spec, "w": w, "H": H, "bound": label}
            t0 = time.time()
            row["pruned"] = c_bibfs(u, nu, B, int(budget_pruned), prunew=w)
            row["all"] = c_bibfs(u, nu, B, int(budget_all), prunew=0)
            row["time"] = round(time.time() - t0, 1)
            print(json.dumps(row), flush=True)


# ----------------------------------------------------------------------------- item 3: the structure-aware attacker
def rev_ops(ops, inv):
    """The reverse of a compressed route, with every vertex v renamed inv[v].  The literal word of
    ('run', p, q, l) is p, q, p, ... (l letters), so its reverse is a run that starts at the last letter."""
    out = []
    for op in reversed(ops):
        if op[0] == "m":
            out.append(("m", inv[op[1]]))
        elif op[0] == "run":
            _, p, q, l = op
            last, other = (p, q) if l % 2 == 1 else (q, p)
            out.append(("run", inv[last], inv[other], l))
        else:
            out.append(("rep", rev_ops(op[1], inv), op[2]))
    return out


def norm_ops(ops):
    return [("m", op[1]) if op[0] == "m" else ("run", op[1], op[2], op[3]) if op[0] == "run" else ("rep", norm_ops(op[1]), op[2]) for op in ops]


def ops_len(ops):
    return sum(1 if op[0] == "m" else op[3] if op[0] == "run" else op[2] * ops_len(op[1]) for op in ops)


def ops_size(ops):
    return sum(1 + (ops_size(op[1]) if op[0] == "rep" else 0) for op in ops)


def expand_ops(ops):
    w = []
    for op in ops:
        if op[0] == "m":
            w.append(op[1])
        elif op[0] == "run":
            w.extend(op[1] if i % 2 == 0 else op[2] for i in range(op[3]))
        else:
            sub = expand_ops(op[1])
            for _ in range(op[2]):
                w.extend(sub)
    return w


def compose_route(pc):
    """The route from Q to a relabelling of Q' from the attacker's pieces: Q's side, then the other side reversed and
    renamed (vertex v of the meeting quiver Y1 is vertex inv[v] of Y0, since Y0 = relabel(Y1, perm))."""
    perm = pc["perm"]
    inv = [0] * len(perm)
    for i, j in enumerate(perm):
        inv[j] = i
    a = [("m", v) for v in pc["wq"]] + [op for s in pc["segs0"] for op in norm_ops(s)] + ([("m", pc["v0"])] if pc["v0"] is not None else [])
    b = [("m", v) for v in pc["wqp"]] + [op for s in pc["segs1"] for op in norm_ops(s)] + ([("m", pc["v1"])] if pc["v1"] is not None else [])
    return a + rev_ops(b, inv), perm


def blackbox(insts, tag, limit=3_000_000):
    inp = os.path.join(CACHE, "bb_in_%s.json" % tag)
    outp = os.path.join(CACHE, "bb_out_%s.jsonl" % tag)
    json.dump(insts, open(inp, "w"))
    subprocess.run([PY, "-I", os.path.join(CODE, "review23_n21_blackbox.py"), inp, outp, str(limit)], check=True)
    return [json.loads(l) for l in open(outp)]


def make_instance(iid, u, H, w, bound, rng, target=None):
    n = nverts(u)
    Q = full(u, n)
    T = negq(Q) if target is None else full(target, n)
    p1 = list(range(n)); rng.shuffle(p1)
    p2 = list(range(n)); rng.shuffle(p2)
    return {"id": iid, "Q": relabel(Q, p1), "Qp": relabel(T, p2), "bound": bound, "w": w, "H": H}


def check_routes(insts, res, replay_limit, tag):
    out = []
    by = {i["id"]: i for i in insts}
    for r in res:
        inst = by[r["id"]]
        row = {"id": r["id"], "bound": inst["bound"], "H": inst["H"], **{k: r["summary"][k] for k in ("found", "depth", "walks", "ops", "keys", "route_ops", "time")}}
        if r["summary"]["found"]:
            ops, perm = compose_route(r["pieces"])
            L = ops_len(ops)
            row["length"] = L
            row["length_agrees_with_attacker"] = L == r["length"]
            row["compressed_size_own_count"] = ops_size(ops)
            if "word" in r:
                row["word_agrees"] = expand_ops(ops) == r["word"]
            if L <= replay_limit:
                uq = upper(inst["Q"])
                tgt = upper(relabel(inst["Qp"], perm))
                rp = c_replay(uq, tgt, ops, inst["bound"], tag=tag)
                row["replay"] = rp
                row["verified"] = (rp["failed_bound"] == 0 and rp["end_equals_target"] == 1 and rp["end_iso_target"] == 1
                                   and rp["length"] == L and rp["max_height"] <= inst["bound"])
                # independent of the attacker's relabelling: the end is isomorphic to Q'
                rp2 = c_replay(uq, upper(inst["Qp"]), ops, inst["bound"], tag=tag)
                row["end_iso_Qprime"] = rp2["end_iso_target"]
        out.append(row)
    return out


ATTACK_PARAMS = {"R": [6, 7, 20, 61, 1000, 1001, 10 ** 6, 2 ** 64], "Qt": [3, 8, 60, 1000, 2 ** 64],
                 "P+": [2, 5, 64, 1000, 2 ** 64], "Qa": [2, 5, 12, 48, 1000, 2 ** 64]}


def cmd_attack(seed="7201", trials="2"):
    rng = random.Random(int(seed))
    insts = []
    for name, pars in ATTACK_PARAMS.items():
        for par in pars:
            u, H, w, Lcf = fam(name, par)
            for t in range(int(trials)):
                inst = make_instance("%s:%d:%d:x1" % (name, par, t), u, H, w, H, rng)
                inst["Lcf"] = Lcf
                insts.append(inst)
    for name, par in [("R", 9), ("Qt", 8), ("P+", 9), ("Qa", 9), ("Qa", 1000)]:
        u, H, w, Lcf = fam(name, par)
        inst = make_instance("%s:%d:0:x1e6" % (name, par), u, H, w, H * 10 ** 6, rng)
        inst["Lcf"] = Lcf
        insts.append(inst)
    res = blackbox(insts, "fam%s" % seed)
    rows = check_routes(insts, res, 3_000_000, "fam")
    by = {i["id"]: i for i in insts}
    for row in rows:
        row["closed_form"] = by[row["id"]]["Lcf"]
        if row.get("length") is not None and row["closed_form"] is not None:
            row["length_eq_closed_form"] = row["length"] == row["closed_form"]
        if row.get("length", 0) > 10 ** 7:
            row["length"] = "2^%.3f" % math.log2(row["length"])
        print(json.dumps(row), flush=True)
    # the long routes: write replay programs for the C engine, to be run separately
    for r in res:
        inst = by[r["id"]]
        if r["summary"]["found"] and r["id"].split(":")[1] == "1000" and r["id"].endswith(":0:x1"):
            ops, perm = compose_route(r["pieces"])
            path = os.path.join(CACHE, "long_%s.txt" % r["id"].replace(":", "_"))
            write_prog(path, upper(inst["Q"]), upper(relabel(inst["Qp"], perm)), ops, inst["bound"])
            print("# long replay program %s: %d mutations, %d ops" % (path, ops_len(ops), ops_size(ops)), flush=True)


# ----------------------------------------------------------------------------- recount the note's files (data only)
def load(fn):
    return [json.loads(l) for l in open(os.path.join(HERE, fn))]


def fit_slope(xs, ys):
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    mx, my = statistics.mean(lx), statistics.mean(ly)
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)


def cmd_jsonl():
    # attack files
    A = load("owf_barrier_attack.jsonl") + load("owf_barrier_attack_bigbound.jsonl")
    ver = [r for r in A if r.get("verified") is not None]
    print("attack: %d instances, %d found; %d verified (all True: %s), %d not replayed; max walks %d, max keys %d, max time %.3f"
          % (len(A), sum(r["found"] for r in A), len(ver), all(r["verified"] for r in ver), len(A) - len(ver),
             max(r["walks"] for r in A), max(r["keys"] for r in A), max(r["time"] for r in A)))
    print("  verified routes at height exactly H: %d of %d" % (sum(r.get("route_height") == r["H"] for r in ver), len(ver)))
    bad = []
    for r in A:
        if r.get("verified") is None:
            _, H, w, Lcf = fam(r["family"], r["param"])
            if Lcf is None or r["route_mutations"] != Lcf:
                bad.append((r["family"], r["param"], r["route_mutations"], Lcf))
    print("  unreplayed rows whose length differs from the closed form (or has none): %s" % bad[:6], len(bad))
    for f in ("R", "Qt", "P+", "Qa"):
        rs = [r for r in A if r["family"] == f]
        print("  %s: walks <= %d, keys <= %d, route_ops %d-%d, time <= %.3f, depths %s, max verified param %s"
              % (f, max(r["walks"] for r in rs), max(r["keys"] for r in rs), min(r["route_ops"] for r in rs),
                 max(r["route_ops"] for r in rs), max(r["time"] for r in rs), sorted(set(r["depth"] for r in rs)),
                 max([r["param"] for r in rs if r.get("verified")] or [None])))
    # rows
    for fn in ("owf_barrier_rows_n5.jsonl", "owf_barrier_rows_n6.jsonl", "owf_barrier_rows_n6_dense.jsonl",
               "owf_barrier_rows_n7.jsonl", "owf_barrier_rows_n8.jsonl"):
        R = load(fn)
        keys = sorted(set((r["n"], r["w"], r["mode"]) for r in R))
        for (n, w, mode) in keys:
            rs = [r for r in R if (r["n"], r["w"], r["mode"]) == (n, w, mode)]
            pl = [r for r in rs if r["planted"]]
            W = w ** (n - 2)
            half = [r for r in pl if r["h"] >= W / 2]
            full_ = [r for r in pl if r["h"] >= W]
            line = "rows %s n=%d w=%d %s: draws %d, planted %d (%.2f %%), h>=W/2 %d, h>=W %d (%.2f %%), walk ops median %s" % (
                fn[-12:], n, w, mode, len(rs), len(pl), 100 * len(pl) / len(rs), len(half), len(full_), 100 * len(full_) / len(rs),
                statistics.median(r["planter_walk_ops"] for r in rs))
            if pl:
                top = max(pl, key=lambda r: r["h"])
                ex = [r for r in pl if r.get("generic", {}).get("status") == "found" and r["generic"]["iso"] == r["h"] and r["generic"].get("target_is_Y")]
                ex2 = [r for r in pl if r.get("generic", {}).get("status") == "found" and r["generic"]["iso"] == r["h"]]
                st = [r["structure"] for r in pl]
                line += ("; largest h %d (%.3f), its route %d, its sweep %s (escape %s); generic escape = h and target Y: %d (escape = h: %d); "
                         "inverted %d, verified %d, depths %s; keys median %s max %d; Y opposite among h>=W/2: %d/%d"
                         % (top["h"], top["h"] / W, top["route_mutations"], top["generic"]["popped"], top["generic"]["iso"], len(ex), len(ex2),
                            sum(s["found"] for s in st), sum(bool(s.get("verified")) for s in st), sorted(set(s["depth"] for s in st)),
                            statistics.median(s["keys"] for s in st), max(s["keys"] for s in st),
                            sum(r["Y_is_opposite"] for r in half), len(half)))
            print(line)
        if fn.endswith("n5.jsonl"):
            pl = [r for r in R if r["planted"]]
            ex = [r for r in pl if r.get("generic", {}).get("status") == "found" and r["generic"]["iso"] == r["h"]]
            ext = [r for r in ex if r["generic"].get("target_is_Y")]
            print("  n=5 all w: planted %d; escape = h: %d; escape = h and target Y: %d" % (len(pl), len(ex), len(ext)))
            for lab, S in (("escape=h", ex), ("escape=h & target Y", ext)):
                big = [r for r in S if r["h"] >= 50]
                ratios = [r["generic"]["popped"] / r["route_mutations"] for r in big]
                print("  %s: slope of log sweep on log h over all = %.3f, over h>=20 = %.3f; h>=50: %d rows, sweep/route median %.1f max %.1f"
                      % (lab, fit_slope([r["h"] for r in S], [r["generic"]["popped"] for r in S]),
                         fit_slope([r["h"] for r in S if r["h"] >= 20], [r["generic"]["popped"] for r in S if r["h"] >= 20]),
                         len(big), statistics.median(ratios), max(ratios)))
            half = [r for r in pl if r["h"] >= r["w"] ** 3 / 2]
            print("  n=5 rows with h >= w^3/2: %d, Y opposite: %d, structure depth %s" % (len(half), sum(r["Y_is_opposite"] for r in half), sorted(set(r["structure"]["depth"] for r in half))))
    # perturbations
    P = load("owf_barrier_perturb.jsonl")
    nopart = [r for r in P if not r["planter"]["found"] and r["generic"]["status"] != "found"]
    part = [r for r in P if r not in nopart]
    beyond = [r for r in part if r["generic"]["status"] == "found" and r["generic"]["iso"] > r["w"]]
    low = [r for r in part if r not in beyond]
    print("perturb: %d quivers; no partner %d; partner %d (escape <= w or planter only: %d; beyond a barrier: %d); inverted %d"
          % (len(P), len(nopart), len(part), len(low), len(beyond), sum(r.get("structure", {}).get("found", False) for r in part)))
    for r in beyond:
        print("   beyond: %s %s %s escape %s (H %d, ratio %.2f) popped %s path %s planter %s; structure depth %s walks %s keys %s time %s"
              % (r["family"], r["param"], r["quiver"], r["generic"]["iso"], r["H"], r["generic"]["iso"] / r["H"], r["generic"]["popped"],
                 r["generic"]["path_len"], r["planter"]["found"], r["structure"]["depth"], r["structure"]["walks"], r["structure"]["keys"], r["structure"]["time"]))
    for r in low:
        print("   low: %s %s %s generic %s planter %s" % (r["family"], r["param"], r["quiver"], r["generic"], r["planter"]))
    # random walks
    for fn in ("owf_barrier_rwalk.jsonl", "owf_barrier_rwalk_qa.jsonl"):
        for r in load(fn):
            print("rwalk %s %d h=%d (H %d): component %d, hit %d/%d, median %d, ratio %.0f"
                  % (r["family"], r["param"], r["h"], r["H"], r["component"], r["hit"], r["trials"], r["median_steps"], r["median_steps"] / r["component"]))
    # shortest
    for fn in ("owf_barrier_shortest.jsonl", "owf_barrier_shortest_pruned.jsonl"):
        for r in load(fn):
            print("shortest %s %s %d bound %s: distance %s lb %s nodes %s" % (fn[-14:], r["family"], r["param"], r["bound"], r["distance"], r["lower_bound"], r["nodes"]))
    # masks
    Mk = load("owf_barrier_mask.jsonl")
    print("mask: %d rows, end at fork %d, descent undoes whole climb %d, inverted %d, max log10 height %.1f, depths %s, max time %.2f"
          % (len(Mk), sum(r["end_is_fork"] for r in Mk), sum(r["residual_climb"] == 0 for r in Mk),
             sum(r["structure"]["found"] for r in Mk), max(r["log10_height"] for r in Mk),
             sorted(set(r["structure"]["depth"] for r in Mk)), max(r["structure"]["time"] for r in Mk)))


# ----------------------------------------------------------------------------- item 4: planting
def plant_lines(rows, maxmut=10 ** 7):
    lines = []
    for r in rows:
        n, w = r["n"], r["w"]
        cap = 64 * w ** (n - 2)
        st = [v for s in r["states"] for v in s]
        ex = [(int(x), int(y), int(v)) for (x, y), v in r.get("extra", [])]
        lines.append("plant %d %d %d %d %d %s %d %s" % (n, w, cap, maxmut, len(r["states"]), " ".join(map(str, st)), len(ex),
                                                     " ".join("%d %d %d" % e for e in ex)))
    return lines


def canon_many(us):
    return [tuple(x) if isinstance(x, list) else tuple(json.loads(x)) for x in run_c(["canon %d %s" % (nverts(u), " ".join(map(str, u))) for u in us])]


def z_two(k1, n1, k2, n2):
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else 1
    return (k1 / n1 - k2 / n2) / se


def cmd_rows(seed="7202", fresh="3000", sample="200"):
    rng = random.Random(int(seed))
    # A. the note's own rows, row by row
    for fn in ("owf_barrier_rows_n5.jsonl", "owf_barrier_rows_n6.jsonl", "owf_barrier_rows_n6_dense.jsonl",
               "owf_barrier_rows_n7.jsonl", "owf_barrier_rows_n8.jsonl"):
        R = load(fn)
        t0 = time.time()
        mine = run_c(plant_lines(R))
        their_y = [r["Y"] for r in R if r["planted"]]
        tk = iter(canon_many(their_y)) if their_y else iter([])
        agree = dis = 0
        diffs = []
        cnt = {"both": 0, "only_theirs": 0, "only_mine": 0, "L": 0, "h": 0, "Y": 0, "opp": 0}
        for r, m in zip(R, mine):
            if r["planted"] and m["planted"]:
                cnt["both"] += 1
                k = next(tk)
                okL, okh, okY = r["route_mutations"] == m["len"], r["h"] == m["h"], tuple(m["Ykey"]) == k
                cnt["L"] += okL
                cnt["h"] += okh
                cnt["Y"] += okY
                cnt["opp"] += bool(r["Y_is_opposite"]) == bool(m["Y_is_neg"])
                if not (okL and okh and okY) and len(diffs) < 5:
                    diffs.append((r["w"], r["states"], r["route_mutations"], m["len"], r["h"], m["h"], okY))
            elif r["planted"]:
                next(tk)
                cnt["only_theirs"] += 1
                if len(diffs) < 8:
                    diffs.append(("only theirs", r["w"], r["states"], r["route_mutations"], r["h"], m["fwd"], m["bwd"]))
            elif m["planted"]:
                cnt["only_mine"] += 1
                if len(diffs) < 8:
                    diffs.append(("only mine", r["w"], r["states"], m["len"], m["h"], m["fwd"], m["bwd"]))
        print("A %s: %d rows; planted by both %d, only by owf_barrier %d, only by mine %d; on both: same length %d, same h %d, "
              "same Y up to relabelling %d, same 'Y = -Q' %d (%.1f s)" % (fn, len(R), cnt["both"], cnt["only_theirs"], cnt["only_mine"],
                                                                        cnt["L"], cnt["h"], cnt["Y"], cnt["opp"], time.time() - t0), flush=True)
        for d in diffs:
            print("   diff:", d)
    # B. fresh draws, n = 5
    theirs = load("owf_barrier_rows_n5.jsonl")
    for w in (3, 4, 5, 6):
        rows = [{"n": 5, "w": w, "states": [[rng.randint(-w, w) for _ in range(4)]]} for _ in range(int(fresh))]
        res = run_c(plant_lines(rows))
        pl = [m for m in res if m["planted"]]
        th = [r for r in theirs if r["w"] == w]
        thp = [r for r in th if r["planted"]]
        W = w ** 3
        a1, a2 = len(pl), len(thp)
        b1, b2 = sum(m["h"] >= W / 2 for m in pl), sum(r["h"] >= W / 2 for r in thp)
        c1, c2 = sum(m["h"] >= W for m in pl), sum(r["h"] >= W for r in thp)
        print("B n=5 w=%d: fresh draws %d: planted %d (%.2f %%), h>=w^3/2 %d, h>=w^3 %d, max h %d, Y=-Q among h>=w^3/2 %d | part: %d, %d, %d of %d | z = %.2f, %.2f, %.2f"
              % (w, len(rows), a1, 100 * a1 / len(rows), b1, c1, max(m["h"] for m in pl), sum(m["Y_is_neg"] for m in pl if m["h"] >= W / 2),
                 a2, b2, c2, len(th), z_two(a1, len(rows), a2, len(th)), z_two(b1, len(rows), b2, len(th)), z_two(c1, len(rows), c2, len(th))), flush=True)
    # C. own generic search on planted rows
    n5 = [r for r in theirs if r["planted"]]
    hi = [r for r in n5 if r["h"] >= r["w"] ** 3 / 2]
    lo = [r for r in n5 if r["h"] < r["w"] ** 3 / 2]
    smp = hi + rng.sample(lo, min(int(sample), len(lo)))
    n6 = [r for fn in ("owf_barrier_rows_n6.jsonl", "owf_barrier_rows_n6_dense.jsonl") for r in load(fn) if r["planted"]]
    for label, S in (("n5", smp), ("n6", n6)):
        qs = [m["Q"] for m in run_c(plant_lines(S))]
        yk = canon_many([r["Y"] for r in S])
        nk = canon_many([upper(negq(full(q, nverts(q)))) for q in qs])
        lines = ["minimax %d %d %d %d 2 %d %s" % (r["n"], r["w"], r["h"], tie, 20_000_000, " ".join(map(str, q)))
                 for r, q in zip(S, qs) for tie in (2, 0)]
        out = run_c(lines)
        stats = {"rows": len(S), "level_eq_h": 0, "level_lt_h": 0, "target_is_Y_at_h": 0, "Y_is_negQ_hi": 0, "hi": 0,
                 "target_neg_hi": 0, "pop_agree_part": 0}
        ratios, hs, pops, pops0 = [], [], [], []
        for i, (r, q) in enumerate(zip(S, qs)):
            g2, g0 = out[2 * i], out[2 * i + 1]
            if g2["status"] == "found" and g2["level"] == r["h"]:
                stats["level_eq_h"] += 1
                if tuple(g2["target"]) == yk[i]:
                    stats["target_is_Y_at_h"] += 1
                    hs.append(r["h"]); pops.append(g2["popped"]); pops0.append(g0["popped"])
                    if r["h"] >= 50:
                        ratios.append((g2["popped"] / r["route_mutations"], g0["popped"] / r["route_mutations"]))
            elif g2["status"] == "found" and g2["level"] < r["h"]:
                stats["level_lt_h"] += 1
            if r["h"] >= r["w"] ** (r["n"] - 2) / 2:
                stats["hi"] += 1
                stats["Y_is_negQ_hi"] += yk[i] == nk[i]
                stats["target_neg_hi"] += g2["status"] == "found" and g2["level"] == r["h"] and tuple(g2["target"]) == nk[i]
            gp = r.get("generic", {})
            stats["pop_agree_part"] += gp.get("iso") == g2["level"] and (gp.get("popped") == g2["popped"])
        print("C %s: %s" % (label, json.dumps(stats)), flush=True)
        if label == "n5" and ratios:
            print("   h>=50 with escape = h at Y: %d rows; sweep/route (tie lowest-height) median %.1f max %.1f; (tie FIFO) median %.1f max %.1f"
                  % (len(ratios), statistics.median(a for a, b in ratios), max(a for a, b in ratios),
                     statistics.median(b for a, b in ratios), max(b for a, b in ratios)))
            print("   slope log sweep / log h (tie lowest-height): all %.3f, h>=20 %.3f, h>=50 %.3f; FIFO: all %.3f"
                  % (fit_slope(hs, pops), fit_slope([h for h in hs if h >= 20], [p for h, p in zip(hs, pops) if h >= 20]),
                     fit_slope([h for h in hs if h >= 50], [p for h, p in zip(hs, pops) if h >= 50]), fit_slope(hs, pops0)))


# ----------------------------------------------------------------------------- item 6: perturbations and random walks
def cmd_perturb():
    for u, w, H, cap in [([-5, -6, 5, -2, 4, -6], 6, 51, 204), ([0, 1, 4, -4, -2, -3, 2, -2, -3, -4], 4, 88, 352),
                         ([-1, 2, 5, -5, -5, -4, 2, 0, -4, -5], 5, 212, 848)]:
        n = nverts(u)
        nu = upper(negq(full(u, n)))
        res = {"quiver": u, "w": w, "H_of_member": H}
        for tie in (2, 0):
            res["minimax_tie%d" % tie] = c_minimax(u, w, cap, tie=tie, prune=2)
        res["with_plateau"] = c_minimax(u, w, cap, tie=2, prune=0)
        lv = res["minimax_tie2"]["level"]
        if res["minimax_tie2"]["status"] == "found":
            res["fewest_mutations_at_escape_level"] = c_bibfs(u, res["minimax_tie2"]["target"] if False else nu, lv, 5_000_000)
        print(json.dumps(res), flush=True)


def py_component(u, bound):
    """BFS of the component of Q at bound, with brute-force canonical forms (Python, own code); returns
    (keys, heights, neighbour table with -1 for a refused mutation)."""
    n = nverts(u)
    B0 = full(u, n)
    k0 = brute_canon(B0)
    keys, idx, mats = [k0], {k0: 0}, [B0]
    nbr = []
    i = 0
    while i < len(keys):
        X = mats[i]
        row = []
        for v in range(n):
            Y = mutate(X, v)
            if height(Y) > bound:
                row.append(-1)
                continue
            k = brute_canon(Y)
            if k not in idx:
                idx[k] = len(keys)
                keys.append(k)
                mats.append(Y)
            row.append(idx[k])
        nbr.append(row)
        i += 1
    return keys, [height(M) for M in mats], nbr


def cmd_rwalk(seed="7203", trials="100"):
    rng = random.Random(int(seed))
    for name, par in [("R", 8), ("P+", 2), ("Qa", 2)]:
        u, H, w, _ = fam(name, par)
        t0 = time.time()
        keys, hts, nbr = py_component(u, H)
        n = nverts(u)
        targets = {i for i in range(len(keys)) if hts[i] <= w and i != 0}
        negk = brute_canon(negq(full(u, n)))
        steps_all = []
        for _ in range(int(trials)):
            x, st = 0, 0
            while True:
                y = nbr[x][rng.randrange(n)]
                st += 1
                if y >= 0:
                    x = y
                    if x in targets:
                        break
            steps_all.append(st)
        steps_all.sort()
        med = statistics.median(steps_all)
        print(json.dumps({"member": "%s:%d" % (name, par), "h": H, "component": len(keys), "targets": len(targets),
                          "target_is_neg": [keys[t] == negk for t in targets], "trials": int(trials), "median_steps": med,
                          "min": steps_all[0], "max": steps_all[-1], "median_over_component": round(med / len(keys), 1),
                          "time": round(time.time() - t0, 1)}), flush=True)


def cmd_attackrows(seed="7204"):
    """The black-box attacker on planted rows from the own planter (fresh draws, n = 5), public bound h."""
    rng = random.Random(int(seed))
    insts = []
    for w in (3, 4, 5, 6):
        rows = [{"n": 5, "w": w, "states": [[rng.randint(-w, w) for _ in range(4)]]} for _ in range(3000)]
        res = [m for m in run_c(plant_lines(rows)) if m["planted"]]
        res.sort(key=lambda m: -m["h"])
        pick = res[:3] + rng.sample(res[3:], 2)
        for i, m in enumerate(pick):
            inst = make_instance("row:w%d:%d:h%d" % (w, i, m["h"]), m["Q"], m["h"], w, m["h"], rng, target=m["Y"])
            insts.append(inst)
    res = blackbox(insts, "rows%s" % seed)
    for row in check_routes(insts, res, 3_000_000, "rows"):
        print(json.dumps(row), flush=True)


# ----------------------------------------------------------------------------- main (keep last)
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    globals()["cmd_" + cmd](*sys.argv[2:])
