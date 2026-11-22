# 14. When is a 4-vertex quiver mutation-equivalent to its opposite? Forks, cores and mirror pairs

*Run on 2026-11-11. [Note 12](12-checks-of-notes-03-to-10.md) §7 found that the census of notes 8 and 10 is closed under B ↦ −B, with 33,124 self-mirror classes and 377,451 pairs of mirror classes, none of them certified distinct. A pair that is really one class joined above the census bound would hide a pocket, which is note 10's visibility caveat. This note looks for an invariant that sees orientation. Code: [experiments/n4_opposite.py](../experiments/n4_opposite.py), [experiments/n4_opposite_run.py](../experiments/n4_opposite_run.py), [experiments/n4_opposite_gk.py](../experiments/n4_opposite_gk.py) and [experiments/n4_opposite_tubes.py](../experiments/n4_opposite_tubes.py) (new; they import none of the earlier scripts). Results: the `n4_opposite_*` files in `experiments/`. Quivers are up to relabelling unless stated otherwise. −Q is the opposite quiver, with every arrow reversed. The level of a quiver is its maximal entry and its weight is its number of arrows. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

---

## 1. Answer

1. **Fomin–Neville's invariants [P, I].** Of the invariants of arXiv 2406.03604, only the integral congruence class of the unipotent companion U, and with it the GL₄(ℤ) conjugacy class of the cosquare U⁻ᵀU, can tell Q from −Q. The Alexander polynomial, the Markov invariant and the Alexander lattices are the same for Q and −Q (§2, with proof). All of them are invariants of a mutation class only when the class has a totally proper cyclic ordering. That is certified for 334,168 census classes and impossible for at least 132,611, whose class contains a vortex. A test of whether the cosquare is conjugate to its transpose, through ideal classes, separates 92,999 of the 160,019 mirror pairs it can be run on (assuming GRH), every one of them also certified by item 2 or by Caldero–Keller. In 301 pairs the cosquare is conjugate to its transpose although the two classes are different, so the invariant cannot separate them.
   > **Correction (note 19):** In 301 pairs the test proves the cosquare conjugate to its transpose, but that is a small part of the failures. In random samples of the pairs it left undecided, an explicit conjugator in GL₄(ℤ) exists in 1,398 of 2,500 complete pairs and 639 of 2,500 acyclic pairs. So the cosquare fails to separate thousands of pairs, acyclic ones included. Both of its verdicts depend on GRH as computed, since `bnfcertify` was not run. All 332 verdicts "conjugate" have since been confirmed without GRH by explicit conjugators. See [note 19](19-checks-of-notes-13-to-16.md) §6.1.
2. **A complete invariant for 70.5 % of the census: the core [P, I].** Warkentin's forks and pre-forks cut a mutation class into far regions, which hang from the rest by a single edge and only get heavier, and what is left. Theorem 14.1 (§3): the quivers reached from Q without stepping up into a far region form a set V′(Q); two quivers are mutation-equivalent exactly when their sets meet; and when V′(Q) is finite it contains a least closed part, the *core*, which is the same for every quiver of the class. So for classes with a finite core, mutation equivalence is decided by a search with no bound on the entries, and Q ~ −Q exactly when the core is its own mirror image. 555,828 of the 788,026 census classes have a finite core, of at most 77 quivers.
3. **Certified counts [I].** Of the 377,451 mirror pairs of census classes, 288,393 (76.4 %) are certified to be two different mutation classes by finite cores and Caldero–Keller: 267,697 by the core and 96,780 by an acyclic quiver in the class, 76,084 by both. No two census classes have the same core, so no hidden join was found (§4). With the tube certificates of item 8 the count rises to 375,312 (99.4 %), and 2,139 pairs stay open.
4. **Note 10's visibility caveat [I].** It is closed for the 555,828 classes with a finite core: each is certified different from every other census class, including the 232,198 without a finite core. Before this note, 144 classes were certified. With the tube certificates, 781,036 classes (99.1 %) are pairwise certified different, so a hidden join would have to involve one of the other 6,990. More is true for these classes: their pockets at *every* level can be listed (§5). There are 70,376, born at levels 3 to 58. The largest death/birth² is 1.578 and none exceeds 2, so f(Q, w) ≤ 2w² for every w in these classes. This is a theorem for 239,507 of them, where the largest ratio is 0.703; for the others it rests on one measured property of pre-fork regions.
   > **Correction (note 19):** "A theorem for 239,507 of them" should read 258,363. Proposition 14.3 does not need its core to lie in no far region, so it covers every finite-core class whose far regions are rooted at forks. That adds the 18,856 classes whose core is two forks with a common point of return. The largest ratio there is still 0.703. The other 297,465 classes rest on the measured property. See [note 19](19-checks-of-notes-13-to-16.md) §6.3.
5. **The class of G_k is now known completely (Theorem 14.2, §6) [I].** For every k ≥ 3 its core is seven quivers: G_k, −G_k and the 4-cycle C_k at level k, two at level k² − k and two at level k². Every other quiver of the class has level at least k² − k. So k is the bottom of the class, which note 12 §9 left open; the class has exactly three quivers below level k² − k; and f(G_k, w) = k(k − 1) for every k ≤ w < k(k − 1).
6. **How self-mirror classes realise the reversal [I].** In 28,306 of the 33,124 self-mirror classes a bottom component is its own mirror; in the other 4,818 the bottom components are exchanged in pairs and the reversal happens only above the bottom. Among the 20,434 with a finite core, the map Q ↦ −Q fixes a quiver of the core in 11,167, exchanges the two ends of an edge in 8,235, and does neither in 1,032 (§7). A core with an odd number of quivers always contains a quiver isomorphic to its opposite.
7. **The barrier is not always a mirror join, but the extremes are [I].** Among the classes with several bottom components, the last death belongs to a mirror pair in 4,973 of 15,250. At every bottom from 2 to 9 the largest death does (§7).
8. **The classes without a finite core: tube certificates [I].** These 232,198 classes contain infinite families of quivers that are never forks, in which one vertex grows while the other three keep a small triangle ("tubes", §8). They include the extremes of note 10 at bottoms 2 to 7 and at 9. In a tube the entries follow a linear recurrence, and a finite certificate proves that the core is a finite part plus such families; the bottom of the core is then a finite invariant. 225,208 of the 232,198 classes are certified this way, among them the extremes at bottoms 3 to 7 and 9. The certificate code was written separately from the rest of this note and checked against the census, not read line by line.
9. **What is left [I].** 6,990 classes (0.9 %) have neither a finite core nor a tube certificate, and 2,139 mirror pairs are open. The pockets of the tube classes above the census bound are not listed. A general lemma for tubes, in place of one certificate per class, is missing.
   > **Update (note 22):** [note 22](22-tube-lemma-and-its-limits.md) proves a general lemma for tubes: the step at a dominant growing vertex is a strict up-exit, steps inside the triangle are linear, the recurrence of §8 is the monodromy of a periodic walk with τ set by the Markov constant of the triangle, and every such tube is eventually certifiable. It also proves that no lemma of this form covers every class: the class of the Markov triangle with one pendant arrow (class 707) has a V′ that no finite set plus finitely many tubes contains. Of the 6,990 classes, 2,206 are now certified with polynomial families, the 400 disconnected ones are settled by rank 3 and 1,556 are mutation-acyclic; 2,828 connected classes, mutation-cyclic as far as their bottom quivers show, and 1,211 mirror pairs remain open.

---

## 2. Fomin–Neville: which invariants see the orientation

I read §§1–2, 4–9 and 11–15 of *Cyclically ordered quivers* (arXiv 2406.03604v3, 18 May 2026) in the arXiv PDF.

### What the paper builds [P]

- **Cyclically ordered quiver (COQ).** A quiver with a cyclic ordering σ of its vertices. A *wiggle* swaps two consecutive vertices that are not joined by an arrow (Definition 2.3).
- **Proper vertex.** A vertex j is proper if every path i → j → k makes a right turn: going clockwise from i one meets j before k (Definitions 5.1, 5.2). A *proper mutation* is a mutation at a proper vertex, with j moved clockwise past its out-neighbours (Definition 6.1).
- **Unipotent companion.** For a linear ordering compatible with σ, U is upper triangular with 1 on the diagonal and −b_ij above it (Definition 4.2). Its *cosquare* is U⁻ᵀU (Definition 4.7).
- **Invariants of proper mutation.** Proper mutations and wiggles preserve:
  - the integral congruence class {G U Gᵀ : G ∈ GL_n(ℤ)} (Theorem 7.1);
  - the GL_n(ℤ) conjugacy class of the cosquare (Corollary 7.5);
  - the Alexander polynomial Δ(t) = det(tU − Uᵀ) and the Alexander lattices d_k, the ℤ-spans of the k × k minors of tU − Uᵀ (Corollaries 8.5, 8.8);
  - the Markov invariant M = n − tr(U⁻ᵀU). For n = 4, Δ(t) = (t − 1)⁴ + M·t(t − 1)² + det(B)·t² (formula (9.7)).
