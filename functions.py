#!/usr/bin/python
# -*- coding: utf-8 -*-
# Additional functions for Mezgrman's CLI Twitter client.
# © 2012 Mezgrman.

import config
import userconfig
import os
import curses
import random
from httplib2 import Http
from urlparse import urlparse

def bold(text):
	return "\033[1m" + text + "\033[0;0m"

def orange(text):
	return "\033[93m" + text + "\033[0;0m"

def red(text):
	return "\033[91m" + text + "\033[0;0m"

def stripos(haystack, needle, offset = 0):
	pos = haystack.upper().find(needle.upper(), offset)
	return pos

def html_escape(text):
	return text.replace(u"&", u"&amp;").replace(u'"', u"&quot;").replace(u"<", u"&lt;").replace(u">", u"&gt;")

def html_unescape(text):
	return text.replace(u"&amp;", u"&").replace(u"&quot;", u'"').replace(u"&lt;", u"<").replace(u"&gt;", u">")

def gen_short_code(value):
	return random.choice(config.var.short_code_characters) + random.choice(config.var.short_code_characters)

def expand_url(url, full = False):
	conn = Http()
	conn.force_exception_to_status_code = True
	if(full):
		n = 100
	else:
		n = 0
	
	response = conn.request(url, redirections = n)
	try:
		return response[0]['location']
	except KeyError:
		try:
			return response['location']
		except:
			return url

def expand_urls(text):
	ignored_characters = [u".", u",", u";", u":", u"!", u"?", u"–", u"—", u"…"]
	pieces = []
	words = text.split()
	for word in words:
		if(stripos(word, "http://") == 0 or stripos(word, "https://") == 0):
			if(word[-1:] in ignored_characters):
				temp_word = str(word[:-1])
				temp_rest = str(word[-1:])
				temp_word = expand_url(temp_word) + temp_rest
				pieces.append(temp_word)
			else:
				word = expand_url(word)
				pieces.append(word)
		else:
			pieces.append(word)
	
	return ' '.join(pieces)

def get_links(text):
	ignored_characters = [".", ",", ";", ":", "!", "?", "–", "—", "…"]
	links = []
	words = text.split()
	for word in words:
		if(stripos(word, "http://") == 0 or stripos(word, "https://") == 0):
			if(word[-1:] in ignored_characters):
				word = str(word[:-1])
			
			links.append(word)
	
	return links

def get_domain(link, subdomains = True):
	try:
		domain = urlparse(link)
		if(subdomains):
			return domain[1]
		else:
			domain_parts = domain[1].split('.')
			main_domain = domain_parts[len(domain_parts) - 2] + '.' + domain_parts[len(domain_parts) - 1]
			return main_domain
	except:
		return False
