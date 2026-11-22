# 20. The core of Q_a below its barrier: lines, branches and two spirals; Conjecture 18.7(a) for a ≤ 64

*Run on 2026-11-12. The aim was to prove Conjecture 18.7(a) of [note 18](18-five-vertices-cubic-barrier.md) for every a by a certificate in the style of [note 16](16-five-vertices-above-w-squared.md) §4, or to find out exactly what blocks such a proof. It is not proved for every a. This note describes the set a certificate would have to cover, proves three statements about it for every a, says what resists, and extends the range in which the conjecture holds from a ≤ 22 to a ≤ 64. Code: [experiments/np_qa_core.py](../experiments/np_qa_core.py) and [experiments/np_qa_core.c](../experiments/np_qa_core.c) (new), with `np_rowwalk.py` of note 18. Results: the `np_qa_core_*` files in `experiments/`. Notation of note 18: Q_a = (−(a − 3), a − 2, a + 1, −(a + 1) | R_a) has height w = a + 1; H(a) = 4a³ − 3a² + (5a − 1)/2 for odd a and 4a³ − 3a² + (3a − 4)/2 for even a; m = 2a + 1 and c = 4a² − 5a + 1; W_m(j) is the bounce cycle on p, q, r, s, a step mutates at p and exchanges the names p and q, and (A, B, U, V) = (b_px, b_qx, b_xr, b_xs) is the state of the fifth vertex x. [y]₊ = max(y, 0). Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 23):** Checked in [note 23](23-checks-of-notes-20-to-22.md) with new code. No theorem was found false. Lemma 20.1 and Propositions 20.2 and 20.3 were re-derived by hand and tested. Theorem 20.4 was reproduced by a search that stores every quiver it reaches: without pruning for 2 ≤ a ≤ 26 and a = 32, and with forks not expanded for 2 ≤ a ≤ 32, 36 and 40, with the counts of §7 every time. Corrected below: the claim that no certificate with finitely many polynomial families exists (§1 item 6, §8), which is not supported; the fifth vertex x, which is not a vertex of the class, because Q_a reaches relabellings of itself that move x below H(a) (§3, §6.3, §8); and the wording of §1 item 2, §4.2, §5.2 and §6.2.

---

## 1. Outcome

1. **Conjecture 18.7(a) is not proved for every a. It holds for 2 ≤ a ≤ 64 [I, by exhaustive computation].** For 2 ≤ a ≤ 48 the search uses no pruning, as in Theorem 18.5, which stopped at a = 22. For 49 ≤ a ≤ 64 forks are not expanded, which rests on Lemma 15.5; that search stopped at a = 26. So F(5, w) ≥ 4w³ − 15w² + 19w − 11 for 3 ≤ w ≤ 65 (Theorem 20.4). At w = 65 the barrier is H(64) = 1,036,382 = 3.77·w³ = 30.4·w^{5/2}. The gain comes from not storing the quivers that have exactly two neighbours below H(a): memory falls from order a⁵ to order a³.
2. **The core.** Call *core* the set K(a) of quivers that Q_a reaches through quivers of height < H(a) without entering a fork. By Lemma 15.5 the conjecture at a says that Q_a is the only member of K(a) of height ≤ a + 1. K(a) has about 4a⁵ members: 864,408 at a = 12, 126,448,965 at a = 32 and 4,165,617,632 at a = 64. A certificate has to cover all of them.

   > **Correction (note 23):** The equivalence of §2.1 has a second condition: no exit of a member is a fork of height ≤ a + 1.
3. **Almost all of the core is two families of lines, with closed forms for every a [I, proved].** Each round of the route is a stretch of a line of steps on the pair (p, q). The line goes on beyond both ends of the round. Beyond position 0 of a round with slopes (1, 2) it runs backwards for A + 3 quivers, and beyond position m of a round with slopes (−1, −(2a − 1)) it runs forwards for A + 4 quivers, where A is the entry b_px at that end (Proposition 20.2 gives the quivers; the lengths are measured). These lines hold 98.2 % of the core at a = 12 and 99.1 % at a = 16. They are not on the route, they are not forks, and almost all of them lead nowhere: a mutation off a line at a vertex e has height ≥ H(a) as soon as the two entries of the column of e have product ≥ H(a) + 2 (Lemma 20.1). This part of the core is no obstacle.
4. **About 4a³ to 5a³ quivers near the route are neither on the route nor on these lines [I, measured].** For a = 6 to 16 they fall into 88 to 109 kinds (stretch of the route, and the pairs on which the word from the route steps). A kind is a family with up to five indices. The verdicts of its exits are not constant on orthants of the indices: for example the mutation at r of the route quiver at position j after the t-th turn of the last stretch is a member exactly where A + (m − j)·|U| < H(a), a region bounded by a hyperbola (§5.2). The certificates of note 16 are polynomial inequalities on orthants.
5. **The class of R_a contains infinitely many quivers that are not forks, for every a [I, proved].** From W_m(0), the ten mutations q p q s p s p s q p bring the triangle on p, q, s back to itself and multiply the three entries of r at p, q, s by a fixed matrix with eigenvalues φ⁸ ≈ 46.98, 1 and φ⁻⁸, φ the golden ratio (Proposition 20.3). Every quiver on the way has a pair of vertices among p, q, s with fewer than two arrows, so none is a fork. The same holds at the other end of the cycle, by the mirror symmetry. On these two spirals the entries grow geometrically.
6. **This is what blocks a certificate with finitely many families [I].** The spirals lie in the core as far as their entries stay below H(a). Below H(a) the 4-vertex class of R_a has 65 quivers that are not forks off the cycle at a = 6 and 139 at a = 96, about 18 more for each doubling of a. The 4-vertex parts of members of the core that are not forks and not on the cycle number 66 at a = 6 and 114 at a = 48, and they reach from 8 to 15 mutations away from the cycle (§6.3). New kinds of members appear at every a from 12 to 16, the end of the range that was sorted in full. So the number of families grows without bound, like log a, and the entries along a spiral are not polynomials in its index. A certificate in the style of note 16 lists finitely many families with polynomial entries; it cannot cover the core for all a.

   > **Correction (note 23):** This conclusion is not shown, and its label should be [H]. The depth of the spirals inside K(a) is measured, for a ≤ 48 and at most 15 mutations from the cycle, as §8 and §9 say. Even granting it, the argument rules out only families indexed by the words from the route, with entries polynomial in a and in the run lengths. A family can instead take as free variables the entries of r on a cone, with the row of x. Its entries are then linear, and the round of ten mutations maps it to itself by the matrix of Proposition 20.3(2). §8's plan for the spirals is of this kind. What is measured is that families indexed by the words from the route grow in number with a, up to a = 48. Whether finitely many families parametrised by their state close was not examined ([note 23](23-checks-of-notes-20-to-22.md) §4.2). The 4-vertex parts counted here also depend on the representative the search kept (note in §3).
