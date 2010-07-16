#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import wsgiref.handlers
import string
from google.appengine.ext import webapp, db

class Message(db.Model):
	wid = db.IntegerProperty()
	cnt = db.IntegerProperty()
	reading = db.StringProperty()
	word = db.StringProperty()
	dscr = db.StringProperty()
	ctgr = db.StringProperty()


class CsvHandler(webapp.RequestHandler):
	def get(self, datenumber):
		self.response.headers['Content-Type'] = "application/x-csv; charset=Shift_JIS"
		# ヘッダ行を入れる、改行コードは<CR><LF>とする
		title = u'"ID","文字数","読み方","単語","説明","品詞"'
		self.response.out.write(title.encode('utf-8') + "\r\n")
		query = Message.all()
		#query = db.GqlQuery("SELECT * FROM Message")
		print "bar"
		for q in query:
			print "hoge!"
			# 値はダブルクォートで囲み、値内のダブルクォートは二重化する
			wid = int(q.uid)
			cnt = int(q.cnt)
			reading = string.replace(q.reading, '"', '""').encode('utf-8')
			word = string.replace(q.word, '"', '""').encode('utf-8')
			dscr = string.replace(q.dscr, '"', '""').encode('utf-8')
			ctgr = string.replace(q.ctgr, '"', '""').encode('utf-8')
			#pd = q.postingdate
			self.response.out.write('"%d","%d","%s","%s","%s","%s"\r\n' % (wid,cnt,reading,word,dscr,ctgr)

def main():
	application = webapp.WSGIApplication([
		('/download/(.*).csv', CsvHandler),
		],debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
