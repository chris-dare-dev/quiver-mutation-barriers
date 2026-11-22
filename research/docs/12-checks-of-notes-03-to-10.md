# 12. Checks of notes 3 to 10

*Prepared 2026-11-11. Notes [3](03-profile-correction-and-rank-3.md) to [10](10-n4-quadratic-bound.md) were written on 2026-11-09, each building on the last, and had not been checked. This note records a separate check of their claims with new code, and a targeted prior-art search. Code: [verify/review12.py](../verify/review12.py) (new; it imports none of the scripts being checked). Results: the `review12_*.log` files. Quivers are up to relabelling unless stated otherwise. Labels: **[P]** proven in a cited source; **[I]** derived or measured in this check; **[H]** heuristic.*

> **Follow-up (note 16):** On 5 vertices the barrier is not quadratic. The quiver P⁺_t of height t² joins its opposite only at 2t⁵ − t⁴ + t² − 1, for every t ≥ 2, so F(5, w) ≥ 2w^{5/2} − 11w². The bound F(n, w) ≥ w(w − 1) of §5 is superseded for n ≥ 5 (for n ≥ 6 by adding isolated vertices; connected quivers on 6 and 7 vertices are measured only). See [note 16](16-five-vertices-above-w-squared.md).

---

## 1. Outcome

**No theorem was found false.** These survived re-derivation and independent computation:

- Theorem 3.1, the rank-3 theorem;
- note 4's persistence formula for f and the elder rule in `pockets.py`;
- note 7's census over all 4-vertex quivers (`n4_all.py`);
- the census numbers of notes 8 and 10, including both extremes;
- Theorem 9.1, including the symbolic proof in `n4_mirror_proof.py`.

**Three results came out stronger:**

1. **Theorem 9.1 has a short proof by hand (§4).** Every mutation of G_k creates an entry of size at least k(k − 1), and μ₀μ₃μ₂μ₁ takes G_k to a relabelling of −G_k. No computer is needed for the bound.
2. **The barrier is not special to n = 4 (§5).** Hang a path of extra vertices from G_k. The result is a connected quiver on any n ≥ 4 vertices with f(Q, k) ≥ k(k − 1). So F(n, w) ≥ w(w − 1) for every n ≥ 4, and Problems 5.2 and 6.1 fail for every n ≥ 4, not only n = 4.
3. **The gap in Theorem 3.1(3) is closed (§3).** The claim "more than one labelled island" had been justified only in the computed cases; it now has a general proof.

**What was wrong or incomplete:**

- Note 9 states, for the whole class of G_k, structure that was shown only for the part inside a bound.
- Note 9 calls Problem 5.2 open for n ≥ 5. It fails there (§5).
- Notes 8 and 9 quote Theorem 3.1 as giving a rank-3 class "a single bottom quiver". It gives a single bottom *island*.
- Note 8's linear fit does not hold "within ±2": the residual at bottom 6 is 3.5.
- Note 10 calls 7,119 duplicate rows "a few", and does not say that its bottom-9 extreme is also a mirror pair.
- Notes 3 and 4 still state, without a note, conclusions about n = 4 that note 7 showed to be artefacts of the sample.
- Note 3's prior-art section is out of date. A paper of 26 October 2026 settles the mutation-acyclic half of the 4-vertex question with a polynomial bound (§6).

**Prior art.** The search found nothing that states Theorem 9.1, any super-linear barrier, or a bound like Conjecture 10.1. For mutation-acyclic 4-vertex classes, arXiv 2610.36179 implies f(Q, w) ≤ w⁴ + 4w³ + 6w². G_k and every census extreme are mutation-cyclic, so they lie outside that result, and Conjecture 10.1 is open exactly where it matters.

All fixes are in place as quoted "Correction (note 12)" notes in notes 3 to 10.

---

## 2. How the check was done

