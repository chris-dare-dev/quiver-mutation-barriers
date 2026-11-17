# 8. The barrier ratio on 4 vertices, class by class

*Run on 2026-11-09. This follows [note 7](07-n4-exhaustive.md), which refuted Conjecture 5.1 and left one question for n = 4: is death/birth bounded (Problem 5.2 with n = 4)? Note 7's census was exact only for deaths ≤ 18, and pockets born at 4 were still dying at 18. Here every 4-vertex class with a low bottom is enumerated on its own, up to a much larger bound. Code: [experiments/n4_classes.py](../experiments/n4_classes.py) (new) and `n4_all.py` (new option `--keep-survivors`). Results: `n4_classes_B512.jsonl` (bottoms ≤ 4), `n4_classes_k5_B512.jsonl` (bottoms ≤ 5), `n4_classes_k67_B256.jsonl` (bottoms 6 and 7), the `n4_all_N14*.json` inputs, and the matching `.log` files. Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 9):** The linear trend below does not continue. The explicit family G_k (a mirror pair at bottom k) has barrier exactly k(k − 1), proved for every k ≥ 3. So c(4) = ∞, and f(Q, w)/w is unbounded on 4 vertices. See [note 9](09-n4-mirror-family.md).

> **Correction (note 12):** The table and the mirror structure of §3 were reproduced exactly with independent code ([note 12](12-checks-of-notes-03-to-10.md)). Two statements are wrong as written. First, the fit 16.75·b₀ − 38 misses bottom 6 by 3.5, not "within ±2"; least squares gives 17.2·b₀ − 40, with residuals ≤ 2.8. Second, Theorem 3.1 gives a rank-3 class one bottom *island*, not one bottom quiver (§1 item 5, §4). An acyclic triangle has three bottom quivers, its rotations. The conclusion, that rank 3 has no mirror barrier, stands.

---

## 1. Answer

1. **Every 4-vertex class with bottom ≤ 7, resolved [I].** `n4_all.py` at N = 14 lists every component born at levels ≤ 7 that is still separate at level 14. That covers every class bottom at those levels, and every low pocket that dies above 14. Each of these classes was then enumerated up to bound 512 (bottoms ≤ 5) or 256 (bottoms 6 and 7), and its persistence pairs computed. All 172,746 classes were exhausted. The deaths of the low pockets lie far below the bound, so the figures below are exact for these classes.
2. **The worst ratio grows with the class bottom, linearly in its death [I].**

   | Class bottom | Classes | Classes with several bottom components | Latest death of a bottom component | Its ratio | Worst ratio above the bottom | 99th percentile, all pockets |
   |---|---|---|---|---|---|---|
   | 3 | 1,050 | 51 | 12 | 4.00 | 2.75 | 3.33 |
   | 4 | 4,956 | 281 | 28 | 7.00 | 5.20 | 4.72 |
   | 5 | 16,714 | 725 | 45 | 9.00 | 6.50 | 5.70 |
   | 6 | 45,287 | 1,540 | 66 | 11.00 | 8.57 | 6.44 |
   | 7 | 104,579 | 2,512 | 79 | 11.29 | 9.88 | 7.05 |

   The latest deaths 12, 28, 45, 66, 79 fit 16.75·b₀ − 38 within ±2 at every point. A quadratic fit misses bottom 7 by about 9 (it predicts about 88).
3. **The worst cases are mirror pairs [I].** Every extreme case examined has this form: the six worst at bottom ≤ 4, and the seven worst at bottoms 6 and 7. Each is a class with two components at its lowest level, each the mirror image (B ↦ −B) of the other. To turn the quiver into its opposite, one has to climb to about 10 to 11 times the bottom level. This is note 3's opposite pair at n = 4, many times larger. Among the 334 classes with bottom ≤ 4 that have several bottom components:
   - 214 have this mirror structure;
   - 120 have bottom components that are not mirror images, and their barriers are smaller.
4. **What this says about c(4) [I, H].** c(4) ≥ 11.29, from a class with bottom 7 whose two mirror bottom components join at 79. If the linear trend continues, death ≤ about 16.75 × bottom for these pockets, and the ratio approaches a constant near 17 from below: bounded, but large. If it does not continue, the ratio is unbounded. The five points favour the linear trend, and the 99th percentile grows ever more slowly (+1.39, +0.98, +0.74, +0.61 per level). Neither is a proof.
5. **For the wider question.** At n = 4, Problem 5.2 splits into two questions:
   - for pockets above the class bottom, the worst ratio reaches 9.88 at bottom 7 and is still growing;
   - for mirror pairs at the bottom, one asks how high one must climb to reverse a quiver that lies in its own mirror class. That is a clean, separate question with no analogue in rank 3: a rank-3 class has a single bottom quiver up to relabelling (Theorem 3.1).

   A decision procedure for n = 4 by bounded search needs a bound on both.

---

## 2. Method

**Input.** `n4_all.py run --N 14 --keep-survivors L` stores one quiver of every component born at levels ≤ L that has not merged by level 14. A component born at level b consists of quivers of maximal entry b, so the stored quiver has maximal entry b. These are the class bottoms (one per class with bottom ≤ L), plus the low pockets whose death is above 14. The counts were 6,201 components for L = 4, 23,228 for L = 5 and 153,456 for L = 6, 7 (with `--min-level 6`).

