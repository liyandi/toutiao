# -*- coding: utf-8 -*-
#!/usr/bin/python                        
##################################################
# AUTHOR : Yandi LI
# CREATED_AT : 2015-11-12
# LAST_MODIFIED : 2015年11月15日 星期日 02时03分42秒
# USAGE : python test_api.py
# PURPOSE : TODO
##################################################
import toutiaoframe.core as T

if __name__ == '__main__':

    ###############################
    ## object_info
    ###############################
    pshow = T.RestfulIO().config(REST_METHOD='show', TABLE_NAME='object_info', URL='http://i2.api.weibo.com/2/darwin/table/show.json', APPKEY='1629986123', APPSOURCE='1629986123')
    pshow.getDB({'object_id':'1042015:conceptTag_3e8d041c3fa7d7c1d9e855f5e8595b5f'})

    ###############################
    ## article_new_att2
    ###############################
    pshow = T.RestfulIO().config(REST_METHOD='show', TABLE_NAME='article_new_att2', URL='http://i2.api.weibo.com/2/darwin/table/show.json', APPKEY='1428722706', APPSOURCE='2936099636')
    pshow.getDB('2018279001:25b695c42ce8ca19754544d253148676')

    ###############################
    ## object & entity
    ###############################
    pshow = T.RestfulIO().config(REST_METHOD='show', URL='http://i2.api.weibo.com/2/entity/show.json', TARGET_FIELD='entity', APPSOURCE='2936099636')
    pshow = T.RestfulIO().config(REST_METHOD='show', URL='http://i2.api.weibo.com/2/object/show.json', TARGET_FIELD='object', APPSOURCE='2936099636')
    pshow.getDB({'object_id':'2018279001:25b695c42ce8ca19754544d253148676'})
    

    ###############################
    ## content_tag
    ###############################
    pshow = T.RestfulIO().config(REST_METHOD='show', URL='http://i2.api.weibo.com/2/darwin/platform/object/content_tag.json', TARGET_FIELD='results', APPKEY='1629986123', APPSOURCE='445670032')
    pshow.getDB({'content_id':'2018279001:25b695c42ce8ca19754544d253148676', 'content_type': '2'}) # weibo:1, webpage:2, article:3