The check was made separately from the notes it checks, starting from their statements, with new code, by a fresh instance of the same AI model that wrote the notes. It is an independent derivation and test, not a specialist's reading. Each claim was first re-derived from its statement and then tested with `review12.py`, which was written for this check. The script imports nothing from the code being checked and departs from it on purpose:

- **Global n = 4 census.** It is recomputed on *labelled* matrices, with relabelling edges added to the graph instead of canonical forms, and with a plain Python union–find.
- **Per-class checks.** These use their own enumerator and their own canonical form: the lexicographic maximum over relabellings, where the original takes the minimum. Persistence pairs are found by recomputing the components at every level from scratch, without union–find.
- **Counts of quivers per level.** These come from Burnside's lemma.
- **The symbolic proof.** It was redone with PARI polynomials (cypari2). Exact real-root thresholds replace Cauchy bounds, and pairwise equality tests up to relabelling replace a canonical key.

The prior-art search was a first reading pass over the papers in §6. The statements this note relies on were then re-read against the sources: Theorem 1.1, Corollaries 5.3 and 5.7, Conjecture 5.5 and §6 of arXiv 2610.36179; the metadata of arXiv 2406.03604; and the abstract of arXiv 1102.3382. Statements marked "according to the reading pass" were not re-read.

---

## 3. Claims checked

### Rank 3 and persistence (notes 3 and 4)

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Theorem 3.1(1)–(2): every quiver of a rank-3 class has maximal entry ≥ w*, and S_w is connected inside G_w for w ≥ w* | 3 §4.3 | Confirmed | The proof (Steps 1–3) was re-derived. Persistence over *all* 3-vertex quivers with entries ≤ 60 finds 0 pockets (`review12_rank3.log`) |
| Theorem 3.1(3), labelled: an acyclic triangle with a weight-1 edge has more than one labelled island below j | 3 §4.3, Step 4 | Gap, now closed | Note 3 justified this only "in every computed case". A general proof is below. The measured part was confirmed on all 396 such triangles with weights ≤ 12 in infinite classes: bottom at w*, 2 or 6 islands, f = j on [w*, j), f(w) ≤ w on [j, 2j], and the least cyclic level is j. The triangle (1, 1, 1), which lies outside note 3's 550 infinite classes, has 2 islands, not 6 |
| "A rank-3 class has a single bottom quiver up to relabelling" | 8 §1 item 5, 9 §1 item 3 | Misquoted | Theorem 3.1 gives one bottom *island*. The acyclic triangle (1, 2, 3) has three bottom quivers, its rotations. A root with xy = 2z has two. The conclusion drawn from it, that rank 3 has no mirror barrier, is unaffected |
| f(w) = max(m_w, max{D : b ≤ m_w < D}) | 4 §2 | Confirmed | Proof: the components of X_{m_w} lie in one component of X_L exactly when all but the eldest have died by L. The components alive at m_w other than the eldest are exactly the pairs with b ≤ m_w < D. Measured: 4,765 of 4,765 values of f agree with the definition on census classes |
| Elder rule in `pockets.py` | 4 §2 | Confirmed | The multiset of (birth, death) pairs does not depend on how ties are broken. 248 census classes were sampled from all five files, half of them with pockets. On each, recomputing the components level by level gives the same pairs, size, bottom and exhaustion as the stored row, which `pockets.persistence` produced |

**The missing step of Theorem 3.1(3) [I].**

1. Source and sink moves keep the weight of every labelled edge. Below j, S_w contains only acyclic quivers, so its labelled islands are the orbits of these moves.
2. An orbit consists of one assignment of weights to the edges, together with the cyclic rotations of one vertex order.
3. Rotate A inside its orbit until its source → elbow edge has weight 1: arrows 1 → 2 (weight 1), 2 → 3 (q) and 1 → 3 (l).
4. Mutate at 2, then 1, then 2. The path passes the cyclic quivers (1, q, l + q) and (1, l, l + q), whose maximal entry is l + q = j, and ends at the acyclic quiver 3 → 2 (l), 2 → 1 (1), 3 → 1 (q). This was checked for all q, l ≤ 14.
5. If q ≠ l, the end quiver gives the edges {2, 3} and {1, 3} different weights from A, so it lies in another orbit.
6. If q = l, its vertex order 3, 2, 1 is the reverse of A's order 1, 2, 3, so again it lies in another orbit.

