/* review23_n21_search.c -- independent review code for note 21.
 *
 * Written from scratch for the review of note 21.  It does not include, copy or adapt np_barrier.c, owf_barrier.py,
 * np_corridor.py, np_rowwalk.py, n4_doors.py or any other script of the notes under check.
 *
 * Quivers: skew-symmetric integer matrices on n <= 8 vertices; entries int64, every product formed in __int128 and a
 * quiver with an entry above the bound is discarded before it is stored.  Input tuples are the upper triangle in row
 * order (b01, b02, ..., b12, ...), the convention of the notes.
 *
 * Canonical form (own design): each vertex gets a relabelling-invariant signature (two rounds of hashing of sorted
 * rows); vertices are ordered by signature, and the key is the lexicographic MAXIMUM, over all orderings that respect
 * the signature order, of the upper triangle read column by column ((0,1), (0,2), (1,2), (0,3), ...).
 *
 * Fork: Warkentin, Def. 2.1, read from note 19 section 4: every pair joined by >= 2 arrows, not acyclic, and a vertex
 * r with q_ji > q_ir and q_ji > q_rj for all i -> r -> j, and the in- and out-neighbours of r acyclic.
 *
 * Commands on stdin, one per line; one JSON line per command on stdout.
 *   minimax n w cap tie prune budget e...      lowest-bottleneck search from Q; stops when it POPS a quiver of
 *                                              height <= w not isomorphic to Q.  tie: 0 FIFO, 1 LIFO, 2 lowest height
 *                                              first, 3 random (seeded).  prune bit 0: forks higher than w are popped
 *                                              and counted but not expanded; bit 1: quivers of the plateau of Q (bottleneck
 *                                              <= w) are not targets, i.e. the escape level of note 16 section 6.1.
 *   comp n bound budget prune w e...           all quivers reachable from Q through quivers of height <= bound
 *   bibfs n bound budget prunew e(A)... e(B)... bidirectional BFS, fewest mutations from A to a relabelling of B;
 *                                              prunew > 0: forks higher than prunew are skipped
 *   replayfile path                            literal replay of a (compressed) route file, see read_prog
 *   plant n w cap maxmut k A B U V (k times) ne x y v (ne times)   the bounce-cycle planter of note 21 section 5.1, own code
 *   canon n e...                               print the canonical key
 *   isfork n e...                              print the point of return or -1
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef long long i64;
typedef __int128 i128;
#define MAXN 8
#define MAXM 28

typedef struct { i64 b[MAXN][MAXN]; } Qv;

static int N, M;

static i64 ht(const Qv *q) {
    i64 h = 0;
    for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) { i64 v = q->b[i][j] < 0 ? -q->b[i][j] : q->b[i][j]; if (v > h) h = v; }
    return h;
}

/* mutation at k; returns 0 if an entry exceeds bound in absolute value */
static int mutate(const Qv *in, int k, Qv *out, i64 bound) {
    for (int i = 0; i < N; i++) {
        out->b[i][i] = 0;
        for (int j = i + 1; j < N; j++) {
            i64 v;
            if (i == k || j == k) v = -in->b[i][j];
            else {
                i64 x = in->b[i][k], y = in->b[k][j];
                i128 w = in->b[i][j];
                if (x > 0 && y > 0) w += (i128)x * y;
                else if (x < 0 && y < 0) w -= (i128)x * y;
                if (w > bound || w < -(i128)bound) return 0;
                v = (i64)w;
            }
            if (v > bound || v < -bound) return 0;
            out->b[i][j] = v; out->b[j][i] = -v;
        }
    }
    return 1;
}

static void from_upper(const i64 *e, Qv *q) {
    int t = 0;
    memset(q, 0, sizeof(*q));
    for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) { q->b[i][j] = e[t]; q->b[j][i] = -e[t]; t++; }
}

static void neg(const Qv *a, Qv *o) { for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) o->b[i][j] = -a->b[i][j]; }

/* ------------------------------------------------------------------ canonical key */
static uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ULL; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL; x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL; return x ^ (x >> 31); }
static int cmpu64(const void *a, const void *b) { uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return x < y ? -1 : x > y; }

static int ord_v[MAXN], grp_of_pos[MAXN], used_v[MAXN], vgrp[MAXN];
static i64 best_t[MAXM], cur_t[MAXM];
static int have_best;
static const Qv *cq;
/* column-major position of (a, c), a < c */
static int cpos(int a, int c) { return c * (c - 1) / 2 + a; }

