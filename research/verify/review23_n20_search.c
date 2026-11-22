/* Review of note 20 (note 23): labelled breadth-first search from Q_a.
 *
 * Written from the definitions only; nothing is taken from np_qa_core.c,
 * np_barrier.c or the other scripts under review.
 *
 * Usage: review23_n20_search a mode capacity_millions
 *   mode 0: no pruning.  Every 5x5 labelled skew-symmetric matrix reached from Q_a
 *           (x = vertex 0) through matrices of height < H(a) is stored.
 *   mode 1: forks (Warkentin, Def. 2.1, any number of vertices) are not expanded.
 *           Non-fork matrices of height < H(a) are stored; the forks of height < H(a)
 *           met as exits are stored in a second set and not expanded.
 * No canonical form is used during the search.  Afterwards:
 *   - every stored matrix of height <= a+1 is compared with Q_a under all 120 relabellings;
 *   - |Aut X| is computed for every stored X, and the number of classes is
 *     sum |Aut X| / |G'|, with |G'| = (labelled copies of Q_a reached) * |Aut Q_a|
 *     (argument in note 23);
 *   - deg X = number of the five mutations that are members; X counts as
 *     "stored in the sense of note 20 section 2.2" if deg != 2 or ht X <= a+1.
 * Entries are packed 19 bits each (|entry| < 2^18), 24 bytes per matrix.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define NB 19
#define OFF (1 << 18)
#define MASK ((1ULL << NB) - 1)

typedef struct { uint64_t w[3]; } key3;

static long long H, W;
static int PRUNE;

static int IDX[5][5];
static int PI[10], PJ[10];

static inline void pack(const long long *u, key3 *k) {
    k->w[0] = k->w[1] = k->w[2] = 0;
    for (int i = 0; i < 10; i++) {
        uint64_t v = (uint64_t)(u[i] + OFF);
        int bp = NB * i, wd = bp >> 6, of = bp & 63;
        k->w[wd] |= v << of;
        if (of + NB > 64) k->w[wd + 1] |= v >> (64 - of);
    }
}
static inline void unpack(const key3 *k, long long *u) {
    for (int i = 0; i < 10; i++) {
        int bp = NB * i, wd = bp >> 6, of = bp & 63;
        uint64_t v = k->w[wd] >> of;
        if (of + NB > 64) v |= k->w[wd + 1] << (64 - of);
        v &= MASK;
        u[i] = (long long)v - OFF;
    }
}
static inline uint64_t hash3(const key3 *k) {
    uint64_t h = k->w[0] * 0x9E3779B97F4A7C15ULL;
    h ^= (k->w[1] + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL;
    h ^= (k->w[2] + 0x85EBCA77C2B2AE63ULL) * 0x165667B19E3779F9ULL;
    h ^= h >> 31; h *= 0xBF58476D1CE4E5B9ULL; h ^= h >> 29; h *= 0x94D049BB133111EBULL; h ^= h >> 32;
    return h;
}

typedef struct {
    key3 *E; uint32_t *T; uint64_t n, cap, tmask;
} hset;

static void hs_init(hset *s, uint64_t cap) {
    s->cap = cap; s->n = 0;
    uint64_t ts = 1; while (ts < cap + cap / 2 + 16) ts <<= 1;
    s->tmask = ts - 1;
    s->E = (key3 *)malloc(cap * sizeof(key3));
    s->T = (uint32_t *)calloc(ts, sizeof(uint32_t));
    if (!s->E || !s->T) { fprintf(stderr, "alloc failed\n"); exit(2); }
}
/* returns 1 if inserted, 0 if present */
static int hs_insert(hset *s, const key3 *k) {
    uint64_t h = hash3(k) & s->tmask;
    for (;;) {
        uint32_t e = s->T[h];
        if (e == 0) {
            if (s->n >= s->cap) { fprintf(stderr, "capacity exceeded\n"); exit(3); }
            s->E[s->n] = *k; s->n++; s->T[h] = (uint32_t)s->n;
            return 1;
        }
        key3 *o = &s->E[e - 1];
        if (o->w[0] == k->w[0] && o->w[1] == k->w[1] && o->w[2] == k->w[2]) return 0;
        h = (h + 1) & s->tmask;
    }
}

