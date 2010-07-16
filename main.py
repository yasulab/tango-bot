#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import wsgiref.handlers
import os
import csv
import string
import random
from StringIO import StringIO
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from models import Message

# For Twitter Import
from appengine_twitter import AppEngineTwitter
from basehandler import BaseHandler, h
import twitter

class CsvUploader(webapp.RequestHandler):
	def get(self):
		template_values = {
			'messages': Message.all(),
		}
		path = os.path.join(os.path.dirname(__file__), "upload.html")
		self.response.out.write(template.render(path, template_values))
	def post(self):
		rawfile = self.request.get('file')
		csvfile = csv.reader(StringIO(rawfile))
		for row in csvfile:
			m = Message(
				wid = int(row[0]),
				cnt = int(row[1]),
				reading = unicode(row[2], "utf-8"),
				word = unicode(row[3], "utf-8"),
				dscr = unicode(row[4], "utf-8"),
				ctgr = unicode(row[5], "utf-8")
				)
			m.put()
		self.redirect(self.request.uri)

class DeleteMessage(webapp.RequestHandler):	
	def get(self):
		query = Message.all()
		for q in query:
			print "deleted: ",
			print q.wid,
			print q.cnt,
			print q.reading.encode('utf-8'),
			print q.word.encode('utf-8'),
			print q.dscr.encode('utf-8'),
			print q.ctgr.encode('utf-8')
			q.delete()

class ShowMessage(webapp.RequestHandler):
	def get(self):
		template_values = {
			'messages': Message.all(),
		}
		path = os.path.join(os.path.dirname(__file__), "show.html")
		self.response.out.write(template.render(path, template_values))
		
class Random(webapp.RequestHandler):
	def get(self):
		i = 0
		qlist = []
		while i<10:
			i += 1
			rand = random.randint(0,10000)
			query = db.GqlQuery("SELECT * FROM Message WHERE wid = " + str(rand))
			qlist.append(query[0])
		for q in qlist:
			# 値はダブルクォートで囲み、値内のダブルクォートは二重化する
			print q.wid,
			print q.cnt,
			print q.reading.encode('utf-8'),
			print q.word.encode('utf-8'),
			print q.dscr.encode('utf-8'),
			print q.ctgr.encode('utf-8')

class TwitterBot(webapp.RequestHandler):		
	def get(self):
		print "Hoge!"
		# User Setting and Run Twitter Bot
		debug_flag = True
		#debug_flag = False
		bot_username = 'tango_bot'
		bot_password = '???'
		br = "<br>"
		MAX_LEN = 140
		MAX_DB = 91864
		SPACE = " "
		tweet = ""
		tmp_tweet = ""
			
		while len(tweet) < MAX_LEN:
			tmp_tweet = tweet
			rand = random.randint(0,MAX_DB)
			query = db.GqlQuery("SELECT * FROM Message WHERE wid = " + str(rand))
			tweet += SPACE + query[0].word.encode('utf-8')

		tweet = tmp_tweet
		print "Length of 'tweet': " + str(len(tweet))
		gae_twitter = AppEngineTwitter(bot_username, bot_password)
		api = twitter.Api(username=bot_username, password=bot_password)
		print "I am tweeting: " + tweet #.encode('utf-8')
		print "Status of Tweet Result: " + str(gae_twitter.update(tweet))

def twitter_api_init_gae(self,
			 username=None,
			 password=None,
			 input_encoding=None,
			 request_headers=None):
	import urllib2
	from twitter import Api
	self._cache = None
	
	self._urllib = urllib2
	self._cache_timeout = Api.DEFAULT_CACHE_TIMEOUT
	self._InitializeRequestHeaders(request_headers)
	self._InitializeUserAgent()
	self._InitializeDefaultParameters()
	self._input_encoding = input_encoding
	self.SetCredentials(username, password)


def main():
	# overriding API __init__
	twitter.Api.__init__ = twitter_api_init_gae

	application = webapp.WSGIApplication(
		[('/', CsvUploader),
		 ('/delete', DeleteMessage),
		 ('/show', ShowMessage),
		 ('/random', Random),
		 ('/cron/tweet', TwitterBot)]
		,debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
