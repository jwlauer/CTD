import pandas as pd
from matplotlib import pyplot as plt
import datetime
import pickle
import matplotlib.dates as mdates

# Read the files
dfsonde = pd.read_csv('sonde.txt',
                      #skiprows= 10,
                      #header = 11,       #use the second row (index 1) as column headings
                      parse_dates={'datetime': [0, 1]},  #convert text to dates/times where possible
                      #index_col = 9     #read dates from column 9 into the index
                      )
dfsonde = dfsonde.set_index('datetime')

dfsu1 = pd.read_csv('datalogCTD_su1.txt',
                      #skiprows= 10,
                      #header = 11,       #use the second row (index 1) as column headings
                      parse_dates={'datetime': [0, 1]},  #convert text to dates/times where possible
                      #index_col = 9     #read dates from column 9 into the index
                      )
dfsu1 = dfsu1.set_index('datetime')

dfsu2 = pd.read_csv('datalogCTD_su2.txt',
                      #skiprows= 10,
                      #header = 11,       #use the second row (index 1) as column headings
                      parse_dates={'datetime': [0, 1]},  #convert text to dates/times where possible
                      #index_col = 9     #read dates from column 9 into the index
                      )
dfsu2 = dfsu2.set_index('datetime')

dfsu3 = pd.read_csv('datalogCTD_su3.txt',
                      #skiprows= 10,
                      #header = 11,       #use the second row (index 1) as column headings
                      parse_dates={'datetime': [0, 1]},  #convert text to dates/times where possible
                      #index_col = 9     #read dates from column 9 into the index
                      )
dfsu3 = dfsu3.set_index('datetime')

dfsu5 = pd.read_csv('datalogCTD_su5_processed.txt',
                      #skiprows= 10,
                      #header = 11,       #use the second row (index 1) as column headings
                      parse_dates={'datetime': [0, 1]},  #convert text to dates/times where possible
                      #index_col = 9     #read dates from column 9 into the index
                      )
dfsu5 = dfsu5.set_index('datetime')


#define cell constants from calibration data (micro S)
#k_su2 = 0.7114
#k_su3 = 0.3064 
#k_su4 = 0.298

#compute an average resistance and conductance
dfsu1['R']=(dfsu1['r1']+dfsu1['r2'])/2
dfsu1['conductance']=0.625*(1000/dfsu1['R'])**0.889-8.69

dfsu2['R']=(dfsu2['r1']+dfsu2['r2'])/2
dfsu2['conductance']=.712*(1000/dfsu2['R'])**1.01


dfsu3['R']=(dfsu3['r1']+dfsu3['r2'])/2
dfsu3['conductance']=.335*(1000/dfsu3['R'])**.993

dfsu5['R']=(dfsu5['r1']+dfsu5['r2'])/2
dfsu5['conductance']=0.577*(1000/dfsu5['R'])**1.00

#compute depth
dfsu1['depth'] = (dfsu1['pressure']*100-101300)/9810
dfsu2['depth'] = (dfsu2['pressure']*100-101300)/9810
dfsu3['depth'] = (dfsu3['pressure']*100-101300)/9810
dfsu5['depth'] = (dfsu5['pressure']*100-101300)/9810
dfsonde['depth'] = (dfsonde['Pressure psi a']*6.8947*1000)/9810

#compute depth offset and correct depths
start = '2021-04-01 14:45'
end = '2021-04-01 14:55'
dfsu1_cor = dfsu1[(dfsu1.index>start) & (dfsu1.index<end)]['depth'].mean()
dfsu2_cor = dfsu2[(dfsu2.index>start) & (dfsu2.index<end)]['depth'].mean()
dfsu3_cor = dfsu3[(dfsu3.index>start) & (dfsu3.index<end)]['depth'].mean()
dfsu5_cor = dfsu5[(dfsu5.index>start) & (dfsu5.index<end)]['depth'].mean()
dfsonde_cor = dfsonde[(dfsonde.index>start) & (dfsonde.index<end)]['depth'].mean()

