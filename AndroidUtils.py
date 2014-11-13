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
