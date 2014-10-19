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
import json
import socket
import time
import urllib2
import logging
import zlib
from StringIO import StringIO

http_logger = urllib2.HTTPHandler(debuglevel = 0)
url_loader=urllib2.build_opener(http_logger,urllib2.HTTPCookieProcessor(),urllib2.ProxyHandler({}))
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

def getFbLikes(fbUrl):
    try:
        data = json.loads(get_data("https://graph.facebook.com/?ids="+fbUrl).read())
        data = data[data.keys()[0]]
        return int(data.get(u'shares',0))
    except Exception as ex:
        return 0
headers = {
'Host':	'play.raaga.com',
'User-Agent':	'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0',
'Accept':	'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language':	'en-US,en;q=0.5',
'Accept-Encoding':	'gzip, deflate',
'Cookie':	'__utma=112050951.862127129.1407572439.1407572439.1407572439.1; __utmz=112050951.1407572440.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __gads=ID=f0033145e906ff91:T=1407572439:S=ALNI_MaQWww7ykpq04ZGAH7WWTnppudHVg; RGNC3=Andhra+Pradesh; LALO3=17%2E3752994537354%2C78%2E4744033813477; CTYC3=Hyderabad; CNTC3=IN; _referrer_og=http%3A%2F%2Fwww.raaga.com%2F; _jsuid=479922710; __utma=31459711.1613593576.1409575565.1409581241.1409581241.4; __utmz=31459711.1409575565.1.1.utmcsr=raaga.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _fby_site_=1%7Craaga.com%7C1409575578%7C1409581241%7C1409591745%7C1409591745%7C4%7C1%7C5; loginprompt_show=1; lang=A; geo_latitude=0; geo_longitude=0; mobiletopbarclose=stopnow; PHPSESSID=25ts7nbf9sgrgbktggc5t3aeu4; rightside_overlay_display=0; __utmc=31459711; no_trackyy_100682937=1; __utmb=31459711.5.10.1409581241; _first_pageview=1'
}


try:
    data = open("raaga_index.html").read()
except:    
    data = get_data("http://play.raaga.com/telugu/browse/index/",headers = headers).read()
    open("raaga_index.html","w").write(data)

a = parse(StringIO(data)).getroot()
movies={}
try:
    movies = json.loads(open("song_data.json").read())
except:
    pass
count = 0 
for i in a.cssselect(".browseresult_index_album a"):
    movie_name = i.text_content().strip()
    if(movies.get(movie_name,None)):
        continue
    
    movies[movie_name]= movie_data= {}
    try:
        try:
            data = open("./del_songs_data/"+i.attrib["href"].split("/")[-1]).read()
        except:
            data = get_data(i.attrib["href"], headers=headers).read()
            open("./del_songs_data/"+i.attrib["href"].split("/")[-1],"w").write(data)
            
        song_page = parse(StringIO(data)).getroot()
    except:
        print "error parsing data from " + movie_name + " "
        print i.attrib
        continue
    try:
        #movies[movie_name]["meta_data"] = tostring(song_page.cssselect(".raaga_aldetail_left")[0])
        #extract favourites and year of release from the header
        temp = b = song_page.cssselect(".raaga_aldetail_left")[0]
        try:
            print b.cssselect(".foll_count-num")[0].text_content()
            movie_data["favourite_count"] = k = int(b.cssselect(".foll_count-num")[0].text_content().strip())
        except Exception as ex:
            movie_data["favourite_count"] = -1
            print movie_name ," ####################### No favourite Count Found ################"
            
        try:
            movie_data["year_of_release"] = h = int(b.cssselect(".new_album_details p a")[0].text_content().strip())
        except:
            movie_data["year_of_release"] = -1
            print movie_name ,"################## year of release not available #######################"
        
        print movie_name , h , k
    except:
            print movie_name , "WTFFFFFFFFF, no year or favoutires or meta data"
    
    try:
        movies[movie_name]["img"] = url = temp.cssselect("div.image_wrap_big_albumpage img")[0].attrib["src"]
        print  url
    except:
        print "Image error: "+ movie_name

    try:
        details = temp.cssselect("div.al_detail_title p")
        actors = []
        music_directors = []
        for p in details:
            if("music:" in p.text_content().lower()):
                music_directors = map(lambda x: x.text_content() , p.cssselect("a"))
                movies[movie_name]["music_directors"] = music_directors
            if("cast:" in p.text_content().lower()):
                actors = map(lambda x: x.text_content() , p.cssselect("a"))
                movies[movie_name]["actors"] = actors
        
        print actors
        print music_directors
    except:
        print "Details fetch error"+ movie_name

    songs = song_page.cssselect(".track_list_details_name")
    movies[movie_name]["songs"]= songs_list = []

    for song in songs:
        song_name = song.cssselect("a.track_title")[0].text_content()
        song_url = song.cssselect("a.track_title")[0].attrib["href"]
        id = song_url.split("/")[-1].split("-")[-1]
        fb_like_url = "http://www.raaga.com/play/?id="+id
        
        print song_name
        song_data = {"name":song_name}
        meta_data = song.cssselect("div.tname_sing")
        for meta in meta_data:
            if("singer"  in meta.text_content().lower()):
                singers = map(lambda x :x.text_content() , meta.cssselect("a"))
                print singers
                song_data["singers"]= singers
            if("lyricist" in meta.text_content().lower()):
                lyricist = map(lambda x :x.text_content() , meta.cssselect("a"))
                print lyricist
                song_data["lyricists"]=lyricist
                
        song_data["fb_likes"] = fb_like_count = getFbLikes(fb_like_url)
        print "fb_likes: "+str(fb_like_count)
        songs_list.append(song_data)
        
    count+=1
    if(count>10):
        count = 0
        f = open("song_data.json","w")
        f.write(json.dumps(movies))
        f.close()
