# 21. The barriers do not reopen the mutation-path one-way function

*Run on 2026-11-12. An earlier survey of candidate one-way functions (a wider project's working document, not included here) §3.2 proposed a one-way function whose secret is a mutation route between two quivers inside an entry bound. [Note 1](01-mutation-path-test.md) killed it: iterative deepening on the bound (attack A3) inverts every planted instance, and the planter pays more than the attacker. Later notes have since found quivers Q whose opposite −Q is joined to Q only far above the height w of Q: R_b and Q_t on 4 vertices at about 2w² ([note 15](15-rank-2-orbits-and-the-constant-2.md)), P⁺_t on 5 vertices at about 2w^{5/2} ([note 16](16-five-vertices-above-w-squared.md)), Q_a on 5 vertices at about 4w³ ([note 18](18-five-vertices-cubic-barrier.md)). This note asks whether such barriers give an asymmetry that a planter could use. Code: [experiments/owf_barrier.py](../experiments/owf_barrier.py) (new). It imports `np_corridor.py`, `np_rowwalk.py` and `n4_doors.py` for the families and drives `np_barrier.c`. Results: the `owf_barrier_*` files in `experiments/`, tabulated by `owf_barrier.py summarize` in `owf_barrier_summary.log`. Notation of notes 15, 16 and 18: the height of a quiver is its largest entry, H is the barrier (the least height at which Q reaches −Q), a step mutates the sink p of a double arrow q → p (Lemma 16.1), and a turn mutates a vertex whose column on the pair is (0, −η) (Lemma 16.2). Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 23):** Checked in [note 23](23-checks-of-notes-20-to-22.md) with new code. No result was found false. Every number recomputed agrees. The jump certificate of §4.2 is sound. 53 fresh instances were inverted, and the routes for t and a = 1,000, of up to 8,006,010,012 mutations, were replayed literally. Corrected below: the two route lengths of §3.1 and §6; the dependence of the sweeps on tie-breaking (§3.1); the cost-table row (c) and §5.3, which give the component as the sweep; "1,010 of 1,506" (§5.1); two conditions that §3.2 needs; "all 90 random rows with a barrier" (§1 item 4); and smaller labels. Q_a at a = 2 needs exactly 120 mutations inside 2⁴⁰ (§5.5).

---

## 1. Answer

**Note 1's verdict stands. The barriers make the bound needed to invert high, but not the cost of inverting.** A barrier of the kind found in notes 15 to 18 is built from linear counters on pairs of weight 2. The same linearity has three consequences, and together they close every way a planter could use the barrier.

1. **A literal route over a barrier is long, so the generic attacker is only polynomially behind the planter [I].**
   - The fewest mutations from Q to −Q do not decrease when the bound is raised above H. The counts are 22, 37, 94, 28 and 94 for R_6, R_8, Q_t (t = 3), P⁺_2 and P⁺_3 at every bound from H up to 2⁴⁰, and 312 for the cubic family at a = 3 up to 2⁴⁰; at a = 2 it is 120 up to 2²⁰ and at least 99 at 2⁴⁰, where the search ran over budget (§5.5).
   - So a planter who publishes a literal route writes down about H/4 mutations (R_b), 2H (Q_a), 4(H/2)^{3/4} (Q_t) or 4(H/2)^{3/5} (P⁺_t).
   - The generic attacker's minimax sweep, which is iterative deepening with exact levels, visits about 2, 1.5 and 2 quivers per mutation of that route for R_b, Q_t and P⁺_t. For Q_a it visits about 12a⁵ quivers against 8a³ mutations, so its cost is about the route length to the power 5/3 (§3.1).
   - **Extrapolated [H].** Suppose F(n, w) grows like w^{n−2}, and the number of quivers of height ≤ B in a class like B^{n−3}. Then the sweep costs w^{(n−2)(n−3)}. That is exponential in the bit length of (Q, Q′), but so is the honest replay. At best the sweep costs the planter's cost to the power O(log of the planter's cost): quasi-polynomial, never exponential (§3.2).

     > **Correction (note 23):** Three corrections to this item.
     > - The ratios 2, 1.5 and 2 and the 12a⁵ are the sweeps when ties at the last level go to the lowest height first, which is the best order for the attacker. At the largest parameters (b = 200, t = 14 and t = 64) other orders give up to 2.0, 2.0 and 2.5 times the route, and 20.5·a⁵ at a = 12. No order gives more than the whole component at H (§3.1).
     > - "Never exponential" holds only under (i)–(iii) of §3.2 and two further conditions: γ is bounded below uniformly in n, and the planted barrier is of order w^{n−2}.
     > - At a = 2 the fewest mutations inside 2⁴⁰ is exactly 120 (§5.5).
