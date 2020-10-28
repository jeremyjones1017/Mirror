#!/usr/bin/python3

import sys
import time
import pygame
import datetime
import tkinter as tk
from datetime import timedelta
import numpy as np
import pandas as pd

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
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()
	pygame.init()
	FPS = 1
	main_window = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
	fpsclock = pygame.time.Clock()
	while True:
		run_mirror(main_window,FPS,fpsclock,screen_width,screen_height)
		
def run_mirror(main_window,FPS,fpsclock,screen_width,screen_height):
	bigger_font = pygame.font.Font('freesansbold.ttf',int(screen_width/15))
	big_font = pygame.font.Font('freesansbold.ttf',int(screen_width/20))
	main_font = pygame.font.Font('freesansbold.ttf',int(screen_width/60))
	fonts = [main_font,big_font,bigger_font]
		
	bigger_space = screen_width/15
	big_space = screen_width/20
	main_space = screen_width/60
	spaces = [main_space,big_space,bigger_space]
	i=0
	while True:
		now = datetime.datetime.now()
		today_start = datetime.datetime(now.year, now.month, now.day,0,0,0,0)
		main_window.fill(black)
		do_date(main_window,fonts,spaces,screen_width,screen_height,now)
		do_time(main_window,fonts,spaces,screen_width,screen_height,now)
		
		times,temps_c,temps,hum = read_records(now)
		current_temp = temps[-1]
		do_temp_plot(main_window,fonts,spaces,white,0.85*screen_width,0.1*screen_height,0.1*screen_width,0.1*screen_width,times,temps)
		times,temps_c,temps,hum = read_records(now-datetime.timedelta(days=1))
		do_temp_plot(main_window,fonts,spaces,red,0.85*screen_width,0.1*screen_height,0.1*screen_width,0.1*screen_width,times,temps,axes=False)
		
		text_display(main_window,'Office',0.9*screen_width,0.4*screen_height,white,black,main_font)
		text_display(main_window,str(int(current_temp))+u'\N{DEGREE SIGN}',0.9*screen_width,0.4*screen_height+big_space,white,black,bigger_font)
		
		#if i%60 == 0:
		#	important_dates_df = read_important_dates()
		#do_important_dates(main_window,fonts,spaces,screen_width,screen_height,important_dates_df,now)
		
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
	[main_font,big_font,bigger_font] = fonts
	[main_space,big_space,bigger_space] = spaces
	xpos = 0.1*screen_width
	ypos = 0.05*screen_height
	text_display(main_window,now.strftime("%b %Y"),xpos,ypos,white,black,main_font)
	ypos += big_space
	text_display(main_window,now.strftime("%d"),xpos,ypos,white,black,bigger_font)
	ypos += big_space
	text_display(main_window,now.strftime("%A"),xpos,ypos,white,black,main_font)

def do_time(main_window,fonts,spaces,screen_width,screen_height,now):
	[main_font,big_font,bigger_font] = fonts
	[main_space,big_space,bigger_space] = spaces
	xpos = 0.9*screen_width
	ypos = 0.05*screen_height
	text_display(main_window,now.strftime("%I:%M:%S %p"),xpos,ypos,white,black,main_font)
	
	
def do_temp_plot(main_window,fonts,spaces,color,plot_xcord,plot_ycord,plot_width,plot_height,times,temps,axes=True):
	if axes:
		pygame.draw.line(main_window,color,(plot_xcord,plot_ycord),(plot_xcord,plot_ycord+plot_height))
		pygame.draw.line(main_window,color,(plot_xcord,plot_ycord+plot_height),(plot_xcord+plot_width,plot_ycord+plot_height))
	
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

def read_records(day):
	fn = 'records/{}_{}_{}_temp_hum.txt'.format(day.year,day.month,day.day)
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

if __name__ == '__main__':
	main()