7. **What a proof would need (§8).** (i) Proposition 20.2 and Lemma 20.1 for the lines, which are here. (ii) Closed forms for about a hundred families near the route, and certificates on regions bounded by quadrics. (iii) An induction along the spirals, with entries given by a linear recurrence. None of (ii) and (iii) was done. No member of the core contradicts the conjecture, and the structure is the same from a = 6 to a = 48.

---

## 2. The core and the search

### 2.1 Definition

Let a ≥ 2, w = a + 1 and H = H(a). The *core* K(a) is the set of quivers, up to relabelling, that can be reached from Q_a by mutations through quivers that have height < H and are not forks. A mutation of a member is an *exit*: it is another member, or it has height ≥ H, or it is a fork.

By Lemma 15.5 a reduced route between two quivers of height ≤ w passes no fork higher than w. So if a route from Q_a to a quiver Y of height ≤ w has height < H, its reduction lies in K(a) up to its last quiver, and Y is a member of K(a) or a fork of height ≤ w among the exits. Hence the statement of Theorem 18.5 holds at a, namely that every route from Q_a to a quiver of height ≤ w not isomorphic to Q_a has height at least H, if and only if Q_a is the only member of K(a) of height ≤ w and no exit is a fork of height ≤ w. With Theorem 18.4 that statement gives Conjecture 18.7(a) at a. This is the argument of Theorem 16.6. A certificate for every a has to describe K(a), or a larger set closed in the same sense.

### 2.2 The program

`np_qa_core.c` grows K(a) from a list of seeds, breadth-first, with the mutation, canonical form and fork test of `np_barrier.c` of note 16. It has two modes.

- **plain.** Every member is stored, with the seed it was reached from, the mutation that led to it, its matrix in the labels of that seed, and its five exits.
- **chain.** A member is stored only if it is a seed, has height ≤ w, or does not have exactly two exits that are members. A member with exactly two such exits is *passed through*: the search walks from a stored member along such members to the next stored member and only counts them. Nothing is lost, because a member that is passed through has no neighbours in the core besides the two on its chain. Each chain is walked once from each end, so the number of members passed through is half the sum of the chain lengths; the program checks that this sum is even.

Each mode has a variant without the fork test (`plain-nofork`, `chain-nofork`): then every quiver of height < H is a member. This is the search of Theorem 18.5.

For the description of the core the seeds are the quivers of the first half of the route of Theorem 18.4 that lie below H, each in the frame x, p, q, r, s of its position: the seed (n, j) is W_m(j) with the state it has before the n-th turn. A member then carries the word of mutations, in the names x, p, q, r, s of its seed, that leads to it from the nearest seed. For Theorem 20.4 the only seed is Q_a.

**Stretches.** The first half of the route has four stretches, by the slopes (d, e) of Theorem 18.4: S1 before the first turn, slopes (2a − 2, 2a − 1); S2 before the second, slopes (a, 3); S3, the turns 3 to 2a + 1, slopes (−1, −(2a − 1)); S4 after the bottom, slopes (1, 2). S4 has about 2a² rounds, and the others 2a + 1 together.

### 2.3 Checks of the program

- **Three programs.** For 2 ≤ a ≤ 16 the number of members is the same in mode plain, in mode chain and in `np_barrier` with fork pruning (quivers popped minus forks): 391 at a = 2, 864,408 at a = 12, 3,750,605 at a = 16. Mode chain and `np_barrier` agree for a = 18, 20, 22 and 24 as well: 29,461,148 members at a = 24, where `np_barrier` pops 29,501,788 quivers, the number of note 18 §5.2, and 40,640 of them are forks (`np_qa_core.py crosscheck`, `np_qa_core_crosscheck.log`).
- **Without pruning.** For 2 ≤ a ≤ 22 mode chain-nofork finds the 21 numbers of quivers of Theorem 18.5, from 525 at a = 2 to 61,875,173 at a = 22, which `np_barrier` found by storing every quiver (`np_qa_core.py compare18`, `np_qa_core_compare18.log`).
- **Low quivers.** In every run of this note the set is closed, Q_a is its only member of height ≤ w, and no fork of height ≤ w occurs among the exits.

---

## 3. Anatomy of the core

`np_qa_core.py anatomy` computes K(a) in mode plain for a = 6 to 16 and sorts its members by the word from the route (`np_qa_core_anatomy.log`). A *backward line* is the set of members reached from a seed by the mutations q, p, q, … alone, a *forward line* by p, q, p, … alone; in the frame of the seed these are steps on the pair (p, q) beyond the seed.

| a | H(a) | Core | Route | Backward lines | Forward lines | Others | Members whose 4-vertex part is a fork | Members whose word has a mutation at x |
|---|---|---|---|---|---|---|---|---|
| 6 | 763 | 25,706 | 1,000 | 22,239 | 1,021 | 1,446 | 23,479 | 27 |
| 7 | 1,242 | 56,313 | 1,560 | 51,027 | 1,584 | 2,142 | 53,108 | 30 |
| 8 | 1,866 | 109,326 | 2,276 | 101,878 | 2,319 | 2,853 | 104,966 | 35 |
| 9 | 2,695 | 200,535 | 3,210 | 190,150 | 3,258 | 3,917 | 194,694 | 37 |
| 10 | 3,713 | 340,734 | 4,344 | 327,010 | 4,417 | 4,963 | 333,208 | 40 |
| 11 | 4,988 | 556,926 | 5,748 | 538,912 | 5,828 | 6,438 | 547,358 | 42 |
| 12 | 6,496 | 864,408 | 7,396 | 841,599 | 7,507 | 7,906 | 852,525 | 45 |
| 13 | 8,313 | 1,305,065 | 9,366 | 1,276,317 | 9,486 | 9,896 | 1,290,439 | 46 |
| 14 | 10,407 | 1,898,603 | 11,624 | 1,863,337 | 11,781 | 11,861 | 1,880,936 | 50 |
| 15 | 12,862 | 2,705,863 | 14,256 | 2,662,777 | 14,424 | 14,406 | 2,684,680 | 51 |
| 16 | 15,638 | 3,750,605 | 17,220 | 3,699,004 | 17,431 | 16,950 | 3,725,560 | 52 |

- **Size.** The route has about 4a³ quivers below H in its first half, and the core about 4a⁵: the ratio core/a⁵ is 3.47 at a = 12, 3.58 at a = 16, 3.77 at a = 32 and 3.88 at a = 64 (§7).
- **The lines hold almost everything**: 90.5 % of the core at a = 6, 98.2 % at a = 12, 99.1 % at a = 16.
- **The others** are 5.0a³ quivers at a = 10 and 4.1a³ at a = 16 (§5).
- **The fifth vertex is almost never mutated.** Between 27 (a = 6) and 52 (a = 16) members have a mutation at x in their word from the route. They sit at the far ends of a few lines, where the column of x has passed its bottom (the kinds with x in §5.1).
- **Most members lie over a 4-vertex fork.** The quiver without x is a fork for 99.3 % of the members at a = 16. A 5-vertex quiver is not a fork just because its 4-vertex part is one, and Lemma 15.5 says nothing about such quivers. The 4-vertex class of R_a has few quivers that are not forks (§6.2), and nearly the whole core lies over its forks.

