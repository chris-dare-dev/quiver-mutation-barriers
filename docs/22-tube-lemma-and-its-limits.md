# 22. A lemma for the tubes of note 14, and where a description by tubes fails

*Run on 2026-11-12. [Note 14](14-opposite-quivers-forks-and-cores.md) §8 described the core of 225,208 census classes without a finite core by ad hoc tube certificates and listed "a general lemma for tubes" as open. [Note 19](19-checks-of-notes-13-to-16.md) §6.4 checked those certificates and corrected the use of Theorem 14.1 item 4. The aim here was to find and prove such a lemma, strong enough to compute a finite description of the core of every 4-vertex class and so to decide mutation equivalence on 4 vertices; to certify or settle the 6,990 classes and 2,139 mirror pairs note 14 left open; and to say what this gives for FWZ Problem 2.6.14 at n = 4. Code: [experiments/n4_tube_lemma.py](../experiments/n4_tube_lemma.py) (new; it imports `n4_opposite.py` and `n4_opposite_tubes.py` of note 14). Results: the `n4_tube_*` files in `experiments/`. Quivers are 6-tuples (b01, b02, b03, b12, b13, b23), up to relabelling unless stated otherwise. Labels: **[P]** proven in a cited source; **[I]** my own derivation or measurement; **[H]** heuristic.*

> **Correction (note 23):** Checked in [note 23](23-checks-of-notes-20-to-22.md) with new code. No theorem was found false. Lemmas 22.1, 22.1′, 22.2, 22.3 and 22.6, Proposition 22.4 and Theorem 22.7 were re-derived by hand and tested, and the cuts of V′ for class 707 reproduce exactly. Theorem 22.5 needs two hypotheses, which hold for every tube of the census (note after its proof). The bottoms of all 2,206 new certificates were confirmed by independent exhaustive cuts, an independent engine certified 149 of a sample of 150 classes with the same bottoms, and every count of §6 and §7 recomputes. Corrected below: the signed form of the Markov constant (§2), the rows "j = 1" of the table of §3, and the number of tubes, which counts single families that lie on no cycle (§1 item 1, §3).

---

## 1. Outcome

1. **The tube shapes are classified [I] (§3).** All 6,130,593 families of note 14's 225,208 certificates have one growing vertex and a constant triangle T. T is one of four types: (0, 0, a), (0, 1, a)/(1, a, a), (1, 1, a)/(1, a, a + 1), or the oriented corridor (2, m, m). τ is always a Chebyshev value λʲ + λ⁻ʲ, where λ + 1/λ = C − 2 and C is the Markov constant of T. There are 650,334 tubes: rank-2 corridors (note 15), pair walks on (0, 0, a), and Coxeter-type walks through all three vertices.

   > **Correction (note 23):** 650,334 counts every strongly connected set of families, including single families that lie on no cycle. Those are not tubes. From a sample of 5,353 certificates, there are about 645,600 tubes (note in §3).
2. **The lemma is proved [I] (§4).** It has four parts.
   - At a *dominant* vertex g, the step at g is a strict up-exit (Lemma 22.1). Dominant means the column has both signs, every entry has absolute value ≥ 2, and no arrow of the opposite triangle outweighs both of its column entries. This replaces note 14's monotonicity argument for the growing vertex.
   - Steps inside the triangle act on the column by fixed integer matrices (Lemma 22.2).
   - The monodromy of a period fixes the Pfaffian functional, which gives note 14's recurrence. τ is set by the Markov constant C of the triangle: λ + 1/λ = C − 2 per Coxeter period (Lemma 22.3).
   - A mutation-cyclic triangle stays bounded only on the corridors (2, m, m) and on the Markov quiver (Proposition 22.4).

   **Theorem 22.5 (the tube lemma):** a sign-stable periodic walk is a family for every n, and every such family becomes certifiable once its base is shifted far enough. On τ = 2 corridors every quiver reached in finitely many steps is a polynomial in n. So every class whose V′ is a finite set plus finitely many tubes (and polynomial spikes on corridors) has a certificate, and a search finds it.

   > **Correction (note 23):** Item 1 needs a monodromy with characteristic polynomial (x − 1)(x² − τx + 1) and τ ≥ 2, and item 2 needs a power of M rather than M² when the monodromy has finite order (note after the proof in §4.5). Every tube of the census satisfies this.
3. **The lemma cannot do what was hoped [I, proved] (§5).** V′ is not always a finite set plus finitely many tubes.
   - **The Markov triangle with one pendant arrow** (census class 707, bottom 2): every step inside a Markov triangle is allowed (Lemma 22.6), and V′ contains the corridors v(z, n) = (−(z − 1)(n + 1), (z − 1)n, z) for all z ≥ 2. So V′ has at least L·ln L − 3L quivers below level L, and no finite set plus finitely many families covers it (Theorem 22.7). Measured, V′ grows like L².
   - **Side tubes** (census class 108970, measured): a pendant vertex joined by one arrow to the growing vertex of a (0, 0, 57) tube makes every member of that tube the base of another tube, whose triangle is (0, 1, a) with a an entry of the member. Their τ ≥ a² − 1 is unbounded.
   - Both start where a column entry has absolute value ≤ 1. There, by Lemma 22.1′, the step at the growing vertex is allowed.
4. **The 6,990 classes and 2,139 pairs [I] (§6).** Note 14's engine, extended by polynomial families for the spikes and a corridor search, certifies 2,206 more classes, including 2,155 of the 2,282 connected cyclic classes whose V′ grows linearly. Every crosscheck passes.
   - **Settled otherwise.** The 400 disconnected classes are settled by rank 3, which certifies their 28 open mirror pairs distinct. The 1,556 classes with an acyclic bottom quiver are mutation-acyclic.
   - **Still open:** 2,828 connected mutation-cyclic classes. They are the 456 with a Markov triangle, 2,245 with slow growth, whose failed searches show the side-tube signature (before giving up, the engine had found a tube with τ of 25 to 36 digits in all 2,245, against at most 15 digits in every certificate of note 14), and 127 others.
   - **Mirror pairs.** 900 more are certified by cores and 28 by rank 3. 1,211 stay open: 147 Markov, 1,025 slow and 39 linear.
5. **FWZ Problem 2.6.14 at n = 4 (§7).** Equivalence is decided for a pair of 4-vertex quivers in three cases:
   - one of them is mutation-acyclic (arXiv 2610.36179);
   - one is disconnected (rank 3);
   - both classes have a finite core or a (polynomial) tube certificate.

   This uses no bound on f(Q, w): Conjecture 10.1 is not needed. It is not a decision procedure, because class 707 has no certificate of this form. The route would need a 2-dimensional lemma for Markov pieces and a recursive one for side tubes. On the census, 785,198 of the 788,026 classes are covered and 2,828 are not.

---

## 2. Setting

Fix a quiver X on the vertices 0, 1, 2, 3 and one vertex g. Write T for the full subquiver on the other three vertices, the *triangle* opposite g, and v for the *column* at g: v_i = b_ig for i ≠ g. So X = (T, v). Let I = {i : v_i > 0}, the vertices with arrows into g, and O = {i : v_i < 0}.

