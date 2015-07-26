'''
Created on Jul 25, 2015

@author: abhinav
'''
from db.admin.server import SecretKeys
import tornado
from server import constants
from db.user import Users
from server.constants import NOT_AUTHORIZED, NOT_ACTIVATED, secret_auth,\
    ACTIVATED
import json
from server.logging import logger



def userAuthRequired(func):
    def wrapper(response,*args,**kwargs):
        encodedValue = response.get_argument("encodedKey")
        uid = tornado.web.decode_signed_value(constants.secret_auth , "key", encodedValue)
        if(uid):
            pass
        user = Users.getUserByUid(uid)
        if(not user):
            responseFinish(response,{"messageType":NOT_AUTHORIZED})
            return
        kwargs.update({"user":user})
        logger.info("user : "+uid)
        return func(response,*args,**kwargs)
    return wrapper


def serverSecretFunc(func):
    def wrapper(response,*args,**kwargs):
        server_auth_key = response.get_argument("secretKey")
        if(SecretKeys.isSecretKey(server_auth_key)):
            return func(response,*args,**kwargs)
        response.finish({"code":"error"})
        
    return wrapper





def getEncodedKey(response,uid=None, deviceId = None):
    uid = uid if uid else response.get_argument("uid")
    deviceId = deviceId if deviceId else response.get_argument("deviceId")
    user = Users.getUserByUid(uid, False)
    if(user):
        user = user.get(0)
    else:
        return
    if(not user.isActivated or user.deviceId !=deviceId):
        responseFinish(response,{"statusCode":NOT_ACTIVATED,"payload":user.activationKey})#change to not activated 
        return
    
    encodedValue = tornado.web.create_signed_value(secret_auth , "key",uid)
    responseFinish(response,{"statusCode":ACTIVATED,"payload":encodedValue})#change to not activated 





def responseFinish(response,data):
    data = json.dumps(data)
    #logger.info(data)
    response.finish(data) 
