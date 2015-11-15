# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-11-14
# LAST_MODIFIED : 2015年11月16日 星期一 01时31分28秒
# USAGE : python test_frest.py
# PURPOSE : TODO
##################################################
import toutiaoframe.core as T
import os, arrow, sys
import re
import glob
from toutiaoframe.core import mylogging
  
logging = mylogging.getLogger('test_rest')

def parse_content_tag(res):
  """
  >>> parse_content_tag([{u'display_name': u' \u53cc11',
  ...  u'object_id': u'1042015:internetECommerce_edd2a1564c59dace4cd20bc9aeda73ad',
  ... u'object_type': u'internetECommerce',
  ... u'weight': 1},
  ... {u'category_id': u'1042015:city_2',
  ... u'category_name': u'\u4e2d\u56fd',
  ... u'display_name': u'\u897f\u5b89',
  ... u'object_id': u'1042015:city_20610001',
  ... u'object_type': u'city',
  ... u'weight': 0.75},])

  """
  dis = res[0]
  key = res[1][0].get('content_id', '')

  tag_weights = [(di.get('display_name', ''), di.get('weight', '')) for di in dis]
  tags = []
  for tag, weight in tag_weights:
    if tag and weight:
      tags.append(tag+':'+unicode(weight))
  return key+'\t'+'|'.join(tags)  


if __name__ == "__main__":
  
  ## pfin = T.FileIO('aid', 'r')
  ## pshow = T.RestfulIO(from_queue=pfin.IOQueue).config(REST_METHOD='show', URL='http://i2.api.weibo.com/2/darwin/table/show.json', TABLE_NAME='article_new_att2')
  ## pfout = T.FileIO('local_news_level', 'w', encode=['article_id', 'level'], IOQueue=pshow.to_queue)
  
  pfin = T.FileIO('aid', 'r')
  pfin.formatter = lambda x: {'content_id':x.rstrip('\r\n'), 'content_type': '2'}
  pshow = T.RestfulIO(from_queue=pfin.IOQueue).config(REST_METHOD='show', URL='http://i2.api.weibo.com/2/darwin/platform/object/content_tag.json',
      TARGET_FIELD='results', APPKEY='1629986123', APPSOURCE='445670032', RETURN_KEY=True)
  pfout = T.FileIO('local_news_tag', 'w', IOQueue=pshow.to_queue)
  pfout.formatter = lambda x: parse_content_tag(x).encode('utf-8')+'\n'

  for p in [pfin, pshow, pfout]:
    p.start()

  for p in [pfin, pshow, pfout]:
    p.end()

    
