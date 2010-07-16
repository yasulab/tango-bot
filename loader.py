from google.appengine.tools import bulkloader
from models import Message


class DataLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Message', [
            ('wid', int),
            ('cnt', int),
            ('reading',  lambda x: unicode(x,'utf-8','ignore')),
            ('word',  lambda x: unicode(x,'utf-8','ignore')),
            ('dscr',  lambda x: unicode(x,'utf-8','ignore')),
            ('ctgr',  lambda x: unicode(x,'utf-8','ignore'))
            ])
        
loaders = [DataLoader]
