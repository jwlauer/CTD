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
    
    #from machine import WDT
    #wdt = machine.WDT(timeout=30000)
       #from machine import WDT
    #wdt = machine.WDT(timeout=30000)
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
        flash(1,1)
        
        log_time = start_time + t
        start_time = log_time
        
        #define conductivity sensor 
        p_1 = Pin(19, Pin.OUT)  #connected directly to electrode
        p_2 = Pin(20, Pin.OUT)  #connected to resistor connected to electrode
        adc_p_3 = ADC(26)          #connected to middle pole not adjacent to
        adc_p_4 = ADC(27)          #connected to middle pole adjacent to resistor
        adc_current = ADC(28)
        #        adc_therm = ADC(28)        #Not used in pico 2040, but may be available when picos with for ADCs are released-dummy pin
        con_resistance = 250
        #        therm_resistance = 20000
        cell_const = 1     #run external calibration to get A
        b = 0     #run external calibration to get B
#        C = 1     #run external calibration to get C
#        conductivity_sensor = conductivity4pole.cond_sensor(p_1,p_2,adc_current,adc_p_3,adc_p_4,con_resistance,adc_therm,therm_resistance,A,B,C)
        conductivity_sensor = conductivity4pole_pico.cond_sensor(p_1,p_2,adc_current,adc_p_3,adc_p_4,con_resistance, cell_const, b)

        #define pressure sensor in Pressure.py.  Connect SCL to X9, SDA to X10, VCC to Y7, GND to Y8
        pres_power = Pin(18, Pin.OUT)
        #pres_gnd = Pin('Y8', Pin.OUT_PP)   #not needed since ground pin is in line i2c pins
        i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16), freq = 100000)
                    
        #read values from sensors
        try:
            [r1, r2, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2] = conductivity_sensor.measure()
            #[r1, r2] = conductivity_sensor.measure()
        except:
            [r1, r2, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2] = [-999,-999,-999,-999,-999,-999,-999,-999,-999,-999]
            #[r1, r2] = [-999,-999]
        
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
            
        while time.time() < log_time:          
            flash(1, 0.005)
            machine.lightsleep(1)
            
