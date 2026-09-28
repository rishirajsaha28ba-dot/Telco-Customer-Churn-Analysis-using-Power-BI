import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
df=pd.read_pickle('clean.pkl')
BG='#fcfcfb'; T1='#0b0b0b'; T2='#52514e'; T3='#8a8983'; GRID='#e6e5e0'
BLUE='#2a78d6'; RED='#e34948'; GRAY='#c3c2b7'; NAVY='#0d366b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':T1,'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'axes.edgecolor':GRID})
def M(v):
    sg='−' if v<0 else ''; v=abs(v)
    return sg+(f'${v/1e6:.2f}M' if v>=1e6 else f'${v/1e3:,.0f}K')
def style(ax,title,sub=None):
    ax.set_facecolor(BG)
    for s in ['top','right','left']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(GRID)
    ax.tick_params(length=0)
    ax.set_title(title,loc='left',fontsize=14,fontweight='bold',color=T1,pad=24 if sub else 10)
    if sub: ax.text(0,1.02,sub,transform=ax.transAxes,fontsize=10.5,color=T2,va='bottom')
def g(k):
    t=df.groupby(k).agg(Sales=('Sales','sum'),Profit=('Profit','sum'),Ship=('Shipping Cost','sum'),Disc=('Discount','mean'),Loss=('Loss-Making Flag','mean'),Days=('Ship Days','mean'))
    t['Margin']=t.Profit/t.Sales; t['ShipPct']=t.Ship/t.Sales; return t

fig=plt.figure(figsize=(24,13.5),dpi=100,facecolor=BG)
# header
fig.text(0.025,0.955,'Global Superstore — Profitability Diagnostic Dashboard',fontsize=28,fontweight='bold',color=T1)
fig.text(0.025,0.925,'Where is profit leaking?  51,290 cleaned order lines · 147 countries · Jan 2011 – Dec 2014 · all values USD',fontsize=13,color=T2)
# KPI tiles
S,P=df.Sales.sum(),df.Profit.sum()
kpis=[('Total Sales',M(S),'+90% 2011→2014'),('Total Profit',M(P),'margin flat 11.0%→11.7%'),('Profit Margin',f'{P/S:.1%}','profit ÷ sales'),
      ('Orders',f"{df['Order ID'].nunique():,}",f"AOV ${S/df['Order ID'].nunique():,.0f}"),('Loss-Making Lines',f"{df['Loss-Making Flag'].mean():.1%}",'of 51,290 lines'),
      ('Shipping Cost',f"{df['Shipping Cost'].sum()/S:.1%}",'of sales ('+M(df['Shipping Cost'].sum())+')'),('Profit lost at >20% discount',M(df[df.Discount>0.2].Profit.sum()),'92% of all line losses')]
w=0.95/len(kpis)
for i,(a,b,c) in enumerate(kpis):
    x=0.025+i*w
    ax=fig.add_axes([x,0.80,w-0.008,0.10]); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle='round,pad=0,rounding_size=0.06',transform=ax.transAxes,fc='white',ec=GRID,lw=1.2))
    hi = i==6
    ax.text(0.07,0.76,a,fontsize=11.5,color=T2,transform=ax.transAxes)
    ax.text(0.07,0.36,b,fontsize=26,fontweight='bold',color=RED if hi else T1,transform=ax.transAxes)
    ax.text(0.07,0.10,c,fontsize=10,color=T3,transform=ax.transAxes)

# 1 Sales & margin by year
ax=fig.add_axes([0.035,0.44,0.20,0.29]); y=g('Order Year')
b=ax.bar(y.index.astype(str),y.Sales/1e6,color=BLUE,width=0.6)
for r,(s,m) in zip(b,zip(y.Sales,y.Margin)):
    ax.text(r.get_x()+r.get_width()/2,r.get_height()+0.06,f'${s/1e6:.2f}M',ha='center',fontsize=10.5,fontweight='bold')
    ax.text(r.get_x()+r.get_width()/2,r.get_height()/2,f'margin\n{m:.1%}',ha='center',va='center',fontsize=10,color='white')
ax.set_ylim(0,5); ax.set_yticks([]); style(ax,'Sales grew 90%, margin did not','Sales by order year ($M), margin inside bar')

# 2 Discount band
ax=fig.add_axes([0.29,0.44,0.20,0.29]); d=g('Discount Band').reindex(['No Discount','Low','Medium','High','Very High'])
lab=['0%','0–20%','20–40%','40–60%','60%+']
cols=[BLUE if v>=0 else RED for v in d.Profit]
b=ax.bar(lab,d.Profit/1e3,color=cols,width=0.6); ax.axhline(0,color=T3,lw=1)
for r,(p,l) in zip(b,zip(d.Profit,d.Loss)):
    yy=r.get_height(); ax.text(r.get_x()+r.get_width()/2,yy+(40 if p>=0 else -40),f'{M(p)}\n{l:.0%} loss',ha='center',va='bottom' if p>=0 else 'top',fontsize=9.5)
ax.set_ylim(-650,2150); ax.set_yticks([]); ax.set_xlabel('Discount band')
style(ax,'Deep discounts destroy profit','Profit ($K) & share of loss-making lines')

# 3 Sub-category profit
ax=fig.add_axes([0.575,0.44,0.16,0.29]); s=g('Sub-Category').sort_values('Profit')
ax.barh(s.index,s.Profit/1e3,color=[RED if v<0 else BLUE for v in s.Profit],height=0.65); ax.axvline(0,color=T3,lw=1)
for i,(p,m) in enumerate(zip(s.Profit,s.Margin)):
    ax.text(p/1e3+(4 if p>=0 else -4),i,f'{M(p)} · {m:.0%}',va='center',ha='left' if p>=0 else 'right',fontsize=8.8,color=T2)
