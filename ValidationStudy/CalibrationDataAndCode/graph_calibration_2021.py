import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl
#define function to fit to data
from scipy.optimize import curve_fit
from scipy.stats import t

# Read the file
xls = pd.ExcelFile('Calibration_data_all.xlsx')

sn = xls.sheet_names
names = ['SU1', 'SU2', 'SU3', 'SU5']
d = {}
for name in sn:
    d[name] = pd.read_excel(xls,
                      sheet_name = name,
                      header = 3,       #use the first row (index 1) as column headings
                      #parse_dates={'Datetime'},  #convert text to dates/times where possible
                      #index_col = 9     #read dates from column 9 into the index
                      )

#set up the figures and subfigures (aka axes)
fig, axs = plt.subplots(2,2, sharex = False)
plt.rc('xtick',labelsize=8)
plt.rc('ytick',labelsize=8)


location = ([0,0], [0,1], [1,0], [1,1])

#l = {}
#for i in range(4):
#    x = d[sn[i]]['1/R (uS)']
#    y = d[sn[i]]['Kt']
#    l[sn[i]] = axs[location[i]].plot(x,y,
#        color = 'b', 
#        marker = 'o',
 #       linestyle = 'none',
#        label = sn[i], 
#        )
def zero_int(x, m):
    return m*x

def linear(x,m,b):
    return m*x+b

def power(x,a,b):
    return a*x**b

def power_with_offset(x,a,b,c):
    return a*(x+c)**b

raw_data_2021 = {'SU1':d['SU1 3-17-21'], 'SU2':d['SU2 3-17-21'], 'SU3':d['SU3 3-17-21'], 'SU5':d['SU5 3-17-21']}
raw_data_2020 = {'SU1':d['SU1'], 'SU2':d['SU2'], 'SU3':d['SU3'], 'SU4':d['SU4']}
for i,ax in enumerate(fig.axes):
    if names[i] in raw_data_2020:
        y_2020 = raw_data_2020[names[i]]['1/R (uS)']/1000
        x_2020 = raw_data_2020[names[i]]['Kt']/1000
    y_2021 = raw_data_2021[names[i]]['1/R (uS)']/1000
    x_2021 = raw_data_2021[names[i]]['Kt']/1000
    log_x = np.log(x_2021)
    log_y = np.log(y_2021)
    
    ax.tick_params(axis='both', which = 'major', labelsize =8)
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

    
    #m,b = np.polyfit(x,y,1)
    print(names[i])
    popt0, pcov0 = curve_fit(zero_int, x_2021, y_2021)
    popt1, pcov1 = curve_fit(linear, x_2021, y_2021)
    popt2, pcov2 = curve_fit(linear, log_x, log_y)
    
    if i == 0:
        popt3, pcov3 = curve_fit(power_with_offset, x_2021, y_2021)
    
    m0 = popt0
    (m1,b1) = popt1
    (m_log,b_log) = popt2 
    a = np.exp(b_log)
    b = m_log
    (a2,b2,c2)=popt3
    
    if i < 3:
        x = np.linspace(20/1000,50000/1000,1000)
    else:
        x = np.linspace(100/1000,50000/1000,1000)
        
    linear_y = m1*x+b1
    power_y = a*x**b
    zero_y = m0*x
    offset_y = a2*(x+c2)**b2

    #linear_y = [b1,m1*1.1*max(x_2021)+b1]
    #linear_x = [0,1.1*max(x_2021)]
    
    residuals = y_2021- linear(x_2021, *popt1)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_2021-np.mean(y_2021))**2)
    r_squared = 1 - (ss_res / ss_tot)
    r_squared_l = r_squared
       
    residuals = log_y- (m_log*log_x+b_log)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((np.log(y_2021)-np.mean(np.log(y_2021)))**2)
    r_squared = 1 - (ss_res / ss_tot)
    r_squared_p = r_squared

    residuals = y_2021- zero_int(x_2021, *popt0)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_2021-np.mean(y_2021))**2)
    r_squared = 1 - (ss_res / ss_tot)
    r_squared_z = r_squared
    
    if i == 0: 
        residuals = y_2021- power_with_offset(x_2021, *popt3)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_2021-np.mean(y_2021))**2)
        r_squared = 1 - (ss_res / ss_tot)
        r_squared_po = r_squared
    
    if i == 0:
        if b1<0:
            sign = "-"
        else:
            sign = "+"

        fit2 = ax.plot(x, offset_y,
            color = 'r',
            linestyle = '-.',
            label = ('y=%4.2f(x+%4.1f)$^{%4.2f}$, r$^2_{loglog}$=%4.3f' %(a2,c2,b2,r_squared_po)),
            linewidth = 0.5,
            )    
        fit1 = ax.plot(x, linear_y,
            color = 'b',
            linestyle = '--',
            label = ('y=%4.2fx%s%5.1f, r$^2$=%4.3f' % (m1,sign,abs(b1),r_squared_l)),
            linewidth = 0.5,
            )
        #ax.set_ylim(9,250)
        #ax.set_xlim(16/1000,110)
        
    
        
    if i != 0:
        fit3 = ax.plot(x, power_y,
            color = 'r',
            linestyle = '-.',
            label = ('y=%4.2fx$^{%4.2f}$, r$^2_{loglog}$=%4.3f' % (a,b,r_squared_p)),
            linewidth = 0.5,
            )
        ax.set_xlim(16/1000,110)
        
        fit2 = ax.plot(x, zero_y,
            color = 'b',
            linestyle = '--',
            label = ('y=%4.2fx, r$^2$=%4.3f' %(m0,r_squared_z)),
            linewidth = 0.5,
            )
        
    ax.set_yscale('log')
    ax.set_xscale('log')        

    if names[i] in raw_data_2020: 
        l_2020= ax.plot(x_2020,y_2020,
            color = 'black', 
            markeredgewidth=0.5,
            marker = 'x',
            linestyle = 'none',
            markersize = '3',
            label = '2020 data', 
            )
    l_2021= ax.plot(x_2021,y_2021,
        color = 'black', 
        markeredgewidth=0.5,
        marker = 'o',
        linestyle = 'none',
        markersize = '3',
        fillstyle='none',
        label = '2021 data', 
        )
   
