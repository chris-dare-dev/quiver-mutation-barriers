# 15. The constant 2 is sharp: two mirror families at 2w² − O(w), rank-2 orbits, and where the acyclic method stops

*Run on 2026-11-11. The aim was an effective upper bound on f(Q, w) for mutation-cyclic 4-vertex quivers, with Conjecture 10.1 (F(4, w) ≤ 2w²) as the target. No upper bound for all classes is proved here. What is proved: a new lower bound, which shows the constant 2 cannot be lowered; the complete structure of the orbits of two mutations; a quadratic bound for joins inside such an orbit; and a precise statement of why the method of arXiv 2610.36179 does not carry over. Code: [experiments/n4_doors.py](../experiments/n4_doors.py) (new, pure Python, no packages). Results: the `n4_doors_*.log` files. Quivers are up to relabelling. A quiver is written as the tuple (b01, b02, b03, b12, b13, b23) of the entries above the diagonal; b_ij > 0 means b_ij arrows i → j. Height means maximal entry. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

---

## 1. Outcome

1. **The lower bound doubles, to 2w² − 7w + 2 [I, proved].** For b ≥ 5 let

   R_b = (−b, −b, b − 1, −2, b − 2, −b).

   For every even b ≥ 6, R_b and −R_b are different quivers of height b in one mutation class, joined by a route of height 2b² − 3b − 3 and by no lower route (Theorem 15.13). Hence F(4, w) ≥ 2w² − 7w + 2 for every w ≥ 6 (Corollary 15.14). Theorem 9.1 gave w² − w. So liminf F(4, w)/w² ≥ 2, and Conjecture 10.1, if true, is sharp up to a linear term. For odd b the same value was measured for 5 ≤ b ≤ 59 and is not proved. R_8 is the bottom-8 extreme of note 10 (death 101), and at each of the heights 10, 11 and 12, R_b has the largest death among all quivers with an entry ±2.
