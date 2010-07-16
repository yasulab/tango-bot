# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db

class Import(db.Model):
    # データ作成日時
    created_date = db.DateTimeProperty(auto_now = True, auto_now_add = True)
    # 名前
    name    = db.StringProperty()
    # 年齢
    age     = db.IntegerProperty()
    # 誕生日
    birthday = db.DateProperty()