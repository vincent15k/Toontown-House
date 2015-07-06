#!/usr/bin/env python
import os
import zipfile
import time
import glob

def zipdir(pattern, root, delete=0):
    for file in glob.glob(pattern):
        print 'Adding', file
        zipf.write(file)
        if delete:
            os.unlink(file)

zipf = zipfile.ZipFile('backup_%s.zip' % time.time(), 'w', zipfile.ZIP_DEFLATED)
zipdir('ab/databases/astrondb/*.*', zipf)
zipdir('ab/logs/*.log', zipf, 1)
zipdir('ab/*.nohup', zipf, 1)
zipdir('tth/databases/air_cache/*.*', zipf)
zipdir('tth/databases/air_logs/*.log', zipf, 1)
zipdir('tth/databases/*.db', zipf)
zipf.close()
