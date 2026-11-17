#!/usr/bin/env python
"""
np_corridor_members.py -- the member families of the certificate of note 16 (Theorem 16.6, P+_t for t >= T0), written out.

np_corridor_prove.py certifies the lower bound for P+_t by listing families of quivers with polynomial entries
(the members) and classifying every mutation of every member.  Its log names the members but does not print
their entries.  This script runs the same certificate, records every member the program creates, and prints for
each one its name, the orthant of parameters on which it is used, how it was derived, and its ten entries as
polynomials.  It changes nothing in np_corridor_prove.py: it wraps the class Member of that module and reads the
member names from the program's own output, so the list printed here is the list that was certified, not a second derivation of it.

Vertices x = 0, p = 1, q = 2, c1 = 3, c = 4.  An entry b_uv > 0 means b_uv arrows u -> v.  A domain such as
{'t': 8, 'j': 2} is the orthant t >= 8, j >= 2; variables listed under "fixed" are set to the value shown.
The variables are those of np_corridor_prove.py: t, and the line variables j, v (K), i, r (L), k, u (M1), m (M2),
with t = j + v + 1 on K and t = k + u + 2 on M1; r stands for N + 1 - i on L, N = 2t^3 - t^2 - t.

Usage:  python -I np_corridor_members.py [--T0 8] > np_corridor_members.log        about one minute, no package
"""
import argparse
import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import np_corridor_prove as M  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--T0", type=int, default=8)
    a = ap.parse_args()
    created = []
    final = []
    BaseMember = M.Member

    class Recorded(BaseMember):
        def __init__(self, *args, **kw):
            BaseMember.__init__(self, *args, **kw)
            created.append(self)

    M.Member = Recorded
    buf = io.StringIO()
    args = argparse.Namespace(T0=a.T0, depth=2, split=2, quiet=False, audit_tmax=a.T0 - 1, debug=0)
    with contextlib.redirect_stdout(buf):
        M.cmd_prove(args)
    log = buf.getvalue().split("\n")
    summary = [x for x in log if "claims," in x or x.startswith("exits by verdict") or x.startswith("failed")]
    # the members are the quivers of the final loop of cmd_prove (the claims "above t^2: NAME on DOMAIN"),
    # and K0 = P+_t itself, which is the first member created
    listed, missing = [created[0]], []
    for line in log:
        if not line.startswith("above t^2: "):
            continue
        name, dom = line[len("above t^2: "):].rsplit(" on ", 1)
        name, dom = name.strip(), dom.split("}")[0] + "}"
        cands = [mem for mem in created if mem.name == name and str(mem.dom) == dom]
        if not cands or any(repr(c.M) != repr(cands[0].M) for c in cands):
            missing.append((name, dom, len(cands)))
            continue
        listed.append(cands[0])
    print("# Members of the certificate of np_corridor_prove.py prove --T0 %d" % a.T0)
    print("# the certificate program reported:")
    for x in summary:
        print("#   " + x)
    print("# members written out below: %d" % len(listed))
    print("# entry order: " + " ".join("b_%s%s" % (M.NAMES[i], M.NAMES[j]) for i in range(M.N5) for j in range(i + 1, M.N5)))
    for n, mem in enumerate(listed, 1):
        print()
        print("member %d: %s" % (n, mem.name))
        print("  domain: %s%s" % (mem.dom, "   fixed: %s" % mem.fixed if mem.fixed else ""))
        if mem.word:
            print("  derived from its line member by the mutations at: %s" % " ".join(M.NAMES[w] for w in mem.word))
        if n == 1:
            print("  this is P+_t itself, the one member of height t^2")
        for i in range(M.N5):
            for j in range(i + 1, M.N5):
                print("  b_%s%s = %r" % (M.NAMES[i], M.NAMES[j], mem.M[i][j]))
    if missing:
        print("\nWARNING: %d members of the certificate could not be matched: %s" % (len(missing), missing[:5]))
        sys.exit(1)


if __name__ == "__main__":
    main()
