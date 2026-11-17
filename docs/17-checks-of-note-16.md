# 17. Checks of note 16

*Prepared 2026-11-12. [Note 16](16-five-vertices-above-w-squared.md) was written on 2026-11-11 and had not been checked. This note records a separate check of its claims, in the way [note 12](12-checks-of-notes-03-to-10.md) checked notes 3 to 10. Code: [verify/review17.py](../verify/review17.py) (new; it imports none of `np_corridor.py`, `np_corridor_prove.py`, `n4_doors.py`). Results: the `review17_*.log` files. Notation as in note 16: vertices x = 0, p = 1, q = 2, c₁ = 3, c = 4; N = 2t³ − t² − t; H⁺(t) = 2t⁵ − t⁴ + t² − 1; height means maximal entry; quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** derived or measured in this check; **[H]** heuristic.*

---

## 1. Outcome

**No theorem of note 16 was found false, and the certificate of Theorem 16.6 has no gap.**

- **Theorem 16.6 for t ≥ 8: the argument of §4.1 closes.** Each of the 766 exits in `np_corridor_prove.log` was certified again with other code (PARI polynomials, the check's own mutation, the check's own fork test), among them all 54 fork verdicts and all 161 verdicts "member". For each verdict "member" the target was rebuilt from its name at the true parameters and shown to lie where it was made a member. The claims cover every member and every vertex, the members cover every true parameter value, and every member except K(0) has an entry above t² (§4).
- **Theorem 16.5 (t ≤ 64): confirmed for every t, for both families.** The check's own enumerator and canonical form give the same number of quivers below the barrier as `np_corridor_family_plus.jsonl` and `np_corridor_family.jsonl` for all 63 values of t, and one quiver of height ≤ t² in each (§5).
- **Lemmas 16.1 to 16.3, Theorem 16.4 and Corollary 16.7: confirmed by hand**, and on integers for 2 ≤ t ≤ 64 (§6).
- **Lemma 15.5 is valid on any number of vertices.** Its proof in note 15 uses only that all pairs of a fork are joined (§7).
- **The measured statements agree with their logs.** The quivers on 6 and 7 vertices were recomputed (§8).

**Four results came out stronger:**

1. **Theorem 16.5 holds for P⁺_t up to t = 80.** The same search, with no use of forks, was run for 65 ≤ t ≤ 80, where H⁺(t) no longer fits the 32-bit keys of `np_barrier.c`: 36,792,093 more quivers, and one of height ≤ t² for each t.
2. **The star quivers of §5 need no fork pruning.** For all six, a search without pruning finds one quiver of height ≤ w below the height of the route, and a second one at that height. Note 16 had searched with fork pruning.
3. **The constant 11 of Corollary 16.7 is the best one.** The least constant on w = (t + 1)² − 1 tends to 11 from below, and with 10 the inequality fails first at w = 783.
4. **The closure on integers holds for every t from 2 to 80, not only 8 to 11.** The set that P⁺_t reaches below H⁺(t) without entering a fork higher than t² has one quiver of height ≤ t². For ten values of t from 8 to 24 it is exactly the set of instances of the members.

**What was wrong or overstated** (none of it touches a theorem):

- §4.2: at t = 5 the backward line has 230 quivers below H⁺ and there are 35 others, not 231 and 34.
- §6.2: the share of rows over budget goes up to 50 %, not 51 %.
- §1 item 6: "none of the others reaches another quiver of height ≤ 7 below 1,000,000" omits that 1,516 of those searches ran over their budget. §6.3 states it correctly.
- §4.1: the count of 938 certified claims includes one line, "(definitions)", that the script prints as ok without testing anything. There are 937 checks.
- §1 item 2: "a polynomial F(5, w) has degree at least 5/2". A polynomial has an integer degree, so at least 3; what is proved is growth of order at least w^{5/2}.

All fixes are in place as quoted "Correction (note 17)" notes in note 16.

---

## 2. How the check was done

The check was made separately from the note it checks, starting from its statements, with new code, by a fresh instance of the same AI model that wrote note 16. It is an independent derivation and test, not a specialist's reading. Each claim was first re-derived from its statement and then tested with `review17.py`. The script departs from the code being checked on purpose:

- **Mutation.** On upper-triangle tuples, written through [x]₊; a second kernel on matrices is checked against it.
- **Canonical form.** Vertices are ordered by their sorted rows and ties are broken by the least tuple. `np_barrier.c` and `np_corridor.py` take the least tuple over all 120 relabellings.
- **Fork test.** Every pair of a fork is joined, so its orientation is a tournament, and "acyclic" is tested as "no oriented triangle". The code being checked removes sources.
- **Polynomials.** PARI (cypari2). A sign p ≥ 0 on a box is certified as in note 16, by writing the box as an orthant of fresh variables and checking that no coefficient is negative. `selftest` checks this test, the zero test and evaluation on 4,000 random polynomials with known coefficients.
- **The certificate.** `np_corridor_prove.log` is read as an untrusted list of claims. Nothing of `np_corridor_prove.py` runs. Each claim is proved again, and the three statements that make the claims a proof (coverage, membership of every target, every member above t²) are checked by the check's code, not taken from the log (§4.3).

`np_corridor_prove.py` and `np_barrier.c` were also read line by line (§4.1, §5). A rerun of `np_corridor_prove.py prove --T0 8 --audit-tmax 11` is byte-identical to the stored log.

---

## 3. Claims checked

### Theorem 16.6 and its certificate (note 16 §4)

