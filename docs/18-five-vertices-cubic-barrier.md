# 18. A fifth vertex over a bounce cycle: barriers of order w³ on five vertices

*Run on 2026-11-12. The aim was to find out whether routes over several pairs of weight 2 give 5-vertex barriers of higher order than the w^{5/2} of [note 16](16-five-vertices-above-w-squared.md). They do, in the whole range that could be searched. Code: [experiments/np_rowwalk.py](../experiments/np_rowwalk.py) (new), which drives `np_barrier.c` and uses `np_corridor.py` of note 16. Results: the `np_rowwalk_*` files in `experiments/`. Quivers are up to relabelling. A 5-vertex quiver is written as the tuple (b01, b02, b03, b04, b12, b13, b14, b23, b24, b34), or as (row | R): the row (b01, b02, b03, b04) of vertex 0 = x, and the 4-vertex quiver R = (b12, b13, b14, b23, b24, b34) on the vertices 1 to 4. b_ij > 0 means b_ij arrows i → j. Height means maximal entry; a route is a sequence of mutations; the escape level of a quiver of height w is the least height of a route from it to another quiver of height ≤ w (note 16 §6.1). Steps, turns, columns and slopes are those of note 16 §2. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

---

## 1. Outcome

1. **A 5-vertex quiver of height w that is joined to its opposite only at 4w³ − 15w² + O(w) [I; the route is proved for every w, the lower bound is an exhaustive search for w ≤ 23].** For a ≥ 2 let

   Q_a = (−(a − 3), a − 2, a + 1, −(a + 1) | −(a + 1), −a, 2, −2, −a, −(a + 1)),

   H(a) = 4a³ − 3a² + (5a − 1)/2 for odd a,  H(a) = 4a³ − 3a² + (3a − 4)/2 for even a.

   Q_a has height w = a + 1 and is not isomorphic to its opposite.
   - **The route (Theorem 18.4, by hand, checked by integer mutation for a ≤ 48).** A route of (2a + 2)(4a² − a + 6) mutations, none of them at vertex 0, leads from Q_a to −Q_a. Its height is H(a).
   - **No lower route, 2 ≤ a ≤ 22 (Theorem 18.5, exhaustive search without pruning).** The set of all quivers that Q_a reaches through quivers of height below H(a) contains no quiver of height ≤ a + 1 other than Q_a. For 23 ≤ a ≤ 26 the same holds with fork pruning, which rests on Lemma 15.5.

   So F(5, w) ≥ H(w − 1) ≥ 4w³ − 15w² + 19w − 11 for 3 ≤ w ≤ 23 (Corollary 18.6). At w = 23 the barrier is 41,171 = 3.38·w³ = 16.2·w^{5/2}. The family P⁺_t of note 16 gives 1,807 there.
2. **Conjecture 16.9 does not survive in its upper half [I].** It says F(5, w) = Θ(w^{5/2}). On 3 ≤ w ≤ 23 the lower bound H(w − 1) is a cubic polynomial in w for each parity. H(w − 1)/w^{5/2} is 2.75 at w = 4, 7.68 at w = 9 and 16.2 at w = 23, and it grows like 4·√w. A proof that F(5, w)/w^{5/2} is unbounded still needs the lower bound for every a (Conjecture 18.7a). The route exists for every a.
3. **The mechanism is a cycle of 2a + 2 mutations on four vertices [I].** The four vertices 1 to 4 of Q_a carry R_a = (−(a + 1), −a, 2, −2, −a, −(a + 1)), the fourth family of note 16 §6.2. R_a has two disjoint pairs of weight 2. Steps on one pair move its two other vertices along columns of slopes −1 and +1; after m = 2a + 1 steps one of them is at its bottom, a mutation there (a turn) is one step on the other pair, and the quiver is back at its start with two names exchanged (Lemma 18.1). The route walks round this cycle 4a² − a + 6 times. The fifth vertex is never mutated. It has a column on each pair. Whenever one of its columns passes its bottom, the slope of the other changes (Proposition 18.3), and that is how a counter of slope 2 comes to run for 2a² turns while the other column climbs by 2a + 1 per turn.
4. **The records of note 16 §6 are walks round such cycles [I].** The census records at w = 3 and w = 4 (escape levels 70 and 107) and the best rows over R_3, R_4, R_5 (99, 272, 437) are all reproduced by the two rules of Lemma 18.2; the two census records lie on the cycle with m = 5. Over R_a for a = 3 to 6, every row with a large escape level is a walk: 28 of 28 above 30, 29 of 29 above 60, 27 of 28 above 100 and 22 of 22 above 200 have escape level equal to the height of the walk (§6). The one exception is a walk on a cycle that contains x.
5. **The test of note 16 §7 [I].** Note 16 gave two predictions for the fourth family at a = 6, 7, 8: about 650, 910, 1,220 if it follows 5·w^{5/2}, and about 690, 1,020, 1,460 if it follows 2·w³. Measured: 765, 1,242 and 1,868. For a = 6 and 7 this is a scan of every row; for a = 8 the rules were applied to every row and the eight highest were confirmed by search.
6. **Within this design the degree is 3 and the constant is 4 [H].** The slopes of the two columns change by a linear map of determinant 1 and trace 2a − 1 at each pair of bounces. In every high walk found, the slopes come down to (1, 2), where a bounce reverses both rates and the walk runs back as its mirror image. The quivers of height w whose slopes do that after one pair of bounces give at most about w·m² ≤ 4w³ (§7). Two pairs of bounces need a cycle of length about √w and give order w^{5/2}; the census records at w = 3 and 4 are of that kind, on the cycle with m = 5.
7. **Six vertices at w = 2 [I].** A random sample of 9,664 isolated 6-vertex quivers of height 2 has largest escape level 18, with 83 % of the searches over budget (§8); on 5 vertices the record is 14.
8. **What is open.** The lower bound for every a (Conjecture 18.7a); any upper bound for F(5, w) (Conjecture 18.7b is F(5, w) = Θ(w³), with little support on its upper side); and whether the degree of F(n, w) is n − 2 (Question 18.8), which the values w, 2w² and 4w³ for n = 3, 4, 5 suggest.

---

## 2. The bounce cycle

**Definition.** Let m ≥ 3 and 0 ≤ j ≤ m + 1. W_m(j) is the quiver on four vertices p, q, r, s with two arrows q → p, two arrows s → r, and the columns

r: (b_pr, b_qr) = (m − j, −(m + 1 − j)),  s: (b_ps, b_qs) = (j, −(j − 1)).

So for 1 ≤ j ≤ m there are m − j arrows p → r, m + 1 − j arrows r → q, j arrows p → s and j − 1 arrows s → q. The number j is the *position*. A *step* mutates at p and then exchanges the names p and q, as in note 16 §2.

