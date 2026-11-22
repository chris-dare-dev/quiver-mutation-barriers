"""Review 3 of note 22: self-test of review23_n22_lib against stored data (conventions only).
  1. stored kid/mkid of note-14 and note-22 certificates are canonical under lib.canon, and mkid = canon(-kid);
  2. lib.cut at 32b and 128b (caps 6000 / 24000) reproduces n1, n2 of n4_tube_classify.jsonl.gz on a sample;
  3. lib.exits on random quivers: the unique-return-vertex property (note 14 consequence (a)).
Usage: python -I review23_n22_selftest.py [N]"""
import gzip, json, random, sys, time
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
bad = 0
n = 0
for path in ("n4_opposite_tubes.jsonl.gz", "n4_tube_certify2.jsonl.gz"):
    with gzip.open(path, "rt") as f:
        for line in f:
            r = json.loads(line)
            if "kid" not in r:
                continue
            k, mk = tuple(r["kid"]), tuple(r["mkid"])
            n += 1
            if L.canon(k) != k or L.canon(mk) != mk or L.level(mk) != r["bK"] or L.level(k) != r["bK"]:
                bad += 1
print(f"1. kid and mkid canonical, level(kid) = level(mkid) = bK (mkid is the least mirrored bottom quiver, not canon(-kid)): {n} records, failures {bad}")

with gzip.open("n4_tube_classify.jsonl.gz", "rt") as f:
    recs = [json.loads(l) for l in f]
rng = random.Random(1)
sample = rng.sample(recs, N)
agree = dis = 0
t0 = time.time()
for r in sample:
    x = tuple(r["x"])
    c1, ok1, _ = L.cut(x, 32 * r["b"], cap=6000)
    c2, ok2, _ = L.cut(x, 128 * r["b"], cap=24000)
    if len(c1) == r["n1"] and len(c2) == r["n2"] and ok2 == r["ok2"]:
        agree += 1
    else:
        dis += 1
        if dis <= 5:
            print("   differs:", r["i"], r["b"], (len(c1), len(c2), ok2), (r["n1"], r["n2"], r["ok2"]))
print(f"2. cut sizes at 32b / 128b against n4_tube_classify: {N} classes, agree {agree}, differ {dis} ({time.time()-t0:.0f}s)")

rng = random.Random(2)
two = 0
cnt = 0
for _ in range(200000):
    t = tuple(rng.randint(-9, 9) for _ in range(6))
    ex = L.exits(t)
    cnt += len(ex) > 0
    two += len(ex) > 1
print(f"3. 200000 random quivers, entries in [-9, 9]: with an exit {cnt}, with two return vertices {two}")
