'''
Created on Jul 25, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import OK_UPDATES
from db.user import Users
import datetime
from db.quizzes import Quiz, Categories
from db.badges import Badges
import json
from server.router_server import routerServer
import HelperFunctions




@userAuthRequired
def getAllUpdates(response, user=None):
    isLogin = response.get_argument("isLogin",False)
    isFistLogin =  response.get_argument("isFirstLogin",False)
    lastOfflineChallengeIndex = int(response.get_argument("lastOfflineChallengeIndex",0));
    retObj = {"messageType":OK_UPDATES,
                               "payload7":user.toJson(),
                               "payload3":"["+','.join(map(lambda x:x.to_json(),user.getRecentUserFeed()))+"]",
                               "payload5":"["+','.join(map(lambda x:x.to_json(),user.getUserChallenges(fromIndex=lastOfflineChallengeIndex)))+"]"
                               }
    if(isLogin):
        quizzes = None
        categories= None
        badges = None
        userMaxQuizTimestamp = response.get_argument("maxQuizTimestamp",None)
        if(userMaxQuizTimestamp):
            userMaxQuizTimestamp = datetime.datetime.utcfromtimestamp(float(userMaxQuizTimestamp)+1)
            quizzes = Quiz.getAllQuizzes(userMaxQuizTimestamp)
            categories = Categories.getAllCategories(userMaxQuizTimestamp)
            retObj["payload"]="["+','.join(map(lambda x:x.toJson() , quizzes ))+"]"
            retObj["payload1"] ="["+','.join(map(lambda x:x.toJson() , categories ))+"]"
            
        userMaxBadgesTimestamp = response.get_argument("maxBadgesTimestamp",None)
        if(userMaxBadgesTimestamp):
            userMaxBadgesTimestamp = datetime.datetime.utcfromtimestamp(max(0,float(userMaxBadgesTimestamp)+1))
            badges = Badges.getNewBadges(userMaxBadgesTimestamp)
            retObj["payload2"] = "["+",".join(map(lambda x:x.toJson(),badges))+"]"

        retObj["payload6"]=json.dumps({server.serverId : server.addr for server in routerServer.servers.values()})#id:serveraddr
     
    if(isFistLogin):
        retObj["payload8"]= json.dumps(user.getChatFriends())
    
    
    recentMessages = None
    lastSeenTimestamp = response.get_argument("lastSeenTimestamp",None)
    if(lastSeenTimestamp):
        lastSeenTimestamp = datetime.datetime.utcfromtimestamp(float(lastSeenTimestamp))
        recentMessages = "["+','.join(map(lambda x:x.to_json(),user.getRecentMessagesIfAny(lastSeenTimestamp)))+"]"
        retObj["payload4"] = recentMessages #unseen messages if any
        
    retObj["payload10"] = json.dumps({"serverTime":HelperFunctions.toUtcTimestamp(datetime.datetime.now())})
    responseFinish(response, retObj)
    if(isLogin):
        #every time user logs in lets increment the index
        user.incrementLoginIndex()

# TYPE for requests to getServerDetails