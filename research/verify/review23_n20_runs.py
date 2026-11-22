"""Review of note 20: drive review23_n20_search and compare with note 20's data files.

Usage:
  python -I review23_n20_runs.py STORE PRUNE A1 A2 ... > log
    STORE = labelled | classes, PRUNE = 0 | 1.
Writes one JSON line per a to review23_n20_search_<store>_<mode>.jsonl (appending) and a
comparison line to stdout.  Note 20's numbers are read from np_qa_core_family*.jsonl as data.
Note 18's np_barrier counts with fork pruning (quivers popped, forks included) for a = 23..26
are typed in from note 18 section 5.2.
"""
import json
import os
import subprocess
import sys
import time

CODE = os.path.dirname(os.path.abspath(__file__))            # verify/
HERE = os.path.join(os.path.dirname(CODE), "experiments")    # the scripts under review and all stored results
BIN = os.path.expanduser('~/.cache/qmb-review23/review23_n20_search')
os.makedirs(os.path.dirname(BIN), exist_ok=True)
P66_PRUNED = {23: 23800313, 24: 29501788, 25: 36312433, 26: 44255806}


def load(fn):
    out = {}
    with open(os.path.join(HERE, fn)) as f:
        for line in f:
            r = json.loads(line)
            out[r['a']] = r
    return out


def main():
    store, prune = sys.argv[1], int(sys.argv[2])
    alist = [int(x) for x in sys.argv[3:]]
    ref = load('np_qa_core_family.jsonl' if prune else 'np_qa_core_family_nofork.jsonl')
    mode = 'pruned' if prune else 'nopruning'
    outfn = os.path.join(HERE, 'review23_n20_search_%s_%s.jsonl' % (store, mode))
    print('# review23_n20_search, store=%s, prune=%d, started %s' % (store, prune, time.strftime('%Y-%m-%d %H:%M:%S')))
    for a in alist:
        est = ref[a]['members'] if a in ref else int((4.0 if prune else 12.5) * a**5)
        if store == 'labelled':
            est *= 120 if a in (2, 4) else 12
        cap = est * 1.15 / 1e6 + 1.0
        t0 = time.time()
        res = subprocess.run([BIN, str(a), str(prune), '%.3f' % cap, '1' if store == 'classes' else '0'],
                             capture_output=True, text=True)
        if res.returncode != 0:
            print('a=%d FAILED rc=%d %s' % (a, res.returncode, res.stderr.strip()))
            sys.stdout.flush()
            continue
        r = json.loads(res.stdout)
        r['wall'] = round(time.time() - t0, 1)
        with open(outfn, 'a') as f:
            f.write(json.dumps(r) + '\n')
        line = ('a=%d H=%d entries=%d G\'=%d classes=%d (rem %d) stored20=%d forks=%d low=%d low_not_Q_a=%d '
                'low_forks=%d wall=%.1fs' % (a, r['H'], r['stored_entries'], r['G_prime'], r['classes'],
                                             r['classes_remainder'], r['stored_sense_71_classes'],
                                             r['fork_classes'], r['low_relabellings_of_Q_a'], r['low_others'],
                                             r['forks_of_height_le_w'], r['wall']))
        if a in ref:
            q = ref[a]
            same = (q['members'] == r['classes'] and q['stored'] == r['stored_sense_71_classes']
                    and q['members_of_height_le_w'] == 1 and q['forks_of_height_le_w'] == r['forks_of_height_le_w']
                    and q['H'] == r['H'])
            line += ' | note20: members=%d stored=%d -> %s' % (q['members'], q['stored'], 'equal' if same else 'DIFFERENT')
        else:
            line += ' | note20: no entry'
        if prune and a in P66_PRUNED:
            tot = r['classes'] + r['fork_classes']
            line += ' | note18 np_barrier popped %d vs members+forks %d -> %s' % (
                P66_PRUNED[a], tot, 'equal' if tot == P66_PRUNED[a] else 'DIFFERENT')
        print(line)
        sys.stdout.flush()


if __name__ == '__main__':
    main()