**Per class** (`n4_classes.py`). For each stored quiver, the class is enumerated up to relabelling inside bound B by breadth-first search. The persistence pairs of the maximal-entry filtration are then computed with note 4's elder rule. A class met several times (once per surviving component) is kept once, keyed by its least canonical quiver at its lowest level. All 172,746 classes were exhausted: B = 512 for bottoms ≤ 5 and B = 256 for bottoms 6 and 7.

**Visibility.** Ratios up to B/b are visible for births b ≤ B/4: at least 32 for births at the bottom levels 3 to 7. Every death reported for a bottom component is far below B.

**Mirror test.** For classes with several bottom components (bottom ≤ 4), the bottom level was split into plateau components. The test then checked whether the canonical form of −B, for a quiver B of each component, lies in another bottom component, in the same one, or not in the class. For the eight worst pockets at bottoms 6 and 7, it checked whether −B of the pocket's quiver lies in the class inside its death bound.

---

## 3. Results

**Bottom components, deaths near the top** (number of pockets at each death):

| Bottom | Latest deaths |
|---|---|
| 3 | 8 (2), 9 (1), 10 (2), 12 (1) |
| 4 | 20 (1), 21 (2), 22 (1), 24 (1), 28 (1) |
| 5 | 33 (1), 35 (2), 37 (1), 41 (1), 45 (1) |
| 6 | 54 (2), 55 (1), 56 (1), 61 (1), 66 (1) |
| 7 | 72 (1), 73 (1), 74 (1), 77 (1), 79 (1) |

**The eight worst pockets at bottoms 6 and 7:**

| Ratio | Bottom | Birth | Death | Mirror pair | Class size ≤ 256 |
|---|---|---|---|---|---|
| 11.29 | 7 | 7 | 79 | yes | 128 |
| 11.00 | 6 | 6 | 66 | yes | 144 |
| 11.00 | 7 | 7 | 77 | yes | 114 |
| 10.57 | 7 | 7 | 74 | yes | 360 |
| 10.43 | 7 | 7 | 73 | yes | 482 |
| 10.29 | 7 | 7 | 72 | yes | 126 |
| 10.17 | 6 | 6 | 61 | yes | 164 |
| 9.88 | 7 | 8 | 79 | no | 240 |

The classes with the worst barriers are thin: 114 to 482 quivers up to maximal entry 256, against thousands for typical classes.

**Mirror structure** (classes with bottom ≤ 4 and several bottom components; components counted per class):

| Bottom components | Mirror of a component is another bottom component | Self-mirror components | Classes |
|---|---|---|---|
| 2 | 2 | 0 | 188 |
| 2 | 0 | 0 | 108 |
| 2 | 0 | 2 | 8 |
| 3 | 2 | 1 | 18 |
| 3 | 0 | 0 | 4 |
| 4 | 4 | 0 | 8 |

---

## 4. Discussion

**Mirror pairs [H].** B ↦ −B commutes with mutation, so a class either equals its mirror class or not. When it does, and its bottom quiver is not isomorphic to its own opposite, the class has at least two bottom components, interchanged by the mirror map. Joining them means turning a quiver into its opposite by mutations. In rank 3 this costs nothing: a mutation-cyclic class has a unique root, and acyclic triangles are reoriented by sink and source moves. At n = 4 the cost appears to grow linearly with the bottom level, about 10 to 11 times it in the worst classes found. A family of 4-vertex quivers Q_b with Q_b ~ Q_b^op and a mirror barrier of order 16·b would explain the table. Finding it, as for P_k in note 7, is the natural next step.

**Thin classes.** The worst classes are among the thinnest. Few quivers at low weight means few routes, so the reversal must go high. Note 2 found that the low part of a class grows like w^1.1 at n = 4; the worst classes sit at the bottom of that range.

**The decision question at n = 4.** If the linear trend holds, f(Q, w) ≤ about 17·w for every 4-vertex class. Bounded search with that bound would then decide mutation equivalence on 4 vertices. This is FWZ Problem 2.6.14 restricted to n = 4, which is open beyond weights ≤ 2 (Armstrong-Williams et al., note 3 §5).

---

## 5. Limitations

- The data covers classes with bottom ≤ 7 only. The linear fit uses five points and is a heuristic.
- The surviving components are taken from n4_all at N = 14, so a class whose bottom pieces at levels ≤ 7 are all present is found. A pocket that dies below 14 is found through its class, not separately.
- The mirror test was done for all classes with bottom ≤ 4 and for the eight worst pockets at bottoms 6 and 7, not for all classes.

---

## 6. Reproduce

```bash
PY=python
$PY -I n4_all.py run --N 14 --keep-survivors 4 --out n4_all_N14.json
$PY -I n4_classes.py n4_all_N14.json --B 512 --workers 10 --out n4_classes_B512.jsonl
$PY -I n4_all.py run --N 14 --keep-survivors 5 --out n4_all_N14_k5.json
$PY -I n4_classes.py n4_all_N14_k5.json --B 512 --workers 10 --out n4_classes_k5_B512.jsonl
$PY -I n4_all.py run --N 14 --keep-survivors 7 --out n4_all_N14_k7.json
$PY -I n4_classes.py n4_all_N14_k7.json --B 256 --min-level 6 --workers 12 --out n4_classes_k67_B256.jsonl
```

Both scripts overwrite their output.

---

## Sources

- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.14: https://arxiv.org/abs/1608.05735
- Armstrong-Williams, Hirst, Jackson, Lee (decidability of mutation-acyclicity at n = 4, weights ≤ 2): https://arxiv.org/abs/2411.04209
- Notes 3, 4, 5 and 7 of this repository.