- **Allowed steps, exits, V′ and N** are as in note 14 §3: a step X → μ_m(X) is a strict up-exit step if (μ_m X, m) is an exit (a fork or pre-fork with point of return m) and (X, m) is not; every other step is allowed; V′(x) is the set of quivers reached from x by allowed steps. By note 19 §6.4, V′(x) = N for every x of the class that lies in no far region, where N is the set of quivers of the class that lie in no far region. Its quivers of least level, the *bottom of N*, are a complete invariant of the class.
- **The Markov constant** of a 3-vertex quiver with weights x, y, z is C = x² + y² + z² − xyz if it is an oriented 3-cycle and x² + y² + z² + xyz otherwise. Written with signed entries as b₁₂² + b₂₃² + b₃₁² − b₁₂b₂₃b₃₁, it is invariant under mutation [P: BBH, Lemma 3.1, as checked in note 3]. A 3-vertex quiver is mutation-cyclic exactly when it is an oriented 3-cycle with x, y, z ≥ 2 and C ≤ 4 [P: BBH Theorem 1.2, quoted as Proposition 2.1 of arXiv 2610.36179], and a quiver with a mutation-cyclic full subquiver is mutation-cyclic [P: BMR08 Corollary 5.3, same Proposition 2.1].

> **Correction (note 23):** The weight form above is invariant, and it is what the code uses. The signed form is not: at the path (b₁₂, b₂₃, b₃₁) = (1, 1, 0) it gives 2, and after the mutation at 2, at (−1, −1, −1), it gives 4, while the weight form gives 2 both times. It fails in 24,035 of 60,000 random mutations. A correct signed form subtracts |b₁₂b₂₃b₃₁| when the three entries have one sign and adds it otherwise.
- **The Markov quiver** is the oriented 3-cycle with weights 2, 2, 2 (C = 4). Its mutation class is itself.
- **Families** are those of note 14 §8: a triple Y(0), Y(1), Y(2) continued by e(n + 3) = (τ + 1)e(n + 2) − (τ + 1)e(n + 1) + e(n), with every entry certified constant, or of fixed sign with non-decreasing absolute value. A *polynomial family* (§6.2) is a sequence of quivers Y(n), n ≥ 0, whose entries are polynomials in n, certified in the same way.

---

## 3. The tube shapes (step 1)

Note 14's `tubeshapes` looked at 600 classes and recorded the lightest triangle high up. `n4_tube_lemma.py shapes` (`n4_tube_shapes.log`) does more. It re-runs all 225,208 certificates of note 14 with full output and, for every family, records:

- the vertex g common to its non-constant entries;
- the triangle T opposite g, and whether it is constant along the family;
- the type of T and its Markov constant C(T);
- whether τ is a Chebyshev value t_k(C − 2), where t₀ = 2, t₁ = C − 2 and t_{k+1} = t₁t_k − t_{k−1};
- whether hypotheses (D1)–(D3) of Lemma 22.1 hold at every step at g.

It then forms the *tubes*: the strongly connected sets of families, linked by the steps between them.

All 225,208 certificates were certified again, with 6,130,593 families in all.

| Triangle T | Families | Classes with it | Markov constant C(T) | τ = λʲ + λ⁻ʲ, with λ + 1/λ = C − 2 |
|---|---|---|---|---|
| (1, 1, a) / (1, a, a + 1) | 3,443,791 | 103,768 | 4 to 26,025,304 (988 values) | j = 2: 3,429,093; j = 1: 14,626; j = 4: 72 |
| (0, 1, a) / (1, a, a) | 2,553,838 | 107,816 | 5 to 25,922 (134 values) | j = 2: 2,550,239; j = 1: 3,599 |
| (2, m, m), oriented | 88,765 | 28,119 | 4 | τ = 2 in all |
| (0, 0, a) | 44,199 | 10,343 | a², 4 to 3,969 (59 values) | j = 1/2: 39,282; j = 1: 4,160; j = 3/2: 679; j = 2: 56; j = 5/2: 22 |
| any other triangle | 0 | 0 | | |

> **Correction (note 23):** In the rows "j = 1" of (1, 1, a) and of (0, 0, a), most families have C = 4, that is T = (1, 1, 1) or (0, 0, 2). There λ = 1 and τ = 2 for every j, so j has no meaning. In a sample, this holds for 254 of the 318 such (1, 1, a) families and 72 of the 112 such (0, 0, a) families. They should be listed as "C = 4, τ = 2". The other entries of the table were confirmed on 181,985 families of 5,353 regenerated certificates, in proportion.

- **Every family has exactly one growing vertex, and its triangle is constant**: 6,130,593 of 6,130,593.
- **Every τ fits** the formula in the last column. For (0, 0, a), the half-integer j are the steps of the pair walk with c = a: λ^{1/2} + λ^{−1/2} = a.
- **Every step at a growing vertex** (6,130,593, one per family) is covered by Lemma 22.1. (D1)–(D3) hold at n = 0 in 6,128,907 families and from n = 1 on in the other 1,686, where the engine checks n = 0 directly.
- **The tubes.** There are 650,334 tubes, the strongly connected sets of families.

| Walk | Triangle | Tubes |
|---|---|---|
| all three vertices of T | (1, 1, a) / (1, a, a + 1) | 288,063 |
| all three vertices of T | (0, 1, a) / (1, a, a) | 255,424 |
| two vertices: the rank-2 orbit with c = 2, a corridor | (2, m, m) | 80,402 |
| the pair walk with c = a, and the sign flip at the vertex not joined to the pair | (0, 0, a) | 21,504 |
| one vertex per step, followed by a relabelling | (1, 1, a), (0, 1, a), (2, m, m) | 2,818 + 1,909 + 214 |

> **Correction (note 23):** `shapes` counts every strongly connected component of the graph of families as a tube. Its test for a single family that lies on no cycle ends in `pass` and does nothing. So 650,334 includes such single families, which are not tubes. In a sample of 5,353 certificates, 123 of the 131 components in the last row are single families on no cycle: all the (1, 1, a) and (0, 1, a) ones. Only 8 are one-family tubes with a step back to themselves, all (2, m, m). So the last row should be the 214 (2, m, m) tubes, and there are about 650,334 − 4,727 ≈ 645,600 tubes; this rests on the sample. The other rows agree with the sample to about one point ([note 23](23-checks-of-notes-20-to-22.md) §3.3).

- **Classes by the triangles of their tubes.**
  - Only (0, 1, a): 84,890. Only (1, 1, a): 83,515. Only (2, m, m): 24,171. Only (0, 0, a): 8,217.
  - Two or three types: 24,415.

**What this says [I].**

