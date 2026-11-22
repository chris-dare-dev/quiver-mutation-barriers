# 11. Conjecture 10.1: the visibility caveat, descent at n = 4 and the shape of the worst joins

*Run on 2026-11-11. This follows [note 10](10-n4-quadratic-bound.md), which found every pocket born at b ≤ 9 dying by 1.834·b² and stated Conjecture 10.1, F(4, w) ≤ 2w². Three questions are taken up here. How much of note 10's visibility caveat can mutation invariants and a higher enumeration bound close? Does note 6's Problem 6.1, "descent with bounded detours", hold at n = 4? How do the worst joins climb? Note 12, a separate check of notes 3 to 10 made at the same time, is cited where it overlaps. Code: [experiments/n4_evidence.py](../experiments/n4_evidence.py) (new). Results: `n4_bfz_check.json`, `n4_certify.json`, `n4_rejoin_c8_summary.json` and `n4_rejoin_c8.jsonl`, `n4_gk_descent_symbolic.log`, `n4_descent_gk.jsonl`, `n4_descent_summary.json` and `n4_descent.jsonl`, `n4_joins.jsonl` and `n4_joins.log`, and the matching `.log` files. Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

---

## 1. Answer

1. **Two invariants, which separate almost nothing [P, I].** Berenstein–Fomin–Zelevinsky write a mutation as a congruence by an integer unimodular matrix (§2). On 4 vertices the gcd of the entries and |Pf(B)| are therefore mutation invariants. They passed 27,803 random mutation steps (§2). But on the census of notes 8 and 10 they take only 311 values over 788,026 classes. They certify 26 classes as separate from every class with a lower or equal bottom. The other 788,000 share their pair with a class of lower bottom (780,013) or only with classes of the same bottom (7,987). Mutation-acyclicity separates 118 more:
   - Caldero–Keller separates two classes whose bottom quivers are both acyclic;
   - Beineke–Brüstle–Hille with Warkentin separate an acyclic class from one whose bottom has a mutation-cyclic triangle.

   Any of the remaining 787,882 could in principle hide a pocket.
2. **The caveat is narrowed, not closed [I].** Every uncertified class with bottom 6 to 9 was enumerated again up to 8b² (288, 392, 512 and 648), with full persistence: 765,131 classes, 144 million quivers. None reaches a lower level, none joins another bottom component, and no pocket of any birth dies between the census bound and 8b². Classes with bottom ≤ 5 had already been enumerated to 512, which is at least 20·b². So a pocket born at b ≤ 9 that the census cannot see would have to die above 8·b². That is four times the conjectured 2b², and more than four times the largest death seen (1.834·b²). Bounded search cannot exclude it. That needs an invariant that sees orientation (note 12 §7).
3. **Problem 6.1 is false at n = 4 [I].** Let C_k be the oriented 4-cycle with weights k, k, k, k − 1. It lies in the class of G_k and is lighter than G_k (total weight 4k − 1 against 5k − 1). G_k reaches it, or any other lighter quiver, only through a quiver of maximal entry k(k − 1) (Theorem 11.1, §4; note 12 §4 gives a two-line proof by hand, and Proposition 12.1 extends it to every n ≥ 4). So D(G_k) = (k − 1)·max(G_k), and no constant c(4) exists. The starting point, that G_k and −G_k have the same total weight, is true, but the third bottom quiver of the class is lighter than both. On the census (all 788,026 classes, 67.8 million quivers), the largest D/max grows with the bottom much as note 8's barrier ratio did: 3.33, 4.75, 6.60, 10.0, 10.3, 12.4 and 13.6 for bottoms 3 to 9. But D/max² never exceeds 1.67. The quivers of minimal total weight of each class are joined within 1.83·w², where w is their largest maximal entry. So the decision procedure "descend, then join the lightest quivers" survives in quadratic form (Problem 11.2), with the same constant 2 as Conjecture 10.1. The census extremes of note 10 all fall in the join half; G_k falls in the descent half.
4. **The worst joins climb a weight-2 corridor, not a single product step [I].** An optimal join path was extracted for the ten worst pockets at each birth level 3 to 9 (130 pockets), and for G_4 to G_12 (§5). In every case the bottleneck height equals the recorded death. The paths have the same shape:
   - one mutation from the birth level to a first level J, with J ≤ 1.00·b² throughout (the a-priori bound is b + b²);
   - then a run of mutations alternating between the two ends of an arrow of weight 2. Along it the entries grow linearly, by at most 2b per step in the ladders found;
   - then at most a short tail to the peak.

   The peak is a product of two entries of the starting quiver only for G_k (9 of 9), and for 1 of the 70 bottom pockets and 5 of the 60 others. The extremes split as J + corridor + tail. For example b = 9: 144 = 68 + 76 + 0, and b = 6: 66 = 24 + 30 + 12. So note 9's mechanism, a single step to the product k(k − 1), is not how the census extremes arise. A proof of F(4, w) ≤ 2w² along the "one step reaches at most w + w²" route would also have to bound the gain along weight-2 corridors. This gain reaches 1.11·b² in the data.
