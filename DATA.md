# Data

The stored results of the scripts are **not in git**. They are distributed as one compressed archive, to be attached to a release of this repository.

| | |
|---|---|
| File | `mutation-barriers-data-v1.tar.xz` |
| Size | 101,292,880 bytes (96.6 MiB) compressed; 259,670,177 bytes (about 260 MB) unpacked |
| Files | 471 |
| SHA-256 | `e71d5b7d3de065fc444e417208850bb22205f719d6992939458bbac65d1bcab2` |
| Where to get it | TODO-REPOSITORY-URL (the release page of this repository, once the archive is attached to a release) |

## Installing it

From the root of a clone of this repository, with the archive downloaded there:

```bash
echo "e71d5b7d3de065fc444e417208850bb22205f719d6992939458bbac65d1bcab2  mutation-barriers-data-v1.tar.xz" | sha256sum -c
tar -xJf mutation-barriers-data-v1.tar.xz
```

The archive contains one directory, `experiments/`, and unpacks its files next to the scripts, which is where the scripts look for them; the checking scripts of `verify/` read and write there too. It adds files only and overwrites no script. The `.gitignore` keeps the unpacked files out of git. The largest file, `n4_classes_k67_B256.jsonl`, is 70 MB and is in the archive only.

Nothing needs the archive to get started: `verify/smoke.py` and `verify/smoke_certificates.sh` run from a clean clone.

## What is in it

