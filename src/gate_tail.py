"""GATE: is raw-popular's advantage a popularity-bias artefact?
Re-score every condition on TAIL targets only (items outside the top 20% by
training popularity). If the advantage vanishes, the headline is an artefact."""
import numpy as np, pandas as pd, scipy.sparse as sp, time, os
exec(open('src/experiment.py').read().split('# ---------------------------------------------------------------- sweep')[0])

tail_cut = np.quantile(POP_COUNT, 0.80)
TAIL = POP_COUNT < tail_cut
print(f"\ntail items: {TAIL.sum()}/{n_items} ({TAIL.mean():.1%}) below {tail_cut:.0f} training interactions")

TGT_T = TGT & TAIL[None, :]
n_t = TGT_T.sum(1)
keep = n_t >= 1
print(f"users with >=1 tail target: {keep.sum()}/{n_users}")

def eval_tail(S):
    S = np.where(MASK, S, -np.inf)
    top = np.argpartition(-S, KEVAL, axis=1)[:, :KEVAL]
    hits = np.take_along_axis(TGT_T, top, 1)
    rec = np.zeros(n_users)
    rec[keep] = hits[keep].sum(1) / np.minimum(KEVAL, n_t[keep])
    return rec[keep]

out=[]
rec = eval_tail(np.tile(POP_COUNT,(n_users,1))); out.append(("popularity",0,rec.mean()))
M = item_matrix([pool[u] for u in range(n_users)])
out.append(("full",-1,eval_tail(M@B).mean()))

for k in KS:
    for cond in ["random","recency","popular"]:
        M = item_matrix(select(k,cond))
        out.append((f"raw-{cond}",k,eval_tail(M@B).mean()))
    for src,tag in [("random","attr"),("popular","attr-pop")]:
        sels=select(k,src); Pf=translate(sels,ATTR_FULL)
        sim=Pf@An_FULL.T
        ex=np.argpartition(-sim,M_EXP,axis=1)[:,:M_EXP]
        E=np.zeros((n_users,n_items)); np.put_along_axis(E,ex,1.0,axis=1)
        out.append((tag,k,eval_tail(E@B).mean()))

T=pd.DataFrame(out,columns=["cond","k","tail_recall"])
T.to_csv('results/tail.csv',index=False)
piv=T.pivot(index="k",columns="cond",values="tail_recall")
print("\n=== TAIL-ONLY Recall@20 (targets outside top 20% popularity) ===")
print(piv.round(4).to_string())
pf=T[(T.cond=='popularity')].tail_recall.iloc[0]
print(f"\npopularity floor on tail = {pf:.4f}")
print("\n=== popular vs random on TAIL targets ===")
for k in KS:
    a=T[(T.cond=='raw-popular')&(T.k==k)].tail_recall.iloc[0]
    b=T[(T.cond=='raw-random')&(T.k==k)].tail_recall.iloc[0]
    print(f"  k={k:3d}  popular={a:.4f}  random={b:.4f}  diff={a-b:+.4f}  {'popular wins' if a>b else 'RANDOM WINS'}")