5. **Status of Conjecture 10.1 [H].** Still open, still supported by every measurement, not proved. What changed:
   - a pocket that the census could hide would now need death above 8·b² (§3);
   - the conjecture splits into a quadratic descent and a quadratic join of the lightest quivers (Problem 11.2). These hold on the census with constants 1.67 and 1.83;
   - the worst joins share one shape, which says where a proof has to bound things (§5);
   - by note 12 §6, a quartic bound from arXiv 2610.36179 already covers the mutation-acyclic classes. The conjecture is open exactly for mutation-cyclic classes, where every extreme lies.

---

## 2. Invariants

**The congruence [P].** In the proof of Lemma 3.2 of *Cluster algebras III* (arXiv math/0305434v3, p. 25), BFZ fix k and a sign ε. They rewrite the mutation rule as

b′_ij = −b_ij if i = k or j = k, and b′_ij = b_ij + b_ik·max(0, ε b_kj) + max(0, −ε b_ik)·b_kj otherwise,  (3.1)

and then as

B̃′ = (J_{m,k} + E_k) B̃ (J_{n,k} + F_k).  (3.2)

Here J is the identity with −1 in position k, E_k has its only nonzero entries e_ik = max(0, −ε b_ik) in column k, and F_k has its only nonzero entries f_kj = max(0, ε b_kj) in row k. The lemma itself states only that mutation preserves the rank; the factorisation is the proof. It was checked against the arXiv PDF.

**For a quiver [I].** If B is skew-symmetric, then f_kj = max(0, −ε b_jk) = e_jk, so F_k = E_kᵀ and μ_k(B) = E B Eᵀ with E = J + E_k. E is an integer matrix. Since J E_k = E_k, E_k J = −E_k and E_k² = 0, we get E² = I, and det E = −1. Hence Pf(μ_k B) = det E · Pf(B) = −Pf(B). The entries of E B Eᵀ are integer combinations of those of B and conversely, so the gcd of the entries is unchanged. On 4 vertices, Pf(B) = b01·b23 − b02·b13 + b03·b12, so |Pf| and gcd are mutation invariants.

**Why nothing stronger comes from this.** An alternating integer 4 × 4 matrix is congruent over GL₄(ℤ) to diag(d₁J₂, d₂J₂) with d₁ | d₂. Here d₁ is the gcd of the entries and d₁d₂ = |Pf|. This is the standard alternating Smith form, recalled and not re-checked here. So (gcd, |Pf|) is the complete congruence invariant. Mutation classes are much finer than congruence classes, and B ↦ −B, which exchanges the two bottoms of every mirror pair, keeps both numbers.

**Numerical check** (`n4_evidence.py bfz`, `n4_bfz_check.json`). The check used 3,000 random paths on n = 4, 5 and 6 vertices, with starting entries in [−4, 4] and up to 40 steps. Each path stopped at the 2³¹ − 1 guard, which 2,997 of them reached; the largest entry seen was 2,138,265,442. All 27,803 steps passed, for both signs ε (55,606 checks):
- E B Eᵀ equals the mutation computed by `mutation_path.mutate`;
- E² = I;
- det E = −1 by exact elimination.

All 9,638 steps on 4 vertices kept (gcd, |Pf|).

**On the census** (`n4_evidence.py certify`, `n4_certify.json`). The five class files of notes 8 and 10 hold 801,772 rows. 13,746 of them repeat a class already listed, always with the same bottom: the bottom ≤ 5 file contains the 6,166 classes with bottom ≤ 4 again, and the others are pockets of lower classes reached from higher survivors. That leaves 788,026 classes, as in note 10.

