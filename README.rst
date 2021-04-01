Overview
============

This repository includes code for developing a simple conductivity, temperature, depth (CTD) sensor using a `PyBoard <https://store.micropython.org/product/PYBv1.1H>`__, a `MS5803-05BA <https://www.amsys-sensor.com/products/pressure-sensor/ms5803-series-digital-absolute-pressure-sensors-up-to-1-2-5-7-14-30-bar/>`__ pressure sensor, a `Littlefuse PS103J2 <https://www.littelfuse.com/~/media/electronics/datasheets/leaded_thermistors/littelfuse_leaded_thermistors_interchangeable_thermistors_standard_precision_ps_datasheet.pdf.pdf>`__ NTC thermistor, and `MicroPython <https://micropython.org/>`__.  It contains Gerber files for a minimal circuitboard for mounting the MS5803 sensor and for simplifying wiring for the electrical conductivity sensor.  It also contains STL files for 3-d printing an optional housing for the electrodes and/or MS5803 sensor. 

Full documentation is avilable at https://ctd.readthedocs.io/en/latest/index.html.

Principle of Operation
----------------------

The electrical conductivity sensor requires no components other than a few resistors and either two or four electrodes.  Code is provided for both the 2-pole and 4-pole versions.  Both utilize a pseudo-DC method for making the electrical conductivity (EC) measurement that involves raising one electrode to a voltage near 3.3V using a digitial IO of the PyBoard, placing the other at a low digital output (close to 0V), taking an ADC reading (from which current through the circuit can be computed), and then switching the 3.3V and ground pins and repeating a number of times. A similar method is described in `NIST Special Publication 260-142 <https://www.nist.gov/system/files/documents/srm/260-142-2ndVersion.pdf>`__. For conductivities under around 10,000 μS/m\ :sup:`2`, the two-pole sensor appears to work, but it exhibits significant drift for higher conductivities.  Since 10,000 μS/m\ :sup:`2` is in the middle of the range of conductivities expected in many estuaries and is well below conductivities expected in marine environments, the 4-pole version is recommended for use in those settings.  The 2-pole version may be appropriate in freshwater systems. 

Depth is estimated based on pressure measurements made using the MS5803_05BA pressure sensor.  The MS5803 also provides a temperature signal, but provisions are also made for using an NTC thermistor for temperature measurements. The thermistor can be wired in parallel with the conductivity sensor, reducing the number of wires required for assembly.  However, if wired in parallel, thermistor measurements must be made very quickly in order to prevent polarization. 

Use of Code
-----------

To install, modify the file logger_ctd.py to reflect the EC configuration (two pole or four pole) and temperature measurement source. All pin definitions are specified in that file. The four-pole version of the code requires the use of four ADC pins, two pins for powering the conductivity sensor, two pins for powering the MS5803-05 pressure sensor, and two pins for I2C communication with the MS5803-05 pressure sensor. The two-pole version requires two fewer pins.  After making any required modifications, copy all files to the microcontroller. If using a PyBoard, all that is necessary is to copy the files to an SD card and insert into the SD slot. The program will then run automatically when the board is reset and will save the datalog file to the SD card. 

While the code has not been tested on other microcontrollers, it should be useable on any microcontroller with at least three accurate ADC pins (four if using the NTC thermistor). 

Deployment
----------

The logging file places the device in the low-power wait state (not deep sleep) that results in an average current consumption of around 1-2 mA. An LED flashes periodically during operation. The logging file can be modified to place the device in deep sleep, but this proved unreliable because the device sometimes did not mount the SD card upon waking, thereby terminating the logging cycle.  This could be addressed in a future version by calling the PyBoard's watchdog timer. There are notes in logger_ctd.py indicating where this can be enabled--but the main loop in that program would need to be modified.

Date and time are obtained from the PyBoard's Real Time Clock (RTC), which can be calibrated to an accuracy of better than several minutes per year. Setting and calibrating the clock is covered in the `MicroPython docs <https://docs.micropython.org/en/latest/library/pyb.RTC.html#pyb-rtc>`__. The PyBoard also includes a "VBACK" pin for adding a backup battery. A CR2032 battery can keep the clock running for many months (probalby years).  

Interpretation of Measurements
------------------------------

The sensor returns the apparent DC resistance between electrodes, computed using R = 3.3V / I, where I is the current estimated across the current sensing resistor. This resistance is computed for each direction of current flow and then averaged. While this DC resistance is highly correlated with electrical conductivity, it also depends in part on the geometry of the electrodes, which can vary from sensor to sensor. This means that a separate calibration curve must be developed for each sensor using a solution of known conductivity.  The calibration curve is often represented as an inverse relationship between EC and R, EC = 1/(R*k), where R is the average resistance returned by the sensor (Ohms) and k is the cell constant of the sensor (cm \ :sup:`2`) that is determined by calibration. The code includes functions to simplify collection of calibration data points. 

Code was tested with MicroPython 1.10 on a PyBoard v1.1 or MicroPython v1.14 2021/04/01 unstable release (using rp2-pico-20210401-unstable-v1.14-128-gca3d51f12) on Raspberry Pi Pico 2040.