| Claim | Verdict | Evidence |
|---|---|---|
| Theorem 16.6 for t ≥ 8: no route below H⁺(t) from P⁺_t to another quiver of height ≤ t² | Confirmed | §4: 766 of 766 exits certified again, coverage complete, 148 of 148 members above t² (`review17_replay.log`) |
| The logical argument of §4.1 ("Why this proves the theorem") | Closes | §4.3 |
| The closed forms of M1(k) and M2(m), and the 14 single quivers | Confirmed | Re-derived by hand (§4.2); identities I8 to I11 in PARI; integers for t = 3 to 14 (`review17_closedforms.log`, `review17_singles.log`) |
| "The script finds 14 kinds [of derived members], none more than two mutations from a line" | Confirmed | The same 14 kinds come out of the replay |
| "For L(i) the claims are certified for all t, i, r in their domain, which contains the true triples" | Confirmed, with one addition | At i = 2 the backward exit is the formula of L at (1, r + 1). It is the member L(1) only on the true triples, where r + 1 = N. That is enough, and §4.3 says why |
| The ends of the ranges: K(1) to K(0), K(t − 2) to K(t − 1), L(2) to L(1), L(N) to L(N + 1), M1(3) to L(−2), M1(t − 3) to M1(t − 2), M2(0) to L(−t) | Confirmed | §4.3, items (a) to (c) |
| The table of claims: 24 + 161 + 428 + 54 + 123 + 148 = 938, all certified | Confirmed; 937 are checks | One of the 24 identity lines is hard-coded as ok ("definitions"). The rerun reproduces the log byte for byte |
| §4.2 "Closed forms" for t = 5 to 12 | Confirmed | The check's closed forms against integer mutation for t = 3 to 14, L(i) to i = 600, M2(m) to m = 60 |
| §4.2 "Verdicts": 1,928 integer evaluations, none wrong | Confirmed | The log; and 2,298 evaluations of the check's own, three per claim, with the integer kernel |
| §4.2 "The list against the search": 1,985, 2,827, 3,882, 5,174 quivers at t = 8 to 11, none missing, none extra | Confirmed, and extended | `review17_closure.log`, `review17_instances.log`: the same four numbers; the two sets are equal for t = 8 to 14, 16, 20 and 24 |
| §4.2 core of P⁺_t: 120, 125, 263, 492, 840, 1,331, 1,985, 2,827, 3,882 for t = 2 to 10 | Confirmed | `review17_closure.log` |
| §4.2 cores of P_t and of Q_t, and "of which on the route" | Agrees with the logs | `np_corridor_core.log`; not recomputed for P_t. The route counts 14, 47, 114, 227, 398, 639, 962, 1,379, 1,902 were recomputed (`review17_anatomy.log`) |
| §4.2 "At t = 5 … 227 quivers of the route, 231 on the backward line, and 34 others" | Wrong by one | 227 on the route, 230 on the backward line, 35 others: 5 beyond the ends of the first line and 30 on branches. 231 is the size of the branch that starts at L(0) with a backward step; it contains μ_{c₁}L(−1) |

### Theorem 16.5 (note 16 §3.3)

| Claim | Verdict | Evidence |
|---|---|---|
| For 2 ≤ t ≤ 64 the set reached from P⁺_t below H⁺(t) contains no other quiver of height ≤ t² | Confirmed for all 63 values | §5; `review17_plain.log` |
| The same for P_t and H(t) | Confirmed for all 63 values | The same log |
| The row "Quivers reached below H⁺": 157, 173, 381, 726, 1,247, 2,961, 5,803, 23,980, 193,929, 1,561,537 | Confirmed | Equal at all 63 values of t, also the number of mutations that lead above the bound |
| The row "Quivers reached below H": 46, 135, …, 1,301,189 | Confirmed | Equal at all 63 values of t |
| "25.7 million quivers for P⁺_t and 21.4 million for P_t" | Confirmed | 25,717,726 and 21,427,901 |
| "The opposite reached at exactly H" | Confirmed | By the route (Theorem 16.4), checked on integers for t ≤ 64 |
| The rows H⁺(t), H⁺/w², H⁺/w^{5/2}, H(t), H/w^{5/2}, 2w²; the closed forms of H(t) for even and odd t | Confirmed | Recomputed |
| "Products are formed in 64-bit integers … no overflow can occur" | Confirmed | Reading of `np_barrier.c`: factors are at most the cap, which is below 2³¹; a quiver above the cap is discarded before it is stored; keys are compared in full, not by hash |
| `pycheck`, `selftest` | Agree with their logs | Not rerun |

### The hand proofs (note 16 §2, §3.2, §4)

| Claim | Verdict | Evidence |
|---|---|---|
| Lemma 16.1 (step), Lemma 16.2 (turn), Lemma 16.3 (the top), and the corollary of §2 | Confirmed | Re-derived; 20,000 random quivers each on 5 to 7 vertices (`review17_lemmas.log`) |
| Theorem 16.4(1): P⁺_t and −P⁺_t are not isomorphic | Confirmed | p has in-weight 3; the out-weights are t² + 1, 2t² − t, 2t², 2t² − t, 2t, and none of them is 3 for an integer t ≥ 2. On integers for t ≤ 64 |
| Theorem 16.4(2): the table of columns of K(j) and L(i); the route of 4t³ − 2t² + 4 mutations; one quiver of height H⁺(t), all others at most H⁺(t) − t² | Confirmed | Each line of the proof re-derived (§6); identities I1 to I7 for all t ≥ 2 (PARI); integers for t ≤ 64 (`review17_route.log`) |
| Theorem 16.4(3): the same for P_t with H(t) and ⌊t²/2⌋ | Confirmed | By hand; integers for t ≤ 64 |
| "This full subquiver is Q_t of note 15" | Confirmed | Q_t's vertices 0, 1, 2, 3 are c, p, q, c₁ |
| "Mutation-cyclic": Markov constant −2t⁵ + 2t⁴ + 2t³ + 2t² + 1 of the triangle q → c → c₁ → q | Confirmed | (t² − 1)² + (2t)² + t⁴ − 2t³(t² − 1); it is −7 at t = 2 and decreases |
| Corollary 16.7: F(5, w) ≥ H⁺(⌊√w⌋) ≥ 2w^{5/2} − 11w² for w ≥ 4 | Confirmed | §6; in exact integers for 4 ≤ w < 2,000,000 (`review17_corollary.log`) |
| "On 4 ≤ w < 4,225 the least constant is 10.57 … H⁺(⌊√w⌋) > 2w² except at w = 6, 7, 8 and 15" | Confirmed | 10.5647, at w = 4,224; exceptions 6, 7, 8, 15 |
| Lemma 16.8 (scaling a row) | Confirmed | By hand |
| "Lemma 16.1 with one other vertex is Theorem 15.1(1) for c = 2" | Not checked | |

