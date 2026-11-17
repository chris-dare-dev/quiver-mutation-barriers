# The runner protocol

`taskbatch` schedules tasks and keeps records. It does no computing of its own: a repository that uses it supplies a **runner**, a command with two sub-commands, and the scheduler talks to it through its command line and its standard output. This page is the whole contract between the two.

## What belongs to whom

| The scheduler (`taskbatch/`, the same in every repository) | The repository |
|---|---|
| reads the batch file: `name`, `[scheduler]`, `[limits]`, and the `limits` of each `[[tasks]]` table | the runner command, which knows what a task is and how to compute it |
| asks the runner for the tasks of a batch, orders them by cost, gives each its limits | the batch files in `batches/`: which task sets, with which parameters |
| starts one process per task, enforces the time and memory limits, keeps the memory budget | the task kinds, their predicted values and whatever registry maps tasks to claims |
| writes one record per task, skips recorded tasks on a rerun, prints reports | the `[tool.taskbatch]` table of `pyproject.toml` |

The repository's settings are two keys, both optional:

```toml
[tool.taskbatch]
runner = ["{python}", "-I", "runners/task_runner.py"]   # default for --runner
description_keys = []                                    # batch-file keys that belong to the runner
```

`{python}` is the interpreter running the scheduler; an argument that names a file of the repository is made absolute. `description_keys` lists the top-level keys of a batch file, other than `tasks`, that the scheduler passes to the runner without reading them (a repository whose batch files also list the objects to compute on would name that key here). Any other unknown key in a batch file is refused.

## `expand`: from a batch description to tasks

```
<runner> expand '<description>'
```

The description is one JSON object: every `[[tasks]]` table of the batch file in order, under the key `tasks`, each without its `limits`; and each of the repository's description keys, an absent one as an empty array. The scheduler reads none of it except that each task set has a `kind`.

The runner prints, on its standard output, one line per task and then one closing line:

```
@task {"id": "barrier/R/8", "kind": "barrier", "set": 0, "group": "barrier R", "cost": 8, …}
@meta {"tasks": 1, "python": "3.12.14", "core": "1.0"}
```

and exits with status 0. Other lines are ignored. `@meta` must give the number of tasks as `tasks`; its other keys are the runner's versions and are stamped on every record as `runner`. The expansion is refused if the count is wrong, if two tasks share an id, if the runner exits with another status (its last lines that mention an error are shown) or if it takes more than ten minutes.

The scheduler reads five fields of a task. Everything else is the runner's and is handed back unchanged.

| Field | Type | Default | Use |
|---|---|---|---|
| `id` | string | required | names the task in records and reports; unique in the batch; a task with a record is not computed again |
| `kind` | string | required | default for `group` |
| `cost` | number | 0 | tasks start cheapest first; `[[limits.tier]]` tables give limits by cost. A hint, not an estimate of time |
| `set` | integer | 0 | index of the `[[tasks]]` table the task came from, which selects that table's own `limits` |
| `group` | string | `kind` | the row of the report's summary the task is counted in |

A task may carry `predicted`; it is copied into the record when the result gives none.

## `run`: one task, one result

```
<runner> run '<task>'
```

The task is the JSON object of its `@task` line, unchanged. The process runs in the repository root with no standard input, as the leader of a process group of its own; its standard output and error go to one log file. It may be killed at any moment, without warning, when it reaches a limit or when the scheduler stops. It must not rely on cleaning up after itself.

The runner prints one line and exits with status 0:

```
@result {"status": "ok", "value": 101, "predicted": 101, "agrees": true, "method": "least-height-first search"}
```

If it prints several, the last counts. The scheduler reads four fields; every other key is stored under `detail` in the record (`detail.method` is shown by `report --full`).

| Field | Meaning |
|---|---|
| `status` | `ok`: a value was computed and agrees with the predicted one, or there is none. `mismatch`: computed and different. `unsupported`: the runner has no method for this task |
| `value` | what was computed, any JSON value |
| `predicted` | what was expected, in the same shape |
| `agrees` | `true`, `false`, or `null` when nothing is predicted |

The runner decides only those three statuses. The scheduler decides the others from what happened to the process:

| What happened | Status |
|---|---|
| a result line with one of the three statuses, exit status 0 | that status |
| wall time over the limit; the scheduler kills the process | `timeout` |
| over the memory limit (killed by the control group, or by the scheduler when it polls) | `memory` |
| exit status above 0 | `error`, with the last lines of the log that mention an error (lines containing `--back trace--` are dropped) |
| ended by a signal for another reason, or exit status 0 without a readable result line | `crashed` |

## Records

One JSON object per task that ended, appended to `results.jsonl` of the run directory in a single write: `task_id`, `task` (the payload), `status`, `value`, `predicted`, `agrees`, `detail`, `error`, `wall_seconds`, `cpu_seconds`, `peak_rss_mb`, `limits`, `memory_guard`, `exit_code`, `exit_signal`, `started_at`, `log`, and the stamp of the run: `run_id`, `runner` (the versions of `@meta`) and `code` (the git commit of the repository and whether the working tree differed from it).

## Using the scheduler in another repository

Copy the directory `taskbatch/` and the scheduler's tests (`tests/fake_runner.py`, `helpers.py`, `test_cli.py`, `test_config.py`, `test_report.py`, `test_runner.py`, `test_scheduler.py`, `test_settings.py`, `test_store.py`), add the `[tool.taskbatch]` table, and write a runner. The package was first written for another repository of the same author, whose runner is in another language. The protocol is the same, and what was specific to that repository (one batch-file key and the default runner) became the two settings above.
