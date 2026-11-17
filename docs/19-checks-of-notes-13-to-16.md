# 19. Checks of notes 13, 14, 15 and 16

*Prepared 2026-11-12. Notes [13](13-conjecture-5-5-up-to-height-18.md), [14](14-opposite-quivers-forks-and-cores.md), [15](15-rank-2-orbits-and-the-constant-2.md) and [16](16-five-vertices-above-w-squared.md) were written on 2026-11-11, and several of their proofs are computer-assisted. Before this check, notes 13 and 14 and Theorem 15.13 had not been checked. Note 16 was checked in parallel in [note 17](17-checks-of-note-16.md); the checks of note 16 made here were finished before the results of note 17 were seen. This note records a separate check of the four notes, in the way [note 12](12-checks-of-notes-03-to-10.md) checked notes 3 to 10.*

*Code: [verify/review19.py](../verify/review19.py) for notes 15 and 16, and `verify/review19_n13_*.py`, `review19_n14a_*.py` and `review19_n14b_*.py` for notes 13 and 14. All are new and none imports the scripts being checked; three of the note-14 scripts call them on purpose to obtain or probe their output, and say so in their headers. Results: the `review19_*.log` files.*

*Versions checked:*

| Note | Version |
|---|---|
| 13 | 2026-11-11 14:59 |
| 14 | 2026-11-11 16:23:44, unchanged from the start to the end of the check, so nothing was added to it after that time |
| 15 | 2026-11-12 11:12 |
| 16 | 2026-11-12 11:38, with the notes of notes 17 and 18 |

*Quivers are up to relabelling unless stated otherwise. Labels: **[P]** proven in a cited source; **[I]** derived or measured in this check; **[H]** heuristic.*

---

## 1. Outcome

**No theorem was found false.** These survived re-derivation and independent computation:

- note 16: Lemmas 16.1 to 16.3, Theorems 16.4 to 16.6 and Corollary 16.7;
- note 15: Theorem 15.1, Corollary 15.2, Proposition 15.3, Lemmas 15.4 and 15.5, Theorems 15.6 and 15.13, Corollaries 15.7 and 15.14, Proposition 15.8;
- note 14: Theorems 14.1 and 14.2 and Proposition 14.3;
- note 13: its main result, Conjecture 5.5 of arXiv 2610.36179 on all 106,918,566 quivers of height ≤ 18, and Proposition 13.1.

**Results that came out stronger:**

1. **Lemma 15.5 now rests on a source that has been read.** Warkentin's thesis was fetched and read for this check.
   - Its Definition 2.1 is the definition of a fork used in notes 14, 15 and 16 and in all three certificate scripts.
   - Note 15 adds "no entry is smaller" to Lemma 2.5. That statement is in Warkentin's own proof.
   - Lemma 2.3.e makes the point of return unique (§4).
2. **Theorem 15.13 has had its second reading.** The certificate `prove2` covers every cell of its exit table. A search without forks finds the join of R_b and −R_b at exactly 2b² − 3b − 3 for every b from 5 to 48, odd b included.
3. **Proposition 14.3 holds without its hypothesis on the core.** It applies to all 258,363 finite-core classes whose far regions are rooted at forks, not only to note 14's 239,507. The bound 0.703·birth² is unchanged (§6.3).
4. **The cosquare test's verdicts "conjugate" no longer depend on GRH.** All 332 were rebuilt with explicit conjugators in GL₄(ℤ).
5. **All of note 13's per-class verdicts were recomputed.** Independent code repeated all 418,042 per-class searches with the same verdicts. It also reproduced the pass and fail counts exactly for every height ≤ 10.
6. **Theorem 14.2 is now complete as a proof.** Its script leaves three facts of the proof unchecked. They were certified here for every k ≥ 3.
7. **All 788,026 cores of the census were recomputed independently.** They match the stored ones. 322 tube certificates, the extremes among them, survived an attack with independent code.

**What was wrong or incomplete.**

*Note 14 §2, the cosquare test:*

- **It fails on far more than 301 pairs.** In random samples of the pairs it left undecided, the cosquare is conjugate to its transpose in 1,398 of 2,500 complete pairs and 639 of 2,500 acyclic pairs.
- **Acyclic pairs are not exempt.** Q = (3, 1, 0, 1, 1, −3) is acyclic, its cosquare is conjugate to its transpose, and Q and −Q lie in different classes. This is the 4-vertex case of the question in Fomin and Neville's Remark 12.11.
- **GRH.** As computed, both verdicts of the test depend on GRH, not only "different".
- **"The smallest" is mislabelled.** The quiver it names is the first in census order.

*Elsewhere in note 14:*

- **§3.** The formula given for P̃ is wrong when k and k′ are not joined.
- **§6.** The script for Theorem 14.2 does not check three facts that its proof states.
- **§1 item 4, §5 and §9.** The split between proved and measured classes is 258,363 and 297,465, not 239,507 and 316,321.
- **§8, the conclusion of the tube certificates.**
  - It cites Theorem 14.1 item 4, which assumes V′ finite. What holds without finiteness is V′(x) = N, which is enough.
  - The justification of "the growing vertex" is not the right argument. The conclusion stands (§6.4).
  - One check in the engine's table is vacuous.

*Note 13:*

- **Acyclic quivers at the bottom.** They are at the bottom only of classes that contain a quiver of height ≤ 18.
- **Item 3 of Proposition 13.1.** Its proof needs Caldero–Keller for every acyclic quiver of the class.
- **The cheap equivalence test.** It needs both quivers of height ≤ 18.
- **The stored run.** The N = 18 run predates the last edit of `n4_conj55.py`. Every number re-derived agrees with it.

