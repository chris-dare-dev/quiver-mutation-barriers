# 13. Conjecture 5.5 of arXiv 2610.36179, tested on every 4-vertex quiver up to height 18

*Run on 2026-11-11. [Note 12](12-checks-of-notes-03-to-10.md) §6 found arXiv 2610.36179, which bounds the height of a mutation path from a mutation-acyclic 4-vertex quiver to an acyclic one. Its Conjecture 5.5 says the quiver's own height suffices; the authors checked this up to height 3. Here it is tested on every 4-vertex quiver up to height 18. Code: [experiments/n4_conj55.py](../experiments/n4_conj55.py) (new). It reuses the enumeration of `n4_all.py` and the mutation of `n4_plateaus.py`; its checks use the canonical form and mutation of `review12.py`. Results: the `n4_conj55_*` files in `experiments/`. Quivers are up to relabelling unless stated otherwise. Height means maximal entry. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

---

## 1. Outcome

**Conjecture 5.5 holds for every 4-vertex quiver of height at most 18 [I, using P].** The authors had checked heights ≤ 3.

- **All quivers of height 1 to 18 were tested.** There are 106,918,566 of them, up to relabelling.
  - 45,694,973 reach an acyclic quiver through quivers of height at most their own.
  - The other 61,223,593 do not. Every one of them is certified mutation-cyclic, so none is a counterexample.
  - Nothing is left undetermined. §4 has the counts per height.
- **How the failing quivers were settled.** 60,387,676 are certified on their component of G_18. The other 835,917, in 418,042 components, are certified by a per-class search. The highest that search had to go was height 6,161. The quartic bound of Corollary 5.3 at h = 18 is 130,248.
- **Certificates, by the first one found:**
  - a mutation-cyclic full triangle: 50,110,169;
  - a vortex: 9,261,670;
  - Lemma 2.4: 1,598,562;
  - Corollary 5.2: 253,191;
  - a finite class with no acyclic quiver (the dreaded torus): 1.
- **The classes tested.** The quivers lie in at most 52,762,146 mutation classes, the number of components of G_18.
- **Checks (§5).**
  - The paper's own counts are reproduced at heights ≤ 3.
  - A second, separately written count agrees exactly on all 6,171,451 quivers of height ≤ 11.
  - Samples of both verdicts and of the certificates re-check.
  - No component with an acyclic quiver carries a certificate of mutation-cyclicity.
- **For the wider question (§6).**
  - Every mutation-acyclic 4-vertex class has f(Q, w) ≤ w for w ≤ 18, has no pocket born at ≤ 18, and has its acyclic quivers at its bottom.
    > **Correction (note 19):** The last clause needs the hypothesis of Proposition 13.1 item 3: if the class contains a quiver of height ≤ 18, its acyclic quivers are at its bottom. A class whose least height is above 18 is not covered. See [note 19](19-checks-of-notes-13-to-16.md).
  - Every pocket born at ≤ 18 therefore lies in a mutation-cyclic class. This covers all 75,951 pockets of note 7.
  - All 123,691 census classes of note 12 with a pocket are certified mutation-cyclic directly, including the 6,037 note 12 left undecided.
  - Up to w = 18, Conjecture 10.1 is a statement about mutation-cyclic classes only.

---

## 2. The statement

I read §§1–2 and 5–6 of the paper in the arXiv PDF (v1, 26 October 2026).

**Conjecture 5.5 (verbatim).** "Every mutation-acyclic four-vertex quiver Q admits a mutation sequence to an acyclic quiver along which every arrow multiplicity is at most ht(Q)."

**Height.** ht(Q) = max_{i<j} |b_ij(Q)|, the largest arrow multiplicity (paper §2). This is the maximal entry of notes 3 to 12. The bound applies to every quiver along the sequence, including Q itself and the acyclic endpoint.

