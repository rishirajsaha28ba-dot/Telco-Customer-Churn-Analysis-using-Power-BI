import html, pandas as pd
from content import *
BASE='IMGBASE/'
df=pd.read_pickle('clean.pkl'); S,P=df.Sales.sum(),df.Profit.sum()
e=html.escape
kpis=[('Total Sales','$12.64M','+90% 2011→2014',0),('Total Profit','$1.47M','margin flat 11.0%→11.7%',0),('Profit Margin','11.6%','profit ÷ sales',0),('Orders','25,035','AOV $505',0),('Loss-Making Lines','24.5%','of 51,290 lines',0),('Shipping Cost','10.7%','of sales ($1.35M)',0),('Lost at >20% discount','−$814K','92% of all line losses',1)]
leaks=[('Discounts >20%','−$814K · 90% of lines lose money'),('29 loss-making countries','−$448K (Turkey, Nigeria, Netherlands)'),('Tables sub-category','−$64K · 29% avg discount, −8.5% margin'),('SE Asia / EMEA / LATAM South','2.0% / 5.4% / 4.6% margin'),('Shipping mode','Not a leak: margin 11.4–11.8% for all')]
css="""
body{margin:0;background:#e6e5e0;font-family:Inter,Arial,Helvetica,sans-serif;color:#0b0b0b}
section{width:1920px;height:1080px;background:#fcfcfb;position:relative;overflow:hidden;box-sizing:border-box;padding:36px 44px;margin:0 auto 20px}
h1{font-size:40px;margin:0 0 6px;font-weight:800}
.sub{font-size:18px;color:#52514e;margin:0 0 22px}
.kpis{display:flex;gap:14px;margin-bottom:22px}
.kpi{flex:1;background:#fff;border:1px solid #e6e5e0;border-radius:12px;padding:14px 18px}
.kpi .l{font-size:15px;color:#52514e}.kpi .v{font-size:36px;font-weight:800;margin:4px 0}.kpi .n{font-size:13px;color:#8a8983}
.red{color:#e34948}.blue{color:#2a78d6}
.row{display:flex;gap:18px;align-items:flex-start}
.row img{display:block}
.panel{background:#f3f2ee;border:1px solid #e6e5e0;border-radius:14px;padding:18px 22px;width:400px;box-sizing:border-box}
.panel h3{margin:0 0 10px;font-size:22px}
.leak{display:flex;gap:14px;margin:12px 0}.leak b{font-size:26px;width:22px}.leak .t{font-size:17px;font-weight:700}.leak .d{font-size:14px;color:#52514e}
.foot{position:absolute;bottom:14px;left:44px;font-size:13px;color:#8a8983}
.sum{background:#eaf2fc;border:1px solid #b7d3f6;border-radius:12px;padding:14px 20px;font-size:18px;line-height:1.45;margin-bottom:18px}
.sum b{color:#184f95;font-size:14px;letter-spacing:.5px;display:block;margin-bottom:4px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:1150px}
.qa{background:#fff;border:1px solid #e6e5e0;border-radius:12px;padding:12px 16px;height:182px;box-sizing:border-box}
.qa .k{font-size:12px;font-weight:700;color:#2a78d6;letter-spacing:.5px}.qa .q{font-size:16px;font-weight:700;margin:4px 0 6px}.qa .a{font-size:13.5px;line-height:1.38}.qa .m{font-size:11.5px;color:#8a8983;font-style:italic;margin-top:5px}
.recs{background:#f3f2ee;border:1px solid #e6e5e0;border-radius:14px;padding:18px 24px;width:640px;box-sizing:border-box;height:760px}
.recs h3{margin:0 0 10px;font-size:22px}.rec{margin:0 0 14px}.rec .t{font-size:17px;font-weight:700}.rec .i{font-size:16px;font-weight:700;margin:3px 0}.rec .w{font-size:14px;color:#52514e}
.recs ul{margin:6px 0 0;padding-left:20px;font-size:13.5px;color:#52514e;line-height:1.5}
"""
def img(n,w): return f'<img src="{BASE}{n}.png" style="width:{w}px" alt="{n}">'
p1=f"""<section data-document-role="page" data-label="Dashboard">
<h1>Global Superstore — Profitability Diagnostic Dashboard</h1>
<p class="sub">Where is profit leaking? 51,290 cleaned order lines · 147 countries · Jan 2011 – Dec 2014 · all values USD</p>
<div class="kpis">{''.join(f'<div class="kpi"><div class="l">{e(a)}</div><div class="v{" red" if r else ""}">{e(b)}</div><div class="n">{e(c)}</div></div>' for a,b,c,r in kpis)}</div>
<div class="row">{img('c1_year',440)}{img('c2_discount',430)}{img('c3_subcat',403)}{img('c4_region',442)}</div>
<div class="row" style="margin-top:6px">{img('c5_ship',440)}{img('c6_category',430)}{img('c7_country',384)}
<div class="panel" style="margin-left:40px"><h3>Ranked profit leaks</h3>{''.join(f'<div class="leak"><b class="{"red" if i<4 else ""}" style="{"color:#8a8983" if i==4 else ""}">{i+1}</b><div><div class="t">{e(t)}</div><div class="d">{e(d)}</div></div></div>' for i,(t,d) in enumerate(leaks))}</div></div>
<div class="foot">Source: GlobalSuperstoreData_Final.xlsx, cleaned (see Cleaning Log). Red = loss / below 75% of avg margin; blue = profit.</div>
</section>"""
clean=['Ship Date: 2 Excel serials → dates','Country: UK/US → United Kingdom/United States (149 → 147)','Product ID: 83 embedded spaces removed','Names: 273 double spaces collapsed','Quantity: 17 blanks imputed (Sales ÷ product unit price)','Discount: 16 blanks imputed (Country + Sub-Category mode); 2 × 0.85 capped at 0.80','Verified: no duplicates, Order-ID year = order year, ship days 0–7']
p2=f"""<section data-document-role="page" data-label="Answer Sheet">
<h1>Answer Sheet — Key Business Questions &amp; Recommendations</h1>
<p class="sub">Global Superstore profitability diagnostic · method stated under each answer</p>
<div class="sum"><b>EXECUTIVE SUMMARY (CFO)</b>{e(SUMMARY)}</div>
<div class="row"><div class="grid">{''.join(f'<div class="qa"><div class="k">Q{i+1} · {e(s.upper())}</div><div class="q">{e(q)}</div><div class="a">{e(a)}</div><div class="m">Method: {e(m)}</div></div>' for i,(s,q,a,m) in enumerate(QA))}</div>
<div class="recs"><h3>Recommendations — actionable within one quarter</h3>{''.join(f'<div class="rec"><div class="t">{e(t)}</div><div class="i {"red" if i<3 else "blue"}">{e(imp)}</div><div class="w">{e(w)}</div></div>' for i,(t,imp,w) in enumerate(RECS))}
<div class="rec"><div class="t">Data cleaning applied (51,290 rows)</div><ul>{''.join(f'<li>{e(c)}</li>' for c in clean)}</ul></div></div></div>
</section>"""
doc=f'<!doctype html><html><head><meta charset="utf-8"><title>Global Superstore Answer Sheet</title><style>{css}</style></head><body>{p1}{p2}</body></html>'
open('canva_answer_sheet.html','w').write(doc)
