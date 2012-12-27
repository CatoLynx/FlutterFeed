#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python wrapper for the TwExtender API.
# © 2012 Mezgrman.

import urllib
import urllib2
import re
from xml.dom.minidom import parseString

class Object(object):
	pass

class TwExtenderAPIResponse(object):
	def __init__(self):
		self.error = None
		self.code = None
		self.author = None
		self.date = None
		self.text = None
		self.tweet = None
		self.in_reply_to_status = Object()
		setattr(self.in_reply_to_status, 'author', None)
		setattr(self.in_reply_to_status, 'id', None)

class TwExtenderError(Exception):
	def __init__(self, value = ""):
		self.err = value
	
	def __str__(self):
		return repr(self.err)

class API:
	def __init__(self, api_key):
		self.api_key = api_key
	
	def parse_xml_response(self, data):
		response = TwExtenderAPIResponse()
		tag_content = re.compile(r"<.+>(?P<content>.*)</.+>")
		dom = parseString(data)
		try:
			root = dom.getElementsByTagName("twextender")[0]
		except IndexError:
			return False
		try:
			error = tag_content.match(root.getElementsByTagName("error")[0].toxml()).group('content')
		except IndexError:
			error = None
		response.error = error
		try:
			code = tag_content.match(root.getElementsByTagName("code")[0].toxml()).group('content')
		except IndexError:
			code = None
		response.code = code
		try:
			author = root.getElementsByTagName("author")[0]
		except IndexError:
			author = None
		response.author = author
		try:
			date = tag_content.match(root.getElementsByTagName("date")[0].toxml()).group('content')
		except IndexError:
			date = None
		response.date = date
		try:
			text = tag_content.match(root.getElementsByTagName("text")[0].toxml()).group('content')
		except IndexError:
			text = None
		response.text = text
		try:
			tweet = tag_content.match(root.getElementsByTagName("tweet")[0].toxml()).group('content')
		except IndexError:
			tweet = None
		response.tweet = tweet
		try:
			in_reply_to_status = root.getElementsByTagName("in_reply_to_status")[0]
		except IndexError:
			in_reply_to_status = None
			response.in_reply_to_status = None
		else:
			try:
				in_reply_to_status_author = tag_content.match(in_reply_to_status.getElementsByTagName("author")[0].toxml()).group('content')
			except IndexError:
				in_reply_to_status_author = None
			try:
				in_reply_to_status_id = tag_content.match(in_reply_to_status.getElementsByTagName("id")[0].toxml()).group('content')
			except IndexError:
				in_reply_to_status_id = None
			response.in_reply_to_status.author = in_reply_to_status_author
			response.in_reply_to_status.id = in_reply_to_status_id
		return response
	
	def post_tweet(self, author_username, text, in_reply_to_username = None, in_reply_to_status_id = None):
		raw_request_data = {'api_key': self.api_key, 'author_username': author_username, 'text': text.encode('utf-8')}
		if(in_reply_to_username is not None and in_reply_to_status_id is not None):
			raw_request_data['in_reply_to_username'] = in_reply_to_username
			raw_request_data['in_reply_to_status_id'] = in_reply_to_status_id
		request_data = urllib.urlencode(raw_request_data)
		req = urllib2.Request("http://dev.mezgrman.de/tweet/create", request_data)
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			resp = TwExtenderAPIResponse()
			resp.error = err
			return resp
		except:
			resp = TwExtenderAPIResponse()
			resp.error = "Generic Error."
			return resp
		response_data = response.read()
		parsed_response = self.parse_xml_response(response_data)
		return parsed_response
