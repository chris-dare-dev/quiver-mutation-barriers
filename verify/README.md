# Checking code

Code that checks the results, kept apart from the code that produced them (`../experiments/`). Stored results of both kinds unpack into `../experiments/` ([../DATA.md](../DATA.md)); run everything from there:

```bash
cd experiments
python -I ../verify/review17.py replay
```

All of this code, like the code it checks, was written by instances of the same AI model. "Independent" below means: written separately, from the statements, without importing the code under review. It does not mean a different author, and it is not a mathematician's reading.

## `smoke.py` and `smoke_certificates.sh`

- `smoke.py` was written for this repository. It uses the standard library only, imports nothing from `experiments/` or from the other scripts here, and reads no stored result. It recomputes, from the definition of mutation: for R₈ the barrier 101, the 35 quivers below it, the 37 mutations and the 28 quivers at 101; the route of G₈ and the barriers of G_k (k ≤ 12), R_b (b ≤ 14), Q_t (t = 3, 4), P⁺_t (t = 2, 3) and Q_a (a ≤ 4, with route lengths for a ≤ 3); and Conjecture 5.5 up to height 4 (the counts of quivers and of those that reach an acyclic quiver within their height). `--full` adds Q₇ (1,242), R_b to b = 20 and heights 5 and 6. Its expected values are typed from the article. What it shares with the rest: nothing but the definitions.
- `smoke_certificates.sh` runs the repository's own certificate programs (`n4_doors.py prove2`, `prove`; `np_corridor_prove.py prove`; the Q₇ route of `np_rowwalk.py`) and checks their last lines. It is not an independent check: it shows that the programs run from a clean copy and certify what the notes say.

## The task runner and its core

The tasks of [../batches/](../batches/) are computed by `../runners/task_runner.py` with the package [../qmb/](../qmb/). This is how each kind of task relates to the code under check and to the code in this directory:

| Task kind, method | Computed by | What it shares |
|---|---|---|
| `quiver`, `barrier` and `reach` by search, `route`, `conj55` | `qmb/`: its own mutation, canonical form, fork test, searches and route words, standard library only | Nothing with `experiments/`, nothing with this directory. `qmb/` was written for this repository from the statements of the article and the paper; no script here imports it, and it imports none. `smoke.py` and `qmb/` are two separate implementations of the same definitions, and neither reads the other. |
| `barrier` and `reach` with method `np_barrier` | `experiments/np_barrier.c`, built by `make build` | The search is the code under check. `qmb/` only writes its input line, and tests that the quiver it reports is the opposite of the start. |
| `reach` with method `np_qa_core` | `experiments/np_qa_core.py` driving `np_qa_core.c` | The code under check, run again. |
| `certificate` | `experiments/n4_doors.py prove2`, `prove`; `np_corridor_prove.py prove` | The certificate programs themselves, run again; the task reads their verdict. Not an independent check, as for `smoke_certificates.sh`. |
| `conj55_program` | `experiments/n4_conj55.py run`, `resolve`, `summary` | The code under check, run again. |
| `core`, `tube` | `experiments/n4_opposite_run.py cores`, `n4_opposite_tubes.py run`, `n4_tube_lemma.py certify2`, on stored inputs | The code under check, run again on the stored output of the stage before it. |
| `census` (`decided-classes`) | `review23_n22_counts.py` of this directory, on stored outputs | The counting script of note 23, run again on the stored outputs of the programs it checks. It recounts those outputs and regenerates none of them. |

Where two methods compute the same task, they can be compared: `make test` checks `np_barrier.c` against the searches of `qmb/` at small parameters (and `np_qa_core.py` too, when numpy is installed), and the section batches compare the searches of `qmb/` with the stored counts of the original programs (P⁺_t for t ≤ 12, Q_a for a ≤ 7, with and without expanding forks). `../tests/test_independence.py` fails if a script of this directory or of `experiments/` imports `qmb/` or the scheduler, or if `smoke.py` imports anything outside the standard library.

`qmb/`, the batch files and the tests were written by an instance of the same AI model as the rest.

## The checks of notes 12, 17, 19 and 23

File names: `reviewNN…` belongs to note NN; a tag `nMM` names the note under check (`review19_n13_…` checks note 13 and belongs to note 19; `n14a`, `n14b` are two separate checks of note 14).

