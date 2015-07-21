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
import RouterServerUtils
import logging
import HelperFunctions
import Config 
import ProgressiveQuizHandler
from logging.handlers import TimedRotatingFileHandler
import Utils

dbUtils = None
routerServer = None
logger = None

 
# log start
def create_timed_rotating_log(path):
    """"""
    logger = logging.getLogger("Quizapp time log")
    logger.setLevel(logging.INFO)
 
    handler = TimedRotatingFileHandler(path,
                                       when="H",
                                       interval=1,
                                       backupCount=240)
    logger.addHandler(handler)
    return logger


# log end


pushMessagesBuffer = []
userGcmMessageQueue = []
GCM_BATCH_COUNT = 10
def sendGcmMessages():
    while(len(userGcmMessageQueue)>0):
        uids , packetData = userGcmMessageQueue.pop()
        registrationIds = None
        if(isinstance(uids, list)):
            registrationIds = []
            for uid in uids:
                user = dbUtils.getUserByUid(uid)
                if(user and user.gcmRegId):
                    registrationIds.append(user.gcmRegId)
            if(registrationIds):
                pushMessagesBuffer.append({"registration_ids":registrationIds,"data":packetData })        
        else:
            user =dbUtils.getUserByUid(uids)
            if(user and user.gcmRegId):
                pushMessagesBuffer.append({"registration_ids":[user.gcmRegId],"data":packetData })            
                                          
    c = len(pushMessagesBuffer)
    if(c >0):
        for i in range(min(c , GCM_BATCH_COUNT)):
            data = pushMessagesBuffer.pop()  # { registrationIds:[] , data :{} }
            data = json.dumps(data)
            logger.info("GCM:PUSH:")
            logger.info(data)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch("https://android.googleapis.com/gcm/send", lambda response: logger.info(response), method='POST', headers=Config.GCM_HEADERS, body=data) #Send it off!


#            logger.info(AndroidUtils.get_data('https://android.googleapis.com/gcm/send',post= data,headers = Config.GCM_HEADERS).read()) 
             

def addUidToQueue(uid, packetData):
    userGcmMessageQueue.append([uid,packetData])

def addUidsToQueue(uids, packetData):
    userGcmMessageQueue.append([uids,packetData])


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
        logger.info("user : "+uid)
        return func(response,*args,**kwargs)
    return wrapper

@tornado.web.asynchronous 
def registerWithGoogle(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['googlePlus']
    callback = onRegisterWithGPlusNetwork(response,user)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+userAccessToken,callback) # here we try     

@tornado.web.asynchronous
def registerWithFacebook(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['facebook']
    callback = onRegisterWithFbNetwork(response,user)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://graph.facebook.com/v2.4/me?fields=id,cover,name,email,address,picture,location,gender,birthday,verified,friends&access_token="+userAccessToken,callback) # here we try     


def onRegisterWithGPlusNetwork(response, user):
    def newFunc(httpResponse):
        data = httpResponse.buffer  
        temp =json.loads(data.read())
        if(not temp or temp.get("error",None)):
            responseFinish(response, {"messageType":NOT_AUTHORIZED})
        else:
            try:
                gPlusFriends = user.get('gPlusFriendUids',None) # list of friend uids
                userIp = response.request.remote_ip
                userObject = dbUtils.registerUser( user["name"], 
                                                   user["deviceId"], 
                                                   user["emailId"], 
                                                   user.get("pictureUrl",None),
                                                   user.get("coverUrl",None),
                                                   user.get("birthday",None),
                                                   user.get("gender",None),
                                                   user.get("place",None),
                                                   userIp ,
                                                   user.get("facebook",None),
                                                   user.get("googlePlus",None),
                                                   True,
                                                   gPlusUid = temp["user_id"],
                                                   gPlusFriends = gPlusFriends,
                                                   connectUid = user.get("connectUid",None)
                                                   )
                encodedKey = tornado.web.create_signed_value(secret_auth , "key",userObject.uid)
                responseFinish(response,{"messageType":GPLUS_USER_SAVED , "payload":encodedKey})
            except Exception as ex:
                responseFinish(response, {"messageType":NOT_AUTHORIZED})
    return newFunc


def getByKeyList(d , *keyList):
    for key in keyList:
        if(not d):
            return None
        d= d.get(key,None)
    return d

def onRegisterWithFbNetwork(response, user):
    def newFunc(httpResponse):
        data = httpResponse.buffer  
        temp =json.loads(data.read())
        if(not temp or temp.get("error",None)):
            responseFinish(response, {"messageType":NOT_AUTHORIZED})
            logger.error("error in fetching data")
        else:
            fbFriends = user.get("fbFriendUids",None) or map(lambda friend: friend["id"]  , getByKeyList(temp , "friends","data"))
            try:
                userIp = response.request.remote_ip
                userObject = dbUtils.registerUser( user["name"], 
                                                   user["deviceId"], 
                                                   temp.get("email",None), 
                                                   user.get("pictureUrl",None) or getByKeyList(temp,"picture","data","url"),
                                                   user.get("coverUrl",None) or getByKeyList(temp,"cover","src"),
                                                   user.get("birthday",None),
                                                   user.get("gender",None) or getByKeyList(temp,"gender"),
                                                   user.get("place",None),
                                                   userIp ,
                                                   facebookToken= user.get("facebook",None),
                                                   gPlusToken = user.get("googlePlus",None),
                                                   isActivated = True,
                                                   fbUid = temp["id"],
                                                   fbFriends = fbFriends,
                                                   connectUid = user.get("connectUid",None)
                                               )
                encodedKey = tornado.web.create_signed_value(secret_auth , "key",userObject.uid)
                responseFinish(response,{"messageType":FACEBOOK_USER_SAVED , "payload":encodedKey})
            except:
                responseFinish(response, {"messageType":NOT_AUTHORIZED})
    return newFunc




@userAuthRequired
def getUserByUid(response, user=None):
    uid = response.get_argument("uid")
    user = dbUtils.getUserByUid(uid)
    responseFinish(response, {"messageType":OK_USER_INFO,
                              "payload":user.toJson(),
                            }
                  )
    
@userAuthRequired
def getPreviousMessages(response ,user=None):
    uid2 = response.get_argument("uid2")
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_MESSAGES,
                              "payload":"["+','.join(map(lambda x:x.to_json() ,dbUtils.getMessagesBetween(user.uid, uid2, toIndex,fromIndex)  ))+"]",
                            }
                  )