#show the legend
    ax.legend(frameon=False, loc='upper left', prop={'size':7})#, ncol=3)

    ax.set_title(names[i], fontsize=9)
    
#handles, labels = ax[0].get_legend_handles_labels()
#order = [3,2,0,1]   
#ax[0].legend([handles[idx] for idx in order], [labels[idx]for idx in order], frameon=False, loc='upper left', prop={'size':7})#, ncol=3)


print('got here')   
#Set up the y axis labels
axs[0,0].set_ylabel('Sensor 1/R (mS)', fontsize = 9)
axs[1,0].set_ylabel('Sensor 1/R (mS)', fontsize = 9)
axs[1,0].set_xlabel('EXO EC (mS/cm)', fontsize = 9)
axs[1,1].set_xlabel('EXO EC (mS/cm)',fontsize = 9)
print('got here')   
fig.tight_layout()
print('got here')   


#FIGURE 2
#compute confidence limits of inverse of regression

def confidence_limits(x,y,b0,b1,m,xhat0,alpha):
    n = x.size
    yhat = b0 + b1*x
    xbar = x.mean()
    s2yx = ((y-yhat)**2).sum()/(n-2)
    #syx = s2yx**0.5
    s2xhat0 = (s2yx/b1**2)*(1/m+1/n+((xhat0-xbar)**2)/((x-xbar)**2).sum())
    sxhat0 = s2xhat0**0.5
    t_stat = t.ppf(1-alpha/2,df=n-2)
    yplus = b0 + b1*xhat0 + t_stat*sxhat0
    yminus = b0 + b1*xhat0 - t_stat*sxhat0
    xplus = (yplus - b0)/b1
    xminus = (yminus - b0)/b1
    return(xminus,xhat0,xplus)

def error_analysis(x_obs,y_obs,m,b):
    n = x_obs.size
    y_est = m * x_obs + b
    residuals = y_obs - y_est
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_obs-np.mean(y_obs))**2)
    r_squared = 1 - (ss_res / ss_tot)
    ser = np.sqrt((1/(n-2))*(np.sum(residuals**2)))
    relative_error = residuals/y_obs 
    rmse = np.sqrt(np.sum(residuals**2)/n) 
    rmsre = np.sqrt(np.sum(relative_error**2)/n)
    return(r_squared,ser,rmse,rmsre)     