dfsu1['depth']=dfsu1['depth']-dfsu1_cor
dfsu2['depth']=dfsu2['depth']-dfsu2_cor
dfsu3['depth']=dfsu3['depth']-dfsu3_cor
dfsu5['depth']=dfsu5['depth']-dfsu5_cor
dfsonde['depth']=dfsonde['depth']-dfsonde_cor


dfsonde['conductance']=dfsonde['Cond uS/cm']/1000

#dfsu4['depth'] = (dfsu4['pressure']*100-101300)/9810

#correct temperatures using offset from sonde during night of April 2
dfsu1_sub = dfsu1.loc['2021-4-2 00:00':'2021-4-2 8:00']
dfsu2_sub = dfsu2.loc['2021-4-2 00:00':'2021-4-2 8:00']
dfsu3_sub = dfsu3.loc['2021-4-2 00:00':'2021-4-2 8:00']
dfsu5_sub = dfsu5.loc['2021-4-2 00:00':'2021-4-2 8:00']
dfsonde_sub = dfsonde.loc['2021-4-2 00:00':'2021-4-2 8:00']

Toffset_su1_therm = dfsonde_sub['Temp C'].mean()-dfsu1_sub['therm_T'].mean()
Toffset_su2_therm = dfsonde_sub['Temp C'].mean()-dfsu2_sub['therm_T'].mean()
Toffset_su3_therm = dfsonde_sub['Temp C'].mean()-dfsu3_sub['therm_T'].mean()

Toffset_su1_MS = dfsonde_sub['Temp C'].mean()-dfsu1_sub['MS5803_T'].mean()
Toffset_su2_MS = dfsonde_sub['Temp C'].mean()-dfsu2_sub['MS5803_T'].mean()
Toffset_su3_MS = dfsonde_sub['Temp C'].mean()-dfsu3_sub['MS5803_T'].mean()
Toffset_su5_MS = dfsonde_sub['Temp C'].mean()-dfsu5_sub['MS5803_T'].mean()

dfsu1['therm_T corrected']=dfsu1['therm_T']+Toffset_su1_therm
dfsu2['therm_T corrected']=dfsu2['therm_T']+Toffset_su2_therm
dfsu3['therm_T corrected']=dfsu3['therm_T']+Toffset_su3_therm

dfsu1['MS5803_T corrected']=dfsu1['MS5803_T']+Toffset_su1_MS
dfsu2['MS5803_T corrected']=dfsu2['MS5803_T']+Toffset_su2_MS
dfsu3['MS5803_T corrected']=dfsu3['MS5803_T']+Toffset_su3_MS
dfsu5['MS5803_T corrected']=dfsu5['MS5803_T']+Toffset_su5_MS


#set up the figures and subfigures (aka axes)
fig, axs = plt.subplots(3, sharex = True)


import numpy as np
def plot_CDT_data(dfs,start1,end1,start2,end2,color_t,label_t,linewidth_t,linestyle_t,axs):
    
    for i in range(len(dfs)):
        df = dfs[i]
        mask = (((df.index > start1) & (df.index < end1)) 
            | ((df.index >= start2) & (df.index < end2)))
        x_values = np.array(df.index)
    
        #Plot a line on each figure
        y_values_masked = np.ma.masked_where(mask, df)
        line = axs[i].plot(x_values,y_values_masked, 
                color = color_t, 
                label = label_t, 
                linewidth = linewidth_t, 
                linestyle = linestyle_t
            )

start1 = '2021-4-2 14:20'
end1 = '2021-4-3 16:40'
start2 = '2021-4-4 17:00'
end2 = '2021-4-4 18:40'