- **The triangle is fixed.** Every family has exactly one growing vertex, and its triangle is constant. So a tube is a walk of a 3-vertex quiver with a fourth vertex carried along: the frozen-row picture of Lemma 22.2.
- **Four triangle types.** Three of them, (0, 0, a), (0, 1, a)/(1, a, a) and (1, 1, a)/(1, a, a + 1), lie in mutation-acyclic 3-vertex classes with a light pair. The fourth, (2, m, m), is mutation-cyclic, as Proposition 22.4 predicts. No tube has an abundant acyclic triangle or a Markov triangle. That fits §5.1: a Markov triangle in V′ brings a 2-dimensional orbit, which no family covers.
- **τ comes from the Markov constant of the triangle.** Mostly j = 2: two Coxeter periods, because the Coxeter transformation has the eigenvalue −1 (Lemma 22.3) and note 14's recurrence needs the eigenvalue 1. For (2, m, m), C = 4 and τ = 2. Examples: T = (0, 1, 3) has C = 10 and τ = 8² − 2 = 62; T = (1, 1, 135) has C = 18,362 and τ = 18,360² − 2 = 337,089,598.
- **Lemma 22.1 covers every growing-vertex step** of note 14's certificates. Along a family T is constant and the column entries do not decrease, so (D1)–(D3) at one n give them for all later n. Note 19 §6.4's monotone-margin argument is not needed.
- **The walks.**
  - On (2, m, m) the walk is the rank-2 orbit of note 15 with c = 2: the corridors of note 11.
  - On (0, 0, a) it is the rank-2 orbit with c = a, together with the step at the vertex not joined to the pair, which only flips the sign of its entry.
  - On the two other types it uses all three vertices: a Coxeter-type walk through the acyclic members, with the oriented triangle (1, a, a) or (1, a, a + 1) between them.
  - In 4,941 tubes each step is one mutation followed by a relabelling, so a single family carries the walk.

    > **Correction (note 23):** In 214 tubes, all (2, m, m) (note after the table of tubes).

---

## 4. The lemma (step 2)

The lemma has four parts: a step at the growing vertex is a strict up-exit (Lemma 22.1); steps inside the triangle act linearly on the column (Lemma 22.2); the linear map of one period has a fixed shape, with growth set by the Markov constant (Lemma 22.3); and every such orbit is a family that a certificate can close (Theorem 22.5). Proposition 22.4 lists the walks that can carry a tube when the triangle is mutation-cyclic.

### 4.1 The step at a dominant vertex

**Lemma 22.1 [I].** Let X = (T, v) and suppose

- (D1) v has a positive and a negative entry;
- (D2) |v_i| ≥ 2 for every i ≠ g;
- (D3) |b_ij| < max(|v_i|, |v_j|) for all i, j ≠ g.

Then (X, g) is not an exit and (μ_g X, g) is one, so the step at g is a strict up-exit step. μ_g X is a fork with point of return g when the two vertices on the same side of g are joined by at least two arrows, and a pre-fork with vertices {g, k, k′} otherwise, where k, k′ are those two vertices.

*Proof.* By (D1), I and O are both non-empty, so one of them is a pair {k, k′} and the other a single vertex i₀.

- *(X, g) is not an exit.* A fork with point of return g needs b_ji > max(b_ig, b_gj) for every path i → g → j. Such a path exists by (D1), and (D3) rules the inequality out. A pre-fork with point of return g needs a full triangle {g, i, j} that is a 3-vertex fork with point of return g, so |b_ij| would be its strictly largest weight; (D3) rules that out too.
- *The entries of Y = μ_g X.* The arrows at g are reversed, so in Y the in-neighbours of g are O and the out-neighbours are I. For i ∈ I and j ∈ O there is a path i → g → j in X, and b^Y_ij = b_ij + v_i·|v_j|. By (D2), v_i·|v_j| ≥ 2·max(v_i, |v_j|), and by (D3), b_ij > −max(v_i, |v_j|). So b^Y_ij > max(v_i, |v_j|) ≥ 2: every arrow between the two sides of g points from I to O and is heavier than both arrows at g in its triangle. The entry between k and k′ does not change.
- *If |b_kk′| ≥ 2*, Y is abundant. It is not acyclic: j → g → i → j is an oriented cycle for i ∈ I, j ∈ O. For every path j → g → i in Y the arrows i → j outweigh both arrows at g, as just shown. The in- and out-neighbourhoods of g have at most two vertices each, so they are acyclic. So Y is a fork with point of return g.
- *If |b_kk′| ≤ 1*, take Y ∖ {k}, the triangle {g, i₀, k′}. It is an oriented 3-cycle with weights |v_i₀|, |v_k′| ≥ 2 and a third weight larger than both, opposite g. So it is a fork with point of return g, and so is Y ∖ {k′}. The vertex i₀ lies on the other side of g from k and k′, so its arrows to them both point from I to O: both leave i₀ or both enter it. So Y is a pre-fork with vertices {g, k, k′}. ∎

Along a family with constant T and constant signs of v whose entries at g do not decrease in absolute value, (D1)–(D3) at n = 0 imply them for every n. This is a direct proof of the "growing vertex" step of note 14 §8, which note 19 §6.4 justified through monotone margins. The census check is in §3: (D1)–(D3) hold at n = 0 at every such step of every certificate.

### 4.2 Steps inside the triangle

**Lemma 22.2 [I].** Let k ≠ g and ε = sign(v_k). Then μ_k X = (μ_k T, E v), where E = E_k^ε(T) is the integer matrix with (Ev)_k = −v_k and (Ev)_j = v_j + [ε·b_jk]₊·v_k for j ∉ {g, k}. It has determinant −1. If v_k = 0, then Ev = v.

*Proof.* The mutation rule at k gives b′_jg = b_jg + [b_jk]₊[b_kg]₊ − [−b_jk]₊[−b_kg]₊. If v_k > 0 the second product vanishes; if v_k < 0 the first does. ∎

So a walk inside T along which the mutated entries of v keep fixed signs moves v by a fixed product of such matrices. This is the frozen-row rule for a cluster algebra of rank 3 with one frozen vertex. For a pair of vertices it is Theorem 15.1 of note 15, the rank-2 orbit.

### 4.3 The monodromy of a period

Let w = (k₁, …, k_p) be a walk inside T with μ_w(T) = π(T) for a relabelling π that fixes g, and let ε ∈ {±1}^p be the signs of the mutated entries. Put M = P_π·E_p ⋯ E_1, the *monodromy*. Here P_π is the permutation matrix of π.

**Lemma 22.3 [I].**

1. **A fixed eigenvector.** Let κ(T) = (b_bc, −b_ac, b_ab) for T on the vertices a < b < c. Then Pf(X) = ±⟨v, κ(T)⟩, and κ is a left eigenvector of M with eigenvalue ±1. So the characteristic polynomial of M is (x − η)(x² − t·x + η·det M) for some η = ±1 and an integer t. Since det M = ±1, M² has eigenvalues 1, λ, 1/λ. Its entries therefore satisfy note 14's recurrence with τ = λ + 1/λ, which is a definition there.
2. **Growth from the Markov constant.** Let T be acyclic with weights p (source to middle), q (source to sink) and r (middle to sink), and let w mutate the sink three times in a row (a Coxeter period, with π = id). Suppose each mutated entry of v is positive. Then the characteristic polynomial of M is (x + 1)(x² − (C − 2)x + 1), where C = p² + q² + r² + pqr is the Markov constant of T. So two periods give τ = (C − 2)² − 2.

