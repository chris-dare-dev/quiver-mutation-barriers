# 16. Five vertices force barriers above w²: F(5, w) ≥ 2w^{5/2} − 11w²

*Run on 2026-11-11. The aim was to find out whether more vertices force barriers of higher degree than the w(w − 1) of Theorem 9.1, by construction and targeted search on 5 and 6 vertices. Code: [experiments/np_corridor.py](../experiments/np_corridor.py), [experiments/np_barrier.c](../experiments/np_barrier.c) and [experiments/np_corridor_prove.py](../experiments/np_corridor_prove.py) (all new). Results: the `np_corridor_*` files in `experiments/`. Quivers are up to relabelling. A 5-vertex quiver is written as the tuple (b01, b02, b03, b04, b12, b13, b14, b23, b24, b34); b_ij > 0 means b_ij arrows i → j. Height means maximal entry, and a route is a sequence of mutations, as in [note 15](15-rank-2-orbits-and-the-constant-2.md). [x]₊ = max(x, 0). Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 17):** Checked in [note 17](17-checks-of-note-16.md) with new code (`review17.py`). No theorem was found false. For Theorem 16.6, all 766 exits of the certificate were certified again with PARI and with independent mutation and fork tests, the targets of the 161 verdicts "member" were checked at the true parameters, and the claims cover every member: the argument of §4.1 closes. For Theorem 16.5, the counts were reproduced for all 63 values of t and both families, and the search for P⁺_t was continued to t = 80. Lemma 15.5 holds on any number of vertices. Five small points are corrected below: §1 items 2 and 6, the table of claims in §4.1, the core at t = 5 in §4.2, and the budget shares in §6.2.

> **Follow-up (note 18):** The routes of §6 "over several pairs of weight 2" are walks round one cycle on four vertices, with a fifth vertex that is never mutated, and they give more than w^{5/2}. The quiver Q_a = (−(a − 3), a − 2, a + 1, −(a + 1), −(a + 1), −a, 2, −2, −a, −(a + 1)), of height w = a + 1, joins its opposite at exactly 4a³ − 3a² + O(a) for 2 ≤ a ≤ 22: the route is proved for every a, and the lower bound is an exhaustive search without pruning. So F(5, w) ≥ 4w³ − 15w² + 19w − 11 for 3 ≤ w ≤ 23, which is 41,171 = 16.2·w^{5/2} at w = 23, and the upper half of Conjecture 16.9 is withdrawn (§7). Theorems 16.4 to 16.6 and Corollary 16.7 are not affected. See [note 18](18-five-vertices-cubic-barrier.md).

---

## 1. Outcome

1. **A 5-vertex quiver and its opposite that are joined only at 2w^{5/2} − w² + w − 1 [I, proved with computer assistance].** For t ≥ 2 let

   P⁺_t = (1, −(t² − 1), −t(t − 1), t², −2, t(t − 1), t², −t², t² − 1, −2t),  H⁺(t) = 2t⁵ − t⁴ + t² − 1.

   P⁺_t has height w = t² and is not isomorphic to its opposite −P⁺_t.
   - **The route (Theorem 16.4, by hand).** A route of 4t³ − 2t² + 4 mutations leads from P⁺_t to −P⁺_t. Exactly one quiver on it has height H⁺(t); all others are at most H⁺(t) − t².
   - **No lower route, 2 ≤ t ≤ 64 (Theorem 16.5, exhaustive search).** For each of these t, the set of all quivers that P⁺_t reaches through quivers of height below H⁺(t) was computed in full, with no pruning. It contains no quiver of height ≤ t² other than P⁺_t.
   - **No lower route, every t ≥ 8 (Theorem 16.6, symbolic certificate).** By note 15's Lemma 15.5 a reduced route between quivers of height ≤ t² passes no fork higher than t². The quivers that remain usable below H⁺(t) lie on two lines of steps on a pair of weight 2 and on short branches. `np_corridor_prove.py` certifies 766 exits of these quivers, with entries that are polynomials in t and the position: each is another member, has height ≥ H⁺(t), or is a fork higher than t².

   So f(P⁺_t, w) ≥ 2t⁵ − t⁴ + t² − 1 for every t ≥ 2 and t² ≤ w < H⁺(t).
2. **F(5, w) ≥ 2w^{5/2} − 11w² for every w ≥ 4 (Corollary 16.7) [I].** So F(5, w)/w² is unbounded: a polynomial F(5, w) has degree at least 5/2, and Conjecture 10.1 (F(4, w) ≤ 2w²) has no analogue with any constant on 5 vertices. At w = 4,096 the barrier is 2,130,710,527 = 127.0·w². Theorem 9.1 and Proposition 12.1 gave w(w − 1) for every n ≥ 4; note 15 gave 2w² − 7w + 2 on 4 vertices (Corollary 15.14).
   > **Correction (note 17):** A polynomial has an integer degree. What is proved is that F(5, w) grows at least like w^{5/2}; a polynomial bound for F(5, w) therefore has degree at least 3. The constant 11 is the best one for all w: on w = (t + 1)² − 1 the least constant tends to 11 from below, and with 10 the inequality fails first at w = 783 ([note 17](17-checks-of-note-16.md) §6).
3. **The mechanism is a chain of two counters [I].** The four vertices p, q, c₁, c of P⁺_t carry note 15's quiver Q_t: a pair of weight 2 and two other vertices whose entries at the pair run through arithmetic progressions. The first, c₁, runs down in t − 1 steps while c climbs to about 2t³. A mutation at c₁ then turns c into a counter that takes about 2t³ steps to run down. The fifth vertex x climbs by t² at each of those steps. At the top, the mutation at c and the next step on the pair give opposite quivers (Lemma 16.3), and the second half of the route is the mirror image of the first.
4. **Within this design, 5/2 is the limit, on any number of vertices [I, H].** The identity at the top forces the vertices other than the pair to form a star around the last counter. Counters then cannot drive one another, and the number of steps is at most about 2w·√((n − 4)·w) (§5). Measured: with two counters on 6 vertices the barrier is 1.33·w^{5/2} at w = 32, and with three on 7 vertices 1.66·w^{5/2} at w = 48, against at most 0.99·w^{5/2} for the same construction with one (P_t, §3).
5. **At small w other routes are higher, and their growth is not known [I].** A census of the 5-vertex quivers of height w whose every mutation is higher (§6.1) gives, as the largest escape level found, 14 at w = 2, 70 at w = 3 and 107 at w = 4 (on 4 vertices: none, 12 and 28). Fixed 4-vertex quivers with a fifth row give 272 at w = 5 and 437 at w = 6 (§6.2). These routes run for 400 to 1,218 mutations over several pairs of weight 2. P⁺_t gives 51 at w = 4 and 413 at w = 9.
6. **Three kinds of family give nothing above w² [I].**
   - *Rigid quivers* in the style of G_k: of 84,495 templates with entries 0, ±1, ±6, ±7 whose every mutation is above 14, 2,838 escape, by routes of two to five mutations and at most at 49 = w²; none of the others reaches another quiver of height ≤ 7 below 1,000,000 (§6.3).
     > **Correction (note 17):** This holds for the 80,141 templates whose search closed below 1,000,000. For the other 1,516 the search ran over its budget of 5,000 quivers, as §6.3 says, so for them nothing is shown.
   - *A fixed 4-vertex quiver with a growing fifth row*: a route that never mutates the fifth vertex scales linearly with that row (Lemma 16.8), and the measured barriers grow slowly: 70, 102, 111 for rows up to 3, 4, 5 (§6.2).
   - *Counters that bounce*: one pair with two counters of slope 1 gives 15, 36, 48 at w = 3, 4, 5, near 2w² (§6.2).