**Lemma 18.1 (the bounce cycle) [I].**
1. **Steps.** For 0 ≤ j ≤ m, a step takes W_m(j) to W_m(j + 1).
2. **The turn.** The mutation of W_m(m) at r is W_m(0) with the names r and s exchanged. So m steps and one turn lead from W_m(0) back to W_m(0), with r and s exchanged, and with p and q exchanged if m is odd.
3. **Mirror.** For 0 ≤ j ≤ m + 1, the opposite of W_m(j), with the names p ↔ q and r ↔ s exchanged, is W_m(m + 1 − j).
4. **Height.** W_m(j) has height max(m + 1 − j, j, 2) for 1 ≤ j ≤ m, and m + 1 for j = 0 and j = m + 1. For odd m the lowest is W_m((m + 1)/2), of height (m + 1)/2, and it is isomorphic to its opposite.
5. **R_a.** R_a = (−(a + 1), −a, 2, −2, −a, −(a + 1)) is W_{2a+1}(a + 1) with (p, q, r, s) = (4, 1, 2, 3).

*Proof.* (1) The first entries m − j and j of the two columns are ≥ 0. By Lemma 16.1 each column moves one place along its progression, with slopes −1 and +1, and the arrows between r and s do not change. (2) In W_m(m) the column of r is (0, −1), and there are two arrows s → r. Lemma 16.2 with y = r and η = 1: the second entry of s drops by 2, from −(m − 1) to −(m + 1); the column of r becomes (0, 1); the arrows between r and s are reversed. These are the columns (m, −(m + 1)) and (0, 1) of W_m(0), for s and r in this order. (3) Reversing all arrows of W_m(j) gives two arrows p → q and r → s, m − j arrows r → p, m + 1 − j arrows q → r, j arrows s → p and j − 1 arrows q → s. With p′ = q, q′ = p, r′ = s, s′ = r these are the arrows of W_m(m + 1 − j). (4) and (5) are read off. ∎

**Remarks.**
- **The turn is a step on the other pair.** The mutation at r is a step on the pair (r, s). On that pair the columns of p and q in W_m(m) are (b_rp, b_sp) = (0, −m) and (b_rq, b_sq) = (1, m − 1), with slopes −m and m. So the cycle uses two pairs of weight 2: m steps on one, where the slopes are ∓1, then one step on the other, where they are ∓m.
- **A square and a pentagon at each end.** In W_m(m) the vertices p and r are not joined, so the mutations at p and at r commute: the turn can be made at position m or one step later, at position m + 1 (Lemma 18.2). In W_m(m − 1) they are joined by one arrow, which gives a pentagon.
- **The class of R_a near the cycle [I, measured].** For 2 ≤ a ≤ 20, exactly 2a + 7 quivers of the class of R_a are joined to it through quivers of height ≤ 2a + 3: the 2a + 3 quivers W_m(j), 0 ≤ j ≤ m + 1, the next quiver of the line at either end, and the fifth quiver of the pentagon at either end. None is a fork, and R_a is the only one of height ≤ a + 1 (`np_rowwalk.py cycle`, `np_rowwalk_cycle.log`). The class has more quivers that are not forks: the lines continue beyond both ends, with growing entries.
- **The bouncing counters of note 16.** The quiver (−2, 0, a, 1, −(a + 1), 2) of note 16 §6.2, "one pair, two counters of slope 1 that bounce", is W_a(0): the cycle with m = a, taken at its highest position, where a quiver of height w allows only m = w − 1. Note 16 found escape levels near 2w² for it. R_a is the cycle with m = 2w − 1 at its lowest position.
- `np_rowwalk.py cycle` checks statements (1) to (3) and (5) by integer mutation for 3 ≤ m ≤ 41.

---

## 3. A fifth vertex on the cycle

Let x be a further vertex, joined to W_m(j) in any way. Record it by its *state*

(A, B, U, V) = (b_px, b_qx, b_xr, b_xs).

(A, B) is the column of x on the pair (p, q). The pair (U, V) plays the same part for the pair (r, s).

**Lemma 18.2 (the fifth vertex) [I].**
- **(S) A step from position j, 0 ≤ j ≤ m.** If A ≥ 0, the state becomes (2A + B, −A, U, V). If A < 0, it becomes (B, −A, U + |A|·(m − j), V + |A|·j).
- **(T) The turn at position m, with r and s renamed.** If U ≥ 0, the state becomes (A, B − U, V, −U). If U < 0, it becomes (A, B, V + 2U, −U).
- **(Q) The square.** A step from position m followed by the mutation at r gives the same quiver as the turn followed by a step: the quiver at position 1 of the next round.
- **(M) Mirror.** Let X be the quiver at position j with state (A, B, U, V). Then −X, with the names p ↔ q and r ↔ s exchanged, is the quiver at position m + 1 − j with state (−B, −A, −V, −U).

*Proof.* (S) is Lemma 16.1 for the columns m − j ≥ 0 and j ≥ 0 of r and s and the column (A, B) of x: for A ≥ 0 no entry between x, r, s changes, and for A < 0 the entries b_xr and b_xs gain |A|·(m − j) and |A|·j. (T) The arrows at r in W_m(m) are two arrows s → r, one arrow r → q, and U arrows x → r or |U| arrows r → x. If U > 0, the paths x → r → q add U to b_xq, so B falls by U. If U < 0, the paths s → r → x add 2|U| to b_sx, so V falls by 2|U|. In both cases U changes sign, and r and s are renamed. (Q) holds because p and r are not joined in W_m(m). (M) follows from Lemma 18.1(3): the entries at x change sign, and the names are exchanged. ∎

`np_rowwalk.py cycle` checks (S), (T) and (M) on 35,880 random states for 3 ≤ m ≤ 41, and (Q) on 1,560 of them.

**Slopes.** Put d = A + B and e = U + V. While A ≥ 0, the column (A, B) moves by d per step: (A, B) ↦ (A + d, B − d). While U ≤ 0, a turn takes (U, V) to (U + e, −U). So over a round of m steps and one turn without other events, A grows by m·d and −U falls by e.

**Proposition 18.3 (bounces) [I].**
1. A step with A ≥ 0 and a turn with U ≤ 0 change neither d nor e.
2. A step with A < 0 changes (d, e) to (d + 2|A|, e + m·|A|). A turn with U > 0 changes (d, e) to (d − U, e − 2U).
3. **The column on (p, q) passes its bottom.** Let d < 0 and let A fall below 0. After at most two steps with A < 0 the column climbs again, and in total (d, e) ↦ (−d, e + m·|d|).
4. **The column on (r, s) passes its bottom.** Let e > 0 and let U rise above 0. After at most two turns with U > 0, U is negative again and falls, and in total (d, e) ↦ (d − e, −e).
5. Hence, if 0 < d < e, the two bounces (4) and then (3) give

   (d, e) ↦ (e − d, (m − 1)·e − m·d) = M·(d, e),  M = [[−1, 1], [−m, m − 1]],  det M = 1,  tr M = m − 2.

*Proof.* (1) and (2) are read off from Lemma 18.2. (3) Let A′ ∈ [0, |d|) be the last non-negative value and α = |d| − A′ ∈ (0, |d|]. The next column is (−α, −(|d| − α)). The step gives (−(|d| − α), α) and adds m·α to e. If |d| − α > 0, one more step gives (α, |d| − α) and adds m·(|d| − α). The column now has slope |d| and first entry ≥ 0, and e has grown by m·|d|. (4) is the same computation for (U, V): the two positive values of U at the turns are β ∈ (0, e] and e − β. Their sum e is subtracted from d, and e changes by −2e. (5) is the composition. ∎

