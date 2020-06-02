from .util import read_and_merge
from .extract import Vt, SS
import numpy as np
import os

def read_node(node,vd,simdir=".",
                           x="gate OuterVoltage",
                          ys=["drain TotalCurrent"],backupflag=None):
   forfile = "{0}/{1}_Vd{2}_for_des.plt".format(simdir,node,vd)
   revfile = "{0}/{1}_Vd{2}_rev_des.plt".format(simdir,node,vd)
   filelist = []
   for fn in [forfile,revfile]:
      if os.path.exists(fn):
         filelist.append(fn)
      else:
         print ("Warning: ", fn, "does not exist, skipping entry")

   if not backupflag is None:
      backupname = simdir+"/sim_backup/{0}_Vd{1}_{2}.csv".format(node,vd,backupflag)
   else:
      backupname = None

   return read_and_merge(filelist,x,ys,backupname)

def summarize_LG(name,LN,RS,ITH,ILOW,factor=1,VDlin="0.05",VDsat="0.50"):
   SSdata   = np.empty(len(LN))
   DIBLdata = np.empty(len(LN))
   n = 0
   for ln,rs,Ith,Ilow in zip(LN,RS,ITH,ILOW):
      node = "{0}/{1}/R{2}".format(name,ln,rs)
      VG_lin,ID_lin = read_node(node,VDlin,
                                    x="gate OuterVoltage",
                                   ys=["drain TotalCurrent"])
      VG_sat,ID_sat = read_node(node,VDsat,
                                    x="gate OuterVoltage",
                                   ys=["drain TotalCurrent"])
      ID_lin *= factor
      ID_sat *= factor

      SS_lin = SS(VG_lin,ID_lin,Ith,Ilow)
      Vt_lin = Vt(VG_lin,ID_lin,Ith)
      Vt_sat = Vt(VG_sat,ID_sat,Ith)

      deltaVD = float(VDsat) - float(VDlin)
      DIBL = 1000 * (Vt_lin - Vt_sat ) / deltaVD

      SSdata[n]   = SS_lin
      DIBLdata[n] = DIBL
      n += 1

   return SSdata, DIBLdata

def summarize_Vt(name,LN,RS,ITH,factor=1,VD="0.05"):
   Vtdata   = np.empty(len(LN))
   n = 0
   for ln,rs,Ith in zip(LN,RS,ITH):
      node = "{0}/{1}/R{2}".format(name,ln,rs)
      VG,ID = read_node(node,VD,
                        x="gate OuterVoltage",
                       ys=["drain TotalCurrent"])

      Vtdata[n] = Vt(VG,ID*factor,Ith)
      n += 1

   return Vtdata