static void canon_rec(int pos, int state) {
    if (pos == N) {
        int gt = !have_best;
        for (int a = 0; a < M && !gt; a++) { if (cur_t[a] > best_t[a]) gt = 1; else if (cur_t[a] < best_t[a]) break; }
        if (gt) { memcpy(best_t, cur_t, sizeof(i64) * M); have_best = 1; }
        (void)state;
        return;
    }
    for (int v = 0; v < N; v++) {
        if (used_v[v] || vgrp[v] != grp_of_pos[pos]) continue;
        used_v[v] = 1; ord_v[pos] = v;
        int st = state, ok = 1;
        for (int a = 0; a < pos; a++) {
            i64 x = cq->b[ord_v[a]][v];
            cur_t[cpos(a, pos)] = x;
            if (have_best && st == 0) {
                i64 y = best_t[cpos(a, pos)];
                if (x < y) { ok = 0; break; }
                if (x > y) st = 1;
            }
        }
        if (ok) canon_rec(pos + 1, st);
        used_v[v] = 0;
    }
}

static void canon(const Qv *q, i64 *key) {
    uint64_t s1[MAXN], s2[MAXN], tmp[MAXN];
    for (int i = 0; i < N; i++) {
        int t = 0;
        for (int j = 0; j < N; j++) if (j != i) tmp[t++] = (uint64_t)q->b[i][j];
        qsort(tmp, t, sizeof(uint64_t), cmpu64);
        uint64_t h = 1469598103934665603ULL;
        for (int a = 0; a < t; a++) h = mix(h ^ tmp[a]);
        s1[i] = h;
    }
    for (int i = 0; i < N; i++) {
        int t = 0;
        for (int j = 0; j < N; j++) if (j != i) tmp[t++] = mix((uint64_t)q->b[i][j] * 0x100000001B3ULL ^ s1[j]);
        qsort(tmp, t, sizeof(uint64_t), cmpu64);
        uint64_t h = s1[i];
        for (int a = 0; a < t; a++) h = mix(h ^ tmp[a]);
        s2[i] = h;
    }
    /* order vertices by s2 (ascending), groups of equal s2 */
    int idx[MAXN];
    for (int i = 0; i < N; i++) idx[i] = i;
    for (int i = 1; i < N; i++) { int x = idx[i], j = i - 1; while (j >= 0 && s2[idx[j]] > s2[x]) { idx[j + 1] = idx[j]; j--; } idx[j + 1] = x; }
    int g = -1;
    for (int p = 0; p < N; p++) {
        if (p == 0 || s2[idx[p]] != s2[idx[p - 1]]) g++;
        grp_of_pos[p] = g; vgrp[idx[p]] = g;
    }
    memset(used_v, 0, sizeof(used_v));
    have_best = 0; cq = q;
    canon_rec(0, 0);
    memcpy(key, best_t, sizeof(i64) * M);
}

/* key -> quiver (in the canonical labelling) */
static void from_key(const i64 *key, Qv *q) {
    memset(q, 0, sizeof(*q));
    for (int c = 1; c < N; c++) for (int a = 0; a < c; a++) { q->b[a][c] = key[cpos(a, c)]; q->b[c][a] = -key[cpos(a, c)]; }
}

/* ------------------------------------------------------------------ forks */
static int acyclic_on(const Qv *q, const int *vs, int nv) {
    int indeg[MAXN] = {0}, alive[MAXN] = {0};
    for (int a = 0; a < nv; a++) alive[vs[a]] = 1;
    for (int a = 0; a < nv; a++) for (int c = 0; c < nv; c++) if (q->b[vs[a]][vs[c]] > 0) indeg[vs[c]]++;
    int removed = 0, progress = 1;
    while (progress) {
        progress = 0;
        for (int a = 0; a < nv; a++) {
            int v = vs[a];
            if (alive[v] && indeg[v] == 0) {
                alive[v] = 0; removed++; progress = 1;
                for (int c = 0; c < nv; c++) if (alive[vs[c]] && q->b[v][vs[c]] > 0) indeg[vs[c]]--;
            }
        }
    }
    return removed == nv;
}

