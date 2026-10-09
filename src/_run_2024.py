"""
The Disclosure Curve: utility vs re-identifiability across input forms.
MovieLens 1M. Seed 42. All conditions computed offline, no API calls.

Two axes:
  UTILITY          Recall@20 / NDCG@20 against held-out items
  RE-IDENTIFIABILITY  rank of the true user when an adversary matches the
                      system's *holding* against every full user profile

Input forms compared at matched k:
  raw-random    k item IDs, drawn at random
  raw-recency   k most recently rated item IDs
  raw-popular   k most-watched item IDs (Biega 2020's best kNN strategy)
  attr          TRANSLATION: k items -> structured attribute profile
                (genre weights + decade weights + popularity tier). No titles.
  attr-oblique  TRANSLATION, coarse: genre weights only. Maximum obliqueness.
Plus: full history (ceiling) and popularity (floor).
"""
import numpy as np, pandas as pd, scipy.sparse as sp, time, json, os, re

SEED = 2024
RNG = np.random.default_rng(SEED)
KEVAL = 20
KS = [1, 2, 3, 5, 8, 13, 21, 34, 55]
MINPOOL = max(KS)
M_EXP = 20   # exemplar items a description expands into before scoring
N_TEST_CANDIDATES = 2000
DATA = os.environ.get("ML1M_DIR", "data/ml-1m")
OUT = os.environ.get("OUT_DIR", "results")
os.makedirs(OUT, exist_ok=True)
t_start = time.time()

# ---------------------------------------------------------------- load
r = pd.read_csv(f"{DATA}/ratings.dat", sep="::", engine="python",
                names=["userId", "movieId", "rating", "timestamp"])
mv = pd.read_csv(f"{DATA}/movies.dat", sep="::", engine="python",
                 names=["movieId", "title", "genres"], encoding="latin-1")
print(f"raw: {len(r)} ratings, {r.userId.nunique()} users, {r.movieId.nunique()} films")

pos = r[r.rating >= 4].copy()
for _ in range(5):
    ic = pos.movieId.value_counts(); pos = pos[pos.movieId.isin(ic[ic >= 20].index)]
    uc = pos.userId.value_counts();  pos = pos[pos.userId.isin(uc[uc >= 20].index)]
print(f"after filter: {len(pos)} positives, {pos.userId.nunique()} users, {pos.movieId.nunique()} films")

items = np.sort(pos.movieId.unique())
i2x = {m: i for i, m in enumerate(items)}
n_items = len(items)

# ---------------------------------------------------------------- item attributes
mv = mv[mv.movieId.isin(items)].copy()
mv["x"] = mv.movieId.map(i2x)
mv = mv.sort_values("x")

GENRES = sorted({g for gs in mv.genres for g in gs.split("|")})
G = np.zeros((n_items, len(GENRES)), dtype=np.float64)
for x, gs in zip(mv.x.values, mv.genres.values):
    for g in gs.split("|"):
        G[x, GENRES.index(g)] = 1.0
G = G / np.maximum(G.sum(1, keepdims=True), 1e-9)   # row-normalised genre mix

years = mv.title.str.extract(r"\((\d{4})\)\s*$")[0].astype(float).values
years = np.where(np.isnan(years), np.nanmedian(years), years)
DEC_EDGES = [0, 1960, 1970, 1980, 1990, 1995, 2000, 9999]
dec_idx = np.digitize(years, DEC_EDGES) - 1
D = np.zeros((n_items, len(DEC_EDGES) - 1))
D[np.arange(n_items), dec_idx] = 1.0

print(f"attributes: {len(GENRES)} genres, {D.shape[1]} era bands")

# ---------------------------------------------------------------- user split
users = pos.userId.unique().copy(); RNG.shuffle(users)
cand_users = set(users[:N_TEST_CANDIDATES]); train_users = set(users[N_TEST_CANDIDATES:])
d = pos[pos.userId.isin(train_users)]
X = sp.csr_matrix((np.ones(len(d), np.float32),
                   (pd.Categorical(d.userId).codes, d.movieId.map(i2x).values)),
                  shape=(d.userId.nunique(), n_items))
print(f"train matrix {X.shape}, nnz {X.nnz}")

POP_COUNT = np.asarray(X.sum(0)).ravel().astype(np.float64)
POP_TIER = np.zeros((n_items, 4))
qs = np.quantile(POP_COUNT, [0.25, 0.5, 0.75])
POP_TIER[np.arange(n_items), np.digitize(POP_COUNT, qs)] = 1.0

