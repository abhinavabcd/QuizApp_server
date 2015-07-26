'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import OK_MESSAGES, NOTIFICATION_GCM_INBOX_MESSAGE,\
    OK_SEND_MESSAGE
from db.user.chats import UserChatMessages
from db.user import Users
from server.gcm_utils import addUidToQueue

@userAuthRequired
def getChatMessages(response ,user=None):
    uid2 = response.get_argument("uid2")
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_MESSAGES,
                              "payload":"["+','.join(map(lambda x:x.to_json() ,UserChatMessages.getMessagesBetween(user.uid, uid2, toIndex,fromIndex)  ))+"]",
                            }
                  )
    

    
@userAuthRequired
def sendChatMessages(response ,user=None):
    toUser = Users.getUserByUid(response.get_argument("toUser"))
    textMessage = response.get_argument("textMessage")
    UserChatMessages.insertChat(user, toUser, textMessage)
    addUidToQueue(toUser.uid, {"fromUser":user.uid,
                                "fromUserName":user.name,
                                "textMessage":textMessage,
                                "messageType":NOTIFICATION_GCM_INBOX_MESSAGE 
                                })
    responseFinish(response, {"messageType":OK_SEND_MESSAGE})