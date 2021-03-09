""" Module for executing code on embedded device

This module runs the logger program.  It flashes the blue led once, for one seccond, if there is an error, then
goes into standby and will try again after the appropriate logging interval.

"""

import machine
import time
from machine import Pin

log_interval = 30 #seconds
green = Pin(25,Pin.OUT)
green.value(1)
try:
    import logger_ctd_nothermistor_pico
    logger_ctd_nothermistor_pico.log(log_interval)
except:
    for i in range(10):
        green.value(1)
        time.sleep(1)
        green.value(0)
        time.sleep(1)
    machine.lightsleep(log_interval)