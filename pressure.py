def MS5803(i2c, power_pin=None, ground_pin=None):
    """ A function for reading pressure and temperature from an MS5803 sensor.
    
    The function assumes that the MS5803 is hooked up according to instructions at
    https://thecavepearlproject.org/2014/03/27/adding-a-ms5803-02-high-resolution-pressure-sensor/.
    Power and ground should be connected through a 100 nf (104) decoupling capacitor, and CSB
    should be pulled high using a 10 kOhm resistor.
    
    Code modified from https://github.com/ControlEverythingCommunity/MS5803-05BA/blob/master/Python/MS5803_05BA.py
    Distributed with a free-will license.
    Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
    MS5803_05BA
    
    Args:
        i2c: an I2C bus object
        power_pin: the pin object representing the pin used to power the MS5803 (optional)
        ground_pin: the pin object representing the pin used to ground the MS5803 (optional)

    Returns:
        Tuple containing pressure (hPa) and temperature (degrees C).
    
    Example:
        import pressure
        from machine import I2C, Pin
        i2c = I2C(scl='X9', sda='X10', freq = 100000)
        power_pin = Pin('Y7', Pin.OUT_PP)
        ground_pin = Pin('Y8', Pin.OUT_PP)
        [pres, ctemp] = pressure.MS5803(i2c, power_pin, ground_pin)
    """
    import time
    
    #turn on power and turn off ground if necessary
    if not(power_pin is None):
        power_pin.value(1)
        
    if not(ground_pin is None):
        ground_pin.value(0)
        
    #check if device is connected--should be at address 118
    #i2c.scan()
    
    # MS5803_05BA address, 0x76(118)
    #       0x1E(30)    Reset command
    reset_command = bytearray([0x1E])
    i2c.writeto(0x76, reset_command)

    time.sleep(0.5)

    # Read 12 bytes of calibration data
    # Read pressure sensitivity
    data = bytearray(2)
    data = i2c.readfrom_mem(0x76, 0xA2, 2)
    C1 = data[0] * 256 + data[1]

    # Read pressure offset
    data = i2c.readfrom_mem(0x76, 0xA4, 2)
    C2 = data[0] * 256 + data[1]

    # Read temperature coefficient of pressure sensitivity
    data = i2c.readfrom_mem(0x76, 0xA6, 2)
    C3 = data[0] * 256 + data[1]

    # Read temperature coefficient of pressure offset
    data = i2c.readfrom_mem(0x76, 0xA8, 2)
    C4 = data[0] * 256 + data[1]

    # Read reference temperature
    data = i2c.readfrom_mem(0x76, 0xAA, 2)
    C5 = data[0] * 256 + data[1]

    # Read temperature coefficient of the temperature
    data = i2c.readfrom_mem(0x76, 0xAC, 2)
    C6 = data[0] * 256 + data[1]

    # MS5803_05BA address, 0x76(118)
    #       0x40(64)    Pressure conversion(OSR = 256) command
    pressure_command = bytearray([0x40])
    i2c.writeto(0x76, pressure_command)

    time.sleep(0.5)

    # Read digital pressure value
    # Read data back from 0x00(0), 3 bytes
    # D1 MSB2, D1 MSB1, D1 LSB
    value = bytearray(3)
    value = i2c.readfrom_mem(0x76, 0x00, 3)
    D1 = value[0] * 65536 + value[1] * 256 + value[2]

    # MS5803_05BA address, 0x76(118)
    #       0x50(64)    Temperature conversion(OSR = 256) command
    temperature_command = bytearray([0x50])
    i2c.writeto(0x76, temperature_command)
    time.sleep(0.5)

    # Read digital temperature value
    # Read data back from 0x00(0), 3 bytes
    # D2 MSB2, D2 MSB1, D2 LSB

    value = i2c.readfrom_mem(0x76, 0x00, 3)
    D2 = value[0] * 65536 + value[1] * 256 + value[2]

    dT = D2 - C5 * 256
    TEMP = 2000 + dT * C6 / 8388608
    OFF = C2 * 262144 + (C4 * dT) / 32
    SENS = C1 * 131072 + (C3 * dT ) / 128
    T2 = 0
    OFF2 = 0
    SENS2 = 0

    if TEMP > 2000 :
        T2 = 0
        OFF2 = 0
        SENS2 = 0
    elif TEMP < 2000 :
        T2 = 3 * (dT * dT) / 8589934592
        OFF2 = 3 * ((TEMP - 2000) * (TEMP - 2000)) / 8
        SENS2 = 7 * ((TEMP - 2000) * (TEMP - 2000)) / 8
        if TEMP < -1500 :
            SENS2 = SENS2 + 3 * ((TEMP + 1500) * (TEMP +1500))

    TEMP = TEMP - T2
    OFF = OFF - OFF2
    SENS = SENS - SENS2
    pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
    cTemp = TEMP / 100.0
    fTemp = cTemp * 1.8 + 32

    # Output data to screen
    print("Pressure : %.2f mbar" %pressure)
    print("Temperature in Celsius : %.2f C" %cTemp)
    print("Temperature in Fahrenheit : %.2f F" %fTemp)
    
    if not(power_pin is None):
        power_pin.value(0)
        
    return([pressure, cTemp])
