# -*- coding: utf-8 -*-
# Class definitions and stuff like that
# © 2012 Mezgrman

from flutterfeed_functions import *
from ssl import SSLError
import flutterfeed_config as config
import flutterfeed_plugins as plugins
import flutterfeed_strings as strings
import base64
import os
import pickle
import re
import sqlite3
import sys
import time
import traceback
import tweetpony
import twextender
import twitlonger
import urllib2
import urwid

try:
	import pynotify
except:
	popup_notifications = False
else:
	popup_notifications = True

class Object(object):
	pass

class SelectableText(urwid.Text):
	def selectable(self):
		return True
	
	def keypress(self, size, key):
		return key

class DialogList(urwid.WidgetWrap):
	selected = None
	
	def __init__(self, dialog, entries, attr):
		self.dialog = dialog
		content = [urwid.AttrWrap(SelectableText(html_unescape(entry)), None, attr[1]) for entry in entries]
		self.selected = (0, content[0].get_text()[0])
		self.height = len(entries)
		self.width = 0
		for entry in entries:
			if (len(entry) + (config.geometry.dialog_padding * 2)) > self.width:
				self.width = (len(entry) + (config.geometry.dialog_padding * 2))
		self._listbox = urwid.AttrWrap(urwid.ListBox(content), attr[0])
		self.__super.__init__(self._listbox)
	
	def keypress(self, size, key):
		if key == 'enter':
			widget, index = self._listbox.get_focus()
			text, text_attr = widget.get_text()
			self.selected = (index, text)
			self.dialog._action(urwid.Button("List"))
		else:
			return self._listbox.keypress(size, key)

class Dialog(urwid.WidgetWrap):
	b_pressed = None
	edit_texts = None
	selected = None
	_blank = urwid.Text("")
	_edit_widgets = None
	_list_widget = None
	
	def __init__(self, msg, buttons, edit_items, list_items, attr, body):
		lines = msg.splitlines()
		max_line_width = 0
		for line in lines:
			if len(line) > max_line_width:
				max_line_width = len(line)
		message_width = (max_line_width + (config.geometry.dialog_padding * 2))
		button_widgets = []
		max_button_width = 0
		button_grid_width = (config.geometry.dialog_padding * 2)
		for button in buttons:
			cur_button_width = len(button) + 4
			if cur_button_width > max_button_width:
				max_button_width = cur_button_width
			button_widgets.append(urwid.AttrMap(urwid.Button(button, self._action), attr[1], attr[2]))
		button_grid_width = ((max_button_width + config.geometry.button_h_spacing) * len(buttons) + 1)
		width = message_width if message_width > button_grid_width else button_grid_width
		height = (len(lines) + 3 + (config.geometry.dialog_padding * 2))
		self.dialog_text = urwid.Text(msg, 'center')
		msg_widget = urwid.Padding(self.dialog_text, 'center', width - (config.geometry.dialog_padding * 2))
		button_grid = urwid.GridFlow(button_widgets, max_button_width, config.geometry.button_h_spacing, config.geometry.button_v_spacing, 'center')
		widget_list = [msg_widget]
		if edit_items:
			height += (len(edit_items) * 3)
			self._edit_widgets = []
			for item in edit_items:
				if (len(item[1]) + (config.geometry.dialog_padding * 2)) > width:
					width = (len(item[1]) + (config.geometry.dialog_padding * 2))
				caption = urwid.Padding(urwid.Text(item[0], 'center'), 'center', width - (config.geometry.dialog_padding * 2))
				widget = urwid.Edit(edit_text = item[1], align = 'center')
				self._edit_widgets.append(widget)
				text_edit = urwid.Padding(urwid.AttrMap(widget, 'edit'), 'center', width - (config.geometry.dialog_padding * 2))
				widget_list += [self._blank, caption, text_edit]
			if width < (config.geometry.text_input_min_width + (config.geometry.dialog_padding * 2)):
				width = (config.geometry.text_input_min_width + (config.geometry.dialog_padding * 2))
		if list_items:
			self._list_widget = DialogList(self, list_items, ('list', 'list selected'))
			if width < self._list_widget.width:
				width = self._list_widget.width
			height += (self._list_widget.height + 1)
			list_widget = urwid.Padding(urwid.BoxAdapter(self._list_widget, self._list_widget.height), 'center', width - (config.geometry.dialog_padding * 2))
			widget_list += [self._blank, list_widget]
		widget_list += [self._blank, button_grid]
		self.combined = urwid.AttrMap(urwid.Filler(urwid.Pile(widget_list, 2)), attr[0])
		overlay = urwid.Overlay(self.combined, body, 'center', width, 'middle', height)
		self.__super.__init__(overlay)
	
	def _action(self, button):
		if self._edit_widgets:
			self.edit_texts = [widget.get_edit_text() for widget in self._edit_widgets]
		if self._list_widget:
			self.selected = self._list_widget.selected
		self.b_pressed = button.get_label()

class Notification(urwid.WidgetWrap):
	_blank = urwid.Text("")
	
	def __init__(self, msg, attr, body):
		lines = msg.splitlines()
		max_line_width = 0
		for line in lines:
			if len(line) > max_line_width:
				max_line_width = len(line)
		width = (max_line_width + (config.geometry.dialog_padding * 2))
		height = (len(lines) + (config.geometry.dialog_padding * 2))
		self.dialog_text = urwid.Text(msg, 'center')
		msg_widget = urwid.Padding(self.dialog_text, 'center', width - (config.geometry.dialog_padding * 2))
		self.combined = urwid.AttrMap(urwid.Filler(msg_widget), attr[0])
		overlay = urwid.Overlay(self.combined, body, 'center', width, 'middle', height)
		self.__super.__init__(overlay)

class ClientQuit(Exception):
	def __init__(self, value = "Client quit."):
		self.err = value
	
	def __str__(self):
		return repr(self.err)

