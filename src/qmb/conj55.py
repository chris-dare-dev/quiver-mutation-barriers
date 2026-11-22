"""Conjecture 5.5 of Armstrong-Williams, Hirst, Jackson and Lee at one height, by direct enumeration.

For a height h: the four-vertex quivers of height exactly h, up to relabelling, and how many of them reach
an acyclic quiver through quivers of height at most h.  A quiver that does not is a counterexample to the
conjecture unless it is mutation-cyclic; deciding that is not done here.
"""

from __future__ import annotations

import itertools

from .quiver import Quiver, canonical, height, is_acyclic, neighbours


def split(h: int) -> tuple[int, int]:
    """(quivers of height exactly h, those that reach an acyclic quiver within height h)."""
    if h < 1:
        raise ValueError("the height must be at least 1")
    entries = range(-h, h + 1)
    exact: set[Quiver] = set()
    reaching: set[Quiver] = set()
    todo: list[Quiver] = []
    for quiver in itertools.product(entries, repeat=6):
        if not any(quiver):
            continue
        acyclic = is_acyclic(quiver)
        if acyclic or height(quiver) == h:
            form = canonical(quiver)
            if height(form) == h:
                exact.add(form)
            if acyclic and form not in reaching:
                reaching.add(form)
                todo.append(form)
    while todo:
        current = todo.pop()
        for other in neighbours(current):
            if height(other) <= h and other not in reaching:
                reaching.add(other)
                todo.append(other)
    return len(exact), sum(1 for quiver in exact if quiver in reaching)