7. **Conjecture on the degree [H].** Conjecture 16.9: F(5, w) = Θ(w^{5/2}). The lower half is Corollary 16.7. The upper half rests only on the values of item 5, which are 2.5, 4.5, 3.3, 4.9 and 5.0 times w^{5/2} for w = 2 to 6. Whether the degree of F(n, w) grows with n is open (Question 16.10): nothing found here exceeds degree 5/2 for any n.
   > **Follow-up (note 18):** The upper half does not hold up. The fourth family of §6.2 has a closed form and exceeds degree 5/2 on the whole range that could be searched: see the notes in §7.

---

## 2. Steps and turns on a pair of weight 2

Note 15 §3 describes the orbit of two mutations on 4 vertices. The three lemmas below are what the route needs, for any number of vertices. Lemma 16.1 with one other vertex is Theorem 15.1(1) for c = 2, read in the opposite quiver.

**Setting.** A quiver with two vertices p, q joined by two arrows q → p. For every other vertex e put A_e = b_pe and B_e = b_qe, the *column* of e, and S_ef = b_ef for two such vertices. A *step* mutates at p and then exchanges the names p and q. A *backward step* mutates at q and exchanges the names; it undoes a step.

**Lemma 16.1 (step) [I].** After the mutation at p: b′_pq = 2, b′_pe = −A_e, b′_qe = B_e + 2[A_e]₊ and S′_ef = S_ef + [−A_e]₊[A_f]₊ − [A_e]₊[−A_f]₊. So after the exchange of names there are again two arrows q → p, and:
- a column with A_e ≥ 0 becomes (2A_e + B_e, −A_e);
- a column with A_e < 0 becomes (B_e, −A_e);
- if every A_e ≥ 0, no S_ef changes.

A column of the form (a_j, −a_{j−1}) with a_j ≥ 0 therefore becomes (a_{j+1}, −a_j) with a_{j+1} = 2a_j − a_{j−1}. While its first entry stays ≥ 0, the column runs through an arithmetic progression with difference d_e = A_e + B_e, the *slope* of e.

*Proof.* The mutation rule at p is b′_ij = b_ij + [b_ip]₊[b_pj]₊ − [−b_ip]₊[−b_pj]₊ for i, j ≠ p, and it reverses the arrows at p. For (q, e): b_qp = 2 and b_pe = A_e. For (e, f): b_ep = −A_e and b_pf = A_f. ∎

**Lemma 16.2 (turn) [I].** Let y have the column (0, −η) with η ≥ 1: y is not joined to p, and there are η arrows y → q. Let S_ey ≥ 0 for every other vertex e. Then the mutation at y changes only the following: B_e becomes B_e − η·S_ey for every e; the column of y becomes (0, η); every S_ey changes sign. So the slope of e drops by η·S_ey, and the slope of y changes from −η to η.

*Proof.* The arrows at y are y → q and e → y. The only paths through y run e → y → q, and they add S_ey·η to b_eq. ∎

**Lemma 16.3 (the top) [I].** In the situation of Lemma 16.2 suppose also that every A_e ≥ 0, that η·S_ey = 2(A_e + B_e) for every e ≠ y, and that S_ef = 0 whenever e, f ≠ y. Then μ_y(X) = −μ_p(X), with the same labels.

*Proof.* By Lemma 16.1, μ_p(X) has b_pq = 2, b_pe = −A_e, b_qe = B_e + 2A_e, b_py = 0, b_qy = −η and the entries S of X. By Lemma 16.2, μ_y(X) has b_qp = 2, b_pe = A_e, b_qe = B_e − 2(A_e + B_e) = −(B_e + 2A_e), b_py = 0, b_qy = η, the entries −S_ey, and S_ef = 0. These are the entries of −μ_p(X). ∎

**Corollary [I].** If a route R leads from X₀ to X and X is as in Lemma 16.3, then X₀ and −X₀ lie in one mutation class. The route R, then μ_y, then μ_p, then the mutations of R in reverse order leads from X₀ to −X₀, because mutation commutes with reversing all arrows. Its height is the larger of the height of R and the height of μ_p(X).

`np_corridor.py grid` checks the identity of Lemma 16.3 on 4,350 quivers of the kind built in §3, and `family`, `family_plus` check the columns predicted by Lemmas 16.1 and 16.2 at every quiver of the routes of §3 for t = 2 to 64.

---

## 3. The family

### 3.1 The quivers

Name the vertices x = 0, p = 1, q = 2, c₁ = 3, c = 4. Both quivers have the same arrows among p, q, c₁, c:

| Arrow | q → p | p → c₁ | c₁ → q | p → c | q → c | c → c₁ |
|---|---|---|---|---|---|---|
| Weight | 2 | t(t − 1) | t² | t² | t² − 1 | 2t |

This full subquiver is Q_t of note 15 (Theorem 15.6) with its vertices renamed. The fifth vertex is attached in two ways.

| | x and p | x and q | x and c | x and c₁ | Tuple |
|---|---|---|---|---|---|
| **P_t** (D = ⌊t²/2⌋) | p → x, t² | x → q, t² − D | x → c, 2D | none | (−t², t² − D, 0, 2D, −2, t(t − 1), t², −t², t² − 1, −2t) |
| **P⁺_t** | x → p, 1 | q → x, t² − 1 | x → c, t² | c₁ → x, t(t − 1) | (1, −(t² − 1), −t(t − 1), t², −2, t(t − 1), t², −t², t² − 1, −2t) |

Both have height t² for t ≥ 2. In P_t every column starts with a first entry ≥ 0, and x climbs with slope D. In P⁺_t the vertex x starts one step earlier, as an in-neighbour of p; after one step it has slope t², twice as much. Put

N = 2t³ − t² − t,  H(t) = t² + (2t³ − t² + 1)·⌊t²/2⌋,  H⁺(t) = 2t⁵ − t⁴ + t² − 1 = (t + N + 1)·t² − 1.

For even t, H(t) = t⁵ − t⁴/2 + 3t²/2. For odd t, H(t) = t⁵ − t⁴/2 − t³ + 2t² − 1/2.

### 3.2 The route

**Theorem 16.4 [I].** Let t ≥ 2.
1. P⁺_t and −P⁺_t are not isomorphic, and they lie in one mutation class.
2. There is a route from P⁺_t to −P⁺_t with 4t³ − 2t² + 4 mutations. One quiver on it has height H⁺(t), and every other has height at most H⁺(t) − t².
3. The same holds for P_t with H(t) in place of H⁺(t) and ⌊t²/2⌋ in place of t².

*Proof for P⁺_t.* Let K(0) = P⁺_t and let K(j) be the quiver after j steps on the pair (p, q), for 0 ≤ j ≤ t − 1. Let L(0) = μ_{c₁}K(t − 1), and let L(i) be the quiver i steps after L(0), for 0 ≤ i ≤ N + 1. The claim is that these quivers have the following columns and entries.

