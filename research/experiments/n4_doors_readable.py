#!/usr/bin/env python
"""
n4_doors_readable.py -- the polynomial certificates of note 15, written out claim by claim.

`n4_doors.py prove2` certifies the 30 claims behind Theorem 15.13 (R_b for even b >= 6) and `n4_doors.py prove`
the 43 claims behind Theorem 15.6 (Q_t for t >= 3).  Their logs give one line per claim.  This script runs the
same certificates and prints, under each claim, every symbolic step the program made for it: each mutation with
the quiver it was applied to and the result, each relabelling found, the entry that certifies "height >= H", and
the point of return of each fork.  A reader can then check a claim by hand from the formulas.

It changes nothing in n4_doors.py: it wraps the functions smutate, same_up_to_relabelling, cert_height and
cert_fork of that module while the certificate runs, so what is printed is what was certified, not a second
derivation.

Reading the output.  A quiver is (b01, b02, b03, b12, b13, b23); b_ij > 0 means b_ij arrows i -> j.  Entries are
polynomials in the variables of n4_doors.py.  In prove2 the variable t stands for c = b/2, and j, v are the
indices of the general member A(j), with c = j + v + 1; n and u are the indices along the plateau.  A domain such
as {'t': 3} is the orthant t >= 3.  "p >= 0 on the domain" is certified by shifting every variable to its lower
bound and checking that no coefficient of the expanded polynomial is negative.

Usage:  python -I n4_doors_readable.py prove2 > n4_doors_prove2_readable.log     (Theorem 15.13; under a second)
        python -I n4_doors_readable.py prove  > n4_doors_prove_readable.log      (Theorem 15.6; a few seconds)
No package is needed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n4_doors as D  # noqa: E402

TRACE = []


def show(q):
    return "(" + ",  ".join(repr(D.P.lift(e)) for e in q) + ")"


def wrap():
    base_mut, base_same, base_h, base_f = D.smutate, D.same_up_to_relabelling, D.cert_height, D.cert_fork

    def smutate(q, k, dom):
        m = base_mut(q, k, dom)
        TRACE.append("mutation at vertex %d, signs certified on %s\n          of  %s\n          is  %s" % (k, dom, show(q), show(m)))
        return m

    def same(q1, q2):
        p = base_same(q1, q2)
        TRACE.append("equal up to relabelling: %s\n          %s\n          %s" % (
            "new vertex i is old vertex p[i], p = %s" % (p,) if p is not None else "NO RELABELLING FOUND", show(q1), show(q2)))
        return p

    def cert_height(q, H, dom):
        a = base_h(q, H, dom)
        if a is not None:
            e = D.P.lift(q[a])
            s = D.wsign(e, dom)
            TRACE.append("height: the entry b%d%d = %r has sign %+d on %s, and |b%d%d| - H = %r >= 0 there" % (
                D.PAIRS[a] + (e, s, dom) + D.PAIRS[a] + (s * e - H,)))
        else:
            TRACE.append("height: NO ENTRY CERTIFIED")
        return a

    def cert_fork(q, dom, b):
        r = base_f(q, dom, b)
        TRACE.append("fork: %s on %s; every entry has absolute value >= 2 and a certified sign, some entry exceeds b = %r"
                     % ("point of return %s" % r if r is not None else "NOT CERTIFIED", dom, D.P.lift(b)))
        return r

    D.smutate, D.same_up_to_relabelling, D.cert_height, D.cert_fork = smutate, same, cert_height, cert_fork


class Interleave:
    """Writes the lines of the certificate, each followed by the steps recorded since the previous line."""
    def __init__(self, out):
        self.out, self.buf, self.n = out, "", 0

    def write(self, s):
        self.buf += s
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            is_claim = line.rstrip().endswith(("ok", "FAILED")) or "  ok  " in line or " ok     " in line or "FAILED" in line
            if is_claim:
                self.n += 1
                self.out.write("claim %d.  %s\n" % (self.n, line))
                for t in TRACE:
                    self.out.write("        - " + t + "\n")
                if not TRACE:
                    self.out.write("        - a polynomial identity or inequality in the entries above, checked coefficient by coefficient\n")
                self.out.write("\n")
            else:
                self.out.write(line + "\n")
            del TRACE[:]

    def flush(self):
        self.out.flush()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("prove", "prove2"):
        sys.exit(__doc__)
    which = sys.argv[1]
    out = sys.stdout
    if which == "prove2":
        out.write("# Theorem 15.13: R_b = (-b, -b, b-1, -2, b-2, -b), b = 2c even, c >= 3, H = 2b^2 - 3b - 3.\n"
                  "# In the formulas t stands for c.  Lam(xk, yk, xl, yl, z) = (2, -xk, -xl, -yk, -yl, z): vertices 0, 1 carry the\n"
                  "# double arrow 0 -> 1, the column of vertex 2 is (xk, yk), the column of vertex 3 is (xl, yl), and b23 = z.\n"
                  "# Members: A(0) = R_b relabelled, A(j) = Lam((2j-1)b, -(2j+1)b, 2(c-j), -2(c-j-1), b-1) for 1 <= j <= c-1,\n"
                  "#          A(c) = Lam((2c-1)b, -(2c+1)b, 0, 2, b-1), B = mu_3 A(c-1), B' = mu_3 A(c).\n"
                  "# Plateau: P(m) = Lam(2(T-1-m), -2(T-m), 2(m-1), -2(m-2), H), 1 <= m <= T = b(b-1)/2 (with the end cases printed below).\n"
                  "# A forward step mutates at vertex 0 and exchanges the names 0, 1; a backward step mutates at 1 and exchanges them.\n\n")
    else:
        out.write("# Theorem 15.6: Q_t for t >= 3, H_t = 2t^4 - t^3 - t^2 + 2t.  The members are defined in n4_doors.py (cmd_prove).\n\n")
    wrap()
    sys.stdout = Interleave(out)
    try:
        (D.cmd_prove2 if which == "prove2" else D.cmd_prove)(None)
    finally:
        sys.stdout = out


if __name__ == "__main__":
    main()