@userAuthRequired
def subscribeTo(response, user=None):
    uid2 = response.get_argument("uid2")
    dbUtils.addsubscriber(dbUtils.getUserByUid(uid2), user)
    responseFinish(response, {"messageType":OK})

@userAuthRequired
def unSubscribeTo(response, user=None):
    uid2 = response.get_argument("uid2")
    dbUtils.removeSubscriber(dbUtils.getUserByUid(uid2), user)
    responseFinish(response, {"messageType":OK})

@userAuthRequired
def onOfflineChallengeCompleted(response, user=None):
    offlineChallengeId = response.get_argument("offlineChallengeId")
    challengeData = response.get_argument("challengeData")
    if(dbUtils.onUserCompletedChallenge(user,offlineChallengeId, challengeData)):
        responseFinish(response,{"messageType":OK})
    else:
        responseFinish(response,{"messageType":FAILED})
        
@userAuthRequired
def getOfflineChallengeById(response, user=None):
    offlineChallenge = dbUtils.getOfflineChallengeById(response.get_argument("offlineChallengeId"), user)
    if(offlineChallenge):
        responseFinish(response, {"messageType":OK_CHALLENGES,"payload":offlineChallenge.to_json()})    
        return
    responseFinish(response,{"messageType":FAILED})
    
    
@userAuthRequired
def addOfflineChallenge(response, user=None):
    uid2 = response.get_argument("uid2")
    offlineChallengeId = response.get_argument("offlineChallengeId",None)
    challengeData = response.get_argument("challengeData")
    offlineChallenge = dbUtils.addOfflineChallenge(user, uid2, challengeData, offlineChallengeId);
    if(offlineChallenge):
        challengeData = json.loads(challengeData)
        ## send notification
        addUidToQueue(uid2, {"fromUser":user.uid,
                                "fromUserName":user.name,
                                "quizId":challengeData["quizId"],
                                "payload1":offlineChallenge.offlineChallengeId,
                                "quizName":dbUtils.getQuizDetails(challengeData["quizId"]).name,
                                "messageType":NOTIFICATION_GCM_OFFLINE_CHALLENGE_NOTIFICATION 
                              })
    responseFinish(response, {"messageType":OK , "payload":offlineChallenge.to_json()})
    

@userAuthRequired
def loadQuestionsInOrder(response, user=None):
    questionIds = json.loads(response.get_argument("questionIds"))
    questions = dbUtils.getQuestionsById(questionIds)
    responseFinish(response, {"messageType":OK_QUESTIONS, "payload":"["+",".join(map( lambda x:x.to_json(),questions))+"]"})
    
    
