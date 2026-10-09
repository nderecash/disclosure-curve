"""GATE: the fair comparison. Restrict BOTH context and disclosure conditions
to tail items, so every condition gets the same 20 slots for tail retrieval."""
import numpy as np, pandas as pd, scipy.sparse as sp
exec(open('src/experiment.py').read().split('# ---------------------------------------------------------------- sweep')[0])
us=pd.read_csv(f"{DATA}/users.dat",sep="::",engine="python",names=["userId","gender","age","occ","zip"])
occ=dict(zip(us.userId,us.occ))
tail_cut=np.quantile(POP_COUNT,0.80); TAIL=POP_COUNT<tail_cut
TGT_T=TGT&TAIL[None,:]; n_t=TGT_T.sum(1); keep=n_t>=1
def eval_tail(S, restrict_to_tail):
    S=np.where(MASK,S,-np.inf)
    if restrict_to_tail: S=np.where(TAIL[None,:],S,-np.inf)
    top=np.argpartition(-S,KEVAL,axis=1)[:,:KEVAL]
    h=np.take_along_axis(TGT_T,top,1); r=np.zeros(n_users)
    r[keep]=h[keep].sum(1)/np.minimum(KEVAL,n_t[keep]); return r[keep].mean()

tr=pos[pos.userId.isin(train_users)].copy(); tr["occ"]=tr.userId.map(occ)
GP={}
for o,g in tr.groupby("occ"):
    v=np.zeros(n_items); np.add.at(v,g.movieId.map(i2x).values,1.0); GP[o]=v/max(g.userId.nunique(),1)
test_occ=np.array([occ[u] for u in uids])
S_grp=np.vstack([GP[o] for o in test_occ])
S_glob=np.tile(POP_COUNT,(n_users,1))

rows=[]
def rec(name,val): rows.append({"condition":name,"tail_recall_at20":val}); print(f"{name:44s}{val:11.4f}")

print("=== ML-1M, FAIR comparison: every condition restricted to tail items ===")
print(f"{'condition':44s}{'tail R@20':>11s}")
rec("global popularity (no disclosure)", eval_tail(S_glob,True))
rec("group context (no disclosure)",     eval_tail(S_grp,True))
for k in [1,3,5,8,13,21,34,55]:
    M=item_matrix(select(k,"random"))
    rec(f"individual disclosure, {k} items", eval_tail(M@B,True))
M=item_matrix([pool[u] for u in range(n_users)])
rec("full history", eval_tail(M@B,True))

print("\n=== for contrast, the UNFAIR comparison I ran before ===")
rec("UNFAIR: group context, tail-restricted", eval_tail(S_grp,True))
rec("UNFAIR: disclosure 8, NOT restricted",   eval_tail(item_matrix(select(8,'random'))@B,False))
pd.DataFrame(rows).to_csv("results/fair_ml1m.csv",index=False)
print("\nwrote results/fair_ml1m.csv")