| | Classes |
|---|---|
| Distinct (gcd, \|Pf\|) values | 311 |
| gcd = 1 | 777,156 |
| Pf = 0 | 7,870 |
| Certified by the invariants: no other class with a lower or equal bottom has the same pair | 26 |
| Certified in addition by Caldero–Keller (acyclic against acyclic) | 6 |
| Certified in addition by acyclic against mutation-cyclic | 112 |
| Share the pair with a class of lower bottom | 780,013 |
| Share it only with classes of the same bottom | 7,987 |

By bottom:

| Bottom | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| Classes | 13 | 147 | 1,050 | 4,956 | 16,714 | 45,287 | 104,579 | 213,511 | 401,769 |
| Certified | 1 | 2 | 2 | 3 | 3 | 4 | 3 | 4 | 4 |
| Lower bottom shares the pair | 0 | 72 | 757 | 4,436 | 16,008 | 44,173 | 103,201 | 211,779 | 399,587 |
| Only equal bottoms share it | 12 | 73 | 291 | 517 | 703 | 1,110 | 1,375 | 1,728 | 2,178 |

The question was only about classes sharing invariants with a class of *lower* bottom. Classes that share them only with classes of the same bottom must be counted too. A second bottom component that joins above the bound is listed as a class with the same bottom as its partner, and note 8's extremes were all of that kind (mirror pairs).

**Caldero–Keller [P].** Two acyclic quivers in one class are joined by sink and source mutations (Cor. 4, restated as FWZ Thm 2.6.11; checked in note 3). These keep the underlying weighted graph, so two census classes whose bottom quivers are both acyclic would have been joined at their common bottom level. 203,602 classes have an acyclic bottom quiver. But a class is certified this way only if it and every class sharing its pair with a lower or equal bottom have acyclic bottoms. That holds for 6 classes.

**Acyclic against mutation-cyclic [P].** By Beineke–Brüstle–Hille (Thm 1.2, checked in note 3), an oriented triangle with weights x, y, z ≥ 2 and x² + y² + z² − xyz ≤ 4 is mutation-cyclic. Full subquivers of mutation-acyclic quivers are mutation-acyclic (Warkentin, arXiv 1102.3382; abstract checked in note 12). So a class whose bottom quiver contains such a triangle is not mutation-acyclic, and it differs from every class with an acyclic bottom. The bottom quivers split as follows:
- 203,602 acyclic;
- 453,344 with a mutation-cyclic triangle;
- 131,080 neither.

A class is certified this way when it and every class sharing its pair with a lower or equal bottom are pairwise separated by these two tests. That adds 112 classes. In all, 144 of the 788,026 classes are certified.

---

## 3. Re-enumeration at 8b²

**Method** (`n4_evidence.py rejoin --c 8`). A hidden pocket born at b in a class C would appear as a census class R of its own. R has the same invariants as C and a bottom at least that of C, and its join lies above the census bounds of both. Pairwise bidirectional search between R and each candidate C would be impractical: on average 788,026/311 ≈ 2,500 classes share a pair. Instead, each uncertified class R was enumerated again from its bottom quiver inside max(census bound, 8b²), and its elder-rule persistence recomputed. A join of R to a lower or equal-bottom region at or below the new bound then shows up as a persistence pair dying above the census bound, whichever partner it joins. The 26 classes certified by invariants were skipped; the 118 certified by acyclicity were re-enumerated anyway.

| Bottom | 6 | 7 | 8 | 9 |
|---|---|---|---|---|
| Census bound | 256 | 256 | 192 | 192 |
| New bound 8b² | 288 | 392 | 512 | 648 |
| Classes re-enumerated | 45,283 | 104,576 | 213,507 | 401,765 |
| Quivers | 9,989,403 | 21,385,497 | 41,559,961 | 71,220,438 |
| Reached a lower level | 0 | 0 | 0 | 0 |
| Pairs dying above the census bound (any birth) | 0 | 0 | 0 | 0 |
| Largest death/birth² over births 3–9 | 1.833 (6 → 66) | 1.612 (7 → 79) | 1.578 (8 → 101) | 1.778 (9 → 144) |

All 765,131 enumerations were exhausted (`n4_rejoin_c8_summary.json`; `n4_rejoin_c8.jsonl`, which would list any class with a finding, is empty). The last row reproduces note 10's extremes.