*Proof.*
1. Pf is invariant up to sign under mutation and relabelling (note 15 §2), and in the order (a, b, c, g) its expansion is ⟨v, κ(T)⟩ up to sign. So ⟨Mv, κ⟩ = ±⟨v, κ⟩ for all v in the cone where the signs are ε. A linear identity on an open cone holds everywhere.
2. At a sink k of T, with v_k > 0, Lemma 22.2 gives v_j ↦ v_j + |b_jk|·v_k. The product over the three sinks is the transpose of the Coxeter transformation Φ = −E⁻¹Eᵀ of the Euler form E = [[1, −p, −q], [0, 1, −r], [0, 0, 1]]. It has the same characteristic polynomial as Φ, up to x ↦ 1/x, and the Coxeter polynomial is self-reciprocal. Expanding det(xE + Eᵀ):

   (x + 1)³ − pqr·x(x + 1) − (p² + q² + r²)·x(x + 1) = (x + 1)(x² − (C − 2)x + 1). ∎

Item 2 is the case of a pure Coxeter walk. The census tubes also pass through oriented triangles, for example (1, a, a) between two copies of (0, 1, a). For them τ = t_k is measured (§3), not proved, where t₀ = 2, t₁ = C − 2 and t_{k+1} = t₁·t_k − t_{k−1}, so that t_k = λᵏ + λ⁻ᵏ. For T = (0, 0, a) the pair walk of note 15 makes half a Coxeter period per step, and τ = a with a² − 2 = C − 2.

### 4.4 Which walks keep a mutation-cyclic triangle bounded

**Proposition 22.4 [I, from P].** Let T be mutation-cyclic and take an infinite walk inside T that never mutates the same vertex twice in a row, along which T takes finitely many values up to relabelling. Then from some point on every step keeps the weights of T. Either T = (2, m, m), oriented, and the steps alternate at the two ends of the arrow of weight 2 (the corridor of notes 11 and 15, τ = 2), or T is the Markov quiver.

*Proof.* Every quiver of the class is an oriented 3-cycle with weights ≥ 2 (Proposition 2.1 of arXiv 2610.36179, applied to each member). Take weights x, y, z around the cycle. The step at the vertex opposite z changes z to xy − z.

- *After a step that raises a weight, every later step raises one.* Suppose the last step raised z to z′ = xy − z > z, so z′ > xy/2. The step opposite x gives yz′ − x > x(y²/2 − 1) ≥ x, since y ≥ 2. The step opposite y raises y the same way. The step opposite z′ undoes the last one, which the walk does not do. This is the monotonicity of note 3 Step 2 and FN Lemma 3.6.
- *So no step raises a weight*, since otherwise T would grow without bound. Steps that lower the total weight can happen only finitely often. So from some point on every step is *flat*: at the vertex opposite z with xy = 2z.
- *Two flat steps in a row.* After a flat step opposite z, the weights are again x, y, z, in reversed cyclic order. The next step is at another vertex, say opposite x. It is flat only if yz = 2x, that is y·xy/2 = 2x, so y = 2 and z = x. Then T = (2, m, m) with m = x, and the flat steps are at the two ends of the arrow of weight 2. A flat step opposite that arrow as well needs m² = 4, which is the Markov quiver. ∎

For mutation-acyclic T the bounded part of the class of T is finite, and the census shows which closed walks occur (§3). No general statement is proved here.

**Checks** (`n4_tube_lemma.py lemma`, `n4_tube_lemma.log`):
- **Lemma 22.1.** In 20,000 random quivers with (D1)–(D3), the step at g is a strict up-exit every time. With (D2) dropped, so that some |v_i| ≤ 1, it is one in none of 2,000, as Lemma 22.1′ says. With (D3) dropped it still is in 1,809 of 2,000, so (D3) is sufficient, not necessary.
- **Lemmas 22.2 and 22.3(1).** 20,000 random steps inside T agree with E·v, and |Pf| = |⟨v, κ(T)⟩| in all.
- **Lemma 22.3(2).** For 2,000 random acyclic triangles, three sink steps return T and have the characteristic polynomial (x + 1)(x² − (C − 2)x + 1).
- **Proposition 22.4.** Among the mutation-cyclic triangles with weights ≤ 200, the 199 with two or more flat steps are all (2, m, m), and only (2, 2, 2) has three.

### 4.5 The tube lemma

**Theorem 22.5 [I].** Let T, w, π, ε and M be as in §4.3. Put v_n = Mⁿ·v₀, and let u_{n,s} = E_s ⋯ E_1·v_n be the columns along the walk.

1. **An orbit is a family.** Suppose that for each s, the k_s-th entry of u_{n,s−1}, as a sequence in n, is certified of sign ε_s by note 14's criterion: value of sign ε_s at n = 0, with non-decreasing absolute value and non-decreasing absolute differences, checked at n = 0, 1, 2. The sequence satisfies the recurrence of M, by Cayley–Hamilton. Then for every n ≥ 0 the walk w from (T, v_n) passes through the quivers (T_s, u_{n,s}) and ends at π(T, v_{n+1}). So the quivers met along the walk form p families.
2. **Every orbit is eventually certifiable.** Every integer linear form ℓ(v_n) + c is either constant in n or, from some n₁ on, of constant sign with non-decreasing absolute value and non-decreasing absolute differences. So every comparison made by the closure check of note 14 along such a family is decided for all n ≥ n₁, and the family started at n₁ passes every check that concerns it alone.
3. **Corridors and spikes.** If M is unipotent (τ = 2), every entry of every family is a polynomial in n. So is every quiver reached from the family by a fixed sequence of steps, including steps at g. Its signs are certified for all n ≥ 0 by the Newton criterion: if p(0) > 0 and every forward difference Δʲp(0), j ≥ 1, is ≥ 0, then p(n) = Σ Δʲp(0)·C(n, j) is positive and non-decreasing.

*Proof.*
1. Induction on (n, s). At each step the mutated entry has the sign ε_s for that n, so by Lemma 22.2 the mutation acts as E_s.
2. Replace M by M² if needed (Lemma 22.3). Then ℓ(v_n) + c = Aλⁿ + Bλ⁻ⁿ + C₀ with λ > 1, or a polynomial in n when λ = 1.
   - If A ≠ 0, the term Aλⁿ dominates the value, its first difference and its second difference, so all three have the sign of A from some explicit n₁ on.
   - If A = 0, the integer sequence converges to C₀, so it is eventually constant. Then Bλ⁻ⁿ vanishes, so B = 0 and the sequence is constant.
   - A polynomial is eventually monotone with the sign of its leading coefficient, and so are its differences.
3. Polynomials in n are closed under sums and products, and the mutation rule uses only these and signs. ∎