2. **A second family, of another type [I, proved].** For t ≥ 3, Q_t = (−t², −(t² − 1), 2t, −2, t(t − 1), −t²) has height t² and is joined to −Q_t at exactly H_t = 2t⁴ − t³ − t² + 2t (Theorem 15.6). In R_b the barrier is a plateau: b(b − 1)/2 consecutive quivers of height exactly 2b² − 3b − 3 on one weight-2 line. In Q_t it is a single commuting square at the end of a corridor of about 2t³ steps.
3. **How the proofs work [I].** A reduced route between two quivers of height ≤ w never passes a fork higher than w (Lemma 15.5, from Warkentin's Lemma 2.5). So a reduced route from R_b to −R_b that stays below the barrier can use only b/2 + 3 quivers, and for Q_t only 2t³ − t² + 5. Each of their exits is another member, a quiver at or above the barrier, or a fork higher than the starting height. These are polynomial statements, 30 for R_b and 43 for Q_t. `n4_doors.py prove2` and `prove` certify each for all parameters by expanding a polynomial at its lower bounds and checking that no coefficient is negative. The same structures were found by search for b ≤ 60 and t ≤ 30.
4. **Orbits of two mutations are completely described [I, proved].** Take a pair of vertices with c ≥ 2 arrows and mutate alternately at its ends. In suitable coordinates one step is the piecewise linear map (x, y) ↦ (y + c·[x]₊, −x) on the two entries from each other vertex (Theorem 15.1). Each such column is V-shaped along the orbit. The sixth entry z changes only where a column passes its bottom. The quantity c·z − (x_k y_l − x_l y_k) is constant and equals ±Pf.
5. **A proved special case of the quadratic bound [I].** Two quivers of height ≤ w in the same orbit of two mutations are joined inside that orbit within height w² + w (Proposition 15.3). By brute force, commuting squares come within about w/2 of w² (w² − ⌈w/2⌉ for w ≤ 8); on the infinite orbits the maximum is near w + w²/4.
6. **The corridor lemma of note 11, corrected [I].** On a weight-2 line, between the two bottoms, the slopes s_k, s_l, the distance D between the bottoms and the constant value ζ of z satisfy

   s_k·s_l·(D − 3) + s_l·a_k + s_k·e_l = ±Pf − 2ζ (Corollary 15.2).

   Note 11's proposed lemma (run ≤ b − 1, increment ≤ 2b) is true for a corridor that starts at a quiver of height ≤ b. It does not bound the worst joins. In R_b the barrier is ζ itself, on a line entered at height b² − b. In Q_t the long corridor starts at height about 2b^{3/2}, with b = t², and has increments √b and 1.
7. **Both barriers follow the Pfaffian [I].** Pf(R_b) = 2(b − 1)² and the barrier is |Pf| + b − 5; Pf(Q_t) = H_t − 5t. A quiver of height w has |Pf| ≤ 2w² unless it is a vortex.
8. **Doors [I].** A door is an oriented 4-cycle with weights p, q, r, s and one diagonal (rs − pq)/2. Mutating at the two vertices off the diagonal gives its opposite, and both intermediate quivers have height (pq + rs)/2 when that exceeds p, q, r and s (§6). The census extremes at births 4 to 7 are the doors (16, 1, 2, 20), (20, 1, 2, 35), (24, 1, 2, 54) and (24, 1, 2, 67), and Q_t crosses at the door (2t, 1, 2, H_t − t). A scan of 702,945 doors with q, r ≤ 5 that separate their two sides found no ratio above 1.834 for bottoms ≤ 30.
9. **The method of arXiv 2610.36179 does not extend as it stands [P, I] (§7).**
   - The invariant it uses is available: of the 27,554 census classes with a pocket born at ≤ 9, 27,507 have exactly one proper wiggle class that survives proper mutations to depth 4. Its Markov value M is negative for 25,100 of them. G_k has M = −k⁴ + k³ + 4k² − 2k + 1, R_b has M = −2b³ + 5b² + 9 and Q_t has M = −4t⁵ + 2t⁴ + 2t³ + t² + 5.
   - The inequalities it needs are not: 3 ≤ m and 2|Pf| < m come from an acyclic quiver in the class. Without them each local lemma has counterexamples in these classes (doors for Lemma 4.2, the plateau of R_b for Lemma 4.5).
   - No bound of the same shape holds. V_b = (−b, 2, −1, −b, 1, 1) has one proper wiggle class, M = 5 and Pf = −2 for every b ≥ 3, and it is joined to −V_b only at height b + 1 (Proposition 15.8). So f(Q, w) ≤ max(w, T₀) fails for every T₀ that depends only on M and Pf.
   - On the census the latest death exceeds |M| in 1,976 classes (113 against 8 in the worst), max(|M|, 2|Pf|) in 15 and |M| + 2|Pf| in 5, each of those five by exactly 1.
10. **What an upper bound still needs [I, H] (§8).** For all 30,527 census pockets born at ≤ 9 there is a join of least height on which every quiver at the top height has an entry of absolute value ≤ 2. So the summits lie on squares, pentagons and weight-2 lines, where §3 applies. What is missing is a bound on ζ along a line and on the door at its end. Conjecture 10.1 is still open. Nothing found exceeds 2w² − w.

---

## 2. Notation

- **Mutation, height, routes.** As in notes 3 to 12. A *route* is a sequence of mutations; its height is the largest height of a quiver on it. Two quivers are *joined at L* if some route between them has height ≤ L. A labelled route is *reduced* if no two consecutive mutations are at the same vertex. Cancelling such a pair removes two quivers from the route, so every route can be reduced without raising its height.
- **f and F.** f(Q, w) is the least L at which all quivers of height ≤ w in the class of Q are joined. F(n, w) is its maximum over n-vertex quivers.
- **Pfaffian.** Pf = b01·b23 − b02·b13 + b03·b12. A mutation changes its sign, and a relabelling multiplies it by the sign of the permutation, so |Pf| is a class invariant [P, note 11 §2]. If one quiver of the class has height w, then |Pf| ≤ 3w².
- **[x]₊** = max(x, 0).

---

## 3. Orbits of two mutations

### 3.1 Line coordinates

Fix two vertices i, j with c = b_ij ≥ 0 and let k, l be the other two. For u = k, l put x_u = b_ui and y_u = b_uj, and put z = b_kl. Write the quiver as

Λ_c(x_k, y_k; x_l, y_l; z), which is the tuple (c, −x_k, −x_l, −y_k, −y_l, z) for the vertex order (i, j, k, l).

The pair (x_u, y_u) is the *column* of u. A *forward step* mutates at i and then exchanges the names of i and j, so that the arrows of the pair again point from the first vertex to the second. A backward step mutates at j and exchanges the names. The orbit of the quiver under the two mutations, up to relabelling, is the sequence of forward and backward steps. Positions on it are numbered by n ∈ ℤ.

**Theorem 15.1 (orbits of two mutations) [I].**

1. **The step.** A forward step takes Λ_c(x_k, y_k; x_l, y_l; z) to Λ_c(σ(x_k, y_k); σ(x_l, y_l); z′), where

   σ(x, y) = (y + c·[x]₊, −x),  z′ = z + [x_k]₊·[−x_l]₊ − [−x_k]₊·[x_l]₊.

   The backward step is the inverse: σ⁻¹(x, y) = (−y, x − c·[−y]₊).
2. **The invariant.** P = c·z − (x_k·y_l − x_l·y_k) does not change, and |P| = |Pf|.
3. **Columns (c ≥ 2).** A nonzero column is of exactly one of two types.
   - *With a bottom.* There are unique integers a ≥ 1, e ≥ 0 and t such that, with p₀ = −e, p₁ = a, p_{m+1} = c·p_m − p_{m−1} and q₀ = −a, q₁ = e, q_{m+1} = c·q_m − q_{m−1}, the column is

     (−e, a) at position t,  (p_m, −p_{m−1}) at t + m,  (q_{m−1}, −q_m) at t − m  (m ≥ 1).

     Both sequences increase strictly from m = 1 on. The first entry x is negative at t − 1, non-positive at t, and non-negative everywhere else.
   - *Always cyclic.* x > 0 > y at every position, and the column is (v_n, −v_{n−1}) with v_{n+1} = c·v_n − v_{n−1} and all v_n ≥ 1. For c = 2 this means that v is constant.
4. **Valley.** For each column, W(n) = max(|x|, |y|) is non-increasing up to some position and non-decreasing after it. So W(n) ≤ max(W(n₁), W(n₂)) for n₁ ≤ n ≤ n₂.
5. **z.** z(n + 1) ≠ z(n) only if one column has a bottom at t with n ∈ {t − 1, t} and the other column has x > 0 at n. If that column is k, z decreases by |x_k|·x_l; if it is l, z increases by x_k·|x_l|.

*Proof.* (1) is the mutation rule at i: the entry b_uj gains b_ui·b_ij when u → i → j, and b_kl gains [b_ki]₊[b_il]₊ − [−b_ki]₊[−b_il]₊ with b_il = −x_l. The arrows at i are reversed, so after the exchange of names the pair has c arrows from the first vertex to the second.

(2) In the order (i, j, k, l), Pf = b_ij·b_kl − b_ik·b_jl + b_il·b_jk = c·z − x_k·y_l + x_l·y_k. A direct computation from (1) gives (x_k·y_l − x_l·y_k)′ − (x_k·y_l − x_l·y_k) = c·(x_k·[x_l]₊ − x_l·[x_k]₊) = c·(z′ − z).

(3) Sort a nonzero column by signs. If x ≤ 0 ≤ y it is (−e, a) with a = y ≥ 1, or (−a, 0) = (q₀, −q₁) with e = 0. If x ≥ 1 and y ≥ 0 it is (p₁, −p₀). If x < 0 and y < 0 it is (q₀, −q₁). If x = 0 > y it is (q₁, −q₂) with e = 0. In each of these cases the formulas follow from (1) by induction, with p_{m+1} − p_m ≥ p_m − p_{m−1} ≥ a + e ≥ 1 and the same for q. There remains x > 0 > y. Then σ(x, y) = (c·x − |y|, −x). Either some forward or backward step leaves this region, and the column is of the first type, or none does. Uniqueness: t − 1 is the first position where x < 0.

(4) With a bottom, W = q_m at t − m and p_m at t + m for m ≥ 2, and W = max(a, e) at t − 1, t, t + 1; and p₂ = c·a + e and q₂ = c·e + a are at least max(a, e). An always-cyclic column has v_{n+1} − v_n ≥ v_n − v_{n−1}, so v is convex.

(5) follows from the formula for z′ and the signs in (3). ∎

**Remarks.**
- The full subquiver on {u, i, j} evolves as a 3-vertex quiver, so its Markov constant c² + x² + y² ∓ c·|xy| is constant along the orbit (minus for an oriented triangle). For c = 2 it is 4 + s² with s = a + e for a column with a bottom, and 4 for an always-cyclic one. A mutation at a vertex v changes the triangle opposite v and keeps the Markov constants of the three triangles through v.
- For c = 2 the entries are p_m = a + (m − 1)·s and q_m = e + (m − 1)·s: arithmetic progressions with increment s, the *slope* of the column.
- For c = 0 the orbit is a commuting square, and for c = 1 it is the pentagon with five quivers up to relabelling [P, the pentagon relation, as used in arXiv 2610.36179 (10)].
- The always-cyclic columns with c ≥ 3 are the mutation-cyclic triangles. Soukup's Theorem 1.3 [P, as quoted in arXiv 2610.36179 §4; not read here] describes the same orbits for ice quivers with two mutable vertices. I did not find the height statements below in the papers consulted.

### 3.2 The conservation law on a weight-2 line

**Corollary 15.2 [I].** Let c = 2 and let both columns have bottoms, at t_k < t_l, with slopes s_k, s_l. Put D = t_l − t_k and assume D ≥ 2. Then z is constant, say ζ, on the positions t_k + 1, …, t_l − 1, and

s_k·s_l·(D − 3) + s_l·a_k + s_k·e_l = P − 2ζ ≤ |Pf| + 2|ζ|.

Consequently, on these positions every entry of the two columns is at most (|Pf| + 2|ζ|)/min(s_k, s_l) + max(s_k, s_l).

*Proof.* At position n = t_k + m = t_l − m′ the columns are (p_m, −p_{m−1}) and (q_{m′−1}, −q_{m′}), with p for k and q for l. No step between these positions changes z, by Theorem 15.1(5). So x_k·y_l − x_l·y_k = −p_m·q_{m′} + p_{m−1}·q_{m′−1} = −(s_l·p_m + s_k·q_{m′} − s_k·s_l), and p_m = a_k + (m − 1)·s_k, q_{m′} = e_l + (m′ − 1)·s_l, m + m′ = D. For the last claim let D ≥ 3. The largest entry of column k on these positions is p_{D−1}, and s_l·p_{D−1} = P − 2ζ − s_k·e_l + s_k·s_l; the largest entry of column l is q_{D−1}, and s_k·q_{D−1} = P − 2ζ − s_l·a_k + s_k·s_l. If D = 2 there is one position, with the entries a_k, e_k ≤ s_k and a_l, e_l ≤ s_l. ∎

**The first corridor [I].** Let Q have height ≤ w and a pair of weight 2, and let one column of Q be an oriented triangle that descends in the direction walked. Then that column reaches its least height W within w − 1 steps, and until then every entry of the other column is at most 2w² − w. *Proof.* While it descends, the larger entry of the column falls by at least 1 at each step, from at most w to at least 1. The other column has slope at most 2w, because 4 + s² ≤ 4 + (|x| + |y|)², so each of its entries grows by at most 2w per step, from at most w. ∎ This is the lemma that note 11 §5 and §6 asked for. "Least height" matters: the bottom position t of Theorem 15.1(3) can be two steps further on, and for Λ₂(w − 1, −w; w, w; z) the other column is at 2w² − w after w − 1 steps and at 2w² + 3w there. The script checks the statement on all 4,403 descending columns with w ≤ 6 (`n4_doors_orbit.log`). The lemma bounds the first corridor only: after a square or a door (§5, §6) the next corridor starts from a quiver that is not low.

### 3.3 Joins inside an orbit

**Proposition 15.3 [I].** Let X and Y have height ≤ w and lie in the same orbit of the mutations at two vertices i, j. Then they are joined inside that orbit within height w² + w.

*Proof.* If |b_ij| ≤ 1 the orbit has at most five quivers up to relabelling, any two are joined through at most one other, and one mutation of a quiver of height w has height at most w + w².

Let c = |b_ij| ≥ 2 and let X, Y be at positions n₁ < n₂. By Theorem 15.1(4) every column entry at the positions between is at most w, so only |z| can exceed w. By (5), z falls at the steps t_k − 1 and t_k, by a_k·x_l and e_k·x_l, and rises at t_l − 1 and t_l, by a_l·x_k and e_l·x_k; a step where both x are ≤ 0 changes nothing. Assume t_k ≤ t_l.
- If t_l = t_k, z is constant.
- If t_l = t_k + 1, z falls by a_k·e_l at step t_k − 1 and rises by the same amount at step t_k + 1. Both factors are entries at positions between n₁ and n₂ when both steps are, so the dip is at most w².
- If t_l ≥ t_k + 2, z first falls and then rises. So z ≤ w throughout, and z ≥ −w − min(d_k, d_l), where d_k and d_l are the total fall and the total rise between n₁ and n₂. Each single change is a product of two entries at a position between n₁ and n₂, so it is at most w². If at most one fall or at most one rise lies between n₁ and n₂, this already gives min(d_k, d_l) ≤ w². If both falls and both rises do, then position t_k + 2 lies between n₁ and n₂ as well, so c·a_k + e_k ≤ w and d_k ≤ (a_k + e_k)·w ≤ w².
- If a column has no bottom, z is monotone between n₁ and n₂. ∎

**Brute force** (`n4_doors.py orbit`, `n4_doors_orbit.log`). The step formulas, the invariant, the triangle constants and the closed forms of Theorem 15.1(3) passed 160,000 random steps with c = 2 to 6 and 252 columns. For every starting point of height exactly w (385,728 at w = 7), the largest height strictly between two consecutive positions of height ≤ w is:

| w | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|
| c = 2 | 3 | 5 | 8 | 9 | 15 | 16 |
| c = 3 | – | 4 | 5 | 7 | 10 | 11 |
| c = 4 | – | – | 5 | 6 | 8 | 10 |

For c = 2 and w ≠ 3 these are w + ⌊w/2⌋²; at even w the extreme is Λ₂(−w/2, 0; w/2, −w; −w). So on the infinite orbits the bound of Proposition 15.3 is far from attained.

The finite orbits are different (`n4_doors.py orbit01`, `n4_doors_orbit01.log`). For every quiver of height exactly w with b01 = 0 or 1, the largest height needed inside the orbit to reach a non-isomorphic quiver of height ≤ w is:

| w | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| b01 = 0 (square) | 3 | 7 | 14 | 22 | 33 | 45 | 60 |
| b01 = 1 (pentagon) | 2 | 4 | 7 | 10 | 14 | 19 | 24 |
| w² + w | 6 | 12 | 20 | 30 | 42 | 56 | 72 |

The squares give w² − ⌈w/2⌉, for example (0, −4, 3, 4, −4, 2), whose two middle corners have height 14. So the bound w² + w is sharp up to a term of order w, and it is the commuting squares, the doors of §6, that attain it. A barrier of order 2w² never separates two quivers of height ≤ w of the same orbit. In §5.1 it lies on one weight-2 line, but the ends of that line have height about w².

---

## 4. Forks

A *fork* is a quiver with all entries of absolute value ≥ 2 that is not acyclic and has a vertex r, the point of return, such that b_ji > b_ir and b_ji > b_rj whenever i → r → j, and such that the in-neighbours and the out-neighbours of r each span an acyclic subquiver [P, Warkentin's thesis, Def. 2.1, as quoted in note 3 §5.2].

**Lemma 15.4 (Warkentin, Lemma 2.5) [P; proof re-derived here, I].** Let F be a fork with point of return r and let k ≠ r. Then μ_k(F) is a fork with point of return k, no entry of μ_k(F) is smaller in absolute value than in F, and the total weight is larger.

*Proof.* All arrows between an out-neighbour and an in-neighbour of r point from the first to the second. So an oriented triangle cannot avoid r: either its three vertices lie on one side of r, which is acyclic, or the vertex that is alone on its side is a source or a sink of the triangle. Now take i → k → j in F. If i → j, the entry grows by b_ik·b_kj. Otherwise j → i, the triangle contains r, and the entry opposite r is its largest. If i = r, the new weight between r and j is b_rk·b_kj − b_jr ≥ 2·b_kj − b_jr > b_kj > b_jr. The case j = r is the same. So every changed entry grows, and exceeds both b_ik and b_kj. That is the inequality required of the point of return k in μ_k(F). The in- and out-neighbours of k keep their arrows among themselves. A cycle among them would contain an oriented triangle, which passes through r and lies on one side of k. Then k and one vertex of the triangle lie on opposite sides of r, and the rule above gives the arrow between them the wrong direction. Finally F is not acyclic and both sides of r are acyclic, so r is neither a source nor a sink. Take i on the side of r opposite to k. Then {i, r, k} is an oriented triangle of F, and after μ_k it is an oriented triangle again, with the arrow between i and r reversed as computed above. So μ_k(F) is not acyclic. ∎

**Lemma 15.5 (fork exclusion) [I].** On a reduced route from X to Y, every fork has height at most max(ht X, ht Y).

*Proof.* Let R be a fork on the route with point of return r. If the route leaves R at k ≠ r, the next quiver is a fork with point of return k and is at least as high. The route is reduced, so it leaves that one at a vertex other than k, and so on to Y. Hence ht Y ≥ ht R. If the route leaves R at r, it arrived at some k ≠ r. Read backwards, it leaves R at k, and the same argument gives ht X ≥ ht R. ∎

Note 3 §5.2 already recorded the tree structure behind this, and note 14 §3 quotes it as (F1) and (F2) from Ervin, arXiv 2306.07502, Lemmas 2.7 and 2.8 [P]: the edge from a fork to its return mutation is a bridge of the labelled mutation graph, and the side of the fork is a tree of forks. Lemma 15.5 is the form that §5 uses.

> **Update (note 17):** The proofs of Lemmas 15.4 and 15.5 were re-read for their use on 5 vertices in note 16. Neither uses n = 4: they need only that every pair of a fork is joined, so that every vertex other than r lies on one side of r and every cycle contains an oriented triangle. On 20,000 random forks each with 5 and 6 vertices and on 400,000 random reduced routes, no exception was found. The definition of a fork above agrees with Ervin's Definition 2.5 (arXiv 2306.07502v2), read through an automated summary; his Lemma 2.7 states the fork and the larger number of arrows, and "no entry is smaller" is the part proved here. See [note 17](17-checks-of-note-16.md) §7.

> **Update (note 19):** Warkentin's thesis has now been read (https://d-nb.info/1214302807/34). Its Definition 2.1 is the definition above. Its Lemma 2.5 is Ervin's Lemma 2.7. The entry-wise statement "no entry of μ_k(F) is smaller" is in Warkentin's own proof, which begins: "for any two vertices i, j the number of arrows |q_ij| cannot decrease through the mutation". So Lemma 15.4 is [P] as stated, for every number of vertices. By his Lemma 2.3.e the point of return of a fork is unique. See [note 19](19-checks-of-notes-13-to-16.md) §4.

**Checks** (`n4_doors.py forks`, `n4_doors_forks.log`). Lemma 15.4 held on 120,000 mutations of 20,000 random forks. On the 139 optimal join paths stored by note 11, 2,364 quivers lie above the endpoints, and none is a fork.

---

## 5. Two families with barrier near 2w²

### 5.1 The plateau family R_b

*Numbering.* Theorem 15.13 and Corollary 15.14 were added last, after note 16 had cited Theorem 15.6 for Q_t; that is why their numbers are out of order.

**Theorem 15.13 [I].** Let b ≥ 6 be even and R_b = (−b, −b, b − 1, −2, b − 2, −b).
1. R_b and −R_b have height b, are not isomorphic and lie in one mutation class.
2. There is a route from R_b to −R_b of height 2b² − 3b − 3.
3. Every route from R_b to −R_b has height at least 2b² − 3b − 3.

**Corollary 15.14 [I].** F(4, w) ≥ 2w² − 3w − 3 for every even w ≥ 6, and F(4, w) ≥ 2w² − 7w + 2 for every w ≥ 6. In particular liminf F(4, w)/w² ≥ 2. The same bounds hold for F(n, w), n ≥ 5, if disconnected quivers are admitted (add isolated vertices).

*Proof.* For even w use R_w. For odd w use R_{w−1}, which has height w − 1 ≤ w, and 2(w − 1)² − 3(w − 1) − 3 = 2w² − 7w + 2. ∎

For connected quivers on n ≥ 5 vertices nothing is claimed: the argument of Proposition 12.1 used that no mutation of G_k is low, and that fails here.

> **Follow-up (note 16):** On 5 vertices more is true. Q_t with a fifth vertex attached (the quiver P⁺_t) is connected, has height t² and joins its opposite only at 2t⁵ − t⁴ + t² − 1, so F(5, w) ≥ 2w^{5/2} − 11w². The proof uses Lemma 15.5 and a certificate of the same kind as the one above. See [note 16](16-five-vertices-above-w-squared.md).

| b | 6 | 8 | 10 | 12 | 20 | 40 | 60 |
|---|---|---|---|---|---|---|---|
| 2b² − 3b − 3 | 51 | 101 | 167 | 249 | 737 | 3,077 | 7,017 |
| ratio to b² | 1.417 | 1.578 | 1.670 | 1.729 | 1.842 | 1.923 | 1.949 |
| b(b − 1) (Theorem 9.1) | 30 | 56 | 90 | 132 | 380 | 1,560 | 3,540 |

**The region.** Write b = 2c and H = 2b² − 3b − 3. In R_b the pair (2, 1) has weight 2. In line coordinates for that pair, with k = 0 and l = 3, put

- A(0) = Λ₂(−b, −b; b, −(b − 2); b − 1), which is R_b;
- A(j) = Λ₂((2j − 1)b, −(2j + 1)b; 2(c − j), −2(c − j − 1); b − 1) for 1 ≤ j ≤ c − 1;
- A(c) = Λ₂((2c − 1)b, −(2c + 1)b; 0, 2; b − 1);
- B = μ_l A(c − 1) = (2, −(b² − b − 2), 2, b² − b, 0, −(b − 1)) and B′ = μ_l A(c) = (2, −(b² − b), 0, b² − b + 2, 2, −(b − 1)), in the same labels.

A(0), …, A(c) are consecutive positions of one line. Column k is (−a, −e) with (a, e) = (b, b) at A(0), and climbs with slope 2b. Column l descends with slope 2 and is (2, 0) at A(c − 1). There l is joined to only one end of the pair, and the square of μ_j and μ_l has the corners A(c − 1), A(c), B, B′. The region 𝓡_b is the set of these c + 3 quivers. Their heights are b, 3b, 5b, …, (b − 1)b for A(0) to A(c − 1), (b + 1)b for A(c), b² − b for B and b² − b + 2 for B′. All are below H, and only A(0) is at or below b.

**The exits.** μ_i is the forward step and μ_j the backward step of the line of A; "fork" means a fork higher than b. For B and B′ the columns μ_i, μ_j refer to the pair (0, 1) of their tuples.

| Member | μ_i | μ_j | μ_k | μ_l |
|---|---|---|---|---|
| A(0) | fork | A(1) | fork | fork |
| A(j), 1 ≤ j ≤ c − 2 | A(j − 1) | A(j + 1) | height ≥ H | fork |
| A(c − 1) | A(c − 2) | A(c) | height ≥ H | B |
| A(c) | A(c − 1) | height ≥ H | height ≥ H | B′ |
| B | height = H | B′ | height ≥ H | A(c − 1) |
| B′ | B | fork | height ≥ H | A(c) |

**The plateau.** T = b(b − 1)/2. In the labels of B, with the pair (0, 1), put

P(m) = Λ₂(2(T − 1 − m), −2(T − m); 2(m − 1), −2(m − 2); H) for 2 ≤ m ≤ T − 1,

P(1) = Λ₂(2(T − 2), −2(T − 1); 0, 2; H) and P(T) = Λ₂(−2, 0; 2(T − 1), −2(T − 2); H). Then P(1) is the forward step of B, P(m + 1) is the forward step of P(m), and the forward step of P(T) is −B relabelled. This is Theorem 15.1 for B = Λ₂(b² − b − 2, −(b² − b); −2, 0; −(b − 1)): both columns have slope 2 and bottom (2, 0); the bottoms are T positions apart; and z jumps from −(b − 1) to −(b − 1) + 2·(b² − b − 2) = H at the first bottom and back at the second. Every column entry of P(m) is at most 2T = b² − b < H, so all T quivers of the plateau have height exactly H.

*Proof of Theorem 15.13.* **(3).** Suppose a route from R_b to a relabelling of −R_b has height below H. Reduce it. Its ends have height b, so by Lemma 15.5 it contains no fork higher than b. It starts at A(0). By the table, a mutation of a member of 𝓡_b is a member, has height ≥ H, or is a fork higher than b. So the route stays in 𝓡_b and ends at a member of height b, which is A(0). Then −R_b would be isomorphic to R_b. It is not: the pairs (out-weight, in-weight) of R_b are (b − 1, 2b), (2b − 2, 2), (b + 2, b), (b, 2b − 3), and no vertex of −R_b has in-weight 2.

**(2).** Go A(0), A(1), …, A(c − 1), then μ_l to B, then P(1), …, P(T), then to −B. Mutation commutes with reversing all arrows, so the mirror image of the first c steps leads from −B to −R_b. The route has b(b − 1)/2 + b + 1 steps and height H.

**(1)** follows from (2) and the pairs in (3). ∎

**Certification** (`n4_doors.py prove2`, `n4_doors_prove2.log`). The 30 claims are the cells of the table, the steps of the plateau, the heights of the members, and Pf(R_b) = 2(b − 1)² = H − (b − 5). They are certified for every c ≥ 3 by the method described in §5.4. For the general member A(j) the variables are j and v = c − 1 − j on the domain {j ≥ 1, v ≥ 1}; for the general step of the plateau they are m and u = T − 1 − m on {m ≥ 2, u ≥ 1}.

**Numerical check, and odd b** (`n4_doors.py family3 --bmax 60`, `n4_doors_family3.log`). For every b from 5 to 60 a bottleneck search that uses no forks returns 2b² − 3b − 3 as the least height at which R_b reaches another quiver of height ≤ b, with −R_b as the quiver reached. For even b the search from R_b through non-forks below H and forks of height ≤ b gives exactly 𝓡_b, the exits are as in the table, and the plateau has b(b − 1)/2 quivers. For odd b the region has a different shape, because column l passes its bottom at (1, ·), and I did not write out the proof. So F(4, w) ≥ 2w² − 3w − 3 is proved for even w ≥ 6 and measured for odd w from 5 to 59 [I].

**In the census.** R_8 is the bottom-8 extreme of note 10 (death 101), whose join path note 11 printed without recognising a family: 3 steps, a square, a plateau of 28 quivers. R_9 is one of the two pockets (9, 132), and R_5, R_6, R_7 give 32, 51, 74, below the census maxima 45, 66, 79.

### 5.2 The door family Q_t

For t ≥ 3 put N = 2t³ − t² − t and H_t = t·(N + 2) = 2t⁴ − t³ − t² + 2t.

**Theorem 15.6 [I].** Let Q_t = (−t², −(t² − 1), 2t, −2, t(t − 1), −t²).
1. Q_t and −Q_t have height t², are not isomorphic and lie in one mutation class.
2. There is a route from Q_t to −Q_t of height H_t.
3. Every route from Q_t to −Q_t has height at least H_t.

**Corollary 15.7 [I].** F(4, w) ≥ H_⌊√w⌋ ≥ 2w² − 9·w^{3/2} for every w ≥ 9.

*Proof.* With t = ⌊√w⌋ we have t ≤ √w < t + 1, so t⁴ > w² − 4w^{3/2} + 6w − 4√w + 1, and H_t > 2t⁴ − t³ − t² ≥ 2w² − 9w^{3/2} + 11w − 8√w + 2. ∎

This is weaker than Corollary 15.14; the script confirms the inequality for w ≤ 200,000. The interest of the family is its mechanism: the barrier is a door, and the corridor leading to it is far longer than the height of Q_t. Note 16 uses Q_t as a block on 5 vertices.

| t | 3 | 4 | 5 | 6 | 8 | 10 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| height t² | 9 | 16 | 25 | 36 | 64 | 100 | 400 | 900 |
| H_t | 132 | 440 | 1,110 | 2,352 | 7,632 | 18,920 | 311,640 | 1,592,160 |
| H_t / t⁴ | 1.630 | 1.719 | 1.776 | 1.815 | 1.863 | 1.892 | 1.948 | 1.966 |
| 2b² − 3b − 3 at b = t² (R_b; measured only, at b = 9 and 25) | 132 | 461 | 1,172 | 2,481 | 7,997 | 19,697 | 318,797 | 1,617,297 |

### 5.3 The region of Q_t below H_t

In Q_t the pair (2, 1) has weight 2. In line coordinates for that pair, with k = 0 and l = 3, put q_m = t² + (m − 1)·(2t² − 1) and

- K(0) = Λ₂(−(t² − 1), −t²; t², −t(t − 1); 2t), which is Q_t;
- K(j) = Λ₂(q_j, −q_{j+1}; t(t − j), −t(t − j − 1); 2t) for 1 ≤ j ≤ t − 1;
- K(t) = Λ₂(q_t, −q_{t+1}; 0, t; 2t).

These are t + 1 consecutive positions of one line. Column k is (−a, −e) with (a, e) = (t² − 1, t²) at K(0), and climbs with slope 2t² − 1. Column l descends with slope t and is (t, 0) at K(t − 1). Note that q_t = N + 1.

The second line is

- L(n) = Λ₂(t(n − 1), −tn; N + 2 − n, −(N + 1 − n); 2t) for 1 ≤ n ≤ N + 1;
- L(0) = Λ₂(−t, 0; N + 2, −(N + 1); 2t), L(−1) = Λ₂(0, t; N + 3, −(N + 2); −tN), L(−2) = Λ₂(t, 0; N + 4, −(N + 3); −tN).

These are N + 4 consecutive positions of one line. Column k climbs with slope t as n grows. Column l descends with slope 1 and reaches (1, 0) at n = N + 1. Between the bottoms z = 2t. Corollary 15.2 reads t·(N + 1) = |Pf| + 4t, with |Pf(Q_t)| = 2t⁴ − t³ − t² − 3t = H_t − 5t.

The two lines are glued by one commuting square: in K(t − 1) the vertex l is joined to only one end of the pair, and μ_l K(t − 1) = L(0), μ_l K(t) = L(1).

**The region** 𝓜_t is the set of these (t + 1) + (N + 4) = 2t³ − t² + 5 quivers. Their heights are t² for K(0), q_{j+1} for K(j) with j ≥ 1 (so N + 1 for K(t − 1) and N + 2t² for K(t)), max(tn, N + 2 − n) for L(n) with n ≥ 1, N + 2 for L(0) and tN for L(−1), L(−2). All are below H_t, and only K(0) is at or below t².

**The exits.** Here μ_i is the forward step, μ_j the backward step, and "fork" means a fork higher than t².

| Member | μ_i | μ_j | μ_k | μ_l |
|---|---|---|---|---|
| K(0) | fork | K(1) | fork | fork |
| K(j), 1 ≤ j ≤ t − 2 | K(j − 1) | K(j + 1) | height ≥ H_t | fork |
| K(t − 1) | K(t − 2) | K(t) | height ≥ H_t | L(0) |
| K(t) | K(t − 1) | height ≥ H_t | height ≥ H_t | L(1) |
| L(−2) | fork | L(−1) | height ≥ H_t | height ≥ H_t |
| L(−1) | L(−2) | L(0) | height ≥ H_t | height ≥ H_t |
| L(0) | L(−1) | L(1) | K(t − 1) | height ≥ H_t |
| L(1) | L(0) | L(2) | K(t) | height ≥ H_t |
| L(n), 2 ≤ n ≤ N | L(n − 1) | L(n + 1) | fork | height ≥ H_t |
| L(N + 1) | L(N) | height = H_t | height ≥ H_t | height = H_t |

Two rows can be read off by hand. For 1 ≤ n ≤ N + 1, μ_l L(n) contains the entry t(n − 1) + 2t(N + 2 − n) = t(2N + 3 − n) ≥ t(N + 2). For 2 ≤ n ≤ N, μ_k L(n) has the entries 2t²n + N + 1 − n and t²n(n − 1) − 2 opposite k, both larger than tn, t(n − 1) and 2t, so k is a point of return.

### 5.4 Proof of Theorem 15.6

**(3).** Suppose a route from Q_t to a relabelling of −Q_t has height below H_t. Reduce it. Its ends have height t², so by Lemma 15.5 it contains no fork higher than t². It starts at K(0) ∈ 𝓜_t. By the table, a mutation of a member of 𝓜_t is a member, has height ≥ H_t, or is a fork higher than t². So the route never leaves 𝓜_t, and it ends at a member of height t². That is K(0), so −Q_t would be isomorphic to Q_t. It is not: the pairs (out-weight, in-weight) of Q_t are (2t, 2t² − 1), (2t² − t, 2), (t² + 1, t²), (t², t² + t), and no vertex of −Q_t has in-weight 2.

**(2).** Go K(0), K(1), …, K(t − 1), then μ_l to L(0), then L(1), …, L(N + 1). All these are below H_t. In L(N + 1) = Λ₂(tN, −t(N + 1); 1, 0; 2t) the vertices j and l are not joined, μ_j and μ_l each give a quiver of height exactly H_t, and μ_l μ_j L(N + 1) = −L(N + 1) with the same labels. Mutation commutes with reversing all arrows, so the mirror image of the first half of the route leads from −L(N + 1) to −Q_t. The route has 2N + 2t + 4 steps.

**(1)** follows from (2) and the pairs listed in (3). ∎

*Terminology.* 𝓜_t is what a reduced route from Q_t to −Q_t can use below H_t. It is not the whole component of Q_t below H_t, which also contains forks and is about twice as large (100, 235, 463 and 806 quivers at t = 3 to 6, `n4_doors_doors12.log`). Note 14 calls a different, intrinsic object the core of a class.

**How the table is certified** (`n4_doors.py prove`, `n4_doors_prove.log`). The entries of the members are polynomials in t and in the position. The script mutates them symbolically; each sign that the mutation rule needs is certified first. A statement p ≥ 0 on a domain such as {t ≥ 3, n ≥ 2, u ≥ 1} is certified by substituting t = 3 + t′, n = 2 + n′, u = 1 + u′ and checking that every coefficient of the expanded polynomial is ≥ 0. Three kinds of claim occur: The cells K(j − 1) and L(n − 1) of the μ_i column, and the μ_j cells of L(−2), L(−1) and L(0), are the same edges as the certified backward and forward steps, read in the other direction; they have no claim of their own.
- an identity of polynomial tuples, up to a stated relabelling ("is K(j + 1)", "equals L(0)");
- "height ≥ H_t": a named entry e with a certified sign and |e| − H_t ≥ 0;
- "fork higher than t²": all six entries certified ≥ 2 in absolute value with strict signs, the quiver not acyclic, a point of return r with every strict inequality of the definition certified, both sides of r acyclic, and one entry certified > t².

For the general member K(j) the variables are j and v = t − 1 − j, on the two domains {j ≥ 1, v ≥ 1} and {j ≥ 2, v ≥ 0}, which together are 1 ≤ j ≤ t − 1, t ≥ 3. For L(n) the variables are t, n and u = N + 1 − n, treated as free, with H_t = t(n + u + 1); no claim about L(n) needs the relation between n, u and t. All 43 claims are certified. They include the heights of the members and Pf(Q_t) = H_t − 5t.

**Independent numerical check** (`n4_doors.py family --tmax 30`, `n4_doors_family.log`). For each t from 3 to 30 the script computes, by search from Q_t, the set of quivers reached through non-forks of height < H_t and forks of height ≤ t². It equals 𝓜_t (2t³ − t² + 5 quivers; 53,105 at t = 30). Every exit is classified as in the table, and a bottleneck search without any use of forks returns H_t as the least height at which Q_t reaches another quiver of height ≤ t², with −Q_t as the quiver reached. `n4_doors.py selftest` checks the mutation and canonical form of this script against `mutation_path.mutate` and `bounded_paths.canonical` on 20,000 random quivers, and reproduces the census extremes 28, 45, 66, 79, 101, 144 and k(k − 1) for G_3 to G_12.

### 5.5 A two-parameter family

Q_{t,b} = (−b, −(2t² − 1 − b), 2t, −2, b − t, −b) has height b for t² ≤ b < 2t², and Q_{t,t²} = Q_t. For every t from 3 to 9 and every b in that range, the bottleneck search gives a join with −Q_{t,b} at exactly (2t² + t − 1)·b − 2t³ + 2t (`n4_doors.py family2`, `n4_doors_family2.log`) [I, measured, not proved]. The ratio to b² is about 2t²/b, so within this family the squares b = t² are the best case.

---

## 6. Doors

**Definition.** For integers p, q, r, s ≥ 1 with pq ≡ rs mod 2, the *door* D(p, q, r, s) is the quiver (p, (rs − pq)/2, −s, q, 0, r): the oriented 4-cycle 0 → 1 → 2 → 3 → 0 with weights p, q, r, s and the diagonal b02 = (rs − pq)/2.

**Lemma [I].** μ₁ μ₃ D = −D with the same labels. The other two corners of this commuting square have b02 = (rs + pq)/2 and −(rs + pq)/2. Its Pfaffian is pr − qs.

*Proof.* μ₁ adds pq to b02 and μ₃ subtracts rs; both reverse their own arrows; b13 = 0. ∎

So a door is a place where a class crosses to its mirror image at a cost of (pq + rs)/2, which can be much less than the products in sight. Whether the two sides are joined lower elsewhere depends on the class.

**The census extremes at births 4 to 7 are doors [I].** On the optimal join paths of note 11:

| Birth | Death | Door | (pq + rs)/2 |
|---|---|---|---|
| 4 | 28 | D(16, 1, 2, 20) | 28 |
| 5 | 45 | D(20, 1, 2, 35) | 45 |
| 6 | 66 | D(24, 1, 2, 54) | 66 |
| 7 | 79 | D(24, 1, 2, 67) | 79 |
| t² | H_t | D(2t, 1, 2, H_t − t) | H_t |

For births 4, 5, 6 the door is D(4b, 1, 2, 2b² − 3b), which gives 2b² − b. That pattern stops at b = 7. The bottom-8 extreme (101) is not a door: it is R_8, and its top is the plateau of 28 quivers of §5.1. The bottom-9 extreme (144) passes two commuting squares that are not doors.

**Scan** (`n4_doors.py doors`, `n4_doors_doors.log`, `n4_doors_doors12.log`). For each door with q, r ≤ 5, p ≤ 40, s ≤ 1,500 and pq ≤ rs, the script computes the component of D among quivers of height below H = (pq + rs)/2. If it does not contain −D, the two sides are joined only at H or above, and H/b² is recorded for the least height b in the component. 702,945 doors separate their sides. For every bottom b from 3 to 30 the door with the largest H has (q, r) = (1, 2). The largest H/b² is 1.8333, at b = 6. A second scan of (q, r) = (1, 2) with p ≤ 120 and s ≤ 2,600 reaches b = 36 and finds the maxima at the squares: 1.7188 at 16, 1.7760 at 25 and 1.8148 at 36, which are Q_4, Q_5, Q_6.

**Beyond the census: every quiver of height 10, 11 or 12 with an entry ±2** (`n4_doors.py scan2`, `n4_doors_scan2_b10.log`, `n4_doors_scan2_b11_12.log`). The bottom quivers of the census extremes at births 4 to 9 all have an entry ±2. For each quiver of height exactly b with such an entry, the script enumerates the component inside height ≤ 2.5·b² and computes its pockets born at b, as note 8 did.

| b | 10 | 11 | 12 |
|---|---|---|---|
| Bound 2.5·b² | 250 | 302 | 360 |
| Largest death of a pocket born at b | 167 | 206 | 249 |
| 2b² − 3b − 3 | 167 | 206 | 249 |
| Quiver | R_10 | R_11 | R_12 |
| Next largest death | 155 | 187 | 236 |

So R_b is the extreme at these three heights, by a clear margin. A pocket that dies above the bound is not seen, and quivers without an entry ±2 are not covered.

---

## 7. The method of arXiv 2610.36179 in mutation-cyclic classes

*I read §§2, 4 and 5 and Appendix A of the paper, and §§13 to 15 of Fomin–Neville (arXiv 2406.03604), in the cached texts. I did not read Neville's arXiv 2409.17832 beyond the statements quoted in those two.*

### 7.1 What the method uses [P]

- A *cyclic ordering* of the vertices is proper at k if every path i → k → j runs clockwise. A *wiggle* swaps two neighbours on the circle that are not joined. A wiggle class is proper if every vertex is proper in some ordering of it, and totally proper if this persists under all proper mutations (Fomin–Neville, Def. 14.1). A quiver has at most one totally proper class (Fomin–Neville Thm 14.3), and a mutation-acyclic quiver has one (Neville).
- The Markov value M_ω = a² + b² + c² + d² + e² + f² + abd + ace + bcf + def + acdf, for the entries (a, …, f) read in the order ω, is unchanged by proper mutations. On a totally proper class it is a class invariant m.
- If the class contains an acyclic quiver, all terms of M are ≥ 0 there. This gives the two inequalities that Appendix A uses throughout: 3 ≤ m, and 2|Pf| < m (Lemma 2.4).
- Theorem 5.1 takes a route to an acyclic quiver that minimises its height, then the number of quivers at that height, then its length, and shows that a stretch at the top height F > max(ht, m) can be replaced. The replacement is local. It looks at the first two mutation vertices i, j of the stretch: no arrow (Lemma 4.2), one arrow (Lemma 4.4 and Proposition 4.7), two or more (Lemma 4.5). Every case is closed by showing that the configuration would force m > T, m < 3 or 2|Pf| ≥ m.

### 7.2 The invariant exists in the classes that matter [I]

`n4_doors.py coq` and `markov-census` implement proper orderings, wiggles, proper mutation and M. The code reproduces m = 5 for the acyclic quiver of Remark 4.8 and M = 41 for Example 5.4 of arXiv 2610.36179, and M was constant along all proper mutations tried.

| Quiver | Height | Pf | Proper wiggle classes | M | Survives proper mutations to depth 7 |
|---|---|---|---|---|---|
| G_k, k = 3 … 8 | k | k | 1 | −k⁴ + k³ + 4k² − 2k + 1 | yes |
| census extreme, birth 4 (death 28) | 4 | 12 | 1 | −123 | yes |
| birth 5 (45) | 5 | 5 | 1 | −395 | yes |
| birth 6 (66) | 6 | 6 | 1 | −859 | yes |
| birth 7 (79) | 7 | 19 | 1 | −1,171 | yes |
| birth 8 (101), which is R_8 | 8 | −98 | 1 | −695 | yes |
| birth 9 (144) | 9 | −9 | 1 | −4,874 | yes |
| Q_t, t = 3 … 6 | t² | H_t − 5t | 1 | −4t⁵ + 2t⁴ + 2t³ + t² + 5 | yes |
| R_b, b = 5 … 12 | b | 2(b − 1)² | 1 | −2b³ + 5b² + 9 | yes |

The formula for G_k was checked for k = 3 to 59. The ones for Q_t and R_b are computed symbolically, in the ordering ⟨0, 3, 2, 1⟩; the proper orderings depend only on the signs of the entries.

On the whole census (`n4_doors_markov.log`): 27,554 of the 788,026 classes have a pocket born at ≤ 9. For 27,507 of them the bottom quiver has exactly one proper wiggle class that survives proper mutations to depth 4; for 47 no class survives, and their largest death/birth² is 0.17. Where one class survives, M < 0 in 25,100 classes, M > 0 in 2,347 and M = 0 in 60. "Survives to depth 4" is a necessary condition for total properness, not a proof of it.

So the classes with large barriers carry the Fomin–Neville invariant, as far as a finite test can tell. What they lack is positivity.

### 7.3 Where each lemma fails [I]

| Step of the paper | Uses | Counterexample in a mutation-cyclic class |
|---|---|---|
| Lemma 4.2, second assertion: of the two middle corners of a commuting square between low quivers, one is low | 4m ≤ 9 or 2\|Pf\| ≥ m in the bad cases | Every door: the corners have heights h, (pq + rs)/2, (pq + rs)/2, h. For the door of the bottom-6 extreme they are 54, 66, 66, 54 with M = −859; for C_5, in the class of G_5, they are 5, 25, 20, 5 |
| Lemma 4.5: after a first step to height F across a double arrow, no return to a low quiver within F | m > F, 2\|Pf\| ≥ m | R_b for every even b ≥ 6 (§5.1): from B, of height b² − b, the first step reaches 2b² − 3b − 3; b(b − 1)/2 − 1 further steps alternating at the two ends of a weight-2 arrow stay there, and the next one returns to height b² − b. For R_8, the bottom-8 extreme, the heights are 56, then 28 times 101, then 56 |
| Lemma 4.4 and Proposition 4.7: a stretch across a single arrow has a low replacement | m − 2\|Pf\| ≤ −5 and similar | V_b below: the stretch μ₃, μ₀, μ₂ has heights b + 1, b + 1, b, crosses a single arrow, and has no replacement at all |

The square of Appendix A.1 shows the mechanism in the smallest case. For P = (0, b, −c, d, −e, f) with vertices 0 and 1 not joined, the four corners have b23 = f, f − bc, f − de and f − bc − de, and M = b² + c² + d² + e² + f² − f·(bc + de). The paper excludes f − bc − de < −T by showing m would be too small. With (b, c, d, e, f) = (T, 1, T, 2, T + 1) one gets M = 6 − T, Pf = T and corners T + 1, 1, 1 − T, 1 − 2T. The two neighbours of P have height T, and each reaches another quiver of height ≤ T only at T + 1; checked for T = 10, 20, 40 and 100 (`n4_doors_ahjl.log`).

### 7.4 No bound of the same shape

**Proposition 15.8 [I].** For b ≥ 3 let V_b = (−b, 2, −1, −b, 1, 1). Then:
1. V_b has exactly one proper wiggle class, with Markov value 5, and Pf(V_b) = −2;
2. μ₀ V_b and μ₂ V_b are relabellings of V_b, μ₃ V_b has height b + 1 and μ₁ V_b has height b² − 2;
3. μ₂ μ₀ μ₃ V_b is a relabelling of −V_b, through heights b + 1, b + 1, b, and V_b is not isomorphic to −V_b.

So V_b and −V_b are joined at b + 1 and not lower, and f(V_b, b) ≥ b + 1.

*Proof.* The arrows of V_b are 1 → 0 (b), 0 → 2 (2), 3 → 0 (1), 2 → 1 (b), 1 → 3 (1), 2 → 3 (1). Then μ₀ V_b = μ₂ V_b = (b, −2, 1, b, 1, −1), which is V_b with 0 and 2 exchanged; μ₃ V_b = (−(b + 1), 1, 1, −b, −1, −1); μ₁ V_b = (b, 2 − b², −1, b, −1, b + 1). The pairs (out-weight, in-weight) of V_b are (2, b + 1), (b + 1, b), (b + 1, 2), (1, 2); −V_b has a vertex with (2, 1) and V_b has none. The proper orderings depend only on the signs of the entries, the proper class is that of ⟨0, 2, 1, 3⟩, and its Markov value is the constant polynomial 5. ∎

The script checks all of this for 3 ≤ b ≤ 200, and that the proper class survives proper mutations to depth 6 for b ≤ 40.

**Consequences [I].**
- In mutation-acyclic classes, Theorem 5.1 of the paper gives f(Q, w) ≤ max(w, m(Q)) (note 12 §6): pockets are born only below m. Proposition 15.8 shows that nothing like this holds in mutation-cyclic classes with a proper wiggle class, whatever function of M and Pf replaces m: the values (M, Pf) = (5, −2) occur with a pocket at every level b ≥ 3. The quantity H(Q) of the paper's Corollary 5.2 is max(b, 5) for V_b.
- The violation is by 1, and there are large ones. On the census the latest death of a class exceeds |M| in 1,976 classes. The worst is the class of (2, −7, −9, 8, −8, 2), with M = 8, Pf = −124 and a pocket dying at 113. Against max(|M|, 2|Pf|) there are 15 violations, by at most 5; against |M| + 2|Pf| there are 5, each by exactly 1.
- **So the Pfaffian, which the acyclic case controls through 2|Pf| < m, is an independent quantity here, and it is the one that tracks the barriers:** 113 against |Pf| = 124 above, 2b² − 3b − 3 against |Pf| = 2(b − 1)² for R_b, H_t against |Pf| = H_t − 5t for Q_t, and Corollary 15.2 for every weight-2 corridor. But |Pf| does not bound the barrier either: G_k has Pf = k and barrier k² − k.

**Conclusion.** The reduction of arXiv 2610.36179 fails for mutation-cyclic classes at a definite point: its local lemmas are false there, because the inequalities 3 ≤ m and 2|Pf| < m are properties of an acyclic representative, not of the invariant. A replacement would have to bound the height of a stretch relative to the heights next to it, not against a class constant, and it would have to accept the door squares and the weight-2 plateaus as irreducible. I did not find such a statement.

*Related parts, written the same day.* [Note 13](13-conjecture-5-5-up-to-height-18.md) tests Conjecture 5.5 of the same paper on the mutation-acyclic side. [Note 14](14-opposite-quivers-forks-and-cores.md) asks when a quiver is mutation-equivalent to its opposite. It builds a complete invariant, the core, for the classes where forks and pre-forks leave a finite remainder, and it certifies total properness for 334,168 census classes and excludes it for at least 132,611; I did not match those lists against the pocket classes above. The classes it leaves open are those with infinite "tubes" of quivers that are never forks (its §8). The tubes with a weight-2 arrow are the lines of §3 here, and Theorem 15.1 gives their heights. Q_t, V_b and the doors are mirror pairs in its sense.

---

## 8. What an upper bound still needs

**Observation 15.9 (thin summits) [I, measured].** For each of the 30,527 census pockets born at ≤ 9, let e be the least height at which it reaches another quiver at or below its birth level. In every case there is a route of height e on which each quiver of height exactly e has an entry of absolute value ≤ 2 (`n4_doors.py thin`, `n4_doors_thin.log`). For 362 of the pockets e is below the death stored in the census, because the elder rule lets a pocket survive its first join. With "≤ 1" this holds for 28,129 pockets and with "= 0" for 13,634. If every quiver above the birth level is required to have such an entry, a route of height e still exists for 30,523 pockets; the four exceptions include the bottom-9 extreme, whose route passes a quiver with least entry 3 in the valley between its two peaks.

So on the census the top of every barrier lies in an orbit of two mutations of weight 0, 1 or 2, where Theorem 15.1 describes everything: a commuting square (the doors), a pentagon, or a weight-2 line with its plateau. I could not prove the observation. A proof would have to show that a quiver with all entries ≥ 3 that is not a fork is never needed at the top.

**Where the height comes from [I, H].**
- On a weight-2 line, by Corollary 15.2, the columns between the bottoms are bounded by |Pf| + 2|ζ| + max slope. So a corridor is long only when ζ or |Pf| is large, and |Pf| ≤ 3w².
- At a square between two non-adjacent vertices, the two middle corners differ from the ends by products of two entries.
- The open point is the size of ζ and of the entries at a door when the route reaches them from a quiver that is not low. In R_b the plateau value ζ = 2w² − 3w − 3 is the barrier itself, on a line entered at height w² − w. In Q_t the long line is entered at height N + 1 ≈ 2w^{3/2} with ζ = 2√w, and the barrier is the door at its end.

**Status of Conjecture 10.1 [H].** Open. What changed:
- the lower bound is now 2w² − 7w + 2, so the constant 2 cannot be improved;
- 2b² − b, the value at births 4, 5, 6, is not contradicted: R_b gives 2b² − 3b − 3 and Q_t gives 2b² − b^{3/2} − b + 2√b at b = t²;
- the route to a proof suggested in note 11 §6 ("one step, then one corridor of run ≤ b − 1 and increment ≤ 2b") describes neither family: R_b needs a square and then a plateau, Q_t two corridors and two squares;
- the barriers of R_b, of Q_t and of every weight-2 corridor follow |Pf|, and a quiver of height w has |Pf| ≤ 2w² unless it is a vortex: the three products in Pf have the same sign only for the 16 sign patterns of a vortex (`n4_doors_coq.log`). A vortex can have |Pf| up to 3w². So a class with a barrier above 2w² would most likely contain a low vortex. On the census no class whose bottom quiver is a vortex has a pocket born at ≤ 9 (`n4_doors_markov.log`).

**Problems.**
- **Problem 15.10.** Prove Observation 15.9.
- **Problem 15.11.** Does a class that contains a vortex of height w ever need a join above 2w²? Such a class has no proper cyclic ordering at that quiver, and |Pf| can reach 3w².
- **Problem 15.12.** Prove Theorem 15.13 for odd b, and the formula of §5.5 for Q_{t,b}, by the method of §5.4.
- **Problem 15.15.** Is F(4, w) = 2w² − 3w − 3 for all large w? It is the largest death among quivers with an entry ±2 at each of the heights 10, 11 and 12 (§6).

---

## 9. Limitations

- **No upper bound for all classes.** The aim is not reached. Proposition 15.3 covers joins inside one orbit of two mutations only.
- **Theorems 15.13 and 15.6 are computer-assisted.** The 30 and 43 polynomial claims are checked by a program of about 350 lines (class `P`, `nonneg`, `smutate`, `cert_fork`, `cert_height`, `cmd_prove`, `cmd_prove2`). Two rows of the table of Q_t are done by hand in §5.3. The searches for b ≤ 60 and t ≤ 30 are independent of the certificates but share the mutation code.
- **Theorem 15.13 is proved for even b only.** For odd b the value 2b² − 3b − 3 is measured, for 5 ≤ b ≤ 59.
- **Checked once, separately, not by a specialist.** That check, made before §5.1 existed, wrote its own mutation and canonical form; confirmed Theorem 15.6 by plain search without forks for t ≤ 18; rebuilt the exit table of Q_t for t ≤ 12; tested Lemmas 15.4 and 15.5 on 40,000 random forks and 381,895 reduced routes; re-ran §3 on random lines; and compared each helper of the certificate code with its own on at least 160,000 cases. It found no theorem false. It corrected three side claims, fixed above: the sharpness of Proposition 15.3 (squares attain w² − ⌈w/2⌉), the statement of the first corridor, and an earlier sentence that the worst joins all cross at doors. It also found the family R_b on its own, while the scan of §6 was finding it here. **Theorem 15.13, its certificates (`prove2`) and §5.1 were written after that check and were not covered by it.** The check's own search had given the join of R_b at exactly 2b² − 3b − 3 for 4 ≤ b ≤ 60 and b = 64, 81, 100, and regions of about b/2 + 3 quivers.
  > **Update (note 19):** Theorem 15.13 has now had a second reading ([note 19](19-checks-of-notes-13-to-16.md)). Every cell of its exit table is a claim of `prove2` or the reverse of a certified step, and a rerun of `prove2` is identical to the log. A labelled search that uses no forks gives the join of R_b and −R_b at exactly 2b² − 3b − 3, and nothing lower, for every b from 5 to 48, odd b included. Theorem 15.6 was checked the same way for t = 3 to 16, and Theorem 15.1, Corollary 15.2, Proposition 15.3 and Proposition 15.8 by independent code. No error was found.
- **Lemma 15.4 is quoted from Warkentin's thesis through note 3's reading of it** and through Ervin's restatement as read in note 14; neither source was opened here. The proof in §4 is my own and was tested on random forks.
  > **Update (note 19):** Both sources have now been opened; see the note in §4.
- **Total properness is tested to finite depth** (4 on the census, 7 on the named quivers). Proposition 15.8 and the failures in §7.3 do not depend on it.
- **The door scan covers mirror doors with q, r ≤ 5 only**, and squares that are not doors are not scanned. "Nothing above 2w²" is a statement about the census (w ≤ 9), this scan (bottoms ≤ 36), the quivers of height 10 to 12 with an entry ±2, inside 2.5·b², and the families found.
- **Corollary 15.14 for n ≥ 5** holds for disconnected quivers only. [Note 16](16-five-vertices-above-w-squared.md), written after this one, treats connected quivers on 5 vertices.
- **Prior art.** I did not search again. Note 12 §6 found nothing that states Theorem 9.1 or Conjecture 10.1, and its caveat stands: Warkentin's 2014 thesis and Neville's 2025 thesis were not read. The orbits of §3 overlap with Soukup's Theorem 1.3 and Fomin–Neville's Proposition 3.13 (note 3 §5.2 item 3); the height statements and the family are not in what I read.

---

## 10. Reproduce

```bash
PY=python
$PY -I n4_doors.py selftest > n4_doors_selftest.log
$PY -I n4_doors.py prove2 > n4_doors_prove2.log                                 # Theorem 15.13: 30 claims
$PY -I n4_doors.py family3 --bmax 60 --show 8 > n4_doors_family3.log
$PY -I n4_doors.py prove > n4_doors_prove.log                                   # Theorem 15.6: 43 claims, a few seconds
$PY -I n4_doors.py family --tmax 30 --show 3 7 > n4_doors_family.log            # about 80 seconds
$PY -I n4_doors.py family2 --tmax 9 > n4_doors_family2.log
$PY -I n4_doors.py orbit --samples 20000 --c 2 3 4 --wmax 7 > n4_doors_orbit.log   # about 3 minutes
$PY -I n4_doors.py orbit01 --wmax 8 > n4_doors_orbit01.log                      # about 4 minutes
$PY -I n4_doors.py forks > n4_doors_forks.log
$PY -I n4_doors.py doors --qmax 5 --rmax 5 --pmax 40 --smax 1500 --bmax 30 --workers 8 > n4_doors_doors.log
$PY -I n4_doors.py doors --qmax 1 --rmax 2 --pmax 120 --smax 2600 --bmax 36 --workers 8 > n4_doors_doors12.log
$PY -I n4_doors.py scan2 --b 10 --workers 8 > n4_doors_scan2_b10.log               # 11 minutes
$PY -I n4_doors.py scan2 --b 11 12 --workers 8 > n4_doors_scan2_b11_12.log        # about 44 minutes in all
$PY -I n4_doors.py coq --depth 7 --depth-joins 5 > n4_doors_coq.log
$PY -I n4_doors.py ahjl > n4_doors_ahjl.log
$PY -I n4_doors.py markov-census --depth 4 --workers 6 > n4_doors_markov.log
$PY -I n4_doors.py thin --workers 6 > n4_doors_thin.log
```

The script writes only to standard output. `forks` and `coq` read note 11's `n4_joins.jsonl`; `markov-census` and `thin` read the class files of notes 8 and 10, two of them gzip-compressed. `selftest` needs numpy, for the comparison with the older scripts; nothing else does.

---

## Sources

- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*, §§2, 4, 5 and Appendix A: https://arxiv.org/abs/2610.36179
- Fomin, Neville, *Cyclically ordered quivers*, §§13–15 (vortices, totally proper orderings, Fomin–Neville Def. 15.5 of forks): https://arxiv.org/abs/2406.03604
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014, Def. 2.1 and Lemma 2.5, as read in note 3: https://d-nb.info/1214302807/34
- Berenstein, Fomin, Zelevinsky, *Cluster algebras III*, proof of Lemma 3.2 (the sign of the Pfaffian), as read in note 11: https://arxiv.org/abs/math/0305434
- Ervin, *New hereditary and mutation-invariant properties arising from forks*, Lemmas 2.7 and 2.8, as read in note 14: https://arxiv.org/abs/2306.07502
- Notes 3, 7, 9, 10, 11, 12, 13 and 14 of this repository.
