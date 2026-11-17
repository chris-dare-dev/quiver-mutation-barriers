"""Review 3 of note 22, item 1 (tubes): the family graph with note 22's definition, written from its description,
on the regenerated sample of note-14 certificates (~/.cache/qmb-review23/n14_certs.jsonl.gz).

A family is keyed by (tau, the largest (Y(0), Y(1), Y(2)) over the 24 simultaneous relabellings).  The step at m
links F to G if the triple (mu_m F(d), mu_m F(d+1), mu_m F(d+2)), continued with F's tau, has G's key for some
d in (0, 1, 2, 3, -1, -2, -3) (first hit).  Strongly connected components are formed with self-links left out of
the adjacency (as note 22's `shapes` does), and every component is counted, single families on no cycle included.
The walk of a component is "three vertices" if some family uses three vertices for links inside it, else "pair"
(with c the weight between the two vertices of families that use two).  The "pair" components with no c are then
split: single family with a self-link (one mutation and a relabelling per period) or single family on no cycle.
Usage: python -I review23_n22_tubes2.py > review23_n22_tubes2.log"""
import gzip
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__))), "experiments"))  # the scripts under review
import review23_n22_lib as L
from review23_n22_shapes import tarjan, group

IN = os.path.expanduser("~/.cache/qmb-review23/n14_certs.jsonl.gz")
SH = (0, 1, 2, 3, -1, -2, -3)


def key_of(tau, Y):
    return (tau, max(tuple(L.relabel(y, k) for y in Y) for k in range(24)))


def nxt(Y, tau):
    return tuple((tau + 1) * (c - b) + a for a, b, c in zip(*Y))


def prv(Y, tau):
    return tuple((tau + 1) * (a - b) + c for a, b, c in zip(*Y))


def shift(Y, d, tau):
    Y = tuple(Y)
    while d > 0:
        Y = (Y[1], Y[2], nxt(Y, tau))
        d -= 1
    while d < 0:
        Y = (prv(Y, tau), Y[0], Y[1])
        d += 1
    return Y


def main():
    tab = Counter()
    tab_rand = Counter()
    ncls = nrand = 0
    with gzip.open(IN, "rt") as f:
        for line in f:
            c = json.loads(line)
            if not c["rec"] or c["rec"].get("status") != "certified":
                continue
            ncls += 1
            rnd = c["why"] == "random"
            nrand += rnd
            fams = [(tau, tuple(tuple(y) for y in Y)) for tau, Y in c["fams"]]
            keys = {key_of(t, Y): fid for fid, (t, Y) in enumerate(fams)}
            firsts = {(k[0], k[1][0]) for k in keys}
            gv = []
            for t, Y in fams:
                var = [a for a in range(6) if not (Y[0][a] == Y[1][a] == Y[2][a])]
                com = set(range(4))
                for a in var:
                    com &= set(L.PAIRS[a])
                gv.append(min(com) if len(com) == 1 else None)
            link = {}
            for fid, (t, Y) in enumerate(fams):
                row = {}
                for m in range(4):
                    if m == gv[fid]:
                        continue
                    Yp = tuple(L.mutate(y, m) for y in Y)
                    for d in SH:
                        Z = shift(Yp, -d, t)
                        if (t, L.canon(Z[0])) not in firsts:
                            continue
                        k = key_of(t, Z)
                        if k in keys:
                            row[m] = keys[k]
                            break
                link[fid] = row
            adj = {fid: sorted({g for g in row.values() if g != fid}) for fid, row in link.items()}
            for comp in tarjan(adj):
                cs = set(comp)
                used = [sorted(m for m, g in link[fid].items() if g in cs) for fid in comp]
                ws = set()
                for fid, ms in zip(comp, used):
                    if len(ms) == 2:
                        ws.add(abs(L.e(fams[fid][1][0], ms[0], ms[1])))
                if any(len(ms) >= 3 for ms in used):
                    walk = "three vertices"
                elif ws:
                    walk = "pair, c = %s" % sorted(ws)
                elif len(comp) == 1 and link[comp[0]] and comp[0] in link[comp[0]].values():
                    walk = "pair without c: one family with a self-link"
                elif len(comp) == 1:
                    walk = "pair without c: one family ON NO CYCLE"
                else:
                    walk = "pair without c: several families"
                tr = " + ".join(sorted({group(L.tri_type(L.tri_entries(fams[fid][1][0], gv[fid]))) for fid in comp if gv[fid] is not None}))
                tab[(walk, tr)] += 1
                if rnd:
                    tab_rand[(walk, tr)] += 1
    tot = sum(tab.values())
    totr = sum(tab_rand.values())
    print(f"classes {ncls} (random {nrand}); components {tot} (random {totr}, {totr / max(1, nrand):.3f} per class; note 22: 650,334 / 225,208 = 2.888)")
    for k, v in sorted(tab.items(), key=lambda kv: -kv[1]):
        print(f"   {v:7d} ({tab_rand[k]:6d}, {100 * tab_rand[k] / max(1, totr):.2f} %)  {k[0]} | {k[1]}")


if __name__ == "__main__":
    main()
