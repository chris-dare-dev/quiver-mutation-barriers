# 23. Checks of notes 20, 21 and 22

*Prepared 2026-11-14. Notes [20](20-core-of-the-cubic-family.md), [21](21-barriers-and-the-mutation-path-owf.md) and [22](22-tube-lemma-and-its-limits.md) were written on 2026-11-12, and none had been checked. This note records a separate check, in the way [note 12](12-checks-of-notes-03-to-10.md), [note 17](17-checks-of-note-16.md) and [note 19](19-checks-of-notes-13-to-16.md) checked earlier notes: the proofs re-derived by hand, and the key numbers recomputed with new code.*

*Code: `verify/review23_lead_n20_xmove.py`, `review23_lead_n21_mask.py` and `review23_lead_n22.py`; `review23_n20_*`, `review23_n21_*` and `review23_n22_*`. None imports or adapts the scripts being checked. Two scripts call a script being checked on purpose, as a black box, and say so in their headers. `review23_n21_blackbox.py` calls `owf_barrier.py attack` to obtain routes, which are then checked with independent code. `review23_n22_regen14.py` calls `n4_opposite_tubes.py one` to regenerate note 14's certificates, which are not stored, and its printed output is then checked with independent code. Results: the `review23_*.log` files.*

*Versions checked:*

| Note | Version |
|---|---|
| 20 | 2026-11-12 16:10 |
| 21 | 2026-11-12 16:28 |
| 22 | 2026-11-12 17:20 |

*Quivers are up to relabelling unless stated otherwise. Labels: **[P]** proven in a cited source; **[I]** derived or measured in this check; **[H]** heuristic.*

---

## 1. Outcome

**No theorem was found false.** These survived re-derivation and independent computation:

- note 20: Lemma 20.1, Propositions 20.2 and 20.3, Theorem 20.4 at every a searched, and Corollary 20.5;
- note 21: every number that was recomputed, the jump certificate of §4.2, and the inversions of §4;
- note 22: Lemmas 22.1, 22.1′, 22.2, 22.3 and 22.6, Proposition 22.4 and Theorem 22.7; the bottoms of all 2,206 new certificates; and every count of §6 and §7. Theorem 22.5 holds once two hypotheses are added (§4.4).

**Results that came out stronger:**

1. **Theorem 20.4 has an independent check.** A search that stores every quiver it reaches, with no skipping of quivers that have two neighbours, gives note 20's counts exactly:
   - without pruning for every a from 2 to 26 and for a = 32 (142,619,202 quivers below H at a = 26, 402,712,351 at a = 32);
   - with forks not expanded for every a from 2 to 32 and for a = 36 and 40 (126,448,965 at a = 32, 390,321,574 at a = 40).

   Every quiver of height ≤ a + 1 met is a relabelling of Q_a, and no fork of height ≤ a + 1 is met. The quivers that note 20 stores are exactly those that do not have two neighbours below H(a), so its bookkeeping is a property of the set, not of the order of the walk.
2. **Note 21 §5.5: Q_a at a = 2 needs exactly 120 mutations inside 2⁴⁰**, not "between 99 and 120". The search without forks finished at 7,800,118 quivers.
3. **Note 21's long routes have been replayed literally.** Q_t and P⁺_t at t = 1,000 (3,998,000,004 mutations) and Q_a at a = 1,000 (8,006,010,012 mutations) reach the relabelled opposite, at exactly H.
4. **Note 22's measured cuts of class 707 reproduce exactly** with independent code: 823, 3,181, 12,383 and 49,157 quivers of V′ at levels 25, 50, 100 and 200.
5. **Note 22's 2,206 new certificates have an independent check**, which note 22 lacked.
   - **Bottoms.** For every one of the 2,206 classes, an exhaustive cut of V′ at level 1,024·b was complete, 13,083,090 quivers in all. Its bottom equals the certified bottom of N in every class.
   - **An independent engine.** On a sample of 150 classes it certified 149, with the same bottoms and no failure of closure in 563,622 steps. The 150th is inconclusive, not a counterexample.
   - **The counts.** Every count of §6 and §7 recomputes: 2,828 open classes, 1,211 open pairs, 900, 406, 28, 783,242 and 785,198.

**What was wrong or incomplete.**

*Note 20:*

- **The claim that no certificate with finitely many polynomial families can exist is not supported** (§1 item 6, §8 obstacle 1, and the follow-ups in note 18). What is measured is that families indexed by the words from the route would grow in number with a. Families parametrised by their state on a cone are not ruled out, and §8's own plan for the spirals uses them (§4.2).
- **x is not a vertex of the class.** Below H(a), and through quivers that are not forks, Q_a reaches 12 labelled copies of itself, and 8 of them move the fifth vertex. The mechanism is the pentagon at a single arrow (§4.1). So "the 4-vertex part" of a member and "a mutation at x in its word" depend on the representative the search kept. This affects the last two columns of §3, the table of §6.3, and the "another route" paragraph of §8.
- **Smaller points.**
  - §1 item 2 omits "and no exit is a fork of height ≤ a + 1".
  - The hypothesis of the backward lines in §4.2 leaves out the last line for odd a.
  - §4.2 uses two denominators, 841,489 and 841,486, without saying so.
  - §5.2's "after the bottom" includes four positions before the bottom step.
  - §6.2 counts the cycle as W_m(0), …, W_m(m), while note 18 counts m + 2 positions.

*Note 21:*

- **§3.2 needs two assumptions it does not state:**
  - the exponent γ of the route length must be bounded below uniformly in n;
  - the planted barrier itself must be of order w^{n−2}; assumption (i) bounds only the maximum F(n, w).

  Assumption (ii) is not needed for the quasi-polynomial bound (§4.3).