**Labelled, but equivalent up to relabelling.** The sequence is a sequence of mutations of the labelled quiver Q. The paper's identity (3), μ_{π⁻¹(k)}(Q^π) = (μ_k Q)^π, and the fact that relabelling keeps height and acyclicity [P] make the two readings equivalent. A path in the graph of quivers up to relabelling lifts to a labelled sequence from Q. That sequence passes through relabellings of the same quivers and ends at a relabelling of an acyclic quiver, which is acyclic [I].

**The theorems around it [P].**

- **Theorem 1.1 (= 5.1).** A mutation-acyclic 4-vertex quiver Q reaches an acyclic quiver through quivers of height ≤ max{ht(Q), m(Q)}. Here m(Q) is the Markov invariant of Fomin–Neville, evaluated on the totally proper wiggle class of Q.
- **Corollary 5.2.** Put H(Q) = max of ht(Q) and the Markov values M_ω(Q) of all proper wiggle classes [ω] of Q (paper (13)).
  - If Q has no proper wiggle class, it is mutation-cyclic.
  - Otherwise, Q is mutation-acyclic exactly when its component in the mutation graph on quivers of height ≤ H(Q) contains an acyclic quiver.
- **Corollary 5.3.** If Q has a proper wiggle class and height h, then H(Q) ≤ h⁴ + 4h³ + 6h². The hypothesis excludes only vortices, which are mutation-cyclic.
- **Corollary 5.7.** Mutation equivalence up to relabelling is decidable for pairs of 4-vertex quivers of which at least one is mutation-acyclic.
- **Lemma 2.4.** If a connected Q is mutation-acyclic, then m(Q) ≥ 3 and 2|p(Q)| < m(Q), where p is the Pfaffian. This is the source of the Markov exclusion of Lemma 2.6.

**How the authors checked it** (their program `conjecture_evidence.py`, not run here):

1. **Every connected quiver of height ≤ 3.** There are 34, 633 and 4,276 of them at heights 1, 2 and 3, up to relabelling. Each either reaches an acyclic quiver by a search within its own height or is mutation-cyclic. The mutation-cyclic ones are certified by a mutation-cyclic full triangle, a vortex or a Markov exclusion within three mutations. The exceptions are the dreaded torus at height 2 and four quivers at height 3, which Corollary 5.2 certifies. Up to relabelling and reversal, the four are mutation-equivalent to the quiver of Example 5.4.
2. **Regions of low acyclic classes.** From each connected acyclic quiver with entries in {0, 1, 2}, every quiver reachable within height 10: 94,344 quivers in 320 regions.
3. **A random sample.** 2,000 random mutation-acyclic quivers of heights 6 to 60, made by random mutation from acyclic quivers.

Two cases are proven in the paper:

- **Classes with a dense acyclic quiver.** The conjecture holds for every class containing an acyclic quiver with at least two arrows between every pair of vertices. The reason is Felikson–Tumarkin's decreasing mutations.
- **Disconnected quivers.** These are covered by the first paragraph of the proof of Theorem 5.1, through a componentwise descent within ht(Q).

Note 12 §6's paraphrase is accurate. The height-3 check covers connected quivers only.

---

## 3. Method

Let G_L be the mutation graph on 4-vertex quivers of height ≤ L, up to relabelling. Let a(Q) be the least L at which the component of Q in G_L contains an acyclic quiver. Then a(Q) ≥ ht(Q), and Q satisfies Conjecture 5.5 exactly when a(Q) = ht(Q) or Q is mutation-cyclic. Call Q **failing** when a(Q) > ht(Q).

**Step 1: the global run** (`n4_conj55.py run --N 18 --H 18`).

- **Enumeration.** All 106,918,566 quivers of height 1 to 18 are enumerated as in note 7, with the canonical keys of `n4_all.py`. The zero quiver is left out; it is acyclic.
- **Invariants of each quiver.** Computed vectorized:
  - acyclicity, as nilpotency of the arrow matrix;
  - connectivity;
  - mutation-cyclic full triangles;
  - vortices;
  - the proper wiggle classes and their Markov values. These use the six cyclic orders ⟨1, v₂, v₃, v₄⟩, properness as defined in paper §2.1, and wiggle classes by label propagation;
  - H(Q) of (13);
  - the test of Lemma 2.4.