**What is left of the caveat.** A pocket born at b that the census misses dies above the census bound of its own class, and above the bound at which its own row was enumerated. The table takes the least such bound over the classes that share its invariants (`n4_certify.json`, then the run above):

| Birth b | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| A hidden death would exceed, note 10 | 512·b² | 128·b² | 56.9·b² | 32·b² | 20.5·b² | 7.1·b² | 5.2·b² | 3.0·b² | 2.37·b² |
| … now | 512·b² | 128·b² | 56.9·b² | 32·b² | 20.5·b² | 8·b² | 8·b² | 8·b² | 8·b² |

So the caveat now concerns only pockets with death/birth² > 8, about 4.4 times the largest ratio observed. Note 12 §7, written in parallel, comes at it from the mirror side. It finds that 754,902 of the classes form 377,451 mirror pairs of distinct classes, which is exactly how a hidden mirror join would look. It searched 400 of those pairs at each of bottoms 8 and 9 up to 6b², and none joined. Here every class is covered, to 8b². Neither closes the caveat. A hidden join can only be excluded by an invariant, and (gcd, |Pf|) and acyclicity separate only 144 classes.

> **Update (note 14):** An invariant that sees orientation now exists for most classes. The core of a class (forks and pre-forks) is a complete invariant when it is finite, which holds for 555,828 classes; all of these are certified, against 144 here. 288,393 of the 377,451 mirror pairs are certified to be two classes, and 375,312 with the tube certificates of note 14 §8, which describe the core of 225,208 of the 232,198 classes without a finite core. The 6,990 classes left are still covered only by the 8·b² enumeration of this section. See [note 14](14-opposite-quivers-forks-and-cores.md).

---

## 4. Problem 6.1 at n = 4

For a quiver x that is not of minimal total weight in its class, D(x) is the least bound L such that x reaches a lighter quiver through quivers of maximal entry ≤ L (note 6). Problem 6.1 asks for a constant c(n) with D(x) ≤ c(n)·max(x).

**Theorem 11.1 [I].** For k ≥ 3, let C_k be the quiver with rows (0, −k, 0, k − 1), (k, 0, −k, 0), (0, k, 0, −k), (−(k − 1), 0, k, 0). This is the oriented 4-cycle 0 → 3 → 2 → 1 → 0 with weights k − 1, k, k, k. C_k lies in the mutation class of G_k, and its total weight 4k − 1 is smaller than that of G_k, 5k − 1. Every mutation path from G_k to a quiver of smaller total weight passes a quiver of maximal entry at least k(k − 1), and one such path stays at k(k − 1). Hence D(G_k) = k(k − 1) = (k − 1)·max(G_k), and Problem 6.1 has no constant c(4).

*Proof.* Note 12 §4, written in parallel with this note, shows by hand that each of the four mutations of G_k creates an entry of size k² or k² − k, and that μ₂μ₁(G_k) is the oriented 4-cycle C_k, with maximal entries k² − k and then k along the way. A path from G_k to a lighter quiver begins with a mutation of G_k, so it passes a quiver of maximal entry at least k² − k, and μ₂μ₁ attains this. Hence D(G_k) = k(k − 1). ∎

**An independent check by computer.** I found the theorem by computer before note 12 appeared, as follows. `n4_evidence.py gk-symbolic` reruns note 9's symbolic search, whose closed set S has 11 quivers, and adds the total weight of each member as a polynomial in k (`n4_gk_descent_symbolic.log`). The members of S are:

| Level | Total weight | Members | Lighter than G_k |
|---|---|---|---|
| k | 4k − 1 | 1 (C_k) | yes |
| k | 5k − 1 | 2 (G_k, −G_k) | no |
| k² − k | k² + 3k − 1 | 2 | no |
| k² − k | 2k² + 2k − 1 | 2 | no |
| k² | k² + 4k − 1 | 2 | no |
| k² | 2k² + 3k − 1 | 2 | no |

All signs are valid for k > 6; the largest Cauchy bound over 1,689 polynomials is 6. Take a path from G_k to a lighter quiver. If it stays in S, it ends at C_k. C_k is in another bottom component, and by Theorem 9.1 the bottom components join only at level k² − k. If it leaves S, it passes a quiver of maximal entry above k² + 4k. The union-find over the levels of S finds D(G_k) = k² − k. For 3 ≤ k ≤ 6, `n4_evidence.py descent --gk` computes D exactly on the enumerated class inside (k + 4)k (`n4_descent_gk.jsonl`): D(G_k) = 6, 12, 20, 30. The same run gives k(k − 1) for k = 7 to 12, 16 and 20.

