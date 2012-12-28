#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python wrapper for the TwExtender API.
# © 2012 Mezgrman.

import urllib
import urllib2
import json

class Object(object):
	pass

class TwExtenderError(Exception):
	def __init__(self, value = ""):
		self.err = value
	
	def __str__(self):
		return repr(self.err)

class API:
	def __init__(self, api_key):
		self.api_key = api_key
	
	def post_tweet(self, author_username, text, in_reply_to_username = None, in_reply_to_status_id = None, code = False):
		raw_request_data = {'api_key': self.api_key, 'author_username': author_username, 'text': text.encode('utf-8'), 'code': "code" if code else ""}
		if in_reply_to_username is not None and in_reply_to_status_id is not None:
			raw_request_data['in_reply_to_username'] = in_reply_to_username
			raw_request_data['in_reply_to_status_id'] = in_reply_to_status_id
		request_data = urllib.urlencode(raw_request_data)
		req = urllib2.Request("http://api.mezgrman.de/tweets/create.json", request_data)
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			resp = {'error': err}
			return resp
		except:
			resp = {'error': "Generic error."}
			return resp
		response_data = response.read()
		return json.loads(response_data)