- **When these are invariants of the quiver.** A COQ is *totally proper* if every COQ in its proper mutation class is proper (Fomin–Neville Definition 14.1). A quiver has at most one totally proper ordering up to wiggles (Fomin–Neville Theorem 14.3). Only then are the invariants above invariants of the mutation class (Fomin–Neville Corollary 14.2, Fomin–Neville Remark 14.4).
- **Opposites (§12).** The opposite COQ reverses the arrows and the cyclic ordering. Its cosquare is conjugate in GL_n(ℤ) to the *transpose* of the cosquare of Q (Fomin–Neville Lemma 12.5), and an integer matrix need not be conjugate to its transpose (Fomin–Neville Remark 12.6). So if two COQs are related by proper mutations up to opposites, their cosquares are conjugate up to transpose (Fomin–Neville Corollary 12.8).
- **Example 12.10.** Five cyclic 3-vertex quivers with M = −50: weights (3, 7, 9) and its opposite, (5, 5, 5), and (4, 5, 7) and its opposite. Each is minimal in its class, so the five classes are distinct by Beineke–Brüstle–Hille. The cosquares of the first four are pairwise non-conjugate. For (4, 5, 7) and its opposite the conjugacy classes coincide. So the cosquare separates (3, 7, 9) from its opposite and does not separate (4, 5, 7) from its opposite.

### Which of them can tell Q from −Q [I]

**Only the congruence class of U and the conjugacy class of the cosquare.** The polynomial invariants cannot:

*Proof.* Take the linear ordering v₁ < … < v_n for Q and the reversed ordering for the opposite COQ. Then U_opp = w Uᵀ w, where w is the permutation matrix that reverses the order. Hence tU_opp − U_oppᵀ = w (tUᵀ − U) w = w (tU − Uᵀ)ᵀ w. A matrix and its transpose have the same k × k minors, and conjugating by w permutes them up to sign. So Q and its opposite have the same Alexander lattices d_k, the same Alexander polynomial, the same Markov invariant and the same det B. ∎

This agrees with Chelnokov's theorem that piecewise-polynomial invariants of 4-vertex quivers are functions of det B, which Fomin and Neville quote in Fomin–Neville Remark 14.26.

**A test [I].** Let C be the cosquare and f its characteristic polynomial, and suppose f is irreducible, with L = ℚ[x]/(f). The ℤ-span of the entries of an eigenvector of C for the eigenvalue x is a lattice in L. Replacing C by G C G⁻¹ with G ∈ GL₄(ℤ) replaces the eigenvector by its image under G and keeps the lattice (this is the Latimer–MacDuffee correspondence, recalled and not re-derived here). So if C and Cᵀ are conjugate, the lattices of C and Cᵀ differ by a factor in L, and the ideals they generate in the maximal order of L lie in one ideal class. `n4_opposite.transpose_test` compares these two ideal classes with PARI. Different classes prove that C is not conjugate to Cᵀ. Equal classes prove nothing unless ℤ[x] is the maximal order. PARI's `bnfinit` assumes GRH, so a verdict "different" is conditional on it.
> **Correction (note 19):** `transpose_test` calls `bnfinit` and `bnfisprincipal` but never `bnfcertify`. As computed, every verdict depends on GRH, not only "different", and so do the class numbers. All 332 verdicts "conjugate" (301 + 26 + 5 in the table below) have since been made unconditional: for each, an explicit G ∈ GL₄(ℤ) with CG = GCᵀ was checked in integers. Of 25 sampled verdicts "different", `bnfcertify` certified 20; the other 5 timed out. See [note 19](19-checks-of-notes-13-to-16.md).

### Do they apply on 4 vertices [P, I]

- **Proper orderings.** A 4-vertex quiver has a proper cyclic ordering exactly when it is not a *vortex*: a complete quiver with a source or sink whose other three vertices carry an oriented 3-cycle (Fomin–Neville Proposition 13.2) [P].
- **Totally proper orderings.** Two sufficient conditions are known [P]:
  - the class is mutation-acyclic (Neville, arXiv 2409.17832, quoted as Fomin–Neville Remark 15.10);
  - every quiver of the class is complete and vortex-free, and Q has a proper ordering (Fomin–Neville Theorem 15.7).

  One necessary condition: no quiver of the class is a vortex (Fomin–Neville Remark 14.7).
- **On the census [I]** (`n4_opposite_run.py summary`, `n4_opposite_summary.log`):

| | Classes |
|---|---|
| An acyclic quiver in a bottom component, so totally proper by Neville | 204,498 |
| Finite core (§3) whose quivers are complete and vortex-free and whose exits are all forks, so totally proper by Fomin–Neville Theorem 15.7 | 196,262 |
| Either | 334,168 |
| Both | 66,592 |
| Finite core containing a vortex, so no totally proper ordering | 132,611 |

  The second row uses §3: such a class consists of its core and of forks, and forks are complete and vortex-free.

- **The extremes are out of reach.** G_k has a zero entry, so Fomin–Neville Theorem 15.7 does not apply to it. It has one proper ordering, and a search through 3,000 COQs of its proper mutation class found none that is not proper (k = 3, 4, 5, 8, 12; `n4_opposite_extremes.log`). So it may be totally proper, but no cited result certifies it. The same holds for the census extremes at bottoms 2 to 9.

### The cosquare test on the census [I]

`n4_opposite_run.py fn` (`n4_opposite_fn.jsonl.gz`, `n4_opposite_fn.log`) ran the test on the classes of the table above, one class of each mirror pair and every self-mirror class: 174,149 classes. "Acyclic" means an acyclic quiver in a bottom component, with the ordering of Observation 11.6. "Complete core" means the second row of the table, without such an acyclic quiver, with the unique proper ordering of a core quiver (Proposition 13.5).

| Verdict | Acyclic, mirror pair | Acyclic, self-mirror | Complete core, mirror pair | Complete core, self-mirror |
|---|---|---|---|---|
| Classes tested | 96,780 | 10,938 | 63,239 | 3,192 |
| Different ideal classes: the cosquare is not conjugate to its transpose | 78,036 | 0 | 14,963 | 0 |
| Same ideal class, ℤ[x] not maximal: undecided | 17,240 | 9,812 | 47,073 | 3,057 |
| Same ideal class, ℤ[x] maximal: the cosquare is conjugate to its transpose | 0 | 26 | 301 | 5 |
| Alexander polynomial reducible: not tested | 1,480 | 1,096 | 889 | 130 |
| PARI error in `bnfinit` | 24 | 4 | 13 | 0 |