*Notes 15, 16 and 17:*

- **Out of date.** Notes 15 and 16 say that Warkentin's thesis was not read. Note 15, through the note of note 17, says that "no entry is smaller" is not in it.
- **One false statement.** Note 17 §7 says that a fork may have more than one point of return. It has exactly one (Warkentin, Lemma 2.3.e).

All fixes are in place as quoted "Correction (note 19)" or "Update (note 19)" notes (§7).

---

## 2. How the check was done

The check was made separately from the notes it checks, starting from their statements, with new code, by fresh instances of the same AI model that wrote the notes. It is an independent derivation and test, not a specialist's reading.

**Notes 15 and 16, and the sources of §4.**

- **The searches of `review19.py`.**
  - All are on labelled quivers, with Python integers.
  - They use no canonical form during the search, so no relabelling bookkeeping can go wrong.
  - No fork is pruned unless stated.
  - A canonical form is applied only at the end. It is the lexicographic maximum over relabellings; the scripts being checked use the minimum.
- **The fork test and the Markov value** are written from Warkentin's Definition 2.1 and from Fomin–Neville's Definitions 4.2, 5.1 and 5.2.
- **The three certificate scripts** were read line by line and rerun: `np_corridor_prove.py`, and `n4_doors.py prove` and `prove2`. The reruns are identical to the stored logs, apart from the audit lines of `np_corridor_prove.py`, which were run for t = 8 only.

**Notes 13 and 14** were checked in three separate passes, each with its own code:

- note 13;
- the theorems of note 14: Theorem 14.1 against Ervin and Warkentin, Theorem 14.2, and the cosquare;
- note 14's counts and tube certificates.

The points used below were then re-checked against the logs of these passes, and four things were recomputed: the acyclic cosquare example, the count 258,363 in `n4_opposite_pockets.log`, the reconciliation of note 13's certificate counts, and the vacuous check of note 14 §8.

---

## 3. Claims checked

### Note 16

Note 17 checked note 16 in full and found no theorem false. The checks here were made without knowing its results, and they agree with it wherever both looked.

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Lemmas 16.1 (step), 53.2 (turn), 53.3 (the top) and the corollary of §2 | 16 §2 | Confirmed | Proofs re-derived. Random tests: 40,000 quivers each for 53.1 and 53.2, and 20,159 quivers that satisfy the hypotheses of 53.3, with no failure (`review19_lemmas16.log`) |
| Theorem 16.4: the route of 4t³ − 2t² + 4 mutations; one quiver at H⁺(t), all others at most H⁺(t) − t²; P⁺_t ≇ −P⁺_t; the same for P_t | 16 §3.2 | Confirmed | Proof re-derived. For every t from 2 to 64, `route16` builds the route and checks: every column of the table; μ_c(T) = −μ_p(T); every height; the number of mutations; non-isomorphism, by a canonical form; and the in-weight argument (`review19_route16.log`) |
| Theorem 16.5: no lower route for 2 ≤ t ≤ 64, both families | 16 §3.3 | Confirmed | A labelled breadth-first search without fork pruning, for every t from 2 to 64 and both families, finds no quiver of height ≤ t² below H other than relabellings of the start. The counts are those of the table. P⁺_t has two labelled copies of each class (3,123,074 = 2 × 1,561,537 at t = 64) and P_t one (1,301,189), for totals of 25.7 and 21.4 million classes (`review19_search16.log`, `review19_search16_small.log`) |
| `np_barrier.c` | 16 §3.3 | Sound | §5 |
| Theorem 16.6, the certificate for t ≥ 8 | 16 §4 | Confirmed | `np_corridor_prove.py` read line by line (§5). Rerun: 938 claims, 149 members, all certified. The exits are 161 member, 428 height, 54 fork and 123 new member, 766 in all. Note 17 replayed every verdict with PARI |
| The core of P⁺_t and of P_t (table of §4.2) | 16 §4.2 | Confirmed, t ≤ 10 | Own fork test, forks above t² pruned. P⁺_t: 120, 125, 263, 492, 840, 1,331, 1,985, 2,827, 3,882. P_t: 42, 120, 258, 490, 839, 1,328, 1,980, 2,822, 3,874 (`review19_core16.log`) |
| Lemma 15.5 as used in §4.1 | 16 §4.1 | Confirmed at the source | §4 |
| Corollary 16.7 | 16 §4 | Confirmed | 2(s − 1)⁵ − (s − 1)⁴ − (2s⁵ − 11s⁴) = 24s³ − 26s² + 14s − 3 > 0 for s ≥ 2. Least constant on 4 ≤ w < 4,225: 10.5647. H⁺(⌊√w⌋) ≤ 2w² exactly at w = 6, 7, 8, 15 (`review19_cor16.log`) |
| Remark "mutation-cyclic" | 16 §3.3 | Confirmed | The triangle q → c → c₁ → q is oriented, its weights are ≥ 2, and its Markov constant −2t⁵ + 2t⁴ + 2t³ + 2t² + 1 is below 4 |
| The records 14, 70, 107, 272 and 437 (§6.1, §6.2) | 16 §6 | Confirmed | Own labelled minimax search without pruning on the five quivers named in §6. Each joins at exactly that level, and each time at a relabelling of its opposite (`review19_records16.log`). They remain lower bounds for F(5, w) |
| Lemma 16.8 | 16 §6.2 | Confirmed | [x]₊ is positively homogeneous |
| §5, the count for pure routes | 16 §5 | Correctly labelled [H] | Constraints 1 to 4 re-derived. Note 18 has since found routes of order w³ outside this design |

