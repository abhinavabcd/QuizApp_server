'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import FAILED, OK, OK_CHALLENGES,\
    NOTIFICATION_GCM_OFFLINE_CHALLENGE_NOTIFICATION
from db.user.challenge import OfflineChallenge
import json
from server.gcm_utils import addUidToQueue
from db.quizzes import Quiz


@userAuthRequired
def onOfflineChallengeCompleted(response, user=None):
    offlineChallengeId = response.get_argument("offlineChallengeId")
    challengeData = response.get_argument("challengeData")
    if(OfflineChallenge.onUserCompletedChallenge(user,offlineChallengeId, challengeData)):
        responseFinish(response,{"messageType":OK})
    else:
        responseFinish(response,{"messageType":FAILED})
        
        
        

        
@userAuthRequired
def getOfflineChallengeById(response, user=None):
    offlineChallenge = OfflineChallenge.getOfflineChallengeById(response.get_argument("offlineChallengeId"), user)
    if(offlineChallenge):
        responseFinish(response, {"messageType":OK_CHALLENGES,"payload":offlineChallenge.to_json()})    
        return
    responseFinish(response,{"messageType":FAILED})
    
    
@userAuthRequired
def addOfflineChallenge(response, user=None):
    uid2 = response.get_argument("uid2")
    offlineChallengeId = response.get_argument("offlineChallengeId",None)
    challengeData = response.get_argument("challengeData")
    offlineChallenge = OfflineChallenge.addOfflineChallenge(user, uid2, challengeData, offlineChallengeId);
    if(offlineChallenge):
        challengeData = json.loads(challengeData)
        ## send notification
        addUidToQueue(uid2, {"fromUser":user.uid,
                                "fromUserName":user.name,
                                "quizId":challengeData["quizId"],
                                "payload1":offlineChallenge.offlineChallengeId,
                                "quizName":Quiz.getQuizDetails(challengeData["quizId"]).name,
                                "messageType":NOTIFICATION_GCM_OFFLINE_CHALLENGE_NOTIFICATION
                              })
    responseFinish(response, {"messageType":OK , "payload":offlineChallenge.to_json()})



@userAuthRequired
def getUserChallenges(response, user=None):
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_CHALLENGES, 
                              "payload":"["+','.join(map(lambda x:x.to_json() ,user.getUserChallenges(toIndex, fromIndex) ))+"]",
                           })