- **It is sound here.** No self-mirror class gets the verdict "different", in 14,130 cases. For a self-mirror class the cosquare must be conjugate to its transpose, by Fomin–Neville Lemma 12.5 and Fomin–Neville Theorem 14.3.
- **It separates 92,999 of the 160,019 pairs**: 78,036 acyclic pairs (81 %) and 14,963 pairs with a complete core (24 %). The verdicts assume GRH. Every one of these pairs is also certified by Caldero–Keller or by the core (§4), so the cosquare confirms them and adds none.
- **It provably fails on 301 pairs.** There ℤ[x] is the maximal order and the two ideal classes agree, so the cosquare of Q is conjugate to its transpose, which is the cosquare class of −Q. But Q and −Q have different cores, so they are not mutation-equivalent. These are 4-vertex analogues of (4, 5, 7) in Example 12.10. All 301 are mutation-cyclic. The smallest has rows (0, 5, 4, −3), (−5, 0, 2, 5), (−4, −2, 0, 5), (3, −5, −5, 0): all four of its mutations are forks, so its core is itself, it is not isomorphic to its opposite, and its Alexander polynomial has M = −91 and det B = 1, with class number 6.
- **No acyclic pair fails this way.** Among the 96,780 acyclic mirror pairs, none has a maximal ℤ[x] and equal ideal classes. Fomin and Neville's Remark 12.11 says they know no 3-vertex acyclic example either. The 17,240 undecided acyclic pairs could still contain one.
  > **Correction (note 19):** "Provably fails on 301 pairs" should be "on at least 301 pairs". Among the pairs left undecided, an explicit integer conjugator exists in 1,398 of 2,500 sampled complete pairs. "The smallest" quiver is only the first such quiver in census order (class 9630, level 5, weight 24). There are smaller ones, of weight 22 (class 18592) and with |M| = 63 (class 9641). Its stated properties are all correct. The undecided acyclic pairs do contain failures: in 639 of 2,500 sampled ones the cosquare is conjugate to its transpose. The first is Q = (3, 1, 0, 1, 1, −3), which is acyclic with proper order ⟨0, 1, 3, 2⟩ and M = 36. The conjugator G = [[−2, −3, 4, 3], [−3, −2, 3, 1], [4, 3, −4, −2], [3, 1, −2, 0]] has det G = 1 and CG = GCᵀ. The sink and source orbits of Q and −Q are disjoint, so Q ≁ −Q by Caldero–Keller. This is a 4-vertex acyclic answer to the question of Fomin–Neville's Remark 12.11, which they ask for 3 vertices. See [note 19](19-checks-of-notes-13-to-16.md) §6.1.
- **Most pairs are undecided** because ℤ[x] is rarely maximal: the test compares classes in the maximal order, which loses information. Integral conjugacy itself was not tested (§10).

---

## 3. Forks, pre-forks and the core

### Definitions [P]

All of these are Warkentin's (thesis, 2014). I took the statements from Ervin, arXiv 2306.07502, who restates them and proves the versions for the labelled mutation graph. Warkentin's thesis itself was not read.

- **Fork** (Ervin, Definition 2.5). An abundant quiver F (every pair of vertices joined by at least two arrows) that is not acyclic, with a vertex r, the *point of return*, such that:
  - for every path i → r → j there are arrows j → i, and more of them than arrows i → r and than arrows r → j;
  - the full subquivers on the in-neighbours and on the out-neighbours of r are acyclic.
- **Pre-fork** (Ervin, Definition 4.5). A quiver P with two vertices k ≠ k′ such that:
  - P ∖ {k} and P ∖ {k′} are forks with a common point of return r;
  - every other vertex i has arrows to both k and k′, or from both.

  There is no condition on the arrows between k and k′. With two or more of them, P is a fork.
- **Exit.** I call a pair (Y, m) an *exit* if Y is a fork with point of return m or a pre-fork with point of return m.

### The quoted lemmas [P]

- **(F1)** (Ervin, Lemma 2.7; Warkentin, Lemma 2.5). If F is a fork with point of return r and k ≠ r, then μ_k(F) is a fork with point of return k and has more arrows than F.
- **(F2)** (Ervin, Lemma 2.8; Warkentin, Lemma 2.8). If F is a fork with point of return r, the edge between F and μ_r(F) is a bridge of the labelled mutation graph. The side containing F is a tree, and all its quivers are forks.
- **(F3)** (Ervin, Lemma 4.6; Warkentin, Corollary 6.2). If P is a pre-fork with vertices {r, k, k′} and m ∉ {r, k, k′}, then μ_m(P) is a pre-fork with vertices {m, k, k′}, with more arrows and the same arrows between k and k′.
- **(F4)** (Ervin, Lemma 4.23 and Corollaries 4.24, 4.25). Let P be a pre-fork with vertices {r, k, k′} and fewer than two arrows between k and k′. Let P̃ be P if k and k′ are not joined, and P with k and k′ exchanged if they are joined by one arrow; then P̃ = μ_k μ_k′ μ_k μ_k′ μ_k(P). Removing the edges labelled μ_r at P and at P̃ cuts the labelled mutation graph in two. Every quiver on the side of P is a tip, a wing, a pre-fork or a fork (Ervin, Definitions 4.14, 4.18). It has at least as many arrows as P, and exactly as many only if it is P or P̃.
  > **Correction (note 19):** The formula for P̃ holds only when k and k′ are joined by one arrow. When they are not joined, μ_k μ_k′ μ_k μ_k′ μ_k(P) = μ_k(P), a wing, and P̃ = P is right because μ_k′ μ_k μ_k′ μ_k(P) = P. The quoted lemmas match their sources, which were read for note 19. (F1) is Warkentin's Lemma 2.5, (F2) his Lemma 2.8 and (F3) his Corollary 6.2. Ervin's Lemma 4.23 and Corollary 4.25 prove the region statement of (F4) for the labelled graph; Warkentin proved it for the exchange graph (Lemmas 6.7 and 13.20–13.22). Consequence (a) for forks is Warkentin's Lemma 2.3.e. Consequence (c) is stated in his proof of Lemma 2.5. "A pre-fork with two or more arrows between k and k′ is a fork" is his Lemma 6.1. See [note 19](19-checks-of-notes-13-to-16.md) §4 and §6.2.

**Far regions.** For an exit (Y, m), write Up(Y, m) for the side of Y in (F2) or (F4), and call it the *far region* rooted at Y. The edges removed are its *bridges*, and μ_m(Y) is its *foot*. In words: a far region is joined to the rest of the class only through its root, and its root is its lightest quiver.

Three consequences are used below [I]:

- **(a) The return vertex is unique.** If (Y, m) and (Y, m′) are exits, then m = m′.
  - *A fork.* A complete quiver with an oriented cycle has an oriented triangle T. Removing the point of return r leaves an acyclic quiver, so r ∈ T. Every path i → r → j has arrows j → i. So T is the triangle i → r → j → i for some i, j, and the fork condition makes its edge opposite r strictly its largest. This determines r.
  - *A pre-fork that is not a fork.* The pair {k, k′} is its only pair with fewer than two arrows, and r is the point of return of the two triangles P ∖ {k} and P ∖ {k′}.
  - *A pre-fork with two or more arrows between k and k′.* It is a fork with the same point of return r. Indeed k and k′ lie on the same side of r, so no path i → r → j has {i, j} = {k, k′}, and the other paths lie in P ∖ {k} or P ∖ {k′}. And P ∖ {r} is acyclic, because k and k′ lie on the same side of its third vertex.
- **(b) At most one light pair.** Every quiver of a far region has at most one pair of vertices joined by fewer than two arrows. This holds for forks, pre-forks, wings and tips by their definitions.
- **(c) Forks only grow, entry by entry.** In (F1), every entry of μ_k(F) that differs from the entry of F is strictly larger in absolute value. So in the far region of a fork, the level never drops along a path away from the root.

  *Proof.* A mutation at k changes b_ij only when i → k → j, and then b′_ij = b_ij + b_ik·b_kj. Removing r leaves an acyclic quiver, since each side of r is acyclic and all arrows between the two sides go from the out-side to the in-side.
  - If r ∉ {i, j}, the triangle i, k, j is acyclic, so i → j and the entry grows.
  - If r = i and j → r, then k is an out-neighbour and j an in-neighbour of r, so the fork condition gives b_kj > b_jr. The new entry is b_rk·b_kj − b_jr ≥ 2b_kj − b_jr > b_jr. If instead r → j, the entry grows.
  - The case r = j is symmetric. ∎

### Steps and closures

A step X → μ_m(X) is a *strict up-exit step* if (μ_m(X), m) is an exit and (X, m) is not. Every other step is *allowed*. Let V′(X) be the set of quivers, up to relabelling, reached from X by allowed steps. A set of quivers is *closed* if no allowed step leaves it.

**Theorem 14.1 [I, from F1–F4].** Let A and B be 4-vertex quivers.

1. A and B are mutation-equivalent up to relabelling if and only if V′(A) and V′(B) meet.
2. If V′(A) is finite, it contains exactly one minimal non-empty closed set. Call it the *core* K(A). If A ~ B and V′(B) is also finite, then K(A) = K(B). So among quivers with finite V′, the core is a complete invariant of the mutation class.
3. K(−A) = −K(A). So if V′(A) is finite, A ~ −A if and only if −K(A) = K(A), if and only if some X in K(A) has −X in K(A).
4. Suppose V′(A) is finite and some quiver of the class lies in no far region. Then K(A) is exactly the set N of quivers of the class that lie in no far region. If two quivers of K(A) are joined in the class through quivers of level ≤ L, they are joined through quivers of K(A) of level ≤ L.
5. If V′(A) is finite and K(A) contains no pair X, μ_m(X) that are both exits for the same vertex m (a *balanced edge*), then the hypothesis of item 4 holds.