2. **A compressed route is cheap for the planter only because the counters are linear, and a structure-aware attacker follows the same counters [I].**
   - **The attacker.** It descends out of fork regions (Warkentin's Lemma 2.5) and by total weight, walks on pairs of weight 2 with the step and turn of Lemmas 16.1 and 16.2, and jumps along each stretch of the walk with an exact certificate (§4).
   - **Results.** It inverted all 246 randomly relabelled instances of R_b, Q_t, P⁺_t and Q_a it was given:
     - heights w from 3 to 2^{128}, barriers up to 2^{321} (P⁺_t at t = 2⁶⁴);
     - public bound H or 10⁶·H;
     - each in at most 71 walks, 1,400 isomorphism tests and 0.04 s;
     - all 192 routes of at most 3·10⁶ mutations were replayed literally and verified.
   - **The generic cost at these sizes [H, extrapolated from §3.1].** Q_a at a = 2⁶⁴ has a route of about 2^{195} mutations and a generic sweep of about 2^{324} quivers. The structure-aware attacker needed 120 operations, 255 tests and under 0.02 s.

     > **Correction (note 23):** "120 operations" counts the attacker's walk operations: 120, 113 and 113 in the three trials. The compressed route it returns has 77 operations in each trial, the figure of §6.
3. **No planter found produces a hard instance [I].**
   - **Random rows over the bounce cycle (n = 5 to 8).**
     - n = 5: a route returns low in 8 to 19 % of draws, with walk height above w³ in 0.1 to 0.4 %, and every planted instance (1,506 of 1,506) was inverted with a verified route.
     - n = 6: 50 of 4,000 draws plant, never above w⁴/2.
     - n = 7 and 8: none of 1,500 draws plants at all.
   - **Perturbations of the explicit families.** Changing one entry by ±1 or ±2 leaves a partner of height ≤ w in only 17 of 288 cases, 10 of them beyond a barrier. Only one barrier is as high as the original's, and the structure-aware attacker inverts all 17.
   - **Random walks inside the bound.** They cross a barrier only after about 40 to 800 times as many steps as the generic sweep visits.

     > **Correction (note 23):** "40 to 800 times" compares with the component at bound h, not with the minimax sweep. For Q_a the component is about twice the sweep: at a = 4 the planter pays 822 times the component and 1,524 times the sweep (§5.3).
   - **Climbs into the forks.** Hiding −Q behind a random climb of up to 30 mutations, to height 10^{98,042}, is undone by fork descent and weight descent: 198 of 198 masked instances were inverted.
4. **Why: the structure leaks [I, H].** It is the fourth of the general causes of failure that the wider project's summary lists (not included here).
   - Every barrier found is a mirror barrier: Q′ is −Q up to relabelling, in all four families and in all 90 random rows with a barrier above w^{n−2}/2.

     > **Correction (note 23):** The 90 random rows are those with walk height h ≥ w^{n−2}/2. Y ≅ −Q in all 90. But in 11 of them, all at w = 3, the generic search escapes lower, at 4, 8 or 9, so their barrier is below w³/2.
   - Its route is a walk out to a symmetric top, followed by the mirror image of the same walk.
   - So the public pair names its own route. A barrier is high because a counter runs for w^{n−2} steps. A counter that runs for w^{n−2} steps is an arithmetic progression, and an arithmetic progression can be jumped over.

What is not settled is in §8. In short, it is a route made of many walks with genuinely different choices at each joint. No such instance is known, and no design for one.

---

## 2. Instance and costs

**Instance [P, the survey §3.2].** Public: two quivers Q, Q′ on n vertices and a bound B. Secret: a mutation route from Q to a relabelling of Q′ through quivers of height ≤ B. Inversion: any such route. Here Q has height w, Q′ ≅ −Q, and B ≥ H, the barrier, so a route exists and none lies below H. Every instance is relabelled at random on both ends.

**The three costs.**
- **Planter.** Either the length L of the literal route, which the verifier replays (L·n² operations on numbers of log H bits), or the number of operations of a compressed route: runs on a pair, single mutations, and repeated periods (§4.1).
- **Generic attacker.** Attack A3 of note 1 with exact levels: the minimax (lowest-bottleneck) search of `np_barrier` from Q, stopped when it reaches another quiver of height ≤ w. Its cost is the number of quivers it pops, written *sweep*. Two variants are also reported:
  - the same search with forks not expanded, which is justified by Lemma 15.5;
  - the whole component at the first level 4^k ≥ H, which is what A3 with levels 4, 16, 64, … sweeps at its last level.
- **Structure-aware attacker.** Walks, walk operations, isomorphism tests and time (§4).

---

## 3. The generic attacker (step 1)

### 3.1 Measured on the four families [I]

`owf_barrier.py generic` (`owf_barrier_generic.jsonl`). L is the length of the route the minimax search finds, which is the published route.

| Family, parameter | w | H | L | Sweep | Sweep, forks pruned | Component at the A3 level 4^k ≥ H | Sweep / L |
|---|---|---|---|---|---|---|---|
| R_b, b = 20 | 20 | 737 | 211 | 410 | 226 | 996 | 1.94 |
| R_b, b = 200 | 200 | 79,397 | 20,101 | 40,100 | 20,206 | 245,636 | 1.99 |
| Q_t, t = 6 | 36 | 2,352 | 796 | 1,206 | 815 | 3,132 | 1.52 |
| Q_t, t = 14 | 196 | 73,920 | 10,588 | 15,905 | 10,626 | 78,742 | 1.50 |
| P⁺_t, t = 8 | 64 | 61,503 | 1,924 | 3,924 | 2,968 | 6,440 | 2.04 |
| P⁺_t, t = 64 | 4,096 | 2,130,710,527 | 1,040,388 | 2,081,732 | 1,561,544 | not run | 2.00 |
| Q_a, a = 6 | 7 | 763 | 2,020 | 99,300 | 28,734 | 365,323 | 49 |
| Q_a, a = 12 | 13 | 6,496 | 14,824 | 3,024,718 | 884,907 | > 9.9·10⁶ (budget) | 204 |

> **Correction (note 23):** Four points on this table.
> - **L** is the route that the minimax search finds. It is the route of Theorem 18.4 plus 4 mutations for even a ≥ 4, and plus 6 for odd a and for a = 2, in every row of `owf_barrier_generic.jsonl`: 2,020 = 2,016 + 4 and 14,824 = 14,820 + 4. §4.3 and §6 use the theorem's route, which is also what the attacker returns.
> - **The sweeps** are those of one tie-breaking order at the last level, lowest height first, which is the best order for the attacker. Over six orders an independent search gives 410–574 at b = 20, 1,206–1,607 at t = 6, 3,924–4,006 at t = 8, 99,302–156,554 at a = 6 and 3,024,719–5,093,974 at a = 12. The ceiling is the whole component at H: 608, 1,618, 5,924, 192,459 and 6,004,807. The ratios and exponents below are therefore best cases, and the conclusions survive.
> - **The A3 level at a = 12** closes at 35,666,621 quivers.
> - **"To within 1 %"** below holds only at b = 200 (0.5 %) and t = 14 (0.4 %). It is 7 % at b = 20 and 2.4 % at t = 6 ([note 23](23-checks-of-notes-20-to-22.md) §3.2).

All 90 rows are in `owf_barrier_summary.log`: 45 members (R_b for 10 values of b, Q_t for t = 3 to 14, P⁺_t for 2 ≤ t ≤ 10 and t = 16, 32, 64, Q_a for 2 ≤ a ≤ 12), each with and without fork pruning. In every row the quiver reached is −Q, at exactly H.

- **R_b, Q_t, P⁺_t: the sweep is a constant times the route.** The ratio settles at 2.0, 1.5 and 2.0. The class below the barrier is the route and little else; note 15 found the same for R_b and Q_t (a region of c + 3 quivers plus the plateau, and 2t³ − t² + 5 quivers). With fork pruning the sweep of R_b and Q_t is the route itself to within 1 %, and that of P⁺_t is 1.5 times the route.
- **Q_a: the sweep grows like a⁵.**
  - It is 12.2·a⁵ at a = 10 and 12 (note 18 reports about 12a⁵), and 3.6·a⁵ with fork pruning (note 20 reports about 4a⁵ for the core). The route has 8a³ + O(a²) mutations.
  - So the sweep is about the route length to the power 5/3: log(sweep)/log(L) is 1.55 at a = 12 and rises towards 5/3.
  - The extra quivers are note 20's lines: each round of the route continues as a line of steps beyond its ends for about A further quivers, and these lines lead nowhere.
- **A3 with coarse levels** costs up to 15 times the exact sweep, because its last level overshoots H by up to a factor 4.

So for fixed n the generic attacker's cost is the planter's literal cost to the power 1 (three families) or 5/3 (Q_a). Random rows give the same picture (§5.1): the sweep grows like h^{1.65} and is a median of 12 and at most 34 times the route.

### 3.2 What the conjectured growth gives [H]

Write s for the input size, s ≈ C(n, 2)·log₂(2w + 1) bits.

**What the proven bounds give [I].**
- *Lower bounds.* F(4, w) ≥ 2w² − 7w + 2 (Corollary 15.14). F(5, w) ≥ 4w³ − 15w² + 19w − 11 for 3 ≤ w ≤ 23 (Corollary 18.6; note 20 extends the range).
- *Consequence.* A3 must reach those heights on some pair, and the measured sweeps of §3.1 are polynomials in w: about w² for R_b and 12w⁵ for Q_a.
- *At fixed n this is already exponential in s,* because w is exponential in its own bit length. So is the honest replay, which is a polynomial in w of degree 2 (R_b) or 3 (Q_a). The question is therefore not whether the generic cost is exponential in s, but how it compares with the planter's.

**Under conjectures.** Assume:
- **(i)** F(n, w) ≍ w^{n−2}. This is Question 18.8; the values w, 2w², 4w³ for n = 3, 4, 5 suggest it.
- **(ii)** The quivers of height ≤ B in a class number about B^{e(n)} with e(n) ≈ n − 3. Note 2 fitted 1.14, 1.88 and 2.26 for n = 4, 5, 6.

Then A3 at the barrier sweeps about F^{e(n)} ≈ w^{(n−2)(n−3)} = 2^{(n−2)(n−3)·log₂ w} quivers. Since s ≈ (n²/2)·log₂ w, this is about 2^{2s(1 − O(1/n))}. **So yes: under (i) and (ii) the generic cost is exponential in the size of the input as n grows.**

That is the wrong comparison, because the honest side is exponential in s too:
- **(iii)** The literal route over a barrier has length at least H^γ. In the four families γ is 1 (R_b, Q_a), 3/4 (Q_t) and 3/5 (P⁺_t). §5.5 finds no shorter route at any higher bound it searched to the end.

So the planter's replay costs T ≥ F^γ ≈ w^{γ(n−2)}, and the generic cost is about T^{e(n)/γ}:
- **For fixed n** that is a polynomial.
- **For growing n**, the barrier needs w ≥ 2 (every family has w ≥ 3), so T ≥ 2^{γ(n−2)} and n ≤ 2 + log₂ T/γ. The generic cost is then at most T^{(log₂ T)/γ²}: quasi-polynomial in the planter's own cost.
- **The cryptographic requirement** is a generic cost of 2^λ for a planter cost poly(λ). It would need n of order λ/log λ, and then T ≥ 2^{γ(n−2)} is not polynomial. Under (i) to (iii) that is impossible.

> **Correction (note 23):** The algebra is right, but the conclusion needs two conditions that are not stated. (1) γ must be bounded below uniformly in n. If γ(n) → 0, for example like 1/n, then T ≥ 2^{γ(n−2)} no longer bounds n. (2) The planted barrier must be of order w^{n−2}, so that n = O(log H). Assumption (i) bounds F(n, w), the maximum over all quivers, not the barrier of the instance. A planter with H much smaller than w^{n−2} on many vertices is not covered. Under (ii) its sweep would be about H^{n−3}, exponential in n, while T stays polynomial in H. On the other hand, (ii) is not needed for the quasi-polynomial bound: the trivial e(n) ≤ C(n, 2) gives 2^{O((log T)³)}. (ii) is needed only for "exponential in s". Note 2's fit at n = 6, 2.26, is 25 % below n − 3. Assumption (iii) is measured on four families whose routes are linear counters, and note 20's spirals show that entries can also grow geometrically along a route ([note 23](23-checks-of-notes-20-to-22.md) §4.3).

The only way out is to compress the route, so that T is polynomial in log H rather than in H. Then H can be 2^λ and the generic cost is H^{Θ(1)} = 2^{Θ(λ)}: a real gap against the generic attacker. Sections 4 and 5 show that the compression is exactly what the structure-aware attacker undoes.

---

## 4. A structure-aware attacker (step 2)

### 4.1 What it does [I]

`owf_barrier.py`, classes `Walk` and `Attack`.

1. **Descent.**
   - *Fork descent.* While a quiver is a fork (Warkentin, Def. 2.1), mutate at its point of return. By Warkentin's Lemma 2.5 every other mutation of a fork is a heavier fork, so this is the only way down. By the Tree Lemma 2.8 it retraces any climb into the fork's far region (note 14 §3; the definition holds on any number of vertices, note 19 §4).
   - *Weight descent.* Between fork steps, the steepest descent on total arrow weight (note 1, attack A2). Its end is a second starting quiver at each end; the end after fork descent alone is the first.
2. **Walks.** On a pair of weight 2 with two arrows q → p:
   - *Step.* The walk mutates p, the sink (Lemma 16.1).
   - *Turn.* It turns at a vertex y of a chosen turn set T when y's column is (0, −η), η ≥ 1 (Lemma 16.2). If the step is lower than the turn, it steps first and turns at the next quiver, where y's column is (−η, 0): the two ways round the commuting square of Lemma 18.2(Q) end at the same quiver.
   - *Runs.* Between events the walk moves by runs. While every column has first entry ≥ 0, l steps are the closed form (A, B) ↦ (A + l·d, B − l·d) with d = A + B, and the entries between the other vertices do not change (Lemma 16.1). A run stops at the first event: a turn, a column at its bottom (the last position with first entry ≥ 0), the end of that regime, or the bound.
   - On W_m(j) with T = {r, s} this is the bounce-cycle walk of note 18 (Lemmas 18.1 and 18.2). For R_b, Q_t and P⁺_t the turns are note 15's and note 16's turns at the counters.
3. **Periods.** When the walk turns at the same vertex with the same orientation of the pair twice, the stretch between the two turns is a candidate period. The attacker replays it on the line X(k) = X + k·(X − X_prev), with every entry an affine function c₀ + c₁k (§4.2). If the replay certifies the period for 0 ≤ k < K, the walk jumps K periods at once.
4. **Search.**
   - From both ends (Q and Q′), and from −Q and −Q′ (the backward walks), the attacker runs a walk for every pair of weight 2 and every turn set.
   - At depth d + 1 it starts again from the quivers at the ends of the depth-d operations and from their neighbours, lowest first, up to 400 per end. This is how R_b reverses direction at the plateau and how odd b changes pair.
   - A match is a quiver met from both ends, up to relabelling. It can be a quiver of height ≤ w met anywhere on a walk (inside runs and jumps it is found by solving linear inequalities), a quiver at the end of an operation, or a neighbour of one.
   - The default depth is 4.

The output is a compressed route: for each end a list of runs, single mutations and repeated periods, then the reversed list from the other end, relabelled.

### 4.2 Why the jumps are exact [I]

Let X_prev and X be the quivers at two consecutive turns of the same kind, with X = P(X_prev) for the period P of recorded decisions. Put S(k) = X + kΔ, Δ = X − X_prev, entry by entry.
- **Replay.** The attacker replays P on S(k). Each decision of the walk at k = 0 (turn or not, step or run, run length, which event ends the run, the sign of every factor in the mutation rule b′_ij = b_ij + [b_ik]₊[b_kj]₊ − [−b_ik]₊[−b_kj]₊) becomes a requirement that an affine function of k keeps its sign, or stays zero, on 0 ≤ k ≤ k_max.
- **Inside a run.** The first entry A_e + i·d_e is bilinear in the position i and in k. A bilinear function on a rectangle takes its extreme values at the corners, so four corner checks bound the whole run.
- **Products.** A product of two non-constant entries fails the certificate. In every period found, one factor is a core entry that does not depend on k.
- **Squares.** The choice between the two ways round a commuting square is not re-checked for every k. Both ways end at the same quiver, and the recorded one is height-checked, so the word is a valid route either way; the certificate is about the mutation word, not about the walk's preferences.
- **Heights.** Each height requirement |c₀ + c₁k| ≤ B bounds k.
- **Conclusion.** If the replay ends at S(k + 1) entry by entry, then P(S(k)) = S(k + 1) for every integer 0 ≤ k ≤ k_max: on that range every mutation of the period is the same polynomial map, and the affine identity holds identically in k. Hence Pᴷ(X) = S(K) for K = k_max + 1, and every quiver inside the jump has height ≤ B.

**Checks** (`owf_barrier.py selftest`, `owf_barrier_selftest.log`):
- the closed form of a run against integer mutation, on 2,999 random runs with n = 4 to 7;
- the canonical form against `np_corridor.canon`;
- for Q_a with 2 ≤ a ≤ 8: the accelerated walk against the walk without jumps (same end quiver, same length, same low quivers), and every recorded prefix replayed literally.

### 4.3 Results [I]

`owf_barrier.py attack` (`owf_barrier_attack.jsonl`, `owf_barrier_attack_bigbound.jsonl`). Three random relabellings per row; maxima over the three.

| Family, parameter | Public bound | Walks | Iso tests | Compressed route (ops) | Route (mutations) | Time | Literal replay |
|---|---|---|---|---|---|---|---|
| R_b, b = 5 to 13, 20, 60, 61, 100, 200, 1,000, 1,001 | H | ≤ 71 | ≤ 880 | 8 (even b), 11–12 (odd b) | 17 to 501,504 | ≤ 0.03 s | all verified, height H |
| R_b, b = 10⁶, 2⁶⁴ | H | 71 | 880 | 8 | 5.0·10¹¹, 2^{127} | ≤ 0.03 s | too long |
| Q_t, t = 3 to 14, 60, 1,000, 10⁶, 2⁶⁴ | H | 1 | 3 | 9 | 94 to 2^{194} | < 0.01 s | verified up to t = 60 |
| P⁺_t, t = 2 to 10, 16, 32, 64, 1,000, 10⁶, 2⁶⁴ | H | ≤ 17 | ≤ 267 | 8–11 | 28 to 2^{194} | ≤ 0.01 s | verified up to t = 64 |
| Q_a, a = 2 to 12, 22, 48, 64, 1,000, 10⁶, 2⁶⁴ | H | ≤ 20 | ≤ 458 | 56–79 | 120 to 2^{195} | ≤ 0.02 s | verified up to a = 64 |
| R_b, Q_t, P⁺_t, Q_a at 8, 9, 1,000, 10⁶ | 10⁶·H | ≤ 71 | ≤ 1,400 | as above | as above | ≤ 0.04 s | verified where ≤ 3·10⁶ |

- **Totals.** 246 instances, 246 inverted. 192 routes were replayed literally and verified: they end at the relabelled Q′, and their height is exactly H, even when the public bound was 10⁶·H. The other 54 are too long to replay; their lengths agree with the closed forms (2a + 2)(4a² − a + 6) for Q_a and 4t³ − 2t² + 4 for Q_t and P⁺_t.

> **Correction (note 23):** Nine of the 54 routes not replayed are R_b, at b = 10⁶ and 2⁶⁴. For even b their length is b(b − 1)/2 + b + 1. Since then the routes of Q_t and P⁺_t at t = 1,000 (3,998,000,004 mutations) and of Q_a at a = 1,000 (8,006,010,012) have been replayed literally, and reach the relabelled opposite at exactly H. Only Q_a routes use jumps, four per route.
- **Q_t and P⁺_t.** One walk from Q does it: the walk climbs the counter, turns at the top by Lemma 16.3, and runs down the mirror image to −Q.
- **Q_a.** The walk from Q is the route of Theorem 18.4. It is found in the first one to twenty walks. Its long stretches S3 and S4 (note 20 §2.2), on the way up and again on the way down, become four certified jumps; the whole route from Q to −Q is one walk.
- **R_b.** It needs depth 1: after the line, the plateau is walked backwards. Odd b leaves the line by a mutation at a column's bottom, which breaks the pair, and a second mutation makes a new pair.
- **Cost is flat in the parameter.** The work depends on how many stretches the route has, not on how long they are: 8 to 79 operations for routes of 17 to 2^{195} mutations.

### 4.4 Fork descent [I]

`owf_barrier.py mask` (`owf_barrier_mask.jsonl`). Q′ is −Q followed by a random climb of l mutations, with no immediate repeat, and the public bound is the height of the climb.

| Member | Climb l | Trials | Climb ends at a fork | Fork descent alone undoes the whole climb | log₁₀ of the largest height | Inverted | Depth | Max time |
|---|---|---|---|---|---|---|---|---|
| R_8, R_9 | 5, 10, 20 | 60 | 59 | 49 | 2,917.3 | 60 | 0–1 | 0.04 s |
| Q_t, t = 4 | 5, 10, 20 | 30 | 30 | 23 | 3,738.5 | 30 | 0 | < 0.01 s |
| P⁺_t, t = 4 | 5, 10, 20 | 30 | 26 | 2 | 1,145.1 | 30 | 0 | < 0.01 s |
| Q_a, a = 5, 6 | 5, 10, 20 | 60 | 59 | 27 | 829.5 | 60 | 0 | 0.17 s |
| all six | 30 | 18 | 18 | 11 | 98,041.7 | 18 | 0–1 | 2.95 s |

- **The climb soon reaches the forks.** A random climb from −Q enters a fork region after a few mutations: 192 of 198 climbs end at a fork. Once a climb with no immediate repeat reaches a fork it stays among forks, by Warkentin's Lemma 2.5, because the point of return is the vertex just mutated.
- **Fork descent retraces it.** Fork descent climbs back down the tree of forks exactly.
- **What it leaves is short.** The part of the climb before the first fork is a few mutations through non-forks, and fork descent alone undoes the whole climb in 112 of 198 cases. For P⁺_4 it rarely does: the class is bushy near −P⁺_4.
- **Weight descent finishes it.** Steepest descent on total weight (note 1's A2) removes the residue: every masked instance was inverted, at depth 0 or 1.
- A first version of the attacker without weight descent failed on 16 of 30 masked P⁺_4 instances (other random climbs); with it, none fails.

---

## 5. Planting (step 3)

### 5.1 Random rows over the bounce cycle, n = 5 to 8 [I]

`owf_barrier.py rows` (`owf_barrier_rows_n{5,6,7,8}.jsonl`, `owf_barrier_rows_n6_dense.jsonl`).

**The planter.**
- Q is W_m(j) at its lowest position (m = 2w − 1, j = w, height w; for n = 5 this is R_{w−1} with a fifth vertex, the base of Q_a), with n − 4 further vertices.
- Each further vertex gets a random state (A, B, U, V) with entries in [−w, w]. The further vertices are not joined to each other ("star"), or joined by random entries in [−w, w] ("dense").
- The planter walks Q by the bounce-cycle rule (pair (p, q), turn set {r, s}), forwards and backwards, inside the cap 64·w^{n−2}. It plants (Q, Y) for the first quiver Y of height ≤ w on the walk that is not isomorphic to Q.
- Its secret is the walk to Y, and h is the height of that walk.

**The two attackers.** `np_barrier` from Q at height w with cap h (`np_barrier8`, the same source with MAXN = 8, for n = 8), and the structure-aware attacker on (Q, Y) relabelled, with public bound h.

| n, w | Draws | Planted | h ≥ w^{n−2}/2 | h ≥ w^{n−2} | Largest h (/w^{n−2}) | Its route | Its generic sweep | Planter walk ops (median) | Generic reaches Y exactly at h | Structure-aware: inverted, verified | Iso tests (median, max) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5, 3 | 3,000 | 569 | 46 | 9 | 86 (3.19) | 474 | 6 (a lower route exists) | 48 | 358 | 569, 569 | 231, 19,758 |
| 5, 4 | 3,000 | 395 | 25 | 9 | 83 (1.30) | 296 | 4,660 | 38 | 257 | 395, 395 | 130, 1,782 |
| 5, 5 | 3,000 | 286 | 14 | 12 | 187 (1.50) | 570 | 11,521 | 35 | 212 | 286, 286 | 155, 1,088 |
| 5, 6 | 3,000 | 256 | 5 | 4 | 428 (1.98) | 1,188 | 40,560 | 34 | 183 | 256, 256 | 133, 899 |
| 6, 3 | 1,500 | 23 | 0 | 0 | 23 (0.28) | 18 | 963 | 56 | 14 | 23, 23 | 825, 1,514 |
| 6, 3, dense | 1,000 | 22 | 0 | 0 | 10 (0.12) | 12 | 75 | 57 | 15 | 22, 22 | 719, 1,875 |
| 6, 4 | 1,500 | 5 | 0 | 0 | 8 (0.03) | 8 | 37 | 49 | 2 | 5, 5 | 464, 1,062 |
| 7, 3 | 1,000 | 0 | – | – | – | – | – | 62 | – | – | – |
| 8, 3 | 500 | 0 | – | – | – | – | – | 70 | – | – | – |

- **On 5 vertices random rows do plant, and with barriers of the right order.** The largest are 2w³ at w = 6, against 4w³ for the designed Q_a. They are rare: a walk height ≥ w³ in 0.13 to 0.40 % of draws, falling with w.

> **Correction (note 23):** The rates of walk height ≥ w³ are 0.30, 0.30, 0.40 and 0.13 % for w = 3 to 6, so they do not fall monotonically. And 4w³ is the limit of H(a)/w³ for the designed family. At w = 6 the designed Q_5 has H = 437 = 2.02·w³, the same order as the best random row, and an independent planter's fresh draw planted a barrier of exactly 437.
- **Every one of the 90 rows with h ≥ w³/2 plants the opposite, Y ≅ −Q.** Where the generic escape equals h (1,010 of 1,506 rows), the sweep grows like h^{1.65} and is a median of 12 and at most 34 times the route (47 rows with h ≥ 50). It is the Q_a picture again.

> **Correction (note 23):** The generic escape equals h in 1,216 of the 1,506 rows. 1,010 is the number of those in which, in addition, the first quiver of height ≤ w other than Q that the search pops is Y. That depends on tie-breaking: another order gives 1,096. The exponent 1.65 is a fit over the 47 rows with h ≥ 50; over all 1,216 rows the slope is 1.88. In 11 of the 90 rows with h ≥ w³/2, all at w = 3, the escape is below h.
- **Every planted instance falls to the structure-aware attacker, at depth 0:** among the walks it tries from each end (every pair of weight 2, both directions, every turn set) is the planter's own walk. All 1,506 routes were replayed and verified.
- **From 6 vertices on, random rows stop planting.**
  - At n = 6 the walks return low in 0.3 to 2.2 % of draws, never above w⁴/2, and never at the opposite.
  - At n = 7 and 8, none of 1,500 walks returns low inside 64·w^{n−2}.
  - With k further vertices, a return needs every one of them to come back at the same time. Lemma 16.3 needs η·S_ey = 2(A_e + B_e) for each of them at one turn, and k independent random slopes almost never meet that.
  - So the cubic-type barrier on more vertices, if it exists, has to be designed. Random rows do not give w^{n−2}.

### 5.2 Perturbations of the explicit families [I]

`owf_barrier.py perturb` (`owf_barrier_perturb.jsonl`). Every quiver obtained by changing one entry by ±1 or ±2 while keeping the height ≤ w, from R_b for b = 6, 7, 8, 10, from Q_t for t = 3, 4, from P⁺_t for t = 2, 3, and from Q_a for a = 3 to 6: 288 quivers.

For each one:
- the generic search for another quiver of height ≤ w, up to 4H;
- the planter's walks for every pair, direction and turn set, up to 64H;
- the structure-aware attacker on whatever partner either finds.

- **271 of the 288 have no partner at all.** No other quiver of height ≤ w is reached below 4H, and no walk finds one below 64H. A planter cannot plant them: it has no route to publish.
- **7 have a partner only at height ≤ w.** It is joined to them without any barrier (the cubic family at a = 3, 4, 5).
- **10 have a partner beyond a barrier.**
  - One is high: (−5, −6, 5, −2, 4, −6), a perturbation of R_6. It joins its opposite at 52 (H(R_6) = 51) by a route of 83 mutations that runs on six different pairs. The generic sweep is 148 quivers. The structure-aware attacker needs depth 3: 777 walks, 8,825 tests, 0.3 s.
  - The other 9 have barriers of at most 0.41·H: 21 for R_6, 42 for Q_t at t = 3, 13 for P⁺_2, and 6 to 25 for the cubic family. Their generic sweeps are at most 35 quivers.
- **The structure-aware attacker inverts all 17.**

So perturbing a family member hides nothing. It either destroys the instance or leaves a smaller one.

### 5.3 Height-restricted random walks [I]

`owf_barrier.py rwalk` (`owf_barrier_rwalk.jsonl`, `owf_barrier_rwalk_qa.jsonl`).
- The component of Q at bound h is dumped by `np_barrier --dump`.
- The planter walks it at random: a random vertex at each step, and a mutation that would leave the bound is refused and counts as a step.
- It stops at the first quiver of height ≤ w that is not Q.

| Member | h | Component (≈ generic sweep) | Trials hit | Median steps | Median / component |
|---|---|---|---|---|---|
| R_8 | H = 101 | 98 | 100/100 | 5,216 | 53 |
| R_12 | H = 249 | 220 | 100/100 | 21,536 | 98 |
| R_12 | 2H | 574 | 100/100 | 55,536 | 97 |
| Q_t, t = 4 | H = 440 | 476 | 100/100 | 176,734 | 371 |
| P⁺_t, t = 4 | H = 1,807 | 764 | 100/100 | 323,996 | 424 |
| P⁺_t, t = 4 | 2H | 1,620 | 100/100 | 801,851 | 495 |
| Q_a, a = 2 | H = 21 | 1,189 | 100/100 | 197,041 | 166 |
| Q_a, a = 3 | H = 88 | 8,070 | 20/20 | 4,688,634 | 581 |
| Q_a, a = 4 | H = 212 | 27,923 | 20/20 | 22,955,922 | 822 |

All 20 rows are in the summary. The corridor over a barrier is a path, so a random walk crosses it diffusively, in about the square of its length. A planter who samples by walking at random inside the bound pays 40 to 800 times what the generic attacker pays, and the ratio grows with the parameter. This is note 1's "planting costs more than inverting", now on the families with the highest barriers.

> **Correction (note 23):** The column "Component (≈ generic sweep)" is the component at bound h, which includes the quivers of height exactly h. For Q_a it is about twice the minimax sweep: 27,923 against 15,065 at a = 4. Against the sweep, the planter pays 1,524 times as much there, not 822.

### 5.4 Masking by a climb

See §4.4. A planter who publishes a high Q′, obtained from −Q by a random climb, hides nothing: fork descent and weight descent bring Q′ back to −Q. Up to 30 mutations of climb, to height 10^{98,042}, they found the route in every case.

### 5.5 No short literal route above the barrier [I]

`owf_barrier.py shortest` (`owf_barrier_shortest.jsonl`, `owf_barrier_shortest_pruned.jsonl`): a bidirectional breadth-first search for the fewest mutations from Q to −Q, inside bounds from H up to 2⁴⁰. It was run twice:
- over every quiver within the bound, with a budget of 3·10⁶ quivers;
- skipping forks higher than w, with a budget of 6·10⁶. This is exact: a shortest route is reduced, and by Lemma 15.5 a reduced route between quivers of height ≤ w passes no fork higher than w.

| Member | H | Fewest mutations at bound H | … at 4H, 16H, 256H | … at 2²⁰ | … at 2⁴⁰ | Quivers searched at 2⁴⁰, forks skipped (all quivers) |
|---|---|---|---|---|---|---|
| R_6 | 51 | 22 | 22, 22, 22 | 22 | 22 | 353 (24,336) |
| R_8 | 101 | 37 | 37, 37, 37 | 37 | 37 | 342 (58,259) |
| Q_t, t = 3 | 132 | 94 | 94, 94, 94 | 94 | 94 | 650 (104,377) |
| P⁺_t, t = 2 | 51 | 28 | 28, 28, 28 | 28 | 28 | 122,166 (over budget) |
| P⁺_t, t = 3 | 413 | 94 | 94, 94, 94 | 94 | 94 | 78,124 (1,010,527) |
| Q_a, a = 2 | 21 | 120 | 120, 120, 120 | 120 | between 99 and 120 (over budget) | > 6.06·10⁶ (over budget) |
| Q_a, a = 3 | 88 | 312 | 312, 312, 312 | 312 | 312 | 4,824,416 (over budget) |

- **Raising the bound does not shorten the route.** In every search that finished, the shortest route at a bound far above H is as long as the route at H. A planter cannot buy a short secret by going higher.
- **Without the high forks, the class is small even at 2⁴⁰.** Searching all quivers at 2⁴⁰ meets the bushy high region that note 1 found, and for P⁺_2 and Q_a it runs over budget. Skipping the forks that Lemma 15.5 rules out leaves a few hundred quivers for R_b and Q_t and about 10⁵ for P⁺_t. The cubic family keeps far more high quivers that are not forks, consistent with note 20's spirals: 4.8·10⁶ at 2⁴⁰ for a = 3. For a = 2 the search ran over 6·10⁶ and proves only that no route inside 2⁴⁰ has fewer than 99 mutations.

> **Correction (note 23):** The cell for Q_a at a = 2 and 2⁴⁰ is now settled: the fewest mutations is 120. An independent search with forks higher than w skipped finished at 7,800,118 quivers. P⁺_2 over all quivers at 2⁴⁰ also finished: 28, from 3,505,268 quivers.

---

## 6. Cost table

Planter: the literal route (mutations), and the compressed route (operations of the planter's own walk). Generic: the minimax sweep (quivers), measured; at large parameters it is extrapolated from the fits of §3.1 [H]: about b² for R_b, 1.5·(4t³) for Q_t, 2·(4t³) for P⁺_t, and 12.2·a⁵ for Q_a. Structure-aware: isomorphism tests and time, measured.

| Instance | n | w | Barrier | Planter: literal route | Planter: compressed | Generic sweep | Structure-aware | Outcome |
|---|---|---|---|---|---|---|---|---|
| R_b, b = 200 | 4 | 200 | 79,397 | 20,101 | 8 ops | 40,100 | 880 tests, 0.03 s | inverted |
| R_b, b = 2⁶⁴ | 4 | 2⁶⁴ | 2^{129} | 2^{127} | 8 ops | ≈ 2^{128} [H] | 880 tests, 0.03 s | inverted |
| Q_t, t = 14 | 4 | 196 | 73,920 | 10,588 | 9 ops | 15,905 | 3 tests | inverted |
| Q_t, t = 2⁶⁴ | 4 | 2^{128} | 2^{257} | 2^{194} | 9 ops | ≈ 2^{194.6} [H] | 3 tests | inverted |
| P⁺_t, t = 64 | 5 | 4,096 | 2.1·10⁹ | 1,040,388 | 11 ops | 2,081,732 | 3 tests | inverted |
| P⁺_t, t = 2⁶⁴ | 5 | 2^{128} | 2^{321} | 2^{194} | 11 ops | ≈ 2^{195} [H] | 3 tests | inverted |
| Q_a, a = 12 | 5 | 13 | 6,496 | 14,820 | 77 ops | 3,024,718 (884,907 pruned) | 222 tests, 0.01 s | inverted |
| Q_a, a = 22 | 5 | 23 | 41,171 | 88,320 | 76 ops | ≈ 6.2·10⁷ (note 18: 61,875,173 below H) | 255 tests, 0.01 s | inverted |
| Q_a, a = 2⁶⁴ | 5 | 2⁶⁴ | 2^{194} | 2^{195} | 77 ops | ≈ 2^{324} [H] | 255 tests, 0.01 s | inverted |
| (a) random rows, n = 5, w = 6, best of 3,000 | 5 | 6 | 428 | 1,188 | 34 ops per draw; ≈ 750 draws per h ≥ w³ | 40,560 | ≤ 899 tests | 1,506 of 1,506 inverted |
| (a) random rows, n = 6 | 6 | 3–4 | ≤ 23 | ≤ 18 | ≈ 56 ops per draw | ≤ 963 | ≤ 1,875 tests | 50 of 50 inverted; none above w⁴/2 |
| (a) random rows, n = 7, 8 | 7, 8 | 3 | – | – | 62–70 ops per draw | – | – | nothing planted in 1,500 draws |
| (b) perturbations | 4, 5 | 4–16 | ≤ 52 (≈ H once) | ≤ 83 | – | ≤ 148 | ≤ 8,825 tests | 271 of 288 unplantable; 17 of 17 inverted |
| (c) random walk, Q_a, a = 4 | 5 | 5 | 212 | median 2.3·10⁷ steps | – | 27,923 | 415 tests | planter pays 822× the sweep |
| Masking by a climb of 5 to 30 | 4, 5 | 6–16 | the climb, up to 10^{98,042} | climb + route | – | not run (bound 10^{98,042}) | ≤ 3 s | 198 of 198 inverted |

> **Correction (note 23):** In row Q_a, a = 12, the literal route 14,820 is the route of Theorem 18.4; §3.1's L = 14,824 is the minimax route. In row (c), 27,923 is the component at H; the minimax sweep is 15,065, so the planter pays 1,524 times the sweep. The generic sweeps of the table are best cases of tie-breaking (note in §3.1).

**Reading the table.**
- *Literal secret.* The generic attacker is within a constant (R_b, Q_t, P⁺_t) or a 5/3 power (Q_a, random rows) of the planter.
- *Compressed secret.* The generic attacker is exponentially behind, and the structure-aware attacker is level with the planter: it runs the planter's own walk.
- *Planters other than the family formulas.* They either cannot plant (n ≥ 7, 271 of 288 perturbations), or plant low barriers, or pay more than the generic attacker (random walks).

---

## 7. Why the structure leaks [I, H]

The mechanism behind every barrier found has three parts.

1. **A counter climbs linearly.** It is a column on a pair of weight 2 that moves through an arithmetic progression (Lemma 16.1). A fifth vertex over a bounce cycle is the same thing one level up: a ball between two walls whose slopes change by a fixed linear map at each bounce (Proposition 18.3).
2. **The top is symmetric.** At the top, Lemma 16.3 or the mirror rule 18.2(M) identifies the walk with its mirror image.
3. **The route is the walk there and back.** It is a walk to the top, followed by the walk back as the opposite.

Each part leaks.
- **(1) is why the barrier is high and why it is compressible.** A counter reaches height w^{n−2} only by running w^{n−2} steps of an arithmetic progression. That is why literal routes are long (§5.5) and the generic attacker keeps pace. It is also why a short description exists: the progression is an affine function of the step count, and the attacker certifies and jumps it as easily as the planter writes it (§4.2).
- **(2) fixes Q′.** In every family, and in all 90 random rows with h ≥ w^{n−2}/2, the far quiver is −Q. The instance names its own target, and the route to it is the walk from Q, so inverting is planting.
- **(3) bounds the search.** A route that is one walk out and one walk back has at most two segments from each end, so a search over walk programs from both ends is shallow: depth 0 for Q_t, P⁺_t, Q_a and every random row, and depth 1 for R_b.

This is cause 4 of the wider project's summary (not included here) in a new place. Here the leaked invariant is not a lattice or a Mukai vector but the piecewise-linear structure of mutation on a pair of weight 2. The same structure gave Proposition 15.3, the closed forms of Theorems 15.6, 16.4 and 18.4, and note 20's lines.

---

## 8. What is not settled [H]

- **Routes of many walks.** Suppose a planted route consisted of r ≫ 1 walk segments joined at high quivers, with b ≥ 2 genuinely different continuations at each joint, all of them still ending low and above a barrier. A meet-in-the-middle over walk programs would then cost about b^{r/2}, and the generic sweep would cost H^{Θ(1)} with H exponential.
  - Nothing found has this shape. Every route found uses at most four segments per end: the 83-step R_6 perturbation needed depth 3, everything else depth ≤ 1.
  - Random rows lose their returns as soon as more than one vertex has to come back (§5.1).
  - Joining walks at quivers that are not low is the "large-n low-weight band" of note 1 §4.4 in another form. It is a mathematics question, and no design for it is known.
- **The attacker is a search, not a theorem.** It inverts every instance it was given. It is not proved to invert every instance with a barrier, for instance one whose stretches grow quadratically: the certificate refuses products of two growing entries, and the walk then falls back to single steps.
- **Large n is extrapolated.** Assumptions (i) and (ii) of §3.2 are conjectures (Question 18.8 and note 2's fits). No family with F(n, w) ≍ w^{n−2} is known for n ≥ 6, and random rows do not produce one.
- **The survey's other attacks were not needed** (g-vector reconstruction, tropical linearisation).

---

## 9. Limitations

- **Parameters.**
  - The generic sweeps stop at a = 12 for Q_a (3·10⁶ quivers) and at t = 64 for P⁺_t; larger values in §6 are extrapolations [H].
  - The A3 level component was capped at 10⁷ quivers.
  - The random rows use w ≤ 6 at n = 5, w ≤ 4 at n = 6, and w = 3 at n = 7 and 8, with caps 64·w^{n−2}.
  - The perturbations cover ±1 and ±2 in one entry of 12 family members.
- **`np_barrier8`** is `np_barrier.c` with MAXN = 8 and MAXM = 28, compiled into `~/.cache/qmb-np/`. It was used for one n = 8 run, in which nothing was planted, so it was never actually called.
- **The canonical form `ckey`** sorts the vertices by a relabelling-invariant signature and minimises over the permutations within each class. The selftest compares it with `np_corridor.canon`.
- **Literal verification** was run for every route of at most 3·10⁶ mutations. Longer routes rest on the certificate of §4.2 and on agreement with the closed forms of the route lengths.
- **Attacker versions.** Weight descent (§4.1) was added after a first masking run had failed on 16 of 30 P⁺_4 instances. Every stored result was rerun with the final code.

---

## 10. Reproduce

```bash
PY=python
$PY -I np_corridor.py build                                    # np_barrier in ~/.cache/qmb-np/
sed -e 's/^#define MAXN 7$/#define MAXN 8/' -e 's/^#define MAXM 21$/#define MAXM 28/' np_barrier.c > ~/.cache/qmb-np/np_barrier8.c
gcc -O2 -o ~/.cache/qmb-np/np_barrier8 ~/.cache/qmb-np/np_barrier8.c
$PY -I owf_barrier.py selftest > owf_barrier_selftest.log
$PY -I owf_barrier.py generic --l4 --budget 10000000 --out owf_barrier_generic.jsonl > owf_barrier_generic.log     # about 4 minutes
$PY -I owf_barrier.py attack --families R --params 5-13,20,60,61,100,200,1000,1001,1e6,2^64 --trials 3 --verify 3000000 --out owf_barrier_attack.jsonl
$PY -I owf_barrier.py attack --families Qt --params 3-14,60,1000,1e6,2^64 --trials 3 --verify 3000000 --out owf_barrier_attack.jsonl --append
$PY -I owf_barrier.py attack --families P+ --params 2-10,16,32,64,1000,1e6,2^64 --trials 3 --verify 3000000 --out owf_barrier_attack.jsonl --append
$PY -I owf_barrier.py attack --families Qa --params 2-12,22,48,64,1000,1e6,2^64 --trials 3 --verify 3000000 --out owf_barrier_attack.jsonl --append
$PY -I owf_barrier.py attack --families R Qt P+ Qa --params 8,9,1000,1e6 --trials 3 --bound-factor 1000000 --verify 3000000 --out owf_barrier_attack_bigbound.jsonl
$PY -I owf_barrier.py rows --n 5 --w 3 4 5 6 --rows 3000 --generic --budget 5000000 --seed 1 --out owf_barrier_rows_n5.jsonl
$PY -I owf_barrier.py rows --n 6 --w 3 4 --rows 1500 --generic --budget 2000000 --seed 2 --out owf_barrier_rows_n6.jsonl
$PY -I owf_barrier.py rows --n 6 --w 3 --rows 1000 --mode dense --generic --budget 2000000 --seed 3 --out owf_barrier_rows_n6_dense.jsonl
$PY -I owf_barrier.py rows --n 7 --w 3 --rows 1000 --generic --budget 300000 --seed 4 --out owf_barrier_rows_n7.jsonl
$PY -I owf_barrier.py rows --n 8 --w 3 --rows 500 --generic --budget 100000 --seed 5 --out owf_barrier_rows_n8.jsonl
$PY -I owf_barrier.py perturb --out owf_barrier_perturb.jsonl
$PY -I owf_barrier.py rwalk --members R:8 R:10 R:12 Qt:3 Qt:4 P+:2 P+:3 P+:4 Qa:2 --out owf_barrier_rwalk.jsonl
$PY -I owf_barrier.py rwalk --members Qa:3 Qa:4 --bound-factors 1 --trials 20 --max-steps 200000000 --seed 2 --out owf_barrier_rwalk_qa.jsonl   # about 4 minutes
$PY -I owf_barrier.py mask --lengths 5 10 20 --trials 10 --out owf_barrier_mask.jsonl
$PY -I owf_barrier.py mask --lengths 30 --trials 3 --seed 2 --out owf_barrier_mask.jsonl --append
$PY -I owf_barrier.py shortest --out owf_barrier_shortest.jsonl                                    # about 15 minutes
$PY -I owf_barrier.py shortest --prune --budget 6000000 --out owf_barrier_shortest_pruned.jsonl    # about 15 minutes
$PY -I owf_barrier.py summarize > owf_barrier_summary.log
```

- The `*.log` files of `rows`, `perturb`, `mask` and `shortest` repeat their `.jsonl` rows.
- The rows runs and the random walks are seeded, so the numbers repeat exactly. The search order of the attacker depends on the random relabelling, so its cost columns can vary a little between runs.
- `rwalk` was first started with Q_a at a = 3 and 4 included, 100 trials each. It was stopped by hand after the other members and rerun for Q_a with 20 trials, as above. The stopped run had not flushed its `.jsonl`, so `owf_barrier_rwalk.jsonl` was restored from the rows printed in `owf_barrier_rwalk.log`. The first command above gives the same rows, because those members draw the same random numbers. Every subcommand now flushes after each row.
- The pruned `shortest` run was stopped during Q_a at a = 2 and bound 2⁴⁰; its first 35 rows were restored from its log, and the last seven searches were run as three separate commands and appended. The single command above gives the same rows.

---

## Sources

- Notes [1](01-mutation-path-test.md) (attacks A1 to A3 and the verdict), [2](02-bounded-paths.md) §1 (the count exponents), [14](14-opposite-quivers-forks-and-cores.md) §3 (forks, far regions, Theorem 14.1), [15](15-rank-2-orbits-and-the-constant-2.md) (R_b, Q_t, Lemma 15.5), [16](16-five-vertices-above-w-squared.md) (Lemmas 16.1 to 16.3, P⁺_t), [18](18-five-vertices-cubic-barrier.md) (the bounce cycle, Lemmas 18.1, 18.2, Proposition 18.3, Q_a), [19](19-checks-of-notes-13-to-16.md) §4 (Warkentin's lemmas on any number of vertices) and [20](20-core-of-the-cubic-family.md) (the core of Q_a and its lines) of this repository.
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Def. 2.1, Lemmas 2.5 and 2.8, as read for note 19: https://d-nb.info/1214302807/34