Neither argument needs C_k to be the lightest quiver of the whole class. Note 12 (Proposition 12.1) hangs a path of weight-1 arrows from G_k and gets the same barrier on every n ≥ 4, so Problem 6.1 fails for every n ≥ 4.

**What this changes.** In the class of G_k the lightest quiver of S is unique, so the "join between minimal quivers" half of the decision procedure is trivial there. The difficulty sits entirely in the descent. A descent-based procedure at n = 4 therefore needs detours of quadratic size as well:

**Problem 11.2.** Is there a constant c such that both of the following hold?
- D(x) ≤ c·max(x)² for every 4-vertex quiver x that is not of minimal total weight in its class.
- The quivers of minimal total weight of each class are joined within c·w², where w is the largest maximal entry among them.

Both together would give a decision procedure:
1. Descend from each of the two quivers, searching inside c·max² for a lighter quiver at each step. When no lighter quiver is found, the current quiver has minimal total weight.
2. If the two end quivers have different total weights, the classes differ.
3. Otherwise search for a join inside c·T², where T is their common total weight. T bounds the maximal entry of every quiver of minimal total weight.

**The census** (`n4_evidence.py descent`, `n4_descent_summary.json`). Every class of the census was enumerated with its edges inside min(census bound, 256): 256 for bottoms ≤ 7, 192 for 8 and 9. That is 67,799,154 quivers, all exhausted. D(x) was computed for every quiver x of each component at once, by a union–find over levels in which each component keeps a heap of the quivers still waiting for a lighter one. D is exact relative to the component: a path to a lighter quiver of height at most the bound stays inside it. Every quiver that is not of minimal total weight in its component found a lighter one.

| Bottom | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| Classes | 1,050 | 4,956 | 16,714 | 45,287 | 104,579 | 213,511 | 401,769 |
| Quivers | 1,279,275 | 2,854,423 | 5,074,593 | 8,802,165 | 13,581,871 | 14,886,139 | 20,490,442 |
| Quivers with D > max (descent needs a detour) | 310 | 2,036 | 7,092 | 18,411 | 40,719 | 76,469 | 129,114 |
| Classes containing one | 117 | 807 | 3,254 | 8,771 | 20,943 | 40,585 | 72,782 |
| Largest D/max | 3.33 | 4.75 | 6.60 | 10.00 | 10.29 | 12.38 | 13.56 |
| Largest D/max² (maximal entry ≥ 3) | 1.11 | 1.19 | 1.32 | 1.67 | 1.47 | 1.55 | 1.51 |
| Classes with several quivers of minimal total weight | 913 | 3,888 | 11,552 | 28,773 | 60,724 | 118,038 | 210,625 |
| … that are not joined at their own level | 34 | 228 | 552 | 1,208 | 1,921 | 3,391 | 4,266 |
| Largest join of the minimal quivers / w² | 1.33 | 1.75 | 1.80 | 1.83 | 1.61 | 1.58 | 1.78 |

For bottoms 1 and 2 the largest D/max is 1.0 and 2.0, and D/max² is at most 0.44.

**Reading [I].**
- **The linear form fails on the census too.** The worst D/max grows with the bottom, much as note 8's barrier ratio does. In the worst cases at bottoms 6 and 9, the lightest quivers of the class lie *above* its bottom. At bottom 6 a quiver of maximal entry 6 and total weight 29 reaches the class's unique lightest quiver (total 28, maximal entry 7) only at 60. At bottom 9 a quiver of total weight 42 reaches the two lightest quivers (total 41, maximal entry 22) only at 122.
- **The quadratic form fits.** D/max² stays at or below 1.67, and G_k has D/max² = (k − 1)/k < 1.
- **The join half carries note 10's extremes.** The largest join of the minimal quivers is 12, 28, 45, 66, 79, 101 and 144 at w = 3 to 9. These are exactly note 10's largest bottom-component deaths. In each of these classes there are exactly two lightest quivers, both at the bottom level. So, on this census, both halves of Problem 11.2 hold with c = 2: the descent with 1.67 and the join with 1.83.