> **Correction (note 23):** The vertex x is not a vertex of the class. Below H(a), and through quivers that are not forks, Q_a reaches 12 labelled copies of itself, and all 120 at a = 2 and 4. Eight of the 12 move x: for example x ↔ r at a = 3, by the five mutations x r x r x, and x ↔ q at a = 6, by 39 mutations of height 407. The mechanism is the pentagon: if two vertices i and j are joined by one arrow, μ_i μ_j μ_i μ_j μ_i exchanges them. So the last two columns of the table, and the two bullets above on x and on the 4-vertex part, describe the labelled representatives that mode plain happened to keep, not K(a). Theorem 20.4 counts up to relabelling and is not affected ([note 23](23-checks-of-notes-20-to-22.md) §4.1).

---

## 4. The lines

### 4.1 Steps backwards, and exits off a line

**Setting**, as in note 16 §2: a quiver with two arrows q → p; for every other vertex e the column (A_e, B_e) = (b_pe, b_qe); S_ef = b_ef for two such vertices. A *backward step* mutates at q and exchanges the names p and q. From the mutation rule at q, as in Lemma 16.1:

- a column with B_e ≤ 0 becomes (−B_e, A_e + 2B_e), and a column with B_e > 0 becomes (−B_e, A_e);
- S′_ef = S_ef + [−B_e]₊[B_f]₊ − [B_e]₊[−B_f]₊, so no S_ef changes if every B_e ≤ 0.

**Lemma 20.1 (exits off a line) [I].** Let X have two arrows q → p, let L ≥ 1 and let e be a third vertex with column (A_e, B_e).
- If A_e > 0 > B_e and A_e·|B_e| ≥ L + 2, then μ_e(X) has height ≥ L.
- If A_e < 0 < B_e, then μ_e(X) has height ≥ |A_e|·B_e + 2.

*Proof.* In the first case there are A_e arrows p → e and |B_e| arrows e → q. The mutation at e adds A_e·|B_e| to b_pq = −2. In the second case there are B_e arrows q → e and |A_e| arrows e → p, and the mutation adds |A_e|·B_e to b_qp = 2. ∎

So on a line of steps a mutation at a vertex off the pair can stay below H only where the two entries of the column of that vertex have product below H + 2. For a column of slope ±1 that is within about √H steps of its bottom.

### 4.2 The two families

For 1 ≤ t with 2(t − 1) < c, the turn 2a + 1 + t of the route has U < 0 (table of Theorem 18.4), and after it the route is at position 0 with the state

(A_t, −(A_t − 1), −(c − 2t), c − 2t + 2),  A_t = 2a − 3 + (t − 1)·m.

> **Correction (note 23):** For odd a the condition 2(t − 1) < c leaves out the last backward line, t = c/2 + 1 = T. Its turn has U = 0 and leaves U = +2. The state formula above and Proposition 20.2(1) hold there too, and the counts below include that line. The range should read 1 ≤ t ≤ T = t* − 1.

For 1 ≤ k ≤ 2a − 1 the route is at position m before the turn 2 + k with the state (A′_k, −(A′_k + 1), −u_{k−1}, u_{k−2}), A′_k = 4a² + 1 − k·m, u_i = a − 2 + i·(2a − 1).

**Proposition 20.2 (the lines) [I].** Let a ≥ 2.

1. **Backward lines.** Let (A, −(A − 1), U, V) be the state at position 0 after the turn 2a + 1 + t, as above, and let BL_t(k) be the quiver k backward steps from there. For 2 ≤ k ≤ A it has two arrows q → p, the columns

   r: (m + k, −(m + k + 1)),  s: (k − 2, −(k − 1)),  x: (A − k, −(A − k − 1)),

   m − 1 arrows r → s, b_xr = U and b_xs = V + A − 1.
2. **Forward lines.** Let (A, −(A + 1), U, V) be the state at position m before the turn 2 + k′, as above, and let FL_{k′}(k) be the quiver k steps from there. For 2 ≤ k ≤ A + 1 it has two arrows q → p, the columns

   r: (k − 2, −(k − 3)),  s: (m + k, −(m + k − 1)),  x: (A − k, −(A − k + 1)),

   m − 1 arrows r → s, b_xr = U − (A − 1) and b_xs = V.
3. None of these quivers is a fork. So BL_t(k) is a member of K(a) whenever its height is < H(a), and so is FL_{k′}(k).

*Proof.* (1) At position 0 the columns are r: (m, −(m + 1)), s: (0, 1), x: (A, −(A − 1)), with two arrows s → r. The first backward step has B_s = 1 > 0 and B_r, B_x ≤ 0: it adds m + 1 to b_rs = −2 and A − 1 to b_xs, and gives the columns (m + 1, −(m + 2)), (−1, 0), (A − 1, −(A − 2)). From then on every B_e is ≤ 0 as long as A − k − 1 ≥ 0, so no S_ef changes and each column moves by (A_e, B_e) ↦ (−B_e, A_e + 2B_e): the column of s runs through (0, −1), (1, −2), …, and the other two along their progressions. (2) is Lemma 16.1 in the same way: at position m the columns are r: (0, −1), s: (m, −(m − 1)), x: (A, −(A + 1)). The first step gives r: (−1, 0). The second has A_r = −1 < 0: it adds m + 1 to b_rs and A − 1 to b_rx, and gives r: (0, 1). After that every first entry is ≥ 0 as long as A − k ≥ 0. (3) In a fork every oriented triangle contains the point of return, and its side opposite the point of return is strictly its largest (note 14 §3, consequence (a)). BL_t(k) has the oriented triangle p → r → q → p with sides m + k, m + k + 1, 2, whose largest side is opposite p. If A − k ≥ 3 it also has the oriented triangle p → x → q → p with sides A − k, A − k − 1, 2, whose largest side is opposite q; so it has no point of return. If A − k ≤ 2, x and q are joined by fewer than two arrows. For FL the triangle p → s → q → p has sides m + k, m + k − 1, 2, with the largest opposite q; if A − k ≥ 2 the triangle p → x → q → p has sides A − k, A − k + 1, 2, with the largest opposite p; and if A − k ≤ 1, x and p are joined by fewer than two arrows. Along a line the entries of r and s grow with k, the entries between r, s and x are constant, and the entries of the column of x are at most V + A − 1 = b_xs on a backward line and at most |U| + A − 1 = |b_xr| on a forward line. So the height does not decrease along the line up to the quiver considered, and the line reaches it from the route through quivers of height < H. ∎

**Checks and counts** (`np_qa_core.py lines`, `np_qa_core_lines.log`; a = 3 to 12). The closed forms agree with integer mutation at every quiver of every line: 841,486 quivers on 259 backward lines and 6,463 on 23 forward lines at a = 12.

