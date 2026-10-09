"""
MECHANISM TEST for the AAC application.

Claim under test: context-derived specificity substitutes for user-disclosed
specificity. Operationalised here as: does GROUP-LOCAL popularity retrieve
long-tail items that GLOBAL popularity cannot, without any individual
disclosure, and at what identification cost?

Occupation stands in for "shared setting" (the room). It is a structural
proxy only. The ethical argument in the AAC case requires a grouping that is a
property of the environment (a room), not of the person.
"""
import numpy as np, pandas as pd, scipy.sparse as sp, time
exec(open('src/experiment.py').read().split('# ---------------------------------------------------------------- sweep')[0])

us = pd.read_csv(f"{DATA}/users.dat", sep="::", engine="python",
                 names=["userId","gender","age","occ","zip"])
occ = dict(zip(us.userId, us.occ))

tail_cut = np.quantile(POP_COUNT, 0.80)
TAIL = POP_COUNT < tail_cut
TGT_T = TGT & TAIL[None, :]
n_t = TGT_T.sum(1); keep = n_t >= 1

def eval_tail(S):
    S = np.where(MASK, S, -np.inf)
    top = np.argpartition(-S, KEVAL, axis=1)[:, :KEVAL]
    hits = np.take_along_axis(TGT_T, top, 1)
    r = np.zeros(n_users); r[keep] = hits[keep].sum(1)/np.minimum(KEVAL, n_t[keep])
    return r[keep].mean()

def eval_std(S):
    S = np.where(MASK, S, -np.inf)
    top = np.argpartition(-S, KEVAL, axis=1)[:, :KEVAL]
    hits = np.take_along_axis(TGT, top, 1)
    return (hits.sum(1)/np.minimum(KEVAL, n_tgt)).mean()

# group popularity computed ONLY from TRAINING users (never the test cohort)
train_ids = sorted(train_users)
tr = pos[pos.userId.isin(train_users)].copy()
tr["occ"] = tr.userId.map(occ)
GPOP = {}
for o, g in tr.groupby("occ"):
    v = np.zeros(n_items)
    idx = g.movieId.map(i2x).values
    np.add.at(v, idx, 1.0)
    GPOP[o] = v / max(g.userId.nunique(), 1)      # per-capita, so group size is fair

test_occ = np.array([occ[u] for u in uids])
groups, counts = np.unique(test_occ, return_counts=True)
print(f"groups present in cohort: {len(groups)}, sizes {counts.min()}-{counts.max()} (median {int(np.median(counts))})")

# ---- GATE 1: is group popularity actually different from global popularity?
gl_top = set(np.argsort(-POP_COUNT)[:20])
ov = []
for o in groups:
    gt = set(np.argsort(-GPOP[o])[:20])
    ov.append(len(gt & gl_top)/20)
print(f"\nGATE 1  overlap of group top-20 with global top-20: mean {np.mean(ov):.1%}  range {min(ov):.0%}-{max(ov):.0%}")

# ---- conditions
S_glob = np.tile(POP_COUNT, (n_users,1))
S_grp  = np.vstack([GPOP[o] for o in test_occ])
# "local core": group popularity restricted to globally-tail items
S_grp_tail = S_grp.copy(); S_grp_tail[:, ~TAIL] = -np.inf

rows = []
rows.append(("global popularity (no disclosure, no context)", 0, eval_std(S_glob), eval_tail(S_glob)))
rows.append(("group popularity (context only, no disclosure)", 0, eval_std(S_grp), eval_tail(S_grp)))
rows.append(("group popularity restricted to tail items", 0, eval_std(S_grp_tail), eval_tail(S_grp_tail)))
for k in [1,3,8,13]:
    M = item_matrix(select(k,"random"))
    rows.append((f"individual disclosure, {k} random items", k, eval_std(M@B), eval_tail(M@B)))
    # context + individual, combined
    Sc = (M@B); Sc = Sc/np.maximum(np.abs(Sc).max(1,keepdims=True),1e-9)
    Sg = S_grp/np.maximum(S_grp.max(1,keepdims=True),1e-9)
    rows.append((f"  + group context, {k} items", k, eval_std(Sc+Sg), eval_tail(Sc+Sg)))

R = pd.DataFrame(rows, columns=["condition","k","std_recall","tail_recall"])
print("\n=== UTILITY ===")
print(R.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# ---- GATE 2: identification cost of group membership alone
# How far does knowing someone's group narrow the candidate set?
print("\n=== GATE 2  identification cost ===")
sizes = pd.Series(test_occ).value_counts()
print(f"  knowing the group narrows {n_users} users to a median of {int(sizes.median())} "
      f"(smallest group {sizes.min()}, largest {sizes.max()})")
print(f"  P(identified at rank 1) from group alone <= {1/sizes.median():.1%}")
print(f"  for comparison, 8 random disclosed items identified 90.3% at rank 1")

# ---- GATE 3: does group context ADD anything over global once you have disclosure?
print("\n=== GATE 3  does context add beyond disclosure? ===")
for k in [1,3,8,13]:
    a = R[(R.k==k)&(R.condition.str.startswith("individual"))].tail_recall.iloc[0]
    b = R[(R.k==k)&(R.condition.str.startswith("  + group"))].tail_recall.iloc[0]
    print(f"  k={k:3d}  disclosure alone={a:.4f}   +context={b:.4f}   delta={b-a:+.4f}")

R.to_csv("results/context_test.csv", index=False)
