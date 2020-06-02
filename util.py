import sys
sys.path.insert(0,"..")

from simIOtools.plt_reader import readPLT
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rc, gridspec
import matplotlib
from simIOtools.csv_writer import write_column

def read_and_concat(filenames,variables):
   Var_data = [[] for i in variables]
   for n, fn in enumerate(filenames):
      #print ("reading",fn)
      rd = readPLT()
      rd.read_plt(fn)
      for vardata, var in zip(Var_data,variables):
         vardata.append(rd.retrieve(var))
   return [np.concatenate(arr) for arr in Var_data]

def merge(Idx_data,Var_data):
   idx_data, keepidx = np.unique(Idx_data,return_index=True)
   sort_idx  = np.argsort(idx_data)

   arr_return = [idx_data[sort_idx]]
   for vardata in Var_data:
      arr_return.append( vardata[keepidx][sort_idx] )
   return arr_return

def read_and_merge(filenames,index,variables,backupname=None):
   data = read_and_concat(filenames,[index]+variables)
   merged_data = merge(data[0],data[1:])
   if not backupname is None:
      colnames = [[n.replace(',','_')] for n in [index]+variables]
      write_column(backupname,colnames,merged_data,force=False)
   return merged_data 

## Split according to the uniqueness of index entries
def read_and_split(filename,index,variables):
   rd = readPLT()
   rd.read_plt(filename)
   Idx_data = rd.retrieve(index)
   Var_data = [rd.retrieve(v) for v in variables]

   Idx_entries = np.unique(Idx_data)

   dict_return = {}
   for entry in Idx_entries:
      filter_idx = (Idx_data == entry)
      Var_filtered = [data[filter_idx] for data in Var_data]
      dict_return[entry] = dict(zip(variables,Var_filtered))

   return dict_return

def merge_and_split(filenames,splitidx,mergeidx,variables):
   data = read_and_concat(filenames,[splitidx,mergeidx]+variables)
   splitidx_data = data[0]
   split_entries = np.unique(splitidx_data)

   dict_return = {}
   for entry in split_entries:
      filter_idx = (splitidx_data == entry)
      mergeidx_data = data[1][filter_idx]
      var_data = [arr[filter_idx] for arr in data[2:]]

      data_filtered_merged = merge(mergeidx_data,var_data)
      dict_return[entry] = dict(zip([mergeidx]+variables,
                                    data_filtered_merged))
   return split_entries,dict_return

axislabelfont   = {'labelweight':'bold',
                   'labelsize'  :'large',
                   'titleweight':'bold' }
legendlabelfont = {'fontsize':'medium'}

def plot_init(figsize,nrow,ncol, TITLE=None, subplotidx=False):

   #matplotlib.use('Agg')
   rc('axes',linewidth=1.5,**axislabelfont)
   rc('font',size=12,weight='bold')
   rc('legend',frameon=False,**legendlabelfont)
   fig  = plt.figure(figsize=figsize,constrained_layout=True)
   gs   = gridspec.GridSpec(nrow,ncol,figure=fig)
   AX   = [fig.add_subplot(g) for g in gs]

   xp = -0.1
   yp = 1.05
   if TITLE is None:
      TITLE = [""] * nrow * ncol
      xp = -0.2
      yp = 0.95
   if len(AX)==1:
      AX[0].set_title(TITLE[0],
                      fontsize=14,x=xp ,y=yp,
                      ha="left",weight='bold')
   else:
      for n, (ax, tit) in enumerate(zip(AX,TITLE)):
         if subplotidx:
            index = chr(ord('a') + n)
            ax.set_title("({0})".format(index) + " " + tit,
                         fontsize=14,x=xp ,y=yp,
                         ha="left",weight='bold')
         else:
            ax.set_title(tit,
                         fontsize=14,x=xp ,y=yp,
                         ha="left",weight='bold')

   for ax in AX:
      ax.tick_params(axis='y',direction='inout',length=8,width=1.5)
      ax.tick_params(axis='x',which='major',direction='inout',length=8,width=1.5)
      ax.tick_params(axis='x',which='minor',direction='in',length=2,width=1)
   return fig, AX