So the fifth vertex moves like a ball between two walls. Between bounces one column falls and the other climbs, at constant rates. A bounce of one column changes the rate of the other. In the notation of note 16 §5 the subquiver Σ on the vertices other than p and q is {r, s, x}. It is not a star, and a turn at r with U < 0 is a mutation of Σ at a vertex that is not a sink. Such routes are not pure, and the count of note 16 §5 does not apply to them.

---

## 4. The records of note 16 in this language

`np_rowwalk.py phases` walks a row over R_a round the cycle by the rules (S) and (T), taking at each turn the lower of the two ways round the square (Q). `np_rowwalk.py blocks` prints the route of least height found by the search, cut into runs. The table lists, for each record, the stretches of constant slopes (`np_rowwalk_phases.log`; the logs call a round a half-period).

| Row over R_a, or state (A, B, U, V) | a, m | Rounds | Slopes (d, e) in order, up to the top | Values of A at the bounces | Height of the walk | Escape level by search |
|---|---|---|---|---|---|---|
| (−3, −2, −1, 2), the record of w = 3 | 2, 5 | 68 | (5, 7), (3, 3), (−2, −7), (2, 3), (1, 1), (−1, −3), (1, 2), (0, 0) | 23, 3, 48, 3, 70 | 70 | 70 |
| (−1, 4, −2, 4) at position 2 of W_5, the census record of w = 4 | –, 5 | 97 | (5, 7), (4, 5), (−2, −7), (2, 3), (−1, −3), (1, 2) | 34, 2, 72, 2, 107 | 107 | 107 |
| (−3, −4, 2, 1) | 3, 7 | 46 | (4, 5), (0, −3), (−1, −5), (1, 2), (0, 0) | 39, 4, 99 | 99 | 99 |
| (−5, −5, 3, 1) | 4, 9 | 84 | (6, 7), (0, −5), (−1, −7), (1, 2), (0, 0) | 77, 5, 272 | 272 | 272 |
| (−2, 3, 6, −6) = Q_5 | 5, 11 | 101 | (8, 9), (5, 3), (−1, −9), (1, 2) | 101, 2, 437 | 437 | 437 |
| (−4, 4, 7, −6) | 6, 13 | 143 | (10, 11), (6, 3), (−1, −11), (1, 2) | 144, 1, 765 | 765 | 765 |

- **Which pairs.** At R_a the pairs of weight 2 are (1, 4) and (2, 3). The walk steps on (1, 4) and turns at 2 and 3 in turn. The routes printed by the search show runs on other pairs, such as (1, 2), (3, 4) and (1, 3), (2, 4). These are the same two pairs after the relabellings that the pentagons at the ends of the line bring in: the search takes the three-mutation side of a pentagon where it is lower. For Q_5 the walk has 1,212 mutations and the route of the search 1,218, with the same height.
- **One period.** A period is two rounds, 2m + 2 mutations: m steps, a turn, m steps, a turn. In the long stretch before the top, with slopes (1, 2), the column of x on the pair gains 2m per period and the other column loses 4. For a = 2, 3, 4, 5 that is 10, 14, 18, 22 against 4, as seen in note 16 (blocks of twelve mutations at w = 3).
- **What ends a stretch.** A column of x passes its bottom. At the top it is the column on (r, s): its entries pass through (−2, 4), (0, 2), (2, 0), (0, −2) or through (−1, 3), (1, 1), (1, −1), (−1, −1), the slope d changes from 1 to −1, and the route runs down as the mirror image of the way up.
- **The first rows of the table start one step before the family.** For (−3, −4, 2, 1) and (−5, −5, 3, 1) the first step has A = −1 and adds m to e. After it the slopes are (2a − 2, 2a − 1), those of Q_a. This start needs b_1x = 2a − 3 ≤ a + 1, so it exists for a ≤ 4 only.
- **The records at w = 3 and w = 4 have two pairs of bounces before the last stretch**: M takes (5, 7) to (2, 3) and (2, 3) to (1, 2) for m = 5.
- **The census record at w = 4.** (−4, −2, 1, 2, 1, −4, −2, −2, 3, −4), escape level 107 (note 16 §6.1), is the quiver at position 2 of the cycle W_5 with the fifth vertex in the state (−1, 4, −2, 4), up to relabelling: the tuple (1, −4, −2, 4, −2, 3, 2, −4, −1, −2) has the same canonical form. In the labels of the census its route of 602 mutations has none at vertex 1 and 135 at vertex 0, and its long stretches repeat five steps on the pair (0, 4), a turn at 2, five steps, a turn at 3 (`np_rowwalk.py blocks`). So the passive vertex is 1, and x lies on the cycle.

---

## 5. The family Q_a

### 5.1 The route

Write m = 2a + 1 and c = 4a² − 5a + 1 = (4a − 1)(a − 1). Q_a is the quiver at position a + 1 of the cycle of R_a, with (p, q, r, s) = (4, 1, 2, 3) and the state (A, B, U, V) = (a + 1, a − 3, a − 2, a + 1). Its slopes are (d, e) = (2a − 2, 2a − 1), and M·(2a − 2, 2a − 1) = (1, 2).

**Theorem 18.4 [I].** Let a ≥ 2.
1. Q_a has height a + 1 and is not isomorphic to −Q_a.
2. There is a route from Q_a to −Q_a with (2a + 2)(4a² − a + 6) mutations, none of them at x. For odd a it ends at −Q_a with the same labels, and for even a with the labels 1 ↔ 4 and 2 ↔ 3 exchanged.
3. The height of the route is H(a). For odd a one quiver on it has height H(a). For even a there are 2a + 5. All others have height at most H(a) − 1. No entry away from x exceeds 2a + 2.

*Proof.* **The first half.** Walk from Q_a: a steps to position m, then turns and rounds of m steps. The claim is that the state at position m, before the n-th turn, is as follows.

| n | A | B | U | V | (d, e) |
|---|---|---|---|---|---|
| 1 | 2a² − a + 1 | −(2a² − 3a + 3) | a − 2 | a + 1 | (2a − 2, 2a − 1) |
| 2 | 4a² + 1 | −(4a² − a + 1) | a + 1 | −(a − 2) | (a, 3) |
| 2 + k, 1 ≤ k ≤ 2a − 1 | 4a² + 1 − k·m | −(4a² + 2 − k·m) | −u_{k−1} | u_{k−2} | (−1, −(2a − 1)) |
| 2a + 1 + t, 1 ≤ t ≤ t* | 2a − 3 + (t − 1)·m | −(2a − 4 + (t − 1)·m) | −(c − 2(t − 1)) | c + 2 − 2(t − 1) | (1, 2) |

Here u_i = a − 2 + i·(2a − 1), and t* = c/2 + 2 for odd a, t* = (c + 3)/2 for even a.

