import pyb
from pyb import Pin, ADC
import time
import math

p_1 = Pin('Y3', Pin.OUT_PP)
p_1.low()
p_2 = Pin('Y4', Pin.OUT_PP)
p_2.low()
adc = ADC(Pin('Y11'))
#works best with 200 measurements, t = 0.001
#def measure(n,t,printflag):   #printflag = 
def measure(n,t,printflag):	#take a reading
	meas1 = []
	meas2 = [] 
	for i in range(n):
		p_2.low()
		p_1.high()
		time.sleep(t)
		read1 = adc.read()
		meas1.append(read1)
		p_1.low()
		time.sleep(20*t)
		p_2.high()
		time.sleep(t)
		read2 = adc.read()
		meas2.append(read2)
		p_2.low()
		time.sleep(20*t)
		if printflag: 
			print('%s, %s' % (read1, read2))
	upper_index = math.ceil(3*n/4)
	lower_index = math.floor(n/4)
	sampled_length = (upper_index - lower_index)
	result1 = sum(sorted(meas1)[lower_index:upper_index])/sampled_length
	result2 = sum(sorted(meas2)[lower_index:upper_index])/sampled_length
	print('result1 = %s, median1 = %s, result2 = %s, median2 = %s' % (result1, sorted(meas1)[n//2], result2, sorted(meas2)[n//2]))
	r1 = 149.8/(((4095)/result1)-1)
	r2 = 149.8*(4095-result2)/result2
	#enter input command here to read the number from the sonde
	sonde_reading = input('Type the sonde number here:')
	print('Count1 = %s, Count2 = %s, R1 = %s, R2 = %s, sonde=%s' % (result1, result2, r1, r2, sonde_reading))
	return (result1, result2)
	
#will need to define pins as an array, something like this:
adc(0) = ADC(Pin('Y11'))
p_pos(0) = Pin('Y3', Pin.OUT_PP)
p_nex(0) = Pin('Y4', Pin.OUT_PP)
adc(1) = ADC(Pin('X7'))
p_pos(1) = Pin('Y3', Pin.OUT_PP)
p_neg(1) = Pin('Y4', Pin.OUT_PP)

def calibrate(n):
	#sensor identifies the sensor index
	sonde = float(input('enter sonde value:'))
	for i in range(n):
		input('Press enter when ready to perform measurement %s' % (i))
		#measurements--need to get the measurement function to take the pin dictionary as input
		
		f = open('calibration.txt', 'a')
		f.write('%s/%s/%s,%s:%s:%s,%s,%s\r\n' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6], str(total), battery))
		f.close()

	