| | c₁ | c | x | c ↔ c₁ | x → c | x ↔ c₁ |
|---|---|---|---|---|---|---|
| K(0) | ((t − 1)t, −t²) | (t², t² − 1) | (−1, t² − 1) | c → c₁, 2t | t² | c₁ → x, t(t − 1) |
| K(j), 1 ≤ j ≤ t − 1 | ((t − 1 − j)t, −(t − j)t) | (t² + j(2t² − 1), −(t² + (j − 1)(2t² − 1))) | (jt² − 1, −((j − 1)t² − 1)) | c → c₁, 2t | 2t² | none |
| L(i), 0 ≤ i ≤ N + 1 | (it, −(i − 1)t) | (N + 1 − i, −(N + 2 − i)) | ((t − 1 + i)t² − 1, −((t − 2 + i)t² − 1)) | c₁ → c, 2t | 2t² | none |

- **K(0) to K(1).** The columns of c₁ and c have first entry ≥ 0 and slopes −t and 2t² − 1. The column of x has first entry −1, so by Lemma 16.1 it becomes (t² − 1, 1), and the entries from x to c₁ and c gain A_{c₁} = (t − 1)t and A_c = t². They become 0 and 2t².
- **K(j) to K(j + 1), 1 ≤ j ≤ t − 2.** All first entries are ≥ 0, so each column moves one place along its progression (slopes −t, 2t² − 1 and t²) and nothing else changes.
- **K(t − 1) to L(0).** In K(t − 1) the column of c₁ is (0, −t), there are 2t arrows c → c₁, and x is not joined to c₁. Lemma 16.2 with η = t lowers the slope of c by 2t², to −1, and gives c₁ the column (0, t) and slope t. Note t² + (t − 1)(2t² − 1) = N + 1.
- **L(i) to L(i + 1).** All first entries are ≥ 0 for i ≤ N + 1. The slopes are t, −1 and t².
- **The top.** In T = L(N + 1) the column of c is (0, −1). There are 2t arrows c₁ → c and 2t² arrows x → c, which is twice the slopes of c₁ and x, and x and c₁ are not joined. Lemma 16.3 gives μ_c(T) = −μ_p(T).

By the corollary of §2 the route K(0), …, K(t − 1), L(0), …, L(N + 1), μ_c(T) = −μ_p(T), −T, …, −K(0) leads to −P⁺_t. It has 2·(t − 1 + 1 + N + 1) + 2 = 4t³ − 2t² + 4 mutations.

*Heights.* On K(j) and L(i) the largest entry is the first entry of x at L(N + 1), which is (t + N)t² − 1 = H⁺(t) − t²; the entries of c₁ are at most (N + 1)t and those of c at most N + 2. In μ_p(T) the entry between q and x is (t + N + 1)t² − 1 = H⁺(t), and every other entry is smaller.

*Not isomorphic.* In P⁺_t the vertex p has exactly three arrows coming in (two from q and one from x). In −P⁺_t the numbers of incoming arrows are the numbers of outgoing arrows of P⁺_t: t² + 1, 2t² − t, 2t², 2t² − t and 2t. None is 3.

*P_t.* The same argument, without the first case: the column of x is (t² + jD, −(t² + (j − 1)D)) from K(0) on, there are 2D arrows x → c, and x and c₁ are not joined. The top entry is t² + (t + N + 1)D = H(t). In P_t the vertex p has exactly two arrows coming in, and the numbers of outgoing arrows are t² + D, 3t² − t, t² + 1, t² and 2t. ∎

### 3.3 No lower route: exhaustive search for t up to 64

**Theorem 16.5 [I, by exhaustive computation].** Let 2 ≤ t ≤ 64. Every route from P⁺_t to a quiver of height ≤ t² that is not isomorphic to P⁺_t has height at least H⁺(t). The same holds for P_t and H(t).

*Method* (`np_corridor.py family`, `family_plus`; `np_corridor_family.log`, `np_corridor_family_plus.log`). For each t the program `np_barrier` computes the set of all quivers, up to relabelling, that the start reaches through quivers of height at most H − 1. No fork is pruned. The search ends with every exit above H − 1, and the set contains one quiver of height ≤ t², the start. A second search with bound H returns H as the least height at which another quiver of height ≤ t² is reached, and that quiver is the opposite of the start. Products are formed in 64-bit integers and every quiver with an entry above the bound is discarded, so no overflow can occur; H⁺(64) = 2,130,710,527 is below 2³¹.

| t | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 16 | 32 | 64 |
|---|---|---|---|---|---|---|---|---|---|---|
| w = t² | 4 | 9 | 16 | 25 | 36 | 64 | 100 | 256 | 1,024 | 4,096 |
| H⁺(t) | 51 | 413 | 1,807 | 5,649 | 14,291 | 61,503 | 190,099 | 2,031,871 | 66,061,311 | 2,130,710,527 |
| H⁺ / w² | 3.19 | 5.10 | 7.06 | 9.04 | 11.03 | 15.02 | 19.01 | 31.00 | 63.00 | 127.00 |
| H⁺ / w^{5/2} | 1.594 | 1.700 | 1.765 | 1.808 | 1.838 | 1.877 | 1.901 | 1.938 | 1.969 | 1.984 |
| Quivers reached below H⁺ | 157 | 173 | 381 | 726 | 1,247 | 2,961 | 5,803 | 23,980 | 193,929 | 1,561,537 |
| H(t), for P_t | 30 | 193 | 920 | 2,737 | 7,182 | 30,816 | 95,150 | 1,016,192 | 33,031,680 | 1,065,359,360 |
| H / w^{5/2} | 0.938 | 0.794 | 0.898 | 0.876 | 0.924 | 0.940 | 0.952 | 0.969 | 0.984 | 0.992 |
| Quivers reached below H | 46 | 135 | 314 | 597 | 1,037 | 2,463 | 4,828 | 19,971 | 161,575 | 1,301,189 |
| 2w², the bound of Conjecture 10.1 on 4 vertices | 32 | 162 | 512 | 1,250 | 2,592 | 8,192 | 20,000 | 131,072 | 2,097,152 | 33,554,432 |

All 63 values of t pass every check, for both families. The checks are: the height is t²; the columns of the proof at every quiver of the route; the identity of Lemma 16.3; the heights on the route; no isomorphism with the opposite; no other quiver of height ≤ t² below H; the opposite reached at exactly H. Over the 63 values the searches below H visit 25.7 million quivers for P⁺_t and 21.4 million for P_t.

> **Update (note 17):** Another enumerator, in Python integers and with another canonical form, finds the same number of quivers and the same number of mutations that leave the bound for all 63 values of t and both families (25,717,726 and 21,427,901 quivers in all), and one quiver of height ≤ t² each time. Continued for P⁺_t to 65 ≤ t ≤ 80, beyond the 32-bit keys of `np_barrier.c`, it gives the same outcome: the theorem holds for P⁺_t for 2 ≤ t ≤ 80 ([note 17](17-checks-of-note-16.md) §5).