- **The sweeps depend on how ties are broken at the last level.** The figures of §3.1 and §6 are the best case for the attacker: ties go to the lowest height first. Other orders give up to 2.5 times the route for P⁺_t and 20.5·a⁵ for Q_a. The conclusions survive.
- **Two route lengths.** §3.1's L is the route that the minimax search finds: Theorem 18.4's route plus 4 mutations for even a ≥ 4, and plus 6 for odd a and for a = 2. §4.3 and §6 use the theorem's route. So "L … which is the published route" is wrong as worded.
- **Cost-table row (c)** gives the component at H, 27,923, as the generic sweep. The minimax sweep is 15,065, so the planter pays 1,524 times the sweep, not 822. The same applies to "≈ generic sweep" in §5.3.
- **"1,010 of 1,506 rows"** counts the rows where the escape equals h *and* the first low quiver popped is Y. The escape equals h in 1,216 rows.
- **"All 90 random rows with a barrier above w^{n−2}/2"** (§1 item 4): these are the rows with walk height h ≥ w^{n−2}/2. In 11 of them (w = 3) the generic escape is lower, at 4 to 9.
- **Smaller points.**
  - "120 operations" at a = 2⁶⁴ counts walk operations; the compressed route has 77.
  - "To within 1 %" holds at b = 200 and t = 14 only.
  - The rate of walk heights ≥ w³ does not fall with w.
  - At w = 6 the designed Q_5 is also at 2.02·w³.
  - Nine of the 54 routes not replayed are R_b.
  - The A3 component at a = 12 closes at 35,666,621.

*Note 22:*

- **Theorem 22.5 needs two hypotheses** (§4.4):
  - item 1 uses note 14's three-point criterion, which needs the recurrence (x − 1)(x² − τx + 1) with τ ≥ 2;
  - item 2's "replace M by M²" does not cover monodromies of finite order.

  Every tube of the census has τ ≥ 2, so no result of note 22 is affected.
- **The signed form of the Markov constant** in §2, b₁₂² + b₂₃² + b₃₁² − b₁₂b₂₃b₃₁, is not invariant. It goes from 2 to 4 under one mutation of a path. The weight form is invariant and is what the code uses, so no number changes.
- **650,334 is not the number of tubes.** The script counts single families that lie on no cycle as tubes, because its test for them ends in `pass`. About 645,600 are tubes, an estimate from a sample. The last row of the table of tubes should be the 214 one-family tubes, all (2, m, m), and "in 4,941 tubes" should read 214.
- **The rows "j = 1"** of the table of §3 are mostly triangles with C = 4, where τ = 2 for every j, so j has no meaning there.
- **One point settled, nothing to correct.** The mirror of a certificate is a certificate, so one certified class would settle its mirror pair. No open pair has exactly one class certified, so 1,211 stands.

All fixes are in place as quoted "Correction (note 23)" notes (§5).

---

## 2. How the check was done

The check was made separately from the notes it checks, starting from their statements, with new code, by fresh instances of the same AI model that wrote the notes. It is an independent derivation and test, not a specialist's reading.

**By hand, and with three short scripts:**
- every lemma, proposition and theorem of the three notes that is not a computation was re-derived by hand;
- the lemmas of note 22 were tested with new code, and these were recomputed: Theorem 22.7, the cuts of class 707 and the main tube of class 108970 (`review23_lead_n22.py`);
- note 21's masking results were recomputed from the stored climbs (`review23_lead_n21_mask.py`);
- the findings below that this note relies on were checked against the stored files and, for the moving vertex x, with a separate search (`review23_lead_n20_xmove.py`).

**With separate code for each note:**
- **Note 20.** A search in C on labelled 5 × 5 matrices with no canonical form, and the same search up to relabelling with its own canonical form, validated against the labelled one wherever both ran. Also the route of Theorem 18.4, the lines, the spiral, the region table and the 4-vertex searches of §6, in Python.
- **Note 21.**
  - A minimax search, a component search and a bidirectional breadth-first search in C, with several tie-breaking orders.
  - Its own planter, and a literal replay of every route the attacker returned.
  - The attacker itself was called as a black box.
- **Note 22.**
  - A library of its own, checked against the stored cut sizes at 32b and 128b in 300 of 300 sampled classes.
  - Note 14's certificates are not stored with their families. 5,353 of them were regenerated by calling note 14's engine as a black box, and the families it printed were then analysed with the check's code.
  - Note 22's own certificates are not stored either, only a summary line per class. They were checked through exhaustive cuts for all 2,206 classes, and through certificates built by an engine written for the check for 150 of them.
  - The counts were recomputed from the stored summaries.

The fork test is written in every script from Warkentin's Definition 2.1, as quoted in note 14 §3 and read for note 19. Pre-forks are written from Ervin's Definition 4.5, as quoted in note 14 §3.

---

## 3. Claims checked

