import yfinance as yf
import pandas as pd
import json

def main():
	days_ago_list = [0,1,5,-1]
	my_stonks = pd.read_csv('stonks.txt',delimiter='\t')
	
	stonk_list = list_stonks(my_stonks)
	
	stonk_dict = get_stonk_info(stonk_list)
	
	with open('stonk_info.json','w') as outfile:
		json.dump(stonk_dict,outfile)
	
	
def list_stonks(df):
	non_unique_stonk_list = list(df.stonk)
	
	stonk_list = []
	for stonk in non_unique_stonk_list:
		if stonk not in stonk_list:
			stonk_list.append(stonk)
	
	return stonk_list

def get_stonk_info(stonk_list):
	data = yf.download(tickers=' '.join(stonk_list),period='1y',group_by='ticker')
	
	dates = list(data[stonk_list[0]].index)
	dates = [str(d)[0:10] for d in dates]
	
	stonk_dict = dict()
	stonk_dict['Date'] = dates
	
	for stonk in stonk_list:
		close_arr = list(data[stonk]['Close'])
		stonk_dict[stonk] = close_arr
	
	return stonk_dict
	
if __name__ == '__main__':
	main()