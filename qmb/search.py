"""Searches in the mutation graph, up to relabelling, bounded by height.

barrier(Q)        the least H such that the opposite of Q is reached from Q through quivers of height
                  at most H: a search that always expands a quiver of least height, with no pruning
below(Q, H)       every quiver reached from Q through quivers of height below H
shortest(Q, H)    the least number of mutations from Q to its opposite through heights at most H
"""

from __future__ import annotations

import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from .quiver import Quiver, canonical, fork_point, height, neighbours, opposite


@dataclass(frozen=True)
class Barrier:
    level: int | None  # None if the opposite is not in the mutation class
    popped: int  # quivers taken from the queue before the opposite was reached


def barrier(quiver: Sequence[int]) -> Barrier:
    start, target = canonical(quiver), canonical(opposite(quiver))
    queue, seen, level, popped = [(height(start), start)], {start}, 0, 0
    while queue:
        at, current = heapq.heappop(queue)
        level = max(level, at)
        popped += 1
        if current == target:
            return Barrier(level, popped)
        for other in neighbours(current):
            if other not in seen:
                seen.add(other)
                heapq.heappush(queue, (height(other), other))
    return Barrier(None, popped)


@dataclass(frozen=True)
class Region:
    quivers: int  # reached through heights below the bound, the start included
    low: int  # of these, of height at most that of the start
    has_opposite: bool
    forks: int  # forks met and not expanded (0 unless forks are pruned)


def below(quiver: Sequence[int], bound: int, *, prune_forks: bool = False) -> Region:
    """The quivers reached from `quiver` through quivers of height below `bound`.

    With `prune_forks` a fork other than the start is counted apart and not expanded, and is not one of
    the quivers reached.
    """
    start = canonical(quiver)
    low_bound = height(start)
    seen, todo, forks = {start}, [start], 0
    while todo:
        current = todo.pop()
        for other in neighbours(current):
            if height(other) < bound and other not in seen:
                seen.add(other)
                if prune_forks and fork_point(other) is not None:
                    forks += 1
                else:
                    todo.append(other)
    reached = [x for x in seen if not prune_forks or x == start or fork_point(x) is None]
    return Region(
        quivers=len(reached),
        low=sum(1 for x in reached if height(x) <= low_bound),
        has_opposite=canonical(opposite(quiver)) in seen,
        forks=forks,
    )


def shortest(quiver: Sequence[int], bound: int) -> tuple[int | None, list[int]]:
    """The least number of mutations to the opposite through heights at most `bound`, and the heights
    along one route of that length."""
    start, target = canonical(quiver), canonical(opposite(quiver))
    previous: dict[Quiver, Quiver | None] = {start: None}
    layer = [start]
    while layer and target not in previous:
        following = []
        for current in layer:
            for other in neighbours(current):
                if height(other) <= bound and other not in previous:
                    previous[other] = current
                    following.append(other)
        layer = following
    if target not in previous:
        return None, []
    heights = []
    at: Quiver | None = target
    while at is not None:
        heights.append(height(at))
        at = previous[at]
    return len(heights) - 1, heights[::-1]
