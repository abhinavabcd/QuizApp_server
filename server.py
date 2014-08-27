import os
import random
import string
from tornado.httpclient import HTTPRequest
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options, parse_command_line
import tornado.options
import tornado.web
from tornado import websocket

import json
from Constants import *
import Db
import AndroidUtils
import MasterServerUtils
import logging
import HelperFunctions
import Config 
import ProgressiveQuizHandler

dbUtils = Db.DbUtils()#initialize Db
masterSever = MasterServerUtils.MasterServerUtils(Config.WebServersMap)

logging.basicConfig(filename='log',level=logging.INFO)



gcmQueue = []
phoneNumberQueue = []
GCM_BATCH_COUNT = 10
def sendGcmMessages():
    while(len(phoneNumberQueue)>0):
        uids , packetData = phoneNumberQueue.pop()
        registrationIds = None
        if(isinstance(uids, list)):
            registrationIds = []
            for uid in uids:
                user = dbUtils.getUserByUid(uid)
                if(user and user.gcmRegId):
                    registrationIds.append(user.gcmRegId)
            if(registrationIds):
                addGcmToQueue(registrationIds, packetData)            
        else:
            user =dbUtils.getUserByUid(uid)
            if(user and user.gcmRegId):
                addGcmToQueue([user.gcmRegId], packetData)            
                                          
    c = len(gcmQueue)
    if(c >0):
        for i in range(min(c , GCM_BATCH_COUNT)):
            data = gcmQueue.pop()  # { registrationIds:[] , data :{} }
            data = json.dumps(data)
            logging.info("GCM:PUSH:")
            logging.info(data)
            logging.info(AndroidUtils.get_data('https://android.googleapis.com/gcm/send',post= data,headers = GCM_HEADERS).read()) 
             
def addGcmToQueue(registrationIds, packetData):
    gcmQueue.append({"registration_ids":registrationIds,"data":packetData })

def addUidToQueue(uid, packetData):
    phoneNumberQueue.append([uid,packetData])

def addUidsToQueue(uids, packetData):
    phoneNumberQueue.append([uids,packetData])


_userCache= {}

def userAuthRequired(func):
    def wrapper(response,*args,**kwargs):
        encodedValue = response.get_argument("encodedKey")
        uid = tornado.web.decode_signed_value(secret_auth , "key", encodedValue)
        if(uid):
            pass
        user = dbUtils.getUserByUid(uid)
        if(not user):
            responseFinish(response,{"messageType":NOT_AUTHORIZED})
            return
        kwargs.update({"user":user})
        return func(response,*args,**kwargs)
    return wrapper

@tornado.web.asynchronous 
def registerWithGoogle(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['googlePlus']
    callback = onRegisterWithSocialNetwork(response,user,GPLUS_USER_SAVED)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+userAccessToken,callback) # here we try     

