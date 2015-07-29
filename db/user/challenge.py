'''
Created on Jul 24, 2015

@author: abhinav
'''
from mongoengine import Document , StringField, IntField
import bson

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
    

        
   

            