@userAuthRequired
def addBadges(response, user=None):
    badgeIds = json.loads(response.get_argument("badgeIds"))
    dbUtils.addBadges(user, badgeIds)
    responseFinish(response, {"messageType":OK})
    

@userAuthRequired
def setStatusMsg(response, user = None):
    msg = response.get_argument("statusMsg")
    user.status = msg[:30]
    user.save()
    responseFinish(response, {"messageType":OK})
        

@userAuthRequired
def addFeedback(response, user=None):
    msg = response.get_argument("feedback")
    dbUtils.addFeedback(user, msg)
    responseFinish(response, {"messageType":OK})
    
    
@userAuthRequired
def getLeaderboards(response , user = None):
    quizId = response.get_argument("quizId")
    globalList = dbUtils.getGlobalLeaderboards(quizId)
    localList  = dbUtils.getLocalLeaderboards(quizId, user)
    responseFinish(response, {"messageType":OK_SCORE_BOARD,
                              "payload":json.dumps(globalList),
                              "payload1":json.dumps(localList)
                              })
    
@userAuthRequired
def sendInboxMessages(response ,user=None):
    toUser = dbUtils.getUserByUid(response.get_argument("toUser"))
    textMessage = response.get_argument("textMessage")
    dbUtils.insertInboxMessage(user, toUser, textMessage)
    addUidToQueue(toUser.uid, {"fromUser":user.uid,
                                "fromUserName":user.name,
                                "textMessage":textMessage,
                                "messageType":NOTIFICATION_GCM_INBOX_MESSAGE 
                                })
    responseFinish(response, {"messageType":OK_SEND_MESSAGE})

@userAuthRequired
def getUsersInfo(response , user=None):
    uidList = json.loads(response.get_argument("uidList"))
    responseFinish(response, {"messageType": OK_USERS_INFO, 
                                "payload": "["+','.join(map(lambda x:dbUtils.getUserByUid(x,long=False).toJsonShort() , uidList))+"]"
                              })


@userAuthRequired
def getPreviousFeed(response, user=None):
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_FEED, 
                              "payload":"["+','.join(map(lambda x:x.to_json() ,dbUtils.getRecentUserFeed(user, toIndex,fromIndex) ))+"]",
                               })
    
@userAuthRequired
def getUserChallenges(response, user=None):
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_CHALLENGES, 
                              "payload":"["+','.join(map(lambda x:x.to_json() ,dbUtils.getUserChallenges(user, toIndex, fromIndex) ))+"]",
                           })

@userAuthRequired
def updateQuizWinStatus(response, user=None):
    quizId = response.get_argument("quizId")
    xpPoints = float(response.get_argument("xpPoints"))
    winStatus = int(response.get_argument("winStatus"))
    uid2 = response.get_argument("uid2")
    userAnswers1 = response.get_argument("userAnswers1",None)
    userAnswers2 = response.get_argument("userAnswers2",None)
    
    dbUtils.updateQuizWinStatus(user , quizId , xpPoints, winStatus , uid2, userAnswers1 , userAnswers2)
    responseFinish(response , {"messageType":OK})
    

def searchByUserName(response, user=None):
    s = response.get_argument("searchQ")
    users = dbUtils.searchByStartsWithUserName(s)
    responseFinish(response, {"messageType":OK,"payload":"["+",".join(map(lambda x:x.toJson(),users))+"]"})
    

