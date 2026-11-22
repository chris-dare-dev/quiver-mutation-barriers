# 5. Traps — local minima of total weight and their escape heights

*Run on 2026-11-09. This continues [note 4](04-pockets.md), which split pockets into climbs (greedy descent on total weight leaves them, and its highest point is the barrier) and traps (local minima of total weight, where descent is stuck). Here every local minimum of total weight is examined, not only pocket bottoms. Code: [experiments/traps.py](../experiments/traps.py) (new; `census`, `pairs`, `summarize`). Results: `traps_n4_B4096.jsonl`, `traps_n5_B512.jsonl`, `traps_n5_B2048.jsonl`, `traps_n6_B128.jsonl`, `traps_n7_B48.jsonl`, `traps_sparse_n5_B512.jsonl`, `traps_pairs_n5_B512.jsonl`, `traps_pairs_n6_B128.jsonl`, and the matching `.log` files. The components are note 4's. Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 7):** Conjecture 5.1 is false. An exhaustive computation over all 4-vertex quivers up to maximal entry 18 finds 75,951 pockets, born at every level from 2 to 17. The family P_k gives a pocket born at every level k ≥ 5 that dies at k + 2. The "no traps at n = 4" observations here and in note 6 hold only for the random classes sampled, whose bottoms are at maximal entry ≤ 3. Problem 5.2 now includes n = 4, with c(4) ≥ 4.5. See [note 7](07-n4-exhaustive.md).
>
> **Correction (note 9):** Problem 5.2 fails for n = 4: c(4) = ∞, because the mirror family G_k has f(G_k, k) ≥ k(k − 1) (Theorem 9.1). It is open for n ≥ 5. See [note 9](09-n4-mirror-family.md).

> **Follow-up (note 6):** A local search for traps at maximal entries up to 16,384 (about 780,000 local minima at n = 5, 6) finds escape ratios that do not grow with weight. The maxima are 4.51 (n = 5) and 5.85 (n = 6), and there are no traps at n = 4. No family of traps with growing ratio turned up. The data leans towards a bounded c(n) in Problem 5.2. See [note 6](06-trap-hunt.md).

> **Correction (note 12):** Problem 5.2 has no constant c(n) for any n ≥ 4, connected quivers included. Take G_k with a path of n − 4 extra vertices hung from vertex 0. It is a local minimum of total weight whose escape height is at least k(k − 1) (note 12, Proposition 12.1). So the procedure of §5 is complete only where such a constant exists.

---

## 1. Answer

**Definitions.** The *total weight* of a quiver is its number of arrows. A *local minimum* is a quiver that no single mutation makes lighter; greedy descent on total weight stops exactly there. The *escape height* e(x) is the least bound L such that x is joined to the lowest quiver of its class by mutations through quivers of maximal entry ≤ L. A *trap* is a local minimum with e(x) > max(x). Every other local minimum is *harmless*: it reaches the bottom of the class without exceeding its own weight.

1. **Local minima are common, traps are rare [I].**

   | Set | Local minima | Traps | Traps / local minima |
   |---|---|---|---|
   | n = 4 | 760 | 13 | 1.7 % |
   | n = 5, bound 512 | 1,471 | 56 | 3.8 % |
   | n = 5, bound 2,048 | 2,317 | 120 | 5.2 % |
   | n = 6 | 673 | 42 | 6.2 % |
   | n = 7 | 155 | 18 | 12 % |
   | sparse n = 5 | 3,452 | 0 | 0 % |

   Greedy descent therefore nearly always ends at a harmless minimum.
