import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd
matplotlib.rcParams["svg.fonttype"]="path"
plt.rcParams.update({"font.size":21,"font.family":"DejaVu Sans",
    "axes.spines.top":False,"axes.spines.right":False,"axes.linewidth":1.6,
    "xtick.major.width":1.6,"ytick.major.width":1.6,"xtick.labelsize":19,"ytick.labelsize":19})
INK="#15202b"; MUT="#5d6b7a"
S=pd.read_csv('results/summary.csv'); T=pd.read_csv('results/tail.csv')
m=T.merge(S[['cond','k','pct_rank1','recall']],on=['cond','k'],how='left')
POP=S[S.cond=='popularity'].recall.iloc[0]; FULL=S[S.cond=='full'].recall.iloc[0]
POPT=T[T.cond=='popularity'].tail_recall.iloc[0]; FULLT=T[T.cond=='full'].tail_recall.iloc[0]
C={'raw-random':'#2f6f9f','raw-recency':'#d4722a','raw-popular':'#b0353a','attr':'#3f8f73'}
L={'raw-random':'Random items','raw-recency':'Most recent','raw-popular':'Most popular','attr':'Attribute description'}

# ---------- FIG 1: the inversion. Reference labels live in a right margin, clear of all data.
fig,ax=plt.subplots(1,2,figsize=(17.5,6.7))
XMAX=142
for a,col,floor,ceil,ttl,yl in [
  (ax[0],'recall',POP,FULL,'Standard Recall@20','Recall@20'),
  (ax[1],'tail_recall',POPT,FULLT,'Recall@20, uncommon items only','Recall@20 (uncommon items)')]:
    for c in C:
        g=m[m.cond==c].sort_values('k')
        a.plot(g.pct_rank1*100,g[col],'o-',color=C[c],lw=3.4,ms=9,label=L[c])
    a.set_xlim(-4,XMAX); a.set_xticks([0,20,40,60,80,100])
    a.axhline(ceil,ls='--',c=INK,lw=2,xmax=(104+4)/(XMAX+4))
    a.axhline(floor,ls=':',c=MUT,lw=2,xmax=(104+4)/(XMAX+4))
    a.text(108,ceil,'full history',fontsize=18,va='center',ha='left',color=INK)
    a.text(108,floor,'popularity\ndefault',fontsize=18,va='center',ha='left',color=MUT,linespacing=1.25)
    a.set_xlabel('% of people identified at rank 1',fontsize=21)
    a.set_ylabel(yl,fontsize=21); a.set_title(ttl,fontsize=24,loc='left',pad=14,color=INK,fontweight='bold')
ax[1].set_ylim(-0.0055,0.0445)
ax[1].annotate('0.0000',xy=(37,0.0),xytext=(30,0.0095),fontsize=21,color='#b0353a',
    fontweight='bold',ha='center',arrowprops=dict(arrowstyle='->',color='#b0353a',lw=2.4))
# legend in the empty upper-left pocket, above the red curve
ax[0].legend(frameon=False,fontsize=18,loc='upper left',bbox_to_anchor=(0.02,0.86),
             handlelength=1.6,labelspacing=.45)
fig.tight_layout()
fig.savefig('figures/p1.svg',facecolor='white'); fig.savefig('figures/chk1.png',dpi=110,facecolor='white')

# ---------- FIG 2: fair comparison + identification cost
k=[1,3,5,8,13,21,34,55]; d=[.0581,.0682,.0854,.0954,.1064,.1319,.1505,.1775]
idm=[3.2,45.8,72.9,90.3,98.0,99.8,100,100]
fk=[1,2,3,5,8,13]; fid=[17.2,62.1,72.4,87.4,94.3,97.7]
fig,ax=plt.subplots(1,2,figsize=(17.5,6.7))
XHI=190
for a in ax:
    a.set_xscale('log',base=2); a.set_xlim(.85,XHI); a.set_xticks(k); a.set_xticklabels(k)
    a.set_xlabel('items disclosed',fontsize=21)
xm=np.log2(62/.85)/np.log2(XHI/.85)
ax[0].plot(k,d,'o-',c='#2f6f9f',lw=3.6,ms=10)
ax[0].axhline(.0476,c='#3f8f73',lw=3.4,xmax=xm); ax[0].axhline(.0408,ls=':',c=MUT,lw=2.4,xmax=xm)
ax[0].axhline(.2319,ls='--',c=INK,lw=2,xmax=xm)
ax[0].set_ylim(.030,.247)
ax[0].text(66,.0540,'context only',fontsize=18,va='bottom',ha='left',color='#3f8f73')
ax[0].text(66,.0345,'popularity default',fontsize=18,va='top',ha='left',color=MUT)
ax[0].text(66,.2319,'full history',fontsize=18,va='center',ha='left',color=INK)
ax[0].set_ylabel('Recall@20 (uncommon items)',fontsize=21)
ax[0].set_title('One item beats all the context',fontsize=24,loc='left',pad=14,color=INK,fontweight='bold')
ax[1].plot(k,idm,'o-',c='#b0353a',lw=3.6,ms=10,label='MovieLens, films')
ax[1].plot(fk,fid,'s-',c='#d4722a',lw=3.6,ms=10,label='Frappe, phone apps')
ax[1].axhline(3,ls=':',c='#3f8f73',lw=3,xmax=xm)
ax[1].set_ylim(-5,108)
ax[1].text(66,3,'context membership:\n3% or less',fontsize=18,va='center',ha='left',color='#3f8f73',linespacing=1.25)
ax[1].set_ylabel('% identified at rank 1',fontsize=21)
ax[1].set_title('What disclosure costs',fontsize=24,loc='left',pad=14,color=INK,fontweight='bold')
ax[1].legend(frameon=False,fontsize=19,loc='lower right',bbox_to_anchor=(1.0,0.12),
             handlelength=1.6,labelspacing=.45)
fig.tight_layout()
fig.savefig('figures/p2.svg',facecolor='white'); fig.savefig('figures/chk2.png',dpi=110,facecolor='white')

# ---------- FIG 3: context variables
fig,ax=plt.subplots(figsize=(10.2,4.3))
v=['home / work','weekend?','weekday','time of day','weather']; g=[-2.3,10.9,15.3,36.0,64.7]
ax.barh(v,g,color=['#b0353a' if x<0 else '#3f8f73' for x in g],height=.62)
ax.axvline(0,c=INK,lw=1.8)
ax.set_xlabel('% gain over the popularity default',fontsize=20)
ax.set_title('Which cue you pick matters more\nthan whether you have one',fontsize=21,loc='left',pad=10,color=INK,fontweight='bold')
fig.tight_layout()
fig.savefig('figures/p3.svg',facecolor='white'); fig.savefig('figures/chk3.png',dpi=110,facecolor='white')
print("figs ok")
