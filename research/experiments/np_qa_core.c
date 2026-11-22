/*
 * np_qa_core.c -- the core of a 5-vertex quiver below a height H, grown from a list of labelled seeds.
 *
 * The core is the set of quivers, up to relabelling, that the seeds reach through quivers of height < H without
 * entering a fork (Warkentin, thesis Def. 2.1).  A fork is recorded as an exit and not expanded.  The search is
 * breadth-first from all seeds at once, so every stored member carries the seed it was reached from (its root), the
 * mutation that led to it, and its matrix in the labels of that seed.  For every stored member and every vertex the
 * exit is recorded: another member (with its id), height >= H, or a fork.
 *
 * Two modes (argv[2]):
 *   plain   every member is stored.
 *   chain   a member is stored only if it is a seed, has height <= w, or does not have exactly two exits that are
 *           members.  A member with exactly two such exits is passed through: the search walks from one stored
 *           member along such members to the next stored one and only counts them.  Nothing is lost: a member that
 *           is passed through has no neighbour in the core besides the two on its chain.  Every chain is walked
 *           once from each end, so the number of members passed through is half the sum of the chain lengths.
 *   plain-nofork, chain-nofork   the same without the fork test: every quiver of height < H is a member and is
 *           expanded (the search of Theorem 18.5, which does not use Lemma 15.5).
 *
 * Input (stdin):  n H w nseeds budget
 *                 then nseeds lines, each the upper triangle b01 b02 ... of a seed.
 * Output (file argv[1], binary, little endian; "-" writes no file):
 *     int64 count; then per stored member
 *     int32 lab[m]      upper triangle in the labels of its root, m = n(n-1)/2
 *     int32 parent      -1 for a seed
 *     int32 root        index of the seed in the input
 *     int32 depth       number of mutations from the root along the way it was found
 *     int32 move        the mutation that led from the parent, -1 for a seed
 *     int32 second      chain mode: the second mutation of the chain from the parent, -1 if there is none
 *     int32 chain       chain mode: the number of members passed through on the way from the parent;
 *                       negative if the mutations of the chain do not alternate between two vertices
 *     int32 code[n]     exit at vertex v: 0 member, 1 height >= H, 2 fork higher than w, 3 fork of height <= w
 *     int32 target[n]   member id for code 0, else the height of the mutated quiver (capped at 2^31 - 1)
 *     int32 clen[n]     chain mode: members passed through between this member and target[v]
 * A summary line is printed on stdout.
 *
 * Build:  gcc -O2 -o ~/.cache/qmb-np/np_qa_core np_qa_core.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 6
#define MAXM 15

static int n, m;
static int nperm;
static int (*perm)[MAXN];
static int64_t H, W;
static int use_forks = 1;

static void gen_perms(void) {
    int p[MAXN], c[MAXN], i, cnt = 1;
    for (i = 2; i <= n; i++) cnt *= i;
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
}

/* canonical form: the lexicographically least upper triangle over all relabellings */
static void canon(const int64_t B[MAXN][MAXN], int32_t *out) {
    int32_t best[MAXM], cur[MAXM];
    int first = 1;
    for (int q = 0; q < nperm; q++) {
        const int *p = perm[q];
        int k = 0, state = first ? -1 : 0;
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

static void pack(const int64_t B[MAXN][MAXN], int32_t *key) {
    int k = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) key[k++] = (int32_t)B[i][j];
}

static int64_t height(const int64_t B[MAXN][MAXN]) {
    int64_t mx = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) { int64_t a = B[i][j] < 0 ? -B[i][j] : B[i][j]; if (a > mx) mx = a; }
    return mx;
}

