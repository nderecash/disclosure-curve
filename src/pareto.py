import pandas as pd, numpy as np
S=pd.read_csv('results/summary.csv')
df=pd.read_csv('results/sweep_allseeds.csv')
POP=df[df.cond=='popularity'].recall.mean(); FULL=df[df.cond=='full'].recall.mean()

sel=S[~S.cond.isin(['popularity','full','attr-shuffled-control'])].copy()
sel['priv']=1-sel.pct_rank1          # fraction NOT identified at rank 1

# Pareto frontier: maximise recall and priv jointly
pts=sel[['cond','k','recall','priv','pct_rank1']].values
dom=[]
for i,(c,k,r,p,_) in enumerate(pts):
    strictly=any((rr>=r and pp>=p and (rr>r or pp>p)) for _,_,rr,pp,_ in pts)
    dom.append(not strictly)
sel['pareto']=dom
print("=== PARETO FRONTIER (utility vs non-identification) ===")
f=sel[sel.pareto].sort_values('recall')
for _,r in f.iterrows():
    print(f"  {r['cond']:14s} k={int(r.k):3d}  recall={r.recall:.4f}  identified@1={r.pct_rank1:5.1%}")

print(f"\npopularity floor {POP:.4f} | full ceiling {FULL:.4f}")

print("\n=== HEAD TO HEAD at matched identification risk ===")
for tgt in [0.2,0.4,0.6,0.9]:
    print(f"\n  ~{tgt:.0%} of users identified at rank 1:")
    for c in ['raw-random','raw-recency','raw-popular','attr','attr-pop']:
        g=sel[sel.cond==c]
        if len(g)==0: continue
        i=(g.pct_rank1-tgt).abs().idxmin()
        r=sel.loc[i]
        print(f"     {c:12s} k={int(r.k):3d}  recall={r.recall:.4f}  (actual {r.pct_rank1:.1%})")

print("\n=== DOES POPULAR SELECTION DOMINATE RANDOM? ===")
for k in [1,2,3,5,8,13,21,34,55]:
    a=sel[(sel.cond=='raw-popular')&(sel.k==k)].iloc[0]
    b=sel[(sel.cond=='raw-random')&(sel.k==k)].iloc[0]
    dr=a.recall-b.recall; dp=b.pct_rank1-a.pct_rank1
    verdict="DOMINATES" if dr>0 and dp>0 else "no"
    print(f"  k={k:3d}  Δrecall={dr:+.4f}  Δidentified={-dp:+.1%}  {verdict}")

print("\n=== TRANSLATION vs POPULARITY FLOOR ===")
for c in ['attr','attr-pop','attr-oblique']:
    best=sel[sel.cond==c].recall.max()
    print(f"  {c:14s} best recall {best:.4f}  -> {'ABOVE' if best>POP else 'BELOW'} floor ({POP:.4f})")

ctrl=S[S.cond=='attr-shuffled-control']
a=S[S.cond=='attr']
print("\n=== TRANSLATION SIGNAL ABOVE SHUFFLED CONTROL ===")
for k in [1,5,13,55]:
    x=a[a.k==k].recall.iloc[0]; y=ctrl[ctrl.k==k].recall.iloc[0]
    print(f"  k={k:3d}  attr={x:.4f}  control={y:.4f}  gap={x-y:+.4f}")
sel.to_csv('results/pareto.csv',index=False)
