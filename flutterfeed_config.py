#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file contains the part of the client configuration that should NOT be edited by the user.
# © 2012 Mezgrman.

import flutterfeed_tokens as tokens

class commands:
	cmd_prefix = u"/"
	tweet = cmd_prefix + u"tweet"
	retweet = cmd_prefix + u"rt"
	favorite = cmd_prefix + u"fav"
	unfavorite = cmd_prefix + u"unfav"
	follow = cmd_prefix + u"follow"
	unfollow = cmd_prefix + u"unfollow"
	last_tweets = cmd_prefix + u"last"
	profile = cmd_prefix + u"profile"
	reply = cmd_prefix + u"reply"
	mentions = cmd_prefix + u"me"
	conversation = cmd_prefix + u"conv"
	relationship = cmd_prefix + u"rel"
	delete = cmd_prefix + u"del"
	replyall = cmd_prefix + u"rall"
	dump = cmd_prefix + u"dump"
	trends = cmd_prefix + u"trends"
	logout = cmd_prefix + u"logout"
	clear = cmd_prefix + u"clear"
	filter_word = cmd_prefix + u"filterword"
	filter_user = cmd_prefix + u"filteruser"
	filter_client = cmd_prefix + u"filterclient"
	filter_regex = cmd_prefix + u"filterregex"
	unfilter_word = cmd_prefix + u"unfilterword"
	unfilter_user = cmd_prefix + u"unfilteruser"
	unfilter_client = cmd_prefix + u"unfilterclient"
	unfilter_regex = cmd_prefix + u"unfilterregex"
	list_word_filter = cmd_prefix + u"wordfilter"
	list_user_filter = cmd_prefix + u"userfilter"
	list_client_filter = cmd_prefix + u"clientfilter"
	list_regex_filter = cmd_prefix + u"regexfilter"
	messages = cmd_prefix + u"dms"
	message = cmd_prefix + u"dm"
	block = cmd_prefix + u"block"
	unblock = cmd_prefix + u"unblock"
	report_as_spam = cmd_prefix + u"report"
	help = cmd_prefix + u"help"
	afk_mode_on = cmd_prefix + u"afkon"
	afk_mode_off = cmd_prefix + u"afkoff"
	lists = cmd_prefix + u"lists"
	create_list = cmd_prefix + u"createlist"
	highlight_word = cmd_prefix + u"highlightword"
	highlight_user = cmd_prefix + u"highlightuser"
	highlight_client = cmd_prefix + u"highlightclient"
	highlight_regex = cmd_prefix + u"highlightregex"
	unhighlight_word = cmd_prefix + u"unhighlightword"
	unhighlight_user = cmd_prefix + u"unhighlightuser"
	unhighlight_client = cmd_prefix + u"unhighlightclient"
	unhighlight_regex = cmd_prefix + u"unhighlightregex"
	list_highlighted_words = cmd_prefix + u"highlightedwords"
	list_highlighted_users = cmd_prefix + u"highlightedusers"
	list_highlighted_clients = cmd_prefix + u"highlightedclients"
	list_highlighted_regexes = cmd_prefix + u"highlightedregexes"
	refresh = cmd_prefix + u"refresh"

class geometry:
	statusbar_height = 1
	statusbar_spacing = 1
	cmdline_height = 1
	cmdline_spacing = 1
	dialog_padding = 1
	button_h_spacing = 1
	button_v_spacing = 1
	text_input_min_width = 20

class oauth:
	consumer_key = tokens.consumer_key
	consumer_secret = tokens.consumer_secret

class system:
	version = "1.0"
	client_name = "FlutterFeed"
	client_description = "A CLI Twitter client for Linux written in Python."
	db_file = ".flutterfeed/flutterdatabase.db"
	stream_timeout = 60
	stream_reconnect_delay = 10
	statusbar_loading_delay = 1
	statusbar_update_interval_left = 300
	statusbar_update_interval_right = 1
	api_retry_count = 5
	api_retry_delay = 5
	api_retry_errors = [500, 502, 503, 504]
	exit_key = "ctrl x"
	submit_key = "enter"
	twitlonger_application_name = tokens.twitlonger_application_name
	twitlonger_api_key = tokens.twitlonger_api_key
	twextender_api_key = tokens.twextender_api_key
	stream_security = True
	notification_icon = "icon.png"
	default_account_name = "default"

class var:
	verifier_prompt_delay = 5
	beep = False
	popups = True
	short_code_length = 2
	short_code_characters = u"abcdefghijklmnopqrstuvwxyz0123456789"
	min_tweets_to_keep = ((len(short_code_characters) ** short_code_length) / 2)
	block_separator_character = u"="
	block_separator_width = 146
	statusbar_spacing_character = u" "
	conversation_default_tweet_count = 50
	linebreak_max_searchback = 75
	notify_freq = 750
	notify_dur = 25
	statusbar_time_format = "%d.%m.%Y %H:%M:%S"
	tweet_command_required = False
	last_tweet_count = 10
	mentions_count = 25
	messages_count = 10
	tweet_preview_length = 50
	default_notification_timeout = 1.0
	palette = [
		('statusbar', 'light gray', 'default'),
		('statusbar bold', 'light gray, bold', 'default', 'bold'),
		('feed', 'light gray', 'default'),
		('feed bold', 'light gray, bold', 'default', 'bold'),
		('cmdline', 'light gray', 'default'),
		('cmdline bold', 'light gray, bold', 'default', 'bold'),
		('dialog', 'white', 'dark cyan'),
		('dialog bold', 'white, bold', 'dark cyan', 'bold'),
		('button', 'white', 'dark blue'),
		('button bold', 'white, bold', 'dark blue', 'bold'),
		('button focus', 'white', 'dark red'),
		('button focus bold', 'white, bold', 'dark red', 'bold'),
		('edit', 'white', 'dark red'),
		('edit bold', 'white, bold', 'dark red', 'bold'),
		('list', 'white', 'dark blue'),
		('list bold', 'white, bold', 'dark blue', 'bold'),
		('list selected', 'white', 'dark red'),
		('list selected bold', 'white, bold', 'dark red', 'bold'),
		('short code', 'light blue', 'default'),
		('author', 'light gray, bold', 'default', 'bold'),
		('tweet', 'light gray', 'default'),
		('mention', 'light cyan, bold', 'default', 'bold'),
		('notification', 'light green', 'default'),
		('favorite', 'yellow', 'default'),
		('favorite mention', 'yellow, bold', 'default', 'bold'),
		('highlighted', 'light green', 'default'),
		('warning', 'yellow', 'default'),
		('error', 'light red', 'default'),
	]