### The 4-vertex census (notes 7, 8 and 10)

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| 106,918,566 quivers with maximal entry ≤ 18 | 7 §1 | Confirmed | Burnside's lemma gives the same count at all 18 levels (`review12_burnside.log`) |
| The pockets found by `n4_all.py` | 7 §1 | Confirmed for deaths ≤ 8 | A slow labelled implementation over 24,137,569 matrices and 67,148,504 edges finds 1,417 pockets with death ≤ 8, 269 of them with death ≤ 6. These are the same (birth, death) multisets as the stored N = 18 run. The components alive at N = 8, counted by birth level, are identical to those of `n4_all.py --N 8`, apart from the zero quiver, which `n4_all.py` omits (`review12_n4slow_N8.log`) |
| P_k: a plateau of k − 1 quivers with no exit, death k + 2, and lowest reachable level about √k | 7 §1 items 2–3 | Confirmed for k = 5–32 | The lowest levels reached within 2k match note 7's list (`review12_extremes.log`) |
| Note 8's table: classes, classes with several bottom components, latest deaths 12 to 79, ratios, worst ratio above the bottom | 8 §1 | Confirmed | Recomputed from the stored rows (`review12_classes.log`). The 99th percentiles agree up to the percentile convention: by nearest rank they are 3.33, 4.60, 5.67, 6.44 and 7.00 |
| "16.75·b₀ − 38 within ±2 at every point" | 8 §1 item 2 | False as written | The residual is 3.5 at bottom 6. Least squares gives 17.2·b₀ − 40, with residuals ≤ 2.8. The trend is superseded in any case |
| Mirror structure for bottom ≤ 4: 334 classes, 214 of them with mirror pairs | 8 §3 | Confirmed exactly | An own plateau-based test reproduces all six rows of the table |
| 788,026 classes; "a few found a lower bottom" | 10 §1–2 | Count confirmed; wording wrong | 2,213 rows in the bottom-8 file and 4,906 in the bottom-9 file have a lower bottom, as do 461 rows in the bottom-6/7 file. Every one repeats a class already listed, with the same pairs up to the bound |
| Note 10's table (largest deaths 12 … 144); every pocket dies by 1.834·b²; pockets above the bottom die by 1.31·b² | 10 §1 | Confirmed | Recomputed. The maxima are 66/36 = 1.8333 and 106/81 = 1.3086 |
| Extremes: the bottom-6 mirror pair joins at 66, H(9, 8, 4, 2) joins at 144 | 8, 10 | Confirmed | Own enumerator at bound 400, above the census bounds of 256 and 192. H(9, 8, 4, 2) is also a mirror pair: its two bottom quivers are H and −H |
| The heavy-block scan: every other class of that shape is ≤ 1.125 | 10 §1 | Confirmed from the stored scan | H(9, 8, 2, 4) is the same class |
| Spot check of the census | 8, 10 | Confirmed | 248 of 248 sampled classes match the check's enumerator exactly |

### Theorem 9.1 and its proof script (note 9)

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| f(G_k, k) ≥ k(k − 1), with G_k and −G_k joined at exactly k(k − 1) | 9 §1 | Confirmed; short proof | §4. The check's own enumeration gives the join k(k − 1) for k = 3–8, 10, 12 and 16 |
| `n4_mirror_proof.py`: signs, Cauchy bounds, `key`, closure | 9 §3 | Sound | See the notes below the table |
| "Its mutation class contains three quivers of maximal entry k"; "below k² + 4k the class of G_k has only 11 quivers" | 9 §1 | Overstated | Shown only for the component of G_k inside the bound, not for the class. In the PARI search inside 2k², 3k² and k³, the bottom level is the same three quivers each time (31 quivers inside k³). The third bottom quiver is C_k, the oriented 4-cycle with weights k, k − 1, k, k, which is its own opposite |
| "Checked … numerically for k = 3 to 200" | 9 §1 | Wording | Only the values of k listed in §3 were checked |
| `n4_mirror_proof.py` prints `n4_mirror_proof.log` | 9 §6 | Partly | The small-k numerical lines come from a separate driver. `review12.py extremes` reproduces them |
| Problem 5.2 "open for n ≥ 5" | 9 §4 | False | §5 |