static void tomat(const long long *u, long long B[5][5]) {
    for (int i = 0; i < 5; i++) B[i][i] = 0;
    for (int t = 0; t < 10; t++) { B[PI[t]][PJ[t]] = u[t]; B[PJ[t]][PI[t]] = -u[t]; }
}

/* acyclic test of the full subquiver on vertex mask */
static int acyclic_mask(long long B[5][5], int mask) {
    while (mask) {
        int found = -1;
        for (int v = 0; v < 5 && found < 0; v++) {
            if (!(mask >> v & 1)) continue;
            int src = 1;
            for (int u = 0; u < 5; u++) if (u != v && (mask >> u & 1) && B[u][v] > 0) { src = 0; break; }
            if (src) found = v;
        }
        if (found < 0) return 0;
        mask &= ~(1 << found);
    }
    return 1;
}

static int is_fork(long long B[5][5]) {
    for (int t = 0; t < 10; t++) { long long v = B[PI[t]][PJ[t]]; if (v < 2 && v > -2) return 0; }
    if (acyclic_mask(B, 31)) return 0;
    for (int r = 0; r < 5; r++) {
        int in = 0, out = 0;
        for (int i = 0; i < 5; i++) if (i != r) { if (B[i][r] > 0) in |= 1 << i; else out |= 1 << i; }
        int ok = 1;
        for (int i = 0; i < 5 && ok; i++) if (in >> i & 1)
            for (int j = 0; j < 5 && ok; j++) if (out >> j & 1)
                if (!(B[j][i] > B[i][r] && B[j][i] > B[r][j])) ok = 0;
        if (ok && acyclic_mask(B, in) && acyclic_mask(B, out)) return 1;
    }
    return 0;
}

static int PERM[120][5];
static void gen_perms(void) {
    int c = 0, p[5];
    for (p[0] = 0; p[0] < 5; p[0]++) for (p[1] = 0; p[1] < 5; p[1]++) for (p[2] = 0; p[2] < 5; p[2]++)
    for (p[3] = 0; p[3] < 5; p[3]++) for (p[4] = 0; p[4] < 5; p[4]++) {
        int used = 0, okk = 1;
        for (int i = 0; i < 5; i++) { if (used >> p[i] & 1) okk = 0; used |= 1 << p[i]; }
        if (okk) { memcpy(PERM[c], p, sizeof p); c++; }
    }
}
/* X == Y relabelled by perm t: Y[t[i]][t[j]] == X[i][j] for all i, j */
static int iso_by(long long X[5][5], long long Y[5][5], const int *t) {
    for (int i = 0; i < 5; i++) for (int j = i + 1; j < 5; j++) if (Y[t[i]][t[j]] != X[i][j]) return 0;
    return 1;
}
static int aut_order(long long B[5][5]) {
    long long inv[5];
    for (int v = 0; v < 5; v++) {
        long long pos = 0, neg = 0;
        for (int j = 0; j < 5; j++) { if (B[v][j] > 0) pos += B[v][j]; else neg -= B[v][j]; }
        inv[v] = pos * 4000000LL + neg;
    }
    int distinct = 1;
    for (int i = 0; i < 5; i++) for (int j = i + 1; j < 5; j++) if (inv[i] == inv[j]) distinct = 0;
    if (distinct) return 1;
    int c = 0;
    for (int p = 0; p < 120; p++) {
        int ok = 1;
        for (int i = 0; i < 5; i++) if (inv[PERM[p][i]] != inv[i]) { ok = 0; break; }
        if (ok && iso_by(B, B, PERM[p])) c++;
    }
    return c;
}
static int is_relabelling(long long X[5][5], long long Y[5][5]) {
    for (int p = 0; p < 120; p++) if (iso_by(X, Y, PERM[p])) return 1;
    return 0;
}

/* Canonical form (mode canonical only): sort the vertices by a relabelling-invariant
 * key (sum of out-weights, sum of in-weights, largest signed entry of the row), and take
 * the lexicographic maximum of the upper triangle over the orders compatible with it. */
