import pynance as pn
import pandas as pd
import os
import datetime

def main():
	os.system('clear')
	days_ago_list = [0,20,120,250]
	stonks = stonks(days_ago_list)
	for i in stonks:
		print(i)
	
def stonks(days_ago_list):
	stonks_df = pd.read_csv('stonks/stonks.txt',delimiter='\t')
	transfers_df = pd.read_csv('stonks/money_transfers.txt',delimiter='\t')
	
	to_return = []
	
	for days_ago in days_ago_list:
		portfolio,value,date = get_current_value(stonks_df,transfers_df,days_ago)
		#print('${:,.2f}'.format(value),portfolio)
		to_return.append([portfolio,value,date])
		
	return to_return

def get_current_value(stonks_df,transfers_df,days_ago):
	#print('Values from {} days ago'.format(days_ago))
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
	
	#Add up stonk values
	cash = value
	portfolio = dict()
	stonk_value = dict()
	for index,row in stonks_df.iterrows():
		trade_date = datetime.datetime.strptime(row.trade_date,'%m-%d-%Y')
		
		this_stonk_df = pn.data.get(row.stonk)
		position_date = pd.to_datetime(this_stonk_df.index[days_ago])
		
		if position_date >= trade_date:
			close_prices = list(this_stonk_df.Close)
			
			stonk_value[row.stonk] = [list(this_stonk_df.Close)[days_ago],str(this_stonk_df.index[days_ago])[0:10]]
			
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
	#for s in portfolio:
	#	if s == 'Cash':
	#		print('{} - ${:,.2f}'.format(s,portfolio[s]))
	#	elif portfolio[s] == 1:
	#		print('{} - {} share (${:,.2f} @ {})'.format(s,portfolio[s],stonk_value[s][0],stonk_value[s][1]))
	#	elif portfolio[s] > 1:
	#		print('{} - {} shares (${:,.2f} each @ {})'.format(s,portfolio[s],stonk_value[s][0],stonk_value[s][1]))
	#print('Total portfolio value - ${:,.2f}'.format(value))
	#print('\t {:.1f}% of the input value (${:,.2f})'.format(100.*value/input_value,input_value))  
	#print('Total portfolio value {} workdays ago - ${:,.2f}'.format(days_ago,value))
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