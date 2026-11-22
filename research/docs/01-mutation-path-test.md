# 1. The planted mutation-path one-way function, tested and killed

*Run on 2026-11-08. This is the experiment proposed in an earlier survey of candidate one-way functions (a wider project's working document, not included here) §3.2. Code: [experiments/mutation_path.py](../experiments/mutation_path.py). Results: `mutation_path.jsonl` (random-walk grid), `mutation_deepest.jsonl` (adversarial planting at the public bound), `mutation_corridor.jsonl` (adversarial planting inside a small bound), `mutation_component.jsonl` (bounded component sizes), `mutation_growth.json` (entry growth), `mutation_failed_recheck.jsonl`, and the matching `*.log` files. Labels: **[P]** proven in a cited source; **[I]** my own argument or measurement; **[H]** heuristic.*

---

## 1. Answer

**The mutation-path one-way function is dead, for a structural reason that does not depend on toy sizes.** Every planted instance was inverted: 1,080 of 1,080 random-walk instances, 60 of 60 adversarially planted instances at the public bound, and 30 of 30 adversarially planted instances inside a small bound. Median inversion time was 0.3 s; the slowest took 57 s.

The reason is a trade-off forced by quiver mutation itself [I, measured]:

- **Growth is doubly exponential.** Along an unrestricted random walk the largest entry squares roughly every three steps. The number of steps before an entry exceeds 2^(2^k) is about 1, 3, 5, 8, 11, 14 for k = 1, …, 6, independent of the number of vertices. So an entry bound B permits only O(log log B) weight-increasing steps.
- **Bushy is shallow; deep is thin.** Near a low-weight quiver almost every mutation stays inside a large bound, so the ball grows at branching about n − 1, but it is exhausted in depth 7 to 11. Deep paths exist only where mutations do not increase weight, and there the branching inside the bound is 1.1 to 1.9. Neither regime is expensive to search: a bushy ball of radius 10 is at most (n − 1)^10 states, and a thin corridor is searched in time linear in its length.
- **Deep paths live inside small bounds.** Every long path found stayed inside entries ≤ 16 or ≤ 256 even when the public bound was 2^30. An attacker who searches at bounds 4, 16, 64, … in turn (iterative deepening on the bound) finds the shortest path at the first bound that connects the endpoints. In the corridor test this recovered exact shortest paths of length 129, 66, 51 and 49 in under 1.5 s each, where plain bidirectional search at the public bound had failed with a million states.
- **No asymmetry.** In all 30 corridor instances the planter, which had to search the bounded component to find a deep quiver, expanded more states than the attacker needed to invert. A one-way function whose forward direction costs more than its inverse is not one.

The design has two knobs, the bound B and the path length L, and they are coupled against the designer: depth requires low weight, low weight means a small searchable component, and high weight means a shallow ball. Random-walk sampling does not even reach the deep regime: non-backtracking bounded walks die after about ten steps at every bound tested, and 100-step walks with backtracking end a median of 14 mutations from the start.

---

## 2. Set-up

**Instances.** Quivers are skew-symmetric integer matrices on n ∈ {6, 8, 10, 12} vertices. The start Q is random, connected, with entries in [−3, 3] and at least one entry of absolute value 3, which guarantees an infinite mutation class for n ≥ 3 **[P]** (mutation-finite quivers have all weights ≤ 2). The secret is a mutation sequence with no immediate repeats; every intermediate quiver has entries bounded by B ∈ {4, 16, 256, 2^16, 2^30}. Public data: Q, Q′, n, B. The attacker must output any mutation sequence from Q to Q′ inside the bound; outputs were verified by replay.

**Planting strategies.**

- `uniform`: random allowed vertex at each step; stop if every vertex would exceed the bound.
- `cyclic`: as above, preferring vertices that are not sinks or sources (a designer avoiding orientation-only moves).
- `backtrack`: as `uniform`, but step back along the previous edge instead of stopping, so the walk always has length L ∈ {10, 30, 100}.
- `deepest`: adversarial. Breadth-first search inside a planting bound (300k or 1M states), then take a random quiver at the maximal depth reached. In the corridor test the planting bound (16 or 256) is smaller than the public bound (2^30).

**Attacks.** The attacker sees only Q, Q′, n, B.

- **A0**, component size: BFS from Q inside the bound, with a node budget, to measure how much there is to search.
- **A1**, bidirectional BFS inside the bound, expanding the smaller frontier, node budget 200k (grid) or 1M (adversarial).
- **A2**, greedy steepest descent on total arrow weight from both ends, then A1 between the two local minima.
- **A3**, iterative deepening on the bound: A1 at B′ = 4, then 16, 64, …, up to B, with a per-level budget (100k or 300k).

Not implemented, because not needed: g-vector or framing reconstruction, tropical linearisation, and invariant-based pruning.

**Sizes.** 1,080 random-walk instances (n × B × L × 3 strategies × 8 trials), 60 adversarial instances at the public bound, 30 corridor instances, 45 component measurements, 600 growth walks. All runs together took under ten minutes on 8 cores.

---

## 3. Results

### 3.1 Entry growth along unrestricted walks (200 walks per n, 40 steps)

| Threshold | n = 6 | n = 8 | n = 10 |
|---|---|---|---|
| Median steps until some entry exceeds 2^2 | 1 | 1 | 1 |
| 2^4 | 3 | 3 | 3 |
| 2^8 | 6 | 5 | 5 |
| 2^16 | 8 | 8 | 8 |
| 2^30 | 11 | 11 | 11 |
| 2^64 | 14 | 14 | 15 |

Each column fits "about 2.7 steps per doubling of the bit length". Every walk exceeded 2^64 within 40 steps.

### 3.2 Bounded components (BFS from Q, budget 10^6 states, 3 random Q per cell)

| n | B | Component size | Depth reached | Branching ratio of the frontier near the end |
|---|---|---|---|---|
| 6 | 4 | 1, 2, 27k (all exhausted) | 0 to 47 | — |
| 6 | 16 | 3k, 33k, 323k (all exhausted) | 23 to 49 | — |
| 6 | 256 | 239k (exhausted, depth **129**), > 10^6, > 10^6 | 11 to 129 | 1.2 to 3.1 |
| 6 | 2^16, 2^30 | > 10^6 | 9 to 11 | 3.0 to 4.7 (of n − 1 = 5) |
| 8 | 16 | 847k (exhausted), > 10^6, > 10^6 | 25 to 37 | 1.1 to 1.3 |
| 8 | 256 | > 10^6 | 11 to 13 | 1.7 to 2.3 |
| 8 | 2^16, 2^30 | > 10^6 | 8 | 6.4 to 6.9 (of 7) |
| 10 | 4 | 1 (all three) | 0 | — |
| 10 | 16 | > 10^6 | 16 to 27 | 1.1 to 1.9 |
| 10 | 256 | > 10^6 | 8 to 9 | 2.6 to 4.1 |
| 10 | 2^16, 2^30 | > 10^6 | 7 | 7.4 to 8.8 (of 9) |

The two regimes are visible directly: at small bounds the component is thin and deep; at large bounds the first seven to ten levels grow almost freely and the budget is spent before the bound bites.

### 3.3 Random-walk grid (1,080 instances, attacks A1 and A2 with 200k nodes each)

| n | B | Instances | Inverted | Non-backtracking walks stuck | Their median length | Median shortest distance found | Max distance found | Median A1 nodes | Median time |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 4 | 72 | 72 | 65% | 5 | 2 | 36 | 3 | < 0.01 s |
| 6 | 16 | 72 | 72 | 83% | 7 | 5.5 | 18 | 28 | 0.44 s |
| 6 | 256 | 72 | 72 | 79% | 8 | 6.5 | 22 | 50 | 0.48 s |
| 6 | 2^16 | 72 | 72 | 83% | 10 | 9 | 100 | 137 | 0.25 s |
| 6 | 2^30 | 72 | 72 | 69% | 10 | 10 | 100 | 388 | 0.28 s |
| 8 | 16 | 72 | 72 | 81% | 8 | 7 | 24 | 72 | 0.86 s |
| 8 | 256 | 72 | 72 | 81% | 10 | 8 | 20 | 92 | 0.57 s |
| 8 | 2^16 | 72 | 72 | 77% | 10 | 10 | 100 | 498 | 0.27 s |
| 8 | 2^30 | 72 | 72 | 65% | 11 | 11 | 100 | 1,698 | 0.28 s |
| 10 | 16 | 72 | 71 (72 after recheck) | 77% | 10 | 8 | 34 | 148 | 0.95 s |
| 10 | 256 | 72 | 72 | 81% | 10 | 9 | 18 | 136 | 0.50 s |
| 10 | 2^16 | 72 | 72 | 73% | 10 | 10 | 100 | 936 | 0.26 s |
| 10 | 2^30 | 72 | 72 | 65% | 11 | 11.5 | 100 | 7,398 | 0.27 s |

(The n = 8 and n = 10 rows for B = 4 are omitted: the component is almost always a single quiver.)

- **Walks die.** Without backtracking, 65 to 83 % of walks stopped before reaching L because every other vertex would exceed the bound, after a median of 5 to 11 steps that barely grows with B. This matches §3.1.
- **Backtracking walks fold back.** Over all n and B ≥ 16, 100-step backtracking walks ended at a median shortest distance of 14 (L = 30: 10; L = 10: 8). The maximum of 100 occurred in thin high-weight corridors, where bidirectional BFS found the full path with at most 464k nodes because the branching inside the bound was about 1.
- **The one failure** (n = 10, B = 16, backtrack, L = 100) was a budget artifact. Re-attacked with 1.5M nodes: shortest distance 34, found by A1 in 18 s and by A3 at B′ = 16 with the same cost.
- **Descent.** A2 inverted 1,077 of 1,080 within budget. The two descents landed on the same local minimum in 26 to 64 of 72 instances per cell, more often at large B; otherwise BFS between minima needed a few hundred nodes.

### 3.4 Adversarial planting at the public bound (60 instances, planting budget 300k states, attack budget 10^6)

| n | B | Planted depth | A1 inverted | Median A1 nodes | A2 inverted | Median time |
|---|---|---|---|---|---|---|
| 6 | 256 | 12 to 25 | 5/5 | 3,253 | 5/5 | 2.9 s |
| 6 | 2^16 | 9 | 5/5 | 352 | 5/5 | 1.5 s |
| 6 | 2^30 | 8 to 9 | 5/5 | 366 | 5/5 | 1.2 s |
| 8 | 256 | 8 to 10 | 5/5 | 172 | 5/5 | 2.2 s |
| 8 | 2^16, 2^30 | 7 | 10/10 | 309 to 1,342 | 10/10 | ≤ 1.1 s |
| 10 | 256 | 7 to 10 | 5/5 | 419 | 5/5 | 2.4 s |
| 10 | 2^16, 2^30 | 6 | 10/10 | 391 to 1,132 | 10/10 | ≤ 1.0 s |
| 12 | 256 | 7 to 8 | 5/5 | 275 | 5/5 | 2.3 s |
| 12 | 2^16, 2^30 | 6 | 10/10 | 483 to 1,880 | 10/10 | ≤ 1.0 s |

A breadth-first planter with 300k states cannot get deeper than 6 to 9 at large bounds, because the ball is bushy. The planted quivers had weights up to 2.4·10^7; descent brought them back to weight 20 to 130 and, in most cases, to the same minimum as Q.

### 3.5 The corridor test: deep planting inside a small bound, attack at B = 2^30 (30 instances)

| n | Planting bound | Planted depth | A1 at the public bound | A2 | **A3 iterative deepening** | A3 bound found | Max A3 nodes | Max A3 time |
|---|---|---|---|---|---|---|---|---|
| 6 | 16 | 23 to 49 | 3/5 | 3/5 | **5/5** | 16 | 37,959 | 0.4 s |
| 6 | 256 | 11 to **129** | 3/5 | 5/5 | **5/5** | 64 to 256 | 14,184 | 0.1 s |
| 8 | 16 | 13 to 51 | 1/5 | 2/5 | **5/5** | 16 | 92,206 | 1.5 s |
| 8 | 256 | 9 to 12 | 5/5 | 5/5 | **5/5** | 64 to 256 | 2,826 | < 0.1 s |
| 10 | 16 | 15 to 33 | 0/5 | 1/5 | **5/5** | 16 | 64,570 | 1.0 s |
| 10 | 256 | 9 to 12 | 5/5 | 5/5 | **5/5** | 64 to 256 | 1,991 | < 0.1 s |

- A1 at the public bound fails in 14 of 30 within a million states, exactly where the planted depth exceeds about 15: the frontier at B = 2^30 grows at about n − 1 per level.
- A3 recovers the **exact shortest path** (its length equals the planted depth) in all 30, at the planting bound or below, with at most 92k nodes.
- **Planting cost exceeded inversion cost in all 30 instances.** The planter expanded 188 to 10^6 states; A3 expanded 144 to 92k. The ratio was typically 10 to 1,000.

---

## 4. Interpretation

1. **The two knobs are coupled against the designer [I].** Depth needs non-growing steps, which exist only in low-weight regions, which are searchable. Width needs growing steps, which are limited to O(log log B). So the bounded exchange graph is a low-weight core, searchable by deepening on the bound, decorated with shallow bushy balls and thin corridors. No parameter choice gives both depth and width.
2. **Random sampling cannot even reach the hard-looking regime.** Honest parties sampling by random walk get distance about 14 after 100 steps. A planter who wants depth must search, and the search costs more than the inversion.
3. **The tropical and g-vector attacks were not needed.** Generic graph search with one idea, deepening on the bound, suffices at these sizes. The survey's risks 1 and 2 (entry growth, tropical structure) were the right diagnosis; risk 1 alone was fatal.
4. **What this does not settle [H].** The only regime not reached is a large-n, permanently low-weight one: n ≥ 20 with entries ≤ 16 throughout, where the bounded component could have 2^128 or more states and wide frontiers, so that generic meet-in-the-middle costs 2^64 or more. In that regime the problem is "navigate the bounded-weight mutation graph of a large wild quiver", which is close to the open complexity questions on mutation equivalence (Soukup; Neville). Three things argue against it: honest sampling still cannot produce deep instances there (the stuck rates in §3.3 are flat in n); weight ≤ 2 is the mutation-finite world, which is classified and easy, so any hardness would have to live in the narrow band of weights 3 to 16; and nothing is known about descent or canonical forms in that band. It is a mathematics question, not a cryptographic lead.

> **Follow-up (note 2):** The bounded-path property suggested here was measured exactly on 37 exhausted components (n = 4, 5, 6) and on 170 forced excursions: f(Q, w) = max(w, w*(Q)) + ε with a threshold w* ≤ 24 and ε usually 0, mostly ≤ 2, ε/w → 0; excursions are spikes. See [note 2](02-bounded-paths.md).
>
> **Correction (note 3):** Note 2's f values were overstated by a flaw in its profile code. Corrected and taken up to relabelling, f(Q, w) ≤ w at n = 4. At n ≥ 5, small pockets push f above w in about a quarter of (component, w) pairs, by up to a factor 2.6. Excursions are still spikes. See [note 3](03-profile-correction-and-rank-3.md).
>
> **Follow-up (note 21):** The barriers of notes 15, 16 and 18 do not reopen this function. Planted pairs (Q, −Q) over the barriers of R_b, Q_t, P⁺_t and Q_a have literal routes about as long as the barrier, and the routes get no shorter at any higher bound. So iterative deepening costs 1.5 to 2 times the planter's route for R_b, Q_t and P⁺_t, and about its 5/3 power for Q_a. Compressing the route, the only way to make planting cheap, uses the same linear counters that a structure-aware attacker follows: it inverted every family member it was given, up to w = 2^{128}, in under 0.05 s. Random rows over the bounce cycle, perturbations, random walks inside the bound and climbs into the forks plant nothing harder. See [note 21](21-barriers-and-the-mutation-path-owf.md).

---

## 5. Where this leaves the survey

| Survey item | Status after this experiment |
|---|---|
| §3.2 mutation-path one-way function | **Dead** at toy sizes for structural reasons (growth, coupling of B and L, deepening attack, no forward/inverse asymmetry). Only the large-n low-weight band is unexamined, and it is not reachable by honest random sampling |
| §3.1 template gap | Still valid as a critique of the earlier candidates, but the one candidate it revived is gone |
| §3.7 structure 6 (piecewise-linear dynamics) | The experiment shows why: the dynamics has a potential (total weight) that both constrains honest walks and guides the attacker |

The wider project's verdict stands with one more candidate closed. The lasting output of this note is a precise description of bounded mutation graphs of wild quivers (thin deep cores, shallow bushy balls, doubly exponential growth), which may be of independent interest for the complexity of mutation equivalence.

---

## 6. Limitations

- n ≤ 12, B ≤ 2^30 (int64 safety: products of two entries must fit). The large-n low-weight regime of §4.4 was not reached.
- Starting quivers are dense with entries in [−3, 3]. Sparse starts with one heavy edge, or starts chosen deep inside a component, were not tested; the structural argument covers them but the numbers do not.
- The adversarial planter uses BFS. A depth-first planter would find deep quivers more cheaply, which would weaken the "planting costs more than inversion" statement but not the inversion costs.
- Budgets were 200k to 1.5M states. All failures of A1 and A2 were budget failures; A3 never failed.
- Branching ratios in §3.2 are frontier ratios inside a budget, not asymptotic growth rates.

## 7. Reproduce

```bash
PY=python
$PY -I mutation_path.py growth --n 6 8 10 --walks 200 --steps 40 --log2-thresholds 2 4 8 16 30 64 --out mutation_growth.json
$PY -I mutation_path.py component --n 6 8 10 --B 4 16 256 65536 1073741824 --trials 3 --budget 1000000 --workers 4 --out mutation_component.jsonl
$PY -I mutation_path.py grid --n 6 8 10 --B 4 16 256 65536 1073741824 --L 10 30 100 --strategies uniform cyclic backtrack --trials 8 --comp-budget 50000 --bfs-budget 200000 --workers 8 --out mutation_path.jsonl
$PY -I mutation_path.py grid --n 6 8 10 12 --B 256 65536 1073741824 --L 0 --strategies deepest --trials 5 --comp-budget 300000 --bfs-budget 1000000 --workers 6 --seed 20261110 --out mutation_deepest.jsonl
$PY -I mutation_path.py grid --n 6 8 10 --B 1073741824 --plant-bound 16 256 --L 0 --strategies deepest --trials 5 --comp-budget 1000000 --bfs-budget 1000000 --a3-budget 300000 --workers 6 --seed 20261111 --out mutation_corridor.jsonl
$PY -I mutation_path.py grid --n 10 --B 16 --L 100 --strategies backtrack --trials 1 --seed 20261964 --comp-budget 1000 --bfs-budget 1500000 --a3-budget 1500000 --workers 1 --out mutation_failed_recheck.jsonl
$PY -I mutation_path.py summarize mutation_path.jsonl
```

The first grid run predates the A3 attack and the `plant_bound` field, so its rows lack `a3_*` keys; `summarize` tolerates that. `grid` overwrites its output unless `--append` is given.

## Sources

- Felikson, Shapiro, Tumarkin, *Skew-symmetric cluster algebras of finite mutation type* (weights ≤ 2 characterisation) [M, recalled]
- Soukup, *Complexity of quiver mutation equivalence*: https://arxiv.org/abs/2306.03232
- Neville, *Long mutation cycles*: https://www.arxiv.org/pdf/2304.11505v1
