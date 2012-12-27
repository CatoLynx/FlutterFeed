#!/usr/bin/python
# -*- coding: utf-8 -*-
# Attempt at a simple plugin system for Mezgrman's CLI Twitter client.
# © 2012 Mezgrman.

import flutterfeed_strings as strings

def on_command(instance, command, data_array):
	#command = command.lower()
	return (command, data_array)

def on_tweet(instance, tweet_id, author, text, is_mention):
	return (tweet_id, author, text, is_mention)

def on_retweet(instance, tweet_id, retweeted_by, original_author, text, is_mention):
	return (tweet_id, retweeted_by, original_author, text, is_mention)

def on_message(instance, message_id, sender, text):
	return (message_id, sender, text)

def on_delete(instance, status_id, user_id):
	return (status_id, user_id)

def on_direct_message_delete(instance, message_id, user_id):
	return (message_id, user_id)

def on_statusbar_update_left(instance, me):
	return me

def on_notification(instance, frequency, duration, status, message, event):
	return frequency, duration, status, message, event

def on_init():
	print strings.startup_text
	return

def on_ready(instance):
	return

def on_exit(instance):
	print strings.quit_text
	return
