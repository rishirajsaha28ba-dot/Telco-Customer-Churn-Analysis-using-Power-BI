import pandas as pd
pd.set_option('display.width',250)
df=pd.read_pickle('clean.pkl')
def agg(g):
    t=df.groupby(g).agg(Sales=('Sales','sum'),Profit=('Profit','sum'),Ship=('Shipping Cost','sum'),Disc=('Discount','mean'),Lines=('Sales','size'),Loss=('Loss-Making Flag','mean'),Orders=('Order ID','nunique'))
    t['Margin']=t.Profit/t.Sales; t['Ship%']=t.Ship/t.Sales; return t
S,P=df.Sales.sum(),df.Profit.sum(); print('KPIs',S,P,P/S,df['Order ID'].nunique(),df['Customer ID'].nunique(),df.Country.nunique(),df['Loss-Making Flag'].mean(),df['Shipping Cost'].sum()/S, S/df['Order ID'].nunique())
for g in ['Order Year','Category','Sub-Category','Segment','Ship Mode','Market',['Market','Region'],'Discount Band','Order Priority']:
    print(agg(g).sort_values('Profit').round(3).to_string(),'\n')
print(agg(['Segment','Discount Band']).Profit.unstack().round(0))
print('disc>20% loss rate',df[df.Discount>0.2]['Loss-Making Flag'].mean(), 'profit',df[df.Discount>0.2].Profit.sum(),'sales',df[df.Discount>0.2].Sales.sum())
print('loss lines total loss',df[df.Profit<0].Profit.sum())
print(agg('Country').sort_values('Profit').head(12).round(3))
print(agg(['Category','Discount Band']).Profit.unstack().round(0))
print(df.groupby('Ship Mode')['Ship Days'].mean())
