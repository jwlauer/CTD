""" Module for executing code on embedded device

This module runs the logger program.  It flashes the blue led once, for one seccond, if there is an error, then
goes into standby and will try again after the appropriate logging interval.

"""

import pyb,time
log_interval = 30 #seconds
try:
    import logger_ctd
    logger_ctd.log(log_interval)
except:
    pyb.led(4).on()
    time.sleep(1)
    pyb.RTC.wakeup(log_interval*1000)
    pyb.standby()