2. **At n = 4 traps occur only at low weight [I].** All 13 have total weight ≤ 32, in 4 of 58 classes. The other 747 local minima, up to total weight 4,096, are harmless. With note 4's n = 4 pockets (all born at weight ≤ 8, all closing within 4), this suggests that at n = 4, f(Q, w) ≤ w for every w above a small absolute constant (Conjecture 5.1 in §5).
3. **A trap's barrier is usually the height of one of its mutations, but not the lowest one [I].** On the best escape path, the highest quiver is the first mutation in 96 of 120 traps at n = 5, bound 2,048 (31 of 56 at bound 512, 23 of 42 at n = 6, 10 of 18 at n = 7). So e(x) = max(μ_k(x)) for some vertex k. It equals the least of these n values only in 7 to 23 % of cases: the cheapest first step usually leads into another trap.
4. **Most barriers are shallow [I].** Try every walk of k mutations from the trap, follow it by greedy descent, and keep the lowest such route that ends at a harmless minimum. With k ≤ 2 this finds e(x) exactly in 102 of 120 traps at n = 5, bound 2,048 (85 %). The rate is 33 of 56 at bound 512, 25 of 42 at n = 6, 15 of 18 at n = 7 and 6 of 13 at n = 4. The rest need longer walks.
5. **Escape ratios.** e/max for traps has a median of 1.25 to 1.57 and a maximum of 2.33 (n = 4), 5.39 (n = 5), 3.05 (n = 6) and 2.33 (n = 7). These are the extreme pockets of note 4.
6. **Random pairs barely notice traps [I].** 11,800 random pairs at n = 5 and 8,000 at n = 6, each pair in one class with maximal entry ≤ B/4, were joined by plain search. It needed no bound above the pair's own maximal entry in 99.6 % and 99.0 % of pairs. After greedy descent from both ends first, the figures are 99.8 % and 99.3 % relative to the original weights. The worst ratios, 4.12 and 3.05, are unchanged by the descent, because they come from traps.
7. **No structural signature found [I].** No trap is a fork. Traps contain a mutation-cyclic triangle (a 3-vertex subquiver that is a rank-3 root, note 3 §4.3) more often than harmless minima do: 28 % against 11 %, and against 15 % for quivers in general (n = 5, small sample). That is an enrichment, not a criterion.
8. **For the wider question.** The bounded-path question has reduced to a single quantity: the escape ratio of local minima of total weight (Problem 5.2). If that ratio is bounded by some c(n), then greedy descent followed by a bounded search decides mutation equivalence.

---

## 2. Method

