import machine
import pyb
import time
from pyb import Pin, ADC
import pressure
import math
import array as arr
import thermistor_ac
import conductivity4pole
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
	
    >>> import logger
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
    
    while True:
            #keep track of elapsed time
        start_time = time.time()
        log_time = start_time + t
        try:
            wdt.feed()
        except:
            pass
            
        
        #define clock object, set next wakeup time (in milliseconds) and get the time
        rtc = pyb.RTC()
        datetime = rtc.datetime()

        #light up LED to let user know it is on
        led = pyb.LED(2)
        led.on()

        #wait 15 seconds to allow user to jump in
        time.sleep(5)

        #flash LED to let user know reading is being taken
        led.off()
        time.sleep(0.5)
        led.on()

        #define clock object, set next wakeup time (in milliseconds) and get the time
        rtc = pyb.RTC()
        datetime = rtc.datetime()

        #define conductivity sensor 
        p_1 = Pin('X3', Pin.OUT_PP)  #connected directly to electrode
        p_2 = Pin('X4', Pin.OUT_PP)  #connected to resistor connected to electrode
        adc_current = ADC('X7')
        adc_p_3 = ADC('X5')          #connected to middle pole not adjacent to
        adc_p_4 = ADC('X6')          #connected to middle pole adjacent to resistor
        adc_therm = ADC('X8')
        con_resistance = 250
        therm_resistance = 20000
        A = 1     #run external calibration to get A
        B = 1     #run external calibration to get B
        C = 1     #run external calibration to get C
        t_1 = Pin('X3', Pin.OUT_PP)
        t_2 = Pin('X4', Pin.OUT_PP)
        conductivity_sensor = conductivity4pole.cond_sensor(p_1,p_2,adc_current,adc_p_3,adc_p_4,con_resistance,adc_therm,therm_resistance,A,B,C,t_1,t_2)

        try:
            wdt.feed()
        except:
            pass
            
        #define pressure sensor in Pressure.py.  Connect SCL to X9, SDA to X10, VCC to Y7, GND to Y8
        pres_power = Pin('Y7', Pin.OUT_PP)
        pres_gnd = Pin('Y8', Pin.OUT_PP)
        i2c = machine.I2C(scl='X9', sda='X10', freq = 100000)
                    
        #write header in textfile
        #headerline = 'YY/MM/DD,Hour:Min:Sec,count1,count2,r1,r2,temp,pressure\r\n'
        #f = open('datalogDuw.txt','a')
        #f.write(headerline)
        #f.close()

        #read values from sensors
        try:
            [r1, r2, T, k, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2] = conductivity_sensor.measure()
        except:
            [r1, r2, T, k, icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2] = [-999,-999,-999,-999,-999,-999,-999,-999,-999,-999]
        try:
            [pres, ctemp] = pressure.MS5803(i2c, pres_power, pres_gnd)
        except:
            pres = -999
            ctemp = -999
            print('Pressure reading failed')
        try:
            wdt.feed()
        except:
            pass
            
        
        #write results to file
        outputtxt = ('%s/%s/%s,%s:%s:%s,' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6]))
        outputtxt += ('%5.2f,%5.2f,' % (r1, r2))
        outputtxt += ('%s,' % T)
        outputtxt += ('%s, %s, %s, %s, %s, %s,' % (icount1, probe3count1, probe4count1, icount2, probe3count2, probe4count2))
        outputtxt += ('%s\r\n' % pres)
        print (outputtxt)
        try:
            f = open('datalogCTD.txt','a')
            f.write(outputtxt)
            f.close()
        except:
            led1 = pyb.LED(1)
            led1.on()
            led2.on()
            led3 = pyb.LED(3)
            led.on()
            led4 = pyb.LED(4)
            led.on()
            time.sleep(1)
            
        sw = pyb.Switch()    
        while time.time() < log_time:    
            try:
                wdt.feed()
            except:
                pass          
            led.on()
            time.sleep(0.005)
            led.off()
            if sw():
                pyb.usb_mode(None)
                pyb.LED(3).on()
                time.sleep(5)
                pyb.usb_mode('VCP+MSC')
                try:
                    wdt.feed()
                except:
                    pass
                break
            rtc.wakeup(2000)
            pyb.stop()
            