- **Where a line ends.** A backward line has A + 3 quivers and a forward line A + 4. After the last quiver given by the proposition the column of x passes its bottom, all three columns then have slopes of one sign, and the next quiver is a fork. The one exception for each a ≥ 4 is the backward line of the last round, which reaches H earlier: it is 4 quivers shorter for odd a and 5 for even a.
- **How many.** There are T = t* − 1 backward lines (t* as in Theorem 18.4) and 2a − 1 forward lines. For 4 ≤ a ≤ 12 the backward lines have 2aT + m·T(T − 1)/2 quivers less those 4 or 5, which is 841,491 − 5 at a = 12, and the forward lines have (2a − 1)(2a² − a + 5), which is 6,463 at a = 12. The first number is 4a⁵ to leading order.
- **Exits.** Of the 841,489 members of the backward lines of S4 at a = 12, 840,789 have all three exits at x, r and s of height ≥ H; at a = 16 it is 3,697,495 of 3,698,858 (`np_qa_core_anatomy.log`). The exceptions are about 5a² quivers, and the kinds of §5 start from them. Lemma 20.1 alone gives the three exits for 798,721 of the 841,486 quivers at a = 12 (94.9 %); the others are within about √H steps of an end of their line.

> **Correction (note 23):** 841,489 counts the backward lines of S4 together with the backward line of the round of the bottom, which has 3 quivers. 841,486 counts only the 259 lines of Proposition 20.2. Both figures, and 840,789 and 798,721, reproduce.

So the bulk of the core is described by one proposition for every a, and its exits by one lemma up to about √H steps from the ends of the lines.

---

## 5. The branches near the route

### 5.1 Kinds

`np_qa_core.py branches` takes the members that are neither on the route nor on a line of §3 and sorts them by *kind*: the stretch of the seed, and the *skeleton* of the word, which records the pairs of vertices on which the word steps and drops the lengths of its runs. For example "ps q" is a run of mutations alternating between p and s, then one at q. (`np_qa_core_branches.log`; the table shows 26 of the 116 kinds that occur for 6 ≤ a ≤ 16.)

| Stretch | Skeleton | a = 8 | 10 | 12 | 14 | 16 | At a = 16: turns of the seeds; positions; longest runs |
|---|---|---|---|---|---|---|---|
| S4 | r | 911 | 1,810 | 3,170 | 5,087 | 7,654 | 473 turns; j = 0 to 32; 1 |
| S3 | rs | 625 | 1,162 | 1,959 | 3,056 | 4,501 | 17 turns; j = 0 to 33; 17 |
| S3 | s | 194 | 310 | 452 | 622 | 820 | 31 turns; j = 2 to 33; 1 |
| S4 | ps | 123 | 205 | 304 | 428 | 568 | 230 turns; j = 2 to 5; 17 |
| S4 | qr | 114 | 194 | 292 | 412 | 550 | 230 turns; j = 0 and 32; 5 |
| S4 | s | 120 | 189 | 274 | 375 | 492 | 474 turns; j = 2 to 17; 1 |
| S4 | ps q | 61 | 102 | 154 | 218 | 292 | 145 turns; j = 2; 17, 1 |
| S4 | qr p | 39 | 67 | 103 | 146 | 197 | 144 turns; j = 32; 5, 1 |
| S3 | ps | 68 | 86 | 104 | 122 | 140 | 31 turns; j = 2 and 33; 5 |
| S3 | qr | 66 | 84 | 102 | 120 | 138 | 31 turns; j = 0 and 32; 5 |
| S3 | ps rs | 26 | 43 | 64 | 89 | 118 | 15 turns; j = 33; 2, 15 |
| S4 | qr pq | 15 | 30 | 48 | 75 | 106 | 80 turns; j = 32; 5, 3 |
| S3 | ps q | 44 | 57 | 69 | 81 | 93 | 31 turns; j = 2; 5, 1 |
| S4 | pq r | 24 | 38 | 54 | 71 | 90 | the last turn; j = 0; 91, 1 |
| S3 | qr pq | 16 | 27 | 42 | 62 | 81 | 31 turns; j = 32; 5, 4 |
| S4 | qr pq qr | 8 | 18 | 31 | 47 | 66 | 38 turns; j = 32; 3, 2, 3 |
| S3 | qr pq qr | 16 | 33 | 46 | 54 | 62 | 31 turns; j = 32; 3, 2, 3 |
| S4 | ps qs | 10 | 17 | 27 | 39 | 54 | 54 turns; j = 2; 4, 2 |
| S3 | ps pq | 1 | 7 | 17 | 34 | 48 | 31 turns; j = 2; 5, 4 |
| S4 | ps qs p | 6 | 11 | 19 | 28 | 39 | 39 turns; j = 2; 4, 2, 1 |
| S3 | ps qs ps | 5 | 13 | 22 | 27 | 31 | 31 turns; j = 2; 4, 2, 2 |
| S4 | ps pq | 1 | 4 | 9 | 18 | 29 | 20 turns; j = 2; 5, 4 |
| S3 | qr pq qr p | 0 | 0 | 2 | 8 | 17 | 17 turns; j = 32; 3, 2, 3, 1 |
| S3 | ps qs ps q | 0 | 0 | 1 | 8 | 16 | 16 turns; j = 2; 4, 2, 2, 1 |
| S3 | pq px qx | 4 | 6 | 8 | 10 | 12 | 2 turns; j = 33; 991, 2, 12 |
| S4 | ps qs ps q | 0 | 0 | 1 | 4 | 8 | 8 turns; j = 2; 4, 2, 2, 1 |

| a | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Members off the route and the lines | 1,446 | 2,142 | 2,853 | 3,917 | 4,963 | 6,438 | 7,906 | 9,896 | 11,861 | 14,406 | 16,950 |
| Kinds | 88 | 89 | 95 | 99 | 98 | 99 | 103 | 105 | 106 | 109 | 108 |
| Kinds with at least a members | 29 | 31 | 32 | 32 | 33 | 35 | 35 | 36 | 36 | 38 | 40 |
| Words with 4 runs | 7 | 5 | 8 | 8 | 10 | 8 | 16 | 24 | 36 | 47 | 62 |
| Words with 5 runs | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 |

- **Three sorts of kind.**
  - *One mutation off the route*: "r" and "s". These are families with the two indices of the route, turn and position (§5.2).
  - *Lines on another pair of weight 2.* "rs" is a line of steps on the pair (r, s), on which the turn is one step. At position 2 there are two arrows p → s, and at position m − 1 two arrows r → q; "ps" and "qr" are the lines on these pairs. Their members have the indices of the seed and the length of the run.
  - *Words that change pair*, such as "ps q", "qr pq qr", "ps qs ps q". They start at positions 0, 2, m − 1 and m, the two ends of the cycle, where some pairs have 0 or 1 arrows. These are the beginnings of the spirals of §6.
- **The kinds with x.** "pq x", "pq px", "pq px qx", "pq qx" and a few longer ones hang at the far end of the forward lines of the turns 3 and 4, of the backward line of the second round and of the last backward line. Together they have at most 52 members for a ≤ 16.
- **The list is not stable.** Each of the kinds "ps qs ps q" and "qr pq qr p" is empty up to a = 11 in S3 and has 16 or 17 members at a = 16; in S4 they start at a = 12 and a = 13. Words with four runs go from 7 to 62. About ten kinds near Q_a (stretch S1) occur for one parity of a only.