### Note 15

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Theorem 15.1 (1)–(5) | 15 §3.1 | Confirmed | 50,000 random steps with c = 0 to 6: the step formula, its inverse, the invariant P and \|P\| = \|Pf\|. 3,120 columns with c = 2 to 6: closed forms, sign pattern and valley (`review19_orbits.log`) |
| Corollary 15.2 | 15 §3.2 | Confirmed | 11,398 random weight-2 lines with D ≥ 2: z is constant between the bottoms and the identity is exact |
| The first corridor | 15 §3.2 | Confirmed | Proof re-derived: 4 + s² = 4 + (\|x\| ∓ \|y\|)², so s ≤ 2w |
| Proposition 15.3, and its table for c ≥ 2 | 15 §3.3 | Confirmed | Proof re-derived. Exhaustive over lines with c ≥ 2 from every start of height w ≤ 5: no gap above w² + w. The maxima reproduce the table: 3, 5, 8, 9 for c = 2; 4, 5, 7 for c = 3; 5, 6 for c = 4 |
| Lemma 15.4 | 15 §4 | Confirmed, [P] | Warkentin's thesis, Lemma 2.5 and its proof (§4) |
| Lemma 15.5 | 15 §4 | Confirmed | §4 |
| Theorem 15.6 and the region 𝓜_t | 15 §5.2–5.4 | Confirmed | `prove` read line by line, rerun identical (43 claims). Labelled search without pruning for t = 3 to 16: the only class of height ≤ t² below H_t is that of Q_t, and −Q_t is reached at H_t. The components below H_t have 100, 235, 463 and 806 quivers at t = 3 to 6, the numbers of §5.4 (`review19_search15.log`) |
| Corollary 15.7 | 15 §5.2 | Confirmed | Proof re-derived |
| Theorem 15.13 and the region 𝓡_b | 15 §5.1 | Confirmed | `prove2` read line by line: every cell of the exit table is a claim or the reverse of a certified step. Rerun identical (30 claims). Search without forks for every b from 5 to 48: the join with −R_b is at exactly 2b² − 3b − 3, and nothing joins lower |
| Corollary 15.14 | 15 §5.1 | Confirmed | 2(w − 1)² − 3(w − 1) − 3 = 2w² − 7w + 2 |
| Odd b | 15 §5.1 | Measured, and now independently to b = 48 | As above. A proof is still missing (Problem 15.12) |
| Proposition 15.8 (V_b) | 15 §7.4 | Confirmed, b = 3 to 80 | Own test of proper orderings and M = n − tr(U⁻ᵀU): one proper cyclic order ⟨0, 2, 1, 3⟩, M = 5, Pf = −2. The heights of the four mutations, the route to −V_b at b + 1, and V_b ≇ −V_b all check (`review19_vb.log`). V_b is mutation-cyclic: {0, 1, 2} is an oriented triangle with weights b, 2, b and Markov constant 4 |
| M of G_k, R_b and Q_t | 15 §7.2 | Confirmed | One proper order, and the stated polynomials, for R_b with b = 5 to 24, Q_t with t = 3 to 11, and G_k with k = 3 to 29 (`review19_markov15.log`) |
| The door lemma | 15 §6 | Confirmed | Random doors |
| \|Pf\| ≤ 2w² unless the quiver is a vortex | 15 §8 | Confirmed | The 16 sign patterns with three Pfaffian terms of one sign are exactly the vortex patterns. The largest \|Pf\| of a non-vortex quiver with entries ≤ 7 is 98 = 2·7² (`review19_pf15.log`) |

