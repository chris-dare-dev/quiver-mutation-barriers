# 9. On 4 vertices f(Q, w)/w is unbounded

*Run on 2026-11-09. This follows [note 8](08-n4-ratio.md), whose worst cases for n = 4 were mirror pairs: a quiver and its opposite, both at the bottom of a class, joined only high above it. Note 8 fitted their barrier linearly (about 16.75 × bottom) and suggested c(4) ≈ 17. Here I extract an explicit family from those cases and prove that the barrier is quadratic, so no linear bound exists. Code: [experiments/n4_mirror.py](../experiments/n4_mirror.py) and [experiments/n4_mirror_proof.py](../experiments/n4_mirror_proof.py) (new). Results: `n4_mirror_scan.jsonl`, `n4_mirror_family.jsonl` and `n4_mirror_proof.log`. Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Follow-up (note 10):** The census now covers every class with bottom ≤ 9 (788,026 classes). Every pocket born at b ≤ 9 dies by 1.834·b²; the extremes are sporadic and the infinite families stay near b². Conjecture 10.1, F(4, w) ≤ 2w², fits all of it. See [note 10](10-n4-quadratic-bound.md).

> **Correction (note 12):** Theorem 9.1 holds, and it has a short proof that needs no computer ([note 12](12-checks-of-notes-03-to-10.md) §4). Each mutation of G_k creates an entry of k² or k² − k. The sequence μ₀μ₃μ₂μ₁ takes G_k to −G_k relabelled by 0 ↔ 1, 2 ↔ 3, through the oriented 4-cycle C_k with weights k, k − 1, k, k, at height k² − k. The symbolic proof was rerun independently with PARI: same 11 quivers, all signs valid for k ≥ 4. Four statements are corrected. (1) The three quivers of maximal entry k, and the 11 quivers below k² + 4k, are proved for the component of G_k inside that bound, not for its class (see the note after the theorem). (2) In rank 3 a class has a single bottom *island*, not a single bottom quiver (§1 item 3). (3) In §4, Problem 5.2 is not open for n ≥ 5. G_k with a path of extra vertices gives connected quivers on every n ≥ 4 with f(Q, k) ≥ k(k − 1), so F(n, w) ≥ w(w − 1) and c(n) = ∞ for every n ≥ 4 (Proposition 12.1). (4) The small-k lines of `n4_mirror_proof.log` come from a separate driver, not from `n4_mirror_proof.py`; `review12.py extremes` reproduces them. No earlier statement of the theorem was found in the literature (note 12 §6).

> **Update (note 14):** The whole class of G_k is now described, for every k ≥ 3 and with no bound on the entries. Its core has seven quivers: G_k, −G_k and C_k at level k, two at level k² − k and two at level k². Every other quiver of the class has level at least k² − k. So k is the bottom of the class, the class has exactly three quivers below level k² − k, and f(G_k, w) = k(k − 1) for k ≤ w < k(k − 1) (Theorem 14.2). See [note 14](14-opposite-quivers-forks-and-cores.md).

> **Update (note 15):** The lower bound is now F(4, w) ≥ 2w² − 7w + 2 for every w ≥ 6. For even b ≥ 6 the quivers R_b = (−b, −b, b − 1, −2, b − 2, −b) and −R_b, of height b, are joined at exactly 2b² − 3b − 3 ([note 15](15-rank-2-orbits-and-the-constant-2.md), Theorem 15.13). G_k gives w² − w. So "at least quadratic" stands, and the constant of any quadratic bound is at least 2.

---

## 1. Answer

**Theorem 9.1 [I, computer-assisted proof].** For k ≥ 3, let G_k be the 4-vertex quiver with rows

(0, k, −k, −k), (−k, 0, 0, k), (k, 0, 0, −(k−1)), (k, −k, k−1, 0).

Its mutation class contains three quivers of maximal entry k, among them G_k and its opposite −G_k (checked symbolically for k > 6 and numerically for k = 3 to 200). Any mutation path joining two of them passes through a quiver of maximal entry at least k(k−1), and they are joined at exactly that level. Hence

> f(G_k, k) ≥ k(k − 1),