*Proof.* Work in the labelled mutation graph, on which S₄ acts by relabelling. Exits, far regions and allowed steps are carried to themselves by S₄ and by X ↦ −X.

**Step 1: a far region is left where it was entered.** Let a path enter Up(Y, m) by a bridge, from X = μ_m(Y) to Y or from X̃ = μ_m(Ỹ) to Ỹ, and later leave it. It leaves by a bridge, so it returns to X or to X̃. The quiver X̃ is X with k and k′ exchanged. So the excursion can be cut out, after relabelling the rest of the path by the transposition (k k′) when the two ends differ. The new path is shorter, visits only relabellings of quivers of the old one, and ends at a relabelling of the old end.

**Step 2: shortest paths go down, then up.** Take a path from A to a relabelling of B that is shortest among all such paths. Its reverse is shortest from B to a relabelling of A.
- By Step 1, once the path makes an up-exit step into Up(Y, m) it stays there.
- Suppose a later step goes from Z to μ_m′(Z) with (Z, m′) an exit. Read backwards, this is an up-exit step into Up(Z, m′), so the reversed path stays in Up(Z, m′), and Y ∈ Up(Z, m′). Also Z ∈ Up(Y, m). By (F2) and (F4) each of Y, Z has at least as many arrows as the other, so Z ∈ {Y, Ỹ}, and by (a) m′ = m. Then the path returns to X or to X̃, and Step 1 gives a shorter path, a contradiction.

So after its first strict up-exit step, say out of X_i, the path makes no step of the form Z → μ_m′(Z) with (Z, m′) an exit. Reversed, the part of the path after X_i therefore has no strict up-exit step, and neither has the reverse of the step out of X_i, because (X_i, m) is not an exit. So X_i lies in V′(A) and in V′(B). If the path has no strict up-exit step, B itself lies in V′(A). This proves item 1; the converse is clear.

**Item 2.** V′(A) is finite and closed, so it contains a minimal non-empty closed set S. For a ∈ S the set V′(a) is closed, non-empty and inside S, so V′(a) = S. If S′ is another minimal closed set in V′(A) or in V′(B) with B ~ A, take a ∈ S and b ∈ S′. By item 1, S ∩ S′ = V′(a) ∩ V′(b) is non-empty, and it is closed, so S = S′.

**Item 3.** X ↦ −X carries allowed steps to allowed steps.

**Item 4.** A step from X ∈ N to Y ∉ N enters some far region that does not contain X, so it crosses a bridge upwards, (Y, m) is an exit, and (X, m) is not, because an exit lies in its own far region. So N is closed. A step between two quivers of N is allowed, because its target is not an exit. By Step 1, a path between two quivers of N can be cleared of all excursions out of N, and this removes quivers without adding any. So any two quivers of N are joined inside N, by allowed steps, without raising the level. By item 1, V′(A) contains a quiver z of N. Then V′(z) ⊂ N by closedness and V′(z) ⊃ N by connectedness, so N = V′(z) is finite, closed and strongly connected. Hence it is the minimal closed set.

**Item 5.** Suppose a quiver x of K(A) lies in Up(Y, m). Every quiver of a far region is joined to the root by a path inside the region whose steps towards the root are allowed: in the proof of (F4) the path from the root never mutates a fork or pre-fork at its point of return, so no reversed step is an up-exit step. So Y ∈ K(A), and then μ_m(Y) ∈ K(A), since the step down a bridge is allowed. K(A) is strongly connected under allowed steps, so some allowed path returns from μ_m(Y) to x. It must cross a bridge of Up(Y, m) upwards, and that step is allowed only if its source is also an exit for m. This is a balanced edge in K(A). ∎

**Remarks.**

- The proof does not use n = 4. The code does.
- The theorem says nothing when V′(A) is infinite. Whether a class has a finite core is itself an invariant of the class.
- **A core of one quiver.** If all four mutations of Q are exits, that is, μ_m(Q) is a fork or pre-fork with point of return m for each m, then K(Q) = {Q}. Such a Q is the only quiver of its class with this property, and Q ~ −Q exactly when Q is isomorphic to its opposite. 98,280 census classes are of this kind. In all of them the four mutations are forks, and in 2,552 the quiver is isomorphic to its opposite, so the other 95,728 are not mutation-equivalent to their opposites. Fomin and Neville's Corollary 15.12 treats these quivers and shows that they are totally proper.

### Checks of the quoted lemmas against the code [I]

`n4_opposite_run.py lemmas` (`n4_opposite_lemmas.log`) took 139,855 quivers on random walks from 3,000 census classes and kept 65,217 distinct exits (59,739 forks, 5,478 pre-forks that are not forks).

| Check | Cases | Failures |
|---|---|---|
| No quiver has two return vertices (consequence (a)) | 139,855 quivers | 0 |
| (F1) and (F3): the step away from the return vertex gives an exit for the mutated vertex, with more arrows | 184,695 steps | 0 |
| (F2), (F4): the far region, explored to radius 7 without crossing its bridges, does not contain its foot, and no quiver in it is lighter than the root | 1,200 regions, 2,910,784 labelled quivers | 0 |
| (F4): μ_k μ_k′ μ_k μ_k′ μ_k exchanges k and k′ when they are joined by one arrow | 400 regions | 0 |
| Consequence (b): no quiver of a far region has two light pairs | 1,200 regions | 0 |
| The level does not drop along a step away from the root | 1,200 regions | 0 |

The 1,200 regions are 400 rooted at forks, 400 at pre-forks with k and k′ not joined, and 400 at pre-forks with k and k′ joined by one arrow. The last row is proved for forks (consequence (c)). **For pre-fork regions it is a measurement only.** It is used in §5 and nowhere else.
> **Update (note 19):** Two further independent searches found no drop. One covered 7,764 regions to radius 5 and 6 (9,065,945 labelled quivers). The other covered 1,620 regions to radius 7 and 8 (9,620,126 labelled quivers), 1,300 of them hanging from census cores. Both checked the stronger property that every quiver is joined to its root through quivers of level at most its own. The property is still measured, not proved; a proof sketch is in [note 19](19-checks-of-notes-13-to-16.md) §6.3.

**The core does not depend on the starting quiver [I].** `n4_opposite_run.py walks` (`n4_opposite_walks.log`) took 3,000 census classes with a finite core and made three random mutation walks of up to 40 steps out of each bottom quiver, stopping before the entries pass 10³⁰⁰. The core computed from the end of the walk is the core of the class in all 9,000 cases. 8,997 of the walks end outside the core, the highest at level about 10²⁹⁹.

---

## 4. The census

### Cores

`n4_opposite_run.py cores` computed V′ and the core of every census class from its bottom quiver, giving up after 800 quivers or at the first quiver of level above 10⁶ (`n4_opposite_cores.jsonl.gz`, `n4_opposite_cores.log`).

| Bottom | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | All |
|---|---|---|---|---|---|---|---|---|---|---|
| Classes | 13 | 147 | 1,050 | 4,956 | 16,714 | 45,287 | 104,579 | 213,511 | 401,769 | 788,026 |
| Finite core | 8 | 23 | 216 | 1,571 | 7,173 | 25,671 | 65,148 | 151,778 | 304,240 | 555,828 |
| Search stopped at a cap | 5 | 124 | 834 | 3,385 | 9,541 | 19,616 | 39,431 | 61,733 | 97,529 | 232,198 |

- **The share with a finite core grows with the bottom**, from 16 % at bottom 2 to 76 % at bottom 9.
- **Cores are small.** The largest has 77 quivers. 98,795 cores are a single quiver (98,280 of them with all four mutations exits, the rest in small classes where a mutation returns the same quiver), 84,310 have two, 111,119 have four.
- **Cores reach above the census bounds.** The highest level in a core is 1,312. 14,076 cores reach above level 192 and 779 above 512.
- **No hidden join.** The 555,828 finite cores are pairwise different (`n4_opposite_mirror.log`). So no two of these census classes are the same mutation class.
- **Which cores lie in no far region.** 533,364 cores have no balanced edge or contain a quiver that passes a direct test, so item 4 of the theorem applies to them. The other 22,464 have a balanced edge; 18,856 of those are two forks with a common point of return.