- **Union–find over levels.** It runs over L = 1, …, 18. After each level it marks the components that contain an acyclic quiver, which gives a(Q) for every Q of height ≤ 18, capped at 18.

**Step 2: certificates on the component of G_18.** A failing Q with a(Q) ≤ 18 would be a counterexample. Otherwise the component of Q in G_18 is searched for a certificate of mutation-cyclicity. Every quiver of the component lies in the class of Q. The certificates, in the order tried:

| Name | Certificate | Source |
|---|---|---|
| tri | a member has a mutation-cyclic full triangle | Beineke–Brüstle–Hille with Warkentin; paper Prop. 2.1 [P] |
| vortex | a member is a vortex, i.e. has no proper wiggle class | Fomin–Neville Prop. 13.2 and Thm 2.2; paper Lemma 2.7 [P] |
| markov | a connected member has every proper wiggle class with M < 3 or M ≤ 2\|p\| | paper Lemma 2.4 [P] |
| closed | no member has a mutation above height 18, so the component is the whole class, and it has no acyclic quiver | [I] |
| cor52 | some member X has H(X) ≤ 18 | Corollary 5.2 applied to X [P] |

The last one works because the component of X in G_{H(X)} lies inside this component, which has no acyclic quiver. Quivers with none of these certificates are **undetermined**.

**Step 3: per-class searches** (`resolve`). For each component of G_18 with an undetermined quiver, one representative is searched upward through its class, lowest bottleneck height first. A quiver's bottleneck is the least possible maximum height over paths from the representative. The search stops at the first of:

- an acyclic quiver (a counterexample, with an explicit path);
- a quiver with a tri, vortex or markov certificate;
- the Corollary 5.2 bound.

**The Corollary 5.2 bound [I, from P].** Let K be the least value of max(H(X), bottleneck(X)) over the quivers X reached so far. Once the next bottleneck exceeds K, the whole component of the representative in G_K has been reached. Let X* attain K. The component of X* in G_{H(X*)} lies in that component, and no quiver reached is acyclic. So X* is mutation-cyclic by Corollary 5.2.

A cache passes a verdict to later searches that meet an already settled class. The search reaches at most 2,000,000 quivers per class; no search came near this.

**Step 4: the census classes of note 12** (`census`). The same search is run on the bottom quiver of each of the 123,691 census classes with a pocket born ≤ B/4.

**Checks.** These are in §5.

---

## 4. Results

**Per height** (`n4_conj55_N18_summary.log`, from `n4_conj55_N18.log` and `n4_conj55_N18_resolve.log`).

- "Reach" means the component of the quiver in G_h contains an acyclic quiver.
- "Certified in G_18" means a certificate was found on the quiver's component of G_18.
- "Per-class search" means `resolve` settled it.

