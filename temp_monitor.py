#!/usr/bin/python3

import adafruit_dht
import board
import datetime
import os

'''Records the temperature (in C and F) and Humidity of the connected DHT
probe in today's file in the records directory.

This should be run with a cron job every 5 minutes'''

def main():
	now = datetime.datetime.now()
	dirname = '/home/pi/Programing/Mirror/records'
	filename = os.path.join(dirname,'{}_{}_{}_temp_hum.txt'.format(now.year,now.month,now.day))
	
	dhtSensor = adafruit_dht.DHT22(board.D4)
	
	tc,tf,hum = get_temp_hum(dhtSensor)
	
	if os.path.exists(filename):
		with open(filename,'a') as record:
			record.write('\n{}\t{}\t{}\t{}'.format(now.strftime('%Y-%m-%d %H:%M:%S'),tc,tf,hum))
	else:
		with open(filename,'w') as record:
			record.write('Time\tTemp_C\tTemp_F\tHum')
			record.write('\n{}\t{}\t{}\t{}'.format(now.strftime('%Y-%m-%d %H:%M:%S'),tc,tf,hum))
	
def get_temp_hum(dhtSensor):
	record_done = False
	while record_done == False:
		try:
			humidity = dhtSensor.humidity
			temp_c = dhtSensor.temperature
			temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
			humidity = format(humidity,".2f")
			record_done = True
		except RuntimeError:
			continue
	
	return temp_c,temp_f,humidity
	
if __name__ == '__main__':
	main()