- **Up to the first turn.** In Q_a the first entry A = a + 1 is ≥ 0 and d = 2a − 2 ≥ 0. By (S), a steps give A = a + 1 + a(2a − 2). This is the line n = 1.
- **The first turn and the round after it.** The turn has U = a − 2 ≥ 0. By (T) it lowers B by a − 2, so d = a, and (U, V) becomes (a + 1, −(a − 2)). Then m steps add m·a to A. This is the line n = 2.
- **The second turn.** It has U = a + 1 > 0. It lowers B by a + 1, so d = −1, and (U, V) becomes (−(a − 2), −(a + 1)) = (−u₀, u₋₁). The column on (r, s) has passed its bottom: (d, e) = (2a − 2, 2a − 1) ↦ (−1, −(2a − 1)), as in Proposition 18.3(4).
- **The turns 3 to 2a + 1.** Now U ≤ 0 at every turn, and (T) gives (U, V) ↦ (V + 2U, −U): the numbers u_k = −U satisfy u_k = 2u_{k−1} − u_{k−2}. Each round lowers A by m, one per step. Since 4a² + 1 = (2a − 1)·m + 2, the first entry stays ≥ 2 during the rounds that end at the turns 3 to 2a + 1, and before turn 2a + 1 the column is (2, −3). These are the lines n = 2 + k.
- **The bottom.** After turn 2a + 1 the state is (2, −3, −u_{2a−1}, u_{2a−2}) with u_{2a−1} = 4a² − 3a − 1 and u_{2a−2} = 4a² − 5a. Three steps give the columns (1, −2), (0, −1), (−1, 0). The step from position 3 has A = −1: by (S) the column becomes (0, 1), U gains m − 3 and V gains 3. So U = −c and V = c + 2, and (d, e) = (−1, −(2a − 1)) ↦ (1, 2) as in Proposition 18.3(3). The remaining m − 4 steps give the column (2a − 3, −(2a − 4)). This is the line t = 1.
- **The last stretch.** A grows by m per round, and (U, V) ↦ (U + 2, −U) at each turn as long as U ≤ 0. For odd a the table gives U = 0 at t = c/2 + 1, where (T) changes nothing but the names. So the lines hold up to t*.

**The top, odd a.** Let T₁ be the quiver before turn 2a + 1 + t*. Its state is (A₁, −(A₁ − 1), 2, 0) with A₁ = 2a − 3 + (c/2 + 1)·m. The column of r is (0, −1), there are two arrows s → r and two arrows x → r, the slopes of s and x are both 1, and x and s are not joined. This is the situation of Lemma 16.3 with y = r, so μ_r(T₁) = −μ_p(T₁). By the corollary of note 16 §2, the first half, then μ_r, then μ_p, then the first half in reverse order is a route from Q_a to −Q_a. The quiver μ_r(T₁) has the state (A₁, −(A₁ + 1), 0, −2), and A₁ + 1 = H(a).

**The top, even a.** Before turn 2a + 1 + t* the state is (A₁, −(A₁ − 1), 1, 1) with A₁ = 2a − 3 + ((c + 1)/2)·m = H(a). The turn gives T₂ at position 0 with state (A₁, −A₁, 1, −1). Its slope d is 0, so m + 1 further steps change nothing at x and lead to position m + 1 with the same state, and with the names p, q as in T₂. By (M) with j = 0 this quiver is −T₂ with the labels p ↔ q, r ↔ s exchanged. So the first half, then m + 1 steps, then the first half in reverse order with these labels exchanged is a route from Q_a to −Q_a with the labels exchanged: mutation commutes with reversing all arrows and with relabelling.

**Count.** For odd a the first half has a + (2a + 2 + c/2)·(m + 1) mutations and the middle has 2. For even a the first half has a + 1 + (2a + (c + 3)/2)·(m + 1) mutations and the middle has m + 1. Both totals are (2a + 2)(4a + 5 + c) = (2a + 2)(4a² − a + 6).

**Heights.** Away from x the entries are those of W_m(j), at most m + 1 = 2a + 2. In a round with A ≥ 0 the entries of the column move monotonically, so it is enough to look at the turns and at the bottom. Before turn 2 + k the entries at x are at most 4a² + 2 and u_{2a−1} < 4a². In the last stretch |U|, |V| ≤ c + 2 and A, |B| ≤ A₁. For odd a the largest entry of the first half is A₁ = H(a) − 1, and μ_r(T₁) has the entry A₁ + 1 = H(a). For even a the quivers of height H(a) = A₁ are the quiver before the last turn, T₂ and the m + 1 quivers after it, and the mirror image of the first: m + 4 = 2a + 5. And 4a² + 2 < H(a) for a ≥ 2. The values of H(a) follow from c: A₁ + 1 = 4a³ − 3a² + (5a − 1)/2 for odd a, and A₁ = 4a³ − 3a² + (3a − 4)/2 for even a.

**Not isomorphic.** The sums of the absolute values of the entries at the vertices x, 1, 2, 3, 4 of Q_a are 4a − 3, 3a, 3a + 1, 3a + 4, 3a + 4 for a ≥ 3. For a ≥ 5 an isomorphism from Q_a to −Q_a must fix the vertices 1 and 2. But Q_a has a + 1 arrows 2 → 1 and −Q_a has them from 1 to 2. For a = 2, 3, 4 the canonical forms differ. ∎

*Checks* (`np_rowwalk.py family`; `np_rowwalk_family.log`, `np_rowwalk_family_pruned.log`, `np_rowwalk_family_route_only.log`). For every a from 2 to 48 the route was built by integer mutation, with Python integers. Checked for each a: the height of Q_a; no mutation at x; the number of mutations; the state before every turn of the first half against the table (10 turns at a = 2, 4,587 at a = 48); the relabelling at the middle; the last quiver, entry by entry; the height H(a); the positions of the quivers of height H(a); and that Q_a and −Q_a have different canonical forms. All 47 values pass.

### 5.2 No lower route, for a up to 22

**Theorem 18.5 [I, by exhaustive computation].** Let 2 ≤ a ≤ 22. Every route from Q_a to a quiver of height ≤ a + 1 that is not isomorphic to Q_a has height at least H(a). So Q_a and −Q_a are joined at exactly H(a), and f(Q_a, w) ≥ H(a) for a + 1 ≤ w < H(a).

*Method* (`np_rowwalk.py family --prune 0`; `np_rowwalk_family.log`). As in Theorem 16.5. For each a the program `np_barrier` computes the set of all quivers, up to relabelling, that Q_a reaches through quivers of height at most H(a) − 1. No fork is pruned, and mutations at x are included. The set contains one quiver of height ≤ a + 1, the start, and none lower. A second search with bound H(a) returns H(a) as the least height at which another quiver of height ≤ a + 1 is reached, and that quiver is −Q_a. Products are formed in 64-bit integers and every quiver with an entry above the bound is discarded; H(22) = 41,171.

