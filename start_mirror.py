#!/usr/bin/python3

import os
import csv

def main():
	mirror_active = check_mirror_state()
	print(mirror_active)
	
	if mirror_active == False:
		activate_mirror()
	
def check_mirror_state():
	mirror_command = '/home/pi/Mirror/start_mirror.py'
	ps_command = 'ps aux | grep "{}" > tmp'.format(mirror_command)
	os.system(ps_command)
	
	ps_output = []
	with open('tmp','r') as input_file:
		input_file_reader = csv.reader(input_file,delimiter = '\t')
		for line in input_file_reader:
			ps_output.append(line)
	
	os.remove('tmp')
	
	mirror_active = False
	n_open = 0
	for line in ps_output:
		if mirror_command in line[0] and 'grep' not in line[0]:
			n_open+=1
			#print('1',line)
		#else:
		#	print('0',line)
	if n_open > 1:
		mirror_active = True
	
	return mirror_active
	
def activate_mirror():
	import mirror
	mirror.main()



if __name__ == '__main__':
	main()
