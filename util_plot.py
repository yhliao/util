from matplotlib import pyplot as plt
from matplotlib import rc, gridspec
import numpy as np
from PIL import Image

def plot_init(figsize,nrow,ncol, TITLE=None):
   axislabelfont   = {'labelweight':'bold','labelsize':11}
   rc('axes',linewidth=1.2,**axislabelfont)
   rc('font',weight='bold',size=10)
   rc('legend',frameon=False)
   fig  = plt.figure(figsize=figsize,constrained_layout=True)
   gs   = gridspec.GridSpec(nrow,ncol,figure=fig)
   AX   = [fig.add_subplot(g) for g in gs]

   if TITLE is None:
      TITLE = [""] * nrow * ncol
   for n, (ax, tit) in enumerate(zip(AX,TITLE)):
     index = chr(ord('a') + n)
     #ax.set_title("({0})".format(index) + " " + tit,
     #              fontsize=14,x=-0.1 ,y=1.05,ha="left",weight='bold')
     ax.set_title(tit,
                   fontsize=14,x=-0.1 ,y=1.05,ha="left",weight='bold')

   return fig, AX

def save_and_show(fig,filename):
   fig.savefig(filename)
   Image.open(filename).show()

def EngForm(num,floatdigit=2):
   def isbetween(num,low,high):
      return (num >= low) and (num < high)
   digit = np.floor(np.log10(num))
   if isbetween(digit,-15,-12):
      unit = 'f'
      factor = 1e15
   elif isbetween(digit,-12,-9):
      unit = 'p'
      factor = 1e12
   elif isbetween(digit,-9,-6):
      unit = 'n'
      factor = 1e9
   elif isbetween(digit,-6,-3):
      unit = 'u'
      factor = 1e6
   elif isbetween(digit,-3,0):
      unit = 'm'
      factor = 1e3
   elif isbetween(digit,3,6):
      unit = 'K'
      factor = 1e-3
   elif isbetween(digit,6,9):
      unit = 'M'
      factor = 1e-6
   elif isbetween(digit,9,12):
      unit = 'G'
      factor = 1e-9
   elif isbetween(digit,12,15):
      unit = 'T'
      factor = 1e-12
   else:
      unit   = ''
      factor = 1
   return "{0:.{1}f}{2}".format(num*factor,floatdigit,unit)
