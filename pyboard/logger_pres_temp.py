import machine
import pyb
import time
from pyb import Pin, ADC
import pressure
import math
import array as arr
import time

def log(t):
    """ A function for logging data from an MS5803 sensor to file at a regular interval.
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
	
    >>> import logger_pres_temp as logger
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
    red = pyb.LED(1)
    green = pyb.LED(2)
    yellow = pyb.LED(3)
    blue = pyb.LED(4)
    
    green.on()
    blue.on()
    #wait 10 seconds to allow user to jump in
    time.sleep(10)
    green.off()
    blue.off()
    
    #write file header
    outputtxt = 'date,time,pressure(mbar),temperature(C)\r\n'
    try:
        f = open('datalogCTD.txt','a')
        f.write(outputtxt)
        f.close()
    except:
        #briefly turn all leds on if fails to write
        red.on()
        green.on()
        yellow.on()
        blue.on()
        time.sleep(1)
        red.off()
        green.off()
        blue.off()
        yellow.off()
    
    start_time = time.time()
    
    while True:

        try:
            wdt.feed()
        except:
            pass
                  
        #flash LED to let user know reading is being taken
        green.off()
        time.sleep(0.5)
        green.on()

        #define clock object, set next wakeup time (in milliseconds) and get the time
        rtc = pyb.RTC()
        datetime = rtc.datetime()
        log_time = start_time + t
        start_time = log_time

        try:
            wdt.feed()
        except:
            pass
            
        #define pressure sensor in Pressure.py.  Connect SCL to X9, SDA to X10, VCC to Y7, GND to Y8
        pres_power = Pin('Y7', Pin.OUT_PP)
        pres_gnd = Pin('Y8', Pin.OUT_PP)
        i2c = machine.I2C(scl='Y10', sda='Y9', freq = 100000)
                    
        #write header in textfile
        #headerline = 'YY/MM/DD,Hour:Min:Sec,count1,count2,r1,r2,temp,pressure\r\n'
        #f = open('datalogDuw.txt','a')
        #f.write(headerline)
        #f.close()

        #read values from sensors
        try:
            [pres, ctemp] = pressure.MS5803(i2c, pres_power, pres_gnd)
        except:
            pres = -999
            ctemp = -999
            print('Pressure reading failed')
            yellow.on()
            time.sleep(1)
            yellow.off()
        try:
            wdt.feed()
        except:
            pass
        
        #write results to file
        outputtxt = ('%s/%s/%s,%s:%s:%s,' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6]))
        outputtxt += ('%s,%s\r\n' % (pres, ctemp))
        print (outputtxt)
        try:
            f = open('datalogCTD.txt','a')
            f.write(outputtxt)
            f.close()
        except:
            #briefly turn all leds on if fails to write
            red.on()
            green.on()
            yellow.on()
            blue.on()
            time.sleep(1)
            red.off()
            green.off()
            blue.off()
            yellow.off()
            
        sw = pyb.Switch()    
        while time.time() < log_time:    
            try:
                wdt.feed()
            except:
                pass          
            green.on()
            time.sleep(0.005)
            green.off()
            if sw():
                pyb.usb_mode(None)
                yellow.on()
                time.sleep(5)
                pyb.usb_mode('VCP+MSC')
                try:
                    wdt.feed()
                except:
                    pass
                break
            rtc.wakeup(2000)
            pyb.stop()
            