**Notes on `n4_mirror_proof.py`.**

- **Signs.** Every sign and comparison goes through `sign`: the signs in the mutation rule, absolute values, maxima, the bound test, the order of levels and the level filter of the union–find.
- **Cauchy bounds.** The bound 1 + max|aᵢ/aₙ| contains every root, so the signs used hold for k > 6.
- **Distinctness.** For each relabelling the script takes the smallest bound among the entries that differ, which is correct.
- **`key`.** It takes the least tuple of normalised coefficient tuples over the 24 relabellings. This is constant on relabelling orbits and separates them, so it is a canonical form for polynomial matrices.
- **Closure.** The closure argument is sound.
- **Independent rerun.** A PARI rerun finds the same 11 quivers and 20 exits, with levels k, k² − k and k² holding 3, 4 and 4 quivers. The largest real root of any polynomial whose sign is used is 3.45, so every sign holds for k ≥ 4, not only for k > 6 (`review12_symbolic.log`).

### Traps and descent (notes 5 and 6)

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| The procedure of Problem 5.2 is complete if c(n) exists | 5 §5 | Correct but void | No such c(n) exists for any n ≥ 4 (§5) |
| Problem 6.1 | 6 §4 | False for every n ≥ 4 | Note 11 proves n = 4 by computer; §4 and §5 here prove every n ≥ 4 by hand |
| "e(x) ≥ D(x), unless x is itself the lightest" | 6 §1 item 1 | Imprecise | The condition needed is that the lowest quiver of the class (least maximal entry first) is lighter than x. Note 6 handles its ten exceptions correctly |

---

## 4. Theorem 9.1: a short proof

Label G_k's vertices 0 to 3 as in note 9. Its arrows are 0 → 1, 2 → 0, 3 → 0 and 1 → 3 of weight k, and 3 → 2 of weight k − 1.

**(a) Every mutation of G_k is heavy.**

| Mutation | New entry | Size |
|---|---|---|
| μ₀ | b₂₁ | k² |
| μ₁ | b₀₃ | k² − k |
| μ₂ | b₃₀ | k² |
| μ₃ | b₁₂ | k² − k |

Each new entry is the product of the two arrows of a path through the mutated vertex, less at most one existing entry.

**(b) The join.** μ₂μ₁(G_k) = C_k, the oriented 4-cycle 0 → 2 → 3 → 1 → 0 with weights k, k − 1, k, k. Its four mutations create the products of the arrows at each vertex: k², k², k² − k and k² − k. Then μ₀μ₃(C_k) is −G_k, relabelled by 0 ↔ 1, 2 ↔ 3. The maximal entries along μ₁, μ₂, μ₃, μ₀ are k² − k, k, k² − k, k.

**(c) G_k and −G_k are different quivers.** Their multisets of (out-weight, in-weight) differ:

- G_k: {(k, 2k), (k, k), (k, k − 1), (2k − 1, k)};
- −G_k: {(2k, k), (k, k), (k − 1, k), (k, 2k − 1)}.

**Conclusion.** For k ≥ 3, k² − k > k. By (a), G_k is then alone in its component of X_L for every L < k² − k, and so are −G_k and C_k. By (b) and (c), −G_k is a second quiver of S_k(G_k). Hence f(G_k, k) ≥ k(k − 1), and G_k, C_k and −G_k are joined at exactly k(k − 1). ∎ `review12.py handproof` checks (a)–(c) with PARI for every k ≥ 3 (`review12_handproof.log`).

