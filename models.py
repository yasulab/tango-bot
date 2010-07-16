from google.appengine.ext import db

class Message(db.Model):
	wid = db.IntegerProperty()
	cnt = db.IntegerProperty()
	reading = db.StringProperty()
	word = db.StringProperty()
	dscr = db.StringProperty()
	ctgr = db.StringProperty()
