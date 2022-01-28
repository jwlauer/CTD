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
dfsu5['conductance']=0.574*(1000/dfsu5['R'])**1.014

#compute depth
dfsu1['depth'] = (dfsu1['pressure']*100-101300)/9810
dfsu2['depth'] = (dfsu2['pressure']*100-101300)/9810
dfsu3['depth'] = (dfsu3['pressure']*100-101300)/9810
dfsu5['depth'] = (dfsu5['pressure']*100-101300)/9810
dfsonde['depth'] = (dfsonde['Pressure psi a']*6.8947*1000)/9810

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

#Plot a line on each figure
sonde = axs[0].plot(dfsonde['Temp C'], 
        color = 'black', 
        label = 'EXO3', 
        linewidth = 1, 
        linestyle = '--'
        )

sonde = axs[1].plot(dfsonde['Cond uS/cm']/1000, 
        color = 'black', 
        label = 'EXO3', 
        linewidth = 1,
        linestyle = '--',
        )
sonde = axs[2].plot(dfsonde['depth'], 
        color = 'black', 
        label = 'EXO3', 
        linewidth = 1,
        linestyle = '--',
        )


#Plot a line on each figure
#l1 = axs[0].plot(dfsu1['MS5803_T corrected'], 
#        color = 'b', 
#        label = 'SU1', 
#        linewidth = 0.5, 
#        linestyle = '-'
#        )
l1 = axs[0].plot(dfsu1['therm_T corrected'], 
        color = 'b', 
        label = 'SU1', 
        linewidth = 0.3, 
        linestyle = '-'
        )
l1 = axs[1].plot(dfsu1['conductance'], 
        color = 'b', 
        label = 'SU1', 
        linewidth = 0.3,
        linestyle = '-',
        )
l1 = axs[2].plot(dfsu1['depth'], 
        color = 'b', 
        label = 'SU1', 
        linewidth = 0.3,
        linestyle = '-',
        )

#Plot a line on each figure
#l2 = axs[0].plot(dfsu2['MS5803_T corrected'], 
#        color = 'r', 
#        label = 'SU2', 
#        linewidth = 0.5, 
#        linestyle = '-'
#        )
l2 = axs[0].plot(dfsu2['therm_T corrected'], 
        color = 'r', 
        label = 'SU2', 
        linewidth = 0.3, 
        linestyle = '-'
        )
l2 = axs[1].plot(dfsu2['conductance'], 
        color = 'r', 
        label = 'SU2', 
        linewidth = 0.3,
        linestyle = '-',
        )
l2 = axs[2].plot(dfsu2['depth'], 
        color = 'r', 
        label = 'SU2', 
        linewidth = 0.3,
        linestyle = '-',
        )


#Plot a line on each figure
#l3 = axs[0].plot(dfsu3['MS5803_T corrected'], 
#        color = 'g', 
#        label = 'SU3', 
#        linewidth = 0.5, 
#        linestyle = '-'
#        )
l3 = axs[0].plot(dfsu3['therm_T corrected'], 
        color = 'lime', 
        label = 'SU3', 
        linewidth = 0.3, 
        linestyle = '-'
        )
l3 = axs[1].plot(dfsu3['conductance'], 
        color = 'lime', 
        label = 'SU3', 
        linewidth = 0.3,
        linestyle = '-',
        )
l3 = axs[2].plot(dfsu3['depth'], 
        color = 'lime', 
        label = 'SU3', 
        linewidth = 0.3,
        linestyle = '-',
        )

#Plot a line on each figure
l5 = axs[0].plot(dfsu5['MS5803_T corrected'], 
        color = 'lightgray', 
        label = 'SU5', 
        linewidth = 0.3, 
        linestyle = '-'
        )

l5 = axs[1].plot(dfsu5['conductance'], 
        color = 'lightgray', 
        label = 'SU5', 
        linewidth = 0.3,
        linestyle = '-',
        )
l5 = axs[2].plot(dfsu5['depth'], 
        color = 'lightgray', 
        label = 'SU5', 
        linewidth = 0.3,
        linestyle = '-',
        )



#Add the second line to each figure
#l2 = axs[0].plot(dfsonde['Temp °C'], color='r', label = 'EXO-3', linewidth = 0.5)
#l2 = axs[1].plot(dfsonde['Cond µS/cm'], color='r', label = 'EXO-3', linewidth = 0.5)
#l2 = axs[2].plot(dfsonde['Depth m'], color='r', label = 'EXO-3', linewidth = 0.5)

#Add the third line to each figure
#l3 = axs[0].plot(dflevel['TEMPERATURE'], color='g', label = 'LevelLogger', linewidth = 0.5)
#l3 = axs[1].plot(dflevel['Cond µS/cm'], color='g', label = 'LevelLogger', linewidth = 0.5)
#l3 = axs[2].plot(dflevel['Depth, m'], color='g', label = 'LevelLogger', linewidth = 0.5)

#Set the axis limits
axs[0].set_xlim(xmin=datetime.datetime(2021, 4, 1, hour=15, minute = 15), xmax=datetime.datetime(2021, 4, 5, hour=19))
axs[0].set_ylim(ymin = 8, ymax = 18)
axs[1].set_ylim(ymin = 0, ymax = 30)
axs[2].set_ylim(ymin = 0, ymax = 4)
#set the figure title
#fig.suptitle('May 9-10 Deployment')

#show the legend
axs[2].legend(fontsize = 8, ncol=len(axs[2].lines), frameon=False)

#Set up the y axis labels
axs[0].set_ylabel('T (°C)', fontsize = 9)
axs[1].set_ylabel('EC (μS/cm)', fontsize = 9)
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
#myFmt = mdates.DateFormatter('%d %h %H:%M')
#axs[0].xaxis.set_major_formatter(myFmt)

#copy the old figure to a new figure using pickle
#ig2 is now not a reference to fig, so changes to fig2 won't affect fig
p = pickle.dumps(fig)
fig2 = pickle.loads(p)

fig2.show()

#ReSet the axis limits
ax = fig2.get_axes()
ax[0].set_xlim(xmin=datetime.datetime(2021, 4, 2, hour=16), xmax=datetime.datetime(2021, 4, 3, hour=16))
#ax[0].set_ylim(5,7)
#ax[1].set_ylim(0,200)
#ax[2].set_ylim(0,3)

#Reset the title
fig2.suptitle('April 2-3 Deployment')