**What this changes.**

- The computer-assisted part of note 9 is needed only for the shape of the component inside k² + 4k (three bottom quivers, 11 quivers in all). The bound does not depend on it.
- The same three facts prove note 11's Theorem 11.1. C_k is lighter than G_k (4k − 1 against 5k − 1), so D(G_k) ≥ k(k − 1), with equality along μ₂μ₁.
- G_k is mutation-cyclic. Its full subquiver on {0, 1, 3} is the cyclic triangle (k, k, k), with Markov constant 3k² − k³ < 4, so it is mutation-cyclic by Beineke–Brüstle–Hille [P]. Full subquivers of mutation-acyclic quivers are mutation-acyclic (Warkentin, arXiv 1102.3382) [P], so G_k is not mutation-acyclic.

---

## 5. Every n ≥ 4, connected quivers included

**Proposition 12.1 [I].** Let n ≥ 4 and k ≥ 3. Let Q = Q_{n,k} be G_k with n − 4 further vertices 4, …, n − 1 hung from vertex 0 as a path 0 – 4 – 5 – ⋯ – (n − 1) of weight-1 arrows, oriented in any way. Then:

1. Q is connected and is a local minimum of total weight;
2. f(Q, k) ≥ k(k − 1);
3. μ₂μ₁(Q) lies in the class of Q and is lighter. Every path from Q to a lighter quiver, or to the lowest quiver of the class, passes a quiver of maximal entry ≥ k(k − 1).

Hence F(n, w) ≥ w(w − 1) for every n ≥ 4 and w ≥ 3. Problems 5.2 and 6.1 have no constant c(n) for any n ≥ 4, even when restricted to connected quivers.

*Proof.* Call vertices 0 to 3 the block and the rest the tail.

**The block evolves on its own.** A mutation changes only the entries between neighbours of the mutated vertex. Tail vertices start with all their neighbours in {0} ∪ tail, and a mutation at a tail vertex creates arrows only between such neighbours. So no tail vertex ever becomes adjacent to vertex 1, 2 or 3. The entries inside the block therefore change only under mutations at block vertices, and exactly as in G_k.

**The tail stays small.** The full subquiver on {0} ∪ tail is a path. Under tail mutations it stays in the class of a quiver of type A_{n−3}, whose entries are 0 and ±1, and whose quivers all have at least n − 4 arrows.

**Below k² − k, nothing changes in the block.** By §4(a), every quiver reached from Q through maximal entry < k² − k still has the block G_k. It therefore has exactly four entries of absolute value k, and total weight at least that of Q.

**Item 2.** Let X = μ₀μ₃μ₂μ₁(Q). The mutations μ₁, μ₂ and μ₃ do not touch the tail. μ₀ reverses the arrow between 0 and 4 and creates one arrow of weight k between vertex 4 and vertex 2 or 1. So X has maximal entry k and five entries of absolute value k, and the path to it climbs to k² − k. X lies in S_k(Q) and is isomorphic to no quiver reached below k² − k.

**Item 1.** A tail mutation of the path either leaves the total weight unchanged or adds one arrow. A block mutation adds at least k² − 2k.

**Item 3.** μ₂μ₁ changes only the block, to C_k, which lowers the total weight by k. No quiver reached below k² − k is lighter than Q, and none is the lowest quiver of the class, since μ₂μ₁(Q) has the same maximal entry and is lighter. ∎

`review12.py pendant` checks every item for n = 5, 6 and 7, k = 3, 4, 5, 6 and 8, and both orientations of the tail. It finds 2, 10 and 84 labelled quivers below k² − k for n = 5, 6 and 7, all with block G_k (`review12_pendant.log`).

For disconnected quivers the statement is immediate, because an isolated vertex is fixed by every mutation.

**What this changes.** The barrier-ratio data of notes 4 to 6 for n = 5 to 7 describes random dense classes, not the worst case. Examples are c(5) ≥ 5.39 and the "no growth with weight" conclusion of note 6.

