import pandas as pd
import os
import datetime
import json
import math

def main():
	#days_ago_list = [0,1,5,20]
	days_ago_list = range(30)
	
	data = stonks(days_ago_list)
	
	for i in data:
		print(i[1])
	
def stonks(days_ago_list):
	stonks_df = pd.read_csv('stonks/stonks.txt',delimiter='\t')
	transfers_df = pd.read_csv('stonks/money_transfers.txt',delimiter='\t')
	
	to_return = []
	
	for days_ago in days_ago_list:
		portfolio,value,date = get_current_value(stonks_df,transfers_df,days_ago)
		to_return.append([portfolio,value,date])
		
	return to_return

def get_current_value(stonks_df,transfers_df,count_back_days_ago):
	#Add up deposits and withdrawals
	value = 0.
	for index,row in transfers_df.iterrows():
		if row.transfer_type == 'deposit':
			value += row.amount
		elif row.transfer_type == 'withdrawal':
			value -= row.amount
		else:
			print('Error in tallying transfers. The row looked like this: \n{}'.format(row))
	input_value = value
	
	days_ago = -1 - count_back_days_ago
	
	#Read downloaded file
	with open('stonks/stonk_info.json') as json_file:
		stonk_info = json.load(json_file)
	
	#Add up stonk values
	cash = value
	portfolio = dict()
	stonk_value = dict()
	for index,row in stonks_df.iterrows():
		trade_date = datetime.datetime.strptime(row.trade_date,'%m-%d-%Y')
		
		this_stonk_value = stonk_info[row.stonk]
		position_date = datetime.datetime.strptime(stonk_info['Date'][days_ago],'%Y-%m-%d')
		
		if position_date >= trade_date:
			close_prices = stonk_info[row.stonk]
			
			stonk_value[row.stonk] = [close_prices[days_ago],position_date]
			i=0
			while math.isnan(stonk_value[row.stonk][0]):
				i-=1
				stonk_value[row.stonk][0] = close_prices[days_ago-i]
			
			if row.trade_type == 'buy':
				value = value + row.shares * (stonk_value[row.stonk][0] - row.price)
				cash -= (row.price * row.shares)
			elif row.trade_type == 'sell':
				value = value + row.shares * (row.price - stonk_value[row.stonk][0])
				cash += (row.price * row.shares)
			else:
				print('Error in tallying values. The row looked like this: \n{}'.format(row))
			portfolio = update_portfolio(row,portfolio)

	portfolio['Cash'] = cash
	return portfolio,value,position_date

def update_portfolio(r,p):
	#r - row of the stonk csv
	#p - portfolio dictionary
	if r.stonk not in p:
		p[r.stonk] = r.shares
		if r.trade_type == 'sell': print('Error - first trade is a sell')
	else:
		if r.trade_type == 'buy':
			p[r.stonk] += r.shares
		elif r.trade_type == 'sell':
			p[r.stonk] -= r.shares
	return p

def get_date(n_days):
	now = datetime.datetime.now()
	today = now.replace(hour=0,minute=0,second=0,microsecond=0)
	yesterday = today - datetime.timedelta(days = 1)
	
	if n_days == 0:
		if now > now.replace(hour=18,minute=0,second=0,microsecond=0):
			date = today
		else:
			date = yesterday
	else:
		date = today - datetime.timedelta(days = n_days)
		
	while date.weekday() >= 5:
		date -= datetime.timedelta(days = 1)
	
	return date
	
if __name__ == '__main__':
	main()