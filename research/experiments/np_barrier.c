/*
 * np_barrier.c -- bottleneck search in the mutation graph of a quiver, up to relabelling (note 13).
 *
 * For a quiver Q with maximal entry m, and a level w >= m, this finds the escape level
 *
 *     iso(Q, w) = the least L such that the component of Q in X_L contains a quiver of maximal
 *                 entry <= w that is not in the component of Q in X_w,
 *
 * where X_L is the mutation graph restricted to quivers of maximal entry <= L.  If iso is found,
 * the class of Q has two quivers of maximal entry <= w that every mutation path joins only through
 * a quiver of maximal entry >= iso, so f(Q, w) >= iso(Q, w).  The search is a minimax Dijkstra
 * (lowest bottleneck first) on canonical forms, with exact integer arithmetic: products are formed
 * in 64 bits and every quiver with an entry above the cap (< 2^31) is discarded.
 *
 * With prune = 1 a fork (Warkentin, thesis Def. 2.1) other than the start is recorded but not
 * expanded.  By Warkentin's Lemma 2.5 a mutation of a fork away from its point of return is a fork
 * whose point of return is the mutated vertex, so a walk that enters a fork can leave the forks only
 * by backtracking, and no entry decreases on the way in.  Minimax paths between non-forks therefore
 * avoid forks, and a fork of level <= w is reached through its ancestors of level <= w.
 *
 * Input, one task per line:   n w cap budget prune b01 b02 ... b(n-2)(n-1)   (upper triangle by rows)
 * Output, one JSON line per task.
 *
 * Build:  gcc -O2 -o ~/.cache/qmb-np/np_barrier np_barrier.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 7
#define MAXM 21

static int n, m;
static int nperm;
static int (*perm)[MAXN];
static int pairidx[MAXN][MAXN];

static void gen_perms(void) {
    int p[MAXN], c[MAXN], i, cnt = 1;
    for (i = 2; i <= n; i++) cnt *= i;
    free(perm);
    perm = malloc(sizeof(int[MAXN]) * cnt);
    nperm = 0;
    for (i = 0; i < n; i++) { p[i] = i; c[i] = 0; }
    memcpy(perm[nperm++], p, sizeof(int) * MAXN);
    i = 0;
    while (i < n) {                       /* Heap's algorithm */
        if (c[i] < i) {
            int a = (i % 2 == 0) ? 0 : c[i], t = p[a];
            p[a] = p[i]; p[i] = t;
            memcpy(perm[nperm++], p, sizeof(int) * MAXN);
            c[i]++; i = 0;
        } else { c[i] = 0; i++; }
    }
    int k = 0;
    for (i = 0; i < n; i++) for (int j = i + 1; j < n; j++) { pairidx[i][j] = k; pairidx[j][i] = k; k++; }
}

/* canonical form: the lexicographically least upper triangle over all relabellings */
static void canon(const int64_t B[MAXN][MAXN], int32_t *out) {
    int32_t best[MAXM], cur[MAXM];
    int first = 1;
    for (int q = 0; q < nperm; q++) {
        const int *p = perm[q];
        int k = 0, state = first ? -1 : 0;  /* -1: cur < best already; 0: equal so far */
        int stop = 0;
        for (int i = 0; i < n && !stop; i++)
            for (int j = i + 1; j < n; j++) {
                int32_t v = (int32_t)B[p[i]][p[j]];
                if (state == 0) {
                    if (v > best[k]) { stop = 1; break; }
                    if (v < best[k]) state = -1;
                }
                cur[k++] = v;
            }
        if (!stop && state == -1) { memcpy(best, cur, sizeof(int32_t) * m); first = 0; }
    }
    memcpy(out, best, sizeof(int32_t) * m);
}

static void unpack(const int32_t *key, int64_t B[MAXN][MAXN]) {
    int k = 0;
    for (int i = 0; i < n; i++) {
        B[i][i] = 0;
        for (int j = i + 1; j < n; j++) { B[i][j] = key[k]; B[j][i] = -key[k]; k++; }
    }
}

/* mu_v(B) into N; returns the maximal entry, or -1 if some entry exceeds cap */
static int64_t mutate(const int64_t B[MAXN][MAXN], int v, int64_t N[MAXN][MAXN], int64_t cap) {
    int64_t mx = 0;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            int64_t x;
            if (i == v || j == v) x = -B[i][j];
            else {
                int64_t a = B[i][v], b = B[v][j];
                x = B[i][j];
                if (a > 0 && b > 0) x += a * b;
                else if (a < 0 && b < 0) x -= a * b;
            }
            N[i][j] = x;
            int64_t ax = x < 0 ? -x : x;
            if (ax > mx) mx = ax;
        }
    return mx > cap ? -1 : mx;
}

