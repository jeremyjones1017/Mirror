#!/usr/bin/python3

import sys
import time
import pygame
import datetime
import tkinter as tk
from datetime import timedelta
import numpy as np
import pandas as pd
from noaa_sdk import NOAA
import pytz
import wget
import os

#Colors
black=(0,0,0)
white=(255,255,255)
red=(255,0,0)
blue=(0,200,255)
orange=(255,165,0)
green=(0,255,0)
yellow=(255,255,0)
purple=(128,0,128)

def main():
	root = tk.Tk()
	pygame.init()
	FPS = 1
	if len(sys.argv) == 2:
		if sys.argv[1] == 'w':
			screen_width = 540
			screen_height = 960
			main_window = pygame.display.set_mode((screen_width,screen_height))
	else:
		screen_width = root.winfo_screenwidth()
		screen_height = root.winfo_screenheight()
		main_window = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
	
	fpsclock = pygame.time.Clock()
	pygame.mouse.set_visible(False)
	while True:
		run_mirror(main_window,FPS,fpsclock,screen_width,screen_height)
		
def run_mirror(main_window,FPS,fpsclock,screen_width,screen_height):
	bigger_font = pygame.font.Font('freesansbold.ttf',int(screen_width/15))
	big_font = pygame.font.Font('freesansbold.ttf',int(screen_width/20))
	main_font = pygame.font.Font('freesansbold.ttf',int(screen_width/60))
	small_font = pygame.font.Font('freesansbold.ttf',int(screen_width/100))
	fonts = [small_font,main_font,big_font,bigger_font]
		
	bigger_space = screen_width/15
	big_space = screen_width/20
	main_space = screen_width/45
	spaces = [main_space,big_space,bigger_space]
	
	swans_island_coords = (44.18318112881812,-68.41599063902959)
	swans_island_zip = '04685'
	i=0
	
	offline = False
	try:
		forecast = get_weather_forecast(swans_island_coords,swans_island_zip)
	except:
		offline = True
	
	
	while True:
		now = datetime.datetime.now()
		today_start = datetime.datetime(now.year, now.month, now.day,0,0,0,0)
		main_window.fill(black)
		important_dates_df = read_important_dates()
		
		
		online_time = check_online_time(now)
		
		print(online_time)
		
		if online_time:
			do_date(main_window,fonts,spaces,screen_width,screen_height,now)
			do_time(main_window,fonts,spaces,screen_width,screen_height,now)
			
			try:
				times,temps_c,temps,hum = read_records(now,'office')
				current_office_temp = int(temps[-1])
				#do_temp_plot(main_window,fonts,spaces,white,0.85*screen_width,0.1*screen_height,0.1*screen_width,0.1*screen_width,times,temps)
			except:
				times,temps_c,temps,hum = [[0],[0],[0],[0]]
				current_office_temp = '--'
			try:
				times,temps_c,temps,hum = read_records(now,'cassian_room')
				current_cas_temp = int(temps[-1])
				#do_temp_plot(main_window,fonts,spaces,blue,0.85*screen_width,0.1*screen_height,0.1*screen_width,0.1*screen_width,times,temps,axes=False)
			except:
				times,temps_c,temps,hum = [[0],[0],[0],[0]]
				current_cas_temp = '--'
			
			
			text_display(main_window,'Office',0.9*screen_width,0.02*screen_height,white,black,main_font)
			text_display(main_window,str(current_office_temp)+u'\N{DEGREE SIGN}',0.9*screen_width,0.02*screen_height+big_space,white,black,bigger_font)
			
			text_display(main_window,"Cassian's Room",0.9*screen_width,0.09*screen_height,white,black,main_font)
			text_display(main_window,str(current_cas_temp)+u'\N{DEGREE SIGN}',0.9*screen_width,0.09*screen_height+big_space,white,black,bigger_font)
			
			if not offline:
				if i%300 == 0 and i != 0:
					forecast = get_weather_forecast(swans_island_coords,swans_island_zip)
					
				temp_color = outdoor_temp_color_scale(forecast.current_temp)
				text_display(main_window,"Swans Island",0.9*screen_width,0.16*screen_height,temp_color,black,main_font)
				text_display(main_window,str(int(forecast.current_temp))+u'\N{DEGREE SIGN}',0.9*screen_width,0.16*screen_height+big_space,temp_color,black,bigger_font)
				
				forecast_space = 0
				text_display(main_window,'Today',0.15*screen_width,0.25*screen_height+forecast_space,white,black,big_font)
				forecast_space += big_space
				for ind in [2,4,6,8,10,12]:
					if len(forecast.temps) > ind+1:
						temp_color = outdoor_temp_color_scale(forecast.temps[ind])
						line_x = 0.05*screen_width
						line_width = 0.2*screen_width
						line_y = 0.25*screen_height+forecast_space-0.5*main_space
						pygame.draw.line(main_window,temp_color,(line_x,line_y),(line_x+line_width,line_y))
						time_str = forecast.times[ind].strftime("%I %p")
						if time_str[0] == '0': time_str = time_str[1:]
						text_display(main_window,time_str+' '+str(int(forecast.temps[ind]))+u'\N{DEGREE SIGN}',0.12*screen_width,0.25*screen_height+forecast_space,temp_color,black,main_font)
						url = forecast.condition_icon_urls[ind]
						icon_name = convert_url_to_fn(url)
						if not os.path.exists('images/'+icon_name):
							icon_loc = wget.download(url, out='images/{}'.format(icon_name))
						icon_img = pygame.image.load('images/'+icon_name)
						#rect = icon_img.get_rect()
						icon_img = pygame.transform.rotozoom(icon_img, 0., 0.3)
						main_window.blit(icon_img,(0.2*screen_width,0.25*screen_height+forecast_space-0.25*main_space))
						forecast_space += main_space
						if len(forecast.conditions[ind]) < 20:
							text_display(main_window,forecast.conditions[ind],0.12*screen_width,0.25*screen_height+forecast_space,temp_color,black,main_font)
							forecast_space += main_space
						else:
							texts = split_up_text(forecast.conditions[ind],15)
							for text in texts:
								text_display(main_window,text,0.12*screen_width,0.25*screen_height+forecast_space,temp_color,black,main_font)
								forecast_space += main_space
						
				forecast_space = 0
				
				long_term_forecast_xpos = 0.85*screen_width
				long_term_forecast_ypos = 0.25*screen_height
				
				text_display(main_window,'This Week',long_term_forecast_xpos,long_term_forecast_ypos+forecast_space,white,black,big_font)
				forecast_space += big_space
				for ind,date in enumerate(forecast.minmax_dates):
					if ind < 5:
						avg_temp = (forecast.max_temps[ind] + forecast.min_temps[ind])/2
						temp_color = outdoor_temp_color_scale(avg_temp)
						line_width = 0.2*screen_width
						line_x = long_term_forecast_xpos - line_width/2
						line_y = long_term_forecast_ypos+forecast_space-0.5*main_space
						pygame.draw.line(main_window,temp_color,(line_x,line_y),(line_x+line_width,line_y))
						text_display(main_window,date.strftime("%m/%d"),long_term_forecast_xpos,long_term_forecast_ypos+forecast_space,temp_color,black,main_font)
						forecast_space += main_space
						text_display(main_window,'Low: '+str(int(forecast.min_temps[ind]))+u'\N{DEGREE SIGN} High: '+str(int(forecast.max_temps[ind]))+u'\N{DEGREE SIGN} ',long_term_forecast_xpos,long_term_forecast_ypos+forecast_space,temp_color,black,main_font)
						forecast_space += main_space
						'''
						for j,cond_dt in enumerate(forecast.long_conditions_dt):
							if cond_dt.date() == date.date():
								if ''.join(forecast.long_conditions[j]) != '':
									text_display(main_window,cond_dt.strftime("%I:%M %p"),long_term_forecast_xpos,long_term_forecast_ypos+forecast_space,temp_color,black,main_font)
									forecast_space += main_space
									for cond_summary in forecast.long_conditions[j]:
										if cond_summary != '':
											text_display(main_window,cond_summary,long_term_forecast_xpos,long_term_forecast_ypos+forecast_space,temp_color,black,main_font)
											forecast_space += main_space
						'''
					
		
				if i%60 == 0:
					important_dates_df = read_important_dates()
				do_important_dates(main_window,fonts,spaces,screen_width,screen_height,important_dates_df,now)
				
				cassian_img = pygame.image.load('images/Cassian_Nov_21_2020.jpg')
				cassian_img = pygame.transform.rotozoom(cassian_img, 0., 0.08)
				rect = cassian_img.get_rect()
				main_window.blit(cassian_img,(0.5*screen_width-rect.center[0],0.8*screen_height))
		
		for event in pygame.event.get():
			if event.type==pygame.QUIT or (event.type==pygame.KEYUP and (event.key==pygame.K_ESCAPE or event.key==pygame.K_q)):
				pygame.quit()
				sys.exit()
		pygame.display.update()
		fpsclock.tick(FPS)
		i+=1
		
