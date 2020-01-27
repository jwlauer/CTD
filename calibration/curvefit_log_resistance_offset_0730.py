# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:43:19 2019

@author: Wes
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('Calibration30.csv')
  
Cond = np.array(df['Sonde'])
#Count1 = np.array(df['Count1'])
#Count2 = np.array(df['Count2'])
#DividerResistor = 1000

R1 = np.array(df['Computed R1'])
R2 = np.array(df['Computed R2'])


#R1 = DividerResistor/((4095/Count1)-1)
#R2 = DividerResistor*(4095-Count2)/Count2
logCond = np.log10(Cond)


figure1, (subplot1, subplot2) = plt.subplots(1,2,False,True)
#figure1, subplot2 = plt.subplots()
subplot1.loglog(R1,Cond,'ro',label='R1')
subplot2.loglog(R2,Cond,'bo',label='R2')
#subplots.plot(logInvR2,logCond,'bo',label='logInvCount2')
subplot1.set_ylabel('Log Conductivity, $\mu$S/cm')
#subplot2.set_ylabel('Log Conductivity, $\mu$S/cm')
subplot1.set_xlabel('Log Resistance')
subplot2.set_xlabel('Log Resistance')

from scipy.optimize import curve_fit
def func(x, A, B, C):
    return A + B*np.log(x - C)              #linear model
    #return A * np.exp(-B * x) + C      #2-parameter exponential model
    #return A*np.exp(B + x) + C  #3-parameter exponential model
    #return A * (x - B) ** C         #power function model
    #return A + B*x + C*x**2            #polynomial model

popt1, pcov1 = curve_fit(func, R1, logCond)
popt2, pcov2 = curve_fit(func, R2, logCond)

(A1, B1, C1) = popt1
(A2, B2, C2) = popt2

print('Optimized Parameters 1 in Y = 10^A(x-C)^B: A = %4.6f, B = %4.6f, C = %4.6f' %(A1, B1, C1))
print('Optimized Parameters 2 in Y = 10^A(x-C)^B: A = %4.6f, B = %4.6f, C = %4.6f' %(A2, B2, C2))

Rs = np.arange(180,2000,10) 
subplot1.loglog(Rs, 10**func(Rs, *popt1), 'r-')
subplot2.loglog(Rs, 10**func(Rs, *popt2), 'b-')
figure1.show()

logPredictedCond1 = func(R1,*popt1)
PredictedCond1 = 10**logPredictedCond1
Error1 = Cond-PredictedCond1
PercentError1 = 100*Error1/Cond
SSE1 = sum(Error1**2)
AverageAbsolutePercentError1 = sum(abs(PercentError1))/len(PercentError1)
RMSE1 = (SSE1/len(Error1))**0.5
print('RMSE1 = %s, AvgAbsPercentError1 = %s' % (RMSE1, AverageAbsolutePercentError1))
import statistics
print('Standard Deviation of Percent Error1 = %s' %(statistics.stdev(PercentError1)))

logPredictedCond2 = func(R2,*popt2)
PredictedCond2 = 10**logPredictedCond2
Error2 = Cond-PredictedCond2
PercentError2 = 100*Error2/Cond
SE2 = Error2**2
SSE2 = sum(SE2)
RMSE2 = (SSE2/len(SE2))**0.5
AverageAbsolutePercentError2 = sum(abs(PercentError2))/len(PercentError2)
print('RMSE2 = %s, AvgAbsPercentError2 = %s' % (RMSE2, AverageAbsolutePercentError2))
print('Standard Deviation of Percent Error2 = %s' %(statistics.stdev(PercentError2)))

figure2, subplot2 = plt.subplots()
subplot2.plot(Cond,PredictedCond1,'ro',label="From1")
subplot2.plot(Cond,PredictedCond2,'bo',label="From2")
subplot2.plot(Cond,Cond,'b-')
subplot2.set_xlabel('Observed, $\mu$S/cm')
subplot2.set_ylabel('Predicted, $\mu$S/cm')
figure2.show()

figure3, subplot3 = plt.subplots()
subplot3.loglog(Cond,PredictedCond1,'ro',label="From1")
subplot3.loglog(Cond,PredictedCond2,'bo',label="From2")
subplot3.plot(Cond,Cond,'b-')
subplot3.set_xlabel('Observed, $\mu$S/cm')
subplot3.set_ylabel('Predicted, $\mu$S/cm')
figure3.show()

figure4, subplot4 = plt.subplots()
subplot4.loglog(Cond, Error1, 'ro')
subplot4.loglog(Cond, Error2, 'bo')
subplot4.set_xlabel('Conductivity, $\mu$S/cm')
subplot4.set_ylabel('Error in Conductivity, $\mu$S/cm')
figure4.show()

figure5, subplot5 = plt.subplots()
subplot5.plot(Cond, PercentError1, 'ro')
subplot5.plot(Cond, PercentError2, 'bo')
subplot5.set_xlabel('Conductivity, $\mu$S/cm')
subplot5.set_ylabel('Percent Error in Conductivity')
subplot5.set_ylim([-8,8])
subplot5.set_xscale('log')
figure5.show()
