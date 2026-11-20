# Mirror barriers in quiver mutation

<!--
  Badges: the GitHub-dynamic ones (CI, last commit) render once the repo is
  public. The static ones always render.
-->
[![CI](https://github.com/chris-dare-dev/quiver-mutation-barriers/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/chris-dare-dev/quiver-mutation-barriers/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Code: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Text and data: CC BY 4.0](https://img.shields.io/badge/text%20%26%20data-CC%20BY%204.0-green.svg)](LICENSE-TEXT.md)
[![Status](https://img.shields.io/badge/status-no%20human%20review-orange.svg)](#status)
[![Last commit](https://img.shields.io/github/last-commit/chris-dare-dev/quiver-mutation-barriers.svg)](https://github.com/chris-dare-dev/quiver-mutation-barriers/commits)

**How high must a mutation path between two quivers of small height climb?**
Notes, code and stored results behind the draft paper [paper/mutation-barriers.pdf](paper/mutation-barriers.pdf).

A quiver is a skew-symmetric integer matrix, its *height* its largest entry, and mutation is the move of Fomin–Zelevinsky cluster algebras. A computable bound on the height a route needs would decide mutation equivalence, which is not known to be decidable for four or more vertices.

## Result

No upper bound was found for n ≥ 4 vertices. What was found are lower bounds: quivers that reach their opposite −Q, but only far above their own height. At height 8, the example R₈ = (−8, −8, 7, −2, 6, −8) reaches −R₈ in 37 mutations and by no route below height 101.

| Vertices | Barrier at height 8 | Support |
|---|---|---|
| 4 | 56 | proof by hand |
| 4 | 101 | computer-assisted proof |
| 5 | 1,242 | exhaustive search |

In general F(4, w) ≥ w(w − 1) and F(5, w) ≥ 4w³ − O(w²), the latter computational for w ≤ 65.

## Try it

```bash
python3 -I verify/smoke.py   # about 15 s, standard library only: recomputes the headline numbers
make test && make smoke      # tests, then the same numbers as tasks under the scheduler
```

## Read

| | |
|---|---|
| [paper/](paper/mutation-barriers.pdf) | The draft paper |
| [docs/](docs/README.md) | 23 notes in reading order: arguments, computations, checks |
| [CLAIMS.md](CLAIMS.md) | Each claim, its script, stored output and command, and what has been rerun |
| [DATA.md](DATA.md) | The stored results and how to install them |
| [GUIDE.md](GUIDE.md) | Full results table, limits, layout, tasks and batches |

## Status

Everything here was produced with extensive help from AI tools. Proofs and computations were rechecked by fresh instances of the same model, but **no human has read the paper** and no specialist has checked an argument. Each result is labelled *proved by hand*, *computer-assisted proof*, *computational* (a stated range only) or *conjecture*. Do not cite them as established until a mathematician has read them.

Cite via [CITATION.cff](CITATION.cff).