### 3.1 Note 20

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Lemma 20.1 | 20 §4.1 | Confirmed | By hand: the mutation at e changes b_pq to −2 + A_e·\|B_e\|, or b_qp to 2 + \|A_e\|·B_e. 200,000 random quivers on 3 to 6 vertices (`review23_n20_checks_all.log`) |
| Proposition 20.2, the closed forms of both lines | 20 §4.2 | Confirmed | By hand: the first backward step adds m + 1 to b_rs and A − 1 to b_xs. Of the forward steps, the first takes r to (−1, 0), and the second adds m + 1 and A − 1. Then every column moves along its progression. By mutation: the route of Theorem 18.4 rebuilt for a = 2 to 20, with no mismatch at any turn, and every k of every line checked (`review23_n20_lines_a2_14.log`, `_a15_20.log`) |
| Proposition 20.2(3), not forks | 20 §4.2 | Confirmed | Re-derived from consequence (a) of note 14 §3: two oriented triangles whose largest sides are opposite different vertices. Own fork test: no fork in the closed-form ranges |
| The line lengths A + 3 and A + 4, and the exception | 20 §4.2 | Confirmed for 4 ≤ a ≤ 20 | The last backward line is 4 quivers shorter (odd a) or 5 (even a). Each other line ends at a fork |
| The hypothesis "1 ≤ t with 2(t − 1) < c" | 20 §4.2 | Too narrow | For odd a it leaves out the last line, t = c/2 + 1, whose turn starts with U = +2. The state formula and the closed forms hold there too. It should read 1 ≤ t ≤ T |
| 841,486 quivers on 259 backward lines, 6,463 on 23 forward lines (a = 12), and the two formulas | 20 §4.2 | Confirmed, 4 ≤ a ≤ 20 | 2aT + m·T(T − 1)/2 = 841,491 at a = 12, less 5. (2a − 1)(2a² − a + 5) = 23 · 281 |
| Exits: 840,789 of 841,489; Lemma 20.1 alone settles 798,721 of 841,486 | 20 §4.2 | Confirmed | 841,489 includes the backward line of the bottom round, which has 3 quivers; 841,486 is the 259 lines of the proposition (`review23_n20_exits.log`) |
| Proposition 20.3, the table of ten mutations | 20 §6.1 | Confirmed | All ten rows re-derived by hand. 20,000 random triples in the cone (200,000 mutations): every b_rk > 0, and every triangle has a pair with fewer than two arrows |
| The matrix, and (t − 1)(t² − 47t + 1) | 20 §6.1 | Confirmed | Trace 48, sum of principal minors 48, determinant 1 |
| Statement (3), β′ ≥ 23.5β | 20 §6.1 | Confirmed, sharp | Inequalities re-derived. The four rays of the cone give β′/β = 76, 34, 65.5 and 23.5, the last on (β, β, β/2) |
| The spiral on five vertices | 20 §6.1 | Confirmed | Four rounds from the route at position 0, a = 2, 3, 6, 12: no fork, heights ×47 per round, classes pairwise distinct |
| Runs of five: d₁, d₂ and the recurrence | 20 §6.1 | Confirmed | 7 runs at a = 6 and at a = 96. The first step of each run has a smaller increment (24 against 29 at a = 6), so d is constant from the second step |
| Theorem 20.4 | 20 §7 | Confirmed where searched | §1 item 1 of this note (`review23_n20_search_*.log`) |
| Corollary 20.5 and the table of §7 | 20 §7 | Confirmed | H(w − 1) − (4w³ − 15w² + 19w − 11) = (3w + 2)/2 for even w and (w + 1)/2 for odd w. H(64) = 1,036,382 = 3.774·w³ = 30.43·w^{5/2} |
| §3: core = route + lines + others; the percentages | 20 §3 | Confirmed from the table | 98.23 % and 99.09 % at a = 12 and 16; 3.47, 3.58, 3.77 and 3.88·a⁵ |
| §3: the last two columns ("4-vertex part is a fork", "mutation at x") | 20 §3 | Depend on the representative | §4.1 |
| §5.2, the region table | 20 §5.2 | Confirmed exactly | At a = 8, 12, 16 and 24. The rows include positions 0 to 3 of the round of the bottom, before the bottom step: strictly after it there are 1,958 at a = 8, not 1,962 |
| §6.2, the 4-vertex counts | 20 §6.2 | Confirmed with a convention | All of a = 6, and the column "cap H" for a = 12 to 96, match when "the cycle" is W_m(0), …, W_m(m). With note 18's m + 2 quivers W_m(0), …, W_m(m + 1), every count is one less |
| §6.3, the 4-vertex parts of the core | 20 §6.3 | Not reproducible as stated | With the first breadth-first representative grown from the route: 59 parts and 804 members over them at a = 6 (note 20: 66 and 811), 65 and 1,353 at a = 8 (70 and 1,358). The rows "among the first row" and "largest distance" agree. §4.1 |
| §1 item 6 and §8 obstacle 1: no certificate with finitely many polynomial families | 20 §1, §8 | Not supported | §4.2 |