> **Correction (note 23):** Two hypotheses are missing; neither affects a result of this note, because every tube of the census has τ ≥ 2 ([note 23](23-checks-of-notes-20-to-22.md) §4.4).
> - **Item 1.** Note 14's criterion is checked at n = 0, 1, 2. That suffices only for sequences with e(n + 3) = (τ + 1)e(n + 2) − (τ + 1)e(n + 1) + e(n) and τ ≥ 2. The recurrence of M is that one only if M has characteristic polynomial (x − 1)(x² − τx + 1). For a Coxeter period with π = id the eigenvalue is −1 (Lemma 22.3(2)), and then M² must be used, as note 14 does. With τ < 2 the check can pass and the entry fall: differences 0, 1, 1, 0, −1 for τ = 1.
> - **Item 2.** "Replace M by M²" does not cover τ ∈ {−2, −1, 0, 1}. There the monodromy has finite order, for example for the path T = (0, 1, 1), where C = 2 and M has eigenvalues −1 and ±i. Then ℓ(v_n) is periodic, neither constant nor eventually monotone. Replacing M by a power M^k, with k dividing 12, makes the family constant or polynomial. Such an orbit is finite, so a certificate can put it in E.

**What the lemma gives, and what it does not.**

- **Given the tubes, it closes them.** Suppose V′(x) is a finite set together with finitely many tubes and spikes:
  - the tubes are orbits of periodic walks inside a fixed triangle, each with an eventually periodic sign pattern;
  - the spikes are polynomial families reached from τ = 2 tubes, as in item 3.

  Then a certificate of note 14's form exists, with the polynomial families of item 3, and enumerating candidate certificates finds one. This proves the soundness that note 14 checked one certificate at a time, and it explains the recurrence that note 14 took as a definition.
- **It does not say that V′(x) has this form.** That is the statement a decision procedure needs, and §5 shows it is false: there are classes whose V′ is no finite set plus finitely many tubes.
- **It does not cover spikes on exponential tubes.** When a column entry of a τ > 2 tube has absolute value ≤ 1, the step at the growing vertex is allowed (Lemma 22.1′). It multiplies two growing entries, so the new entries grow like λ²ⁿ: neither a tube in a fixed triangle nor a family of note 14. This is how the side tubes of §5.2 begin.

---

## 5. Where a description by tubes fails

Two things make V′ larger than a finite set plus finitely many tubes. Both start from a column entry of absolute value at most 1, where Lemma 22.1 does not apply. The converse is short.

**Lemma 22.1′ [I].** If |v_i| ≤ 1 for some i ≠ g, then (μ_g X, g) is not an exit, so the step at g is allowed.

*Proof.* In Y = μ_g X the pair {g, i} carries at most one arrow, so Y is not a fork. A pre-fork with point of return g and vertices {g, k, k′} needs the triangles Y ∖ {k} and Y ∖ {k′} to be forks with point of return g. If i ∉ {k, k′}, both contain i. If i = k, the triangle Y ∖ {k′} contains i. Either way one of them has a weight ≤ 1, so it is not a fork. ∎

On a τ = 2 corridor with such an entry, the step at the growing vertex is therefore allowed. It leads to quivers whose entries are quadratic in n, the *spikes* of class 1034 (§6.2). Note 14's engine aborts there, and the polynomial families of Theorem 22.5(3) close them. The two phenomena below are different. The first provably cannot be closed by any finite number of families; for the second this is measured, not proved.

### 5.1 The Markov obstruction

Let X₀ be the quiver with the Markov triangle on {1, 2, 3}, 1 → 2 → 3 → 1 with two arrows each, and one arrow from vertex 1 to vertex 0: X₀ = (−1, 0, 0, 2, −2, 2), with column v = (1, 0, 0). It is the bottom-2 self-mirror census class 707, which note 14 left at "E cap".

**Lemma 22.6 [I].** Let T be the Markov quiver and k a vertex of T. Then (μ_k X, k) is not an exit. So every step inside a Markov triangle is allowed, and the triangle stays the Markov quiver.

*Proof.* μ_k T is again the Markov quiver.
- *A fork with point of return k* needs b_ji > b_ik for the path i → k → j through k inside μ_k T, but both are 2.
- *A pre-fork with point of return k* has vertices {k, k₁, k₁′} and a fourth vertex i₀.
  - If g ∈ {k₁, k₁′}, then the triangle μ_k T would have to be a fork, which it is not: its largest weight is attained three times.
  - Otherwise {k₁, k₁′} is the rest of μ_k T and i₀ = g. The triangles {k, k₁′, g} and {k, k₁, g} are oriented 3-cycles, and g has arrows to both k₁ and k₁′ or from both. In the first case the two cycles read k₁′ → k → g → k₁′ and k₁ → k → g → k₁, so k has two in-neighbours in μ_k T. In the second case it has two out-neighbours. An oriented 3-cycle has one of each. ∎

**Theorem 22.7 [I].** Let X₀ be as above.

1. X₀ lies in no far region, and its class is mutation-cyclic.
2. For every z ≥ 2 and n ≥ 0, V′(X₀) contains the quiver with the Markov triangle and column

   v(z, n) = (−(z − 1)(n + 1), (z − 1)n, z),

   in the labelling where T is 1 → 2 → 3 → 1 and v_i = b_i0. For z ≥ 3 and n ≥ 1 these quivers are pairwise non-isomorphic and have level (z − 1)(n + 1).
3. Hence V′(X₀) has at least L·ln L − 3L quivers of level ≤ L for large L. A finite set together with r families, of note 14's kind or polynomial, has at most |E| + r(6L + 9). So no certificate of note 14's form exists for this class, with any caps. The same holds with the polynomial families of §6.2.

*Proof.*
1. X₀ has two pairs with no arrow, {0, 2} and {0, 3}. By consequence (b) of note 14 §3 it lies in no far region. The Markov quiver is mutation-cyclic (C = 4, weights 2), so the class is (§2).
2. Work up to relabelling. A step at vertex 1, followed by exchanging the names 2 ↔ 3 to restore the orientation of T, acts by Lemma 22.2 as

   (v₁, v₂, v₃) ↦ (−v₁, v₃ + 2v₁, v₂) if v₁ ≥ 0, and (−v₁, v₃, v₂ + 2v₁) if v₁ ≤ 0.

   The rotations (v₁, v₂, v₃) ↦ (v₂, v₃, v₁) are relabellings that keep T. By Lemma 22.6 every such step is allowed. Then:
   - (a, 0, 1 − a) ↦ (−a, 1 + a, 0), a rotation of (1 + a, 0, −a). So from X₀ = (1, 0, 0) every (a, 0, 1 − a), a ≥ 1, is reached.
   - (a, 0, 1 − a) is a rotation of (0, 1 − a, a). The step at the zero entry gives (0, a, 1 − a), a rotation of (1 − a, 0, a) = v(a, 0).
   - From v(z, n), the step at the negative entry gives ((z − 1)(n + 1), z, −(z − 1)(n + 2)), a rotation of v(z, n + 1).

   For z ≥ 3 and n ≥ 1 at most one entry of v(z, n) equals ±2, so T is the only Markov triangle of the quiver. Hence an isomorphism between two such quivers fixes g and T, and acts on v by a rotation. The single negative entry fixes the rotation, so v(z, n) is an invariant of the quiver.