static int fork_point(const Qv *q) {
    for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) { i64 v = q->b[i][j]; if (v < 2 && v > -2) return -1; }
    int all[MAXN];
    for (int i = 0; i < N; i++) all[i] = i;
    if (acyclic_on(q, all, N)) return -1;
    for (int r = 0; r < N; r++) {
        int in[MAXN], out[MAXN], ni = 0, no = 0;
        for (int v = 0; v < N; v++) { if (v == r) continue; if (q->b[v][r] > 0) in[ni++] = v; else out[no++] = v; }
        int ok = 1;
        for (int a = 0; a < ni && ok; a++) for (int c = 0; c < no && ok; c++) {
            int i = in[a], j = out[c];
            i64 qji = q->b[j][i];               /* arrows j -> i */
            if (!(qji > q->b[i][r] && qji > q->b[r][j])) ok = 0;
        }
        if (ok && acyclic_on(q, in, ni) && acyclic_on(q, out, no)) return r;
    }
    return -1;
}

/* ------------------------------------------------------------------ node store and hash */
typedef struct {
    i64 *keys; i64 *aux1; i64 *aux2; int *par; signed char *pv; unsigned char *flag;
    size_t n, cap;
    int *tab; size_t tcap;
} Store;

static uint64_t khash(const i64 *k) { uint64_t h = 0x12345; for (int a = 0; a < M; a++) h = mix(h ^ (uint64_t)k[a]); return h; }

static void st_init(Store *s, size_t cap) {
    s->cap = cap; s->n = 0;
    s->keys = malloc(sizeof(i64) * M * cap); s->aux1 = malloc(sizeof(i64) * cap); s->aux2 = malloc(sizeof(i64) * cap);
    s->par = malloc(sizeof(int) * cap); s->pv = malloc(cap); s->flag = calloc(cap, 1);
    s->tcap = 1; while (s->tcap < 2 * cap + 16) s->tcap <<= 1;
    s->tab = malloc(sizeof(int) * s->tcap); memset(s->tab, -1, sizeof(int) * s->tcap);
    if (!s->keys || !s->tab) { fprintf(stderr, "out of memory\n"); exit(1); }
}
static void st_free(Store *s) { free(s->keys); free(s->aux1); free(s->aux2); free(s->par); free(s->pv); free(s->flag); free(s->tab); }

/* find; if absent and ins, insert; returns index or -1; *isnew set */
static long st_get(Store *s, const i64 *k, int ins, int *isnew) {
    size_t m = s->tcap - 1, h = khash(k) & m;
    *isnew = 0;
    while (s->tab[h] >= 0) {
        if (memcmp(s->keys + (size_t)s->tab[h] * M, k, sizeof(i64) * M) == 0) return s->tab[h];
        h = (h + 1) & m;
    }
    if (!ins) return -1;
    if (s->n >= s->cap) return -2;
    long id = (long)s->n++;
    memcpy(s->keys + (size_t)id * M, k, sizeof(i64) * M);
    s->tab[h] = (int)id; *isnew = 1;
    return id;
}

/* ------------------------------------------------------------------ heap for minimax */
typedef struct { i64 bn; i64 tk; int id; } HE;
static HE *heap; static size_t hn, hcap;
static int he_less(const HE *a, const HE *b) { return a->bn < b->bn || (a->bn == b->bn && a->tk < b->tk); }
static void hpush(HE e) {
    if (hn == hcap) { hcap = hcap ? 2 * hcap : 1 << 16; heap = realloc(heap, sizeof(HE) * hcap); }
    size_t i = hn++; heap[i] = e;
    while (i > 0) { size_t p = (i - 1) / 2; if (he_less(&heap[i], &heap[p])) { HE t = heap[i]; heap[i] = heap[p]; heap[p] = t; i = p; } else break; }
}
static HE hpop(void) {
    HE top = heap[0]; heap[0] = heap[--hn];
    size_t i = 0;
    for (;;) { size_t l = 2 * i + 1, r = l + 1, m = i;
        if (l < hn && he_less(&heap[l], &heap[m])) m = l;
        if (r < hn && he_less(&heap[r], &heap[m])) m = r;
        if (m == i) break; HE t = heap[i]; heap[i] = heap[m]; heap[m] = t; i = m; }
    return top;
}

static uint64_t rng_state = 88172645463325252ULL;
static uint64_t xrand(void) { rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17; return rng_state; }

static void print_key(const i64 *k) { printf("["); for (int a = 0; a < M; a++) printf("%s%lld", a ? "," : "", k[a]); printf("]"); }

