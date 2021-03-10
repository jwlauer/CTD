"""
A two-pole conductivity sensor containing a thermistor.

"""

import pyb
from pyb import Pin, ADC
import time
import math
import array as arr
import thermistor_ac

class Cond_sensor:
    """
    A class for interacting with a two-pole conductivity sensor and thermistor.

    Performs measurement using the analog to digial controller
    to read values of voltage drop across the probe and to
    read values from the thermistor.  Also includes methods for
    converting readings to physical values, based on calibration
    parameters specified when instantiated. Requires following
    import statements::
	
        import pyb
        from pyb import Pin, ADC
        import time
        import math
        import array as arr
        import thermistor

    Parameters
    ----------
    p_1 : :obj:'pyb.Pin(pinid, Pin.OUT_PP)'
        Power/ground pin connected to electrode through resistor, on ADC side of conductivity cell
    p_2 : :obj:'pyb.Pin(pinid, Pin.OUT_PP)'
        Power/ground pin connected to electrode through resistor to electrode NOT on ADC side of conductivity cell
    con_adc : :obj:'pyb.ADC(pinid)'
        ADC pin connected between conductivity resistor and conductivity electrode.  
        On pyboard, ADC can be the following pins 
        (unshielded):  X1,X2,X3,X4,X5,X6,X7,X8,X11,X12,Y11,Y12. Also, the
        shielded ADC pins are X19,X20,X21,X22.
    con_resistance : float
        Resistance (ohms) of sensing resistors for conductivity
    therm_adc : :obj:'pyb.ADC(pinid)' 
        ADC pin connected between thermistor resistor and thermistor
    therm_resistance : float
        Resistance in measurement circuit for 10KOhm Thermistor
    A : float
        Calibration coefficient A
    B : float
        Calibration coefficient B
    C : float
        Calibration coefficient C
    therm_power : obj:'pyb.Pin(pinid, Pin.OUT_PP'), optional
        Power pin for thermistor used to power thermistor, on ADC side of thermister cell.  
        Defaults to none (power from 3.3V).
    therm_ground : obj:'pyb.Pin(pinid, Pin.OUT_PP'), optional
        Ground pin for thermistor. Defaults to none (use if hardwired to ground).
        
    Attributes
    ----------        
    count1 : float
        Average value of middle two quartiles of ADC counts for +V applied to resistor
    count2 : float
        Average value of middle two quartiles of ADC counts for +V applied to probe
    R1 : float
        Apparent resistance of cell computed from count1 
    R2 : float
        Apparent resistance of cell computed from count2
    T : float
        Temperature (degrees C)
    k : float
        Conductivity (uS/cm)
    S : float
        Salinity

    Example
    -------
    >>> p1 = Pin('Y3', Pin.OUT_PP)
    >>> p2 = Pin('Y4', Pin.OUT_PP)
    >>> t1 = Pin('Y2', Pin.OUT_PP)
    >>> t2 = Pin('Y5', Pin.OUT_PP)
    >>> adc1 = ADC('X1')
    >>> adc2 = ADC('X2')
    >>> Res = 1000
    >>> A = 1
    >>> B = 1
    >>> C = 1
    >>> TRes = 10000
    >>> Sensor1 = cond_sensor(p1,p2,adc1,Res,adc2,TRes,A,B,C,t1)
    >>> Sensor1.calibrate()
    >>> #run external calibration to get A,B,C
    >>> A = 1 #enter correct values here
    >>> B = 1
    >>> C = 1
    >>> Sensor1.measure()

    """
    def __init__(self,p_1,p_2,con_adc,con_r,therm_adc,therm_r,A,B,C,therm_p=None,therm_g=None):
        self.p_1 = p_1
        self.p_2 = p_2
        self.con_adc = con_adc
        self.con_resistance = con_r
        self.therm_adc = therm_adc
        self.therm_resistance = therm_r
        self.A = A
        self.B = B
        self.C = C
        self.therm_power = therm_p
        self.therm_ground = therm_g
        self.p_1.low()
        self.p_2.low()

    def conductivity(self,r2,A,B,C):
        """
        Apply the sensor-specific conductivity calibration equation.

        Compute a sensor-specific value of conductivity from measured cell resistance
        and calibration values. Returns a sensor-specific value of conductivity
        Using the non-linear form for k that best fits our calibration data. 
        Parameters A, B, and C are all sensor-specific parameters that must
        be found by calibration.   
        
        Parameters
        ----------
        r2 : float
            Apparent resistance of the solution when the power is applied to electrode connected 
            directly to the power pin.
        A : float
            Calibration coefficient A 
        B : float
            Calibration coefficient B 
        C : float
            Calibration coefficient C 

        Returns
        -------
        float
            Calibrated conductivity.
                
        """
        k = 10**A*(r2-B)**C
        return k   

    def salinity(self,T,k):
        """
        Compute salinity for seawater and estuarine water.      
        
        Salinity computation is from Miller, Bradford, and Peters,
        USGS Water Supply Paper 2311.    
        
        Parameters
        ----------      
        T : float
            Temperature (degrees C)
        k : float
            Conductance (mS/cm) 

        Returns
        -------
        float
            Salinity (parts per thousand)
                
        """
        B0 = 0.13855E1
        B1 = -0.46485668E-1
        B2 = 0.14887785E-2
        B3 = -0.63083433E-4
        B4 = 0.25144517E-5
        B5 = -0.59600245E-7
        B6 = 0.57778085E-9
        K = B0 + B1*T + B2*T**2 + B3*T**3 + B4*T**4 + B5*T**5 + B6*T**6
        A = 0.36996/(k**(-1.07)-0.7464E-3)
        chlorinity = A * K
        salinity = 1.80655 * chlorinity
        return salinity
            
    def k25(self,k,T):
        """
        Calculate conductivity at standard temperature of 25C, for KCl or fresh water (not seawater).
        
        Given by USGS Water Supply Paper and Pawlowicz 2008.
        
        """
        return k*(1/(1+0.0191*(T-25)))
    
    def TDS(self,k25):
        """
        Calculate total dissolved solids from conductivity at 25C, from Pawlowicz 2008, which says the coefficient varies widely.
        """
        TDS = 0.65*k25
        return TDS

    def measure(self, saveflag = False,n = 100,on1 = 100, off1 = 100, on2 = 100, off2 = 100): #take a reading
        """
        Perform a measurement of conductivity across a two-pole probe.
        
        Parameters
        ----------
        saveflag : boolean, optional
            Flag to determine if output is saved for calibration, default false
        n : int, optional
            Number of adc readings to take for the measurement, default = 100
        on1 : int, optional
            Time in microseconds that power pin 1 is on before taking a reading, default = 100
        off1 : int, optional
            Time in microseconds that power pin 1 is turned off before turning on power pin, default = 100
        on2 : int, optional
            Time in microseconds that power pin 2 is on before taking a reading, default = 100
        off2 : int,optional
            Time in microseconds that power pin 2 is turned off before turning on power pin, default = 100
    
        Returns
        -------
        count1 : int
            Count from ADC1.
        resistance1 : float
            Computed resistance from ADC1.
        count2 : int
            Count from ADC2.
        resistance2 : float
            Computed restance from ADC2.
        temperature : float
            Temperature (degress C).
        conductivity : float
            Conductivity.
            
        Note
        ----
        Also sets the value for temperature, conductivity, salinity, counts, and resistances
        """        
        meas1 = arr.array('l',[0]*n)
        meas2 = arr.array('l',[0]*n)
        read1_us = arr.array('l',[0]*n)
        read2_us = arr.array('l',[0]*n)
        #startticks = time.ticks_us()
        for i in range(n):
            self.p_1.high()
            time.sleep_us(on1)
            meas1[i] = self.con_adc.read()
            self.p_1.low()
            time.sleep_us(off1)
            self.p_2.high()
            time.sleep_us(on2)
            meas2[i] = self.con_adc.read()
            self.p_2.low()
            time.sleep_us(off2)
        upper_index = math.ceil(3*n/4)
        lower_index = math.floor(n/4)
        sampled_length = (upper_index - lower_index)
        self.count1 = sum(sorted(meas1)[lower_index:upper_index])/sampled_length
        self.count2 = sum(sorted(meas2)[lower_index:upper_index])/sampled_length
        self.r1 = self.con_resistance*((2*self.count1/4095)-1)/(1-self.count1/4095)
        self.r2 = self.con_resistance*(4095/self.count2-2)
        
        #call thermistor reading, with 400 adc readings per measurement
        self.T = thermistor_ac.temperature(self.therm_adc, self.therm_power, self.therm_ground, self.therm_resistance, 400)        
        self.k = self.conductivity(self.r2,self.A,self.B,self.C)
        self.S = self.salinity(self.T, self.k)
        #self.k25 = self.k25(self.k,self.T)     

        return(self.count1, self.r1, self.count2, self.r2, self.T, self.k)

    def calibrate(self):
        """
        Record calibration data.

        Prompts user to enter data about calibration standard, then makes measurement and 
        saves results to user-specified file.
        """
        fname = input('Enter file name: ')
        headerline = 'Sonde,Count1,Computed R1,Count2,Computed R2,Temperature\r\n'
        f = open(fname,'w')
        f.write(headerline)
        f.close()

        n = int(input('Enter number of samples to test: '))
        for i in range(n):
            k_cal = float(input('Enter conductivity for standard calibration fluid: '))
            input('Now place probe in fluid and press enter when ready')
            self.measure()
            textline = ('%s,%s,%s,%s,%s,%s\r\n' % (k_cal,self.count1,self.r1,self.count2,self.r2,self.T))
            print(textline)
            f = open(fname,'a')
            print(f.write(textline))
            f.close()
            time.sleep(0.5)
            
