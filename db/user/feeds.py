from mongoengine import Document, StringField , ReferenceField , IntField, DateTimeField
from mongoengine.fields import DateTimeField
from db.user import Users
import HelperFunctions
import datetime

    
class Feed(Document):
    fromUid = StringField()
    type = IntField(default = 0)
    message = StringField()
    message2= StringField()
    timestamp = DateTimeField()
    

class UserFeed(Document):
    uidFeedIndex = StringField()#uid_LOGININDEX
    feedMessage = ReferenceField(Feed)
    
    @staticmethod
    def getRecentUserFeed(user, toIndex=-1, fromIndex=0):
        ind = toIndex if toIndex>0 else user.userFeedIndex.index
        cnt =50
        userFeedMessages = []
        while(ind>fromIndex):
            for i in UserFeed.objects(uidFeedIndex = user.uid+"_"+str(ind)):
                userFeedMessages.append(i.feedMessage)#getting from reference field
                cnt-=1
            if(cnt<=0):
                break
            ind-=1
        return userFeedMessages
    

    
    @staticmethod
    def publishFeedToUser(fromUser ,  toUser, _type, message, message2):
        f = Feed()
        f.fromUid = fromUser.uid
        f.type = _type
        f.message = message
        if(message2!=None):
            f.message2 = message2
        f.timestamp = HelperFunctions.toUtcTimestamp(datetime.datetime.now())
        f.save()
        
        userFeed = UserFeed()
        userFeed.uidFeedIndex= toUser.uid+"_"+str(toUser.userFeedIndex.getAndIncrement(toUser).index)
        userFeed.feedMessage = f
        userFeed.save()
                
    