| a | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 10 | 12 | 16 | 20 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w = a + 1 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 11 | 13 | 17 | 21 | 23 |
| H(a) | 21 | 88 | 212 | 437 | 763 | 1,242 | 1,866 | 3,713 | 6,496 | 15,638 | 30,828 | 41,171 |
| H / w³ | 0.78 | 1.38 | 1.70 | 2.02 | 2.22 | 2.43 | 2.56 | 2.79 | 2.96 | 3.18 | 3.33 | 3.38 |
| H / w^{5/2} | 1.35 | 2.75 | 3.79 | 4.96 | 5.89 | 6.86 | 7.68 | 9.25 | 10.66 | 13.12 | 15.25 | 16.23 |
| Mutations of the route | 120 | 312 | 660 | 1,212 | 2,016 | 3,120 | 4,572 | 8,712 | 14,820 | 34,476 | 66,612 | 88,320 |
| Quivers reached below H | 525 | 3,907 | 13,645 | 41,316 | 95,260 | 206,989 | 396,948 | 1,206,172 | 2,995,196 | 12,599,812 | 38,426,424 | 61,875,173 |
| H⁺(⌊√w⌋), the bound of note 16 | – | 51 | 51 | 51 | 51 | 51 | 413 | 413 | 413 | 1,807 | 1,807 | 1,807 |
| 2w², the bound of Conjecture 10.1 on 4 vertices | 18 | 32 | 50 | 72 | 98 | 128 | 162 | 242 | 338 | 578 | 882 | 1,058 |

All 21 values of a pass every check. The number of quivers below H(a) grows about like a⁵, which is what stops the search.

**With fork pruning, a up to 26** (`np_rowwalk_family_pruned.log`). For 23 ≤ a ≤ 26 the same two searches were run without expanding forks. This is justified by Lemma 15.5, which holds on any number of vertices ([note 17](17-checks-of-note-16.md) §7): a reduced route between two quivers of height ≤ a + 1 passes no fork higher than a + 1. Each search finds one quiver of height ≤ a + 1 below H(a), and −Q_a at exactly H(a). The run was stopped after a = 26.

| a | 23 | 24 | 25 | 26 |
|---|---|---|---|---|
| w = a + 1 | 24 | 25 | 26 | 27 |
| H(a) | 47,138 | 53,602 | 60,687 | 68,313 |
| H / w³ | 3.41 | 3.43 | 3.45 | 3.47 |
| H / w^{5/2} | 16.7 | 17.2 | 17.6 | 18.0 |
| Quivers reached below H, forks not expanded | 23,800,313 | 29,501,788 | 36,312,433 | 44,255,806 |

**Checks of the search.**
- `np_corridor.py selftest` of note 16 validates `np_barrier` against the known 4-vertex values, with and without pruning.
- `np_rowwalk.py pycheck` (`np_rowwalk_pycheck.log`): for a = 2 to 7 a breadth-first search in pure Python, with Python integers, finds the same number of quivers below H(a) as `np_barrier` (525 to 206,989), and one of height ≤ a + 1.
- A search with fork pruning and the larger bound 16w³ gives the same escape level H(a) for every a from 2 to 14 (`np_rowwalk_shape.log`).

**Corollary 18.6 [I].** F(5, w) ≥ H(w − 1) for 3 ≤ w ≤ 23, where H(w − 1) = 4w³ − 15w² + (41w − 20)/2 for even w and 4w³ − 15w² + (39w − 21)/2 for odd w. In particular F(5, w) ≥ 4w³ − 15w² + 19w − 11 on this range. The same holds for F(n, w), n ≥ 6, if disconnected quivers are admitted.

**What is not proved.** For a ≥ 23 (a ≥ 27 with Lemma 15.5) there is no lower bound. A certificate in the style of note 16 §4 would have to describe the quivers below H(a), and there are about 12·a⁵ of them, against 8a³ on the route. The others are reached by mutations at x and at r or s in the middle of a round, and they were not analysed.

> **Correction (note 20):** The last sentence is wrong about where the other quivers are. With forks not expanded, 98 % of them at a = 12 lie on the lines of steps on the pair (p, q) that continue each round beyond its two ends, not at mutations at x, r or s. These lines have closed forms for every a, and a mutation off them is high as soon as the two entries of the column concerned have product ≥ H(a) + 2 ([note 20](20-core-of-the-cubic-family.md) §4). Without pruning it is the same picture: at a = 12, 2,969,824 of the 2,995,196 quivers below H(a) have exactly two neighbours below H(a) and lie on runs of steps on one pair.

> **Follow-up (note 20):** The theorem now holds for 2 ≤ a ≤ 48 without pruning and for 49 ≤ a ≤ 64 with fork pruning, by the same searches run without storing the quivers that have exactly two neighbours below H(a); at a = 64 there are 4,165,617,632 quivers below H(64) = 1,036,382 with forks not expanded. So Corollary 18.6 holds for 3 ≤ w ≤ 65. A certificate for every a was not obtained. Besides the route and the lines, the set to be covered has about 4a³ to 5a³ quivers near the route, in about a hundred kinds whose domains are not orthants, and two spirals of quivers that are not forks, at the two ends of the bounce cycle, on which the entries grow geometrically. The spirals make the number of families grow with a, which a certificate with finitely many polynomial families cannot cover. See [note 20](20-core-of-the-cubic-family.md).

> **Correction (note 23):** The last sentence of the follow-up overstates note 20. What is measured, up to a = 48, is that families indexed by the words from the route would grow in number with a. Families parametrised by their state on cones, which the round of ten mutations maps linearly, are not ruled out ([note 23](23-checks-of-notes-20-to-22.md) §4.2). Nor are the other quivers reached "by mutations at x" in any sense intrinsic to the class: below H(a) Q_a reaches relabellings of itself that move x, through pentagons at single arrows ([note 23](23-checks-of-notes-20-to-22.md) §4.1). The theorem and its extension in note 20 were reproduced with independent code: without pruning for every a ≤ 26 and a = 32, and with forks not expanded for every a ≤ 32 and a = 36 and 40.

---

## 6. The other rows over R_a

### 6.1 Scans

`np_rowwalk.py scan` computes the escape level of (row | R_a) for every row with entries ≤ a + 1, one of each pair {row, −(row read backwards)}; the two quivers of a pair are opposite, so they have the same escape level. The search prunes forks, discards quivers above the cap 16w³ and stops at a budget of quivers.

| a | w | Rows | Escape found | Closed below the cap | Over budget | Cap | Budget | Largest escape levels | Best row |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 4 | 3,321 | 683 | 1,946 | 692 | 1,024 | 60,000 | 99, 88, 85 | (−3, −4, 2, 1) |
| 4 | 5 | 7,381 | 1,188 | 4,669 | 1,524 | 2,000 | 100,000 | 272, 245, 218 | (−5, −5, 3, 1) |
| 5 | 6 | 14,365 | 1,952 | 9,449 | 2,964 | 3,456 | 150,000 | 437, 428, 426 | (−2, 3, 6, −6) = Q_5 |
| 6 | 7 | 25,425 | 2,864 | 18,682 | 3,879 | 5,488 | 400,000 | 765, 763, 754 | (−4, 4, 7, −6) |
| 7 | 8 | 41,905 | 4,199 | 31,918 | 5,788 | 8,192 | 700,000 | 1,242, 1,229, 1,227 | (−4, 5, 8, −8) = Q_7 |

