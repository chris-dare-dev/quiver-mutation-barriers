# 2. The bounded-path conjecture for quiver mutation, measured

*Run on 2026-11-08. This is the follow-up ranked first in an earlier survey of candidate one-way functions (a wider project's working document, not included here) §4 after [note 1](01-mutation-path-test.md). Code: [experiments/bounded_paths.py](../experiments/bounded_paths.py). Results: `bounded_profile_n4.jsonl` (ambient bound 65536), `bounded_profile_n7*.jsonl`, `bounded_profile_sparse_n{5,6,7}.jsonl`, `bounded_excursions_n7.jsonl`, `bounded_excursions_sparse.jsonl`, `bp_sizing_n7.jsonl` (extension, §8), `bounded_profile_n4_B4096.jsonl`, `bounded_profile_n5.jsonl` (512), `bounded_profile_n5_B128.jsonl`, `bounded_profile_n6.jsonl` (32), `bounded_profile_n6_B64.jsonl`, `bounded_excursions.jsonl`, `bp_sizing.jsonl`, `bounded_profile_summary.log`, and the matching `.log` files. Labels: **[I]** my own measurement or argument; **[H]** heuristic; **[P]** proven in a cited source.*

> **Correction (note 3, 2026-11-09):** The `profile` code tested whether S_w is connected only at levels ≥ w, where a level is a maximal entry that occurs in the class. When no quiver of the class has maximal entry in [w, f), it reported the next level as f(w), although S_w was already connected at bound w. All f values in §1, §4.2, §4.3, §5 and §8 are affected; the excursion test and the growth counts are not. Rerun with the same seeds ([note 3](03-profile-correction-and-rank-3.md) §3):
>
> - The sparse staircase of §8.3 is entirely the artifact.
> - Corrected and labelled, f(w) ≤ w for every w ≥ 12 at n = 4.
> - Up to relabelling, which is the convention of the open problem (FWZ Problem **2.6.14**, not 2.6.12), f(w) ≤ w at every w in 17 of 18 exhausted components at n = 4.
> - What survives are small *pockets* at n ≥ 5 (note 3 §3.5).
>
> The labelled thresholds of §4.3 are real but are mostly relabelling copies: at n = 7 the labelled S_3 splits into 7! = 5,040 islands, which are a single island up to relabelling.

---

## 1. Answer

Let Q be a quiver on n vertices, S_w(Q) the set of quivers in its mutation class with all entries of absolute value ≤ w, and G_B the graph on quivers with entries ≤ B whose edges are mutations. Define f(Q, w) as the least ambient bound w′ at which S_w(Q) lies in one connected component of G_{w′}. The conjecture was that f(Q, w) stays close to w.

1. **The strong form, f(Q, w) = w, is false, but it fails only below a threshold.** In every one of the 37 exhaustively enumerated components (n = 4, 5, 6) there is a component-dependent threshold w*(Q) ∈ [3, 12] for n = 4 and 5, and ∈ [4, 24] for n = 6, below which the low-weight quivers of the class form several islands that join only when the ambient bound reaches w*.
2. **Above the threshold the conjecture holds with small excess.** For w ≥ 12, f(Q, w) = w in 129 of 212 exact measurements (61 %), f ≤ w + 2 in 181 of 212 (85 %), and f(w)/w decreases with w: at n = 4 the worst ratio is 1.75 at w = 12 and 1.04 at w = 256; at n = 5 it is 1.00 at w = 12 and 1.92 at w = 64 (one component with 1,664 states). The refined empirical law is f(Q, w) = max(w, w*(Q)) + ε(Q, w) with ε usually 0, mostly ≤ 2, and ε/w → 0.
3. **High-weight excursions are spikes, never bridges.** 170 of 170 pairs produced by forcing a walk through entries above 10², 10⁴, 10⁶ or 10⁸ and descending again reconnected at a bound at most 8 above max(w_Q, w_Q′), 79 % with no excess at all, and the excess shows no dependence on the excursion height.
4. **The measurement is robust.** For every component exhausted at two different ambient bounds, the profile f(w) agreed exactly (30 of 30 comparisons). Every large excess reported by a truncated enumeration disappeared when the component was exhausted; the mechanism is identified in §3.
5. **A side result.** The number of weight-≤ w quivers in a mutation class grows polynomially, with fitted exponents 1.14, 1.88, 2.26 for n = 4, 5, 6, close to n − 3. The low-weight part of a wild mutation class is thin. This is the structural fact behind note 1's attack and behind the cheapness of iterative deepening.
6. **Extension (§8).** At n = 7 the picture holds where it can be measured exactly, thresholds grow with n (≥ 17), and one case shows that an exhausted enumeration can still miss a low-weight island beyond its ambient bound. Sparse starting quivers reveal a second regime: f(w) follows a staircase at the terms 3, 8, 21, 55, 144 of the weight-3 Kronecker recurrence, so the additive excess is unbounded while f(w)/w stays below about 2.6. The conjecture should be stated multiplicatively or polynomially, not with f = w + O(1).

**Consequence for decidability [I].** Iterative deepening on the entry bound (note 1, attack A3) is a complete procedure for mutation equivalence of two quivers of weight ≤ w as soon as f(n, w) is bounded by an effective function F(n, w): search inside F(n, w); if the quivers are not connected there, they are not mutation-equivalent. The dense data at n ≤ 6 is consistent with F(n, w) = max(2w, w*_max(n)), where w*_max(n) is the largest threshold (10, 12, 24 here); the sparse data of §8 violates 2w three times (f(24) = 55 twice, f(5) = 11 once) while F(n, w) = max(3w, w*_max(n)) holds on every exact row of this note, and the corridor argument of §8.3 suggests a polynomial rather than linear F. This is a measurement at small n, not a theorem, and the thresholds and rank-2 corridors are the parts a proof would have to control.

---

## 2. Statement and context

- **Definitions.** Quivers are skew-symmetric integer matrices; mutation μ_k as in note 1. G_B, S_w(Q), f(Q, w) as above; f(n, w) = sup over classes.
- **Conjecture (bounded paths).** There is a function F(n, w), close to w, with f(Q, w) ≤ F(n, w) for all Q on n vertices.
- **Why it matters.** Mutation equivalence is not known to be decidable (Fomin–Williams–Zelevinsky, Problem 2.6.12) [P]. Descent on arrow multiplicities decides it in rank 3 (Beineke–Brüstle–Hille classification; Neville) [P], and Neville shows that descent cannot be confluent in general [P]. The bounded-path property is the alternative to confluence: it makes bounded search complete without requiring a potential function to be monotone.
- **In the language of hearts.** For the 3-Calabi–Yau category of a quiver with potential, mutations are simple tilts and arrow multiplicities are dimensions of Ext¹ between simples (Keller–Yang; King–Qiu) [P, recalled]. The conjecture says that reachable hearts whose simples have bounded Ext¹ are connected through hearts of bounded Ext¹, with the bound exceeded only below a threshold.
- **Relation to note 1.** The attack there succeeded because planted paths stayed inside small bounds; this note turns that observation into a quantitative statement about mutation classes.

---

## 3. Method

**Merging profile (`profile`).** Enumerate the component C of Q inside a large ambient bound B_big by breadth-first search, recording each quiver's maximal entry. Add the quivers of C in order of increasing maximal entry to a union–find structure, uniting each new quiver with its already-present neighbours. After each level w′, check for each target w ≤ w′ whether S_w is in a single class; the first such w′ is f(Q, w). When the enumeration exhausts C, the result is exact for every w < B_big provided no weight-≤ w quiver of the class attaches only through weights above B_big; such an island is invisible and makes the reported f a lower bound (§8.1 shows one case at n = 7). The two-bound comparison of §4.1 is the check. When the budget truncates the enumeration, the result is unreliable in a specific way: breadth-first order reaches distant low-weight islands through short high-weight paths before it reaches the long low-weight corridors to them, so a truncated run can report two islands as unconnected at a low bound and inflate f. Every inflated value in this note came from a truncated run (§4.1).

**Forced excursions (`excursions`).** From a random dense start Q with entries in [−3, 3] (at least one entry 3, so the class is infinite [P]), random-walk without immediate repeats inside the bound 2²⁹ until some entry exceeds W_high ∈ {10², 10⁴, 10⁶, 10⁸}; then descend greedily on total arrow weight to a local minimum Q′. Find the least bound at which Q and Q′ are connected by bidirectional search with a 300k-node budget per bound, trying max(w_Q, w_Q′) + 0, …, + 8 and then 16, 32, 64, 128, 256, 1024. Fifteen instances per (n, W_high), n ∈ {4, 5, 6}.

**Sizes.** 40 components at n = 4 (two ambient bounds), 24 at n = 5, 16 at n = 6, with up to 5·10⁶ states each; 180 excursion instances. Everything ran in under an hour on 8 cores.

---

## 4. Results

### 4.1 Robustness across ambient bounds

| n | Components | Exhausted in at least one run | Exhausted in both runs | Identical f(w) in both |
|---|---|---|---|---|
| 4 | 20 | 18 | 14 | 14 |
| 5 | 12 | 12 | 10 | 10 |
| 6 | 8 | 7 | 6 | 6 |

Disagreements occurred only for components that were truncated in at least one run: n = 4 trial 4 (f(24) = 342 against 380, f(64) = 1808 against 2072, truncated in both), n = 4 trial 8 (f(128) = 5842 at bound 65536 against 128 at bound 4096, where a larger low-weight part of the component was reached), and n = 6 trials 1 and 4 at bound 64 (truncated; 52 to 64 against 11 to 16 from the exhausted run at bound 32). These are the breadth-first artifact of §3 and are excluded below.

### 4.2 Exact merging profiles (exhausted components only)

> **Correction (note 3):** These tables use the faulty rule. The "f(w) = w" column undercounts, and most excesses above w = 8 are missing levels, not islands. For example, every n = 4 value at w = 256 is ≤ 256 when corrected. Corrected tables, labelled and up to relabelling, are in note 3 §3.

**n = 4** (18 exhausted components; ambient bounds 4096 and 65536)

| w | components with exact f | median \|S_w\| | f(w) = w | f(w) ≤ w+2 | max f(w) − w | max f(w)/w | all f(w) values |
|---|---|---|---|---|---|---|---|
| 3 | 18 | 42 | 5 | 10 | 7 | 3.33 | 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6, 6, 6, 7, 9, 10 |
| 4 | 18 | 42 | 5 | 15 | 6 | 2.50 | 4, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 7, 9, 10 |
| 5 | 18 | 48 | 5 | 14 | 5 | 2.00 | 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 7, 8, 8, 9, 10 |
| 6 | 18 | 60 | 10 | 16 | 4 | 1.67 | 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 9, 10 |
| 8 | 18 | 75 | 8 | 17 | 7 | 1.88 | 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 10, 15 |
| 12 | 18 | 150 | 11 | 14 | 9 | 1.75 | 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 15, 15, 17, 21 |
| 16 | 18 | 198 | 8 | 16 | 5 | 1.31 | 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 18, 21, 21 |
| 24 | 18 | 327 | 9 | 15 | 15 | 1.62 | 24, 24, 24, 24, 24, 24, 24, 24, 24, 25, 25, 25, 25, 25, 26, 27, 29, 39 |
| 32 | 18 | 486 | 8 | 16 | 13 | 1.41 | 32, 32, 32, 32, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 33, 33, 39, 45 |
| 64 | 18 | 1,023 | 6 | 15 | 23 | 1.36 | 64, 64, 64, 64, 64, 64, 65, 65, 65, 65, 66, 66, 66, 66, 66, 71, 76, 87 |
| 128 | 18 | 2,080 | 7 | 15 | 16 | 1.12 | 128, 128, 128, 128, 128, 128, 128, 129, 129, 129, 129, 129, 129, 129, 129, 132, 141, 144 |
| 256 | 18 | 4,144 | 8 | 13 | 11 | 1.04 | 256, 256, 256, 256, 256, 256, 256, 256, 257, 257, 257, 258, 258, 261, 263, 265, 267, 267 |

**n = 5** (12 exhausted components; ambient bounds 128 and 512)

| w | components with exact f | median \|S_w\| | f(w) = w | f(w) ≤ w+2 | max f(w) − w | max f(w)/w | all f(w) values |
|---|---|---|---|---|---|---|---|
| 3 | 12 | 120 | 1 | 2 | 9 | 4.00 | 3, 5, 6, 6, 6, 6, 8, 8, 9, 9, 11, 12 |
| 4 | 12 | 168 | 1 | 6 | 8 | 3.00 | 4, 5, 6, 6, 6, 6, 8, 8, 9, 9, 11, 12 |
| 5 | 12 | 240 | 2 | 6 | 7 | 2.40 | 5, 5, 6, 6, 6, 6, 8, 8, 9, 9, 11, 12 |
| 6 | 12 | 420 | 5 | 8 | 6 | 2.00 | 6, 6, 6, 6, 6, 7, 8, 8, 9, 9, 11, 12 |
| 8 | 12 | 756 | 6 | 10 | 4 | 1.50 | 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 11, 12 |
| 12 | 12 | 1,854 | 12 | 12 | 0 | 1.00 | 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12 |
| 16 | 12 | 2,892 | 11 | 12 | 1 | 1.06 | 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17 |
| 24 | 12 | 6,402 | 10 | 11 | 5 | 1.21 | 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 25, 29 |
| 32 | 12 | 11,004 | 9 | 11 | 10 | 1.31 | 32, 32, 32, 32, 32, 32, 32, 32, 32, 33, 33, 42 |
| 64 | 12 | 39,462 | 9 | 10 | 59 | 1.92 | 64, 64, 64, 64, 64, 64, 64, 64, 64, 65, 78, 123 |

**n = 6** (7 exhausted components; ambient bound 32, so f is measured only for w ≤ 16; at ambient bound 64 the six components exhausted there give trial 0: f(24)=24, f(32)=32, trial 2: f(24)=24, f(32)=32, trial 3: f(24)=24, f(32)=32, trial 5: f(24)=27, f(32)=32, trial 6: f(24)=24, f(32)=32, trial 7: f(24)=24, f(32)=32)

| w | components with exact f | median \|S_w\| | f(w) = w | f(w) ≤ w+2 | max f(w) − w | max f(w)/w | all f(w) values |
|---|---|---|---|---|---|---|---|
| 3 | 7 | 720 | 0 | 2 | 21 | 8.00 | 4, 5, 7, 9, 9, 10, 24 |
| 4 | 7 | 1,440 | 1 | 2 | 20 | 6.00 | 4, 5, 7, 9, 9, 10, 24 |
| 5 | 7 | 5,760 | 2 | 3 | 19 | 4.80 | 5, 5, 7, 9, 9, 10, 24 |
| 6 | 7 | 8,640 | 2 | 3 | 18 | 4.00 | 6, 6, 7, 9, 9, 10, 24 |
| 8 | 7 | 26,640 | 2 | 5 | 16 | 3.00 | 8, 8, 9, 9, 10, 11, 24 |
| 12 | 7 | 66,240 | 6 | 6 | 12 | 2.00 | 12, 12, 12, 12, 12, 12, 24 |
| 16 | 7 | 148,320 | 4 | 4 | 11 | 1.69 | 16, 16, 16, 16, 24, 24, 27 |
| 24 | 6 | 345,240 | 5 | 5 | 3 | 1.12 | 24, 24, 24, 24, 24, 27 |
| 32 | 6 | 581,040 | 6 | 6 | 0 | 1.00 | 32, 32, 32, 32, 32, 32 |

### 4.3 Thresholds

The threshold w*(Q) = f(Q, 3), the bound at which the weight-3 quivers of the class first become connected:

- n = 4: 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6, 6, 6, 7, 9, 10
- n = 5: 3, 5, 6, 6, 6, 6, 8, 8, 9, 9, 11, 12
- n = 6: 4, 5, 7, 9, 9, 10, 24

Above the threshold the typical pattern is f(w) = w with occasional +1 or +2. The components with the largest thresholds and the largest later excesses are the smallest ones (954 to 8,152 states at their ambient bound), where S_w has only a few dozen elements and the low-weight part is sparse.

### 4.4 Growth of the low-weight part

Median |S_w| over exhausted components, fitted as a power of w for w ≥ 8: exponent 1.14 at n = 4, 1.88 at n = 5, 2.26 at n = 6. The number of quivers of weight ≤ w in an infinite mutation class grows polynomially, roughly like w^(n−3), while the number of all skew-symmetric matrices with entries ≤ w grows like w^(n(n−1)/2).

### 4.5 Forced excursions

| n | W_high | Instances | Reached W_high | Descent returned to Q | Connected | Excess 0 | Excess ≤ 2 | Max excess | Median path length | Median search nodes |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 10^2 | 15 | 15 | 7 | 15/15 | 13 | 15 | 1 | 2 | 2 |
| 4 | 10^4 | 15 | 15 | 4 | 15/15 | 9 | 13 | 6 | 3 | 17 |
| 4 | 10^6 | 15 | 15 | 3 | 15/15 | 9 | 14 | 3 | 3 | 16 |
| 4 | 10^8 | 15 | 11 | 3 | 11/11 | 11 | 11 | 0 | 1 | 1 |
| 5 | 10^2 | 15 | 15 | 9 | 15/15 | 13 | 14 | 5 | 0 | 0 |
| 5 | 10^4 | 15 | 15 | 10 | 15/15 | 13 | 14 | 3 | 0 | 0 |
| 5 | 10^6 | 15 | 15 | 6 | 15/15 | 13 | 15 | 2 | 1 | 2 |
| 5 | 10^8 | 15 | 13 | 2 | 13/13 | 10 | 11 | 8 | 2 | 6 |
| 6 | 10^2 | 15 | 15 | 6 | 15/15 | 13 | 14 | 6 | 1 | 1 |
| 6 | 10^4 | 15 | 15 | 8 | 15/15 | 11 | 15 | 2 | 0 | 0 |
| 6 | 10^6 | 15 | 15 | 7 | 15/15 | 11 | 12 | 6 | 1 | 1 |
| 6 | 10^8 | 15 | 11 | 4 | 11/11 | 9 | 10 | 4 | 1 | 2 |

170 of 170 pairs that reached their target height connected; the connecting bound exceeded max(w_Q, w_Q′) by 0 in 135 cases (79 %), by at most 2 in 158 (93 %), and by at most 8 in all. The largest search used 8,181 nodes. Descent from the high point took 7 steps (median) and returned to max entry 3 in 81 % of cases; the 10 walks that did not reach their target got stuck at every vertex exceeding the walk bound 2^29 first.

---

## 5. Interpretation

1. **Two regimes, one law.** Below w*(Q) the low-weight quivers of a class are islands; at w*(Q) they connect; above it, paths stay within the bound up to a small additive excess that vanishes relative to w. Written as f(Q, w) = max(w, w*(Q)) + ε(Q, w), the conjecture is a statement about two quantities: the threshold w* and the excess ε. The data bounds both at n ≤ 6: w* ≤ 24 and ε ≤ 59 in absolute terms, ε/w ≤ 0.04 at w = 256.
2. **Why excursions cannot be bridges [H].** A mutation that raises the maximal entry from w to roughly w² (the generic growth of note 1) can be undone only by the inverse mutation, and the forms reachable from the high point without returning are a tree-like spike (note 1 §4). Descent from the spike returns to its root. A bridge would need a high-weight path between two low-weight regions that is not homotopic, inside the bounded graph, to a low-weight path; the excursion data found none in 170 attempts up to height 10⁸.
3. **What a proof would need.** A local statement of the form: if a shortest path between two quivers of weight ≤ w passes through a quiver of weight > max(w, w*) + c, then the path can be rerouted around it without increasing its length by more than a bounded amount. This is a confluence-type statement weaker than Neville's (which concerns descent to a canonical form), and the thresholds show it can only hold above w*. In rank 3 it should follow from the Beineke–Brüstle–Hille classification and the Markov constant; that is the first case to try.
4. **The thin low-weight part.** Polynomial growth of |S_w| like w^(n−3) says that a mutation class is "one-dimensional in weight" for n = 4 and gains one dimension per vertex. It explains why iterative deepening is cheap (the search space at bound w′ is polynomial in w′), why the note 1 one-way function had no room, and it is a candidate for an exact statement: the quivers of weight ≤ w in a wild class should be counted by a quasi-polynomial in w of degree n − 3 [H].
5. **Decidability.** With F(n, w) = max(2w, w*_max(n)), bounded search at bound F decides mutation equivalence of weight-≤ w quivers for n ≤ 6 on all data here. Proving any effective F would settle Problem 2.6.12 for bounded-weight inputs. The threshold w*_max(n) is the quantity to understand first; its growth in n (10, 12, 24 at n = 4, 5, 6 on small samples) is unknown.

---

## 6. Limitations

- Sections 1 to 7: n ≤ 6, random dense starting quivers with entries in [−3, 3], 37 exhausted components. Section 8 adds n = 7 (3 exact components at bound 32, 8 at bound 16) and sparse starts (17 exhausted components at n = 5, 6, 7). Quivers with large initial entries were not tested.
- f is exact only below the ambient bound of an exhausted enumeration (4096 or 65536 at n = 4, 128 or 512 at n = 5, 32 or 64 at n = 6); paths through larger weights are invisible by construction. All f values found were far below the ambient bound, so this did not bite, but the n = 6 data stops at w = 32.
- The threshold and excess statistics rest on 7 to 18 components per n; the extreme values (w* = 24, ε = 59) are single components.
- The excursion test uses greedy descent to pick Q′; other descent rules might land on different local minima. The connection search had a 300k-node budget per bound and never needed more than 8,181 nodes.
- The power-law fits use three to six medians each; the exponents are indicative.
- The heart-theoretic reading and the Vinberg–Elashvili style claims are recalled, not re-derived.

## 7. Reproduce

```bash
PY=python
$PY -I mutation_path.py component --n 4 5 --B 8 32 128 512 2048 --trials 2 --budget 2000000 --workers 8 --seed 777 --out bp_sizing.jsonl
$PY -I bounded_paths.py profile --n 4 --B-big 65536 --budget 3000000 --w 3 4 5 6 8 12 16 24 32 64 128 256 --trials 20 --workers 4 --seed 20261108 --out bounded_profile_n4.jsonl
$PY -I bounded_paths.py profile --n 4 --B-big 4096  --budget 3000000 --w 3 4 5 6 8 12 16 24 32 64 128 256 --trials 20 --workers 4 --seed 20261108 --out bounded_profile_n4_B4096.jsonl
$PY -I bounded_paths.py profile --n 5 --B-big 512 --budget 3000000 --w 3 4 5 6 8 12 16 24 32 64 --trials 12 --workers 4 --seed 20261208 --out bounded_profile_n5.jsonl
$PY -I bounded_paths.py profile --n 5 --B-big 128 --budget 3000000 --w 3 4 5 6 8 12 16 24 32 64 --trials 12 --workers 4 --seed 20261208 --out bounded_profile_n5_B128.jsonl
$PY -I bounded_paths.py profile --n 6 --B-big 32 --budget 3000000 --w 3 4 5 6 8 12 16 --trials 8 --workers 4 --seed 20261308 --out bounded_profile_n6.jsonl
$PY -I bounded_paths.py profile --n 6 --B-big 64 --budget 5000000 --w 3 4 5 6 8 12 16 24 32 --trials 8 --workers 3 --seed 20261308 --out bounded_profile_n6_B64.jsonl
$PY -I bounded_paths.py excursions --n 4 5 6 --W-high 100 10000 1000000 100000000 --trials 15 --budget 300000 --workers 6 --seed 20261109 --out bounded_excursions.jsonl
$PY -I bounded_paths.py summarize bounded_excursions.jsonl
```

Same seed and n give the same quivers across ambient bounds, which is what makes §4.1 a like-for-like comparison. `profile` and `excursions` overwrite their output unless `--append` is given.

---

## 8. Extension: n = 7 and sparse starting quivers (run the same day)

### 8.1 A correction to the method

An enumeration that exhausts the component inside ambient bound B_big gives f(Q, w) exactly only if every weight-≤ w quiver of the class is reachable through weights ≤ B_big. A low-weight island joined to the rest of the class only through weights above B_big is invisible, and the run then reports a lower bound. The test for this is the two-bound comparison of §4.1: at n ≤ 6 it never failed (30 of 30). At n = 7 it failed once in three: trial 7 below is exhausted at both bounds 16 and 32, yet reports f(3..12) = 11 to 12 at bound 16 and 17 at bound 32, because a further island of 5,040 weight-3 quivers attaches only through weight 17. So the thresholds in §4.3 are lower bounds in principle; the agreement across bounds is the evidence that they are exact there.

### 8.2 n = 7, dense starts (8 components, ambient bounds 16 and 32)

| Trial | Component size at bound 16 | f(3) | f(4) | f(5) | f(6) | f(8) | f(12) | Exhausted at bound 32? | f at bound 32 (w = 3, …, 24) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 2,756,880 | 8 | 8 | 8 | 8 | 8 | 12 | no (budget 6M hit) |
| 1 | 2,333,520 | 12 | 12 | 12 | 12 | 12 | 14 | no (budget 6M hit) |
| 2 | 372,960 | 12 | 12 | 12 | 12 | 12 | 12 | yes: 12, 12, 12, 12, 12, 12, 16, 24 |
| 3 | 685,440 | 6 | 6 | 6 | 6 | 9 | 12 | yes: 6, 6, 6, 6, 9, 12, 16, 24 |
| 4 | 2,343,600 | 6 | 6 | 6 | 6 | 8 | 12 | no (budget 6M hit) |
| 5 | 5,851,440 | 8 | 8 | 8 | 8 | 8 | 12 | no (budget 6M hit) |
| 6 | 1,537,200 | 14 | 14 | 14 | 14 | 14 | 14 | no (budget 6M hit) |
| 7 | 101,520 | 11 | 11 | 11 | 11 | 11 | 12 | yes: 17, 17, 17, 17, 17, 17, 24, 28 |

All eight components exhaust at bound 16 (101k to 5.9M states); only three exhaust at bound 32 within 6M states, so the remaining five rows at bound 32 are truncated and their values (22 to 32) are the breadth-first artifact of §3, not measurements. Within what is exact: f(12) = 12 in 6 of 8 components at bound 16 and f(12) ≤ 14 in 8 of 8; the three components exact at bound 32 have thresholds 6, 12 and 17 and then f(16) ∈ {16, 16, 24}, f(24) ∈ {24, 24, 28}. The thresholds grow with n: the largest exact values are 10, 12, 24 and ≥ 17 for n = 4, 5, 6, 7.

Forced excursions at n = 7 (dense): 60 of 60 pairs that reached their height reconnected, 49 with zero excess, 52 with excess ≤ 2, maximal excess 13 (bound 16 from weight 3, once at height 10² and once at 10⁸), largest search 212,501 nodes.

### 8.3 Sparse starts: a second regime

> **Correction (note 3):** This staircase is an artifact of the profile code (see the note at the top). Corrected, f(w) ≤ w for every w ≥ 4 in every exhausted sparse component. 3, 8, 21, 55 are the levels that occur, which are Fomin–Neville's Chebyshev weights (Prop. 3.13), not connection bounds. Observations 1 to 3 below and the revised statement of §8.4 do not hold.

Sparse starting quivers (a random spanning tree plus 0 to 2 edges, all weights 1 except one edge of weight 3) give a different profile.

| n | Trial | Edges | Component size | Exhausted | Max entry in component | f(w) for the w list | Max f(w)/w |
|---|---|---|---|---|---|---|---|
| 5 | 0 | 4 | 9,168 | yes | 127 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24, f(32)=45, f(64)=64 | 2.00 |
| 5 | 1 | 4 | 2,568 | yes | 127 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24, f(32)=45, f(64)=64 | 2.00 |
| 5 | 2 | 5 | 74,160 | yes | 127 | f(3)=3, f(4)=4, f(5)=8, f(6)=8, f(8)=8, f(12)=12, f(16)=21, f(24)=24, f(32)=32, f(64)=64 | 1.60 |
| 5 | 3 | 6 | 562,080 | yes | 128 | f(3)=4, f(4)=4, f(5)=5, f(6)=7, f(8)=8, f(12)=13, f(16)=17, f(24)=24, f(32)=32, f(64)=64 | 1.33 |
| 5 | 4 | 4 | 9,168 | yes | 127 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24, f(32)=45, f(64)=64 | 2.00 |
| 5 | 5 | 4 | 4,032 | yes | 63 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=55, f(32)=55 | 2.29 |
| 5 | 6 | 5 | 74,640 | yes | 120 | f(3)=3, f(4)=4, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24, f(32)=32, f(64)=64 | 1.75 |
| 5 | 7 | 6 | 1,823,520 | yes | 128 | f(3)=4, f(4)=4, f(5)=5, f(6)=6, f(8)=8, f(12)=12, f(16)=16, f(24)=24, f(32)=32, f(64)=64 | 1.33 |
| 5 | 8 | 4 | 9,168 | yes | 127 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24, f(32)=45, f(64)=64 | 2.00 |
| 5 | 9 | 5 | 56,160 | yes | 108 | f(3)=4, f(4)=4, f(5)=8, f(6)=8, f(8)=8, f(12)=12, f(16)=21, f(24)=24, f(32)=32, f(64)=64 | 1.60 |
| 6 | 0 | 6 | 837,720 | yes | 64 | f(3)=4, f(4)=4, f(5)=5, f(6)=8, f(8)=8, f(12)=12, f(16)=16, f(24)=24, f(32)=32 | 1.33 |
| 6 | 1 | 7 | 6,000,000 | no | 64 | f(3)=37, f(4)=48, f(5)=48, f(6)=48, f(8)=48, f(12)=48, f(16)=61, f(24)=64, f(32)=64 | 12.33 |
| 6 | 2 | 7 | 6,000,001 | no | 64 | f(3)=3, f(4)=4, f(5)=5, f(6)=7, f(8)=8, f(12)=12, f(16)=19, f(24)=28, f(32)=36 | 1.19 |
| 6 | 3 | 5 | 79,200 | yes | 63 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=55, f(32)=55 | 2.29 |
| 6 | 4 | 7 | 2,522,160 | yes | 64 | f(3)=3, f(4)=4, f(5)=5, f(6)=7, f(8)=8, f(12)=12, f(16)=16, f(24)=24, f(32)=32 | 1.17 |
| 6 | 5 | 5 | 39,360 | yes | 64 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24, f(32)=45 | 2.00 |
| 6 | 6 | 6 | 6,000,000 | no | 64 | f(3)=3, f(4)=4, f(5)=5, f(6)=6, f(8)=8, f(12)=12, f(16)=16, f(24)=24, f(32)=32 | 1.00 |
| 6 | 7 | 6 | 712,800 | yes | 60 | f(3)=4, f(4)=4, f(5)=11, f(6)=11, f(8)=11, f(12)=15, f(16)=29, f(24)=29, f(32)=41 | 2.20 |
| 7 | 0 | 6 | 305,424 | yes | 30 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24 | 2.00 |
| 7 | 1 | 6 | 205,632 | yes | 27 | f(3)=3, f(4)=8, f(5)=8, f(6)=8, f(8)=8, f(12)=21, f(16)=21, f(24)=24 | 2.00 |
| 7 | 2 | 8 | 6,000,000 | no | 32 | f(3)=19, f(4)=19, f(5)=21, f(6)=32, f(8)=32, f(12)=32, f(16)=32, f(24)=32 | 6.33 |
| 7 | 3 | 7 | 6,000,000 | no | 32 | f(3)=3, f(4)=4, f(5)=6, f(6)=6, f(8)=8, f(12)=30, f(16)=30, f(24)=30 | 2.50 |
| 7 | 4 | 7 | 6,000,001 | no | 32 | f(3)=3, f(4)=4, f(5)=6, f(6)=6, f(8)=8, f(12)=24, f(16)=29, f(24)=31 | 2.00 |
| 7 | 5 | 7 | 6,000,003 | no | 32 | f(3)=12, f(4)=16, f(5)=16, f(6)=16, f(8)=16, f(12)=16, f(16)=16, f(24)=24 | 4.00 |
| 7 | 6 | 7 | 6,000,000 | no | 32 | f(3)=12, f(4)=19, f(5)=21, f(6)=28, f(8)=32, f(12)=32, f(16)=32, f(24)=32 | 4.75 |
| 7 | 7 | 7 | 6,000,001 | no | 32 | f(3)=12, f(4)=16, f(5)=16, f(6)=16, f(8)=32, f(12)=32, f(16)=32, f(24)=32 | 4.00 |

Three observations [I]:

1. **A staircase.** In the exhausted sparse components, f(w) ≠ w takes almost only the values 8 (34×), 21 (22×), 45 (5×), 4 (5×), 55 (4×), 11 (3×). The values 3, 8, 21, 55, 144 satisfy u_{k+1} = 3u_k − u_{k−1}, the linear recurrence of the weight-3 Kronecker pair; ratios of consecutive terms tend to (3 + √5)/2 ≈ 2.618. One n = 5 component (trial 5) is exhausted inside ambient bound 128 with maximal entry 63: the corridor's next step is 144. The low-weight quivers of such a class sit on arms that meet at junctions whose weight is the next recurrence term, so S_w becomes connected only when the ambient bound reaches that term.
2. **Unbounded additive excess, bounded ratio.** On the staircase, f(w) − w grows without bound (f(12) = 21, f(24) = 55, and f(56) would be 144), but f(w)/w stays below the corridor ratio: the largest ratio over all exhausted sparse components is 2.29. The bound F(n, w) = 2w suggested by the dense data is violated 3 time(s) in exact data (n=5 trial 5: f(24)=55; n=6 trial 3: f(24)=55; n=6 trial 7: f(5)=11); F(n, w) = max(3w, w*_max(n)) holds on every exact row of this note, including the sparse ones.
3. **A corridor of weight b gives ratio about b [H].** A Kronecker pair of weight b has recurrence u_{k+1} = b·u_k − u_{k−1} with ratio → (b + √(b² − 4))/2 ≈ b. A class containing such a corridor with members of weight ≤ w requires b² − 1 ≤ w, so the multiplicative constant can grow like √w and f(w) like w^(3/2) in the worst case. The right form of the conjecture is therefore polynomial, f(n, w) ≤ C·w^(3/2) or similar, not linear with a universal constant. Any proof must treat rank-2 corridors first; in rank 3 the Markov constant and the Beineke–Brüstle–Hille classification should make this explicit.

Forced excursions with sparse starts (n = 5, 6, 7): 170 of 170 reconnected, 165 with zero excess and all 170 with excess ≤ 1. Excursions are spikes in both regimes; the staircase is a property of the low-weight part itself, not of excursions.

### 8.4 Revised statement

Putting §4 and §8 together, the measured law is

> f(Q, w) = max(w, w*(Q)) + ε(Q, w), where w*(Q) is a class threshold (≤ 24 at n ≤ 6, ≥ 17 at n = 7, growing with n) and ε is small for dense classes, while classes with a heavy rank-2 corridor instead follow a staircase f(w) = next corridor term, with f(w)/w bounded by the corridor ratio.

The decidability consequence of §1 survives in weaker form: bounded search is complete once f(n, w) ≤ F(n, w) for an effective F, and the data supports a polynomial F (max(3w, w*_max(n)) on all exact rows here) but rules out F = 2w and makes a universal linear constant unlikely.

### 8.5 Reproduce (extension)

```bash
PY=python
$PY -I mutation_path.py component --n 7 --B 8 16 32 --trials 2 --budget 6000000 --workers 3 --seed 7777 --out bp_sizing_n7.jsonl
$PY -I bounded_paths.py profile --n 7 --B-big 32 --budget 6000000 --w 3 4 5 6 8 12 16 24 --trials 8 --workers 3 --seed 20261408 --out bounded_profile_n7.jsonl
$PY -I bounded_paths.py profile --n 7 --B-big 16 --budget 6000000 --w 3 4 5 6 8 12 --trials 8 --workers 3 --seed 20261408 --out bounded_profile_n7_B16.jsonl
$PY -I bounded_paths.py excursions --n 7 --W-high 100 10000 1000000 100000000 --trials 15 --budget 300000 --workers 4 --seed 20261409 --out bounded_excursions_n7.jsonl
$PY -I bounded_paths.py excursions --n 5 6 7 --W-high 100 10000 1000000 100000000 --trials 15 --budget 300000 --workers 4 --seed 20261509 --sparse --out bounded_excursions_sparse.jsonl
$PY -I bounded_paths.py profile --n 5 --B-big 128 --budget 4000000 --w 3 4 5 6 8 12 16 24 32 64 --trials 10 --workers 3 --seed 20261508 --sparse --out bounded_profile_sparse_n5.jsonl
$PY -I bounded_paths.py profile --n 6 --B-big 64 --budget 6000000 --w 3 4 5 6 8 12 16 24 32 --trials 8 --workers 3 --seed 20261608 --sparse --out bounded_profile_sparse_n6.jsonl
$PY -I bounded_paths.py profile --n 7 --B-big 32 --budget 6000000 --w 3 4 5 6 8 12 16 24 --trials 8 --workers 3 --seed 20261708 --sparse --out bounded_profile_sparse_n7.jsonl
```

## Sources

- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.12: https://arxiv.org/pdf/1608.05735
- Neville, *Long mutation cycles* (descent in rank 3; non-confluence in general): https://www.arxiv.org/pdf/2304.11505v1
- Soukup, *Complexity of quiver mutation equivalence*: https://arxiv.org/abs/2306.03232
- Recalled [M]: Beineke, Brüstle, Hille, *Cluster-cyclic quivers with three vertices and the Markov equation*; Felikson, Shapiro, Tumarkin (mutation-finite ⟺ weights ≤ 2); Keller–Yang and King–Qiu (mutations as simple tilts; exchange graphs of hearts).
- [Note 1](01-mutation-path-test.md).
