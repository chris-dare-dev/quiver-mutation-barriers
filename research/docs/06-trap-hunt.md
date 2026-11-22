# 6. Hunting for traps with large escape ratios

*Run on 2026-11-09. This tests [note 5](05-traps.md)'s Problem 5.2: is the escape ratio e(x)/max(x) of local minima of total weight bounded by a constant c(n)? Code: [experiments/hunt.py](../experiments/hunt.py) (new; `calibrate`, `hunt`, `bwalk`, `climb`, `summarize`). Results: `hunt_calibrate.jsonl`, `hunt_bwalk_n4.jsonl` and `hunt_bwalk_n{5,6}.jsonl.gz` (gzip-compressed) with their `.log` files, and `hunt_climb_census.jsonl` (its round-by-round output is quoted in §3). Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 7):** The n = 4 statements below (no traps, support for Conjecture 5.1) are true of the random low-bottom classes sampled, not of 4-vertex classes in general. Conjecture 5.1 is false; see [note 7](07-n4-exhaustive.md).
>
> **Correction (note 11):** Problem 6.1 (§4) is false at n = 4. The class of note 9's G_k contains the oriented 4-cycle with weights k, k, k, k − 1, whose total weight 4k − 1 is below G_k's 5k − 1. Every path from G_k to a lighter quiver passes a quiver of maximal entry k(k − 1), so D(G_k) = (k − 1)·max(G_k) for every k ≥ 3 (Theorem 11.1). At n = 4 only a quadratic form, D(x) ≤ c·max(x)², can hold. See [note 11](11-n4-invariants-descent-joins.md).

> **Correction (note 12):** Problem 6.1 fails for every n ≥ 4, connected quivers included (note 12, Proposition 12.1); note 11 proved the case n = 4 by computer. In §1 item 1, the inequality e(x) ≥ D(x) needs the lowest quiver of the class (least maximal entry first) to be lighter than x. It is not enough that x is not the lightest. The ten exceptions found there are handled correctly.

---

## 1. Answer

1. **A local certificate for escape ratios [I].** For a local minimum x of total weight, let the *descent barrier* D(x) be the least bound L such that some path through quivers of maximal entry ≤ L leads from x to a lighter quiver. A bottleneck search from x finds D(x) without enumerating the class. Every path from x to the bottom of its class passes a lighter quiver, so e(x) ≥ D(x) (unless x is itself the lightest), and a large D/max certifies a large escape ratio. On note 5's 249 census traps:
   - D = e for 219;
   - D < e for 20;
   - D > e never;
   - 10 found no lighter quiver inside the cap. For these, the lowest quiver of the class (least maximal entry) is not lighter than the trap, so D does not bound e.

   All 249 run in under a second.
2. **About 780,000 local minima, at maximal entries up to 16,384 [I].** Random walks confined below a bound W (2 million steps each, W = 256 to 16,384, 32 walks per W) recorded every local minimum with maximal entry ≥ W/8 that they visited:
   - n = 5: 395,619 local minima, of which 453 certified traps (D > max);
   - n = 6: 384,804 local minima, of which 2,181 certified traps;
   - n = 4: 1,005 local minima, none a trap.

   Every one reached a lighter quiver within 12 times its maximal entry (no search hit its cap).
3. **The ratio does not grow with weight [I].** Over two and a half decades of maximal entry:
   - the median of D/max falls, from 2.00 to 1.29 at n = 5 and from 1.85 to 1.23 at n = 6;
   - the 90th percentile stays between 1.8 and 3.6;
   - the maximum is 4.51 at n = 5 (at maximal entry 41) and 5.85 at n = 6 (at maximal entry 2,123).

   The n = 5 record is still note 4's 5.39, found by enumeration.
4. **n = 4 has no traps above low weight [I].** None of the 1,005 local minima with maximal entry from 17 to above 4,096 is a trap. With note 5 (all 13 traps at total weight ≤ 32), this is strong support for Conjecture 5.1.
5. **No family with growing ratio [I].** Two searches failed to produce larger traps:
   - Hill-climbing (short random walks from the worst traps, then descent) saturates at 5.39. Its two new traps have ratio about 5.3, one at maximal entry 7,409. The neighbourhood of a trap descends back into the same few traps.
   - For each of the 40 worst traps, alternating mutation at a heavy pair (up to 8 rounds, then descent) never produced a trap more than 4 times heavier. Fomin–Neville's Chebyshev corridors do not carry traps up in weight.
