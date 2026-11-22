# 3. Note 2's staircase was a measurement error, and rank 3 is settled

*Run on 2026-11-09. This note does two things after note 2: a prior-art check of the bounded-path question, and the cases of rank 2 and rank 3. The rank-3 work exposed an error in note 2's profile code, so every note-2 profile was rerun. Code: [experiments/bounded_paths.py](../experiments/bounded_paths.py) (corrected `profile`, new `--unlabelled` flag and `compare` subcommand) and [experiments/rank3_paths.py](../experiments/rank3_paths.py) (new). Results: `bounded_profile_v2_*.jsonl` (labelled) and `bounded_profile_v2_*_unl.jsonl` (up to relabelling), with the same seeds and bounds as note 2; `bounded_profile_v2_allw_n{4,5,6}_unl.jsonl` (every w); `rank3_profile.jsonl`; and the matching `.log` files. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic; **[M]** recalled, not re-checked.*

> **Update (note 4):** On more components the pocket ratio is larger than measured here. It reaches 5.39 at n = 5, from a pocket born at 166 that rejoins at 895, so "F(n, w) ≈ 2.6w fits all exact data" (§6) no longer holds. Note 4 recasts pockets as persistence pairs of the maximal-entry filtration and splits them into climbs and traps. See [note 4](04-pockets.md).

> **Correction (note 12):** Checked in [note 12](12-checks-of-notes-03-to-10.md). Theorem 3.1 stands. The step of part (3) that rested on computed cases ("in every computed case", Step 4) now has a proof; see the note after Step 4. The statements about n = 4 in §1 items 3–4, §3.4 and §6, such as "excess is essentially absent at n = 4", describe the random sample only, whose class bottoms are ≤ 3. In fact 4-vertex classes have pockets born at every level (note 7), and f(Q, w)/w is unbounded on every n ≥ 4, connected quivers included (notes 9 and 12). §5.2 predates arXiv 2610.36179 (Armstrong-Williams–Hirst–Jackson–Lee, 26 October 2026). That paper bounds the heights on a path from a mutation-acyclic 4-vertex quiver to an acyclic one polynomially in its height, which gives f(Q, w) ≤ w⁴ + 4w³ + 6w² for those classes. Its §6 also shows that the criterion in Theorem 2.9 of arXiv 2411.04209 (item 4) was misstated; the class counts stand. Item 5's "Neville's Markov-type invariant" is *Mutation-acyclic quivers are totally proper*.

---

## 1. Answer

1. **Note 2's profile code overstated f(w) [I].** It tested whether S_w is connected only at levels ≥ w, where a level is a value that occurs as the maximal entry of some quiver in the class. When no quiver of the class has maximal entry in [w, f), it reported the next level that occurs as f(w), even though S_w was already connected at bound w. The low-weight parts of wild classes skip many values, so this happened often. With the same seeds, the corrected code reproduces all 593 exact note-2 values under the old rule (the seven sets at the smaller bounds). Of the 330 (component, w) pairs where note 2 reported f(w) > w, 174 have no excess at all.
2. **The Kronecker staircase is entirely this artifact [I].** In every exhausted sparse component at n = 5, 6 and 7, the corrected f(w) is ≤ w for every w ≥ 4. The only excess left is f(3) = 4 in five components, and up to relabelling it disappears too. The terms 3, 8, 21, 55 are real, but they are maximal entries that occur in the class, not connection bounds. They are Fomin–Neville's Chebyshev weights u_j(3) [P]. The corridor law that note 2's staircase had suggested (Conjecture C of §6) and the w^(3/2) and 3w forms of Conjecture A (§6) lose their evidence.
3. **Most dense thresholds are relabelling copies [I].** Note 2 counted labelled matrices. The open problem, FWZ Problem 2.6.14 (not 2.6.12 as note 2 cites it), is stated up to relabelling [P]. Up to relabelling, f(w) ≤ w at every w from 3 to 1,024 in 17 of 18 exhausted dense components at n = 4. In the exception, the two islands are a quiver and its opposite, and they join at bound 6. Labelled, the corrected thresholds are real but small (≤ 10 at n = 4), and they vanish above w = 12.
4. **Genuine islands remain at n ≥ 5: "pockets" [I].** Up to relabelling, excess is essentially absent at n = 4. At n = 5 to 7 it is common once f is measured at every w, not just note 2's list: f(w) > w in 370 of 1,512 (component, w) pairs at n = 5 (w ≤ 128) and in 56 of 240 at n = 6 (w ≤ 32). At n = 7, measured only on note 2's list, it is 10 of 64. The islands are small: 1 to 7 quivers each, beside one large island, and their number grows with w. The ones inspected are local minima of the maximal entry; 14 of the 35 quivers inspected are Warkentin forks. They rejoin at up to 2.56 times their weight (n = 5: a pocket at weight 48 rejoins at 123). They are the one phenomenon of note 2 that survives as a research question.
5. **Rank 3 is settled, and the staircase predicted for rank 3 does not exist [I, assembled largely from [P]].** For every class on three vertices with minimal representative w*: every quiver of the class has maximal entry ≥ w*, and up to relabelling S_w is connected inside G_w for every w ≥ w*. There are no thresholds, islands or staircases (Theorem 3.1). Labelled, the same holds except for acyclic triangles with an edge of weight 1. For those, the labelled islands at w* rejoin at the smallest cyclic quiver of the class, of weight min(pq + l) over the three rotations. The calculation covers all 553 classes with minimal entries ≤ 10, for every w ≤ 512. Most of this is already in Fomin–Neville §3, Beineke–Brüstle–Hille, Assem–Blais–Brüstle–Samson and Caldero–Keller. It is not a publishable note on its own.
6. **Prior art [P].** No paper studies S_w, f or the connectivity of bounded-weight parts of a mutation class. Of ten claims about the literature that had been recalled from memory at the start, six needed correction (§5). Two corrections matter for the stability-manifold reading of the question (Problem F of §6). First, Stab(D^b(K_l)) for l ≥ 3 is C × ℍ, and every stability condition there has a σ-exceptional pair (Dimitrov–Katzarkov), so a "wild region without exceptional pairs" does not exist. Second, King–Qiu contain no chamber description of Stab.
7. **What survives of the starting conjectures (§6).** The decidability motivation, now with the right problem number and the right convention (unlabelled). The pockets, which take over from thresholds and corridors as the open structure. The polynomial growth of |S_w|, which the error did not touch. And a cleaner heart-theoretic question: the three-level tower of hearts, labelled quivers and unlabelled quivers, in which labelled islands are monodromy. The rank-3 and corridor programme is finished or void.