/* ------------------------------------------------------------------ minimax */
static void cmd_minimax(i64 w, i64 cap, int tie, int prune, long budget, const i64 *e) {
    Qv q, x, y; from_upper(e, &q);
    i64 kq[MAXM], knq[MAXM], k[MAXM];
    canon(&q, kq); { Qv nq; neg(&q, &nq); canon(&nq, knq); }
    Store s; st_init(&s, (size_t)budget + 8);
    /* aux1 = bottleneck, aux2 = height; flag bit0 popped, bit1 fork */
    int nw; long id0 = st_get(&s, kq, 1, &nw);
    s.aux1[id0] = ht(&q); s.aux2[id0] = ht(&q); s.par[id0] = -1; s.pv[id0] = -1;
    hn = 0; i64 seq = 0;
    hpush((HE){s.aux1[id0], 0, (int)id0});
    long popped = 0, forks = 0, target = -1; int status = 0; /* 0 exhausted, 1 found, 2 budget */
    i64 level_found = -1;
    long below = 0;
    while (hn > 0) {
        HE he = hpop();
        long id = he.id;
        if (s.flag[id] & 1) continue;
        if (he.bn != s.aux1[id]) continue;
        s.flag[id] |= 1; popped++;
        from_key(s.keys + (size_t)id * M, &x);
        if (s.aux2[id] <= w && memcmp(s.keys + (size_t)id * M, kq, sizeof(i64) * M) != 0 && (!(prune & 2) || s.aux1[id] > w)) { target = id; status = 1; level_found = s.aux1[id]; break; }
        if ((prune & 1) && s.aux2[id] > w && fork_point(&x) >= 0) { s.flag[id] |= 2; forks++; continue; }
        for (int v = 0; v < N; v++) {
            if (!mutate(&x, v, &y, cap)) continue;
            canon(&y, k);
            int isnew; long j = st_get(&s, k, 1, &isnew);
            if (j == -2) { status = 2; break; }
            i64 hy = ht(&y), bn = he.bn > hy ? he.bn : hy;
            if (isnew || (!(s.flag[j] & 1) && bn < s.aux1[j])) {
                s.aux1[j] = bn; s.aux2[j] = hy; s.par[j] = (int)id; s.pv[j] = (signed char)v;
                i64 tk;
                seq++;
                if (tie == 0) tk = seq; else if (tie == 1) tk = -seq; else if (tie == 2) tk = hy * (i64)1000000000 + seq; else tk = (i64)(xrand() >> 2);
                hpush((HE){bn, tk, (int)j});
            }
        }
        if (status == 2) break;
    }
    /* below = number of popped nodes with bottleneck < level_found */
    if (status == 1) for (size_t i = 0; i < s.n; i++) if ((s.flag[i] & 1) && s.aux1[i] < level_found) below++;
    long plen = 0;
    if (status == 1) { long c = target; while (s.par[c] >= 0) { plen++; c = s.par[c]; } }
    printf("{\"cmd\":\"minimax\",\"status\":\"%s\",\"level\":%lld,\"popped\":%ld,\"below\":%ld,\"forks_popped\":%ld,\"path_len\":%ld,\"stored\":%zu,\"target_is_neg\":%d",
           status == 1 ? "found" : status == 2 ? "budget" : "exhausted", (long long)level_found, popped, below, forks, plen, s.n,
           status == 1 ? (memcmp(s.keys + (size_t)target * M, knq, sizeof(i64) * M) == 0) : 0);
    if (status == 1) { printf(",\"target\":"); print_key(s.keys + (size_t)target * M); }
    printf("}\n"); fflush(stdout);
    st_free(&s);
}

/* ------------------------------------------------------------------ component */
static void cmd_comp(i64 bound, long budget, int prune, i64 w, const i64 *e) {
    Qv q, x, y; from_upper(e, &q);
    i64 k[MAXM];
    Store s; st_init(&s, (size_t)budget + 8);
    canon(&q, k); int nw; st_get(&s, k, 1, &nw);
    size_t head = 0; long forks = 0, low = 0; int status = 0;
    while (head < s.n) {
        long id = (long)head++;
        from_key(s.keys + (size_t)id * M, &x);
        if (ht(&x) <= w) low++;
        if (prune && ht(&x) > w && fork_point(&x) >= 0) { forks++; continue; }
        for (int v = 0; v < N; v++) {
            if (!mutate(&x, v, &y, bound)) continue;
            canon(&y, k);
            int isnew; long j = st_get(&s, k, 1, &isnew);
            if (j == -2) { status = 2; break; }
        }
        if (status) break;
    }
    printf("{\"cmd\":\"comp\",\"status\":\"%s\",\"size\":%zu,\"forks\":%ld,\"low\":%ld}\n", status ? "budget" : "closed", s.n, forks, low);
    fflush(stdout);
    st_free(&s);
}

