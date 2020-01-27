#This code reads temperature from a 10K thermistor using a pyboard.
#The thermistor is a Littlefuse PS103J2
#https://www.littelfuse.com/~/media/electronics/datasheets/leaded_thermistors/littelfuse_leaded_thermistors_interchangeable_thermistors_standard_precision_ps_datasheet.pdf.pdf
#Input parameters:
#adc_pin:  Any pin connected to an analog to digital converter on a pyboard
#R (optinoal): Value of the fixed resistor in the resistor divider. Default is 20,000 ohm.
#n (optional): Number of readings to make--returns average of middle two quartiles. Defaults to 100.
#power_pin (optional): If a digital pin is to be used to power the thermistor.  Note that the
#thermistor may also be powered by the 3.3V pin.  In that case, this argument is not required.

import math
import array as arr
import time
from pyb import Pin, ADC

def temperature(analog_pin, power_pin = None, ground_pin = None, R = 20000, n = 100):    

    #Define constants for conversion
    A = 0.001125308852122
    B = 0.000234711863267
    C = 0.000000085663516
    
    #Allocate array for storing temperature readings
    T = arr.array('f',[0]*n)

    #Turn on the power if necessary, then wait a moment
    if power_pin is not None: power_pin.off()
    time.sleep_ms(1)

    #Turn off the ground if necessary, then wait a moment
    if ground_pin is not None: ground_pin.off()
    time.sleep_ms(1)

    #Loop through readings, computing thermistor resistance
    #and temperature, then storing in array
    for i in range(n):
        
        #if possible, switch current on pins to ensure
        #no net accumulation of charge if this is in parallel with pins that have a capacitance
        if power_pin is not None:
            power_pin.on()
            ontick = time.ticks_us()
            time.sleep_us(1000)
            count = analog_pin.read()
            power_pin.off()
            offtick = time.ticks_us()
            time_on = time.ticks_diff(offtick, ontick)
            power_pin.off()
            if ground_pin is not None:
                ground_pin.on()
                time.sleep_us(time_on)
                ground_pin.off()
            
        #calculate resistance and temperature, being careful not to cause an overload 
        if count>0:
            if count < 4095:
                R_t = ((count/4095)*R)/(1-count/4095)
                T[i] = 1/((A+B*(math.log(R_t)))+C*((math.log(R_t))**3))-273.15
            else:
                T[i] = -55
        else:
            T[i] =150
    #Turn the power back off if possible
    if power_pin is not None: power_pin.off()

    #Define and analyze the middle two quartiles
    upper_index = math.ceil(3*n/4)
    lower_index = math.floor(n/4)
    sampled_length = (upper_index - lower_index)
    T_mean_of_mid_quartiles = sum(sorted(T)[lower_index:upper_index])/sampled_length

    return T_mean_of_mid_quartiles
