"""This repository's runner: the protocol, the task kinds, and whole batches through the scheduler."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from qmb import families, search
from qmb.backends import BUILD, BackendError, np_barrier
from qmb.tasks import STAGES, TaskError, agrees, expand_batch, parse_conj55_summary, parse_counts, run_task
from taskbatch.cli import EXIT_FAILED, EXIT_LIMITS, EXIT_OK
from taskbatch.config import load_config
from taskbatch.model import Task
from taskbatch.runner import RunnerError, expand
from taskbatch.settings import REPOSITORY, load_settings

RUNNER = (sys.executable, "-I", str(REPOSITORY / "runners" / "task_runner.py"))
HAVE_C = (BUILD / "np_barrier").is_file() and (BUILD / "np_qa_core").is_file()
HAVE_NUMPY = importlib.util.find_spec("numpy") is not None


def runner(verb: str, request: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*RUNNER, verb, json.dumps(request)], capture_output=True, text=True, cwd=REPOSITORY
    )


def one(table: dict[str, Any]) -> dict[str, Any]:
    (task,) = expand_batch({"tasks": [table]})
    return task


class Protocol(unittest.TestCase):
    def test_the_repository_names_this_runner(self) -> None:
        self.assertEqual(load_settings().runner, RUNNER)

    def test_expand_prints_the_tasks_and_a_closing_line(self) -> None:
        description = {
            "tasks": [
                {"kind": "barrier", "family": "R", "range": [5, 7]},
                {"kind": "conj55", "heights": [2]},
            ]
        }
        done = runner("expand", description)
        self.assertEqual(done.returncode, 0, done.stderr)
        lines = done.stdout.splitlines()
        self.assertTrue(all(line.startswith("@task ") for line in lines[:-1]))
        meta = json.loads(lines[-1].removeprefix("@meta "))
        self.assertEqual(meta["tasks"], 4)
        self.assertIn("python", meta)
        tasks = [json.loads(line.removeprefix("@task ")) for line in lines[:-1]]
        self.assertEqual(
            [task["id"] for task in tasks], ["barrier/R/b=5", "barrier/R/b=6", "barrier/R/b=7", "conj55/h=2"]
        )
        self.assertEqual([task["set"] for task in tasks], [0, 0, 0, 1])
        for task in tasks:
            self.assertLessEqual({"id", "kind", "cost", "set", "group", "predicted", "evidence"}, set(task))

    def test_the_scheduler_reads_the_expansion(self) -> None:
        tasks, versions = expand(RUNNER, {"tasks": [{"kind": "route", "family": "G", "values": [8]}]})
        self.assertEqual(
            [(task.id, task.kind, task.cost, task.group) for task in tasks],
            [("route/G/k=8", "route", 8, "route G_k")],
        )
        self.assertNotIn("tasks", versions)

    def test_run_prints_one_result(self) -> None:
        task = one({"kind": "barrier", "family": "R", "values": [8]})
        done = runner("run", task)
        self.assertEqual(done.returncode, 0, done.stderr)
        result = json.loads(done.stdout.splitlines()[-1].removeprefix("@result "))
        self.assertEqual(
            (result["status"], result["value"], result["predicted"], result["agrees"]), ("ok", 101, 101, True)
        )

    def test_errors_end_with_a_status_and_one_line(self) -> None:
        with self.assertRaisesRegex(RunnerError, "no family 'Z'"):
            expand(RUNNER, {"tasks": [{"kind": "barrier", "family": "Z", "values": [3]}]})
        failed = runner("run", {"id": "x", "kind": "barrier", "family": "Z", "value": 3, "method": "search"})
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(
            failed.stderr.strip(), "task_runner.py: error: no family 'Z'; the families are G, R, Qt, P+, Qa"
        )
        self.assertEqual(failed.stdout, "")
        self.assertEqual(subprocess.run([*RUNNER, "nonsense"], capture_output=True).returncode, 2)


class Kinds(unittest.TestCase):
    def test_predicted_values_and_evidence(self) -> None:
        self.assertEqual(one({"kind": "barrier", "family": "P+", "values": [3]})["predicted"], 413)
        reach = one({"kind": "reach", "family": "R", "values": [8]})
        self.assertEqual(reach["predicted"], {"quivers": 35, "low": 1})
        self.assertEqual(reach["evidence"][0]["file"], "owf_barrier_summary.log")
        route = one({"kind": "route", "family": "R", "values": [8]})
        self.assertEqual(route["predicted"]["mutations"], 37)
        self.assertEqual(route["predicted"]["first_heights"], [8, 24, 40, 56])  # typed from the article
        self.assertEqual(
            one({"kind": "conj55", "heights": [3]})["predicted"], {"quivers": 4317, "reach_acyclic": 2916}
        )
        self.assertIsNone(one({"kind": "reach", "family": "R", "values": [7]})["predicted"])

    def test_each_kind_computes_its_value(self) -> None:
        cases = [
            (
                {"kind": "quiver", "family": "R", "values": [8]},
                {"height": 8, "mutation_heights": [62, 24, 57, 48]},
            ),
            ({"kind": "barrier", "family": "G", "values": [8]}, 56),
            ({"kind": "reach", "family": "P+", "values": [2]}, {"quivers": 157, "low": 1}),
            (
                {"kind": "reach", "family": "Qa", "values": [2], "prune_forks": True},
                {"quivers": 391, "low": 1},
            ),
            (
                {"kind": "route", "family": "R", "values": [8], "method": "shortest"},
                {"mutations": 37, "top": 101},
            ),
            ({"kind": "conj55", "heights": [1]}, {"quivers": 41, "reach_acyclic": 39}),
            ({"kind": "certificate", "names": ["R_b"]}, {"claims": 30, "certified": True}),
            ({"kind": "synthetic", "items": [{"name": "s", "value": 7, "predicted": 7}]}, 7),
        ]
        for table, value in cases:
            with self.subTest(kind=table["kind"]):
                result = run_task(one(table))
                self.assertEqual((result["status"], result["agrees"]), ("ok", True))
                self.assertEqual(result["value"], value)
        route = run_task(one({"kind": "route", "family": "Qa", "values": [3]}))
        self.assertEqual(route["status"], "ok")
        self.assertEqual(route["value"]["mutations"], 312)

    def test_the_second_enumerator_against_the_search_of_the_core(self) -> None:
        # verify/review17.py plain shares no code with qmb; both count the quivers below the barrier
        for t in (2, 3, 4):
            region = search.below(families.p_plus(t), families.barrier_p_plus(t))
            result = run_task(one({"kind": "reach", "family": "P+", "values": [t], "method": "review17"}))
            self.assertEqual((result["status"], result["agrees"]), ("ok", True))
            self.assertEqual(result["value"], {"quivers": region.quivers, "low": region.low})
            self.assertEqual(result["method"], "verify/review17.py plain, no pruning")

    def test_a_wrong_predicted_value_is_a_mismatch(self) -> None:
        table = {"kind": "barrier", "family": "R", "values": [8], "control": {"predicted": 100}}
        task = one(table)
        self.assertEqual(
            (task["id"], task["group"], task["control"]), ("barrier/R/b=8!control", "negative control", True)
        )
        result = run_task(task)
        self.assertEqual(
            (result["status"], result["value"], result["predicted"], result["agrees"]),
            ("mismatch", 101, 100, False),
        )

    def test_agreement_of_tables_is_on_the_predicted_keys(self) -> None:
        self.assertIsNone(agrees(5, None))
        self.assertTrue(agrees({"a": 1, "extra": 2}, {"a": 1}))
        self.assertFalse(agrees({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(agrees({"a": 2}, {"a": 1}))
        self.assertFalse(agrees(None, 3))

    def test_what_cannot_be_expanded_is_refused(self) -> None:
        refused = [
            {"kind": "nonsense"},
            {"kind": "barrier", "family": "R"},
            {"kind": "barrier", "family": "R", "values": [8], "range": [5, 9]},
            {"kind": "barrier", "family": "R", "values": [4]},
            {"kind": "barrier", "family": "R", "values": [8], "method": "magic"},
            {"kind": "barrier", "family": "R", "values": [8], "typo": 1},
            {"kind": "route", "family": "R", "values": [7]},
            {"kind": "route", "family": "Qt", "values": [3]},
            {"kind": "reach", "family": "R", "values": [8], "method": "np_qa_core"},
            {"kind": "reach", "family": "R", "values": [8], "method": "review17"},
            {"kind": "reach", "family": "P+", "values": [3], "method": "review17", "prune_forks": True},
            {"kind": "certificate", "names": ["S_b"]},
            {"kind": "conj55", "heights": [9]},
            {"kind": "census", "stages": ["finite-cores"]},
            {"kind": "barrier", "family": "R", "values": [8], "control": {"wrong": 1}},
        ]
        for table in refused:
            with self.subTest(table=table), self.assertRaises(ValueError):
                expand_batch({"tasks": [table]})
        twice = {"kind": "barrier", "family": "R", "values": [8]}
        with self.assertRaisesRegex(TaskError, "two tasks"):
            expand_batch({"tasks": [twice, twice]})

    def test_the_output_of_the_original_programs_is_read(self) -> None:
        summary = (
            "| h | quivers | connected | acyclic | components of G_h | reach acyclic within h | fail | a | b | counterexamples | undetermined |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|\n"
            "| 3 | 4,317 | 4,276 | 2,299 | 1,192 | 2,916 | 1,401 | 1,363 (578 / 596) | 38 (0 / 0) | 0 | 0 |\n"
            "totals: {'quivers': 5011, 'connected': 4943, 'pass': 3476, 'fail': 1535, 'counterexamples': 0, 'left': 0}\n"
            "failing quivers by certificate (run's first certificate, else resolve's): {'tri': 569, 'cor52': 55}\n"
            "resolve, largest cor52 bound K per height of the representative: {3: (41, 41)} (second entry: h^3 + h^2 + 5)\n"
        )
        found = parse_conj55_summary(summary)
        self.assertEqual(
            found["heights"]["3"],
            {"quivers": 4317, "reach_acyclic": 2916, "fail": 1401, "counterexamples": 0, "undetermined": 0},
        )
        self.assertEqual(found["totals"]["pass"], 3476)
        self.assertEqual(found["failing_by_certificate"], {"tri": 569, "cor52": 55})
        self.assertTrue(found["largest_search_is_h3_h2_5"])
        log = "788026 census classes read (3s)\n  0 (8s)\ntotal: core found 555828, search stopped at a cap 232198 (caps: 800 quivers, level 1000000) (520s)\n"
        self.assertEqual(
            parse_counts(STAGES["finite-cores"], log),
            {"classes": 788026, "finite_cores": 555828, "search_stopped_at_a_cap": 232198},
        )
        self.assertIsNone(parse_counts(STAGES["finite-cores"], "nothing of the kind\n"))


@unittest.skipUnless(HAVE_C, "the C programs are not built (make build)")
class CBackEnds(unittest.TestCase):
    def test_np_barrier_against_the_search_in_python(self) -> None:
        for key, values in (("R", [6, 9]), ("Qt", [3]), ("P+", [2, 3]), ("Qa", [2, 3])):
            chosen = families.family(key)
            for value in values:
                with self.subTest(family=key, value=value):
                    quiver = chosen.quiver(value)
                    barrier = run_task(
                        one({"kind": "barrier", "family": key, "values": [value], "method": "np_barrier"})
                    )
                    self.assertEqual(
                        (barrier["status"], barrier["value"]), ("ok", search.barrier(quiver).level)
                    )
                    self.assertTrue(barrier["first_other_low_quiver_is_the_opposite"])
                    reach = run_task(
                        one({"kind": "reach", "family": key, "values": [value], "method": "np_barrier"})
                    )
                    region = search.below(quiver, chosen.barrier(value))
                    self.assertEqual(reach["value"], {"quivers": region.quivers, "low": region.low})

    def test_a_barrier_above_32_bits_is_unsupported_and_not_a_mismatch(self) -> None:
        # H+(64) = 2,130,710,527 fits in 32 bits and H+(65) = 2,302,734,849 does not: the C search would
        # discard every quiver above 2^31 - 1 and report a part of the region as if it were all of it
        self.assertLess(families.barrier_p_plus(64), 2**31)
        self.assertGreaterEqual(families.barrier_p_plus(65), 2**31)
        for kind in ("barrier", "reach"):
            result = run_task(one({"kind": kind, "family": "P+", "values": [65], "method": "np_barrier"}))
            self.assertEqual(
                (result["status"], result["value"], result["agrees"]), ("unsupported", None, None)
            )
            self.assertIn("32 bits", result["reason"])
        with self.assertRaisesRegex(BackendError, "32 bits"):
            np_barrier(families.p_plus(2), low=4, cap=2**31, n=5)

    @unittest.skipUnless(HAVE_NUMPY, "numpy is not installed (experiments/requirements.txt)")
    def test_the_programs_of_experiments_against_python(self) -> None:
        for prune in (False, True):
            table = {
                "kind": "reach",
                "family": "Qa",
                "values": [3],
                "method": "np_qa_core",
                "prune_forks": prune,
            }
            region = search.below(families.q_a(3), 88, prune_forks=prune)
            result = run_task(one(table))
            self.assertEqual(
                (result["status"], result["value"]), ("ok", {"quivers": region.quivers, "low": region.low})
            )
        program = run_task(one({"kind": "conj55_program", "N": 3, "workers": 1}))
        self.assertEqual(program["status"], "ok")
        self.assertEqual(program["value"]["heights"]["3"]["reach_acyclic"], 2916)
        self.assertEqual(program["value"]["totals"]["counterexamples"], 0)


class Batches(unittest.TestCase):
    """The batch files of the repository, and two of them through the scheduler."""

    def taskbatch(self, verb: str, batch: str, out: Path) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-m", "taskbatch", verb, f"batches/{batch}.toml", "--out", str(out)]
        if verb == "run":
            command += ["--quiet", "--memory-guard", "poll"]
        return subprocess.run(command, capture_output=True, text=True, cwd=REPOSITORY, timeout=300)

    def records(self, out: Path) -> dict[str, dict[str, Any]]:
        lines = (out / "results.jsonl").read_text().splitlines()
        return {record["task_id"]: record for record in map(json.loads, lines)}

    def test_every_batch_file_expands(self) -> None:
        names = sorted(path.stem for path in (REPOSITORY / "batches").glob("*.toml"))
        self.assertLessEqual({"smoke", "limits-demo", "negative-control"}, set(names))
        self.assertLessEqual({f"section-{n:02d}" for n in (5, 7, 8, 9, 10, 12, 13, 14)}, set(names))
        for name in names:
            with self.subTest(batch=name):
                config = load_config(REPOSITORY / "batches" / f"{name}.toml")
                tasks = expand_batch(config.description)
                self.assertTrue(tasks)
                self.assertEqual(config.name, name)
                for task in tasks:
                    self.assertLessEqual(
                        config.limits_for(Task.from_payload(task)).memory_mb, config.memory_budget_mb
                    )

    def test_the_negative_control_ends_in_mismatches_and_status_1(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            done = self.taskbatch("run", "negative-control", Path(scratch))
            self.assertEqual(done.returncode, EXIT_FAILED, done.stderr)
            records = self.records(Path(scratch))
            self.assertEqual(len(records), 3)
            self.assertEqual({record["status"] for record in records.values()}, {"mismatch"})
            self.assertEqual(records["barrier/R/b=8!control"]["value"], 101)
            self.assertEqual(records["barrier/R/b=8!control"]["predicted"], 100)

    def test_the_limits_demo_stops_two_tasks_and_ends_with_status_3(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            done = self.taskbatch("run", "limits-demo", Path(scratch))
            self.assertEqual(done.returncode, EXIT_LIMITS, done.stderr)
            statuses = {task_id: record["status"] for task_id, record in self.records(Path(scratch)).items()}
            self.assertEqual(statuses.pop("synthetic/sleeps-past-its-time-limit"), "timeout")
            self.assertEqual(statuses.pop("synthetic/allocates-past-its-memory-limit"), "memory")
            self.assertEqual(set(statuses.values()), {"ok"})
            # a rerun computes nothing, and the same again with larger limits computes the two that were stopped
            again = self.taskbatch("plan", "limits-demo", Path(scratch))
            self.assertIn("6 tasks, 0 to compute, 6 already recorded", again.stdout)

    def test_a_section_batch_through_the_scheduler(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            done = self.taskbatch("run", "section-08", Path(scratch))
            self.assertEqual(done.returncode, EXIT_OK, done.stderr)
            records = self.records(Path(scratch))
            self.assertEqual({record["status"] for record in records.values()}, {"ok"})
            self.assertEqual(
                (records["barrier/Qt/t=3"]["value"], records["barrier/R/b=9"]["value"]), (132, 132)
            )
            self.assertEqual(records["barrier/R/b=9"]["runner"]["qmb"], "1.0")


if __name__ == "__main__":
    unittest.main()