def text_display(window,text,xpos,ypos,font_col,back_col,font):
	disp_surf=font.render(text,True,font_col,back_col)
	disp_rect = disp_surf.get_rect(center=(xpos, ypos))
	window.blit(disp_surf,disp_rect)

def do_date(main_window,fonts,spaces,screen_width,screen_height,now):
	[small_font,main_font,big_font,bigger_font] = fonts
	[main_space,big_space,bigger_space] = spaces
	xpos = 0.12*screen_width
	ypos = 0.05*screen_height
	text_display(main_window,now.strftime("%b %Y"),xpos,ypos,white,black,main_font)
	ypos += big_space
	text_display(main_window,now.strftime("%d"),xpos,ypos,white,black,bigger_font)
	ypos += big_space
	text_display(main_window,now.strftime("%A"),xpos,ypos,white,black,main_font)

def do_time(main_window,fonts,spaces,screen_width,screen_height,now):
	[small_font,main_font,big_font,bigger_font] = fonts
	[main_space,big_space,bigger_space] = spaces
	xpos = 0.12*screen_width
	ypos = 0.02*screen_height
	text_display(main_window,now.strftime("%I:%M:%S %p"),xpos,ypos,white,black,main_font)
	
	
def do_temp_plot(main_window,fonts,spaces,color,plot_xcord,plot_ycord,plot_width,plot_height,times,temps,axes=True):
	if axes:
		#Draw axes
		pygame.draw.line(main_window,color,(plot_xcord,plot_ycord),(plot_xcord,plot_ycord+plot_height))
		pygame.draw.line(main_window,color,(plot_xcord,plot_ycord+plot_height),(plot_xcord+plot_width,plot_ycord+plot_height))
		#Draw and label ticks
		ticks = [50,65,80]
		for tick in ticks:
			draw_tick(tick,main_window,color,plot_xcord,plot_ycord,plot_height,plot_width,fonts)
	
	#times in minutes since start of the day
	
	times /= 1440.
	times *= plot_width
	times += plot_xcord
	
	temps /= 100.
	temps = 1. - temps
	temps *= plot_height
	temps += plot_ycord

	for i,val in enumerate(times):
		if i != 0:
			pygame.draw.line(main_window,color,(times[i-1],temps[i-1]),(times[i],temps[i]))

