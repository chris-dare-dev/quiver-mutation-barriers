# Mirror barriers in quiver mutation

*How high must a mutation path between two quivers of small height climb? Notes, code and stored results behind the draft paper [paper/mutation-barriers.pdf](paper/mutation-barriers.pdf) and the article "How High Must a Mutation Path Climb?" (TODO-ARTICLE-URL).*

> **Status of these results.** Everything here was produced with extensive help from AI tools. The proofs and computations were rechecked by fresh instances of the same AI model, mostly with separately written code (some certificates were rerun rather than reimplemented, and some ranges rest on a single program), but **no human has read the paper**, and no specialist has checked a single argument. Each result is labelled by how it is supported: **proved by hand**; a **computer-assisted proof**, which covers every value of the parameters, with a program checking finitely many polynomial identities and inequalities; **computational**, meaning an exhaustive check over a stated range and nothing beyond it; or **conjecture**. Nobody should cite these results as established until a mathematician has read them.

**Start here:** `python3 -I verify/smoke.py` recomputes the headline numbers below from the definition of mutation in about 15 seconds, with the standard library only and without the data archive. `make smoke` computes the same numbers as tasks under a scheduler and prints the [table below](#headline-numbers-recomputed). Then [CLAIMS.md](CLAIMS.md) maps every claim of the article to a script, a stored output and a command, and says what has been run again here.

## The question

A quiver here is a skew-symmetric integer matrix; its *height* is its largest entry in absolute value. Mutation at a vertex is the move of Fomin and Zelevinsky's cluster algebras. Two quivers are compared up to relabelling of the vertices. A *route* is a sequence of mutations, and its height is the largest height of a quiver on it. For a quiver Q and w ≥ 0, let f(Q, w) be the least L ≥ w such that any two quivers of height at most w in the mutation class of Q are joined by a route of height at most L, and let F(n, w) be the largest f(Q, w) over quivers on n vertices. Whether two quivers are mutation-equivalent is not known to be decidable for four or more vertices, and a computable bound on F(n, w) would decide it.

The question arose from a failed attempt to build a one-way function from mutation paths ([note 1](docs/01-mutation-path-test.md), [note 21](docs/21-barriers-and-the-mutation-path-owf.md)).

## The answer

No upper bound on F(n, w) was found for n ≥ 4. What was found are lower bounds: quivers Q that reach their opposite −Q, but only far above the height of both. The running example is R₈ = (−8, −8, 7, −2, 6, −8), of height 8: it reaches −R₈ in 37 mutations, and by no route below height 101. At height 8 there is a ladder: 56 on four vertices (proved by hand), 101 on four vertices (computer-assisted proof), 1,242 on five vertices (exhaustive search).

## Main results

The rows are those of the article's status table, with its labels. "Paper" numbers refer to [paper/mutation-barriers.pdf](paper/mutation-barriers.pdf); the article numbers its statements differently, and [CLAIMS.md](CLAIMS.md) gives both.

| Result | Statement | Support | Note | Certificate or data |
|---|---|---|---|---|
| G_k (article Thm 5.1) | G_k is joined to −G_k at exactly k(k − 1); F(n, w) ≥ w(w − 1) for n ≥ 4 | proof by hand | [9](docs/09-n4-mirror-family.md), [12](docs/12-checks-of-notes-03-to-10.md) §4 | `verify/smoke.py`; `review12_handproof.log` |
| R_b (Thm 7.2) | R_b is joined to −R_b at exactly 2b² − 3b − 3, even b ≥ 6 | route by hand; lower bound computer-assisted (30 claims) | [15](docs/15-rank-2-orbits-and-the-constant-2.md) §5 | `n4_doors_prove2.log`, written out in `n4_doors_prove2_readable.log` |
| Q_t (Section 7) | Q_t is joined to −Q_t at exactly 2t⁴ − t³ − t² + 2t, t ≥ 3 | computer-assisted (43 claims) | [15](docs/15-rank-2-orbits-and-the-constant-2.md) §5 | `n4_doors_prove.log`, `n4_doors_prove_readable.log` |
| Remark 8.1 | F(4, w) ≤ 2w² | conjecture; census evidence up to w = 9 | [10](docs/10-n4-quadratic-bound.md), [11](docs/11-n4-invariants-descent-joins.md) | `n4_classes_*.jsonl*` |
| P⁺_t (Thm 9.1) | P⁺_t is joined to −P⁺_t at 2t⁵ − t⁴ + t² − 1; F(5, w) ≥ 2w^{5/2} − 11w² | route by hand; search for t ≤ 80; certificate for t ≥ 8 | [16](docs/16-five-vertices-above-w-squared.md), [17](docs/17-checks-of-note-16.md) | `np_corridor_prove.log`; the member families in `np_corridor_members.log` |
| Q_a route (Thm 10.1) | a route from Q_a to −Q_a of height 4a³ − 3a² + O(a) | derived by hand, printed as a sketch; replayed for a ≤ 48 | [18](docs/18-five-vertices-cubic-barrier.md) §5 | `np_rowwalk_family*.log` |
| Prop 10.2 | no lower route; F(5, w) ≥ 4w³ − O(w²) | computational, w ≤ 65; conjectured beyond | [18](docs/18-five-vertices-cubic-barrier.md), [20](docs/20-core-of-the-cubic-family.md) | `np_qa_core_family*.jsonl` |
| Prop 12.1 | Conjecture 5.5 of Armstrong-Williams, Hirst, Jackson and Lee | computational, height ≤ 18, resting on cited theorems | [13](docs/13-conjecture-5-5-up-to-height-18.md) | `n4_conj55_N18_summary.log` |
| Section 13 | 785,198 of 788,026 census classes decided | computational, certificates not stored | [14](docs/14-opposite-quivers-forks-and-cores.md), [22](docs/22-tube-lemma-and-its-limits.md) | `review23_n22_counts.log`; a regenerated sample of 5,353 certificates |
| Thm 13.2 | the Markov quiver with a pendant arrow has no tube certificate | proof by hand | [22](docs/22-tube-lemma-and-its-limits.md) §5 | `n4_tube_markov.log` (cuts only) |

File names without a directory are stored results; they are in the data archive ([DATA.md](DATA.md)), not in git.

## Headline numbers, recomputed

`make smoke` runs the batch [batches/smoke.toml](batches/smoke.toml): 66 tasks, about ten seconds on four processes, with the standard library only and without the data archive. Each row is one quantity of one task: the value the article states, and what the task computed in its latest record in [records/](records/). `make smoke` ends by printing this table from its own fresh run, and fails if it is not the table printed here.

<!-- BEGIN GENERATED headline: tools/claims.py tables -->
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
- **Shared code.** Not every "independent" check is independent of the code it checks. [verify/README.md](verify/README.md) says, script by script, what each one shares with what it verifies.
- **The census can hide joins.** A pocket that joined its class only above the bound to which the class was enumerated (192 or more) would not be seen.
- **Cited theorems.** Proposition 12.1 rests on published and preprint theorems, among them Theorem 5.1 of arXiv:2610.36179 (an unrefereed preprint of 26 October 2026) for 253,191 quivers.
- **Prior art.** The literature search (9 to 16 November 2026) did not cover MathSciNet or zbMATH. Prior art could exist under other names.
- **What was run again here.** The records cover the smoke batch, the section batches, the recount of Section 13 from stored outputs, the searches for P⁺_t up to t = 80 (by both enumerators up to t = 64, by the second alone above, as in the original runs), and Conjecture 5.5 to height 18 by the original program. The rest was not run again: the searches for Q_a above a = 12, the census, the cores and the tube certificates rest on the original outputs. [CLAIMS.md](CLAIMS.md) says so row by row.
- **Known discrepancies** between the paper, the notes and the logs are listed in [CLAIMS.md](CLAIMS.md#known-discrepancies).

## Tasks, batches and records

Every claim that a program can check is a **task**: one computation with one answer, for example the least height at which R₈ is joined to −R₈. A task carries the value that is predicted for it (a closed form of the article, a number the article prints, or a count copied from a stored result) and names the stored result that holds the original number. A **batch** is a file in [batches/](batches/) that lists tasks with their time and memory limits. The scheduler, [taskbatch/](taskbatch/PROTOCOL.md), runs a batch with one process per task, stops a task at its limits, and appends one **record** per task: status, computed value, predicted value, limits, time, peak memory, versions and commit. The claim tables of [CLAIMS.md](CLAIMS.md) are generated from the records. A claim whose tasks have no record reads "not re-run", whatever the stored results say; the 471 stored results are the original outputs and were not turned into records.

```bash
make plan BATCH=batches/section-07.toml
```

```bash
make run BATCH=batches/section-07.toml
```

```bash
make report BATCH=batches/section-07.toml
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
| `long-qa` | 110 | Q_a for a ≤ 48 without pruning and a ≤ 64 with forks not expanded | `make build`, numpy | not run; hours |
| `long-conj55` | 1 | Conjecture 5.5 to height 18, by the original program | numpy | 48 min, 11 GB |
| `long-section-13` | 3 | the cores and the tube certificates, regenerated from stored inputs | the data archive, numpy | never run |
| `limits-demo` | 6 | a task stopped at its time limit and one at its memory limit, next to four that finish | Python | 3 s |
| `negative-control` | 3 | predicted values that are wrong on purpose: each task must end `mismatch` | Python | 1 s |

The long batches are the original long runs, described as tasks with limits. `long-pplus` and `long-conj55` have been run. The other two are for a machine left alone for hours and have not been run for this repository; their claims read "not re-run". The census of Section 8 is not a task at all ([CLAIMS.md](CLAIMS.md#tasks-and-records)). The task kinds and the keys of a batch file are listed at the top of [qmb/tasks.py](qmb/tasks.py); what a run guarantees, and the contract between the scheduler and the program that computes, are in [taskbatch/PROTOCOL.md](taskbatch/PROTOCOL.md).

The records in [records/](records/) were computed on one machine, from committed code, and each names its commit. [claims/RECORDS.md](claims/RECORDS.md) lists every task with its predicted value, its stored evidence and its record.

## Repository layout

| Path | What it is |
|---|---|
| [paper/](paper/) | The draft paper, `mutation-barriers.tex` and its PDF (16 November 2026) |
| [docs/](docs/README.md) | 23 notes in reading order, with an index: the arguments, computations and checks |
| [CLAIMS.md](CLAIMS.md) | Article section → repository path; every claim → script, stored output, command, and what the records say; what is not stored; known discrepancies |
| [claims/](claims/) | `claims.toml`, the registry of claims and their tasks; `expected.json`, predicted values and stored evidence by task; `RECORDS.md`, generated: every task with its record |
| [batches/](batches/) | Batch files: which tasks, which limits |
| [records/](records/) | The records of the batches that were run for this repository |
| [qmb/](qmb/) | The core that tasks compute with: mutation, relabelling, forks, the families and their closed forms, searches, the task kinds. Standard library only. It is new code: the scripts of `experiments/` and `verify/` do not use it |
| [runners/task_runner.py](runners/task_runner.py) | The command the scheduler calls: lists the tasks of a batch, computes one task |
| [taskbatch/](taskbatch/PROTOCOL.md) | The scheduler: batch files, limits, records, reports. First written for another repository of the same author and copied here under a neutral name; `PROTOCOL.md` is its contract with a runner |
| [tests/](tests/) | Tests of the core, the runner, the registry and the scheduler |
| [experiments/](experiments/README.md) | The scripts behind the notes, two C programs, `requirements.txt` |
| [verify/](verify/README.md) | Checking code, kept apart from the code it checks: `smoke.py` and the scripts of notes 12, 17, 19, 23 |
| [DATA.md](DATA.md) | The stored results: one archive, its checksum, every file in it |
| [tools/](tools/) | The script that rewrote references in the stored results, the archive builder, the builder of `claims/expected.json` and the generator of the claim tables |
| `Makefile`, `Dockerfile`, `pyproject.toml`, `.python-version`, `.github/workflows/` | Targets, container, lint settings, the interpreter, continuous integration |
| [LICENSE](LICENSE), [LICENSE-TEXT.md](LICENSE-TEXT.md) | MIT for code; CC BY 4.0 for prose, paper and data |
| [CITATION.cff](CITATION.cff) | How to cite |

**Two clicks.** The data for a figure: [CLAIMS.md](CLAIMS.md#article-sections-and-figures) → the file. The proof certificate for a theorem: the table above → the log (after unpacking the archive), or [CLAIMS.md](CLAIMS.md#the-status-table-row-by-row) → the command that regenerates it.

## Reproducing

**The smoke run** needs Python 3 and nothing else (run with CPython 3.12.14 and 3.14.4):

```bash
python3 -I verify/smoke.py            # about 15 s, under 100 MB: R_8 (101, 35 quivers, 37 mutations), G_8, R_b, Q_t, P+_t, Q_a, Conjecture 5.5 to height 4
python3 -I verify/smoke.py --full     # about 2.5 min, under 500 MB: adds Q_7 (1,242), R_b to b = 20, Conjecture 5.5 to height 6
sh verify/smoke_certificates.sh       # about 10 s: the 30 + 43 claims of note 15 and the certificate of note 16, from the repository's own programs
```

**The tests and the smoke batch** need Python 3.11 or later, and a C compiler for the tests of the C search (they are skipped without one). Linux is assumed: the scheduler reads `/proc` and, where `systemd-run --user` is available, uses control groups.

```bash
make test             # under a minute: the core against values computed by hand, the runner, the registry, the scheduler
make smoke            # about 10 s: the smoke batch, computed afresh, and the headline table from it
make test-slow        # several minutes: verify/smoke.py and the section batches, each computed afresh
```

Without Python 3.12, make or a compiler on the machine, build the container once (this needs the network) and run inside it without:

```bash
docker build -t mutation-barriers .
docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/work -w /work mutation-barriers make test
```

**In a clean container**, with no network and the repository mounted read-only:

```bash
docker run --rm --network none -v "$PWD":/repo:ro -w /repo python:3.12-slim python3 -I verify/smoke.py
docker run --rm --network none -v "$PWD":/repo:ro -w /repo python:3.12-slim sh verify/smoke_certificates.sh
```

Measured here: 20 s and 12 s, with the image holding CPython 3.12.16; both pass.

**Everything else.** Python 3.12 with the two packages of `experiments/requirements.txt`, and gcc for the two search programs:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r experiments/requirements.txt
```

Download the archive `mutation-barriers-data-v1.tar.xz` from the release page (TODO-REPOSITORY-URL) and install it as described in [DATA.md](DATA.md): it unpacks into `experiments/`. Every note that computes something ends with a *Reproduce* section giving the exact commands, run from `experiments/` with `python -I`; [CLAIMS.md](CLAIMS.md) collects the ones behind the article with their run times and memory. Many commands overwrite the stored files, so rerun them in a copy. What was rerun for this repository, and what was not, is listed in [DATA.md](DATA.md#verification).

## Licence and citation

Code: [MIT](LICENSE). Text (notes, paper, this README) and data: [CC BY 4.0](LICENSE-TEXT.md). Citation metadata: [CITATION.cff](CITATION.cff). The papers the notes cite are not included.

## A note on method

> **PLACEHOLDER, to be written by the author before publication.** This section is reserved for the author's own account of how this work was produced and checked. It is deliberately empty. The factual status is in the box at the top of this page.