---

## 6. Prior art

### The papers

**Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*, arXiv 2610.36179 (26 October 2026) [P, statements checked].** Height means maximal entry.

- **Theorem 1.1 (= 5.1).** A mutation-acyclic 4-vertex quiver Q reaches an acyclic quiver through quivers of height ≤ max{ht(Q), m(Q)}, where m(Q) is a Markov value.
- **Corollary 5.3.** If Q has a proper wiggle class, then H(Q) ≤ h⁴ + 4h³ + 6h², with h = ht(Q). This covers the mutation-acyclic quivers: Theorem 1.1 evaluates m(Q) on their totally proper wiggle class and states the resulting O(h²⁴) search for them.
- **Conjecture 5.5.** ht(Q) alone suffices. It is verified for heights ≤ 3.
- **Corollary 5.7.** Mutation equivalence up to relabelling is decidable for pairs of 4-vertex quivers of which at least one is mutation-acyclic. According to the reading pass, the paper says the method decides nothing when both quivers are mutation-cyclic.
- **§6.** Theorem 2.9 of their earlier arXiv 2411.04209, which note 3 cites, stated its criterion incorrectly. The paper corrects it (Theorem 6.2) and confirms the class counts 534 and 133.

**Consequence for the bounded-path question [I, from P].** In a mutation-acyclic 4-vertex class, every X in S_w reaches an acyclic quiver through height ≤ w⁴ + 4w³ + 6w². Up to relabelling, the acyclic quivers of one class are joined by source and sink mutations, which keep every weight (Caldero–Keller). So f(Q, w) ≤ w⁴ + 4w³ + 6w² for these classes. If Conjecture 5.5 holds, then f(Q, w) ≤ w, and mutation-acyclic 4-vertex classes have no pockets at all.

**Other papers.**

- **Fomin, Neville, *Cyclically ordered quivers*, arXiv 2406.03604** (v3, May 2026, to appear in Advances in Math.). It builds new mutation invariants. Its introduction says that there is no known algorithm for detecting mutation equivalence. According to the reading pass, its Example 12.10 gives 3-vertex quivers that are not mutation-equivalent to their opposites. It says nothing on weight bounds.
- **Neville, *Mutation-acyclic quivers are totally proper*, arXiv 2409.17832.** Note 3 lists it only as "Neville's Markov-type invariant". It is the input to 2610.36179.
- **Warkentin, arXiv 1102.3382** [P, abstract checked]: full subquivers of mutation-acyclic quivers are mutation-acyclic.
- **No bounds on weights, according to the reading pass.** None of these addresses bounded weights or the barrier between a quiver and its opposite:
  - Ervin, arXiv 2306.07502;
  - Ervin and Neville, arXiv 2504.06573;
  - Seven, arXiv 1201.4270;
  - Ladkani, arXiv 1104.0436;
  - Fomin and Neville, *Long mutation cycles*, arXiv 2304.11505.
- **Soukup, arXiv 2306.03232, §4, according to the reading pass.** It suggests a bound in the style of Coward–Lackenby on how high paths must go, without a theorem. This is the nearest published framing of F(n, w).
- **Chelnokov, arXiv 2311.01784, abstract, according to the reading pass.** Piecewise-polynomial invariants of 4-vertex quivers are functions of det B, so they cannot tell Q from −Q.
- **Not read.** Warkentin's 2014 thesis (its repository blocked automated access) and Neville's 2025 thesis.

### Verdicts

