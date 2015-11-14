# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-11-12
# LAST_MODIFIED : 2015年11月14日 星期六 16时39分20秒
# USAGE : python test_core.py
# PURPOSE : TODO
##################################################
import sys, time, random
import toutiaoframe.core as T
import subprocess


if __name__ == "__main__":

  ##################################
  ## TEST FileIO write
  ##################################
  ## a = T.FileIO('newfile', 'w')
  ## a.start()
  ## for i in range(10):
  ##   time.sleep(random.uniform(0,2))
  ##   a.en_from_queue(str(i)+'\n')
  ## a.end()

  ##################################
  ## TEST FileIO read&write
  ##################################
  ## a = T.FileIO('mylogging.py', 'r')
  ## b = T.FileIO('newfile', 'w', from_queue=a.IOQueue)
  ## for p in [a, b]:
  ##   p.start()
  ## for p in [a, b]:
  ##   p.end()

  ##################################
  ## TEST RestfulIO basic
  ##################################
  ## a = T.RestfulIO().config(REST_METHOD='test')
  ## a.start()
  ## for i in xrange(10):
  ##   a.en_from_queue(str(i))
  ##   time.sleep(random.randint(0,3))
  ## a.end()

  ##################################
  ## TEST RestfulIO combined with FileIO
  ##################################
  ## # we write to a, b read from to_queue for a and write to a file
  ## a = T.RestfulIO().config(REST_METHOD='test')
  ## b = T.FileIO('newfile', 'a') 
  ## b.IOQueue = a.to_queue
  ## for p in [a, b]:
  ##   p.start()
  ## for i in xrange(10):
  ##   a.en_from_queue(str(i))
  ##   time.sleep(random.randint(0,3))
  ## for p in [a, b]:
  ##   p.end()
  
  ##################################
  ## TEST RestfulIO combined with FileIO, fault-aproof
  ##################################
  ## # we write to a, b read from to_queue for a and write to a file
  ## a = T.RestfulIO().config(REST_METHOD='test')
  ## b = T.FileIO('newfile', 'a') 
  ## b.IOQueue = a.to_queue
  ## for p in [a, b]:
  ##   p.start()
  ## for i in xrange(10):
  ##   if i == 4:
  ##     a.en_from_queue(None)
  ##   a.en_from_queue(str(i))
  ## for p in [a, b]: # BEAWARE that the order MATTERS
  ##   p.end()
    
  ##################################
  ## TEST RestfulIO combined with Restful queries
  ##################################
  pput = T.RestfulIO().config(REST_METHOD='insert', TABLE_NAME='article_duplicate')
  pshow = T.RestfulIO().config(REST_METHOD='show', TABLE_NAME='article_duplicate')
  pdel = T.RestfulIO().config(REST_METHOD='delete', TABLE_NAME='article_duplicate')
  pf = T.FileIO('newfile', 'a', encode=['object_id', 'article_id'], append_newline=True) 
  pf.IOQueue = pshow.to_queue
  for p in [pput, pshow, pdel, pf]:
    p.start()

  for i,j in zip(['1', '2'], ['1', '1'], ):
    pshow.en_from_queue(i)
  for i,j in zip(['1', '2'], ['1', '1'], ):
    data = {"object_id": i, "article_id": j}  
    pput.en_from_queue(data)

  time.sleep(2) # for insertion to finish
  for i,j in zip(['1', '2'], ['1', '1'], ):
    pshow.en_from_queue(i)
  for i,j in zip(['1', '2'], ['1', '1'], ):
    data = {"object_id": i}  
    pdel.en_from_queue(data)

  time.sleep(2) # for insertion to finish
  for i,j in zip(['1', '2'], ['1', '1'], ):
    pshow.en_from_queue(i)

  for p in [pput, pshow, pdel, pf]:
    p.end()

  ##################################
  ## TEST UpdateSubsciber
  ##################################
  ## pus = T.UpdateSubsciber(WATCH_CYCLE=20)
  ## pus.start()
  ## pus.register(pus.testfunc, ['newfile'])
  ## time.sleep(5)
  ## subprocess.check_call(["touch", "newfile"])
  ## time.sleep(30)
  ## pus.end()
