#!/usr/bin/python3

import mirror
import os
import csv

def main():
	mirror_active = check_mirror_state()
	
	if mirror_active == False:
		activate_mirror()
	
def check_mirror_state():
	mirror_command = 'sh -c cd /home/pi/Mirror/ && python3 mirror.py'
	#mirror_command = 'sh -c cd /home/pi/Programing/Mirror/ && python3 mirror.py w'
	ps_command = 'ps aux | grep "{}" > tmp'.format(mirror_command)
	os.system(ps_command)
	
	ps_output = []
	with open('tmp','r') as input_file:
		input_file_reader = csv.reader(input_file,delimiter = '\t')
		for line in input_file_reader:
			ps_output.append(line)
	
	os.remove('tmp')
	
	mirror_active = False
	for line in ps_output:
		if mirror_command in line[0] and 'grep' not in line[0]:
			mirror_active = True
			break
	
	return mirror_active
	
def activate_mirror():
	mirror.main()



if __name__ == '__main__':
	main()