A larger range is in `np_qa_core_kinds.log`: mode chain, where only the members that are not passed through are stored and the words are those of the search, so the counts are not those of the table above. Kinds of stored members: 109 at a = 6, 132 at a = 12, 133 at a = 16, 143 at a = 24, 157 at a = 32, 171 at a = 40 and 175 at a = 48; kinds with at least a members: 33, 41, 43, 49, 55, 59 and 59. Neither number settles.

### 5.2 A family whose domain is not an orthant

Take the route quiver at position j with state (A, B, U, V), after the bottom, with U < 0. The mutation at r adds (m − j)·|U| to b_px, because there are m − j arrows p → r and |U| arrows r → x. `np_qa_core.py region` compares (`np_qa_core_region.log`):

| a | Route quivers after the bottom with U < 0 | μ_r is a member, and A + (m − j)·\|U\| < H | μ_r has height ≥ H, and A + (m − j)·\|U\| ≥ H | Other cases | Forks |
|---|---|---|---|---|---|
| 8 | 1,962 | 1,020 | 942 | 0 | 0 |
| 12 | 6,734 | 3,429 | 3,305 | 0 | 0 |
| 16 | 16,082 | 8,127 | 7,955 | 0 | 0 |
| 24 | 54,650 | 27,464 | 27,186 | 0 | 0 |

> **Correction (note 23):** The first column counts the route quivers from the round of the bottom on, including positions 0 to 3 of that round, which come before the bottom step. Strictly after the bottom there are 1,958 at a = 8, not 1,962. All five columns reproduce exactly with this convention, at a = 8, 12, 16 and 24.

So μ_r of the route quiver is a member exactly where A + (m − j)·|U| < H(a). After the t-th turn of the last stretch A = A_t + j and |U| = c − 2t, so the condition is

A_t + j + (m − j)(c − 2t) < H(a).

In the plane of the indices (t, j) this is the region on one side of a hyperbola, and about half of the route lies in it. The family "μ_r of a route quiver" is therefore a member on a region that is not an orthant in t, j or in any shift of them. Some of its own exits are members in turn, on smaller regions: the words r q at position m − 1 and r s in the last rounds, for example.

Note 16 certifies a verdict on a domain {variable ≥ bound} by expanding a polynomial at the bounds. To use it here one would declare μ_r of every route quiver a member, whatever its height, and certify the exits of that larger family; where an exit is neither high nor a fork on the whole domain, it becomes a family too. Whether this ends after finitely many families was not tried, and by §6 no list that is independent of a can be complete.

---

## 6. The spirals

### 6.1 Ten mutations on three vertices

Consider a quiver on p, q, r, s in which p, q, s carry the triangle T₀: two arrows q → p, one arrow q → s, none between p and s. Write the entries of r as (b_rp, b_rq, b_rs) = (−α, β, −γ). W_m(0) is this quiver with (α, β, γ) = (m, m + 1, 2).

**Proposition 20.3 (the spiral) [I].** Let β > 0, 0 ≤ α ≤ β and 0 ≤ γ ≤ β/2. Apply the ten mutations q, p, q, s, p, s, p, s, q, p in this order.
1. Before each of them there are arrows from r to the vertex that is mutated.
2. After the ten mutations the triangle on p, q, s is T₀ again, with the same labels, and the entries of r are (−α′, β′, −γ′) with

   α′ = −23α + 42β − 12γ,  β′ = −42α + 76β − 21γ,  γ′ = −12α + 21β − 5γ.

3. Again β′ > 0, 0 ≤ α′ ≤ β′ and 0 ≤ γ′ ≤ β′/2, and β′ ≥ 23.5·β.
4. After each of the ten mutations two of the vertices p, q, s are joined by fewer than two arrows. So none of the quivers is a fork.

Hence, for every a ≥ 2, the mutations (q p q s p s p s q p)^k applied to W_m(0) give quivers of the class of R_a that are not forks, pairwise not isomorphic, of heights β_k ≥ 23.5^k·(m + 1). The matrix of (2) has determinant 1 and characteristic polynomial (t − 1)(t² − 47t + 1), with roots φ⁸ = (47 + 21√5)/2 ≈ 46.98, 1 and φ⁻⁸.

*Proof.* A mutation at k ∈ {p, q, s} with b_rk > 0 replaces b_rj by b_rj + b_rk·[b_kj]₊ and b_rk by −b_rk. The table follows the triangle and the entries of r.

| Step | Mutation at | b_rk before it | Entries of r after it (b_rp, b_rq, b_rs) | Triangle after it (b_pq, b_ps, b_qs) |
|---|---|---|---|---|
| | | | (−α, β, −γ) | (−2, 0, 1) |
| 1 | q | β | (2β − α, −β, β − γ) | (2, 0, −1) |
| 2 | p | 2β − α | (α − 2β, 3β − 2α, β − γ) | (−2, 0, −1) |
| 3 | q | 3β − 2α | (4β − 3α, 2α − 3β, β − γ) | (2, −2, 1) |
| 4 | s | β − γ | (6β − 3α − 2γ, 2α − 3β, γ − β) | (0, 2, −1) |
| 5 | p | 6β − 3α − 2γ | (−(6β − 3α − 2γ), 2α − 3β, 11β − 6α − 3γ) | (0, −2, −1) |
| 6 | s | 11β − 6α − 3γ | (16β − 9α − 4γ, 8β − 4α − 3γ, −(11β − 6α − 3γ)) | (0, 2, 1) |
| 7 | p | 16β − 9α − 4γ | (−(16β − 9α − 4γ), 8β − 4α − 3γ, 21β − 12α − 5γ) | (0, −2, 1) |
| 8 | s | 21β − 12α − 5γ | (26β − 15α − 6γ, 8β − 4α − 3γ, −(21β − 12α − 5γ)) | (−2, 2, −1) |
| 9 | q | 8β − 4α − 3γ | (42β − 23α − 12γ, −(8β − 4α − 3γ), −(21β − 12α − 5γ)) | (2, 0, 1) |
| 10 | p | 42β − 23α − 12γ | (−(42β − 23α − 12γ), 76β − 42α − 21γ, −(21β − 12α − 5γ)) | (−2, 0, 1) |

With α ≤ β and γ ≤ β/2 the ten entries of the third column are at least β, β, β, β/2, 2β, 3.5β, 5β, 6.5β, 2.5β and 13β, which gives (1), and the last row gives (2). For (3): α′ ≥ 13β > 0; β′ − α′ = 34β − 19α − 9γ ≥ 10.5β; γ′ ≥ 6.5β; β′/2 − γ′ = 17β − 9α − 5.5γ ≥ 5.25β; β′ ≥ (76 − 42 − 10.5)β. (4) is read off the last column: every triangle has an entry 0 or ±1. The quivers after 10k mutations have height β_k, since α_k ≤ β_k, γ_k ≤ β_k/2 and the triangle has entries ≤ 2; these heights increase strictly, so the quivers are pairwise not isomorphic. A quiver with a pair of vertices joined by fewer than two arrows is not a fork. ∎