### Note 14

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Q and −Q have the same Alexander polynomial, Alexander lattices, M and det B | 14 §2 | Confirmed | U_opp = wUᵀw by hand. On 300 random quivers: Δ(t), every minor up to sign, and M agree |
| The ideal-class test: different classes in the maximal order imply not conjugate; equal classes with ℤ[x] maximal imply conjugate | 14 §2 | Confirmed | Latimer–MacDuffee. The adjugate columns are right eigenvectors of C and of Cᵀ |
| "A verdict 'different' is conditional on [GRH]" | 14 §2 | Incomplete | `transpose_test` never calls `bnfcertify`, so as computed every verdict, and every class number, rests on GRH. All 332 verdicts "conjugate" are now unconditional: for each, an explicit G ∈ GL₄(ℤ) with CG = GCᵀ was checked in integers. Of 25 sampled verdicts "different", `bnfcertify` certified 20; the other 5 timed out at 45 s (`review19_n14a_cosq.log`) |
| The cosquare table: 174,149 classes, 92,999 of 160,019 pairs separated, 14,130 self-mirror classes never "different" | 14 §2 | Confirmed | A re-tabulation of `n4_opposite_fn.jsonl.gz`. Own PARI code agrees on 592 records |
| "It provably fails on 301 pairs" | 14 §2, §1 item 1 | Understated | Among pairs the test left undecided, an explicit conjugator exists in 1,398 of 2,500 sampled complete pairs and 639 of 2,500 sampled acyclic pairs (`review19_n14a_cosq2_complete.log`, `…_acyclic.log`). Extrapolated, that is thousands of pairs |
| "No acyclic pair fails this way … The 17,240 undecided acyclic pairs could still contain one" | 14 §2 | True as stated; the open point is settled | No acyclic pair has a maximal ℤ[x] with equal ideal classes, but the undecided ones do contain such pairs. The first: Q = (3, 1, 0, 1, 1, −3) (§6.1) |
| "The smallest has rows (0, 5, 4, −3), …" | 14 §2 | Wording | Every stated property checks, and an explicit conjugator exists. But it is the first such quiver in census order (class 9630, level 5, weight 24). Smaller ones exist: weight 22 (class 18592) and \|M\| = 63 (class 9641) (`review19_n14a_example.log`) |
| The totally-proper table: 204,498, 196,262, 334,168, 66,592, 132,611 | 14 §2 | Not recomputed | |
| (F1), (F2), (F3) | 14 §3 | Confirmed at the sources | Warkentin's Lemma 2.5, Lemma 2.8 and Corollary 6.2; Ervin's Lemmas 2.7, 2.8 and 4.6 |
| (F4) | 14 §3 | Correction | When k and k′ are not joined, μ_k μ_k′ μ_k μ_k′ μ_k(P) = μ_k(P), a wing, not P (10,278 cases). When they are joined by one arrow, it is P with k and k′ exchanged (16,888 cases). The rest of (F4) matches Ervin's Lemma 4.23 and Corollary 4.25 (`review19_n14a_preds.log`) |
| Consequences (a), (b), (c) | 14 §3 | Confirmed | Partly published: (a) for forks is Warkentin's Lemma 2.3.e; (c) is in his proof of Lemma 2.5; "a pre-fork with ≥ 2 arrows between k and k′ is a fork" is his Lemma 6.1. Wings and tips have a light pair by definition. 540,000 quivers, no failure |
| The code's exit tests and the direct test of lying in no far region | 14 §3, §4 | Sound | `fork_return`, `prefork_returns` and `exit_returns` agree with own predicates written from Ervin's definitions, on 540,000 quivers and, separately, on 99,222. In all 348,330 cases where `certainly_in_core` returns True, the quiver is none of fork, pre-fork, wing or tip (`review19_n14a_preds.log`, `review19_n14b_units.log`) |
| Theorem 14.1, items 1–4 | 14 §3 | Confirmed | Proof re-derived twice, separately |
| Theorem 14.1, item 5 | 14 §3 | Confirmed | Fork regions are trees. In pre-fork regions, Ervin's proof of Corollary 4.25 never mutates a fork or pre-fork at its point of return, and wings and tips are never exits |
| Theorem 14.2: seven core quivers, twelve far regions, f(G_k, w) = k(k − 1) | 14 §6 | Confirmed; proof completed | Own run for k = 3 to 40. The symbolic script makes every decision through the certified sign test. It does not check three facts that its proof states: that no quiver of the core is an exit, that the printed levels are maxima (they are chosen by evaluating at k = 10⁶), and that the seven are pairwise non-isomorphic. All three were certified for every k ≥ 3 with the same test. The least pre-fork root weight is 2k³ − 2k² − 1, above 6(k² − k) − 6 (`review19_n14a_gk.log`, `review19_n14a_gksym.log`) |
| The tables of §4: finite cores, mirror pairs, the separation of capped classes | 14 §4 | Confirmed | All numbers reproduce. All 788,026 class cores were recomputed with independent code, and every stored field matches. 3,320 cores match as exact sets. The split 176,910 / 55,237 / 51 reproduces; the check's own search order separates all 232,198 classes as 176,910 / 55,287 / 1 (`review19_n14b_counts.log`, `review19_n14b_fullsum.log`, `review19_n14b_cores.log`) |
| Proposition 14.3 | 14 §5 | Confirmed; holds more generally | The hypothesis that the core lies in no far region is not needed (§6.3). Spot check of 602 classes against the pockets file and the census: no mismatch (`review19_n14a_pockets_big.log`) |
| §5 counts: 70,376 pockets, births 3 to 58, maximum ratio 1.578, at most 1.020 for births ≥ 10 | 14 §5 | Confirmed | `n4_opposite_pockets.log` and the 602-class spot check |
| "A theorem for 239,507 classes; for the other 316,321 it rests on … pre-fork regions" | 14 §1 item 4, §5, §9 | Correction | 258,363 and 297,465 (§6.3) |
| Levels do not drop away from the root in pre-fork regions | 14 §3, §10 | Still measured, now much more widely | No drop in 7,764 further regions to radius 5 and 6 (9,065,945 labelled quivers), nor in 1,620 regions to radius 7 and 8 (9,620,126 labelled quivers), of which 1,300 hang from census cores. The controls fire. A proof sketch is in §6.3 (`review19_n14a_mono.log`, `review19_n14a_mono_r6.log`, `review19_n14b_prefork_r7.log`, `review19_n14b_prefork_r8.log`) |
| The tube engine: sign test, linear mutation of families, shifts between families | 14 §8 | Sound | Read line by line (§6.4) |
| "The growing vertex" | 14 §8 | Wrong argument, right conclusion | §6.4 |
| "If x lies in no far region, V′(x) is the core (Theorem 14.1, item 4)" | 14 §8 | Correction | Item 4 assumes V′ finite. Its proof gives V′(x) = N, the set of quivers of the class that lie in no far region, without finiteness. N is the same for every quiver of the class, and that is all the certificate needs |
| "Every Y(n) with n ≥ 3 lies above the lowest level of E" | 14 §8 | Wording | The code compares with the lowest level of E and of Y(0), Y(1), Y(2). Holds in all 225,208 certified classes |
| The table "Checks by the engine" | 14 §8 | One row vacuous, one weak | §6.4 |
| Independent attack on the tube certificates | (new) | Confirmed | 322 certificates, among them the six extremes and τ up to about 10¹⁰. Steps checked: 1,088,289 linear steps at n = 0 to 44, 37,355 steps out of E, and 362,763 growing-vertex steps. Own V′ search: 990,882 quivers, all inside the certificate. The bottom of the core agrees in 322 of 322. Of 120 deliberately broken certificates, 117 are flagged; the other 3 had a redundant family (`review19_n14b_tubecheck_*.log`, `…_tubeplat.log`, `…_tubecontrol.log`) |
| The combined table of §8 | 14 §8 | Confirmed | 225,208, 6,990, 374,616, 375,312, 2,139, 31,804 and 781,036 all reproduce (`review19_n14b_counts.log`) |
| §1 item 6 and §7: self-mirror classes, the action of ι, the last deaths | 14 §1, §7 | Not recomputed | Only the mirror counts were rechecked |

