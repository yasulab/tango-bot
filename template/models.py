# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db

class Import(db.Model):
    # �f�[�^�쐬����
    created_date = db.DateTimeProperty(auto_now = True, auto_now_add = True)
    # ���O
    name    = db.StringProperty()
    # �N��
    age     = db.IntegerProperty()
    # �a����
    birthday = db.DateProperty()