---

## 5. The shape of the worst joins

**Method** (`n4_evidence.py joins`, `n4_joins.jsonl`, `n4_joins.log`). The pockets were taken from the class files, ranked by death/birth²:
- the ten worst born at the bottom of their class at each birth b = 3 to 9 (70 pockets);
- the ten worst born above the bottom at each b = 4 to 9 (60 pockets; none is born at 3 above a lower bottom);
- G_4 to G_12.

Each class was enumerated inside the pocket's death. The targets are the quivers of level ≤ b outside the pocket's component at level death − 1. This skips a merger with a sibling born at the same level, which the pocket survives by the elder rule; that happened once, a bottom-6 pocket that meets a sibling at 26 and the eldest component at 56. The join height d is the bottleneck height to the targets. Among the paths of height d, the one chosen has the fewest quivers above b, then the fewest steps. d equals the recorded death for all 139.

**The extremes** (worst pocket at each birth; "corridor" is the longest run alternating between the two ends of a weight-2 arrow, with the level gained along it):

| b | Pocket | Class bottom | Death d | d/b² | J | Before corridor | Corridor steps | Corridor gain | After corridor | Quivers above b | Path steps |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | bottom | 3 | 12 | 1.33 | 8 | −3 | 4 | 6 | 1 | 27 | 28 |
| 4 | bottom | 4 | 28 | 1.75 | 16 | 0 | 2 | 4 | 8 | 7 | 8 |
| 5 | bottom | 5 | 45 | 1.80 | 20 | 0 | 3 | 15 | 10 | 9 | 10 |
| 6 | bottom | 6 | 66 | 1.83 | 24 | 0 | 4 | 30 | 12 | 11 | 12 |
| 7 | bottom | 7 | 79 | 1.61 | 24 | 0 | 5 | 43 | 12 | 13 | 14 |
| 8 | bottom | 8 | 101 | 1.58 | 24 | 0 | 2 | 32 | 45 | 36 | 37 |
| 9 | bottom | 9 | 144 | 1.78 | 68 | 0 | 8 | 76 | 0 | 27 | 28 |
| 4 | above | 3 | 11 | 0.69 | 5 | 3 | 5 | 3 | 0 | 10 | 11 |
| 5 | above | 4 | 26 | 1.04 | 14 | 0 | 4 | 12 | 0 | 8 | 9 |
| 6 | above | 5 | 39 | 1.08 | 16 | 0 | 5 | 23 | 0 | 10 | 11 |
| 7 | above | 6 | 60 | 1.22 | 25 | 0 | 3 | 24 | 11 | 10 | 11 |
| 8 | above | 7 | 79 | 1.23 | 47 | 0 | 7 | 32 | 0 | 14 | 15 |
| 9 | above | 8 | 106 | 1.31 | 62 | 0 | 8 | 44 | 0 | 16 | 17 |
| k | G_k | k | k(k − 1) | (k − 1)/k | k(k − 1) | 0 | 0 | 0 | 0 | 1 | 2 |

d = J + before + corridor gain + after in all 139 paths. "Before" is the net change of level between J and the start of the corridor; it is negative once (b = 3, where the path drops from 8 to 5 before the corridor).

**Over all 139:**

| | Bottom pockets (70) | Pockets above the bottom (60) | G_4 … G_12 (9) |
|---|---|---|---|
| One excursion above b | 69 | 60 | 9 |
| Peak reached in one step from level ≤ b | 1 | 0 | 9 |
| Peak = product of two entries of the starting quiver | 1 | 5 | 9 |
| First level J = product of two entries of the launch quiver | 19 | 15 | 9 |
| Largest J / b² | 1.00 | 0.86 | 0.92 |
| Corridor of ≥ 2 steps on the climb | 59 | 60 | 0 |
| Longest corridor (steps) | 42 | 8 | 0 |
| Largest net gain between J and the corridor / b² | 0.86 | 0.48 | 0 |
| Largest corridor gain / b² | 1.11 | 0.80 | 0 |
| Largest gain after the corridor / b² | 0.94 | 0.22 | 0 |
| Constant-increment ladders (≥ 3 equal rises) | 28 | 9 | 0 |
| Largest ladder increment / b | 2.00 | 1.29 | – |
| Most quivers above b on a chosen path | 115 | 16 | 1 |