**Checks of the search.**
- `np_corridor.py selftest` (`np_corridor_selftest.log`): the search returns k(k − 1) for G_3 to G_12 and the census extremes 12, 28, 45, 66, 79, 101, 144 of note 10, each with and without fork pruning, and H_t = 2t⁴ − t³ − t² + 2t for note 15's Q_3 to Q_10. The Python mutation agrees with `mutation_path.mutate` on 20,000 random mutations.
- `np_corridor.py pycheck` (`np_corridor_pycheck.log`): for t = 2 to 9 a breadth-first search in pure Python, with Python integers and its own canonical form, finds the same number of quivers below H as `np_barrier` for both families (46 to 3,505 and 157 to 4,223), and one of height ≤ t².

**Remarks.**
- **Mutation-cyclic.** The vertices q, c, c₁ span the oriented triangle q → c → c₁ → q with weights t² − 1, 2t, t². Its Markov constant is −2t⁵ + 2t⁴ + 2t³ + 2t² + 1, which is negative for t ≥ 2, so the triangle is mutation-cyclic by Beineke–Brüstle–Hille [P, as used in note 12 §4], and P_t and P⁺_t are not mutation-acyclic by Warkentin's subquiver theorem [P, as used there]. The bounds of arXiv 2610.36179 do not concern them.
- **More vertices.** Adding isolated vertices gives the same bound for F(n, w), n ≥ 6. For connected quivers, hang a path of weight-1 arrows from x. No mutation of the route is at x, so the route is unchanged and ends at the quiver with the five old vertices reversed and the path kept. For n = 6 and 7 and t = 2, 3, 4, with either orientation of the path, the search finds no quiver of height ≤ t² outside the starting plateau below H(t), and the first one at exactly H(t) (`np_corridor.py pendant`, `np_corridor_pendant.log`; run for P_t, measured and not proved). The starting plateau has 2 quivers for n = 6 and 5 for n = 7: the path can be re-oriented at no cost.
- **Free parameters.** The construction works with a counter of decrement h that is exhausted after m steps, a second column (a₀, 2h² − 1 − a₀), and x = (A_x, D − A_x) with 2D arrows x → c: the quiver `two_counter(h, m, a0, D, Ax)` of the script. The identity at the top holds for all 4,350 parameter sets tried. The escape level equals the height of the route for 3,666 of them. Of the 684 others, 528 have h = 1, where c does not climb. Among the 210 sets with h ≥ 2, a₀ ≥ h², A_x ≥ h² and D ≥ h it fails once (`np_corridor.py grid`, `np_corridor_grid.log`).

---

## 4. No lower route, for every t

**Theorem 16.6 [I, computer-assisted].** Let t ≥ 2. Every route from P⁺_t to a quiver of height ≤ t² that is not isomorphic to P⁺_t has height at least H⁺(t) = 2t⁵ − t⁴ + t² − 1. Hence f(P⁺_t, w) ≥ H⁺(t) for t² ≤ w < H⁺(t), and P⁺_t and −P⁺_t are joined at exactly H⁺(t).

**Corollary 16.7 [I].** F(5, w) ≥ H⁺(⌊√w⌋) ≥ 2w^{5/2} − 11w² for every w ≥ 4. In particular liminf F(5, w)/w^{5/2} ≥ 2 and F(5, w)/w² → ∞. The same bound holds for F(n, w), n ≥ 6, if disconnected quivers are admitted.

*Proof of the corollary.* P⁺_t and −P⁺_t have height t² ≤ w for t = ⌊√w⌋. H⁺ is increasing and ⌊√w⌋ > √w − 1, and 2(s − 1)⁵ − (s − 1)⁴ ≥ 2s⁵ − 11s⁴ for s ≥ 2. ∎ On 4 ≤ w < 4,225 the least constant is 10.57 in place of 11, and H⁺(⌊√w⌋) > 2w² except at w = 6, 7, 8 and 15 (`np_corridor_family_plus.log`, last lines).

### 4.1 The proof

For 2 ≤ t ≤ 64 this is Theorem 16.5. For t ≥ 8 it is the method of note 15 §5.

