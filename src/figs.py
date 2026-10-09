import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":9,"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False})
S=pd.read_csv('results/summary.csv'); T=pd.read_csv('results/tail.csv')
m=T.merge(S[['cond','k','pct_rank1','recall','lo','hi']],on=['cond','k'],how='left')
POP=S[S.cond=='popularity'].recall.iloc[0]; FULL=S[S.cond=='full'].recall.iloc[0]
POPT=T[T.cond=='popularity'].tail_recall.iloc[0]; FULLT=T[T.cond=='full'].tail_recall.iloc[0]
C={'raw-random':'#4C72B0','raw-recency':'#DD8452','raw-popular':'#C44E52','attr':'#55A868','attr-pop':'#8172B3'}
L={'raw-random':'Random items','raw-recency':'Most recent items','raw-popular':'Most popular items','attr':'Attribute description','attr-pop':'Attribute description (popular source)'}

# FIG 1+2 side by side: the inversion
fig,axes=plt.subplots(1,2,figsize=(10,4.1))
for ax,ycol,floor,ceil,title,ylab in [
  (axes[0],'recall',POP,FULL,'(a) Standard Recall@20','Recall@20'),
  (axes[1],'tail_recall',POPT,FULLT,'(b) Recall@20 on long-tail targets','Recall@20, tail items only')]:
    for c in C:
        g=m[m.cond==c].sort_values('k')
        ax.plot(g.pct_rank1*100,g[ycol],'o-',color=C[c],ms=4,lw=1.6,label=L[c])
        for _,r in g.iterrows():
            if int(r.k) in (1,13,55):
                ax.annotate(f"{int(r.k)}",(r.pct_rank1*100,r[ycol]),fontsize=7,
                            xytext=(3,3),textcoords='offset points',color=C[c])
    ax.axhline(ceil,ls='--',c='k',lw=.9); ax.axhline(floor,ls=':',c='grey',lw=.9)
    ax.text(1,ceil,' full history',fontsize=7,va='bottom')
    ax.text(1,floor,' popularity baseline',fontsize=7,va='bottom',color='grey')
    ax.set_xlabel('% of users identified at rank 1'); ax.set_ylabel(ylab); ax.set_title(title,fontsize=10,loc='left')
axes[0].legend(frameon=False,fontsize=7.5,loc='lower right')
fig.tight_layout(); fig.savefig('figures/fig1_inversion.pdf'); fig.savefig('figures/fig1_inversion.png',dpi=160)

# FIG 3: headline vs tail scatter
from scipy.stats import spearmanr
mm=m[~m.cond.isin(['popularity','full'])].dropna(subset=['pct_rank1'])
rho,p=spearmanr(mm.recall,mm.tail_recall)
fig,ax=plt.subplots(figsize=(4.6,3.8))
for c in C:
    g=mm[mm.cond==c]; ax.scatter(g.recall,g.tail_recall,color=C[c],s=26,label=L[c])
ax.set_xlabel('Standard Recall@20'); ax.set_ylabel('Recall@20, tail targets only')
ax.set_title(f'Spearman $\\rho$ = {rho:.3f} (p = {p:.3f}, n = {len(mm)})',fontsize=9,loc='left')
ax.legend(frameon=False,fontsize=7)
fig.tight_layout(); fig.savefig('figures/fig2_metric_disagreement.pdf'); fig.savefig('figures/fig2_metric_disagreement.png',dpi=160)
print("figures written; rho=",round(rho,3),"p=",round(p,4))
