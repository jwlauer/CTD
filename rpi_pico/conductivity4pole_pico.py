"""A four-pole conductivity sensor containing a thermistor.

"""

import machine
from machine import Pin, ADC
import time
import math
import array as arr

class cond_sensor:
    """A class for interacting with a four-pole conductivity sensor and thermistor.

    Performs measurement using the analog to digial converter
    to read values of voltage drop across the two inner electrodes 
    (when excited by a square wave applied to two outer electrodes) 
    and to read values from the thermistor.  Also includes methods for
    converting readings to physical values, based on calibration
    parameters specified when instantiated. Requires following import statements::
	
        import machine
        from machine import Pin, ADC
        import time
        import math
        import array as arr
    
    Parameters
    ----------
    gpio1 : :obj:'machine.Pin(pinid, Pin)'
        Power/ground pin connected directly to current balancing resistor R1
    gpio2 : :obj:'machine.Pin(pinid, Pin)'
        Power/ground pin connected to current measuring resistor R1
    adc1 : :obj:'machine.ADC(pinid)'
        ADC pin connected to electrode 3 (sensing pole farthest from current measuring resistor)
    adc2 : :obj:'machine.ADC(pinid)'
        ADC pin connected to electrod 4 (sensing pole closest to current measuring resistor)
    adc3_current : :obj:'machine.ADC(pinid)'
        ADC pin connected between conductivity resistor and conductivity electrode
    con_resistance: float
        Resistance (ohm) of current measuring resistor 
    cell_const : float
        Cell constant (1/cm), found through calibration
    b : float
        Intercept in linear calibration equation
       
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
    >>> import conductivity4pole_pico
    >>> gpio1 = Pin(19,Pin.OUT)
    >>> gpio2 = Pin(20,Pin.OUT)
    >>> adc1 = ADC(26)
    >>> adc2 = ADC(27)
    >>> adc3_current = ADC(28)
    >>> res = 250
    >>> cell_const = 1
    >>> b = 0
    >>> Sensor1 = conductivity4pole_pico.cond_sensor(gpio1,gpio2,adc1,adc2,adc3_current,res,cell_const,b)
    >>> Sensor1.calibrate()
    >>> #run external calibration to get cell constant and intercept b
    >>> Sensor1.cell_const = 1 #enter correct values here
    >>> Sensor1.b = 0
    >>> Sensor1.measure()

    """
    
        
    def __init__(self, gpio1, gpio2, adc1, adc2, adc3_current, con_resistance, cell_const, b):
        
        self.gpio1 = gpio1
        self.gpio2 = gpio2
        self.adc1 = adc1
        self.adc2 = adc2
        self.adc3_current = adc3_current
        self.con_resistance = con_resistance
        self.cell_const = cell_const
        self.b = b
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
        for i in range(n):
            self.gpio1.high()
            time.sleep_us(on1)
            imeas1[i] = (self.adc3_current.read_u16() >> 4)
            p3meas1[i] = (self.adc1.read_u16() >> 4)
            p4meas1[i] = (self.adc2.read_u16() >> 4)
            self.gpio1.low()
            time.sleep_us(off1)
            
            self.gpio2.high()
            time.sleep_us(on2)
            imeas2[i] = (self.adc3_current.read_u16() >> 4)
            p3meas2[i] = (self.adc1.read_u16() >> 4)
            p4meas2[i] = (self.adc2.read_u16() >> 4)
            self.gpio2.low()
            time.sleep_us(off2)

        endtime = time.ticks_us()
        elapsed_time = endtime - starttime            

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
        
        #clean data by sampling middle two quartiles       
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
        #self.T = thermistor_ac.temperature(self.adc_therm, self.therm_power, self.therm_ground, self.therm_resistance, 400)        
        #self.k = self.conductivity(self.resistance2,self.A,self.B,self.C)
        #self.S = self.salinity(self.T, self.k)
        #self.k25 = self.k25(self.k,self.T)
            
        if printflag:
            for i in range (n):
                print('R1 = %s, R2 = %s, V1 = %s, V2 = %s, i1 = %s, i2 = %s, p3count1 = %s, p3count2 = %s, p4count1 = %s, p4count2 = %s' % (R1[i], R2[i], V1[i], V2[i], i1[i], i2[i], p3meas1[i], p3meas2[i], p4meas1[i], p4meas2[i]))
            print('elapsed time = %s micro seconds' % (elapsed_time))
            print('speed = %s Hz' % (n/elapsed_time*1000000))
            
        return(self.resistance1, self.resistance2, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2)

    def calibrate(self):
        """
        Record calibration data.

        Prompts user to enter data about calibration standard, then makes measurement and 
        saves results to user-specified file.
        """
        fname = input('Enter file name: ')
        headerline = 'EC_from_standard,Count1,Computed R1,Count2,Computed R2,Temperature\r\n'
        f = open(fname,'w')
        f.write(headerline)
        f.close()

        n = int(input('Enter number of samples to test: '))
        for i in range(n):
            k_cal = float(input('Enter conductivity for standard calibration fluid: '))
            std_temp = float(input('Enter temperature of standard calibration fluid: '))
            input('Now place probe in fluid and press enter when ready')
            self.measure()
            textline = ('%s,%s,%s,%s,%s\r\n' % (k_cal,self.count1,self.r1,self.count2,self.r2,std_temp))
            print(textline)
            f = open(fname,'a')
            print(f.write(textline))
            f.close()
            time.sleep(0.5)
            