**The classes without a finite core are separated from the others [I].** Suppose a class u whose search stopped were the same class as one with a finite core K. Every finite core has at most 77 quivers and level at most 1,312.
- If the bottom quiver of u passes the direct test for lying in no far region (by consequence (b): it has two light pairs, or is abundant and not a fork, or its one light pair fails the shape of a pre-fork, wing or tip), then V′ of it is K by item 4. But the search from it found 800 quivers or a quiver above level 10⁶. This covers 176,910 classes.
- If the search found such a quiver above level 1,312, it would lie in K. This covers 55,237 more.
- For the last 51, the closure of the lowest such quiver found is again larger or higher than every finite core (`n4_opposite_summary.log`).

So each of the 555,828 classes with a finite core is certified different from every other census class.

### Mirror pairs

`n4_opposite_run.py plateaus` and `mirror` (`n4_opposite_plateaus.jsonl.gz`, `n4_opposite_mirror.log`) recompute the bottom components of every class and their mirror images with this note's code. They reproduce note 12: 803,939 bottom components, 33,124 self-mirror classes, 377,451 mirror pairs.

A mirror pair is certified distinct in two ways.

- **By the core.** Both classes have finite cores, and the cores differ (Theorem 14.1). In every such pair the mirror image of one core is the core of the other class, as item 3 predicts.
- **By an acyclic quiver [P].** If a class contains an acyclic quiver, so does its mirror. Two acyclic quivers in one class are joined by sink and source mutations (Caldero–Keller, Corollary 4, as quoted in note 11). These keep every weight, so the two would lie in one bottom component. They do not.

| Bottom | Mirror pairs | By the core | By an acyclic quiver | By either | Open |
|---|---|---|---|---|---|
| 2 | 22 | 1 | 19 | 19 | 3 |
| 3 | 323 | 53 | 183 | 185 | 138 |
| 4 | 1,945 | 585 | 813 | 1,021 | 924 |
| 5 | 7,340 | 3,121 | 2,515 | 4,147 | 3,193 |
| 6 | 20,785 | 11,786 | 6,270 | 13,784 | 7,001 |
| 7 | 49,501 | 30,948 | 13,524 | 34,396 | 15,105 |
| 8 | 102,482 | 73,076 | 26,278 | 78,548 | 23,934 |
| 9 | 195,053 | 148,127 | 47,178 | 156,293 | 38,760 |
| All | 377,451 | 267,697 | 96,780 | 288,393 | 89,058 |

The open pairs are mutation-cyclic classes without a finite core, as far as the two tests see. For the 20,434 self-mirror classes with a finite core, the core equals its mirror image in every case, as it must.

---

## 5. Every pocket of a class with a finite core

**Pockets can sit outside the core.** In 570 of the 6,427 finite-core classes with several bottom components, the core alone does not reproduce the census (`n4_opposite_corecheck.log`). Example: the quiver with rows (0, 6, 6, −4), (−6, 0, 6, 5), (−6, −6, 0, 2), (4, −5, −2, 0) is a fork with point of return 3, of level 6 and weight 29. Its mutation at 3 has level 14 and weight 33, and is not a fork. So this fork is the root of a far region, and the only way out of the region climbs to level 14. It is a bottom component by itself, and it joins the other bottom component of its class only at 27. (F1) says that a fork gets heavier away from its point of return; it says nothing about the mutation *at* the point of return.

**The extended core.** Let K̂ be the core together with the roots of the far regions that hang from it, each joined to its foot.

**Proposition 14.3 [I].** Let Q have a finite core that lies in no far region (items 4, 5 of Theorem 14.1), and suppose every far region hanging from the core is rooted at a fork. Then the pockets of the class of Q, at every level, are the persistence pairs of the finite graph K̂ filtered by level. In particular the class has finitely many pockets, each dies at or below the highest level of the core, and f(Q, w) ≤ max(w, that level) for every w.

*Proof.* By (F2) the far region of a fork is a tree of forks, and by consequence (c) the level does not drop away from the root. So a quiver of level ≤ L in a far region is joined to the root through quivers of level ≤ L. Hence every component of the sublevel set at L meets K̂. Two quivers of K̂ joined at level ≤ L in the class are joined inside K̂ at level ≤ L: cut out the excursions beyond the roots as in Step 1. ∎

For far regions rooted at pre-forks the same argument needs the last row of the table in §3, which is measured and not proved.

> **Correction (note 19):** The hypothesis that the core lies in no far region is not needed. Two facts are enough, both from Step 1 of the proof of Theorem 14.1. First, every quiver outside K lies in a far region hanging from K: a shortest path from K to it leaves K by a strict up-exit step and never comes back out. Second, a path between quivers of K̂ can be cleared of its excursions. So Proposition 14.3 holds for every class with a finite core whose hanging far regions are all rooted at forks. That is 258,363 classes (`n4_opposite_pockets.log`), not 239,507. See [note 19](19-checks-of-notes-13-to-16.md) §6.3.

**The census** (`n4_opposite_run.py pockets`, `n4_opposite_pockets.jsonl.gz`, `n4_opposite_pockets.log`). The persistence pairs of K̂ were computed for all 555,828 classes with a finite core.

- **Agreement with the census.** In all 555,828 classes, the deaths of the bottom components computed from K̂ are exactly the census deaths. The census found them by enumeration inside a bound; here no bound is used.
- **All pockets.** There are 70,376 pockets, born at levels 3 to 58, hanging from 5,812,660 roots.

| Birth | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13–20 | 21–58 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pockets | 4 | 36 | 141 | 727 | 1,451 | 3,672 | 5,683 | 5,784 | 5,859 | 5,501 | 27,950 | 13,568 |
| Largest death/birth² | 0.667 | 1.062 | 0.800 | 1.417 | 1.163 | 1.578 | 1.494 | 1.020 | 0.950 | 0.764 | 0.598 | 0.252 |

- **No pocket dies above 2·birth².** The largest ratio is 101/64 = 1.578, at the bottom-8 extreme of note 10. For births of 10 or more it is 1.020, and it falls as the birth grows. The largest death of any pocket is 121.
- **What is proved.** Proposition 14.3 applies to 239,507 classes. In those, every pocket has death ≤ 0.703·birth², so f(Q, w) ≤ max(w, 0.703·w²) for every w. For the other 316,321 classes with a finite core, f(Q, w) ≤ 2w² for every w holds if the level does not drop away from the root in pre-fork regions.
  > **Correction (note 19):** With the hypothesis on the core dropped, the counts are as follows. Proposition 14.3 applies to 258,363 classes: the 239,507, and 18,856 whose core is two forks with a common point of return. The bound 0.703·birth² still holds there. The other 297,465 rest on the pre-fork property: 293,857 with a certified core and 3,608 with a balanced core of another kind.

These classes do not include the worst cases. The extremes of note 10 at bottoms 4, 5, 6, 7 and 9 have no finite core (§8).

---

## 6. The class of G_k

**Theorem 14.2 [I, from F1–F4].** Let k ≥ 3, and let G_k be the quiver of Theorem 9.1.

1. The core of the class of G_k has seven quivers:
   - G_k, −G_k and the oriented 4-cycle C_k with weights k, k, k, k − 1, at level k;
   - μ₁(G_k) and its mirror image, at level k² − k;
   - μ₂(G_k) and its mirror image, at level k².

   The core is the path G_k — μ₁(G_k) — C_k — −μ₁(G_k) — −G_k together with the path G_k — μ₂(G_k) — C_k — −μ₂(G_k) — −G_k. The map X ↦ −X reflects it and fixes C_k.
2. Twelve far regions hang from the core: four rooted at forks, of levels k² and k² − k, and eight rooted at pre-forks whose levels are cubic in k. Every quiver of a far region has level at least k² − k.
3. So k is the least level in the class; the class has exactly three quivers of level below k² − k; and f(G_k, w) = k(k − 1) for every k ≤ w < k(k − 1).
4. A quiver Q is mutation-equivalent to G_k if and only if V′(Q) contains one of the seven.

*Proof.* `n4_opposite_gk.py` runs the functions of `n4_opposite.py` on quivers whose entries are polynomials in k. A comparison is accepted only if it holds for every integer k ≥ 3: p > 0 is accepted when p(j + 3) has non-negative coefficients and a positive constant term. Any comparison that cannot be decided this way stops the run. None did (`n4_opposite_gk.log`). The run finds the seven quivers, the sixteen steps between them and the twelve strict up-exit steps, and it checks that each of the seven reaches every other. So the seven form a closed, strongly connected set, which is the core. No two of the seven are exits for one vertex, so by item 5 the core lies in no far region.

