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

directorsData = []
moviesData = []
castData = []
producersData = []
musicDirectorsData = []

directorFameFilter = 2 # threshold to generate questions related to persons by number of movies involved in (>=)
producerFameFilter = 3
castFameFilter = 3
optionsSize = 4
maxCastSize = 3
maxCastRoleIndex = 3

#register_connection("NewMovies", "NewMoviesData") 
#register_connection("default", "quizApp") 
connect('FNewMoviesData')

class director(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
#    meta = {"data": "NewMoviesData"}
    
class producer(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
#    meta = {"data": "NewMoviesData"}
    
class cast(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
#    meta = {"data": "NewMoviesData"}
    
class music_director(DynamicDocument):
#    uid = StringField(unique=True)
    name = StringField()
    link = StringField()
    islinkValid = BooleanField(default=False)
#    meta = {"data": "NewMoviesData"}

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
#    meta = {"data": "NewMoviesData"}
    
class role_data(DynamicDocument):
    cast = ReferenceField('cast')
    castName = StringField()
    role = StringField()
    movie = ReferenceField('movie_data')
    

def createQuestion(questionDescription,options,answer,hint,tags):
        dbUtils = DbUtils(Config.dbServer)
        dbUtils.addQuestion(generateKey(),0 ,questionDescription , [], options, answer, hint , "" , 10, 10 , tags) #addQuestion

def bracesFormatter(mName):
    if mName.find('(')>=0:
        if mName.find(')')>=0:
            #mNameSplit = re.split("[\(\) ]+", mName)
            try:
                ind1 = mName.index('(')
                ind2 = mName.index(')')
                if ind1!=0 and (mName[ind1-1]!=' ' or mName[ind1-1]!='\t'):
                    tmp1 = mName[0:ind1]
                    tmp2 = mName[ind1:]
                    mName = tmp1 + " " + tmp2
                    ind2 = ind2 + 1
                if ind2!=len(mName)-1 and (mName[ind2+1]!=' ' or mName[ind1+1]!='\t'):
                    tmp1 = mName[0:ind2+1]
                    tmp2 = mName[ind2+1:]
                    mName = tmp1 + " " + tmp2
            except:
                pass
            try:
                ind1 = mName.index('(')
                ind2 = mName.index(')')
                tmp = mName[ind1:ind2+1]
                tmp = tmp.replace(' ','-')
                mName = mName[:ind1]+tmp+mName[ind2+1:]
            except:
                pass
        else:
            mName.replace("(","")
    elif mName.contains(')'):
        mName.replace(")","")
    return mName

def movieNameFormatter(mName):
    mName = re.sub("\(.*\)","",mName)
    mName = re.sub("[\(\)]+","",mName)
    mName = re.sub("\s+"," ",mName)
    return mName


def generateMovieNameQuestions(movie):
    if movie.title==None:
        return
    splitTitle = movieNameFormatter(movie.title).split()
    if len(splitTitle)<2: # if 2 is changed, you have to change getOptions method below and split
        return
#    print splitTitle
    dash = " _____ "
    qList = ["Complete the movie title- 'X'","Identify the missing word from the movie title- 'X'"]
    ques = random.choice(qList)
    ind = random.randrange(len(splitTitle))
    answer = splitTitle[ind]
    splitTitle[ind] = dash
    ques = ques.replace('X',' '.join(splitTitle))
#    bigTitleMovies = moviesData.__call__(title=re.compile(r'.* .* .*'))
#    #bigTitleMovies = movie_data.objects(__raw__={'title':{'$regex': '/.* .* .*/i'},'islinkValid':'True'})
#    print bigTitleMovies
#    moviesData.rewind()
#    print len(bigTitleMovies)
    options = set()
    while len(options)<optionsSize:
        options = getOptionsSetForMovieNameQuestion(moviesData,"title")
    #    print splitTitle
    #    print options
        try:
            options = set(x.split()[ind] for x in options)
        except:
            options = set(x.split()[1] for x in options) # CAUTION
        options.add(answer)
    options = list(options)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    try:
        createQuestion(ques, options, answer, movie.note, ["movies","movie-name","new"])
    except:
        createQuestion(ques, options, answer, "", ["movies","movie-name","new"])
#    sys.exit()
    
    
def generateMovieDirectorQuestions(movie):
    if movie.director==None or len(movie.director)==0:
        return
    qList = ["Who is the director of 'X' movie?","'X' movie was directed by ____.","Who has directed the movie 'X' ?"]
    ques = random.choice(qList)
    ques = ques.replace('X',movie.title)
    options = set()
    while len(options)<optionsSize:
        options = getOptionsSet(directorsData)
        options.add(movie.director[0].name)
    options = list(options)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    try:
        createQuestion(ques, options, movie.director[0].name, movie.note, ["movies","director"])
    except:
        createQuestion(ques, options, movie.director[0].name, "", ["movies","director"])


def generateMovieGenreQuestions(movie):
    try:
        if len(movie.genre)==0:
            return
    except:
        return
    qList = ["What is the genre of 'X' movie?","'X' movie is of genre ____."]
    ques = random.choice(qList)
    ques = ques.replace('X',movie.title)

    answer = movie.genre[0]
    print answer
    mainOptions = set()
    mainOptions.add(answer)
    while(len(mainOptions)<optionsSize):
        options = list(getOptionsSetObject(moviesData))

        for option in options:
            print mainOptions
            if len(mainOptions)==optionsSize:
                break
            try:
                if (not option["genre"][0] in mainOptions) and (not option["genre"][0] in movie.genre):
                    mainOptions.add(option["genre"][0])
            except:
                print "not genre"
                pass
    mainOptions = list(mainOptions)
    random.shuffle(mainOptions)
    mainOptions = [x.replace(',','-') for x in mainOptions]
    # to generate string
    mainOptions = ', '.join(mainOptions)
    print mainOptions    
    try:
        if movie.note.lower().find("genre")<0:
            createQuestion(ques, mainOptions, answer, movie.note, ["movies","genre"])
        else:
            createQuestion(ques, mainOptions, answer, "", ["movies","genre"])
    except:
        createQuestion(ques, mainOptions, answer, "", ["movies","genre"])
        
def generateDirectorMovieQuestions(direc):
    if direc.name==None:
        return
    qList = ["Which one of the following movies was directed by 'X' ?","'X' has directed ____ movie."]
    
    ques = random.choice(qList)
    ques = ques.replace('X',direc.name)
    directorMovies = moviesData.__call__(director=direc)
    moviesData.rewind()
    notDirectorMovies = moviesData.__call__(director__nin=[direc])
    moviesData.rewind()
    if len(directorMovies)<directorFameFilter:
        return
    print len(directorMovies)
    print direc.name
    print direc.id
    print len(notDirectorMovies) 
    
    movie = random.choice(directorMovies)
    options = set()
    while len(options)<optionsSize:
        options = getOptionsSet(notDirectorMovies,"title")
        options.add(movie.title)
    options = list(options)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    
#    print options
#    print ques
    try:
        createQuestion(ques, options, movie.title, movie.note, ["movies","director"])
    except:
        createQuestion(ques, options, movie.title, "", ["movies","director"])

           
def generateMovieProducerQuestions(movie):
    try:
        if len(movie.producer)==0: # or movie.producer[0].name==None
            return
    except:
        return
#    for i in range(len(movie.producer)):
#        print movie.producer[i].name
        
    qList = ["Who is the producer of 'X' movie?","'X' movie was produced by ____."]
    ques = random.choice(qList)
    ques = ques.replace('X',movie.title)
    
    options = set()
    while len(options)<optionsSize:
        options = getOptionsSet(producersData)
        options.add(movie.producer[0].name)
    options = list(options)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
#    print options
#    print ques
    try:
        if movie.note.lower().find("produce")<0:
            createQuestion(ques, options, movie.producer[0].name, movie.note, ["movies","producer"])
        else:
            createQuestion(ques, options, movie.producer[0].name, "", ["movies","producer"])
    except:
        createQuestion(ques, options, movie.producer[0].name, "", ["movies","producer"])
        
        
def generateProducerMovieQuestions(prod):
    if prod.name==None:
        return
    qList = ["Which one of the following movies was produced by 'X' ?","'X' has produced for ____ movie."]
    
    ques = random.choice(qList)
    ques = ques.replace('X',prod.name)
    producerMovies = moviesData.__call__(producer=prod)
    moviesData.rewind()
    notProducerMovies = moviesData.__call__(producer__nin=[prod])
    moviesData.rewind()
    if len(producerMovies)<producerFameFilter:
        return
    print len(producerMovies)
    print prod.name
    print prod.id
    print len(notProducerMovies) 
    
    movie = random.choice(producerMovies)
    options = set()
    while len(options)<optionsSize:
        options = getOptionsSet(notProducerMovies,"title")
        options.add(movie.title)
    options = list(options)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    
#    print options
#    print ques
    try:
        createQuestion(ques, options, movie.title, movie.note, ["movies","producer"])
    except:
        createQuestion(ques, options, movie.title, "", ["movies","producer"])        


def generateCastMovieQuestions(cas):
    if cas.name==None:
        return
    qList = ["Identify the movie in which 'X' is present?","'X' has acted in ____ movie.","Select the movie in which 'X' has acted?"]
    
    ques = random.choice(qList)
    ques = ques.replace('X',cas.name)
    castMovies = moviesData.__call__(cast=cas)
    moviesData.rewind()
    notCastMovies = moviesData.__call__(cast__nin=[cas])
    moviesData.rewind()
    if len(castMovies)<castFameFilter:
        return
    print len(castMovies)
    print cas.name
    print cas.id
    print len(notCastMovies) 
    
    movie = random.choice(castMovies)
    options = set()
    while len(options)<optionsSize:
        options = getOptionsSet(notCastMovies,"title")
        options.add(movie.title)
    options = list(options)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    
#    print options
#    print ques
    try:
        createQuestion(ques, options, movie.title, movie.note, ["movies","cast"])
    except:
        createQuestion(ques, options, movie.title, "", ["movies","cast"]) 

# This method is customized for cast        
def generateMovieCastQuestions(movie):
    try:
        if len(movie.cast)==0:
            return
    except:
        return
    qList = ["Identify the cast starred in 'X' movie.","Which of the following cast belongs to the movie 'X' ?","In movie 'X', identify the cast present"]
    ques = random.choice(qList)
    ques = ques.replace('X',movie.title)
    
    # to generate combinations
    mainOptions = []
    if len(movie.cast)> maxCastSize:
        opsize = maxCastSize
    else:
        opsize = len(movie.cast)
     
    while(len(mainOptions)<optionsSize-1):
        options = list(getOptionsSet(castData, maxOptions=opsize))
        # Polish Cast names 
#        for x in range(len(options)):
#            spx = options[x].split()
#            tmp = ""
#            i=0
#            while len(tmp)<5 and i<len(spx): # To ensure option is sufficiently long
#                tmp  = [' '.join(spx[:i]) ]
#                i = i+1
#            if len(tmp)>=5:
#                options[x] = tmp

        # To check if option is valid
        state = True
        for option in options:
            state = state and (option in movie.cast)
        if state:
            continue
        
        if not options in mainOptions:
            mainOptions.append(options)
    
    # to add correct answer to options
    answerCast = set()
    for i in range(len(movie.cast)):
        if i > maxCastSize:
            break
        answerCast.add(movie.cast[i].name)
    if not answerCast in mainOptions:
        mainOptions.append(answerCast)
    
    random.shuffle(mainOptions)
    
    # to generate string
    mainOptions = [' - '.join(options) for options in mainOptions]
    mainOptions = [x.replace(',',' ') for x in mainOptions]
    mainOptions = ', '.join(mainOptions)
    answerCast = ' - '.join(answerCast)
        
    try:
        if movie.note.lower().find("cast")<0:
            createQuestion(ques, mainOptions, answerCast, movie.note, ["movies","cast"])
        else:
            createQuestion(ques, mainOptions, answerCast, "", ["movies","cast"])
    except:
        createQuestion(ques, mainOptions, answerCast, "", ["movies","cast"])

def generateMovieMusicDirectorQuestions(movie):
    try:
        if len(movie.music_director)==0:
            return
    except:
        return
    qList = ["Who is the music director of movie 'X'?","For the movie 'X', Identify the correct music director."]
    ques = random.choice(qList)
    ques = ques.replace('X',movie.title)

    # to generate combinations
    mainOptions = []
    while(len(mainOptions)<optionsSize-1):
        options = getOptionsSet(musicDirectorsData,maxOptions=len(movie.music_director))
        
        #TODO: Copy code from above cast method - This is incomplete
        if not options in mainOptions:
            mainOptions.append(options)
    
    # to add correct answer to options
    answer = set()
    for i in range(len(movie.music_director)):
        answer.add(movie.music_director[i].name)
    if not answer in mainOptions:
        mainOptions.append(answer)
    
    random.shuffle(mainOptions)
    
    # to generate string
    mainOptions = [' - '.join(options) for options in mainOptions]
    mainOptions = [x.replace(',',' ') for x in mainOptions]
    mainOptions = ', '.join(mainOptions)
    answer = ' - '.join(answer)


    try:
        if movie.note.lower().find("music")<0:
            createQuestion(ques, mainOptions, answer, movie.note, ["movies","music-director"])
        else:
            createQuestion(ques, mainOptions, answer, "", ["movies","music-director"])
    except:
        createQuestion(ques, mainOptions, answer, "", ["movies","music-director"])

def generateMovieYearOfReleaseQuestions(movie):
    if movie.release_date==None:
        return
    qList = ["In which year did the movie 'X' was released?","'X' movie was released in ____.","Guess the year of release for the movie 'X'"]
    ques = random.choice(qList)
    ques = ques.replace('X',movie.title)
    finOptions = set()
    answer = (movie.release_date).split('-')[2]
    finOptions.add(answer)
    while len(finOptions)<optionsSize:
        options = list(getOptionsSet(moviesData,"release_date"))
        for i in range(len(options)):
            if len(finOptions)==optionsSize:
                break
            option = options[i]
            if option!=None:
                finOptions.add(option.split('-')[2])
                
    options = list(finOptions)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    try:
        createQuestion(ques, options, answer, movie.note, ["movies","release-year"])
    except:
        createQuestion(ques, options, answer, "", ["movies","release-year"])
        
def generateYearOfReleaseMovieQuestions(movie):
    if movie.release_date==None:
        return
    qList = ["In year 'X' which of the following movies was released?","____ movie was released in the year 'X'.","Identify the movie released in 'X'"]
    ques = random.choice(qList)
    ques = ques.replace('X',(movie.release_date).split('-')[2])
    finOptions = set()
    answer = movie.title
    finOptions.add(answer)
    tmp = set()
    tmp.add((movie.release_date).split('-')[2])
    while len(tmp)<optionsSize:
        options = list(getOptionsSetObject(moviesData))
        for i in range(len(options)):
            if len(tmp)==optionsSize:
                break
            option = options[i]
            if option!=None:
                if not (option.release_date).split('-')[2] in tmp:
                    finOptions.add(option.title)
                    tmp.add((option.release_date).split('-')[2])
                    
    options = list(finOptions)
    random.shuffle(options)
    options = [x.replace(',','-') for x in options]
    options = ', '.join(options)
    try:
        createQuestion(ques, options, answer, movie.note, ["movies","release-year"])
    except:
        createQuestion(ques, options, answer, "", ["movies","release-year"])

def generateRoleCastQuestions(movieData):
    if movieData.fullCast==None or len(movieData.fullCast)==0:
        return
    qList = ["Identify the actor/actress who played the role of 'X' in the movie 'Y'","Which of the following actor/actress has acted in the role of 'X' in movie 'Y' ?",
             "In the movie 'Y', _____ has acted in the role 'X'?"]
#    print movieData.fullCast[0]['role']
    for fcast in movieData.fullCast:
        ind = movieData.fullCast.index(fcast)
#        print ind
        ques = random.choice(qList)
        ques = ques.replace('Y',movieData.title)
        cRole = role_data.objects(_id=fcast)[0]
        if cRole.cast.islinkValid==False or ind>maxCastRoleIndex: # Hard limit to improve questions
            return
        ques = ques.replace('X',cRole.role)
        answer = cRole.cast.name.strip()
        if answer=="":
            return
#        print answer
        mainOptions = set()
        mainOptions.add(answer)
        
        while len(mainOptions)<optionsSize:
            options = list(getOptionsSetObject(moviesData))
            options = [x.fullCast for x in options]
#            print options
            for option in options:
                if len(option)==0:
                    continue
                if len(mainOptions)==optionsSize:
                    break
                try:
                    
                    tmpRole = role_data.objects(_id=option[ind])[0]
                    nam = (tmpRole.cast.name).strip()
                    if nam!="" and tmpRole.cast.islinkValid:
                        mainOptions.add(nam)
                except (IndexError):
                    if ind>0:
                        objs = role_data.objects(_id=option[-1])
                        if len(objs)>0 and objs[0].cast.name.strip()!="" and objs[0].cast.islinkValid:
                            mainOptions.add(objs[0].cast.name.strip())
                    
#                    except:
#                        pass

#        while len(mainOptions)<optionsSize:
#            options = list(getOptionsSet(castData, "name"))
#            for option in options:
#                if len(mainOptions)==optionsSize:
#                    break
#                mainOptions.add(option)                
        mainOptions = list(mainOptions)
        random.shuffle(mainOptions)
        mainOptions = [x.replace(',','-') for x in mainOptions]
        mainOptions = ', '.join(mainOptions)
        print ques
        print answer
        print mainOptions
        try:
            createQuestion(ques, mainOptions, answer, movieData.note, ["movies","role"])
        except:
            createQuestion(ques, mainOptions, answer, "", ["movies","role"]) 
#    sys.exit()   

def generateCastRoleQuestions(movieData):
    if movieData.fullCast==None:
        return
    qList = ["Identify the role played by 'X' in the movie 'Y'","In the movie 'Y', _____ character was acted by 'X'.",
             "In the movie 'Y', _____ role was played by 'X'?"]
    
    for fcast in movieData.fullCast:
        ind = movieData.fullCast.index(fcast)
        ques = random.choice(qList)
        ques = ques.replace('Y',movieData.title)
        cRole = role_data.objects(_id=fcast)[0]
#        cCast = cast.objects(_id=cRole.cast)[0]
        if cRole.cast.islinkValid==False or ind>maxCastRoleIndex: # Hard limit to improve questions
            return
        ques = ques.replace('X',cRole.cast.name)
        answer = cRole.role.strip()
        if answer=="":
            return
        mainOptions = set()
        mainOptions.add(answer)
        while len(mainOptions)<optionsSize:
            options = list(getOptionsSetObject(moviesData))
            options = [x.fullCast for x in options]
            for option in options:
                if len(option)==0:
                    continue
                if len(mainOptions)==optionsSize:
                    break
                try:
                    tmpRole = role_data.objects(_id=option[ind])[0]
                    nam = (tmpRole.role).strip()
                    if nam!="" and tmpRole.cast.islinkValid and (len(nam)<=len(random.choice(list(mainOptions))) or len(nam)<20):
                        mainOptions.add(nam)
                except (IndexError):
                    if ind>0:
                        objs = role_data.objects(_id=option[-1])
                        if len(objs)>0 and objs[0].role.strip()!="" and objs[0].cast.islinkValid and (len(objs[0].role.strip())<=len(random.choice(list(mainOptions))) or len(objs[0].role.strip())<20):
                            mainOptions.add(objs[0].role.strip())
        
        mainOptions = list(mainOptions)
        random.shuffle(mainOptions)
        mainOptions = [x.replace(',','-') for x in mainOptions]
        mainOptions = ', '.join(mainOptions)
        print ques
        print answer
        print mainOptions
        try:
            createQuestion(ques, mainOptions, answer, movieData.note, ["movies","role"])
        except:
            createQuestion(ques, mainOptions, answer, "", ["movies","role"])

'''
def getOptionsSet(objList,maxOptions = 5):
    options = set()
    if len(objList)<maxOptions:
        for obj in objList:
            options.add(obj.name)
        return options
    
    while len(options)<maxOptions:
        options.add(random.choice(objList).name)
    objList.rewind()
    return options
'''
        
def getOptionsSet(objList,field="name",maxOptions = optionsSize-1):
    options = set()
#    if len(objList)<maxOptions:
#        for obj in objList:
#            options.add(obj[field])
#        return options
    
    while len(options)<maxOptions:
        choic = random.choice(objList)
#        print choic.id
#        print field
#        print choic[field]
        options.add(choic[field])
    objList.rewind()
    return options

def getOptionsSetObject(objList,maxOptions = optionsSize-1):
    options = set()
    
    while len(options)<maxOptions:
        choic = random.choice(objList)
#        print choic.id
#        print field
#        print choic[field]
        options.add(choic)
    objList.rewind()
    return options

def getOptionsSetForMovieNameQuestion(objList,field="name",maxOptions = optionsSize-1):
    options = set()
#    if len(objList)<maxOptions:
#        for obj in objList:
#            options.add(movieNameFormatter(obj[field]))
#        return options
    
    while len(options)<maxOptions:
        cmovie  = movieNameFormatter(random.choice(objList)[field])
        if len(cmovie.split())>=2:
            options.add(cmovie)
    objList.rewind()
    return options

moviesData = movie_data.objects(islinkValid=True)
directorsData = director.objects()  
musicDirectorsData = music_director.objects()  
castData = cast.objects()    
producersData = producer.objects()

# MovieName Based questions from here
'''
for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieDirectorQuestions(movieData)
   
ques  = Questions.objects()
with open('movie_director.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()


for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieProducerQuestions(movieData)

ques  = Questions.objects()
with open('movie_producer.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()


for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieCastQuestions(movieData)

ques  = Questions.objects()
with open('movie_cast.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()

for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieYearOfReleaseQuestions(movieData)
    
ques  = Questions.objects()
with open('movie_release_year.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()
'''
'''
for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieMusicDirectorQuestions(movieData)
    
ques  = Questions.objects()
with open('movie_music_director.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()
'''


#Director questions
'''
for i in range(len(directorsData)):
    directorData  = directorsData[i]
    generateDirectorMovieQuestions(directorData)
    
ques  = Questions.objects()
with open('director_movie.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

directorsData.rewind()

for i in range(len(producersData)):
    producerData  = producersData[i]
    generateProducerMovieQuestions(producerData)
    
ques  = Questions.objects()
with open('producer_movie.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

producersData.rewind()

for i in range(len(castData)):
    casData  = castData[i]
    generateCastMovieQuestions(casData)

ques  = Questions.objects()
with open('cast_movie.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

castData.rewind()


for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateYearOfReleaseMovieQuestions(movieData)
    
ques  = Questions.objects()
with open('release_year_movie.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()
'''
'''
for i in range(len(musicDirectorsData)):
    musicDirectorData  = musicDirectorsData[i]
    generateMusicDirectorMovieQuestions(musicDirectorData)
    
ques  = Questions.objects()
with open('music_director_movie.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()
musicDirectorsData.rewind()
'''
'''
# Need to change database to OldMoviesData to generate for it
for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieNameQuestions(movieData)

ques  = Questions.objects()
with open('new_movie_name.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()


for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateMovieGenreQuestions(movieData)
    
 
ques  = Questions.objects()
with open('movie_genre.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()


for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateRoleCastQuestions(movieData)
  

ques  = Questions.objects()
with open('role_cast.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()


for i in range(len(moviesData)):
    movieData  = moviesData[i]
    generateCastRoleQuestions(movieData)

ques  = Questions.objects()
with open('cast_role.json', 'w') as outfile:
    json.dump(ques.to_json(), outfile)
ques.delete()

moviesData.rewind()
'''