3. The pairs with z ≥ 3, n ≥ 1 and (z − 1)(n + 1) ≤ L number Σ_{m=2}^{⌊L/2⌋} (⌊L/m⌋ − 1) ≥ L·ln L − 3L for large L.

   A family of note 14 has certified monotone entries, so its total weight is non-decreasing and strictly increasing from n = 1 on, unless the family is constant. A polynomial family's weight is strictly increasing from n = 8, its degree bound, on. So each has at most 6L + 9 members of level ≤ L, since the weight is at most 6 times the level. ∎

The check is `n4_tube_lemma.py markov` (`n4_tube_markov.log`).
- It reached v(z, n) for z ≤ 40 and n ≤ 40 by 1,677 real mutations, none of them a strict up-exit.
- It found the 1,599 quivers pairwise non-isomorphic.
- In 60,000 random steps inside a Markov triangle, (μ_k X, k) was never an exit.
- The exhaustive cut of V′(X₀) at level 25, 50, 100 and 200 has 823, 3,181, 12,383 and 49,157 quivers, almost all with a Markov triangle. The ratio is about 4 per doubling, so V′ in fact grows quadratically, faster than the L·ln L proved here.

**What the Markov piece is [H].** On a Markov triangle, the column v moves under the three steps exactly as the shear coordinates of an integral lamination on the once-punctured torus move under flips (Fomin–Thurston; not read here). So V′ ∩ {T Markov} is a union of orbits of the mapping class group acting on laminations. Its orbits are classified, but this is a 2-dimensional object: a lemma for 1-parameter tubes cannot describe it.

The parity of the entries of v, as a multiset, is invariant under the moves above. So the column (−1, 1, 1) is not in the orbit of (1, 0, 0), though it lies in the same plane v₁ + v₂ + v₃ = 1. A decision procedure for these classes would need the orbit invariant, and it would need to control the steps at g where Lemma 22.1′ allows them.

### 5.2 Side tubes: infinitely many tubes with unbounded τ

Census class 108970 (bottom 7, the quiver x = (8, 0, −7, −7, 2, 1) lies in no far region) shows the second phenomenon. Note 14's engine fails on it with "level bound", after finding tubes with τ = 7, 2,302, 5,759,998, 17,842,174 and more.

**The mechanism [I].**
- **The main tube.** V′(x) contains the (0, 0, 57) tube Y_k = (A_{k+1}, 0, −57, −1, A_k, 0), with A₀ = 49, A₁ = 2,791 and A_{k+1} = 57A_k − A_{k−1}. It is a pair walk on {0, 3}, with 57 arrows, and growing vertex 1. Each Y_k → Y_{k+1} is one allowed step.
- **A pendant vertex.** Vertex 2 is joined only to the growing vertex 1, by one arrow. So the column at vertex 1 has an entry of absolute value 1, Lemma 22.1′ applies, and the full triangle on {0, 1, 2} is (0, 1, A_{k+1}).
- **The side tubes.** Each Y_k is therefore also the base of a second tube. Its triangle is (0, 1, a) with a = A_{k+1}, its growing vertex is 3, and its walk is the Coxeter-type walk of the (0, 1, a) tubes of §3. By Lemma 22.3 and §3 that tube grows by λ + 1/λ = C − 2 = a² − 1 per period, and its τ is a² − 1 or (a² − 1)² − 2. So τ grows without bound with k.

**Measured** (`n4_tube_lemma.py side`, `n4_tube_side.log`):
- **The main tube.** The exhaustive cut of V′(x) at level 10¹² has 425 quivers and contains the five Y_k below the cut. The step Y_k → Y_{k+1} is allowed for all 24 values of k tried.
- **The side tubes.** From each of the first 25 members, a walk of 12 allowed steps at vertices 0, 1, 2 keeps the triangle on {0, 1, 2} of the shape (0, 1, a) or (1, a, a), and the entries at vertex 3 grow at the predicted rate. For example, at the 25th member, a has 46 digits and the entry has 500 digits after 12 steps.

This is not proved for every k, and I did not prove that no finite set of families covers V′(x) here; the growth rates differ for each k, which makes a single family covering two side tubes impossible only when the corresponding quadratic fields differ. The Markov obstruction of §5.1 is the proved one. The side tubes show that the failure is not confined to classes with a Markov triangle: they come from a weight-1 entry between a pendant vertex and the growing vertex of a tube.

---

## 6. The 6,990 classes and 2,139 mirror pairs (step 3)

### 6.1 What they are

`n4_tube_lemma.py classify` (`n4_tube_classify.log`) sorts the 6,990 classes by their bottom quiver and by V′ cut at levels 32b and 128b, where b is the bottom. A class is put in the first of these kinds that applies:

- **disconnected:** the bottom quiver has an isolated vertex, or two components on two vertices;
- **acyclic bottom:** a bottom component contains an acyclic quiver;
- **Markov triangle:** some quiver of the cut has a Markov triangle;
- **connected and cyclic:** split by growth. "Linear" means the cut grows by a factor of at least 2.5 from 32b to 128b, as τ = 2 corridors do. "Slow" means it grows less, as exponential tubes do.

| Kind | Classes | Self-mirror | In mirror pairs | Open mirror pairs (note 14) |
|---|---|---|---|---|
| disconnected | 400 | 176 | 224 | 28 |
| acyclic bottom | 1,556 | 332 | 1,224 | 0 (Caldero–Keller) |
| Markov triangle | 456 | 162 | 294 | 147 |
| connected and cyclic, V′ linear | 2,282 | 412 | 1,870 | 935 |
| connected and cyclic, V′ slow | 2,296 | 238 | 2,058 | 1,029 |
| all | 6,990 | 1,320 | 5,670 | 2,139 |

- **Disconnected classes are settled by rank 3 [P, I].** A mutation acts inside one component, so the class of T ⊔ {g} is the class of T together with an isolated vertex. 292 of the 400 have a triangle that is not mutation-cyclic, so they are mutation-acyclic. The other 108 have a mutation-cyclic triangle, whose class is determined by its root (BBH Theorem 5.1, note 3 Theorem 3.1).
  - A flat step at a root reverses the cyclic order of the weights. So T ~ −T exactly when the root has two equal weights or a flat step.
  - This holds for the 52 classes that the census calls self-mirror and fails for the 56 in census mirror pairs. So the 28 open mirror pairs of disconnected classes are certified distinct.
- **Acyclic-bottom classes are mutation-acyclic.** Their equivalence is decided by arXiv 2610.36179, and their mirror pairs were already certified by Caldero–Keller in note 14.
- **Markov classes** are the classes of §5.1. For class 707 no certificate of note 14's form exists (Theorem 22.7). For the other 455 this is measured, not proved: half of them hit the cap of 24,000 quivers at level 128b, and the rest grow quadratically.

