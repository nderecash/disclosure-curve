"""
Frappe: the same protocol, but with REAL environmental context.
Context here is a property of the SITUATION (time of day), not of the person.
Evaluated per (user, context) cell: given that someone is in this context,
can the context's own app distribution predict what they use, with no
personal history at all?
"""
import numpy as np, pandas as pd, scipy.sparse as sp, time, json
SEED=42; RNG=np.random.default_rng(SEED); KEVAL=10
KS=[1,2,3,5,8,13]; MINPOOL=max(KS)
CTX='daytime'

f=pd.read_csv('data/frappe/Mobile_Frappe/frappe/frappe.csv', sep='\t')
f=f[['user','item',CTX]].drop_duplicates()
print(f"raw unique (user,item,ctx): {len(f)} | users {f.user.nunique()} | apps {f.item.nunique()}")

for _ in range(6):
    ic=f.item.value_counts(); f=f[f.item.isin(ic[ic>=10].index)]
    uc=f.groupby('user').item.nunique(); f=f[f.user.isin(uc[uc>=MINPOOL+3].index)]
print(f"after filter: {len(f)} rows | users {f.user.nunique()} | apps {f.item.nunique()}")

items=np.sort(f.item.unique()); i2x={m:i for i,m in enumerate(items)}; n_items=len(items)
ctxs=sorted(f[CTX].unique()); print(f"contexts: {ctxs}")

users=f.user.unique().copy(); RNG.shuffle(users)
n_te=int(0.35*len(users))
test_u=set(users[:n_te]); train_u=set(users[n_te:])
d=f[f.user.isin(train_u)].drop_duplicates(['user','item'])
X=sp.csr_matrix((np.ones(len(d)),(pd.Categorical(d.user).codes,d.item.map(i2x).values)),
                shape=(d.user.nunique(),n_items))
print(f"train {X.shape} nnz {X.nnz} | test users {len(test_u)}")

POP=np.asarray(X.sum(0)).ravel().astype(float)
tail_cut=np.quantile(POP,0.80); TAIL=POP<tail_cut
print(f"tail items: {TAIL.sum()}/{n_items} ({TAIL.mean():.0%})")

# context popularity from TRAINING users only
ftr=f[f.user.isin(train_u)]
CPOP={}
for c,g in ftr.groupby(CTX):
    v=np.zeros(n_items); np.add.at(v,g.item.map(i2x).values,1.0)
    CPOP[c]=v/max(g.user.nunique(),1)
print("context overlap with global top-10:", 
      {c: f"{len(set(np.argsort(-CPOP[c])[:10]) & set(np.argsort(-POP)[:10]))/10:.0%}" for c in ctxs})

def train_ease(Xm,lam=100.0):
    G=np.asarray((Xm.T@Xm).todense(),np.float64); di=np.diag_indices(G.shape[0]); G[di]+=lam
    P=np.linalg.inv(G); B=P/(-np.diag(P)); B[di]=0.0; return B
t=time.time(); B=train_ease(X); print(f"EASE {time.time()-t:.1f}s")

# per test user: pool/target split, targets keep their context
cells=[]; pools={}; fullp={}
for u,g in f[f.user.isin(test_u)].groupby('user'):
    gi=g.drop_duplicates('item')
    idx=gi.item.map(i2x).values; ctx=gi[CTX].values
    if len(idx)<MINPOOL+3: continue
    nt=max(1,int(round(0.25*len(idx)))); perm=RNG.permutation(len(idx)); ts=set(perm[:nt])
    pool=np.array([idx[j] for j in range(len(idx)) if j not in ts])
    if len(pool)<MINPOOL: continue
    pools[u]=pool; fullp[u]=idx
    tg={}
    for j in sorted(ts): tg.setdefault(ctx[j],[]).append(idx[j])
    for c,its in tg.items(): cells.append((u,c,np.array(its)))
uids=sorted(pools); n_users=len(uids); u2r={u:i for i,u in enumerate(uids)}
print(f"cohort: {n_users} users, {len(cells)} (user,context) cells")

def rec_at_k(scores, pool, tgt, restrict=None):
    s=scores.copy(); s[pool]=-np.inf
    if restrict is not None: s[~restrict]=-np.inf
    top=np.argpartition(-s,KEVAL)[:KEVAL]
    return np.isin(top,tgt).sum()/min(KEVAL,len(tgt))

# identification: holding vs all full profiles
FULL=np.zeros((n_users,n_items))
for u in uids: FULL[u2r[u],fullp[u]]=1.0
FULLn=FULL/np.maximum(np.linalg.norm(FULL,axis=1,keepdims=True),1e-9)
def ident(H):
    Hn=H/np.maximum(np.linalg.norm(H,axis=1,keepdims=True),1e-9)
    S=Hn@FULLn.T; tr=S[np.arange(n_users),np.arange(n_users)]
    return ((S>tr[:,None]).sum(1)+1)

rows=[]
def add(cond,k,recs,idrate):
    rows.append(dict(cond=cond,k=k,recall=float(np.mean(recs)),n_cells=len(recs),ident=idrate))

# --- zero-disclosure conditions, evaluated per cell
for name,getv,restr in [("global popularity",lambda c:POP,None),
                        ("global popularity, tail only",lambda c:POP,TAIL),
                        ("context popularity",lambda c:CPOP[c],None),
                        ("context popularity, tail only",lambda c:CPOP[c],TAIL)]:
    r=[rec_at_k(getv(c),pools[u],t_,restr) for u,c,t_ in cells]
    add(name,0,r,0.0)

# --- shuffled context control
sh={c:CPOP[RNG.permutation(ctxs)[0]] for c in ctxs}
accs=[]
for _ in range(20):
    perm=list(RNG.permutation(ctxs)); mp=dict(zip(ctxs,perm))
    accs.append(np.mean([rec_at_k(CPOP[mp[c]],pools[u],t_,TAIL) for u,c,t_ in cells]))
add("shuffled context, tail only",0,accs,0.0)

# --- individual disclosure
for k in KS:
    H=np.zeros((n_users,n_items)); sel={}
    for u in uids:
        s=RNG.choice(pools[u],min(k,len(pools[u])),replace=False); sel[u]=s
        H[u2r[u],s]=1.0
    S=H@B
    r=[rec_at_k(S[u2r[u]],pools[u],t_,None) for u,c,t_ in cells]
    rt=[rec_at_k(S[u2r[u]],pools[u],t_,TAIL) for u,c,t_ in cells]
    idr=float((ident(H)==1).mean())
    add(f"individual disclosure ({k} apps)",k,r,idr)
    add(f"individual disclosure ({k} apps), tail only",k,rt,idr)

R=pd.DataFrame(rows); R.to_csv('results/frappe.csv',index=False)
print("\n=== FRAPPE: Recall@10 ===")
for _,x in R.iterrows():
    print(f"  {x['cond']:46s} recall={x.recall:.4f}  identified@1={x.ident:.1%}")
