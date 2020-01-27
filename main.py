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