### 6.2 A second pass: polynomial families and corridor search

`n4_tube_lemma.py certify2` is note 14's engine with three changes.

1. **Polynomial families.** A τ = 2 base is turned into a family whose six entries are polynomials in n of degree ≤ 8, stored as their values at n = 0, …, 8. Mutation is computed exactly, including the step at the growing vertex, where two growing entries are multiplied. Every sign and every comparison is certified for all n ≥ 0 by the Newton criterion of Theorem 22.5(3); an undetermined one, or a degree above 8, aborts the attempt. The closure check is the same as note 14's:
   - every step from a family is a strict up-exit for all n, or lands in a known family up to a shift of −3 to 3 and a relabelling, or gives a new family, which is closed in turn;
   - quivers below a negative shift that are reached by an allowed step must lie in E or in a family.

   This closes the spikes of Lemma 22.1′.

   **Example: census class 1034** (bottom 3, start (3, 0, −2, 0, 3, −2)). Note 14 failed with "E cap". Its V′ contains corridors such as (N, 0, −(N − 2), −3, 2, −3), N even, whose column at vertex 0 has a zero entry. The step at vertex 0 is therefore allowed (Lemma 22.1′), and it leads to a spike of two quivers at level about N², for example (−20, 0, 18, −3, −358, −3) at N = 20. From there the next steps go back to the corridors or are strict up-exits. The second pass certifies the class with 14 families, 10 of them polynomial; its bottom of N is (3, 0, −3, 0, 2, 2), equal to its own mirror image.
2. **A corridor search.** From a frontier quiver, besides note 14's forward path, which climbs into the spikes, the engine walks the rank-2 orbit of every pair with two arrows. It stops at the first step that is not allowed, so the quivers on the walk lie in V′. Bases are read off these walks too.
3. **Larger caps.** E may hold 6,000 quivers, the certificate 1,200 families, and each class gets 12 seconds.

The bottom of N is computed as in note 14, from E and the first three members of each family. Those are quivers of V′, because every base is read off a walk of allowed steps and every new family is reached by a step that is allowed for all n. A broken certificate cannot pass: the closure would fail, and note 19's control of note 14's engine applies unchanged to the parts that are shared.

**The run** (`n4_tube_certify2.log`, `n4_tube_pairs.log`), on all 6,990 classes:

| Kind | Classes | Certified | Main reason for failure |
|---|---|---|---|
| connected and cyclic, V′ linear | 2,282 | **2,155** | E cap 81, level bound 37, other 9 |
| connected and cyclic, V′ slow | 2,296 | **51** | level bound 1,991, no periodic base 243, time 11 |
| Markov triangle | 456 | 0 | time 454, E cap 2 |
| acyclic bottom | 1,556 | 0 | level bound 1,246, E cap 266, other 44 |
| disconnected | 400 | 0 | no periodic base 318, E cap 82 |
| all | 6,990 | **2,206** | |

- **Polynomial families** occur in 2,150 of the 2,206 new certificates. Every new certificate separates the bottom of the core from the fourth members of its families.
- **Crosschecks** (`certify2` summary):
  - "the bottom of the core equals its mirror image" agrees with the census mirror map in 2,206 of 2,206 classes;
  - no new bottom equals the bottom of another certified class, old or new;
  - in all 900 mirror pairs with both classes newly certified, the two bottoms are mirror images and different.
- **A brute-force check** (`verify2`, `n4_tube_verify2.log`) on 200 random new certificates. It uses the same mutation and exit code, so it is not independent in the sense of note 19.

> **Correction (note 23):** An independent check now exists, with code that shares nothing with `certify2`. The cut of V′(x) at level 1,024·b was complete for every one of the 2,206 classes, 13,083,090 quivers in all. Its least level and its bottom quivers equal the certified bottom of N in 2,206 of 2,206. An independent engine built its own certificates for 150 classes: 103 random, the class 1034 and the extremes. It certified 149 with the same bottoms and found no failure of closure in 563,622 steps. Class 500677 it could not certify, which is inconclusive, and its bottom is confirmed by the cut. The certificates of `certify2` themselves are not stored, only a summary line per class, so they cannot be re-checked without rerunning it.
  - All 200 are certified again with the same bottom.
  - The exhaustive cut of V′ at level min(20,000, 4L) was complete in 189 classes and stopped at 60,000 quivers in 11. Its 3,342,067 quivers all lie in E or in a family.
  - The least quivers of the cut are the certified bottom in all 189 complete cuts.
  - Replaying the allowed steps out of the members Y(3) to Y(10) of every family gives 150,648 steps, all landing in E or in a family.
- **What is left.** The failures are of the two kinds of §5.
  - The Markov classes run out of time with E full.
  - The slow classes keep finding new tubes at higher levels. A rerun that records what was found (`sidesig`, `n4_tube_sidesig.log`) shows the side-tube signature:
    - before giving up, the engine had found a tube with τ of 25 to 36 digits in all 2,245 slow classes it leaves open, and in 42 of the 127 linear ones;
    - no certificate of note 14 has τ above 15 digits;
    - a τ that large comes from a triangle that carries an entry of another tube, as in class 108970 (§5.2).
  - The disconnected and acyclic classes are decided otherwise (§6.1), so their failures do not matter.

### 6.3 After this note

| | Classes | Mirror pairs | Self-mirror classes |
|---|---|---|---|
| census | 788,026 | 377,451 | 33,124 |
| finite core (note 14) | 555,828 | | |
| tube certificate: note 14 / this note | 225,208 / 2,206 | | |
| certified by cores, note 14 (with Caldero–Keller) | | 375,312 | 31,804 |
| certified by cores, this note | | 900 | 406 |
| disconnected, settled by rank 3 | 400 | 28 | 52 |
| acyclic bottom quiver, mutation-acyclic | 1,556 | | |
| **open** | **2,828** | **1,211** | |

- **The open classes.** 2,828 connected, mutation-cyclic classes are open, as far as the bottom quivers show:
  - 456 with a Markov triangle;
  - 2,245 with slow growth;
  - 127 with linear growth.
- **The open pairs.** The 1,211 open mirror pairs are 147 Markov pairs, 1,025 slow pairs and 39 linear pairs.
- **Pairwise distinct.** 783,242 classes are now pairwise certified different: note 14's 781,036 and the 2,206 new ones, whose bottoms of N are new.
- **Hidden joins.** A hidden join between census classes would have to involve one of the 2,828 open classes, one of the 1,556 mutation-acyclic ones (decidable by arXiv 2610.36179, but not run here), or one of the 400 disconnected ones.

---

## 7. What this gives for FWZ Problem 2.6.14 at n = 4 (step 4)

Combine the known pieces with this note's.