/* ------------------------------------------------------------------ bidirectional BFS */
static void cmd_bibfs(i64 bound, long budget, i64 prunew, const i64 *ea, const i64 *eb) {
    Qv a, b, x, y; from_upper(ea, &a); from_upper(eb, &b);
    i64 ka[MAXM], kb[MAXM], k[MAXM];
    canon(&a, ka); canon(&b, kb);
    if (memcmp(ka, kb, sizeof(i64) * M) == 0) { printf("{\"cmd\":\"bibfs\",\"distance\":0}\n"); return; }
    Store s; st_init(&s, (size_t)budget + 8);
    /* aux1 = dist from A (or -1), aux2 = dist from B (or -1) */
    int nw; long ia = st_get(&s, ka, 1, &nw), ib = st_get(&s, kb, 1, &nw);
    s.aux1[ia] = 0; s.aux2[ia] = -1; s.aux1[ib] = -1; s.aux2[ib] = 0;
    long *fr[2], fn[2], fcap[2];
    for (int t = 0; t < 2; t++) { fcap[t] = 1024; fr[t] = malloc(sizeof(long) * fcap[t]); fn[t] = 0; }
    fr[0][fn[0]++] = ia; fr[1][fn[1]++] = ib;
    long depth[2] = {0, 0}; long best = -1; int status = 0; long pruned = 0;
    while (fn[0] > 0 && fn[1] > 0 && best < 0) {
        if ((long)s.n >= budget) { status = 2; break; }
        int sd = fn[0] <= fn[1] ? 0 : 1;
        long nn = 0, ncap = 1024; long *nx = malloc(sizeof(long) * ncap);
        for (long f = 0; f < fn[sd]; f++) {
            from_key(s.keys + (size_t)fr[sd][f] * M, &x);
            for (int v = 0; v < N; v++) {
                if (!mutate(&x, v, &y, bound)) continue;
                if (prunew > 0 && ht(&y) > prunew && fork_point(&y) >= 0) { pruned++; continue; }
                canon(&y, k);
                int isnew; long j = st_get(&s, k, 1, &isnew);
                if (j == -2) { status = 2; break; }
                i64 *mine = sd == 0 ? s.aux1 : s.aux2, *oth = sd == 0 ? s.aux2 : s.aux1;
                if (isnew) { mine[j] = -1; oth[j] = -1; }
                if (mine[j] >= 0) continue;
                mine[j] = depth[sd] + 1;
                if (oth[j] >= 0) { long d = depth[sd] + 1 + oth[j]; if (best < 0 || d < best) best = d; }
                if (nn == ncap) { ncap *= 2; nx = realloc(nx, sizeof(long) * ncap); }
                nx[nn++] = j;
            }
            if (status) break;
        }
        if (status) { free(nx); break; }      /* level not completed: do not count it */
        free(fr[sd]); fr[sd] = nx; fn[sd] = nn; depth[sd]++;
    }
    long lb = depth[0] + depth[1] + 1;
    if (best >= 0) printf("{\"cmd\":\"bibfs\",\"distance\":%ld,\"nodes\":%zu,\"pruned_hits\":%ld}\n", best, s.n, pruned);
    else if (fn[0] == 0 || fn[1] == 0) printf("{\"cmd\":\"bibfs\",\"distance\":null,\"closed\":1,\"nodes\":%zu}\n", s.n);
    else printf("{\"cmd\":\"bibfs\",\"distance\":null,\"budget\":1,\"lower_bound\":%ld,\"nodes\":%zu,\"depths\":[%ld,%ld]}\n", lb, s.n, depth[0], depth[1]);
    fflush(stdout);
    free(fr[0]); free(fr[1]); st_free(&s);
}

/* ------------------------------------------------------------------ literal replay of a compressed route file
 * format: line 1: n bound; line 2: Q (upper triangle); line 3: target (upper triangle, or 'none');
 * then ops: 'm v' | 'run p q l' | 'rep K' ... 'end' (no nesting needed but supported); the literal word of
 * 'run p q l' is p, q, p, q, ... (l letters); 'rep K' repeats its block K times. */