static int acyclic(const int64_t B[MAXN][MAXN], unsigned mask) {
    unsigned rem = mask;
    while (rem) {
        unsigned src = 0;
        for (int i = 0; i < n; i++) if (rem >> i & 1) {
            int has_in = 0;
            for (int j = 0; j < n; j++) if ((rem >> j & 1) && B[j][i] > 0) { has_in = 1; break; }
            if (!has_in) src |= 1u << i;
        }
        if (!src) return 0;
        rem &= ~src;
    }
    return 1;
}

/* point of return if B is a fork, else -1 */
static int fork_return(const int64_t B[MAXN][MAXN]) {
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
        int64_t a = B[i][j] < 0 ? -B[i][j] : B[i][j];
        if (a < 2) return -1;
    }
    if (acyclic(B, (1u << n) - 1)) return -1;
    for (int r = 0; r < n; r++) {
        unsigned in = 0, out = 0;
        int ok = 1;
        for (int i = 0; i < n; i++) { if (B[i][r] > 0) in |= 1u << i; if (B[r][i] > 0) out |= 1u << i; }
        for (int i = 0; i < n && ok; i++) if (in >> i & 1)
            for (int j = 0; j < n; j++) if (out >> j & 1)
                if (!(B[j][i] > B[i][r] && B[j][i] > B[r][j])) { ok = 0; break; }
        if (ok && acyclic(B, in) && acyclic(B, out)) return r;
    }
    return -1;
}

/* ---- node store, hash table, heap ---- */
static int32_t *keys;       /* budget * m */
static int32_t *level, *best, *parent;
static uint8_t *done, *pmove;
static int64_t nnodes, cap_nodes;
static int32_t *table; static int64_t tsize, tmask;
typedef struct { int32_t h; int32_t lv; int32_t id; } hent;
static hent *heap; static int64_t hn, hcap;

static uint64_t hashkey(const int32_t *k) {
    uint64_t h = 1469598103934665603ULL;
    for (int i = 0; i < m; i++) { h ^= (uint32_t)k[i]; h *= 1099511628211ULL; h ^= h >> 29; }
    return h;
}

static int64_t lookup_insert(const int32_t *k, int *isnew) {
    uint64_t pos = hashkey(k) & tmask;
    for (;;) {
        int32_t id = table[pos];
        if (id < 0) {
            if (nnodes >= cap_nodes) { *isnew = -1; return -1; }
            memcpy(keys + nnodes * m, k, sizeof(int32_t) * m);
            table[pos] = (int32_t)nnodes; *isnew = 1;
            return nnodes++;
        }
        if (memcmp(keys + (int64_t)id * m, k, sizeof(int32_t) * m) == 0) { *isnew = 0; return id; }
        pos = (pos + 1) & tmask;
    }
}

static int hless(hent a, hent b) { return a.h < b.h || (a.h == b.h && (a.lv < b.lv || (a.lv == b.lv && a.id < b.id))); }
static void hpush(hent e) {
    if (hn >= hcap) { hcap = hcap ? hcap * 2 : 1024; heap = realloc(heap, sizeof(hent) * hcap); }
    int64_t i = hn++;
    while (i > 0) { int64_t p = (i - 1) / 2; if (!hless(e, heap[p])) break; heap[i] = heap[p]; i = p; }
    heap[i] = e;
}
static hent hpop(void) {
    hent top = heap[0], e = heap[--hn];
    int64_t i = 0;
    for (;;) {
        int64_t c = 2 * i + 1;
        if (c >= hn) break;
        if (c + 1 < hn && hless(heap[c + 1], heap[c])) c++;
        if (!hless(heap[c], e)) break;
        heap[i] = heap[c]; i = c;
    }
    heap[i] = e;
    return top;
}

static void print_key(const int32_t *k) {
    printf("[");
    for (int i = 0; i < m; i++) printf(i ? ",%d" : "%d", k[i]);
    printf("]");
}