`np_qa_core.py spiral` checks the table on 20,000 random triples (200,000 mutations) and statement (3) on the four rays of the cone (`np_qa_core_spiral.log`).

**Remarks.**
- **The same mechanism as the route, one vertex down.** On the spiral the vertex r is never mutated. The three vertices p, q, s go round a cycle of ten mutations, and r follows as the fifth vertex follows the bounce cycle in note 18. For Q_a the slopes of x come down to (1, 2), and the height of the route is a polynomial in a. Here one round multiplies the entries of r by a matrix with an eigenvalue 46.98, and they grow geometrically.
- **Runs of five.** The first three mutations q, p, q are the positions −1, −2, −3 of the backward line of §4. After them the ten mutations are five steps on the pair (s, p) and five on the pair (q, p), in fixed labels. Along a run the height grows by a constant d. For the runs after the first three mutations, d₁ = 2m + 3, d₂ = 15m + 16 and d_{i+1} = 7d_i − d_{i−1} + (m − 4), measured on 8 runs at a = 6 and 5 at a = 96; the ratio d_{i+1}/d_i tends to φ⁴ = (7 + 3√5)/2 ≈ 6.854 (`np_qa_core_forkless.log`).
- **The other end.** By Lemma 18.1(3) the opposite of W_m(j) is W_m(m + 1 − j) with p ↔ q and r ↔ s exchanged. So the opposite spiral starts at W_m(m + 1), one step beyond the last position, with s as the passive vertex.
- **Five vertices.** Apply the same mutations to a 5-vertex quiver X whose part on p, q, r, s is W_m(0), for example the route at position 0 of any round. Every quiver obtained has a pair among p, q, s with fewer than two arrows, so none is a fork, and their heights are unbounded. So the class of Q_a contains infinitely many quivers that are not forks, and those that are reached through quivers of height < H(a) are members of K(a).

### 6.2 How much of the class of R_a is not a fork

`np_qa_core.py forkless` computes, on four vertices, the quivers of the class of R_a that are reached from the bounce cycle through quivers of height below a cap that are not forks (`np_qa_core_forkless.log`). The table gives the number of them off the cycle and, after the stroke, their largest distance from the cycle.

| a | H(a) | Cap 4a² | H | 4H | 16H | 256H | H² | H³ |
|---|---|---|---|---|---|---|---|---|
| 6 | 763 | 27 / 7 | 65 / 11 | 113 / 15 | 163 / 18 | 261 / 25 | 349 / 29 | 815 / 45 |
| 12 | 6,496 | 35 / 9 | 83 / 15 | 139 / 19 | 187 / 23 | 283 / 29 | 461 / 38 | 1,107 / 60 |
| 24 | 53,602 | 41 / 10 | 101 / 19 | 157 / 23 | 207 / 26 | 299 / 33 | 581 / 48 | 1,339 / 75 |
| 48 | 435,526 | 51 / 13 | 121 / 23 | 175 / 26 | 227 / 30 | 321 / 37 | 667 / 56 | 1,577 / 90 |
| 96 | 3,511,438 | 57 / 14 | 139 / 26 | 191 / 30 | 245 / 34 | 315 / 40 | 763 / 65 | 1,789 / 104 |

> **Correction (note 23):** "The cycle" here is W_m(0), …, W_m(m). Note 18 counts the m + 2 quivers W_m(0), …, W_m(m + 1), and with that convention every count of the table is one less. With the convention stated, an independent search reproduces the row a = 6 up to cap H², the column "Cap H", and 57 / 14 at a = 96.

- **It never closes.** For a fixed a the number grows with the cap, as Proposition 20.3 says it must. Each factor 4 in the cap adds about 50 quivers.
- **Below H(a) it grows like log a**: 65, 83, 101, 121, 139 for a = 6, 12, 24, 48, 96, about 18 for each doubling of a.
- **Where.** At a = 96 the 139 quivers hang from the positions 0, 1, 2 (34, 10 and 60 of them) and 2a, 2a + 1 (33 and 2). The longest word from position 0 is q p q, then runs of five steps on (s, p), (q, p), (s, p), (q, p) and three more steps: the spiral, with heights 194, 195, 196, 197, 581, 970, …, 2,123,524, 3,073,155 < H(96) = 3,511,438. The others lie within a few mutations of the spirals.
- On four vertices every other mutation of the cycle and of these quivers is a fork or reaches the cap.

### 6.3 The spirals in the core

`np_qa_core.py ends` takes the stored members of K(a) (mode chain, grown from the route) and looks at their 4-vertex parts, the quivers without x (`np_qa_core_ends.log`).

| a | 6 | 8 | 12 | 16 | 24 | 32 | 40 | 48 |
|---|---|---|---|---|---|---|---|---|
| Quivers of the class of R_a below H(a), not forks, off the cycle (§6.2) | 65 | 71 | 83 | 91 | 101 | 109 | 117 | 121 |
| … their largest distance from the cycle | 11 | 13 | 15 | 17 | 19 | 20 | 22 | 23 |
| 4-vertex parts of stored members of K(a), not forks, off the cycle | 66 | 70 | 82 | 94 | 98 | 102 | 110 | 114 |
| … of these among the quivers of the first row | 46 | 49 | 54 | 61 | 67 | 70 | 77 | 81 |
| … their largest distance from the cycle | 8 | 10 | 10 | 12 | 13 | 12 | 14 | 15 |
| Stored members of K(a) over such parts | 811 | 1,358 | 2,988 | 5,189 | 11,545 | 20,408 | 31,657 | 45,417 |

- **The core follows the spirals, and further as a grows.** The 4-vertex parts off the cycle go from 66 to 114, and the farthest from 8 to 15 mutations from the cycle. With the fifth vertex attached the heights are larger than on four vertices, so the core stops earlier than the 4-vertex class does (23 mutations at a = 48).
- **Many states of x over each.** At a = 48 there are 45,417 stored members over 114 parts: the same 4-vertex quiver occurs with the states of x of many rounds. This is about 0.4a³ members.
- **Parts outside the first row** (20 at a = 6, 33 at a = 48) are not reached from the cycle through quivers that are not forks, on four vertices and below H(a). In the core they are reached through members whose 4-vertex part is a fork, or after a mutation at x. They were not examined further.

> **Correction (note 23):** The 4-vertex part of a member depends on which labelled representative the search keeps, because the class contains relabellings of Q_a that move x (note in §3). An independent search keeps the first breadth-first representative grown from the route. At a = 6 it finds 59 parts and 804 members over them, where the table has 66 and 811; at a = 8 it finds 65 and 1,353, where the table has 70 and 1,358. The rows "among the first row" and "largest distance" agree. The table describes the search, not K(a).

---

## 7. The conjecture for a ≤ 64

