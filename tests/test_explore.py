"""A quiver of the reader's own: the task kind "explore", the command python3 -m qmb, the example batch."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
import unittest.mock
from pathlib import Path
from typing import Any

from qmb import families, search
from qmb.kinds import explore
from qmb.tasks import TaskError, expand_batch, run_task
from taskbatch.cli import EXIT_OK
from taskbatch.settings import REPOSITORY

R8 = [-8, -8, 7, -2, 6, -8]
NEAR_R8 = [-8, -8, 7, -2, 6, -7]  # one entry changed: not joined to its opposite at any height near 101
EXAMPLE = REPOSITORY / "examples" / "own-quivers.toml"
SCHEDULER = (sys.executable, "-m", "taskbatch")
QUIETLY = ("--quiet", "--memory-guard", "poll")


def one(table: dict[str, Any]) -> dict[str, Any]:
    (task,) = expand_batch({"tasks": [{"kind": "explore"} | table]})
    return task


def command(*arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "qmb", "explore", *map(str, arguments)],
        capture_output=True,
        text=True,
        cwd=REPOSITORY,
        timeout=120,
    )


class Expansion(unittest.TestCase):
    def test_a_table_is_one_task_named_by_its_entries_or_by_its_name(self) -> None:
        task = one({"quiver": R8})
        self.assertEqual(task["id"], "explore/-8,-8,7,-2,6,-8")
        self.assertEqual((task["quiver"], task["cap"], task["budget"]), (R8, None, explore.BUDGET))
        self.assertEqual((task["predicted"], task["evidence"], task["group"]), (None, [], "explore"))
        named = one({"quiver": R8, "name": "R8", "cap": 200, "budget": 50, "predicted": {"barrier": 101}})
        self.assertEqual(named["id"], "explore/R8")
        self.assertEqual((named["cap"], named["budget"], named["predicted"]), (200, 50, {"barrier": 101}))

    def test_what_is_not_a_quiver_or_a_stop_is_refused(self) -> None:
        refused = [
            {},
            {"quiver": []},
            {"quiver": [1, 2]},  # two entries are no upper triangle
            {"quiver": [1, 2.5, 3]},
            {"quiver": [1, True, 3]},
            {"quiver": "1 2 3"},
            {"quiver": R8, "cap": 7},  # below the height of the quiver
            {"quiver": R8, "cap": "high"},
            {"quiver": R8, "budget": 0},
            {"quiver": R8, "name": "two words"},
            {"quiver": R8, "name": ""},
            {"quiver": R8, "predicted": 101},
            {"quiver": R8, "predicted": {"barier": 101}},
            {"quiver": R8, "family": "R"},
        ]
        for table in refused:
            with self.subTest(table=table), self.assertRaises(TaskError):
                one(table)
        with self.assertRaisesRegex(TaskError, "two tasks"):
            expand_batch({"tasks": [{"kind": "explore", "quiver": R8}] * 2})

    def test_a_negative_control_is_made_as_for_the_other_kinds(self) -> None:
        task = one({"quiver": R8, "name": "R8", "control": {"predicted": {"barrier": 100}}})
        self.assertEqual((task["id"], task["group"]), ("explore/R8!control", "negative control"))
        self.assertEqual(run_task(task)["status"], "mismatch")


class Survey(unittest.TestCase):
    def test_the_running_example_of_the_article(self) -> None:
        result = explore.survey(tuple(R8))
        self.assertEqual(
            result["value"], {"height": 8, "barrier": 101, "quivers": 35, "low": 1, "mutations": 37}
        )
        self.assertEqual((result["vertices"], result["mutation_heights"]), (4, [62, 24, 57, 48]))
        self.assertEqual((result["popped"], result["stopped"]), (68, None))

    def test_it_agrees_with_the_searches_on_the_families(self) -> None:
        cases = [(families.g, 6), (families.r, 9), (families.q_t, 3), (families.p_plus, 3), (families.q_a, 2)]
        for member, parameter in cases:
            quiver = member(parameter)
            with self.subTest(quiver=quiver):
                value = explore.survey(quiver)["value"]
                level = search.barrier(quiver).level
                assert level is not None
                region = search.below(quiver, level)
                found = (value["barrier"], value["quivers"], value["low"])
                self.assertEqual(found, (level, region.quivers, 1))
                self.assertEqual(value["mutations"], search.shortest(quiver, level)[0])

    def test_a_quiver_that_is_its_own_opposite(self) -> None:
        # the Markov quiver: reversing every arrow is the same as exchanging two vertices
        value = explore.survey((2, -2, 2))["value"]
        self.assertEqual(value, {"height": 2, "barrier": 2, "quivers": 1, "low": 1, "mutations": 0})

    def test_a_cap_or_a_budget_gives_a_bound_and_no_barrier(self) -> None:
        capped = explore.survey(tuple(NEAR_R8), cap=1000)
        self.assertEqual(capped["value"], {"height": 8, "no_route_up_to": 1000})
        self.assertEqual(capped["stopped"], "cap")
        # the bound is true: the quivers reached through heights at most 1000 do not hold the opposite
        self.assertFalse(search.below(NEAR_R8, 1001).has_opposite)
        spent = explore.survey(tuple(NEAR_R8), budget=200)
        self.assertEqual((spent["stopped"], spent["popped"]), ("budget", 200))
        self.assertFalse(search.below(NEAR_R8, spent["value"]["no_route_up_to"] + 1).has_opposite)
        self.assertEqual(set(spent["value"]), {"height", "no_route_up_to"})

    def test_the_budget_also_ends_the_search_for_a_shortest_route(self) -> None:
        # 68 quivers find the barrier of R_8; the shortest route at the barrier passes more than 68
        value = explore.survey(tuple(R8), budget=68)["value"]
        self.assertEqual(value, {"height": 8, "barrier": 101, "quivers": 35, "low": 1})

    def test_a_class_seen_whole_without_the_opposite(self) -> None:
        # no small quiver of this kind is known here, so the search is replaced by its answer
        whole = search.Barrier(level=None, popped=14, cleared=None)
        with unittest.mock.patch.object(search, "barrier", return_value=whole):
            result = explore.survey((1, 0, 1))
        self.assertEqual(result["value"], {"height": 1, "whole_class": 14})
        self.assertIsNone(result["stopped"])
        self.assertIn("the mutation class has 14 quivers", "\n".join(explore.lines(result)))


class Statuses(unittest.TestCase):
    def test_without_a_prediction_the_task_is_ok_and_agrees_with_nothing(self) -> None:
        for table in ({"quiver": R8}, {"quiver": NEAR_R8, "cap": 1000}):
            result = run_task(one(table))
            self.assertEqual((result["status"], result["agrees"], result["predicted"]), ("ok", None, None))
            self.assertIsNotNone(result["value"])

    def test_a_prediction_is_compared_on_its_own_keys(self) -> None:
        right = run_task(one({"quiver": R8, "predicted": {"barrier": 101, "mutations": 37}}))
        self.assertEqual((right["status"], right["agrees"]), ("ok", True))
        wrong = run_task(one({"quiver": R8, "predicted": {"barrier": 100}}))
        self.assertEqual((wrong["status"], wrong["agrees"]), ("mismatch", False))
        bound = run_task(one({"quiver": NEAR_R8, "cap": 1000, "predicted": {"no_route_up_to": 1000}}))
        self.assertEqual(bound["status"], "ok")

    def test_a_predicted_barrier_that_the_search_did_not_reach_is_a_mismatch(self) -> None:
        result = run_task(one({"quiver": NEAR_R8, "cap": 1000, "predicted": {"barrier": 101}}))
        self.assertEqual((result["status"], result["agrees"]), ("mismatch", False))


class Command(unittest.TestCase):
    def test_it_says_what_it_found(self) -> None:
        done = command(*R8)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(
            done.stdout.splitlines(),
            [
                "quiver    (-8, -8, 7, -2, 6, -8) on 4 vertices, of height 8",
                "mutation  at each vertex in turn gives heights 62, 24, 57, 48",
                "barrier   101: the opposite is reached through heights at most 101, and not below",
                "below it  35 quivers up to relabelling, the start included; 1 of height at most 8",
                "route     37 mutations at the least, staying at or below 101",
                "searched  68 quivers, taken in order of height",
            ],
        )

    def test_a_stopped_search_says_what_it_excludes_and_why(self) -> None:
        capped = command(*NEAR_R8, "--cap", 1000)
        self.assertEqual(capped.returncode, 0, capped.stderr)
        self.assertIn("not found: no route to the opposite stays at or below height 1000", capped.stdout)
        self.assertIn("the cap of 1000 left quivers out", capped.stdout)
        spent = command(*NEAR_R8, "--budget", 200)
        self.assertIn("stopped at its budget of 200 quivers", spent.stdout)
        self.assertIn("a higher route is not excluded", spent.stdout)

    def test_json_is_what_the_task_computes(self) -> None:
        printed = json.loads(command(*R8, "--json").stdout)
        self.assertEqual(printed, explore.survey(tuple(R8)))
        as_task = run_task(one({"quiver": R8}))
        self.assertEqual(printed, {key: as_task[key] for key in printed})

    def test_what_is_not_a_quiver_ends_with_status_2_and_one_line(self) -> None:
        for arguments in ([1, 2, 3, 4], [1, 1, 1, "--cap", 0], [1, 1, 1, "--budget", 0]):
            done = command(*arguments)
            self.assertEqual((done.returncode, done.stdout), (2, ""))
            self.assertEqual(len(done.stderr.splitlines()), 1)
            self.assertTrue(done.stderr.startswith("python3 -m qmb: error: "))


class Guide(unittest.TestCase):
    def test_the_commands_of_the_guide_print_what_the_guide_shows(self) -> None:
        text = (REPOSITORY / "GUIDE.md").read_text(encoding="utf-8")
        block = r"```bash\npython3 -m qmb explore ([^\n]+)\n```\n\n```text\n(.*?)```"
        shown = re.findall(block, text, re.DOTALL)
        self.assertEqual(len(shown), 2)
        for arguments, output in shown:
            with self.subTest(arguments=arguments):
                self.assertEqual(command(*arguments.split()).stdout, output)

    def test_the_readme_names_a_command_that_runs(self) -> None:
        text = (REPOSITORY / "README.md").read_text(encoding="utf-8")
        (arguments,) = re.findall(r"^python3 -m qmb explore ([-0-9 ]+?) +#", text, re.MULTILINE)
        self.assertEqual(command(*arguments.split()).returncode, 0)
        self.assertIn("(GUIDE.md#a-quiver-of-your-own)", text)
        self.assertIn("\n## A quiver of your own\n", (REPOSITORY / "GUIDE.md").read_text(encoding="utf-8"))


class Example(unittest.TestCase):
    def test_the_example_is_outside_the_batches_of_the_claims(self) -> None:
        # every task of batches/ must belong to a claim; a reader's quivers belong to none
        description = tomllib.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual({table["kind"] for table in description["tasks"]}, {"explore"})
        for path in (REPOSITORY / "batches").glob("*.toml"):
            tables = tomllib.loads(path.read_text(encoding="utf-8")).get("tasks", [])
            self.assertNotIn("explore", {table["kind"] for table in tables}, path.name)

    def test_the_example_through_the_scheduler(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            done = subprocess.run(
                [*SCHEDULER, "run", str(EXAMPLE.relative_to(REPOSITORY)), "--out", scratch, *QUIETLY],
                capture_output=True,
                text=True,
                cwd=REPOSITORY,
                timeout=300,
            )
            self.assertEqual(done.returncode, EXIT_OK, done.stderr)
            lines = (Path(scratch) / "results.jsonl").read_text().splitlines()
            records = {record["task_id"]: record for record in map(json.loads, lines)}
        self.assertEqual({record["status"] for record in records.values()}, {"ok"})
        self.assertEqual(records["explore/R8"]["agrees"], True)
        self.assertEqual(records["explore/R8-last-entry-7"]["value"], {"height": 8, "no_route_up_to": 1000})
        self.assertEqual(
            records["explore/3,-2,2,-1,3,-3"]["value"],
            {"height": 3, "barrier": 10, "quivers": 8, "low": 1, "mutations": 16},
        )
        self.assertEqual(records["explore/stopped-by-budget"]["detail"]["stopped"], "budget")


if __name__ == "__main__":
    unittest.main()
