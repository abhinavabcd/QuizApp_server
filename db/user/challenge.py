'''
Created on Jul 24, 2015

@author: abhinav
'''
from mongoengine import Document , StringField, EmailField, BooleanField, FloatField , ListField , DateTimeField , IntField , ReferenceField
import bson
from db.user import Users
import HelperFunctions
import json
from Constants import WHAT_USER_HAS_GOT, FEED_CHALLENGE
from db.user.feeds import UserFeed
from db.user.games import UserGamesHistory

class OfflineChallenge(Document):
    offlineChallengeId = StringField(unique=True)
    fromUid_userChallengeIndex = StringField()
    toUid_userChallengeIndex = StringField()
    challengeType = IntField(default=0)
    challengeData = StringField()  # {quizId:asdasd ,userAnswers:[], questions:[]}
    challengeData2 = StringField()
    wonUid = StringField()
    meta = {
            'indexes':['toUid_userChallengeIndex']
            }
    def toJson(self):
        sonObj = self.to_mongo()
        if(self.offlineChallengeId == None):
            sonObj["offlineChallengeId"] = self._id
        del sonObj["_id"]
        return bson.json_util.dumps(sonObj)
        
    @staticmethod
    def getOfflineChallengeById(offlineChallengeId, user):
        
        offlineChallenge =  OfflineChallenge.objects(offlineChallengeId=offlineChallengeId).get(0)
        if(user.uid in offlineChallenge.fromUid_userChallengeIndex or user.uid in offlineChallenge.toUid_userChallengeIndex):
            return offlineChallenge
        return None
    
    @staticmethod
    def addOfflineChallenge(fromUser, toUid , challengeData, offlineChallengeId=None):
        toUser = Users.getUserByUid(toUid)
        
        offlineChallenge = OfflineChallenge()
        if(offlineChallengeId!=None):
            offlineChallenge.offlineChallengeId = offlineChallengeId
        else:
            offlineChallenge.offlineChallengeId = HelperFunctions.generateKey(10)
        offlineChallenge.fromUid_userChallengeIndex = fromUser.uid+"_"+str(fromUser.userChallengesIndex.index) # yeah , its a little bit funny too # fuck you , i was not funny , that was over optimization for an unreleased app !!!
        offlineChallenge.toUid_userChallengeIndex = toUid+"_"+str(toUser.userChallengesIndex.getAndIncrement(toUser).index)
        offlineChallenge.challengeData = challengeData
        offlineChallenge.save()
        return offlineChallenge
        
    @staticmethod
    def onUserCompletedChallenge(user ,challengeId,challengeData2):
        offlineChallenge = OfflineChallenge.objects(offlineChallengeId=challengeId).get(0)
        offlineChallenge.challengeData2 = challengeData2
        fromUser = Users.getUserByUid(offlineChallenge.fromUid_userChallengeIndex.split("_")[0])
        
        if(offlineChallenge.challengeType==0):
            try:
                challengeData1= json.loads(offlineChallenge.challengeData)
                challengeData2= json.loads(offlineChallenge.challengeData2)
                quizId = challengeData1["quizId"]
                a = challengeData1["userAnswers"][-1][WHAT_USER_HAS_GOT]
                b = challengeData2["userAnswers"][-1][WHAT_USER_HAS_GOT]
                won , lost , tie = 0, 0, 0 
                winStatus = -2
                if(a==b):
                    offlineChallenge.whoWon = ""
                    winStatus  = 0
                    won , lost,tie = 0 ,0 ,1
                elif(a>b):
                    offlineChallenge.whoWon = offlineChallenge.fromUid_userChallengeIndex
                    won , lost , tie = 0 ,1 ,0 
                    winStatus = -1
                else:
                    offlineChallenge.whoWon = offlineChallenge.toUid_userChallengeIndex
                    won , lost ,tie = 1 , 0 ,0
                    winStatus = 1
                
                
                offlineChallenge.save()
                UserGamesHistory.updateQuizWinStatus(user, quizId, a+20*won, winStatus,fromUser.uid, None, None)
                UserFeed.publishFeedToUser(user, fromUser, FEED_CHALLENGE, challengeId , None )
                UserGamesHistory.updateQuizWinStatus(fromUser, quizId, b+20*lost, -winStatus, user.uid , None, None)
                return True
            except:
                return False
        return True
    def getUserChallenges(self, user , toIndex =-1 , fromIndex = 0):
        limit =20
        if(fromIndex!=0):
            limit = 1000000
        index = toIndex
        if(toIndex==-1):
            index = user.userChallengesIndex.index
        userChallenges = []
        count =0
        while(index>fromIndex):
            for i in OfflineChallenge.objects(toUid_userChallengeIndex = user.uid+"_"+str(index)):
                userChallenges.append(i)#getting from reference field
                count+=1
            if(count>limit):
                break
            index-=1
        return userChallenges

            