int main(int argc, char **argv) {
    int verbose_path = argc > 1 && strcmp(argv[1], "--path") == 0;
    int dump = argc > 1 && strcmp(argv[1], "--dump") == 0;   /* list every node popped: key, level, bottleneck */
    char *line = NULL; size_t ll = 0;
    int cur_n = -1; int64_t cur_budget = -1;
    while (getline(&line, &ll, stdin) > 0) {
        char *s = line; long long w, cap, budget; int prune;
        int nn = (int)strtol(s, &s, 10);
        if (nn < 2 || nn > MAXN) continue;
        w = strtoll(s, &s, 10); cap = strtoll(s, &s, 10); budget = strtoll(s, &s, 10); prune = (int)strtol(s, &s, 10);
        if (cap > 2147483647LL) cap = 2147483647LL;
        if (nn != cur_n) { n = nn; m = n * (n - 1) / 2; gen_perms(); cur_n = nn; cur_budget = -1; }
        if (budget != cur_budget) {
            free(keys); free(level); free(best); free(parent); free(done); free(pmove); free(table);
            cap_nodes = budget + 64;
            keys = malloc(sizeof(int32_t) * cap_nodes * m);
            level = malloc(sizeof(int32_t) * cap_nodes); best = malloc(sizeof(int32_t) * cap_nodes);
            parent = malloc(sizeof(int32_t) * cap_nodes); done = malloc(cap_nodes); pmove = malloc(cap_nodes);
            tsize = 1024; while (tsize < 2 * cap_nodes) tsize *= 2; tmask = tsize - 1;
            table = malloc(sizeof(int32_t) * tsize);
            cur_budget = budget;
        }
        memset(table, 0xff, sizeof(int32_t) * tsize);
        nnodes = 0; hn = 0;
        int64_t B[MAXN][MAXN], N[MAXN][MAXN];
        int32_t k0[MAXM], key[MAXM];
        for (int i = 0; i < m; i++) k0[i] = (int32_t)strtol(s, &s, 10);
        unpack(k0, B);
        int64_t m0 = 0;
        for (int i = 0; i < m; i++) { int64_t a = k0[i] < 0 ? -(int64_t)k0[i] : k0[i]; if (a > m0) m0 = a; }
        if (w < m0) w = m0;
        canon(B, key);
        int isnew; int64_t sid = lookup_insert(key, &isnew);
        level[sid] = (int32_t)m0; best[sid] = (int32_t)m0; parent[sid] = -1; done[sid] = 0; pmove[sid] = 255;
        hpush((hent){(int32_t)m0, (int32_t)m0, (int32_t)sid});
        int64_t popped = 0, plateau = 0, forks = 0, capped = 0, lowest = m0, maxh = m0;
        int64_t found = -1; int over = 0;
        if (dump) printf("{\"dump\":[");
        while (hn > 0) {
            hent e = hpop();
            if (done[e.id] || e.h != best[e.id]) continue;
            done[e.id] = 1; popped++;
            if (e.h > maxh) maxh = e.h;
            if (level[e.id] < lowest) lowest = level[e.id];
            if (dump) { printf(popped > 1 ? ",[" : "["); print_key(keys + (int64_t)e.id * m); printf(",%d,%d]", level[e.id], e.h); }
            if (e.h <= w) plateau++;
            else if (level[e.id] <= w && !dump) { found = e.id; break; }
            if (popped > budget) { over = 1; break; }
            unpack(keys + (int64_t)e.id * m, B);
            if (prune && e.id != sid && fork_return(B) >= 0) { forks++; continue; }
            for (int v = 0; v < n; v++) {
                int64_t mx = mutate(B, v, N, cap);
                if (mx < 0) { capped++; continue; }
                canon(N, key);
                int64_t id = lookup_insert(key, &isnew);
                if (isnew < 0) { over = 1; break; }
                int32_t h = e.h > mx ? e.h : (int32_t)mx;
                if (isnew) { level[id] = (int32_t)mx; best[id] = h; parent[id] = e.id; done[id] = 0; pmove[id] = (uint8_t)v; hpush((hent){h, (int32_t)mx, (int32_t)id}); }
                else if (!done[id] && h < best[id]) { best[id] = h; parent[id] = e.id; pmove[id] = (uint8_t)v; hpush((hent){h, (int32_t)mx, (int32_t)id}); }
            }
            if (over) break;
        }
        if (dump) printf("],");
        else printf("{");
        printf("\"n\":%d,\"w\":%lld,\"cap\":%lld,\"start\":", n, w, cap); print_key(k0);
        printf(",\"popped\":%lld,\"nodes\":%lld,\"plateau\":%lld,\"forks\":%lld,\"capped\":%lld,\"lowest\":%lld,\"maxh\":%lld",
               (long long)popped, (long long)nnodes, (long long)plateau, (long long)forks, (long long)capped, (long long)lowest, (long long)maxh);
        if (found >= 0) {
            printf(",\"status\":\"found\",\"iso\":%d,\"target\":", best[found]); print_key(keys + found * m);
            int64_t len = 0; for (int64_t x = found; parent[x] >= 0; x = parent[x]) len++;
            printf(",\"path_len\":%lld", (long long)len);
            if (verbose_path) {
                printf(",\"path\":[");
                int64_t *st = malloc(sizeof(int64_t) * (len + 1)); int64_t t = 0;
                for (int64_t x = found; x >= 0; x = parent[x]) st[t++] = x;
                for (int64_t i = t - 1; i >= 0; i--) { print_key(keys + st[i] * m); if (i) printf(","); }
                printf("],\"levels\":[");
                for (int64_t i = t - 1; i >= 0; i--) printf(i ? "%d," : "%d", level[st[i]]);
                printf("]");
                free(st);
            }
        } else if (over) printf(",\"status\":\"budget\"");
        else printf(",\"status\":\"%s\"", capped ? "cap" : "closed");
        printf("}\n");
        fflush(stdout);
    }
    return 0;
}
