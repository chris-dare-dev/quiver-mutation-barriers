"""The scheduler with fake tasks: outcomes, isolation, resumption, ordering, the memory budget."""

from __future__ import annotations

import unittest

from taskbatch.config import ConfigError
from taskbatch.memory import CgroupGuard

from .helpers import SchedulerCase, fake_config

SLEEPER = {"name": "sleeper", "sleep": 60}
HOG = {"name": "hog", "allocate_mb": 400, "sleep": 60}


class Outcomes(SchedulerCase):
    def test_each_way_a_task_can_end_is_recorded(self) -> None:
        config = fake_config(
            [
                {"name": "fine", "value": 7, "predicted": 7},
                {"name": "no-prediction", "value": [1, 0, 1]},
                {"name": "differs", "value": 1, "predicted": 2},
                {"name": "no-method", "unsupported": True, "predicted": 5},
                {"name": "fails", "exit": 3},
                {"name": "segfault", "signal": "SIGSEGV"},
                {"name": "says-nothing", "silent": True},
            ],
            {"items": [SLEEPER], "limits": {"time_seconds": 0.4}},
            [HOG],
        )
        outcome = self.run_batch(config)

        self.assertEqual(
            self.statuses(),
            {
                "fine": "ok",
                "no-prediction": "ok",
                "differs": "mismatch",
                "no-method": "unsupported",
                "fails": "error",
                "segfault": "crashed",
                "says-nothing": "crashed",
                "sleeper": "timeout",
                "hog": "memory",
            },
        )
        self.assertEqual(outcome.total(), 9)
        records = {task_id.removeprefix("fake/"): record for task_id, record in self.latest().items()}

        fine = records["fine"]
        self.assertEqual((fine["value"], fine["predicted"], fine["agrees"]), (7, 7, True))
        self.assertEqual(fine["task"]["name"], "fine")
        self.assertEqual(fine["detail"], {"method": "fake"})
        self.assertEqual(fine["limits"], {"time_seconds": 20, "memory_mb": 100})
        self.assertEqual(fine["runner"], {"fake_version": "1"})
        self.assertEqual(fine["code"], {"commit": "0" * 40, "dirty": False})
        self.assertEqual(fine["memory_guard"], self.guard_class.name)
        self.assertGreater(fine["peak_rss_mb"], 1)
        self.assertGreaterEqual(fine["wall_seconds"], 0)
        self.assertIsNone(fine["log"])

        self.assertEqual(records["no-prediction"]["agrees"], None)
        self.assertEqual((records["differs"]["value"], records["differs"]["agrees"]), (1, False))
        # a task that computed nothing still carries the predicted value it was given
        self.assertEqual(records["no-method"]["predicted"], 5)
        self.assertEqual(records["sleeper"]["predicted"], None)

        self.assertIn("asked to fail", records["fails"]["error"])
        self.assertEqual(records["fails"]["exit_code"], 3)
        self.assertEqual(records["segfault"]["exit_signal"], "SIGSEGV")
        self.assertEqual(records["says-nothing"]["error"], "ended without a result")

        self.assertEqual(records["sleeper"]["exit_signal"], "SIGKILL")
        self.assertLess(records["sleeper"]["wall_seconds"], 5)
        self.assertEqual(records["sleeper"]["limits"]["time_seconds"], 0.4)
        self.assertLess(records["hog"]["wall_seconds"], 20)
        self.assertGreater(records["hog"]["peak_rss_mb"], 50)

        for name in ("fails", "segfault", "says-nothing", "sleeper", "hog"):
            self.assertTrue((self.run_dir / records[name]["log"]).exists(), name)
        self.assertEqual(len(list((self.run_dir / "logs").iterdir())), 5)

    def test_a_killed_task_does_not_lose_the_others(self) -> None:
        quick = [{"name": f"quick-{i}", "sleep": 0.05, "value": i, "predicted": i} for i in range(12)]
        config = fake_config(
            quick[:6],
            {"items": [SLEEPER], "limits": {"time_seconds": 0.3}},
            [HOG],
            quick[6:],
            workers=3,
            memory_budget_mb=300,
        )
        self.run_batch(config)
        statuses = self.statuses()
        self.assertEqual(statuses.pop("sleeper"), "timeout")
        self.assertEqual(statuses.pop("hog"), "memory")
        self.assertEqual(statuses, {f"quick-{i}": "ok" for i in range(12)})