dfs = (dfsu1['therm_T corrected'], dfsu1['conductance'], dfsu1['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'b','SU1',0.3,'-',axs)

dfs = (dfsu3['therm_T corrected'], dfsu3['conductance'], dfsu3['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'lime','SU3',0.3,'-',axs)

dfs = (dfsu5['MS5803_T corrected'], dfsu5['conductance'], dfsu5['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'gray','SU5',0.3,'-',axs)

dfs = (dfsonde['Temp C'], dfsonde['conductance'], dfsonde['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'black','EXO3',1,'--',axs)

dfs = (dfsu2['therm_T corrected'], dfsu2['conductance'], dfsu2['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'r','SU2',0.3,'-',axs)

handles,labels = axs[0].get_legend_handles_labels()
handles = [handles[0],handles[4],handles[1],handles[2],handles[3]]

#Set the axis limits
axs[0].set_xlim(xmin=datetime.datetime(2021, 4, 1, hour=15, minute = 15), xmax=datetime.datetime(2021, 4, 5, hour=19))
axs[0].set_ylim(ymin = 8, ymax = 13)
axs[1].set_ylim(ymin = 0, ymax = 35)
axs[2].set_ylim(ymin = 0, ymax = 4)
#set the figure title
#fig.suptitle('May 9-10 Deployment')

#show the legend
handles,labels = axs[0].get_legend_handles_labels()
handles = [handles[0],handles[4],handles[1],handles[2],handles[3]]
labels =  [labels[0],labels[4],labels[1],labels[2],labels[3]]
axs[0].legend(handles,labels,fontsize = 8, ncol=len(axs[2].lines), frameon=False)

#Set up the y axis labels
axs[0].set_ylabel('T (°C)', fontsize = 9)
axs[1].set_ylabel('EC (mS/cm)', fontsize = 9)
axs[2].set_ylabel('Depth (m)',fontsize = 9)

#p = pickle.dumps(fig)


#format the x axis dates
locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
formatter = mdates.ConciseDateFormatter(locator)
axs[0].xaxis.set_major_locator(locator)
axs[0].xaxis.set_major_formatter(formatter)
axs[0].tick_params(axis='both', which = 'major', labelsize =8)
axs[1].tick_params(axis='both', which = 'major', labelsize =8)
axs[2].tick_params(axis='both', which = 'major', labelsize =8)
#fig.align_labels()

#the following is an altnernate way to format dates
myFmt = mdates.DateFormatter('%d %h %H:%M')
axs[0].xaxis.set_major_formatter(myFmt)

#copy the old figure to a new figure using pickle
#ig2 is now not a reference to fig, so changes to fig2 won't affect fig
p = pickle.dumps(fig)
fig2 = pickle.loads(p)

fig2.show()

start1 = '2021-4-1 10:20'
end1 = '2021-4-1 14:50'
start2 = '2021-4-3 17:00'
end2 = '2021-4-4 18:40'

axs2 = fig2.get_axes()

dfs = (dfsu1['therm_T corrected'], dfsu1['conductance'], dfsu1['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'b','SU1',0.3,'-',axs2)

dfs = (dfsu3['therm_T corrected'], dfsu3['conductance'], dfsu3['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'lime','SU3',0.3,'-',axs2)

dfs = (dfsu5['MS5803_T corrected'], dfsu5['conductance'], dfsu5['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'gray','SU5',0.3,'-',axs2)

dfs = (dfsonde['Temp C'], dfsonde['conductance'], dfsonde['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'black','EXO3',1,'--',axs2)

dfs = (dfsu2['therm_T corrected'], dfsu2['conductance'], dfsu2['depth'])
plot_CDT_data(dfs, start1, end1, start2, end2,'r','SU2',0.3,'-',axs2)

#change order of labesl in legend
handles,labels = axs2[0].get_legend_handles_labels()
handles = [handles[0],handles[4],handles[1],handles[2],handles[3]]
labels =  [labels[0],labels[4],labels[1],labels[2],labels[3]]
axs2[0].legend(handles,labels,fontsize = 8, ncol=len(axs[2].lines), frameon=False)

#the following is an altnernate way to format dates
locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
formatter = mdates.ConciseDateFormatter(locator)
axs2[0].xaxis.set_major_locator(locator)
axs2[0].xaxis.set_major_formatter(formatter)
myFmt = mdates.DateFormatter('%d %h %H:%M')
axs2[0].xaxis.set_major_formatter(myFmt)

#ReSet the axis limits

axs2[0].set_xlim(xmin=datetime.datetime(2021, 4, 2, hour=16), xmax=datetime.datetime(2021, 4, 3, hour=16))
axs2[0].set_ylim(8,16)
axs2[1].set_ylim(0,30)
#ax[2].set_ylim(0,3)

#Reset the title
#fig2.suptitle('April 2-3 Deployment')

fig3, ((SU1,SU2),(SU3,SU5)) = plt.subplots(2,2)

start1 = '2021-4-1 14:50'
end1 = '2021-4-2 14:20'
start2 = '2021-4-3 17:00'
end2 = '2021-4-4 17:00'
start3 = '2021-4-4 18:40'
end3 = '2021-4-5 19:00'

def plot_validation_data(x,y,start1,end1,start2,end2,start3,end3,axs):

    y_r = y.loc[((y.index > start1) & (y.index < end1)) | 
                    ((y.index > start2) & (y.index < end2)) | 
                    ((y.index > start3) & (y.index < end3))]
    
    #interpolate the values of the sonde onto the recorded data from
    #the other sensor.
    
    x_r = x.reindex(x.index.union(y_r.index)).interpolate(method='index').reindex(y_r.index)
    
    y_r['sonde_cond']=x_r['conductance']
    y_r['error']=y_r['sonde_cond']-y['conductance']
    y_r['sq_error']=y_r['error']**2
    y_r['rel_error']=y_r['error']/y_r['sonde_cond']
    y_r['sq_rel_error']=y_r['rel_error']**2
    RMSE = (y_r['sq_error'].mean())**0.5
    RMSRE = (y_r['sq_rel_error'].mean())**0.5
    ME = y_r['error'].mean()
    MRE = y_r['rel_error'].mean()
    
    #plot
    points = axs.plot(y_r['sonde_cond'],y_r['conductance'], 
            color = 'black', 
            markeredgewidth=0.5,
            marker = 'o',
            linestyle = 'none',
            markersize = '1',
            fillstyle = 'none'
        )
    text = "ME=%4.2f\nMRE=%4.2f\nRMSE=%4.2f\nRMSRE=%4.3f" %(ME,MRE,RMSE,RMSRE)
    axs.text(0.05,.9, text, fontsize=7, transform = axs.transAxes, verticalalignment='top')
    
    x = [0.05,y_r['sonde_cond'].max()*1.1]
    line = axs.plot(x,x,
                    color = 'black',
                    linestyle = '-',
                    linewidth = 1)
    
    axs.set_xlim(xmin = 0.05, xmax = y_r['sonde_cond'].max()*1.2)
    axs.set_ylim(ymin = 0.05, ymax = y_r['sonde_cond'].max()*1.2)
    axs.set_xscale('log')
    axs.set_yscale('log')
    #fig4, ax = plt.subplots()
    #ax.plot(y_r.index,y_r['sonde_cond'],
    #        color = 'black',
    #        linestyle = '-')

    
plot_validation_data(dfsonde,dfsu1,start1,end1,start2,end2,start3,end3,SU1)
plot_validation_data(dfsonde,dfsu2,start1,end1,start2,end2,start3,end3,SU2)
plot_validation_data(dfsonde,dfsu3,start1,end1,start2,end2,start3,end3,SU3)
plot_validation_data(dfsonde,dfsu5,start1,end1,start2,end2,start3,end3,SU5)

SU1.set_ylabel('sensor EC (mS/cm)', fontsize = 9)
SU3.set_ylabel('sensor EC (mS/cm)', fontsize = 9)
SU3.set_xlabel('EXO EC (mS/cm)', fontsize = 9)
SU5.set_xlabel('EXO EC (mS/cm)', fontsize = 9)

SU1.set_title('SU1', fontsize=9)
SU2.set_title('SU2', fontsize=9)
SU3.set_title('SU3', fontsize=9)
SU5.set_title('SU5', fontsize=9)
fig3.tight_layout()