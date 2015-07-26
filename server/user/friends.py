'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from db.user import Users
from server.constants import OK



@userAuthRequired
def subscribeTo(response, user=None):
    uid2 = response.get_argument("uid2")
    user.addsubscriber(Users.getUserByUid(uid2), user)
    responseFinish(response, {"messageType":OK})
    
    
@userAuthRequired
def unSubscribeTo(response, user=None):
    uid2 = response.get_argument("uid2")
    user.removeSubscriber(Users.getUserByUid(uid2), user)
    responseFinish(response, {"messageType":OK})