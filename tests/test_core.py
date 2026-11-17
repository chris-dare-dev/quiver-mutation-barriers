"""The core against values computed by hand or printed in the article."""

from __future__ import annotations

import itertools
import random
import unittest

from qmb import conj55, families, search
from qmb.quiver import (
    canonical,
    fork_point,
    from_arrows,
    from_matrix,
    height,
    is_acyclic,
    isomorphic,
    matrix,
    mutate,
    mutate_matrix,
    opposite,
    relabel,
    vertices,
)

R8 = (-8, -8, 7, -2, 6, -8)


class Mutation(unittest.TestCase):
    def test_the_worked_example_of_the_article(self) -> None:
        # R_8 at vertex 0: the paths 1 -> 0 -> 3 and 2 -> 0 -> 3 add 8 * 7 = 56 to b13 = 6 and to b23 = -8;
        # b12 keeps its two arrows, because 1 and 2 both point into 0
        self.assertEqual(families.r(8), R8)
        self.assertEqual(mutate(R8, 0), (8, 8, -7, -2, 62, 48))
        self.assertEqual([height(mutate(R8, k)) for k in range(4)], [62, 24, 57, 48])

    def test_small_quivers_by_hand(self) -> None:
        self.assertEqual(mutate((1,), 0), (-1,))  # one arrow, reversed
        # the Markov quiver 0 -> 1 -> 2 -> 0 with double arrows: at 1 the path 0 -> 1 -> 2 adds 4 to b02 = -2
        self.assertEqual(mutate((2, -2, 2), 1), (-2, 2, -2))
        # a path 0 -> 1 -> 2 with single arrows: mutation at the middle creates the arrow 0 -> 2
        self.assertEqual(mutate((1, 0, 1), 1), (-1, 1, -1))
        # a source or a sink: only the arrows at the vertex turn round
        self.assertEqual(mutate((3, 5, 7), 0), (-3, -5, 7))

    def test_mutation_is_an_involution_and_agrees_with_the_definition(self) -> None:
        rng = random.Random(1)
        for n in (2, 3, 4, 5):
            for _ in range(200):
                quiver = tuple(rng.randint(-9, 9) for _ in range(n * (n - 1) // 2))
                k = rng.randrange(n)
                self.assertEqual(mutate(quiver, k), from_matrix(mutate_matrix(matrix(quiver), k)))
                self.assertEqual(mutate(mutate(quiver, k), k), quiver)

    def test_a_tuple_is_the_upper_triangle_of_a_skew_symmetric_matrix(self) -> None:
        rows = matrix(R8)
        self.assertEqual(rows[0], [0, -8, -8, 7])
        self.assertTrue(all(rows[i][j] == -rows[j][i] for i in range(4) for j in range(4)))
        self.assertEqual(from_matrix(rows), R8)
        self.assertEqual([vertices((0,) * m) for m in (1, 3, 6, 10)], [2, 3, 4, 5])
        with self.assertRaises(ValueError):
            vertices((0, 0))


class Relabelling(unittest.TestCase):
    def test_the_canonical_form_does_not_depend_on_the_labels(self) -> None:
        rng = random.Random(2)
        for n in (3, 4, 5):
            quiver = tuple(rng.randint(-6, 6) for _ in range(n * (n - 1) // 2))
            forms = {canonical(relabel(quiver, sigma)) for sigma in itertools.permutations(range(n))}
            self.assertEqual(len(forms), 1)
            self.assertEqual(relabel(quiver, tuple(range(n))), quiver)

    def test_mutation_commutes_with_relabelling_and_with_reversing_the_arrows(self) -> None:
        sigma = (2, 0, 3, 1)
        for k in range(4):
            self.assertEqual(relabel(mutate(R8, sigma[k]), sigma), mutate(relabel(R8, sigma), k))
            self.assertEqual(mutate(opposite(R8), k), opposite(mutate(R8, k)))

    def test_arrows_by_name(self) -> None:
        self.assertEqual(from_arrows(["a", "b", "c"], {("a", "b"): 2, ("c", "a"): 3}), (2, -3, 0))
        # the paper writes Q_t as a tuple; the article by its arrows
        t = 3
        self.assertTrue(isomorphic(families.q_t(t), (-t * t, -(t * t - 1), 2 * t, -2, t * (t - 1), -t * t)))


class Shapes(unittest.TestCase):
    def test_acyclic_quivers(self) -> None:
        self.assertTrue(is_acyclic((1, 1, 1)))  # 0 -> 1, 0 -> 2, 1 -> 2
        self.assertFalse(is_acyclic((1, -1, 1)))  # 0 -> 1 -> 2 -> 0
        self.assertTrue(is_acyclic((0, 0, 0, 0, 0, 0)))

    def test_the_fork_of_the_proof_of_theorem_7_2(self) -> None:
        # paper, proof of Theorem 3.4, b = 8, j = 1: mu_3 A(1) has the arrows below and is a fork with
        # point of return 3
        fork = from_arrows(
            ["0", "1", "2", "3"],
            {("1", "0"): 24, ("0", "2"): 50, ("1", "2"): 22, ("3", "1"): 4, ("3", "0"): 7, ("2", "3"): 6},
        )
        self.assertEqual(fork_point(fork), 3)
        self.assertTrue(isomorphic(fork, mutate(mutate(R8, 1), 3)))  # A(1) is one step from R_8
        self.assertIsNone(fork_point(R8))
        self.assertIsNone(fork_point((8, 8, 8, 1, 8, 8)))  # a pair joined by one arrow
        self.assertIsNone(fork_point((2, 2, 2)))  # acyclic


class Families(unittest.TestCase):
    def test_heights_and_closed_forms(self) -> None:
        cases = [("G", 8, 8, 56), ("R", 8, 8, 101), ("Qt", 3, 9, 132), ("P+", 3, 9, 413), ("Qa", 7, 8, 1242)]
        for key, value, tall, barrier in cases:
            chosen = families.family(key)
            self.assertEqual(height(chosen.quiver(value)), tall)
            self.assertEqual(chosen.height(value), tall)
            self.assertEqual(chosen.barrier(value), barrier)
        self.assertEqual(families.barrier_q_a(12), 6496)
        with self.assertRaises(ValueError):
            families.family("Z")
        with self.assertRaises(ValueError):
            families.family("G").check(2)

    def test_the_routes_of_the_theorems(self) -> None:
        g8 = families.replay(families.g(8), families.word_g(8))
        self.assertEqual(g8.heights, (8, 56, 8, 56, 8))
        self.assertTrue(g8.ends_at_opposite)
        r8 = families.replay(R8, families.word_r(8))
        self.assertEqual((r8.mutations, r8.top, r8.at_top, r8.ends_at_opposite), (37, 101, 28, True))
        self.assertEqual(r8.heights[:4], (8, 24, 40, 56))
        p2 = families.replay(families.p_plus(2), families.word_p_plus(2))
        self.assertEqual((p2.mutations, p2.top, p2.at_top, p2.ends_at_opposite), (28, 51, 1, True))
        for a, at_top in ((2, 9), (3, 1)):  # 2a + 5 quivers at the top for even a, one for odd a
            qa = families.replay(families.q_a(a), families.word_q_a(a), fifth_vertex=True)
            self.assertEqual(qa.mutations, (2 * a + 2) * (4 * a * a - a + 6))
            self.assertEqual(
                (qa.top, qa.at_top, qa.ends_at_opposite), (families.barrier_q_a(a), at_top, True)
            )
            self.assertEqual((qa.mutations_at_x, qa.largest_away_from_x), (0, 2 * a + 2))
        with self.assertRaises(ValueError):
            families.word_r(7)


class Searches(unittest.TestCase):
    def test_the_running_example(self) -> None:
        self.assertEqual(search.barrier(R8).level, 101)
        region = search.below(R8, 101)
        self.assertEqual((region.quivers, region.low, region.has_opposite), (35, 1, False))
        self.assertTrue(search.below(R8, 102).has_opposite)
        count, heights = search.shortest(R8, 101)
        self.assertEqual(count, 37)
        self.assertEqual(max(heights), 101)
        self.assertEqual(search.shortest(R8, 100), (None, []))

    def test_small_cases_by_hand(self) -> None:
        # one arrow: the opposite is the same quiver with its two vertices exchanged
        self.assertEqual(search.barrier((1,)).level, 1)
        # G_5: every mutation has height at least 20, and the route of Theorem 5.1 has height 20
        self.assertEqual(search.barrier(families.g(5)).level, 20)
        self.assertEqual(search.below(families.g(5), 20).quivers, 1)

    def test_forks_are_not_expanded_when_pruned(self) -> None:
        q2 = families.q_a(2)
        plain, pruned = search.below(q2, 21), search.below(q2, 21, prune_forks=True)
        self.assertEqual((plain.quivers, plain.low, plain.forks), (525, 1, 0))
        self.assertEqual((pruned.quivers, pruned.low), (391, 1))
        self.assertGreater(pruned.forks, 0)


class Conjecture(unittest.TestCase):
    def test_the_first_heights(self) -> None:
        self.assertEqual(conj55.split(1), (41, 39))
        self.assertEqual(conj55.split(2), (653, 521))
        with self.assertRaises(ValueError):
            conj55.split(0)


if __name__ == "__main__":
    unittest.main()