@tornado.web.asynchronous
def registerWithFacebook(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['facebook']
    callback = onRegisterWithSocialNetwork(response,user,GPLUS_USER_SAVED)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://graph.facebook.com/me?access_token="+userAccessToken,callback) # here we try     

def onRegisterWithSocialNetwork(response, user, responseCode = FACEBOOK_USER_SAVED):
    def newFunc(httpResponse):
        data = httpResponse.buffer  
        temp =json.loads(data.read())
        if(not temp or temp.get("error",None)):
            responseFinish(response, {"messageType":NOT_AUTHORIZED})
        else:
            try:
                userIp = response.request.remote_ip
                userObject = dbUtils.registerUser( user["name"], user["deviceId"], user["emailId"], user.get("pictureUrl",None),user.get("coverUrl",None),user.get("birthday",None),user.get("gender",None),user.get("place",None),userIp , user.get("facebook",None),user.get("googlePlus",None),True)
                encodedKey = tornado.web.create_signed_value(secret_auth , "key",userObject.uid)
                responseFinish(response,{"messageType":responseCode , "payload":encodedKey})
            except:
                responseFinish(response, {"messageType":NOT_AUTHORIZED})
    return newFunc


@userAuthRequired
def getPreviousMessages(response ,user=None):
    uid2 = dbUtils.getUserByUid(response.get_argument("uid2"))
    toIndex = int(response.get_argument("toIndex",-1))
    responseFinish(response, {"messageTye":OK_PREVIOUS_MESSAGES,
                              "payload":"["+','.join(map(lambda x:x.to_json() ,dbUtils.getMessagesBetween(user.uid, uid2, toIndex)  ))+"]",
                               })
    
@userAuthRequired
def getPreviousFeed(response, user=None):
    toIndex = int(response.get_argument("toIndex",-1))
    responseFinish(response, {"messageTye":OK_PREVIOUS_FEED, 
                              "payload":"["+','.join(map(lambda x:x.to_json() ,dbUtils.getRecentUserFeed(user, toIndex) ))+"]",
                               })
    
@userAuthRequired
def getPreviousChallenges(response, user=None):
    
    

@userAuthRequired
def getAllUpdates(response, user=None):
    userMaxTimestamp = datetime.datetime.utcfromtimestamp(float(response.get_argument("maxQuizTimestamp")))
    
    lastSeenTimestamp = response.get_argument("lastSeenTimestamp",None)
    payload3 = None
    if(lastSeenTimestamp):
        lastSeenTimestamp = datetime.datetime.utcfromtimestamp(float(lastSeenTimestamp))
        payload3 = "["+','.join(map(lambda x:x.toJson(),dbUtils.getRecentMessagesIfAny(user, lastSeenTimestamp)))+"]"
        
    quizzes = dbUtils.getAllQuizzes(userMaxTimestamp)
    categories = dbUtils.getAllCategories(userMaxTimestamp)
    
    responseFinish(response, {"messageType":OK_UPDATES,
                              "payload":"["+','.join(map(lambda x:x.toJson() , quizzes ))+"]",
                               "payload1":"["+','.join(map(lambda x:x.toJson() , categories ))+"]",
                               "payload2":"["+','.join(map(lambda x:x.to_json(),dbUtils.getRecentUserFeed(user)))+"]",
                               "payload3":payload3 #unseen messages if any
#                               "payload4":dbUtils.getRecentChallenges()
                              }
                   )
    dbUtils.incrementLoginIndex(user)
# TYPE for requests to getServerDetails
@userAuthRequired
def getServerDetails(response, quizId,user=None):
    type = int(response.get_argument("type",0))
    if(type==PROGRESSIVE_QUIZ): 
        quiz = dbUtils.getQuizDetails(quizId)
        responseFinish(response, {"messageType":OK_SERVER_DETAILS,   "payload1":masterSever.getQuizWebSocketServer(quiz, user) })
        return

def addWebServer(response):
    serveraddr = response.get_argument("serveraddr")
    sid = response.get_argument("sid")
    masterSever.addServer(sid, serveraddr)
    
def removeWebServer(response):
    sid = response.get_argument("sid")
    masterSever.removeServer(sid)
    
def updateWebServerMap(response):
    webServerMap  = json.loads(response.get_argument("webServerMap"))
    masterSever.updateWebServerMap(webServerMap)


@userAuthRequired
def getQuestionById(response, user=None):
    qId = response.get_argument("qId",None)
    question = dbUtils.getQuestionById(qId)
    if(question):
        response.finish({"messageType":OK_QUESTION , "payload1":question.to_json()})
    else:
        response.finish({"messageType": NOT_FOUND})

@userAuthRequired
def getUserInfo(response, user =None):
    responseFinish(response,{"messageType": OK_USER_INFO, "payload":dbUtils.getUserInfo(user).to_json()})

def responseFinish(response,data):
    data = json.dumps(data)
    logging.info(data)
    print data
    response.finish(data) 

@userAuthRequired
def setGCMRegistrationId(response, user=None):
    regId = response.get_argument("regId")
    dbUtils.setUserGCMRegistationId(user, regId)
    responseFinish(response,{"messageType":REG_SAVED })


def reloadConfiguration(response):
    pass
    

def getEncodedKey(response,uid=None, deviceId = None):
    uid = uid if uid else response.get_argument("uid")
    deviceId = deviceId if deviceId else response.get_argument("deviceId")
    user = dbUtils.getUserById(uid)
    if(user):
        user = user.get(0)
    else:
        return
    if(not user.isActivated or user.deviceId !=deviceId):
        responseFinish(response,{"statusCode":NOT_ACTIVATED,"payload":user.activationKey})#change to not activated 
        return
    
    encodedValue = tornado.web.create_signed_value(secret_auth , "key",uid)
    responseFinish(response,{"statusCode":ACTIVATED,"payload":encodedValue})#change to not activated 

@userAuthRequired
def initAppConfig(response , user=None):
    responseFinish(response,{"messageType":OK, "payload1":json.dumps({"serverTime":HelperFunctions.toUtcTimestamp(datetime.datetime.now())})})

@userAuthRequired
def updateUserRating(response , user=None):
    user.rating = float(response.get_argument("rating",0))
    user.save()
    responseFinish(response,{"messageType":RATING_OK})
    return


#sample functionality
serverFunc = {
              "registerWithGoogle":registerWithGoogle,
              "registerWithFacebook":registerWithFacebook,
              "getAllUpdates":getAllUpdates
             }

#server web request commands with json
class Func(tornado.web.RequestHandler):
    def get(self,task=None):
        task = task if task!=None else self.get_argument("task",None)
        logging.info(task)
        logging.info(self.request.arguments)
        print self.request.arguments
        func = serverFunc.get(task,None)
        if(func):
            func(self)
            return
        self.send_error(404)
        
        
    def post(self,*args,**kwargs):
        return self.get(*args,**kwargs)

#create a mongo class that is a test document that is same as the Test class in testSampleGson project java file
class QuizApp(tornado.web.Application):
    def __init__(self):
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "html/"),
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            autoescape=None,
        )
        static_path = dict(path=settings['static_path'], default_filename='index.html')
           
        handlers = [                    
            (r"/func", Func),
            (r"/pQuiz", ProgressiveQuizHandler.GenerateProgressiveQuizClass(dbUtils, responseFinish, userAuthRequired)),
            (r"/(.*)", tornado.web.StaticFileHandler,static_path)               
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(QuizApp())
    http_server.listen(HTTP_PORT)
    tornado.ioloop.PeriodicCallback(sendGcmMessages, 2000).start()
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    main()

    #testCases