### 3.2 Note 21

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| The components below H, with and without pruning, and the A3 components | 21 §3.1 | Confirmed | 209, 806, 2,961, 95,260 and 2,995,196 below H, without pruning, for R_20, Q_6, P⁺_8 and Q_a at a = 6 and 12. With pruning: 25, 416, 2,005, 26,683 and 870,583. A3 components: 996, 3,132 and 365,323. The 870,583 is note 20's 864,408 members plus 6,175 forks (`review23_n21_generic_small.log`, `_large.log`) |
| The sweeps of §3.1 and their ratios to L | 21 §3.1 | Confirmed as the best case | Reproduced when ties at the last level go to the lowest height first, within 2 for Q_a. Other orders (first in, first out; last in, first out; three random orders) give more, up to the whole component at H. See the table below |
| L, "the published route" | 21 §3.1 | Mislabelled | The minimax route is Theorem 18.4's route plus 4 (even a ≥ 4) or plus 6 (odd a, and a = 2), in every row of `owf_barrier_generic.jsonl`. §4.3 and §6 use the theorem's route |
| "> 9.9·10⁶ (budget)" for the A3 level at a = 12 | 21 §3.1 | Settled | 35,666,621, a closed search |
| "With fork pruning the sweep of R_b and Q_t is the route itself to within 1 %" | 21 §3.1 | Only at the largest parameters | 0.5 % at b = 200 and 0.4 % at t = 14; 7 % at b = 20 and 2.4 % at t = 6 |
| §3.2, the algebra | 21 §3.2 | Confirmed, under more assumptions | §4.3 |
| §5.5, the fewest mutations | 21 §5.5 | Confirmed; one cell settled | 22, 37, 94, 28, 94 and 312 at H, 4H, 16H, 256H, 2²⁰ and 2⁴⁰. Q_a at a = 2 and bound 2⁴⁰: 120 (7,800,118 quivers, forks skipped). P⁺_2 over all quivers at 2⁴⁰: 28, from 3,505,268 quivers. Where both searches finished they agree (`review23_n21_shortest_a.log`, `_qa.log`) |
| §5.5, skipping forks is exact | 21 §5.5 | Confirmed | "Reduced" in note 15 §2 means no two consecutive mutations at one vertex. A shortest route has none, and Lemma 15.5 holds on any number of vertices (note 19 §4) |
| The structure-aware attacker inverts every instance | 21 §4.3 | Confirmed on a fresh sample | 53 new random relabellings of the four families, including the bound 10⁶·H and a = 2⁶⁴, all inverted. Every route of at most 3·10⁶ mutations (36) was replayed literally, to the relabelled Q′ at exactly H, and so were the three of §1 item 3 of this note. 20 rows of the check's own planter: all inverted at depth 0 and verified (`review23_n21_attack.log`, `_attackrows.log`, `_longreplay.log`) |
| The jump certificate of §4.2 | 21 §4.2 | Sound | Run lengths inside a period are the recorded constants. A period whose run length would vary with k fails a stop-event requirement and is not jumped, so the domain of (position, k) is a rectangle. A product of two growing entries is refused. Every intermediate quiver is height-checked. Only Q_a routes use jumps: four per route |
| "The other 54 … agree with the closed forms (2a + 2)(4a² − a + 6) … and 4t³ − 2t² + 4" | 21 §4.3 | Incomplete | 9 of the 54 are R_b, whose length is b(b − 1)/2 + b + 1 for even b |
| §4.4, masking by a climb | 21 §4.4 | Confirmed | From the stored climbs, with own fork test and descents: 192 of 198 climbs end at a fork, fork descent alone returns to −Q in 112, and fork descent with steepest descent on total weight returns to −Q in all 198. The largest climb reaches 10^{98,041.7} (`review23_lead_n21_mask.log`) |
| §5.1, the table and the rates | 21 §5.1, §1 item 3 | Confirmed, with four fixes | Every count recomputes from the files. The check's own planter gives the same planted set on all 17,500 stored draws (1,506; 28; 22; 0; 0), and the same rates on 3,000 fresh draws per w (\|z\| ≤ 1.3). Own generic search: the same escape level on all 1,556 planted rows of n = 5 and 6 (`review23_n21_rows.log`, `_rows_escape.log`). Fixes: §4.5 |
| §5.2, perturbations | 21 §5.2 | Confirmed | 288, 271, 7, 10 and 17 recount. (−5, −6, 5, −2, 4, −6) rerun: escape 52, sweep 148, route 83, and 83 is also the fewest mutations at bound 52 (`review23_n21_perturb.log`) |
| §5.3, random walks | 21 §5.3 | Confirmed; one label | All 20 ratios recompute. Own walks, 100 trials: R_8 5,069 (note 21: 5,216), P⁺_2 12,739 (13,328), Q_a at a = 2 178,995 (197,041). "Component (≈ generic sweep)": for Q_a the component at H is about twice the sweep (27,923 against 15,065 at a = 4) |
| §6, the cost table | 21 §6 | Confirmed, three labels | Every closed form and power of 2 checks (2^{129}, 2^{127}, 2^{257}, 2^{194}, 2^{194.6}, 2^{321}, 2^{195}, 2^{323.6}; 88,320; 41,171). Row Q_a, a = 12: 14,820 is the theorem's route, not §3.1's L. Row (c): 27,923 is the component; the sweep is 15,065 |
| §1 item 2, "120 operations" at a = 2⁶⁴ | 21 §1 | Two quantities | 120, 113 and 113 walk operations in the three trials; the compressed route has 77 operations in all three |

The sweeps by tie-breaking (quivers popped until the first other quiver of height ≤ w), against the whole component at bound H:

| Member | Sweep in note 21 | Range over six orders | Component at H |
|---|---|---|---|
| R_20 | 410 | 410–574 | 608 |
| R_200 | 40,100 | 40,100–40,396 | 60,098 |
| Q_t, t = 6 | 1,206 | 1,206–1,607 | 1,618 |
| Q_t, t = 14 | 15,905 | 15,905–21,202 | 21,224 |
| P⁺_t, t = 8 | 3,924 | 3,924–4,006 | 5,924 |
| P⁺_t, t = 64 | 2,081,732 | 2,081,732–2,602,436 | 3,123,076 |
| Q_a, a = 6 | 99,300 | 99,302–156,554 | 192,459 |
| Q_a, a = 12 | 3,024,718 | 3,024,719–5,093,974 | 6,004,807 |
| Q_a, a = 12, forks pruned | 884,907 | 884,908–1,751,552 | 1,754,405 |

At the largest parameters the ratio to the route is 2.00–2.01 for R_b, 1.50–2.00 for Q_t and 2.00–2.50 for P⁺_t, and the sweep of Q_a at a = 12 is 12.2·a⁵ to 20.5·a⁵ (the component is 24.1·a⁵). The conclusions of note 21, a constant factor for three families and about the 5/3 power for Q_a, do not depend on the order.

### 3.3 Note 22