| h | quivers | reach an acyclic quiver within h | fail | certified in G_18 | per-class search | counterexamples | undetermined |
|---|---|---|---|---|---|---|---|
| 1 | 41 | 39 | 2 | 2 | 0 | 0 | 0 |
| 2 | 653 | 521 | 132 | 132 | 0 | 0 | 0 |
| 3 | 4,317 | 2,916 | 1,401 | 1,363 | 38 | 0 | 0 |
| 4 | 17,353 | 10,415 | 6,938 | 6,671 | 267 | 0 | 0 |
| 5 | 51,841 | 28,523 | 23,318 | 22,734 | 584 | 0 | 0 |
| 6 | 127,541 | 66,393 | 61,148 | 59,424 | 1,724 | 0 | 0 |
| 7 | 273,813 | 135,932 | 137,881 | 135,396 | 2,485 | 0 | 0 |
| 8 | 531,537 | 255,752 | 275,785 | 270,115 | 5,670 | 0 | 0 |
| 9 | 955,033 | 446,963 | 508,070 | 499,577 | 8,493 | 0 | 0 |
| 10 | 1,613,981 | 739,339 | 874,642 | 858,804 | 15,838 | 0 | 0 |
| 11 | 2,595,341 | 1,166,783 | 1,428,558 | 1,407,167 | 21,391 | 0 | 0 |
| 12 | 4,005,273 | 1,776,593 | 2,228,680 | 2,192,746 | 35,934 | 0 | 0 |
| 13 | 5,971,057 | 2,611,703 | 3,359,354 | 3,311,954 | 47,400 | 0 | 0 |
| 14 | 8,643,013 | 3,740,365 | 4,902,648 | 4,833,516 | 69,132 | 0 | 0 |
| 15 | 12,196,421 | 5,229,234 | 6,967,187 | 6,871,266 | 95,921 | 0 | 0 |
| 16 | 16,833,441 | 7,159,350 | 9,674,091 | 9,540,580 | 133,511 | 0 | 0 |
| 17 | 22,785,033 | 9,612,933 | 13,172,100 | 13,005,143 | 166,957 | 0 | 0 |
| 18 | 30,312,877 | 12,711,219 | 17,601,658 | 17,371,086 | 230,572 | 0 | 0 |
| total | 106,918,566 | 45,694,973 | 61,223,593 | 60,387,676 | 835,917 | 0 | 0 |

**Counts of quivers.** The counts per level are those of note 7, which note 12 confirmed by Burnside's lemma. 8,643 of the quivers are disconnected. The paper proves the conjecture for these (§2), and none of them is a counterexample here either.

**The classes tested.** Each component of G_18 lies in one mutation class. So the number of components of G_18 meeting height ≤ h bounds the number of classes tested from above. These numbers are 13, 160, 1,210, 6,174, 23,052, 69,085, 175,496, 393,297, 802,648, 1,519,065, 2,702,265, 4,572,773, 7,415,899, 11,598,158, 17,584,786, 25,951,046, 37,397,606 and 52,762,146 for h = 1 to 18. The last is note 7's count of components alive at level 18. For h ≤ 9, note 10's census puts the number of classes at 788,026, against 802,648 components here. Note 10 resolved its classes at bounds 192 to 512. A class whose low components join only above 18 counts once there and more than once here. The components of G_h that contain a height-h quiver number 13, 157, 1,192, …, 16,350,217 at h = 1, 2, 3, …, 18. Of these, 3,170,326 at h = 18 contain an acyclic quiver.

**Certificates.** Each quiver is counted by the first certificate found. In G_18 the order tried is tri, vortex, markov, closed, cor52. In the per-class search it is whichever is met first.

| Certificate | Failing quivers | Rests on |
|---|---|---|
| tri: a mutation-cyclic full triangle | 50,110,169 | Beineke–Brüstle–Hille and Warkentin [P] |
| vortex | 9,261,670 | Fomin–Neville Prop. 13.2, and every mutation-acyclic quiver having a totally proper class (Fomin–Neville, Neville) [P] |
| markov: Lemma 2.4 | 1,598,562 | Lemma 2.4 of the paper, which rests on Neville's theorem [P] |
| closed: finite class | 1 | none [I]; this is the dreaded torus at height 2 |
| cor52: Corollary 5.2 | 253,191 | Theorem 5.1 of the paper [P] |
| total | 61,223,593 | |

Two counts bound how much rests on which certificate:

- **At most 1,851,753 failing quivers rest on Lemma 2.4 or Corollary 5.2.** Every other one has a triangle, a vortex or a closed class on its component of G_18, or met a triangle or a vortex in the per-class search.
- **At least 11,113,422 have no triangle in what was searched.** These rest on a vortex, Lemma 2.4 or Corollary 5.2.

**The per-class search** (`n4_conj55_N18_resolve.log`; 2,464 s on 4 workers).

- It searched 418,042 components holding 835,917 failing quivers.
- It stopped at a vortex in 335,036 searches, at the Corollary 5.2 bound in 66,918, at a triangle in 15,894 and at Lemma 2.4 in 194. 166 of these verdicts came through the cache.
- The largest search reached 4,316 quivers, with K = 942.
- The largest Corollary 5.2 bound was K = 6,161, from the height-18 representative (−18, −18, 0, −17, 2, −18). Its search reached 1,817 quivers.
- No search came near its budget of 2,000,000 quivers.
- None reached an acyclic quiver.

