# Scripts

The scripts behind the notes ([../docs/README.md](../docs/README.md) says which script belongs to which note). Each script's docstring lists its sub-commands; each note's *Reproduce* section gives the exact commands for its results. The checking scripts are in [../verify/](../verify/README.md).

## Running

- From this directory, as `python -I SCRIPT …` (`-I` isolates the interpreter from the environment; the scripts add their own directory to the module path).
- Interpreter and packages: CPython 3.12 and `requirements.txt` (numpy 2.5.4, cypari2 2.2.4). cypari2 is needed only by `n4_opposite.py fn`. The certificate programs need no package: `n4_doors.py` (except `selftest`), `n4_doors_readable.py`, `np_corridor_prove.py`, `np_corridor_members.py`.
- The stored results unpack into this directory ([../DATA.md](../DATA.md)). Most commands overwrite their output files or write to standard output; rerun them in a copy if you want to compare with the stored files.
- Quivers are tuples of the entries above the diagonal of the exchange matrix, row by row: (b01, b02, b03, b12, b13, b23) on four vertices, ten entries on five. b_ij > 0 means b_ij arrows i → j. Height is the largest absolute entry. Quivers are compared up to relabelling of the vertices.
- Sampling: most sub-commands that sample take a `--seed` option with a fixed default, or seed with a constant. The scripts were not audited one by one for this, so a rerun of a sampling command can differ from the stored file in its sample. The certificates and the exhaustive searches use no randomness.

## The C programs

| Source | Built by | Binary | Used by |
|---|---|---|---|
| `np_barrier.c` | `python -I np_corridor.py build` (runs `gcc -O2 -Wall`) | `~/.cache/qmb-np/np_barrier` | `np_corridor.py`, `np_rowwalk.py`, `np_qa_core.py crosscheck`, `owf_barrier.py` |
| `np_qa_core.c` | `python -I np_qa_core.py build` | `~/.cache/qmb-np/np_qa_core` (or the path in `NP_QA_CORE_BIN`) | `np_qa_core.py` |

Both are plain C with no dependency beyond the C library; the build line is also in each file's header. `make build`, from the repository root, compiles the same two files with the same flags (`gcc -O2 -Wall`) into `build/`, where the task runner looks for them; it does not touch `~/.cache/qmb-np/`. They were built with gcc 15 on x86-64 Linux for the stored results, and `np_barrier.c` was rebuilt for this repository (see DATA.md, Verification). `owf_barrier.py` uses a second binary of `np_barrier.c` for eight vertices, `~/.cache/qmb-np/np_barrier8`; the two lines that build it are in the *Reproduce* section of [note 21](../docs/21-barriers-and-the-mutation-path-owf.md). `np_qa_core.py` keeps a cache of regions in `~/.cache/qmb-np/qa_core/` (1.7 GB for the runs of note 20).

## These scripts and the tasks

The scripts here are the programs that produced the stored results, and they are unchanged by the tasks and batches of this repository ([../README.md](../README.md#tasks-batches-and-records)). A task that needs one of them runs it as a program, in an empty scratch directory under `~/.cache/qmb-scratch/` (or `$QMB_SCRATCH`), never in this directory, so nothing here is overwritten. The package `../qmb/` is separate code and is not imported by any script here.

## Files added for this repository

- `n4_doors_readable.py` prints the 30 claims of Theorem 15.13 and the 43 claims of Theorem 15.6 with every symbolic step.
- `np_corridor_members.py` prints the 149 member families of the certificate of Theorem 16.6.

Both wrap the certificate programs without changing them, so they print what was certified.

## Memory and time

The long runs and what the original logs record for them are listed in [../CLAIMS.md](../CLAIMS.md). The largest: `n4_conj55.py run --H 18` (27 minutes, 11 GB), `np_rowwalk.py family` to a = 22 without pruning (35 minutes, 9 GB; about 70 bytes per quiver of the budget), `np_qa_core.py family` to a = 64 (about an hour on 12 workers), `n4_opposite_run.py fn` (up to 4 GB of PARI stack per worker).