| Scripts | Note | Checks |
|---|---|---|
| `review12.py` | [12](../docs/12-checks-of-notes-03-to-10.md) | notes 3 to 10: rank 3, the census, G_k (hand proof, symbolic rerun, n ≥ 5) |
| `review17.py` | [17](../docs/17-checks-of-note-16.md) | note 16: the P⁺_t route, the search (second enumerator), the certificate (second certifier) |
| `review19.py`, `review19_n13_*`, `review19_n14a_*`, `review19_n14b_*` | [19](../docs/19-checks-of-notes-13-to-16.md) | notes 13 to 16: Conjecture 5.5 to height 10, cores, pockets, tube certificates, R_b, Q_t, P⁺_t |
| `review23_n20_*`, `review23_n21_*`, `review23_n22_*`, `review23_lead_*`, and the C programs `review23_n20_search.c`, `review23_n21_search.c` | [23](../docs/23-checks-of-notes-20-to-22.md) | notes 20 to 22: the Q_a searches, the attacker, the tube lemma and the counts of Section 13 |

### What each script shares with the code it checks

Generated from the import statements and the file names in each script. "Imports from `experiments/`" is code shared with the scripts under check; "own modules" are other files of this directory; "reads" are stored results of the scripts under check that the script takes as input (to compare with, or to start from).

