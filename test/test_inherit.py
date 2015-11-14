# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-11-13
# LAST_MODIFIED : 2015年11月13日 星期五 16时44分48秒
# USAGE : python test_inherit.py
# PURPOSE : TODO
##################################################
import toutiaoframe.core as T
import toutiaoframe.mylogging as mylogging
import time, random, os, sys

logging = mylogging.getLogger("Parent")

class Parent(T.Core):

  def __init__(self):
    super(self.__class__, self).__init__(self)


  @classmethod
  def main(cls, ):
    for i in xrange(10):
      logging.info('GOT %s', i)
    a = T.FileIO('newfile', 'w')
    a.start()
    for i in range(10):
        time.sleep(random.uniform(0,2))
        a.en_from_queue(str(i)+'\n')
    a.end()
    


if __name__ == "__main__":
  Parent.main()