---

## 2. The measurement error

**What the code did.** `merging_profile` adds the quivers of the enumerated component in order of maximal entry (the *levels* that occur), with union–find over mutation edges. For a target w it started checking S_w only at the first level L ≥ w, and reported L as f(w) when S_w was connected there. If no quiver of the class has maximal entry in [w, L), then S_w = S_{m_w}, where m_w is the largest level ≤ w. That set may have been connected since level m_w ≤ w, and the true f(w) is then ≤ w.

**Example** (sparse n = 5, trial 0, note 2 §8.3 row 1). The levels present are 3, 8, 9, 21, 24, 45, 48, 55, 63, 64, 71, 72, 80 and 127; the corridor values 8, 21 and 55 are among them, and 4 to 7 are not. So S_3 = S_4 = … = S_7 (1,008 labelled quivers, connected at bound 3).

| w | 3 | 4 | 5 | 6 | 8 | 12 | 16 | 24 | 32 | 64 |
|---|---|---|---|---|---|---|---|---|---|---|
| note 2 (old rule) | 3 | 8 | 8 | 8 | 8 | 21 | 21 | 24 | 45 | 64 |
| corrected | 3 | 3 | 3 | 3 | 8 | 9 | 9 | 24 | 24 | 64 |

**The fix.** f(w) is now the least level ≥ m_w at which S_w is connected, so f(w) ≤ w means no excess. The old value is kept in each row as `f_note2`. Components only merge, so the prefix of states known to lie in one component only grows. Checking connectivity is therefore linear in the component size, which makes it cheap to evaluate f at every w (§3.4). On 36 recomputed rows, this incremental check gives the same output as the direct one.

**What the error did not touch.** The forced-excursion test (note 2 §4.5, §8.2, §8.3) searched at explicit bounds and is unaffected. So are the counts |S_w| and the growth exponents (note 2 §4.4), and the two-bound robustness check as a comparison between runs. Neither are the thresholds f(3) of note 2 §4.3: level 3 is present in every dense sample.

---

## 3. The rerun of note 2

### 3.1 Excess before and after, by set

Same seeds, bounds and w lists as note 2. "Pairs" are (component, w) pairs with f(w) exact, over components exhausted both labelled and up to relabelling.

| Set (note 2 file) | Components exhausted | Pairs | Excess, note-2 rule | Excess, corrected, labelled | Excess, corrected, up to relabelling |
|---|---|---|---|---|---|
| n = 4, bound 4096 | 18 | 216 | 126 | 36 | 3 |
| n = 5, bound 128 | 12 | 120 | 54 | 47 | 11 |
| n = 6, bound 32 | 7 (+1 unlabelled only) | 49 | 32 | 32 | 7 (+3) |
| sparse n = 5, bound 128 | 10 | 100 | 47 | 3 | 0 |
| sparse n = 6, bound 64 | 5 (+3 unlabelled only) | 45 | 24 | 2 | 0 (+0) |
| n = 7, bound 16 | 8 | 48 | 37 | 36 | 4 |
| sparse n = 7, bound 32 | 2 (+6 unlabelled only) | 16 | 10 | 0 | 0 (+0) |

### 3.2 Sparse starts: no staircase

In every exhausted sparse component, the corrected labelled f(w) is ≤ w for all w ≥ 4. Labelled excess remains only at w = 3, where f(3) = 4 in three components at n = 5 and two at n = 6, with 5 to 60 islands. Up to relabelling, those islands are one. At n = 7, two sparse components are exhausted labelled and eight up to relabelling, and none has any excess. The corridor values appear only as the levels that occur, which note 2's rule turned into connection bounds. Note 2's remark that one n = 5 component "has maximal entry 63 because the next step is 144" is correct about the levels; the corrected f there is 3, 3, 3, 3, 8, 8, 8, 21, 21, 63, all ≤ w.

### 3.3 Dense starts, labelled

The corrected labelled profiles keep real thresholds at small w, but the "small excess above the threshold" of note 2 §4.2 (ε ≤ 2 typically, f(256) up to 267) was the artifact:

- **n = 4** (18 components): f(w) ≤ w for every w ≥ 12 in all 18. The thresholds (the largest f(w) with f(w) > w) are 4, 4, 4, 5, 5, 6, 6, 6, 6, 6, 7, 9 and 10, plus 5 components with none. They are note 2's f(3) values, which the error does not affect: every dense start has maximal entry 3, so level 3 is always present. What the error inflated was the excess above the threshold.
- **n = 5** (12 components): no excess at w = 12 and 16. Excess at w ≥ 24 occurs in two components only (§3.5).
- **n = 6** (7 components, bound 32): thresholds 5 to 27.

### 3.4 Up to relabelling

Quivers are identified when they differ by a simultaneous permutation of rows and columns. The canonical form is the lexicographically least P B Pᵀ, over the permutations that list the vertices in increasing order of their sorted row; it was checked to be invariant on 1,500 random relabellings. Mutation commutes with relabelling, so G_B descends to the quotient. The FWZ problem, Caldero–Keller and the rank-3 classification are all stated in this convention (§5).

**n = 4, every w from 3 to 1,024** (`bounded_profile_v2_allw_n4_unl.jsonl`): f(w) ≤ w at every w in 17 of 18 exhausted components. The exception (trial 14) has f(3) = f(4) = f(5) = 6. Its S_3 consists of exactly two quivers, each the opposite (−B) of the other. Each sits alone in its island, and the two join at bound 6. Identifying B with −B does not merge them earlier, because the identification is not part of the graph; it only shows what the two islands are.

**Labelled islands are relabelling copies.** At w = 3 the labelled S_3 splits into 2 to 5,040 islands in most dense components: 720 = 6! in five of seven components at n = 6, and 5,040 = 7! in seven of eight at n = 7. Up to relabelling, the same sets are one island in all but 2 of 45 dense components (n = 4 to 7). The exceptions are the opposite pair at n = 4 and n = 5 trial 10. The labelled thresholds thus measure how far one must go to realise a relabelling by mutations, which is a monodromy question, not a connectivity question (§6).

**n = 5 and 6, every w** (`bounded_profile_v2_allw_n5_unl.jsonl` at bound 512 for w ≤ 128, `bounded_profile_v2_allw_n6_unl.jsonl` at bound 64 for w ≤ 32; every component exhausted). Here the excess is not rare:

- f(w) > w in 370 of 1,512 (component, w) pairs at n = 5 (9 of 12 components) and in 56 of 240 at n = 6 (5 of 8).
- Note 2's w list missed most of it, because the excess sits in w-intervals between the listed values. For example, in n = 5 trial 1, f jumps to 181 for w = 97–106 and to 262 for w = 107–128.
- The worst ratios are 123/48 = 2.56 (n = 5, trial 11), 262/107 = 2.45 (n = 5, trial 1) and 27/16 = 1.69 (n = 6, trial 5).
- In n = 5 trial 0 the excess persists at every w, with f(w)/w between 1.1 and 1.3 above w = 20, and the later junctions 81, 94, 107, 120 and 133 are evenly spaced by 13.

These values are lower bounds in the sense of note 2 §8.1: an island joined only above bound 512 would be invisible.

### 3.5 Pockets: the genuine islands

Up to relabelling, these are all the islands at n ≤ 7 for note 2's w list (n = 7 at bound 32). The every-w runs (§3.4) find many more at n = 5, all of the same shape: one large island and up to 8 small ones of 1 to 7 quivers each. For example, n = 5 trial 1 at w = 128 has small islands of 1, 1, 1, 1, 2, 3, 6 and 7 quivers next to one of 1,671.

| n | Trial | w | Islands of S_w | Smallest islands | Joined at bound | f(w)/w |
|---|---|---|---|---|---|---|
| 4 | 14 | 3–5 | 2 | 1 + 1 quiver (Q and −Q) | 6 | 2.00 |
| 5 | 0 | 4–6 | 2–3 | 2 and 3 quivers at weight 4 | 10, 12 | 2.50 |
| 5 | 0 | 24–64 | 2–3 | 1 + 1 quiver at weights 50, 54 | 29, 42, 78 | 1.21–1.31 |
| 5 | 3 | 4 | 3 | – | 5 | 1.25 |
| 5 | 4 | 6 | 3 | – | 7 | 1.17 |
| 5 | 10 | 3 | 2 | – | 4 | 1.33 |
| 5 | 11 | 64 | 2 | 3 quivers at weights 48, 48, 63 | 123 | 1.92 (2.56 at w = 48) |
| 6 | 0 | 6–16 | 2 | – | 7, 9, 24 | 1.50 |
| 6 | 1 | 4, 12, 16 | 2–3 | – | 5, 16, 18 | 1.33 |
| 6 | 4 | 8 | 4 | – | 11 | 1.38 |
| 6 | 5 | 5–16 | 2–3 | 1 + 4 quivers at weight 16 | 6, 9, 27 | 1.69 |
| 7 | 0, 1, 5, 6, 7 | 4–24 | 2–10 | – | 5 to 31 | 1.50 |

What the inspected pockets have in common [I]:

- **They are local minima of the maximal entry.** In the pockets inspected (n = 5 trials 0 and 11, n = 6 trial 5), each quiver either has every mutation at a strictly higher maximal entry or lies in a pocket of 2 to 4 quivers joined at their own level. Example (n = 5, trial 0): a quiver of maximal entry 50 whose five mutations have maximal entries 76, 78, 129, 156 and 1,655.
- **Some are forks, most are not.** None of the five quivers in the small-w pockets is a fork in Warkentin's sense (abundant, with a point of return; Definition 2.1 of his thesis); most have entries 0 or 1. At larger w forks appear: in n = 5 trial 1 at w = 128, 12 of the 22 pocket quivers are forks. This fits his Lemma 2.5 [P]. Away from the point of return a fork tree only raises weights, so the part of a tree inside S_w is a subtree containing its root fork. It becomes a pocket when the root's return mutation raises the maximal entry above w.
- **They are not opposite pairs,** except at n = 4. Identifying B with −B merges the islands earlier in none of the six n = 5 and n = 6 cases tested.

### 3.6 Robustness across ambient bounds

Up to relabelling, every set was also run at note 2's larger ambient bound: 65,536 at n = 4, 512 at n = 5, 64 at n = 6 and 32 at n = 7. Every component exhausted at both bounds gives the same f(w) at both, for every w up to half the smaller bound: 216 of 216 at n = 4, 120 of 120 at n = 5, 56 of 56 at n = 6 and 40 of 40 at n = 7. All n = 7 components are exhausted at bound 32 up to relabelling, against 3 of 8 labelled in note 2.

Note 2 §8.1's warning case (n = 7, trial 7) was a relabelling effect. There, 5,040 weight-3 quivers attached only through weight 17. Up to relabelling, that component has no excess at w ≤ 12 at either bound.

The labelled runs at the larger bounds were not repeated. They take hours, and note 2 already made the labelled two-bound comparison.

---

## 4. Rank 2 and rank 3

### 4.1 Rank 2

The mutation class of the Kronecker quiver K_b (b ≥ 1) is {B, −B} as labelled matrices and a single quiver up to relabelling: mutation at either vertex only reverses the arrows. f(Q, w) = w trivially. The "line" one pictures for K_b is the exchange graph of seeds, or of hearts, not of quivers. The Chebyshev numbers appear in quivers only when K_b sits inside a larger quiver: alternating mutation at the two Kronecker vertices multiplies the other weights by u_j(b) (Fomin–Neville, Prop. 3.13 [P]).

### 4.2 Rank-3 moves

Write a cyclic quiver as (x, y, z), its weights around the oriented 3-cycle, and an acyclic one as (p, q, l): arrows source → elbow (p), elbow → sink (q) and source → sink (l). In rank 3 a mutation changes one weight, the one opposite the mutated vertex [P, Fomin–Zelevinsky; FN §3]:

- cyclic, at the vertex opposite z: z ↦ |xy − z|. The result is cyclic if xy > z, has a zero edge if xy = z, and is acyclic if xy < z;
- acyclic, at the elbow: l ↦ l + pq, and the result is cyclic;
- acyclic, at the source or sink: weights unchanged, arrows at that vertex reversed. The roles cycle: (p, q, l) → (q, l, p).

### 4.3 The theorem

Call a cyclic quiver a **root** if all its weights are ≥ 2 and 2z ≤ xy for each weight z and the other two x, y.

**Theorem 3.1 (rank 3) [I, from [P] ingredients].** Let Q have three vertices. Its class contains a root (mutation-cyclic) or an acyclic quiver (mutation-acyclic), never both. Let w* be the maximal entry of a root, or of an acyclic quiver, in the class; this does not depend on the choice. Then:

1. every quiver in the class has maximal entry ≥ w*, so S_w = ∅ for w < w*;
2. up to relabelling, S_w is connected inside G_w for every w ≥ w*, so f(Q, w) ≤ w;
3. labelled, (2) holds for mutation-cyclic classes and for acyclic triangles with all weights ≥ 2. For an acyclic triangle with an edge of weight 1, let j = min over the three rotations (p, q, l) of pq + l, the smallest maximal entry of a cyclic quiver in the class. For w* ≤ w < j, S_w consists of acyclic quivers in more than one labelled island, and f(Q, w) ≥ j. Measured, not proved: there are 2 islands (6 when two weights equal 1), f(Q, w) = j for w* ≤ w < j, and f(Q, w) ≤ w for w ≥ j (§4.5).

*Proof.*

**Step 1 (descent).** A cyclic quiver that is not a root has a move that lowers one weight and changes no other. If all weights are ≥ 2, some 2z > xy, and then |xy − z| < z. If a weight is 1, say x = 1 and z ≥ y, the move opposite z gives z − y < z. An acyclic quiver has no lowering move (FN Lemma 3.5 [P]). Lowering moves strictly decrease the total weight, so from any quiver they reach a root or an acyclic quiver, and the maximal entry never increases on the way.

**Step 2 (roots).** Let x, y, z ≥ 2. If 2z ≥ xy then 2y ≤ xz, since otherwise 4yz > x²yz and x < 2; likewise 2x ≤ yz. So if the move opposite z does not raise z, the other two moves do not lower their weights (the strict form is FN Lemma 3.6 [P]). Now take a reduced path (no immediate backtracking) from a root R. No move from R lowers a weight. By induction, no step of the path lowers a weight, and every quiver on it is cyclic with weights ≥ 2. If the step into a quiver at vertex k did not lower its weight, then the move back at k does not raise it, so the other two moves do not lower theirs, and a reduced path continues with one of those. Hence the whole class of R is cyclic with weights ≥ 2 and contains no acyclic quiver. Every member X is joined to R by a path along which no weight rises. A reduced path between two roots does not lower total weight in either direction, so every step keeps the weights, and all roots of a class have the same weights. This is the mutation-cyclic half of Beineke–Brüstle–Hille (Thm 1.2) and Assem–Blais–Brüstle–Samson (Thm 1.1) [P]. Items 1 to 3 follow for mutation-cyclic classes, labelled as well.

