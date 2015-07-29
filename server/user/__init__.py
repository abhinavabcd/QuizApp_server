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
def addFeedback(response, user=None):
    msg = response.get_argument("feedback")
    user.addFeedback(msg)
    responseFinish(response, {"messageType":OK})


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





