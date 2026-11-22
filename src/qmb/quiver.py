"""Quivers as tuples, mutation, relabelling, height, and Warkentin's forks.

A quiver on n vertices is the tuple of the entries b_ij, i < j, of its exchange matrix, row by row:
(b01, b02, b03, b12, b13, b23) on four vertices.  b_ij > 0 means b_ij arrows i -> j.  The height is the
largest absolute entry.  Two quivers are the same up to relabelling when one is the other with its
vertices permuted; `canonical` picks the least tuple among the relabellings.

Standard library only.  The scripts of research/verify/ do not import this module.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable, Mapping, Sequence
from functools import cache

Quiver = tuple[int, ...]


def vertices(quiver: Sequence[int]) -> int:
    """The number of vertices of a quiver given as the upper triangle of its matrix."""
    n = 2
    while n * (n - 1) // 2 < len(quiver):
        n += 1
    if n * (n - 1) // 2 != len(quiver):
        raise ValueError(f"{len(quiver)} entries are not the upper triangle of a square matrix")
    return n


def height(quiver: Sequence[int]) -> int:
    return max((abs(entry) for entry in quiver), default=0)


def opposite(quiver: Sequence[int]) -> Quiver:
    """The quiver with every arrow reversed."""
    return tuple(-entry for entry in quiver)


def matrix(quiver: Sequence[int]) -> list[list[int]]:
    """The skew-symmetric exchange matrix."""
    n = vertices(quiver)
    rows = [[0] * n for _ in range(n)]
    entries = iter(quiver)
    for i in range(n):
        for j in range(i + 1, n):
            rows[i][j] = next(entries)
            rows[j][i] = -rows[i][j]
    return rows


def from_matrix(rows: Sequence[Sequence[int]]) -> Quiver:
    n = len(rows)
    return tuple(rows[i][j] for i in range(n) for j in range(i + 1, n))


def from_arrows(names: Sequence[str], arrows: Mapping[tuple[str, str], int]) -> Quiver:
    """The quiver on the named vertices, in that order, with `arrows[(u, v)]` arrows u -> v."""
    n = len(names)
    rows = [[0] * n for _ in range(n)]
    for (tail, head), weight in arrows.items():
        i, j = names.index(tail), names.index(head)
        if i == j or rows[i][j]:
            raise ValueError(f"a loop or a repeated pair at {tail}, {head}")
        rows[i][j], rows[j][i] = weight, -weight
    return from_matrix(rows)


def mutate_matrix(rows: Sequence[Sequence[int]], k: int) -> list[list[int]]:
    """Fomin-Zelevinsky mutation at k, from the definition.

    b'_ij = -b_ij if k is i or j, and b_ij + (|b_ik| b_kj + b_ik |b_kj|) / 2 otherwise.  The second term
    is b_ik b_kj when both are positive (paths i -> k -> j), its negative when both are negative, else 0.
    """
    n = len(rows)
    out = [list(row) for row in rows]
    for i in range(n):
        for j in range(n):
            if k in (i, j):
                out[i][j] = -rows[i][j]
            else:
                out[i][j] = rows[i][j] + (abs(rows[i][k]) * rows[k][j] + rows[i][k] * abs(rows[k][j])) // 2
    return out


_Move = tuple[tuple[int, ...], tuple[tuple[int, int, int, int, int], ...]]
_Relabelling = tuple[tuple[int, int], ...]


@cache
def _tables(n: int) -> tuple[tuple[_Move, ...], tuple[_Relabelling, ...]]:
    """For n vertices: per vertex, the entries a mutation negates and those it may change; and, per
    permutation, where each entry of the relabelled quiver comes from and with which sign."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    index = {pair: position for position, pair in enumerate(pairs)}

    def entry(i: int, j: int) -> tuple[int, int]:
        return (index[i, j], 1) if i < j else (index[j, i], -1)

    moves = []
    for k in range(n):
        negated = tuple(position for position, pair in enumerate(pairs) if k in pair)
        changed = tuple(
            (position, *entry(i, k), *entry(k, j)) for position, (i, j) in enumerate(pairs) if k not in (i, j)
        )
        moves.append((negated, changed))
    relabellings = tuple(
        tuple(entry(sigma[i], sigma[j]) for i, j in pairs) for sigma in itertools.permutations(range(n))
    )
    return tuple(moves), relabellings


def mutate(quiver: Sequence[int], k: int) -> Quiver:
    """Mutation at vertex k."""
    negated, changed = _tables(vertices(quiver))[0][k]
    out = list(quiver)
    for position in negated:
        out[position] = -quiver[position]
    for position, first, first_sign, second, second_sign in changed:
        into, out_of = first_sign * quiver[first], second_sign * quiver[second]  # b_ik and b_kj
        if into > 0 and out_of > 0:
            out[position] += into * out_of
        elif into < 0 and out_of < 0:
            out[position] -= into * out_of
    return tuple(out)


def relabel(quiver: Sequence[int], sigma: Sequence[int]) -> Quiver:
    """The quiver whose vertex i is the vertex sigma[i] of `quiver`: entry (i, j) is b_{sigma i, sigma j}."""
    rows = matrix(quiver)
    n = len(rows)
    return tuple(rows[sigma[i]][sigma[j]] for i in range(n) for j in range(i + 1, n))


def canonical(quiver: Sequence[int]) -> Quiver:
    """The least tuple among the relabellings of the quiver."""
    return min(
        tuple(sign * quiver[position] for position, sign in relabelling)
        for relabelling in _tables(vertices(quiver))[1]
    )


def isomorphic(first: Sequence[int], second: Sequence[int]) -> bool:
    return len(first) == len(second) and canonical(first) == canonical(second)


def neighbours(quiver: Sequence[int]) -> list[Quiver]:
    """The mutations of a quiver at each of its vertices, in canonical form."""
    return [canonical(mutate(quiver, k)) for k in range(vertices(quiver))]


def _acyclic_on(rows: Sequence[Sequence[int]], chosen: Iterable[int]) -> bool:
    remaining = set(chosen)
    while remaining:
        sources = [v for v in remaining if not any(rows[u][v] > 0 for u in remaining)]
        if not sources:
            return False
        remaining -= set(sources)
    return True


def is_acyclic(quiver: Sequence[int]) -> bool:
    """Whether the quiver has no oriented cycle."""
    rows = matrix(quiver)
    return _acyclic_on(rows, range(len(rows)))


def fork_point(quiver: Sequence[int]) -> int | None:
    """The point of return if the quiver is a fork (Warkentin, Def. 2.1), else None.

    A fork is a quiver in which every two vertices are joined by at least two arrows, which is not
    acyclic, and which has a vertex r such that b_ji > b_ir and b_ji > b_rj for every path i -> r -> j
    and such that the full subquivers on the in-neighbours and on the out-neighbours of r are acyclic.
    """
    rows = matrix(quiver)
    n = len(rows)
    if any(abs(entry) < 2 for entry in quiver) or _acyclic_on(rows, range(n)):
        return None
    for r in range(n):
        into = [i for i in range(n) if rows[i][r] > 0]
        out_of = [j for j in range(n) if rows[r][j] > 0]
        if (
            all(rows[j][i] > rows[i][r] and rows[j][i] > rows[r][j] for i in into for j in out_of)
            and _acyclic_on(rows, into)
            and _acyclic_on(rows, out_of)
        ):
            return r
    return None