### Note 13

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Certificate "tri" | 13 §3 | Confirmed | Proposition 2.1 of arXiv 2610.36179 asks for an oriented triangle with x, y, z ≥ 2 and x² + y² + z² − xyz ≤ 4. `sc_tri` tests exactly this. Brute force on all 3-vertex quivers with entries in [−8, 8]: 0 mismatches (`review19_n13_units.log`) |
| Certificate "vortex" | 13 §3 | Confirmed | A vortex is complete (Fomin–Neville, Def. 13.1), and the code requires completeness. Fomin–Neville Proposition 13.2 holds on all 729 sign patterns, 16 of them vortices |
| Certificate "markov" (Lemma 2.4) | 13 §3 | Confirmed | It requires connectedness and tests every ordering of every proper class, with the paper's order (4) and Pf = af − be + cd. On 40,000 random walks from acyclic quivers no certificate fired (`review19_n13_soundness.log`) |
| Certificate "cor52" | 13 §3 | Confirmed | H is the maximum of M over the proper classes, as in the paper's (13). It is never used for a quiver without a proper class |
| The stopping rule of the per-class search | 13 §3 | Confirmed | Re-derived. Independent code repeated all 418,042 searches. Each gave the same verdict and certificate type, and every Corollary 5.2 row the same bound K. The rows are 66,785 Corollary 5.2, 335,003 vortex, 15,894 triangle and 194 Lemma 2.4, plus 166 via the cache (`review19_n13_allrows_a.log`, `…_b.log`) |
| Pass and fail counts per height (§4) | 13 §4 | Confirmed exactly for h ≤ 10; consistent for 11–18 | Own labelled union–find for heights 1 to 10, for example 1,613,981, 739,339 and 874,642 at h = 10. All 1,889,317 failing quivers of height ≤ 10 are certified cyclic by own code. Heights 11 to 18: about 564,000 random quivers; the pass fractions agree with the table and all 376,568 failing ones are certified (`review19_n13_lowh_*.log`, `review19_n13_lowcert_*.log`, `review19_n13_samples_random*.log`) |
| Counts of quivers and certificates | 13 §1, §4 | Confirmed | Burnside's count per height (`review19_n13_arith.log`). tri 50,110,169, vortex 9,261,670, markov 1,598,562, closed 1, cor52 253,191, by arithmetic from the logs and the full rerun |
| "The largest bound needed grows like h³", exactly h³ + h² + 5 | 13 §4 | Confirmed for h ≤ 10 | Attained by (−h, 2, 0, −(h − 1), −h, −h); for example 1,105 at h = 10 (`review19_n13_lowcert_10.log`) |
| The paper's own counts | 13 §5 | Confirmed | 34, 633 and 4,276 connected quivers at heights 1 to 3; Theorem 6.2's 534 / 133 and 27 / 1; evidence (i)'s torus and four exceptions (`review19_n13_lowcert_1_3.log`, `review19_n13_evid.log`) |
| The census: all 123,691 classes with a pocket are mutation-cyclic | 13 §6 | Confirmed | Own certificates: 96,594 triangle, 26,816 Lemma 2.4, 168 vortex, 113 Corollary 5.2 (`review19_n13_census.log`) |
| Proposition 13.1, items 1 and 2 | 13 §6 | Confirmed | |
| Proposition 13.1, item 3 | 13 §6 | Statement true; step missing in the proof | The proof shows only that one acyclic quiver has the least height. By Caldero–Keller (the paper's Lemma 2.8), all acyclic quivers of C have the same weighted graph, hence the same height |
| §1: every mutation-acyclic class "has its acyclic quivers at its bottom" | 13 §1 | Hypothesis missing | It needs a quiver of height ≤ 18 in the class, as item 3 of Proposition 13.1 says |
| §6: equivalence of a pair "in which one quiver is mutation-acyclic of height ≤ 18" is decided within height h | 13 §6 | Overstated | It needs both quivers of height ≤ 18. A higher quiver needs the bound of Theorem 5.1 |
| Provenance of the stored run | 13 §8 | Note | `n4_conj55_N18.json.gz` (14:14) and its resolve (14:56) predate the last edit of `n4_conj55.py` (14:58). Every height-18 number re-derived here agrees |
| Number of classes tested (52,762,146 components of G_18) | 13 §4 | Not checked | The argument is correct |

---

## 4. Lemma 15.5 at its sources

Read for this check: Warkentin's thesis (TU Chemnitz 2014, fetched from the DNB link that notes 3, 15 and 16 cite) and Ervin, arXiv 2306.07502.

- **The definition [P].**
  - **Warkentin, Definition 2.1.** An abundant quiver Q is a fork if it is not acyclic and has a vertex r such that (F1) q_ji > q_ir and q_ji > q_rj for all i ∈ Q⁻(r) and j ∈ Q⁺(r), and (F2) Q⁻(r) and Q⁺(r) are acyclic.
  - **The same definition elsewhere.** It is Ervin's Definition 2.5, note 15's definition in §4, and the test in `cert_fork` (both scripts) and `fork_return` (`np_barrier.c`).
- **Lemma 2.3 [P].** In a fork every oriented triangle has the form i → r → j → i with q_ji the strictly largest weight. So the point of return is uniquely determined (2.3.e).
- **Lemma 2.5 [P].** If Q is a fork and k is not its point of return, μ_k(Q) is a fork with point of return k and more arrows. Ervin's Lemma 2.7 is the same statement.
  - The proof begins: "for any two vertices i, j the number of arrows |q_ij| cannot decrease through the mutation".
  - So the part of Lemma 15.4 that note 15 and note 17 treat as their own, "no entry of μ_k(F) is smaller", is in the source.
  - The proof uses no assumption on the number of vertices.
- **Lemma 2.8, the Tree Lemma [P].** The edge between Q and μ_r(Q) is a bridge, and the side of Q is a tree of forks. Ervin's Lemma 2.8 is the version for the labelled mutation graph.
- **Lemma 15.5 follows [I].** Suppose a reduced route leaves a fork at a vertex other than its point of return. Then every later quiver is a fork, and no entry decreases, to the end of the route. If it leaves the fork at its point of return, it entered at another vertex, and the same holds read backwards. This is note 15's proof. It holds for every n, so the uses on 5 vertices in notes 16 and 18 are covered.
- **arXiv 1102.3382** is Warkentin's note *Subquivers of mutation-acyclic quivers are mutation-acyclic*. It is the right source for the subquiver theorem used in notes 12, 13 and 16, and it contains nothing on forks. The note itself says that the fact was already stated by Buan, Marsh and Reiten (2008, Cor. 5.3).

---

## 5. Notes on the certificate scripts

**`np_corridor_prove.py` (Theorem 16.6).**

- **`nonneg` and `smutate`.** `nonneg` shifts every bounded variable to its bound and requires non-negative coefficients. It refuses a variable without a bound. `smutate` needs only weak signs: where an entry at the mutated vertex is zero, both products vanish.
- **`cert_fork`.** It asks for:
  - strict signs at all ten entries, each of absolute value ≥ 2;
  - a quiver that is not acyclic;
  - an entry above t²;
  - Warkentin's (F1) with strict inequalities, and (F2).
- **The domains.** The six domains of K(j) cover {j ≥ 1, v ≥ 1, j + v ≥ 7}, and the three of M1(k) cover {k ≥ 3, u ≥ 1, k + u ≥ 6}. Each retry splits a domain into {variable = bound} and {variable ≥ bound + 1}.
- **The ends of the ranges.** Where a step changes the sign pattern, the domain is split and the end slice is recognised separately. An example is the backward step of K(j) at j = 1, which is recognised as K0. The formula of K at j = 0 is not P⁺_t, and it is never used.
- **The free variable r of L(i).** At i = 2 the backward step lands on L(1) only on the true triples r = N + 1 − i. That is enough, as note 17 also notes.

**`n4_doors.py prove` and `prove2` (Theorems 15.6 and 15.13).**

- **The arithmetic** is the same as above. `wsign` and `ssign` raise an error instead of passing when a sign is not certified.
- **The exit tables.** Every cell of the tables of §5.1 and §5.3 is either a certified claim or the reverse of a certified step (a forward step undoes a backward step).
- **The ends of the lines** are covered by identities of formulas: K(j) at j = t − 1; A(j) at j = 1 and j = c − 1; L(n) at n = 1.
- **"Every member except the start has an entry above its height".** For L(n) this follows from N + 1 ≥ t² + t + 1: either n ≥ t + 1, or u ≥ t² + 1.

**`np_barrier.c` (Theorem 16.5 and the census of note 16 §6).**

- **No overflow.** Every stored entry is at most the cap, which is below 2³¹, so every product is below 2⁶².
- **The search.** The canonical form, the hash table and the minimax Dijkstra are correct.
- **Fork pruning.** With pruning on, a fork is tested for an escape before it is pruned. The pruning is valid. A reduced route between two non-forks contains no fork, because a route that enters a tree of forks at its root can only go up it. The runs of Theorem 16.5 use no pruning.

---

## 6. Note 14 in detail

### 6.1 The cosquare and its transpose [I]

**The example.** Take Q = (3, 1, 0, 1, 1, −3), whose arrows are 0 → 1 (3), 0 → 2, 1 → 2, 1 → 3 and 3 → 2 (3).

- **Q is acyclic.** Its topological order ⟨0, 1, 3, 2⟩ is proper, and there M = 36.
- **C is conjugate to Cᵀ.** Let C = U⁻ᵀU be the cosquare for this order. The matrix

  G = [[−2, −3, 4, 3], [−3, −2, 3, 1], [4, 3, −4, −2], [3, 1, −2, 0]]

  has det G = 1 and CG = GCᵀ.
- **Q and −Q lie in different classes.** Their orbits under sink and source mutations, two quivers each up to relabelling, are disjoint. So by Caldero–Keller, Q and −Q are not mutation-equivalent.

Each step was checked with separate code. The class is mutation-acyclic, so it is totally proper (Neville), and the cosquare is a class invariant. By Fomin–Neville's Lemma 12.5 the cosquare of −Q is conjugate to Cᵀ, hence to C. So no test based on the conjugacy class of the cosquare can separate this mirror pair.

Fomin and Neville's Remark 12.11 says they know no 3-vertex acyclic example of this kind. This is a 4-vertex one (census class 1070). It is one of 639 found in a sample of 2,500 of the 17,240 undecided acyclic pairs.

**What remains true.**

- The test is sound wherever it says "different" (under GRH).
- The pairs it separates are all separated by the core or by Caldero–Keller as well.
- A complete test of integral conjugacy (Eick–Hofmann–O'Brien, which note 14 §10 proposes) would not help with these pairs, because their matrices really are conjugate. Such pairs are common: about half of the complete undecided pairs and a quarter of the acyclic ones in the samples.

### 6.2 (F4) and the sources of §3

**(F1) to (F3) are as quoted.**

- (F1) is Warkentin's Lemma 2.5.
- (F2) is his Lemma 2.8. Ervin proves it for the labelled graph.
- (F3) is his Corollary 6.2.

**(F4) needs one correction.** Warkentin proves the region statement for the exchange graph (Lemma 6.7 for q_kk′ = 0, Lemmas 13.20 to 13.22 for |q_kk′| = 1). Ervin proves it for the labelled graph, and that is the version note 14 uses. Its formula "P̃ = μ_k μ_k′ μ_k μ_k′ μ_k(P)" holds only when k and k′ are joined by one arrow. When they are not joined, μ_k′ μ_k μ_k′ μ_k(P) = P, and P̃ = P is right.

**Two slips in Ervin**, noted during the check of note 14 and not re-checked:

- His Corollary 4.24 is literally false for Q̃.
- His Corollary 4.20 has ∈ and ∉ exchanged relative to his Lemma 4.17.

Note 14 uses neither statement.

### 6.3 Proposition 14.3 without the hypothesis on the core [I]

**Two facts suffice.** Let V′(Q) be finite, with core K.

- **(i) Every quiver outside K lies in a far region hanging from K.** Take a shortest path from K to such a quiver. It leaves K by a step that is not allowed, which is a strict up-exit step into a far region with its foot in K. By Step 1 of the proof of Theorem 14.1, a shortest path never leaves a far region it has entered, since that would bring it back to the foot.
- **(ii) A path between two quivers of K̂ can be cleared of its excursions into far regions.** This is Step 1 again. It removes quivers without adding any.

**Why this is enough.** With (i), the fork regions (trees on which the level does not drop away from the root) and (ii), the proof of Proposition 14.3 goes through unchanged. Nowhere does it use that K lies in no far region.

**The count.** `n4_opposite_pockets.log` records 258,363 classes whose far regions are all rooted at forks. That is the 239,507 of note 14 plus the 18,856 balanced cores made of two forks with a common point of return; in those classes every quiver is a fork. The largest death/birth² among the 258,363 is 0.703, at class 193314. So the pockets of 258,363 classes are proved. For the other 297,465 finite-core classes the listing rests on the measured monotonicity of pre-fork regions:

- 293,857 classes with a certified core and a pre-fork root;
- 3,608 balanced cores of other kinds.

**A proof sketch for pre-fork regions [I, H].** It comes from the second pass over note 14, and it is not yet written out.

- **(A)** An outward step never lowers the level. Check each triangle through the mutated vertex. The only entry that can shrink is |b_iκ| at a wing mutated at κ′, with |q_kk′| = 1. It becomes b − a, where b = |b_iκ′| ≥ a + 2 (Ervin, Corollary 4.12) and b is unchanged, so the maximum does not fall.
- **(B)** The region is the closure of {P, P̃} under outward steps.

Together these would make Proposition 14.3 a theorem for all 555,828 finite-core classes.

### 6.4 The tube engine

**The parts that are sound.**

- **The sign test.** It is a correct induction, and τ ≥ 2 is enforced. "Undetermined" always aborts the certificate.
- **The linear mutation of a family.** It is used only when one factor of every product is constant with a certified sign. The result is cross-checked against the concrete mutation of Y(0), Y(1), Y(2).
- **Shifts between families.** They are matched on three consecutive terms under one relabelling. That fixes them for all n, because relabelling commutes with the recurrence. For δ < 0 the first members are checked as quivers.
- **The empty frontier.** Certification requires an empty frontier, so every allowed step out of E lands in E or in a family.

**The growing vertex.** The text justifies it by "x, y ≥ 2 do not decrease" and monotonicity in x and y. The engine does not check x, y ≥ 2, and that is not the reason the step is right. What the engine checks:

- every entry not at m is constant;
- every entry at m is constant or of certified sign with non-decreasing absolute value;
- (Y(n), m) is not an exit for any n;
- (μ_m Y(n), m) is an exit for n = 0, 1, 2.

This suffices for all n. An entry of μ_m Y(n) away from m that differs from Y(n) lies opposite m in a triangle i, m, j that carries a path j → m → i, and it equals c + |b_im|·|b_mj| with c constant. Every fork or pre-fork condition at m that involves it asks it to point i → j and to exceed |b_im| and |b_mj|, and the margin c + |b_im|(|b_mj| − 1) does not decrease in n. The other conditions involve only constant entries and the fixed signs at m.

**Measured.** All 362,763 growing-vertex steps of 322 certificates, at n ≤ 44, are strict up-exits. A synthetic attack built 25,737 families whose growing-vertex step is an exit at n = 0, and none fails at any n ≤ 40 (`review19_n14b_mono.log`).

**The table "Checks by the engine".**

- **The row "a certificate with a wrong τ, or with one entry of Y(2) changed, is rejected" carries no information.** The procedure closes the changed family alone, with no other families, and it rejects the unchanged family too, in 120 of 120 cases (`review19_n14b_probe.log`). The evidence that row was meant to give now comes from the independent control above: 117 of 120 broken certificates are flagged.
- **The brute-force row is weak.** `no_exit_closure` stops at the first quiver above 10¹². The median is 156 quivers per class, and 27 of 60 classes reach the cap of 4,000.

---

## 7. Corrections made in place

- **Note 13.** Three notes: §1 (the hypothesis for "acyclic quivers at the bottom"), the proof of Proposition 13.1 item 3, and §6 (the pair test). One note in §7 records the provenance of the stored run.
- **Note 14.**
  - §1 item 1: the cosquare's failures, GRH, the explicit conjugators.
  - §1 item 4: the proved count.
  - §2, "A test": GRH.
  - §2, the cosquare table: 301 pairs, "the smallest", the acyclic example.
  - §3: (F4), and the sources of (F1) to (F3) and of consequences (a) and (c).
  - §3, the last row of the table of checks: the further measurements.
  - §5: Proposition 14.3 and the proved split.
  - §6: the three facts certified for Theorem 14.2.
  - §8: "the growing vertex", the conclusion, and the table of checks.
  - §9 and §10.
- **Note 15.** §4: Lemma 15.4 at its source. §9: the second reading of Theorem 15.13 and the sources now read.
- **Note 16.** §8: Warkentin's thesis has been read.
- **Note 17.** §7: the point of return is unique.

---

## 8. Still unchecked

- **Note 16.** The measured statements of §5 and §6 other than the five records. Note 17 compared them with their logs, and note 18 has since gone further.
- **Note 15.** The census statements of §§6 to 8: the door scans, `scan2`, Observation 15.9 and the Markov census. Also the reading of arXiv 2610.36179 in §7.1 and §7.3.
- **Note 14.**
  - The totally-proper table of §2.
  - §7, the self-mirror classes and the last deaths.
  - The balanced-edge counts 533,364 / 22,464, which were checked only once.
  - A full rerun of `n4_opposite_tubes.py run`; 322 of its certificates were attacked instead.
  - Level monotonicity in pre-fork regions, which is still measured.
- **Note 13.** The N = 14 consistency run, and the components of G_18. Heights 11 to 18 were checked only by samples and by the per-class searches.

---

## 9. Reproduce

```bash
PY=python
$PY -I ../verify/review19.py route16 --tmin 2 --tmax 64 > review19_route16.log                               # about 15 minutes
$PY -I ../verify/review19.py search16 --t 2 3 4 5 6 8 10 --classes --at-H > review19_search16_small.log
$PY -I ../verify/review19.py search16 --t $(seq 5 64) --fam P+ P --procs 6 > review19_search16.log            # about 40 minutes, up to 2 GB per worker
$PY -I ../verify/review19.py cor16 > review19_cor16.log
$PY -I ../verify/review19.py search15 --t $(seq 3 16) --b $(seq 5 48) > review19_search15.log
$PY -I ../verify/review19.py orbits --samples 50000 --wmax 5 > review19_orbits.log
$PY -I ../verify/review19.py vb --bmax 80 > review19_vb.log
for q in "-2,-2,-1,2,-2,-2,1,-2,-2,-2:2:40" "-3,-2,-1,2,-3,-2,2,-2,-2,-3:3:120" "-4,-2,1,2,1,-4,-2,-2,3,-4:4:160" \
         "-5,-5,3,1,-5,-4,2,-2,-4,-5:5:320" "-2,3,6,-6,-6,-5,2,-2,-5,-6:6:480"; do
  Q=${q%%:*}; r=${q#*:}; $PY -I ../verify/review19.py bottleneck --n 5 --quiver="$Q" --w ${r%%:*} --cap ${r#*:} --budget 20000000
done > review19_records16.log
```

- **Short drivers.** `review19_lemmas16.log`, `review19_core16.log`, `review19_markov15.log` and `review19_pf15.log` come from short drivers that import `review19.py`. Each log states what it checks.
- **Notes 13 and 14.** The scripts `review19_n13_*.py`, `review19_n14a_*.py` and `review19_n14b_*.py` give their command lines in their headers. Their logs carry the same names.
  - Large intermediate files are in `~/.cache/qmb-review19/`.
  - `review19_n14b_full.py` recomputes every core of the census in chunks. `review19_n14b_fullsum.py` compares the result with the stored files.
  - `review19_n14b_tubecert.py` and `review19_n14b_probe.py` call `n4_opposite_tubes.py` on purpose. The families are not stored, so they must be regenerated before they can be checked with independent code.
- **The cosquare scripts** need cypari2.

---

## Sources

- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014: Definition 2.1, Lemmas 2.3, 2.5 and 2.8, Lemma 6.1, Corollary 6.2. https://d-nb.info/1214302807/34 (read for this check)
- Warkentin, *Subquivers of mutation-acyclic quivers are mutation-acyclic*: https://arxiv.org/abs/1102.3382 (read)
- Ervin, *New hereditary and mutation-invariant properties arising from forks*: Definitions 2.5, 4.5, 4.14 and 4.18; Lemmas 2.7, 2.8, 4.6 and 4.23; Corollaries 4.12, 4.24 and 4.25. https://arxiv.org/abs/2306.07502 (read)
- Fomin, Neville, *Cyclically ordered quivers*: Definitions 4.2, 5.1, 5.2 and 13.1; Fomin–Neville Lemma 12.5; Fomin–Neville Remark 12.11; Fomin–Neville Proposition 13.2. https://arxiv.org/abs/2406.03604
- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*: Proposition 2.1, Lemmas 2.4 and 2.8, Corollary 5.2 and (13). https://arxiv.org/abs/2610.36179
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Notes 12, 13, 14, 15, 16, 17 and 18 of this repository.