**Theorem 20.4 [I, by exhaustive computation].**
1. Let 2 ≤ a ≤ 48. The set of all quivers that Q_a reaches through quivers of height < H(a) contains no quiver of height ≤ a + 1 other than Q_a. No pruning is used.
2. Let 49 ≤ a ≤ 64. The set of quivers that Q_a reaches through quivers of height < H(a), forks not expanded, contains no quiver of height ≤ a + 1 other than Q_a, and no fork of height ≤ a + 1 is met.

So for 2 ≤ a ≤ 64 every route from Q_a to a quiver of height ≤ a + 1 that is not isomorphic to Q_a has height at least H(a), and with Theorem 18.4 the quivers Q_a and −Q_a are joined at exactly H(a). For 49 ≤ a ≤ 64 this uses Lemma 15.5.

**Corollary 20.5 [I].** F(5, w) ≥ H(w − 1) ≥ 4w³ − 15w² + 19w − 11 for 3 ≤ w ≤ 65.

*Method* (`np_qa_core.py family`; `np_qa_core_family_nofork.log` for (1), `np_qa_core_family.log` for (2)). Mode chain of §2.2 with the single seed Q_a. The search ends with every exit of every stored member classified, and it counts the members of height ≤ a + 1 among the stored ones; a member of height ≤ a + 1 is always stored. Entries are 64-bit integers, every quiver with an entry ≥ H(a) is discarded, and H(64) < 2²⁰.

| a | 22 | 26 | 32 | 40 | 48 | 56 | 64 |
|---|---|---|---|---|---|---|---|
| w = a + 1 | 23 | 27 | 33 | 41 | 49 | 57 | 65 |
| H(a) | 41,171 | 68,313 | 128,046 | 251,258 | 435,526 | 693,138 | 1,036,382 |
| H / w³ | 3.38 | 3.47 | 3.56 | 3.65 | 3.70 | 3.74 | 3.77 |
| H / w^{5/2} | 16.2 | 18.0 | 20.5 | 23.3 | 25.9 | 28.3 | 30.4 |
| Quivers below H, no pruning | 61,875,173 | 142,619,202 | 402,712,351 | 1,228,877,393 | 3,057,734,065 | – | – |
| … of these stored | 131,864 | 209,209 | 371,928 | 693,380 | 1,157,906 | – | – |
| Quivers below H, forks not expanded | 18,945,464 | 44,205,101 | 126,448,965 | 390,321,574 | 978,814,710 | 2,127,520,764 | 4,165,617,632 |
| … of these stored | 57,618 | 91,197 | 162,487 | 304,661 | 512,065 | 797,003 | 1,171,845 |
| Quivers of height ≤ a + 1 among them | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

All 47 values of a pass without pruning and all 63 with forks not expanded: the set is closed, it has one quiver of height ≤ a + 1, and with pruning no fork of height ≤ a + 1 is met. Over all a the two runs visit 26,022,613,227 and 46,287,598,375 quivers. Without pruning the number of quivers below H is 12.0·a⁵ at a = 32 and at a = 48. The chains that are passed through are runs of mutations alternating between two vertices, that is, lines of steps on one pair; over all a, 8 of the walks along a chain do not alternate in the run with pruning, and 2 in the run without.

**What is new against Theorem 18.5.** The search is the same, but a quiver with exactly two neighbours below H(a) is not stored. The search then stores about 4.5a³ quivers with pruning and 10.5a³ without, in place of 3.9a⁵ and 12a⁵: 1,171,845 of 4,165,617,632 at a = 64, and 1,157,906 of 3,057,734,065 at a = 48 without pruning. The time is still of order a⁵, because every quiver of a line is visited. With Proposition 20.2 and Lemma 20.1 the lines could be crossed in one stride; this was not programmed.

---

## 8. What blocks a certificate, and what a proof would need

**The method of note 16** lists families of quivers with polynomial entries, each on a domain {variable ≥ bound}, and certifies for every family and every vertex that the mutation is a member, has height ≥ the barrier, or is a fork higher than the start. For P⁺_t there are two lines, two backward lines and 14 derived kinds, each with at most one index besides t.

**What the core of Q_a has instead.**

| Part of the core | Members | Families | Entries | Status |
|---|---|---|---|---|
| The route (first half) | ≈ 4a³ | 4 stretches, indices (turn, position) | polynomial (Theorem 18.4) | closed forms proved |
| Lines beyond the ends of the rounds | ≈ 4a⁵ | 2, indices (turn, length) | polynomial (Proposition 20.2) | closed forms proved; exits high by Lemma 20.1 except within about √H of an end |
| Branches near the route | 4a³ to 5a³ | 88 to 109 kinds for 6 ≤ a ≤ 16, up to five indices | expected polynomial, not derived [H] | open: domains bounded by quadrics (§5.2) |
| The two spirals and what hangs on them | on four vertices 65 to 139 quivers for a = 6 to 96, each with the fifth vertex in many states (§6.3) | grows with a | geometric along the spiral (Proposition 20.3) | open: needs an induction along the spiral |

**The obstacles, in order of weight.**

1. **An unbounded number of families (the spirals).** For every bound N there is an a from which on the core contains words from the route with more than N runs [H: Proposition 20.3 gives the quivers and that they are not forks; that enough of them lie below H(a) with the fifth vertex attached is measured, §6.3]. The entries of a spiral are not polynomials in its index. So no finite list of families with polynomial entries describes K(a) for all a, nor a closed set that contains it. A proof must treat the spirals by another argument. Lemma 15.5 does not cut them off: their quivers are not forks. Pre-forks do not either: without expanding the pre-forks (note 14 §3) of total weight above 10(a + 1), the core loses 36 members at a = 6 and 110 at a = 16 (`np_qa_core.py prefork`, `np_qa_core_prefork.log`).

   > **Correction (note 23):** The conclusion does not follow (note at §1 item 6). Families parametrised by their state on cones, which the round of ten mutations maps linearly, are not ruled out, and the plan for the spirals below is of that kind. What the measurement supports is that families indexed by the words from the route grow in number with a.
2. **Domains that are not orthants.** The families one mutation off the route are members on regions such as A_t + j + (m − j)(c − 2t) < H(a). A certificate needs either a cover of such regions by charts on which the polynomial test works, or the detour of §5.2 through larger families.
3. **Volume.** About a hundred families with two to five indices, each with five exits, on several charts and for both parities of a, against 938 claims for P⁺_t.

**What would close the gap.**