**The largest bound needed grows like h³ [I, measured].** For representatives of height h, the largest Corollary 5.2 bound the search needed is exactly h³ + h² + 5 at every h from 3 to 18 (`n4_conj55_N18_summary.log`). It is also exact at h = 2, in the N = 9 route (`n4_conj55_N9_summary.log`). At h = 3 the value is 41, the H(Q) of Example 5.4. So in practice, certifying mutation-cyclicity this way took cubic height, not the quartic of Corollary 5.3. That the pattern continues above 18 is a guess [H].

**Height 3 compared with the paper.** Here 38 failing quivers of height 3 need the per-class search, all settled by Corollary 5.2. The paper's evidence (i) has four exceptions at height 3. Its certificates are searched within three mutations and with full Markov exclusion, so the two counts measure different things.

---

## 5. Checks

**Unit checks** (`check`, `n4_conj55_check.log`, 36 checks, all pass). Against the paper:

- **Example 5.4.** One proper wiggle class, Markov value 41, p² = 225 and H = 41. The acyclic quiver (0, 0, 3, 5, 1, 1) has (M, p²) = (41, 225) in its order 1 < 2 < 3 < 4. The component inside height 41 has 238 labelled quivers, the paper's number (119 up to relabelling), and none is acyclic.
- **Remark 5.6.** G_x is acyclic with m = x³ + 4x² + x + 2 for x = 1 to 8.
- **Remark 2.5.** L_k has M = 2k² + 1 and p = k² for k = 1 to 5.
- **Proposition 6.1.** μ₁ of the double-arrow box is Markov-excluded.
- **The dreaded torus.** It is closed under mutation.

Against slow references, on all 15,625 labelled quivers with entries in [−2, 2] and on 20,000 random ones of height ≤ 9:

- acyclicity, triangles (against `review12.py`), vortices and connectivity agree;
- vortex ⟺ no proper wiggle class holds on every one, which is Fomin–Neville's Proposition 13.2;
- the pure-Python invariants used by `resolve` agree with the vectorized ones of `run`;
- H and the Lemma 2.4 test are unchanged under relabelling, and H under reversal.

**The paper's own counts are reproduced [I].**

- **Connected quivers.** 34, 633 and 4,276 at heights 1, 2 and 3 (evidence (i)).
- **Theorem 6.2 (height ≤ 2).** The paper has 534 mutation-acyclic and 133 mutation-cyclic connected quivers, and 27 and 1 disconnected ones, counting the zero quiver. Here:
  - connected: 32 + 502 = 534 reach an acyclic quiver within their height, and 2 + 131 = 133 fail;
  - disconnected: 7 + 19 = 26 pass, which is 27 with the zero quiver, and 0 + 1 = 1 fails (`n4_conj55_N9_summary.log`).

**A second count for heights 1 to 11** (`recount`; `n4_conj55_N9_recount.log` and `n4_conj55_N18_recount_10_11.log`). It enumerates the quivers of each height from `review12.py`'s canonical form (the lexicographic maximum over relabellings, against the minimum key of `run`). For each quiver it runs a plain BFS inside its height. The quivers, connected quivers, passing quivers and failing connected quivers agree exactly at every height. At height 11 that is 2,595,341, 2,594,844, 1,166,783 and 1,428,487. This recomputes the pass/fail split of all 6,171,451 quivers of height ≤ 11 by a second route.

**A second route for heights 1 to 9.** A run with N = 9 leaves 30,952 failing quivers undetermined in G_9. `resolve` certifies all of them mutation-cyclic. They lie in 13,511 components: 8,870 are settled by a vortex, 3,878 by Corollary 5.2, 719 by a triangle and 44 by Lemma 2.4. That run took 27 s, and its resolve 73 s (`n4_conj55_N9_resolve.log`). The pass and fail counts are those of the N = 18 run.

