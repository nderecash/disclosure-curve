"""GATE 4: is the group-tail result real, or does ANY grouping work?
If shuffled group labels give the same tail recall, the grouping carries no
information and the gain is just the tail-restriction."""
import numpy as np, pandas as pd
exec(open('src/experiment.py').read().split('# ---------------------------------------------------------------- sweep')[0])
us = pd.read_csv(f"{DATA}/users.dat", sep="::", engine="python",
                 names=["userId","gender","age","occ","zip"])
occ = dict(zip(us.userId, us.occ))
tail_cut = np.quantile(POP_COUNT, 0.80); TAIL = POP_COUNT < tail_cut
TGT_T = TGT & TAIL[None,:]; n_t = TGT_T.sum(1); keep = n_t>=1
def eval_tail(S):
    S=np.where(MASK,S,-np.inf); top=np.argpartition(-S,KEVAL,axis=1)[:,:KEVAL]
    h=np.take_along_axis(TGT_T,top,1); r=np.zeros(n_users)
    r[keep]=h[keep].sum(1)/np.minimum(KEVAL,n_t[keep]); return r[keep].mean()

tr = pos[pos.userId.isin(train_users)].copy(); tr["occ"]=tr.userId.map(occ)
def build(labels_tr, labels_te):
    GP={}
    for o,g in tr.groupby(labels_tr):
        v=np.zeros(n_items); np.add.at(v, g.movieId.map(i2x).values, 1.0)
        GP[o]=v/max(g.userId.nunique(),1)
    S=np.vstack([GP[o] for o in labels_te]); S=S.copy(); S[:,~TAIL]=-np.inf
    return eval_tail(S)

real = build(tr.occ.values, np.array([occ[u] for u in uids]))
print(f"REAL occupation groups, tail-restricted : {real:.4f}")

rng=np.random.default_rng(0); sh=[]
for i in range(20):
    uniq=tr.userId.unique(); lab=rng.integers(0,21,len(uniq)); m=dict(zip(uniq,lab))
    lt=tr.userId.map(m).values
    lte=rng.integers(0,21,n_users)
    sh.append(build(lt,lte))
sh=np.array(sh)
print(f"SHUFFLED groups (20 runs)               : {sh.mean():.4f}  [{sh.min():.4f}, {sh.max():.4f}]")
print(f"\ngain from real grouping: {real-sh.mean():+.4f}  ({real/max(sh.mean(),1e-9):.2f}x)")

# and the pure tail-popularity baseline with NO grouping at all
v=POP_COUNT.copy().astype(float); S=np.tile(v,(n_users,1)); S[:,~TAIL]=-np.inf
print(f"GLOBAL popularity, tail-restricted      : {eval_tail(S):.4f}")
