#!/usr/bin/python
# -*- coding: utf-8 -*-
# FlutterFeed – the command-line Python Twitter client made by Mezgrman.
# © 2012 Mezgrman.

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
	if(gui):
		window_id = x_display.get_input_focus().focus.id

import stuff
import config
import userconfig
from functions import *
import plugins
import urwid
import thread
import locale
import traceback
import sys
import argparse
import tweepy
#import urwid.html_fragment

locale.setlocale(locale.LC_ALL, '')

parser = argparse.ArgumentParser(description = config.system.client_description)
parser.add_argument('-nb', '--nobackfill', action = 'store_true', help = userconfig.strings.args_nobackfill)
parser.add_argument('-m', '--manual', action = 'store_true', help = userconfig.strings.args_manual)
parser.add_argument('-t', '--tweet', help = userconfig.strings.args_tweet)
parser.add_argument('-k', '--keywords', help = userconfig.strings.args_keywords)
parser.add_argument('-u', '--users', help = userconfig.strings.args_users)
parser.add_argument('-l', '--locations', help = userconfig.strings.args_locations)
parser.add_argument('-d', '--database', help = userconfig.strings.args_database)
parser.add_argument('-a', '--account', help = userconfig.strings.args_account)
args = parser.parse_args()

def main():
	global parser
	global args
	client = stuff.Client(ui, args, gui, x_display, window_id)
	client.login()
	if(args.tweet is not None):
		try:
			client.api.update_status(args.tweet)
		except tweepy.error.TweepError, err:
			print red(userconfig.error.api_error % err)
		raise stuff.ClientQuit
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
ui.register_palette(userconfig.var.palette)
try:
	ui.run_wrapper(main)
except stuff.ClientQuit:
	sys.exit()
except KeyboardInterrupt:
	pass
#except:
	#with(open("screenshots.html", "w")) as f:
		#f.write("\n\n".join(urwid.html_fragment.screenshot_collect()))
