#!/usr/bin/env python
"""
review23_n21_blackbox.py -- BLACK-BOX driver for the review of note 21, item 3.

This is the only review script that touches owf_barrier.py: it imports it in its own process and calls the
structure-aware attacker (class Attack) as a black box.  Nothing of owf_barrier.py is
copied or adapted.  Input: a JSON file of instances built by review23_n21_review.py (Q, Q' as full matrices, the
public bound, the low height w).  Output (JSON lines, to a file under ~/.cache/qmb-review23/n21/): the attacker's summary,
its route length, and the route itself -- the literal word with the relabelling when it has at most --word-limit
mutations, otherwise the compressed pieces (fork-descent words, segments, extra mutations, relabelling).  The route is
checked afterwards by review23_n21_review.py with its own replay; nothing here is trusted beyond producing the route.
"""
import json
import os
import sys

EXP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments")
sys.path.insert(0, EXP)
import owf_barrier as ob     # black box


def main():
    inp, outp, limit = sys.argv[1], sys.argv[2], int(sys.argv[3])
    insts = json.load(open(inp))
    with open(outp, "w") as out:
        for inst in insts:
            Q = tuple(tuple(r) for r in inst["Q"])
            Qp = tuple(tuple(r) for r in inst["Qp"])
            A = ob.Attack(Q, Qp, inst["bound"], wlow=inst["w"], max_ops=4000, tmode="all", depth=4)
            r = {"id": inst["id"], "summary": A.summary()}
            if A.found:
                r["length"] = ob.found_length(A)
                (Y0, segs0, v0), (Y1, segs1, v1) = A.found
                perm = ob.iso_perm(Y0, Y1)
                r["pieces"] = {"wq": list(A.wq), "segs0": segs0, "v0": v0, "wqp": list(A.wqp), "segs1": segs1, "v1": v1,
                               "perm": perm}
                if r["length"] <= limit:
                    word, perm2 = A.word()
                    r["word"] = word
                    r["perm"] = perm2
            out.write(json.dumps(r) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
