from mongoengine import Document, StringField , ReferenceField , IntField, DateTimeField
import datetime
import HelperFunctions

    
class GameEvent(Document):
    fromUid = StringField()
    type = IntField(default = 0)
    message = StringField()
    message2= StringField()
    message3 = StringField()
    timestamp = DateTimeField()
    
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.timestamp = datetime.datetime.now()
    

class UserFeed(Document):
    uidFeedIndex = StringField()#uid_LOGININDEX
    feedMessage = ReferenceField(GameEvent)
    
    @staticmethod
    def publishFeedToUser(fromUid ,  user, _type, message, message2):
        f = Feed()
        f.fromUid = fromUid
        f.type = _type
        f.message = message
        if(message2!=None):
            f.message2 = message2
        f.timestamp = HelperFunctions.toUtcTimestamp(datetime.datetime.now())
        f.save()
        
        userFeed = UserFeed()
        userFeed.uidFeedIndex= user.uid+"_"+str(user.userFeedIndex.getAndIncrement(user).index)
        userFeed.feedMessage = f
        userFeed.save()