**Step 3 (acyclic classes, up to relabelling).** By Caldero–Keller (Cor. 4; restated as FWZ Thm 2.6.11) [P], any two acyclic quivers in a class are joined, up to isomorphism, by source and sink mutations. These keep the weights, so the acyclic quivers form one island inside G_{w*} up to relabelling. With Step 1 this gives items 1 and 2.

A rank-3 argument that avoids cluster categories also works [I]. Take a path between two acyclic quivers, and on it a cyclic quiver of largest total weight. Its two path neighbours are not heavier. If all its weights are ≥ 2, Step 2 forces both neighbours to be the same quiver, and the path backtracks. Otherwise take it as (1, y, z) with b₁₂ = 1, b₂₃ = y, b₃₁ = z and z > y (after B ↦ −B if needed). Its moves that do not raise the total weight are at most μ₂ (giving A, acyclic) and μ₁ (giving C, cyclic (1, z, z − y), non-raising when z ≤ 2y). If both path neighbours come from the same move, the path backtracks. Otherwise they are A and C, and μ₂(C) is acyclic and is a source/sink rotation of A up to relabelling. This was computed by hand and checked for all y < 30, z < 60. So the segment A – Q – C can be replaced by A – (source/sink moves) – μ₂(C) – C, all of smaller total weight. The case y = z, where both moves give paths, is similar. The cases yz ≤ 2 belong to mutation-finite classes, which the enumeration covers. Induction on the multiset of total weights of the cyclic quivers on the path leaves a path of source/sink moves only.

**Step 4 (labelled).** For acyclic quivers with all weights ≥ 2, FN Lemma 3.8 [P] says that the acyclic quivers in a labelled class are reorientations of one another with the labels fixed. So the labelled acyclic quivers are already joined by source/sink moves, and Step 1 gives item 3. With a weight-1 edge, the detour of Step 3 joins A to a relabelled copy of itself, which in every computed case lies in a different source/sink orbit. So the labelled class contains several such orbits. Any labelled path between two of them must pass through a cyclic quiver. A cyclic quiver descends with non-increasing maximal entry to an acyclic one, and the last cyclic quiver before that is (p, q, l + pq) for some rotation, so it has maximal entry ≥ j. This gives f ≥ j; the rest of item 3 is measured. ∎

> **Correction (note 12):** "In every computed case" can be replaced by a proof. Source and sink moves keep the weight of every labelled edge, and below j the labelled islands are their orbits. An orbit consists of one assignment of weights to the edges together with the cyclic rotations of one vertex order. Rotate A in its orbit so that its source → elbow edge has weight 1: arrows 1 → 2 (1), 2 → 3 (q), 1 → 3 (l). Mutating at 2, then 1, then 2 passes the cyclic quivers (1, q, l + q) and (1, l, l + q), whose maximal entry is l + q = j, and ends at the acyclic quiver 3 → 2 (l), 2 → 1 (1), 3 → 1 (q). If q ≠ l, this end quiver gives the edges {2, 3} and {1, 3} different weights from A. If q = l, its vertex order 3, 2, 1 is the reverse of A's. Either way it lies in another orbit, so S_w has at least two labelled islands for w* ≤ w < j. The measured part of (3) was confirmed on all 396 such triangles with weights ≤ 12 in infinite classes. The triangle (1, 1, 1), of finite mutation type, has 2 islands, not 6. See [note 12](12-checks-of-notes-03-to-10.md).

**Corollary.** Up to relabelling, rank-3 mutation equivalence is decided by search inside G_{max(w_Q, w_Q′)}. This is just the rank-3 descent algorithm in another form (ABBS §2.5; FN §3).

### 4.4 Labelled rank 3 in one line

Labelled islands in rank 3 come only from weight-1 edges. A cyclic quiver (1, y, z) with y < z ≤ 2y has two non-raising moves, and they lead to relabelled copies of the same acyclic quiver. FN's Example 3.11 (isomorphic acyclic quivers that are not labelled-equivalent) is the large-weight case of this, where the copies are never joined at all. This is the simplest instance of the monodromy reading in §6.

### 4.5 Computation

`rank3_paths.py profile --W0 10 --w-max 512 --B-big 8192` lists every class whose minimal representative has entries ≤ 10 (553 classes, 550 infinite), deduplicated by the canonical minimal quiver. It measures the corrected f(w) for w = 1, …, 512, labelled and up to relabelling [I]:

- every component is exhausted at bound 8192, and S_w is connected for every w in all 550 infinite classes;
- w_min equals the maximal entry of the minimal representative in all 550;
- up to relabelling, f(w) ≤ w for every w in all 550 classes, and S_{w*} is one island in all 550;
- labelled: no excess in all 157 mutation-cyclic classes (Markov constants ≤ 4, as BBH predicts), all 54 path classes (one zero weight), and all 249 acyclic triangles with weights ≥ 2. All 90 acyclic triangles with a weight-1 edge have excess: 2 islands at w* (6 when two weights are 1), exactly one join at j = min(pq + l), and f(w) ≤ w for w ≥ j. The maximal labelled f(w)/w is 2.00, attained by every triangle (1, a, a), where w* = a and j = 2a.

---

## 5. Prior art and the recalled claims

Checked on 2026-11-09 against the arXiv full texts in a first reading pass. The key passages were then re-read for FWZ 2.6.14, Caldero–Keller Cor. 4, FN Example 3.11, Lemmas 3.5–3.8 and Prop. 3.13, and Warkentin Def. 2.1 and Lemma 2.5. The rest are as the first pass recorded them and were not re-read.

### 5.1 The claims recalled from memory

| Recalled claim | Status | What the source says |
|---|---|---|
| Weight ≤ 2 criterion (Derksen–Owen) | confirmed; attribution | Felikson–Shapiro–Tumarkin Thm 2.6, called well known; Derksen–Owen Cor. 8 proves one direction, using the rank-3 classification of ABBS. Connectedness is needed |
| Finite types: surfaces + 11 exceptions | confirmed | FST Thm 6.1: E6, E7, E8, Ẽ6, Ẽ7, Ẽ8, E6^(1,1), E7^(1,1), E8^(1,1), X6, X7; FST Thm 8.2: every mutation-infinite class grows exponentially |
| BBH: cyclic criterion, Markov constant | confirmed | Thm 1.2: (x, y, z) is cluster-cyclic iff x, y, z ≥ 2 and C ≤ 4; Lemma 3.1: invariance of C; Thm 5.1: unique representative reached by strict descent |
| ABBS: rank-3 classes | confirmed | Thm 1.1: mutation-cyclic classes, up to transposition and permutation, ↔ triples 2 ≤ a ≤ b ≤ c with ab ≥ 2c; Prop. 2.5: the root has the fewest arrows; §2.5: the descent algorithm |
| Neville: rank-3 descent, non-confluence | corrected | Fomin–Neville (Selecta 2025) prove long mutation cycles (Thm 1.1); there is no non-confluence theorem, only the remark that descent would have to be confluent over arbitrarily large diamonds. Rank 3 is in §3, "without claiming any originality". Quivers are labelled |
| Soukup: NP-hardness | corrected scope | Thm 1.1 (reach exactly k arrows between two vertices) and Thm 1.2 (reach a quiver with no arrows between frozen vertices) both need frozen vertices. Nothing is shown for mutation equivalence of all-mutable quivers |
| FWZ Problem 2.6.12 | corrected | It is **Problem 2.6.14**, and mutation equivalence there is up to isomorphism (Def. 2.6.1). The matrix version (Problem 2.8.2) allows simultaneous renumbering |
| Caldero–Keller | confirmed, up to isomorphism | Cor. 4: the acyclic seeds form a connected subgraph of the exchange graph; FWZ Thm 2.6.11: sink/source mutations reach a quiver isomorphic to Q′. There is no labelled version, and FN Ex. 3.11 shows that one fails |
| Keller–Yang, King–Qiu, chambers | partly | KY Thm 3.2: derived equivalence of Ginzburg algebras. KQ: the principal component EG° and Ext quivers as coloured quivers (Thm 8.10). **KQ contain no chamber description of Stab**; that picture (Bridgeland; Woolf) is still [M] |
| Dimitrov–Katzarkov, wild Kronecker | **corrected** | Stab(D^b(K_l)) ≅ **C × ℍ** for l ≥ 3, not C². **Every** σ has a σ-exceptional pair, so Stab is the union of the exceptional-pair cells (DK, arXiv 1602.09117 v3, Thm 1.5) |
| Kronecker entropy | corrected by a factor 2 | DHKK §4: S∘[−1] on D^b(K_m) has entropy log λ with λ = ((m + √(m² − 4))/2)², that is 2·log((m + √(m² − 4))/2). Ikeda: mass growth equals entropy under an algebraicity hypothesis; no Kronecker example |

### 5.2 Prior art on bounded weights

No paper studies S_w(Q), its connectivity, f, or counts of bounded-weight quivers in an infinite class. The nearest work:

1. **Warkentin's thesis (TU Chemnitz 2014)** [P]. *Forks* are abundant non-acyclic quivers with a point of return. Mutation away from the point of return gives a fork with no weight decreased (Lemma 2.5), so the fork side of each return edge is a tree in which weights only grow. Every connected mutation-infinite quiver is mutation-equivalent to a fork (Thm 3.2). Consequence for us [I]: the part of a fork tree inside S_w is a subtree containing the tree's root. It is a pocket exactly when the root's return mutation leaves S_w, and §3.5 finds pockets of this kind as well as pockets of non-forks.
2. **Ervin, "forkless part" (EJC 2024, arXiv 2306.07502)** [P]. The non-forks form one convex subgraph of the labelled mutation graph, which is finite for some classes and infinite for others. [H] If the forkless part is finite, f(Q, w) ≤ w above some threshold whenever the walk from a fork back to the forkless part never raises the maximal entry. Lemma 2.5 gives that inside the fork tree but not across the return edge. Pockets made of non-forks live in the forkless part.
3. **Fomin–Neville Prop. 3.13 and Soukup Thm 1.3** [P]: weights along alternating mutations are the Chebyshev combinations u_j(a)b + u_{j−1}(a)c, and growth is exponential with ratio (a + √(a² − 4))/2 for a ≥ 3. These are the corridor values of note 2 §8.3, already known.
4. **Armstrong-Williams–Hirst–Jackson–Lee, arXiv 2411.04209** [P]: a computer-assisted proof that mutation-acyclicity is decidable for n = 4 with weights ≤ 2 (667 classes, breadth-first search to depth 12). This is the nearest methodological precedent.
5. **Further reading:** Neville's Markov-type invariant for mutation-acyclic quivers (arXiv 2409.17832); Fomin–Neville, arXiv 2406.03604 ("no known algorithm for detecting mutation equivalence"); Seven (arXiv 1201.4270); Warkentin, arXiv 1102.3382; Ladkani (arXiv 1104.0436); Lawson (arXiv 1505.01735).