# attribute matrix the "translated" profile lives in
ATTR_FULL = np.hstack([G, D, POP_TIER])          # genres + era + popularity tier
ATTR_OBL  = G                                     # genres only

# ---------------------------------------------------------------- test cohort
td = pos[pos.userId.isin(cand_users)].sort_values("timestamp")
uids, pool, target = [], [], []
for uid, g in td.groupby("userId"):
    idx = g.movieId.map(i2x).values                    # timestamp order
    nt = max(1, int(round(0.2 * len(idx))))
    perm = RNG.permutation(len(idx)); tset = set(perm[:nt])
    p = np.array([idx[j] for j in range(len(idx)) if j not in tset])
    if len(p) < MINPOOL:
        continue
    uids.append(uid)
    target.append(np.array([idx[j] for j in sorted(tset)]))
    pool.append(p)
n_users = len(uids)
print(f"fixed cohort: {n_users} users (pool >= {MINPOOL})")

# ---------------------------------------------------------------- models
def train_ease(Xm, lam=250.0):
    Gm = np.asarray((Xm.T @ Xm).todense(), np.float64)
    di = np.diag_indices(Gm.shape[0]); Gm[di] += lam
    P = np.linalg.inv(Gm); B = P / (-np.diag(P)); B[di] = 0.0
    return B

t = time.time(); B = train_ease(X); print(f"EASE trained {time.time()-t:.1f}s")

# ---------------------------------------------------------------- eval scaffolding
MASK = np.ones((n_users, n_items), bool)
TGT = np.zeros((n_users, n_items), bool)
for u in range(n_users):
    MASK[u, pool[u]] = False          # whole pool excluded at EVERY k
    TGT[u, target[u]] = True
n_tgt = TGT.sum(1)
DISC = 1.0 / np.log2(np.arange(2, KEVAL + 2))
IDCG = np.array([DISC[:min(KEVAL, t_)].sum() for t_ in n_tgt])

def evaluate(S):
    S = np.where(MASK, S, -np.inf)
    top = np.argpartition(-S, KEVAL, axis=1)[:, :KEVAL]
    order = np.argsort(-np.take_along_axis(S, top, 1), axis=1)
    top = np.take_along_axis(top, order, 1)
    hits = np.take_along_axis(TGT, top, 1)
    return hits.sum(1) / np.minimum(KEVAL, n_tgt), (hits * DISC).sum(1) / IDCG

# ---------------------------------------------------------------- selection
def select(k, cond):
    """Return list of selected item indices per user."""
    out = []
    for u in range(n_users):
        p = pool[u]
        kk = len(p) if k == "all" else k
        if cond == "random":    sel = RNG.choice(p, kk, replace=False)
        elif cond == "recency": sel = p[-kk:]
        elif cond == "popular": sel = p[np.argsort(-POP_COUNT[p])[:kk]]
        out.append(np.asarray(sel))
    return out

def item_matrix(sels):
    rows, cols = [], []
    for u, s in enumerate(sels):
        rows.extend([u] * len(s)); cols.extend(s.tolist())
    return sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n_users, n_items))

# ---------------------------------------------------------------- TRANSLATION
# A translated profile keeps no titles. It keeps a weighted description of
# WHAT the person wants, built from the k items, in attribute space.
# Scoring: every candidate item is scored by how well its attributes match
# the profile (cosine), so the system never sees an item the user named.
def translate(sels, A):
    """k items -> attribute profile (n_users x n_attrs), L2 normalised."""
    P = np.zeros((n_users, A.shape[1]))
    for u, s in enumerate(sels):
        P[u] = A[s].mean(0)
    return P / np.maximum(np.linalg.norm(P, axis=1, keepdims=True), 1e-9)

An_FULL = ATTR_FULL / np.maximum(np.linalg.norm(ATTR_FULL, axis=1, keepdims=True), 1e-9)
An_OBL  = ATTR_OBL  / np.maximum(np.linalg.norm(ATTR_OBL,  axis=1, keepdims=True), 1e-9)

# ---------------------------------------------------------------- RE-IDENTIFIABILITY
# Adversary holds whatever the system holds, and searches the full user
# database for the best match. We report the rank of the TRUE user.
# Each adversary is optimal for its own representation (fair comparison).
FULLP = np.zeros((n_users, n_items), np.float32)
for u in range(n_users):
    FULLP[u, pool[u]] = 1.0
    FULLP[u, target[u]] = 1.0
FULLP_n = FULLP / np.maximum(np.linalg.norm(FULLP, axis=1, keepdims=True), 1e-9)

