import machine
import time
from machine import Pin, ADC
import pressure
import math
import array as arr
#import thermistor_ac
import conductivity4pole_pico
import time

def log(t):
    """ A function for logging data to file at a regular interval.

    The function saves a line of text at each interval representing conductivity, temperature,
    pressure. The device then goes into standby mode for interval t.  After interval t, the
    device awakes as if from a hard reset.  The function is designed to be called from
    main.py. Puts device in standby mode upon completion.

    Parameters
    ----------
    t: int
        logging interval (seconds)
    
    Example
    -------
    To log data at 30 second intervals, save the following two lines as main.py
	
    >>> import logger_ctd_nothermistor_pico as logger
    >>> logger.log(30)
	
    Note
    ----
    For more robust logging, the lines related to the watchdog timer can be enabled
    by removing the comments.  However, once the watchdog timer is set, it will automatically
    reset the board after the watchdog timer interval unless the timer is fed. This ensures
    that the board will continue to log even if an error is encountered, but it can
    cause unexpected results if the user wishes to interact with the board over serial.

    """
    
    green = Pin(25, Pin.OUT)   
    green.value(1)

    #wait 10 seconds to allow user to jump in
    time.sleep(10)
    green.value(0)
    def flash(n,t):
        for i in range(n):
            green.value(1)
            time.sleep(t)
            green.value(0)
            time.sleep(t)
            
    #write file header
    outputtxt = 'date,time,R1(ohm),R2(ohm),temp(C),pres(mbar)\r\n'
    try:
        f = open('datalogCTD.txt','a')
        f.write(outputtxt)
        f.close()
    except:
        #short flash led if fails to write
        flash(20,0.2)
        
    start_time = time.time()   
    
    while True:
        #long single flash LED to let user know reading is being taken
        machine.freq(125000000)
        flash(1,1)
        
        log_time = start_time + t
        start_time = log_time
        
        #define conductivity sensor 
        gpio1 = Pin(19, Pin.OUT)  #connected directly to electrode
        gpio2 = Pin(20, Pin.OUT)  #connected to resistor connected to electrode
        adc1 = ADC(26)          #connected to middle pole not adjacent to
        adc2 = ADC(27)          #connected to middle pole adjacent to resistor
        adc3_current = ADC(28)
        #adc_therm = ADC(28)        #Not used in pico 2040, but may be available on other 2040 boards
        con_resistance = 250
        #therm_resistance = 20000
        cell_const = 1    
        b = 0     
        conductivity_sensor = conductivity4pole_pico.cond_sensor(gpio1,gpio2,adc1,adc2,adc3_current,con_resistance,cell_const,b)

        #define pressure sensor in Pressure.py.  
        pres_power = Pin(18, Pin.OUT)
        #pres_gnd = Pin(19, Pin.OUT_PP)   #not needed if ground pin directly connected to gnd
        i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16), freq = 100000)
                    
        #read values from sensors
        try:
            [r1, r2, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2] = conductivity_sensor.measure(n = 50)
        except:
            [r1, r2, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2] = [-999,-999,-999,-999,-999,-999,-999,-999,-999,-999]
        
        try:
            [pres, ctemp] = pressure.MS5803(i2c, pres_power)
        except:
            pres = -999
            ctemp = -999
            print('Pressure reading failed')
            flash(5,.2)
        
        #write results to file
        #outputtxt = ('%s/%s/%s,%s:%s:%s,' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6]))
        outputtxt = ('%s,' % start_time)
        outputtxt += ('%5.2f,%5.2f,' % (r1, r2))
        outputtxt += ('%s,' % ctemp)
        outputtxt += ('%s\r\n' % pres)
        print (outputtxt)
        try:
            f = open('datalogCTD.txt','a')
            f.write(outputtxt)
            f.close()
            flash(3,0.5)
        except:
            flash(20,0.2)
        
        machine.freq(10000000)
        while time.time() < log_time:          
            flash(1, 0.05)
            green.value(0)
            time.sleep(1)
            #machine.lightsleep(1)
            
