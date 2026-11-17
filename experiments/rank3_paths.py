#!/usr/bin/env python
"""
rank3_paths.py -- the bounded-path measurement of note 2 in rank 3 (note 3).

A rank-3 quiver is a skew-symmetric 3x3 matrix.  Every mutation class has a minimal
representative: an acyclic quiver (p1, p2, l) -- arrows 1->2 (p1), 2->3 (p2), 1->3 (l) -- or a
cyclic quiver (a, b, c) -- arrows 1->2 (a), 2->3 (b), 3->1 (c) -- with 2 <= a, b, c and each
entry at most half the product of the other two.  This script lists the classes whose minimal
representative has entries <= --W0, and for each class measures f(w) for every w up to --w-max,
both for labelled quivers (the convention of note 2) and up to relabelling of the vertices.

Subcommands:
  profile    one JSONL row per class: minimal representative, type, Markov constant,
             labelled and unlabelled f(w), islands at the minimal level
  summarize  tables from the JSONL file

Run from experiments/ with python -I.  Reuses bounded_paths.merging_profile (corrected f).
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mutation_path import DT  # noqa: E402
from bounded_paths import canonical, enumerate_component, merging_profile  # noqa: E402


def acyclic(p1, p2, l):
    B = np.zeros((3, 3), dtype=DT)
    B[0, 1], B[1, 2], B[0, 2] = p1, p2, l
    return B - B.T


def cyclic(a, b, c):
    B = np.zeros((3, 3), dtype=DT)
    B[0, 1], B[1, 2], B[2, 0] = a, b, c
    return B - B.T


def candidates(W0):
    """Minimal representatives (with repetitions across classes; deduplicated later)."""
    out = []
    r = range(0, W0 + 1)
    for p1 in r:
        for p2 in r:
            for l in r:
                if sum(x > 0 for x in (p1, p2, l)) >= 2:
                    out.append(("acyclic", (p1, p2, l), acyclic(p1, p2, l)))
    for a in range(2, W0 + 1):
        for b in range(2, W0 + 1):
            for c in range(2, W0 + 1):
                if 2 * a <= b * c and 2 * b <= a * c and 2 * c <= a * b:
                    out.append(("cyclic", (a, b, c), cyclic(a, b, c)))
    return out


def class_key(Q, bound, budget):
    states, exhausted = enumerate_component(Q, bound, budget, unlabelled=True)
    lo = min(states.values())
    return min(k for k, v in states.items() if v == lo), exhausted


def _task(task):
    kind, weights, bound, budget, w_list = task
    Q = acyclic(*weights) if kind == "acyclic" else cyclic(*weights)
    lab = merging_profile(Q, bound, budget, w_list, unlabelled=False)
    unl = merging_profile(Q, bound, budget, w_list, unlabelled=True)
    row = {"kind": kind, "weights": list(weights), "B_big": bound}
    if kind == "cyclic":
        a, b, c = weights
        row["markov_C"] = a * a + b * b + c * c - a * b * c
    for tag, r in (("lab", lab), ("unl", unl)):
        f = {int(w): v for w, v in r["f"].items()}
        m = {int(w): v for w, v in r["m"].items()}
        row[tag] = {"comp_size": r["comp_size"], "exhausted": r["exhausted"], "max_level": r["max_level"],
                    "w_min": min(m.values()), "islands_at_w_min": r["classes_at_w"][min(m)],
                    "unconnected_w": r["unconnected_w"],
                    "excess_w": [w for w in sorted(f) if f[w] > w],
                    # the levels at which an island first joins: (m, f(m)) with f(m) > m
                    "joins": sorted({(m[w], f[w]) for w in f if f[w] > m[w]}),
                    "max_ratio": max(f[w] / w for w in f), "max_excess": max(f[w] - w for w in f),
                    "f": f}
    return row


def cmd_profile(args):
    seen = set()
    tasks = []
    for kind, weights, Q in candidates(args.W0):
        key, exhausted = class_key(Q, args.B_big, args.budget)
        if key in seen:
            continue
        seen.add(key)
        tasks.append((kind, weights, args.B_big, args.budget, list(range(1, args.w_max + 1))))
    print(f"{len(tasks)} classes with minimal representative <= {args.W0}", flush=True)
    with open(args.out, "w") as f, Pool(args.workers) as pool:
        for r in pool.imap_unordered(_task, tasks, chunksize=4):
            f.write(json.dumps(r) + "\n")


def cmd_summarize(args):
    rows = [json.loads(l) for l in open(args.file) if l.strip()]
    infinite = [r for r in rows if r["lab"]["max_level"] > 2]
    print(f"{len(rows)} classes, {len(infinite)} infinite (some entry > 2)")
    for tag in ("unl", "lab"):
        rs = [r[tag] for r in infinite]
        print(f"\n[{tag}] exhausted {sum(r['exhausted'] for r in rs)}/{len(rs)}, "
              f"unconnected rows {sum(bool(r['unconnected_w']) for r in rs)}")
        print(f"  classes with f(w) <= w for every w: {sum(not r['excess_w'] for r in rs)}")
        print(f"  classes with one island at w_min: {sum(r['islands_at_w_min'] == 1 for r in rs)}")
        if any(r["excess_w"] for r in rs):
            print(f"  max f(w)/w: {max(r['max_ratio'] for r in rs):.3f}   max f(w) - w: {max(r['max_excess'] for r in rs)}")
    print("\nlabelled joins (m -> f(m)) for the first classes with excess:")
    shown = 0
    for r in infinite:
        if r["lab"]["joins"] and shown < args.show:
            shown += 1
            print(f"  {r['kind']:>7} {tuple(r['weights'])}: w_min {r['lab']['w_min']}, islands {r['lab']['islands_at_w_min']}, "
                  f"joins {r['lab']['joins'][:8]}, max ratio {r['lab']['max_ratio']:.2f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("profile")
    pr.add_argument("--W0", type=int, default=10)
    pr.add_argument("--w-max", type=int, default=512)
    pr.add_argument("--B-big", type=int, default=8192)
    pr.add_argument("--budget", type=int, default=2000000)
    pr.add_argument("--workers", type=int, default=4)
    pr.add_argument("--out", default="rank3_profile.jsonl")
    pr.set_defaults(func=cmd_profile)
    sm = sub.add_parser("summarize")
    sm.add_argument("file")
    sm.add_argument("--show", type=int, default=25)
    sm.set_defaults(func=cmd_summarize)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