**No component is both [I].** A component with an acyclic member is mutation-acyclic, so none of its members may carry a tri, vortex or markov certificate. At N = 9, none of the 204,498 components of G_9 with an acyclic member, holding 947,454 quivers, carries one (`n4_conj55_N9.log`). The same holds at N = 14, for 2,489,473 such components of G_14 holding 10,982,237 quivers (`n4_conj55_N14.log`). The N = 14 run counts 11,634,565 components of G_14, note 7's number of components alive at level 14.

**Samples.** `verify` uses separate code (`n4_conj55_N9_verify.log`):

- **Passing quivers.** A labelled BFS without canonical forms. Its path is replayed and every height checked.
- **Failing quivers.** A BFS on `review12.py`'s canonical form, which must exhaust the component without an acyclic quiver.

At N = 9, 2,000 of 2,000 passing quivers and 2,000 of 2,000 failing ones are confirmed. At N = 18, 2,000 of 2,000 of each are confirmed (`n4_conj55_N18_verify.log`). Most sampled passing quivers are acyclic themselves: 1,896 of the 2,000 at N = 18. The exhaustive recount above covers the non-trivial ones up to height 11.

`verify-resolve` replays resolve's certificates. It reaches the certified quiver X from the representative within the stated height and re-tests the certificate on X. For Corollary 5.2 it also computes H(X) again and exhausts the *labelled* component of X inside height H(X), with no acyclic quiver found. At N = 9 all 944 sampled certificates hold, the largest labelled component being 3,360 quivers (`n4_conj55_N9_verify_resolve.log`). At N = 18 all 1,094 sampled certificates hold: 300 each of cor52, tri and vortex, and all 194 of markov. The largest labelled component is 6,712 (`n4_conj55_N18_verify_resolve.log`). So do the 40 cor52 rows with the largest bounds, K = 5,207 to 6,161 (`n4_conj55_N18_verify_resolve_largest.log`).

**Note 12's census split is reproduced** (`n4_conj55_census.log`): 96,068 classes with a triangle at the bottom, 21,586 found by searching upward, and 6,037 undecided.

---

## 6. What follows for the wider question

**Proposition 13.1 [I, from P and §4].** Let C be a mutation class of 4-vertex quivers that contains an acyclic quiver, and let w ≤ 18.

1. The quivers of C of height ≤ w are joined to each other through quivers of height ≤ w. So f(Q, w) ≤ w for every Q in C.
2. C has no pocket born at a level ≤ 18.
3. If C contains a quiver of height ≤ 18, then its acyclic quivers have the least height in C.

*Proof.*

1. Let X and Y be quivers of C of height ≤ w. They are mutation-acyclic quivers of height ≤ 18, so by §4 they reach acyclic quivers A_X and A_Y through quivers of height ≤ ht(X) and ≤ ht(Y), both ≤ w. By Caldero–Keller (paper Lemma 2.8), A_Y is reached from A_X, up to relabelling, by mutations at sinks and sources. These keep the weighted graph and so the height. So A_X and A_Y are joined at height ht(A_X) = ht(A_Y) ≤ w.
2. A pocket born at L would be a second component of C's quivers of height ≤ L inside G_L. Item 1 with w = L rules it out.
3. A quiver of C of least height reaches an acyclic quiver without going higher, so that acyclic quiver has the least height too. ∎

