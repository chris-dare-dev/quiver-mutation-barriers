# 7. All 4-vertex quivers: Conjecture 5.1 is false

*Run on 2026-11-09. This tests [note 5](05-traps.md)'s Conjecture 5.1: on 4 vertices, pockets are born only below an absolute constant, so f(Q, w) ≤ w above it. Notes 4 to 6 supported it on random classes. Here every 4-vertex quiver up to a bound is examined. Code: [experiments/n4_all.py](../experiments/n4_all.py), [experiments/n4_family.py](../experiments/n4_family.py) and [experiments/n4_plateaus.py](../experiments/n4_plateaus.py) (all new). Results: `n4_all_N14.json`, `n4_all_N18.json`, `n4_family.log`, and the `n4_all_*.log` files. Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Follow-up (note 8):** All 172,746 classes with bottom ≤ 7 were resolved up to bound 256–512. The ratio grows with the class bottom: 4.0, 7.0, 9.0, 11.0 and 11.29 for bottoms 3 to 7, so c(4) ≥ 11.29. The extremes are mirror pairs at the bottom, and their death fits about 16.75·bottom − 38. See [note 8](08-n4-ratio.md).

> **Correction (note 12):** Independently checked in [note 12](12-checks-of-notes-03-to-10.md): the 106,918,566 quivers (by Burnside's lemma, level by level); the pockets with death ≤ 8 (1,417, the same (birth, death) multiset from a slow implementation on labelled matrices); and the family P_k for k = 5 to 32. §4's heuristic, that acyclic quivers are never in pockets, now has a published counterpart. Conjecture 5.5 of arXiv 2610.36179, verified for height ≤ 3, says that a mutation-acyclic 4-vertex quiver reaches an acyclic one without exceeding its own height. That would rule out pockets in mutation-acyclic classes. The paper proves the weaker bound max{ht(Q), m(Q)}, which is at most h⁴ + 4h³ + 6h² for h = ht(Q). Of the 123,691 census classes with a pocket, none contains an acyclic quiver inside its bound, and 117,654 are certified mutation-cyclic (note 12 §6).

> **Update (note 13):** Conjecture 5.5 holds for every 4-vertex quiver of height ≤ 18. So §4's heuristic holds with a proof for births ≤ 18: no mutation-acyclic class has a pocket born at ≤ 18. In a mutation-acyclic class that meets height ≤ 18, the acyclic quivers lie at the bottom. All 75,951 pockets above lie in mutation-cyclic classes. See [note 13](13-conjecture-5-5-up-to-height-18.md).

---

## 1. Answer

1. **Exhaustive persistence for n = 4 [I].** I enumerated every skew-symmetric 4×4 integer matrix with maximal entry ≤ 18, up to relabelling: 106,918,566 quivers and 67,830,090 mutation edges between them. I then ran the persistence of note 4 on this whole set at once, which covers every 4-vertex mutation class whose bottom has maximal entry ≤ 18.
   - It finds 75,951 pockets with death ≤ 18, born at every level from 2 to 17.
   - An independent check on 400 random pockets confirmed 259 of the 261 born above their class bottom: no exit at birth, and death equal to the bottleneck height. The other 2 die by the elder rule's tie-break against another pocket born at the same level.
2. **Conjecture 5.1 is false [I].** Let P_k be the quiver with rows

   (0, −k, −(k−1), k), (k, 0, −2, 1), (k−1, 2, 0, −2), (−k, −1, 2, 0).

   Exact computation for every 5 ≤ k ≤ 60 shows:
   - its plateau component at level k has k − 1 quivers and no exit;
   - it first reaches a quiver of maximal entry < k at bound k + 2.

   So P_k is a pocket born at k that dies at k + 2. Pockets are born at every level, and f(Q, w) > w happens at arbitrarily large w on 4 vertices.
3. **The pockets of P_k sit arbitrarily far above their class bottom [I].** The lowest quiver reachable from P_k has maximal entry 3, 4, 5, 5, 6, 7, 8, 9, 11 and 13 for k = 5, 8, 12, 16, 24, 32, 48, 64, 96 and 128, roughly √k. The class bottom can only be lower, so birth/bottom ≥ k/(√k + 2), which is unbounded. The "bounded band" correction suggested by the N = 14 data (birth ≤ 2.75 × bottom) fails too: it is 3.5 at N = 18 and grows along this family.
4. **The barrier ratio at n = 4 is at least 4.5 and possibly unbounded [I].**
   - Over all pockets with death ≤ 18, death/birth reaches 4.5: four pockets are born at 4 and die at 18, at the visibility limit.
   - The births 3 are settled: their deaths stop at 12, identically at N = 14 and N = 18.
   - The births 4 are not. At N = 18 their deaths are spread over 5 to 18, with 4 to 9 pockets at each of 15, 16, 17 and 18.
   - All the birth-4 pockets dying at 15 or later are second bottom components: their classes have several components at their lowest level (4), which join only far above it, as in note 3's opposite pair.
5. **Why notes 4–6 missed this [I].** Their random classes start from entries in [−3, 3], and their bottoms sit at maximal entry ≤ 3. In those classes pockets are rare and low (born ≤ 7, death ≤ 12, as here for bottom 3). Most 4-vertex classes have higher bottoms, and there pockets are as common as at n = 5. The "n = 4 is special" observation was a property of the sample, not of n = 4.
6. **Two structural facts [I].** No pocket's lowest quiver is acyclic: 0 of 75,951. 57 % of pocket bottoms are local minima of total weight (traps), and the rest are climbs.
7. **For the wider question.** Conjecture 5.1 is withdrawn. Problem 5.2 (is death/birth bounded by c(n)?) now includes n = 4, with c(4) ≥ 4.5 and an open tail. The family P_k shows that a bound on f(Q, w) − w cannot depend on the class bottom alone. It shows nothing against a ratio bound: its own barrier is additive (+2).

---

## 2. Method

**Enumeration** (`n4_all.py run --N N`). For each level M ≤ N, the script generates all upper-triangle 6-tuples with b₀₁ = M and the other entries in [−M, M]. Every quiver of maximal entry M has such a labelling. It encodes each tuple in base 2N + 1 and takes the least code over the 24 relabellings as the canonical key, which gives every quiver of maximal entry exactly M once. For every quiver it computes the 4 mutations (vectorized) and keeps those of maximal entry ≤ N as edges, at level max(level of either end). Edge targets are found by binary search in the sorted keys.

**Persistence.** Levels are processed in order with vectorized union–find (hooking and pointer jumping). A component is born at level L when all its quivers have maximal entry L. At each level, the tracked components that now share a root are grouped. The one with the earliest birth survives (ties: lowest node index), and the others die at L, recording a pair when L exceeds the birth. Each pocket is stored with its lowest quiver and with the lowest level of the component it belongs to at level N (its class bottom, as far as visible inside N).

**Cost.** N = 14: 98 s. N = 18: 590 s and several GB of memory. The script is exact for deaths ≤ N; a pocket that dies above N survives at N and is counted among the survivors.

**The family** (`n4_family.py`). P_k was read off the N = 18 output: the five bottom-4 pockets born at 12, 13 and 14 all have the same shape. For each k the script computes:

- the plateau component of P_k at level k, by search over quivers of maximal entry exactly k, with its exits;
- the bottleneck height at which P_k first reaches a quiver of maximal entry < k;
- the lowest maximal entry inside the component of P_k at bound 2k.

**Plateau scan** (`n4_plateaus.py`). This is a first, per-level approach. It finds the plateau components without exits (5,304 at M = 4, 222,068 at M = 8). These turned out to be mostly class bottoms, because almost every 4-vertex quiver lies near the bottom of its own class. Telling pockets from bottoms needs the global computation above, so the scan is kept only as a record.

---

## 3. Results

**Pockets by class bottom** (N = 18; the class bottom is the lowest level in the pocket's component at level 18):

| Class bottom | Pockets | Births | Max birth/bottom | Max death/birth |
|---|---|---|---|---|
| 2 | 2 | 2 | 1.00 | 2.00 |
| 3 | 107 | 3–7 | 2.33 | 4.00 |
| 4 | 822 | 4–14 | 3.50 | 4.50 |
| 5 | 2,517 | 5–16 | 3.20 | 3.60 |
| 6 | 4,863 | 6–17 | 2.83 | 3.00 |
| 8 | 8,565 | 8–17 | 2.12 | 2.25 |
| 10 | 9,357 | 10–17 | 1.70 | 1.80 |
| 13 | 6,260 | 13–17 | 1.31 | 1.38 |
| 17 | 950 | 17 | 1.00 | 1.06 |

For bottom ≥ 5 the maxima are set by the visibility limit (death ≤ 18). At N = 14 the bottom-3 row was identical, and the bottom-4 row reached birth 11 and ratio 3.50.

**Births and deaths of low pockets:**

| Birth | Deaths at N = 14 | Deaths at N = 18 |
|---|---|---|
| 3 | 4–12 (57 pockets) | 4–12 (57 pockets, identical) |
| 4 | 5–14 (313) | 5–18 (340); 4 to 9 pockets at each of 15–18 |
| 5 | 6–14 (728) | 6–18 (877) |

**The family P_k** (`n4_family.log`, all k from 5 to 60 computed):

| k | 5 | 6 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|---|
| Plateau component size | 4 | 5 | 9 | 19 | 39 | 59 |
| Exit at level k | no | no | no | no | no | no |
| Death | 7 | 8 | 12 | 22 | 42 | 62 |

The lowest maximal entry reachable from P_k inside bound 2k (component exhausted) is 3, 4, 5, 5, 6, 7, 8, 9, 11, 13 for k = 5, 8, 12, 16, 24, 32, 48, 64, 96, 128. Neighbouring members P_k and P_{k−1} are not joined inside bound k + 2, and the growing bottoms suggest they lie in different classes.

**Other counts** (N = 18): 43,350 of 75,951 pocket bottoms are local minima of total weight, and none is acyclic. Components alive at N by birth level (class bottoms, or pockets dying above 18) are 13, 147, 1,050, 4,964, … for births 1, 2, 3, 4, …: one per class, plus the unresolved pockets.

---

## 4. Discussion

**What survives for n = 4.**
- The bounded-path property can still hold in the multiplicative form of Problem 5.2: every pocket dies by c(4) times its birth. The data gives c(4) ≥ 4.5.
- The open tail is formed by the second bottom components of classes whose bottom is at level 4 (deaths still appearing at 15–18).
- Whether two minimal components of a class can be arbitrarily far apart, relative to their level, is the concrete question. It is the n = 4 case of the "minimal quivers are not unique" remark in note 6 §3.

**Acyclic quivers are never in pockets [H].** With 0 acyclic pocket bottoms among 75,951, the natural conjecture is that an acyclic quiver can always be joined to the bottom of its class through quivers of no larger maximal entry. For mutation-acyclic classes, Caldero–Keller (note 3 §5) relates their acyclic quivers by sink/source mutations, which keep the weights [P]. What is missing is that an acyclic quiver attains the class bottom.

**The sampling lesson.** Notes 4–6 used random classes with small entries, whose bottoms sit at maximal entry ≤ 3. At n = 4 that sample hides almost everything: of the 75,951 pockets, only 109 belong to classes with bottom ≤ 3. At n ≥ 5 the same bias may hide structure too. A census over all quivers is feasible at n = 4 up to maximal entry 18. At n = 5 the count grows like (2N + 1)¹⁰/120 and is out of reach beyond very small N.

---

## 5. Limitations

- Exhaustive only up to maximal entry 18. Pockets dying above 18 are invisible, so the ratio maxima at birth ≥ 4 are lower bounds.
- "Class bottom" means the lowest level in the component at level 18. A class whose low parts join only above 18 is split, and its bottom is overestimated for the higher part.
- The family P_k is verified by computation for 5 ≤ k ≤ 60 (pocket property) and k ≤ 128 (reachable bottom), not proved for all k. A symbolic proof would have to describe the plateau chain of length k − 1.

---

## 6. Reproduce

```bash
PY=python
$PY -I n4_all.py run --N 14 --out n4_all_N14.json > n4_all_N14.log
$PY -I n4_all.py run --N 18 --out n4_all_N18.json > n4_all_N18.log     # about 10 minutes, several GB
$PY -I n4_family.py --kmin 5 --kmax 60 > n4_family.log
$PY -I n4_plateaus.py scan --lo 3 --hi 8 --out n4_plateaus.jsonl        # the first, per-level approach
```

`n4_all.py` and `n4_plateaus.py` overwrite their output.

---

## Sources

- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Notes 3 to 6 of this repository.
