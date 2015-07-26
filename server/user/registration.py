'''
Created on Jul 25, 2015

@author: abhinav
'''
import json
import tornado
from server.utils import responseFinish
from server.constants import NOT_AUTHORIZED, secret_auth, GPLUS_USER_SAVED,\
    FACEBOOK_USER_SAVED
from db.user import Users
from server.logging import logger



@tornado.web.asynchronous 
def registerWithGoogle(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['googlePlus']
    callback = onRegisterWithGPlusNetwork(response,user)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+userAccessToken,callback) # here we try     

@tornado.web.asynchronous
def registerWithFacebook(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['facebook']
    callback = onRegisterWithFbNetwork(response,user)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://graph.facebook.com/v2.4/me?fields=id,cover,name,email,address,picture,location,gender,birthday,verified,friends&access_token="+userAccessToken,callback) # here we try     


def onRegisterWithGPlusNetwork(response, user):
    def newFunc(httpResponse):
        data = httpResponse.buffer  
        temp =json.loads(data.read())
        if(not temp or temp.get("error",None)):
            responseFinish(response, {"messageType":NOT_AUTHORIZED})
        else:
            try:
                gPlusFriends = user.get('gPlusFriendUids',None) # list of friend uids
                userIp = response.request.remote_ip
                userObject = Users.registerUser( user["name"], 
                                                   user["deviceId"], 
                                                   user["emailId"], 
                                                   user.get("pictureUrl",None),
                                                   user.get("coverUrl",None),
                                                   user.get("birthday",None),
                                                   user.get("gender",None),
                                                   user.get("place",None),
                                                   userIp ,
                                                   user.get("facebook",None),
                                                   user.get("googlePlus",None),
                                                   True,
                                                   gPlusUid = temp["user_id"],
                                                   gPlusFriends = gPlusFriends,
                                                   connectUid = user.get("connectUid",None)
                                                   )
                encodedKey = tornado.web.create_signed_value(secret_auth , "key",userObject.uid)
                responseFinish(response,{"messageType":GPLUS_USER_SAVED , "payload":encodedKey})
            except Exception as ex:
                responseFinish(response, {"messageType":NOT_AUTHORIZED})
    return newFunc


def getByKeyList(d , *keyList):
    for key in keyList:
        if(not d):
            return None
        d= d.get(key,None)
    return d

def onRegisterWithFbNetwork(response, user):
    def newFunc(httpResponse):
        data = httpResponse.buffer  
        temp =json.loads(data.read())
        if(not temp or temp.get("error",None)):
            responseFinish(response, {"messageType":NOT_AUTHORIZED})
            logger.error("error in fetching data")
        else:
            fbFriends = user.get("fbFriendUids",None) or map(lambda friend: friend["id"]  , getByKeyList(temp , "friends","data"))
            try:
                userIp = response.request.remote_ip
                userObject = Users.registerUser( user["name"], 
                                                   user["deviceId"], 
                                                   temp.get("email",None), 
                                                   user.get("pictureUrl",None) or getByKeyList(temp,"picture","data","url"),
                                                   user.get("coverUrl",None) or getByKeyList(temp,"cover","src"),
                                                   user.get("birthday",None),
                                                   user.get("gender",None) or getByKeyList(temp,"gender"),
                                                   user.get("place",None),
                                                   userIp ,
                                                   facebookToken= user.get("facebook",None),
                                                   gPlusToken = user.get("googlePlus",None),
                                                   isActivated = True,
                                                   fbUid = temp["id"],
                                                   fbFriends = fbFriends,
                                                   connectUid = user.get("connectUid",None)
                                               )
                encodedKey = tornado.web.create_signed_value(secret_auth , "key",userObject.uid)
                responseFinish(response,{"messageType":FACEBOOK_USER_SAVED , "payload":encodedKey})
            except:
                responseFinish(response, {"messageType":NOT_AUTHORIZED})
    return newFunc