- **Theorem 9.1.** Not found in the literature. Not certain, since the two theses were not read.
- **Conjecture 10.1.** Open. For mutation-acyclic classes, 2610.36179 implies a quartic bound, and its Conjecture 5.5 would give the strong form f ≤ w. The conjecture adds the mutation-cyclic case, where no bound of any kind is known. G_k and the extremes of every birth level from 3 to 9 are mutation-cyclic. All of them but the bottom-5 one contain a mutation-cyclic full triangle in their bottom quiver; the bottom-5 class has one at level 18.
- **The census agrees with this split [I].** Of the 123,691 census classes with a pocket born at ≤ B/4, none contains an acyclic quiver inside its bound. 117,654 contain a quiver with a mutation-cyclic full triangle, so they are mutation-cyclic. 6,037 are left undecided by this test (`review12_cyclic2.log`). This is the class-level form of note 7's finding that no pocket bottom is acyclic.
  > **Update (note 13):** All 123,691 are mutation-cyclic. A per-class search with the certificates of arXiv 2610.36179 settles the 6,037 undecided classes: Lemma 2.4 settles 5,756, a vortex 168 and Corollary 5.2 113 (`n4_conj55_census.log`). This does not use Conjecture 5.5. See [note 13](13-conjecture-5-5-up-to-height-18.md).
- **Decidability at n = 4.** Still open, as of October 2026, for pairs of mutation-cyclic quivers.

---

## 7. Note 10's visibility caveat: a mirror test

Note 10's caveat: a bottom component that joins its class only above the computed bound would be listed as a separate class. Every census extreme is a mirror pair, so a hidden join would most likely be one too. The test (`review12.py mirror`, `review12_mirror.log`) found:

- **The census is closed under B ↦ −B.** For every one of the 788,026 classes, the mirror images of its bottom components are found in the census.
- **Most classes are not their own mirror.** 33,124 classes are. The other 754,902 form 377,451 pairs of distinct classes that are mirror images. A hidden mirror join would look exactly like one of these pairs. That most classes differ from their mirror fits Fomin–Neville's 3-vertex examples.
- **No sampled pair joins higher up.** For bottoms ≤ 7 the census bounds are already at least 5.2·b². For bottoms 8 and 9 (bound 192, which is 2.37·b² at b = 9), 400 random pairs at each bottom were searched up to 6b², and none joined.
- **Mirror structure beyond note 8.** The number of classes with a mirror pair among their bottom components is 2, 36, 176, 313, 673, 838, 1,446 and 1,552 at bottoms 2 to 9.

This is a sample, not a proof. Deciding whether a class equals its mirror needs an invariant that sees orientation, and (gcd, |Pf|) does not (note 11). [Note 11](11-n4-invariants-descent-joins.md), written in parallel, takes the caveat further with invariants and a re-enumeration at 8b².

> **Update (note 14):** 288,393 of the 377,451 mirror pairs are now certified to be two different classes: 267,697 by a complete invariant of classes with a finite core, 96,780 by Caldero–Keller. With the tube certificates of note 14 §8 the count is 375,312, and 2,139 pairs stay open. No pair turned out to be one class. Fomin–Neville's cosquare is the only one of their invariants that sees orientation, and it applies only to totally proper classes. See [note 14](14-opposite-quivers-forks-and-cores.md).

---

## 8. Corrections made in place

- **Note 3.** A note at the head covers the n = 4 statements, the new prior art and the corrected criterion of arXiv 2411.04209. A note after Step 4 gives the proof that closes Theorem 3.1(3).
- **Note 4.** The n = 4 rarity holds only for the sample, and no linear F(n, w) exists for any n ≥ 4.
- **Note 5.** Problem 5.2 fails for every n ≥ 4.
- **Note 6.** Problem 6.1 fails for every n ≥ 4, and the condition for e ≥ D is stated precisely.
- **Note 7.** The checks of this note are recorded, together with the published counterpart of §4's heuristic.
- **Note 8.** The residual of the linear fit, and "one bottom island" in place of "one bottom quiver".
- **Note 9.** A head note covers the short proof, the class-versus-component scope, "one bottom island", n ≥ 5 and the provenance of the log. A note after the theorem fixes the scope of its first sentence.
- **Note 10.** The duplicate rows, H(9, 8, 4, 2) as a mirror pair, r_T·b as a measurement, and the prior art.

---

## 9. Still unchecked