/* mu_v(B) into N; returns the maximal entry (the entries of B are below 2^31, so nothing overflows) */
static int64_t mutate(const int64_t B[MAXN][MAXN], int v, int64_t N[MAXN][MAXN]) {
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
    return mx;
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

/* mu_v(B) into N.  0: a quiver of height < H that is not a fork; 1: height >= H; 2: fork higher than w; 3: fork of height <= w */
static int classify(const int64_t B[MAXN][MAXN], int v, int64_t N[MAXN][MAXN], int64_t *mx) {
    *mx = mutate(B, v, N);
    if (*mx >= H) return 1;
    if (use_forks && fork_return(N) >= 0) return *mx <= W ? 3 : 2;
    return 0;
}

static int32_t *keys, *labm, *parent, *root, *depth, *move, *second, *chain, *code, *target, *clen;
static int64_t nnodes, cap_nodes;
static int32_t *table; static int64_t tsize, tmask;
static uint64_t *seedinv; static int64_t ssize, smask;

static uint64_t hashkey(const int32_t *k) {
    uint64_t h = 1469598103934665603ULL;
    for (int i = 0; i < m; i++) { h ^= (uint32_t)k[i]; h *= 1099511628211ULL; h ^= h >> 29; }
    return h;
}

static int64_t lookup(const int32_t *k, int insert, int *isnew) {
    uint64_t pos = hashkey(k) & tmask;
    for (;;) {
        int32_t id = table[pos];
        if (id < 0) {
            if (!insert) { *isnew = 0; return -1; }
            if (nnodes >= cap_nodes) { *isnew = -1; return -1; }
            memcpy(keys + nnodes * m, k, sizeof(int32_t) * m);
            table[pos] = (int32_t)nnodes; *isnew = 1;
            return nnodes++;
        }
        if (memcmp(keys + (int64_t)id * m, k, sizeof(int32_t) * m) == 0) { *isnew = 0; return id; }
        pos = (pos + 1) & tmask;
    }
}

/* an invariant of the relabelling class (never 0), to recognise the seeds on a chain cheaply */
static uint64_t invariant(const int64_t B[MAXN][MAXN]) {
    uint64_t s1 = 0, s2 = 0, s3 = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
        uint64_t a = (uint64_t)(B[i][j] < 0 ? -B[i][j] : B[i][j]);
        s1 += a; s2 += a * a; s3 += a * a * a;
    }
    uint64_t h = s1 * 0x9E3779B97F4A7C15ULL ^ s2 * 0xC2B2AE3D27D4EB4FULL ^ s3 * 0x165667B19E3779F9ULL;
    return h ? h : 1;
}
static void inv_add(uint64_t h) {
    uint64_t pos = h & smask;
    while (seedinv[pos] && seedinv[pos] != h) pos = (pos + 1) & smask;
    seedinv[pos] = h;
}
static int inv_has(uint64_t h) {
    uint64_t pos = h & smask;
    while (seedinv[pos]) { if (seedinv[pos] == h) return 1; pos = (pos + 1) & smask; }
    return 0;
}