**An example.** For the bottom-9 extreme (death 144), the labelled path from the birth quiver runs as follows:
- one mutation, at vertex 0, creates the entry 68 = J;
- eight mutations alternate between vertices 1 and 0, which are joined by an arrow of weight 2. One entry grows 9, 25, 42, 59, 76, 93, 110, 127, 144, by 17 = 2b − 1 per step after the first. The level stays at 68 until that entry passes it;
- along the run two other entries count down, 8, 6, 4, 2, 0 and 7, 5, 3, 1, by 2 every two steps. The corridor ends when the first reaches 0, and the next mutation descends.

The bottom-6 extreme (death 66) is the same:
- J = 24;
- a corridor of four steps, on which the growing entry runs 6, 18, 30, 42, 54 (steps of 12 = 2b) while two entries count down to 0;
- one final step to 66, off the corridor.

**Reading [H].**
- One mutation from level w reaches at most w + w². The data never needs more than b² for the first step, and in the bottom-9 extreme the first step does not even set the peak.
- The rest of the climb is a walk along an affine (weight-2) Kronecker corridor, where entries grow linearly (Chebyshev with parameter 2). In every ladder found the increment is at most 2b.
- In the four extremes printed (b = 6, 7, 8, 9):
  - the increment is a sum of two entries of the birth quiver: 12 = 6 + 6, 12 = 7 + 5, 13 = 8 + 5 and 17 = 9 + 8;
  - the run stops when an entry that starts at most b counts down to 0;
  - the peak is the growing entry: a start of at most b, plus the number of steps times the increment.

  If this held in general, with increment at most 2w and run at most w − 1 steps, the corridor would peak at most w + (w − 1)·2w = 2w² − w. That is just below the 2w² of Conjecture 10.1 (§6), and it is the shape a proof along the "one step reaches w + w²" route would have to take. The bottom-9 extreme, 144 = 2·9·8, is the class of the heavy block H(9, 8, 4, 2) of note 10, with counter 8 and increment 9 + 8.
- Conversely, a family whose counter and increment both stay near their maxima would come close to 2b², and anything more would break the conjecture. Note 10's scan of heavy blocks H(a, c, p, q) found 2ac only once. Engineering a weight-2 corridor with counter c = b − 1 and increment 2b − 1 at the bottom of its class is the natural next experiment.

---

## 6. Status of Conjecture 10.1

**Conjecture 10.1 (F(4, w) ≤ 2w²) remains a conjecture [H].** The evidence now stands as follows.

| | Note 10 | After this note (and note 12) |
|---|---|---|
| Classes covered | 788,026 (bottom ≤ 9) | the same |
| Largest death/birth², births ≤ 9 | 1.834 | the same, reproduced in the re-enumeration to 8b² |
| A pocket hidden from the census would need death/b² above | 2.37 (at b = 9) | 8 |
| Classes certified separate by invariants and acyclicity | – | 144 |
| Lower bound | F(4, w) ≥ w(w − 1) (G_k) | the same, and F(n, w) ≥ w(w − 1) for every n ≥ 4 (note 12) |
| Mutation-acyclic classes | – | f(Q, w) ≤ w⁴ + 4w³ + 6w² (arXiv 2610.36179, via note 12 §6) |
| Descent half, D/max² | – | ≤ 1.67 on the census; Problem 6.1 false in linear form |
| Join half, lightest quivers / w² | – | ≤ 1.83 on the census |

**Why the constant 2 [H].** The three largest ratios of note 10 are 28, 45 and 66 at b = 4, 5, 6. Each equals b(2b − 1) = 2b² − b. The bottom-6 path shows the form b + (b − 1)·2b directly (§5): the growing entry starts at b and gains 2b per step for b − 1 steps. At b = 7, 8, 9 the extremes are lower (79, 101, 144 against 91, 120, 153). If the corridor's run is at most b − 1 steps and its increment at most 2b, the corridor peaks at 2b² − b. That is below 2w² for every w, and would make Conjecture 10.1 nearly sharp.