p1 = Pin('X1', Pin.OUT_PP)
p2 = Pin('X2', Pin.OUT_PP)
t1 = Pin('X1', Pin.OUT_PP)
t2 = Pin('X2', Pin.OUT_PP)
adc1 = ADC('X3')
adc2 = ADC('X4')
Res = 1000
A = 1
B = 1
C = 1
TRes = 20000
Sensor1 = Cond_sensor(p1,p2,adc1,Res,adc2,TRes,A,B,C,t1)

p1 = Pin('X6', Pin.OUT_PP)
p2 = Pin('X5', Pin.OUT_PP)
t1 = Pin('X6', Pin.OUT_PP)
t2 = Pin('X5', Pin.OUT_PP)
adc1 = ADC('X7')
adc2 = ADC('X8')
Res = 1000
A = 1
B = 1
C = 1
TRes = 20000
Sensor2 = Cond_sensor(p1,p2,adc1,Res,adc2,TRes,A,B,C,t1)

p1 = Pin('X20', Pin.OUT_PP)
p2 = Pin('X19', Pin.OUT_PP)
t1 = Pin('X20', Pin.OUT_PP)
t2 = Pin('X19', Pin.OUT_PP)
adc1 = ADC('X21')
adc2 = ADC('X22')
Res = 1000
A = 1
B = 1
C = 1
TRes = 20000
Sensor3 = Cond_sensor(p1,p2,adc1,Res,adc2,TRes,A,B,C,t1)

p1 = Pin('X10', Pin.OUT_PP)
p2 = Pin('X9', Pin.OUT_PP)
t1 = Pin('X10', Pin.OUT_PP)
t2 = Pin('X9', Pin.OUT_PP)
adc1 = ADC('X11')
adc2 = ADC('X12')
Res = 1000
A = 1
B = 1 
C = 1
TRes = 20000
Sensor4 = Cond_sensor(p1,p2,adc1,Res,adc2,TRes,A,B,C,t1)
