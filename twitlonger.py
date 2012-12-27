#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python wrapper for the TwitLonger API.
# © 2012 Mezgrman.

import urllib
import urllib2
import re
from xml.dom.minidom import parseString

class Object(object):
	pass

class TwitLongerAPIResponse(object):
	def __init__(self):
		self.error = None
		self.post = Object()
		setattr(self.post, 'id', None)
		setattr(self.post, 'link', None)
		setattr(self.post, 'user', None)
		setattr(self.post, 'short_url', None)
		setattr(self.post, 'content', None)

class TwitLongerError(Exception):
	def __init__(self, value = ""):
		self.err = value
	
	def __str__(self):
		return repr(self.err)

class API:
	def __init__(self, application, api_key):
		self.application = application
		self.api_key = api_key
	
	def parse_xml_response(self, data):
		response = TwitLongerAPIResponse()
		tag_content = re.compile(r"<.+>(?P<content>.*)</.+>")
		dom = parseString(data)
		try:
			root = dom.getElementsByTagName("twitlonger")[0]
		except IndexError:
			return False
		try:
			error = tag_content.match(root.getElementsByTagName("error")[0].toxml()).group('content')
		except IndexError:
			error = None
		response.error = error
		try:
			post = root.getElementsByTagName("post")[0]
		except IndexError:
			post = None
			response.post = post
		else:
			try:
				post_id = tag_content.match(post.getElementsByTagName("id")[0].toxml()).group('content')
			except IndexError:
				post_id = None
			try:
				post_link = tag_content.match(post.getElementsByTagName("link")[0].toxml()).group('content')
			except IndexError:
				post_link = None
			try:
				post_user = tag_content.match(post.getElementsByTagName("user")[0].toxml()).group('content')
			except IndexError:
				post_user = None
			try:
				post_short_url = tag_content.match(post.getElementsByTagName("short")[0].toxml()).group('content')
			except IndexError:
				post_short_url = None
			else:
				if(post_short_url == "isgdfail"):
					post_short_url = False
			try:
				post_content = tag_content.match(post.getElementsByTagName("content")[0].toxml()).group('content')
			except IndexError:
				post_content = None
			response.post.id = post_id
			response.post.link = post_link
			response.post.user = post_user
			response.post.short_url = post_short_url
			response.post.content = post_content
		return response
	
	def post_tweet(self, username, message, in_reply = None, in_reply_user = None):
		raw_request_data = {'application': self.application, 'api_key': self.api_key, 'username': username, 'message': message.encode('utf-8')}
		if(in_reply is not None and in_reply_user is not None):
			raw_request_data['in_reply'] = in_reply
			raw_request_data['in_reply_user'] = in_reply_user
		request_data = urllib.urlencode(raw_request_data)
		req = urllib2.Request("http://www.twitlonger.com/api_post", request_data)
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			resp = TwitLongerAPIResponse()
			resp.error = err
			return resp
		except:
			resp = TwitLongerAPIResponse()
			resp.error = "Generic Error."
			return resp
		response_data = response.read()
		parsed_response = self.parse_xml_response(response_data)
		return parsed_response
	
	def link_posts(self, message_id, twitter_id):
		raw_request_data = {'application': self.application, 'api_key': self.api_key, 'message_id': message_id, 'twitter_id': twitter_id}
		request_data = urllib.urlencode(raw_request_data)
		req = urllib2.Request("http://www.twitlonger.com/api_set_id", request_data)
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			resp = TwitLongerAPIResponse()
			resp.error = err
			return resp
		except:
			resp = TwitLongerAPIResponse()
			resp.error = "Generic Error."
			return resp
		response_data = response.read()
		parsed_response = self.parse_xml_response(response_data)
		return parsed_response
	
	def get_tweet(self, identifier):
		if("://" in identifier):
			identifier = self.get_message_id_from_url(identifier)
		if(not identifier):
			resp = TwitLongerAPIResponse()
			resp.error = "Invalid URL supplied."
			return resp
		req = urllib2.Request("http://www.twitlonger.com/api_read/%s" % identifier)
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			resp = TwitLongerAPIResponse()
			resp.error = err
			return resp
		except:
			resp = TwitLongerAPIResponse()
			resp.error = "Generic Error."
			return resp
		response_data = response.read()
		parsed_response = self.parse_xml_response(response_data)
		return parsed_response
	
	def get_message_id_from_url(self, url):
		try:
			url_parts = url.split("/")
			if(url_parts[2] == "tl.gd"):
				message_id = url_parts[3]
			elif((url_parts[2] == "twitlonger.com" or url_parts[2] == "www.twitlonger.com") and url_parts[3] == "show"):
				message_id = url_parts[4]
			else:
				return False
		except:
			return False
		return message_id
	
	def process_text(self, text):
		for word in text.split():
			if("://" in word):
				tweet = self.get_tweet(word)
				if(not tweet.error):
					text = tweet.post.content
		return text