**Lemma 15.5 [I, note 15; from Warkentin's Lemma 2.5, P].** On a reduced route from X to Y, every fork has height at most max(ht X, ht Y).

**The members.** The script lists families of quivers whose entries are polynomials. In the coordinates of §2:

| Member | c₁ | c | x | c → c₁ | x → c | x → c₁ |
|---|---|---|---|---|---|---|
| K(0) = P⁺_t, K(j), L(i) | as in §3.2 | | | | | |
| M1(k), 3 ≤ k ≤ t − 2: k backward steps from L(0) | ((k − 2)t, −(k − 1)t) | (N + 1 + k, −(N + 2 + k)) | ((t − 1 − k)t² − 1, −((t − 2 − k)t² − 1)) | tN | 2t² | t((t − 2)t² − 1) |
| M2(m), m ≥ 0: t + 1 + m backward steps from L(0) | ((t − 1 + m)t, −(t + m)t) | (N + t + 2 + m, −(N + t + 3 + m)) | (mt² + 1, −((m + 1)t² + 1)) | tN | −(H⁺ − 2t²) | 0 |

Besides these lines there are the quivers between and beyond them, which the script derives by symbolic steps: K(−1), K(−2), K(t), K(t + 1), K(t + 2), and L(−1), L(−2), L(−(t − 1)), L(−t) on the backward line, where the columns of c₁ and of x pass their bottoms. Finally there are the *derived* members: whenever an exit of a member is not certified as high or as a fork, the mutated quiver becomes a member itself, with the same variables. The script finds 14 kinds, none more than two mutations from a line:

μ_x K(0), μ_p μ_x K(0), μ_c K(0), μ_q μ_c K(0), μ_{c₁} μ_c K(0), μ_x K(j), μ_{c₁} μ_x K(j), μ_q μ_x K(1), μ_{c₁} K(j), μ_x L(i), μ_{c₁} μ_x L(i), μ_{c₁} L(i), μ_{c₁} L(N + 1), μ_{c₁} L(−1).

The backward line is the new feature against 4 vertices, where it stops at a fork after two quivers. Here x is not joined to c₁ on M2, so its quivers are not forks. The line runs at height H⁺ − 2t², set by the arrows c → x, until the column of x reaches H⁺.

**The certificate** (`np_corridor_prove.py prove --T0 8`, `np_corridor_prove.log`). For every member and every vertex the script mutates symbolically, certifying first the sign of every entry at that vertex, and then certifies one of:

- **member**: the result equals another member, as an identity of polynomial matrices up to a relabelling of the vertices;
- **height**: a named entry e with a certified sign and |e| − H⁺ ≥ 0;
- **fork**: all ten entries certified ≥ 2 in absolute value with strict signs, the quiver not acyclic, a point of return r with every strict inequality of the definition, both sides of r acyclic, and one entry certified > t².

An inequality p ≥ 0 on a domain {variable ≥ bound} is certified by shifting each variable to its bound and checking that no coefficient of the expanded polynomial is negative. When a certificate fails on a domain, the script retries on the two parts {variable = bound} and {variable ≥ bound + 1}, at most twice.

The variables: t ≥ 8 for single quivers; j ≥ 1, v ≥ 1 with t = j + v + 1 for K(j), 1 ≤ j ≤ t − 2; k ≥ 3, u ≥ 1 with t = k + u + 2 for M1(k), 3 ≤ k ≤ t − 3; t and m ≥ 0 for M2; and t, i ≥ 2, r ≥ 1 for L(i), where r stands for N + 1 − i and is treated as free, with H⁺ written as (t + i + r)t² − 1. The half-planes j + v ≥ 7 and k + u ≥ 6 are covered by finitely many domains of the first kind.

| Claims | Number |
|---|---|
| Identities: H⁺ = (t + N + 1)t² − 1; the steps between K(0), K(1), K(t − 1), L(0); μ_c = −μ_p at the top, of height exactly H⁺; three backward steps from L(0) give M1(3), and from M1(t − 2) give M2(0); the formulas of M1 at k = 2 and M2 at m = −1 are L(−2) and L(−t); signs on the way to the 14 single quivers | 24 |
| Exits: member | 161 |
| Exits: height ≥ H⁺ | 428 |
| Exits: fork higher than t² | 54 |
| Exits: a new derived member | 123 |
| Every member except K(0) has an entry above t² | 148 |
| **All certified** | **938** |

> **Correction (note 17):** 937 of these are checks. One of the 24 identity lines, "the formula of K at j = t−1 is K(t−1), and of L at i = 0, 1 with r = N+1−i is L(0), L(1)", is printed as ok without a test; it holds by the way the script defines these quivers. Note 17 certified all 766 exits again with other code, and checked on its own that the claims cover every member and that every member except K(0) is above t². One caution for reruns: the script's table of recognised quivers lists M1(6), which is a member only for t ≥ 8, so `--T0` must not be set below 8.

**Why this proves the theorem.** Let t ≥ 8 and suppose a route from P⁺_t to a quiver Y of height ≤ t² has height below H⁺(t). Reduce it; this does not raise its height. By Lemma 15.5 it passes no fork higher than t². It starts at the member K(0). By the certificate, a mutation of a member is a member, or has height ≥ H⁺(t), or is a fork higher than t². So every quiver of the route is a member, and so is Y. Every member except K(0) has an entry above t², so Y is isomorphic to P⁺_t. ∎

Two points of bookkeeping. A step from a member of a line leads to the member with the next index, and at the ends of each range that is one of the single quivers: K(1) to K(0), K(t − 2) to K(t − 1), L(2) to L(1), L(N) to L(N + 1), M1(3) to L(−2), M1(t − 3) to M1(t − 2), M2(0) to L(−t). For L(i) the claims are certified for all t, i, r in their domain, which contains the true triples (t, i, N + 1 − i).

> **Update (note 17):** One point to add. The domain of L(i) is not closed under the backward step: at i = 2 the exit is the formula of L at (1, r + 1), and this is the member L(1) only if r + 1 = N. That holds on the true triples and fails elsewhere in the domain. The proof uses the true triples only, so it is not affected ([note 17](17-checks-of-note-16.md) §4.3). The same applies to the exit from the top to L(N).

### 4.2 Checks of the certificate

- **Closed forms** (`np_corridor_prove.py check`, `np_corridor_prove_check.log`). For t = 5 to 12 the formulas of K(j), L(i) (i ≤ 400), M1(k) and M2(m) (m ≤ 38) agree with integer mutation.
- **Verdicts.** Each of the 482 height and fork verdicts was re-evaluated with integers at four points of its domain: 1,928 evaluations, none wrong.
- **The list against the search.** For t = 8, 9, 10, 11 the instances of the members that lie below H⁺ are exactly the quivers found by `np_corridor.py core --plus`, a search from P⁺_t through non-forks below H⁺: 1,985, 2,827, 3,882 and 5,174 quivers, with none missing and none extra.
- **Closure on integers.** For the same t, every mutation of every instance below H⁺ (9,925 to 25,870 mutations) is an instance, or has height ≥ H⁺, or is a fork higher than t²; and exactly one instance has height ≤ t².
- **Overlap.** For 8 ≤ t ≤ 64 the theorem is proved twice, by the certificate and by Theorem 16.5, which uses neither forks nor polynomials.

The core found by search, for comparison with 4 vertices (`np_corridor_core.log`, `np_corridor_core_plus.log`):

| t | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| Core of Q_t on 4 vertices (note 15), 2t³ − t² + 5 | 17 | 50 | 117 | 230 | 401 | 642 | 965 | 1,382 | 1,905 |
| Core of P⁺_t | 120 | 125 | 263 | 492 | 840 | 1,331 | 1,985 | 2,827 | 3,882 |
| Core of P_t | 42 | 120 | 258 | 490 | 839 | 1,328 | 1,980 | 2,822 | 3,874 |
| … of which on the route | 14 | 47 | 114 | 227 | 398 | 639 | 962 | 1,379 | 1,902 |

At t = 5 the core of P⁺_t consists of the 227 quivers of the route, 231 on the backward line, and 34 others: the ends of the first line and the branches listed above.

> **Correction (note 17):** The backward line has 230 quivers below H⁺ at t = 5, and there are 35 others: K(5), K(6), K(7), K(−1), K(−2) and 30 on branches. 231 is the size of the branch that starts at L(0) with the backward step; it contains μ_{c₁}L(−1) besides the line (`review17_anatomy.log`). The sizes of the core for t = 2 to 11 were reproduced, and the same search gives one quiver of height ≤ t² for every t from 2 to 64.

**What is not certified.** P_t has no certificate; for it the lower bound is Theorem 16.5 only (t ≤ 64). The certificate was run for T₀ = 8, so 2 ≤ t ≤ 7 rests on the search alone.

---

## 5. Why this design stops at 5/2

**The constraints [I].** Call a route *pure* if it consists of steps with every first entry ≥ 0 and of turns as in Lemma 16.2, and ends with the identity of Lemma 16.3 at a vertex y.

1. A turn at z acts on the full subquiver Σ on the vertices other than p, q as the mutation of Σ at z, and under Lemma 16.2 the vertex z is a sink of Σ. So along a pure route Σ changes only by reversing all arrows at a sink, and its underlying graph is constant.
2. At the top, Lemma 16.3 requires S_ef = 0 for e, f ≠ y. So Σ is a star with centre y throughout.
3. Hence a turn at a leaf z lowers the slope of y only, by η_z·S_yz, and no counter changes the slope of another. Each leaf turns once: afterwards its slope is +η_z, and only a turn at y could lower it.
4. At the top, η_y·S_zy = 2η_z. With η_y = 1 the slope of y before the turns is δ = 2·Σ η_z² − 1.

**The count [H].** Let there be k counters with decrements η_z and starting values V_z ≤ w, and let all entries of the starting quiver be ≤ w. Then δ ≤ 2w gives Σ η_z² ≤ w + 1/2. The counter z turns after V_z/η_z steps, and until then it contributes 2η_z² to the slope of y. So y reaches at most w + Σ 2η_z·V_z ≤ w + 2w·√(k(w + 1/2)), and that is the number of steps left when the last counter has turned. A climbing leaf x needs 2·(slope of x) arrows x → y at the top. These are at most w in the starting quiver, or 2w if x starts as an in-neighbour of p with one arrow, as in P⁺_t; more arrows x → p would join x to the counters by more than w arrows. So the slope of x is at most w, and

height ≲ w · 2w·√(k·w) = 2√k · w^{5/2},  with k ≤ n − 4.

P⁺_t attains this for k = 1. The first route of P⁺_t is not pure in its first step only.

**Measured** (`np_corridor.py star`, `np_corridor_star.log`; the search uses fork pruning here). The quiver `star(k, h, m, a0, D, Ax)` has k equal counters on n = k + 4 vertices and x as in P_t.

| k | n | (h, m, a₀, D) | w | Height of the route | / w^{5/2} | Lower route found |
|---|---|---|---|---|---|---|
| 1 | 5 | (2, 3, 8, 4) | 8 | 140 | 0.77 | none |
| 2 | 6 | (2, 3, 8, 4) | 8 | 236 | 1.30 | none |
| 2 | 6 | (3, 5, 18, 9) | 18 | 1,809 | 1.32 | none |
| 2 | 6 | (4, 7, 32, 16) | 32 | 7,728 | 1.33 | none |
| 3 | 7 | (2, 5, 12, 6) | 12 | 810 | 1.62 | none |
| 3 | 7 | (4, 11, 48, 24) | 48 | 26,568 | 1.66 | none |

> **Update (note 17):** Without fork pruning the result is the same for all six quivers: one quiver of height ≤ w below the height of the route, and a second one at that height (`review17_star.log`). So for these six the join is at exactly the height of the route.

So more vertices raise the constant, by about √(n − 4), and not the exponent. A route that is not pure, for instance one that uses several pairs of weight 2 or that does not end in a mirror image, is not covered by this argument. §6 shows that such routes exist and are higher at small w.

---

## 6. The searches

### 6.1 Census of isolated quivers

**Method** (`np_corridor.py census`). Call a quiver of height w *isolated* if each of its mutations is higher than w. For every isolated n-vertex quiver of height w, up to relabelling and reversal of all arrows, the search computes the *escape level*: the least L such that the quiver reaches another quiver of height ≤ w through quivers of height ≤ L. Then f(Q, w) is at least the escape level. The search is exhaustive below L, up to a cap on the height and a budget of quivers. It does not expand forks, which is justified by Lemma 15.5: a route that enters a fork can only go on to forks that are at least as high.

**Validation on 4 vertices** (`np_corridor_census_n4.log`). For w = 3 to 7 the largest escape levels are 12, 28, 45, 66 and 79, the largest deaths of bottom components in note 10's census of all classes. For w = 2 no isolated quiver has an escape.

**Five vertices.**

| w | Isolated quivers searched | Escape found | Closed below the cap | Over budget | Cap | Largest escape levels | Largest / w² | / w^{5/2} |
|---|---|---|---|---|---|---|---|---|
| 2 | 2,288 | 725 | 945 | 618 | 512 | 14, 13, 10, 10 | 3.5 | 2.5 |
| 3 | 148,858 | 35,231 | 99,564 | 14,063 | 400 | 70, 45, 45, 42, 40 | 7.8 | 4.5 |
| 4, at least four entries ±2 | 414,257 of 2,685,691 | 81,998 | 252,220 | 80,039 | 1,024 | 107, 106, 102, 98, 97 | 6.7 | 3.3 |

- **w = 3.** Of the 113,627 quivers without an escape below the cap or within the budget, a random sample of 20,000 was searched again with cap 2,000 and budget 200,000. None has an escape: 17,773 close below 2,000 and 2,227 run over the budget. The record 70 belongs to (−3, −2, −1, 2, −3, −2, 2, −2, −2, −3). Its route has 418 mutations, none of them at vertex 0. The other four vertices carry a square of four arrows of weight 2 with two diagonals of weight 3. The route walks along these pairs in turn, and for long stretches it repeats a block of twelve mutations: five steps on one pair, a turn at a third vertex, five steps back and a turn at the fourth.
- **w = 2.** The record 14 is (−2, −2, −1, 2, −2, −2, 1, −2, −2, −2), with a route of 12 mutations: steps on one pair, a turn at vertex 1 after the first step, and a turn at vertex 0 after which the route retraces its steps to the opposite quiver. One column climbs by 4 per step to 14.
- **Escape levels by the number of entries ±2 (w = 3).** With 0, 1 or 2 such entries the largest escape level is 21, 17 and 17. With 3 to 6 it is 45, 40, 45 and 70. This is the reason for the restriction at w = 4.
- **w = 4.** Only the isolated quivers with at least four entries ±2 were searched. The record 107 belongs to (−4, −2, 1, 2, 1, −4, −2, −2, 3, −4), with a route of 602 mutations. 80,039 searches ran over the budget of 20,000 quivers. A sample of 2,000 of them, searched again with budget 150,000, gave no escape: 1,031 close below the cap and 969 run over again (`np_corridor_census_n5_w4_recheck.log`). So 107 is a lower bound for the record at w = 4.

**What the census does not see.** A quiver whose search closes below the cap either has no other quiver of height ≤ w in its class or joins one above the cap. Quivers that are not isolated are not started from. So the values are lower bounds for F(5, w).

### 6.2 A fixed 4-vertex quiver with a fifth row

**Lemma 16.8 (scaling a row) [I].** Let a route from Q to Q′ contain no mutation at the vertex x, and let λ ≥ 1 be an integer. Multiply every entry at x by λ, in Q and in Q′. The same mutations lead from the first quiver to the second, and along the route every entry at x is multiplied by λ while the other entries are unchanged.

*Proof.* A mutation at k ≠ x changes b_xj by [b_xk]₊[b_kj]₊ − [−b_xk]₊[−b_kj]₊, which is linear in the row of x, and changes no entry away from x by anything that involves x. ∎

So if x is never mutated, a barrier grows at most linearly with the row of x. A barrier of higher degree needs the other four vertices to change with w, as Q_t does in P⁺_t.

**Measured** (`np_corridor.py rows`, `np_corridor_rows.log`, `np_corridor_rows_db2_a5.log`). The four vertices 1 to 4 carry a fixed quiver R, written (b12, b13, b14, b23, b24, b34), and vertex 0 is attached by every row with entries ≤ k. The table gives the largest escape level found among the (2k + 1)⁴ rows; w is the height. The searches use cap 16w³ (8w³ for the last family) and a budget of 30,000 to 150,000 quivers, and between 4 % and 51 % of the rows run over it, so every value is a lower bound.

> **Correction (note 17):** The largest share is 7,332 of 14,641 rows, which is 50 %, not 51 %.

| R | Description | k | w | Largest escape level | Route | / w^{5/2} |
|---|---|---|---|---|---|---|
| (−3, −2, 2, −2, −2, −3) | the square of the w = 3 record | 3 | 3 | 70 | 418 mutations | 4.5 |
| | | 4 | 4 | 102 | 574 | 3.2 |
| | | 5 | 5 | 111 | 636 | 2.0 |
| (−4, −2, 2, −2, −2, −4) | the same square, diagonals 4 | 4 | 4 | 51 | 172 | 1.6 |
| (−4, −2, 3, −3, −2, −4) | two of its sides raised to 3 | 4 | 4 | 46 | 18 | 1.4 |
| (−(a + 1), −a, 2, −2, −a, −(a + 1)), a = 3 | the other two sides raised to a | 4 | 4 | 99 | 374 | 3.1 |
| a = 4 | | 5 | 5 | 272 | 846 | 4.9 |
| a = 5 | | 6 | 6 | 437 | 1,218 | 5.0 |
| (−2, 0, a, 1, −(a + 1), 2), a = 2, 3, 4 | one pair, two counters of slope 1 that bounce | 3, 4, 5 | 3, 4, 5 | 15, 36, 48 | 13, 18, 47 | 1.0, 1.1, 0.9 |

- With R fixed, the barrier grows slowly with the row: 70, 102, 111. This is what Lemma 16.8 allows.
- The fourth family changes R with w and grows faster: 70 (a = 2, the record of w = 3), 99, 272, 437. Its routes have 374 to 1,218 mutations. No closed form for the best row was found; the best rows are (−3, −2, −1, 2), (−3, −4, 2, 1), (−5, −5, 3, 1) and (−2, 3, 6, −6).
  > **Follow-up (note 18):** There is a closed form. R_a returns to itself after 2a + 1 steps on one pair of weight 2 and one step on the other, and the fifth vertex has a column on each pair. For a = 5 to 8 the best rows have x1 + x4 = −(2a − 2) and x2 + x3 = 2a − 1: (−(a − 3), a − 2, a + 1, −(a + 1)) for odd a and (−(a − 2), a − 2, a + 1, −a) for even a, with escape levels 4a³ − 3a² + (5a − 1)/2 and 4a³ − 3a² + 3a/2 for a ≤ 14. The rows (−3, −4, 2, 1) and (−5, −5, 3, 1) reach the same slopes after one step, and (−3, −2, −1, 2) has a longer chain of bounces ([note 18](18-five-vertices-cubic-barrier.md) §4 and §6).
- Counters that only bounce between two walls stay at about 2w².

### 6.3 Rigid quivers

Theorem 9.1 needs no long route: every mutation of G_k is high, and two mutations at vertices that are not joined cancel. `np_corridor.py templates` looks for the same on 5 vertices with a product of three entries (`np_corridor_templates.log`, `np_corridor_templates.jsonl.gz`).

- **Templates.** All 5-vertex quivers with entries in {0, ±1, ±6, ±7}, height 7 and every mutation above 14: 84,495 up to relabelling and reversal.
- **Result.** 2,838 reach another quiver of height ≤ 7, at an escape level between 29 and 49 = 7²: 2,828 by a route of two mutations and 10 by four or five. For the other 81,657 the search was repeated with cap 1,000,000: none has an escape; 80,141 searches close below the cap (1,221 of them without meeting it, so these quivers are the only ones of height ≤ 7 that their class can reach without passing a fork) and 1,516 run over the budget of 5,000 quivers.

A hand argument points the same way [I]. Suppose a route goes up by one mutation at v, up again by one mutation at a neighbour u of v, and then down twice. After the first step the new entries, of order k², join the in-neighbours of v to its out-neighbours. After the second, entries of order k³ appear between v and the vertices on the other side of u. A single mutation at a third vertex t that removes them needs an entry of order k² at t in the right direction, and the mutation at v creates none, since t would have to be both an in-neighbour and an out-neighbour of v.

---

## 7. The degree of F(n, w)

**What is established.**

| n | Lower bound for F(n, w) | Status | Upper bound |
|---|---|---|---|
| 3 | w | Theorem 3.1 | w |
| 4 | 2w² − 7w + 2 | Corollary 15.14, proved | 2w² conjectured (22.1); supported by the census for w ≤ 9 |
| 5 | 2w^{5/2} − 11w² | Theorem 16.6 and Corollary 16.7, proved (computer-assisted) | none |
| ≥ 6 | as for 5, with isolated vertices; connected quivers and the constant √(n − 4) are measured only | §3.3, §5 | none |

**Conjecture 16.9 [H].** F(5, w) = Θ(w^{5/2}).

- *For it.* The lower half is Corollary 16.7. For the upper half there is only this: the largest escape levels found at w = 2 to 6 (14, 70, 107, 272, 437, from §6.1 and §6.2) are 2.5, 4.5, 3.3, 4.9 and 5.0 times w^{5/2}, with no clear trend, while their ratios to w² grow from 3.5 to 12.1.
- *Against it.* Those values are lower bounds from searches with caps and budgets. They come from routes over several pairs of weight 2, which §5 does not cover and for which no family is known. Five values of w cannot separate w^{5/2} from w³: the same numbers are 1.8, 2.6, 1.7, 2.2 and 2.0 times w³.
- *A test.* The fourth family of §6.2 at a = 6 to 8. If its largest escape level stays near 5·w^{5/2}, it should be about 650, 910 and 1,220; if it follows 2·w³, about 690, 1,020 and 1,460.

> **Follow-up (note 18), the test:** The largest escape levels of the fourth family at a = 6, 7, 8 are 765, 1,242 and 1,868, above both predictions. For a = 6 and 7 this is a scan of every row with entries ≤ a + 1 (cap 16w³, budgets 400,000 and 700,000); for a = 8 every row was walked by the rules of note 18 and the eight best were searched. With the closed form the family was followed further. The escape level of Q_a = (−(a − 3), a − 2, a + 1, −(a + 1) | R_a) is 21, 88, 212, 437, 763, 1,242, 1,866, 2,695, 3,713, 4,988, 6,496, 8,313, 10,407, 12,862, 15,638, 18,827, 22,381, 26,400, 30,828, 35,773, 41,171 for a = 2 to 22, each by a search without pruning that finds no other quiver of height ≤ a + 1 below it. These are 4a³ − 3a² + (5a − 1)/2 for odd a and 4a³ − 3a² + (3a − 4)/2 for even a. In w = a + 1 that is 4w³ − 15w² + O(w), and 16.2·w^{5/2} at w = 23. **The upper half of Conjecture 16.9 is withdrawn.** Conjecture 18.7 replaces it: the same lower bound for every a, and F(5, w) = Θ(w³). No trend was visible in "For it" because the values at w = 3 and 4 (70 and 107) come from a shorter cycle with a longer chain of bounces, and 4w³ − 15w² is close to 5·w^{5/2} at w = 5 and 6. See [note 18](18-five-vertices-cubic-barrier.md).

**Question 16.10.** Does the degree of F(n, w) grow with n? The pure routes of §5 give degree 5/2 for every n ≥ 5. A higher degree would need counters that drive one another, which the mirror identity of Lemma 16.3 excludes, or a route that is not a mirror image of itself.

> **Follow-up (note 18):** The last sentence is too strong. The route of Q_a is a mirror image of itself, and for odd a its top is an instance of Lemma 16.3. It is higher than the pure routes of §5 because it is not pure: the three vertices other than the pair carry a pair of weight 2 of their own, the turns are steps on that pair, and each of the two columns of the fifth vertex changes the slope of the other when it passes its bottom (note 18, Proposition 18.3). On 5 vertices the degree is at least 3 on the range searched. For n ≥ 6 the question is open; Question 18.8 asks whether the degree is n − 2.

**For the wider question.** Conjecture A of note 3 §6 (a polynomial F(n, w)) is still open, and its degree is at least 2 for n = 4 and at least 5/2 for n ≥ 5. A decision procedure by bounded search on 5 vertices needs a bound of at least 2w^{5/2} − 11w², against 2w² on 4 vertices.

---

## 8. Limitations

- **Theorem 16.6 is computer-assisted.** For t ≥ 8 it rests on the 938 claims of `np_corridor_prove.py`, on Lemma 15.5 and so on Warkentin's Lemma 2.5, which was not read here (note 15 re-derives it, and `np_corridor.py selftest` checks it on 20,000 random forks with 4 and 5 vertices). For t ≤ 7 it rests on the search of Theorem 16.5 alone. The certificate had no separate check when it was written; §4.2 lists the checks that were made.
  > **Update (note 17):** A separate check has been made ([note 17](17-checks-of-note-16.md)); it is not a specialist's reading. It replayed the certificate with independent code, re-read the proofs of Lemmas 15.4 and 15.5 (they hold on any number of vertices), and tested them on 40,000 random forks and 400,000 reduced routes with 5 and 6 vertices. The definition of a fork and Warkentin's Lemma 2.5 were read in Ervin's restatement (arXiv 2306.07502v2, Definition 2.5 and Lemma 2.7), through an automated summary; the thesis is still unread. The search of Theorem 16.5 was reproduced for t ≤ 64 and continued to t = 80 for P⁺_t.
  >
  > **Update (note 19):** Warkentin's thesis has now been read. Definition 2.1 and Lemma 2.5 are as used here, and the proof of Lemma 2.5 states that no entry decreases. A third, independent check found no error, again without forks and with other code ([note 19](19-checks-of-notes-13-to-16.md)). It searched all labelled quivers below H for t = 2 to 64 and both families. It rebuilt the route and its columns for t = 2 to 64, reproduced the cores of the table of §4.2 for t ≤ 10 and the records 14, 70, 107, 272 and 437, and reran the certificate.
- **P_t and the quivers on 6 and 7 vertices are measured, not proved**, beyond the range of the searches.
- **§5 is a heuristic count** for pure routes. It is not an upper bound for F(5, w).
- **The census is not exhaustive.** It starts from isolated quivers only, its caps are 512, 400 and 1,024, and at w = 4 it covers only quivers with at least four entries ±2. The values are lower bounds.
- **Conjecture 16.9 has little support on its upper side.**
  > **Follow-up (note 18):** It is withdrawn in its upper half; see §7.
- **Six vertices.** No census was run on 6 vertices.
  > **Follow-up (note 18):** A random sample of 9,664 isolated 6-vertex quivers of height 2 gives 18 as the largest escape level, with 83 % of the searches over budget ([note 18](18-five-vertices-cubic-barrier.md) §8). A census is still missing.
- **Prior art.** No new search was made. Note 12 §6 found no statement of a super-linear barrier; Warkentin's 2014 thesis and Neville's 2025 thesis were not read.

---

## 9. Reproduce

```bash
PY=python
$PY -I np_corridor.py build                                   # gcc -O2, binary in ~/.cache/qmb-np/
$PY -I np_corridor.py selftest > np_corridor_selftest.log
$PY -I np_corridor.py family --tmin 2 --tmax 64 --out np_corridor_family.jsonl > np_corridor_family.log            # about 4 minutes
$PY -I np_corridor.py family_plus --tmin 2 --tmax 64 --out np_corridor_family_plus.jsonl > np_corridor_family_plus.log
$PY -I np_corridor.py pycheck --tmin 2 --tmax 9 > np_corridor_pycheck.log
$PY -I np_corridor_prove.py check --tmin 5 --tmax 12 > np_corridor_prove_check.log
$PY -I np_corridor_prove.py prove --T0 8 --audit-tmax 11 > np_corridor_prove.log                                   # about 1 minute
$PY -I np_corridor.py core --t 2 3 4 5 6 7 8 9 10 11 12 > np_corridor_core.log
$PY -I np_corridor.py core --t 4 5 6 --branches >> np_corridor_core.log
$PY -I np_corridor.py core --plus --t 2 3 4 5 6 7 8 9 10 > np_corridor_core_plus.log
$PY -I np_corridor.py core --plus --t 4 5 6 --branches >> np_corridor_core_plus.log
$PY -I np_corridor.py grid > np_corridor_grid.log
$PY -I np_corridor.py pendant --n 6 7 --t 2 3 4 > np_corridor_pendant.log
$PY -I np_corridor.py star > np_corridor_star.log
for w in 2 3 4 5 6 7; do $PY -I np_corridor.py census --n 4 --w $w --cap $((16*w*w)) --budget 100000; done > np_corridor_census_n4.log
$PY -I np_corridor.py census --n 5 --w 2 --cap 512 --budget 200000 --out np_corridor_census_n5_w2.jsonl.gz > np_corridor_census_n5_w2.log
$PY -I np_corridor.py census --n 5 --w 3 --cap 400 --budget 20000 --recheck-cap 2000 --recheck-budget 200000 --recheck-sample 20000 \
    --out np_corridor_census_n5_w3.jsonl.gz > np_corridor_census_n5_w3.log
$PY -I np_corridor.py census_summary --file np_corridor_census_n5_w3.jsonl.gz >> np_corridor_census_n5_w3.log
$PY -I np_corridor.py census --n 5 --w 4 --min-twos 4 --cap 1024 --budget 20000 --out np_corridor_census_n5_w4_min4.jsonl.gz   # several hours
$PY -I np_corridor.py templates --k 7 --out np_corridor_templates.jsonl.gz > np_corridor_templates.log
$PY -I np_corridor.py rows --kind rstar --k 3 --budget 60000 > np_corridor_rows.log       # then --k 4, --k 5; square --a 4 --k 4; db1 --a 3 --k 4;
                                                                                         # db2 --a 3 --k 4; db2 --a 4 --k 5 --budget 100000;
                                                                                         # bounce --a 2,3,4 --k 3,4,5 --budget 30000 --capf 8
$PY -I np_corridor.py rows --kind db2 --a 5 --k 6 --budget 150000 > np_corridor_rows_db2_a5.log
```

- The stored w = 4 census was run from a scratch driver that calls the same functions (`isolated`, `dedupe`, `np_barrier` with fork pruning) and was then summarised with `census_summary`; its log records this. The recheck of 2,000 over-budget quivers was run the same way.
- `np_barrier` reads one task per line and writes one JSON line; its header comment gives the format. `np_corridor.py path --n 5 --quiver … --full` prints a route of least height for any quiver.
- `np_corridor_prove.py` needs no package. Its two last audits import `np_corridor.py`.

---

## Sources

- Notes [3](03-profile-correction-and-rank-3.md), [9](09-n4-mirror-family.md), [10](10-n4-quadratic-bound.md), [11](11-n4-invariants-descent-joins.md), [12](12-checks-of-notes-03-to-10.md) and [15](15-rank-2-orbits-and-the-constant-2.md) of this repository. Lemma 15.5 (fork exclusion), Theorem 15.1 (orbits of two mutations), Theorem 15.6 (the quiver Q_t) and the certificate method of note 15 §5.3 are used as stated there.
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Def. 2.1 and Lemma 2.5, as quoted in notes 3 and 15 (not read here): https://d-nb.info/1214302807/34
- Beineke, Brüstle, Hille, *Cluster-cyclic quivers with three vertices and the Markov equation*, as used in note 12: https://arxiv.org/abs/math/0612213
- Warkentin, *Subquivers of mutation-acyclic quivers are mutation-acyclic*, as used in note 12: https://arxiv.org/abs/1102.3382
- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.14: https://arxiv.org/abs/1608.05735
