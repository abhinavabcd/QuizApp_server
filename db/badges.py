'''
Created on Jul 24, 2015

@author: abhinav
'''
import bson
from mongoengine import Document, StringField, DateTimeField, IntField
import HelperFunctions
import datetime


class Badges(Document):
    badgeId = StringField(unique=True)
    name = StringField()
    description = StringField()
    assetPath = StringField()
    condition = StringField()
    type=IntField(default=0)
    modifiedTimestamp = DateTimeField()
    
    meta = {
        'indexes': [
            '-modifiedTimestamp'
            ]
        }
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["modifiedTimestamp"] = HelperFunctions.toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)

    @staticmethod
    def addOrModifyBadge(badgeId=None, name=None, description=None, assetPath=None, condition=None,  type=0, isDirty=1):
        #print badgeId, type , description, assetPath, condition
        badgeId = str(badgeId)
        badge = Badges.objects(badgeId=badgeId)
        
        if(len(badge)>0):
            bdg = badge=badge.get(0)
        else:
            bdg = badge = Badges()
            bdg.badgeId = badgeId

        bdg.type = type
        bdg.name = name
        bdg.description = description
        bdg.assetPath = assetPath
        bdg.condition = condition
        bdg.modifiedTimestamp = datetime.datetime.now()
        bdg.save()
        return True
    
    @staticmethod
    def getNewBadges(userMaxTimestamp):
        return Badges.objects(modifiedTimestamp__gte = userMaxTimestamp)


