import pandas as pd, numpy as np
SRC='/root/.claude/uploads/5c5197dd-edf2-5b67-8b87-ad8d7893aa58/02c9d96c-GlobalSuperstoreData_Final.xlsx'
df=pd.read_excel(SRC,sheet_name=0)
log=[]
def L(issue,col,n,fix): log.append(dict(Issue=issue,Column=col,Rows_Affected=int(n),Fix_Applied=fix))
m=df['Ship Date'].map(lambda v:isinstance(v,(int,float)))
L('Ship Date stored as Excel serial number, not a date','Ship Date',m.sum(),'Converted serial to date (base 1899-12-30)')
df['Ship Date']=pd.to_datetime(df['Ship Date'].map(lambda v: pd.Timestamp('1899-12-30')+pd.Timedelta(days=int(v)) if isinstance(v,(int,float)) else v))
for a,b in [('UK','United Kingdom'),('US','United States')]:
    n=(df.Country==a).sum(); df.loc[df.Country==a,'Country']=b
    L(f'Inconsistent country label "{a}"','Country',n,f'Standardised to "{b}"')
n=df['Product ID'].str.contains(r'\s').sum(); df['Product ID']=df['Product ID'].str.replace(r'\s','',regex=True)
L('Embedded spaces in Product ID (e.g. "TEC-HP -10003345")','Product ID',n,'Removed whitespace')
for c in ['Product Name','Customer Name','City','State']:
    s=df[c].str.replace(r'\s+',' ',regex=True).str.strip(); n=(s!=df[c]).sum()
    if n: L('Double / leading / trailing spaces','%s'%c,n,'Collapsed to single spaces and trimmed')
    df[c]=s
# Quantity impute from unit price of same product
up=(df.Sales/df.Quantity/(1-df.Discount.fillna(0)))
mq=df.Quantity.isna()
ref=df.assign(up=df.Sales/df.Quantity).groupby('Product ID')['up'].median()
q=(df.Sales/df['Product ID'].map(ref)).round().clip(1,14)
q=q.fillna(df.groupby('Sub-Category').Quantity.transform('median'))
df.loc[mq,'Quantity']=q[mq]
L('Missing Quantity','Quantity',mq.sum(),'Imputed = Sales ÷ median unit price of same Product ID (rounded, 1–14)')
md=df.Discount.isna()
mode=df.groupby(['Country','Sub-Category']).Discount.agg(lambda s:s.mode().iloc[0] if s.notna().any() else np.nan)
fill=df.set_index(['Country','Sub-Category']).index.map(mode.to_dict().get)
df.loc[md,'Discount']=pd.Series(fill,index=df.index)[md]
df.loc[df.Discount.isna(),'Discount']=0
L('Missing Discount','Discount',md.sum(),'Imputed with modal discount for the same Country + Sub-Category (discount policy is set at that level)')
mx=df.Discount>0.8; df.loc[mx,'Discount']=0.8
L('Discount above documented maximum (0.85 > 0.80)','Discount',mx.sum(),'Capped at 0.80')
df['Quantity']=df.Quantity.astype(int)
L('Dual market labels for Austria (EU/EMEA) & Mongolia (APAC/EMEA)','Market',((df.Country=='Austria')&(df.Market=='EMEA')).sum()+((df.Country=='Mongolia')&(df.Market=='APAC')).sum(),'Retained — both combinations exist in Dim_Geography reference table; flagged only')
L('Checks passed: no duplicate Row IDs, no Order-ID/Order-Date year mismatch, Ship Days 0–7, Sales>0, Shipping Cost≥0','All',0,'No action needed')
# calculated fields
df['Ship Days']=(df['Ship Date']-df['Order Date']).dt.days
df['Order Year']=df['Order Date'].dt.year
df['Unit Selling Price']=df.Sales/df.Quantity
df['Profit Margin %']=df.Profit/df.Sales
df['Shipping Cost % of Sales']=df['Shipping Cost']/df.Sales
df['Loss-Making Flag']=(df.Profit<0).astype(int)
df['Discount Band']=pd.cut(df.Discount,[-1,0,0.1999,0.3999,0.5999,1],labels=['No Discount','Low','Medium','High','Very High']).astype(str)
df.to_pickle('clean.pkl'); pd.DataFrame(log).to_pickle('log.pkl')
print(pd.DataFrame(log).to_string()); print(df.Country.nunique())
