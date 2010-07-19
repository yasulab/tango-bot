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

# For Import Models on GAE DB
from models import *
import datetime
from email.utils import parsedate

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
		MAX_DB = 91864
		qlist = []
		while i<10:
			i += 1
			rand = random.randint(0,MAX_DB)
			query = db.GqlQuery("SELECT * FROM Message WHERE wid = " + str(rand))
			qlist.append(query[0])
		for q in qlist:
			print q.wid,
			print q.cnt,
			print q.reading.encode('utf-8'),
			print q.word.encode('utf-8'),
			print q.dscr.encode('utf-8'),
			print q.ctgr.encode('utf-8')

class TwitterTweet(webapp.RequestHandler):		
	def get(self):
		# User Setting and Run Twitter Bot
		tweet = ""
		tmp_tweet = ""
			
		while len(tweet) < MAX_LEN:
			tmp_tweet = tweet
			rand = random.randint(0,MAX_DB)
			query = db.GqlQuery("SELECT * FROM Message WHERE wid = " + str(rand))
			tweet += SPACE + query[0].word.encode('utf-8')

		tweet = tmp_tweet
		print "Length of 'tweet': " + str(len(tweet))
		print "I am tweeting: " + tweet #.encode('utf-8')
		print "Status of Tweet Result: " + str(gae_twitter.update(tweet))

class TwitterReply(webapp.RequestHandler):
	def get(self):
		# User Setting and Run Twitter Bot
		tweet = ""
		tmp_tweet = ""
		request_uname = "NULL"
		request_word = "NULL"

		# Get Latest Reply
		replies = Reply.all()
		recent_reply = replies[0].text
		recent_uname = replies[0].uname
		recent_dt = replies[0].datetime
		print "recent_reply = " + recent_reply.encode('utf-8')
		print "recent_uname = " + recent_uname.encode('utf-8')
		print "recent_dt = " + recent_dt.strftime(DT_FORMAT)
		print 
   
		# Search Most Recent Tweet
		results = api.GetReplies()
		results.reverse()
		
		flag_enable = 0
		for i,result in enumerate(results):
			rt = result.text
			rt_len = len(rt)
			rt_dt = UTC2JST(rfc2datetime(result.created_at))
			print "[Debug] rt["+str(i)+"]: " + rt.encode('utf8') +" "+ rt_dt.strftime(DT_FORMAT)
				
			if flag_enable:
				print
				print "I am going to tweet the tweet above."
				if rt_len > MAX_LEN:
					print "But, this tweet length is longer that 140 characters, so skipped it."
					continue
				if rt.startswith("@tango_bot") == False:
					print "But, this tweet does not start with '@tango_bot'."
					continue
				if recent_dt > rt_dt:
					print "But, this tweet was tweeted before than recent_tweet."
					continue
				"""
				Retweet and brek
				"""
				request_word = rt.encode('utf8').lstrip(search_term+SPACE)
				request_uname = result.user.screen_name.encode('utf8')
				print "request_word = " + request_word
				print "request_uname = " + request_uname
				break
               
			if recent_reply == rt:
				print
				print "Found same reply as recent_reply in Timeline"
				if recent_dt > rt_dt:
					print "But, this reply would be already replied before."
					print
					continue
				print
				flag_enable = 1
				if i == len(results)-1:
					print
					print "There are no tweet found that I should tweet."
					print
					return

		if request_uname == "NULL":
			print "Oops, 'request_uname' is 'NULL'. Check when it stored."
			print "recent_reply = " + recent_reply.encode('utf-8')
			print "recent_uname = " + recent_uname.encode('utf-8')
			print "flag_enable = " + str(flag_enable)
			return
			
		tweet = "@" + request_uname
		while len(tweet) < MAX_LEN:
			tmp_tweet = tweet
			if debug_flag:
				rand = random.randint(0,100)
			else:
				rand = random.randint(0,MAX_DB)
			query = db.GqlQuery("SELECT * FROM Message WHERE wid = " + str(rand))
			tweet += SPACE + query[0].word.encode('utf-8') + request_word
		
		tweet = tmp_tweet
		print
		print "Length of 'tweet': " + str(len(tweet))
		print "I am tweeting: " + tweet
		
		if debug_flag:
			print "==================================="
			print "Avoided tweeting due to debug_flag."
			print "==================================="
			return
		
		print "Status of Tweet Result: " + str(gae_twitter.update(tweet))
		print
		
		print "Deleting all data from 'Tweet' model..."
		reply_model = Reply.all()
		for r in reply_model:
			print "deleted: ",
			print "'" + r.text.encode('utf-8') + "'",
			print "'" + r.uname.encode('utf-8') + "'",
			print "'" + r.datetime.strftime(DT_FORMAT) + "'"
			r.delete()

		print
		print "Stored following data into Reply model: "
		r = Reply(
			text = unicode('@tango_bot'+SPACE+request_word, "utf-8"),
			uname = unicode(request_uname, "utf-8"),
			datetime = rt_dt
			)
		r.put()		
		reply_model = Reply.all()
		for r in reply_model:
			print "'" + r.text.encode('utf-8') + "'",
			print "'" + r.uname.encode('utf-8') + "'",
			print "'" + r.datetime.strftime(DT_FORMAT) + "'"
		print

