# Notes

The detailed arguments, computations and checks behind the paper ([../paper/mutation-barriers.pdf](../paper/mutation-barriers.pdf)). The notes are in the order in which the work was done, so a note may be corrected by a later one; such corrections are quoted at the top of the note they correct, and in place. Each note states what it builds on, labels every statement by its evidence, lists its limitations, and ends with a *Reproduce* section (commands run from `experiments/` with `python -I`) and its sources.

Evidence labels used in the notes: **[P]** proven in a cited source; **[I]** derived or measured in this work; **[H]** heuristic. The article and the README use a coarser, result-level labelling (proved by hand / computer-assisted proof / computational / conjecture); [../../CLAIMS.md](../../CLAIMS.md) gives it for every claim of the article. A statement headed "Theorem" in a note may be an exhaustive computation over a stated range or a computer-assisted proof; the bracket after its number says which ("[I, by exhaustive computation]", "[I, computer-assisted]"). Where a note and the paper differ in what they call a result or in how firmly they state it, the paper and the article are the later reading; the cases found are listed in [../../CLAIMS.md](../../CLAIMS.md#known-discrepancies).

**Who wrote and checked these notes.** The notes, the code and the checks were produced with extensive help from AI tools, and no human has read them as a mathematician would. Notes 12, 17, 19 and 23 are checks of earlier notes: each was made separately from the notes it checks, starting from their statements, with new code (in `verify/`), by a fresh instance of the same AI model. They are part of this work, not an outside review and not a specialist's reading.

**Reading order.** For the barriers alone: notes 9, 15 (§4–5), 16, 18, then the checks 12 (§4), 17, 19 and 23. For the census and Conjecture 5.5: notes 7, 8, 10, 13. For cores and tubes: notes 14 and 22. Notes 1 to 6 are the path that led to the question: the failed one-way function, a measurement error and its correction, pockets and traps.

| Note | Topic | Scripts |
|---|---|---|
| **How the question arose** | | |
| [1](01-mutation-path-test.md) | A planted mutation-path one-way function, tested and killed | `mutation_path.py` |
| [2](02-bounded-paths.md) | The bounded-path conjecture, measured (its staircase is corrected in note 3) | `bounded_paths.py` |
| [3](03-profile-correction-and-rank-3.md) | Note 2's staircase was a measurement error; quivers must be compared up to relabelling; rank 3 is settled (Theorem 3.1) | `bounded_paths.py`, `rank3_paths.py` |
| [4](04-pockets.md) | Pockets: persistence of the height filtration | `pockets.py` |
| [5](05-traps.md) | Traps: local minima of total weight and their escape heights | `traps.py` |
| [6](06-trap-hunt.md) | Hunting for traps with large escape ratios | `hunt.py` |
| **Four vertices** | | |
| [7](07-n4-exhaustive.md) | Every 4-vertex quiver up to a bound: pockets are born at every height | `n4_all.py`, `n4_family.py`, `n4_plateaus.py` |
| [8](08-n4-ratio.md) | The barrier ratio class by class: the census, least heights up to 7 | `n4_classes.py` |
| [9](09-n4-mirror-family.md) | **G_k**: f(Q, w)/w is unbounded on 4 vertices (Theorem 9.1; hand proof in note 12 §4) | `n4_mirror.py`, `n4_mirror_proof.py` |
| [10](10-n4-quadratic-bound.md) | Is F(4, w) ≤ 2w²? The census completed to least height 9 (Conjecture 10.1) | `n4_classes.py`, `n4_block_scan.py` |
| [11](11-n4-invariants-descent-joins.md) | The visibility caveat of the census, descent, and the shape of the worst joins | `n4_evidence.py` |
| [12](12-checks-of-notes-03-to-10.md) | Checks of notes 3 to 10; the hand proof for G_k and its extension to n ≥ 4 (Proposition 12.1) | `verify/review12.py` |
| [13](13-conjecture-5-5-up-to-height-18.md) | **Conjecture 5.5 of arXiv 2610.36179** on every 4-vertex quiver of height ≤ 18 | `n4_conj55.py` |
| [14](14-opposite-quivers-forks-and-cores.md) | When is a quiver equivalent to its opposite? **Forks, cores**, mirror pairs, first tube certificates | `n4_opposite.py`, `n4_opposite_run.py`, `n4_opposite_gk.py`, `n4_opposite_tubes.py` |
| [15](15-rank-2-orbits-and-the-constant-2.md) | **R_b and Q_t**: the constant 2 is sharp (Theorems 15.6, 15.13); orbits of two mutations; fork exclusion (Lemma 15.5) | `n4_doors.py`, `n4_doors_readable.py` |
| [22](22-tube-lemma-and-its-limits.md) | **The tube lemma**, second-pass certificates, and the Markov quiver with a pendant arrow (Theorem 22.7) | `n4_tube_lemma.py` |
| **Five vertices** | | |
| [16](16-five-vertices-above-w-squared.md) | **P⁺_t**: F(5, w) ≥ 2w^{5/2} − 11w² (Theorems 16.4–16.6) | `np_corridor.py`, `np_barrier.c`, `np_corridor_prove.py`, `np_corridor_members.py` |
| [17](17-checks-of-note-16.md) | Checks of note 16 | `verify/review17.py` |
| [18](18-five-vertices-cubic-barrier.md) | **Q_a**: a fifth vertex over a bounce cycle, barriers of order w³ (Theorem 18.4, Conjecture 18.7) | `np_rowwalk.py` |
| [20](20-core-of-the-cubic-family.md) | The region of Q_a below its barrier: lines, branches, spirals; no lower route for a ≤ 64 | `np_qa_core.py`, `np_qa_core.c` |
| **Checks, and the attacker** | | |
| [19](19-checks-of-notes-13-to-16.md) | Checks of notes 13, 14, 15 and 16 | `verify/review19*.py` |
| [21](21-barriers-and-the-mutation-path-owf.md) | The barriers do not reopen the one-way function | `owf_barrier.py` |
| [23](23-checks-of-notes-20-to-22.md) | Checks of notes 20, 21 and 22 | `verify/review23*.py`, two C programs |

**Numbering of statements.** A statement numbered N.k (Theorem 15.13, Lemma 16.1, Conjecture 18.7) is statement k of note N. The paper and the article number their statements independently; [../../CLAIMS.md](../../CLAIMS.md) gives the correspondence. Statements of cited papers keep the numbers of their papers, and two cases need care. In notes 12 to 15, Fomin and Neville's paper has its own Lemma 12.5, Definition 13.1, Definition 14.1, Theorem 14.3 and Theorem 15.7; in the notes these are written "Fomin–Neville Lemma 12.5" and so on (in script comments they appear with the arXiv number or as "FN"). And Theorem 5.1, Corollary 5.2 and Conjecture 5.5 always belong to arXiv 2610.36179, while note 5 states Conjecture 5.1 and Problem 5.2. Notes 1 and 2 have no numbered statements.

**Not here.** Notes 1, 2 and 21 refer to an earlier survey of candidate one-way functions, a working document of a wider project that is not included; nothing in the results depends on it. The papers cited are not included.