| Script | Imports from `experiments/` | Own modules | Reads stored results of `experiments/` |
|---|---|---|---|
| `review12.py` | — | — | `n4_all_N18.json`, `n4_block_scan.jsonl`, `n4_classes_B512.jsonl`, `n4_classes_k5_B512.jsonl`, `n4_classes_k67_B256.jsonl`, `n4_classes_k8_B192.jsonl.gz` and 1 more |
| `review17.py` | — | — | `np_corridor_core_plus.log`, `np_corridor_family.jsonl`, `np_corridor_family_plus.jsonl`, `np_corridor_prove.log` |
| `review19.py` | — | — | — |
| `review19_n13_arith.py` | — | `review19_n13_lib` | `n4_conj55_N18.log`, `n4_conj55_N18_resolve.json.gz`, `n4_conj55_N18_resolve.log`, `n4_conj55_N18_summary.log` |
| `review19_n13_census.py` | — | `review19_n13_lib` | `n4_classes_B512.jsonl`, `n4_classes_k5_B512.jsonl`, `n4_classes_k67_B256.jsonl`, `n4_classes_k8_B192.jsonl.gz`, `n4_classes_k9_B192.jsonl.gz` |
| `review19_n13_evid.py` | — | `review19_n13_lib` | — |
| `review19_n13_lib.py` | — | — | — |
| `review19_n13_lowcert.py` | — | `review19_n13_lib` | — |
| `review19_n13_lowh.py` | — | `review19_n13_lib` | — |
| `review19_n13_samples.py` | — | `review19_n13_lib` | `n4_conj55_N18.json.gz`, `n4_conj55_N18_resolve.json.gz` |
| `review19_n13_soundness.py` | — | `review19_n13_lib` | — |
| `review19_n13_units.py` | — | `review19_n13_lib` | — |
| `review19_n14a_cosq.py` | — | `review19_n14a_lib` | `n4_opposite_cores.jsonl.gz`, `n4_opposite_fn.jsonl.gz`, `n4_opposite_plateaus.jsonl.gz` |
| `review19_n14a_cosq2.py` | — | `review19_n14a_cosq`, `review19_n14a_lib` | `n4_opposite_cores.jsonl.gz`, `n4_opposite_fn.jsonl.gz`, `n4_opposite_plateaus.jsonl.gz` |
| `review19_n14a_example.py` | — | `review19_n14a_cosq2`, `review19_n14a_lib` | — |
| `review19_n14a_gk.py` | — | `review19_n14a_lib` | — |
| `review19_n14a_gksym.py` | `n4_opposite`, `n4_opposite_gk` | — | — |
| `review19_n14a_lib.py` | — | — | — |
| `review19_n14a_mono.py` | — | `review19_n14a_lib` | `n4_opposite_cores.jsonl.gz` |
| `review19_n14a_pockets.py` | — | `review19_n14a_gk`, `review19_n14a_lib` | `n4_classes_B512.jsonl`, `n4_classes_k5_B512.jsonl`, `n4_classes_k67_B256.jsonl`, `n4_classes_k8_B192.jsonl.gz`, `n4_classes_k9_B192.jsonl.gz`, `n4_opposite_cores.jsonl.gz` and 1 more |
| `review19_n14a_preds.py` | `n4_opposite` | `review19_n14a_lib` | — |
| `review19_n14b_cores.py` | `n4_opposite` | `review19_n14b_lib` | `n4_classes_B512.jsonl`, `n4_classes_k5_B512.jsonl`, `n4_classes_k67_B256.jsonl`, `n4_classes_k8_B192.jsonl.gz`, `n4_classes_k9_B192.jsonl.gz`, `n4_opposite_cores.jsonl.gz` and 1 more |
| `review19_n14b_counts.py` | — | `review19_n14b_lib` | `n4_classes_B512.jsonl`, `n4_classes_k5_B512.jsonl`, `n4_classes_k67_B256.jsonl`, `n4_classes_k8_B192.jsonl.gz`, `n4_classes_k9_B192.jsonl.gz`, `n4_opposite_cores.jsonl.gz` and 2 more |
| `review19_n14b_full.py` | — | `review19_n14b_cores`, `review19_n14b_lib` | — |
| `review19_n14b_fullsum.py` | — | `review19_n14b_lib` | `n4_opposite_cores.jsonl.gz`, `n4_opposite_plateaus.jsonl.gz` |
| `review19_n14b_lib.py` | — | — | — |
| `review19_n14b_mono.py` | — | `review19_n14b_lib` | — |
| `review19_n14b_prefork.py` | — | `review19_n14b_cores`, `review19_n14b_lib` | — |
| `review19_n14b_probe.py` | `n4_opposite`, `n4_opposite_tubes` | — | — |
| `review19_n14b_single.py` | — | `review19_n14b_lib` | — |
| `review19_n14b_tubecert.py` | `n4_opposite_tubes` | — | `n4_opposite_cores.jsonl.gz`, `n4_opposite_tubes.jsonl.gz` |
| `review19_n14b_tubecheck.py` | — | `review19_n14b_lib` | — |
| `review19_n14b_tubecontrol.py` | — | `review19_n14b_lib`, `review19_n14b_tubecheck` | — |
| `review19_n14b_tubeplat.py` | — | `review19_n14b_cores`, `review19_n14b_lib` | `n4_opposite_plateaus.jsonl.gz` |
| `review19_n14b_units.py` | `n4_opposite` | `review19_n14b_lib` | — |
| `review23_lead_n20_xmove.py` | — | `review23_lead_n21_mask` | — |
| `review23_lead_n21_mask.py` | — | — | `owf_barrier_mask.jsonl` |
| `review23_lead_n22.py` | — | — | — |
| `review23_n20_checks.py` | — | `review23_n20_lib` | — |
| `review23_n20_ends.py` | — | `review23_n20_checks`, `review23_n20_lib` | — |
| `review23_n20_lib.py` | — | — | — |
| `review23_n20_runs.py` | — | — | `np_qa_core_family.jsonl`, `np_qa_core_family_nofork.jsonl` |
| `review23_n20_xmove.py` | — | `review23_n20_lib` | — |
| `review23_n21_blackbox.py` | `owf_barrier` | — | — |
| `review23_n21_review.py` | — | — | `owf_barrier_attack.jsonl`, `owf_barrier_attack_bigbound.jsonl`, `owf_barrier_mask.jsonl`, `owf_barrier_perturb.jsonl`, `owf_barrier_rows_n5.jsonl`, `owf_barrier_rows_n6.jsonl` and 7 more |
| `review23_n22_bottoms.py` | — | `review23_n22_lib` | `n4_tube_certify2.jsonl.gz` |
| `review23_n22_c1034.py` | — | `review23_n22_lib` | — |
| `review23_n22_counts.py` | — | `review23_n22_lib` | `n4_opposite_cores.jsonl.gz`, `n4_opposite_plateaus.jsonl.gz`, `n4_opposite_tubes.jsonl.gz`, `n4_tube_certify2.jsonl.gz`, `n4_tube_classify.jsonl.gz` |
| `review23_n22_engine.py` | — | `review23_n22_lib` | `n4_tube_certify2.jsonl.gz`, `n4_tube_classify.jsonl.gz` |
| `review23_n22_engine_500677.py` | — | `review23_n22_engine` | `n4_tube_certify2.jsonl.gz` |
| `review23_n22_engine_highlam.py` | — | `review23_n22_engine` | `n4_tube_certify2.jsonl.gz` |
| `review23_n22_engine_retry.py` | — | `review23_n22_engine` | `n4_tube_certify2.jsonl.gz` |
| `review23_n22_lib.py` | — | — | — |
| `review23_n22_markovC.py` | — | `review23_n22_lib` | — |
| `review23_n22_rank3.py` | — | `review23_n22_lib` | `n4_opposite_plateaus.jsonl.gz`, `n4_opposite_tubes.jsonl.gz`, `n4_tube_classify.jsonl.gz` |
| `review23_n22_regen14.py` | — | — | `n4_opposite_cores.jsonl.gz`, `n4_opposite_tubes.jsonl.gz` |
| `review23_n22_selftest.py` | — | `review23_n22_lib` | `n4_opposite_tubes.jsonl.gz`, `n4_tube_certify2.jsonl.gz`, `n4_tube_classify.jsonl.gz` |
| `review23_n22_shapes.py` | — | `review23_n22_lib` | — |
| `review23_n22_tubes2.py` | — | `review23_n22_lib`, `review23_n22_shapes` | — |

