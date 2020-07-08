import numpy as np
from scipy.integrate import cumtrapz
from .util_IdVg import Curve_IdVg

epsilon_Ox = 3.9 * 8.85e-14
epsilon_Si = 11.9 * 8.85e-14

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

def fit_Rp(VG,ID,Vt,Vd=0.05,Vovlim=[0.2,0.4],plotax=None,showRp=False,**plotprop):
    Vov = VG-Vt

    selIdx = np.all([Vov>Vovlim[0],Vov<Vovlim[1]],axis=0)

    m, Rp = np.polyfit(1/Vov[selIdx],Vd/ID[selIdx],1)

    if not plotax is None:
        keepIdx = (Vov > 0.1)
        Rtot   = Vd/ID[keepIdx]
        invVov = 1/Vov[keepIdx]
        plotax.plot(invVov,Rtot,**plotprop)
        plotax.plot([0,invVov[0]],[Rp,Rp+invVov[0]*m],'--',c='k')
        plotax.set_ylim(bottom=0)
        plotax.set_xlim(left=0)
        if showRp:
            plotax.axhline(y=Rp,ls='--',c='k')
            _, right = plotax.get_xlim()
            plotax.text(s='R$_p$ = {0:.2f}$\Omega$-$\mu$m'.format(Rp),
                        y=Rp,x=right*0.95,ha='right',va='bottom')

    return Rp, m

def Rslope_to_mob(slope,devdim,EOT):
    Cox = epsilon_Ox / EOT
    mob = devdim['L']/devdim['W'] / Cox/slope
    return mob

def Rch_to_mob(Rch,Qinv,devdim):
    ##  Rch    =  L   / ( W  * Qinv  * mob)
    ## [V-s/C] = [um] / ([um]*[C/cm2]*[cm2/V-s])
    mob = devdim['L']/devdim['W'] / Qinv / Rch
    return mob

def Rch(EOT,Vov,devdim,mob):
    ##  Rch    =  L   / ( W  * Qinv  * mob)
    ## [V-s/C] = [um] / ([um]*[C/cm2]*[cm2/V-s])
    Qinv = Vov_to_Qinv(Vov,EOT)
    Rch = devdim['L']/devdim['W'] / Qinv / mob
    return Rch

def IdVg_to_Gm(VG,ID):
   Gm = np.diff(ID)/np.diff(VG)
   VGmid = (VG[:-1] + VG[1:] )/2

   return VGmid, Gm

def IdVg_to_mob(VG,ID,Vt,Rp,EOT,devdim,Vovmin=0.1,Vd=0.05):
    ## Rp, Vt obtained from fittings
    Vov = VG-Vt-ID*Rp/2

    selIdx = np.all([Vov>Vovmin],axis=0)
    Vov = Vov[selIdx]

    Rch  = Vd/ID[selIdx] - Rp
    Qinv = Vov_to_Qinv(Vov,EOT)

    mob  = Rch_to_mob(Rch,Qinv,devdim)


    return Vov, mob

def IdVg_CV_to_mob(IdVgCurve,
                   VG_CV,Cch,Rp,devdim,
                   Vovmin=0.1):
    ## Vt, Rp obtained from fittings

    Vov  = IdVgCurve.VG-IdVgCurve.Vt-IdVgCurve.ID*Rp/2
    ## Also ensure the VG range does not exceed that of CV
    selIdx = np.all([Vov>Vovmin,IdVgCurve.VG<np.max(VG_CV)],axis=0)
    VG   = IdVgCurve.VG[selIdx]
    ID   = IdVgCurve.ID[selIdx]

    Vgint = VG - ID * Rp/2
    Rch   = IdVgCurve.VD/ID - Rp
    ## Align Qinv to the VG from IdVg

    VG_QV, Qinv = CV_to_Qinv(VG_CV,Cch)
    Qinv = np.interp(VG,VG_QV,Qinv)
    mob  = Rch_to_mob(Rch,Qinv,devdim)

    return Vgint, Qinv,mob

# First-Order Estimation of mobility from Gm and CV
## Supposed to work around peak gm
def gm_CV_to_mob(VG,Gm,VG_CV,Cch,devdim,Vd=0.05):
    Cch = np.interp(VG, VG_CV, Cch)

    mob = devdim['L']/devdim['W']/Vd * Gm / Cch
    #return Gm /Vd
    return mob

## De-embed Rs, Rd from Gm, Gds
def GmGds_to_gmgds(VG,Gm,VG_Gds,Gds,Rs,Rd):
   Gds = np.interp(VG,VG_Gds,Gds)
   ## gm, gds: intrinsic
   ## J [gm gds]^T = G = [Gm Gd]^T
   length = len(VG)
   J = np.zeros((length,2,2))
   G = np.zeros((length,2))

   G[:,0] = Gm
   G[:,1] = Gds

   J[:,0,0] = 1-Rs*Gm
   J[:,0,1] = -Gm * (Rs + Rd)
   J[:,1,0] = -Rs * Gds
   J[:,1,1] = 1- Gds * (Rs + Rd)

   g = np.linalg.solve(J,G)

   ## unpack the results
   gm  = g[:,0]
   gds = g[:,1]

   return gm, gds

def VGVD_to_vgvd(VGref,VG,VD,ID,Rs,Rd):
   ID = np.interp(VGref,VG,ID)

   R_min = np.min(VD/ID)
   if (Rs + Rd) > R_min:
      raise ValueError ("Rs + Rd can not exeed {0}!".format(R_min))

   vg = VGref - ID *  Rs
   vd = VD - ID * (Rs+Rd)

   return vg,vd

def CV_to_Qinv(VG,Cch):
    Qinv = cumtrapz(y=Cch,x=VG,initial=0)
    return VG,Qinv

def Vov_to_Qinv(Vov,EOT):
    Cox = epsilon_Ox / EOT
    Qinv = Cox * Vov
    return Qinv

def IdVg2_to_Rs(Curve1,Curve2,Vovmin=0.2):
   Vt1=  Curve1.Vt
   Vt2=  Curve2.Vt
   VD1=  Curve1.VD
   VD2=  Curve2.VD

   VG = Curve1.VG[(Curve1.VG>Vt1+Vovmin)]
   
   ID1=  np.interp(VG,Curve1.VG,Curve1.ID)
   ID2=  np.interp(VG,Curve1.VG,Curve2.ID)

   Coeff_2 = (ID2- ID1) /2
   Coeff_1 = Vt2- Vt1 + (VD1 - VD2) /2 * np.ones(len(VG))
   Coeff_0 = -((VG-Vt1)*ID2*VD1-(VG-Vt2)*ID1*VD2) / ID1/ID2

   Coeff_matrix = np.vstack((Coeff_2,Coeff_1,Coeff_0)).T
   RSD = []
   for C in Coeff_matrix:
      Rs = max(np.roots(C))
      RSD.append(np.abs(Rs))
   return VG,RSD


def Vov_to_Eeff(Vov,EOT,NA):
    ## Eeff = Vov / 6 Toxe + Qdm / epsilon_Si
    phiS = 2 * 0.0259 * np.log(NA/1e10)
    Qdm  = (2 * epsilon_Si * 1.6e-19 * NA * phiS ) ** 0.5

    Eeff = Vov/6/EOT + Qdm / epsilon_Si

    return Eeff