---

## 6. What this does to the starting conjectures

The work started from the measurements of note 2 and from the following working statements. Here w*(Q) is the threshold of note 2, the bound at which the low quivers of the class of Q first become connected.

- **Conjecture A (bounded paths).** There is a function F(n, w), polynomial in w for fixed n, such that any two mutation-equivalent quivers on n vertices with entries ≤ w are joined by a mutation path all of whose quivers have entries ≤ F(n, w).
- **Conjecture B (dense law).** For a class without heavy rank-2 corridors, f(Q, w) = max(w, w*(Q)) + ε with ε bounded independently of w.
- **Conjecture C (corridor law).** If the class of Q contains a Kronecker subquiver K_b on which the rest of the quiver acts trivially along the corridor, then f(Q, w) on a corridor interval equals the next term of the recurrence, and f(Q, w)/w ≤ (b + √(b² − 4))/2 + o(1). It predicted a staircase already in rank 3.
- **Conjecture D (growth).** |S_w(Q)| is eventually a quasi-polynomial in w, of degree depending on n.
- **Problem E (thresholds).** Characterise w*(Q). Is it bounded by a function of n alone?
- **Problem F (hearts).** Translate A to D into statements about the space of stability conditions: let Stab_{≤w} be the union of the chambers of hearts with all Ext¹(S_i, S_j) ≤ w; are its components merged inside Stab_{≤F(n,w)}?
- **Corollary G (decidability).** Any effective F in Conjecture A gives a decision procedure for mutation equivalence of quivers with entries ≤ w: bidirectional search among the quivers with entries ≤ F(n, w).

| Starting statement or measurement | After this note |
|---|---|
| Note 2: the dense excess and the corridor staircase | Artifact (§2, §3). Corrected labelled: no excess above w = 12 at n = 4; sparse: none above w = 3 |
| Note 2: thresholds | Real for labelled quivers, mostly relabelling. Up to relabelling: one opposite-pair case at n = 4, plus the pockets at n = 5 to 7 |
| Note 2: excursions, growth, and its caveat | Unaffected |
| Conjecture A | Restate up to relabelling. Worst measured ratio 2.56 (n = 5, w = 48). F(n, w) ≈ 2.6w fits all exact data, F = w does not, and the growth of the excess with w is open |
| Conjecture B | Restate: f(Q, w) ≤ w up to relabelling outside pockets. True in rank 3 (Theorem 3.1) and on all n = 4 data except one opposite pair; at n = 5, pockets affect a quarter of the (component, w) pairs |
| Conjecture C (corridor law) | Withdrawn; the corridor values are FN's Chebyshev weights, a known fact |
| Conjecture D (growth) | Unaffected; note 2's counts are labelled, and unlabelled counts differ by a factor ≤ n! |
| Problem E (thresholds) | Becomes the **pocket problem**: describe the local minima of the maximal entry that are not in the main island of S_w, and bound their barrier (the bound at which they rejoin) |
| Problem F (hearts) | Sharper: see below |
| Rank 2 and rank 3 | Settled; the predicted rank-3 staircase does not exist |
| Problem F: the stability conditions of the Kronecker quiver | Must be restated: Stab(K_l) ≅ C × ℍ, with exceptional pairs everywhere |
| Problem F: the entropy log φ² attached to a corridor | The DHKK functor has entropy 2·log((b + √(b² − 4))/2); which functor "advances along a corridor" must be fixed first |
| The programme as a whole | The striking phenomena were the artifact. What is left is narrower: pockets and growth |

**Problem F, restated [H].** The mutation picture has three levels. Hearts in the principal component EG° map onto seeds and labelled quivers, and labelled quivers map onto quivers up to relabelling. Each map is a quotient by a group action: autoequivalences (the cluster modular group) and S_n. A labelled island structure over a connected unlabelled S_w is the monodromy of loops of bounded weight. The labelled f is the bound at which those loops generate every relabelling the class realises; the rank-3 weight-1 triangles are the first example. Stab_{≤w}, the union of chambers of hearts with all Ext¹(S_i, S_j) ≤ w, is one level higher still. It is connected exactly when the unlabelled S_w is connected inside G_w *and* bounded-weight loops generate the deck group of hearts over unlabelled quivers. The second condition is a question about the cluster modular group, and Stab_{≤w} could be disconnected even in rank 3. This is the precise form of Problem F, and it is untested.

