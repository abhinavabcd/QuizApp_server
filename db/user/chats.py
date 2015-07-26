from mongoengine import Document , StringField, EmailField, BooleanField, FloatField , ListField , DateTimeField , IntField , ReferenceField
import HelperFunctions
from utils import reorderUids , reorder , Uid1Uid2Index
import datetime 
import bson


class UserChatMessages(Document):
    fromUid_toUid_index = StringField()  # tag to identify block of messages
    fromUid = StringField()
    toUid = StringField()
    message = StringField()
    timestamp = DateTimeField()
    fromUid_LoginIndex = StringField()  # uid1_LOGININDEX
    toUid_LoginIndex = StringField()  # uid2_LOGININDEX
    meta = {
        'indexes': [
               ('toUid_LoginIndex', '-timestamp'),
               'fromUid_toUid_index'
            ]
            }
    def to_json(self):
        son = self.to_mongo()
        del son["fromUid_LoginIndex"]
        del son["toUid_LoginIndex"]
        son["timestamp"] = HelperFunctions.toUtcTimestamp(self.timestamp)
        return bson.json_util.dumps(son)
        


    @staticmethod
    def insertChat(fromUser, toUser , message):
        chatMessage = UserChatMessages()
        chatMessage.fromUid = fromUser.uid
        chatMessage.toUid = toUser.uid
        chatMessage.message = message
        chatMessage.timestamp = datetime.datetime.now()
        chatMessage.fromUid_LoginIndex = fromUser.uid + "_" + str(fromUser.loginIndex)
        chatMessage.toUid_LoginIndex = toUser.uid + "_" + str(toUser.loginIndex)
        user1 , user2 = reorder(fromUser, toUser)
        # experimental only
        chatMessage.fromUid_toUid_index = user1.uid + "_" + user2.uid + "_" + str(Uid1Uid2Index.getAndIncrementIndex(fromUser, toUser))
        chatMessage.save()
        # if user is logged in , send him some notification
        
        # experimental only

        
    @staticmethod
    def getMessagesBetween(uid1, uid2 , toIndex=-1, fromIndex=0):
        uid1 , uid2 = reorderUids(uid1, uid2)
        if(toIndex == -1):
            r = Uid1Uid2Index.objects(uid1_uid2=uid1 + "_" + uid2)
            if(not r):
                return []
            r = r.get(0)
            toIndex = r.index
        messages = []
        i = toIndex + 1
        count = 0 
        while(i > fromIndex):
            tag = uid1 + "_" + uid2 + "_" + str(i)
            for message in UserChatMessages.objects(fromUid_toUid_index=tag):
                messages.append(message)
                count += 1
            i -= 1
            if(count > 20):
                break 
            
        return messages
    