**The lemmas and Theorem 22.7** (`review23_lead_n22_lemmas.log`, `_markov.log`, `_side.log`):

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Lemma 22.1 | 22 §4.1 | Confirmed | Proof re-derived. 20,000 random quivers with (D1)–(D3): (X, g) is never an exit and (μ_g X, g) always is. It is a fork in all 16,029 cases with \|b_kk′\| ≥ 2, and a pre-fork that is not a fork in all 3,971 with \|b_kk′\| ≤ 1 |
| Lemma 22.1′ | 22 §5 | Confirmed | Proof re-derived. 20,000 random quivers with an entry \|v_i\| ≤ 1: (μ_g X, g) is never an exit |
| Lemma 22.2 | 22 §4.2 | Confirmed | 20,000 random steps |
| Lemma 22.3(1) | 22 §4.3 | Confirmed | \|Pf\| = \|⟨v, κ(T)⟩\| in 20,000 random quivers. The sign is fixed: Pf(μ_k B) = −Pf(B) in all of them, and a relabelling multiplies Pf by its sign, so η = (−1)^p·sign(π) does not depend on v |
| Lemma 22.3(2) | 22 §4.3 | Confirmed | det(xE + Eᵀ) expanded by hand. 2,000 random acyclic triangles with weights ≤ 12: three sink steps return T and give (x + 1)(x² − (C − 2)x + 1). With an isolated vertex the sink is not unique, and each vertex must be mutated once |
| Proposition 22.4 | 22 §4.4 | Confirmed | Proof re-derived. Among the oriented triangles with weights in [2, 200] and C ≤ 4, the 199 with two flat steps are all (2, m, m), and only (2, 2, 2) has three |
| Theorem 22.5 | 22 §4.5 | Confirmed with two hypotheses | §4.4 |
| Lemma 22.6 | 22 §5.1 | Confirmed | Proof re-derived. 60,000 random quivers with a Markov triangle: (μ_k X, k) is never an exit |
| Theorem 22.7(1) | 22 §5.1 | Confirmed | X₀ has three pairs with fewer than two arrows; a far region allows one (note 14 §3 (b)) |
| Theorem 22.7(2) | 22 §5.1 | Confirmed | The moves of the proof replayed with real mutations: v(z, n) for 2 ≤ z ≤ 40 and 0 ≤ n ≤ 40 reached by 1,638 mutations, every one allowed. The 1,599 quivers are pairwise non-isomorphic, and the level is (z − 1)(n + 1) for z ≥ 3, n ≥ 1 |
| Theorem 22.7(3) | 22 §5.1 | Confirmed | The count is ≥ L·ln L − 3L at every L tried (5,070 against 3,908 at L = 1,000). The bound 6L + 9 on a family re-derived: weight strictly increasing from n = 1 (note 14's families) or n = 7 (polynomial ones) |
| The cuts of V′(X₀) | 22 §5.1 | Confirmed exactly | 823, 3,181, 12,383 and 49,157 quivers at levels 25, 50, 100 and 200 (782, 3,118, 12,294 and 49,030 with a Markov triangle). On every Markov quiver of the cut at 50, \|v₁ + v₂ + v₃\| = 1, which is Pf = ±2 |
| The parity remark | 22 §5.1 | Confirmed | The column (−1, 1, 1) is not in the cut at level 50 |
| Class 108970: the main tube | 22 §5.2 | Confirmed, k ≤ 11 | Y_k → Y_{k+1} is one allowed mutation at vertex 0 for k = 0 to 11. Y_0 lies in V′(x): the cut at level 3,000 has 95 quivers and contains it. x has two pairs with fewer than two arrows |
| Class 108970: the side tubes | 22 §5.2 | Confirmed, k ≤ 3 | From Y_0 to Y_3, 12 allowed steps at the vertices 0, 1, 2 keep the triangle (0, 1, a) or (1, a, a), and the entries at vertex 3 grow by a factor a at each step that is not flat |

**Tube shapes, certificates and counts** (`review23_n22_*.log`):

| Claim | Where (note §) | Verdict | Evidence |
|---|---|---|---|
| Every family has one growing vertex and a constant triangle; four types; no Markov triangle | 22 §3 | Confirmed on a sample | 5,353 certificates regenerated: 5,000 random, plus those with the largest τ, the most families and the largest L, and the 6 extremes. All certified again with the same bottom and the same number of families, 181,985 families in all, every one with one growing vertex and a constant triangle (`review23_n22_shapes.log`) |
| The shares by type, and the largest C | 22 §3 | Confirmed in proportion | Shares of families 55.65, 41.98, 1.58 and 0.79 % (note 22: 56.17, 41.66, 1.45, 0.72). The largest C, 26,025,304 and 25,922, reproduce, and C = 4 for every (2, m, m) family |
| τ = λʲ + λ⁻ʲ with λ + 1/λ = C − 2 | 22 §3 | Confirmed; the rows "j = 1" mislabelled | Every τ is such a value. j = 2 in 99.57 % of the (1, 1, a) group and 99.80 % of the (0, 1, a) group. Most families counted as "j = 1" have C = 4, where τ = 2 for every j: 254 of 318 for (1, 1, a), and 72 of 112 for (0, 0, a) |
| (D1)–(D3) at every growing-vertex step | 22 §3 | Confirmed | From n = 0 in 181,932 families and from n = 1 in 53 (0.029 %; note 22: 0.028 %). The step at g is a strict up-exit for every n ≤ 8 in all of them |
| 650,334 tubes; the table of tubes; "in 4,941 tubes" | 22 §3 | Overcounted | `shapes` counts single families on no cycle as tubes (the test for them ends in `pass`). Rebuilt to note 22's definition: 2.875 components per class against 2.888, and the main rows agree to about one point. Of the 131 components in the last row, 123 are single families on no cycle, all (1, 1, a) and (0, 1, a); 8 are one-family tubes, all (2, m, m). About 645,600 tubes (`review23_n22_tubes2.log`) |
| The Markov constant, signed form | 22 §2 | Wrong | Not invariant in 24,035 of 60,000 random mutations; the weight form in 0 (`review23_n22_markovC.log`) |
| The bottoms of the 2,206 new certificates | 22 §6.2 | Confirmed, all 2,206 | Cut of V′(x) at level 1,024·b, complete in every class (13,083,090 quivers). Least level, bottom and the mirror bottom equal the stored ones in 2,206 of 2,206. x lies in N in every class. Every cut has more than 77 quivers, so none of these classes has a finite core (`review23_n22_bottoms.log`) |
| Closure of the certificates | 22 §6.2 | Confirmed on 149 of 150 | Own engine (periodic walks, derived families, a finite E; closure checked for members up to n = 10). Sample: class 1034; 8 classes each for the most families, the most polynomial families, the largest E, the largest L and a bottom above the census bottom; 6 slow classes; 103 random. 149 certified with the same bottom, 563,622 closure steps, 0 failures. Class 500677 was not certified at any size of E from 2,000 to 10⁶: inconclusive, and its bottom is confirmed by the cut (`review23_n22_engine*.log`) |
| Class 1034 | 22 §6.2 | Confirmed | 14 families, bottom (3, 0, −3, 0, 2, 2), self-mirror. The corridor quivers lie in V′, the step at vertex 0 is allowed for every N checked from 4 to 100, and at N = 20 it gives (−20, 0, 18, −3, −358, −3) (`review23_n22_c1034.log`) |
| The tables of §6.1, §6.2 and §6.3; 2,828; 1,211; 900; 406; 28; 783,242; 785,198 | 22 §6, §7 | Confirmed | Recomputed from the stored summaries. The mirror map rebuilt from the plateaus gives 33,124 self-mirror classes and 377,451 pairs (`review23_n22_counts.log`) |
| No new bottom equals another certified bottom | 22 §6.2 | Confirmed | The 227,414 tube certificates have 227,414 distinct bottoms, and no new one equals the mirror bottom of a class other than its census mirror |
| Mirror pairs with one class certified | 22 §6.3 | None | All 1,800 new certificates in census pairs have their mirror class certified too, and none has a bottom equal to its own mirror. All 406 self-mirror ones do |
| The disconnected classes and the rank-3 rule | 22 §6.1 | Confirmed | All 400 are a triangle and an isolated vertex; the case of two components on two vertices does not occur. 292 descend to an acyclic quiver. For the 108 with a cyclic root, the rule "two equal weights or a flat step" agrees in 108 of 108 with a direct closure under flat steps (Theorem 3.1): 52 self-mirror, 56 in pairs (`review23_n22_rank3.log`) |
| The 1,556 acyclic-bottom classes contain an acyclic quiver | 22 §6.1 | Confirmed | In 1,300 the bottom quiver itself; in 256 another quiver at the bottom level |
| The side-tube signature | 22 §6.2 | Consistent with the files | The largest τ of a certificate of note 14 is 677,316,344,191,202 (15 digits). `n4_tube_sidesig.log` has no τ between 11 and 24 digits, and 2,287 = 2,245 + 42 between 25 and 36. These τ were not recomputed |

---

## 4. Notes

### 4.1 The fifth vertex of Q_a is not a vertex of the class [I]

A labelled breadth-first search from Q_a, through quivers that are not forks and have height < H(a), reaches 12 labelled copies of Q_a. At a = 2 and 4 it reaches all 120. Q_a has no automorphism other than the identity. Eight of the 12 copies move vertex 0, which is x:

| a | Copy reached | Shortest word | Its height | H(a) |
|---|---|---|---|---|
| 3 | x ↔ r | 5 mutations, 0 2 0 2 0 | 26 | 88 |
| 3 | x ↔ r | 7 mutations | 20 | 88 |
| 5 | x ↔ r | 31 mutations | 234 | 437 |
| 6 | x ↔ q | 39 mutations | 407 | 763 |
| 6 | x ↔ q | 335 mutations | 398 | 763 |

The mechanism is the pentagon. If two vertices i and j are joined by one arrow, then μ_i μ_j μ_i μ_j μ_i(B) is B with i and j exchanged [I: tested on 20,000 random quivers on 3 to 7 vertices; it is the period-5 exchange relation of rank-2 type A₂ in Fomin and Zelevinsky's *Cluster algebras II*, recalled, not re-read here]. At a = 3 the quiver Q_3 itself has one arrow between x and r (U = a − 2 = 1), and the word 0 2 0 2 0 is that pentagon. At a = 6 the word is a walk of steps on the pair (p, q) with one turn, then the pentagon 0 1 0 1 0 on x and q, then the same walk with x in the place of q (`review23_lead_n20_xmove.log`, `review23_n20_xmove.log`).

**What this changes.**
- **Theorem 20.4 is not affected.** It counts quivers up to relabelling and compares the low ones with Q_a up to relabelling.
- **Everything that names x in a member of K(a) depends on the labelled representative the search keeps.** This covers "the 4-vertex part", "a mutation at x in the word" and the kinds with x. The words are those of the search, as note 20 §9 says of the kinds. The vertex x is not a vertex of the class, so the last two columns of note 20 §3 and the table of §6.3 describe the search, not K(a). An independent search that keeps the first breadth-first representative finds 59 4-vertex parts at a = 6 where note 20 has 66.
- **§8's "another route to a proof".** "Routes that never mutate x" must be read in a fixed labelling. The explicit list of exceptions would have to contain every member below H(a) in which x is joined to another vertex by one arrow, since the pentagon there exchanges x with that vertex.

### 4.2 What blocks a certificate for Q_a [I, H]

Note 20 proves that the spirals exist for every a (Proposition 20.3), and measures that the core follows them, up to 15 mutations from the cycle at a = 48. That is about one and a half rounds of ten. From this, §1 item 6 concludes, labelled [I], that a certificate with finitely many polynomial families "cannot cover the core for all a". §8 obstacle 1 concludes that "no finite list of families with polynomial entries describes K(a) for all a, nor a closed set that contains it".

This does not follow, for two reasons.
- **The premise is measured.** The depth of the spirals in K(a) is measured only for a ≤ 48, as §8 itself says ([H]) and §9 repeats ("measured, not proved").
- **Even granting the premise, it rules out only families indexed by the words from the route.** Those families have entries polynomial in a and in the run lengths.
  - A family can instead take as free variables the entries (α, β, γ) of r, with the row of x, on a cone. Its entries are linear in those variables.
  - The round of ten mutations maps such a family to itself by the matrix of Proposition 20.3(2).
  - §8's own plan for the spirals is an induction of exactly this kind. A closed set that contains K(a) may also contain the whole spiral, including its quivers above H(a).

What can be said is this [H]. Families indexed by the words from the route would have to grow in number with a: measured for a ≤ 48, while the spirals exist for every a. The spirals need families parametrised by their state, with an induction along the map of a round. Whether finitely many such families close was not examined. The same holds for the follow-ups in note 18.

### 4.3 What note 21 §3.2 needs [I]

The algebra of §3.2 is right. A3 at the barrier sweeps F^{e(n)} ≈ w^{(n−2)(n−3)}, and (n − 2)(n − 3)/C(n, 2) = 2(1 − O(1/n)). With T ≥ H^γ the sweep is T^{e(n)/γ}. With e(n) ≤ n − 2 and n ≤ 2 + log₂T/γ it is at most T^{(log₂T)/γ²}. Three conditions are used without being stated:

1. **γ must be bounded below uniformly in n.** If γ(n) → 0, for example like 1/n, then T ≥ 2^{γ(n−2)} no longer bounds n, and the bound fails. Assumption (iii) is measured on four families whose routes are linear counters, with γ = 1, 3/4 and 3/5. Note 20's spirals show that entries can also grow geometrically along a route, so (iii) is a genuine assumption about the routes over barriers, not a general fact.
2. **The planted barrier must be of order w^{n−2}.** Assumption (i) bounds F(n, w), the maximum over all quivers of height ≤ w. The argument uses H ≈ F, so n = O(log H). A planter with H much smaller than w^{n−2} on many vertices is not covered: under (ii) its sweep would be about H^{n−3}, exponential in n, while T stays polynomial in H.
3. **(ii) is not needed for the upper bound.** The trivial e(n) ≤ C(n, 2) gives T^{O((log T)²)} = 2^{O((log T)³)}, which is still quasi-polynomial. (ii) is needed only for "exponential in s".

The fit e(n) ≈ n − 3 matches note 2's 1.14 and 1.88 but not 2.26 at n = 6, which is 25 % below 3. The label [H] is right. "Under (i) to (iii) that is impossible" should add conditions 1 and 2, and so should "never exponential" in §1 item 1.

### 4.4 Theorem 22.5: two hypotheses [I]

- **Item 1** certifies the sign of each mutated entry by note 14's criterion: the right sign at n = 0, with non-decreasing absolute value and non-decreasing absolute differences, checked at n = 0, 1, 2.
  - Three points suffice only for a sequence that satisfies e(n + 3) = (τ + 1)e(n + 2) − (τ + 1)e(n + 1) + e(n) with τ ≥ 2. Then the differences satisfy d(n + 2) − d(n + 1) = (τ − 2)·d(n + 1) + (d(n + 1) − d(n)), and induction applies.
  - The proof says instead that the sequence "satisfies the recurrence of M, by Cayley–Hamilton". By Lemma 22.3, M has characteristic polynomial (x − η)(x² − tx + η·det M). That is note 14's recurrence only if η = 1 and det M = 1. For a Coxeter period with π = id, η = −1 (Lemma 22.3(2)).
  - So item 1 needs the hypothesis that M has characteristic polynomial (x − 1)(x² − τx + 1) with τ ≥ 2, for example M replaced by M² as note 14 does. With τ < 2, d = 0, 1, 1, 0, −1 passes the check at n = 0, 1, 2 for τ = 1 and then falls.
- **Item 2** says "replace M by M² if needed. Then ℓ(v_n) + c = Aλⁿ + Bλ⁻ⁿ + C₀ with λ > 1, or a polynomial."
  - This misses τ ∈ {−2, −1, 0, 1}. There M² has eigenvalues on the unit circle and finite order. An example is T = (0, 1, 1), the path A₃: C = 2, and M has eigenvalues −1 and ±i.
  - Then ℓ(v_n) is periodic: neither constant nor eventually monotone. The fix is to replace M by a power M^k with k dividing 12, after which the family is constant or polynomial.
  - Such a periodic orbit is finite, so a certificate puts it in E, and nothing is lost.

Every tube found in the census has τ ≥ 2 (§3 of note 22), so no result of note 22 depends on either point.

### 4.5 Note 21 §5.1: four fixes [I]

- **"Where the generic escape equals h (1,010 of 1,506 rows)."** The escape equals h in 1,216 rows. 1,010 is the number of those in which the first quiver of height ≤ w that the search pops, other than Q, is Y. That depends on tie-breaking: the check's search gives 1,096. The exponent 1.65 is a fit over the 47 rows with h ≥ 50. Over all 1,216 rows the slope is 1.88.
- **"Every one of the 90 rows with h ≥ w³/2 plants the opposite."** True: Y ≅ −Q in 90 of 90. But §1 item 4 calls them "random rows with a barrier above w^{n−2}/2". In 11 of them, all at w = 3, the generic search escapes lower, at 4, 8 or 9, so their barrier is below w³/2.
- **"A walk height ≥ w³ in 0.13 to 0.40 % of draws, falling with w."** The rates are 0.30, 0.30, 0.40 and 0.13 % for w = 3 to 6. They do not fall monotonically.
- **"The largest are 2w³ at w = 6, against 4w³ for the designed Q_a."** At w = 6 the designed Q_5 has H = 437 = 2.02·w³, and one of the check's fresh draws planted a barrier of exactly 437. 4w³ is the limit of H(a)/w³ as a grows.

### 4.6 Note 22 §7: what is decided at n = 4 [I, H]

The statement of §7 is right as written. Equivalence is decided when one quiver is mutation-acyclic, when one is disconnected, and when both classes have a finite core or a tube certificate. It is not a decision procedure, because class 707 has no certificate of this form (Theorem 22.7). Two remarks.

- **The census numbers stand.** 785,198 classes are covered and 2,828 are not. No open mirror pair is settled by the mirror of a single certificate (§3.3).
- **One certificate may be enough [H].** A certificate gives all of N for its class: E and the families together are N, since every quiver in them is reached by allowed steps from a quiver in no far region. Membership in E or in a family is decidable, because the entries of a family are monotone. So equivalence with a certified class A is decided for any quiver B from which a quiver of B's class in no far region can be computed. Fork descent does this inside a fork region. Whether the descent through Ervin's pre-fork regions (tips, wings) is effective was not checked. If it is, the exception in §7 narrows to pairs in which *neither* class has a certificate.

---

## 5. Corrections made in place

- **Note 20.**
  - A note under the title.
  - §1 item 2: the condition on forks.
  - §1 item 6: the certificate claim.
  - §3: the vertex x.
  - §4.2: the range of t, and the two denominators.
  - §5.2: "after the bottom".
  - §6.2: the convention for the cycle.
  - §6.3: the representative.
  - §8: obstacle 1, and "another route to a proof".
- **Note 18.** The two follow-ups of note 20, in §5.2 and §9.
- **Note 21.**
  - A note under the title.
  - §1 items 1, 2 and 4.
  - §3.1: L, the tie-breaking, the budget cell, and "1 %".
  - §3.2: the conditions.
  - §4.3: the routes not replayed.
  - §5.1: the four fixes of §4.5.
  - §5.3: the component and the sweep.
  - §5.5: the cell for Q_a at a = 2.
  - §6: rows Q_a (a = 12) and (c).
- **Note 22.**
  - A note under the title.
  - §1 item 1: the number of tubes.
  - §1 item 2: Theorem 22.5.
  - §2: the signed Markov constant.
  - §3: the rows "j = 1", the table of tubes, and "in 4,941 tubes".
  - §4.5: the two hypotheses of Theorem 22.5.
  - §6.2: the independent check.
  - §8: the polynomial engine.

---

## 6. Still unchecked

- **Note 20.**
  - Theorem 20.4 without pruning for 33 ≤ a ≤ 48, and with forks not expanded for a = 33 to 35, 37 to 39 and 41 to 64. These rest on note 20's search alone, which agrees with the independent one wherever both ran.
  - The kinds of §5.1 and `np_qa_core_kinds.log`.
  - The pre-fork count of §8 (36 and 110 members).
- **Note 21.**
  - The attacker's results at b, t, a = 10⁶ and 2⁶⁴. They rest on the certificate of §4.2, found sound, and on the closed forms of the route lengths.
  - The n = 7 and 8 rows beyond the stored draws.
- **Note 22.**
  - The certificates of `certify2` themselves, which are not stored. Their bottoms and the closure of independently built certificates were checked instead.
  - The full re-run of `shapes` on all 225,208 certificates. A sample of 5,353 was regenerated, and the corrected number of tubes is an estimate from it.
  - The τ values of `sidesig`.
  - Class 500677, which the independent engine could not certify.
  - The lamination picture of §5.1, which is heuristic.

---

## 7. Reproduce

```bash
PY=python
$PY -I ../verify/review23_lead_n22.py lemmas > review23_lead_n22_lemmas.log
$PY -I ../verify/review23_lead_n22.py markov 25 50 100 200 > review23_lead_n22_markov.log    # about 1 minute
$PY -I ../verify/review23_lead_n22.py side > review23_lead_n22_side.log
$PY -I ../verify/review23_lead_n21_mask.py > review23_lead_n21_mask.log
$PY -I ../verify/review23_lead_n20_xmove.py > review23_lead_n20_xmove.log                   # about 5 minutes
$PY -I ../verify/review23_lead_n20_xmove.py pentagon >> review23_lead_n20_xmove.log
```

- The extra lines at the end of `review23_lead_n22_markov.log` (the column (−1, 1, 1), the 1,599 classes, the sums of the column) come from a short driver that imports `review23_lead_n22.py`; the log states what each line checks.
- **Note 20.** `review23_n20_search.c` is compiled into `~/.cache/qmb-review23/`. `review23_n20_checks.py`, `review23_n20_runs.py`, `review23_n20_ends.py` and `review23_n20_xmove.py` give their command lines in their headers. The searches up to a = 40 need up to about 14 GB.
- **Note 22.** `review23_n22_lib.py` is the library. The scripts `review23_n22_{selftest,counts,rank3,markovC,regen14,shapes,tubes2,bottoms,c1034,engine,engine_retry,engine_highlam,engine_500677}.py` give their command lines in their headers, and their logs carry the same names. The regenerated note 14 certificates are in `~/.cache/qmb-review23/n14_certs.jsonl.gz`.
- **Note 21.** `review23_n21_review.py` drives `review23_n21_search.c` and gives its subcommands in its header. Its black-box inputs and outputs and the replay programs are in `~/.cache/qmb-review23/n21/`.

---

## Sources

- Notes [20](20-core-of-the-cubic-family.md), [21](21-barriers-and-the-mutation-path-owf.md) and [22](22-tube-lemma-and-its-limits.md), the notes checked here. Notes [14](14-opposite-quivers-forks-and-cores.md) §3 (forks, pre-forks, consequences (a) and (b)) and §8, [15](15-rank-2-orbits-and-the-constant-2.md) §2 and Lemma 15.5, [16](16-five-vertices-above-w-squared.md) §2, [18](18-five-vertices-cubic-barrier.md) (the route and the bounce cycle) and [19](19-checks-of-notes-13-to-16.md) §4 (Warkentin's lemmas on any number of vertices).
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Def. 2.1, as read for note 19: https://d-nb.info/1214302807/34. Ervin, arXiv 2306.07502, Def. 4.5 (pre-forks), as quoted in note 14 §3.
- The pentagon: Fomin and Zelevinsky, *Cluster algebras II*, the exchange relations of rank 2 and type A₂ (period 5 up to the transposition), recalled, not re-read here; tested in `review23_lead_n20_xmove.log`.
