# 4. Pockets, as persistence of the maximal-entry filtration

*Run on 2026-11-09. This note takes up the pocket problem in the form [note 3](03-profile-correction-and-rank-3.md) §6 gave it: describe the pockets, and bound their barriers. Code: [experiments/pockets.py](../experiments/pockets.py) (new). Results: `pockets_n4_B4096.jsonl`, `pockets_n5_B512.jsonl`, `pockets_n5_B2048.jsonl`, `pockets_n6_B128.jsonl`, `pockets_n7_B48.jsonl`, `pockets_sparse_n5_B512.jsonl`, `pockets_sparse_n6_B128.jsonl`, and the matching `.log` files. Everything here is up to relabelling of the vertices, the convention of FWZ Problem 2.6.14. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Follow-up (note 5):** Note 5 surveys every local minimum of total weight. Traps are 2 to 12 % of them, and none occur at n = 4 above total weight 32. Most trap barriers are the height of one first mutation, and a 2-step lookahead followed by descent finds 85 % of them at n = 5. The open question is reduced to Problem 5.2: is the escape ratio of local minima bounded by some c(n)? See [note 5](05-traps.md).

> **Correction (note 12):** Checked in [note 12](12-checks-of-notes-03-to-10.md). The formula of §2 and the elder rule were re-derived and checked with independent code: 4,765 values of f, and the pairs of 248 census classes. Two conclusions need narrowing. First, "At n = 4 they are rare" (§1 item 2) holds only for the random sample, whose class bottoms are ≤ 3 (note 7). Second, no linear F(n, w) exists for any n ≥ 4, connected quivers included (note 12, Proposition 12.1). So the ratios measured here for n = 5 to 7, such as c(5) ≥ 5.39, describe random dense classes, not the worst case.

---

## 1. Answer

