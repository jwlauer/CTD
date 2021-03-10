"""A four-pole conductivity sensor containing a thermistor.

"""

import pyb
from pyb import Pin, ADC
import time
import math
import array as arr
import thermistor_ac

class cond_sensor:
    """A class for interacting with a four-pole conductivity sensor and thermistor.

    Performs measurement using the analog to digial converter
    to read values of voltage drop across the two inner electrodes 
    (when excited by a square wave applied to two outer electrodes) 
    and to read values from the thermistor.  Also includes methods for
    converting readings to physical values, based on calibration
    parameters specified when instantiated. 
    
    Parameters
    ----------
    gpio1 : :obj:'pyb.Pin(pinid, Pin.OUT_PP)'
        Power/ground pin connected directly to current balancing resistor R1
    gpio2 : :obj:'pyb.Pin(pinid, Pin.OUT_PP)'
        Power/ground pin connected to current measuring resistor R1
    adc1 : :obj:'pyb.ADC(pinid)'
        ADC pin connected to pole 3 (sensing pole farthest from current measuring resistor)
    adc2 : :obj:'pyb.ADC(pinid)'
        ADC pin connected to pole 4 (sensing pole closest to current measuring resistor)
    adc3_current : :obj:'pyb.ADC(pinid)'
        ADC pin connected between conductivity resistor and conductivity electrode
    adc4_therm : :obj:'pyb.ADC(pinid)'
        ADC pin connected between thermistor resistor and thermistor
    con_resistance: float
        Resistance (ohm) of current measuring resistor 
    therm_resistance : float
        Resistance in measurement circuit for 10KOhm Thermistor
    cell_const : float
        Cell constant (1/cm) of conductivity probe (found by calibration)
    b : float
        Intercept in linear calibration equation
    therm_power : obj:'pyb.Pin(pinid, Pin.OUT_PP'), optional
        Power pin used to power thermistor.  Defaults to none (power from 3.3V).
    therm_ground : :obj:'pyb.Pin(pinid, Pin.OUT_PP'), optional
        Ground pin used to ground thermistor.  Defaults to none (directly wired to ground).
        
    Attributes
    ----------     
    resistance1 : float
        Apparent resistance computed from count1 
    resistance2 : float
        Apparent resistance computed from count2
    T : float
        Temperature (degrees C)
    k : float
        Conductivity (uS/cm)
    S : float
        Salinity
    
    Example
    -------
    >>> gpio1 = Pin('X3', Pin.OUT_PP)
    >>> gpio2 = Pin('X4', Pin.OUT_PP)
    >>> t_1 = gpio1  #may be same pin as connected to charged electrode
    >>> t_2 = gpio2  #may be same pin as connected to charged electrode
    >>> adc1 = ADC('X5')
    >>> adc2 = ADC('X6')
    >>> adc3_current = ADC('X7')
    >>> adc4_therm = ADC('X8')
    >>> res = 250
    >>> cell_const = 1
    >>> b = 0
    >>> tres = 20000
    >>> Sensor1 = cond_sensor(gpio1,gpio2,adc1,adc2,adc3_current,adc4_therm,res,tres,cell_const,b,t_1,t_2)
    >>> Sensor1.calibrate()
    >>> #run external calibration to get cell constant and b
    >>> cell_const = 1 #enter correct values here
    >>> b = 0
    >>> Sensor1.measure()

    """
    
        
    def __init__(self,gpio1,gpio2,adc1,adc2,adc3_current,adc4_therm,con_resistance,therm_resistance,cell_const,b,therm_power = None,therm_ground = None):
        
        self.gpio1 = gpio1
        self.gpio2 = gpio2
        self.gpio1.low()
        self.gpio2.low()
        self.adc1 = adc1
        self.adc2 = adc2
        self.adc3_current = adc3_current
        self.adc4_therm = adc4_therm
        self.con_resistance = con_resistance
        self.therm_resistance = therm_resistance
        self.cell_const = cell_const
        self.b = b
        self.therm_power = therm_power
        self.therm_ground = therm_ground
        self.gpio1.low()
        self.gpio2.low()

    def conductivity(self,r2,cell_const,b):
        """Apply the sensor-specific conductivity calibration equation.

        Compute a sensor-specific value of conductivity from measured cell resistance
        and calibration values. Returns a sensor-specific value of conductivity
        Using the linear relationship between k and calibration data
        Parameters are sensor-specific parameters that must
        be found by calibration.   
        
        Parameters
        ----------
        r2 : float
            Apparent resistance (ohms) of the solution when the power is applied to electrode connected 
            directly to the power pin.
        cell_const : float
            cell constant (1/cm). Equivalent to slope of d(EC)/dR. 
        b : float
            intercept (micro S/cm) in equation EC = 1/(cell_c*R2)+b 

        Returns
        -------
        float
            Calibrated conductivity
                
        """
        k = 1/(cell_const*r2) + b
        return k     

    def salinity(self,T,k):
        """Salinity computation for seawater and estuarine water.      
        Salinity computation is from Miller, Bradford, and Peters,
        USGS Water Supply Paper 2311.    
        
        Parameters
        ----------      
        T: float
            Temperature (degrees C)
        k: float
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

    def measure(self, printflag = False,n = 12,on1 = 0, off1 = 0, on2 = 0, off2 = 0): #take a reading
        """
        Performs a measurement of conductivity across a four-pole probe.
        
        Parameters
        ----------
        saveflag: boolean, optional
            Flag to determine if output is saved for calibration, default false
        n: int, optional
            Number of adc readings to take for the measurement, default = 12
        on1: int, optional
            time in microseconds that power pin 1 is on before taking a reading, default = 0
        off1: int, optional
            time in microseconds that power pin 1 is turned off before turning on power pin, default = 0
        on2: int, optional
            time in microseconds that power pin 2 is on before taking a reading, default = 0
        off2: int,optional
            time in microseconds that power pin 2 is turned off before turning on power pin, default = 0
            
        Returns
        -------
        resistance1 : float
            Apparent resistance computed using normal polarity.
        resistance2 : float
            Apparent resistance computed using reverse polarity.
        temperature : float
            Temperature (degrees C)
        conductivity : float
            Conductivity.
                            
        Note
        ----
        Also sets the value for temperature, conductivity, counts, and resistances
        """
        
        #pre-allocate arrays for counts to be read into
        imeas1 = arr.array('l',[0]*n)
        imeas2 = arr.array('l',[0]*n)
        p3meas1 = arr.array('l',[0]*n)
        p3meas2 = arr.array('l',[0]*n)
        p4meas1 = arr.array('l',[0]*n)
        p4meas2 = arr.array('l',[0]*n)

        starttime = time.ticks_us()
        #read1_us = arr.array('l',[0]*n)
        #read2_us = arr.array('l',[0]*n)
        #startticks = time.ticks_us()
        for i in range(n):
            #first measurement at initial polarity
            self.gpio1.high()
            time.sleep_us(on1)
            imeas1[i] = self.adc3_current.read()
            p3meas1[i] = self.adc1.read()
            p4meas1[i] = self.adc2.read()
            self.gpio1.low()
            time.sleep_us(off1)
            
            #second measurement at reverse polarity
            self.gpio2.high()
            time.sleep_us(on2)
            imeas2[i] = self.adc3_current.read()
            p3meas2[i] = self.adc1.read()
            p4meas2[i] = self.adc2.read()
            self.gpio2.low()
            time.sleep_us(off2)
        
        endtime = time.ticks_us()
        
        #pre-allocate arrays for current, voltage drop across poles, and resistance, for flow each direction
        i1 = arr.array('f',[0]*n)
        i2 = arr.array('f',[0]*n)
        V1 = arr.array('f',[0]*n)
        V2 = arr.array('f',[0]*n)
        R1 = arr.array('f',[0]*n)
        R2 = arr.array('f',[0]*n)

        #compute current, voltage, and resistance for each sample (do outside sampling loop to maintain sampling timing)
        for i in range(n):
            try:
                i1[i] = imeas1[i] / 4095 * 3.3 / self.con_resistance 
                i2[i] = (3.3 - imeas2[i] / 4095 * 3.3) / self.con_resistance
                V1[i] = (p3meas1[i] - p4meas1[i])/4095 * 3.3
                V2[i] = (p4meas2[i] - p3meas2[i])/4095 * 3.3
                R1[i] = V1[i]/i1[i]
                R2[i] = V2[i]/i2[i]
            except:
                R1[i] = -999999
                R2[i] = -999999
                print('Error in resistance computation')
                
        upper_index = math.ceil(3*n/4)
        lower_index = math.floor(n/4)
        sampled_length = (upper_index - lower_index)
        self.resistance1 = sum(sorted(R1)[lower_index:upper_index])/sampled_length
        self.resistance2 = sum(sorted(R2)[lower_index:upper_index])/sampled_length

        icount1 = sum(sorted(imeas1)[lower_index:upper_index])/sampled_length
        probe3count1 = sum(sorted(p3meas1)[lower_index:upper_index])/sampled_length
        probe4count1 = sum(sorted(p4meas1)[lower_index:upper_index])/sampled_length
        icount2 = sum(sorted(imeas2)[lower_index:upper_index])/sampled_length
        probe3count2 = sum(sorted(p3meas2)[lower_index:upper_index])/sampled_length
        probe4count2 = sum(sorted(p4meas2)[lower_index:upper_index])/sampled_length
               
        #call thermistor reading, with 400 adc readings per measurement
        self.T = thermistor_ac.temperature(self.adc4_therm, self.therm_power, self.therm_ground, self.therm_resistance, 400)        
        ave_res = (self.resistance1 + self.resistance2)/2
        self.k = self.conductivity(ave_res,self.cell_const,self.b)
        self.S = self.salinity(self.T, self.k)
        #self.k25 = self.k25(self.k,self.T)

        elapsed_time = time.ticks_diff(endtime,starttime)  
        
        if printflag:
            for i in range (n):
                print('R1 = %s, R2 = %s, V1 = %s, V2 = %s, i1 = %s, i2 = %s, p3count1 = %s, p3count2 = %s, p4count1 = %s, p4count2 = %s' % (R1[i], R2[i], V1[i], V2[i], i1[i], i2[i], p3meas1[i], p3meas2[i], p4meas1[i], p4meas2[i]))
            print('elapsed time = %s microseconds' % (elapsed_time))
            print('frequency = %s Hz' % (n/elapsed_time*1000000))
            
        return(self.resistance1, self.resistance2, self.T, self.k, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2)

    def calibrate(self):
        """
        Record calibration data.

        Prompts user to enter data about calibration standard, then makes measurement and 
        saves results to user-specified file.
        """
        fname = input('Enter file name: ')
        headerline = 'EC_from_Standard,Count1,Computed R1,Count2,Computed R2,Temperature\r\n'
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
            