class Client:
	def __init__(self, ui, args, gui, x_display, window_id):
		self.path = os.path.dirname(os.path.realpath(__file__))
		self.ui = ui
		self.args = args
		self.dim = self.ui.get_cols_rows()
		self.width = self.dim[0]
		self.height = self.dim[1]
		self.feed_height = (self.height - (config.geometry.statusbar_height + config.geometry.statusbar_spacing + config.geometry.cmdline_height + config.geometry.cmdline_spacing))
		self.redraw_from_thread = True
		self.afk_mode = False
		self.last_command = ""
		self.name = config.system.client_name
		self.version = config.system.version
		self.gui = gui
		self.x_display = x_display
		self.window_id = window_id
		self.account = config.system.default_account_name if self.args.account is None else self.args.account.lower()
		if not self.gui:
			self.popup_notifications = False
		else:
			self.popup_notifications = popup_notifications
		if self.popup_notifications:
			try:
				self.popup_notifications = pynotify.init(self.name)
			except:
				self.popup_notifications = False
		if not args.database:
			db_file = os.path.join(os.path.expanduser("~"), config.system.db_file)
			dirname = os.path.dirname(db_file)
			if not os.path.exists(dirname):
				os.makedirs(dirname)
		else:
			db_file = args.database
		self.db = sqlite3.connect(db_file)
		self.db_cursor = self.db.cursor()
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `filtered_words` (`word`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `filtered_users` (`user`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `filtered_clients` (`client`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `filtered_regexes` (`regex`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `highlighted_words` (`word`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `highlighted_users` (`user`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `highlighted_clients` (`client`)")
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `highlighted_regexes` (`regex`)")
		self.db.commit()
		self.code_db = sqlite3.connect(":memory:", check_same_thread = False)
		self.code_db_cursor = self.code_db.cursor()
		self.code_db_cursor.execute("CREATE TABLE `codes` (`code_id` INTEGER PRIMARY KEY, `code`, `ID`, `author`, `text`, `in_reply_to`, `tweet_obj`)")
		self.code_db.commit()
		self.cached_tweet_count = 0
		self.notification_count = 0
		self.filtered_words = []
		self.filtered_users = []
		self.filtered_clients = []
		self.filtered_regexes = []
		self.highlighted_words = []
		self.highlighted_users = []
		self.highlighted_clients = []
		self.highlighted_regexes = []
		self.db_cursor.execute("SELECT * FROM `filtered_words`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.filtered_words.append(row[0])
		self.db_cursor.execute("SELECT * FROM `filtered_users`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.filtered_users.append(row[0])
		self.db_cursor.execute("SELECT * FROM `filtered_clients`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.filtered_clients.append(row[0])
		self.db_cursor.execute("SELECT * FROM `filtered_regexes`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.filtered_regexes.append((row[0], re.compile(row[0], re.MULTILINE)))
		self.db_cursor.execute("SELECT * FROM `highlighted_words`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.highlighted_words.append(row[0])
		self.db_cursor.execute("SELECT * FROM `highlighted_users`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.highlighted_users.append(row[0])
		self.db_cursor.execute("SELECT * FROM `highlighted_clients`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.highlighted_clients.append(row[0])
		self.db_cursor.execute("SELECT * FROM `highlighted_regexes`")
		rows = self.db_cursor.fetchall()
		for row in rows:
			self.highlighted_regexes.append((row[0], re.compile(row[0], re.MULTILINE)))
		self.me_update_interval = config.system.statusbar_update_interval_left + 1
		if self.args.keywords:
			self.stream_keywords = [item.strip() for item in self.args.keywords.split(",")] if len(self.args.keywords) > 0 else None
		else:
			self.stream_keywords = []
		if self.args.users:
			self.stream_user_ids = [item.strip() for item in self.args.users.split(u",")] if len(self.args.users) > 0 else None
		else:
			self.stream_user_ids = []
		if self.args.locations:
			self.stream_locations = [float(item.strip()) for item in self.args.locations.split(u",")] if len(self.args.locations) > 0 else None
		else:
			self.stream_locations = None
	
	def authenticate(self):
		self.api = tweetpony.API(config.oauth.consumer_key, config.oauth.consumer_secret)
		try:
			redirect_url = self.api.get_auth_url()
		except tweetpony.APIError as err:
			self.api_error(err, True)
		print strings.auth_url % redirect_url
		try:
			import webbrowser
			webbrowser.open_new_tab(redirect_url)
			time.sleep(config.var.verifier_prompt_delay)
		except:
			pass
		verifier = ""
		while verifier == "":
			verifier = raw_input(strings.verifier_prompt)
		try:
			self.api.authenticate(verifier)
		except tweetpony.APIError as err:
			self.api_error(err, True)
		self.db_cursor.execute("CREATE TABLE IF NOT EXISTS `access_token` (`name`, `key`, `secret`)")
		self.db_cursor.execute("DELETE FROM `access_token` WHERE `name` = ?", (self.account,))
		self.db_cursor.execute("INSERT INTO `access_token` (`name`, `key`, `secret`) VALUES (?, ?, ?)", (self.account, self.api.access_token, self.api.access_token_secret))
		self.db.commit()
		self.login()
	
	def login(self):
		try:
			self.db_cursor.execute("SELECT `key`, `secret` FROM `access_token` WHERE `name` = ?", (self.account,))
			access_token = self.db_cursor.fetchone()
			access_token_key = access_token[0]
			access_token_secret = access_token[1]
		except:
			self.authenticate()
			return
		try:
			self.api = tweetpony.API(config.oauth.consumer_key, config.oauth.consumer_secret, access_token_key, access_token_secret, host = config.api.api_host, root = config.api.api_root, secure = config.api.secure)
		except tweetpony.APIError as err:
			print red(strings.api_error % (err.code, err.description))
			sys.exit(1)
		
		self.twitlonger_api = twitlonger.API(config.system.twitlonger_application_name, config.system.twitlonger_api_key)
		self.twextender_api = twextender.API(config.system.twextender_api_key)
	
	def logout(self):
		self.db_cursor.execute("DELETE FROM `access_token` WHERE `name` = ?", (self.account,))
		self.db.commit()
	
	def check_latest_version(self):
		try:
			req = urllib2.Request("http://www.mezgrman.de/flutterfeed_version.txt")
			req.add_header('Cache-Control', 'no-cache')
			response = urllib2.urlopen(req)
			response_data = response.read().splitlines()
			latest_version = re.sub(r"\n$", u"", response_data[0])
			del response_data[0]
			changelog = re.sub(r"\n$", u"", u"\n".join(response_data))
		except:
			return (None, None)
		else:
			return (latest_version, changelog)
	
	def check_for_update(self):
		latest_version, changelog = self.check_latest_version()
		if latest_version and changelog:
			newer_version = self.version_number_higher(latest_version, self.version)
			return (newer_version, latest_version, changelog)
		else:
			return (None, None, None)
	
	def version_number_higher(self, version1, version2):
		try:
			v1 = [int(part) for part in version1.split()[0].split(".")]
			v2 = [int(part) for part in version2.split()[0].split(".")]
			diff = len(v1) - len(v2)
			if diff > 0:
				v2 += [0] * diff
			elif diff < 0:
				v1 += [0] * abs(diff)
			for i in range(len(v1)):
				if v1[i] > v2[i]:
					return True
				if v1[i] < v2[i]:
					return False
			return False
		except:
			return False
	
	def has_focus(self):
		if self.gui:
			return self.x_display.get_input_focus().focus.id == self.window_id
		else:
			return True
	
	def set_title(self, title):
		sys.stdout.write(u"\x1b]2;%s\x07" % title)
	
	def notify(self, frequency = 440, duration = 200, status = None, message = None, event = None):
		if not self.has_focus():
			frequency, duration, status, message, event = plugins.on_notification(self, frequency, duration, status, message, event)
			self.notification_count += 1
			self.set_title(strings.window_title_notifications % {'username': self.me.screen_name, 'name': self.name, 'version': self.version, 'notifications': self.notification_count})
			if config.var.popups and self.popup_notifications:
				if status:
					title = u"@" + status.user.screen_name
					body = status.text
				elif message:
					title = strings.notification_title % (self.name, self.me.screen_name)
					body = strings.message_popup_notification % message.sender.screen_name
				elif event:
					title = strings.notification_title % (self.name, self.me.screen_name)
					body = event
				n = pynotify.Notification(title, body, os.path.join(self.path, config.system.notification_icon))
				n.show()
			if config.var.beep:
				os.system('beep -f %f -l %f' % (frequency, duration))
	
	def reset_notifications(self):
		self.notification_count = 0
		self.set_title(strings.window_title_no_notifications % {'username': self.me.screen_name, 'name': self.name, 'version': self.version})
	
	def start_ui(self):
		self.me = self.api.user
		self.reset_notifications()
		self.statusbar_content = urwid.Text(u"", align = 'left')
		self.statusbar_refresh()
		self.cmdline_content = urwid.Edit()
		self.cmdline_refresh()
		self.clear_feed(redraw = False)
		self.redraw()
		update = self.check_for_update()
		if update[0]:
			self.info_dialog(strings.update_available % (self.name, update[1], update[2]))
		if not self.args.nobackfill and not self.stream_keywords and not self.stream_user_ids and not self.stream_locations:
			self.backfill(count = self.feed_height)
	
	def clear_feed(self, redraw = True):
		self.feed_lines = urwid.SimpleListWalker([])
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def statusbar_refresh(self):
		self.statusbar = urwid.AttrMap(self.statusbar_content, 'statusbar')
	
	def feed_refresh(self):
		self.feed_content = urwid.ListBox(self.feed_lines)
		try:
			self.feed_content.set_focus(self.feed_lines.focus + 1)
		except IndexError:
			pass
		self.feed = urwid.AttrMap(urwid.Filler(urwid.BoxAdapter(self.feed_content, self.feed_height)), 'feed')
	
	def cmdline_refresh(self):
		self.cmdline = urwid.AttrMap(self.cmdline_content, 'cmdline')
	
	def redraw(self):
		self.display = urwid.Frame(self.feed, self.statusbar, self.cmdline, 'footer')
		self.ui.draw_screen(self.dim, self.display.render(self.dim, True))
	
	def line_break(self, text, prefix = ""):
		if len(prefix + text) > self.width:
			breakpoint = (self.width - len(prefix) - 1)
			indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
			temp = list(text)
			_range = range(((breakpoint - config.var.linebreak_max_searchback) + 1), (breakpoint + 1))
			_range.reverse()
			for i in _range:
				if temp[i] == u" ":
					breakpoint = i + 1
					break
			temp.insert(breakpoint, u"\n" + indent)
			text = u"".join(temp)
		return text
	
	def dialog(self, msg, buttons, edit_items = None, list_items = None, allow_esc = True):
		self.redraw_from_thread = False
		popup = Dialog(msg, buttons, edit_items, list_items, ('dialog', 'button', 'button focus'), self.display)
		keys = True
		while True:
			self.ui.draw_screen(self.dim, popup.render(self.dim, True))
			keys = self.ui.get_input()
			if "window resize" in keys:
				self.dim = self.ui.get_cols_rows()
			if "esc" in keys and allow_esc:
				popup.b_pressed = "Esc"
			else:
				for k in keys:
					popup.keypress(self.dim, k)
			if popup.b_pressed:
				self.redraw_from_thread = True
				return {'button': popup.b_pressed, 'texts': popup.edit_texts, 'selected': popup.selected}
	
	def notification(self, msg, timeout = config.var.default_notification_timeout):
		self.redraw_from_thread = False
		popup = Notification(msg, ('dialog',), self.display)
		self.ui.draw_screen(self.dim, popup.render(self.dim, True))
		time.sleep(timeout)
		self.redraw_from_thread = True
		return
	
	def yes_no_dialog(self, msg, allow_esc = False):
		result = self.dialog(msg, [strings.button_yes, strings.button_no], None, None, allow_esc)
		return (result['button'] == strings.button_yes)
	
	def info_dialog(self, msg, allow_esc = False):
		result = self.dialog(msg, [strings.button_ok], None, None, allow_esc)
		return (result['button'] == strings.button_ok)
	
	def input_dialog(self, msg, caption, allow_esc = True):
		result = self.dialog(msg, [strings.button_ok], [(caption, u"")], None, allow_esc)
		return ((result['button'] == strings.button_ok), result['texts'][0])
	
	def list_dialog(self, msg, list_items, allow_esc = True):
		result = self.dialog(msg, [strings.button_ok], None, [item.replace("\n", " ") for item in list_items], allow_esc)
		return ((result['button'] == strings.button_ok or result['button'] == "List"), result['selected'])
	
	def event_loop(self):
		keys = True
		while True:
			try:
				self.cmdline_content.set_caption(('cmdline bold', strings.prompt % (140 - len(self.cmdline_content.get_edit_text()))))
				if keys:
					self.redraw()
				keys = self.ui.get_input()
				if "window resize" in keys:
					self.dim = self.ui.get_cols_rows()
				elif config.system.exit_key in keys:
					if self.yes_no_dialog(strings.quit_confirmation):
						raise ClientQuit
				elif config.system.submit_key in keys:
					raw_data = self.cmdline_content.get_edit_text()
					self.last_command = raw_data
					if raw_data != u"":
						self.cmdline_content.set_edit_text(u"")
						self.cmdline_content.set_caption(('cmdline bold', strings.prompt_loading))
						data_array = raw_data.split()
						command = data_array[0]
						has_data = (len(data_array) > 1)
						del data_array[0]
						data = ' '.join(data_array)
						args = (command, data_array)
						(command, data_array) = plugins.on_command(self, *args)
						self.process_command(command, data_array)
				else:
					for key in keys:
						self.cmdline_content.keypress((1,), key)
			except KeyboardInterrupt:
				self.cmdline_content.set_edit_text(u"")
	
	def statusbar_update(self):
		time.sleep(config.system.statusbar_loading_delay)
		self.me_update_interval = config.system.statusbar_update_interval_left + 1
		while True:
			if self.me_update_interval > config.system.statusbar_update_interval_left:
				try:
					self.me = plugins.on_statusbar_update_left(self, self.api.verify_credentials())
				except tweetpony.APIError as err:
					return err
				self.me_update_interval = 0
			
			if self.me_update_interval + config.system.statusbar_update_interval_right > config.system.statusbar_update_interval_left:
				countdown = strings.countdown_updating
			else:
				m, s = divmod(config.system.statusbar_update_interval_left - self.me_update_interval, 60)
				countdown = strings.countdown % (m, s)
			
			left_text = strings.statusbar_left % {'username': self.me.screen_name, 'followers': self.me.followers_count, 'following': self.me.friends_count, 'tweets': self.me.statuses_count, 'favorites': self.me.favourites_count}
			right_text = strings.statusbar_right % {'cached_tweets': self.cached_tweet_count, 'time': time.strftime(config.var.statusbar_time_format), 'countdown': countdown}
			space = config.var.statusbar_spacing_character * (self.width - (len(left_text) + len(right_text)))
			self.statusbar_content.set_text(('statusbar bold', left_text + space + right_text))
			if self.notification_count > 0 and self.has_focus():
				self.reset_notifications()
			self.statusbar_refresh()
			if self.redraw_from_thread:
				self.redraw()
			self.me_update_interval += config.system.statusbar_update_interval_right
			time.sleep(config.system.statusbar_update_interval_right)
	
	"""def post_tweet(self, data, in_reply_to = None, in_reply_to_user = None):
		post = True
		twitlonger_used = False
		try:
			tweet = self.api.update_status(status = data, in_reply_to_status_id = in_reply_to)
		except tweetpony.APIError as err:
			if u"140" in err.message:
				if config.var.always_extend_tweet or self.yes_no_dialog(strings.use_twitlonger):
					if not(self.me.protected) or (self.me.protected and self.yes_no_dialog(strings.twitlonger_protected_account)):
						twitlonger_post = self.twitlonger_api.post_tweet(self.me.screen_name, data, in_reply_to, in_reply_to_user)
						if twitlonger_post.error is not None:
							self.info_dialog(strings.twitlonger_error % twitlonger_post.error, False)
							post = False
						else:
							twitlonger_used = True
							data = twitlonger_post.post.content
					else:
						post = False
				else:
					post = False
				if post:
					try:
						tweet = self.api.update_status(status = data, in_reply_to_status_id = in_reply_to)
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						return False
					else:
						if twitlonger_used:
							self.twitlonger_api.link_posts(twitlonger_post.post.id, tweet.id_str)
				else:
					return False
			else:
				self.info_dialog(strings.api_error % (err.code, err.description))
				return False
		return tweet"""
	
	def post_tweet(self, data, in_reply_to = None, in_reply_to_user = None):
		post = True
		twextender_used = False
		try:
			tweet = self.api.update_status(status = data, in_reply_to_status_id = in_reply_to)
		except tweetpony.APIError as err:
			if u"140" in err.message:
				if config.var.always_extend_tweet or self.yes_no_dialog(strings.use_twextender):
					if not(self.me.protected) or (self.me.protected and self.yes_no_dialog(strings.twextender_protected_account)):
						twextender_post = self.twextender_api.post_tweet(self.me.screen_name, data, in_reply_to_user, in_reply_to)
						if 'error' in twextender_post.keys():
							self.info_dialog(strings.twextender_error % twextender_post['error'], False)
							post = False
						else:
							twextender_used = True
							data = twextender_post['tweetable_text']
					else:
						post = False
				else:
					post = False
				if post:
					try:
						tweet = self.api.update_status(status = data, in_reply_to_status_id = in_reply_to)
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						return False
				else:
					return False
			else:
				self.info_dialog(strings.api_error % (err.code, err.description))
				return False
		return tweet
	
	def add_tweet(self, short_code, author, text, source, is_mention, favorited, redraw = True):
		if self.is_word_filtered_text(text) or self.is_user_filtered(author) or self.is_client_filtered(source) or self.is_regex_filtered(text):
			return False
		highlighted = (self.is_word_highlighted_text(text) or self.is_user_highlighted(author) or self.is_client_highlighted(source) or self.is_regex_highlighted(text))
		#text = expand_urls(text)
		part1 = strings.tweet_code_prefix % short_code
		if author != u"":
			part2 = strings.tweet_prefix % author
		else:
			part2 = u""
		text = self.line_break(text, (part1 + part2))
		if is_mention and favorited:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('favorite mention', text)]))
		elif is_mention:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('mention', text)]))
		elif favorited:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('favorite', text)]))
		elif highlighted:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('highlighted', text)]))
		else:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('tweet', text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def add_retweet(self, short_code, retweeted_by, original_author, text, source, is_mention, favorited, redraw = True):
		if self.is_word_filtered_text(text) or self.is_user_filtered(retweeted_by) or self.is_user_filtered(original_author) or self.is_client_filtered(source) or self.is_regex_filtered(text):
			return False
		highlighted = (self.is_word_highlighted_text(text) or self.is_user_highlighted(original_author) or self.is_client_highlighted(source) or self.is_regex_highlighted(text))
		#text = expand_urls(text)
		part1 = strings.tweet_code_prefix % short_code
		part2 = strings.retweet_prefix % (retweeted_by, original_author)
		text = self.line_break(text, (part1 + part2))
		if is_mention and favorited:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('favorite mention', text)]))
		elif is_mention:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('mention', text)]))
		elif favorited:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('favorite', text)]))
		elif highlighted:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('highlighted', text)]))
		else:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('tweet', text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def add_direct_message(self, short_code, author, text, sent = False, redraw = True):
		if self.is_word_filtered_text(text) or self.is_user_filtered(author) or self.is_regex_filtered(text):
			return False
		#text = expand_urls(text)
		part1 = strings.direct_message_code_prefix % short_code
		if author != u"":
			part2 = strings.direct_message_prefix % author
		else:
			part2 = u""
		text = self.line_break(text, (part1 + part2))
		if sent:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('tweet', text)]))
		else:
			self.feed_lines.append(urwid.Text([('short code', part1), ('author', part2), ('mention', text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def add_notification(self, text, is_mention, redraw = True):
		indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
		text = self.line_break(text, indent)
		if is_mention:
			self.feed_lines.append(urwid.Text([indent, ('mention', text)]))
		else:
			self.feed_lines.append(urwid.Text([indent, ('notification', text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def add_warning(self, text, redraw = True):
		indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
		text = self.line_break(text, indent)
		self.feed_lines.append(urwid.Text([indent, ('warning', text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def add_error(self, text, redraw = True):
		indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
		text = self.line_break(text, indent)
		self.feed_lines.append(urwid.Text([indent, ('error', text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def add_text(self, text, has_indent = False, color = None, redraw = True):
		if has_indent:
			indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
		else:
			indent = u""
		text = self.line_break(text, indent)
		if color is None:
			self.feed_lines.append(urwid.Text([indent, text]))
		else:
			self.feed_lines.append(urwid.Text([indent, (color, text)]))
		self.feed_refresh()
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def begin_block(self, title, color, redraw = True):
		if title == u"":
			block_separator = config.var.block_separator_character * self.width
		else:
			if len(strings.block_title_scheme % title) > self.width - 2:
				cutoff = int(round((len(strings.block_title_scheme % title) - (self.width - 2)) / 2))
				title = title[cutoff:-cutoff]
			
			character_count = (self.width - len(strings.block_title_scheme % title)) / 2
			block_separator = config.var.block_separator_character * character_count + (strings.block_title_scheme % title) + config.var.block_separator_character * character_count
		
		indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
		self.feed_lines.append(urwid.Text([indent, (color, block_separator)]))
		
		self.feed_refresh()
		
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def end_block(self, color, redraw = True):
		indent = u" " * len(strings.tweet_code_prefix % (u" " * config.var.short_code_length))
		self.feed_lines.append(urwid.Text([indent, (color, (config.var.block_separator_character * self.width))]))
		
		self.feed_refresh()
		
		if redraw and self.redraw_from_thread:
			self.redraw()
	
	def delete_line(self, short_code):
		for i in range(len(self.feed_lines)):
			if self.feed_lines[i].get_text()[0].startswith(short_code):
				self.feed_lines.remove(self.feed_lines[i])
				return True
		return False
	
	def replace_attribute(self, short_code, attribute_pairs):
		for i in range(len(self.feed_lines)):
			if self.feed_lines[i].get_text()[0].startswith(short_code):
				text, attributes = self.feed_lines[i].get_text()
				new_text = []
				current_pos = 0
				for attribute in attributes:
					new_pos = (current_pos + attribute[1])
					snippet = text[current_pos:new_pos]
					new_attribute = attribute[0]
					for pair in attribute_pairs:
						if attribute[0] == pair[0]:
							new_attribute = pair[1]
					new_text.append((new_attribute, snippet))
					current_pos = new_pos
				self.feed_lines[i].set_text(new_text)
				return True
		return False
	
	def get_data(self, identifier):
		identifier = str(identifier)
		try:
			if len(identifier) == config.var.short_code_length:
				self.code_db_cursor.execute("SELECT `code`, `ID`, `author`, `text`, `in_reply_to`, `tweet_obj` FROM `codes` WHERE `code` = ?", (identifier,))
			else:
				self.code_db_cursor.execute("SELECT `code`, `ID`, `author`, `text`, `in_reply_to`, `tweet_obj` FROM `codes` WHERE `ID` = ?", (identifier,))
			data = self.code_db_cursor.fetchone()
			return(data[0], long(data[1]), data[2], data[3], data[4], pickle.loads(base64.b64decode(data[5])))
		except:
			return False
	
	def get_last_data(self):
		try:
			self.code_db_cursor.execute("SELECT `code`, `ID`, `author`, `text`, `in_reply_to`, `tweet_obj` FROM `codes` ORDER BY `ID` DESC LIMIT 1")
			data = self.code_db_cursor.fetchone()
			return(data[0], long(data[1]), data[2], data[3], data[4], pickle.loads(base64.b64decode(data[5])))
		except:
			return False
	
	def get_tweet_id(self, code):
		try:
			self.code_db_cursor.execute("SELECT `ID` FROM `codes` WHERE `code` = ?", (code,))
			tweet_id = long(self.code_db_cursor.fetchone()[0])
			return tweet_id
		except:
			return False
	
	def get_code(self, tweet_id, author, text, tweet_obj, in_reply_to = None):
		if in_reply_to is not None:
			in_reply_to = str(in_reply_to)
		try:
			try:
				self.code_db_cursor.execute("SELECT `code` FROM `codes` WHERE `ID` = ?", (tweet_id,))
				short_code = self.code_db_cursor.fetchone()[0]
				return short_code
			except:
				self.code_db_cursor.execute("SELECT `code` FROM `codes` ORDER BY `code_id` DESC")
				rows = self.code_db_cursor.fetchall()
				self.cached_tweet_count = len(rows)
				rows = rows[:config.var.min_tweets_to_keep]
				codes = []
				for row in rows:
					codes.append(row[0])
				code_in_use = True
				while code_in_use:
					short_code = gen_short_code(tweet_id)
					code_in_use = (short_code in codes)
				self.delete_line(short_code)
				self.code_db_cursor.execute("DELETE FROM `codes` WHERE `code` = ?", (short_code,))
				self.code_db_cursor.execute("INSERT INTO `codes` (`code`, `ID`, `author`, `text`, `in_reply_to`, `tweet_obj`) VALUES (?, ?, ?, ?, ?, ?)", (short_code, tweet_id, author, html_unescape(text.replace("\n", " ")), in_reply_to, base64.b64encode(pickle.dumps(tweet_obj))))
				self.code_db.commit()
				return short_code
		except:
			return False
	
	def get_replies(self, identifier):
		identifier = str(identifier)
		try:
			if len(identifier) == config.var.short_code_length:
				tweet_id = self.get_tweet_id(identifier)
				if not tweet_id:
					return False
			else:
				tweet_id = identifier
			self.code_db_cursor.execute("SELECT `code`, `ID`, `author`, `text`, `in_reply_to`, `tweet_obj` FROM `codes` WHERE `in_reply_to` = ?", (tweet_id,))
			tweets = [list(item) for item in self.code_db_cursor.fetchall()]
			for i in range(len(tweets)):
				tweets[i][5] = pickle.loads(base64.b64decode(tweets[i][5]))
			return tweets
		except:
			return []
	
	def to_tweet_object(self, tweet_data):
		obj = Object()
		setattr(obj, "id", tweet_data[1])
		setattr(obj, "id_str", str(tweet_data[1]))
		setattr(obj, "user", Object())
		setattr(obj.user, "screen_name", tweet_data[2])
		setattr(obj, "text", tweet_data[3])
		setattr(obj, "in_reply_to_status_id", tweet_data[4])
		if tweet_data[4] is None:
			setattr(obj, "in_reply_to_status_id_str", tweet_data[4])
		else:
			setattr(obj, "in_reply_to_status_id_str", str(tweet_data[4]))
		return obj
	
	def filter_word(self, word):
		if word.lower() in self.filtered_words:
			return False
		else:
			self.filtered_words.append(word.lower())
			self.db_cursor.execute("INSERT INTO `filtered_words` (`word`) VALUES (?)", (word.lower(),))
			self.db.commit()
		return True
	
	def filter_user(self, user):
		if user.lower() in self.filtered_users:
			return False
		else:
			self.filtered_users.append(user.lower())
			self.db_cursor.execute("INSERT INTO `filtered_users` (`user`) VALUES (?)", (user.lower(),))
			self.db.commit()
		return True
	
	def filter_client(self, client):
		if client.lower() in self.filtered_clients:
			return False
		else:
			self.filtered_clients.append(client.lower())
			self.db_cursor.execute("INSERT INTO `filtered_clients` (`client`) VALUES (?)", (client.lower(),))
			self.db.commit()
		return True
	
	def filter_regex(self, regex):
		if (regex, re.compile(regex, re.MULTILINE)) in self.filtered_regexes:
			return False
		else:
			self.filtered_regexes.append((regex, re.compile(regex, re.MULTILINE)))
			self.db_cursor.execute("INSERT INTO `filtered_regexes` (`regex`) VALUES (?)", (regex,))
			self.db.commit()
		return True
	
	def unfilter_word(self, word):
		if word.lower() not in self.filtered_words:
			return False
		else:
			self.filtered_words.remove(word.lower())
			self.db_cursor.execute("DELETE FROM `filtered_words` WHERE `word` = ?", (word.lower(),))
			self.db.commit()
		return True
	
	def unfilter_user(self, user):
		if user.lower() not in self.filtered_users:
			return False
		else:
			self.filtered_users.remove(user.lower())
			self.db_cursor.execute("DELETE FROM `filtered_users` WHERE `user` = ?", (user.lower(),))
			self.db.commit()
		return True
	
	def unfilter_client(self, client):
		if client.lower() not in self.filtered_clients:
			return False
		else:
			self.filtered_clients.remove(client.lower())
			self.db_cursor.execute("DELETE FROM `filtered_clients` WHERE `client` = ?", (client.lower(),))
			self.db.commit()
		return True
	
	def unfilter_regex(self, regex):
		if (regex, re.compile(regex, re.MULTILINE)) not in self.filtered_regexes:
			return False
		else:
			self.filtered_regexes.remove((regex, re.compile(regex, re.MULTILINE)))
			self.db_cursor.execute("DELETE FROM `filtered_regexes` WHERE `regex` = ?", (regex,))
			self.db.commit()
		return True
	
	def is_word_filtered(self, word):
		return word.lower() in self.filtered_words
	
	def is_user_filtered(self, user):
		return user.lower() in self.filtered_users
	
	def is_client_filtered(self, client):
		return client.lower() in self.filtered_clients
	
	def is_regex_filtered(self, text):
		for raw_regex, compiled_regex in self.filtered_regexes:
			if compiled_regex.match(text):
				return True
		return False
	
	def is_word_filtered_text(self, text):
		for word in self.filtered_words:
			if word.lower() in text.lower():
				return True
		return False
	
	def highlight_word(self, word):
		if word.lower() in self.highlighted_words:
			return False
		else:
			self.highlighted_words.append(word.lower())
			self.db_cursor.execute("INSERT INTO `highlighted_words` (`word`) VALUES (?)", (word.lower(),))
			self.db.commit()
		return True
	
	def highlight_user(self, user):
		if user.lower() in self.highlighted_users:
			return False
		else:
			self.highlighted_users.append(user.lower())
			self.db_cursor.execute("INSERT INTO `highlighted_users` (`user`) VALUES (?)", (user.lower(),))
			self.db.commit()
		return True
	
	def highlight_client(self, client):
		if client.lower() in self.highlighted_clients:
			return False
		else:
			self.highlighted_clients.append(client.lower())
			self.db_cursor.execute("INSERT INTO `highlighted_clients` (`client`) VALUES (?)", (client.lower(),))
			self.db.commit()
		return True
	
	def highlight_regex(self, regex):
		if (regex, re.compile(regex, re.MULTILINE)) in self.highlighted_regexes:
			return False
		else:
			self.highlighted_regexes.append((regex, re.compile(regex, re.MULTILINE)))
			self.db_cursor.execute("INSERT INTO `highlighted_regexes` (`regex`) VALUES (?)", (regex,))
			self.db.commit()
		return True
	
	def unhighlight_word(self, word):
		if word.lower() not in self.highlighted_words:
			return False
		else:
			self.highlighted_words.remove(word.lower())
			self.db_cursor.execute("DELETE FROM `highlighted_words` WHERE `word` = ?", (word.lower(),))
			self.db.commit()
		return True
	
	def unhighlight_user(self, user):
		if user.lower() not in self.highlighted_users:
			return False
		else:
			self.highlighted_users.remove(user.lower())
			self.db_cursor.execute("DELETE FROM `highlighted_users` WHERE `user` = ?", (user.lower(),))
			self.db.commit()
		return True
	
	def unhighlight_client(self, client):
		if client.lower() not in self.highlighted_clients:
			return False
		else:
			self.highlighted_clients.remove(client.lower())
			self.db_cursor.execute("DELETE FROM `highlighted_clients` WHERE `client` = ?", (client.lower(),))
			self.db.commit()
		return True
	
	def unhighlight_regex(self, regex):
		if (regex, re.compile(regex, re.MULTILINE)) not in self.highlighted_regexes:
			return False
		else:
			self.highlighted_regexes.remove((regex, re.compile(regex, re.MULTILINE)))
			self.db_cursor.execute("DELETE FROM `highlighted_regexes` WHERE `regex` = ?", (regex,))
			self.db.commit()
		return True
	
	def is_word_highlighted(self, word):
		return word.lower() in self.highlighted_words
	
	def is_user_highlighted(self, user):
		return user.lower() in self.highlighted_users
	
	def is_client_highlighted(self, client):
		return client.lower() in self.highlighted_clients
	
	def is_regex_highlighted(self, text):
		for raw_regex, compiled_regex in self.highlighted_regexes:
			if compiled_regex.match(text):
				return True
		return False
	
	def is_word_highlighted_text(self, text):
		for word in self.highlighted_words:
			if word.lower() in text.lower():
				return True
		return False
	
	def backfill(self, count = None, since_id = None):
		tweets = self.api.home_timeline(count = count, since_id = since_id)
		tweets.reverse()
		for tweet in tweets:
			self.process_status(tweet)
	
	def process_status(self, status):
		if status.user.id == self.me.id:
			self.me = status.user
			self.me_update_interval = config.system.statusbar_update_interval_left + 1
		text = html_unescape(status.text).replace(u"\n", u" ")
		is_mention = False
		if hasattr(status, 'entities'):
			for user in status.entities['user_mentions']:
				if user['id_str'] == self.me.id_str:
					is_mention = True
					break
		if not(self.afk_mode) or (self.afk_mode and is_mention):
			if hasattr(status, 'retweeted_status'):
				original_author = status.retweeted_status.user.screen_name
				text = html_unescape(status.retweeted_status.text).replace('\n', ' ')
				if hasattr(status.retweeted_status, 'entities'):
					for url in status.retweeted_status.entities['urls']:
						text = text.replace(url['url'], url['expanded_url'])
					if 'media' in status.retweeted_status.entities.keys():
						for media in status.retweeted_status.entities['media']:
							text = text.replace(media['url'], media['expanded_url'])
				status.id, status.user.screen_name, original_author, status.text, is_mention = plugins.on_retweet(self, status.id, status.user.screen_name, original_author, status.text, is_mention)
				self.add_retweet(self.get_code(str(status.id), status.user.screen_name, status.text, status, status.in_reply_to_status_id), status.user.screen_name, original_author, text, status.retweeted_status.source, is_mention, status.retweeted_status.favorited)
			else:
				if hasattr(status, 'entities'):
					for url in status.entities['urls']:
						text = text.replace(url['url'], url['expanded_url'])
					if 'media' in status.entities.keys():
						for media in status.entities['media']:
							text = text.replace(media['url'], media['expanded_url'])
				status.id, status.user.screen_name, status.text, is_mention = plugins.on_tweet(self, status.id, status.user.screen_name, status.text, is_mention)
				self.add_tweet(self.get_code(str(status.id), status.user.screen_name, status.text, status, status.in_reply_to_status_id), status.user.screen_name, text, status.source, is_mention, status.favorited)
			if is_mention:
				self.notify(config.var.notify_freq, config.var.notify_dur, status = status)
		
		self.feed_refresh()
		if self.redraw_from_thread:
			self.redraw()
	
	def process_direct_message(self, message):
		if message.recipient.screen_name == self.me.screen_name:
			text = html_unescape(message.text).replace('\n', ' ')
			if hasattr(message, 'entities'):
				for url in message.entities['urls']:
					text = text.replace(url['url'], url['expanded_url'])
				if 'media' in message.entities.keys():
					for media in message.entities['media']:
						text = text.replace(media['url'], media['expanded_url'])
			self.add_direct_message(self.get_code(str(message.id), message.sender.screen_name, message.text, message, None), message.sender.screen_name, text, False)
			self.notify(config.var.notify_freq, config.var.notify_dur, message = message)
			self.feed_refresh()
			if self.redraw_from_thread:
				self.redraw()
	
	def process_event(self, event):
		if event['source']['screen_name'] != self.me.screen_name and not self.is_user_filtered(event['source']['screen_name']):
			if event['event'] == 'favorite':
				event_text = strings.favorite_notification % (event['source']['name'], event['source']['screen_name'], html_unescape(event['target_object']['text']))
				self.add_notification(event_text, True)
				self.notify(config.var.notify_freq, config.var.notify_dur, event = event_text)
			elif event['event'] == 'unfavorite':
				event_text = strings.unfavorite_notification % (event['source']['name'], event['source']['screen_name'], html_unescape(event['target_object']['text']))
				self.add_notification(event_text, True)
				self.notify(config.var.notify_freq, config.var.notify_dur, event = event_text)
			elif event['event'] == 'follow':
				event_text = strings.follower_notification % (event['source']['name'], event['source']['screen_name'])
				self.add_notification(event_text, True)
				self.notify(config.var.notify_freq, config.var.notify_dur, event = event_text)
	
	def start_stream(self):
		class FlutterProcessor(tweetpony.StreamProcessor):
			def on_status(self_, status):
				self.process_status(status)
			
			def on_message(self_, message):
				self.process_direct_message(message)
			
			def on_event(self_, event):
				self.process_event(event)
			
			def on_delete(self_, event):
				if 'status' in event:
					status_id, user_id = plugins.on_delete(self, event.status.id, event.status.user_id)
					data = self.get_data(str(status_id))
					if data:
						short_code, tweet_id, del_username, text, in_reply_to, _tweet = data
						if config.var.mark_deleted:
							self.replace_attribute(short_code, [("tweet", "deleted"), ("highlighted", "deleted"), ("mention", "deleted mention")])
						else:
							self.delete_line(short_code)
						self.feed_refresh()
						if self.redraw_from_thread:
							self.redraw()
				elif 'direct_message' in event:
					message_id, user_id = plugins.on_direct_message_delete(self, event.direct_message.id, event.direct_message.user_id)
					data = self.get_data(str(message_id))
					if data:
						short_code, message_id, del_username, text, in_reply_to, _message = data
						if config.var.mark_deleted:
							self.replace_attribute(short_code, [("tweet", "deleted"), ("highlighted", "deleted"), ("mention", "deleted mention")])
						else:
							self.delete_line(short_code)
						self.feed_refresh()
						if self.redraw_from_thread:
							self.redraw()
		
		stream_processor = FlutterProcessor(self.api)
		while True:
			try:
				if self.stream_user_ids or self.stream_locations:
					self.api.filter_stream(track = self.stream_keywords + [u"@" + self.me.screen_name], follow = self.stream_user_ids + [self.me.id], locations = self.stream_locations, processor = stream_processor)
				else:
					self.api.user_stream(processor = stream_processor, track = self.stream_keywords)
			except SSLError:
				#self.add_error(strings.timeout % config.system.stream_reconnect_delay)
				#time.sleep(config.system.stream_reconnect_delay)
				if not(self.stream_keywords or self.stream_user_ids or self.stream_locations):
					last_tweet_id = self.get_last_data()
					if last_tweet_id:
						last_tweet_id = last_tweet_id[1]
					else:
						last_tweet_id = None
					self.backfill(since_id = last_tweet_id)
				#self.add_notification(strings.stream_reconnecting, False)
				#self.notification(strings.reconnected_after_stream_error)
			except:
				#traceback.print_exc()
				#self.add_error(strings.stream_error % config.system.stream_reconnect_delay)
				#time.sleep(config.system.stream_reconnect_delay)
				if not(self.stream_keywords or self.stream_user_ids or self.stream_locations):
					last_tweet_id = self.get_last_data()
					if last_tweet_id:
						last_tweet_id = last_tweet_id[1]
					else:
						last_tweet_id = None
					self.backfill(since_id = last_tweet_id)
				#self.add_notification(strings.stream_reconnecting, False)
				#self.notification(strings.reconnected_after_stream_error)
	
	def process_command(self, command, data_array):
		clear = True
		has_data = (len(data_array) > 0)
		data = ' '.join(data_array)
		
		if command == config.commands.logout:
			self.logout()
			self.quit()
		elif command == config.commands.help:
			while True:
				try:
					choice = self.list_dialog(strings.help_header, [entry[0] for entry in strings.help_entries])[1][0]
				except:
					break
				else:
					self.info_dialog("%s\n\n%s" % (strings.help_entries[choice][0], strings.help_entries[choice][1]))
		elif command == config.commands.tweet or (not(config.var.tweet_command_required) and (command[:1] != config.commands.cmd_prefix or (len(command) >= 2 and command[0] == config.commands.cmd_prefix and command[1] == command[0]))):
			if command[:1] != config.commands.cmd_prefix:
				data = command + ' ' + data
			
			if len(command) >= 2 and command[0] == config.commands.cmd_prefix and command[1] == command[0]:
				command = command[1:]
				data = command + ' ' + data
			
			if data != '':
				tweet = self.post_tweet(data)
				clear = (tweet != False)
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.retweet:
			if has_data:
				short_code = data_array[0]
				del data_array[0]
				text = ' '.join(data_array)
				tweet_data = self.get_data(short_code)
				if tweet_data != False:
					short_code, tweet_id, tweet_author, tweet_text, in_reply_to, _tweet = tweet_data
					if hasattr(_tweet, "retweeted_status"):
						tweet_id = _tweet.retweeted_status.id_str
						tweet_author = _tweet.retweeted_status.user.screen_name
						tweet_text = _tweet.retweeted_status.text
					if text != '':
						data = strings.retweet_scheme % (text, tweet_author, html_unescape(tweet_text))
						tweet = self.post_tweet(data, in_reply_to = tweet_id, in_reply_to_user = tweet_author)
						clear = (tweet != False)
					else:
						try:
							self.api.retweet(id = tweet_id)
						except tweetpony.APIError as err:
							if "permissible" in err.message:
								self.info_dialog(strings.retweet_failed)
							else:
								self.info_dialog(strings.api_error % (err.code, err.description))
								clear = False
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.favorite:
			if has_data:
				short_code = data_array[0]
				tweet_data = self.get_data(short_code)
				if tweet_data != False:
					short_code, tweet_id, tweet_author, tweet_text, in_reply_to, _tweet = tweet_data
					if hasattr(_tweet, "retweeted_status"):
						tweet_id = _tweet.retweeted_status.id_str
						tweet_author = _tweet.retweeted_status.user.screen_name
						tweet_text = _tweet.retweeted_status.text
					try:
						self.api.favorite(id = tweet_id)
						tweet_preview = tweet_text if len(tweet_text) <= config.var.tweet_preview_length else tweet_text[:config.var.tweet_preview_length] + u" […]"
						self.replace_attribute(short_code, [("tweet", "favorite"), ("highlighted", "favorite"), ("mention", "favorite mention")])
						# self.notification(strings.favorited % (tweet_preview, tweet_author))
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						clear = False
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unfavorite:
			if has_data:
				short_code = data_array[0]
				tweet_data = self.get_data(short_code)
				if tweet_data != False:
					short_code, tweet_id, tweet_author, tweet_text, in_reply_to, _tweet = tweet_data
					if hasattr(_tweet, "retweeted_status"):
						tweet_id = _tweet.retweeted_status.id_str
						tweet_author = _tweet.retweeted_status.user.screen_name
						tweet_text = _tweet.retweeted_status.text
					try:
						self.api.unfavorite(id = tweet_id)
						tweet_preview = tweet_text if len(tweet_text) <= config.var.tweet_preview_length else tweet_text[:config.var.tweet_preview_length] + u" […]"
						self.replace_attribute(short_code, [("favorite", "tweet"), ("highlighted", "favorite"), ("favorite mention", "mention")])
						# self.notification(strings.unfavorited % (tweet_preview, tweet_author))
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						clear = False
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.follow:
			if has_data:
				try:
					self.api.follow(screen_name = data_array[0])
					self.notification(strings.followed % data)
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unfollow:
			if has_data:
				try:
					self.api.unfollow(screen_name = data_array[0])
					self.notification(strings.unfollowed % data)
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.last_tweets:
			if has_data:
				username = data_array[0]
			else:
				username = self.me.screen_name
			try:
				last_tweets = self.api.user_timeline(screen_name = username, count = config.var.last_tweet_count)
				tweets = []
				for tweet in last_tweets:
					tweet.id, tweet.user.screen_name, tweet.text, is_mention = plugins.on_tweet(self, tweet.id, tweet.user.screen_name, tweet.text, False)
					short_code = self.get_code(str(tweet.id), tweet.user.screen_name, tweet.text, tweet, tweet.in_reply_to_status_id)
					tweets.append(strings.tweet_list_format % (short_code, html_unescape(tweet.text)))
				try:
					choice = self.list_dialog(strings.last_tweets_header % (len(last_tweets), username), tweets)[1][1].split()[0]
				except:
					pass
				else:
					self.cmdline_content.set_edit_text(u"%s %s " % (config.commands.reply, choice))
					self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
			except tweetpony.APIError as err:
				self.info_dialog(strings.api_error % (err.code, err.description))
				clear = False
		elif command == config.commands.profile:
			if has_data:
				username = data_array[0]
			else:
				username = self.me.screen_name
			try:
				user = self.api.get_user(screen_name = username)
				lines = []
				lines.append(strings.profile_header % (html_unescape(user.name), user.screen_name) + u"\n")
				try:
					lines.append(strings.profile_item_bio % html_unescape(unicode(user.description)).replace(u"\n", u" ") + u"\n")
				except AttributeError:
					pass
				try:
					lines.append(strings.profile_item_location % html_unescape(unicode(user.location)))
				except AttributeError:
					pass
				try:
					lines.append(strings.profile_item_website % html_unescape(unicode(user.url)))
				except AttributeError:
					pass
				lines.append(strings.profile_item_followers % unicode(user.followers_count))
				lines.append(strings.profile_item_following % unicode(user.friends_count))
				lines.append(strings.profile_item_tweets % unicode(user.statuses_count))
				lines.append(strings.profile_item_listed % unicode(user.listed_count))
				lines.append(strings.profile_item_lang % user.lang)
				try:
					lines.append(strings.profile_item_timezone % user.time_zone)
				except AttributeError:
					pass
				if user.id == self.me.id:
					action = self.dialog(u"\n".join(lines), [strings.button_ok, strings.button_edit_profile], None, None, True)['button']
					if action == strings.button_edit_profile:
						entries = self.dialog(strings.edit_profile_header, [strings.button_ok], [(strings.caption_name, self.me.name), (strings.caption_location, self.me.location), (strings.caption_website, self.me.url), (strings.caption_bio, self.me.description.replace(u"\n", u" "))], None, True)['texts']
						if entries:
							try:
								self.me = self.api.update_profile(name = entries[0], location = entries[1], url = entries[2], description = entries[3])
								self.notification(strings.profile_updated)
							except tweetpony.APIError as err:
								self.info_dialog(strings.api_error % (err.code, err.description))
								clear = False
				else:
					self.info_dialog(u"\n".join(lines))
			except tweetpony.APIError as err:
				self.info_dialog(strings.api_error % (err.code, err.description))
				clear = False
		elif command == config.commands.reply:
			if has_data:
				short_code = data_array[0]
				del data_array[0]
				text = ' '.join(data_array)
				if text != '':
					tweet_data = self.get_data(short_code)
					if tweet_data:
						short_code, tweet_id, tweet_author, tweet_text, in_reply_to, _tweet = tweet_data
						if hasattr(_tweet, "retweeted_status"):
							user = _tweet.retweeted_status.user.screen_name
							tweet_id = _tweet.retweeted_status.id_str
						else:
							user = tweet_author
						data = strings.reply % (user, text)
						tweet = self.post_tweet(data, tweet_id, user)
						clear = (tweet != False)
					else:
						self.info_dialog(strings.invalid_short_code % (short_code, command, data))
						clear = False
				else:
					self.info_dialog(strings.data_required % command)
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.mentions:
			try:
				mentions = self.api.mentions(count = config.var.mentions_count)
				tweets = []
				for mention in mentions:
					mention.id, mention.user.screen_name, mention.text, is_mention = plugins.on_tweet(self, mention.id, mention.user.screen_name, mention.text, False)
					short_code = self.get_code(str(mention.id), mention.user.screen_name, mention.text, mention, mention.in_reply_to_status_id)
					tweets.append(strings.mention_list_format % (short_code, mention.user.screen_name, mention.text))
				try:
					choice = self.list_dialog(strings.mentions_header % len(mentions), tweets)[1][1].split()[0]
				except:
					pass
				else:
					self.cmdline_content.set_edit_text(u"%s %s " % (config.commands.reply, choice))
					self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
					action = self.dialog(strings.mention_select_action, [strings.action_reply, strings.view_conversation], None, None)['button']
					if action == strings.action_reply:
						self.cmdline_content.set_edit_text(u"%s %s " % (config.commands.reply, choice))
					else:
						self.cmdline_content.set_edit_text(u"%s %s" % (config.commands.conversation, choice))
					self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
			except tweetpony.APIError as err:
				self.info_dialog(strings.api_error % (err.code, err.description))
				clear = False
		elif command == config.commands.conversation:
			if has_data:
				short_code = data_array[0]
				try:
					count = int(data_array[1])
				except:
					count = config.var.conversation_default_tweet_count
				
				tweet_id = self.get_tweet_id(short_code)
				if tweet_id:
					try:
						conversation = [tweet[5] for tweet in self.get_replies(tweet_id)]
						x = 0
						tweet = self.get_data(tweet_id)
						if tweet:
							tweet = tweet[5]
						else:
							tweet = self.api.get_status(id = tweet_id)
						if hasattr(tweet, 'retweeted_status'):
							tweet = tweet.retweeted_status
						conversation.insert(0, tweet)
						while x < count:
							if hasattr(tweet, 'retweeted_status'):
								tweet = tweet.retweeted_status
							if tweet.in_reply_to_status_id is not None:
								ref = self.get_data(tweet.in_reply_to_status_id)
								if ref:
									ref = ref[5]
								else:
									ref = self.api.get_status(id = tweet.in_reply_to_status_id)
								conversation.insert(0, ref)
								x += 1
							else:
								break
							tweet = ref
						
						tweets = []
						for tweet in conversation:
							tweet.id, tweet.user.screen_name, tweet.text, is_mention = plugins.on_tweet(self, tweet.id, tweet.user.screen_name, tweet.text, False)
							short_code = self.get_code(str(tweet.id), tweet.user.screen_name, tweet.text, tweet, tweet.in_reply_to_status_id)
							tweets.append(strings.conversation_list_format % (short_code, tweet.user.screen_name, tweet.text))
						try:
							choice = self.list_dialog(strings.conversation_header, tweets)[1][1].split()[0]
						except:
							pass
						else:
							self.cmdline_content.set_edit_text(u"%s %s " % (config.commands.replyall, choice))
							self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						clear = False
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.relationship:
			if has_data:
				user1 = data_array[0]
				try:
					user2 = data_array[1]
				except:
					user2 = user1
					user1 = self.me.screen_name
				try:
					rel = self.api.get_friendship(source_screen_name = user1, target_screen_name = user2)
					rel1 = rel.following
					rel2 = rel.followed_by
					if rel1 and rel2:
						self.info_dialog(strings.rel_both % (user1, user2))
					elif rel1 and not(rel2):
						self.info_dialog(strings.rel_i_follow % (user1, user2))
					elif not(rel1) and rel2:
						self.info_dialog(strings.rel_following_me % (user1, user2))
					elif not(rel1) and not(rel2):
						self.info_dialog(strings.rel_none % (user1, user2))
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.delete:
			if has_data:
				short_code = data_array[0]
				tweet_data = self.get_data(short_code)
				if tweet_data:
					short_code, tweet_id, tweet_author, tweet_text, in_reply_to, _tweet = tweet_data
					try:
						if hasattr(_tweet, "recipient"):
							self.api.delete_message(id = tweet_id)
							message_preview = tweet_text if len(tweet_text) <= config.var.tweet_preview_length else tweet_text[:config.var.tweet_preview_length] + u" […]"
							self.notification(strings.message_deleted % (message_preview, _tweet.recipient.screen_name))
						else:
							self.api.delete_status(id = tweet_id)
							tweet_preview = tweet_text if len(tweet_text) <= config.var.tweet_preview_length else tweet_text[:config.var.tweet_preview_length] + u" […]"
							self.notification(strings.deleted % tweet_preview)
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						clear = False
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.replyall:
			if has_data:
				short_code = data_array[0]
				del data_array[0]
				text = ' '.join(data_array)
				tweet_data = self.get_data(short_code)
				if tweet_data != False:
					short_code, tweet_id, tweet_author, tweet_text, in_reply_to, _tweet = tweet_data
					users = []
					if hasattr(_tweet, "retweeted_status"):
						user = _tweet.retweeted_status.user.screen_name
						tweet_id = _tweet.retweeted_status.id_str
						users.append(u"@" + tweet_author)
					else:
						user = tweet_author
					users.append(u"@" + user)
					words = tweet_text.split()
					for word in words:
						if word[0] == u"@":
							word = re.sub(r"\W+$", "", word)
							if word[1:].lower() != self.me.screen_name.lower() and word[1:] != '' and word not in users:
								users.append(word)
					user_list = ' '.join(users)
					data = strings.replyall % (user_list, text)
					tweet = self.post_tweet(data, tweet_id, user)
					clear = (tweet != False)
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.dump:
			if has_data:
				short_code = data_array[0]
				tweet_id = self.get_tweet_id(short_code)
				if tweet_id != False:
					try:
						tweet = self.api.get_status(id = tweet_id)
						lines = []
						lines.append(strings.dump_header)
						lines.append(strings.dump_short_code % data_array[0])
						lines.append(strings.dump_internal_id % self.get_tweet_id(data_array[0]))
						lines.append(strings.dump_internal_in_reply_to % self.get_data(data_array[0])[4])
						lines.append(strings.dump_internal_username % self.get_data(data_array[0])[2])
						lines.append(strings.dump_internal_text % self.get_data(data_array[0])[3])
						lines.append(strings.dump_id % str(tweet.id))
						lines.append(strings.dump_in_reply_to % str(tweet.in_reply_to_status_id))
						lines.append(strings.dump_author % tweet.user.screen_name)
						lines.append(strings.dump_text % tweet.text)
						lines.append(strings.dump_source % tweet.source)
						self.info_dialog(u"\n".join(lines))
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						clear = False
				else:
					self.info_dialog(strings.invalid_short_code % (short_code, command, data))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.trends:
			try:
				trends = self.api.trends(id = 1)[0].trends
				try:
					choice = self.list_dialog(strings.trends_header, [trend.name for trend in trends])[1][1]
				except:
					pass
				else:
					self.cmdline_content.set_edit_text(u" %s" % choice)
			except tweetpony.APIError as err:
				self.info_dialog(strings.api_error % (err.code, err.description))
				clear = False
		elif command == config.commands.clear:
			self.clear_feed()
			self.feed_refresh()
		elif command == config.commands.filter_word:
			if has_data:
				if self.filter_word(data):
					self.notification(strings.filtered_word % data.lower())
				else:
					self.info_dialog(strings.filter_word_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.filter_user:
			if has_data:
				if self.filter_user(data):
					self.notification(strings.filtered_user % data.lower())
				else:
					self.info_dialog(strings.filter_user_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.filter_client:
			if has_data:
				if self.filter_client(data):
					self.notification(strings.filtered_client % data.lower())
				else:
					self.info_dialog(strings.filter_client_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.filter_regex:
			if has_data:
				if self.filter_regex(data):
					self.notification(strings.filtered_regex % data)
				else:
					self.info_dialog(strings.filter_regex_error % data)
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unfilter_word:
			if has_data:
				if self.unfilter_word(data):
					self.notification(strings.unfiltered_word % data.lower())
				else:
					self.info_dialog(strings.unfilter_word_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unfilter_user:
			if has_data:
				if self.unfilter_user(data):
					self.notification(strings.unfiltered_user % data.lower())
				else:
					self.info_dialog(strings.unfilter_user_error % data.lower())
			else:
				self.info_dialog(strings.data_required % command)
		elif command == config.commands.unfilter_client:
			if has_data:
				if self.unfilter_client(data):
					self.notification(strings.unfiltered_client % data.lower())
				else:
					self.info_dialog(strings.unfilter_client_error % data.lower())
					clear = False
		elif command == config.commands.unfilter_regex:
			if has_data:
				if self.unfilter_regex(data):
					self.notification(strings.unfiltered_regex % data)
				else:
					self.info_dialog(strings.unfilter_regex_error % data)
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.list_word_filter:
			word_filter = ", ".join(self.filtered_words)
			self.info_dialog(strings.word_filter % word_filter)
		elif command == config.commands.list_user_filter:
			user_filter = ", ".join(["@" + user for user in self.filtered_users])
			self.info_dialog(strings.user_filter % user_filter)
		elif command == config.commands.list_client_filter:
			client_filter = ", ".join(self.filtered_clients)
			self.info_dialog(strings.client_filter % client_filter)
		elif command == config.commands.list_regex_filter:
			regex_filter = ", ".join([regex[0] for regex in self.filtered_regexes])
			self.info_dialog(strings.regex_filter % regex_filter)
		elif command == config.commands.highlight_word:
			if has_data:
				if self.highlight_word(data):
					self.notification(strings.highlighted_word % data.lower())
				else:
					self.info_dialog(strings.highlight_word_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.highlight_user:
			if has_data:
				if self.highlight_user(data):
					self.notification(strings.highlighted_user % data.lower())
				else:
					self.info_dialog(strings.highlight_user_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.highlight_client:
			if has_data:
				if self.highlight_client(data):
					self.notification(strings.highlighted_client % data.lower())
				else:
					self.info_dialog(strings.highlight_client_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.highlight_regex:
			if has_data:
				if self.highlight_regex(data):
					self.notification(strings.highlighted_regex % data)
				else:
					self.info_dialog(strings.highlight_regex_error % data)
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unhighlight_word:
			if has_data:
				if self.unhighlight_word(data):
					self.notification(strings.unhighlighted_word % data.lower())
				else:
					self.info_dialog(strings.unhighlight_word_error % data.lower())
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unhighlight_user:
			if has_data:
				if self.unhighlight_user(data):
					self.notification(strings.unhighlighted_user % data.lower())
				else:
					self.info_dialog(strings.unhighlight_user_error % data.lower())
			else:
				self.info_dialog(strings.data_required % command)
		elif command == config.commands.unhighlight_client:
			if has_data:
				if self.unhighlight_client(data):
					self.notification(strings.unhighlighted_client % data.lower())
				else:
					self.info_dialog(strings.unhighlight_client_error % data.lower())
					clear = False
		elif command == config.commands.unhighlight_regex:
			if has_data:
				if self.unhighlight_regex(data):
					self.notification(strings.unhighlighted_regex % data)
				else:
					self.info_dialog(strings.unhighlight_regex_error % data)
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.list_highlighted_words:
			highlighted_words = ", ".join(self.highlighted_words)
			self.info_dialog(strings.highlighted_words % highlighted_words)
		elif command == config.commands.list_highlighted_users:
			highlighted_users = ", ".join(["@" + user for user in self.highlighted_users])
			self.info_dialog(strings.highlighted_users % highlighted_users)
		elif command == config.commands.list_highlighted_clients:
			highlighted_clients = ", ".join(self.highlighted_clients)
			self.info_dialog(strings.highlighted_clients % highlighted_clients)
		elif command == config.commands.list_highlighted_regexes:
			highlighted_regexes = "\n".join([regex[0] for regex in self.highlighted_regexes])
			self.info_dialog(strings.highlighted_regexes % highlighted_regexes)
		elif command == config.commands.messages:
			try:
				received_messages = self.api.received_messages(count = config.var.messages_count)
				sent_messages = self.api.sent_messages(count = config.var.messages_count)
				messages = received_messages + sent_messages
				messages.sort(key = lambda x: x.created_at, reverse=True)
				dms = []
				for message in messages:
					message.id, message.sender.screen_name, message.text = plugins.on_message(self, message.id, message.sender.screen_name, message.text)
					short_code = self.get_code(str(message.id), message.sender.screen_name, message.text, message, None)
					if message.sender.screen_name == self.me.screen_name:
						dms.append(strings.message_list_format_sent % (short_code, message.recipient.screen_name, html_unescape(message.text).replace('\n', ' ')))
					else:
						dms.append(strings.message_list_format_received % (short_code, message.sender.screen_name, html_unescape(message.text).replace('\n', ' ')))
				try:
					choice = self.list_dialog(strings.messages_header % len(messages), dms)[1][1].split()[0]
				except:
					pass
				else:
					self.cmdline_content.set_edit_text(u"%s %s " % (config.commands.reply, choice))
					self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
					self.cmdline_content.set_edit_text(u"%s %s " % (config.commands.message, choice))
					self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
			except tweetpony.APIError as err:
				self.info_dialog(strings.api_error % (err.code, err.description))
				clear = False
		elif command == config.commands.message:
			if has_data:
				identifier = data_array[0]
				del data_array[0]
				text = ' '.join(data_array)
				if text != '':
					if len(identifier) == config.var.short_code_length:
						message_data = self.get_data(identifier)
						if message_data:
							sender = message_data[2]
						else:
							sender = identifier
					else:
						sender = identifier
					try:
						message = self.api.send_message(screen_name = sender, text = strings.message % text)
						self.add_direct_message(self.get_code(str(message.id), message.recipient.screen_name, message.text, message, None), strings.sent_message_prefix + message.recipient.screen_name, text, True)
					except tweetpony.APIError as err:
						self.info_dialog(strings.api_error % (err.code, err.description))
						clear = False
				else:
					self.info_dialog(strings.data_required % command)
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.block:
			if has_data:
				try:
					self.api.block(screen_name = data_array[0])
					self.notification(strings.blocked % data)
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.unblock:
			if has_data:
				try:
					self.api.unblock(screen_name = data_array[0])
					self.notification(strings.unblocked % data)
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.report_as_spam:
			if has_data:
				try:
					self.api.report_spam(screen_name = data_array[0])
					self.notification(strings.reported_as_spam % data)
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		elif command == config.commands.afk_mode_on:
			if not self.afk_mode:
				self.afk_mode = True
				self.add_notification(strings.afk_mode_enabled, False, False)
			else:
				self.notification(strings.afk_mode_already_enabled)
				clear = False
		elif command == config.commands.afk_mode_off:
			if self.afk_mode:
				self.afk_mode = False
				self.add_notification(strings.afk_mode_disabled, False, False)
			else:
				self.notification(strings.afk_mode_not_enabled)
				clear = False
		elif command == config.commands.lists and False:
			try:
				lists = self.api.lists()
				try:
					list_choice = self.list_dialog(strings.lists_header, [html_unescape(list.name) for list in lists])[1][0]
				except:
					pass
				else:
					selected_list = lists[list_choice]
					lines = []
					lines.append(strings.list_details_header % html_unescape(unicode(selected_list.name)) + u"\n")
					lines.append(strings.list_details_item_description % html_unescape(unicode(selected_list.description)) + u"\n")
					lines.append(strings.list_details_item_privacy % unicode(selected_list.mode).capitalize())
					lines.append(strings.list_details_item_members % unicode(selected_list.member_count))
					lines.append(strings.list_details_item_subscribers % unicode(selected_list.subscriber_count))
					action = self.dialog(u"\n".join(lines), [strings.button_members, strings.button_edit, strings.button_add_member, strings.button_delete_list])['button']
					if action == strings.button_members:
						members = self.api.list_members(owner = selected_list.user.screen_name, slug = selected_list.slug)
						try:
							user_choice = self.list_dialog(strings.list_members_header % html_unescape(unicode(selected_list.name)), [strings.list_members_item % (member.name, member.screen_name) for member in members])[1][0]
						except:
							pass
						else:
							selected_user = members[user_choice]
							if self.yes_no_dialog(strings.remove_user_from_list % (selected_user.screen_name, html_unescape(unicode(selected_list.name)))):
								try:
									selected_list = self.api.remove_from_list(slug = selected_list.id, id = selected_user.id)
									self.notification(strings.list_member_removed % (selected_user.screen_name, html_unescape(unicode(selected_list.name))))
								except tweetpony.APIError as err:
									self.info_dialog(strings.api_error % (err.code, err.description))
									clear = False
					elif action == strings.button_edit:
						entries = self.dialog(strings.edit_list_header % html_unescape(unicode(selected_list.name)), [strings.button_ok], [(strings.caption_name, html_unescape(unicode(selected_list.name))), (strings.caption_privacy, selected_list.mode), (strings.caption_description, html_unescape(unicode(selected_list.description)))], None, True)['texts']
						if entries:
							try:
								selected_list = self.api.update_list(slug = selected_list.id, name = entries[0], mode = entries[1], description = entries[2])
								self.notification(strings.list_updated % html_unescape(unicode(selected_list.name)))
							except tweetpony.APIError as err:
								self.info_dialog(strings.api_error % (err.code, err.description))
								clear = False
					elif action == strings.button_add_member:
						username = self.input_dialog(strings.add_list_member % html_unescape(unicode(selected_list.name)), strings.caption_username)
						try:
							user = self.api.get_user(screen_name = username)
							selected_list = self.api.add_to_list(slug = selected_list.id, id = user.id)
							self.notification(strings.list_member_added % (user.screen_name, html_unescape(unicode(selected_list.name))))
						except tweetpony.APIError as err:
							self.info_dialog(strings.api_error % (err.code, err.description))
							clear = False
					elif action == strings.button_delete_list:
						if self.yes_no_dialog(strings.delete_list % html_unescape(unicode(selected_list.name))):
							try:
								selected_list = self.api.delete_list(slug = selected_list.id)
								self.notification(strings.list_deleted % html_unescape(unicode(selected_list.name)))
							except tweetpony.APIError as err:
								self.info_dialog(strings.api_error % (err.code, err.description))
								clear = False
					#TODO: Could be improved / extended
			except tweetpony.APIError as err:
				self.info_dialog(strings.api_error % (err.code, err.description))
				clear = False
		elif command == config.commands.create_list and False:
			entries = self.dialog(strings.create_list_header, [strings.button_ok], [(strings.caption_name, u""), (strings.caption_privacy, u""), (strings.caption_description, u"")], None, True)['texts']
			if entries:
				try:
					created_list = self.api.create_list(name = entries[0], mode = entries[1], description = entries[2])
					self.notification(strings.list_created % html_unescape(unicode(created_list.name)))
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
		elif command == config.commands.refresh:
			last_tweet_id = self.get_last_data()
			if last_tweet_id:
				last_tweet_id = last_tweet_id[1]
			else:
				last_tweet_id = None
			self.backfill(since_id = last_tweet_id)
		elif command == config.commands.sync_following:
			if has_data:
				try:
					source_following = self.api.friends_ids(screen_name = data_array[0])
					target_following = self.api.friends_ids(user_id = self.me.id)
				except tweetpony.APIError as err:
					self.info_dialog(strings.api_error % (err.code, err.description))
					clear = False
				follow = [id for id in source_following if id not in target_following]
				unfollow = [id for id in target_following if id not in source_following]
				total_actions = len(follow) + len(unfollow)
				if self.yes_no_dialog(strings.sync_confirmation % (len(unfollow), len(follow), total_actions)):
					i = 0
					for id in unfollow:
						try:
							i += 1
							progress = (i / total_actions) * 100
							# self.cmdline_content.set_caption(('cmdline bold', strings.prompt_percentage % progress))
							self.api.unfollow(user_id = id)
						except tweetpony.APIError as err:
							self.info_dialog(strings.api_error % (err.code, err.description))
							clear = False
					for id in follow:
						try:
							i += 1
							progress = (i / total_actions) * 100
							# self.cmdline_content.set_caption(('cmdline bold', strings.prompt_percentage % progress))
							self.api.follow(user_id = id)
						except tweetpony.APIError as err:
							self.info_dialog(strings.api_error % (err.code, err.description))
							clear = False
					self.info_dialog(strings.sync_complete % total_actions)
			else:
				self.info_dialog(strings.data_required % command)
				clear = False
		else:
			self.info_dialog(strings.invalid_command % command)
			clear = False
		
		if not clear:
			self.cmdline_content.set_edit_text(self.last_command)
			self.cmdline_content.set_edit_pos(len(self.cmdline_content.get_edit_text()))
	
	def quit(self, hard_quit = False):
		if hard_quit:
			sys.exit()
		else:
			try:
				plugins.on_exit(self)
				self.code_db_cursor.close()
				self.code_db.close()
				self.db_cursor.close()
				self.db.close()
			except:
				pass
			raise ClientQuit
	
	def api_error(self, err, is_fatal = False):
		sys.stdout.write("\n" + red(strings.api_error % (err.code, err.description)) + "\n")
		sys.stdout.flush()
		if is_fatal:
			sys.exit(1)
# Comment to push that swaggy shit up one line.
