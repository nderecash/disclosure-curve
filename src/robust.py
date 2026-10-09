"""GATE: multi-seed replication + bootstrap CIs + Pareto frontier."""
import subprocess, pandas as pd, numpy as np, json, re, os
SEEDS=[42,7,2024]
frames=[]
for s in SEEDS:
    src=open('src/experiment.py').read().replace('SEED = 42',f'SEED = {s}')
    src=src.replace('/results/sweep.csv',f'/results/sweep_{s}.csv').replace('{OUT}/sweep.csv',f'{{OUT}}/sweep_{s}.csv')
    open(f'src/_run_{s}.py','w').write(src)
    r=subprocess.run(['python3','-I',f'src/_run_{s}.py'],capture_output=True,text=True,timeout=600)
    if r.returncode!=0: print(f"seed {s} FAILED"); print(r.stderr[-1500:]); continue
    d=pd.read_csv(f'results/sweep_{s}.csv'); d['seed']=s; frames.append(d)
    print(f"seed {s} ok, {len(d)} rows")
df=pd.concat(frames); df.to_csv('results/sweep_allseeds.csv',index=False)

rng=np.random.default_rng(0)
def boot(v,n=2000):
    v=np.asarray(v); idx=rng.integers(0,len(v),(n,len(v)))
    m=v[idx].mean(1); return v.mean(), np.percentile(m,2.5), np.percentile(m,97.5)

rows=[]
for (c,k),g in df.groupby(['cond','k']):
    m,lo,hi=boot(g.recall.values)
    rows.append(dict(cond=c,k=k,recall=m,lo=lo,hi=hi,
                     ndcg=g.ndcg.mean(),
                     rank_med=g['rank'].median(),
                     rank_q1=g['rank'].quantile(.25),
                     rank_q3=g['rank'].quantile(.75),
                     pct_rank1=(g['rank']==1).mean(),
                     n=len(g)))
S=pd.DataFrame(rows).sort_values(['cond','k'])
S.to_csv('results/summary.csv',index=False)

# cross-seed stability of the headline comparisons
print("\n=== CROSS-SEED STABILITY (Recall@20) ===")
for c in ['raw-random','raw-recency','raw-popular','attr']:
    sub=df[(df.cond==c)&(df.k==13)].groupby('seed').recall.mean()
    print(f"  {c:14s} k=13: " + "  ".join(f"{s}={v:.4f}" for s,v in sub.items()))

pop=df[df.cond=='popularity'].recall.mean()
full=df[df.cond=='full'].recall.mean()
print(f"\npopularity floor = {pop:.4f}   full history ceiling = {full:.4f}")

print("\n=== SUMMARY (recall [95% CI], median re-id rank, %% identified at rank 1) ===")
for c in S.cond.unique():
    print(f"\n{c}")
    for _,r in S[S.cond==c].iterrows():
        print(f"   k={int(r.k):3d}  rec={r.recall:.4f} [{r.lo:.4f},{r.hi:.4f}]  "
              f"ndcg={r.ndcg:.4f}  rank med={r.rank_med:6.1f} (IQR {r.rank_q1:.0f}-{r.rank_q3:.0f})  "
              f"rank1={r.pct_rank1:.1%}")