1. **The bounded-path profile is 0-dimensional persistence [I].** Filter the mutation graph of a class by maximal entry: X_L is the set of quivers with all |entries| ≤ L. A component of X_L is born at its lowest quiver and dies when it merges into an older component (the elder rule). Call a component that dies above its birth level a **pocket**, with birth b and death D. Then f(w) = max(m_w, max{D : b ≤ m_w < D}), where m_w is the largest level ≤ w. The pairs (b, D) therefore carry all of the bounded-path data. On the 12 components of note 3's every-w run, this formula reproduces 3,048 of 3,048 values of f.
2. **Pockets need n ≥ 4 and are common from n = 5 on [I].** In rank 3 there are none (Theorem 3.1). At n = 4 they are rare: 7 pockets in 4 of 58 classes, all born at weight ≤ 8, all closing within 4 of their birth. At n = 5, 6 and 7, about half to two thirds of dense classes have pockets: 33 of 59, 28 of 40 and 20 of 30. Sparse classes (note 2's one-weight-3 trees) rarely have them (3 of 60), and when they do the ratio is ≤ 1.21.
3. **Most pockets are climbs, and greedy descent finds their barrier [I].** In 76 to 90 % of pockets at n ≥ 5, the lowest quiver is not a local minimum of total weight (the number of arrows). Greedy descent on total weight then leaves the pocket, and the highest maximal entry it passes through *equals the death level* in 229 of 245 such pockets at n = 5, 190 of 215 at n = 6 and 43 of 52 at n = 7. A climb is a quiver whose total weight can only fall if its maximal entry first rises, and the barrier is the height of that rise.
4. **The rest are traps: local minima of total weight that are not the class minimum [I].** These are exactly the quivers at which greedy descent is stuck: Fomin–Neville's non-confluence in concrete form. Every n = 4 pocket is a trap, and so are 28 of 273 pockets at n = 5, 32 of 247 at n = 6 and 16 of 68 at n = 7. No simple local rule found their barrier. Taking one mutation and then greedy descent gives it exactly in 33 of 83 traps and undershoots in the rest, because the descent falls back into a pocket.
5. **The barrier ratio is typically below 2 but not bounded by a small constant [I].** At n = 5 to 7, in every birth range, the 90th percentile of D/b lies between 1.33 and 2.0, with no trend in b. The maximum, however, is 3.63 at n = 6. At n = 5 it is 4.30 at bound 512 and 5.39 at bound 2,048, where a trap born at 166 dies at 895. The bound-2,048 run reaches births up to 512, and the distribution looks the same at every scale: D/b > 2 for 4 to 8 % of pockets and D/b > 3 for 0 to 1.4 % in every birth range. The far tail consists mostly of traps.
6. **Forks are a minority [I].** 21 of 273 pocket bottoms at n = 5 are Warkentin forks (89 of 607 at bound 2,048, where births are larger), 6 of 247 at n = 6, and none at n = 4 or 7. Most pockets live in Ervin's forkless part.
7. **For the wider question.** Problem E of note 3 §6 (thresholds) now has a precise form: describe the persistence diagram of the maximal-entry filtration. Climbs are explained by descent; traps are the hard core, and they are the same objects that block a descent algorithm. Conjecture A of note 3 §6 (a bound F(n, w) on the height of joining paths) is false with a linear F of constant near 2; at n = 5 a linear F would need a constant of at least 5.39. Whether any linear F(n, w) exists depends on the tail of the ratio distribution, which this sample cannot settle.

---

## 2. Persistence

**Setting.** Fix a class and work with quivers up to relabelling (canonical forms, note 3 §3.4). For a level L, X_L is the subgraph of quivers with maximal entry ≤ L. Process the levels in increasing order, adding the new quivers and the mutation edges among present quivers, with union–find. When an edge joins two components, the one with the higher birth level (the lowest maximal entry among its quivers) dies at the current level; ties go to the smaller component. Pairs with death equal to birth are discarded. What remains are the pockets, each with its birth b, death D, size at death, and lowest quiver.

**Why it carries f.** At ambient bound m_w (the largest level ≤ w), the components of S_w are exactly the components born at or below m_w and not yet dead. S_w becomes connected at the first level at which all of them have died, except the eldest. Hence

> f(w) = max( m_w, max{ D : b ≤ m_w < D } ).

This turns note 3's profile into a finite list of pairs, which is the natural object to study. The "thresholds" of note 2 are the pockets born at the class minimum level. Its "islands" are the components alive at a given level.

**Validation.** `pockets.py diagram --n 5 --B-big 512` on note 3's 12 n = 5 components gives pairs from which the formula reproduces all 3,048 values f(w), 3 ≤ w ≤ 256, of `bounded_profile_v2_allw_n5_unl.jsonl`.

**Visibility.** The enumeration is breadth-first inside the ambient bound B, so it is connected inside B by construction, and every death it reports is ≤ B and exact. A pocket that joins the class only above B is invisible (the caveat of note 2 §8.1). The statistics below therefore use only pockets born at ≤ B/4, for which any ratio up to 4 would be visible.

---

## 3. Census

Pockets born at ≤ B/4, over components exhausted at the ambient bound B (dense starts are note 2's, with entries in [−3, 3] and the seeds continued past note 2's trials):

| n | B | Components | With pockets | Pockets | Traps | Climbs: barrier = descent maximum | D/b median | D/b 90 % | D/b max | D − b max |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 4096 | 58 | 4 | 7 | 7 | – | 2.00 | 2.13 | 2.33 | 4 |
| 5 | 512 | 59 | 33 | 273 | 28 | 229 of 245 | 1.17 | 1.75 | 4.30 | 228 |
| 5 | 2048 | 46 (of the 59) | 33 | 607 | 76 | 491 of 531 | 1.10 | 1.66 | 5.39 | 1,434 |
| 6 | 128 | 40 | 28 | 247 | 32 | 190 of 215 | 1.17 | 1.65 | 3.63 | 79 |
| 7 | 48 | 30 | 20 | 68 | 16 | 43 of 52 | 1.21 | 1.51 | 2.33 | 6 |
| 5 sparse | 512 | 30 | 2 | 14 | 0 | 14 of 14 | 1.16 | 1.19 | 1.20 | 16 |
| 6 sparse | 128 | 30 | 1 | 56 | 0 | 56 of 56 | 1.12 | 1.15 | 1.21 | 6 |

By birth range at n = 5 (bound 512):

| Birth | Pockets | D/b median | D/b 90 % | D/b max | D − b max | Size median (max) |
|---|---|---|---|---|---|---|
| 1–8 | 25 | 1.33 | 2.00 | 2.50 | 6 | 2 (20) |
| 9–16 | 7 | 1.20 | 1.55 | 2.00 | 9 | 1 (3) |
| 17–32 | 31 | 1.12 | 1.53 | 1.90 | 18 | 2 (10) |
| 33–64 | 63 | 1.15 | 1.69 | 2.56 | 75 | 2 (8) |
| 65–128 | 147 | 1.15 | 1.79 | 4.30 | 228 | 2 (23) |

By birth range at n = 5, bound 2,048 (the 46 components of size ≤ 40,000 at bound 512, births ≤ 512):

| Birth | Pockets | D/b median | D/b 90 % | D/b max | D − b max | Share with D/b > 2 |
|---|---|---|---|---|---|---|
| 1–64 | 86 | 1.17 | 1.69 | 2.56 | 75 | 4.7 % |
| 65–128 | 90 | 1.15 | 1.94 | 4.30 | 228 | 7.8 % |
| 129–256 | 209 | 1.06 | 1.44 | 5.39 | 774 | 3.8 % |
| 257–512 | 222 | 1.10 | 1.69 | 4.69 | 1,434 | 5.9 % |

**Shape of a pocket [I].** Pockets are small: the median size at death is 1 or 2 quivers, and the largest seen is 25. The lowest quiver attains its maximal entry on a single arrow in 251 of 273 cases at n = 5 (199 of 247 at n = 6). It is a strict local minimum of the maximal entry, meaning every mutation raises the maximum, in 170 of 273 cases. The others have a neighbour at the same level inside the pocket. At n = 6 and 7 most pocket bottoms have a zero entry (147 of 247 and 61 of 68), so they are far from abundant.

---

## 4. Climbs and traps

**Climbs.** Let x be the lowest quiver of a pocket. If x is not a local minimum of total weight, some mutation lowers the total weight. Since x is a local minimum of the maximal entry, that mutation raises the maximum. Greedy descent on total weight from x is a path out of the pocket. If it ends in an older component, the death D is at most the highest maximal entry on that path. The data says it is usually exactly that:

| n | Climbs | Descent maximum = D | > D | < D (descent ends in another pocket) |
|---|---|---|---|---|
| 5 | 245 | 229 | 3 | 13 |
| 6 | 215 | 190 | 14 | 11 |
| 7 | 52 | 43 | 1 | 8 |
| sparse 5, 6 | 70 | 70 | 0 | 0 |

So a climb is a quiver whose total weight can only decrease after its maximal entry has gone up, and its barrier is the height of that detour. In rank 3 this cannot happen. There, a non-root cyclic quiver always has a move that lowers one weight and changes no other (Step 1 of Theorem 3.1), so lowering the total weight never raises the maximum. From n = 4 on, a mutation changes several entries at once and can trade a large decrease in some for an increase in the largest.

**Traps.** If x is a local minimum of total weight, greedy descent cannot start. Such an x is a local minimum of total weight other than the class minimum, which is exactly what makes descent algorithms non-confluent. Fomin–Neville show that descent cannot be confluent in general [P]; the traps are concrete instances, and they occur at weights as low as 3 at n = 4. The obvious local rule, one mutation and then greedy descent, gives the barrier exactly in only 4 of 7 traps at n = 4, 7 of 28 at n = 5, 14 of 32 at n = 6 and 8 of 16 at n = 7. In the other cases it gives a lower value, because the descent falls into another pocket. Trap barriers are the larger ones: the median ratio is 1.73 for traps against 1.17 overall at n = 5, and 1.44 against 1.17 at n = 6. At bound 2,048 traps are 76 of 607 pockets (13 %) but 20 of the 32 with ratio above 2, including the three largest (5.39, 4.97, 4.69).

**Example (n = 5, note 3's trial 11).** The quiver with rows (0, 33, 12, −48, 3), (−33, 0, 33, −15, −18), (−12, −33, 0, −5, 2), (48, 15, 5, 0, −4), (−3, 18, −2, 4, 0) has maximal entry 48 and total weight 173. Its five mutations have maximal entries 1,599, 1,101, 48, 189 and 87, and total weights 2,469, 2,347, 229, 435 and 183. So it is a local minimum of both. Its pocket holds 8 quivers and first meets the main island at maximal entry 123.

---

## 5. Is the barrier ratio bounded?

**Robustness.** For the 46 n = 5 components run at both bounds, the pairs with death ≤ 512 are identical at bounds 512 and 2,048 in all 46.

**A stationary distribution with a long tail [I].** Up to birth 512 at n = 5, the ratio D/b does not drift with b:

- the median stays at 1.06 to 1.17 and the 90th percentile at 1.44 to 1.94;
- the share above 2 stays at 4 to 8 %, and the share above 3 at 0 to 1.4 %.

What grows is the number of pockets. The mean number born at or below w, per class, is 1.9, 3.8, 8.4 and 13.2 for w = 64, 128, 256 and 512, roughly linear in w. The worst f(w)/w of a class up to weight W is therefore the maximum of a growing number of draws from what looks like a fixed distribution. If that distribution has bounded support, F(n, w) = c(n)·w holds, with c(5) ≥ 5.39. If its tail is unbounded, sup f(w)/w grows slowly with w.

The sample (607 pockets) cannot distinguish the two. The far tail consists mostly of traps, so the question is a question about trap barriers.

**Descent at larger weights.** The climb result holds at bound 2,048: the descent maximum equals the death in 491 of 531 climbs and never exceeds it. In the other 40, descent ends in another pocket.

---

## 6. What this does to the starting conjectures

The statements are those of [note 3](03-profile-correction-and-rank-3.md) §6.

- **Problem E** is now: describe the persistence diagram of the maximal-entry filtration of a mutation class (up to relabelling), in particular the tail of D/b. The census above is the first data. Climbs reduce to a local statement about descent. Traps are the core, and they connect the bounded-path question to Fomin–Neville's non-confluence.
- **Conjecture A.** F(n, w) = 2w fails at n = 5 and 6 (ratios 5.39 and 3.63). A linear F would need c(5) ≥ 5.39. The ratio distribution looks stationary in w, which a linear F needs, but its tail is unresolved and consists of traps.
- **A two-stage search [H].** Descend greedily on total weight from both quivers, then search with iterative deepening on the bound between the two end points. This is note 1's attack A3 with a descent prefix. Climbs then cost nothing, and the bound needed is set by the traps between the end points. A decision procedure would need a bound on trap barriers, which is the clean form of the open question.
- **Forks.** Warkentin's fork trees and Ervin's forkless part explain the part of the class where weights grow monotonically. Pockets lie almost entirely outside it, so the forkless part is where the bounded-path question lives.

---

## 7. Limitations

- Samples: 30 to 60 random components per n, n ≤ 7, entries in [−3, 3] at the start, ambient bounds 48 to 4096. Births are limited to B/4: ≤ 12 at n = 7, ≤ 32 at n = 6.
- The ratio maximum is a statistic of a growing sample. More components produce larger maxima even if the distribution is fixed, so the 90th percentile is the better summary of the trend.
- "Descent maximum = D" is measured, not proved. The cases where descent overshoots (14 at n = 6) show that greedy descent is not always the cheapest way out.
- Invisible pockets, those joining only above B, are excluded by construction. Restricting births to B/4 makes any ratio up to 4 visible, but not larger ones.

---

## 8. Reproduce

```bash
PY=python
$PY -I pockets.py diagram --n 5 --B-big 512 --trials 60 --workers 8 --seed 20261208 --out pockets_n5_B512.jsonl
$PY -I pockets.py diagram --n 4 --B-big 4096 --trials 60 --workers 8 --seed 20261108 --out pockets_n4_B4096.jsonl
$PY -I pockets.py diagram --n 6 --B-big 128 --trials 40 --workers 8 --seed 20261308 --out pockets_n6_B128.jsonl
$PY -I pockets.py diagram --n 7 --B-big 48 --trials 30 --workers 8 --seed 20261408 --out pockets_n7_B48.jsonl
$PY -I pockets.py diagram --n 5 --B-big 512 --trials 30 --workers 8 --seed 20261508 --sparse --out pockets_sparse_n5_B512.jsonl
$PY -I pockets.py diagram --n 6 --B-big 128 --trials 30 --workers 8 --seed 20261608 --sparse --out pockets_sparse_n6_B128.jsonl
# bound 2048 on the 46 n = 5 components of size <= 40,000 at bound 512
$PY -I pockets.py diagram --n 5 --B-big 2048 --trials 60 --only 1 2 3 4 5 6 8 9 10 11 12 13 14 16 17 19 20 21 22 24 25 26 28 29 30 32 33 34 36 39 40 41 42 43 44 45 46 47 48 50 51 54 55 56 57 59 --budget 3000000 --workers 8 --seed 20261208 --out pockets_n5_B2048.jsonl
$PY -I pockets.py summarize pockets_n4_B4096.jsonl pockets_n5_B512.jsonl pockets_n6_B128.jsonl pockets_n7_B48.jsonl pockets_sparse_n5_B512.jsonl pockets_sparse_n6_B128.jsonl --frac 4
```

`diagram` overwrites its output unless `--append` is given. The first trials of each dense set are note 2's components (same seeds).

---

## Sources

- Fomin, Neville, *Long mutation cycles* (non-confluence of descent): https://arxiv.org/abs/2304.11505
- Warkentin, *Exchange graphs via quiver mutation*, PhD thesis, TU Chemnitz 2014 (forks): https://d-nb.info/1214302807/34; Ervin, forkless part: https://arxiv.org/abs/2306.07502
- Edelsbrunner, Harer, *Computational Topology* (0-dimensional persistence, the elder rule) [standard].
- Notes 1, 2 and 3 of this repository.
