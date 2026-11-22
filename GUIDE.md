# Guide: mirror barriers in quiver mutation

The full reference for [the README](README.md): status, results, headline numbers, limits, tasks, layout and reproduction.

*How high must a mutation path between two quivers of small height climb? Notes, code and stored results behind the draft paper [research/paper/mutation-barriers.pdf](research/paper/mutation-barriers.pdf) and the article "How High Must a Mutation Path Climb?" (TODO-ARTICLE-URL).*

> **Status of these results.** Everything here was produced with extensive help from AI tools. The proofs and computations were rechecked by fresh instances of the same AI model, mostly with separately written code (some certificates were rerun rather than reimplemented, and some ranges rest on a single program), but **no human has read the paper**, and no specialist has checked a single argument. Each result is labelled by how it is supported: **proved by hand**; a **computer-assisted proof**, which covers every value of the parameters, with a program checking finitely many polynomial identities and inequalities; **computational**, meaning an exhaustive check over a stated range and nothing beyond it; or **conjecture**. Nobody should cite these results as established until a mathematician has read them.

**Start here:** `python3 -I research/verify/smoke.py` recomputes the headline numbers below from the definition of mutation in about 15 seconds, with the standard library only and without the data archive. `make smoke` computes the same numbers as tasks under a scheduler and prints the [table below](#headline-numbers-recomputed). Then [CLAIMS.md](CLAIMS.md) maps every claim of the article to a script, a stored output and a command, and says what has been run again here.

## The question

A quiver here is a skew-symmetric integer matrix; its *height* is its largest entry in absolute value. Mutation at a vertex is the move of Fomin and Zelevinsky's cluster algebras. Two quivers are compared up to relabelling of the vertices. A *route* is a sequence of mutations, and its height is the largest height of a quiver on it. For a quiver Q and w ≥ 0, let f(Q, w) be the least L ≥ w such that any two quivers of height at most w in the mutation class of Q are joined by a route of height at most L, and let F(n, w) be the largest f(Q, w) over quivers on n vertices. Whether two quivers are mutation-equivalent is not known to be decidable for four or more vertices, and a computable bound on F(n, w) would decide it.

The question arose from a failed attempt to build a one-way function from mutation paths ([note 1](research/docs/01-mutation-path-test.md), [note 21](research/docs/21-barriers-and-the-mutation-path-owf.md)).

## The answer

No upper bound on F(n, w) was found for n ≥ 4. What was found are lower bounds: quivers Q that reach their opposite −Q, but only far above the height of both. The running example is R₈ = (−8, −8, 7, −2, 6, −8), of height 8: it reaches −R₈ in 37 mutations, and by no route below height 101. At height 8 there is a ladder: 56 on four vertices (proved by hand), 101 on four vertices (computer-assisted proof), 1,242 on five vertices (exhaustive search).

## Main results

The rows are those of the article's status table, with its labels. "Paper" numbers refer to [research/paper/mutation-barriers.pdf](research/paper/mutation-barriers.pdf); the article numbers its statements differently, and [CLAIMS.md](CLAIMS.md) gives both.

| Result | Statement | Support | Note | Certificate or data |
|---|---|---|---|---|
| G_k (article Thm 5.1) | G_k is joined to −G_k at exactly k(k − 1); F(n, w) ≥ w(w − 1) for n ≥ 4 | proof by hand | [9](research/docs/09-n4-mirror-family.md), [12](research/docs/12-checks-of-notes-03-to-10.md) §4 | `research/verify/smoke.py`; `review12_handproof.log` |
| R_b (Thm 7.2) | R_b is joined to −R_b at exactly 2b² − 3b − 3, even b ≥ 6 | route by hand; lower bound computer-assisted (30 claims) | [15](research/docs/15-rank-2-orbits-and-the-constant-2.md) §5 | `n4_doors_prove2.log`, written out in `n4_doors_prove2_readable.log` |
| Q_t (Section 7) | Q_t is joined to −Q_t at exactly 2t⁴ − t³ − t² + 2t, t ≥ 3 | computer-assisted (43 claims) | [15](research/docs/15-rank-2-orbits-and-the-constant-2.md) §5 | `n4_doors_prove.log`, `n4_doors_prove_readable.log` |
| Remark 8.1 | F(4, w) ≤ 2w² | conjecture; census evidence up to w = 9 | [10](research/docs/10-n4-quadratic-bound.md), [11](research/docs/11-n4-invariants-descent-joins.md) | `n4_classes_*.jsonl*` |
| P⁺_t (Thm 9.1) | P⁺_t is joined to −P⁺_t at 2t⁵ − t⁴ + t² − 1; F(5, w) ≥ 2w^{5/2} − 11w² | route by hand; search for t ≤ 80; certificate for t ≥ 8 | [16](research/docs/16-five-vertices-above-w-squared.md), [17](research/docs/17-checks-of-note-16.md) | `np_corridor_prove.log`; the member families in `np_corridor_members.log` |
| Q_a route (Thm 10.1) | a route from Q_a to −Q_a of height 4a³ − 3a² + O(a) | derived by hand, printed as a sketch; replayed for a ≤ 48 | [18](research/docs/18-five-vertices-cubic-barrier.md) §5 | `np_rowwalk_family*.log` |
| Prop 10.2 | no lower route; F(5, w) ≥ 4w³ − O(w²) | computational, w ≤ 65; conjectured beyond | [18](research/docs/18-five-vertices-cubic-barrier.md), [20](research/docs/20-core-of-the-cubic-family.md) | `np_qa_core_family*.jsonl` |
| Prop 12.1 | Conjecture 5.5 of Armstrong-Williams, Hirst, Jackson and Lee | computational, height ≤ 18, resting on cited theorems | [13](research/docs/13-conjecture-5-5-up-to-height-18.md) | `n4_conj55_N18_summary.log` |
| Section 13 | 785,198 of 788,026 census classes decided | computational, certificates not stored | [14](research/docs/14-opposite-quivers-forks-and-cores.md), [22](research/docs/22-tube-lemma-and-its-limits.md) | `review23_n22_counts.log`; a regenerated sample of 5,353 certificates |
| Thm 13.2 | the Markov quiver with a pendant arrow has no tube certificate | proof by hand | [22](research/docs/22-tube-lemma-and-its-limits.md) §5 | `n4_tube_markov.log` (cuts only) |

File names without a directory are stored results; they are in the data archive ([data/README.md](data/README.md)), not in git.

## Headline numbers, recomputed

`make smoke` runs the batch [data/batches/smoke.toml](data/batches/smoke.toml): 66 tasks, about ten seconds on four processes, with the standard library only and without the data archive. Each row is one quantity of one task: the value the article states, and what the task computed in its latest record in [data/records/](data/records/). `make smoke` ends by printing this table from its own fresh run, and fails if it is not the table printed here.

<!-- BEGIN GENERATED headline: src/bookkeeping/claims.py tables -->
| Quantity | Predicted | Computed | Status | Task |
|---|---|---|---|---|
| G₈ and −G₈ are joined at height | 56 | 56 | ok | `barrier/G/k=8` |
| R₈ and −R₈ are joined at height | 101 | 101 | ok | `barrier/R/b=8` |
| quivers reached from R₈ below 101, up to relabelling | 35 | 35 | ok | `reach/R/b=8` |
| mutations on the route from R₈ to −R₈ | 37 | 37 | ok | `route/R/b=8` |
| quivers at height 101 on that route | 28 | 28 | ok | `route/R/b=8` |
| Q₃ and −Q₃ are joined at height | 132 | 132 | ok | `barrier/Qt/t=3` |
| P⁺₃ (height 9) and −P⁺₃ are joined at height | 413 | 413 | ok | `barrier/P+/t=3` |
| mutations on the route from P⁺₃ to −P⁺₃ | 94 | 94 | ok | `route/P+/t=3` |
| top of the route from Q₇ (height 8) to −Q₇ | 1,242 | 1,242 | ok | `route/Qa/a=7` |
| mutations on that route | 3,120 | 3,120 | ok | `route/Qa/a=7` |
| quivers of height exactly 4, up to relabelling | 17,353 | 17,353 | ok | `conj55/h=4` |
| of these, reaching an acyclic quiver within height 4 | 10,415 | 10,415 | ok | `conj55/h=4` |
| claims certified for R_b, even b ≥ 6 | 30 | 30 | ok | `certificate/R_b` |
| claims certified for Q_t, t ≥ 3 | 43 | 43 | ok | `certificate/Q_t` |
| claims certified for P⁺_t, t ≥ 8 | 938 | 938 | ok | `certificate/P+_t/audit-to-7` |
<!-- END GENERATED headline -->

These tasks recompute, at the parameters shown, what the closed forms, the routes and the certificate programs say. They were written by the same AI model as everything else here. They do not replace the proofs, and they are not an independent reading.

## Limits

- **No human reader.** See the status box. The checks recorded in notes 12, 17, 19 and 23 were made by fresh instances of the same AI model that wrote the notes they check. They are a check against slips, not a mathematician's reading.
- **Three kinds of support, not one.** "Computational" results hold on the stated range only: R_b for odd b (5 ≤ b ≤ 59), Proposition 10.2 (a ≤ 64), Proposition 12.1 (height ≤ 18), the census (classes containing a quiver of height ≤ 9).
- **Ranges that rest on one program.** P⁺_t for 65 ≤ t ≤ 80 (two enumerators agree up to t = 64). For Q_a, a second program reproduced the counts without pruning for a ≤ 26 and a = 32, and with forks pruned for a ≤ 32, 36 and 40; the other values up to 64 rest on one program. For Conjecture 5.5, the split was recomputed in full up to height 11 and to height 10 by the check of note 19; above height 11 the passing verdicts were checked on samples.
- **Certificates that are not stored.** The tube certificates behind 227,414 census classes were never stored. A sample of 5,353 was regenerated for this repository; the rest can be regenerated ([CLAIMS.md](CLAIMS.md#what-is-not-stored)).
- **Shared code.** Not every "independent" check is independent of the code it checks. [research/verify/README.md](research/verify/README.md) says, script by script, what each one shares with what it verifies.
- **The census can hide joins.** A pocket that joined its class only above the bound to which the class was enumerated (192 or more) would not be seen.
- **Cited theorems.** Proposition 12.1 rests on published and preprint theorems, among them Theorem 5.1 of arXiv:2610.36179 (an unrefereed preprint of 26 October 2026) for 253,191 quivers.
- **Prior art.** The literature search (9 to 16 November 2026) did not cover MathSciNet or zbMATH. Prior art could exist under other names.
- **What was run again here.** The records cover the smoke batch, the section batches, the recount of Section 13 from stored outputs, the searches for P⁺_t up to t = 80 (by both enumerators up to t = 64, by the second alone above, as in the original runs), the searches for Q_a up to a = 48 without pruning and up to a = 64 with forks not expanded, Conjecture 5.5 to height 18, and the cores and tube certificates of Section 13 from the stored inputs of each stage, the last three by the original programs. The first tube pass was run twice: the first run certified 225,207 classes, one fewer than the stored 225,208, and the second certified 225,208, the same classes as the stored output ([CLAIMS.md](CLAIMS.md#tasks-and-records)). The census was not run again and rests on the original outputs. [CLAIMS.md](CLAIMS.md) says so row by row.
- **Known discrepancies** between the paper, the notes and the logs are listed in [CLAIMS.md](CLAIMS.md#known-discrepancies).

## Tasks, batches and records

Every claim that a program can check is a **task**: one computation with one answer, for example the least height at which R₈ is joined to −R₈. A task carries the value that is predicted for it (a closed form of the article, a number the article prints, or a count copied from a stored result) and names the stored result that holds the original number. A **batch** is a file in [data/batches/](data/batches/) that lists tasks with their time and memory limits. The scheduler, [src/taskbatch/](src/taskbatch/PROTOCOL.md), runs a batch with one process per task, stops a task at its limits, and appends one **record** per task: status, computed value, predicted value, limits, time, peak memory, versions and commit. The claim tables of [CLAIMS.md](CLAIMS.md) are generated from the records. A claim whose tasks have no record reads "not re-run", whatever the stored results say; the 471 stored results are the original outputs and were not turned into records.

```bash
make plan BATCH=data/batches/section-07.toml
```

```bash
make run BATCH=data/batches/section-07.toml
```

```bash
make report BATCH=data/batches/section-07.toml
```

`plan` lists the tasks with their limits and computes nothing. `run` computes every task that has no record yet and writes to `results/<batch>/`, which is not in git. `report` prints tables from the records. `run` ends with status 0 when every task is `ok`, 1 when a task is `mismatch`, `error` or `crashed`, 3 when nothing failed but a task was stopped at a limit, and 2 when the batch cannot be run as asked. A rerun computes the tasks without a record and nothing else; `--retry timeout,memory` computes again the tasks that were stopped, for example with larger limits.

| Batch | Tasks | What it computes | Needs | Here |
|---|---|---|---|---|
| `smoke` | 66 | the headline numbers above | Python | 10 s |
| `section-05` | 152 | G_k for 3 ≤ k ≤ 40: mutation heights, barrier, the quivers below it, the route | Python | 3 s |
| `section-07` | 164 | R_b for 5 ≤ b ≤ 60 and Q_t for 3 ≤ t ≤ 16: barrier by search, route, the two certificate programs | Python | 6 s |
| `section-08` | 4 | the two pockets born at 9 that die at 132 are Q₃ and R₉ | Python | 1 s |
| `section-09` | 149 | P⁺_t: the route for t ≤ 64, the search for t ≤ 12, the certificate program | Python | 30 s |
| `section-10` | 112 | Q_a: the route for a ≤ 48, the searches for a ≤ 7 | Python | 100 s, 450 MB |
| `section-12` | 6 | Conjecture 5.5: the split at each height ≤ 6, by enumeration | Python | 50 s |
| `section-13` | 1 | the counts of Section 13, recounted from the stored outputs of the core and tube programs | the data archive | 20 s, 3 GB |
| `section-14` | 34 | the generic search of Section 14 on R_b, P⁺_t and Q_a | `make build` | 3 s |
| `long-pplus` | 253 | P⁺_t for t ≤ 80 by the two enumerators of the original runs. The C search: barrier and region for t ≤ 64; from t = 65 the barrier is above 2³¹ and its 32 tasks end `unsupported`. The second enumerator (note 17): the region for every t ≤ 80. The route for 65 ≤ t ≤ 80 | `make build` | 7 min: 2 for the C search, 5 for the rest; 520 MB at most for one task |
| `long-qa` | 110 | Q_a for a ≤ 48 without pruning and a ≤ 64 with forks not expanded | `make build`, numpy | 2 h 20 min on four processes (8 h of single-process time); 220 MB at most for one task |
| `long-conj55` | 1 | Conjecture 5.5 to height 18, by the original program | numpy | 48 min, 11 GB |
| `long-section-13` | 3 | the cores and the tube certificates, regenerated from stored inputs | the data archive, numpy | 2 h 13 min: cores 6 min on 8 processes, the tube passes 74 and 53 min on 6 (the first tube pass again: 94 min); 1.5 GB at most for one task |
| `limits-demo` | 6 | a task stopped at its time limit and one at its memory limit, next to four that finish | Python | 3 s |
| `negative-control` | 3 | predicted values that are wrong on purpose: each task must end `mismatch` | Python | 1 s |

The long batches are the original long runs, described as tasks with limits. All four have been run. In `long-section-13` the first tube pass was one certified class short of the stored count in its first run and reproduced it in its second. The census of Section 8 is not a task at all ([CLAIMS.md](CLAIMS.md#tasks-and-records)). The task kinds and the keys of a batch file are listed at the top of [src/qmb/tasks.py](src/qmb/tasks.py); what a run guarantees, and the contract between the scheduler and the program that computes, are in [src/taskbatch/PROTOCOL.md](src/taskbatch/PROTOCOL.md).

The records in [data/records/](data/records/) were computed on one machine, from committed code, and each names its commit; a record that names the machine or a directory outside the repository is not adopted. [data/claims/RECORDS.md](data/claims/RECORDS.md) lists every task with its predicted value, its stored evidence and its record.

## A quiver of your own

The searches run on any quiver, not only on those of the article. A quiver is given by the entries b_ij, i < j, of its exchange matrix, row by row: b₀₁, b₀₂, b₀₃, b₁₂, b₁₃, b₂₃ on four vertices, with b_ij > 0 for b_ij arrows i → j.

```bash
PYTHONPATH=src python3 -m qmb explore 3 -2 2 -1 3 -3
```

```text
quiver    (3, -2, 2, -1, 3, -3) on 4 vertices, of height 3
mutation  at each vertex in turn gives heights 7, 11, 4, 8
barrier   10: the opposite is reached through heights at most 10, and not below
below it  8 quivers up to relabelling, the start included; 1 of height at most 3
route     16 mutations at the least, staying at or below 10
searched  23 quivers, taken in order of height
```

The command looks for the least height at which the quiver is joined to its opposite, counts the quivers reached below that height, and counts the mutations of a shortest route at it. The mutation class of most quivers is infinite, and a quiver need not be joined to its opposite at any height a search reaches, so the search is stopped: `--cap H` leaves out every quiver above height H, and without a cap the search ends after 100,000 quivers (`--budget N` sets another number). Both stops are counts, so a command gives the same answer on every machine. A stopped search still gives a bound, because the quivers are taken in order of height: here R₈ with its last entry changed from −8 to −7.

```bash
PYTHONPATH=src python3 -m qmb explore -8 -8 7 -2 6 -7 --cap 1000
```

```text
quiver    (-8, -8, 7, -2, 6, -7) on 4 vertices, of height 8
mutation  at each vertex in turn gives heights 62, 24, 49, 41
barrier   not found: no route to the opposite stays at or below height 1000
          (the cap of 1000 left quivers out; a higher route is not excluded)
searched  579 quivers, taken in order of height
```

`--json` prints the same result as JSON. The search is the one of [src/qmb/search.py](src/qmb/search.py), in Python integers and without pruning. It compares quivers up to relabelling, at a cost that grows with the number of vertices: here it takes about 18,000 quivers a second on four vertices and 300 on six, and 100,000 quivers on four vertices hold about 120 MB.

Several quivers at once, under time and memory limits and with a record each, are a batch file with tasks of the kind `explore`. [data/examples/own-quivers.toml](data/examples/own-quivers.toml) is one to copy:

```toml
[[tasks]]
kind = "explore"
quiver = [-8, -8, 7, -2, 6, -8]
name = "R8"                                                   # ends the id of the task; otherwise the entries do
cap = 200                                                     # as --cap
budget = 50000                                                # as --budget
predicted = { barrier = 101, quivers = 35, mutations = 37 }   # what you expect, on any keys of the value
```

```bash
make run BATCH=data/examples/own-quivers.toml
```

```bash
make report BATCH=data/examples/own-quivers.toml REPORT_ARGS=--full
```

Only `quiver` is required. With `predicted` a task ends `ok` when the search agrees on every key given, and `mismatch` when it does not. Without it the task ends `ok` whenever the search ends: there is nothing to agree with, and the record holds the numbers. The keys of the value are listed at the top of [src/qmb/kinds/explore.py](src/qmb/kinds/explore.py). These tasks belong to no claim of the article, so the example is kept outside `data/batches/` and nothing of it is in `data/records/`.

## Repository layout

The root holds four folders: `research/` (the notes, the scripts behind them, the checks, the paper), `data/` (what this repository publishes: batches, records, claims, the example batch), `src/` (the code that computes the tasks and keeps the records) and `tests/`. `.github/check_root.py` keeps it so. The Python packages are under `src/`: `make` sets `PYTHONPATH` itself, and a command run by hand starts with `PYTHONPATH=src`.

| Path | What it is |
|---|---|
| [CLAIMS.md](CLAIMS.md) | Article section → repository path; every claim → script, stored output, command, and what the records say; what is not stored; known discrepancies |
| [research/paper/](research/paper/) | The draft paper, `mutation-barriers.tex` and its PDF (16 November 2026) |
| [research/docs/](research/docs/README.md) | 23 notes in reading order, with an index: the arguments, computations and checks |
| [research/experiments/](research/experiments/README.md) | The scripts behind the notes, two C programs, `requirements.txt` |
| [research/verify/](research/verify/README.md) | Checking code, kept apart from the code it checks: `smoke.py` and the scripts of notes 12, 17, 19, 23 |
| [data/README.md](data/README.md) | The stored results: one archive, its checksum, every file in it |
| [data/claims/](data/claims/) | `claims.toml`, the registry of claims and their tasks; `expected.json`, predicted values and stored evidence by task; `RECORDS.md`, generated: every task with its record |
| [data/batches/](data/batches/) | Batch files: which tasks, which limits |
| [data/records/](data/records/) | The records of the batches that were run for this repository |
| [data/examples/](data/examples/own-quivers.toml) | A batch file to copy for quivers of your own, outside the claims |
| [src/qmb/](src/qmb/) | The core that tasks compute with: mutation, relabelling, forks, the families and their closed forms, searches, the task kinds. Standard library only. It is new code: the scripts of `research/experiments/` and `research/verify/` do not use it |
| [src/runners/task_runner.py](src/runners/task_runner.py) | The command the scheduler calls: lists the tasks of a batch, computes one task |
| [src/taskbatch/](src/taskbatch/PROTOCOL.md) | The scheduler: batch files, limits, records, reports. First written for another repository of the same author and copied here under a neutral name; `PROTOCOL.md` is its contract with a runner |
| [src/bookkeeping/](src/bookkeeping/) | The script that rewrote references in the stored results, the archive builder, the builder of `data/claims/expected.json`, the generator of the claim tables, and `adopt.py`, which copies the records of a finished run into `data/records/` |
| [tests/](tests/) | Tests of the core, the runner, the registry and the scheduler |
| `Makefile`, `Dockerfile`, `pyproject.toml`, `.python-version`, `.github/workflows/` | Targets, container, lint settings, the interpreter, continuous integration |
| [LICENSE](LICENSE), [LICENSE-TEXT.md](LICENSE-TEXT.md) | MIT for code; CC BY 4.0 for prose, paper and data |
| [CITATION.cff](CITATION.cff) | How to cite |

**Two clicks.** The data for a figure: [CLAIMS.md](CLAIMS.md#article-sections-and-figures) → the file. The proof certificate for a theorem: the table above → the log (after unpacking the archive), or [CLAIMS.md](CLAIMS.md#the-status-table-row-by-row) → the command that regenerates it.

## Reproducing

**The smoke run** needs Python 3 and nothing else (run with CPython 3.12.14 and 3.14.4):

```bash
python3 -I research/verify/smoke.py          # about 15 s, under 100 MB: R_8 (101, 35 quivers, 37 mutations), G_8, R_b, Q_t, P+_t, Q_a, Conjecture 5.5 to height 4
python3 -I research/verify/smoke.py --full   # about 2.5 min, under 500 MB: adds Q_7 (1,242), R_b to b = 20, Conjecture 5.5 to height 6
sh research/verify/smoke_certificates.sh     # about 10 s: the 30 + 43 claims of note 15 and the certificate of note 16, from the repository's own programs
```

**The tests and the smoke batch** need Python 3.11 or later, and a C compiler for the tests of the C search (they are skipped without one). Linux is assumed: the scheduler reads `/proc` and, where `systemd-run --user` is available, uses control groups.

```bash
make test             # under a minute: the core against values computed by hand, the runner, the registry, the scheduler
make smoke            # about 10 s: the smoke batch, computed afresh, and the headline table from it
make test-slow        # several minutes: research/verify/smoke.py and the section batches, each computed afresh
```

Without Python 3.12, make or a compiler on the machine, build the container once (this needs the network) and run inside it without:

```bash
docker build -t mutation-barriers .
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/work -w /work mutation-barriers make test
```

**In a clean container**, with no network and the repository mounted read-only:

```bash
docker run --rm --network none -v "$PWD":/repo:ro -w /repo python:3.12-slim python3 -I research/verify/smoke.py
docker run --rm --network none -v "$PWD":/repo:ro -w /repo python:3.12-slim sh research/verify/smoke_certificates.sh
```

Measured here: 20 s and 12 s, with the image holding CPython 3.12.16; both pass.

**Everything else.** Python 3.12 with the two packages of `research/experiments/requirements.txt`, and gcc for the two search programs:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r research/experiments/requirements.txt
```

Download the archive `mutation-barriers-data-v1.tar.xz` from the release page (TODO-REPOSITORY-URL) and install it as described in [data/README.md](data/README.md): it unpacks into `research/experiments/`. Every note that computes something ends with a *Reproduce* section giving the exact commands, run from `research/experiments/` with `python -I`; [CLAIMS.md](CLAIMS.md) collects the ones behind the article with their run times and memory. Many commands overwrite the stored files, so rerun them in a copy. What was rerun for this repository, and what was not, is listed in [data/README.md](data/README.md#verification).

## Licence and citation

Code: [MIT](LICENSE). Text (notes, paper, this guide) and data: [CC BY 4.0](LICENSE-TEXT.md). Citation metadata: [CITATION.cff](CITATION.cff). The papers the notes cite are not included.

## A note on method

> **PLACEHOLDER, to be written by the author before publication.** This section is reserved for the author's own account of how this work was produced and checked. It is deliberately empty. The factual status is in the box at the top of this page.
