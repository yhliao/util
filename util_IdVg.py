import numpy as np

def Vt_maxGm(VG,ID,plotax=None):
    Gm = np.diff(ID) / np.diff(VG) 
    idx_maxGm = np.argmax(Gm)
    maxGm    = Gm[idx_maxGm]
    VG_maxGm = (VG[idx_maxGm] + VG[idx_maxGm+1])/2
    ID_maxGm = (ID[idx_maxGm] + ID[idx_maxGm+1])/2

    Vt_expt  = -ID_maxGm / maxGm + VG_maxGm

    if not plotax is None:
        plotax.plot([Vt_expt,VG_maxGm+0.5],[0,ID_maxGm+0.5*maxGm],"--",c='k')
    return Vt_expt

def IdVg_to_Gm(VG,ID):
   Gm = np.diff(ID)/np.diff(VG)
   VGmid = (VG[:-1] + VG[1:] )/2

   return VGmid, Gm
class Curve_IdVg:
   def __init__(self,VG,ID,VD):
      self.VG = VG
      self.ID = ID
      self.VD = VD

      self.Vt = Vt_maxGm(VG,ID) 
      self.VGmid, self.Gm = IdVg_to_Gm(VG,ID)
      