static void canon5(long long B[5][5], long long *out) {
    uint64_t inv[5];
    for (int v = 0; v < 5; v++) {
        long long pos = 0, neg = 0, mx = -OFF;
        for (int j = 0; j < 5; j++) if (j != v) {
            if (B[v][j] > 0) pos += B[v][j]; else neg -= B[v][j];
            if (B[v][j] > mx) mx = B[v][j];
        }
        inv[v] = ((uint64_t)pos << 39) | ((uint64_t)neg << 19) | (uint64_t)(mx + OFF);
    }
    uint64_t sinv[5]; memcpy(sinv, inv, sizeof inv);
    for (int i = 1; i < 5; i++) { uint64_t x = sinv[i]; int j = i - 1; while (j >= 0 && sinv[j] < x) { sinv[j + 1] = sinv[j]; j--; } sinv[j + 1] = x; }
    int first = 1;
    long long best[10], cur[10];
    for (int p = 0; p < 120; p++) {
        const int *t = PERM[p];
        int ok = 1;
        for (int i = 0; i < 5; i++) if (inv[t[i]] != sinv[i]) { ok = 0; break; }
        if (!ok) continue;
        for (int q = 0; q < 10; q++) cur[q] = B[t[PI[q]]][t[PJ[q]]];
        if (first) { memcpy(best, cur, sizeof cur); first = 0; }
        else {
            for (int q = 0; q < 10; q++) { if (cur[q] != best[q]) { if (cur[q] > best[q]) memcpy(best, cur, sizeof cur); break; } }
        }
    }
    memcpy(out, best, sizeof best);
}

