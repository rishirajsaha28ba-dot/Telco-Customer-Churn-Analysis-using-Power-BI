import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
_s=plt.Figure.savefig
plt.Figure.savefig=lambda self,*a,**k: None
exec(open('dash.py').read())
plt.Figure.savefig=_s
# hide header/KPI/leak panel & footer: remove fig texts and non-chart axes
fig.texts.clear()
fig.savefig('dash_hi.png',dpi=200,facecolor=BG)
from PIL import Image
im=Image.open('dash_hi.png'); W,H=im.size
boxes={'c1_year':(0.02,0.405,0.25,0.775),'c2_discount':(0.275,0.405,0.50,0.775),'c3_subcat':(0.535,0.405,0.745,0.775),'c4_region':(0.755,0.405,0.985,0.775),
'c5_ship':(0.02,0.02,0.25,0.385),'c6_category':(0.275,0.02,0.50,0.385),'c7_country':(0.555,0.02,0.755,0.385)}
for n,(x0,y0,x1,y1) in boxes.items():
    im.crop((int(x0*W),int((1-y1)*H),int(x1*W),int((1-y0)*H))).save(f'{n}.png')
print(W,H)