@userAuthRequired
def getAllUpdates(response, user=None):
    isLogin = response.get_argument("isLogin",False)
    isFistLogin =  response.get_argument("isFirstLogin",False)
    lastOfflineChallengeIndex = int(response.get_argument("lastOfflineChallengeIndex",0));
    retObj = {"messageType":OK_UPDATES,
                               "payload7":user.toJson(),
                               "payload3":"["+','.join(map(lambda x:x.to_json(),dbUtils.getRecentUserFeed(user)))+"]",
                               "payload5":"["+','.join(map(lambda x:x.to_json(),dbUtils.getUserChallenges(user , fromIndex=lastOfflineChallengeIndex)))+"]"
                               }
    if(isLogin):
        quizzes = None
        categories= None
        badges = None
        userMaxQuizTimestamp = response.get_argument("maxQuizTimestamp",None)
        if(userMaxQuizTimestamp):
            userMaxQuizTimestamp = datetime.datetime.utcfromtimestamp(float(userMaxQuizTimestamp)+1)
            quizzes = dbUtils.getAllQuizzes(userMaxQuizTimestamp)
            categories = dbUtils.getAllCategories(userMaxQuizTimestamp)
            retObj["payload"]="["+','.join(map(lambda x:x.toJson() , quizzes ))+"]"
            retObj["payload1"] ="["+','.join(map(lambda x:x.toJson() , categories ))+"]"
            
        userMaxBadgesTimestamp = response.get_argument("maxBadgesTimestamp",None)
        if(userMaxBadgesTimestamp):
            userMaxBadgesTimestamp = datetime.datetime.utcfromtimestamp(max(0,float(userMaxBadgesTimestamp)+1))
            badges = dbUtils.getNewBadges(userMaxBadgesTimestamp)
            retObj["payload2"] = "["+",".join(map(lambda x:x.toJson(),badges))+"]"

        retObj["payload6"]=json.dumps({server.serverId : server.addr for server in routerServer.servers.values()})#id:serveraddr
     
    if(isFistLogin):
        retObj["payload8"]= json.dumps(dbUtils.getPeopleWithWhomUserConversed(user))
    
    
    recentMessages = None
    lastSeenTimestamp = response.get_argument("lastSeenTimestamp",None)
    if(lastSeenTimestamp):
        lastSeenTimestamp = datetime.datetime.utcfromtimestamp(float(lastSeenTimestamp))
        recentMessages = "["+','.join(map(lambda x:x.to_json(),dbUtils.getRecentMessagesIfAny(user, lastSeenTimestamp)))+"]"
        retObj["payload4"] = recentMessages #unseen messages if any
        
    retObj["payload10"] = json.dumps({"serverTime":HelperFunctions.toUtcTimestamp(datetime.datetime.now())})
    responseFinish(response, retObj)
    if(isLogin):
        #every time user logs in lets increment the index
        dbUtils.incrementLoginIndex(user)

# TYPE for requests to getServerDetails
@userAuthRequired
def getServer(response, user=None):
    _type = int(response.get_argument("quizType",RANDOM_USER_TYPE))
    if(_type==RANDOM_USER_TYPE): 
        quizId = response.get_argument("quizId")
        quiz = dbUtils.getQuizDetails(quizId)
        sid , serverAddr = routerServer.getQuizWebSocketServer(quiz, user)
        responseFinish(response, {"messageType":OK_SERVER_DETAILS,   "payload1": sid , "payload2":serverAddr})
        return
    
    elif(_type==CHALLENGE_QUIZ_TYPE):
        quizId = response.get_argument("quizId")
        quiz = dbUtils.getQuizDetails(quizId)
        sid , serverAddr = routerServer.getRandomWebSocketServer()
        responseFinish(response, {"messageType":OK_SERVER_DETAILS,   "payload1": sid , "payload2":serverAddr})
        return

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


@userAuthRequired
def activatingBotPQuiz(response, user=None):
    quizId = response.get_argument("quizId")
    sid = response.get_argument("sid")
    routerServer.waitingUserBotOrCancelled(quizId, sid, user.uid)
    responseFinish(response, {"messageType":OK})

def responseFinish(response,data):
    data = json.dumps(data)
    #logger.info(data)
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



###################internal functions##############################
def serverSecretFunc(func):
    def wrapper(response,*args,**kwargs):
        server_auth_key = response.get_argument("secretKey")
        if(dbUtils.isSecretKey(server_auth_key)):
            return func(response,*args,**kwargs)
        response.finish({"code":"error"})
        
    return wrapper

    
@serverSecretFunc
def reloadServerMap(response):
    routerServer.reloadServers()
    responseFinish(response, {"code":OK})

@serverSecretFunc
def getAllActiveServers(response):
    responseFinish(response, {"servers": {server.serverId: server.addr for server in routerServer.servers.values()}})


@serverSecretFunc
def resetAllServerMaps(response):
    secretKey = response.get_argument("secretKey")
    ret =""
    servers = dbUtils.getAllServers(Config.serverGroup)
    http_client = tornado.httpclient.AsyncHTTPClient()
            
    for server in servers:#while starting inform all other local servers to update this map
        try:
            ret+="updating .."+server.serverId+"\n"
            ret+=(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey)+"\n"
            http_client.fetch(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey, lambda response: logger.info(response), method='GET') #Send it off!
            ret+="####\n"
        except:
            ret+="Error...\n"
        response.write(ret)
        ret=""

    responseFinish(response, {"code":OK})





@serverSecretFunc
def reloadGcm(response):
    reloadGcmConfig()
    responseFinish(response, {"code":OK})
    
def reloadGcmConfig():
    Config.GCM_API_KEY = dbUtils.config("gcmauth")
    Config.GCM_HEADERS = {'Content-Type':'application/json',
              'Authorization':'key='+Config.GCM_API_KEY
        }
    
    
