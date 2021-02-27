Overview
============

This repository includes code for developing a simple conductivity, temperature, depth (CTD) sensor using a pyboard, a MS5803-05 pressure sensor, a Littlefuse PS103J2 NTC thermistor, and micropython.

Full documentation is avilable at https://ctd.readthedocs.io/en/latest/index.html.

Code is provided for 2-pole and 4-pole versions of the conductivity sensor.  The methods for interacting with and reading conductivity sensors of these configurations are defined in the conductivity2pole.py and conductivity4pole.py files, respectively.  Both utilize a pseudo-AC method for making the conductivity measurement that involves raising one pole to a voltage near 3.3V, grounding the other, taking an ADC reading, switching the 3.3V and ground pins, and repeating a number of times. For conductivities under around 10,000 \mu S/m2, the two-pole sensor appears to work, but it exhibits significant drift for higher conductivities.  Since 10,000 &alpha; /m2 is in the middle of the range of conductivities expected in many estuaries, the 4-pole version is recommended for use in those settings.  The 2-pole version may be appropriate in freshwater systems. 

The thermistor can be wired in parallel with the conductivity sensor, reducing the number of wires required for hooking it up.  However, if wired in parallel, it is necessary to operate in an alternating current mode in order to prevent polarization on the conductivity electrodes. The thermistor.py file can be used regardless of the wiring configuration. In addition, the temperature sensor on the MS5803 sensor can be used for logging temperature instead of using the thermistor.

To install, modify the file logger_ctd.py to reflect whether you prefer to use the 2-pole or 4-pole configuration and to reflect your wiring configuration. All pin definitions are specified in that file. The 4-pole version of the code requires the use of four ADC pins, two pins for powering the conductivity sensor, two pins for powering the MS5803-05 pressure sensor, and two pins for I2C communication with the MS5803-05 pressure sensor. The two-pole version requires two fewer pins.  To use the code, after making any required modifications, copy all files to an SD card and insert into the SD slot on a pyboard. The program will then run automatically. 

The logging file places the device in the low-power wait state (not deep sleep) that results in an average current consumption of around 1-2 mA. An LED flashes periodically during operation. The logging file can be modified by placing the device in deep sleep, but this proved unreliable because the device sometimes did not mount the SD card upon waking, thereby terminating the logging cycle.  This could be addressed in a future version by calling the pyboard's watchdog timer. There are notes in logger_ctd.py indicating where this can be enabled--but the main loop in that program would need to be modified.

The sensor must be calibrated using a solution of known conductivity. A calibration curve can then be fit to these observations. Python code is provided in the "calibration" folder for doing the curve fitting. 


Tested with MicroPython 1.10 on a pyboard v1.1.