- **The test of note 16 §7.** At a = 6 the largest escape level over all rows is 765; the predictions were about 650 for 5·w^{5/2} and 690 for 2·w³. At a = 7 it is 1,242; the predictions were about 910 and 1,020. For a = 8 no scan was run; the rules of §6.2 with a search of the best rows give 1,868, against about 1,220 and 1,460.
- **Closed below the cap.** For most rows the search ends without another quiver of height ≤ w below 16w³. §7 explains why: the slopes grow at every pair of bounces unless they are special.
- **Over budget.** These searches are not finished, so the largest values are lower bounds for the largest escape level over R_a.

### 6.2 Every row by the rules

`np_rowwalk.py walks` applies (S), (T) and (Q) to every row, forwards and backwards, until another quiver of height ≤ w over R_a is reached or the height passes the cap. This takes no search. The table compares the height of the walk with the escape level of §6.1 (`np_rowwalk_walks.log`, `np_rowwalk_walks_a7_a8.log`).

| a | Rows | The walk returns | Escape found by the scan | … of these, walk height = escape level | … walk higher by 1 to 3 | … walk higher by more | … no return by the walk | Rows above the level L | … with walk height = escape level |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 3,321 | 457 | 683 | 373 | 71 | 13 | 226 | 28 (L = 30) | 28 |
| 4 | 7,381 | 781 | 1,188 | 649 | 62 | 69 | 408 | 29 (L = 60) | 29 |
| 5 | 14,365 | 1,226 | 1,952 | 1,013 | 63 | 149 | 727 | 28 (L = 100) | 27 |
| 6 | 25,425 | 1,747 | 2,864 | 1,473 | 66 | 208 | 1,117 | 22 (L = 200) | 22 |

- **High escape levels are walks.** Above the level L (30, 60, 100, 200 for a = 3 to 6) every row but one has escape level equal to the height of its walk. The exception is (1, 4, 5, −4) over R_5, with escape level 144 and no return by the walk. Its route of 648 mutations has 58 at x and only 2 at vertex 2, one near each end. Between them it repeats six steps on the pair (1, 4), a turn at 0, six steps, a turn at 3: a walk round a cycle with m = 6 on the vertices 0, 1, 3, 4, with vertex 2 passive.
- **Where the walk is higher than the escape level**, the search found a lower route: a side of a pentagon, or mutations at x. The rows without a return by the walk have small escape levels, except the one above.
- **Consistency.** No row that the search closed below the cap has a walk that returns below the cap, with one exception that is none: (−1, 6, 3, 0) over R_5 reaches its opposite by the walk at height 12, and the search shows 42 quivers of height ≤ 6 joined to it within height 6, so the two are joined below the walk. No row that ran over the budget for a = 3, 5, 6 has a walk that returns, and one has for a = 4, at height 10. So the rows over budget do not hide a higher walk round this cycle.
- **a = 7 and 8.** The rules give 1,242 and 1,868 as the largest walk heights over all 41,905 and 65,341 rows (cap 6w³), for the rows (−4, 5, 8, −8) = Q_7 and (−6, 6, 9, −8). For each a the eight rows of largest walk height were searched, and all sixteen escape levels equal the walk heights.

### 6.3 The rows with the slopes of Q_a

`np_rowwalk.py shape` searches the 20 rows with x1 + x4 = −(2a − 2), x2 + x3 = 2a − 1 and x2, x3 ≥ 0 (`np_rowwalk_shape.log`).

| a | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Largest escape level | 23 | 88 | 214 | 437 | 765 | 1,242 | 1,868 | 2,695 | 3,715 | 4,988 | 6,498 | 8,313 | 10,409 |
| H(a) | 21 | 88 | 212 | 437 | 763 | 1,242 | 1,866 | 2,695 | 3,713 | 4,988 | 6,496 | 8,313 | 10,407 |

For odd a the best of them is Q_a. For even a it is (−(a − 2), a − 2, a + 1, −a), which is 2 higher. The other 18 rows are lower by amounts of order a², for example 428, 426, 419, 417, 393 at a = 5.

### 6.4 Every cycle at heights 3, 4 and 5

R_a is the lowest quiver of the cycle with m = 2a + 1. A quiver of height w can also lie on a shorter cycle, at any position of height ≤ w. `np_rowwalk.py allbases` takes every 5-vertex quiver of height ≤ w that consists of a position of a cycle W_m, 3 ≤ m ≤ 2w − 1, and a fifth vertex, and walks it by the rules (cap 8w³, at most 40w² rounds). The mirror image of a backward walk is a forward walk from another quiver of the list. The table gives the largest walk height for each m (`np_rowwalk_allbases.log`).

| w | Quivers | m = 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| 3 | 14,406 | 24 | 33 | 86 | | | | |
| 4 | 85,293 | 32 | 44 | 107 | 84 | 99 | | |
| 5 | 322,102 | 40 | 55 | 133 | 152 | 135 | 184 | 272 |

The quivers of largest walk height were then searched (cap 8w³, fork pruning).

| w | Walk heights, in order | Escape levels by search |
|---|---|---|
| 3 | 86, 70, 61, 45, 33, 31 | 8, 70, 8, 45, 24, 28 |
| 4 | 107, 106, 102, 99, 97, 96, 96, 95 | 107, 106, 102, 99, 97, 96, 96, 11 |
| 5 | 272, 245, 218, 214, 212, 207, 205, 198 | 272, 245, 218, 214, 212, 207, 205, 198 |

- **A walk height is an upper bound for the escape level.** Where the search finds less (8, 8, 24, 28 and 11), another route is lower.
- **The largest escape levels confirmed are 70, 107 and 272: the records of note 16 at w = 3, 4 and 5.** At w = 4 the census of note 16 covered only quivers with at least four entries ±2. Its first three values 107, 106, 102 are the first three here, and the quivers are the same up to relabelling.
- **Which cycle leads.** At w = 3 and 4 it is the cycle with m = 5, with two pairs of bounces. At w = 5 it is the longest cycle, m = 9 = 2w − 1, with one: the eight best quivers are rows over R_4, and the best quiver on a shorter cycle has walk height 184.

### 6.5 The records by height

**The largest escape levels found on 5 vertices.**

| w | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| Largest escape level found | 14 | 70 | 107 | 272 | 437 | 765 | 1,242 | 1,868 |
| Source | census, note 16 | census; R_2, m = 5 | census; m = 5 (R_3 gives 99) | R_4 | Q_5 | R_6, scan | Q_7, scan | R_8, rules and search |
| / w³ | 1.8 | 2.6 | 1.7 | 2.2 | 2.0 | 2.2 | 2.4 | 2.6 |
| / w^{5/2} | 2.5 | 4.5 | 3.3 | 4.9 | 5.0 | 5.9 | 6.9 | 7.7 |

Note 16 saw the first five values and found no trend against w^{5/2}. The values at w = 3 and 4 come from the cycle with m = 5 and two pairs of bounces, which lies above the family there. From w = 5 on, the rows over R_a with the slopes of Q_a lead, and 4w³ − 15w² happens to be close to 5·w^{5/2} at w = 5 and 6.

---

## 7. Why this design gives degree 3