> **Correction (note 19):** One step is missing. The argument shows that one acyclic quiver of C has the least height. By Caldero–Keller (the paper's Lemma 2.8), all acyclic quivers of C have the same weighted graph up to relabelling, hence the same height, so all of them have the least height. The statement is unchanged.

**What this changes.**

- **The quartic bound is replaced by the strong form, up to w = 18.** Note 12 §6 drew f(Q, w) ≤ w⁴ + 4w³ + 6w² for mutation-acyclic classes from Theorem 1.1. Up to w = 18, f(Q, w) ≤ w holds instead.
- **Note 7 §4's heuristic is now a statement with a proof up to level 18.** The heuristic was "acyclic quivers are never in pockets". No mutation-acyclic class has a pocket born at ≤ 18, and the missing step note 7 named, that an acyclic quiver attains the class bottom, is item 3. All 75,951 pockets of note 7 (births 2 to 17) therefore lie in mutation-cyclic classes.
- **All of note 12's pocket classes are mutation-cyclic.** Note 12 §6 found no acyclic quiver inside the bound of any of the 123,691 census classes with a pocket born ≤ B/4, and certified 117,654 of them mutation-cyclic. `census` certifies all 123,691 [I, using P] (`n4_conj55_census.log`). The 6,037 classes note 12 left undecided are certified by Lemma 2.4 (5,756), a vortex (168) and Corollary 5.2 (113). This uses only the per-class search of §3, not Conjecture 5.5.
- **Conjecture 10.1 is now about mutation-cyclic classes only, up to w = 18.** On mutation-acyclic classes it holds in the strong form, f ≤ w. Its content is the mutation-cyclic classes, which hold G_k, every census extreme (note 12) and, up to birth 18, every pocket. There the paper's method decides nothing (Corollary 5.7).
- **Deciding mutation-acyclicity becomes cheap up to height 18.** For a 4-vertex quiver of height h ≤ 18, mutation-acyclicity is decided by a search within height h, that is (2h + 1)⁶ labelled states, instead of within H(Q) ≤ h⁴ + 4h³ + 6h². With Corollary 5.7 the same holds for mutation equivalence of a pair in which one quiver is mutation-acyclic of height ≤ 18. For pairs of mutation-cyclic quivers nothing changes: Problem 2.6.14 of Fomin–Williams–Zelevinsky stays open there.

  > **Correction (note 19):** The pair test needs both quivers of height ≤ 18. The search from a mutation-acyclic quiver of height ≤ 18 stays within its height. For the other quiver, if it is higher than 18, Conjecture 5.5 has not been checked, and its search needs the bound max(ht, m) of Theorem 5.1.

---

## 7. Limitations

- **Height ≤ 18 only.** Beyond 18 nothing is tested. A run at N = 20 (about 198 million quivers) needs roughly twice the memory and time and was not attempted.
- **What the verdict rests on.** The mutation-cyclic side rests on published theorems, as §4's certificate table shows:
  - 253,191 failing quivers were certified first by Corollary 5.2, i.e. by Theorem 5.1 of the paper under test. The authors verified its case analysis by machine, and formalised in Lean only a coarser bound.
  - 1,598,562 were certified first by Lemma 2.4, and 9,261,670 by the vortex criterion. Both go through Neville's theorem that mutation-acyclic quivers are totally proper.
  - At least 11,113,422 have no triangle in what was searched. So they need more than the classical Beineke–Brüstle–Hille and Warkentin certificate.
  - If Theorem 5.1 failed, the quivers certified only by Corollary 5.2 would become undetermined, not counterexamples. No search found a failing quiver of height ≤ 18 to be mutation-acyclic.
  - The passing side needs no citation. Each passing quiver has a path to an acyclic quiver inside its own height. The union–find found these paths for all heights; for heights ≤ 11 every one was found again by separate code, and above height 11 a sample was.
- **Not checked separately when written.** The checks of §5 run through separately written code, but this note and its code had no separate check when they were written. The authors' `conjecture_evidence.py` was not run.
  > **Update (note 19):** A separate check ([note 19](19-checks-of-notes-13-to-16.md)) found no counterexample and no unsound certificate.
  > - **The certificates.** Each of the five is applied with the hypotheses of its source.
  > - **Heights ≤ 10.** The pass and fail counts were recomputed exactly with separate code. All 1,889,317 failing quivers of height ≤ 10 were certified cyclic again.
  > - **The per-class searches.** All 418,042 were repeated with the same verdicts, certificate types and bounds.
  > - **Provenance.** The stored N = 18 run (`n4_conj55_N18.json.gz`, 14:14, and its resolve, 14:56) predates the last edit of `n4_conj55.py` (14:58). Every number that was re-derived agrees with it.
- **Counting convention.** All counts are up to relabelling, not up to reversal. The paper counts the same way.

---

## 8. Reproduce

```bash
PY=python
$PY -I n4_conj55.py check > n4_conj55_check.log
$PY -I n4_conj55.py run --H 18 --N 18 --store-h 18 --out n4_conj55_N18.json.gz > n4_conj55_N18.log      # 27 minutes, 11 GB
$PY -I n4_conj55.py resolve --inp n4_conj55_N18.json.gz --out n4_conj55_N18_resolve.json.gz --H 18 --every 20000 --workers 4 > n4_conj55_N18_resolve.log   # 41 minutes
$PY -I n4_conj55.py summary --run n4_conj55_N18.json.gz --resolve n4_conj55_N18_resolve.json.gz > n4_conj55_N18_summary.log
$PY -I n4_conj55.py verify --inp n4_conj55_N18.json.gz --n 2000 > n4_conj55_N18_verify.log
$PY -I n4_conj55.py verify-resolve --inp n4_conj55_N18_resolve.json.gz --n 300 > n4_conj55_N18_verify_resolve.log
$PY -I n4_conj55.py verify-resolve --inp n4_conj55_N18_resolve.json.gz --n 40 --largest > n4_conj55_N18_verify_resolve_largest.log
$PY -I n4_conj55.py recount --inp n4_conj55_N18.json.gz --hmin 10 --H 11 > n4_conj55_N18_recount_10_11.log   # about 10 minutes
$PY -I n4_conj55.py census > n4_conj55_census.log                                                         # about 3 minutes
$PY -I n4_conj55.py run --H 14 --N 14 --store-h 0 --out ~/.cache/conj55_N14.json.gz > n4_conj55_N14.log  # the consistency check at N = 14
# the second route for heights <= 9
$PY -I n4_conj55.py run --H 9 --N 9 --store-h 9 --out n4_conj55_N9.json.gz > n4_conj55_N9.log
$PY -I n4_conj55.py resolve --inp n4_conj55_N9.json.gz --out n4_conj55_N9_resolve.json.gz --H 9 --every 2000 > n4_conj55_N9_resolve.log
$PY -I n4_conj55.py summary --run n4_conj55_N9.json.gz --resolve n4_conj55_N9_resolve.json.gz > n4_conj55_N9_summary.log
$PY -I n4_conj55.py recount --inp n4_conj55_N9.json.gz --H 9 > n4_conj55_N9_recount.log                # about 2 minutes
$PY -I n4_conj55.py verify --inp n4_conj55_N9.json.gz --n 2000 > n4_conj55_N9_verify.log
$PY -I n4_conj55.py verify-resolve --inp n4_conj55_N9_resolve.json.gz --n 300 > n4_conj55_N9_verify_resolve.log
```

`n4_conj55.py` overwrites its outputs. `census` reads the stored class files of notes 8 and 10.

---

## Sources

- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*, arXiv 2610.36179 (v1, 26 October 2026): Theorem 1.1 (= 5.1), Corollaries 5.2, 5.3 and 5.7, Conjecture 5.5 and its evidence, Example 5.4, Lemmas 2.4, 2.6 and 2.7, Lemma 2.8, Proposition 6.1 and Theorem 6.2: https://arxiv.org/abs/2610.36179
- Beineke, Brüstle, Hille, *Cluster-cyclic quivers with three vertices and the Markov equation*: https://arxiv.org/abs/math/0612213
- Warkentin, *Subquivers of mutation-acyclic quivers are mutation-acyclic*: https://arxiv.org/abs/1102.3382
- Fomin, Neville, *Cyclically ordered quivers*: https://arxiv.org/abs/2406.03604
- Neville, *Mutation-acyclic quivers are totally proper*: https://arxiv.org/abs/2409.17832
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Notes 4, 7, 8, 10, 11 and 12 of this repository.