Every stored result behind the notes: the `.log`, `.json`, `.jsonl` and gzip-compressed outputs of the scripts in `experiments/` and `verify/`. The [manifest](#manifest) lists each file with its size, the script that wrote it and the note that uses it; each note's *Reproduce* section gives the command for each file. By family:

| Files | Written by | Notes | Content |
|---|---|---|---|
| `mutation_*` | `mutation_path.py` | 1 | The planted one-way function: grids, adversarial planting, component sizes, entry growth |
| `bounded_*`, `bp_sizing*`, `rank3_profile.*` | `bounded_paths.py`, `rank3_paths.py` | 2, 3 | Connection profiles of bounded mutation graphs; the corrected profiles (`_v2_`), up to relabelling (`_unl`); rank 3 |
| `pockets_*`, `traps_*`, `hunt_*` | `pockets.py`, `traps.py`, `hunt.py` | 4, 5, 6 | Persistence pairs (birth, death), local minima of total weight, searches for large escape ratios |
| `n4_all_*`, `n4_family.log` | `n4_all.py`, `n4_family.py` | 7, 8, 10 | Every 4-vertex quiver of height ≤ 14 and ≤ 18: persistence of the height filtration, and the survivors kept for the census |
| `n4_classes_*` | `n4_classes.py` | 8, 10 | **The census**: one record per mutation class containing a quiver of height ≤ 9, with its pockets, enumerated to the bound in the file name |
| `n4_mirror_*`, `n4_block_scan.*`, `n4_triangle_patterns.log` | `n4_mirror.py`, `n4_mirror_proof.py`, `n4_block_scan.py` | 9, 10 | G_k and scans of related shapes |
| `n4_joins.*`, `n4_descent*`, `n4_rejoin_c8*`, `n4_certify.json`, `n4_bfz_check.json`, `n4_gk_descent_symbolic.log` | `n4_evidence.py` | 11 | Invariants, the re-enumeration to 8b², descent, the 139 worst join paths |
| `n4_conj55_*` | `n4_conj55.py` | 13 | Conjecture 5.5 to height 18: per-height counts, undetermined quivers and their per-class certificates, recounts, sample checks |
| `n4_opposite_*` | `n4_opposite_run.py`, `n4_opposite_tubes.py`, `n4_opposite_gk.py` | 14 | Cores of the census classes, mirror map, pockets of finite-core classes, one summary record per tube certificate |
| `n4_doors_*` | `n4_doors.py`, `n4_doors_readable.py` | 15 | R_b and Q_t: the two polynomial certificates (and their written-out form), the searches, orbits of two mutations, fork lemmas, scans |
| `np_corridor_*` | `np_corridor.py`, `np_corridor_prove.py`, `np_corridor_members.py` | 16 | P⁺_t: searches to t = 64, the certificate for t ≥ 8, its member families, censuses on 5 vertices |
| `np_rowwalk_*` | `np_rowwalk.py` | 18 | Q_a: the route to a = 48, searches to a = 22 (26 with pruning), scans of rows over the bounce cycle |
| `np_qa_core_*` | `np_qa_core.py` | 20 | Q_a: the region below the barrier for a ≤ 64 (pruned) and a ≤ 48 (not pruned), its lines, kinds and spirals |
| `owf_barrier_*` | `owf_barrier.py` | 21 | The attacker measurements: generic search, structure-aware attacker, random rows, masking |
| `n4_tube_*` | `n4_tube_lemma.py` | 22 | The tube lemma on the census, second-pass certificates (summary records), the Markov cuts |
| `review12_*`, `review17_*`, `review19_*`, `review23_*` | the scripts of `verify/` with the same prefix | 12, 17, 19, 23 | Outputs of the checks |

Not in it: the papers the notes cite; the intermediate files listed under "What is not stored" in [CLAIMS.md](CLAIMS.md#what-is-not-stored).

## Predicted values taken from the stored results

[claims/expected.json](claims/expected.json) is in git. It maps a task of [batches/](batches/) to its predicted value and to the stored result that carries the original number, as file and line. [tools/expected.py](tools/expected.py) writes it from the unpacked archive (`make expected DATA=experiments`) and can check it (`python3 tools/expected.py check experiments`); its docstring says which values are copied from stored results and which are closed forms. It reads the stored results and changes none of them.

A stored result is what an earlier program printed. It is not a record: the records in [records/](records/) are written by the scheduler when a task is computed here, and no stored result was converted into one.

## What was rewritten, and by which script

No stored result was edited by hand for this repository. One script, [tools/renumber_results.py](tools/renumber_results.py), was applied once to a copy of the original outputs, and the archive holds its output. Its docstring is the specification. It changed three kinds of text and no number, count, quiver or timing:

1. **References to notes and to numbered statements.** The notes were first written under a working numbering; logs and records that said, for example, "Theorem 66.4" or named a note by its working number now use the numbers of `docs/` ("Theorem 18.4", "note 18"). 34 distinct references of this kind occur in the stored results. One script and its log (`n4_tube_lemma.py`, `n4_tube_markov.log`) carried a label of note 22's lemmas under an older number still; it was mapped to the current one. One printed line of the same script, in `n4_tube_pairs.log`, named its note by a common noun and now says "after this note".
2. **File names and file-name tags.** The checking scripts and their outputs were renamed to `review12…`, `review17…`, `review19_n13…`, `review23_n20…` (see [verify/README.md](verify/README.md)), and one sub-command, `compare18`, with them: 144 result files were renamed, and mentions of the old names inside logs follow. A few record keys that contained a working number were renamed in the same way, in the scripts and in the stored records alike (`f_note2` in the `bounded_profile_v2_*` files, `subquiver_is_Q_t_of_note_15` in `np_corridor_family*.jsonl`, `stored20` and `note20` in the `review23_n20_search_*` logs).
3. **Absolute paths.** In 14 logs, the absolute path of the Python interpreter became `python`, the absolute path of the experiments directory was dropped, a home directory became `~`, a scratch directory was dropped, and the cache directories got the names the scripts of this repository use (`~/.cache/qmb-…`). The files: `n4_conj55_N18.log`, `n4_opposite_fn.log`, `review19_n13_lowh_10.log`, `review19_n13_lowh_1_7.log`, `review19_n13_lowh_8.log`, `review19_n13_lowh_9.log`, `review19_n14a_cosq.log`, `review19_n14b_cores.log`, `review19_n14b_counts_time.log`, `review19_n14b_full.log`, `review19_n14b_tubecert.log`, `review23_n21_attack.log`, `review23_n22_regen14.log`, `review12_n4slow_N8.log`.

In all, the script changed 598 lines in 84 files and renamed 144 files; 183 of the original files were touched in one way or the other, and the rest are byte-for-byte the original outputs. No gzip-compressed file had a line changed; those that were renamed are byte-for-byte the original files under a new name.

The same rules were applied to the scripts and to the notes, so that a script, its stored output and the note that quotes them agree. This was tested by rerunning programs from the tree of this repository and comparing with the rewritten logs (see [Verification](#verification)).

Left as they were, on purpose:

- In `n4_mirror_proof.log`, `n4_triangle_patterns.log`, `review12_extremes.log` and `review23_n21_rows_escape.log` the word "part" followed by a number is a count ("class part 263" is the size of the part of a class that was enumerated), not a reference.
- Some internal identifiers of scripts contain two-digit numbers that are not note numbers (`cor52` is Corollary 5.2 of arXiv 2610.36179; `n4_conj55` is its Conjecture 5.5).
- Timing lines written by `/usr/bin/time -v` and the dates of the files.

The script is not idempotent and must not be run on the unpacked archive.

## Files generated for this repository

Four files in the archive were written on 17 November 2026, from the tree of this repository, by the commands shown:

| File | Command (from `experiments/`) | What it is |
|---|---|---|
| `n4_doors_prove2_readable.log` | `python -I n4_doors_readable.py prove2` | the 30 claims behind Theorem 15.13 (article Theorem 7.2), with every symbolic step |
| `n4_doors_prove_readable.log` | `python -I n4_doors_readable.py prove` | the 43 claims behind Theorem 15.6 (Q_t) |
| `np_corridor_members.log` | `python -I np_corridor_members.py` | the 149 member families behind the 766 exits of Theorem 16.6 (article Theorem 9.1) |
| `review23_n22_regen14.jsonl.gz` | `python -I ../verify/review23_n22_regen14.py 5000 4`, output copied from `~/.cache/qmb-review23/n14_certs.jsonl.gz` | 5,353 regenerated tube certificates with their 181,985 families (a sample; see CLAIMS.md) |

The stored `review23_n22_regen14.log` is the log of the original run of the same command; the rerun printed the same lines up to the times.

## How it was built

```bash
python3 -I tools/renumber_results.py STAGING/experiments      # once, on a copy of the original outputs
sh tools/build_archive.sh STAGING                               # tar --sort=name --owner=0 --group=0 --numeric-owner | xz -9
python3 -I tools/make_manifest.py STAGING/experiments           # the manifest below
```

`STAGING/experiments` held the 471 files of the manifest. The archive stores no user or group names (owner 0, group 0), and the files keep their modification times.

## Verification

Run on 17 November 2026 on the machine that produced the results (Linux, 8-core AMD Ryzen 7 7800X3D, 64 GB), from a copy of the tree of this repository; commands that read stored results had the archive's files in `experiments/`. Interpreter: CPython 3.12.14 with numpy 2.5.4 and cypari2 2.2.4, unless stated.

| Run | Result |
|---|---|
| SHA-256 of the archive against the value above, then unpacked into a clean copy | OK, 471 files |
| `python3 -I verify/smoke.py` (clean copy, no archive; CPython 3.12.14 and 3.14.4) | 40 checks, 0 mismatches; 15 s, 38 MB |
| `python3 -I verify/smoke.py --full` (CPython 3.14.4) | 0 mismatches; 134 s, 437 MB |
| `sh verify/smoke_certificates.sh` (clean copy, no archive) | all five lines agree (8 s) |
| the two `docker run --rm --network none … python:3.12-slim …` lines of the README (CPython 3.12.16 in the image, repository mounted read-only) | both pass; 20 s and 12 s |
| `n4_doors.py selftest`, `prove2`, `prove`, each compared with its stored log | identical (2 s, under 1 s, under 1 s) |
| `np_corridor_prove.py prove --T0 8 --audit-tmax 11`, compared with `np_corridor_prove.log` | identical (24 s) |
| `np_corridor.py build`, then `family_plus --tmin 2 --tmax 8` | built with gcc 15.2; the lines for t = 2 to 8 agree with `np_corridor_family_plus.log` up to the times |
| `np_rowwalk.py family --amin 7 --amax 7 --search-amax 0` | 3,120 mutations, height 1,242, as in `np_rowwalk_family.log` |
| `owf_barrier.py summarize`, compared with `owf_barrier_summary.log` | identical |
| `../verify/review17.py selftest`, compared with `review17_selftest.log` | identical (6 s) |
| `../verify/review17.py replay`, compared with `review17_replay.log` | same verdicts (fork 54, height 428, member 161, new member 123, failed 0); the order of one list of names and the time differ |
| `../verify/review19_n13_arith.py`, compared with `review19_n13_arith.log` | identical except a final timing line that the stored log has |
| `../verify/review23_n22_regen14.py 5000 4` | 5,353 certificates in 2 min 12 s on 4 processes; same lines as the stored log up to the times |
| **Re-runs of commands whose stored log was touched by the rewrite** (clean `HOME`, 60 to 100 s limit each, at most 4 processes) | |
| `../verify/review23_n22_counts.py`, compared with `review23_n22_counts.log` | byte-identical (20 s) |
| `n4_doors.py coq --depth 7 --depth-joins 5`, `n4_doors.py forks`; `n4_tube_lemma.py lemma`, `markov`, `pairs`; `np_corridor.py selftest`; `np_qa_core.py compare18`; `../verify/review17.py forks`, `lemmas`; `../verify/review19.py orbits --samples 50000 --wmax 5`, `search16 --t 2 3 4 5 6 8 10 --classes --at-H`; `../verify/review23_lead_n22.py lemmas`; `../verify/review23_n22_rank3.py`, `review23_n22_markovC.py`, `review23_n22_shapes.py`, `review23_n22_tubes2.py` (the last two with the stored sample of certificates copied to the cache) | each byte-identical to its stored log |
| `n4_conj55.py census`; `../verify/review12.py rank3 --N 60 --W 12`; `../verify/review17.py closure --tmin 2 --tmax 64` (4 workers); `../verify/review23_n22_selftest.py 300` | identical up to the times |
| `np_corridor.py core --t 2 … 12` and `core --plus --t 2 … 10` | byte-identical to the first part of `np_corridor_core.log` and `np_corridor_core_plus.log`; each stored log continues with the output of a second command (`--branches`), not re-run |
| `n4_tube_lemma.py sidesig`, `np_rowwalk.py family` (to a = 26 pruned, and the route to a = 48), `../verify/review17.py closure --tmin 65 --tmax 80`, `../verify/review19.py route16 --tmin 2 --tmax 64` | not finished within 60 s; stopped, not compared |
| `../verify/review23_n22_regen14.py 20 2` from a `HOME` with no cache directories | creates `~/.cache/qmb-review23/` itself and completes (49 s) |
| `n4_opposite_tubes.py one "[3,3,-3,0,0,-2]"` | prints the record of class 173 as stored (L 39, 26 quivers, 4 families, τ = 2) and its four families |

**Not re-run:** every other command of the notes, in particular all the long searches (`n4_conj55.py run` and `resolve`, the census, `np_corridor.py family_plus` beyond t = 8, `np_rowwalk.py family` with the search, `np_qa_core.py family`, `n4_opposite_run.py`, `n4_opposite_tubes.py run`, `n4_tube_lemma.py`, `owf_barrier.py` measurements) and every other script of `verify/`. Their stored outputs are the original ones, with the references rewritten as described above. No container image was built; the interpreter and package versions above are the pin.

## Licence

The data are released under [CC BY 4.0](LICENSE-TEXT.md), like the text.

## Manifest

| File | Bytes | Date | Written by | Note |
|---|---|---|---|---|
| `bounded_excursions.jsonl` | 66518 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_excursions.log` | 24322 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_excursions_n7.jsonl` | 24009 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_excursions_n7.log` | 8368 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_excursions_sparse.jsonl` | 70072 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_excursions_sparse.log` | 24942 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n4.jsonl` | 11359 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n4.log` | 3478 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n4_B4096.jsonl` | 11262 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n4_B4096.log` | 3432 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n5.jsonl` | 6019 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n5.log` | 1780 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n5_B128.jsonl` | 6000 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n5_B128.log` | 1767 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n6.jsonl` | 3353 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n6.log` | 948 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n6_B64.jsonl` | 3911 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n6_B64.log` | 1117 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n7.jsonl` | 4056 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n7.log` | 1062 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n7_B16.jsonl` | 3422 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_n7_B16.log` | 879 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_sparse_n5.jsonl` | 5278 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_sparse_n5.log` | 1450 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_sparse_n6.jsonl` | 4115 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_sparse_n6.log` | 1107 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_sparse_n7.jsonl` | 3972 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_sparse_n7.log` | 1046 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_summary.log` | 4684 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bounded_profile_v2_allw_n4_unl.jsonl` | 2565645 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_allw_n4_unl.log` | 529741 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_allw_n5_unl.jsonl` | 172729 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_allw_n5_unl.log` | 34823 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_allw_n6_unl.jsonl` | 13735 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_allw_n6_unl.log` | 2732 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n4_B4096.jsonl` | 17230 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n4_B4096.log` | 3429 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n4_B4096_unl.jsonl` | 16959 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n4_B4096_unl.log` | 3405 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n4_unl.jsonl` | 17050 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n4_unl.log` | 3444 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n5_B128.jsonl` | 9018 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n5_B128.log` | 1767 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n5_B128_unl.jsonl` | 8777 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n5_B128_unl.log` | 1745 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n5_unl.jsonl` | 8792 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n5_unl.log` | 1757 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n6.jsonl` | 4889 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n6.log` | 948 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n6_B64_unl.jsonl` | 5449 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n6_B64_unl.log` | 1082 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n6_unl.jsonl` | 4636 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n6_unl.log` | 914 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n7_B16.jsonl` | 4576 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n7_B16.log` | 879 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n7_B16_unl.jsonl` | 4224 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n7_B16_unl.log` | 830 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n7_unl.jsonl` | 5037 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_n7_unl.log` | 996 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n5.jsonl` | 7499 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n5.log` | 1450 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n5_unl.jsonl` | 7287 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n5_unl.log` | 1435 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n6.jsonl` | 5720 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n6.log` | 1100 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n6_unl.jsonl` | 5483 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n6_unl.log` | 1075 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n7.jsonl` | 5436 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n7.log` | 1042 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n7_unl.jsonl` | 5111 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bounded_profile_v2_sparse_n7_unl.log` | 999 | 2026-11-09 | `bounded_paths.py` | 3 |
| `bp_sizing.jsonl` | 11253 | 2026-11-08 | `bounded_paths.py` | 2 |
| `bp_sizing_n7.jsonl` | 1984 | 2026-11-08 | `bounded_paths.py` | 2 |
| `hunt_bwalk_n4.jsonl` | 265483 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_bwalk_n4.log` | 6272 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_bwalk_n5.jsonl.gz` | 12469703 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_bwalk_n5.log` | 6513 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_bwalk_n6.jsonl.gz` | 18498790 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_bwalk_n6.log` | 6579 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_calibrate.jsonl` | 65068 | 2026-11-09 | `hunt.py` | 6 |
| `hunt_climb_census.jsonl` | 10368 | 2026-11-09 | `hunt.py` | 6 |
| `mutation_component.jsonl` | 12482 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_component.log` | 3172 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_corridor.jsonl` | 20750 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_corridor.log` | 66 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_deepest.jsonl` | 32818 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_deepest.log` | 86 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_failed_recheck.jsonl` | 704 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_growth.json` | 1861 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_growth.log` | 1384 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_path.jsonl` | 599480 | 2026-11-08 | `mutation_path.py` | 1 |
| `mutation_path.log` | 1313 | 2026-11-08 | `mutation_path.py` | 1 |
| `n4_all_N14.json` | 3527912 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N14.log` | 1962 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N14_k5.json` | 4611971 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N14_k5.log` | 1962 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N14_k7.json` | 14395111 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N14_k7.log` | 1962 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N14_k9.log` | 1962 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N18.json` | 10320698 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_all_N18.log` | 4304 | 2026-11-09 | `n4_all.py` | 7, 8, 10 |
| `n4_bfz_check.json` | 270 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_block_scan.jsonl` | 160604 | 2026-11-09 | `n4_block_scan.py` | 10 |
| `n4_certify.json` | 1425 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_classes_B512.jsonl` | 2855899 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_B512.log` | 840 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k5_B512.jsonl` | 10689263 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k5_B512.log` | 843 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k67_B256.jsonl` | 70400970 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k67_B256.log` | 855 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k8_B192.jsonl.gz` | 5664869 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k8_B192.log` | 864 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k9_B192.jsonl.gz` | 10326176 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_classes_k9_B192.log` | 877 | 2026-11-09 | `n4_classes.py` | 8, 10 |
| `n4_conj55_N14.log` | 2816 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18.json.gz` | 2614782 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18.log` | 4502 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_recount_10_11.log` | 315 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_resolve.json.gz` | 7140475 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_resolve.log` | 3936 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_summary.log` | 6422 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_verify.log` | 225 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_verify_resolve.log` | 248 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N18_verify_resolve_largest.log` | 244 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9.json.gz` | 119644 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9.log` | 1840 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9_recount.log` | 1212 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9_resolve.json.gz` | 182915 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9_resolve.log` | 1374 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9_summary.log` | 3847 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9_verify.log` | 242 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_N9_verify_resolve.log` | 247 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_census.log` | 651 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_conj55_check.log` | 2498 | 2026-11-11 | `n4_conj55.py` | 13 |
| `n4_descent.jsonl` | 3022350 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_descent.log` | 14012 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_descent_gk.jsonl` | 9298 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_descent_summary.json` | 13653 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_doors_ahjl.log` | 2304 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_coq.log` | 2022 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_doors.log` | 1915 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_doors12.log` | 2300 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_family.log` | 9132 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_family2.log` | 425 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_family3.log` | 11187 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_forks.log` | 287 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_markov.log` | 2238 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_orbit.log` | 2531 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_orbit01.log` | 1492 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_prove.log` | 3812 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_prove2.log` | 2565 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_prove2_readable.log` | 11352 | 2026-11-17 | `n4_doors_readable.py` | 15 |
| `n4_doors_prove_readable.log` | 18998 | 2026-11-17 | `n4_doors_readable.py` | 15 |
| `n4_doors_scan2_b10.log` | 537 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_scan2_b11_12.log` | 1101 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_selftest.log` | 209 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_doors_thin.log` | 2700 | 2026-11-11 | `n4_doors.py` | 15 |
| `n4_family.log` | 4726 | 2026-11-09 | `n4_family.py` | 7 |
| `n4_gk_descent_symbolic.log` | 1120 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_joins.jsonl` | 290141 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_joins.log` | 16451 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_mirror_family.jsonl` | 2830 | 2026-11-09 | `n4_mirror.py` | 9 |
| `n4_mirror_proof.log` | 1564 | 2026-11-09 | `n4_mirror_proof.py` | 9 |
| `n4_mirror_scan.jsonl` | 2590620 | 2026-11-09 | `n4_mirror.py` | 9 |
| `n4_opposite_combined.log` | 1778 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_corecheck.log` | 2007 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_cores.jsonl.gz` | 10564700 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_cores.log` | 898 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_extremes.log` | 1857 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_fn.jsonl.gz` | 2040179 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_fn.log` | 1664 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_gk.log` | 2823 | 2026-11-11 | `n4_opposite_gk.py` | 14 |
| `n4_opposite_lemmas.log` | 412 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_mirror.log` | 3968 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_plateaus.jsonl.gz` | 6831812 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_plateaus.log` | 95 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_pockets.jsonl.gz` | 2816834 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_pockets.log` | 2712 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_summary.log` | 990 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_opposite_tubes.jsonl.gz` | 7273953 | 2026-11-11 | `n4_opposite_tubes.py` | 14 |
| `n4_opposite_tubes.log` | 4166 | 2026-11-11 | `n4_opposite_tubes.py` | 14 |
| `n4_opposite_tubeshapes.log` | 333 | 2026-11-11 | `n4_opposite_tubes.py` | 14 |
| `n4_opposite_walks.log` | 127 | 2026-11-11 | `n4_opposite_run.py` | 14 |
| `n4_rejoin_c8.jsonl` | 0 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_rejoin_c8.log` | 1445 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_rejoin_c8_summary.json` | 1089 | 2026-11-11 | `n4_evidence.py` | 11 |
| `n4_triangle_patterns.log` | 689 | 2026-11-09 | `a one-off driver over n4_classes.py (note 10 §4)` | 10 |
| `n4_tube_certify2.jsonl.gz` | 245630 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_certify2.log` | 1640 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_classify.jsonl.gz` | 158300 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_classify.log` | 489 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_lemma.log` | 685 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_markov.log` | 853 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_pairs.log` | 1319 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_shapes.log` | 1959 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_side.log` | 1788 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_sidesig.log` | 515 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `n4_tube_verify2.log` | 280 | 2026-11-12 | `n4_tube_lemma.py` | 22 |
| `np_corridor_census_n4.log` | 6480 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w2.jsonl.gz` | 21752 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w2.log` | 1296 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w3.jsonl.gz` | 692682 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w3.log` | 2692 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w4_min4.jsonl.gz` | 2600897 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w4_min4.log` | 2751 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_census_n5_w4_recheck.log` | 264 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_core.log` | 8162 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_core_plus.log` | 8936 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_family.jsonl` | 37531 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_family.log` | 14198 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_family_plus.jsonl` | 34648 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_family_plus.log` | 14364 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_grid.log` | 1181 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_members.log` | 55587 | 2026-11-17 | `np_corridor_members.py` | 16 |
| `np_corridor_pendant.log` | 2408 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_prove.log` | 105426 | 2026-11-11 | `np_corridor_prove.py` | 16 |
| `np_corridor_prove_check.log` | 811 | 2026-11-11 | `np_corridor_prove.py` | 16 |
| `np_corridor_pycheck.log` | 1971 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_rows.log` | 10186 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_rows_db2_a5.log` | 1403 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_selftest.log` | 587 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_star.log` | 1245 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_templates.jsonl.gz` | 36873 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_corridor_templates.log` | 1631 | 2026-11-11 | `np_corridor.py` | 16 |
| `np_qa_core_anatomy.log` | 12191 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_branches.log` | 20317 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_compare18.log` | 397 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_crosscheck.log` | 2209 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_ends.log` | 4305 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_family.jsonl` | 28192 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_family.log` | 10767 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_family_nofork.jsonl` | 21143 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_family_nofork.log` | 8029 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_forkless.log` | 2665 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_kinds.log` | 10141 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_lines.log` | 3855 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_prefork.log` | 1280 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_region.log` | 1464 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_rerun.log` | 321 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_qa_core_spiral.log` | 1085 | 2026-11-12 | `np_qa_core.py` | 20 |
| `np_rowwalk_allbases.log` | 4918 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_cycle.log` | 5415 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_family.jsonl` | 14493 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_family.log` | 5967 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_family_pruned.log` | 1353 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_family_route_only.log` | 4281 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_phases.log` | 6706 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_pycheck.log` | 637 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_sample_n5_w2.log` | 1980 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_sample_n6_w2.jsonl.gz` | 159329 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_sample_n6_w2.log` | 2625 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_sample_n6_w2_recheck.jsonl.gz` | 11725 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_sample_n6_w2_recheck.log` | 271 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a3.jsonl.gz` | 24334 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a3.log` | 1628 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a4.jsonl.gz` | 48659 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a4.log` | 1798 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a5.jsonl.gz` | 88731 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a5.log` | 1950 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a6.jsonl.gz` | 123544 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a6.log` | 2114 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a7.jsonl.gz` | 184071 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_scan_a7.log` | 2333 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_shape.log` | 2269 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_walks.log` | 5902 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `np_rowwalk_walks_a7_a8.log` | 3984 | 2026-11-12 | `np_rowwalk.py` | 18 |
| `owf_barrier_attack.jsonl` | 68051 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_attack.log` | 84440 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_attack_bigbound.jsonl` | 16389 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_generic.jsonl` | 35028 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_generic.log` | 35028 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_mask.jsonl` | 84698 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_mask.log` | 84698 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_perturb.jsonl` | 92018 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_perturb.log` | 92018 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n5.jsonl` | 2445503 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n5.log` | 2445679 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n6.jsonl` | 503094 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n6.log` | 503179 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n6_dense.jsonl` | 186004 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n6_dense.log` | 186048 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n7.jsonl` | 179075 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n7.log` | 179117 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n8.jsonl` | 97446 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rows_n8.log` | 97487 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rwalk.jsonl` | 3815 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rwalk.log` | 3815 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rwalk_qa.jsonl` | 435 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_rwalk_qa.log` | 435 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_selftest.log` | 1062 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_shortest.jsonl` | 5408 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_shortest.log` | 5408 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_shortest_pruned.jsonl` | 6001 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_shortest_pruned.log` | 6872 | 2026-11-12 | `owf_barrier.py` | 21 |
| `owf_barrier_summary.log` | 17603 | 2026-11-12 | `owf_barrier.py` | 21 |
| `pockets_n4_B4096.jsonl` | 848307 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n4_B4096.log` | 3779 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n5_B2048.jsonl` | 1230724 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n5_B2048.log` | 5782 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n5_B512.jsonl` | 471647 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n5_B512.log` | 6208 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n6_B128.jsonl` | 624301 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n6_B128.log` | 4856 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n7_B48.jsonl` | 271964 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_n7_B48.log` | 3480 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_sparse_n5_B512.jsonl` | 68773 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_sparse_n5_B512.log` | 2044 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_sparse_n6_B128.jsonl` | 308930 | 2026-11-09 | `pockets.py` | 4 |
| `pockets_sparse_n6_B128.log` | 1965 | 2026-11-09 | `pockets.py` | 4 |
| `rank3_profile.jsonl` | 6636766 | 2026-11-09 | `rank3_paths.py` | 3 |
| `rank3_profile.log` | 445 | 2026-11-09 | `rank3_paths.py` | 3 |
| `review12_burnside.log` | 1135 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_classes.log` | 4928 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_cyclic.log` | 1259 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_cyclic2.log` | 160 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_extremes.log` | 3113 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_handproof.log` | 618 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_mirror.log` | 2553 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_n4slow_N8.log` | 880 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_pendant.log` | 5804 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_rank3.log` | 1704 | 2026-11-11 | `verify/review12.py` | 12 |
| `review12_symbolic.log` | 3732 | 2026-11-11 | `verify/review12.py` | 12 |
| `review17_anatomy.log` | 3539 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_closedforms.log` | 2083 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_closure.log` | 13223 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_closure_65_80.log` | 3583 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_corollary.log` | 1083 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_forks.log` | 669 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_instances.log` | 2985 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_lemmas.log` | 166 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_negctl.log` | 2875 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_pendant.log` | 3548 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_plain.log` | 23225 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_plain_65_80.log` | 2365 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_replay.log` | 6110 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_route.log` | 3019 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_selftest.log` | 573 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_singles.log` | 3052 | 2026-11-12 | `verify/review17.py` | 17 |
| `review17_star.log` | 1383 | 2026-11-12 | `verify/review17.py` | 17 |
| `review19_core16.log` | 1260 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_lemmas16.log` | 265 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_markov15.log` | 215 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_n13_allrows_a.log` | 881 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_n13_allrows_b.log` | 880 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_n13_arith.log` | 3203 | 2026-11-12 | `verify/review19_n13_arith.py` | 19 |
| `review19_n13_census.log` | 288 | 2026-11-12 | `verify/review19_n13_census.py` | 19 |
| `review19_n13_evid.log` | 1279 | 2026-11-12 | `verify/review19_n13_evid.py` | 19 |
| `review19_n13_family.log` | 3258 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_n13_lowcert_10.log` | 487 | 2026-11-12 | `verify/review19_n13_lowcert.py` | 19 |
| `review19_n13_lowcert_1_3.log` | 2043 | 2026-11-12 | `verify/review19_n13_lowcert.py` | 19 |
| `review19_n13_lowcert_4_5.log` | 919 | 2026-11-12 | `verify/review19_n13_lowcert.py` | 19 |
| `review19_n13_lowcert_6.log` | 466 | 2026-11-12 | `verify/review19_n13_lowcert.py` | 19 |
| `review19_n13_lowcert_7_8.log` | 939 | 2026-11-12 | `verify/review19_n13_lowcert.py` | 19 |
| `review19_n13_lowcert_9.log` | 471 | 2026-11-12 | `verify/review19_n13_lowcert.py` | 19 |
| `review19_n13_lowh_10.log` | 1576 | 2026-11-12 | `verify/review19_n13_lowh.py` | 19 |
| `review19_n13_lowh_1_7.log` | 5331 | 2026-11-12 | `verify/review19_n13_lowh.py` | 19 |
| `review19_n13_lowh_8.log` | 1559 | 2026-11-12 | `verify/review19_n13_lowh.py` | 19 |
| `review19_n13_lowh_9.log` | 1563 | 2026-11-12 | `verify/review19_n13_lowh.py` | 19 |
| `review19_n13_lowh_9b.log` | 899 | 2026-11-12 | `verify/review19_n13_lowh.py` | 19 |
| `review19_n13_samples_random.log` | 1779 | 2026-11-12 | `verify/review19_n13_samples.py` | 19 |
| `review19_n13_samples_random20k.log` | 1808 | 2026-11-12 | `verify/review19_n13_samples.py` | 19 |
| `review19_n13_samples_random60k.log` | 1840 | 2026-11-12 | `verify/review19_n13_samples.py` | 19 |
| `review19_n13_samples_resolve.log` | 1470 | 2026-11-12 | `verify/review19_n13_samples.py` | 19 |
| `review19_n13_samples_run.log` | 346 | 2026-11-12 | `verify/review19_n13_samples.py` | 19 |
| `review19_n13_samples_run_all.log` | 353 | 2026-11-12 | `verify/review19_n13_samples.py` | 19 |
| `review19_n13_soundness.log` | 207 | 2026-11-12 | `verify/review19_n13_soundness.py` | 19 |
| `review19_n13_units.log` | 2869 | 2026-11-12 | `verify/review19_n13_units.py` | 19 |
| `review19_n14a_cosq.log` | 3824 | 2026-11-12 | `verify/review19_n14a_cosq.py` | 19 |
| `review19_n14a_cosq2_acyclic.log` | 4021 | 2026-11-12 | `verify/review19_n14a_cosq2.py` | 19 |
| `review19_n14a_cosq2_complete.log` | 2660 | 2026-11-12 | `verify/review19_n14a_cosq2.py` | 19 |
| `review19_n14a_example.log` | 601 | 2026-11-12 | `verify/review19_n14a_example.py` | 19 |
| `review19_n14a_gk.log` | 19158 | 2026-11-12 | `verify/review19_n14a_gk.py` | 19 |
| `review19_n14a_gksym.log` | 1950 | 2026-11-12 | `verify/review19_n14a_gksym.py` | 19 |
| `review19_n14a_mono.log` | 863 | 2026-11-12 | `verify/review19_n14a_mono.py` | 19 |
| `review19_n14a_mono_r6.log` | 866 | 2026-11-12 | `verify/review19_n14a_mono.py` | 19 |
| `review19_n14a_pockets.log` | 10601 | 2026-11-12 | `verify/review19_n14a_pockets.py` | 19 |
| `review19_n14a_pockets_big.log` | 98151 | 2026-11-12 | `verify/review19_n14a_pockets.py` | 19 |
| `review19_n14a_preds.log` | 1096 | 2026-11-12 | `verify/review19_n14a_preds.py` | 19 |
| `review19_n14b_cores.log` | 600 | 2026-11-12 | `verify/review19_n14b_cores.py` | 19 |
| `review19_n14b_counts.log` | 3864 | 2026-11-12 | `verify/review19_n14b_counts.py` | 19 |
| `review19_n14b_counts_time.log` | 757 | 2026-11-12 | `verify/review19_n14b_counts.py` | 19 |
| `review19_n14b_full.log` | 682 | 2026-11-12 | `verify/review19_n14b_full.py` | 19 |
| `review19_n14b_fullsum.log` | 1098 | 2026-11-12 | `verify/review19_n14b_fullsum.py` | 19 |
| `review19_n14b_mono.log` | 197 | 2026-11-12 | `verify/review19_n14b_mono.py` | 19 |
| `review19_n14b_prefork_control.log` | 173 | 2026-11-12 | `verify/review19_n14b_prefork.py` | 19 |
| `review19_n14b_prefork_r7.log` | 441 | 2026-11-12 | `verify/review19_n14b_prefork.py` | 19 |
| `review19_n14b_prefork_r8.log` | 436 | 2026-11-12 | `verify/review19_n14b_prefork.py` | 19 |
| `review19_n14b_probe.log` | 504 | 2026-11-12 | `verify/review19_n14b_probe.py` | 19 |
| `review19_n14b_single.log` | 332 | 2026-11-12 | `verify/review19_n14b_single.py` | 19 |
| `review19_n14b_tubecert.log` | 103 | 2026-11-12 | `verify/review19_n14b_tubecert.py` | 19 |
| `review19_n14b_tubecheck_0.log` | 15824 | 2026-11-12 | `verify/review19_n14b_tubecheck.py` | 19 |
| `review19_n14b_tubecheck_1.log` | 15800 | 2026-11-12 | `verify/review19_n14b_tubecheck.py` | 19 |
| `review19_n14b_tubecheck_2.log` | 15593 | 2026-11-12 | `verify/review19_n14b_tubecheck.py` | 19 |
| `review19_n14b_tubecontrol.log` | 725 | 2026-11-12 | `verify/review19_n14b_tubecontrol.py` | 19 |
| `review19_n14b_tubeplat.log` | 321 | 2026-11-12 | `verify/review19_n14b_tubeplat.py` | 19 |
| `review19_n14b_units.log` | 119 | 2026-11-12 | `verify/review19_n14b_units.py` | 19 |
| `review19_orbits.log` | 1053 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_pf15.log` | 181 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_records16.log` | 765 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_route16.log` | 32 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_search15.log` | 7542 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_search16.log` | 18777 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_search16_small.log` | 3075 | 2026-11-12 | `verify/review19.py` | 19 |
| `review19_vb.log` | 186 | 2026-11-12 | `verify/review19.py` | 19 |
| `review23_lead_n20_xmove.log` | 2666 | 2026-11-14 | `verify/review23_lead_n20_xmove.py` | 23 |
| `review23_lead_n21_mask.log` | 2389 | 2026-11-14 | `verify/review23_lead_n21_mask.py` | 23 |
| `review23_lead_n22_lemmas.log` | 751 | 2026-11-14 | `verify/review23_lead_n22.py` | 23 |
| `review23_lead_n22_markov.log` | 1598 | 2026-11-14 | `verify/review23_lead_n22.py` | 23 |
| `review23_lead_n22_side.log` | 6412 | 2026-11-14 | `verify/review23_lead_n22.py` | 23 |
| `review23_n20_checks_all.log` | 5797 | 2026-11-14 | `verify/review23_n20_checks.py` | 23 |
| `review23_n20_distinct.log` | 594 | 2026-11-14 | `verify/review23_*.py` | 23 |
| `review23_n20_ends.log` | 568 | 2026-11-14 | `verify/review23_n20_ends.py` | 23 |
| `review23_n20_exits.log` | 130 | 2026-11-14 | `verify/review23_*.py` | 23 |
| `review23_n20_lines_a15_20.log` | 3626 | 2026-11-14 | `verify/review23_*.py` | 23 |
| `review23_n20_lines_a2_14.log` | 7189 | 2026-11-14 | `verify/review23_*.py` | 23 |
| `review23_n20_region_forkless.log` | 2571 | 2026-11-14 | `verify/review23_*.py` | 23 |
| `review23_n20_search_classes_nopruning.jsonl` | 15451 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_classes_nopruning.log` | 4319 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_classes_nopruning_a32.log` | 257 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_classes_pruned.jsonl` | 20184 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_classes_pruned.log` | 5725 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_classes_pruned_a36.log` | 262 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_classes_pruned_a40.log` | 262 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_labelled_nopruning.jsonl` | 12535 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_labelled_nopruning.log` | 2609 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_labelled_pruned.jsonl` | 17175 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_search_labelled_pruned.log` | 3706 | 2026-11-14 | `verify/review23_n20_runs.py, review23_n20_search.c` | 23 |
| `review23_n20_xmove.log` | 869 | 2026-11-14 | `verify/review23_n20_xmove.py` | 23 |
| `review23_n21_attack.log` | 23719 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_attackrows.log` | 8190 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_generic_large.log` | 9382 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_generic_small.log` | 9067 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_jsonl.log` | 14695 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_longreplay.log` | 836 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_perturb.log` | 2193 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_rows.log` | 2418 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_rows_escape.log` | 232 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_rwalk.log` | 590 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_selftest.log` | 1603 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_shortest_a.log` | 6510 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n21_shortest_qa.log` | 2801 | 2026-11-14 | `verify/review23_n21_review.py` | 23 |
| `review23_n22_bottoms.log` | 552 | 2026-11-14 | `verify/review23_n22_bottoms.py` | 23 |
| `review23_n22_c1034.log` | 1584 | 2026-11-14 | `verify/review23_n22_c1034.py` | 23 |
| `review23_n22_counts.log` | 3996 | 2026-11-14 | `verify/review23_n22_counts.py` | 23 |
| `review23_n22_engine.log` | 65833 | 2026-11-14 | `verify/review23_n22_engine.py` | 23 |
| `review23_n22_engine_500677.log` | 666 | 2026-11-14 | `verify/review23_n22_engine_500677.py` | 23 |
| `review23_n22_engine_highlam.log` | 3088 | 2026-11-14 | `verify/review23_n22_engine_highlam.py` | 23 |
| `review23_n22_engine_retry.log` | 513 | 2026-11-14 | `verify/review23_n22_engine_retry.py` | 23 |
| `review23_n22_markovC.log` | 212 | 2026-11-14 | `verify/review23_n22_markovC.py` | 23 |
| `review23_n22_rank3.log` | 995 | 2026-11-14 | `verify/review23_n22_rank3.py` | 23 |
| `review23_n22_regen14.jsonl.gz` | 6487554 | 2026-11-17 | `verify/review23_n22_regen14.py` | 23 |
| `review23_n22_regen14.log` | 173 | 2026-11-14 | `verify/review23_n22_regen14.py` | 23 |
| `review23_n22_selftest.log` | 329 | 2026-11-14 | `verify/review23_n22_selftest.py` | 23 |
| `review23_n22_shapes.log` | 4121 | 2026-11-14 | `verify/review23_n22_shapes.py` | 23 |
| `review23_n22_tubes2.log` | 624 | 2026-11-14 | `verify/review23_n22_tubes2.py` | 23 |
| `traps_n4_B4096.jsonl` | 843903 | 2026-11-09 | `traps.py` | 5 |
| `traps_n4_B4096.log` | 4126 | 2026-11-09 | `traps.py` | 5 |
| `traps_n5_B2048.jsonl` | 940803 | 2026-11-09 | `traps.py` | 5 |
| `traps_n5_B2048.log` | 4174 | 2026-11-09 | `traps.py` | 5 |
| `traps_n5_B512.jsonl` | 9900447 | 2026-11-09 | `traps.py` | 5 |
| `traps_n5_B512.log` | 4498 | 2026-11-09 | `traps.py` | 5 |
| `traps_n6_B128.jsonl` | 205650 | 2026-11-09 | `traps.py` | 5 |
| `traps_n6_B128.log` | 3073 | 2026-11-09 | `traps.py` | 5 |
| `traps_n7_B48.jsonl` | 55918 | 2026-11-09 | `traps.py` | 5 |
| `traps_n7_B48.log` | 2155 | 2026-11-09 | `traps.py` | 5 |
| `traps_pairs_n5_B512.jsonl` | 1393915 | 2026-11-09 | `traps.py` | 5 |
| `traps_pairs_n5_B512.log` | 300 | 2026-11-09 | `traps.py` | 5 |
| `traps_pairs_n6_B128.jsonl` | 914594 | 2026-11-09 | `traps.py` | 5 |
| `traps_pairs_n6_B128.log` | 299 | 2026-11-09 | `traps.py` | 5 |
| `traps_sparse_n5_B512.jsonl` | 909564 | 2026-11-09 | `traps.py` | 5 |
| `traps_sparse_n5_B512.log` | 2053 | 2026-11-09 | `traps.py` | 5 |
