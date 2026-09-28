import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
figs=[]
orig=plt.Figure.savefig
def cap(self,*a,**k):
    if self not in figs: figs.append(self)
plt.Figure.savefig=cap
exec(open('dash.py').read()); exec(open('page2.py').read())
plt.Figure.savefig=orig
with PdfPages('Global_Superstore_Answer_Sheet.pdf') as pp:
    for f in figs: pp.savefig(f,facecolor='#fcfcfb')
