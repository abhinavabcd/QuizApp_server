import urllib
import re
import random
from lxml.html import parse, tostring, clean,etree
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
import itertools
import os
import json
import codecs
from StringIO import StringIO
from mongoengine import *
import random
import string
import datetime
import time
import bson
from Config import *
import itertools

db =connect('movieDB')

url_loader=urllib2.build_opener(urllib2.HTTPCookieProcessor(),urllib2.ProxyHandler())
urllib2.install_opener(url_loader)

g_movie_count = 0
g_director_count = 0
g_music_director_count = 0
g_cast_count = 0

class director(Document):
    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=True)
    
class cast(Document):
    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=True)
    
class musicDirector(Document):
    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=True)

class movieData(Document):
    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=True)
    director = ListField(ReferenceField('director'))
    musicDirector = ListField(ReferenceField('musicDirector'))
    cast = ListField(ReferenceField('cast'))
    note = StringField()

def createOrUpdateMovie(name,link=None,islinkvalid=False,director=None,cast=None,musicDirector=None,genre=None,note=None):
    mRow = movieData()
    mRow.uid = g_movie_count
    mRow.name = textList[0]
    mRow.link = link
    mRow.islinkValid = islinkvalid
    mRow.director = director
    mRow.musicDirector = musicDirector
    mRow.cast = cast
    mRow.note = note
    return mRow

def createOrUpdateDirector(name,link):
    global g_director_count
    res = director.objects(link=link)
    if res!=None:
        return res.get(0)
    dRow = director()
    dRow.uid = g_director_count
    g_director_count = g_director_count + 1
    dRow.name = name
    dRow.link = link
    return dRow

def createOrUpdateCast(name,link):
    global g_cast_count
    res = cast.objects(link=link)
    if res!=None:
        return res.get(0)
    cRow = director()
    cRow.uid = g_cast_count
    g_cast_count = g_cast_count + 1
    cRow.name = name
    cRow.link = link
    return cRow

def get_data(url,post=None,headers={}):
    headers['Accept-encoding'] ='gzip'
    req=urllib2.Request(url,post,headers)
    ret = url_loader.open(req) 
    if ret.info().get('Content-Encoding') == 'gzip':
        return StringIO(zlib.decompress(ret.read(),16+zlib.MAX_WBITS))
    return codecs.decode(ret, 'utf-8')

uniqueId = 1
links={}

def checkAndSetLinkRef(link):
    global uniqueId,links
    ret = links.get(link,None)
    if(ret==None):
        links[link]=uniqueId
        uniqueId = uniqueId + 1
        return links[link]
    return None

def insertCombinations(catalog,listItem):
    liobjs = []
    if len(catalog)==0:
        return liobjs
    combis = list(itertools.product(*catalog.values()))
    listItem['searchTags'].append("dummy")
    for combi in combis:
        tmp = ' '.join(map(lambda x: str(x),combi))
        name = listItem['group_Type'] +' '+ tmp
        listItem['name'] = name
        listItem['boUid'] = name
        listItem['searchTags'].pop()
        listItem['searchTags'].append(tmp)
        listItem['unitPrice'] = listItem['unitPrice']+random.randint(0,1000)
        listItem['unitFakePrice'] = listItem['unitPrice'] + 100
    return liobjs

def init_globals():
    pass 

init_globals()
PAGES = 99

if os.path.isfile("links.json"):
    with open("links.json") as json_file:
        links = json.load(json_file)

for i in range(40,PAGES):

    root = parse(get_data('http://en.wikipedia.org/wiki/List_of_Telugu_films_of_19'+str(i))).getroot()
    columns = root.cssselect("table.wikitable th")
    print len(columns)
    rows = root.cssselect("table.wikitable tr")
    rows.pop(0)
    
    matches = map(lambda x: x.cssselect("td"),rows)
    prevLength = -1
    validLinks = []
    for match in matches:
        l = len(match)
        if l==0:
            continue
        if l!=prevLength and prevLength!=-1:
            print "Columns count problem in wikitable"
            break
        prevLength = len(match)
        textList = map(lambda x: x.text_content().strip().split(','),match)#etree.tostring(x)
         
        alist = map(lambda x: x.cssselect('a'),match)
        lnk = alist[0].attrib['href']
        islinkvalid = False
        if len(lnk)>4 and lnk[0:6]=="/wiki/":
            validLinks.append(lnk)
            islinkvalid = True
        # need to refine below line - incorrect
        createOrUpdateMovie(textList[0], lnk, islinkvalid, createOrUpdateDirector(textList[1]), createOrUpdateCast(textList[2]), textList[3],textList[4])
    break

    for k in map(lambda x: 'http://en.wikipedia.org'+x, validLinks):
        if(checkAndSetLinkRef(k)!=None):
            itemData = parse(get_data(k)).getroot() #urllib.urlopen
            images = map(lambda x: x.attrib['data-medium-url'] , itemData.cssselect('ul.thumbnails a'))