typedef struct Op { int kind; int v, p, q; long long l; long long K; struct Op *body; int nbody; } Op;
static FILE *pf;
static int read_block(Op **ops, int *nops) {
    char w[64]; int cap = 16, n = 0; Op *o = malloc(sizeof(Op) * cap);
    while (fscanf(pf, "%63s", w) == 1) {
        if (n == cap) { cap *= 2; o = realloc(o, sizeof(Op) * cap); }
        if (!strcmp(w, "end")) break;
        if (!strcmp(w, "m")) { o[n].kind = 0; if (fscanf(pf, "%d", &o[n].v) != 1) return 0; n++; }
        else if (!strcmp(w, "run")) { o[n].kind = 1; if (fscanf(pf, "%d %d %lld", &o[n].p, &o[n].q, &o[n].l) != 3) return 0; n++; }
        else if (!strcmp(w, "rep")) { o[n].kind = 2; if (fscanf(pf, "%lld", &o[n].K) != 1) return 0; read_block(&o[n].body, &o[n].nbody); n++; }
        else return 0;
    }
    *ops = o; *nops = n; return 1;
}
static Qv RX; static i64 RB, RH; static long long RLEN; static int RFAIL;
static inline void rstep(int v) {
    Qv y;
    if (RFAIL) return;
    if (!mutate(&RX, v, &y, RB)) { RFAIL = 1; return; }
    RX = y; RLEN++;
    i64 h = ht(&RX); if (h > RH) RH = h;
}
static void run_block(Op *o, int n) {
    for (int i = 0; i < n && !RFAIL; i++) {
        if (o[i].kind == 0) rstep(o[i].v);
        else if (o[i].kind == 1) { for (long long t = 0; t < o[i].l && !RFAIL; t++) rstep(t % 2 == 0 ? o[i].p : o[i].q); }
        else for (long long t = 0; t < o[i].K && !RFAIL; t++) run_block(o[i].body, o[i].nbody);
    }
}
static void cmd_replayfile(const char *path) {
    pf = fopen(path, "r");
    if (!pf) { printf("{\"cmd\":\"replay\",\"error\":\"open\"}\n"); return; }
    long long bnd; if (fscanf(pf, "%d %lld", &N, &bnd) != 2) return;
    M = N * (N - 1) / 2;
    i64 e[MAXM], t[MAXM];
    for (int a = 0; a < M; a++) if (fscanf(pf, "%lld", &e[a]) != 1) return;
    for (int a = 0; a < M; a++) if (fscanf(pf, "%lld", &t[a]) != 1) return;
    Op *ops; int nops; read_block(&ops, &nops); fclose(pf);
    from_upper(e, &RX); RB = bnd; RH = ht(&RX); RLEN = 0; RFAIL = 0;
    run_block(ops, nops);
    Qv tq; from_upper(t, &tq);
    int exact = !RFAIL;
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) if (RX.b[i][j] != tq.b[i][j]) exact = 0;
    i64 k1[MAXM], k2[MAXM]; canon(&RX, k1); canon(&tq, k2);
    int iso = !RFAIL && memcmp(k1, k2, sizeof(i64) * M) == 0;
    printf("{\"cmd\":\"replay\",\"failed_bound\":%d,\"length\":%lld,\"max_height\":%lld,\"end_equals_target\":%d,\"end_iso_target\":%d}\n",
           RFAIL, RLEN, (long long)RH, exact, iso);
    fflush(stdout);
}

/* ------------------------------------------------------------------ the planter of note 21 section 5.1 (own code)
 * Q = W_m(j) with m = 2w - 1, j = w on (p, q, r, s) = (0, 1, 2, 3) (note 18 section 2: two arrows q -> p, two arrows
 * s -> r, columns r: (m - j, -(m + 1 - j)), s: (j, -(j - 1))), and k further vertices 4, 5, ... with states
 * (A, B, U, V) = (b_px, b_qx, b_xr, b_xs).  The walk (note 21 section 4.1 item 2, turn set {r, s} = {2, 3}):
 *   late turn: a turn vertex y with column (b_py, b_qy) = (-eta, 0), eta >= 1: mutate y;
 *   early turn: column (0, -eta): mutate y if that is not higher than the step, else step (then a late turn follows);
 *   otherwise a step: mutate p and exchange the names p, q.
 * The walk stops when a mutation leaves the cap, when a labelled state after a turn repeats (a cycle), or after maxmut
 * mutations.  Forwards = from Q; backwards = the forward walk of -Q, mapped back by negation.  The planted Y is the first
 * quiver of height <= w on a walk that is not isomorphic to Q; between the two walks the shorter route wins (forward on
 * ties). */
