import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":9,"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False})
fig,ax=plt.subplots(1,3,figsize=(12.5,3.9))

# --- panel a: ML-1M fair comparison
k=[1,3,5,8,13,21,34,55]; d=[.0581,.0682,.0854,.0954,.1064,.1319,.1505,.1775]
ident=[3.2,45.8,72.9,90.3,98.0,99.8,100,100]
ax[0].plot(k,d,'o-',c='#4C72B0',lw=2,ms=5,label='personal disclosure')
ax[0].axhline(.0476,ls='-',c='#55A868',lw=2); ax[0].axhline(.0408,ls=':',c='grey',lw=1.6)
ax[0].axhline(.2319,ls='--',c='k',lw=1.2)
ax[0].text(1.05,.0490,'group context, no disclosure',fontsize=7.5,c='#55A868')
ax[0].text(1.05,.0345,'popularity default, no disclosure',fontsize=7.5,c='grey')
ax[0].text(1.05,.2360,'full history',fontsize=7.5)
ax[0].set_xscale('log',base=2); ax[0].set_xticks(k); ax[0].set_xticklabels(k)
ax[0].set_xlabel('items disclosed'); ax[0].set_ylabel('long-tail Recall@20')
ax[0].set_title('(a) MovieLens 1M, fair comparison',fontsize=9.5,loc='left')

# --- panel b: identification cost
ax[1].plot(k,ident,'o-',c='#C44E52',lw=2,ms=5,label='MovieLens (films)')
fk=[1,2,3,5,8,13]; fid=[17.2,62.1,72.4,87.4,94.3,97.7]
ax[1].plot(fk,fid,'s-',c='#DD8452',lw=2,ms=5,label='Frappe (apps)')
ax[1].axhline(3.0,ls=':',c='#55A868',lw=1.8)
ax[1].text(1.05,5,'context: ~3% or less',fontsize=7.5,c='#55A868')
ax[1].set_xscale('log',base=2); ax[1].set_xticks(k); ax[1].set_xticklabels(k)
ax[1].set_xlabel('items disclosed'); ax[1].set_ylabel('% of users identified at rank 1')
ax[1].set_title('(b) what disclosure costs',fontsize=9.5,loc='left'); ax[1].legend(frameon=False,fontsize=7.5)

# --- panel c: which context variable
v=['home/work','weekend?','weekday','time of day','weather']
g=[-2.3,10.9,15.3,36.0,64.7]
cols=['#C44E52' if x<0 else '#55A868' for x in g]
ax[2].barh(v,g,color=cols); ax[2].axvline(0,c='k',lw=.8)
ax[2].set_xlabel('% gain over popularity default (tail)')
ax[2].set_title('(c) context variables are not equal (Frappe)',fontsize=9.5,loc='left')
fig.tight_layout(); fig.savefig('figures/guide.png',dpi=160); fig.savefig('figures/guide.pdf')
print("ok")