For item 2: in a fork region the level does not drop below that of the root (consequence (c)), and the fork roots have level ≥ k² − k. In a pre-fork region every quiver has at least as many arrows as the root (F4), so its level is at least a sixth of the root's weight. The run checks that each pre-fork root has weight above 6(k² − k) − 6. Items 3 and 4 follow from Theorem 14.1 and from G_k, −G_k being joined to C_k at exactly k² − k inside the core. ∎

> **Correction (note 19):** The script does not check three facts that this proof states. It does not check that no quiver of the core is an exit, which is needed for "no two of the seven are exits for one vertex". The printed levels are not certified as maxima: they are chosen by evaluating at k = 10⁶. And it does not check that the seven quivers are pairwise non-isomorphic for every k. All three were certified for every k ≥ 3 with the same sign test (`review19_n14a_gksym.log`); an independent run for k = 3 to 40 gives the same core and far regions. The theorem stands. See [note 19](19-checks-of-notes-13-to-16.md).

**Numerical confirmation.** For k = 3 to 200 the plain integer code gives the same core, the same twelve roots and exactly two pockets, both (k, k² − k) (`n4_opposite_extremes.log`).

**What this adds to Theorem 9.1.** Note 9 and note 12 §4 show that G_k and −G_k are joined only at k(k − 1). They do not describe the rest of the class: note 9's symbolic search stops at k² + 4k, and note 12 §9 lists "whether k is the bottom of the class of G_k" as unchecked. Both are now settled, for every k ≥ 3 and with no bound on the entries.

---

## 7. Self-mirror classes and mirror joins

### How the reversal is realised [I]

From `n4_opposite_mirror.log`, for the 33,124 self-mirror census classes:

| Bottom components | Classes |
|---|---|
| Every bottom component is its own mirror image | 28,088 |
| Some are their own mirror image, others are exchanged in pairs | 218 |
| All are exchanged in pairs | 4,818 |

- **At the bottom.** In the first two rows, 28,306 classes, some bottom component is carried to itself. In 12,350 of them that component contains a quiver isomorphic to its own opposite. In the other 15,956 it does not: Q and −Q are different quivers joined by mutations that never leave the bottom level.
- **Above the bottom.** In the last row the reversal exchanges bottom components, so Q reaches −Q only at the death of a mirror pair. These 4,818 classes and the 218 of the second row are the 5,036 classes with a mirror pair among their bottom components that note 12 counted.

**Inside the core** (`n4_opposite_corecheck.log`). 20,434 self-mirror classes have a finite core K. The map ι: X ↦ −X is then an automorphism of the graph on K that preserves levels.

| Action of ι on the core | Classes |
|---|---|
| Fixes a quiver: the core contains a quiver isomorphic to its opposite | 11,167 |
| Fixes no quiver, but exchanges the two ends of an edge: some X has μ_m(X) ≅ −X | 8,235 |
| Neither | 1,032 |

- **Odd cores.** An involution of a set with an odd number of elements has a fixed point. So a self-mirror class whose core has an odd number of quivers contains a quiver isomorphic to its opposite. This holds in all 5,333 such classes. G_k is an example: the core has seven quivers and ι fixes C_k.
- **The mirror path is symmetric.** If a path joins X to −X, its mirror image joins −X to X. In G_k's class the path is G_k, μ₁(G_k), C_k, −μ₁(G_k), −G_k: it is carried to itself, the fixed quiver C_k sits at the bottom, and the barrier is the mirror pair ±μ₁(G_k) on either side of it.
- **Mirror joins above the bottom.** In 1,920 of the 20,434 classes the bottom quiver of the core is joined to its mirror image only above the bottom. The largest such join is 101 at bottom 8 (1.578·b²), then 121 at bottom 9 (1.494·b²) and 51 at bottom 6 (1.417·b²).

### Is the barrier always attained at a mirror join? [I]

No. For each class with several bottom components, take the component that dies last, and ask whether its mirror image is another bottom component of the same class.

| Bottom | Classes with several bottom components | Last death at a mirror pair | Largest death/b² at a mirror pair | Largest elsewhere |
|---|---|---|---|---|
| 2 | 2 | 2 | 1.000 | — |
| 3 | 51 | 32 | 1.333 | 0.778 |
| 4 | 281 | 173 | 1.750 | 1.000 |
| 5 | 725 | 307 | 1.800 | 1.280 |
| 6 | 1,540 | 660 | 1.833 | 1.417 |
| 7 | 2,512 | 829 | 1.612 | 1.245 |
| 8 | 4,269 | 1,433 | 1.578 | 1.547 |
| 9 | 5,870 | 1,537 | 1.778 | 1.395 |

- **Most barriers are not mirror joins.** In 10,277 of the 15,250 classes the last death is not at a mirror pair. Most of these classes are not self-mirror at all: their bottom components are two different quivers unrelated by the reversal.
- **The extremes are.** At every bottom the largest death is at a mirror pair, and so are at least seven of the ten largest. The gap is narrow at bottom 8: 101 at a mirror pair against 99 elsewhere.

So "the worst barrier is a mirror join" holds at every bottom, and "every barrier is a mirror join" is false.

---

## 8. The classes without a finite core

### What stops the search

**What stops the search [I].** In every class looked at, the quivers reached without an up-exit step form a finite part and a few infinite *tubes*. In a tube one vertex has growing entries and the other three vertices carry a triangle T that takes finitely many shapes. `n4_opposite_run.py tubeshapes` (`n4_opposite_tubeshapes.log`) searched 600 of these classes to 1,200 quivers and recorded, for the quivers high up, the lightest of their four triangles:

| Weights of the lightest triangle along the tube | Classes of 600 |
|---|---|
| (1, 1, a), (1, 1, a + 1) and (1, a, a + 1) | 262 |
| (0, 1, a) and (1, a, a), a ≥ 2 | 248 |
| No light pair; every quiver has a cyclic triangle (2, m, m) | 61 |
| (0, 0, a), a ≥ 2: one arrow of weight a and a vertex joined only to the growing vertex | 18 |
| Other | 9 |
| Several of these | 2 |

- **Why they are not far regions.** A quiver of a far region has at most one light pair (consequence (b)). The shapes with a light pair have two of them at least part of the time. The third shape is abundant, but the triangle (2, m, m) has two equal largest weights, so it is not a fork, and every full subquiver of a fork is a fork or is acyclic (Ervin, Lemma 2.6).
- **The third shape is note 11's corridor.** Mutating alternately at the two ends of the weight-2 arrow keeps T = (2, m, m) and adds a constant to the growing entries. Note 11 §5 found that the worst joins of the census run along such corridors.
- **The extremes are here.** The bottom components with the largest death at bottoms 2 to 7 and at 9 lie in classes without a finite core. Only the bottom-8 extreme has one, of 46 quivers up to level 252 (`n4_opposite_extremes.log`).
- **44,220 of these classes contain an acyclic quiver**, so their mirror pairs are certified by Caldero–Keller, and the bound of arXiv 2610.36179 applies to them.

### Tube certificates [I]

For such a class V′(x) is infinite, but it can still be described exactly.

- **Families.** A *family* is a triple of labelled quivers Y(0), Y(1), Y(2) with an integer τ ≥ 2. Each of the six entries is continued by e(n + 3) = (τ + 1)·e(n + 2) − (τ + 1)·e(n + 1) + e(n), and the family is the set of the quivers Y(n), n ≥ 0. This is a definition. Nothing is assumed about where the triple comes from.
  > **Update (note 22):** The recurrence is explained there. Along a tube the triangle opposite the growing vertex is constant, the column moves by the monodromy M of a periodic walk, and the Pfaffian functional is a left eigenvector of M, so M² has eigenvalues 1, λ, 1/λ and τ = λ + 1/λ. In all 6,130,593 families of the certificates, τ = λʲ + λ⁻ʲ with λ + 1/λ = C − 2, where C is the Markov constant of the triangle and j ∈ {1/2, 1, 3/2, 2, 5/2, 4}, mostly 2 (Lemma 22.3 and [note 22](22-tube-lemma-and-its-limits.md) §3).
