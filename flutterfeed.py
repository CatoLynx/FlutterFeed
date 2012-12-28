#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FlutterFeed – A CLI Twitter client for Linux written in Python
# © 2012 Mezgrman

x_display = None
gui = False
window_id = None

try:
	import Xlib.display
except ImportError:
	pass
else:
	try:
		x_display = Xlib.display.Display()
	except:
		pass
	else:
		gui = True
	if gui:
		window_id = x_display.get_input_focus().focus.id

from flutterfeed_functions import *
import flutterfeed_classes as classes
import flutterfeed_config as config
import flutterfeed_plugins as plugins
import flutterfeed_strings as strings
import argparse
import locale
import sys
import thread
import traceback
import tweepy
import urwid
#import urwid.html_fragment

locale.setlocale(locale.LC_ALL, '')

parser = argparse.ArgumentParser(description = config.system.client_description)
parser.add_argument('-nb', '--nobackfill', action = 'store_true', help = strings.args_nobackfill)
parser.add_argument('-m', '--manual', action = 'store_true', help = strings.args_manual)
parser.add_argument('-t', '--tweet', help = strings.args_tweet)
parser.add_argument('-k', '--keywords', help = strings.args_keywords)
parser.add_argument('-u', '--users', help = strings.args_users)
parser.add_argument('-l', '--locations', help = strings.args_locations)
parser.add_argument('-d', '--database', help = strings.args_database)
parser.add_argument('-a', '--account', help = strings.args_account)
args = parser.parse_args()

def main():
	global parser
	global args
	client = classes.Client(ui, args, gui, x_display, window_id)
	client.login()
	if args.tweet is not None:
		try:
			client.api.update_status(args.tweet)
		except tweepy.error.TweepError, err:
			print red(strings.api_error % err)
		raise classes.ClientQuit
	thread.start_new_thread(client.statusbar_update, ())
	client.start_ui()
	if not args.manual:
		thread.start_new_thread(client.start_stream, ())
	plugins.on_ready(client)
	client.event_loop()

plugins.on_init()
#urwid.html_fragment.screenshot_init([(200, 75)], [])
ui = urwid.raw_display.Screen()
# ui.set_terminal_properties(colors = 256)
ui.register_palette(config.var.palette)
try:
	ui.run_wrapper(main)
except classes.ClientQuit:
	sys.exit()
except KeyboardInterrupt:
	pass
#except:
	#with(open("screenshots.html", "w")) as f:
		#f.write("\n\n".join(urwid.html_fragment.screenshot_collect()))