static long long Hof(long long a) {
    if (a % 2) return 4 * a * a * a - 3 * a * a + (5 * a - 1) / 2;
    return 4 * a * a * a - 3 * a * a + (3 * a - 4) / 2;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s a prune(0/1) cap_millions canonical(0/1)\n", argv[0]); return 1; }
    long long a = atoll(argv[1]);
    PRUNE = atoi(argv[2]);
    uint64_t cap = (uint64_t)(atof(argv[3]) * 1e6);
    int CANON = atoi(argv[4]);
    H = Hof(a); W = a + 1;
    if (H > (1 << 18)) { fprintf(stderr, "H too large for packing\n"); return 1; }
    { int t = 0; for (int i = 0; i < 5; i++) for (int j = i + 1; j < 5; j++) { IDX[i][j] = t; PI[t] = i; PJ[t] = j; t++; } }
    gen_perms();
    clock_t t0 = clock();

    long long q0[10] = { -(a - 3), a - 2, a + 1, -(a + 1), -(a + 1), -a, 2, -2, -a, -(a + 1) };
    long long QA[5][5]; tomat(q0, QA);
    long long cq[10]; canon5(QA, cq);

    hset S, F;
    hs_init(&S, cap);
    hs_init(&F, PRUNE ? 8000000 : 16);
    key3 k; pack(CANON ? cq : q0, &k); hs_insert(&S, &k);

    uint64_t nhigh = 0, nforkexit = 0, nforklow = 0, depth = 0, level_end = 1;
    static uint64_t low_idx[1 << 16]; int nlow = 0;
    unsigned long long sum_aut = 0, sum_aut_stored = 0, n_aut_nontriv = 0, n_stored_lab = 0;
    unsigned long long deg_hist[6] = {0};
    low_idx[nlow++] = 0;
    int qa_is_fork = is_fork(QA);

    long long u[10], B[5][5], c[10], cc[10];
    for (uint64_t i = 0; i < S.n; i++) {
        if (i == level_end) { depth++; level_end = S.n; }
        unpack(&S.E[i], u);
        tomat(u, B);
        long long htB = 0; for (int t = 0; t < 10; t++) { long long v = u[t] < 0 ? -u[t] : u[t]; if (v > htB) htB = v; }
        int deg = 0;
        for (int kk = 0; kk < 5; kk++) {
            long long ht = 0;
            for (int t = 0; t < 10; t++) {
                int ii = PI[t], jj = PJ[t];
                long long v;
                if (ii == kk || jj == kk) v = -B[ii][jj];
                else {
                    long long bik = B[ii][kk], bkj = B[kk][jj];
                    v = B[ii][jj];
                    if (bik > 0 && bkj > 0) v += bik * bkj;
                    else if (bik < 0 && bkj < 0) v -= bik * bkj;
                }
                c[t] = v;
                long long av = v < 0 ? -v : v;
                if (av > ht) ht = av;
            }
            if (ht >= H) { nhigh++; continue; }
            long long C[5][5]; tomat(c, C);
            if (PRUNE && is_fork(C)) {
                nforkexit++;
                key3 kf;
                if (CANON) { canon5(C, cc); pack(cc, &kf); } else pack(c, &kf);
                if (hs_insert(&F, &kf) && ht <= W) nforklow++;
                continue;
            }
            deg++;
            key3 kn;
            if (CANON) { canon5(C, cc); pack(cc, &kn); } else pack(c, &kn);
            if (hs_insert(&S, &kn) && ht <= W) { if (nlow < (1 << 16)) low_idx[nlow++] = S.n - 1; else { fprintf(stderr, "too many low\n"); return 4; } }
        }
        int au = CANON ? 1 : aut_order(B);
        sum_aut += au; if (au > 1) n_aut_nontriv++;
        deg_hist[deg]++;
        if (deg != 2 || htB <= W) { sum_aut_stored += au; n_stored_lab++; }
    }

    /* low quivers: relabellings of Q_a?  In labelled mode also list the relabellings. */
    int copies = 0, others = 0;
    char gperms[4096]; gperms[0] = 0; int gl = 0;
    for (int t = 0; t < nlow; t++) {
        unpack(&S.E[low_idx[t]], u); tomat(u, B);
        int found = -1;
        for (int p = 0; p < 120; p++) if (iso_by(QA, B, PERM[p])) { found = p; break; }
        if (found >= 0) {
            copies++;
            if (!CANON && gl < 3900) gl += snprintf(gperms + gl, sizeof gperms - gl, "%s\"%d%d%d%d%d\"", copies > 1 ? ", " : "",
                    PERM[found][0], PERM[found][1], PERM[found][2], PERM[found][3], PERM[found][4]);
        } else others++;
    }
    int autQ = aut_order(QA);
    unsigned long long G = CANON ? 1ULL : (unsigned long long)copies * autQ;
    unsigned long long sum_aut_f = 0;
    for (uint64_t i = 0; i < F.n && PRUNE; i++) { unpack(&F.E[i], u); tomat(u, B); sum_aut_f += CANON ? 1 : aut_order(B); }

    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("{\"a\": %lld, \"mode\": \"%s\", \"store\": \"%s\", \"H\": %lld, \"w\": %lld, \"stored_entries\": %llu, "
           "\"Q_a_is_fork\": %d, \"aut_Q_a\": %d, \"low_entries\": %d, \"low_relabellings_of_Q_a\": %d, \"low_others\": %d, "
           "\"G_prime\": %llu, \"G_prime_perms\": [%s], \"classes\": %llu, \"classes_remainder\": %llu, "
           "\"entries_with_nontrivial_aut\": %llu, \"stored_sense_71_classes\": %llu, \"stored_remainder\": %llu, "
           "\"deg_hist\": [%llu, %llu, %llu, %llu, %llu, %llu], "
           "\"exits_high\": %llu, \"fork_exits\": %llu, \"fork_entries\": %llu, \"fork_classes\": %llu, \"fork_remainder\": %llu, "
           "\"forks_of_height_le_w\": %llu, \"max_bfs_depth\": %llu, \"seconds\": %.1f}\n",
           a, PRUNE ? "forks-not-expanded" : "no-pruning", CANON ? "classes" : "labelled", H, W, (unsigned long long)S.n,
           qa_is_fork, autQ, nlow, copies, others, G, gperms,
           G ? sum_aut / G : 0ULL, G ? sum_aut % G : 0ULL,
           n_aut_nontriv, G ? sum_aut_stored / G : 0ULL, G ? sum_aut_stored % G : 0ULL,
           deg_hist[0], deg_hist[1], deg_hist[2], deg_hist[3], deg_hist[4], deg_hist[5],
           (unsigned long long)nhigh, (unsigned long long)nforkexit, (unsigned long long)F.n,
           G ? sum_aut_f / G : 0ULL, G ? sum_aut_f % G : 0ULL, (unsigned long long)nforklow,
           (unsigned long long)depth, secs);
    fflush(stdout);
    return 0;
}
