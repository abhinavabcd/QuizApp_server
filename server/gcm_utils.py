'''
Created on Jul 25, 2015

@author: abhinav
'''
from server.utils import responseFinish, serverSecretFunc, userAuthRequired
import server
from db.admin.server import Configs
from server import configuration
from server.constants import OK, REG_SAVED
from db.user import Users
import json
from server.logging import logger
import tornado




pushMessagesBuffer = []
userGcmMessageQueue = []
GCM_BATCH_COUNT = 10

@serverSecretFunc
def reloadGcm(response):
    reloadGcmConfig()
    responseFinish(response, {"code":OK})
    
def reloadGcmConfig():
    configuration.GCM_API_KEY = Configs.getKey("gcmauth")
    configuration.GCM_HEADERS = {'Content-Type':'application/json',
              'Authorization':'key='+configuration.GCM_API_KEY
        }
    
    


def sendGcmMessages():
    while(len(userGcmMessageQueue)>0):
        uids , packetData = userGcmMessageQueue.pop()
        registrationIds = None
        if(isinstance(uids, list)):
            registrationIds = []
            for uid in uids:
                user = Users.getUserByUid(uid)
                if(user and user.gcmRegId):
                    registrationIds.append(user.gcmRegId)
            if(registrationIds):
                pushMessagesBuffer.append({"registration_ids":registrationIds,"data":packetData })        
        else:
            user =Users.getUserByUid(uids)
            if(user and user.gcmRegId):
                pushMessagesBuffer.append({"registration_ids":[user.gcmRegId],"data":packetData })            
                                          
    c = len(pushMessagesBuffer)
    if(c >0):
        for i in range(min(c , GCM_BATCH_COUNT)):
            data = pushMessagesBuffer.pop()  # { registrationIds:[] , data :{} }
            data = json.dumps(data)
            logger.info("GCM:PUSH:")
            logger.info(data)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch("https://android.googleapis.com/gcm/send", lambda response: logger.info(response), method='POST', headers=configuration.GCM_HEADERS, body=data) #Send it off!


#            logger.info(AndroidUtils.get_data('https://android.googleapis.com/gcm/send',post= data,headers = Config.GCM_HEADERS).read()) 
             

def addUidToQueue(uid, packetData):
    userGcmMessageQueue.append([uid,packetData])

def addUidsToQueue(uids, packetData):
    userGcmMessageQueue.append([uids,packetData])