#sample functionality
serverFunc = {
              "registerWithGoogle":registerWithGoogle,
              "registerWithFacebook":registerWithFacebook,
              "getAllUpdates":getAllUpdates,
              "reloadServerMap":reloadServerMap,
              "getServer":getServer,
              "activatingBotPQuiz":activatingBotPQuiz,
              "getPreviousMessages":getPreviousMessages,
              "sendInboxMessages":sendInboxMessages,
              "getUsersInfo":getUsersInfo,
              "getLeaderboards":getLeaderboards,
              "updateQuizWinStatus":updateQuizWinStatus,
              "getUserByUid":getUserByUid,
              "addBadges":addBadges,
              "searchByUserName":searchByUserName,
              "subscribeTo":subscribeTo,
              "unSubscribeTo":unSubscribeTo,
              "addOfflineChallenge":addOfflineChallenge,
              "setGCMRegistrationId":setGCMRegistrationId,
              "loadQuestionsInOrder":loadQuestionsInOrder,
              "onOfflineChallengeCompleted":onOfflineChallengeCompleted,
              "getOfflineChallengeById":getOfflineChallengeById,
              "setStatusMsg":setStatusMsg,
              "sendFeedback":addFeedback,
              "getAllActiveServers":getAllActiveServers,
              "reloadGcm":reloadGcm,
              "resetAllServerMaps":resetAllServerMaps
              
              
             }

#server web request commands with json
class Func(tornado.web.RequestHandler):
    def get(self,task=None):
        task = task if task!=None else self.get_argument("task",None)
        logger.info(task)
        logger.info(self.request.arguments)
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
            (r"/progressiveQuiz", ProgressiveQuizHandler.GenerateProgressiveQuizClass(dbUtils, responseFinish, userAuthRequired, addUidToQueue )),
            (r"/(.*)", tornado.web.StaticFileHandler,static_path)               
        ]
        tornado.web.Application.__init__(self, handlers, **settings)




def main():
    
    
    global dbUtils
    global routerServer
    global logger
    global HTTP_PORT 



    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="display a square of a given number",
                        type=int, required=True)
    
    parser.add_argument("--isFirstInit", help="display a square of a given number",
                        type=bool)
    
    parser.add_argument("--gcmServerAuth", help="gcm key for push notifications",
                        type=str)
    
    
    parser.add_argument("--serverId", help="serverId",
                        type=str, required=True)
    
    parser.add_argument("--serverAddr", help="external ip address ",
                        type=str , required=True)
    
    parser.add_argument("--serverGroup", help="unique to identify group , like main , development-1 etc",
                        type=str)
    
    args = parser.parse_args()
    

    Config.serverGroup = args.serverGroup if args.serverGroup else Config.serverGroup
    Config.serverId = args.serverId
        
    Utils.logger = logger = create_timed_rotating_log('quizapp_logs/quizapp'+"_"+Config.serverId+'.log')
        
    
    
    
    logger.info("PROCESS_PID: "+str(os.getpid()))
    logger.info("initializing dbUtils..")
    Utils.dbUtils  = dbUtils = Db.DbUtils(Config.dbServer)#initialize Db
    
#     if(not args.serverAddr.endswith(str(args.port))):
#         print "Serveradd should end with port, continue only if you have configured domain-name:port to your serving host"
    if(not args.serverAddr.startswith("http")):
        print "Serveraddr should shart with http or https"
        return
    
    dbUtils.updateServerMap({Config.serverId: args.serverAddr }, Config.serverGroup)
    ##generate a random key and send an email to help manage
    dbUtils.addSecretKey(HelperFunctions.generateKey(10))
        
    logger.info("initialing router utilities")
    Utils.routerServer = routerServer = RouterServerUtils.RouterServerUtils(dbUtils)
    HTTP_PORT = args.port
    if(args.isFirstInit):
        from CreateBots import createBots
        bots = createBots(dbUtils, Db.UserWinsLosses)
        logger.info("creating bots..")
        print bots
        dbUtils.loadBotUids()
        
        if(not args.gcmServerAuth):
            print "You must supply a  gcm key on first init"
            return
        
    if(args.gcmServerAuth):
        dbUtils.config("gcmauth",args.gcmServerAuth)
    
    
    reloadGcmConfig()
            
    

    http_server = tornado.httpserver.HTTPServer(QuizApp())
    http_server.listen(HTTP_PORT)
    ## this should be moved to seperate queuing service
    tornado.ioloop.PeriodicCallback(sendGcmMessages, 2000).start()
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    main()
    
    #testCases