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
blue=(0,150,255)
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
	main_space = screen_width/60
	spaces = [main_space,big_space,bigger_space]
	
	swans_island_coords = (44.18318112881812,-68.41599063902959)
	swans_island_zip = '04685'
	i=0
	
	devmode = False
	#try:
	forecast = get_weather_forecast(swans_island_coords,swans_island_zip)
	#except:
	#	devmode = True
	
	
	while True:
		now = datetime.datetime.now()
		today_start = datetime.datetime(now.year, now.month, now.day,0,0,0,0)
		main_window.fill(black)
		do_date(main_window,fonts,spaces,screen_width,screen_height,now)
		do_time(main_window,fonts,spaces,screen_width,screen_height,now)
		
		try:
			times,temps_c,temps,hum = read_records(now,'office')
			current_office_temp = int(temps[-1])
			do_temp_plot(main_window,fonts,spaces,white,0.85*screen_width,0.1*screen_height,0.1*screen_width,0.1*screen_width,times,temps)
		except:
			times,temps_c,temps,hum = [[0],[0],[0],[0]]
			current_office_temp = '--'
		try:
			times,temps_c,temps,hum = read_records(now,'cassian_room')
			current_cas_temp = int(temps[-1])
			do_temp_plot(main_window,fonts,spaces,blue,0.85*screen_width,0.1*screen_height,0.1*screen_width,0.1*screen_width,times,temps,axes=False)
		except:
			times,temps_c,temps,hum = [[0],[0],[0],[0]]
			current_cas_temp = '--'
		
		
		text_display(main_window,'Office',0.9*screen_width,0.3*screen_height,white,black,main_font)
		text_display(main_window,str(current_office_temp)+u'\N{DEGREE SIGN}',0.9*screen_width,0.3*screen_height+big_space,white,black,bigger_font)
		
		text_display(main_window,"Cassian's Room",0.9*screen_width,0.5*screen_height,blue,black,main_font)
		text_display(main_window,str(current_cas_temp)+u'\N{DEGREE SIGN}',0.9*screen_width,0.5*screen_height+big_space,blue,black,bigger_font)
		
		if not devmode:
			if i%300 == 0 and i != 0:
				forecast = get_weather_forecast(swans_island_coords,swans_island_zip)
			
			if forecast.current_temp <= 32:
				temp_color = blue
			elif forecast.current_temp >= 75:
				temp_color = red
			else:
				temp_color = white
			text_display(main_window,"Swans Island",0.12*screen_width,0.3*screen_height,temp_color,black,main_font)
			text_display(main_window,str(int(forecast.current_temp))+u'\N{DEGREE SIGN}',0.12*screen_width,0.3*screen_height+big_space,temp_color,black,bigger_font)
			
			forecast_space = 0
			text_display(main_window,'Hourly Forecast',0.12*screen_width,0.4*screen_height+forecast_space,white,black,main_font)
			forecast_space += main_space
			for i in [2,4,6,8,10]:
				if len(forecast.temps) > i+1:
					if forecast.temps[i] <= 32:
						temp_color = blue
					elif forecast.temps[i] >= 75:
						temp_color = red
					else:
						temp_color = white
					text_display(main_window,forecast.times[i].strftime("%m/%d %I:%M %p")+' '+str(int(forecast.temps[i]))+u'\N{DEGREE SIGN}',0.12*screen_width,0.4*screen_height+forecast_space,temp_color,black,main_font)
					url = forecast.condition_icon_urls[i]
					icon_name = convert_url_to_fn(url)
					if not os.path.exists('images/'+icon_name):
						icon_loc = wget.download(url, out='images/{}'.format(icon_name))
					icon_img = pygame.image.load('images/'+icon_name)
					rect = icon_img.get_rect()
					main_window.blit(icon_img,(0.15*screen_width,0.4*screen_height+forecast_space))
					forecast_space += main_space
					text_display(main_window,forecast.conditions[i],0.12*screen_width,0.4*screen_height+forecast_space,temp_color,black,main_font)
					forecast_space += main_space
					
			forecast_space += main_space
			
			text_display(main_window,'Daily Forecast',0.12*screen_width,0.4*screen_height+forecast_space,white,black,main_font)
			forecast_space += main_space
			text_display(main_window,'(min/max)',0.12*screen_width,0.4*screen_height+forecast_space,white,black,main_font)
			forecast_space += main_space
			for i,date in enumerate(forecast.minmax_dates):
				if i < 5:
					if forecast.max_temps[i] <= 32:
						temp_color = blue
					elif forecast.min_temps[i] >= 75:
						temp_color = red
					else:
						temp_color = white
					text_display(main_window,date.strftime("%m/%d")+' '+str(int(forecast.min_temps[i]))+u'\N{DEGREE SIGN} '+str(int(forecast.max_temps[i]))+u'\N{DEGREE SIGN} ',0.12*screen_width,0.4*screen_height+forecast_space,temp_color,black,main_font)
					forecast_space += main_space
		
					
		
		#if i%60 == 0:
		#	important_dates_df = read_important_dates()
		#do_important_dates(main_window,fonts,spaces,screen_width,screen_height,important_dates_df,now)
		
		cassian_img = pygame.image.load('images/Cassian_Nov_21_2020.jpg')
		cassian_img = pygame.transform.rotozoom(cassian_img, 0., 0.08)
		rect = cassian_img.get_rect()
		main_window.blit(cassian_img,(0.5*screen_width-rect.center[0],0.7*screen_height))
		
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
	xpos = 0.9*screen_width
	ypos = 0.05*screen_height
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
	events = list(df.Event)
	dates = list(df.Date)
	day_start = datetime.datetime(day.year, day.month, day.day,0,0,0,0)
	
	xpos = 0.9*screen_width
	ypos = 0.2*screen_height
	
	text_display(main_window,'Upcoming Events')
	for i,event in events:
		days_until_event = (datetime.datetime.strptime(dates[i],'%m/%d') - day_start).days
		text_display

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
		
		for i in range(len(daily_min_forecast)):
			min_temp_c = daily_min_forecast[i]['value']
			max_temp_c = daily_max_forecast[i]['value']
			min_temp_f = min_temp_c*9/5 + 32
			max_temp_f = max_temp_c*9/5 + 32
			strdate = daily_min_forecast[i]['validTime'][0:10]
			
			date = datetime.datetime.strptime(strdate,"%Y-%m-%d")
			
			dates.append(date)
			min_temps.append(min_temp_f)
			max_temps.append(max_temp_f)
			
		forecast.minmax_dates = dates
		forecast.min_temps = min_temps
		forecast.max_temps = max_temps
		
	
		#except:
		#	print('Failed to get NOAA data. Trying again')
	
	return forecast
	
def convert_url_to_fn(url):
	fn = url.split('/')[4:]
	fn[-1] = fn[-1].split('?')[0]
	fn = '_'.join(fn)
	fn = fn.replace(',','_')
	
	return(fn)
	
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
		

if __name__ == '__main__':
	main()