and on 4 vertices sup_Q f(Q, w)/w = ∞. In the notation used from here on, F(4, w) ≥ w(w − 1) for every w ≥ 3.

> **Correction (note 12):** "Its mutation class contains three quivers of maximal entry k" is shown only for the part of the class reachable inside the bound k² + 4k; an independent rerun found the same inside k³. It is not shown for the whole class. The third of these quivers is the oriented 4-cycle C_k with weights k, k − 1, k, k, which is its own opposite. The bound f(G_k, k) ≥ k(k − 1) does not depend on this, and it has a proof by hand ([note 12](12-checks-of-notes-03-to-10.md) §4). "Numerically for k = 3 to 200" means the values of k listed in §3.

**Consequences.**

1. **Problem 5.2 fails for n = 4 (c(4) = ∞).** Note 8's linear fit through bottoms 3 to 7 was right in that range, but this family overtakes it once the bottom passes about 15. No constant c makes "descend greedily, then search inside c · weight" a decision procedure on 4 vertices.
2. **Conjecture A (note 3 §6: a bound F(n, w) that is polynomial in w) survives only in polynomial form.** Any effective bound F(n, w) is at least quadratic in w for n = 4. Whether a polynomial F exists, and so whether bounded search decides mutation equivalence, is still open.
3. **The obstruction is the mirror.** The three bottom quivers lie in the class together with their opposites. Getting from G_k to −G_k requires a quiver whose largest entry is the product k · (k − 1) of two entries of G_k. This mechanism does not exist in rank 3, where a class has a single bottom quiver up to relabelling (Theorem 3.1). It needs at least 4 vertices.
4. **The family is thin.** Below maximal entry k² + 4k, the class of G_k has only 11 quivers, at levels k, k² − k and k². Note 8 found that the worst barriers sit in the thinnest classes; this is the extreme case.

---

## 2. How the family was found

Note 8's worst classes at bottoms 4 to 7 all have the same shape. Vertex 0 has arrows 0 → 1, 2 → 0 and 3 → 0 of weight b, attached to a small triangle T = (b₁₂, b₁₃, b₂₃) on vertices 1, 2, 3. Call this G(b, T). For the two triangles found there, the join level is exactly linear in b (`n4_mirror.py`, b = 4 … 20):

| T | Join level | For b |
|---|---|---|
| (4, −2, 3) | 7b | 4, 5, 6, 7, 8, 10, 12, 16, 20 |
| (−2, 5, −6) | 11b | 6, 7, 8, 10, 12, 16, 20 |

So the ratio depends on T alone. A scan of all 15,624 triangles with entries in [−12, 12], at b = max|T|, found 100 classes in which G(b, T) and −G(b, T) are both at the bottom (`n4_mirror_scan.jsonl`). The best ratio for each size of T:

| max\|T\| | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| best join/b | 2 | 2 | 7 | 4 | 11 | 6 | 7 | 8 | 9 | 10 | 11 |
| T | (−1, 2, −1) | (−2, 3, −1) | (−2, 4, −3) | (0, 5, −4) | (−2, 5, −6) | (0, 7, −6) | (0, 8, −7) | (0, 9, −8) | (0, 10, −9) | (0, 11, −10) | (0, 12, −11) |

From size 7 on, the best triangle is (0, k, −(k − 1)), with ratio k − 1. With b = k this is G_k.

---

## 3. The proof

**Numerical part** (`n4_mirror.py`, exact integer arithmetic). For k = 3 to 12, 16, 20, 25, 30, 35, 40, 50, 75, 100, 150 and 200, the class of G_k was enumerated up to relabelling inside bound (k + 4)k. Each time the enumeration was exhausted, and its lowest level is k. For k ≥ 4 it holds exactly 11 quivers, for k = 3 it holds 29. It has 3 components at level k, which first join at level k(k − 1) (`n4_mirror_family.jsonl`, `n4_mirror_proof.log`). −G_k is among them.

**Symbolic part** (`n4_mirror_proof.py`). The same search is run with entries that are polynomials in k:

1. Start from G_k. Mutate with the Fomin–Zelevinsky rule, deciding each sign of b_ik·b_kj and of b_ik by the sign of a polynomial for large k. Keep every mutation whose maximal entry is ≤ k² + 4k (again a comparison of polynomials). Identify quivers up to relabelling by exact equality of polynomial matrices under the 24 relabellings.
2. The search closes on a set S of 11 quivers. Their levels are k, k² − k and k², and 20 mutations leave the bound.
3. Filter S by level. At level k the three bottom quivers lie in three components; at level k² − k they lie in one.
4. Every polynomial whose sign was used, and every difference that keeps two members of S distinct under every relabelling, is recorded with Cauchy's root bound 1 + max|aᵢ/aₙ|. Beyond that bound its sign is that of its leading coefficient. The largest such bound over the 2,887 polynomials is 6.

So for every k > 6, the quivers reachable from G_k through quivers of maximal entry ≤ k² + 4k are exactly the 11 members of S, with the stated levels and components. Now take any path between two of the three bottom quivers. Either it stays inside S, and then its highest quiver has maximal entry at least k² − k. Or it leaves the bound, and then it passes a quiver of maximal entry above k² + 4k. In both cases f(G_k, k) ≥ k(k − 1). The cases 3 ≤ k ≤ 6 are covered by the numerical part. ∎

The argument does not need the three quivers to be the bottom of the whole class. A quiver of the class below level k reachable only through higher quivers would not change the lower bound.

---

## 4. What this changes

| Earlier statement | Status |
|---|---|
| Conjecture A (note 3 §6): F(n, w) polynomial | Still open. Now known to be at least quadratic at n = 4 |
| Note 5 Problem 5.2: escape ratio ≤ c(n) | False for n = 4 (c(4) = ∞). Open for n ≥ 5, where n = 4 embeds as a lower bound only if a vertex can be added without changing the class's low part (not checked) |
| Note 5 Conjecture 5.1 (n = 4) | Already refuted in note 7 |
| Note 8: c(4) ≈ 17 from a linear fit | Refuted. The fit holds for bottoms ≤ 7, and G_k overtakes it near bottom 15 |
| Corollary G (note 3 §6: decidability from an effective F) | Unchanged. Any effective F, polynomial or not, still gives a decision procedure |

**A sharper question [H].** Is F(4, w) = O(w²)? The barrier of G_k, k(k − 1), is the product of two of its entries. The exhaustive data of note 8 stays below 2·bottom²: the worst deaths are 12, 28, 45, 66 and 79 at bottoms 3 to 7, ratios to bottom² of 1.33, 1.75, 1.80, 1.83 and 1.61. If F(4, w) ≤ 2w², then bounded search at that bound decides mutation equivalence on 4 vertices. Nothing here proves it.

---

## 5. Limitations

- The theorem gives a lower bound on f for one family. It says nothing about upper bounds.
- The symbolic proof relies on the program `n4_mirror_proof.py`, whose polynomial arithmetic and Cauchy bounds are elementary. It agrees with the exact numerical runs for every k checked, from 3 to 200.
- The scan of triangles used b = max|T| and one attachment pattern for vertex 0. Other patterns may give larger barriers.

---

## 6. Reproduce

```bash
PY=python
$PY -I n4_mirror.py --T 4 -2 3 --T -2 5 -6 --b 4 5 6 7 8 10 12 16 20 --K 24 --out mirror_two_triangles.jsonl
$PY -I n4_mirror_proof.py      # symbolic part; prints the closed set, the levels and the Cauchy bound 6
```

The triangle scan and the family runs (`n4_mirror_scan.jsonl`, `n4_mirror_family.jsonl`) were made with short driver loops over `n4_mirror.measure`. The scan used every T with entries in [−12, 12], b = max|T|, bound 24b. The family used b = k, T = (0, k, −(k − 1)), bound (k + 4)k.

---

## Sources

- Fomin, Zelevinsky, *Cluster algebras I* (matrix mutation): https://arxiv.org/abs/math/0104151
- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.14: https://arxiv.org/abs/1608.05735
- Notes 2, 3, 5, 7 and 8 of this repository.