6. **Verdict.** No evidence for an unbounded escape ratio. Every measurement is consistent with c(5) ≈ 5.4 and c(6) ≈ 5.9, read as lower bounds. Problem 5.2 remains open, and the data now leans towards a bounded c(n).
7. **A sharper statement worth proving (Problem 6.1, §4).** "Descent with bounded detours" always works: every quiver not of minimal total weight in its class has a lighter quiver within c(n) times its maximal entry. The 780,000 sampled minima satisfy this with c = 5.85.

---

## 2. Method

**Descent barrier.** `barrier(x, cap, budget)` runs a bottleneck Dijkstra search from x over canonical forms. It pops quivers in order of the largest maximal entry on the best path so far, and stops at the first quiver lighter than x. Neighbours above the cap (12 times max(x)) are skipped, and so is anything after the budget of popped quivers. `calibrate` runs it on the traps stored by note 5's census and compares D with the census escape height e.

**Bounded walks** (`bwalk`). The walk starts from a random dense quiver on n vertices (entries in [−3, 3]). Each step mutates at a random vertex other than the last one, rejecting mutations whose maximal entry exceeds W. At every visited quiver the walk checks the local-minimum condition (no mutation lowers the total weight). Each new local minimum with maximal entry ≥ W/8 is then measured with cap 12·max. The walks see only the part of each class reachable inside W from its start; at W = 16,384 that is a small part of a very large class.

**Hill-climbing** (`climb`). The 24 traps with the largest ratio are kept. In each round, each of them gets 30 children: a random walk of 1 to 6 mutations, then greedy descent to a local minimum. New local minima are measured and the best 24 are kept. Twelve rounds were run, seeded with the census traps.

**Corridor test.** For each of the 40 traps with the largest ratio, and each pair (i, j) with |b_ij| ≥ 2, the test applied (μ_j μ_i)^r for r = 1, …, 8. It then descended greedily and measured the result whenever it was a local minimum heavier than the original.

**Overflow.** Entries are 64-bit integers. A mutation computes products of entries, so it overflows once entries pass about 3·10⁹. A first hill-climbing run met this and reported "traps" with entries near 10¹⁸, including a spurious ratio of 5.56 at maximal entry 5·10⁸. The run was discarded. The script now keeps every quiver it mutates at total weight ≤ 2³¹ − 1, so that every product stays below 2⁶².

---

## 3. Results