def find_and_plot_error_bands(x_obs, y_obs, use_offset, ax):
#Fit power function and adjust input by subracting constant and taking logs
    if use_offset == True:
        popt_test,pcov_test = curve_fit(power_with_offset,x_obs,y_obs)
        (a,b,c)=popt_test
        x_adjusted = np.log(x_obs+c)
        y_adjusted = np.log(y_obs)
    else:
        c = 0
        x_adjusted = np.log(x_obs)
        y_adjusted = np.log(y_obs)
        
    #Fit linear function to adjusted input
    popt1,pcov1 = curve_fit(linear,x_adjusted,y_adjusted)
    (b1,b0) = popt1
    (r2_log,ser_log,rmse_log,rmsre_log)=error_analysis(x_adjusted,y_adjusted,b1,b0)
    if use_offset == False:
        a = np.exp(b0)
        b = b1
        
    #Set up arrays to plot
    x_to_plot = np.linspace(0.95*min(x_obs),1.05*max(x_obs),1000)
    log_x_adj_to_plot = np.log(x_to_plot+c)
    log_y_to_plot = b0+b1*log_x_adj_to_plot
    y_to_plot = np.exp(log_y_to_plot)
    limits = []
    for i in range(len(log_x_adj_to_plot)):
        limits.append(confidence_limits(x_adjusted,y_adjusted,b0,b1,1,log_x_adj_to_plot[i],.05))
    df_limits = pd.DataFrame(limits)
    df_limits = np.exp(df_limits)-c
    df_limits.columns = ['lower','EC','upper']    
    df_limits['Sensor 1/R']=y_to_plot
    df_limits['percent'] = (df_limits['upper']/df_limits['EC']-1)*100
    
    #compute additional statistics in retransformed data
    n = x_obs.size
    residuals = y_obs- a*(x_obs+c)**b
    ser = np.sqrt((1/(n-2))*(np.sum(residuals**2)))
    relative_error = residuals/y_obs 
    rmse = np.sqrt(np.sum(residuals**2)/n) 
    rmsre = np.sqrt(np.sum(relative_error**2)/n)
    
    fit1 = ax.plot(x_to_plot, y_to_plot,
        color = 'b',
        linestyle = '-',
        label = ('Fit Line'),
        linewidth = 0.5,
        )
    
    upper = ax.plot(df_limits['lower'], y_to_plot,
        color = 'grey',
        linestyle = '--',
        label = ('95% limit'),
        linewidth = 0.5,
        )
    
    lower = ax.plot(df_limits['upper'], y_to_plot,
        color = 'grey',
        linestyle = '--',
        label = ('95% limit'),
        linewidth = 0.5,
        )
    
    data= ax.plot(x_obs,y_obs,
        color = 'black', 
        markeredgewidth=0.5,
        marker = 'o',
        linestyle = 'none',
        markersize = '3',
        fillstyle='none',
        label = 'Data used in regression', 
        )
    
    if use_offset == True:
        eqs = "y=%4.3f(x+%4.3f)$^{%4.3f}$\nr$^2_{loglog}$=%4.3f\nSt.Err.=%4.2f\nRMSE=%4.2f\nRMSRE=%4.3f" %(a,c,b,r2_log,ser,rmse,rmsre)
    else:
         eqs = "y=%4.3fx$^{%4.3f}$\nr$^2_{loglog}$=%4.3f\nSt.Err.=%4.2f\nRMSE=%4.2f\nRMSRE=%4.3f" %(a,b,r2_log,ser,rmse,rmsre)
    #eqs = 'Hi'
    #axs2[0,0].set_yscale('log')
    #axs2[0,0].set_xscale('log')
    #for i,ax in enumerate(fig2.axes):  
    #      ax.text(0,0, eqs, fontsize=8, transform = ax.transAxes)  
    ax.text(0.05,.9, eqs, fontsize=7, transform = ax.transAxes, verticalalignment='top')
    
    return(df_limits,r2_log,ser_log,rmse_log,rmsre_log,ser,rmse,rmsre)

#set up the figures and subfigures (aka axes)
#fig2, axs2 = plt.subplots(2,2, sharex = False)
fig2, ((SU1,SU2),(SU3,SU5)) = plt.subplots(2,2)
#fig2.tight_layout()
location = ([0,0], [0,1], [1,0], [1,1])

#SU1 -- Power with offset
x_obs = raw_data_2021['SU1']['Kt']/1000
y_obs = raw_data_2021['SU1']['1/R (uS)']/1000
x_obs = x_obs[0:36]
y_obs = y_obs[0:36]
#n = x_obs.size
(df_SU1limits,r2_log,ser_log,rmse_log,rmsre_log,ser,rmse,rmsre)=find_and_plot_error_bands(x_obs,y_obs,True,SU1)