epsilon0 = 8.85e-14 #  F/cm
class plotFE_QV:

   def __init__ (self,FEparam,epBG,tFE,ax_QV,ax_CQ=None,plotV=False):
      self.FEparam = np.array(FEparam)
      self.epBG  = epBG
      self.tFE   = tFE

      self.prefactor = np.arange(2*len(FEparam),0,-2)

      self.ax_QV = ax_QV
      self.ax_CQ = ax_CQ
      self.plotV  = plotV

      if plotV:
         ax_QV.set_xlabel("FE Voltage $V_{FE}$ (V)"),
      else:
         ax_QV.set_xlabel("Electric Field $E_{FE}$ (MV/cm)")
      ax_QV.set_ylabel("Gate Charge $Q_G$ ($\mu$C/cm$^2$)")

      if not ax_CQ is None:
         ax_CQ.set_xlabel("Gate Charge $Q_G$ ($\mu$C/cm$^2$)")
         ax_CQ.set_ylabel("FE Capacitance $C_{FE}$ ($\mu$F/cm$^2$)")
      self.stack_flag = False

   def Pr(self):
      sol = np.roots(self.prefactor*self.FEparam)
      return np.max(sol)**0.5

   def set_FEpar(self,value,order):
      idx = len(self.FEparam) - (order +1 ) /2
      self.FEparam[int(idx)] = value

   def set_Pr(self,Pr,ordermax,keeporder=[]):

      parlen = int((ordermax+1)/2)
      keeporder = np.array(keeporder)
      FEparam = np.flip([np.flip(self.FEparam,axis=0)[i] 
                           if i in (keeporder-1)/2 else 0
                           for i in range(parlen)],axis=0)
      self.FEparam = FEparam
      self.prefactor = np.arange(2*parlen,0,-2)

      RHS = -self._calc_E(Pr)
      coeff_hi = RHS / Pr**(self.prefactor[0]-1) / self.prefactor[0]

      self.FEparam[0] = coeff_hi

   def _calc_E(self,P):
      Porders = np.array([P**i for i in self.prefactor-1])
      E = np.matmul(self.prefactor * self.FEparam, Porders)
      return E
      
   def set_stack(self,EOT_IL,ax):
      self.CIL = epsilon0 * 3.9 / EOT_IL
      ax.set_xlabel("Gate Charge $Q_G$ ($\mu$C/cm$^2$)")
      ax.set_ylabel("Stack Capacitance $C_{stack}$ ($\mu$F/cm$^2$)")

      self.ax_stack = ax
      self.stack_flag = True

   def add_refC(self,EOT,**kwargs):
      refC = epsilon0 * 3.9 / EOT
      if self.stack_flag:
         self.ax_stack.axhline(refC*1E6,**kwargs)
      else:
         print ("add_refC: Stack Axis is not set! Ignored...")

   def add_curve(self,P,**kwargs):
      E = self._calc_E(P)
      QDE = E * epsilon0 * self.epBG
      Qtot = QDE + P
      VFE = E * self.tFE

      if self.plotV:

         self.ax_QV.plot(VFE,1E6*Qtot,**kwargs)
      else:
         self.ax_QV.plot(E/1E6,1E6*Qtot,**kwargs)

      NCFE = np.diff(Qtot) / np.diff(VFE) 
      if not self.ax_CQ is None:
         self.ax_CQ.plot(1E6*(Qtot[1:]+Qtot[:-1])/2,1E6*NCFE,
                         **kwargs)
      if self.stack_flag:
         Cstack = 1 / (1/NCFE + 1/self.CIL)
         self.ax_stack.plot(1E6*(Qtot[1:]+Qtot[:-1])/2,1E6*Cstack,
                         **kwargs)

def smear(X,Y,deltaX,weights=None,sample=50):
   assert np.all(np.diff(X)>0,axis=0)

   newXmin = min(X) + max(deltaX)
   newXmax = max(X) + min(deltaX)
   newX = np.linspace(newXmin,newXmax,sample)
   totY = np.zeros(sample)
   if weights is None:
      weights = [1/len(deltaX)] * len(deltaX)
   else:
      weights = weights / np.sum(weights)
         
   for dx, w in zip(deltaX,weights):
      x = newX - dx
      totY += np.interp(x,X,Y) * w
   #totY /= len(deltaX)
   return newX, totY

def get_par(group,key,value):
   from preprocessor.parse_specs import lookup_spec
   return lookup_spec([group],key,value,"../par_des/par_spec.bkup")
def get_nodespec(group,key,value):
   from preprocessor.parse_specs import lookup_spec
   return lookup_spec([group],key,value,"../NODE_spec.bkup")

def get_dvsspec(group,key,value):
   from preprocessor.parse_specs import lookup_spec
   return lookup_spec([group],key,value,"../dvs_specs.bkup")

def get_fullspec(group,key,value):
   from preprocessor.preprocess import preprocessor
   pp = preprocessor([],
                     ["../par_des/par_spec","../NODE_spec","../dvs_specs"],False)
   pp.inner_join('NODE[NDE][1]','GEOM[1]','geom')
   pp.inner_join('NODE[NNC][1]','GEOM[1]','geom')
   pp.inner_join('NODE[NDE][2]','GEOM[2]','geom')

   pp.inner_join('NODE[NDE][1]','Stack[NDE]','par')
   pp.inner_join('NODE[NNC][1]','Stack[NFE]','par')
   pp.inner_join('NODE[NDE][2]','Stack[NFE]','par')
   
   return pp.get_specdict(group,key,value)

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
