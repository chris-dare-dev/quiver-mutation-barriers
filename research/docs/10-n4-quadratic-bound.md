# 10. Is F(4, w) ≤ 2w²?

*Run on 2026-11-09. [Note 9](09-n4-mirror-family.md) proved F(4, w) ≥ w(w − 1) and asked whether F(4, w) = O(w²), with the bound 2w² suggested by note 8's data. Here the per-class census of note 8 is extended to every class with bottom 8 or 9, and three families of quivers are scanned for barriers above 2b². Code: `n4_classes.py` (new option `--max-level`), [experiments/n4_block_scan.py](../experiments/n4_block_scan.py) (new). Results: `n4_classes_k8_B192.jsonl.gz`, `n4_classes_k9_B192.jsonl.gz` (gzip-compressed), `n4_block_scan.jsonl`, `n4_triangle_patterns.log`, and the matching `.log` files. Quivers are up to relabelling. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Follow-up (note 11):** BFZ's congruence μ_k(B) = E B Eᵀ makes the gcd of the entries and |Pf| mutation invariants, but on this census they take 311 values and certify only 26 of the 788,026 classes as separate (144 with two acyclicity tests). Re-enumerating every uncertified class with bottom 6–9 (765,131) up to 8b² found no hidden join, so a pocket that this census misses would die above 8·b². Problem 6.1 is false at n = 4 (Theorem 11.1: D(G_k) = k(k − 1)). On the census, D(x) ≤ 1.67·max(x)², and the quivers of minimal total weight of each class are joined within 1.83·w², so a quadratic form of Problem 6.1 (Problem 11.2) fits the data. The worst joins climb by one step to at most b², then along a weight-2 corridor, not by one step to a product of two entries as G_k does. See [note 11](11-n4-invariants-descent-joins.md).

> **Correction (note 12):** The census numbers, the table and both extremes were confirmed with independent code, the extremes at bound 400 ([note 12](12-checks-of-notes-03-to-10.md)). "A few found a lower bottom" (§2) means 2,213 rows at level 8 and 4,906 at level 9. Every one of them repeats a class already counted, with the same pairs, so 788,026 stands. The bottom-9 extreme H(9, 8, 4, 2) is also a mirror pair: its two bottom quivers are H and −H. "Their join is r_T·b" (§1 item 2) is a measurement on two triangles (note 9), not a proof. On prior art, Conjecture 10.1 is open. For mutation-acyclic classes, arXiv 2610.36179 implies f(Q, w) ≤ w⁴ + 4w³ + 6w² and conjectures f(Q, w) ≤ w. So the content of Conjecture 10.1 lies in the mutation-cyclic classes, which contain every census extreme. A mirror test of the visibility caveat found no hidden join (note 12 §7).

> **Follow-up (note 15):** The constant 2 of Conjecture 10.1 cannot be lowered. The bottom-8 extreme of this census (death 101) is the member b = 8 of a family R_b = (−b, −b, b − 1, −2, b − 2, −b) whose mirror join is at exactly 2b² − 3b − 3, proved for every even b ≥ 6 and measured for odd b up to 59 ([note 15](15-rank-2-orbits-and-the-constant-2.md), Theorem 15.13). So F(4, w) ≥ 2w² − 7w + 2. A second family, Q_t, has height b = t² and a mirror join at 2b² − b^{3/2} − b + 2√b; Q_3 and R_9 are the two pockets (9, 132) here, the runners-up at birth 9. The three families scanned in §1 stay near b²; these two tend to 2b². Nothing above 2b² − b was found: among all quivers of height 10, 11 or 12 with an entry ±2 the largest deaths are 167, 206 and 249, at R_10, R_11 and R_12.

---

## 1. Answer

1. **Every pocket born at weight ≤ 9 dies by 1.834·b² [I].** The census now covers every 4-vertex class with bottom ≤ 9: 172,746 classes from note 8 plus 213,511 with bottom 8 and 401,769 with bottom 9 (788,026 in all), each enumerated up to bound 192 or more. Over all their pockets born at b ≤ 9, the largest death/birth² is 1.833, from note 8's bottom-6 mirror pair that joins at 66. No pocket comes near 2.

   | Birth b (= class bottom) | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
   |---|---|---|---|---|---|---|---|
   | Largest death of a bottom component | 12 | 28 | 45 | 66 | 79 | 101 | 144 |
   | death / b² | 1.33 | 1.75 | 1.80 | 1.83 | 1.61 | 1.58 | 1.78 |

   Pockets born above their class bottom stay lower: at most 1.31·b² over all four runs (birth 9, death 106, in a class with bottom 8).
2. **The extremes are sporadic [I].** The values near 1.8 come from isolated quivers that do not extend to infinite families:
   - **Attachment families.** In note 9's families, a vertex is joined by arrows of weight b to a triangle T. Their join is r_T · b, so death/b² = r_T/b, which is largest at b = max|T| and falls as b grows. Over every T with entries ≤ 9 and two orientation patterns of the attached vertex, the largest value is 1.833 (T = (−2, 5, −6), b = 6). The pattern in which all three arrows leave the attached vertex produced no mirror bottoms at all.
   - **The mirror family G_k** of note 9 has death/b² = (k − 1)/k, below 1.
   - **The heavy-block shape** H(a, c, p, q) has rows (0, −p, −a, c), (p, 0, c, −a), (a, −c, 0, −q), (−c, a, q, 0). It produced the bottom-9 extreme (a = 9, c = 8, p = 4, q = 2, join 144 = 2ac). A scan of all a ≤ 14, 0 ≤ c, p, q ≤ a finds that this value is isolated: every other class of this shape stays at or below 1.125.
