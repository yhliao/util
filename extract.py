import numpy as np

def Vt(Vg,Id,Ith=1e-7):
   logId = np.log(np.abs(Id))
   logIth = np.log(Ith)
   idx1 = np.argmax( logId > logIth) 
   Vt = np.interp(logIth,[logId[idx1-1],logId[idx1]],
                            [Vg[idx1-1],   Vg[idx1]] )
   return Vt

def DIBL(Vg,Id1,Id2,deltaVd,Ith=1e-7):
   Vt1 = Vt(Vg,Id1,Ith)
   Vt2 = Vt(Vg,Id2,Ith)
   return (Vt1 - Vt2) / deltaVd * 1000 

def SS(Vg,Id,Ith=1e-7,Ilow=1e-11):
   Vg = np.array(Vg)
   Id = np.array(Id)
   keeparray = np.concatenate([np.diff(abs(Id)) > 0, [True] ])
   Vg = Vg[keeparray]
   Id = Id[keeparray]
   idx_th  = np.argmin(Id < Ith)
   idx_low = np.argmax(Id > Ilow)
   SS = (Vg[idx_th] - Vg[idx_low]) /np.log10(Id[idx_th]/Id[idx_low])
   return SS * 1000

def SSmin(Vg,Id,Irange=[1e-11,1e-6]):
   Vg = np.array(Vg)
   Id = abs(np.array(Id))
   keeparray = (Id>Irange[0]) and (Id<Irange[1])
   Vg = Vg[keeparray]
   Id = Id[keeparray]
   SS = np.diff(Vg) / np.diff(np.log10(Id)) 
   return np.min(SS) * 1000

def Imin(Vg,Id):
   return np.min(Id)

def Imax(Vg,Id):
   return np.max(Id)

