# encoding: utf-8

import sys
import codecs

argvs = sys.argv
argc = len(argvs)

if (argc != 2):
    print 'Usage: # python %s filename' % argvs[0]
    quit()
        
f = codecs.getreader('utf-8')(open(argvs[1]))
line = f.readline()
i = 0
while line:
    try:
        i += 1
        #print unicode(line, 'utf-8', 'ignore')
        print line,
        #    print line.encode('Shift_JIS'),
        #    print line.encode(''),
        #        print line,
        #        print line.encode('Shift_JIS'),
        line = f.readline()
    except UnicodeDecodeError:
        print "error line: " + line

f.close()