1. **Mutation-acyclic quivers [P].** Mutation-acyclicity on 4 vertices is decidable, and equivalence is decided whenever one of the two quivers is mutation-acyclic (arXiv 2610.36179, abstract, with Caldero–Keller).
2. **Disconnected quivers [P, I].** A mutation acts inside one connected component, and a connected quiver stays connected. So a disconnected 4-vertex quiver is a 3-vertex quiver plus an isolated vertex, or two quivers on two vertices. Its class is decided by rank 3: the root of BBH Theorem 5.1 for a mutation-cyclic triangle, Caldero–Keller otherwise (note 3, Theorem 3.1).
3. **Connected mutation-cyclic quivers [I].** Run the core search of note 14 and the certificate search of note 14 §8 with the polynomial families of §6.2 on both quivers. If both stop, the quivers are equivalent exactly when the bottoms of N agree (Theorem 14.1, note 19 §6.4). Theorem 22.5 says a search over all candidate certificates stops whenever V′ is a finite set together with finitely many tubes and polynomial spikes on corridors.

**So, precisely.** On 4 vertices, mutation equivalence up to relabelling is decided for every pair of quivers except possibly when both are connected and mutation-cyclic and one of the two classes has no certificate of this form. Equivalence itself is always semi-decidable, by enumerating mutation sequences. What is missing is a proof of non-equivalence for such pairs.

**On the census.** 785,198 of the 788,026 classes are covered:
- 555,828 have a finite core;
- 227,414 have a tube certificate;
- of the rest, 400 are disconnected and 1,556 have an acyclic quiver at the bottom.

The other 2,828 are connected, mutation-cyclic as far as their bottom quivers show, and without a certificate.

**The route needs no bound on f(Q, w).** Nothing here uses Conjecture 10.1, F(4, w) ≤ 2w², or any bound on barriers: forks and pre-forks cut the class, and the certificates describe what is left with no bound on the entries.

**But it is not a decision procedure.** By Theorem 22.7 the gap is not empty. Class 707, a connected mutation-cyclic class of bottom 2, has no certificate of this form at all, because its V′ is not a finite set plus finitely many tubes. The side tubes of §5.2 suggest that such classes also occur without a Markov triangle. A decision procedure along this route needs two further lemmas:

- **a 2-dimensional one for Markov pieces**, through the orbit invariant of laminations on the once-punctured torus [H];
- **a recursive one for tubes that hang from tubes**, with families in two parameters.

Conjecture 10.1, if proved, would give a decision procedure without either (Corollary G of note 3 §6: an effective bound decides equivalence by bounded search).

---

## 8. Not done

- **The general statement behind §3.** That every tube of a 4-vertex class has a constant triangle, a periodic walk and τ given by the Markov constant is measured on the certificates, not proved. Lemma 22.3 proves it for Coxeter walks, and Proposition 22.4 for mutation-cyclic triangles.
- **Side tubes for every k.** Measured for the first 25 members of the main tube of class 108970. The claim that no finite set of families covers that V′ is not proved.
- **The Markov classes beyond class 707.** Theorem 22.7 is proved for one class. For the other Markov classes of §6 the obstruction is measured: V′ is large in every cut, and every certificate attempt fails.
- **Spikes on exponential tubes.** Neither Theorem 22.5 nor the second pass handles a step at the growing vertex of a τ > 2 tube that Lemma 22.1′ allows. Such steps start the side tubes, and a certificate for them would need families in two parameters.
- **The lamination picture of §5.1** is heuristic. I did not read Fomin–Thurston and did not check the correspondence beyond the parity invariant.
- **Pairwise distinctness of the new certificates** is checked against the bottoms of all 227,414 tube certificates (§6.2); against the finite cores it rests on note 14 §4, which separates every class without a finite core from every class with one.
- **The polynomial engine** (`certify2`) was written for this note and checked by the crosschecks and the brute-force check of §6.2, which share its mutation and exit code. No independent implementation was run, unlike the check of note 14's engine in note 19.

  > **Correction (note 23):** An independent implementation has now been run; see the note in §6.2 and [note 23](23-checks-of-notes-20-to-22.md) §3.3. The counts of §6 and §7 were recomputed from the stored files: 2,828 open classes, 1,211 open pairs, 900 pairs and 406 self-mirror classes certified by cores, 28 pairs by rank 3, 783,242 and 785,198. No open pair has exactly one class certified, so no pair is settled by the mirror of a single certificate.

---

## 9. Reproduce

```bash
PY=python
$PY -I n4_tube_lemma.py classify --procs 6 --out n4_tube_classify.jsonl.gz > n4_tube_classify.log      # about 5 minutes
$PY -I n4_tube_lemma.py lemma > n4_tube_lemma.log
$PY -I n4_tube_lemma.py markov > n4_tube_markov.log
$PY -I n4_tube_lemma.py side > n4_tube_side.log
$PY -I n4_tube_lemma.py shapes --classes 300000 --procs 5 --out ~/.cache/n4_tube_shapes.jsonl.gz   # about 1 hour
$PY -I n4_tube_lemma.py shapes --summary --out ~/.cache/n4_tube_shapes.jsonl.gz > n4_tube_shapes.log
$PY -I n4_tube_lemma.py certify2 --budget 12 --procs 6 --out n4_tube_certify2.jsonl.gz > n4_tube_certify2.log   # about 45 minutes
$PY -I n4_tube_lemma.py verify2 --classes 200 > n4_tube_verify2.log
$PY -I n4_tube_lemma.py sidesig --procs 6 > n4_tube_sidesig.log
$PY -I n4_tube_lemma.py pairs > n4_tube_pairs.log
```

- All commands read the output of note 14: `n4_opposite_tubes.jsonl.gz`, `n4_opposite_plateaus.jsonl.gz` and `n4_opposite_cores.jsonl.gz`. `certify2`, `sidesig` and `pairs` also read `n4_tube_classify.jsonl.gz`, and `verify2`, `sidesig` and `pairs` read `n4_tube_certify2.jsonl.gz`.
- `shapes` re-runs note 14's certificates with full output, so its record file is large and is kept under `~/.cache`. Its log is in `experiments/`.

---

## Sources

- Warkentin, *Exchange graphs via quiver mutation*, thesis, Chemnitz 2014, as read for note 19; Ervin, arXiv 2306.07502 (forks, pre-forks, far regions: note 14 §3).
- Beineke, Brüstle, Hille (BBH), *Cluster-cyclic quivers with three vertices and the Markov equation*: https://arxiv.org/abs/math/0612213 (Theorem 1.2, Lemma 3.1, Theorem 5.1, as checked in note 3).
- Buan, Marsh, Reiten (BMR08), *Cluster mutation via quiver representations*, Corollary 5.3, quoted in arXiv 2610.36179 Proposition 2.1 (not read here).
- Armstrong-Williams, Hirst, Jackson, Lee, *Mutation-acyclicity in rank four is decidable but not semialgebraic*: https://arxiv.org/abs/2610.36179 (abstract, §1, Proposition 2.1).
- Caldero, Keller, *From triangulated categories to cluster algebras II*, Cor. 4: https://arxiv.org/abs/math/0510251 (as quoted in note 11).
- Notes 3, 11, 14, 15 and 19 of this repository.