class RecentReply(webapp.RequestHandler):
	def get(self):
		tweet = "最近来たお題："
		prev_tweet = ""
		odai = ""
		status = api.GetReplies()
		status.reverse()
		recent_text = ''
		
		query = Odai.all()
		for q in query:
			recent_text = q.text.encode('utf8')
			recent_uname = q.uname.encode('utf8')
			recent_dt = q.datetime
		if not recent_text:
			print "Odai Data was not found."
			print
			return
		print "recent_text = '" + recent_text+"'"
		print "recent_uname = '" + recent_uname+"'"
		print "recent_dt = '" + recent_dt.strftime(DT_FORMAT)+"'"
		print

		is_found = False
		for i,s in enumerate(status):
			odai = s.text.encode('utf-8')
			dt = UTC2JST(rfc2datetime(s.created_at))
			uname = s.user.screen_name.encode('utf8')
			print "status["+str(i)+"]"
			print "odai = '"+odai+"'"
			print "uname = '"+uname+"'"
			print "datetime = '"+dt.strftime('%a, %d %b %Y %H:%M:%S')+"'"

			if not odai.startswith("@tango_bot"):
				print "odai does not start with '@tango_bot', so skipped it."
				print
				continue
			if dt <= recent_dt:
				print "odai was replied equal to OR before than recent reply, so skipped it."
				print
				continue
			
			stripped_odai = odai.lstrip("@tango_bot")
			if len(tweet)+len(stripped_odai) > MAX_LEN:
				print "Over MAX_LEN, so did break."
				print
				break
			tweet += stripped_odai
			
			prev_odai = odai
			prev_uname = uname
			prev_dt = dt
			is_found = True
			print

		if is_found == False:
			print 
			print "There are no Odai that I should tweet."
			print
			return
		
		odai = prev_odai
		uname = prev_uname
		dt = prev_dt
		tweet += " #tango_odai"
		print "I am going to tweet: " + tweet
		print "Length of the tweet = " + str(len(tweet))
		if debug_flag:
			print
			print "=================================="
			print "Avoid tweeting due to debug_flag"
			print "=================================="
			return
		print "Status of Tweet Result: " + str(gae_twitter.update(tweet))
		print
		
		print "Deleting all data from 'Tweet' model..."
		odai_model = Odai.all()
		for o in odai_model:
			print "deleted: ",
			print "'" + o.text.encode('utf-8') + "'",
			print "'" + o.uname.encode('utf-8') + "'",
			print "'" + o.datetime.strftime(DT_FORMAT) + "'"
			o.delete()
		print
		
		print "Stored following data into Odai model: "
		o = Odai(
			text = unicode(odai, "utf-8"),
			uname = unicode(uname, "utf-8"),
			datetime = dt
			)
		o.put()		
		odai_model = Odai.all()
		for o in odai_model:
			print "'" + o.text.encode('utf-8') + "'",
			print "'" + o.uname.encode('utf-8') + "'",
			print "'" + o.datetime.strftime(DT_FORMAT) + "'"
		print			
		