**Calibration** (note 5's census traps, n = 4 to 7): see §1 item 1.

**Bounded walks, certified traps by maximal entry of the local minimum:**

| n | Maximal entry | Local minima | Certified traps | D/max median | D/max 90 % | D/max max |
|---|---|---|---|---|---|---|
| 5 | 17–64 | 192 | 5 | 2.00 | 3.57 | 4.51 |
| 5 | 65–256 | 605 | 39 | 1.75 | 2.59 | 3.87 |
| 5 | 257–1,024 | 364 | 118 | 1.49 | 2.25 | 4.31 |
| 5 | 1,025–4,096 | 14,648 | 156 | 1.40 | 2.49 | 3.19 |
| 5 | > 4,096 | 379,810 | 135 | 1.29 | 2.87 | 3.04 |
| 6 | 17–64 | 409 | 42 | 1.85 | 2.81 | 3.21 |
| 6 | 65–256 | 2,691 | 321 | 1.47 | 2.33 | 4.17 |
| 6 | 257–1,024 | 2,721 | 639 | 1.35 | 2.09 | 4.10 |
| 6 | 1,025–4,096 | 25,156 | 763 | 1.24 | 2.09 | 5.85 |
| 6 | > 4,096 | 353,827 | 416 | 1.23 | 1.83 | 3.80 |
| 4 | 17 – > 4,096 | 1,005 | 0 | – | – | – |

The share of traps among local minima varies a lot between walks. At W = 4,096 the walks met few minima, many of them traps (134 of 362 at n = 5). At W = 16,384 some walks entered regions dense with harmless minima (394,218 minima, 202 traps). So these shares say more about where the walks went than about the classes; the ratios of the traps found are what the table is for.

**Hill-climbing:** 12 rounds from the 249 census traps. The best ratios after the last round were 5.39, 5.29 (maximal entry 7,409), 5.28, 4.97, 4.69 and 4.12. New local minima per round fell from 16 to 0 or 1: the descent from short walks keeps landing on known traps.

**Corridor test:** 0 of 40 traps produced a trap descendant more than 4 times heavier. 8 produced trap descendants at all, all of comparable weight.

**Minimal total weight is not unique.** As a side measurement, among exhausted classes (n = 4 at bound 1,024, n = 5 at 256, n = 6 at 64), the number of quivers of minimal total weight per class ranges from 1 to 20. Typical values are 2 to 6, for example reorientations of an acyclic quiver.

---

## 4. What this means

**Problem 5.2, evidence [H].** If the escape ratio were unbounded, one would expect either the maximum to grow with weight, or some local operation to generate heavier traps with the same or larger ratio. Neither shows up. Across 2.5 decades of weight, with about 2,600 certified traps, the maxima are flat (n = 5) or erratic and bounded (n = 6, 5.85 once), and the medians fall. Neither hill-climbing nor Chebyshev corridors produce larger traps. This is evidence, not proof. Most of these traps were found at maximal entry ≥ 1,000, but the samples are walks from random starts, and a rare family could still be missed.

**Problem 6.1 (descent with bounded detours).** Is there c(n) such that every quiver x that is not of minimal total weight in its class has a lighter quiver reachable through quivers of maximal entry ≤ c(n)·max(x)? This is D(x) ≤ c(n)·max(x), the quantity measured here: all sampled minima satisfy it with c = 5.85. If it holds, the following procedure terminates and reaches a quiver of minimal total weight in the class of any input:

1. Descend greedily.
2. When stuck, search inside c(n)·max for a lighter quiver.
3. Repeat.

Every step lowers the total weight. Deciding mutation equivalence (FWZ Problem 2.6.14) would then need one more ingredient, because the minimal quivers are not unique (§3): a bound on the barrier between two minimal quivers of the same class. Problem 6.1 is weaker than Problem 5.2. It asks only for a path to lighter ground, not to the bottom, which is why D(x) ≤ e(x).

**n = 4 [H].** The absence of traps above weight 32 (note 5) and above maximal entry 16 here, among about 1,800 local minima in total, makes Conjecture 5.1 the most promising statement to try to prove. At n = 4 greedy descent should always reach a harmless local minimum once the weight is above a small constant. Mutation at n = 4 changes only the three entries among the other vertices, which may make a case analysis feasible.

---

## 5. Limitations

- D(x) is a lower bound for e(x). It equals e(x) in 88 % of the census traps, and the ratios here can only undercount escape ratios. The maxima are certificates; the "no growth" statement is about D, and e could be larger.
- Bounded walks sample the part of a class near their start, inside W. They do not sample classes uniformly, and large W explores a vanishing fraction of each class.
- Hill-climbing and the corridor test are two specific local searches; their failure does not exclude families reachable by other constructions.
- n ≤ 6, dense random starts with entries in [−3, 3] only.

---

## 6. Reproduce

```bash
PY=python
$PY -I hunt.py calibrate traps_n4_B4096.jsonl traps_n5_B512.jsonl traps_n5_B2048.jsonl traps_n6_B128.jsonl traps_n7_B48.jsonl --cap-ratio 8 --budget 500000 --workers 8 --out hunt_calibrate.jsonl
$PY -I hunt.py bwalk --n 5 --W 256 1024 4096 16384 --trials 32 --steps 2000000 --workers 8 --seed 33000 --out hunt_bwalk_n5.jsonl
$PY -I hunt.py bwalk --n 6 --W 256 1024 4096 16384 --trials 32 --steps 2000000 --workers 8 --seed 34000 --out hunt_bwalk_n6.jsonl
$PY -I hunt.py bwalk --n 4 --W 256 1024 4096 16384 --trials 32 --steps 2000000 --workers 8 --seed 35000 --out hunt_bwalk_n4.jsonl
$PY -I hunt.py climb hunt_calibrate.jsonl --keep 24 --kids 30 --rounds 12 --cap-ratio 12 --budget 300000 --workers 6 --seed 5 --out hunt_climb_census.jsonl
gzip hunt_bwalk_n5.jsonl hunt_bwalk_n6.jsonl      # stored compressed; summarize reads .gz directly
$PY -I hunt.py summarize hunt_bwalk_n5.jsonl.gz
```

`bwalk` and `hunt` overwrite their output unless `--append` is given; `calibrate` and `climb` always overwrite. The corridor test was a one-off script and is not in the repository; it applied (μ_j μ_i)^r, then `hunt.descend` and `hunt.measure`, as described in §2.

---

## Sources

- Fomin, Neville, *Long mutation cycles* (Prop. 3.13: Chebyshev weights along alternating mutations): https://arxiv.org/abs/2304.11505
- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.14: https://arxiv.org/abs/1608.05735
- Notes 4 and 5 of this repository.
