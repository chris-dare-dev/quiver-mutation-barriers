"""Searches in the mutation graph, up to relabelling, bounded by height.

barrier(Q)        the least H such that the opposite of Q is reached from Q through quivers of height
                  at most H: a search that always expands a quiver of least height, with no pruning
below(Q, H)       every quiver reached from Q through quivers of height below H
shortest(Q, H)    the least number of mutations from Q to its opposite through heights at most H

The mutation class of most quivers is infinite and need not hold the opposite, so `barrier` and `shortest`
can be told where to stop: at a height (`cap`) or after a number of quivers (`budget`).  Neither depends
on the machine or its load.
"""

from __future__ import annotations

import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from .quiver import Quiver, canonical, fork_point, height, neighbours, opposite


@dataclass(frozen=True)
class Barrier:
    level: int | None  # None if the opposite was not reached
    popped: int  # quivers taken from the queue before the opposite was reached, or before the search ended
    cleared: int | None = None  # of a search that was stopped: no route to the opposite stays at or below it


def barrier(quiver: Sequence[int], *, cap: int | None = None, budget: int | None = None) -> Barrier:
    """The least height at which `quiver` is joined to its opposite.

    Without `cap` and `budget` the search ends when it reaches the opposite or has seen the whole mutation
    class.  With `cap` it leaves out every quiver above that height; with `budget` it stops once that many
    quivers have been taken from the queue.  A search that was stopped without reaching the opposite still
    gives a bound, `cleared`.  The quivers are taken in order of height, so when one of height L has been
    taken, every quiver joined to the start through heights below L was taken before it: a search stopped
    by its budget at level L has cleared L - 1, and one that ran out of quivers under a cap has cleared
    the cap.  `cleared` stays None when the whole class was seen and the opposite is not in it.
    """
    start, target = canonical(quiver), canonical(opposite(quiver))
    queue, seen, level, popped, left_out = [(height(start), start)], {start}, 0, 0, False
    while queue:
        if budget is not None and popped >= budget:
            return Barrier(None, popped, cleared=level - 1)
        at, current = heapq.heappop(queue)
        level = max(level, at)
        popped += 1
        if current == target:
            return Barrier(level, popped)
        for other in neighbours(current):
            if other in seen:
                continue
            tall = height(other)
            if cap is not None and tall > cap:
                left_out = True
                continue
            seen.add(other)
            heapq.heappush(queue, (tall, other))
    return Barrier(None, popped, cleared=cap if left_out else None)


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


def shortest(quiver: Sequence[int], bound: int, *, budget: int | None = None) -> tuple[int | None, list[int]]:
    """The least number of mutations to the opposite through heights at most `bound`, and the heights
    along one route of that length: `(None, [])` when there is no such route, or when more than `budget`
    quivers were reached before one was found."""
    start, target = canonical(quiver), canonical(opposite(quiver))
    previous: dict[Quiver, Quiver | None] = {start: None}
    layer = [start]
    while layer and target not in previous:
        if budget is not None and len(previous) > budget:
            return None, []
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