- **The random-sample statistics of notes 3 to 6 at n = 5 to 7.** These are the pocket and trap tables, the records 5.39 and 5.85, and the walks of `hunt.py`. They were checked only through the code they share with the census.
- **Note 3's labelled reruns (§3.1–3.3).** Also the alternative rank-3 argument in Step 3, which the theorem does not need.
- **Whether k is the bottom of the class of G_k.** That is, whether some quiver below level k is reachable only through higher quivers. Theorem 9.1 does not need it.
  > **Update (note 14):** Settled. For every k ≥ 3 the class of G_k consists of a core of seven quivers, three of them at level k, and of far regions whose quivers all have level at least k² − k (Theorem 14.2). So k is the bottom. See [note 14](14-opposite-quivers-forks-and-cores.md).
- **Conjecture 10.1 itself.** Also the visibility caveat beyond the mirror sample of §7; note 11 continues this.
- **The two theses.** Statements marked "according to the reading pass" come from the first reading pass and were not re-read against the sources.

---

## 10. Reproduce

```bash
PY=python
$PY -I ../verify/review12.py burnside --N 18 > review12_burnside.log
$PY -I n4_all.py run --N 8 --out ~/.cache/n4_all_N8.json > /dev/null
$PY -I ../verify/review12.py n4slow --N 8 --ref-same-N ~/.cache/n4_all_N8.json > review12_n4slow_N8.log     # about 2 minutes, several GB
$PY -I ../verify/review12.py rank3 --N 60 --W 12 > review12_rank3.log
$PY -I ../verify/review12.py classes --per-file 25 --slow-max 6000 --f-every 4 > review12_classes.log
$PY -I ../verify/review12.py extremes --B 400 --k 3 4 5 6 7 8 10 12 16 --pk 5 6 7 8 10 12 16 20 24 32 > review12_extremes.log
$PY -I ../verify/review12.py mirror --sample 400 --factor 6 --bottoms 8 9 > review12_mirror.log             # several minutes
$PY -I ../verify/review12.py cyclic > review12_cyclic.log
$PY -I ../verify/review12.py cyclic2 > review12_cyclic2.log                                                 # about 3 minutes
$PY -I ../verify/review12.py symbolic --bounds "k^2+4*k" --show > review12_symbolic.log
$PY -I ../verify/review12.py symbolic --bounds "2*k^2" "3*k^2" "k^3" >> review12_symbolic.log
$PY -I ../verify/review12.py handproof > review12_handproof.log
$PY -I ../verify/review12.py pendant --n 5 6 7 --k 3 4 5 6 8 > review12_pendant.log
```

`review12.py` writes only to standard output, so each log is overwritten when the command is rerun. `classes`, `mirror`, `cyclic` and `cyclic2` read the stored class files of notes 8 and 10, two of them gzip-compressed. `symbolic` and `handproof` need cypari2, which is in `requirements.txt`.

---

## Sources

- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*: https://arxiv.org/abs/2610.36179
- Armstrong-Williams, Hirst, Jackson, Lee, *Machine learning mutation-acyclicity of quivers*: https://arxiv.org/abs/2411.04209
- Fomin, Neville, *Cyclically ordered quivers*: https://arxiv.org/abs/2406.03604
- Neville, *Mutation-acyclic quivers are totally proper*: https://arxiv.org/abs/2409.17832
- Warkentin, *Subquivers of mutation-acyclic quivers are mutation-acyclic*: https://arxiv.org/abs/1102.3382
- Beineke, Brüstle, Hille, *Cluster-cyclic quivers with three vertices and the Markov equation*: https://arxiv.org/abs/math/0612213
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Soukup, *Complexity of ice quiver mutation equivalence*: https://arxiv.org/abs/2306.03232
- Chelnokov: https://arxiv.org/abs/2311.01784
- Ervin: https://arxiv.org/abs/2306.07502; Ervin, Neville: https://arxiv.org/abs/2504.06573
- Notes 3 to 10 and 11 of this repository.
