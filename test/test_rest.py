# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-11-14
# LAST_MODIFIED : 2015年11月14日 星期六 22时40分08秒
# USAGE : python test_rest.py
# PURPOSE : TODO
##################################################
import toutiaoframe.core as T
import os, arrow, sys
import re
import glob
from toutiaoframe.core import mylogging
  
logging = mylogging.getLogger('test_rest')
T_WORD = re.compile(ur'(我省|我市|我区|我县|全省|全市|全区|全县)', re.UNICODE)

def listdir(path):
  """ List all files in self._inpath with integer names
  """
  files = sorted((f for f in glob.glob(os.path.join(path, '*out')) if os.path.isfile(f)))
  for fname in files:
    try:
      int(os.path.basename(fname).split('_',1)[0])
    except:
      files.remove(fname)
  return files
  

if __name__ == "__main__":
  import traceback
  
  pshow = T.RestfulIO().config(REST_METHOD='show', TABLE_NAME='article_new_att2')
  pfout = T.FileIO('result', 'w', encode='utf-8')

  for p in [pfout]:
    p.start()

  
  fout = open('result', 'w')
  for i in xrange(1):
    try:
      d = arrow.now()
      dt = d.replace(days=-i).strftime('%Y%m%d')
      fils = listdir('../data/output/'+dt+'/')
      cnt = 0
      for f in fils:
        for line in open(f):
          line = line.decode('utf-8').rstrip('\r\n')
          fields = line.split('\t')
          aid = fields[0]
          title = fields[1]
          author = fields[6]
          if not T_WORD.search(title):
            continue
          cnt += 1
          pfout.en_from_queue('\t'.join([aid, title, author]))
      logging.info("%s DONE, %d of lines", dt, cnt)
    except:
      logging.exception()
      for p in [pfout]:
        p.end(TIMEOUT=5)


  for p in [pfout]:
    p.end()

    
