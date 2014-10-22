import urllib
import re
import copy
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
import itertools

#db =connect('OldMoviesData')
db =connect('TmpNewMoviesData')

url_loader=urllib2.build_opener(urllib2.HTTPCookieProcessor(),urllib2.ProxyHandler())
urllib2.install_opener(url_loader)

g_movie_count = 0
g_director_count = 0
g_music_director_count = 0
g_cast_count = 0
mainLink = "http://en.wikipedia.org/wiki/"
domainName = "http://en.wikipedia.org"
minNameSize = 4

class director(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
    
class producer(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
    
class cast(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
    
class music_director(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)

class movie_data(DynamicDocument):
#    uid = StringField(unique=True)
    title = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
    releaseDate = StringField() # dd-mm-yyyy format
    director = ListField(ReferenceField('director'))
    producer = ListField(ReferenceField('producer'))
    music_director = ListField(ReferenceField('music_director'))
    cast = ListField(ReferenceField('cast'))
    fullCast = ListField(ReferenceField('role_data'))
    
class role_data(DynamicDocument):
    cast = ReferenceField('cast')
    castName = StringField()
    role = StringField()
    movie = ReferenceField('movie_data')
    
#class text_link(Document):
#    text = StringField()
#    link = StringField()
#    isValid = BooleanField()

#title,link=None,islinkvalid=False,director=None,cast=None,music_director=None,genre=None,note=None
def createOrUpdateMovie(dataDict):
    if len(dataDict.keys())<2:
        return None
    if 'link' in dataDict and dataDict['link']!=None:
        res = movie_data.objects(link=dataDict['link'])
        if res.first()!=None:
            return res.first()
        dataDict['islinkValid'] = isLinkValid(dataDict['link'])
    else:
        res = None
        if 'director' in dataDict and len(dataDict['director'])>0:
            direc = dataDict['director'][0].name
            res = movie_data.objects(__raw__={'title':dataDict['title'],'director.name':direc})
        if res==None:
            res = movie_data.objects(title=dataDict['title'])
        if res.first()!=None:
            return res.get(0)
    for k in dataDict.keys():
        try:
            if dataDict[k] == []:
                del dataDict[k]
        except:
            print "check for errors"
    mRow = movie_data()
    for field in dataDict.keys():
        mRow.__setattr__(field, dataDict[field])
#    mRow.uid = g_movie_count
#    mRow.title = textList[0]
#    mRow.link = link
#    mRow.islinkValid = islinkvalid
#    mRow.director = director
#    mRow.music_director = music_director
#    mRow.cast = cast
#    mRow.note = note
    mRow.save()
    return mRow

#name,link
def createOrUpdateDirector(dataDict):
#    global g_director_count
    if (dataDict['link']!=None):
        res = director.objects(link=dataDict['link'])
        if res.first()!=None:
            return res.first() #get(0)
        dataDict['islinkValid'] = isLinkValid(dataDict['link'])
    else:
        res = director.objects(name=dataDict['name'])
        if res.first()!=None:
            return res.first()
    dRow = director()
#    dRow['uid'] = g_director_count
#    g_director_count = g_director_count + 1
    for field in dataDict:
        dRow.__setattr__(field, dataDict[field])
#    dRow.name = name
#    dRow.link = link
    dRow.save()
    return dRow

def createOrUpdateProducer(dataDict):
#    global g_producer_count
    if (dataDict['link']!=None):
        res = producer.objects(link=dataDict['link'])
        if res.first()!=None:
            return res.first()
        dataDict['islinkValid'] = isLinkValid(dataDict['link'])
    else:
        res = producer.objects(name=dataDict['name'])
        if res.first()!=None:
            return res.first()
    pRow = producer()
#    dRow['uid'] = g_producer_count
#    g_producer_count = g_producer_count + 1
    for field in dataDict:
        pRow.__setattr__(field, dataDict[field])
#    dRow.name = name
#    dRow.link = link
    pRow.save()
    return pRow

def createOrUpdateMusicDirector(dataDict):
#    global g_music_director_count
    if (dataDict['link']!=None):
        res = music_director.objects(link=dataDict['link'])
        if res.first()!=None:
            return res.first()
        dataDict['islinkValid'] = isLinkValid(dataDict['link']) 
    else:
        res = music_director.objects(name=dataDict['name'])
        if res.first()!=None:
            return res.first()
    cRow = music_director()
#    cRow['uid'] = g_music_director_count
#    g_music_director_count = g_music_director_count + 1
    for field in dataDict:
        cRow.__setattr__(field, dataDict[field])
#    cRow.name = name
#    cRow.link = link
    cRow.save()
    return cRow

def createOrUpdateCast(dataDict):
#    global g_cast_count
    if (dataDict['link']!=None):
        res = cast.objects(link=dataDict['link'])
        if res.first()!=None:
            return res.first()
        dataDict['islinkValid'] = isLinkValid(dataDict['link'])
    else:
        res = cast.objects(name=dataDict['name'])
        if res.first()!=None:
            return res.first()
    cRow = cast()
#    cRow['uid'] = g_cast_count
#    g_cast_count = g_cast_count + 1
    for field in dataDict:
        cRow.__setattr__(field, dataDict[field])
#    cRow.name = name
#    cRow.link = link
    cRow.save()
    return cRow

def get_data(url,post=None,headers={}):
    headers['Accept-encoding'] ='gzip'
    req=urllib2.Request(url,post,headers)
    ret = url_loader.open(req) 
    if ret.info().get('Content-Encoding') == 'gzip':
        return StringIO(zlib.decompress(ret.read(),16+zlib.MAX_WBITS))
    return codecs.decode(ret, 'utf-8')

Months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
# Returns date as string in the format dd-mm-yyyy
def formatDate(vals,year):
#    print vals,year
    day = ''
    month = ''
    if len(vals)>1:
        vals[0] = vals[0].strip()
        vals[1] = vals[1].strip()
        mach1 = re.match('\d+',vals[1])
        mach2 = re.match('\d+',vals[0])
        if mach1!=None:
            day = mach1.group(0)
        elif mach2!=None: #vasl[0] is date
            tmp = mach2.group(0)
            vals[0] = vals[1]
            vals[1] = tmp
            day = tmp
        if vals[1]=="-" or vals[1]=="":
            day = '00'
    if len(vals)>0:
        mach1 = re.match('\d+',vals[0])
        if mach1!=None:
            day = mach1.group(0)
        else:
            vals[0] = vals[0].lower()
            if vals[0] in Months:
                month = str(Months.index(vals[0])+1)
                if len(month)==1:
                    month = "0"+month
            else:
                for i in range(len(Months)):
                    if vals[0].find(Months[i])>=0:
                        month = str(i+1)
                        if len(month)==1:
                            month = "0"+month
    if day == '':
        day = '00'
    if month == '':
        month = '00'
    return day+'-'+month+'-'+str(year)

# Creates a dictionary of data required by CreateOrUpdateMovie
def buildMovieData(fields,data,links,year):
    dataDict = {}
    for j in range(len(fields)):
        if len(data)<=j:
            break
        if len(data[j])==0:
            continue
        if fields[j]=="director":
            directors = []
            for k in range(len(data[j])):
                if len(data[j][k])<minNameSize:
                    continue
                directors.append(createOrUpdateDirector({"name":string.capwords(data[j][k]),"link":(links[j][k]).get('href')}))
            if len(directors)>0:
                dataDict[fields[j]] = directors
        elif fields[j]=="producer" or fields[j]=="production_house" or fields[j]=="banner" or fields[j]=="production":
            producers = []
            for k in range(len(data[j])):
                if len(data[j][k])<minNameSize:
                    continue
                producers.append(createOrUpdateProducer({"name":string.capwords(data[j][k]),"link":(links[j][k]).get('href')}))
            if len(producers)>0:
                dataDict["producer"] = producers
        elif fields[j]=="cast":
            cast = []
            for k in range(len(data[j])):
                if len(data[j][k])<minNameSize:
                    continue
                cast.append(createOrUpdateCast({"name":string.capwords(data[j][k]),"link":(links[j][k]).get('href')}))
            if len(cast)>0:
                dataDict[fields[j]] = cast
        elif fields[j]=="music_director":
            music_directors = []
            for k in range(len(data[j])):
                if len(data[j][k])<minNameSize:
                    continue
                music_directors.append(createOrUpdateMusicDirector({"name":string.capwords(data[j][k]),"link":(links[j][k]).get('href')}))
            if len(music_directors)>0:
                dataDict[fields[j]] = music_directors
        elif fields[j]=="title" or fields[j]=="movie" :
            if len(data[j])>0:
                dataDict["title"] = string.capwords(data[j][0])
            else:
                dataDict["title"] = None
            if links[j]!=None and len(links[j])!=0 and links[j][0]!="":
                dataDict["link"] = (links[j][0]).get('href')
                dataDict["islinkValid"] = isLinkValid((links[j][0]).get('href'))
        elif fields[j]=="opening":
            dataDict["release_date"] = formatDate(data[j],year)
        elif fields[j]=="notes" or fields[j]=="note":
            if (not "producer" in dataDict) and len(data[j])>0:
                pos = data[j][0].lower().strip().split()
                if len(pos)>2 and pos[0]=="produced" and pos[1]=="by":
                    producers = []
                    if len(' '.join(pos[2:]))>=minNameSize and len(links[j])>0:
                        producers.append(createOrUpdateProducer({"name":string.capwords(' '.join(pos[2:])),"link":(links[j][0]).get('href')}))
                    else:
                        producers.append(createOrUpdateProducer({"name":string.capwords(' '.join(pos[2:])),"link":None}))
                    if len(producers)>0:
                        dataDict["producer"] = producers
                else:    
                    dataDict["note"] = ' '.join(data[j])
            else:    
                dataDict["note"] = ' '.join(data[j])
        else:
            dataDict[fields[j]] = data[j]
    if "ref" in dataDict:
        del dataDict["ref"]
    if "reference" in dataDict:
        del dataDict["reference"]
    if "sources" in dataDict:
        del dataDict["sources"]
    if "source" in dataDict:
        del dataDict["source"]
    if not "release_date" in dataDict:
        dataDict["release_date"] = "00-00-"+year
    return dataDict

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

def readAndUpdateCastData(root,cMovie):
    if root==None:
        return []
    #TODO: Extract cast data
    fullText = root.cssselect("div#mw-content-text")
    chil =  fullText[0].getchildren()
    for p in range(len(chil)):
        if chil[p].tag=="h2":
            try:
                if chil[p].getchildren()[0].text_content().lower().strip()=="cast":
                    rolesLi = chil[p+1].cssselect("li")
                    cast = []
                    roleList = []
                    cMovie.fullCast = []
                    for roleLi in rolesLi:
                        aTags = roleLi.cssselect("a")
#                        if len(aTags)!=0:
#                            print aTags[0].text_content()
#                        print roleLi.text_content()
                        tc = roleLi.text_content().strip()
                        tc  = re.sub("\[.*\]|\(.*\)","",tc)
                        if tc.strip()=="":
                            continue
                        tc = re.split("\sas\s|\.\.+|\/",tc)
#                        print tc
                        if len(aTags)>0:
                            cast.append(createOrUpdateCast({"name":string.capwords(tc[0]),"link":aTags[0].get('href')}))
                        else:
                            cast.append(createOrUpdateCast({"name":string.capwords(tc[0]),"link":None}))
                        newRole = role_data()
                        newRole.cast = cast[-1]
                        tmpRoleName = ' - '.join(tc[1:]).strip()
                        newRole.role = tmpRoleName
                        if tmpRoleName=="":
                            continue
                        if len(tmpRoleName)>20: # Try to make it short
                            tmpRoleName = re.split("\.|/",tmpRoleName)[0].strip()
                            if len(tmpRoleName)>20: # Double check
                                tmpRoleName = tmpRoleName.split()
                                if len(tmpRoleName)>1:
                                    newRole.role = " ".join(tmpRoleName[:1])
                                else:
                                    newRole.role = tmpRoleName[0]
                        newRole.movie = cMovie
                        newRole.save()
                        cMovie.fullCast.append(newRole)
                    cMovie.save() # movie cast is not being updated wantedly just to separate them
#                    ri = raw_input()
                    return cast,roleList
            except:
                print "no probs"

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

def formatStringToDBFieldName(val):
    splitVal = val.lower().split()
    newVal = '_'.join(splitVal)
    return newVal

def init_globals():
    pass 

def isPageValid(page):
    if page.find("Wikipedia does not have an article with this exact name")>=0:
        return True
    else:
        return False

def getValidPage(subLink,dirPath="wikipages"):
    print subLink
    if "/wiki/" in subLink:
        subLink = subLink[6:]
    if os.path.isfile(dirPath+"/"+subLink):
        root = parse(open(dirPath+"/"+subLink)).getroot()
        return root
        
    data = get_data(mainLink+subLink)
    fp = open(dirPath+"/"+subLink,'w')
    fp.write(data.getvalue())
    fp.close()
    root = parse(data).getroot()
    if isPageValid(root.text_content())<0:
        return root
#        root = parse(get_data(subLink+'s')).getroot()
#        if isPageValid(root.text_content())<0:
#            return None
#        else:
#            return root
    else:
        return root

def getReleaseDate(dataDict):
    if dataDict.hasKey('Opening'):
        dataDict['releaseDate'] = ""
        
def isLinkValid(link):
    if link!=None and len(link)>4 and link[0:6]=="/wiki/":
        return True
    return False

# List of Lists with strings
def cleanListOfList(rawList):
    for i in range(len(rawList)):
        for j in range(len(rawList[i])):
            if rawList[i][j]=="":
                rawList[i].pop(j)
            else:
                rawList[i][j] = (rawList[i][j]).strip()
                rawList[i][j] = re.sub('\[.*\]','',rawList[i][j])
                rawList[i][j] = rawList[i][j].replace(':','')
#                try:
                rawList[i][j] = rawList[i][j].encode('ascii','ignore')
                rawList[i][j] = (rawList[i][j]).strip()
#                except:
#                    pass
    return rawList

def buildDirectories(dirPath="wikipages"):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

if os.path.isfile("links.json"):
    with open("links.json") as json_file:
        links = json.load(json_file)


buildDirectories("wikipages")
buildDirectories("wikipages/movies")
init_globals()
#PAGES = 100
#PAGES = 10
PAGES = 15

#for i in range(40,PAGES):
#for i in range(PAGES):
for i in range(10,PAGES):

#    year = "19"+str(i)
#    year = "200"+str(i)
    year = "20"+str(i)    
    root = getValidPage('List_of_Telugu_films_of_'+year)
    if root==None:
        continue
    tables = root.cssselect("table.wikitable")
    for p in range(len(tables)):
        columnNames = tables[p].cssselect("table.wikitable th")
        cspan = []
        j = 0 
        dbFields = []
        for j in range(len(columnNames)):
            col = columnNames[j]
    #        print etree.tostring(col)
            dbFields.append(formatStringToDBFieldName(col.text_content()))
    #        print dbFields
            span = col.get('colspan')
            if span==None:
                span = 1
            cspan.append(int(span))
    
    #    print len(columnNames)
        print dbFields
        rows = tables[p].cssselect("tr")
        rows.pop(0)
        
        matches = map(lambda x: x.cssselect("td"),rows)
        matches_new = copy.deepcopy(matches)
    #    prevLength = -1
        validLinks = []
        x = 0 
        while x<len(matches):
#            try:
                l = 0
                if len(matches[x])==0:
                    continue
    #            print "X is: "+str(x)
                while l<len(matches[x]):
    #                print map(lambda x: x.text_content(),matches[x])
                    span = matches[x][l].get('rowspan')
                    if span!=None and int(span)>1:
                        span = int(span)
                        matches[x][l].set('rowspan','1')
                        for j in range(1,span):
                            if x+j < len(matches):
                                matches[x+j].insert(l,copy.deepcopy(matches[x][l]))
                                matches[x+j][l].set('rowspan','1')
    #                print len(matches[x])
    #                print map(lambda x: x.text_content(),matches[x]) #etree.tostring(x)
                    l = l+1
                    
                print map(lambda x: x.text_content(),matches[x])
                for l in range(len(cspan)):
                    if cspan[l]>1:
                        txt = re.sub("\n","",matches[x][l].text_content().strip())
                        for n in range(cspan[l]-1):
                            if len(matches[x])<l+2:
                                break
                            ele = matches[x].pop(l+1)
                            txt = txt + "," + re.sub("\n","",ele.text_content().strip())
                        matches[x][l].clear()
                        matches[x][l].text = txt
                        
                print map(lambda x: x.text_content(),matches[x])
    #            print "----------^ check spans---------"
    
    #            x=x+1
    #            raw_input()
    #            continue
        #        if l!=prevLength and prevLength!=-1:
        #            print "Columns count problem in wikitable"
        #            break
        #        prevLength = len(matches[x])
        
                #['SEP,7', 'Atanu + Ame = 9', '', '', '']
                textList = map(lambda x: re.split('[,\n&/]+',x.text_content().strip()),matches[x])#etree.tostring(x)
                textList = cleanListOfList(textList)
                
                alist = map(lambda x: x.cssselect('a'),matches[x]) # inconsistent data
        #        print textList
        #        print alist
                # To make links and text consistent
                for k in range(len(alist)):
                    c = 0
                    while len(textList[k])!=len(alist[k]):
                        if c==len(alist[k]):
                            for m in range(c,len(textList[k])):
                                alist[k].append({"href":None})
                            break
    #                    print textList[k]
    #                    print alist[k][c].text_content()
                        if alist[k][c].text_content() in textList[k]: 
                            ind  = textList[k].index(alist[k][c].text_content())
                        else:
                            alist[k].pop(c)
                            continue
                        dif = ind - c
                        for l in range(dif):
                            alist[k].insert(c,{"href":None})
                        c = ind+1
                
        #        print alist
#                print textList
#                print alist      
                tmp = buildMovieData(dbFields, textList, alist, year)
                print tmp
                cMovie = createOrUpdateMovie(tmp)
                if cMovie!=None:
                    if cMovie.islinkValid==True:
                        fullCastData = readAndUpdateCastData(getValidPage(cMovie.link,"wikipages/movies"),cMovie)
                    # TODO: update castData into DB
#            except (IndexError):
#                print "issues with the table rows"
            
            # need to refine below line - incorrect
    #        createOrUpdateMovie(textList[0], lnk, islinkvalid, createOrUpdateDirector(textList[1]), createOrUpdateCast(textList[2]), textList[3],textList[4])
                x = x + 1
#                break
#        break
#    break
'''
    for k in map(lambda x: 'http://en.wikipedia.org'+x, validLinks):
        if(checkAndSetLinkRef(k)!=None):
            itemData = parse(get_data(k)).getroot() #urllib.urlopen
            images = map(lambda x: x.get('data-medium-url') , itemData.cssselect('ul.thumbnails a'))
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
#            relatedItems = map(lambda x: str(getLinkRefOrTmpRef('http://www.themobilestore.in'+str(x.get('href')))) , root.cssselect("div.variant-image a"))
            relatedItems = map(lambda x: str('http://www.themobilestore.in'+str(x.get('href'))) , itemData.cssselect("div.variant-image a"))
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
'''        