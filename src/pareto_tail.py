import pandas as pd, numpy as np
T=pd.read_csv('results/tail.csv'); S=pd.read_csv('results/summary.csv')
m=T.merge(S[['cond','k','pct_rank1','recall']],on=['cond','k'],how='left')
m=m[~m.cond.isin(['popularity','full'])].dropna(subset=['pct_rank1'])
m['priv']=1-m.pct_rank1
pts=m[['recall_x' if 'recall_x' in m else 'tail_recall','priv']].values if False else m[['tail_recall','priv']].values
dom=[not any((r2>=r and p2>=p and (r2>r or p2>p)) for r2,p2 in pts) for r,p in pts]
m['pareto']=dom
print("=== PARETO FRONTIER on TAIL utility vs non-identification ===")
for _,r in m[m.pareto].sort_values('tail_recall').iterrows():
    print(f"  {r['cond']:12s} k={int(r.k):3d}  tail={r.tail_recall:.4f}  identified@1={r.pct_rank1:5.1%}  (headline rec={r.recall:.4f})")

print("\n=== TAIL UTILITY PER UNIT OF IDENTIFICATION ===")
print(f"{'cond':13s}{'k':>4s}{'tail':>9s}{'id@1':>8s}{'tail/id':>10s}")
for _,r in m.sort_values('tail_recall',ascending=False).head(14).iterrows():
    eff=r.tail_recall/max(r.pct_rank1,.001)
    print(f"{r['cond']:13s}{int(r.k):4d}{r.tail_recall:9.4f}{r.pct_rank1:8.1%}{eff:10.4f}")

print("\n=== THE KEY CONTRAST ===")
for c,k in [('raw-random',13),('raw-recency',13),('raw-popular',13),('attr',13),('attr-pop',55)]:
    r=m[(m.cond==c)&(m.k==k)].iloc[0]
    print(f"  {c:12s} k={k:3d}  headline={r.recall:.4f}  tail={r.tail_recall:.4f}  identified@1={r.pct_rank1:5.1%}")
m.to_csv('results/pareto_tail.csv',index=False)

print("\n=== RANK CORRELATION: does headline recall predict tail recall? ===")
from scipy.stats import spearmanr
rho,p=spearmanr(m.recall,m.tail_recall)
print(f"  Spearman rho = {rho:.3f}  (p={p:.3g})  n={len(m)}")
