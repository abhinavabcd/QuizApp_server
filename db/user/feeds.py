from mongoengine import Document, StringField , ReferenceField , IntField, DateTimeField
import datetime
import HelperFunctions
from db.user import GameEvent


    

class UserFeedV2(Document):# second version of feed , 
    uidFeedIndex  = StringField()#uid_LOGININDEX
    gameEvent = ReferenceField(GameEvent)
    
#     @staticmethod
#     def publishFeedToUser(fromUid ,  user, _type, message, message2):
# #         f = Feed()
# #         f.fromUid = fromUid
# #         f.type = _type
# #         f.message = message
# #         if(message2!=None):
# #             f.message2 = message2
# #         f.timestamp = HelperFunctions.toUtcTimestamp(datetime.datetime.now())
# #         f.save()
# #         
#         userFeed = UserFeed()
#         userFeed.uidFeedIndex= user.uid+"_"+str(user.userFeedIndex.getAndIncrement(user).index)
#         userFeed.gameEvent = f
#         userFeed.save()

class UserFeed(Document):
    uidFeedIndex = StringField()#uid_LOGININDEX
    feedMessage = ReferenceField('Feed')