#SU2--Log-log
x_obs = raw_data_2021['SU2']['Kt']/1000
y_obs = raw_data_2021['SU2']['1/R (uS)']/1000
x_obs = x_obs[0:36]
y_obs = y_obs[0:36]
#n = x.size
(df_SU2limits,r2_log,ser_log,rmse_log,rmsre_log,ser,rmse,rmsre)=find_and_plot_error_bands(x_obs,y_obs,False,SU2)


#SU3--Log-Log
x_obs = raw_data_2021['SU3']['Kt']/1000
y_obs = raw_data_2021['SU3']['1/R (uS)']/1000
x_obs = x_obs[12:]
y_obs = y_obs[12:]
#x_obs = x_obs[0:30]
#y_obs = y_obs[0:30]
(df_SU3limits,r2_log,ser_log,rmse_log,rmsre_log,ser,rmse,rmsre)=find_and_plot_error_bands(x_obs,y_obs,False,SU3)


#SU5--Log-Log
x_obs = raw_data_2021['SU5']['Kt']/1000
y_obs = raw_data_2021['SU5']['1/R (uS)']/1000
x_obs = x_obs[0:36]
y_obs = y_obs[0:36]
(df_SU5limits,r2_log,ser_log,rmse_log,rmsre_log,ser,rmse,rmsre)=find_and_plot_error_bands(x_obs,y_obs,False,SU5)

SU1.set_ylabel('Sensor 1/R (mS)', fontsize = 9)
SU3.set_ylabel('Sensor 1/R (mS)', fontsize = 9)
SU3.set_xlabel('EXO EC (mS/cm)', fontsize = 9)
SU5.set_xlabel('EXO EC (mS/cm)',fontsize = 9)

SU1.set_title('SU1', fontsize=9)
SU2.set_title('SU2', fontsize=9)
SU3.set_title('SU3', fontsize=9)
SU5.set_title('SU5', fontsize=9)

#SU1.xticks(fontsize=7)
#SU2.xticks(fontsize=7)
#SU3.xticks(fontsize=7)
#SU5.xticks(fontsize=7)

print('got here')   
fig2.tight_layout()


#Create figure illustrating range of ADC for current measurement

fig3, ax = plt.subplots(figsize=(6.4,3))


k = 1
r = 250
V = 3.3
logec = np.linspace(np.log(100),np.log(50000),100)
ec = np.exp(logec)/1000000

def Vplus(V,r,k,ec):
    return  V*(r+k/ec)/(2*r+k/ec)

def Vminus(V,r,k,ec):
    return V*r/(2*r+k/ec)

def V_curve(V,r,k,ec):
    dVi_plus = -Vplus(V,r,k,1.005*ec)+Vplus(V,r,k,.995*ec)
    return dVi_plus

dmVi_250 = 1000*V_curve(V,250,1,ec)
dmVi_150 = 1000*V_curve(V,150,1,ec)
dmVi_500 = 1000*V_curve(V,500,1,ec)
dmVi_kpt7 = 1000*V_curve(V,250,.7,ec)

positive = ax.plot(ec*1000,dmVi_150,
    color = 'blue', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '--',
    #markersize = '3',
    fillstyle='none',
    label = 'R$_i$=150 Ohm, Cell const. = 1 cm$^{-1}$',
    linewidth = 0.5,
    )
positive = ax.plot(ec*1000,dmVi_250,
    color = 'black', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '-',
    #markersize = '3',
    fillstyle='none',
    label = 'R$_i$=250 Ohm, Cell const. = 1 cm$^{-1}$',
    linewidth = 0.5,
    )

positive = ax.plot(ec*1000,dmVi_500,
    color = 'red', 
    #markeredgewidth=0.5,
    #marker = 'o',
    linestyle = '-.',
    #markersize = '3',
    fillstyle='none',
    label = 'R$_i$=500 Ohm, Cell const. = 1 cm$^{-1}$',
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
    label = 'R$_i$=250 Ohm, Cell const. = 0.7 cm$^{-1}$',
    linewidth = 0.5,
    )

ax.set_ylabel('dV$_{i}$/dEC (mV per % EC)', fontsize = 9)
ax.set_xlabel('EC (mS/cm)', fontsize = 9)
ax.set_xscale('log')
ax.legend(frameon=False, labelspacing = 0.2, prop={'size':7})
ax2 = ax.twinx()
ax2.set_ylabel("ADC Counts per % EC")
ymin, ymax = ax.get_ylim()
ax2.set_ylim(ymin*(2**12-1)/V/1000,ymax*(2**12-1)/V/1000)
fig3.tight_layout()