**Decidability.** FWZ's problem is the unlabelled one, so bounded search should run on canonical forms, which the new `--unlabelled` flag does. Corollary G stands as stated, with the right problem number. The data at n ≤ 7 is consistent with F(n, w) = max(w, b(n, w)), where b is the pocket barrier.

---

## 7. Limitations

- The rerun inherits note 2's samples: random dense starts with entries in [−3, 3] and sparse starts with one weight-3 edge, n ≤ 7, 7 to 20 components per set.
- Pocket statistics come from 20 components at n = 5 and 6. The descriptions (local minima, sizes, forks) rest on the pockets inspected in §3.5, not all of them.
- Theorem 3.1(3) is proved for f ≥ j and measured for f = j and for f ≤ w above j (550 classes with minimal entries ≤ 10, w ≤ 512).
- §5 relies on a single reading pass, not re-read against the sources except where noted; the Dimitrov–Katzarkov and DHKK corrections should be re-read before Problem F is taken up.

---

## 8. Reproduce

```bash
PY=python
# every note-2 profile, corrected, labelled and up to relabelling (same seeds and bounds as note 2)
$PY -I bounded_paths.py profile --n 4 --B-big 4096 --budget 3000000 --w 3 4 5 6 8 12 16 24 32 64 128 256 --trials 20 --workers 4 --seed 20261108 --out bounded_profile_v2_n4_B4096.jsonl
$PY -I bounded_paths.py profile --unlabelled --n 4 --B-big 4096 --budget 3000000 --w 3 4 5 6 8 12 16 24 32 64 128 256 --trials 20 --workers 4 --seed 20261108 --out bounded_profile_v2_n4_B4096_unl.jsonl
#   ... likewise for every command of note 2 §7 and §8.5, with output bounded_profile_v2_<suffix>[_unl].jsonl
$PY -I bounded_paths.py compare bounded_profile_v2_n4_B4096.jsonl bounded_profile_v2_n4_B4096_unl.jsonl
# every w, up to relabelling
$PY -I bounded_paths.py profile --unlabelled --n 4 --B-big 4096 --budget 3000000 --w $(seq 3 2048) --trials 20 --workers 4 --seed 20261108 --out bounded_profile_v2_allw_n4_unl.jsonl
$PY -I bounded_paths.py profile --unlabelled --n 5 --B-big 512 --budget 3000000 --w $(seq 3 256) --trials 12 --workers 4 --seed 20261208 --out bounded_profile_v2_allw_n5_unl.jsonl
$PY -I bounded_paths.py profile --unlabelled --n 6 --B-big 64 --budget 3000000 --w $(seq 3 32) --trials 8 --workers 4 --seed 20261308 --out bounded_profile_v2_allw_n6_unl.jsonl
# rank 3
$PY -I rank3_paths.py profile --W0 10 --w-max 512 --B-big 8192 --workers 4 --out rank3_profile.jsonl
$PY -I rank3_paths.py summarize rank3_profile.jsonl
```

The full rerun is the note-2 command list with `--out` changed. The labelled runs have suffixes `n4_B4096`, `n5_B128`, `n6`, `n7_B16`, `sparse_n5`, `sparse_n6` and `sparse_n7`. The `--unlabelled` runs have the same suffixes plus `n4`, `n5`, `n6_B64` and `n7`, the larger bounds. `profile` overwrites its output unless `--append` is given; `rank3_paths.py profile` always overwrites.

---

## Sources

- Fomin, Williams, Zelevinsky, *Introduction to cluster algebras*, Ch. 1–3 (Def. 2.6.1, Thm 2.6.11, Problem 2.6.14, Problem 2.8.2): https://arxiv.org/abs/1608.05735
- Fomin, Neville, *Long mutation cycles*, §3 (Lemmas 3.5–3.8, Example 3.11, Prop. 3.13): https://arxiv.org/abs/2304.11505
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251
- Beineke, Brüstle, Hille, *Cluster-cyclic quivers with three vertices and the Markov equation*: https://arxiv.org/abs/math/0612213
- Assem, Blais, Brüstle, Samson, *Mutation classes of skew-symmetric 3×3 matrices*: https://arxiv.org/abs/math/0610627
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014: https://d-nb.info/1214302807/34
- Ervin, forkless part of a mutation class: https://arxiv.org/abs/2306.07502
- Soukup, *Complexity of quiver mutation equivalence*: https://arxiv.org/abs/2306.03232
- Felikson, Shapiro, Tumarkin, *Skew-symmetric cluster algebras of finite mutation type*: https://arxiv.org/abs/0811.1703; Derksen, Owen: https://arxiv.org/abs/0804.0787
- Dimitrov, Katzarkov, wild Kronecker quivers: https://arxiv.org/abs/1602.09117 and https://arxiv.org/abs/1311.7125
- Dimitrov, Haiden, Katzarkov, Kontsevich, *Dynamical systems and categories*: https://arxiv.org/abs/1307.8418; Ikeda, *Mass growth of objects and categorical entropy*: https://arxiv.org/abs/1612.00995
- King, Qiu, *Exchange graphs and Ext quivers*: https://arxiv.org/abs/1109.2924; Keller, Yang: https://arxiv.org/abs/0906.0761
- Armstrong-Williams, Hirst, Jackson, Lee: https://arxiv.org/abs/2411.04209
- Notes 1 and 2 of this repository.