**Why the slopes of Q_a [I].** By Proposition 18.3(4) a bounce of the column on (r, s) takes (d, e) to (d − e, −e). If e = 2d this is (−d, −e): both rates are reversed. With the right offsets the walk then retraces itself in mirror image, by Lemma 18.2(M), and ends at the opposite quiver; in Q_a this is the identity at the top. The smallest such slopes are (1, 2). The slopes that reach (1, 2) after one or two pairs of bounces are

M⁻¹·(1, 2) = (m − 3, m − 2),  M⁻²·(1, 2) = (m² − 5m + 5, m² − 4m + 2).

For m = 2a + 1 the first is (2a − 2, 2a − 1), the slopes of Q_a. For m = 5 the second is (5, 7), the slopes of the record at w = 3 after its first step.

**Other rows do not come back [I, H].** M has determinant 1 and trace m − 2, so for m ≥ 5 it has an eigenvalue above m − 3. Its expanding direction (1, 1 + λ), with λ the large eigenvalue, lies inside the cone 0 < d < e, m·d < (m − 1)·e where Proposition 18.3(5) applies again. So the slopes of a generic row grow at every pair of bounces, both columns end up climbing, and no quiver of low height is reached. This fits the scans: the walk returns for 457 of 3,321 rows at a = 3 and for 3,229 of 65,341 at a = 8.

**The count [H].** Take a quiver of height w on a cycle with parameter m, with slopes (m − 3, m − 2).
- m ≤ 2w − 1, because W_m(j) has height at least (m + 1)/2.
- The column on (p, q) reaches A* ≤ w + (w − 1)(m − 3) + m·(w − 1) ≈ 2mw before it starts to fall: at most w − 1 steps to the end of the line at slope m − 3, and one round at slope at most w − 1.
- While it falls by m per round, the other column climbs by m − 2 per round, to about A*·(m − 2)/m.
- Then that column falls by 2 per round, and the first climbs by m per round, to about A*·(m − 2)/2 ≲ w·m².

So the height is at most about w·m² ≤ 4w³, and Q_a has m = 2w − 1 and A* = 4a² + 1. For slopes k·(m − 3, m − 2) with k ≥ 2 the cycle must be shorter by the factor k. For two pairs of bounces the starting slopes are of order m², so m is of order √(2w); the same count gives a height of order m·(2w)², that is w^{5/2}. In general j pairs of bounces give the exponent 2 + 1/j. This is a count for walks round one bounce cycle with a passive fifth vertex. It is not an upper bound for F(5, w).

**Against Lemma 16.8.** Lemma 16.8 says that a route which never mutates x has a height linear in the row of x. That is so here, for each a. The degree 3 comes from the four other vertices: R_a changes with w, the cycle has length 2w, and the number of rounds is 4a² − a + 6.

---

## 8. Six vertices at w = 2

**Method** (`np_rowwalk.py sample`, `recheck`; `np_rowwalk_sample_n6_w2.log`, `np_rowwalk_sample_n6_w2_recheck.log`). 40,000 quivers on 6 vertices were drawn with independent entries: ±2 with probability 0.5, 0 with probability 0.15, ±1 otherwise. Of these, 9,680 have height 2 and are isolated (every mutation is higher than 2), and 9,664 remain up to relabelling and reversal. Each was searched with fork pruning, cap 1,024 and a budget of 30,000 quivers.

| Quivers | Escape found | Closed below the cap | Over budget | Largest escape levels |
|---|---|---|---|---|
| 9,664 | 1,663 | 0 | 8,001 | 18, 14, 13, 11, 11, 11 |

- **The record of the sample is 18**, for (−2, −2, −1, 0, 2, −2, −2, 2, 1, 1, −2, −2, 0, −1, −2), by a route of 91 mutations, none of them at vertex 4. On 5 vertices the record at w = 2 is 14.
- **Most searches did not finish.** 500 of the 8,001 quivers over budget were searched again with a budget of 300,000: none has an escape, 4 close below the cap and 496 run over the budget again.
- **Validation.** With n = 5 the same sampler draws 1,999 isolated quivers and finds the largest escape levels 14 and 13, the first two of the census of note 16 (`np_rowwalk_sample_n5_w2.log`).

So the sample says little. On 6 vertices at height 2 the sets below the cap are too large for these budgets, and 83 % of the sample is undecided. The value 18 is a lower bound for the largest escape level of a 6-vertex quiver of height 2. A census in the sense of note 16 was not run.

---

## 9. The degree of F(n, w)

**What is established.**

| n | Lower bound for F(n, w) | Status | Upper bound |
|---|---|---|---|
| 3 | w | Theorem 3.1 | w |
| 4 | 2w² − 7w + 2 | Corollary 15.14, proved | 2w² conjectured (10.1) |
| 5 | 2w^{5/2} − 11w² for every w ≥ 4 | Corollary 16.7, proved (computer-assisted) | none |
| 5 | 4w³ − 15w² + 19w − 11 for 3 ≤ w ≤ 23 | Corollary 18.6: route proved for every w, lower bound by exhaustive search | none |
| ≥ 6 | as for 5, with isolated vertices | | none |

**Conjecture 18.7 [H].**
- (a) For every a ≥ 2, Q_a and −Q_a are joined at exactly H(a). Hence F(5, w) ≥ 4w³ − 15w² + 19w − 11 for every w ≥ 3, and F(5, w)/w^{5/2} is unbounded.
- (b) F(5, w) = Θ(w³).

*For (a).* Theorem 18.4 gives the route for every a. Theorem 18.5 gives the lower bound for a ≤ 22 without any pruning, and the search with pruning for a ≤ 26. The escape level equals H(a) at every one of these values, for both parities, and the number of quivers below H(a) grows smoothly. *For (b)* there is only this: the scans of every row over R_a for a ≤ 7, with cap 16w³, find nothing above the neighbours of Q_a, and the count of §7 gives 4w³ for walks of this kind. Other 4-vertex classes and routes that mutate all five vertices were not searched at these heights.

> **Follow-up (note 20):** (a) holds for 2 ≤ a ≤ 64, so the bound on F(5, w) in the table above holds for 3 ≤ w ≤ 65. It is open for a ≥ 65. A proof by a certificate as in note 16 is blocked: the class of R_a has infinitely many quivers that are not forks, on two spirals at the ends of the bounce cycle where ten mutations multiply the entries of a fourth vertex by a matrix with eigenvalue φ⁸ ≈ 47, and the set a certificate must cover follows them further as a grows. See [note 20](20-core-of-the-cubic-family.md) §6 and §8.

> **Correction (note 23):** "Blocked" is too strong. A certificate whose families are indexed by the words from the route is blocked, as measured up to a = 48. One whose families are parametrised by their state along the spirals was not tried ([note 23](23-checks-of-notes-20-to-22.md) §4.2).

**Conjecture 16.9, F(5, w) = Θ(w^{5/2}), is withdrawn in its upper half.** It is contradicted for 4 ≤ w ≤ 23 by the factors of the table in §5.2, and it would be refuted for all w by Conjecture 18.7(a).