Not visible in the import statements:

- `review23_n22_regen14.py` **runs** `experiments/n4_opposite_tubes.py one QUIVER` in a subprocess and parses what it prints. The certificates it writes are therefore produced by the code under check; `review23_n22_shapes.py` and `review23_n22_tubes2.py` then examine them with their own code.
- `review19_n14b_tubecert.py` imports `n4_opposite_tubes` for the same purpose: the 322 certificates that `review19_n14b_tubecheck.py` attacks are regenerated by the code under check.
- `review23_n21_review.py` runs `review23_n21_blackbox.py`, which imports `owf_barrier` and calls the attacker as a black box; the routes it returns are replayed with the review's own mutation.
- `review17.py replay` and `review19.py prove16` take the list of members and exits from `np_corridor_prove.log` and re-derive the verdicts. They cannot find a member that the first program did not list; `review17.py instances` and `closure` compare the list with an exhaustive search for t = 8–14, 16, 20, 24.
- `experiments/n4_conj55.py`, a script under check, imports `review12.py` from this directory: its sub-commands `verify`, `verify-resolve`, `recount` and `census` use the canonical form and the mutation of `review12.py`. So the "separately written" recount of note 13 and `review12.py` are one implementation, and the recount lives in the same file as the computation it recounts.
- Scripts that import `n4_opposite` (`review19_n14a_gksym.py`, `review19_n14a_preds.py`, `review19_n14b_cores.py`, `review19_n14b_probe.py`, `review19_n14b_units.py`) do so to compare its predicates with their own on samples, or, for `gksym` and `probe`, to exercise it directly.
- Every script that reads the census reads the same five class files `n4_classes_*`; an error in the enumeration behind those files would be shared by all of them. `review12.py n4slow` re-enumerates height ≤ 8 only.

## Running them

- Python 3.12 with `../experiments/requirements.txt`; `review12.py`, `review17.py` and `review19_n14a_cosq*.py` need cypari2 for their symbolic commands.
- **These scripts write outside the repository.** Several keep intermediate files under `~/.cache/qmb-review17/`, `~/.cache/qmb-review19/` and `~/.cache/qmb-review23/` (and `~/.cache/qmb-review23/n21/`), and create those directories themselves. The scripts of `experiments/` use `~/.cache/qmb-np/` in the same way. Logs are written where the command line redirects them.
- The two C programs are compiled by hand: `gcc -O2 -o ~/.cache/qmb-review23/review23_n20_search review23_n20_search.c`, and the command in the header of `review23_n21_search.c`.
- The exact commands, in order, are in the *Reproduce* sections of notes 12, 17, 19 and 23. What was re-run for this repository is listed in [../DATA.md](../DATA.md#verification).