3. **Verdict [H].** The data supports F(4, w) ≤ 2w², and in fact ≤ 1.84·w², up to w = 9. The worst cases are a handful of thin classes, and the infinite families stay near w². This is evidence for Conjecture 10.1, not a proof.

**Conjecture 10.1.** For every 4-vertex quiver Q and every w, f(Q, w) ≤ 2w². Any effective bound on F(n, w) gives a decision procedure by bounded search (Corollary G of note 3 §6), so this would make bounded search with bound 2w² a decision procedure for mutation equivalence on 4 vertices (FWZ Problem 2.6.14 for n = 4). It is open beyond weights ≤ 2.

> **Follow-up (note 16):** The conjecture is about 4 vertices only. On 5 vertices no bound c·w² holds: F(5, w) ≥ 2w^{5/2} − 11w² (51 at w = 4, and 2,130,710,527 = 127·w² at w = 4,096). See [note 16](16-five-vertices-above-w-squared.md).

---

## 2. Method

**Census.** `n4_all.py run --N 14 --keep-survivors 9` lists one quiver for each component born at levels ≤ 9 that is still separate at level 14. `n4_classes.py --min-level 8 --max-level 8` and `--min-level 9 --max-level 9` then enumerate each such class up to bound 192, compute its persistence pairs and keep each class once:

- 219,044 components → 215,724 classes for level 8;
- 411,585 → 406,675 for level 9.

All were exhausted. A few found a lower bottom: survivors that are pockets of classes with bottoms 4 to 7 dying above 14. For pockets born at b ≤ 9, 2b² ≤ 162 < 192, so any death up to 2b² is visible.

> **Correction (note 12):** "A few" is 2,213 rows at level 8 and 4,906 at level 9 (and 461 in the bottom-6/7 file of note 8). Each one repeats a class already listed in an earlier file, with the same pairs up to the bound, so it is counted once. See [note 12](12-checks-of-notes-03-to-10.md).

**Families.**

| Family | What was scanned | Bound used |
|---|---|---|
| Attachment patterns | Vertex 0 with arrows of weight b to vertices 1, 2, 3, as (out, in, in) or (out, out, out), on every triangle with entries in [−9, 9], at b = max\|T\| and max\|T\| + 1 | 3b² |
| Heavy blocks H(a, c, p, q) | a = 3 to 14, 0 ≤ c, p, q ≤ a | 3a² |

In each case the class is enumerated inside the bound, and the join level of its bottom components is recorded when the quiver lies at its class bottom.

---

## 3. Limitations

- **Visibility.** The census is exact for joins below its bound (192 for bottoms 8 and 9, 256 or 512 for lower bottoms). Suppose a pocket born at b ≤ 9 joined its class only above 192, that is with death/b² > 2.37. Its enumeration would stop at its own birth level, and it would be listed as a separate class with no recorded join. Such a pocket would break Conjecture 10.1 without showing up. Nothing found between 1.84·b² and the bound suggests one exists, but the computation cannot exclude it.
- **Range.** w ≤ 9 only. The extremes at b = 4, 6 and 9 are irregular, so a larger sporadic value at some b ≥ 10 cannot be ruled out.
- **Families.** The family scans cover three shapes. Other shapes may do worse.

> **Follow-up (note 11), on visibility:** The invariants (gcd, |Pf|) and two acyclicity tests certify only 144 of the 788,026 classes as separate. Every other class with bottom 6 to 9 (765,131 classes) was enumerated again up to 8b², with full persistence. None reaches a lower level or joins another bottom component, and no pocket dies between the census bound and 8b². A pocket born at b ≤ 9 that this census misses would therefore die above 8·b² (above 20·b² for b ≤ 5). The caveat is narrowed, not closed. See [note 11](11-n4-invariants-descent-joins.md) §§2–3.

> **Follow-up (note 14), on visibility:** Warkentin's forks and pre-forks give a complete invariant of a mutation class, its core, whenever the core is finite. 555,828 of the 788,026 classes have a finite core, no two of them the same, and each of these classes is certified different from every other census class. So the caveat is closed for them. Their pockets are also known at every level, not only for births ≤ 9: 70,376 pockets, none dying above 1.578·birth². The other 232,198 classes contain infinite tubes of non-forks, and include the extremes at bottoms 4, 5, 6, 7 and 9. A finite certificate describes the core of 225,208 of them, those extremes included. With these certificates, 781,036 classes are pairwise certified different, and a hidden join would have to involve one of the remaining 6,990. The certificate code was checked against the census but not read line by line. See [note 14](14-opposite-quivers-forks-and-cores.md).

---

## 4. Reproduce

```bash
PY=python
$PY -I n4_all.py run --N 14 --keep-survivors 9 --out n4_all_N14_k9.json      # about 55 MB; not kept
$PY -I n4_classes.py n4_all_N14_k9.json --B 192 --min-level 8 --max-level 8 --workers 12 --out n4_classes_k8_B192.jsonl
$PY -I n4_classes.py n4_all_N14_k9.json --B 192 --min-level 9 --max-level 9 --workers 12 --out n4_classes_k9_B192.jsonl
gzip n4_classes_k8_B192.jsonl n4_classes_k9_B192.jsonl
$PY -I n4_block_scan.py 14 n4_block_scan.jsonl
```

The attachment-pattern scan was a one-off driver over the same per-class measurement; its output is `n4_triangle_patterns.log`. The two class files are stored gzip-compressed (6 MB and 10 MB, from 100 MB and 190 MB); read them with `zcat` or Python's `gzip.open`.

---

## Sources

- Notes 8 and 9 of this repository.
- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Problem 2.6.14: https://arxiv.org/abs/1608.05735
