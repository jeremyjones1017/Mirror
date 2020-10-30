from matplotlib import pyplot as plt
import pandas as pd
import datetime
from datetime import timedelta
import matplotlib.dates as mdates

def main():
	fig, ax = plt.subplots()
	
	do_plot(ax,'today','office')
	do_plot(ax,'today','cassian_room')
	do_plot(ax,'yesterday','office')
	do_plot(ax,'yesterday','cassian_room')
	#plt.fmt_xdata = mdates.DateFormatter('%H:%M')
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
	plt.legend()
	plt.show()
	
def do_plot(ax,date_name,location):
	if location == 'office':
		fmt_str = 'k'
	elif location == 'cassian_room':
		fmt_str = 'r'
	if date_name == 'today':
		date = datetime.datetime.now()
		alf = 1.0
	elif date_name == 'yesterday':
		date = datetime.datetime.now() - datetime.timedelta(days=1)
		alf = 0.2
	df = pd.read_csv('/export/temp_records/{}/{}_{}_{}_temp_hum.txt'.format(location,date.year,date.month,date.day),delimiter='\t')
	times = list(df.Time)
	times = [datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') for time in times]
	if date_name == 'yesterday':
		times = [time + datetime.timedelta(days=1) for time in times]
	
	ax.plot(times,df.Temp_F,fmt_str,alpha = alf,label='{} ({})'.format(location,date_name))

if __name__ == '__main__':
	main()
