"""This repository's runner: the protocol, the task kinds, and whole batches through the scheduler."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from typing import Any

from qmb import backends, families, search
from qmb.backends import BUILD, BackendError, Unsupported, keep_output, np_barrier
from qmb.quiver import height, opposite, vertices
from qmb.tasks import (
    STAGES,
    TaskError,
    agrees,
    expand_batch,
    parse_conj55_summary,
    parse_counts,
    parse_np_qa_core,
    parse_review17,
    parse_verdict,
    run_task,
)
from taskbatch.cli import EXIT_FAILED, EXIT_LIMITS, EXIT_OK
from taskbatch.config import load_config
from taskbatch.model import Task
from taskbatch.runner import RunnerError, expand
from taskbatch.settings import REPOSITORY, load_settings

RUNNER = (sys.executable, "-I", str(REPOSITORY / "src" / "runners" / "task_runner.py"))
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
        # research/verify/review17.py plain shares no code with qmb; both count the quivers below the barrier
        for t in (2, 3, 4):
            region = search.below(families.p_plus(t), families.barrier_p_plus(t))
            result = run_task(one({"kind": "reach", "family": "P+", "values": [t], "method": "review17"}))
            self.assertEqual((result["status"], result["agrees"]), ("ok", True))
            self.assertEqual(result["value"], {"quivers": region.quivers, "low": region.low})
            self.assertEqual(result["method"], "research/verify/review17.py plain, no pruning")

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

    def test_a_tube_stage_can_be_tried_on_a_sample(self) -> None:
        whole = one({"kind": "tube", "stages": ["tube-certificates-note-14"], "procs": 6})
        self.assertEqual((whole["id"], whole["sample"]), ("tube/tube-certificates-note-14", None))
        self.assertEqual(whole["predicted"], {"classes": 232198, "certified": 225208})
        sample = one({"kind": "tube", "stages": ["tube-certificates-note-14"], "procs": 2, "sample": 150})
        self.assertEqual(
            (sample["id"], sample["sample"]), ("tube/tube-certificates-note-14/sample-of-150", 150)
        )
        self.assertIsNone(sample["predicted"])  # the counts of a sample are not stored anywhere
        with self.assertRaisesRegex(TaskError, "cannot take a sample"):
            expand_batch({"tasks": [{"kind": "core", "stages": ["finite-cores"], "sample": 150}]})
        # the note 14 program ends its run with the summary of what it wrote
        log = "150 classes\nbottom: classes / certified / failed\n  all: 150 / 142 / 8\ncertified: 142; bottom not separated from the fourth members: 0\nwall time: 20s\n"
        self.assertEqual(
            parse_counts(STAGES["tube-certificates-note-14"], log), {"classes": 150, "certified": 142}
        )

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
        # the other two stages, on the lines of their stored logs that count
        log = "6990 classes; second-pass certificates (polynomial families for tau = 2):\ncertified: 2206; with a bottom of the core: 2206; bottom not separated from the fourth members: 0; polynomial families used in 2150\n"
        self.assertEqual(
            parse_counts(STAGES["tube-certificates-note-22"], log), {"classes": 6990, "certified": 2206}
        )
        log = (
            "census classes: 788026; plateau records 788026\n"
            "mirror map: inconsistent components 0; not an involution 0; self-mirror 33124; pairs 377451\n"
            "finite cores 555828; note-14 tube certificates 225208; note-22 certificates 2206; overlap 50/73 0\n"
            "   acyclic bottom         {'classes': 1556, 'self': 332, 'pair': 1224, 'mirror also in the 6,990': 1224, 'mirror in the same kind': 1224}\n"
            "   disconnected           {'classes': 400, 'self': 176, 'pair': 224, 'mirror also in the 6,990': 224, 'mirror in the same kind': 224, 'open pairs (note 14)': 28}\n"
            "   acyclic bottom         {'E cap': 266, 'more than': 4, 'level bound': 1246, 'no periodic base': 40}\n"
            "§6.3: open classes 2828: {'cyclic slow': 2245, 'Markov triangle': 456, 'cyclic linear': 127}\n"
            "   pairwise distinct (finite cores + tube certificates): 783242; covered: 785198\n"
        )
        counts = parse_counts(STAGES["decided-classes"], log)
        assert counts is not None
        self.assertEqual(list(counts), [key for key, _ in STAGES["decided-classes"].counts])
        self.assertEqual(
            (counts["classes"], counts["acyclic_bottom"], counts["disconnected"], counts["decided"]),
            (788026, 1556, 400, 785198),
        )
        self.assertEqual(counts["settled_by_cores_and_tubes"] + 1556 + 400, counts["decided"])
        # a row of np_qa_core.py family, as the program wrote it for a = 3 without pruning
        line = '{"mode": "chain-nofork", "status": "closed", "H": 88, "w": 4, "stored": 885, "passed_through": 3022, "members": 3907, "chain_sum_is_even": true, "longest_chain": 77, "chains_not_alternating": 0, "seeds": 1, "duplicate_seeds": 0, "seeds_at_or_above_H": 0, "exits_member": 2064, "exits_high": 2361, "exits_fork": 0, "forks_of_height_le_w": 0, "members_of_height_le_w": 1, "max_depth": 229, "a": 3, "seconds": 0.0, "ok": true}'
        core = parse_np_qa_core(line)
        self.assertEqual(
            (core.status, core.barrier, core.members, core.low, core.low_forks, core.stored, core.ok),
            ("closed", 88, 3907, 1, 0, 885, True),
        )
        self.assertEqual(core.passed_through + core.stored, core.members)
        self.assertEqual(core.region(88), {"quivers": 3907, "low": 1})
        self.assertIsNone(core.region(89))  # the search was below another barrier than the task's
        for change in ({"status": "cap"}, {"forks_of_height_le_w": 2}):
            self.assertIsNone(parse_np_qa_core(json.dumps(json.loads(line) | change)).region(88))
        row = parse_review17(
            "P+_t t=80 w=6400 H=6512646399: 3054100 quivers reached below H, 1 of height <= w, 9162272 mutations lead to height >= H | no stored row (113.7s)"
        )
        assert row is not None
        self.assertEqual(
            (row.t, row.barrier, row.quivers, row.low, row.leading_above),
            (80, 6512646399, 3054100, 1, 9162272),
        )
        self.assertIsNone(parse_review17("# P+_t, t = 65..80: 36792093 quivers in all"))
        self.assertEqual(
            parse_verdict("checking\n43 claims, ALL CERTIFIED\n"), {"claims": 43, "certified": True}
        )
        self.assertEqual(
            parse_verdict(
                "938 claims, 149 members, ALL CERTIFIED\n\n"
                "exits by verdict: {'fork': 54, 'height': 428, 'member': 161, 'new': 123}\n"
            ),
            {
                "claims": 938,
                "members": 149,
                "certified": True,
                "exits": {"fork": 54, "height": 428, "member": 161, "new": 123},
            },
        )
        self.assertEqual(parse_verdict("30 claims, 2 FAILED\n"), {"claims": 30, "certified": False})
        self.assertIsNone(parse_verdict("no verdict\n"))


def python_search(
    quiver: Any, *, low: int, cap: int, n: int, prune_forks: bool, budget: int
) -> dict[str, Any]:
    """What np_barrier.c prints for one search, from the searches of qmb instead of the C program.

    The join it reports is the one with the opposite quiver, when the cap allows it; else it reports the
    region within the cap.  For small quivers only, and for the tests only: no task can ask for it.
    """
    joined = search.barrier(quiver)
    if joined.level is not None and joined.level <= cap:
        return {
            "status": "found",
            "iso": joined.level,
            "target": list(opposite(quiver)),
            "popped": joined.popped,
            "plateau": search.below(quiver, joined.level).low,
            "forks": 0,
        }
    region = search.below(quiver, cap + 1, prune_forks=prune_forks)
    return {"status": "cap", "popped": region.quivers, "plateau": region.low, "forks": region.forks}


class NpBarrierTasks(unittest.TestCase):
    """The tasks whose method is np_barrier, with the Python search in place of the C program: what they
    ask of the search and what they make of its answer, on a machine without a C compiler too."""

    def searching(self, answer: Any = python_search) -> unittest.mock.MagicMock:
        patcher = unittest.mock.patch.object(backends, "c_search", side_effect=answer)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def test_a_barrier_task_asks_above_the_barrier_and_reports_the_join(self) -> None:
        asked = self.searching()
        for key, values in (("R", [6, 9]), ("Qt", [3]), ("P+", [2, 3]), ("Qa", [2, 3])):
            chosen = families.family(key)
            for value in values:
                with self.subTest(family=key, value=value):
                    quiver, bound = chosen.quiver(value), chosen.barrier(value)
                    table = {"kind": "barrier", "family": key, "values": [value], "method": "np_barrier"}
                    result = run_task(one(table))
                    self.assertEqual(
                        (result["status"], result["value"], result["agrees"]), ("ok", bound, True)
                    )
                    self.assertEqual(
                        (result["method"], result["search_status"]), ("np_barrier.c, no pruning", "found")
                    )
                    self.assertTrue(result["first_other_low_quiver_is_the_opposite"])
                    self.assertEqual(
                        asked.call_args.kwargs,
                        {
                            "low": height(quiver),
                            "cap": 4 * bound + 1024,
                            "n": vertices(quiver),
                            "prune_forks": False,
                            "budget": 6_000_000,
                        },
                    )

    def test_a_reach_task_asks_one_below_the_barrier_and_reports_the_region(self) -> None:
        asked = self.searching()
        for key, value in (("R", 9), ("P+", 3), ("Qa", 2)):
            with self.subTest(family=key, value=value):
                chosen = families.family(key)
                quiver, bound = chosen.quiver(value), chosen.barrier(value)
                result = run_task(
                    one({"kind": "reach", "family": key, "values": [value], "method": "np_barrier"})
                )
                region = search.below(quiver, bound)
                self.assertEqual(result["value"], {"quivers": region.quivers, "low": region.low})
                self.assertEqual(result["search_status"], "cap")
                self.assertEqual(asked.call_args.kwargs["cap"], bound - 1)
        pruned = {"kind": "reach", "family": "R", "values": [9], "method": "np_barrier", "prune_forks": True}
        with self.assertRaisesRegex(TaskError, "counts forks among the quivers reached"):
            run_task(one(pruned))

    def test_a_search_without_the_expected_answer_gives_no_value(self) -> None:
        barrier = one({"kind": "barrier", "family": "P+", "values": [3], "method": "np_barrier"})
        reach = one({"kind": "reach", "family": "P+", "values": [3], "method": "np_barrier"})
        self.assertEqual((barrier["predicted"], reach["predicted"]), (413, {"quivers": 173, "low": 1}))
        counts = {"popped": 7, "plateau": 1, "forks": 0}
        # no other low quiver within the cap
        for status in ("cap", "closed"):
            self.searching(lambda *_, status=status, **__: {"status": status} | counts)
            result = run_task(barrier)
            self.assertEqual((result["status"], result["value"]), ("mismatch", None))
            self.assertEqual(result["search_status"], status)
            self.assertFalse(result["first_other_low_quiver_is_the_opposite"])
        # another low quiver than the opposite is no join with the opposite
        start = families.p_plus(3)
        self.searching(lambda *_, **__: {"status": "found", "iso": 9, "target": list(start)} | counts)
        result = run_task(barrier)
        self.assertEqual((result["status"], result["value"]), ("mismatch", None))
        self.assertFalse(result["first_other_low_quiver_is_the_opposite"])
        # a region is counted only when the search went through all of it and found no other low quiver
        result = run_task(reach)
        self.assertEqual(
            (result["status"], result["value"], result["search_status"]), ("mismatch", None, "found")
        )

    def test_the_32_bit_rule_is_decided_before_any_search(self) -> None:
        asked = self.searching(AssertionError("no search may be started above 32 bits"))
        self.assertGreaterEqual(families.barrier_p_plus(65), 2**31)
        for kind in ("barrier", "reach"):
            result = run_task(one({"kind": kind, "family": "P+", "values": [65], "method": "np_barrier"}))
            self.assertEqual(
                (result["status"], result["value"], result["agrees"]), ("unsupported", None, None)
            )
            self.assertIn("32 bits", result["reason"])
        for cap in (200, 2**31, 2**33):
            with self.assertRaisesRegex(Unsupported, "32 bits"):
                np_barrier(families.p_plus(2), low=4, cap=cap, n=5, barrier=2**31)
        asked.assert_not_called()
        # a cap above 32 bits is lowered for a barrier that fits, and a spent budget is an error
        asked = self.searching()
        found = np_barrier(families.p_plus(2), low=4, cap=2**33, n=5, barrier=51)
        self.assertEqual((found.status, found.iso, asked.call_args.kwargs["cap"]), ("found", 51, 2**31 - 1))
        self.searching(lambda *_, **__: {"status": "budget", "popped": 5, "plateau": 1, "forks": 0})
        with self.assertRaisesRegex(BackendError, "budget of 5 quivers"):
            np_barrier(families.p_plus(3), low=9, cap=2000, n=5, barrier=413, budget=5)


class Stages(unittest.TestCase):
    def test_a_stage_keeps_its_output_only_when_asked(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            work = Path(home) / "scratch" / "tube-x"
            work.mkdir(parents=True)
            (work / "cores.jsonl.gz").write_bytes(b"input")
            (work / "tubes.jsonl.gz").write_bytes(b"output")
            with unittest.mock.patch.dict(os.environ, {"QMB_KEEP": ""}):
                self.assertEqual(keep_output(work, ["cores.jsonl.gz"]), {})
            with unittest.mock.patch.dict(os.environ, {"QMB_KEEP": str(Path(home) / "kept")}):
                digests = keep_output(work, ["cores.jsonl.gz"])
            kept = Path(home) / "kept" / "tube-x"
            self.assertEqual([path.name for path in kept.iterdir()], ["tubes.jsonl.gz"])
            self.assertEqual((kept / "tubes.jsonl.gz").read_bytes(), b"output")
            self.assertEqual(
                digests,
                {"tubes.jsonl.gz": "e0ee8bb50685e05fa0f47ed04203ae953fdfd055f5bd2892ea186504254f8c3a"},
            )


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
        # the back end decides, before any search: unsupported above 2^31 - 1, whatever the cap
        for cap in (200, 2**31, 2**33):
            with self.assertRaisesRegex(Unsupported, "32 bits"):
                np_barrier(families.p_plus(2), low=4, cap=cap, n=5, barrier=2**31)
        # a cap above 32 bits only bounds the search of a barrier that fits
        found = np_barrier(families.p_plus(2), low=4, cap=2**33, n=5, barrier=families.barrier_p_plus(2))
        self.assertEqual((found.status, found.iso), ("found", families.barrier_p_plus(2)))
        # a search that runs out of its budget is an error, not an answer
        with self.assertRaisesRegex(BackendError, "budget"):
            np_barrier(families.p_plus(3), low=9, cap=2000, n=5, barrier=413, budget=5)

    @unittest.skipUnless(HAVE_NUMPY, "numpy is not installed (research/experiments/requirements.txt)")
    def test_np_qa_core_computes_and_does_not_read_a_kept_summary(self) -> None:
        # np_qa_core.py prints the summary it kept under ~/.cache/qmb-np/ when there is one.  Here the home
        # directory holds a kept summary with a wrong count; a task must compute its own
        kept = {
            "mode": "chain", "status": "closed", "H": 88, "w": 4, "stored": 1, "passed_through": 0, "members": 7,
            "chain_sum_is_even": True, "longest_chain": 0, "forks_of_height_le_w": 0, "members_of_height_le_w": 1,
        }  # fmt: skip
        with tempfile.TemporaryDirectory() as home:
            cache = Path(home) / ".cache" / "qmb-np" / "qa_core"
            cache.mkdir(parents=True)
            (cache / "core_a3_chain_single.bin.json").write_text(json.dumps(kept))
            table = {
                "kind": "reach",
                "family": "Qa",
                "values": [3],
                "method": "np_qa_core",
                "prune_forks": True,
            }
            with unittest.mock.patch.dict(
                os.environ, {"HOME": home, "QMB_SCRATCH": str(Path(home) / "scratch")}
            ):
                result = run_task(one(table))
            self.assertEqual((result["status"], result["value"]), ("ok", {"quivers": 1714, "low": 1}))
            self.assertEqual(json.loads((cache / "core_a3_chain_single.bin.json").read_text())["members"], 7)

    @unittest.skipUnless(HAVE_NUMPY, "numpy is not installed (research/experiments/requirements.txt)")
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
        command = [sys.executable, "-m", "taskbatch", verb, f"data/batches/{batch}.toml", "--out", str(out)]
        if verb == "run":
            command += ["--quiet", "--memory-guard", "poll"]
        return subprocess.run(command, capture_output=True, text=True, cwd=REPOSITORY, timeout=300)

    def records(self, out: Path) -> dict[str, dict[str, Any]]:
        lines = (out / "results.jsonl").read_text().splitlines()
        return {record["task_id"]: record for record in map(json.loads, lines)}

    def test_every_batch_file_expands(self) -> None:
        names = sorted(path.stem for path in (REPOSITORY / "data" / "batches").glob("*.toml"))
        self.assertLessEqual({"smoke", "limits-demo", "negative-control"}, set(names))
        self.assertLessEqual({f"section-{n:02d}" for n in (5, 7, 8, 9, 10, 12, 13, 14)}, set(names))
        for name in names:
            with self.subTest(batch=name):
                config = load_config(REPOSITORY / "data" / "batches" / f"{name}.toml")
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
