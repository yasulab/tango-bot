# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import Context, loader

from XXXXX.models import Import
import csv
import datetime

# アップロードしたCSVファイル内容をデータストアへ保存
def importcsv(request):
    upload_filename = 'csvfile'

    if request.method != 'POST' or not request.FILES.has_key(upload_filename) :
        c = Context()
        t = loader.get_template('importcsvform.html')
        return HttpResponse(t.render(c))

    csvrawfile = request.FILES[upload_filename]
    csvcontents = csv.reader(csvrawfile)
    for cont in csvcontents :
        if len(cont) > 0 :
            data = Import(
                name = unicode(cont[0], 'cp932'),
                age = int(cont[1]),
                birthday = getBirthday(cont[2])
            )
            data.put()

    alllist = Import.all()
    c = Context({'alllist': alllist})
    t = loader.get_template('importcsvresult.html')
    return HttpResponse(t.render(c))

def getBirthday(text):
    tlist = text.split('/')
    result = datetime.date(int(tlist[0]), int(tlist[1]), int(tlist[2]) )
    return result