typedef struct { int found; long long len; i64 h; Qv Y; int reason; long long muts; } WalkRes;

static void walk_plant(const Qv *start, i64 w, i64 cap, long long maxmut, const i64 *kq, WalkRes *R) {
    Qv X = *start, Y1, Y2;
    int p, q;
    if (X.b[1][0] == 2) { p = 0; q = 1; } else { p = 1; q = 0; }
    R->found = 0; R->len = 0; R->h = ht(&X); R->reason = 0; R->muts = 0;
    /* cycle detection: labelled states after turns */
    size_t tcap = 1 << 12; uint64_t *seen = calloc(tcap, sizeof(uint64_t)); size_t nseen = 0;
    i64 k[MAXM];
    while (R->muts < maxmut) {
        int mv = -1, isturn = 0;
        for (int y = 2; y <= 3 && mv < 0; y++) if (X.b[q][y] == 0 && X.b[p][y] < 0) { mv = y; isturn = 1; }
        if (mv < 0) for (int y = 2; y <= 3 && mv < 0; y++) if (X.b[p][y] == 0 && X.b[q][y] < 0) {
            int oky = mutate(&X, y, &Y1, (i64)4e18), okp = mutate(&X, p, &Y2, (i64)4e18);
            if (oky && (!okp || ht(&Y1) <= ht(&Y2))) { mv = y; isturn = 1; } else mv = p;
        }
        if (mv < 0) mv = p;
        Qv Z;
        if (!mutate(&X, mv, &Z, cap)) { R->reason = 1; break; }
        X = Z; R->muts++;
        if (mv == p) { int t = p; p = q; q = t; }
        i64 h = ht(&X); if (h > R->h) R->h = h;
        if (h <= w) {
            canon(&X, k);
            if (memcmp(k, kq, sizeof(i64) * M) != 0) { R->found = 1; R->len = R->muts; R->Y = X; break; }
        }
        if (isturn) {
            uint64_t hh = 0x777 ^ (uint64_t)p * 31 ^ (uint64_t)q * 131;
            for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) hh = mix(hh ^ (uint64_t)X.b[i][j]);
            if (hh == 0) hh = 1;
            size_t m = tcap - 1, s = hh & m; int rep = 0;
            while (seen[s]) { if (seen[s] == hh) { rep = 1; break; } s = (s + 1) & m; }
            if (rep) { R->reason = 2; break; }
            seen[s] = hh; nseen++;
            if (2 * nseen > tcap) {
                size_t nc = tcap * 4; uint64_t *ns = calloc(nc, sizeof(uint64_t));
                for (size_t a = 0; a < tcap; a++) if (seen[a]) { size_t t = seen[a] & (nc - 1); while (ns[t]) t = (t + 1) & (nc - 1); ns[t] = seen[a]; }
                free(seen); seen = ns; tcap = nc;
            }
        }
    }
    if (!R->found && R->muts >= maxmut) R->reason = 3;
    free(seen);
}

static void upper_print(const Qv *q) { printf("["); int f = 1; for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) { printf("%s%lld", f ? "" : ",", (long long)q->b[i][j]); f = 0; } printf("]"); }

