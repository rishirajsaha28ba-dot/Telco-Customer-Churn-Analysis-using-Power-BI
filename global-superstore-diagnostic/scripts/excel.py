import pandas as pd
from PIL import Image
from content import *
df=pd.read_pickle('clean.pkl'); log=pd.read_pickle('log.pkl')
Image.open('dashboard.png').convert('RGB').save('Global_Superstore_Answer_Sheet.pdf',save_all=True,append_images=[Image.open('answers.png').convert('RGB')],resolution=100)
def agg(k):
    t=df.groupby(k).agg(Sales=('Sales','sum'),Profit=('Profit','sum'),Shipping_Cost=('Shipping Cost','sum'),Avg_Discount=('Discount','mean'),Order_Lines=('Sales','size'),Orders=('Order ID','nunique'),Loss_Line_Rate=('Loss-Making Flag','mean'),Avg_Ship_Days=('Ship Days','mean'))
    t['Profit_Margin']=t.Profit/t.Sales; t['Ship_Cost_%_Sales']=t.Shipping_Cost/t.Sales; return t.reset_index()
out='Global_Superstore_Final_Answer_Sheet.xlsx'
with pd.ExcelWriter(out,engine='xlsxwriter') as w:
    wb=w.book; h=wb.add_format({'bold':True,'font_size':18}); b=wb.add_format({'bold':True}); wr=wb.add_format({'text_wrap':True,'valign':'top'}); bw=wb.add_format({'bold':True,'text_wrap':True,'valign':'top','bg_color':'#eaf2fc'})
    ws=wb.add_worksheet('Dashboard'); ws.write(0,0,'Global Superstore — Profitability Diagnostic Dashboard',h); ws.insert_image(2,0,'dashboard.png',{'x_scale':0.62,'y_scale':0.62})
    ws=wb.add_worksheet('Answer Sheet'); ws.set_column(0,0,14); ws.set_column(1,1,45); ws.set_column(2,2,95); ws.set_column(3,3,50)
    ws.write(0,0,'Answer Sheet — Key Business Questions',h); ws.merge_range(2,0,2,3,'Executive summary: '+SUMMARY,wr); ws.set_row(2,48)
    for j,c in enumerate(['Area','Question','Answer','Method']): ws.write(4,j,c,bw)
    for i,r in enumerate(QA):
        for j,v in enumerate(r): ws.write(5+i,j,v,wr)
        ws.set_row(5+i,80)
    ws.write(15,0,'Recommendations',h)
    for j,c in enumerate(['#','Action','Estimated impact','Rationale']): ws.write(16,j,c,bw)
    for i,(t,imp,why) in enumerate(RECS):
        ws.write(17+i,0,i+1); ws.write(17+i,1,t.split('. ',1)[1],wr); ws.write(17+i,2,imp,wr); ws.write(17+i,3,why,wr); ws.set_row(17+i,45)
    S,P=df.Sales.sum(),df.Profit.sum()
    k=pd.DataFrame([('Total Sales',S),('Total Profit',P),('Overall Profit Margin %',P/S),('Number of Orders',df['Order ID'].nunique()),('Number of Customers',df['Customer ID'].nunique()),('Countries',df.Country.nunique()),('Average Order Value',S/df['Order ID'].nunique()),('% Loss-Making Lines',df['Loss-Making Flag'].mean()),('Shipping Cost % of Sales',df['Shipping Cost'].sum()/S),('Profit on lines with Discount >20%',df[df.Discount>0.2].Profit.sum()),('Loss rate, Discount >20%',df[df.Discount>0.2]['Loss-Making Flag'].mean()),('Loss rate, Discount ≤20%',df[df.Discount<=0.2]['Loss-Making Flag'].mean())],columns=['KPI','Value'])
    k.to_excel(w,sheet_name='KPIs',index=False); w.sheets['KPIs'].set_column(0,0,38); w.sheets['KPIs'].set_column(1,1,16)
    log.to_excel(w,sheet_name='Cleaning Log',index=False); w.sheets['Cleaning Log'].set_column(0,0,70); w.sheets['Cleaning Log'].set_column(3,3,90)
    for name,key in [('By Year','Order Year'),('By Category',['Category','Sub-Category']),('By Segment','Segment'),('By Ship Mode','Ship Mode'),('By Market-Region',['Market','Region']),('By Country','Country'),('By Discount Band','Discount Band'),('Segment x Discount',['Segment','Discount Band']),('By Order Priority','Order Priority')]:
        t=agg(key).sort_values('Profit'); t.to_excel(w,sheet_name=name,index=False); w.sheets[name].set_column(0,12,16)
    c=df.copy(); c['Order Date']=c['Order Date'].dt.date; c['Ship Date']=c['Ship Date'].dt.date
    c.to_excel(w,sheet_name='Cleaned Data',index=False)
print('done')