- **Signs for all n.** The differences Δ(n) = e(n + 1) − e(n) satisfy Δ(n + 2) = τ·Δ(n + 1) − Δ(n). If Δ(1) ≥ Δ(0) ≥ 0, then Δ(n + 1) ≥ Δ(n) ≥ 0 for all n, by induction: Δ(n + 2) − Δ(n + 1) = (τ − 2)·Δ(n + 1) + Δ(n + 1) − Δ(n). So an entry with e(0) > 0, Δ(0) ≥ 0 and Δ(1) ≥ Δ(0) is positive and non-decreasing for every n. Sums and integer multiples of entries satisfy the same recurrence, so a comparison between two entries, for all n at once, is decided by three integers or declared undetermined.
- **Mutating a family.** A mutation at m multiplies pairs of entries at m. If one factor of every product is constant in n and all signs are certified, the mutation acts on the varying entries by one integer linear map for all n. Then the mutated quivers form the family of the triple μ_m Y(0), μ_m Y(1), μ_m Y(2).
- **Closure.** For each family and each vertex m, one of three things is certified for all n.
  - *An exit.* The step to μ_m(Y(n)) is a strict up-exit step. The fork and pre-fork conditions are comparisons between entries, so `exit_returns` of `n4_opposite.py` runs unchanged on sequences.
  - *Another family.* μ_m(Y(n)) = Z(n + δ) for a family Z of the certificate, up to relabelling, with −3 ≤ δ ≤ 3. For δ < 0 the first members are checked as quivers.
  - *The growing vertex.* Two growing entries x, y at m are multiplied. Then every entry not at m is constant, the new entries are t + xy with t constant, and x, y ≥ 2 do not decrease. The conditions for a fork or pre-fork with return vertex m hold at n = 0 by direct test. They compare t + xy with x, y and constants and are monotone in x and y, so they hold for all n.
    > **Correction (note 19):** The justification is not the one the engine uses, and "x, y ≥ 2" is never checked. The engine requires every entry not at m to be constant. It requires every entry at m to be constant, or of certified sign with non-decreasing absolute value. It certifies that (Y(n), m) is not an exit for any n, and checks that (μ_m Y(n), m) is an exit for n = 0, 1, 2. This is enough for all n. Each changed entry lies opposite m in a triangle i, m, j that carries a path j → m → i, and equals c + |b_im|·|b_mj| with c constant. Every exit condition that involves it asks it to point i → j and to exceed both factors, and the margin c + |b_im|(|b_mj| − 1) does not decrease in n. All other conditions involve constant entries and the fixed signs at m. All 362,763 such steps in 322 rechecked certificates are strict up-exits. See [note 19](19-checks-of-notes-13-to-16.md) §6.4.
- **Conclusion.** Let E be the set of quivers reached from x by allowed steps through levels ≤ L, outside the families. If every allowed step out of E lands in E or in a family, then E together with the families is closed under allowed steps, so it contains V′(x). If x lies in no far region, V′(x) is the core (Theorem 14.1, item 4). Every Y(n) with n ≥ 3 lies above the lowest level of E, so the *bottom of the core*, its quivers of least level, is a finite known set. It is an invariant of the class, and the class equals its mirror exactly when this set is its own mirror image.
  > **Correction (note 19):** "V′(x) is the core (Theorem 14.1, item 4)" uses item 4 outside its hypothesis, which asks for V′ finite. Without finiteness, the proof of item 4 still gives V′(x) = N, the set of quivers of the class that lie in no far region, and N is the same for every quiver of the class. Its least level, and the quivers there, are therefore an invariant, and that is all the certificate uses. "Lies above the lowest level of E" should read "of E and of Y(0), Y(1), Y(2)", which is what the code compares.

A wrong triple or a wrong τ cannot make a certificate pass: the closure check would fail.

### The run [I]

`n4_opposite_tubes.py run` (`n4_opposite_tubes.jsonl.gz`, `n4_opposite_tubes.log`) looks for the tubes of each class by following the growing direction, proposes triples, and checks the closure. Caps: 1,000 quivers in E, 240 families, 6 seconds per class.

| Bottom | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | All |
|---|---|---|---|---|---|---|---|---|---|---|
| Classes without a finite core | 5 | 124 | 834 | 3,385 | 9,541 | 19,616 | 39,431 | 61,733 | 97,529 | 232,198 |
| Certified | 0 | 76 | 669 | 3,059 | 8,987 | 18,774 | 38,243 | 59,964 | 95,436 | 225,208 |
| Not certified | 5 | 48 | 165 | 326 | 554 | 842 | 1,188 | 1,769 | 2,093 | 6,990 |

- **Why 6,990 fail.** E passes its cap in 3,195; no periodic tube is found within the level bound in 2,645; there are more than 240 families in 883; a comparison is undetermined in 251; the time runs out in 16. A failure means "not certified", not "irregular".
  > **Correction (note 22):** Some failures are irregular after all. The class 707 has no certificate of this form with any caps, because its V′ has at least L·ln L − 3L quivers below level L (Theorem 22.7 of [note 22](22-tube-lemma-and-its-limits.md)). In the connected cyclic classes with linear growth, the "E cap" failures come from spikes, as far as the examples looked at show. A spike is a step at the growing vertex of a τ = 2 corridor that is allowed because a column entry is 0 or ±1 (Lemma 22.1′). Polynomial families close 2,155 of the 2,282 such classes.
- **Growth.** τ = 2, linear growth, occurs in 30,255 certified classes. These are the corridors of note 11.
- **The extremes.** The classes with the largest death at bottoms 3, 4, 5, 6, 7 and 9 are certified. The bottom-2 extreme is not (E cap). The bottom-8 extreme has a finite core.

**Checks by the engine** (`validate`, `crosscheck`; appended to the same log).

| Check | Cases | Failures |
|---|---|---|
| A certified comparison of two sequences against 50 explicit terms | 80,590 comparisons | 0 |
| Every quiver of `no_exit_closure(x, cap=4000, level_cap=10**12)` lies in E or in a family | 300 classes, 119,190 quivers | 0 |
| Allowed steps out of Y(n), n = 3 to 10, land in E or in a family | 177,000 steps | 0 |
| A certificate with a wrong τ, or with one entry of Y(2) changed, is rejected | 200 | 0 |

> **Correction (note 19):** The last row carries no information. The procedure closes the changed family alone, with no other families, and it rejects the unchanged family as well (120 of 120 cases, `review19_n14b_probe.log`). The row on `no_exit_closure` is weak: that search stops at the first quiver above 10¹², after a median of 156 quivers, and 27 of 60 classes reached the cap of 4,000. An independent attack on 322 certificates replaces both rows. It used separate code, covered the extremes at bottoms 3 to 7 and 9, and included 990,882 quivers of V′. Every quiver lay inside its certificate, and the bottom of the core agreed in 322 of 322. As a control, 117 of 120 deliberately broken certificates were flagged; the other 3 had a redundant family. The counts of §4 and of the table below were also recomputed independently, for all 788,026 classes. See [note 19](19-checks-of-notes-13-to-16.md).

**Checks against the census** (`n4_opposite_run.py combined`, `n4_opposite_combined.log`), with this note's code and the bottom components of §4:

- In 221,001 certified classes the bottom of the core is at the census bottom. Its least quiver lies in a bottom component of the same census class, and the least quiver of its mirror image lies in the mirror class, in every case.
- In the other 4,207 the bottom of the core is above the census bottom. In all of them the census bottom quiver fails the direct test for lying in no far region: the bottom component hangs in a far region, as in the example of §5.
- "The bottom of the core equals its mirror image" agrees with the census mirror map in all 225,208 classes: 11,370 self-mirror, 213,838 not.
- No two certified classes have the same bottom of the core.

### Finite cores and tube certificates together [I]

| Bottom | Classes | Finite core | Tube certificate | Neither | Mirror pairs | Certified by cores | With Caldero–Keller | Open |
|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 8 | 0 | 5 | 0 | 0 | 0 | 0 |
| 2 | 147 | 23 | 76 | 48 | 22 | 19 | 22 | 0 |
| 3 | 1,050 | 216 | 669 | 165 | 323 | 282 | 295 | 28 |
| 4 | 4,956 | 1,571 | 3,059 | 326 | 1,945 | 1,840 | 1,870 | 75 |
| 5 | 16,714 | 7,173 | 8,987 | 554 | 7,340 | 7,135 | 7,189 | 151 |
| 6 | 45,287 | 25,671 | 18,774 | 842 | 20,785 | 20,456 | 20,541 | 244 |
| 7 | 104,579 | 65,148 | 38,243 | 1,188 | 49,501 | 49,013 | 49,136 | 365 |
| 8 | 213,511 | 151,778 | 59,964 | 1,769 | 102,482 | 101,727 | 101,895 | 587 |
| 9 | 401,769 | 304,240 | 95,436 | 2,093 | 195,053 | 194,144 | 194,364 | 689 |
| All | 788,026 | 555,828 | 225,208 | 6,990 | 377,451 | 374,616 | 375,312 | 2,139 |

