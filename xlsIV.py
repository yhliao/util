import numpy as np
import xlrd

def read_IV(sheet,period=4,fieldname=["Vg",0.05,0.50,1.00],factor=1):
   ncols = sheet.ncols
   assert period==len(fieldname)
   assert (ncols%period)==0
   RESULT = []
   for i in range(int(ncols/period)):
      devicedata = {}
      Vg = sheet.col_values(period*i)
      Vg = [v for v in Vg if isinstance(v,float)]
      dataArr = [Vg] 
      for j in range(1,period):
         Id = sheet.col_values(period*i+j)
         Id = [I for I in Id if isinstance(I,float) or I=='']
         Id = [I if isinstance(I,float) else 1e-15 for I in Id]
         dataArr.append(np.array(Id)*factor)

      devicedata = dict(zip(fieldname,dataArr))
      RESULT.append(devicedata)
   return RESULT 

def plot_IV(ax,sheet,c,vdidx,unselect=[],yscale='log',factor=1):
   Device_Arr = read_IV(sheet,factor=factor)
   for n, datadict in enumerate(Device_Arr):
      if not n in unselect:
         for idx in vdidx:
            Vgdata = datadict["Vg"]
            Iddata = datadict[idx]
            if yscale == 'log':
               ax.semilogy(Vgdata,Iddata,c=c[n])
            elif yscale == 'lin':
               ax.plot(Vgdata,Iddata,c=c[n])
            else:
               raise AssertionError

def plot_SS(ax,sheet,c,vdidx,unselect=[],label="",factor=1):
   Device_Arr = read_IV(sheet,factor=factor)
   for n, datadict in enumerate(Device_Arr):
      if not n in unselect:
         for idx in vdidx:
            Vgdata = datadict["Vg"]
            Iddata = datadict[idx] 
            logIddata = np.log10(Iddata)
            SSdata = np.diff(Vgdata) / np.diff(logIddata) * 1000
            Idplot = 10 ** (( logIddata[1:] + logIddata[:-1] ) /2)
            ax.semilogx(Idplot,SSdata,c=c[n])

################################################
### Method and Wrapper Class for Extractions ###
### , Summarizing, and Plotting the Trends   ###
################################################
def extract_IV(sheet,vdidx,action,args,unselect,factor=1):
   assert len(vdidx) == len(action)
   assert len(args) == len(action)
   Device_Arr = read_IV(sheet,factor=factor)
   RESULT = [[] for i in range(len(action))]
   for n, datadict in enumerate(Device_Arr):
      if not n in unselect:
         for m, (idx, act, arg) in enumerate(zip(vdidx,action,args)):
            Vgdata = datadict["Vg"]
            if type(idx) is list:
               Iddata_arr = [datadict[i] for i in idx]
               extraction = act(Vgdata,*(Iddata_arr+arg))
            else:
               Iddata = datadict[idx]
               extraction = act(Vgdata,Iddata,*arg)
            RESULT[m].append(extraction)
   return RESULT 

class MeasTrendSummary:
   def __init__(self,LG,MEASType,filepathdir,UNSLECT,factor=1):
      self.LG = LG
      self.VDSEL    = []
      self.ACTION   = []
      self.ARGS     = []
      self.PLOTAX   = []
      self.factor   = factor

      self.MEASType = MEASType
      self.EX_DICT = []
      self.UNSLECT = UNSLECT

      self.IDX_COMP  = []
      self.FUNC_COMP = []
      self.AX_COMP   = []
      self.MEAStype_COMP = []

      self.xticks = range(len(self.LG))
      self.ex_num = 0
      self.comp_num = 0
      self.filepathdir = filepathdir

   def add_extraction(self,vdsel,action,args,plotAX=None):
      assert len(args) == len(self.LG)
      self.VDSEL.append(vdsel)
      self.ACTION.append(action)
      self.ARGS.append(args)
      self.PLOTAX.append(plotAX)

      newidx = self.ex_num
      self.ex_num += 1
      return newidx

   def add_comparison(self,exidx,func,MEASType,plotAX):
      assert len(MEASType) ==2
      self.IDX_COMP  .append(exidx)
      self.FUNC_COMP .append(func)
      self.AX_COMP   .append(plotAX)
      self.MEAStype_COMP.append(MEASType)

      returnidx = self.comp_num
      self.comp_num += 1
      return returnidx

   def _init_exdict(self):
      init_dict = {}
      for meastype in self.MEASType:
         init_dict[meastype] = []
      return init_dict

   def extract(self):
      self.EX_DICT = [self._init_exdict() for i in range(len(self.ACTION))]
      for n, (Lg,unselect_lg) in enumerate(zip(self.LG,self.UNSLECT)):
         fd = xlrd.open_workbook(self.filepathdir+"{0}.xls".format(Lg))
         ARGSARR = [arg[n] for arg in self.ARGS]
         
         for meastype, uns in zip(self.MEASType,unselect_lg):
            sheet  = fd.sheet_by_name(meastype)
            RESULT = extract_IV(sheet,self.VDSEL,
                                self.ACTION,ARGSARR,uns,
                                factor=self.factor)
            
            for ex_dict, result in zip(self.EX_DICT,RESULT):
               ex_dict[meastype].append(result)

   ### Configure once for all extractions
   def plot(self,plottype,meastype,xoffset,**kwargs):
      for ax, ex_dict in zip(self.PLOTAX,self.EX_DICT):
         yarr = ex_dict[meastype]
         if not ax is None:
            if plottype == "scatter":
               xarr = [[i+xoffset] * len(y) for i, y in enumerate(yarr)]
               x_scatter = sum(xarr,[])
               y_scatter = sum(yarr,[])
               ax.scatter(x_scatter,y_scatter,**kwargs)
            if plottype == "error":
               y_avg = [np.mean(y) for y in yarr]
               y_err = [np.std(y) for y in yarr]
               x     = [i+xoffset for i in range(len(yarr))]
               ax.errorbar(x=x,y=y_avg,yerr=y_err,**kwargs)

   ### Configure once for all extractions
   def plot_comparison(self,idx,**kwargs):
      edx  = self.IDX_COMP     [idx]
      func = self.FUNC_COMP    [idx]
      meas = self.MEAStype_COMP[idx]
      ax   = self.AX_COMP      [idx]

      MEAN = []
      STD  = []
      ex_dict = self.EX_DICT[edx]
      for arr1, arr2 in zip(ex_dict[meas[0]],ex_dict[meas[1]]):
         mean, std = func(arr1,arr2)
         MEAN.append(mean)
         STD.append(std)

      ax.errorbar(x=self.xticks,y=MEAN,yerr=STD,**kwargs)
      
   def format_ax(self,ax):
      if not ax is None:
         ax.set_xticks(self.xticks)
         ax.set_xticklabels(labels=self.LG)
         ax.set_xlabel("Gate Length (nm)")
         ax.legend()
