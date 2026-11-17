"""The families of the article, their closed forms, and the routes of its theorems.

Each family is a quiver for every value of one integer parameter.  The closed forms are those the
article states; `predicted_barrier` is the height at which the article says the quiver is joined to its
opposite.  The routes are the words of mutations in the proofs, replayed with integers.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .quiver import Quiver, from_arrows, height, matrix, mutate, opposite, relabel, vertices


def g(k: int) -> Quiver:
    """G_k (Theorem 5.1): arrows 0 -> 1, 2 -> 0, 3 -> 0, 1 -> 3 of weight k and 3 -> 2 of weight k - 1."""
    return (k, -k, -k, 0, k, -(k - 1))


def r(b: int) -> Quiver:
    """R_b (Theorem 7.2)."""
    return (-b, -b, b - 1, -2, b - 2, -b)


def q_t(t: int) -> Quiver:
    """Q_t (Section 7), on the vertices p, q, c1, c."""
    return from_arrows(
        ["p", "q", "c1", "c"],
        {
            ("q", "p"): 2,
            ("p", "c1"): t * (t - 1),
            ("c1", "q"): t * t,
            ("p", "c"): t * t,
            ("q", "c"): t * t - 1,
            ("c", "c1"): 2 * t,
        },
    )


def p_plus(t: int) -> Quiver:
    """P+_t (Theorem 9.1): Q_t on p, q, c1, c and a fifth vertex x, in the order x, p, q, c1, c."""
    return from_arrows(
        ["x", "p", "q", "c1", "c"],
        {
            ("q", "p"): 2,
            ("p", "c1"): t * (t - 1),
            ("c1", "q"): t * t,
            ("p", "c"): t * t,
            ("q", "c"): t * t - 1,
            ("c", "c1"): 2 * t,
            ("x", "p"): 1,
            ("q", "x"): t * t - 1,
            ("x", "c"): t * t,
            ("c1", "x"): t * (t - 1),
        },
    )


def q_a(a: int) -> Quiver:
    """Q_a (Theorem 10.1): the row of x = 0 over the four-vertex quiver on the vertices 1, 2, 3, 4."""
    return (-(a - 3), a - 2, a + 1, -(a + 1), -(a + 1), -a, 2, -2, -a, -(a + 1))


def barrier_g(k: int) -> int:
    return k * (k - 1)


def barrier_r(b: int) -> int:
    return 2 * b * b - 3 * b - 3


def barrier_q_t(t: int) -> int:
    return 2 * t**4 - t**3 - t * t + 2 * t


def barrier_p_plus(t: int) -> int:
    return 2 * t**5 - t**4 + t * t - 1


def barrier_q_a(a: int) -> int:
    return 4 * a**3 - 3 * a * a + ((5 * a - 1) // 2 if a % 2 else (3 * a - 4) // 2)


@dataclass(frozen=True)
class Route:
    """A route replayed with integers: what the theorems state about it."""

    mutations: int
    top: int  # the largest height on the route
    at_top: int  # how many quivers on the route have that height
    ends_at_opposite: bool  # the last quiver is the opposite of the first, up to relabelling
    heights: tuple[int, ...]  # of the first quivers on the route, the start included
    mutations_at_x: int | None = None  # five vertices: mutations at the fifth vertex
    largest_away_from_x: int | None = None  # five vertices: largest entry between the other four


def _replay(start: Quiver, word: Sequence[int], *, head: int = 8) -> tuple[Quiver, int, int, tuple[int, ...]]:
    """The end of a word of mutations, its largest height, how often it occurs, and the first heights."""
    quiver, top, at_top, heights = start, height(start), 1, [height(start)]
    for vertex in word:
        quiver = mutate(quiver, vertex)
        level = height(quiver)
        if level > top:
            top, at_top = level, 1
        elif level == top:
            at_top += 1
        if len(heights) < head:
            heights.append(level)
    return quiver, top, at_top, tuple(heights)


def _apply(start: Quiver, word: Sequence[int]) -> Quiver:
    quiver = start
    for vertex in word:
        quiver = mutate(quiver, vertex)
    return quiver


def _mirror_relabelling(reached: Quiver, half: Quiver, fixed: Sequence[int] = ()) -> tuple[int, ...] | None:
    """A relabelling sigma, fixing the vertices in `fixed`, with reached[sigma i, sigma j] = -half[i, j]."""
    import itertools

    n = vertices(reached)
    target = opposite(half)
    free = [v for v in range(n) if v not in fixed]
    for images in itertools.permutations(free):
        sigma = list(range(n))
        for vertex, image in zip(free, images, strict=True):
            sigma[vertex] = image
        if relabel(reached, sigma) == target:
            return tuple(sigma)
    return None


def _mirrored(
    start: Quiver, half: Sequence[int], middle: Sequence[int], fixed: Sequence[int] = ()
) -> list[int]:
    """The word: `half`, then `middle`, then `half` backwards in the names of the mirror image.

    After `half` the route is at a quiver B; `middle` must lead to the opposite of B with its vertices
    renamed.  Mutation commutes with reversing every arrow, so undoing `half` in the new names leads to
    the opposite of the start.
    """
    at_half = _apply(start, half)
    reached = _apply(at_half, middle)
    sigma = _mirror_relabelling(reached, at_half, fixed)
    if sigma is None:
        raise ValueError("the middle of the route does not reach the mirror image of its first half")
    return [*half, *middle, *(sigma[vertex] for vertex in reversed(half))]


def _steps(count: int, p: int, q: int) -> tuple[list[int], int, int]:
    """`count` steps on a pair: mutate at p, then exchange the names p and q."""
    word = []
    for _ in range(count):
        word.append(p)
        p, q = q, p
    return word, p, q


def word_g(k: int) -> list[int]:
    """Theorem 5.1: the route mu_1, mu_2, mu_3, mu_0."""
    return [1, 2, 3, 0]


def word_r(b: int) -> list[int]:
    """Theorem 7.2 for even b: b/2 - 1 steps on (p, q) = (1, 2), the mutation at 3, then b(b - 1)/2 + 1
    backward steps along the plateau, and the first part again in mirror image."""
    if b % 2 or b < 6:
        raise ValueError("the route of Theorem 7.2 is stated for even b >= 6")
    half, p, q = _steps(b // 2 - 1, 1, 2)
    half.append(3)
    backward, _, _ = _steps(b * (b - 1) // 2 + 1, q, p)  # a backward step mutates at q
    return _mirrored(r(b), half, backward)


def word_p_plus(t: int) -> list[int]:
    """Theorem 9.1: t - 1 steps on (p, q), the mutation at c1, 2t^3 - t^2 - t + 1 further steps, then the
    mutations at p and at c, and the first part again in mirror image."""
    first, p, q = _steps(t - 1, 1, 2)
    second, p, q = _steps(2 * t**3 - t * t - t + 1, p, q)
    return _mirrored(p_plus(t), [*first, 3, *second], [p, 4])


def word_q_a(a: int) -> list[int]:
    """Theorem 10.1: steps on (p, q) to the end of the bounce cycle, then alternately a turn at r and
    2a + 1 steps; the turn at the top for odd a, or 2a + 2 further steps for even a; and the first part
    again in mirror image.  The fifth vertex x = 0 is never mutated."""
    m = 2 * a + 1
    c = 4 * a * a - 5 * a + 1
    turns = 2 * a + 1 + (c // 2 + 2 if a % 2 else (c + 3) // 2)
    p, q, r_, s = 4, 1, 2, 3
    half: list[int] = []
    position = a + 1
    for turn in range(1, turns + 1):
        steps, p, q = _steps(m - position, p, q)
        half += steps
        if turn == turns and a % 2:
            break  # odd a: the first half ends before the turn at the top
        half.append(r_)
        r_, s = s, r_
        position = 0
    middle = [r_, p] if a % 2 else _steps(m + 1, p, q)[0]
    return _mirrored(q_a(a), half, middle, fixed=(0,))


def replay(start: Quiver, word: Sequence[int], *, fifth_vertex: bool = False) -> Route:
    """Replays a word of mutations from a quiver and reports what the route theorems state."""
    end, top, at_top, heights = _replay(start, word)
    mutations_at_x = largest = None
    if fifth_vertex:
        mutations_at_x = sum(1 for vertex in word if vertex == 0)
        quiver, largest = start, 0
        for vertex in [None, *word]:
            if vertex is not None:
                quiver = mutate(quiver, vertex)
            rows = matrix(quiver)
            largest = max(largest, max(abs(rows[i][j]) for i in range(1, 5) for j in range(i + 1, 5)))
    from .quiver import isomorphic

    return Route(
        mutations=len(word),
        top=top,
        at_top=at_top,
        ends_at_opposite=isomorphic(end, opposite(start)),
        heights=heights,
        mutations_at_x=mutations_at_x,
        largest_away_from_x=largest,
    )


@dataclass(frozen=True)
class Family:
    """One family of the article."""

    key: str  # as written in batch files and task ids
    name: str  # as written in the article
    parameter: str
    least: int  # the least value of the parameter for which the article defines or uses the family
    quiver: Callable[[int], Quiver]
    height: Callable[[int], int]
    barrier: Callable[[int], int]
    word: Callable[[int], list[int]] | None
    route_mutations: Callable[[int], int] | None
    route_at_top: Callable[[int], int] | None
    article: str

    def check(self, value: int) -> None:
        if value < self.least:
            raise ValueError(f"{self.name} is defined for {self.parameter} >= {self.least}, not {value}")


FAMILIES: dict[str, Family] = {
    family.key: family
    for family in (
        Family(
            "G", "G_k", "k", 3, g, lambda k: k, barrier_g, word_g, lambda k: 4, lambda k: 2, "Theorem 5.1"
        ),
        Family(
            "R",
            "R_b",
            "b",
            5,
            r,
            lambda b: b,
            barrier_r,
            word_r,
            lambda b: b * (b - 1) // 2 + b + 1,
            lambda b: b * (b - 1) // 2,
            "Theorem 7.2",
        ),
        Family("Qt", "Q_t", "t", 3, q_t, lambda t: t * t, barrier_q_t, None, None, None, "Section 7"),
        Family(
            "P+",
            "P+_t",
            "t",
            2,
            p_plus,
            lambda t: t * t,
            barrier_p_plus,
            word_p_plus,
            lambda t: 4 * t**3 - 2 * t * t + 4,
            lambda t: 1,
            "Theorem 9.1",
        ),
        Family(
            "Qa",
            "Q_a",
            "a",
            2,
            q_a,
            lambda a: a + 1,
            barrier_q_a,
            word_q_a,
            lambda a: (2 * a + 2) * (4 * a * a - a + 6),
            lambda a: 1 if a % 2 else 2 * a + 5,
            "Theorem 10.1",
        ),
    )
}


def family(key: str) -> Family:
    try:
        return FAMILIES[key]
    except KeyError:
        raise ValueError(f"no family {key!r}; the families are {', '.join(FAMILIES)}") from None
