# Conductivity
This repository includes code for developing a simple conductivity, temperature, depth (CTD) sensor using a pyboard and micropython. Code is provided for 2-pole and 4-pole versions of the conductivity sensor.  The sensor must be calibrated using a solution of known conductivity.  Because the response is not linear across the range of conductivities expected in an estuarine setting, the calibration process needs to include multiple points. A calibration curve can then be fit to these observations.

To use the code, simply copy all files to an SD card and insert into the SD slot on a pyboard.  Tested with MicroPython 1.10.
