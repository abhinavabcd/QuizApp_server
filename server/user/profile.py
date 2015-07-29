'''
Created on Jul 25, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import OK_UPDATES, OK_USER_INFO, OK_USERS_INFO,\
    OK_CLASH_INFO, OK_QUIZ_GAME_INFO, OK_GAME_EVENTS
from db.user import Users
import datetime
from db.quizzes import Quiz, Categories
from db.badges import Badges
import json
from server.router_server import routerServer
import HelperFunctions
from db.user.games import UserClashHistory, UserGamesHistory




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



@userAuthRequired
def getAllUpdatesV2(response, user=None):
    isLogin = response.get_argument("isLogin",False)
    isFistLogin =  response.get_argument("isFirstLogin",False)
    lastOfflineChallengeIndex = int(response.get_argument("lastOfflineChallengeIndex",0));
    retObj = {"messageType":OK_UPDATES,
                               "payload7":user.toJson(),
                               "payload3":"["+','.join(map(lambda x:x.to_json(),user.getRecentUserFeedV2()))+"]",
                               "payload5":"["+','.join(map(lambda x:x.to_json(),user.getUserChallenges(fromIndex=lastOfflineChallengeIndex)))+"]"   # game events
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


@userAuthRequired
def getUserByUid(response, user=None):
    uid = response.get_argument("uid")
    is_profile_view = response.get_argument("is_profile_view")# need to show some old games too
    user = Users.getUserByUid(uid)
    responseFinish(response, {"messageType":OK_USER_INFO,
                              "payload":user.toJson(),
                            }
     )


'''
to retrieve short info 
'''
@userAuthRequired
def getUsersInfo(response , user=None):
    uidList = json.loads(response.get_argument("uidList"))
    responseFinish(response, {"messageType": OK_USERS_INFO, 
                                "payload": "["+','.join(map(lambda x:Users.getUserByUid(x,long=False).toJsonShort() , uidList))+"]"
                              })



@userAuthRequired
def getUserGameEvents(response, user=None):
    fromIndex = int(response.get_argument("fromIndex",-1))
    responseFinish(response, {"messageType": OK_GAME_EVENTS, 
                              "payload": "["+','.join(map(lambda x:x.to_json() , user.getGameEvents(toIndex=-1)))+"]"
    })

    
# TYPE for requests to getServerDetails