- **Pairwise different.** The 781,036 classes of the third and fourth columns are pairwise certified different: two finite cores differ (§4), two bottoms of cores differ, and a class without a finite core is never a class with one (§4).
- **Mirror pairs.** 374,616 pairs have both classes in these columns, and in each the two cores, or the two bottoms of cores, are mirror images of each other and different.
- **Self-mirror classes.** For 31,804 of the 33,124 the core is known, and it equals its mirror image.

### Status of this section

The certificate argument is the one above. The engine that produces and checks the certificates, `n4_opposite_tubes.py`, was written from that argument, separately from the rest of this note. I checked its output against the census as listed. I did not read its code line by line. So every count that depends on it is given separately from the counts of §4, which do not.

**What is still missing [H].** A lemma of Warkentin's type for tubes, proved once, would replace the certificates and cover the 6,990 classes that the caps leave out.
> **Correction (note 22):** The lemma is proved in [note 22](22-tube-lemma-and-its-limits.md) §4 for tubes that are given (Lemmas 22.1–22.3, Theorem 22.5). It cannot cover all 6,990 classes. For class 707, with a Markov triangle, it is proved that V′ is not a finite set plus finitely many tubes. Side tubes, with unbounded τ, are measured in class 108970 (§5 there).

---

## 9. What this does to the open problems

- **Note 10's visibility caveat.** Closed for 555,828 classes (70.5 %) by finite cores. With the tube certificates, a hidden join must involve one of 6,990 classes (0.9 %). Note 11's statement that a hidden pocket born at b ≤ 9 would die above 8·b² still stands for those.
- **Conjecture 10.1.** Unchanged as a conjecture. For the classes with a finite core it holds at every level, with constant 1.578 in place of 2; this is proved for 239,507 classes and measured for the rest. Every class that attains the census maxima, except at bottom 8, is outside this set. For the tube classes the certificates show that the census did not split one class in two, but the pockets above the census bound are not listed.
  > **Correction (note 19):** "Proved for 239,507 classes" should read 258,363 (see the note in §5).
- **Decidability at n = 4.** Mutation equivalence up to relabelling is decided, by Theorem 14.1, whenever one of the two quivers has a finite V′ and the search from the other stops. The classes covered are mostly mutation-cyclic. An acyclic quiver is never a fork, pre-fork, wing or tip, since each of those has a fork as a full subquiver, so it lies in no far region and hence in the core. 160,278 of the 555,828 finite cores contain an acyclic quiver, and the other 395,550 classes are therefore mutation-cyclic. This is the side that arXiv 2610.36179 leaves open. It is not a decision procedure: nothing bounds the search when V′ is infinite.
  > **Update (note 22):** With the acyclic case (arXiv 2610.36179) and rank 3 for disconnected quivers, equivalence on 4 vertices is decided whenever one quiver is mutation-acyclic or disconnected, or both classes have a finite core or a tube certificate. No bound on f(Q, w) is used. It is still not a decision procedure: class 707 has no certificate of this form. See [note 22](22-tube-lemma-and-its-limits.md) §7.
- **Problem 11.2.** Not addressed.

---

## 10. Not done

- **Tubes** (§8). No general lemma. The certificates cover 225,208 of 232,198 classes, and their code was not read line by line.
  > **Update (note 22):** Lemma and its limits in [note 22](22-tube-lemma-and-its-limits.md) §§4–5; second-pass certificates and the open classes in §6 there.
- **Pockets of the tube classes.** Not listed. The certificates give the core, not its persistence.
- **Monotone levels in pre-fork regions.** Measured in 800 regions, not proved. Proposition 14.3 is stated only where it is not needed.
  > **Update (note 19):** Measured since in 9,384 further regions, by two independent searches, with no drop. A proof sketch is in [note 19](19-checks-of-notes-13-to-16.md) §6.3: outward steps never lower the level, and the region is the closure of P and P̃ under outward steps. The hypothesis of Proposition 14.3 on the core has been dropped.
- **Warkentin's thesis.** Not read. (F1)–(F4) are quoted from Ervin's paper, which proves (F4) for the labelled graph and cites the thesis for the rest. The checks of §3 test the code against the statements; they do not replace the proofs.
  > **Update (note 19):** Read for [note 19](19-checks-of-notes-13-to-16.md) (https://d-nb.info/1214302807/34). (F1) to (F3) match it, and so does the definition of a fork. For (F4), see the correction in §3.
- **A sharper cosquare test.** The test of §2 compares ideal classes in the maximal order. When ℤ[x] is not maximal, equal classes leave the question open. Integral conjugacy itself (Eick–Hofmann–O'Brien, in Magma) was not run.
- **Total properness of G_k.** Not decided.
- **Not a specialist's reading.** This note had no separate check when it was written.

---

## 11. Reproduce

```bash
PY=python
$PY -I n4_opposite_run.py cores --cap 800 --level-cap 1000000 --procs 9 > n4_opposite_cores.log      # about 9 minutes
$PY -I n4_opposite_run.py plateaus --procs 9 > n4_opposite_plateaus.log
$PY -I n4_opposite_run.py mirror > n4_opposite_mirror.log
$PY -I n4_opposite_run.py summary > n4_opposite_summary.log
$PY -I n4_opposite_run.py corecheck > n4_opposite_corecheck.log
$PY -I n4_opposite_run.py pockets --procs 4 > n4_opposite_pockets.log
$PY -I n4_opposite_run.py fn --procs 3 > n4_opposite_fn.log                                          # PARI, see below
$PY -I n4_opposite_run.py extremes > n4_opposite_extremes.log
$PY -I n4_opposite_run.py lemmas --classes 3000 --balls 400 --radius 7 > n4_opposite_lemmas.log
$PY -I n4_opposite_run.py walks > n4_opposite_walks.log
$PY -I n4_opposite_run.py tubeshapes > n4_opposite_tubeshapes.log
$PY -I n4_opposite_gk.py 3 > n4_opposite_gk.log
$PY -I n4_opposite_tubes.py run --procs 8 > n4_opposite_tubes.log                                        # about an hour
$PY -I n4_opposite_tubes.py crosscheck >> n4_opposite_tubes.log
$PY -I n4_opposite_tubes.py validate --classes 300 --broken 100 >> n4_opposite_tubes.log
$PY -I n4_opposite_run.py combined > n4_opposite_combined.log
```

- `cores`, `plateaus`, `pockets`, `fn` and `n4_opposite_tubes.py run` overwrite their `.jsonl.gz` output. `combined` needs the output of `n4_opposite_tubes.py run`. `mirror`, `summary`, `corecheck`, `extremes`, `lemmas`, `walks`, `tubeshapes` and `n4_opposite_gk.py` write only to standard output.
- `pockets` and `fn` take `--resume FILE` to reuse the complete records of an interrupted run.
- `fn` needs cypari2. Each worker may use up to 4 GB of PARI stack; three workers were used. `pockets`, `fn` and `summary` start their workers before loading the census, which keeps each worker small.
- All of them read the class files of notes 8 and 10 (two are gzip-compressed).

---

## Sources

- Fomin, Neville, *Cyclically ordered quivers*: https://arxiv.org/abs/2406.03604
- Ervin, *New hereditary and mutation-invariant properties arising from forks*: https://arxiv.org/abs/2306.07502
- Warkentin, *Exchange graphs via quiver mutation*, thesis, Chemnitz 2014 (not read; quoted through Ervin and through Fomin–Neville)
- Neville, *Mutation-acyclic quivers are totally proper*: https://arxiv.org/abs/2409.17832 (title and Fomin–Neville's Remark 15.10 only)
- Chelnokov, *On the invariants of 4 × 4 skew-symmetric matrix under cluster mutations*: https://arxiv.org/abs/2311.01784 (abstract and Theorem 1)
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*: https://arxiv.org/abs/2610.36179
- Notes 8, 9, 10, 11 and 12 of this repository.