class Test1(webapp.RequestHandler):
	def get(self):
		status = api.GetReplies()
		status.reverse()
		text = status[0].text.encode('utf8')
		uname = status[0].user.screen_name.encode('utf8')
		dt = UTC2JST(rfc2datetime(status[0].created_at))

		"""
		r = Reply(
			text = unicode(text, "utf-8"),
			uname = unicode(uname, "utf-8"),
			datetime = dt
			)
		r.put()
		"""
		o = Odai(
			text = unicode(text, "utf-8"),
			uname = unicode(uname, "utf-8"),
			datetime = dt
			)
		o.put()
		print "Stored following data into Tweet model: "
		replies = Reply.all()
		for r in replies:
			print "'" + r.text.encode('utf-8') + "'",
			print "'" + r.uname.encode('utf-8') + "'",
			print r.datetime.strftime('%a, %d %b %Y %H:%M:%S')
			
class Test2(webapp.RequestHandler):
	def get(self):
		"""
		print "Deleting all data from 'Tweet' model..."
		replies = Reply.all()
		for r in replies:
			print "deleted: ",
			print "'" + r.text.encode('utf-8') + "'",
			print "'" + r.uname.encode('utf-8') + "'",
			print r.datetime.strftime('%a, %d %b %Y %H:%M:%S')
			r.delete()
		print
		"""
		print "Deleting all data from 'Odai' model..."
		odai = Odai.all()
		for o in odai:
			print "deleted: ",
			print "'" + o.text.encode('utf-8') + "'",
			print "'" + o.uname.encode('utf-8') + "'",
			print o.datetime.strftime('%a, %d %b %Y %H:%M:%S')
			o.delete()
		print

class Test3(webapp.RequestHandler):
	def get(self):
		print "Debugging..."
		print
		status = api.GetReplies()
		for s in status:
			dt = rfc2datetime(s.created_at)
			print UTC2JST(dt).strftime('%a, %d %b %Y %H:%M:%S'),
			print ": " + s.user.screen_name.encode("utf-8") + " " + s.text.encode('utf-8')
			print
			
		
		
def rfc2datetime(rfc):
	pd = parsedate(rfc)[0:6]
	return datetime.datetime(*pd)

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

def UTC2JST(dt):
	"""Convert UTC into JST"""
	dt = dt + datetime.timedelta(hours=9)
	return dt

def main():
	# overriding API __init__
	twitter.Api.__init__ = twitter_api_init_gae

	# Global Variables
	global BOT_USERNAME,BOT_PASSWORD,BR,MAX_LEN,MAX_DB,SPACE,DT_FORMAT
	BOT_USERNAME = 'tango_bot'
	BOT_PASSWORD = '???'
        BR = "<br>"
	MAX_LEN = 140
	MAX_DB = 91864
	SPACE = " "
	DT_FORMAT = '%a, %d %b %Y %H:%M:%S'

	# Global Setting
	global gae_twitter,api,debug_flag
	gae_twitter = AppEngineTwitter(BOT_USERNAME, BOT_PASSWORD)
	api = twitter.Api(username=BOT_USERNAME, password=BOT_PASSWORD)
	debug_flag = False
	#debug_flag = True
	
	application = webapp.WSGIApplication(
		[('/', CsvUploader),
		 ('/delete', DeleteMessage),
		 ('/show', ShowMessage),
		 ('/random', Random),
		 ('/cron/tweet', TwitterTweet),
		 ('/cron/reply', TwitterReply),
		 ('/cron/recent_reply', RecentReply),
		 ('/test1', Test1),
		 ('/test2', Test2),
		 ('/test3', Test3)]
		,debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