**Census** (`traps.py census`). For each class (note 4's components, up to relabelling, inside ambient bound B), the script:

- computes every quiver's total weight;
- finds the local minima with total weight ≤ B and maximal entry ≤ B/4;
- computes escape heights for all quivers at once, with a bottleneck (minimax) Dijkstra search from the lowest quiver of the class (least maximal entry, then least total weight), keeping the parent links.

For each trap it then records:

- the best escape path: its length, where its highest quiver sits on it, and whether the path rises monotonically to that point and falls after it;
- the least maximal entry among the trap's n mutations;
- the lookahead values E_k for k ≤ 3: the lowest height of a walk of at most k mutations followed by greedy descent that ends at a harmless local minimum. E_k(x) ≥ e(x) always; the least k with E_k(x) = e(x) measures how local the barrier is.

**Visibility.** A mutation outside the enumeration has maximal entry > B, so total weight > B, so the reported local minima are exact. The enumeration is connected inside B, so every escape height it reports is exact. The cap max ≤ B/4 keeps every ratio up to 4 visible. A quiver whose escape lies above B is not enumerated at all (note 2 §8.1).

**Pairs** (`traps.py pairs`). In each class, 200 random pairs of quivers with maximal entry ≤ B/4 are drawn, uniformly over the enumerated quivers. For each pair the script measures:

- the level at which the two first become connected (the bound iterative deepening needs);
- the same level for the end points of greedy descent from each.

---

## 3. Results

| Set | Classes | Local minima | Traps (classes) | e/max median | e/max 90 % | e/max max | Highest point is the first step | Found with k ≤ 2 | Not found with k ≤ 3 |
|---|---|---|---|---|---|---|---|---|---|
| n = 4, B = 4,096 | 58 | 760 | 13 (4) | 1.40 | 2.00 | 2.33 | 5 | 6 | 6 |
| n = 5, B = 512 | 59 | 1,471 | 56 (17) | 1.50 | 2.42 | 4.12 | 31 | 33 | 21 |
| n = 5, B = 2,048 | 46 | 2,317 | 120 (26) | 1.57 | 2.36 | 5.39 | 96 | 102 | 13 |
| n = 6, B = 128 | 40 | 673 | 42 (16) | 1.31 | 1.70 | 3.05 | 23 | 25 | 13 |
| n = 7, B = 48 | 30 | 155 | 18 (11) | 1.25 | 1.66 | 2.33 | 10 | 15 | 2 |
| sparse n = 5, B = 512 | 30 | 3,452 | 0 | – | – | – | – | – | – |

**Density.** Local minima per quiver fall with weight. At n = 5 (bound 2,048) the rate is 0.16 at total weight ≤ 32, 0.012 at 33–128, 0.0038 at 129–512 and 0.0022 above. Traps have their own density: 7, 4, 35 and 74 traps in these four ranges, against 1,579, 21,039, 164,294 and 536,595 quivers. That is 1.4 to 2.1 traps per 10⁴ quivers above total weight 128, so traps do not die out at larger weights. At n = 4 there are none above total weight 32 (the density table is in `traps_n4_B4096.log` through `summarize`).

**Shape.** Most traps attain their maximal entry once (117 of 120 at n = 5, bound 2,048). At higher weight most are strict local minima of total weight (112 of 120 at bound 2,048, against 28 of 56 at bound 512, where small ties are common). Many have a zero entry: 37 of 42 at n = 6 and 18 of 18 at n = 7.

**Escape paths.** The median length of the best escape path is 4 to 11 mutations. It rises monotonically to its highest point in 117 of 120 cases at n = 5, bound 2,048, and falls monotonically after it in 90. So the typical escape is one high mutation followed by a long, mostly monotone descent.

**Pairs.** See §1 item 6. Greedy descent from both ends reaches the same local minimum in 27 % of pairs at n = 5 and 6.

---

## 4. Discussion

**Why traps are the core [I].** By note 4, a climb's barrier is the highest point of greedy descent, which is computable by walking downhill. A harmless local minimum needs no climb at all. What remains are traps, where descent cannot start and the way out must first go up. For a decision procedure this splits the work into a local part (descent), which is free, and a global part (getting out of traps), which is not.

**Why the first step matters [H].** In 80 % of the traps at bound 2,048, the whole barrier is paid on the first step. From a local minimum, every mutation adds arrows. One mutation raises the maximal entry to e(x) but opens a long monotone descent. Others raise it less but lead into neighbouring traps. Telling the two apart requires following the descent, which is why the least first-step height predicts e(x) poorly, while k ≤ 2 lookahead with descent predicts it well.

**n = 4 versus n ≥ 5 [H].** At n = 4, note 4 found only 7 pockets, all born at weight ≤ 8, and here every trap has total weight ≤ 32. At n ≥ 5 traps occur at every weight measured, with a roughly constant density per quiver. A mutation at n = 4 touches at most three entries of the other vertices. From n = 5 on it touches at least six, which leaves more room for the trade (lower total weight for a higher maximum) that creates both climbs and traps. This is a heuristic, not an argument.

---

## 5. Conjectures and the open problem

**Conjecture 5.1 (n = 4) [H].** There is an absolute constant w₄ such that no class on 4 vertices has a pocket born above w₄. Equivalently, f(Q, w) ≤ w for every class on 4 vertices and every w ≥ w₄. The data gives w₄ ≥ 8. All observed n = 4 pockets are traps, and in 58 classes no trap has total weight above 32 (no climb was seen at n = 4 at all).

**Problem 5.2 (trap barriers).** For n ≥ 5, is there a constant c(n) with e(x) ≤ c(n)·max(x) for every local minimum x of total weight? The data gives c(5) ≥ 5.39, c(6) ≥ 3.05 and c(7) ≥ 2.33. If such a c(n) exists, the following procedure decides mutation equivalence up to relabelling, which is FWZ Problem 2.6.14:

1. Descend greedily on total weight from both quivers, to local minima x′ and y′.
2. Search between x′ and y′ inside bound c(n)·T, where T is the larger of their total weights. T is at most the larger total weight of the two inputs.

It is complete because max(x′) ≤ T. So if the quivers are equivalent, both x′ and y′ reach the lowest quiver of the class inside bound c(n)·T, and they are therefore joined inside it. The converse direction (that no such c(n) exists) would be shown by a family of traps with e/max unbounded. The tail of the n = 5 ratio distribution (note 4 §5) is the place to look for one.

**Lookahead as a practical rule [H].** E_2, two mutations followed by descent, found the barrier of 85 % of the high-weight traps at n = 5. A search that tries two-step escapes before raising the bound would avoid most of the cost of traps in practice. It is not a proof of anything.

---

## 6. Limitations

- The samples are note 4's: 30 to 60 random classes per n, starting entries in [−3, 3], ambient bounds 48 to 4,096. The n = 7 data is limited to maximal entry ≤ 12.
- Escape heights are measured to the lowest quiver of the class, not to the nearest older component as in note 4. So a trap inside a pocket is counted with the pocket's full barrier.
- The lookahead counts depend on the choice "ends at a harmless local minimum". A walk that ends at a trap with a lower barrier is not credited.
- The triangle comparison (§1 item 7) uses 18 traps from 15 classes at n = 5 and is only indicative.

---

## 7. Reproduce

```bash
PY=python
$PY -I traps.py census --n 6 --B-big 128 --trials 40 --workers 8 --seed 20261308 --out traps_n6_B128.jsonl
$PY -I traps.py census --n 7 --B-big 48 --trials 30 --workers 8 --seed 20261408 --out traps_n7_B48.jsonl
$PY -I traps.py census --n 5 --B-big 512 --trials 60 --budget 1200000 --workers 8 --seed 20261208 --out traps_n5_B512.jsonl
$PY -I traps.py census --n 4 --B-big 4096 --trials 60 --budget 200000 --workers 8 --seed 20261108 --out traps_n4_B4096.jsonl
$PY -I traps.py census --n 5 --B-big 512 --trials 30 --workers 8 --seed 20261508 --sparse --out traps_sparse_n5_B512.jsonl
$PY -I traps.py census --n 5 --B-big 2048 --trials 60 --only 1 2 3 4 5 6 8 9 10 11 12 13 14 16 17 19 20 21 22 24 25 26 28 29 30 32 33 34 36 39 40 41 42 43 44 45 46 47 48 50 51 54 55 56 57 59 --budget 3000000 --workers 8 --seed 20261208 --out traps_n5_B2048.jsonl
$PY -I traps.py pairs --n 5 --B-big 512 --trials 60 --budget 1200000 --npairs 200 --workers 8 --seed 20261208 --out traps_pairs_n5_B512.jsonl
$PY -I traps.py pairs --n 6 --B-big 128 --trials 40 --npairs 200 --workers 8 --seed 20261308 --out traps_pairs_n6_B128.jsonl
$PY -I traps.py summarize traps_n4_B4096.jsonl traps_n5_B512.jsonl traps_n5_B2048.jsonl traps_n6_B128.jsonl traps_n7_B48.jsonl traps_sparse_n5_B512.jsonl
```

`census` overwrites its output unless `--append` is given; `pairs` always overwrites. The budgets are set so that every component exhausted in note 4 is exhausted here and the truncated ones stop early.

---

## Sources

- Fomin, Neville, *Long mutation cycles* (descent and non-confluence): https://arxiv.org/abs/2304.11505
- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.14: https://arxiv.org/abs/1608.05735
- Notes 2, 3 and 4 of this repository.
