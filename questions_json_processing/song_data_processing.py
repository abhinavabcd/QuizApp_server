import urllib
import re
import copy
import random
from lxml.html import parse, tostring, clean,etree
from lxml.etree import strip_tags
import pprint
import StringIO
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
import sys
from Config import *
from Db import *
from HelperFunctions import *
from mongoengine.context_managers import switch_db

dbUtils = DbUtils(Config.dbServer) # creating a conenction each time  ? not good , 
def createQuestion(questionDescription,options,answer,hint,tags , qid = None):
        dbUtils.addQuestion(qid if qid else generateKey(),0 ,questionDescription , [], json.dumps(options), answer, hint , "" , 10, 10 , tags) #addQuestion

def random_insert(lst, item):
    lst.insert(random.randrange(len(lst)+1), item)
    
def check_and_get_options(answer, list_options , count=4, insert_answer=True):
    while(True):
        retry = False
        k = random.sample(list_options, count-1)
        for i in k:
            if (i == answer):
                retry= True
        if(not retry):
            if(insert_answer):
                random_insert(k,answer)
            return k 



movies = json.loads(open(raw_input("Enter json questions file path ::")).read())
likes = []
for movie in movies.keys():
	for song in movies[movie].get("songs",[]):
		try:
			likes.append(int(song["fb_likes"]))
		except:
			pass

# songs and movies with min 30 likes will consider
movie_song = []

for movie in movies.keys():
    for song in movies[movie].get("songs",[]):
            try:
                if(int(song["fb_likes"])+(movies[movie].get("year_of_release",2000)-2000) >= 60):
                    movie_song.append([movie, song])
            except:
                    pass

print len(movie_song)
exit

questions = []
count = 0
all_lyricists = []
all_movies = movies.keys()

temp = {}
all_music_directors = []
for movie in movies:
    movie = movies[movie]
    if(movie.get("music_directors",None)):
        movie["music_directors"] = a = (" and ".join(movie["music_directors"])).strip()
        if(a):
            all_music_directors.append(a)
    
    for song in movie.get("songs",[]):
        if(song.get("lyricists",[])):
            song.get("lyricists").sort()
            a = song["lyricists"].pop()
            if(song["lyricists"]):
                song["lyricists"] = " and ".join([' , '.join(song["lyricists"]), a])
            else:
                song["lyricists"] = a
            
        if(song.get("singers",[])):
            song.get("singers").sort()
            a = song["singers"].pop()
            if(song["singers"]):
                song["singers"] = " and ".join([' , '.join(song["singers"]), a])
            else:
                song["singers"] = a
    

            
        
for i in map( lambda x: x[1].get("lyricists",[]), movie_song):
    if(i):
        temp[i] = True
all_lyricists = temp.keys()

def get_all_songs():
    temp = {}   
    for i in map( lambda x: x[1].get("singers",[]), movie_song):
        if(i):
            temp[i] = True
    return temp.keys()

all_singers = get_all_songs()
all_songs = map(lambda x : x[1]["name"] , movie_song)
 
for movie,song in movie_song:
    lyr = song.get("lyricists",None)
    if(lyr!=None):
        y = movies[movie].get("year_of_release",None)
        answer = lyr
        options = check_and_get_options(answer , all_lyricists,4)
        d = "Who wrote the lyrics for the song '"+song['name']+"' from '"+movie+("("+str(y)+")" if y else "")+"'"
        question = ["lyr_"+str(count),0 ,d , [], options , answer, "" , "" , 10, 10 , ['song','lyricists']]
        questions.append(question)
        count+=1
        print question
##        
##        d = answer+" wrote the lyrics from which song from the movie '"+movie+("("+str(y)+")" if y else "")+"'"
##        answer = song["name"]
##        options = check_and_get_options(answer , all_songs,4)
##        
##        question = ["lyr_"+str(count),0 ,d , [], options , answer, "" , "" , 10, 10 , ['song','lyricists']]
##        questions.append(question)
##        count+=1
##        print question

count = 0
for movie,song in movie_song:
    count+=1
    d = "'"+song["name"]+"' song title is from which movie ?"
        ##    options = check_and_get_options(map(lambda x:x["name"], movies[movie]["song"] ), all_songs, 4 , False)
    options = check_and_get_options(movie, all_movies , 4 )
    question = ["song_movie_"+str(count),0 ,d , [], options , movie, "" , "" , 10, 10 , ['song']]
    print question
    questions.append(question)

count = 0
for movie,song in movie_song:
    count+=1
    y = movies[movie].get("year_of_release",None)
    d = "Who are the singers for the song '"+song['name']+"' from '"+movie+("("+str(y)+")" if y else "")+"'"
    singer = song["singers"]
    if(singer):
##    options = check_and_get_options(map(lambda x:x["name"], movies[movie]["song"] ), all_songs, 4 , False)
        options = check_and_get_options(singer, all_singers , 4)
        question = ["song_movie_"+str(count),0 ,d , [], options , singer, "" , "" , 10, 10 , ['singer','movie']]
        count+=1
        print question
        questions.append(question)

count = 0
for title in set(map(lambda x: x[0] , movie_song)):
    movie = movies[title]
    if(movie.get("music_directors",None)):
        d = "who is the music director of movie '"+title+"'"
        options = check_and_get_options(movie["music_directors"],all_music_directors,4)
        answer = movie["music_directors"]
        if(answer):
            question = ["music_director_"+str(count),0 ,d , [], options , answer, "" , "" , 10, 10 , ['musicdirector','movie']]
            count+=1
            print question
            questions.append(question)

for q in questions:
    print q
    createQuestion(q[2], q[4], q[5], q[6], q[10] , qid = q[0])
    

