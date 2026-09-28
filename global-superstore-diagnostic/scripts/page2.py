import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, textwrap, pandas as pd
from matplotlib.patches import FancyBboxPatch
from content import *
plt.rcParams['text.parse_math']=False
BG='#fcfcfb'; T1='#0b0b0b'; T2='#52514e'; T3='#8a8983'; GRID='#e6e5e0'; BLUE='#2a78d6'; RED='#e34948'
fig=plt.figure(figsize=(24,13.5),dpi=100,facecolor=BG)
fig.text(0.025,0.955,'Answer Sheet — Key Business Questions & Recommendations',fontsize=28,fontweight='bold')
fig.text(0.025,0.925,'Global Superstore profitability diagnostic · method stated under each answer',fontsize=13,color=T2)
ax=fig.add_axes([0.025,0.815,0.95,0.085]); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle='round,pad=0,rounding_size=0.08',transform=ax.transAxes,fc='#eaf2fc',ec='#b7d3f6'))
ax.text(0.012,0.78,'EXECUTIVE SUMMARY (CFO)',fontsize=11,fontweight='bold',color='#184f95',transform=ax.transAxes)
ax.text(0.012,0.40,textwrap.fill(SUMMARY,215),fontsize=12,va='center',transform=ax.transAxes,linespacing=1.4)
# QA grid 2 cols x 4 rows
for i,(sec,q,a,m) in enumerate(QA):
    col=i%2; row=i//2
    x=0.025+col*0.3; y=0.60-row*0.19
    ax=fig.add_axes([x,y,0.29,0.175]); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle='round,pad=0,rounding_size=0.04',transform=ax.transAxes,fc='white',ec=GRID))
    ax.text(0.03,0.88,f'Q{i+1} · {sec.upper()}',fontsize=9.5,fontweight='bold',color=BLUE,transform=ax.transAxes)
    ax.text(0.03,0.76,textwrap.fill(q,70),fontsize=11,fontweight='bold',transform=ax.transAxes,va='top')
    ax.text(0.03,0.58,textwrap.fill(a,88),fontsize=9.6,transform=ax.transAxes,va='top',linespacing=1.3)
    ax.text(0.03,0.05,'Method: '+m,fontsize=8.6,color=T3,style='italic',transform=ax.transAxes)
# recs
ax=fig.add_axes([0.63,0.03,0.345,0.765]); ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0),1,1,boxstyle='round,pad=0,rounding_size=0.02',transform=ax.transAxes,fc='#f3f2ee',ec=GRID))
ax.text(0.04,0.955,'Recommendations — actionable within one quarter',fontsize=15,fontweight='bold',transform=ax.transAxes)
for i,(t,imp,why) in enumerate(RECS):
    y=0.87-i*0.155
    ax.text(0.04,y,t,fontsize=12.5,fontweight='bold',transform=ax.transAxes)
    ax.text(0.04,y-0.035,imp,fontsize=11.5,color=RED if i<3 else BLUE,fontweight='bold',transform=ax.transAxes)
    ax.text(0.04,y-0.065,textwrap.fill(why,78),fontsize=10,color=T2,transform=ax.transAxes,va='top')
log=pd.read_pickle('log.pkl')
ax.text(0.04,0.235,'Data cleaning applied (51,290 rows)',fontsize=12.5,fontweight='bold',transform=ax.transAxes)
lines=['Ship Date: 2 Excel serials → dates','Country: UK/US → United Kingdom/United States (149 → 147)','Product ID: 83 embedded spaces removed','Names: 273 double spaces collapsed','Quantity: 17 blanks imputed (Sales ÷ product unit price)','Discount: 16 blanks imputed (Country+Sub-Cat mode); 2 × 0.85 capped at 0.80','Verified: no duplicates, Order-ID year = order year, ship days 0–7']
for j,l in enumerate(lines): ax.text(0.05,0.195-j*0.026,'• '+l,fontsize=9.8,color=T2,transform=ax.transAxes)
fig.savefig('answers.png',facecolor=BG); fig.savefig('answers.pdf',facecolor=BG)
