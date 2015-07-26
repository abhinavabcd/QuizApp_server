'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from db.user import Users
from server.constants import OK_USER_INFO, OK, OK_USERS_INFO, REG_SAVED
from db.admin.server import Feedback
import json


@userAuthRequired
def getUserByUid(response, user=None):
    uid = response.get_argument("uid")
    user = Users.getUserByUid(uid)
    responseFinish(response, {"messageType":OK_USER_INFO,
                              "payload":user.toJson(),
                            }
                  )


@userAuthRequired
def addFeedback(response, user=None):
    msg = response.get_argument("feedback")
    user.addFeedback(msg)
    responseFinish(response, {"messageType":OK})



'''
to retrieve short info 
'''
@userAuthRequired
def getUsersInfo(response , user=None):
    uidList = json.loads(response.get_argument("uidList"))
    responseFinish(response, {"messageType": OK_USERS_INFO, 
                                "payload": "["+','.join(map(lambda x:Users.getUserByUid(x,long=False).toJsonShort() , uidList))+"]"
                              })



@userAuthRequired
def getUserInfo(response, user =None):
    responseFinish(response,{"messageType": OK_USER_INFO, "payload":user.to_json()})

    

def searchByUserName(response, user=None):
    s = response.get_argument("searchQ")
    users = Users.searchByStartsWithUserName(s)
    responseFinish(response, {"messageType":OK,"payload":"["+",".join(map(lambda x:x.toJson(),users))+"]"})





@userAuthRequired
def setGCMRegistrationId(response, user=None):
    regId = response.get_argument("regId")
    user.setUserGCMRegistationId(regId)
    responseFinish(response,{"messageType":REG_SAVED })





