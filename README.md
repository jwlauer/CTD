# Conductivity
This repository includes code for developing a simple conductivity, temperature, depth (CTD) sensor using a pyboard and micropython. Code is provided for 2-pole and 4-pole versions of the conductivity sensor.  The sensor must be calibrated using a solution of known conductivity.  Because the response is not linear across the range of conductivities expected in an estuarine setting, the calibration process needs to include multiple points. A calibration curve can then be fit to these observations.

To install, modify the file logger_ctd.py to reflect whether you prefer to use the 2-pole or 4-pole configuration and to reflect your wiring configuration. The 4-pole version of the code requires the use of four ADC pins, two pins for powering the device, and two pins for I2C communication with the MS5803-05 pressure sensor. To use the code, after making any required modifications, copy all files to an SD card and insert into the SD slot on a pyboard. The program will then run automatically. 

The logging file places the device in the low-power wait state (not deep sleep) that results in an average current consumption of around 1-2 mA. An LED flashes periodically during operation. The logging file can be modified by placing the device in deep sleep, but this proved unreliable because the device sometimes did not mount the SD card upon waking, thereby terminating the logging cycle.  This could be addressed in a future version by calling the pyboard's watchdog timer. There are notes in logger_ctd.py indicating where this can be enabled--but the main loop in that program would need to be modified.

Tested with MicroPython 1.10 on a pyboard v1.1.

