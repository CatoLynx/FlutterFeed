#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file contains the part of the client configuration that should NOT be edited by the user.
# © 2012 Mezgrman.

import tokens

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

class system:
	version = "0.14 beta"
	client_name = "FlutterFeed"
	client_description = "A Twitter client for the Linux command line."
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

class oauth: # You CAN use your own application to access Twitter by replacing these tokens. But I'm even happier if you leave these as they are :)
	consumer_key = tokens.consumer_key
	consumer_secret = tokens.consumer_secret

class geometry:
	statusbar_height = 1
	statusbar_spacing = 1
	cmdline_height = 1
	cmdline_spacing = 1
	dialog_padding = 1
	button_h_spacing = 1
	button_v_spacing = 1
	text_input_min_width = 20

class strings:	
	tweet_prefix = u"%s: "
	direct_message_prefix = u"[DM] %s: "
	tweet_code_prefix = u"%s "
	direct_message_code_prefix = u"%s "
	reply = u"@%s %s"
	retweet_prefix = u"%s ↻ %s: "
	retweet_scheme = u"%s RT @%s: %s"
	rel_both = u"%s ↔ %s"
	rel_i_follow = u"%s → %s"
	rel_following_me = u"%s ← %s"
	rel_none = u"%s – %s"
	replyall = u"%s %s"
	block_title_scheme = u" %s "
	message = u"%s"
	tweet_list_format = u"%s %s"
	mention_list_format = u"%s %s: %s"
	conversation_list_format = u"%s %s: %s"
	message_list_format_received = u"%s %s: %s"
	message_list_format_sent = u"%s To %s: %s"
	sent_message_prefix = "To "
	startup_text = u"%(client_name)s v%(version)s (c) 2012 @Mezgrman.\nTry /help for a list of available commands.\nInvoke with --help or -h to see possible command line arguments.\nHave fun and tweet me if you like it! :)" % {'client_name': system.client_name, 'version': system.version}
	quit_text = u"Thanks for using %(client_name)s! Goodbye!" % {'client_name': system.client_name}
	help_header = u"Command help (press Esc to hide)\nCommand syntax: /command parameter1 parameter2 | alternative to parameter2 [optional parameter3]"
	help_entries = [
		("Ctrl + X", "Quit the client."),
		("/rt code [text]", "Retweet the tweet with the given short code. If text is given, do a commented RT in the form \"comment RT @user: original tweet\"."),
		("/fav code", "Favorite the tweet with the given short code."),
		("/unfav code", "Favorite the tweet with the given short code."),
		("/follow username", "Follow the given user."),
		("/unfollow username", "Unfollow the given user."),
		("/last [username]", "Show the last tweets by the given user. If no user is given, show your own last tweets."),
		("/profile [username]", "Show the profile information of the given user. If no user is given, show your own profile."),
		("/reply code text", "Reply to the author of the tweet or direct message with the given short code.\nThis command does NOT send direct messages!"),
		("/me", "Show your last mentions."),
		("/conv code [count]", "Show the previous [count] messages of the conversation the tweet with the given short code is part of."),
		("/rel user1 [user2]", "Show the relationship between you and user1 or user1 and user2 if user2 is given."),
		("/del code", "Delete the tweet with the given short code."),
		("/rall code text", "Reply to all people mentioned in the tweet with the given short code."),
		("/trends", "Show the current worldwide trends."),
		("/logout", "Log out of the client."),
		("/clear", "Clear the feed window."),
		("/filterword word", "Add the given word to the word filter."),
		("/filteruser username", "Add the given user to the user filter."),
		("/filterclient clientname", "Add the given client to the client filter."),
		("/filterregex regex", "Add the given regular expression to the regex filter."),
		("/unfilterword word", "Remove the given word from the word filter."),
		("/unfilteruser username", "Remove the given user from the user filter."),
		("/unfilterclient clientname", "Remove the given client from the client filter."),
		("/unfilterregex regex", "Remove the given regular expression from the client filter."),
		("/wordfilter", "Show all words that are currently in the word filter."),
		("/userfilter", "Show all users that are currently in the user filter."),
		("/clientfilter", "Show all clients that are currently in the client filter."),
		("/regexfilter", "Show all regular expressions that are currently in the regex filter."),
		("/highlightword word", "Highlight tweets containing the given word."),
		("/highlightuser username", "Highlight tweets from the given user."),
		("/highlightclient clientname", "Highlight tweets coming from the given client."),
		("/highlightregex regex", "Highlight tweets matching the given regular expression."),
		("/unhighlightword word", "Stop highlighting tweets containing the given word."),
		("/unhighlightuser username", "Stop highlighting tweets from the given user."),
		("/unhighlightclient clientname", "Stop highlighting tweets coming from the given client."),
		("/unhighlightregex regex", "Stop highlighting tweets matching the given regular expression."),
		("/highlightedwords", "Show all words that are currently highlighted."),
		("/highlightedusers", "Show all users that are currently highlighted."),
		("/highlightedclients", "Show all clients that are currently highlighted."),
		("/highlightedregexes", "Show all regular expressions that are currently highlighted."),
		("/dms", "Show your last direct messages."),
		("/dm username | code text", "Send a direct message to the given user or the author of the direct message or tweet with the given short code."),
		("/block username", "Block the given user."),
		("/unblock username", "Unblock the given user."),
		("/report username", "Block and report the given user as spam."),
		("/afkon", "Turn on AFK mode. In AFK mode, only mentions, direct messages, favorite, unvaforite and follower notifications are shown."),
		("/afkoff", "Turn off AFK mode. All new tweets and events are shown."),
		("/refresh", "Manually refresh the timeline."),
		#("/lists", "Show your lists."),
		#("/createlist", "Show a dialog to create a new list."),
		("/help", "Show this help."),
	]