def draw_tick(temp,main_window,color,plot_xcord,plot_ycord,plot_height,plot_width,fonts):
	orig_temp = temp
	temp /= 100.
	temp = 1. - temp
	temp *= plot_height
	temp += plot_ycord
	
	times = np.array([-200.,-30.,30.])
	times /= 1440.
	times *= plot_width
	times += plot_xcord
	
	pygame.draw.line(main_window,color,(times[1],temp),(times[2],temp))
	text_display(main_window,str(orig_temp),times[0],temp,color,black,fonts[0])
	

def read_records(day,location):
	fn = '/export/temp_records/{}/{}_{}_{}_temp_hum.txt'.format(location,day.year,day.month,day.day)
	df = pd.read_csv(fn,delimiter='\t')
	day_start = datetime.datetime(day.year, day.month, day.day,0,0,0,0)
	
	times = df.Time
	tc = np.array(df.Temp_C)
	tf = np.array(df.Temp_F)
	hum = np.array(df.Hum)
	
	time_since_day_start = [(datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S') - day_start).seconds for time in times]
	minutes = np.array(time_since_day_start)/60.
	
	return minutes,tc,tf,hum

def read_important_dates():
	fn = 'important_dates.txt'
	df = pd.read_csv(fn,delimiter='\t')
	
	return df

def do_important_dates(main_window,fonts,spaces,screen_width,screen_height,df,day):
	[small_font,main_font,big_font,bigger_font] = fonts
	[main_space,big_space,bigger_space] = spaces
	events = list(df.Event)
	dates = list(df.Date)
	day_start = datetime.datetime(day.year, day.month, day.day,0,0,0,0)
	
	xpos = 0.5*screen_width
	ypos = 0.55*screen_height
	
	days_until_event = []
	for i,event in enumerate(events):
		event_date = datetime.datetime.strptime(dates[i],'%m/%d')
		event_date = event_date.replace(year=day.year)
		if event_date < day_start:
			event_date = event_date.replace(year=day.year+1)
		days_until_this_event = (event_date - day_start).days
		days_until_event.append(days_until_this_event)
	
	zipped = zip(days_until_event,events)
	zipped = sorted(zipped)
	
	event_space = 0
	
	for i in zipped:
		if i[0] == 0:
			text = '{} is TODAY'.format(i[1])
		else:
			text = '{} days until {}'.format(i[0],i[1])
			
		if i[0] <= 30:
			text+='!'
		if i[0] <= 10:
			text+='!'
			
		gs = int(255-i[0]*255/365)
		text_color = (gs,gs,gs)
		
		text_display(main_window,text,xpos,ypos+event_space,text_color,black,main_font)
		event_space += main_space

def get_weather_forecast(coords,zip_code):
	n = NOAA()
	forecast = weather()
	
	utc = pytz.UTC
	et = pytz.timezone('America/New_York')
	now = datetime.datetime.now()
	now = et.localize(now)
	
	while len(forecast.times) == 0:
		times = []
		temps = []
		conditions = []
		condition_icon_urls = []
		#try:
		'''Hourly Forecast'''
		hourly_forecast = n.get_forecasts(postal_code=zip_code,country='US',hourly=True)
		
		for i in hourly_forecast:
			if i['number'] == 1: forecast.current_temp = int(i['temperature'])
			times.append(datetime.datetime.strptime(i['startTime'][:19],"%Y-%m-%dT%H:%M:%S"))
			temps.append(int(i['temperature']))
			conditions.append(i['shortForecast'])
			condition_icon_urls.append(i['icon'])
		
		forecast.times = times
		forecast.temps = temps
		forecast.conditions = conditions
		forecast.condition_icon_urls = condition_icon_urls
		
		
		'''Daily Forecast'''
		daily_forecast = n.points_forecast(coords[0],coords[1],type='forecastGridData')
		daily_min_forecast = daily_forecast['properties']['minTemperature']['values']
		daily_max_forecast = daily_forecast['properties']['maxTemperature']['values']
		
		dates = []
		min_temps = []
		max_temps = []
		
		for i in range(6):
			min_temp_c = daily_min_forecast[i]['value']
			max_temp_c = daily_max_forecast[i]['value']
			min_temp_f = min_temp_c*9/5 + 32
			max_temp_f = max_temp_c*9/5 + 32
			strdate = daily_min_forecast[i]['validTime'][0:10]
			
			date = datetime.datetime.strptime(strdate,"%Y-%m-%d")
			
			if date.date() > now.date():
				dates.append(date)
				min_temps.append(min_temp_f)
				max_temps.append(max_temp_f)
			
		forecast.minmax_dates = dates
		forecast.min_temps = min_temps
		forecast.max_temps = max_temps
		
		
		'''Long term conditions'''
		long_term_conditions_forecast = daily_forecast['properties']['weather']['values']
		long_conditions_dt = []
		long_conditions = []
		
		for i in range(len(long_term_conditions_forecast)):
			strtime = long_term_conditions_forecast[i]['validTime'][0:19]
			dt = datetime.datetime.strptime(strtime,"%Y-%m-%dT%H:%M:%S")
			UTtime = utc.localize(dt)
			ETtime = UTtime.astimezone(et)
			
			if ETtime > now:
				long_conditions_dt.append(ETtime)
				these_conditions = summarize_conditions(long_term_conditions_forecast[i]['value'])
				long_conditions.append(these_conditions)
				
		#for i,time in enumerate(long_conditions_dt):
		#	print(time)
		#	#print(time,long_conditions[i])
			
		forecast.long_conditions_dt = long_conditions_dt
		forecast.long_conditions = long_conditions
	
		#except:
		#	print('Failed to get NOAA data. Trying again')
	
	return forecast
	
def convert_url_to_fn(url):
	fn = url.split('/')[4:]
	fn[-1] = fn[-1].split('?')[0]
	fn = '_'.join(fn)
	fn = fn.replace(',','_')
	
	return(fn)
	
def split_up_text(full_text,max_len):
	text_list = full_text.split(' ')
	texts = []
	
	j = 0 #iteratable for texts
	for i,text in enumerate(text_list):
		if i == 0:
			texts.append(text)
		elif len(texts[j]) + 1 + len(text) < max_len:
			texts[j] = '{} {}'.format(texts[j],text)
		else:
			texts.append(text)
			j+=1
	
	return texts
	
def summarize_conditions(long_cond):
	summary = []
	for i in long_cond:
		this_cond = ''
		cond_list = []
		if i['coverage'] != None:
			cond_list.append(cap_and_clean(i['coverage']))
		if i['intensity'] != None:
			cond_list.append(cap_and_clean(i['intensity']))
		if i['weather'] != None:
			cond_list.append(cap_and_clean(i['weather']))
		if len(cond_list) > 0:
			this_cond = ' '.join(cond_list)
		#print(i)
		#print('---------------')
		summary.append(this_cond)
	#print('======================')
	
	return summary

def cap_and_clean(input_string):
	output_list = input_string.split('_')
	for i,o in enumerate(output_list):
		output_list[i] = o.capitalize()
	output_string = ' '.join(output_list)
	return output_string

def outdoor_temp_color_scale(temp):
	'''
	if temp >= 80:
		temp_color = red
	elif temp > 32:
		scale = int(255*(1-(temp-32)/48))
		temp_color = (255,scale,scale)
	elif temp == 32:
		temp_color = blue
	elif temp > -40:
		scale_1 = int(200*(temp+40)/72)
		scale_2 = int(255*(temp+40)/72)
		temp_color = (0,scale_1,scale_2)
	else:
		temp_color = black
	'''
	temp_color = white
	return temp_color

def check_online_time(now):
	turn_off_time = now.replace(hour=23, minute=0,second=0,microsecond=0)
	turn_on_time = now.replace(hour=7, minute=0,second=0,microsecond=0)
	if now > turn_on_time and now < turn_off_time:
		return True
	else:
		return False

class weather:
	def __init__(self):
		self.times = []
		self.temps = []
		self.current_temp = -100.
		self.conditions = []
		self.condition_icon_urls = []
		self.minmax_dates = []
		self.min_temps = []
		self.max_temps = []
		self.long_conditions_dt = []
		self.long_conditions = []
		

if __name__ == '__main__':
	main()