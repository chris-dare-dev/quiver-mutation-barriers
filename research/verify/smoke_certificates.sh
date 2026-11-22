#!/bin/sh
# smoke_certificates.sh -- the repository's own certificate programs, run from a clean copy (no data archive, no package).
# Usage: sh research/verify/smoke_certificates.sh      (PYTHON=python3.12 sh research/verify/smoke_certificates.sh to choose the interpreter)
# About 10 seconds.  Each line prints the last line of the program's output and the value it must have.
set -e
PY="${PYTHON:-python3}"
cd "$(dirname "$0")/../experiments"
fail=0
check() {    # check LABEL EXPECTED ACTUAL
    if [ "$2" = "$3" ]; then echo "ok        $1: $3"; else echo "MISMATCH  $1: got '$3', expected '$2'"; fail=1; fi
}
check "Theorem 15.13 (R_b), n4_doors.py prove2" "30 claims, ALL CERTIFIED" "$($PY -I n4_doors.py prove2 | tail -1)"
check "Theorem 15.6 (Q_t), n4_doors.py prove" "43 claims, ALL CERTIFIED" "$($PY -I n4_doors.py prove | tail -1)"
out="$($PY -I np_corridor_prove.py prove --T0 8 --audit-tmax 7)"
check "Theorem 16.6 (P+_t), np_corridor_prove.py prove" "938 claims, 149 members, ALL CERTIFIED" "$(echo "$out" | grep 'claims,')"
check "  its exits" "exits by verdict: {'fork': 54, 'height': 428, 'member': 161, 'new': 123}" "$(echo "$out" | grep '^exits by verdict')"
check "Theorem 18.4 (Q_7 route), np_rowwalk.py" "a=7 w=8 H=1242 H/w^3=2.426 H/w^2.5=6.861 | route: 3120 mutations, height 1242, 1 quivers at H, closed forms at 98 turns ok" "$($PY -I np_rowwalk.py family --amin 7 --amax 7 --search-amax 0 | grep '^a=7' | sed 's/ | all checks ok.*//')"
if [ $fail = 0 ]; then echo "ALL CERTIFICATE PROGRAMS AGREE"; else exit 1; fi
