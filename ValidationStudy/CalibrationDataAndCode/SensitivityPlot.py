import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl
#define function to fit to data
from scipy.optimize import curve_fit
from scipy.stats import t


#Create figure illustrating range of ADC for current measurement

fig3, ax = plt.subplots(figsize=(6.4,3))


k = 1
r = 250
VDD = 3.3
logec = np.linspace(np.log(10),np.log(100000),100)
ec = np.exp(logec)/1000000

def V_ADC3plus(VDD,r,k,ec):
    #return  -VDD*(r+k/ec)/(2*r+k/ec)
    return  VDD*(r)/(2*r+k/ec)

#def Vminus(V,r,k,ec):
#    return V*r/(2*r+k/ec)

def V_curve(V,r,k,ec):
    dV_ADC3plus = V_ADC3plus(V,r,k,1.005*ec)-V_ADC3plus(V,r,k,.995*ec)
    return dV_ADC3plus

dmVi_250 = 1000*V_curve(VDD,250,1,ec)
dmVi_150 = 1000*V_curve(VDD,150,1,ec)
dmVi_500 = 1000*V_curve(VDD,500,1,ec)
dmVi_kpt7 = 1000*V_curve(VDD,250,.7,ec)

#the analytical value of EC*dV/dEC is given here
dmV_calcdEC = 3.3*1000*r*(k/ec**2)*(2*r+k/ec)**-2*ec/100

#theory = ax.plot(ec*1000,dmV_calcdEC,
#    color = 'blue', 
    #markeredgewidth=0.5,
    #marker = 'o',
#    linestyle = '--',
    #markersize = '3',
#    fillstyle='none',
#    label = 'R1=R2=150 $\Omega$, Cell const. = 1 cm$^{-1}$',
#    linewidth = 0.5,
#    )

positive = ax.plot(ec*1000,dmVi_150,
    color = 'blue', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '--',
    #markersize = '3',
    fillstyle='none',
    label = 'R1=R2=150 $\Omega$, K = 1 cm$^{-1}$',
    linewidth = 0.5,
    )
positive = ax.plot(ec*1000,dmVi_250,
    color = 'black', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '-',
    #markersize = '3',
    fillstyle='none',
    label = 'R1=R2=250 $\Omega$, K = 1 cm$^{-1}$',
    linewidth = 0.5,
    )

positive = ax.plot(ec*1000,dmVi_500,
    color = 'red', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '-.',
    #markersize = '3',
    fillstyle='none',
    label = 'R1=R2=500 $\Omega$, K = 1 cm$^{-1}$',
    linewidth = 0.5,
    )
positive = ax.plot(ec*1000,dmVi_kpt7,
    color = 'brown', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '-',
    dashes=(10,5),
    #markersize = '3',
    fillstyle='none',
    label = 'R1=R2=250 $\Omega$, K = 0.7 cm$^{-1}$',
    linewidth = 0.5,
    )

ax.set_ylabel('EC*dV$_{adc3}$/dEC (mV per % EC)', fontsize = 9)
ax.set_xlabel('EC (mS/cm)', fontsize = 9)
ax.set_xscale('log')
ax.legend(frameon=False, labelspacing = 0.2, prop={'size':7})
ax2 = ax.twinx()
ax2.set_ylabel("ADC Counts per % EC")
ymin, ymax = ax.get_ylim()
ax2.set_ylim(ymin*(2**12-1)/VDD/1000,ymax*(2**12-1)/VDD/1000)
fig3.tight_layout()