**Question 18.8.** Is the degree of F(n, w) equal to n − 2? The known lower bounds are w, 2w² − O(w) and 4w³ − O(w²) for n = 3, 4, 5, the last on a finite range. A construction of degree 4 on 6 vertices is not known. Two passive vertices x, y over one cycle each follow the rules of Lemma 18.2. The entry between them changes only at a mutation where their entries point in opposite directions, which happens where a column of one of them passes its bottom, and then by the product of a bottom entry of one and an entry of the other. So two passive vertices can change the constant, and a higher exponent seems to need a sixth vertex that is mutated, or a cycle on five vertices [H].

**For the wider question.** Conjecture A of note 3 §6 (a polynomial F(n, w)) is still open. On 5 vertices a bounded search needs a bound of at least 4w³ − 15w² for w ≤ 23, and the routes it must find have about 8w³ mutations.

---

## 10. Limitations

- **The lower bound is a computation, and it stops at a = 22** (a = 26 with fork pruning). For larger a only the route is known. Theorem 18.5 rests on `np_barrier`, which was validated in note 16 and here against a pure-Python search for a ≤ 7.
- **Theorem 18.4 was derived by hand from Lemmas 18.1 and 18.2 and checked by integer mutation for a ≤ 48.** No symbolic certificate was written for it.
- **§7 is a heuristic count.** Proposition 18.3 is proved, but the statements about which rows return and how high they go were only compared with the scans.
- **The scans are not exhaustive.** They prune forks, stop at 16w³ and at a budget. For a = 8 no scan was run; the rules of §6.2 cover every row, but only for walks round the cycle of R_a.
- **Only the class of R_a was studied.** Other bases with a cycle, such as W_m(j) for even m or for j away from the middle, and cycles of other shapes were not searched systematically. The two exceptions met on the way (§4, §6.2) are cycles with m = 5 and 6.
- **Six vertices.** §8 is a small random sample at w = 2 with a low budget.
- **Prior art.** No new search of the literature was made; see note 16 §8.

---

## 11. Reproduce

```bash
PY=python
$PY -I np_corridor.py build                                   # gcc -O2, binary in ~/.cache/qmb-np/
$PY -I np_rowwalk.py cycle --mmax 41 --rows 40 --amax 20 > np_rowwalk_cycle.log
$PY -I np_rowwalk.py phases --rows 2,-3,-2,-1,2 3,-3,-4,2,1 4,-5,-5,3,1 5,-2,3,6,-6 6,-4,4,7,-6 > np_rowwalk_phases.log
$PY -I np_rowwalk.py blocks --quiver -2 3 6 -6 -6 -5 2 -2 -5 -6 --cap 8000          # the route of the search for Q_5, in runs
$PY -I np_rowwalk.py blocks --quiver -4 -2 1 2 1 -4 -2 -2 3 -4 --cap 4000           # the census record of w = 4
$PY -I np_rowwalk.py family --amin 2 --amax 22 --search-amax 22 --prune 0 --budget 120000000 \
    --out np_rowwalk_family.jsonl > np_rowwalk_family.log                            # about 35 minutes, 9 GB
$PY -I np_rowwalk.py family --amin 23 --amax 26 --search-amax 26 --prune 1 --budget 140000000 > np_rowwalk_family_pruned.log
$PY -I np_rowwalk.py family --amin 23 --amax 48 --search-amax 0 > np_rowwalk_family_route_only.log
$PY -I np_rowwalk.py pycheck --amin 2 --amax 7 > np_rowwalk_pycheck.log
$PY -I np_rowwalk.py scan --a 3 --budget 60000 --out np_rowwalk_scan_a3.jsonl.gz > np_rowwalk_scan_a3.log
$PY -I np_rowwalk.py scan --a 4 --budget 100000 --out np_rowwalk_scan_a4.jsonl.gz > np_rowwalk_scan_a4.log
$PY -I np_rowwalk.py scan --a 5 --budget 150000 --out np_rowwalk_scan_a5.jsonl.gz > np_rowwalk_scan_a5.log
$PY -I np_rowwalk.py scan --a 6 --budget 400000 --out np_rowwalk_scan_a6.jsonl.gz > np_rowwalk_scan_a6.log     # 8 minutes, 12 workers
$PY -I np_rowwalk.py scan --a 7 --budget 700000 --out np_rowwalk_scan_a7.jsonl.gz > np_rowwalk_scan_a7.log     # 28 minutes
for al in "3 30" "4 60" "5 100" "6 200"; do set -- $al; $PY -I np_rowwalk.py walks --a $1 --scan np_rowwalk_scan_a$1.jsonl.gz --level $2 --top 6; done > np_rowwalk_walks.log
for a in 7 8; do $PY -I np_rowwalk.py walks --a $a --capf 6 --top 8 --verify 8; done > np_rowwalk_walks_a7_a8.log
$PY -I np_rowwalk.py shape --amin 2 --amax 14 --budget 6000000 > np_rowwalk_shape.log
for w in 3 4 5; do $PY -I np_rowwalk.py allbases --w $w --verify $((w == 3 ? 6 : 8)); done > np_rowwalk_allbases.log
$PY -I np_rowwalk.py sample --n 6 --w 2 --draws 40000 --cap 1024 --budget 30000 --seed 1 \
    --out np_rowwalk_sample_n6_w2.jsonl.gz > np_rowwalk_sample_n6_w2.log
$PY -I np_rowwalk.py recheck --file np_rowwalk_sample_n6_w2.jsonl.gz --take 500 --budget 300000 \
    --out np_rowwalk_sample_n6_w2_recheck.jsonl.gz > np_rowwalk_sample_n6_w2_recheck.log
$PY -I np_rowwalk.py sample --n 5 --w 2 --draws 60000 --cap 512 --budget 20000 > np_rowwalk_sample_n5_w2.log
```

- `np_rowwalk.py` needs `np_corridor.py`, `np_barrier.c` and, for `sample`, numpy from the venv.
- The `family` search allocates its tables for the whole budget: about 70 bytes per quiver.
- The pruned `family` run was started for a = 23 to 30 and stopped by hand after a = 26; its log says so, and it has no `.jsonl`. `pycheck` was started for a = 8 as well and stopped. The first lines of the three `family` logs carried an older theorem number and were corrected by hand to the number the theorem had at the time (it is now 18.4).
- The scans for a = 3, 4, 5 were run with 4 workers, those for a = 6, 7 with 12; the machine was shared, so the times are upper bounds.

---

## Sources

- Notes [15](15-rank-2-orbits-and-the-constant-2.md) and [16](16-five-vertices-above-w-squared.md) of this repository: Lemma 15.5 (fork exclusion), Lemmas 16.1 to 16.3 (step, turn, top) with the corollary of note 16 §2, Lemma 16.8 (scaling a row), Theorem 16.5 and its method, the census and the row scans of note 16 §6, and Conjecture 16.9.
- [Note 17](17-checks-of-note-16.md), the check of note 16: Lemma 15.5 on any number of vertices (§7).
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Def. 2.1 and Lemma 2.5, as quoted in notes 3 and 15 (not read here): https://d-nb.info/1214302807/34