class Resumption(SchedulerCase):
    def test_a_rerun_computes_nothing(self) -> None:
        config = fake_config(
            [{"name": "a"}, {"name": "b", "exit": 1}, {"name": "c", "value": 1, "predicted": 2}],
            {"items": [SLEEPER], "limits": {"time_seconds": 0.3}},
        )
        self.run_batch(config)
        self.assertEqual(len(self.journal.started()), 4)

        outcome = self.run_batch(config)
        self.assertEqual(outcome.total(), 0)
        self.assertEqual(len(self.journal.started()), 4)

    def test_a_rerun_computes_only_what_has_no_record(self) -> None:
        first = [{"name": "a"}, {"name": "b"}]
        self.run_batch(fake_config(first))
        self.run_batch(fake_config([*first, {"name": "c"}, {"name": "d"}]))
        self.assertEqual(sorted(self.journal.started()), ["fake/a", "fake/b", "fake/c", "fake/d"])

    def test_retry_computes_again_the_chosen_statuses_only(self) -> None:
        config = fake_config(
            [{"name": "a"}, {"name": "b", "exit": 1}],
            {"items": [SLEEPER], "limits": {"time_seconds": 0.3}},
        )
        self.run_batch(config)
        outcome = self.run_batch(config, retry={"timeout"})
        self.assertEqual(dict(outcome), {"timeout": 1})
        self.assertEqual(self.journal.started().count("fake/sleeper"), 2)
        self.assertEqual(len(self.journal.started()), 4)
        # both attempts are on record; the latest one counts
        store_lines = (self.run_dir / "results.jsonl").read_text().splitlines()
        self.assertEqual(len(store_lines), 4)


class Scheduling(SchedulerCase):
    def test_cheapest_first_and_the_given_order_among_equals(self) -> None:
        costs = [5, 1, 3, 1, 0, 4, 3]
        items = [{"name": f"t{i}", "cost": cost} for i, cost in enumerate(costs)]
        self.run_batch(fake_config(items, workers=1))
        self.assertEqual(self.journal.started(), [f"fake/t{i}" for i in (4, 1, 3, 2, 6, 5, 0)])

    def test_limits_of_running_tasks_stay_within_the_budget(self) -> None:
        small = [{"name": f"small-{i}", "sleep": 0.3} for i in range(6)]
        large = [{"name": f"large-{i}", "sleep": 0.3, "cost": 10} for i in range(3)]
        config = fake_config(
            small,
            {"items": large, "limits": {"memory_mb": 250}},
            workers=4,
            memory_budget_mb=300,
            memory_mb=100,
        )
        self.run_batch(config)
        limit = {f"fake/small-{i}": 100 for i in range(6)} | {f"fake/large-{i}": 250 for i in range(3)}
        intervals = self.journal.intervals()
        self.assertEqual(len(intervals), 9)
        most_at_once = 0
        for start, _ in intervals.values():
            together = [task for task, (s, e) in intervals.items() if s <= start < e]
            most_at_once = max(most_at_once, len(together))
            self.assertLessEqual(sum(limit[task] for task in together), 300, together)
        # three small tasks fit the budget together; a large one runs alone
        self.assertEqual(most_at_once, 3)

    def test_workers_bound_the_number_of_processes(self) -> None:
        items = [{"name": f"t{i}", "sleep": 0.2} for i in range(6)]
        self.run_batch(fake_config(items, workers=2, memory_budget_mb=10_000))
        intervals = self.journal.intervals()
        for start, _ in intervals.values():
            self.assertLessEqual(sum(1 for s, e in intervals.values() if s <= start < e), 2)

    def test_tiers_give_costly_tasks_their_own_limits(self) -> None:
        items = [{"name": "cheap", "cost": 1}, {"name": "costly", "cost": 30, "sleep": 60}]
        tiers = [{"min_cost": 10, "time_seconds": 0.3, "memory_mb": 200}]
        self.run_batch(fake_config(items, tiers=tiers))
        records = self.latest()
        self.assertEqual(records["fake/cheap"]["limits"], {"time_seconds": 20, "memory_mb": 100})
        self.assertEqual(records["fake/costly"]["limits"], {"time_seconds": 0.3, "memory_mb": 200})
        self.assertEqual(records["fake/costly"]["status"], "timeout")

    def test_a_limit_above_the_budget_is_refused_before_anything_runs(self) -> None:
        config = fake_config([{"name": "a"}], {"items": [{"name": "b"}], "limits": {"memory_mb": 900}})
        with self.assertRaises(ConfigError):
            self.run_batch(config)
        self.assertEqual(self.journal.started(), [])


@unittest.skipUnless(CgroupGuard.available(), "systemd-run --user --scope is not available")
class OutcomesUnderCgroupLimits(Outcomes):
    guard_class = CgroupGuard


if __name__ == "__main__":
    unittest.main()