ax.set_xlim(-190,370); ax.set_xticks([]); ax.tick_params(axis='y',labelsize=9.5)
style(ax,'Tables is the only loss sub-category','Profit & margin by sub-category')

# 4 Region margin
ax=fig.add_axes([0.83,0.44,0.15,0.29]); r=g(['Market','Region']).sort_values('Margin')
names=[f'{m} · {rg}' if m!=rg else m for m,rg in r.index]
avg=P/S
ax.barh(names,r.Margin*100,color=[RED if v<avg*0.75 else (GRAY if v<avg else BLUE) for v in r.Margin],height=0.65)
ax.axvline(avg*100,color=T1,lw=1,ls='--'); ax.text(avg*100+0.3,len(r)-0.2,'avg 11.6%',fontsize=9,color=T1)
for i,m in enumerate(r.Margin): ax.text(m*100+0.3,i,f'{m:.1%}',va='center',fontsize=8.8,color=T2)
ax.set_xlim(0,31); ax.set_xticks([]); ax.tick_params(axis='y',labelsize=9.5)
style(ax,'Weakest regions','Profit margin by market · region')

# 5 Ship mode
ax=fig.add_axes([0.035,0.07,0.20,0.28]); sm=g('Ship Mode').reindex(['Same Day','First Class','Second Class','Standard Class'])
b=ax.bar(['Same Day','First','Second','Standard'],sm.ShipPct*100,color=BLUE,width=0.6)
for r_,(sp,m,dd) in zip(b,zip(sm.ShipPct,sm.Margin,sm.Days)):
    ax.text(r_.get_x()+r_.get_width()/2,r_.get_height()+0.4,f'{sp:.1%}',ha='center',fontsize=10.5,fontweight='bold')
    ax.text(r_.get_x()+r_.get_width()/2,1.0,f'{dd:.1f} days\nmargin\n{m:.1%}',ha='center',fontsize=9,color='white')
ax.set_ylim(0,21); ax.set_yticks([])
style(ax,'Shipping cost is priced in','Shipping cost as % of sales by ship mode')

# 6 Category: sales vs profit
ax=fig.add_axes([0.29,0.07,0.20,0.28]); c=g('Category').reindex(['Technology','Office Supplies','Furniture'])
x=np.arange(3); ax.bar(x-0.19,c.Sales/1e6,0.36,color=GRAY,label='Sales ($M)'); ax.bar(x+0.19,c.Profit/1e6,0.36,color=BLUE,label='Profit ($M)')
for i,(s_,p_,m_) in enumerate(zip(c.Sales,c.Profit,c.Margin)):
    ax.text(i-0.19,s_/1e6+0.08,f'{s_/1e6:.2f}',ha='center',fontsize=9.5); ax.text(i+0.19,p_/1e6+0.08,f'{p_/1e6:.2f}',ha='center',fontsize=9.5)
    ax.text(i,-0.62,f'margin {m_:.1%}',ha='center',fontsize=10,fontweight='bold',color=RED if m_<0.1 else T1)
ax.set_xticks(x,c.index); ax.set_ylim(0,5.4); ax.set_yticks([]); ax.legend(frameon=False,loc='upper right',fontsize=9.5)
style(ax,'Furniture sells, but earns least','Sales vs profit by category ($M)')

# 7 Top loss countries
ax=fig.add_axes([0.565,0.07,0.15,0.28]); ct=g('Country').sort_values('Profit').head(8)[::-1]
ax.barh(ct.index,ct.Profit/1e3,color=RED,height=0.65)
for i,(p,m) in enumerate(zip(ct.Profit,ct.Margin)): ax.text(p/1e3-2,i,f'{M(p)} · {m:.0%}',va='center',ha='right',fontsize=8.8,color=T2)
ax.set_xlim(-165,0); ax.set_xticks([]); ax.yaxis.tick_right(); ax.tick_params(axis='y',labelsize=9.5)
style(ax,'29 countries lose money','Top 8 loss countries (profit, margin) — total −$448K')

# 8 Leak ranking panel
ax=fig.add_axes([0.765,0.05,0.215,0.31]); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle='round,pad=0,rounding_size=0.03',transform=ax.transAxes,fc='#f3f2ee',ec=GRID))
ax.text(0.05,0.92,'Ranked profit leaks',fontsize=14,fontweight='bold',transform=ax.transAxes)
items=[('1','Discounts >20%','−$814K · 90% of lines lose money'),
       ('2','29 loss-making countries','−$448K (Turkey, Nigeria, Netherlands)'),
       ('3','Tables sub-category','−$64K · 29% avg discount, −8.5% margin'),
       ('4','SE Asia / EMEA / LATAM South','2.0% / 5.4% / 4.6% margin'),
       ('5','Shipping mode','Not a leak: margin 11.4–11.8% for all')]
for i,(n,a,b_) in enumerate(items):
    yy=0.78-i*0.155
    ax.text(0.05,yy,n,fontsize=16,fontweight='bold',color=RED if i<4 else T3,transform=ax.transAxes,va='center')
    ax.text(0.13,yy+0.03,a,fontsize=11.5,fontweight='bold',transform=ax.transAxes,va='center')
    ax.text(0.13,yy-0.035,b_,fontsize=10,color=T2,transform=ax.transAxes,va='center')
fig.text(0.025,0.012,'Source: GlobalSuperstoreData_Final.xlsx, cleaned (see Cleaning Log). Red = loss / below 75% of avg margin; blue = profit.',fontsize=9.5,color=T3)
fig.savefig('dashboard.png',facecolor=BG); fig.savefig('dashboard.pdf',facecolor=BG)