static void cmd_plant(i64 w, i64 cap, long long maxmut, int k, const i64 *st, int ne, const i64 *ex) {
    N = 4 + k; M = N * (N - 1) / 2;
    i64 m = 2 * w - 1, j = w;
    Qv Q; memset(&Q, 0, sizeof(Q));
#define SETB(i, jj, v) do { Q.b[i][jj] = (v); Q.b[jj][i] = -(v); } while (0)
    SETB(1, 0, 2); SETB(3, 2, 2);
    SETB(0, 2, m - j); SETB(1, 2, -(m + 1 - j));
    SETB(0, 3, j); SETB(1, 3, -(j - 1));
    for (int t = 0; t < k; t++) { int x = 4 + t; SETB(0, x, st[4 * t]); SETB(1, x, st[4 * t + 1]); SETB(x, 2, st[4 * t + 2]); SETB(x, 3, st[4 * t + 3]); }
    for (int t = 0; t < ne; t++) SETB((int)ex[3 * t], (int)ex[3 * t + 1], ex[3 * t + 2]);   /* entries between further vertices ("dense") */
#undef SETB
    i64 kq[MAXM], knq[MAXM], ky[MAXM];
    canon(&Q, kq);
    Qv nQ; neg(&Q, &nQ); canon(&nQ, knq);
    WalkRes F, B;
    walk_plant(&Q, w, cap, maxmut, kq, &F);
    walk_plant(&nQ, w, cap, maxmut, knq, &B);   /* -Y is low and not iso to Q iff Y not iso to -Q... map back below */
    int dir = 0; WalkRes *R = NULL;
    if (F.found && (!B.found || F.len <= B.len)) { R = &F; dir = 1; }
    else if (B.found) { R = &B; dir = -1; }
    printf("{\"cmd\":\"plant\",\"Q\":"); upper_print(&Q);
    printf(",\"fwd\":[%d,%lld,%lld,%d,%lld],\"bwd\":[%d,%lld,%lld,%d,%lld]", F.found, F.len, (long long)F.h, F.reason, F.muts, B.found, B.len, (long long)B.h, B.reason, B.muts);
    if (R) {
        Qv Y = R->Y; if (dir < 0) { Qv t; neg(&R->Y, &t); Y = t; }
        canon(&Y, ky);
        printf(",\"planted\":1,\"dir\":%d,\"len\":%lld,\"h\":%lld,\"Y_is_neg\":%d,\"Y\":", dir, R->len, (long long)R->h, memcmp(ky, knq, sizeof(i64) * M) == 0);
        upper_print(&Y);
        printf(",\"Ykey\":"); print_key(ky);
    } else printf(",\"planted\":0");
    printf("}\n"); fflush(stdout);
}

int main(int argc, char **argv) {
    char cmd[64];
    if (argc > 1) rng_state ^= (uint64_t)atoll(argv[1]) * 0x9E3779B97F4A7C15ULL;
    while (scanf("%63s", cmd) == 1) {
        if (!strcmp(cmd, "replayfile")) { char path[4096]; if (scanf("%4095s", path) != 1) break; cmd_replayfile(path); continue; }
        int n; if (scanf("%d", &n) != 1) break;
        N = n; M = n * (n - 1) / 2;
        i64 e[MAXM], e2[MAXM];
        if (!strcmp(cmd, "minimax")) {
            long long w, cap, budget; int tie, prune;
            if (scanf("%lld %lld %d %d %lld", &w, &cap, &tie, &prune, &budget) != 5) break;
            for (int a = 0; a < M; a++) if (scanf("%lld", &e[a]) != 1) return 1;
            cmd_minimax(w, cap, tie, prune, (long)budget, e);
        } else if (!strcmp(cmd, "comp")) {
            long long bound, budget, w; int prune;
            if (scanf("%lld %lld %d %lld", &bound, &budget, &prune, &w) != 4) break;
            for (int a = 0; a < M; a++) if (scanf("%lld", &e[a]) != 1) return 1;
            cmd_comp(bound, (long)budget, prune, w, e);
        } else if (!strcmp(cmd, "bibfs")) {
            long long bound, budget, pw;
            if (scanf("%lld %lld %lld", &bound, &budget, &pw) != 3) break;
            for (int a = 0; a < M; a++) if (scanf("%lld", &e[a]) != 1) return 1;
            for (int a = 0; a < M; a++) if (scanf("%lld", &e2[a]) != 1) return 1;
            cmd_bibfs(bound, (long)budget, pw, e, e2);
        } else if (!strcmp(cmd, "plant")) {
            long long w, cap, maxmut; int k;
            if (scanf("%lld %lld %lld %d", &w, &cap, &maxmut, &k) != 4) break;
            i64 st[4 * 4], ex[3 * 16]; int ne;
            for (int a = 0; a < 4 * k; a++) if (scanf("%lld", &st[a]) != 1) return 1;
            if (scanf("%d", &ne) != 1) return 1;
            for (int a = 0; a < 3 * ne; a++) if (scanf("%lld", &ex[a]) != 1) return 1;
            cmd_plant(w, cap, maxmut, k, st, ne, ex);
        } else if (!strcmp(cmd, "canon")) {
            for (int a = 0; a < M; a++) if (scanf("%lld", &e[a]) != 1) return 1;
            Qv q; from_upper(e, &q); i64 k[MAXM]; canon(&q, k); print_key(k); printf("\n");
        } else if (!strcmp(cmd, "isfork")) {
            for (int a = 0; a < M; a++) if (scanf("%lld", &e[a]) != 1) return 1;
            Qv q; from_upper(e, &q); printf("%d\n", fork_point(&q));
        } else { fprintf(stderr, "unknown command %s\n", cmd); return 1; }
    }
    return 0;
}
