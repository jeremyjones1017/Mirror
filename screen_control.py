#!/usr/bin/python3

import datetime
import os

def main():
	now = datetime.datetime.now()
	turn_off_time = now.replace(hour=23,minute=0,second=0,microsecond=0)
	if now.weekday() == 6:
		turn_on_time = now.replace(hour=13,minute=0,second=0,microsecond=0)
	else:
		turn_on_time = now.replace(hour=7,minute=0,second=0,microsecond=0)
	
	turn_screen_off = 'vcgencmd display_power 0'
	turn_screen_on = 'vcgencmd display_power 1'
	
	if now > turn_off_time:
		os.system(turn_screen_off)
	elif now < turn_on_time:
		os.system(turn_screen_off)
	else:
		os.system(turn_screen_on)

if __name__ == '__main__':
	main()