FULL_ATTR = (FULLP @ ATTR_FULL)
FULL_ATTR_n = FULL_ATTR / np.maximum(np.linalg.norm(FULL_ATTR, axis=1, keepdims=True), 1e-9)
FULL_OBL = (FULLP @ ATTR_OBL)
FULL_OBL_n = FULL_OBL / np.maximum(np.linalg.norm(FULL_OBL, axis=1, keepdims=True), 1e-9)

def reident(H, DB):
    """H: holdings (n_users x d), DB: database (n_users x d), both L2-normed.
    Returns rank (1 = perfectly identified) of the true user."""
    S = H @ DB.T                                   # n_users x n_users
    true = S[np.arange(n_users), np.arange(n_users)]
    return (S > true[:, None]).sum(1) + 1

# ---------------------------------------------------------------- sweep
rows = []
def record(cond, k, rec, ndcg, rank):
    for u in range(n_users):
        rows.append((uids[u], cond, k, rec[u], ndcg[u], int(rank[u])))

# floor: popularity, holds nothing
rec, nd = evaluate(np.tile(POP_COUNT, (n_users, 1)))
record("popularity", 0, rec, nd, np.full(n_users, n_users))

# ceiling: full history
sels_all = [pool[u] for u in range(n_users)]
M = item_matrix(sels_all)
rec, nd = evaluate(M @ B)
Hn = np.asarray(M.todense()); Hn = Hn / np.maximum(np.linalg.norm(Hn, axis=1, keepdims=True), 1e-9)
record("full", -1, rec, nd, reident(Hn, FULLP_n))

for k in KS:
    for cond in ["random", "recency", "popular"]:
        sels = select(k, cond)
        M = item_matrix(sels)
        rec, nd = evaluate(M @ B)
        Hn = np.asarray(M.todense())
        Hn = Hn / np.maximum(np.linalg.norm(Hn, axis=1, keepdims=True), 1e-9)
        record(f"raw-{cond}", k, rec, nd, reident(Hn, FULLP_n))

    # TRANSLATION. The system holds an attribute description, not titles.
    # To predict, the description is expanded into M generic exemplar items that
    # match it, and those go through the SAME model (EASE). This isolates the
    # effect of the input FORM; the scorer is identical across all conditions.
    for src in ["random", "popular"]:
        sels = select(k, src)
        Pf = translate(sels, ATTR_FULL)
        sim = Pf @ An_FULL.T                      # n_users x n_items
        exemplars = np.argpartition(-sim, M_EXP, axis=1)[:, :M_EXP]
        E = np.zeros((n_users, n_items))
        np.put_along_axis(E, exemplars, 1.0, axis=1)
        rec, nd = evaluate(E @ B)
        tag = "attr" if src == "random" else "attr-pop"
        record(tag, k, rec, nd, reident(Pf, FULL_ATTR_n))

        if src == "random":
            Po = translate(sels, ATTR_OBL)
            simo = Po @ An_OBL.T
            exo = np.argpartition(-simo, M_EXP, axis=1)[:, :M_EXP]
            Eo = np.zeros((n_users, n_items)); np.put_along_axis(Eo, exo, 1.0, axis=1)
            rec, nd = evaluate(Eo @ B)
            record("attr-oblique", k, rec, nd, reident(Po, FULL_OBL_n))

            # CONTROL: another user's description, scored for this user.
            # If this performs as well, the condition is recovering population
            # structure rather than anything about the individual.
            shuf = RNG.permutation(n_users)
            Ps = Pf[shuf]
            sims = Ps @ An_FULL.T
            exs = np.argpartition(-sims, M_EXP, axis=1)[:, :M_EXP]
            Es = np.zeros((n_users, n_items)); np.put_along_axis(Es, exs, 1.0, axis=1)
            rec, nd = evaluate(Es @ B)
            record("attr-shuffled-control", k, rec, nd, reident(Ps, FULL_ATTR_n))

df = pd.DataFrame(rows, columns=["user", "cond", "k", "recall", "ndcg", "rank"])
df.to_csv(f"{OUT}/sweep_2024.csv", index=False)

meta = dict(seed=SEED, n_users=n_users, n_items=n_items, minpool=MINPOOL,
            n_train_users=int(X.shape[0]), n_genres=len(GENRES),
            ks=KS, runtime_s=round(time.time() - t_start, 1))
json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=2)

summ = df.groupby(["cond", "k"]).agg(recall=("recall", "mean"),
                                     ndcg=("ndcg", "mean"),
                                     rank=("rank", "median")).round(4)
print("\n=== Recall@20 / NDCG@20 / median re-id rank ===")
print(summ.to_string())
print(f"\ntotal {time.time()-t_start:.1f}s | cohort {n_users} | items {n_items}")
