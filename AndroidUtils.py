'''
Created on Jun 11, 2014

@author: abhinav2
'''
import urllib
import re
from lxml.html import parse, tostring, clean
from lxml.etree import strip_tags
import pprint
import StringIO
#from Levenshtein import ratio
import yajl as json
import socket
import time
import urllib2
import logging
import zlib
from StringIO import StringIO
http_logger = urllib2.HTTPHandler(debuglevel = 1)
url_loader=urllib2.build_opener(http_logger,urllib2.HTTPCookieProcessor(),urllib2.ProxyHandler(),http_logger)
urllib2.install_opener(url_loader)

def get_data(url,post=None,headers={}):
    headers['Accept-encoding'] ='gzip'
    ret= None
    try:
        req=urllib2.Request(url,post,headers)
        ret = url_loader.open(req) 
        if ret.info().get('Content-Encoding') == 'gzip':
            ret = StringIO(zlib.decompress(ret.read(),16+zlib.MAX_WBITS))
    except urllib2.HTTPError, e: 
        ret = None
    return ret



   
# GCM_API_KEY = "AIzaSyCEhpQRBHfeAsdYS85VlcrsB7XQADbEWNw"
#     
#     
# headers={'Content-Type':'application/json',
#           'Authorization':'key='+GCM_API_KEY
#          }
# 
# from Config import *
# 
# json_data = {
#   "registration_ids" : ['APA91bHap44N7mK8VJhZdFLA2qxm3rEvJb4B2l1-odZ1Gz8tkYUFkLfrml5ht6dYcn0Ht4hXTvXx0JqS37wc-QTxf6fZunLDWUUnM3ab2974jvRaTxoF1mYgZE_biABCWAZPyR6PHA0a9S3hTjLbifcfKtPRXWtblP6kUyH4LvGT6Wor00_1uuE'],  
#   "data":{"F":"Me",
#           "FP":"979632329349",
#           "messageType":NOTIFICATION_GCM_USER_IMMUTABLE
#          }
# }
# 
# json_data2 = {
#   "registration_ids" : ['APA91bHap44N7mK8VJhZdFLA2qxm3rEvJb4B2l1-odZ1Gz8tkYUFkLfrml5ht6dYcn0Ht4hXTvXx0JqS37wc-QTxf6fZunLDWUUnM3ab2974jvRaTxoF1mYgZE_biABCWAZPyR6PHA0a9S3hTjLbifcfKtPRXWtblP6kUyH4LvGT6Wor00_1uuE'],  
#   "data":{
#           "messageContent":"abraka dabra",          
#           "messageType":NOTIFICATION_GCM_GENERAL_FROM_SERVER
#           }
# }
# 
# print get_data('https://android.googleapis.com/gcm/send',post= json.dumps(json_data),headers = headers).read()
# print get_data('https://android.googleapis.com/gcm/send',post= json.dumps(json_data2),headers = headers).read()



   

# def insertUsers():
#     from Db import *
