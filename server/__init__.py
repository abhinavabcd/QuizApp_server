import tornado
import os
from server.logging import logger
from server import configuration
import argparse
from db.admin.server import Servers, SecretKeys, BotUids, Configs
import db
import HelperFunctions
from server.router_server import routerServer
from db.create_bots import createBots
from server.gcm_utils import reloadGcmConfig, sendGcmMessages
from server.progressive_quiz_handler import ProgressiveQuizHandler
from server.user.registration import registerWithGoogle, registerWithFacebook
from server.user.profile import getAllUpdates, getAllUpdatesV2,\
    getUserGameEvents
from server.user.chats import getChatMessages, sendChatMessages
from server.admin import reloadServerMap, getAllActiveServers,\
    resetAllServerMaps
from server.quiz import getQuizServer, activatingBotPQuiz, getLeaderboards
from server.user import getUsersInfo, getUserByUid, searchByUserName,\
    setGCMRegistrationId, addFeedback
from server.user.games import updateQuizWinStatus, getUserGameById,\
    getUserClashStats, getUserClashGames
from server.user.badges import addBadges, setStatusMsg
from server.user.friends import subscribeTo, unSubscribeTo
from server.user.challenges import addOfflineChallenge,\
    onOfflineChallengeCompleted, getOfflineChallengeById
from server.questions import loadQuestionsInOrder
from server.user.feed import getPreviousFeed, getFeedV2

#sample functionality
serverFunc = {
              "getServer":getQuizServer,#old code
              "getPreviousMessages":getChatMessages, # old 
              "sendInboxMessages":sendChatMessages, # old
              
               #new code
              "registerWithGoogle":registerWithGoogle,
              "registerWithFacebook":registerWithFacebook,
              "getAllUpdates":getAllUpdates,  #old
              "getAllUpdatesV2":getAllUpdatesV2,              
              
              
              "setGCMRegistrationId":setGCMRegistrationId,
              "addBadges":addBadges,
              "searchByUserName":searchByUserName,
              "setStatusMsg":setStatusMsg,
              
              "getQuizServer":getQuizServer,
              "activatingBotPQuiz":activatingBotPQuiz,
              "addOfflineChallenge":addOfflineChallenge,
              "onOfflineChallengeCompleted":onOfflineChallengeCompleted,
              "getOfflineChallengeById":getOfflineChallengeById,
              "updateQuizWinStatus":updateQuizWinStatus,
              "loadQuestionsInOrder":loadQuestionsInOrder,
              "getLeaderboards":getLeaderboards,              
              ##v2
              "getUserGameById":getUserGameById,
              "getUserClashStats":getUserClashStats,
              "getUserClashGames":getUserClashGames,
              
              
              
              "getUserByUid":getUserByUid,
              "getUsersInfo":getUsersInfo,
              "subscribeTo":subscribeTo,
              "unSubscribeTo":unSubscribeTo,
              
              "getChatMessages":getChatMessages,            
              "sendChatMessages":sendChatMessages,
              #v2
              "getfeed": getFeedV2,# given feed index
              "getUserGameEvents": getUserGameEvents,  # order by time stamp and gameEvent index
              
              "reloadServerMap":reloadServerMap,
              "sendFeedback":addFeedback,
              "getAllActiveServers":getAllActiveServers,
              "reloadGcm":reloadGcmConfig,
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
            (r"/progressiveQuiz", ProgressiveQuizHandler),
            (r"/(.*)", tornado.web.StaticFileHandler,static_path)               
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

def start_server():
    
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
    

    configuration.serverGroup = args.serverGroup if args.serverGroup else configuration.serverGroup
    configuration.serverId = args.serverId
    
    logger.info("PROCESS_PID: "+str(os.getpid()))
    logger.info("initializing dbUtils..")
    
    ######initialize db
    db.init() ## do this before any calls
    
#     if(not args.serverAddr.endswith(str(args.port))):
#         print "Serveradd should end with port, continue only if you have configured domain-name:port to your serving host"
    if(not args.serverAddr.startswith("http")):
        print "Serveraddr should shart with http or https"
        return
    
    if(Servers.isServerIdExists(configuration.serverId, configuration.serverGroup)):
        print "there is already a server entry with the same serverId %s in this group %s clear , if there is no such such server running you can continue"% (configuration.serverId, configuration.serverGroup)
        if(raw_input("y/n : ").lower()=="n"):
            return
    
    Servers.updateServerMap({configuration.serverId: args.serverAddr }, configuration.serverGroup)
    ##generate a random key and send an email to help manage
    SecretKeys.addSecretKey(HelperFunctions.generateKey(10))
        
    logger.info("initialing router utilities")
    HTTP_PORT = args.port
    if(args.isFirstInit):
        bots = createBots()
        BotUids.loadBotUids()
        
        if(not args.gcmServerAuth):
            print "You must supply a  gcm key on first init"
            return
        
    if(args.gcmServerAuth):
        Configs.setkey("gcmauth",args.gcmServerAuth)
    
    
    reloadGcmConfig()
            
    

    http_server = tornado.httpserver.HTTPServer(QuizApp())
    http_server.listen(HTTP_PORT)
    ## this should be moved to seperate queuing service
    tornado.ioloop.PeriodicCallback(sendGcmMessages, 2000).start()
    tornado.ioloop.IOLoop.instance().start()
    