int main(int argc, char **argv) {
    long long nseeds, budget, hh, ww;
    if (argc < 3 || scanf("%d %lld %lld %lld %lld", &n, &hh, &ww, &nseeds, &budget) != 5 || n < 2 || n > MAXN) {
        fprintf(stderr, "usage: np_qa_core out.bin plain|chain|plain-nofork|chain-nofork < input\n");
        return 2;
    }
    H = hh; W = ww;
    int chain_mode = strncmp(argv[2], "chain", 5) == 0;
    use_forks = strstr(argv[2], "nofork") == NULL;
    m = n * (n - 1) / 2;
    gen_perms();
    cap_nodes = budget;
    keys = malloc(sizeof(int32_t) * cap_nodes * m); labm = malloc(sizeof(int32_t) * cap_nodes * m);
    parent = malloc(sizeof(int32_t) * cap_nodes); root = malloc(sizeof(int32_t) * cap_nodes);
    depth = malloc(sizeof(int32_t) * cap_nodes); move = malloc(sizeof(int32_t) * cap_nodes);
    second = malloc(sizeof(int32_t) * cap_nodes); chain = malloc(sizeof(int32_t) * cap_nodes);
    code = malloc(sizeof(int32_t) * cap_nodes * n); target = malloc(sizeof(int32_t) * cap_nodes * n);
    clen = malloc(sizeof(int32_t) * cap_nodes * n);
    tsize = 1024; while (tsize < 2 * cap_nodes) tsize *= 2; tmask = tsize - 1;
    table = malloc(sizeof(int32_t) * tsize);
    ssize = 1024; while (ssize < 4 * nseeds) ssize *= 2; smask = ssize - 1;
    seedinv = calloc(ssize, sizeof(uint64_t));
    if (!keys || !labm || !parent || !root || !depth || !move || !second || !chain || !code || !target || !clen || !table || !seedinv) {
        fprintf(stderr, "out of memory\n"); return 2;
    }
    memset(table, 0xff, sizeof(int32_t) * tsize);
    int64_t B[MAXN][MAXN], N[MAXN][MAXN], M[MAXN][MAXN], K[MAXN][MAXN];
    int32_t key[MAXM], lab[MAXM];
    long long dup_seeds = 0, bad_seeds = 0;
    for (long long s = 0; s < nseeds; s++) {
        for (int i = 0; i < m; i++) { long long x; if (scanf("%lld", &x) != 1) return 2; lab[i] = (int32_t)x; }
        unpack(lab, B);
        if (height(B) >= H) { bad_seeds++; continue; }
        canon(B, key);
        int isnew; int64_t id = lookup(key, 1, &isnew);
        if (isnew < 0) { fprintf(stderr, "budget\n"); return 3; }
        if (!isnew) { dup_seeds++; continue; }
        memcpy(labm + id * m, lab, sizeof(int32_t) * m);
        parent[id] = -1; root[id] = (int32_t)s; depth[id] = 0; move[id] = -1; second[id] = -1; chain[id] = 0;
        inv_add(invariant(B));
    }
    long long seeds_in = nnodes, n_high = 0, n_fork = 0, n_lowfork = 0, n_member = 0, low = 0, maxdepth = 0;
    long long walked_total = 0, longest_chain = 0, impure = 0;
    int over = 0;
    for (int64_t u = 0; u < nnodes && !over; u++) {
        unpack(labm + u * m, B);
        if (height(B) <= W) low++;
        if (depth[u] > maxdepth) maxdepth = depth[u];
        for (int v = 0; v < n; v++) {
            int64_t mx;
            int cls = classify(B, v, N, &mx);
            clen[u * n + v] = 0;
            if (cls) {
                code[u * n + v] = cls; target[u * n + v] = mx > 2147483647LL ? 2147483647 : (int32_t)mx;
                if (cls == 1) n_high++; else { n_fork++; n_lowfork += cls == 3; }
                continue;
            }
            int from = v, sec = -1, pure = 1;
            long long walked = 0;
            int64_t found = -1;
            while (chain_mode) {                    /* N is a member; pass through it if it has exactly one further exit */
                if (height(N) <= W) break;
                if (inv_has(invariant(N))) {        /* it may be a seed: look it up */
                    int isnew; canon(N, key);
                    found = lookup(key, 0, &isnew);
                    if (found >= 0) break;
                }
                int nex = 0, e1 = -1;
                for (int v2 = 0; v2 < n && nex < 2; v2++) {
                    if (v2 == from) continue;
                    int64_t mx2;
                    int c2 = classify(N, v2, M, &mx2);
                    if (c2 == 0) { nex++; e1 = v2; memcpy(K, M, sizeof(K)); }
                    else if (c2 == 3) { nex = 2; }  /* a fork of height <= w next to it: store the member, the exit is recorded there */
                }
                if (nex != 1) break;
                walked++;
                if (walked == 1) sec = e1;
                else if (e1 != ((walked % 2 == 1) ? sec : v)) pure = 0;
                from = e1;
                memcpy(N, K, sizeof(N));
            }
            int isnew = 0; int64_t id = found;
            if (id < 0) { canon(N, key); id = lookup(key, 1, &isnew); }
            if (isnew < 0) { over = 1; break; }
            if (isnew) {
                pack(N, labm + id * m);
                parent[id] = (int32_t)u; root[id] = root[u]; depth[id] = depth[u] + 1 + (int32_t)walked; move[id] = v;
                second[id] = sec; chain[id] = (int32_t)(pure ? walked : -walked);
            }
            code[u * n + v] = 0; target[u * n + v] = (int32_t)id; clen[u * n + v] = (int32_t)walked; n_member++;
            walked_total += walked; if (walked > longest_chain) longest_chain = walked; if (!pure) impure++;
        }
    }
    if (strcmp(argv[1], "-") != 0) {
        FILE *f = fopen(argv[1], "wb");
        if (!f) { fprintf(stderr, "cannot write %s\n", argv[1]); return 2; }
        int64_t cnt = over ? -1 : nnodes;
        fwrite(&cnt, sizeof(int64_t), 1, f);
        for (int64_t u = 0; u < nnodes && !over; u++) {
            fwrite(labm + u * m, sizeof(int32_t), m, f);
            fwrite(parent + u, sizeof(int32_t), 1, f);
            fwrite(root + u, sizeof(int32_t), 1, f);
            fwrite(depth + u, sizeof(int32_t), 1, f);
            fwrite(move + u, sizeof(int32_t), 1, f);
            fwrite(second + u, sizeof(int32_t), 1, f);
            fwrite(chain + u, sizeof(int32_t), 1, f);
            fwrite(code + u * n, sizeof(int32_t), n, f);
            fwrite(target + u * n, sizeof(int32_t), n, f);
            fwrite(clen + u * n, sizeof(int32_t), n, f);
        }
        fclose(f);
    }
    printf("{\"mode\":\"%s\",\"status\":\"%s\",\"H\":%lld,\"w\":%lld,\"stored\":%lld,\"passed_through\":%lld,\"members\":%lld,"
           "\"chain_sum_is_even\":%s,\"longest_chain\":%lld,\"chains_not_alternating\":%lld,\"seeds\":%lld,\"duplicate_seeds\":%lld,"
           "\"seeds_at_or_above_H\":%lld,\"exits_member\":%lld,\"exits_high\":%lld,\"exits_fork\":%lld,\"forks_of_height_le_w\":%lld,"
           "\"members_of_height_le_w\":%lld,\"max_depth\":%lld}\n",
           argv[2], over ? "budget" : "closed", (long long)H, (long long)W, (long long)nnodes, walked_total / 2,
           (long long)nnodes + walked_total / 2, walked_total % 2 ? "false" : "true", longest_chain, impure, seeds_in, dup_seeds, bad_seeds,
           n_member, n_high, n_fork, n_lowfork, low, maxdepth);
    return over ? 3 : 0;
}
