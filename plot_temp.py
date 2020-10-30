from matplotlib import pyplot as plt
import pandas as pd
import datetime
from datetime import timedelta

def main():
	now = datetime.datetime.now()
	today_df = pd.read_csv('records/{}_{}_{}_temp_hum.txt'.format(now.year,now.month,now.day))
	yesterday = now - datetime.timedelta(days=1)
	yest_df = pd.read_csv('records/{}_{}_{}_temp_hum.txt'.format(yesterday.year,yesterday.month,yesterday.day))
	
	plt.plot(today_df.Time,today_df.Temp_F,k-)
	plt.plot(yest_df.Time,yest_df.Temp_F,r-)
	
	plt.show()
	
if __name__ == '__main__':
	main()