> **Correction (note 15):** The corridor lemma asked for here is true, but only for the first corridor. From a quiver of height ≤ b with a weight-2 arrow, the run to the first bottom has at most b − 1 steps and the increment is at most 2b ([note 15](15-rank-2-orbits-and-the-constant-2.md) §3.2). The worst joins do not have that shape. The bottom-8 extreme above (101 = 24 + 32 + 45) is the member b = 8 of a family R_b with a mirror join at exactly 2b² − 3b − 3 (Theorem 15.13): b/2 − 1 corridor steps, a commuting square, and then a plateau of b(b − 1)/2 quivers at that height on a second weight-2 line. In the family Q_t of the same note, with b = t², the corridor that carries the barrier starts at height about 2b^{3/2} and runs for about 2b^{3/2} steps with increments √b and 1. What a weight-2 corridor conserves is s_k·s_l·(D − 3) + s_l·a_k + s_k·e_l = ±Pf − 2ζ (Corollary 15.2). Route 1 below therefore does not give a proof as stated. Nothing known exceeds 2b² − b, and the constant 2 cannot be lowered.

**Two routes to a proof.**
1. *Along the shape of the joins (§5).* Show that a join can always be routed through a single step (at most w + w²), or through one step and one weight-2 corridor whose growing entry starts at most w, gains at most 2w per step and runs at most w − 1 steps.
2. *Through descent (Problem 11.2).* Show that D(x) ≤ 2·max(x)², and that the lightest quivers of a class are joined within 2w². G_k shows the first must be quadratic; note 8's mirror pairs show the second must be.

**Where a counterexample would come from.** It is not inside the census unless its death exceeds 8b². Outside it (b ≥ 10), it would be a class whose corridor keeps both the run and the increment at their maxima beyond b(2b − 1), or whose climb chains two corridors. None of the scanned families does this (note 10).

---

## 7. Limitations

- The invariants and the two acyclicity tests certify 144 classes. Everything else about hidden pockets is a lower bound on how far above the bound such a pocket would have to join.
- Births ≤ 9 only, as in note 10. The re-enumeration also sees pockets born above 9 in the classes it re-enumerates, but these are not a census of those births.
- The descent census measures D relative to the enumerated component. This is exact for every quiver in it (§4), but quivers of the class outside the component are not seen.
- The join shapes are for 139 pockets chosen by ratio, not for all pockets. "Corridor" is a measured description, not a lemma.
- The alternating Smith form used to say that (gcd, |Pf|) is all congruence can give was recalled, not re-checked against a source.

---

## 8. Reproduce

```bash
PY=python
$PY -I n4_evidence.py bfz --paths 3000 --length 40 --n 4 5 6 --seed 42 --out n4_bfz_check.json
$PY -I n4_evidence.py certify --out n4_certify.json
$PY -I n4_evidence.py rejoin --c 8 --workers 12 --out n4_rejoin_c8.jsonl > n4_rejoin_c8.log           # 53 minutes
$PY -I n4_evidence.py gk-symbolic > n4_gk_descent_symbolic.log
$PY -I n4_evidence.py descent --gk 3 4 5 6 7 8 9 10 11 12 16 20 --workers 2 --out n4_descent_gk.jsonl
$PY -I n4_evidence.py descent --min-bottom 1 --max-bottom 9 --bound-cap 256 --workers 4 --out n4_descent.jsonl > n4_descent.log   # 49 minutes on 4 workers
$PY -I n4_evidence.py joins --min-ratio 0 --top 10 --workers 3 --out n4_joins.jsonl
$PY -I n4_evidence.py joins-summary n4_joins.jsonl > n4_joins.log
```

All subcommands read the class files of notes 8 and 10 from the current directory, two of them gzip-compressed, and overwrite their output. `rejoin` and `descent` write only the notable classes to their `.jsonl` file and the counts to `_summary.json`.

---

## Sources

- Berenstein, Fomin, Zelevinsky, *Cluster algebras III: upper bounds and double Bruhat cells*, proof of Lemma 3.2, eqs. (3.1)–(3.2): https://arxiv.org/abs/math/0305434
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Beineke, Brüstle, Hille, *Cluster-cyclic quivers with three vertices and the Markov equation*, Thm 1.2: https://arxiv.org/abs/math/0612213
- Warkentin, *Subquivers of mutation-acyclic quivers are mutation-acyclic*: https://arxiv.org/abs/1102.3382
- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Thm 2.6.11 and Problem 2.6.14: https://arxiv.org/abs/1608.05735
- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*, Cor. 5.3, as read in note 12 §6: https://arxiv.org/abs/2610.36179
- Notes 3, 6, 8, 9, 10 and 12 of this repository.
