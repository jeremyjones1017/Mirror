from matplotlib import pyplot as plt
import pandas as pd
import datetime
from datetime import timedelta

def main():
	now = datetime.datetime.now()
	today_df = pd.read_csv('records/{}_{}_{}_temp_hum.txt'.format(now.year,now.month,now.day),delimiter='\t')
	yesterday = now - datetime.timedelta(days=1)
	yest_df = pd.read_csv('records/{}_{}_{}_temp_hum.txt'.format(yesterday.year,yesterday.month,yesterday.day),delimiter='\t')
	
	today_times = list(today_df.Time)
	today_times = [datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') for time in today_times]
	
	yest_times = list(yest_df.Time)
	yest_times = [datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') for time in yest_times]
	
	plt.plot(today_times,today_df.Temp_F,'k-')
	plt.plot(yest_times,yest_df.Temp_F,'r-')
	
	plt.show()
	
if __name__ == '__main__':
	main()