### Lemma 15.5 (note 15 §4)

| Claim | Verdict | Evidence |
|---|---|---|
| Lemma 15.4 (Warkentin's Lemma 2.5, with "no entry is smaller"), for 5 vertices | Confirmed for every n | §7; 20,000 random forks on 5 and on 6 vertices (`review17_forks.log`) |
| Lemma 15.5 (fork exclusion), for 5 vertices | Confirmed for every n | §7; 200,000 random reduced routes on 5 and on 6 vertices |
| The definition of a fork used by `cert_fork` | Agrees with the published one | Ervin, arXiv 2306.07502v2, Definition 2.5, there attributed to Warkentin's Definition 2.1 (according to a fetched reading, §7) |

### Measured statements (note 16 §3.3, §5, §6, §7)

| Claim | Verdict | Evidence |
|---|---|---|
| Pendant quivers on 6 and 7 vertices, t = 2, 3, 4 (P_t with a path hung from x) | Confirmed | Recomputed without pruning: 97, 276, 634 quivers below H on 6 vertices and 250, 699, 1,594 on 7. The quivers of height ≤ w among them are the starting plateau, 2 and 5 quivers; up to H there are 4 and 10 (`review17_pendant.log`). Labelled "measured, not proved" in note 16, which is right |
| The star quivers of §5: heights 140, 236, 1,809, 7,728, 810, 26,568; "lower route found: none" | Confirmed, and stronger | Recomputed without fork pruning: one quiver of height ≤ w below H in each, two up to H (`review17_star.log`). For these six quivers the join is at exactly the height of the route |
| "Free parameters": 4,350 sets, 3,666, 684, 528, 210 and one failure | Agrees with the log | `np_corridor_grid.log`; not recomputed |
| §5, "Why this design stops at 5/2" | Heuristic, as labelled | The count was followed. Items 3 and 4 assume that the centre y turns only at the top; a pure route with an earlier turn at y is not covered. §8 of note 16 already says that §5 is not an upper bound |
| §6.1 census table for w = 2, 3, 4, the records and their routes, the breakdown by entries ±2, the two rechecks | Agrees with the logs | `np_corridor_census_n5_w{2,3}.log`, `…_w4_min4.log`, `…_w4_recheck.log`; not recomputed |
| §6.1 validation on 4 vertices | Agrees with the log | `np_corridor_census_n4.log` |
| §6.2 table of fixed 4-vertex quivers with a fifth row | Agrees with the logs | `np_corridor_rows.log`, `np_corridor_rows_db2_a5.log`: all 11 rows, the routes and the best rows |
| §6.2 "between 4 % and 51 % of the rows run over [the budget]" | Wrong in the last digit | The largest share is 7,332 of 14,641, which is 50 %. The smallest is 289 of 6,561, 4 % |
| §6.3 templates: 84,495; 2,838 with an escape (2,828 by two mutations, 10 by four or five); 81,657 searched again; 80,141 closed, 1,221 without meeting the cap, 1,516 over budget | Agrees with the log | `np_corridor_templates.log` |
| §1 item 6: "none of the others reaches another quiver of height ≤ 7 below 1,000,000" | Overstated | For 1,516 of them the search ran over its budget of 5,000 quivers |
| §7: the ratios 2.5, 4.5, 3.3, 4.9, 5.0 to w^{5/2}; 3.5 to 12.1 to w²; 1.8, 2.6, 1.7, 2.2, 2.0 to w³; the predictions of the test | Confirmed | Recomputed from 14, 70, 107, 272, 437 |
| §1 item 2, §7: "a polynomial F(5, w) has degree at least 5/2" | Wording | A polynomial bound has degree at least 3. What is proved is F(5, w) ≥ 2w^{5/2} − 11w² |

---

## 4. Theorem 16.6: the certificate

### 4.1 Reading of `np_corridor_prove.py`

The script was read in full. Its parts are sound:

- **`nonneg`, `wsign`, `ssign`.** After the shift to the lower bounds, a polynomial with no negative coefficient is ≥ 0 on the domain. `nonneg` refuses a polynomial with a variable that has no bound. `wsign` gives weak signs and `ssign` gives p ≥ 1 or p ≤ −1.
- **`smutate`.** A weak sign is enough for the mutation rule: where an entry at the mutated vertex is zero, both products vanish. The four cases are right.
- **`cert_fork`.** It asks for a strict sign and absolute value ≥ 2 at all ten entries, a quiver that is not acyclic, an entry above t², and a vertex r with acyclic sides such that every in-neighbour i and out-neighbour j of r have an arrow j → i heavier by at least 1 than both i → r and r → j. This is the definition of §7.
- **The domains.** `orthants` covers {j ≥ 1, v ≥ 1, j + v ≥ 7} by six quarter-planes and {k ≥ 3, u ≥ 1, k + u ≥ 6} by three. A split into {variable = bound} and {variable ≥ bound + 1} loses no integer point. `to_t` rewrites a slice of the K or M1 chart in t with the right lower bound.
- **`recognise`.** A target among the derived members is accepted only if it has the same variables, the same fixed values and a domain that contains the current one. The verdicts "the base" and "the exit y of its base" do not occur in the stored run.
- **The closing claims.** Every member, given or derived, is tested for an entry above t² on its whole domain. Every exit of every member is classified, except the one that leads back to the member it was derived from.

Three remarks, none of them an error in the stored run:

1. **The table `tinst` needs T₀ ≥ 8.** It lists M1(6) and M1(t − 5) as members for every t in the domain. M1(6) is a member only for t ≥ 8. The option `--T0` is not guarded, so a run with a smaller T₀ could accept a non-member. The stored run uses only K(1), K(t − 2), L(2), M1(3), M1(t − 3) and M2(0) from this table.
2. **One claim is not a check.** The line "the formula of K at j = t−1 is K(t−1), and of L at i = 0, 1 with r = N+1−i is L(0), L(1)" is passed as `True`. It is true by the way the script defines these quivers.
3. **The members are more than the core.** A derived member is kept on a whole box, also where it is higher than H⁺ (for instance μ_x K(j), which is below H⁺ only for j up to about √(2t)). This is harmless: the proof needs the members to be closed, not to be low. It is the reason why the script needs depth 2.

### 4.2 The closed forms, re-derived

Lemma 16.1 read backwards: a backward step sends a column (A, B) with B ≤ 0 to (−B, A + 2B) and a column with B > 0 to (−B, A). If Z is the quiver before a forward step and Y the one after, then S_ef(Z) = S_ef(Y) − [−A_e]₊[A_f]₊ + [A_e]₊[−A_f]₊ with the entries A of Z. From L(0), with columns c₁ = (0, t), c = (N + 1, −(N + 2)), x = ((t − 1)t² − 1, −((t − 2)t² − 1)):

- **L(−1).** c₁ = (−t, 0). Its first entry is negative, so the entries from c and x to c₁ change by t·A_c and t·A_x: there are tN arrows c → c₁ and t((t − 2)t² − 1) arrows x → c₁.
- **L(−n), 2 ≤ n ≤ t − 2.** c₁ = ((n − 2)t, −(n − 1)t), c = (N + 1 + n, −(N + 2 + n)), x = ((t − 1 − n)t² − 1, −((t − 2 − n)t² − 1)). All first entries are ≥ 0, so no S changes. This is the formula of M1 at k = n.
- **L(−(t − 1)).** The column of x has passed its bottom: x = (−1, t² − 1). Now x → c₁ has t(t − 2)(t² − 1) arrows and c → x has 2t³ − 3t².
- **L(−t).** x = (−(t² − 1), −1). The arrows between x and c₁ cancel: t(t − 2)(t² − 1) − (t² − 1)(t − 2)t = 0. And c → x has 2t³ − 3t² + (t² − 1)(N + t + 1) = H⁺ − 2t² arrows.
- **L(−(t + 1 + m)), m ≥ 0.** x = (mt² + 1, −((m + 1)t² + 1)) and nothing else changes. This is M2(m).

These agree with the table of members in note 16 §4.1. `review17.py closedforms` certifies them as polynomial identities with certified signs: the step of K(j) is K(j + 1) (I3), the step of L(i) is L(i + 1) with r − 1 for r (I5), two and three backward steps from L(0) give the formula of M1 at k = 2, which is therefore L(−2), and M1(3) (I8), the backward step of M1(k) is M1(k + 1) (I10), two and three backward steps from M1(t − 2) give the formula of M2 at m = −1, which is therefore L(−t), and M2(0) (I9), and the backward step of M2(m) is M2(m + 1) (I11). `singles` prints the fourteen single quivers as polynomials in t.

### 4.3 The replay

**The set of members.** For t ≥ 8 let 𝓜_t consist of:

- the *line members*: K(0); the formula of K at 1 ≤ j ≤ t − 1; K(t), K(t + 1), K(t + 2), K(−1), K(−2); the formula of L at 0 ≤ i ≤ N + 1 with r = N + 1 − i; L(−1); the formula of M1 at 2 ≤ k ≤ t − 2; L(−(t − 1)); the formula of M2 at m ≥ −1;
- the *derived members*: for every verdict "new member" of the log, the quiver μ_v μ_word(B) at every true parameter point of the box of that claim, where B is the line member named in the claim.

In the log the line members are 26 boxes (14 single quivers and 5 lines) and the derived members 123 boxes of 14 kinds. A box fixes some coordinates and bounds the others from below. The charts are (t) for single quivers, (j, v) with t = j + v + 1 for K, (k, u) with t = k + u + 2 for M1, (t, m) for M2, (t, i) for the top, and (t, i, r) with r free for L; the *true* points of the L chart are those with r = N + 1 − i.

**What `review17.py replay` checks.**

- **(A) Every claim.** For each of the 766 lines "exit v of M on box D: verdict", the script builds M from the check's closed forms at the general point of D, mutates symbolically with certified signs, and proves the verdict:
  - *height*: the named entry has a certified sign and absolute value ≥ H⁺ on D (in the L chart H⁺ is (t + i + r)t² − 1, which is H⁺(t) at the true points by identity I1);
  - *fork*: the definition of §7 with the named point of return, and an entry above t²;
  - *member*: the mutated quiver equals the target as a matrix of polynomials, up to a relabelling, and the target is a member at every true point of D (below);
  - *new member*: the signs are certified, so the new member is well defined on D.
  
  Result: 428 height, 54 fork, 161 member, 123 new member, none failed. Each verdict was also evaluated with the integer kernel at the corner of its box and at two random points: 2,298 evaluations agree.
- **(B) Coverage.** For every member box and every vertex except the one the member was made by, each integer point of the box lies in the box of a claim for that vertex: 622 pairs (box, vertex), no hole. The inclusion of boxes is decided exactly, by testing all integer points up to one more than the largest constant. The six boxes of K and the three of M1 contain all true (j, v) and (k, u) with t ≥ 8: a point (j, v) lies in the box with corner (a, 7 − a) for a = min(j, 6), and (k, u) in the one with corner (a, 6 − a) for a = min(k, 5). Every box of a derived member lies in the boxes of the member it was derived from, so the skipped exit leads back to a member.
- **(C) Height.** Every member except K(0) has an entry certified above t² on its whole box: 148 of 148.

**Why a target is a member.** The 161 targets are of three kinds.

- **(a) The formula of a line (29).** In 23 claims the target is the same line at the next or the previous index; in 6 it is the first or the last instance of a line, reached from a single quiver (K(1), K(t − 2), L(2), M1(3), M1(t − 3), M2(0)). The script certifies on the box that the index stays in the range of 𝓜_t: 1 ≤ j′ ≤ t − 1 for K, 2 ≤ k′ ≤ t − 2 for M1, m′ ≥ −1 for M2, 0 ≤ i′ ≤ N + 1 for L. At the ends the formula is a single quiver: K at j = t − 1 and M1 at k = t − 2 by definition, M1 at k = 2 is L(−2) by I8, M2 at m = −1 is L(−t) by I9, and L at r = 0 is the top. The exit K(j − 1) is claimed only on boxes with j ≥ 2; at j = 1 the log has the separate verdict K(0), which holds.
- **(b) A single quiver (25).** The mutated quiver is compared with the check's own matrix for that quiver.
- **(c) A derived member (107).** The target is rebuilt from its name: the same word of mutations on the named line member, at the point with the same t that satisfies the slices in the name. The script checks that these slices hold at that point, that the point lies in a box where a "new member" claim created this kind, and that the two matrices agree up to a relabelling.

**The free variable r.** On the box of L the claims hold for all (t, i, r) with t ≥ 8, i ≥ 2, r ≥ 1, and the exit L(i + 1) needs only r ≥ 1. The exit L(i − 1) is the formula of L at (i − 1, r + 1). For i ≥ 3 this is again a point of the box. For i = 2 it is the formula at (1, r + 1), which is the member L(1) only if r + 1 = N. That holds on the true points and fails elsewhere in the box. So the closure holds on the true points, and the proof needs no more. The same applies to the exit from the top to L(N): the box of the top has a free i, and the true point is i = N + 1.

**The argument.** Let t ≥ 8 and let a reduced route start at P⁺_t = K(0), end at a quiver of height ≤ t², and stay below H⁺(t). By Lemma 15.5 it passes no fork higher than t². By (A) and (B), a mutation of a quiver of 𝓜_t is in 𝓜_t, has height ≥ H⁺(t), or is a fork higher than t². So the route stays in 𝓜_t, and by (C) it ends at K(0). This is the argument of note 16 §4.1, and every step of it is now checked twice. ∎

### 4.4 The exits

The table lists every verdict that occurs for each kind of member (`review17_replay.log`). "Fork" means a fork higher than t², "high" means height ≥ H⁺, and "back" is the vertex the member was made by. Where two verdicts are given, the first holds on some boxes and the second on others.

| Member | μ_x | μ_p | μ_q | μ_{c₁} | μ_c |
|---|---|---|---|---|---|
| K(0) | μ_x K(0) | K(1) | K(−1) | fork | μ_c K(0) |
| K(j), 1 ≤ j ≤ t − 2 | μ_x K(j), or high | K(j + 1) | K(j − 1) | μ_{c₁} K(j) | fork |
| K(t − 1) | high | K(t) | K(t − 2) | L(0) | high |
| K(t) | high | K(t + 1) | K(t − 1) | L(1) | high |
| K(t + 1) | high | K(t + 2) | K(t) | high | high |
| K(t + 2) | high | fork | K(t + 1) | high | high |
| K(−1) | high | K(0) | K(−2) | high | high |
| K(−2) | high | K(−1) | fork | high | high |
| L(0) | high | L(1) | L(−1) | K(t − 1) | high |
| L(1) | high | L(2) | L(0) | K(t) | high |
| L(i), 2 ≤ i ≤ N | μ_x L(i), or high | L(i + 1) | L(i − 1) | μ_{c₁} L(i) | high |
| L(N + 1), the top | high | high (H⁺ exactly) | L(N) | μ_{c₁} L(N + 1) | high |
| L(−1) | high | L(0) | L(−2) | μ_{c₁} L(−1) | high |
| L(−2) | high | L(−1) | M1(3) | high | high |
| M1(k), 3 ≤ k ≤ t − 3 | high | M1(k − 1) | M1(k + 1) | high | high |
| M1(t − 2) | high | M1(t − 3) | L(−(t − 1)) | high | high |
| L(−(t − 1)) | high | M1(t − 2) | L(−t) | high | high |
| L(−t) | high | L(−(t − 1)) | M2(0) | high | high |
| M2(m), m ≥ 0 | high | M2(m − 1) | M2(m + 1) | high | high |
| μ_x K(0) | back | μ_p μ_x K(0) | high | high | high |
| μ_p μ_x K(0) | μ_x K(1) | back | high | high | high |
| μ_c K(0) | high | high | μ_q μ_c K(0) | μ_{c₁} μ_c K(0) | back |
| μ_q μ_c K(0) | high | high | back | high | high |
| μ_{c₁} μ_c K(0) | high | high | high | back | high |
| μ_x K(j) | back | high | high; at j = 1: μ_q μ_x K(1) | μ_{c₁} μ_x K(j), or high | high |
| μ_q μ_x K(1) | μ_x K(0) | high | back | high | high |
| μ_{c₁} K(j) | μ_{c₁} μ_x K(j), or high | fork, or high | fork, or high | back | high |
| μ_{c₁} μ_x K(j) | μ_{c₁} K(j) | high | high | back | high |
| μ_x L(i) | back | high | high | μ_{c₁} μ_x L(i), or high | high |
| μ_{c₁} L(i) | μ_{c₁} μ_x L(i), or high | fork, or high | fork, or high | back | high |
| μ_{c₁} μ_x L(i) | μ_{c₁} L(i) | high | high | back | high |
| μ_{c₁} L(N + 1), μ_{c₁} L(−1) | high | high | high | back | high |

The log lists μ_q μ_x K(1) as a kind of its own for t ≥ 11 and recognises it as μ_p μ_x K(0) for t = 8, 9, 10. The two are the same quiver for every t ≥ 8 (identity I13): x → p is a single arrow in K(0), and this is its pentagon. So the 14 kinds are 13 quivers.

One row by hand, as a check of the reading: μ_{c₁}K(0) is a fork with point of return c₁. In K(0) the arrows at c₁ are p → c₁ (t(t − 1)), c → c₁ (2t), c₁ → q (t²) and c₁ → x (t(t − 1)). After the mutation the in-neighbours of c₁ are q and x and the out-neighbours are p and c. The new arrows are p → q (t³(t − 1) − 2), p → x (t²(t − 1)² − 1), c → q (2t³ − t² + 1) and c → x (2t³ − 3t²). Each is heavier than both arrows at c₁ that it has to beat, for t ≥ 3. The cycle p → q → c₁ → p shows that the quiver is not acyclic, and each side has two vertices.

### 4.5 Negative controls

`review17.py negctl` changes one line of the log at a time and runs the replay on the changed log (`review17_negctl.log`). All 17 changed logs are rejected:

- another entry named in a height verdict (two cases), another point of return, another target on a line, another slice in a derived target, K(t) written for K(t − 2);
- a box widened by one at an end of a range: j ≥ 0 for a fork, j ≥ 1 for K(j − 1), k ≥ 2 for M1(k − 1), u ≥ 0 for M1(k + 1), r ≥ 0 for L(i + 1), m ≥ −1 for M2(m − 1), and a box larger than that of its derived target;
- a "new member" turned into a height verdict, a slice moved from t = 9 to t = 10, a box shrunk from t ≥ 10 to t ≥ 11, and one claim removed. The last two are caught by (B).

### 4.6 On integers

- **Closure** (`review17.py closure`, `review17_closure.log`, `review17_closure_65_80.log`). For every t from 2 to 80 the script computes the set that P⁺_t reaches through quivers of height < H⁺(t) without entering a fork higher than t². It contains one quiver of height ≤ t². No fork of height ≤ t² is met. Its size is 120, 125, 263, 492, 840, 1,331, 1,985, 2,827, 3,882, 5,174 for t = 2 to 11, as in note 16, then 1,041,265 at t = 64 and 2,036,405 at t = 80. This is the argument of §4.1 run on integers, so it also covers 2 ≤ t ≤ 7, where note 16 has the plain search only.
- **Members against the search** (`instances`, `review17_instances.log`). For t = 8 to 14, 16, 20 and 24 the instances of the members at the true parameters that lie below H⁺ are exactly that set (54,381 quivers at t = 24), one instance has height ≤ t², and no mutation of an instance below H⁺ falls outside the three verdicts.
- **Anatomy** (`anatomy`, `review17_anatomy.log`). At t = 5: 227 quivers on the route, 230 on the backward line (it reaches H⁺ at step 231, and the column of x grows from there on), 5 beyond the ends of the first line, and 30 on branches; 492 in all.

---

## 5. Theorem 16.5

`review17.py plain` computes, for each t, the set of all quivers of height < H that the start reaches through such quivers, with no use of forks (`review17_plain.log`). The entries are Python integers.

| | t = 2 | 3 | 4 | 8 | 16 | 32 | 64 | Sum over t = 2 to 64 |
|---|---|---|---|---|---|---|---|---|
| Reached from P⁺_t below H⁺(t) | 157 | 173 | 381 | 2,961 | 23,980 | 193,929 | 1,561,537 | 25,717,726 |
| Reached from P_t below H(t) | 46 | 135 | 314 | 2,463 | 19,971 | 161,575 | 1,301,189 | 21,427,901 |

For all 63 values of t and both families:

- the number of quivers equals the stored one (`below_H.popped`);
- the number of mutations that lead to height ≥ H equals the stored one (`below_H.capped`; 4,684,587 for P⁺_64);
- exactly one quiver of the set has height ≤ t².

The agreement on 47 million quivers is also a check of the two canonical forms against each other.

**Beyond t = 64 [I].** `np_barrier.c` stores entries in 32 bits, and H⁺(65) = 2,302,734,849 is above 2³¹. The same search in Python integers for 65 ≤ t ≤ 80 gives one quiver of height ≤ t² for each t (`review17_plain_65_80.log`): 1,636,055 quivers below H⁺ at t = 65 and 3,054,100 at t = 80, where H⁺ = 6,512,646,399 = 159.0·w². So Theorem 16.5 holds for P⁺_t for 2 ≤ t ≤ 80, and on 8 ≤ t ≤ 80 Theorem 16.6 is proved twice.

**`np_barrier.c`.** Read in full. The mutation forms products of two entries of absolute value at most the cap in 64 bits, and returns "above the cap" before anything is stored. The canonical form is the least upper triangle over all relabellings. The hash table compares whole keys. The search pops quivers in order of the lowest bottleneck; it reports a quiver of height ≤ w reached at a bottleneck above w, and counts the quivers reached at bottleneck ≤ w as the plateau. `np_corridor.py` accepts a row only if the search ended without a find and within its budget, the plateau is 1 and the lowest height is t². That is the statement of the theorem.

---

## 6. The hand proofs

**Lemmas 16.1 to 16.3.** The proofs are complete. In Lemma 16.3 the hypothesis A_y = 0 is what keeps the entries S unchanged under μ_p, and η·S_ey = 2(A_e + B_e) turns B_e − η·S_ey into −(B_e + 2A_e).

**Theorem 16.4.** Each line of the proof was followed.

- K(0) to K(1): x = (−1, t² − 1) becomes (t² − 1, 1), and the entries from x to c₁ and c gain (t − 1)t and t². They become 0 and 2t².
- K(t − 1) to L(0): Lemma 16.2 applies with η = t, since S_{c,c₁} = 2t ≥ 0 and S_{x,c₁} = 0. The slope of c drops from 2t² − 1 to −1, and t² + (t − 1)(2t² − 1) = N + 1.
- The top: c = (0, −1), 2t = 2·(slope of c₁), 2t² = 2·(slope of x), S_{x,c₁} = 0. Lemma 16.3 applies with η = 1.
- Length: 2(t − 1 + 1 + N + 1) + 2 = 4t³ − 2t² + 4.
- Heights: the first entry of x at L(N + 1) is (t + N)t² − 1 = H⁺ − t²; the entry between q and x in μ_p(T) is (t + N + 1)t² − 1 = H⁺.

`closedforms` certifies the steps and the top for all t ≥ 2 (I2 to I6), and `route` runs the whole route on integers for t = 2 to 64: 1,040,388 mutations at t = 64, heights at most 2,130,706,431 before the top and 2,130,710,527 at it.

**Corollary 16.7.** Put s = √w and t = ⌊s⌋, so t > s − 1 ≥ 1. Then H⁺(t) ≥ 2t⁵ − t⁴ > 2(s − 1)⁵ − (s − 1)⁴, since 2x⁵ − x⁴ increases for x > 2/5. And 2(s − 1)⁵ − (s − 1)⁴ − (2s⁵ − 11s⁴) = 24s³ − 26s² + 14s − 3, which has its only real root at 0.405. The condition w < H⁺(t) of Theorem 16.6 holds because (t + 1)² ≤ H⁺(t) for t ≥ 2.

**The constant 11 [I].** At w = (t + 1)² − 1 the least constant c with H⁺(t) ≥ 2w^{5/2} − c·w² is 10.5647 at t = 64, 10.9711 at t = 1,000 and 10.9997 at t = 100,000. It tends to 11 from below, so 11 cannot be replaced by a smaller constant for all w. With 10 the inequality fails first at w = 783.

---

## 7. Lemma 15.5 on five vertices

**The definition [P, according to a fetched reading].** Ervin, arXiv 2306.07502v2, Definition 2.5 (attributed there to Warkentin's thesis, Definition 2.1): a fork is an abundant quiver that is not acyclic, with a vertex r such that for every i with an arrow into r and every j with an arrow out of r the number of arrows from j to i is greater than the number from i to r and than the number from r to j, and such that the in-neighbours and the out-neighbours of r each induce an acyclic subquiver. Abundant means at least two arrows between every pair. Its Lemma 2.7 (Warkentin's Lemma 2.5) says that μ_k of a fork, for k not the point of return, is a fork with point of return k and strictly more arrows. The paper was read through an automated summary of its HTML version, not line by line; the thesis itself was not opened.

**Lemma 15.4 [I].** Note 15 adds "no entry of μ_k(F) is smaller in absolute value than in F", which the height argument needs, and proves the whole lemma. The proof holds for every number of vertices:

1. Every vertex other than r is an in-neighbour or an out-neighbour of r, and every arrow between the two sides points from the out-side to the in-side. So a triangle that avoids r either lies on one side, which is acyclic, or has a vertex alone on its side, and that vertex is a source or a sink of the triangle. Hence every oriented triangle contains r.
2. For i → k → j: if i → j the entry grows by b_ik·b_kj. Otherwise i → k → j → i is oriented, so i = r or j = r, and the entry opposite r is the largest of the triangle. The new weight is at least 2·(that entry) − (a smaller one), which exceeds both b_ik and b_kj.
3. The two sides of k keep their arrows. A cycle in a tournament contains an oriented triangle. Such a triangle on one side of k would contain r, and then k and another of its vertices would lie on opposite sides of r with the arrow between them in the wrong direction.
4. r is neither a source nor a sink. With i on the side of r opposite to k, the triangle on i, r, k is oriented before and after μ_k.

None of the four steps uses n = 4.

**Lemma 15.5.** If a reduced route leaves a fork R at a vertex other than its point of return, all later quivers are forks and no entry decreases, so the last quiver is at least as high. Otherwise the route arrived at R by a mutation at another vertex (or starts at R), and the same holds backwards. A fork may have more than one point of return; the argument works with any of them.

> **Correction (note 19):** A fork has exactly one point of return (Warkentin's thesis, Lemma 2.3.e). Every oriented triangle of a fork has the form i → r → j → i with q_ji the strictly largest weight, so r is the vertex opposite the heaviest arrow of any oriented triangle. The argument above does not depend on this. Also, "no entry is smaller" is stated in Warkentin's proof of his Lemma 2.5, so it is not only note 15's. See [note 19](19-checks-of-notes-13-to-16.md) §4.

**On integers** (`review17.py forks`, `review17_forks.log`). 20,000 forks built at random on 5 vertices and 20,000 on 6: all 80,000 and 100,000 mutations away from the point of return give a fork with point of return the mutated vertex, with no smaller entry and a larger total weight. On 200,000 random reduced routes on 5 vertices, 740,132 quivers are forks, and none is higher than both ends; on 6 vertices, 690,959 and none.

---

## 8. The measured statements

- **P_t.** The lower bound for P_t rests on the search for t ≤ 64 only, as note 16 says (§4.2, "What is not certified"). That search was confirmed here for all 63 values.
- **Six and seven vertices.** The pendant quivers and the star quivers were recomputed with a kernel for n vertices and no pruning (§3). Note 16 labels both as measured. For the twelve pendant quivers and the six star quivers that were run, the statement is exact: the search below the height of the route is complete.
- **The census, the rows and the templates.** Every number in the tables of §6.1, §6.2 and §6.3 and in §1 items 5 and 6 was compared with the logs. They agree, apart from the two points of §1 here. None of these searches was rerun. Note 16 calls the values lower bounds and says what the census does not see; that wording is right.
- **Fork pruning in the census.** `np_barrier` with pruning does not expand a fork other than the start. For a start whose every mutation is higher than w this loses no escape: on a reduced route to another quiver of height ≤ w, the first fork has height ≤ w by Lemma 15.5. So either the search reports that fork, at a level no higher than the route, or the fork is a relabelling of the start and the rest of the route is a shorter route from the start.
- **§5.** The count is a heuristic and is labelled [H].

---

## 9. Corrections made in place

- **Note 16, corrections.** A note at the head. §1 item 2: the degree of a polynomial bound, and the constant 11. §1 item 6: the 1,516 template searches over budget. §4.1, under the table of claims: 937 checks, and `--T0` not below 8. §4.2: 230 and 35 at t = 5. §6.2: 50 % for 51 %.
- **Note 16, updates.** §3.3: the search reproduced and continued to t = 80. §4.1: the free variable r at i = 2. §5: the star quivers without fork pruning. §8: the second reading, and what was read of Warkentin's lemma.
- **Note 15.** A note under Lemma 15.5: Lemmas 15.4 and 15.5 hold on any number of vertices.

---

## 10. Still unchecked

- **The census, the rows and the templates were not rerun** (§6 of note 16), and neither were `grid`, `pycheck` and `selftest` of `np_corridor.py`.
- **The cores of P_t** in §4.2 beyond the route counts.
- **§5 as mathematics.** Whether a pure route with an early turn at the centre can do better was not examined.
- **Warkentin's thesis.** The definition and Lemma 2.5 were read only in Ervin's restatement, through an automated summary.
- **Prior art.** No search was made.
- **A human reading.** Note 16 has now been checked by two instances of one model. Theorem 16.6 for t > 80 rests on two programs and on Lemma 15.5.

---

## 11. Reproduce

```bash
PY=python
$PY -I ../verify/review17.py selftest > review17_selftest.log
$PY -I ../verify/review17.py lemmas > review17_lemmas.log
$PY -I ../verify/review17.py forks > review17_forks.log
$PY -I ../verify/review17.py route --tmin 2 --tmax 64 > review17_route.log                       # about 4 minutes
$PY -I ../verify/review17.py closedforms > review17_closedforms.log
$PY -I ../verify/review17.py singles > review17_singles.log
$PY -I ../verify/review17.py replay > review17_replay.log                                        # one second
$PY -I ../verify/review17.py negctl > review17_negctl.log
$PY -I ../verify/review17.py plain --tmin 2 --tmax 64 --family both --workers 7 > review17_plain.log    # a few minutes
$PY -I ../verify/review17.py plain --tmin 65 --tmax 80 --family plus --workers 6 > review17_plain_65_80.log   # about 4 minutes
$PY -I ../verify/review17.py closure --tmin 2 --tmax 64 --workers 7 > review17_closure.log
$PY -I ../verify/review17.py closure --tmin 65 --tmax 80 --workers 6 > review17_closure_65_80.log       # about 5 minutes
$PY -I ../verify/review17.py instances --t 8 9 10 11 12 13 14 16 20 24 > review17_instances.log
$PY -I ../verify/review17.py anatomy --t 2 3 4 5 6 7 8 9 10 11 12 16 > review17_anatomy.log
$PY -I ../verify/review17.py pendant > review17_pendant.log
$PY -I ../verify/review17.py star > review17_star.log
$PY -I ../verify/review17.py corollary > review17_corollary.log
$PY -I np_corridor_prove.py prove --T0 8 --audit-tmax 11 | cmp - np_corridor_prove.log       # the stored log is reproduced
```

`review17.py` writes only to standard output, apart from `negctl`, which writes its changed logs to `~/.cache/qmb-review17/`. `replay`, `negctl` and `instances` read `np_corridor_prove.log`; `plain` reads the two `np_corridor_family*.jsonl` files. The symbolic commands need cypari2, which is in `requirements.txt`.

---

## Sources

- Notes [15](15-rank-2-orbits-and-the-constant-2.md) and [16](16-five-vertices-above-w-squared.md) of this repository, and [note 12](12-checks-of-notes-03-to-10.md) for the form of this check.
- Ervin, *New hereditary and mutation-invariant properties arising from forks*, Definition 2.5 and Lemmas 2.7 and 2.8 (according to a fetched reading of the HTML version): https://arxiv.org/abs/2306.07502
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Definition 2.1 and Lemma 2.5, as restated by Ervin (not opened): https://d-nb.info/1214302807/34