#            print images
#            print name
            tmpPrice = re.sub("\D","",itemData.cssselect('span.m-w')[0].text_content())
            if tmpPrice == "":
                unitPrice = int(random.random()*10000) 
            else: 
                unitPrice = int(tmpPrice)
            unitFakePrice = unitPrice + 100
            discreteFactor = 1
            isContinuous = False
            isUnique = False
#            print unitPrice
            catalog = {}
            tmp = itemData.cssselect('div#catalog-options')
#            print len(tmp)
            tmp1 = map(lambda x: x.text_content().strip().strip(':'), tmp[0].cssselect('b'))
#            print tmp1
            tmp2 = tmp[0].cssselect('ul.cat-options')
#            print len(tmp1),len(tmp2)
            if len(tmp1)==len(tmp2):
                for i in range(len(tmp2)):
                    catalog[re.sub("[\$\.]","",tmp1[i])] = map(lambda x: x.text_content().strip(), tmp2[i].cssselect('span.catalog-option-title'));
#            print catalog
#            relatedItems = map(lambda x: str(getLinkRefOrTmpRef('http://www.themobilestore.in'+str(x.attrib['href']))) , root.cssselect("div.variant-image a"))
            relatedItems = map(lambda x: str('http://www.themobilestore.in'+str(x.attrib['href'])) , itemData.cssselect("div.variant-image a"))
#            print colors
            searchTags = map(lambda x: x.text_content(), itemData.cssselect("div.bread-crumbs span"))
            if len(searchTags)>0:
                searchTags.pop(0)
#            print searchTags
            name = itemData.cssselect("div#catalog-title h1")[0].text_content() #searchTags[-1] 
            description = itemData.cssselect("div#description")[0].text_content()
#            print description
            selectionMinMax = [1,1]
            isEndPoint = True
            isSearchNode = True
            groupType = None
            properties = {}
            properties["relatedItems"] = relatedItems
            properties.update(catalog)

            tmp = itemData.cssselect("div#feature_groups tr")
            for tmpchild in tmp:
                try:
                    tt = map(lambda x: x.text_content(),tmpchild.cssselect("td"))
                except:
                    tt = []
                if len(tt)==2:
                    properties[re.sub("[\$\.]","",tt[0].strip().strip(':'))] = tt[1].strip().strip(':')
#            print relatedItems
            uid = itemData.cssselect("div#catalog-title h1")[0].text_content()
            
            print k
            fp = open('links.json', 'w')
            json.dump(links, fp)
            fp.close()
#            print properties
#            print properties
#            print liobj.properties
#            print listItem
#            print map(lambda x: etree.tostring(x),itemData.cssselect("div#feature_groups tr"))

#            etree.tostring
#        break
            #ListItem.CreateNew(quantity=5, _rangeList=None, parentListItemRef=None, rootListItemRef=None, parentPath=None, childLists=None, linkedLists, name, description, images, uid, discreteFactor, isContinuous, isUnique, unitPrice, unitFakePrice, isUserAuth, boGroupUid, selectionType, selectionMinMax, viewSpan, isNeeded, expandForEach, isEndPoint, ownerUser, uiRenderRef, searchTags, isSearchNode, indexToItemMap, discountConditions, afterCartConditions, listItemHeadRef, isApprovalNeeded, properties, commonUserTextInput, commonUserFileInput, commonUserSelectInput, commonUserRadioInput, userTextInput, userFileInput, userSelectInput, userRadioInput, group_Type, isTime, save)
        
#    break
        