- **For the lines**: nothing more.
- **For the spirals**: a statement of the following form, by induction on the number of rounds of ten mutations. *If X is a member of K(a) whose part on p, q, s is one of the ten triangles of Proposition 20.3 and whose entries at r and x satisfy the sign conditions of that round, then each exit of X is the next or the previous quiver of the spiral, or a quiver one mutation off it whose own exits are high or forks, or has height ≥ H(a), or is a fork.* The entries after k rounds are the k-th power of a 3 × 3 matrix applied to the start, for r and for x; the inequalities are then statements about a linear recurrence, as in (3) of the proposition. This was not attempted.
- **For the branches**: closed forms by Lemmas 16.1 and 16.2, since every branch is made of runs of steps on a pair of weight 2 and single mutations; then verdicts on regions cut out by the inequality "the entry of the parent is < H(a)".
- **Another route to a proof [H].** At most 52 members have a mutation at x in their word for a ≤ 16 (§3). If the mutation at x could be shown to be high or a fork for every member reached without mutating x, apart from an explicit list, the problem would reduce to routes that never mutate x. On such routes the four vertices p, q, r, s move in the class of R_a and the row of x follows by a piecewise linear rule. A route whose 4-vertex part enters a fork higher than a + 1 stays in forks with growing entries until x is mutated (Lemma 15.4), so only the cycle, the two spirals and the 4-vertex forks above them matter. This is a different organisation of the same work, not a shortcut that was found.

  > **Correction (note 23):** "Routes that never mutate x" has to be read in a fixed labelling. At a member where x and another vertex v are joined by one arrow, the pentagon x v x v x exchanges them (note in §3). So the explicit list would have to contain every such member below H(a). The 52 members of §3 count the words the search kept, not a property of K(a).

**Does anything speak against the conjecture?** No. For 2 ≤ a ≤ 64 the core has one member of height ≤ a + 1. The anatomy is the same for a = 6 to 16, where it was sorted in full, and the numbers of quivers on the lines follow the closed forms of §4.

---

## 9. Limitations

- **No theorem for every a about the barrier.** Proposition 20.2, Lemma 20.1 and Proposition 20.3 hold for every a, but they do not bound the height of a route. Conjecture 18.7(a) is open for a ≥ 65.
- **Theorem 20.4 is a computation.** It rests on `np_qa_core.c` and on the argument of §2.2 that a quiver with two neighbours need not be stored. The program was checked against `np_barrier` and against mode plain for a ≤ 16, against `np_barrier` with pruning up to a = 24 and without pruning up to a = 22 (§2.3). For 49 ≤ a ≤ 64 it uses Lemma 15.5. The second search of Theorem 18.5, which finds −Q_a at exactly H(a), was not repeated; that Q_a and −Q_a are joined at H(a) is Theorem 18.4.
- **The kinds are a description, not a partition into proved families.** A kind is defined by the word that the breadth-first search happened to find. Two words can lead to quivers of one family, and one skeleton can cover several. The counts of kinds are those of this bookkeeping. No closed form was derived for a kind off the lines.
- **"Unbounded number of families" is measured, not proved.** Proposition 20.3 proves that the spirals exist and are not forks. How far they reach inside K(a), with the fifth vertex attached, is measured for a ≤ 48 (§6.3) and for the 4-vertex class for a ≤ 96 (§6.2).
- **§6.2 is a search from the cycle with a cap.** It counts the quivers reached from the cycle through quivers that are not forks and lie below the cap. A quiver that is not a fork and is reached only through forks is not counted.
- **The ends of the lines are measured.** Proposition 20.2 gives the quivers of a line up to the bottom of the column of x. That the line ends at a fork three or four quivers later, and the numbers of quivers in §4.2, are checked for a ≤ 12.
- **The full anatomy (mode plain) stops at a = 16.**
- **Prior art.** No search of the literature was made for this note.

---

## 10. Reproduce

```bash
PY=python
$PY -I np_corridor.py build                                   # np_barrier, for crosscheck
$PY -I np_qa_core.py build                                    # gcc -O2, binary in ~/.cache/qmb-np/
$PY -I np_qa_core.py crosscheck --a 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 20 22 24 > np_qa_core_crosscheck.log
$PY -I np_qa_core.py anatomy --a 6 7 8 9 10 11 12 13 14 15 16 > np_qa_core_anatomy.log
$PY -I np_qa_core.py lines --amin 3 --amax 12 > np_qa_core_lines.log
$PY -I np_qa_core.py branches --a 6 7 8 9 10 11 12 13 14 15 16 > np_qa_core_branches.log
$PY -I np_qa_core.py region --a 6 8 10 12 14 16 20 24 > np_qa_core_region.log
$PY -I np_qa_core.py kinds --a 6 7 8 9 10 11 12 13 14 15 16 18 20 22 24 28 32 36 40 44 48 > np_qa_core_kinds.log
$PY -I np_qa_core.py ends --a 6 8 10 12 14 16 20 24 28 32 36 40 44 48 > np_qa_core_ends.log
$PY -I np_qa_core.py forkless > np_qa_core_forkless.log
$PY -I np_qa_core.py spiral > np_qa_core_spiral.log
$PY -I np_qa_core.py prefork --a 6 8 10 12 14 16 > np_qa_core_prefork.log
$PY -I np_qa_core.py family --amin 2 --amax 64 --workers 12 --out np_qa_core_family.jsonl > np_qa_core_family.log
$PY -I np_qa_core.py family --mode chain-nofork --amin 2 --amax 48 --workers 12 \
    --out np_qa_core_family_nofork.jsonl > np_qa_core_family_nofork.log
$PY -I np_qa_core.py compare18 > np_qa_core_compare18.log
$PY -I np_qa_core.py rerun > np_qa_core_rerun.log
```

- `np_qa_core.py` needs `np_rowwalk.py`, `np_corridor.py`, numpy from the venv and, for `crosscheck`, the binary of `np_barrier.c`.
- The cores are cached in `~/.cache/qmb-np/qa_core/` (1.7 GB for the runs above; the files were deleted afterwards and are rebuilt when needed); `--fresh` recomputes.
- The two `family` runs and `kinds` ran at the same time, up to 25 processes on 16 cores, so the times in the logs are upper bounds: 3,168 s for a = 64 with pruning and 2,264 s for a = 48 without. The run with pruning took the results for a ≤ 16 and a = 18, 20, 22, 24 from the cache that `crosscheck` had filled; its log shows 0.0 s for them.
- The run with pruning was started with the binary as it was before the variants without the fork test were added to `np_qa_core.c`. With the final binary, 60 of the searches were repeated (with pruning for a = 2 to 36, without for a = 2 to 26): same numbers of quivers, of stored quivers and of quivers of height ≤ a + 1 (`np_qa_core.py rerun`, `np_qa_core_rerun.log`).
- `core` is a short form of `anatomy` and was used only while the program was written.

---

## Sources

- [Note 18](18-five-vertices-cubic-barrier.md): the family Q_a, the bounce cycle (Lemma 18.1), the rules for the fifth vertex (Lemma 18.2), the route (Theorem 18.4), the searches (Theorem 18.5) and Conjecture 18.7.
- Notes [15](15-rank-2-orbits-and-the-constant-2.md) and [16](16-five-vertices-above-w-squared.md): Lemma 15.4 (mutations of a fork), Lemma 15.5 (fork exclusion), Lemma 16.1 (step), and the method of the certificate of Theorem 16.6. [Note 14](14-opposite-quivers-forks-and-cores.md) §3: forks, pre-forks, and the oriented triangles of a fork (consequence (a)).
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Def. 2.1 and Lemma 2.5, as quoted in notes 15 and 19 (not read here): https://d-nb.info/1214302807/34
