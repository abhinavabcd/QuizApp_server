'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
import json
from db.badges import Badges
from server.constants import OK



    
@userAuthRequired
def addBadges(response, user=None):
    badgeIds = json.loads(response.get_argument("badgeIds"))
    user.addBadges(badgeIds)
    responseFinish(response, {"messageType":OK})
    

@userAuthRequired
def setStatusMsg(response, user = None):
    msg = response.get_argument("statusMsg")
    user.status = msg[:30]
    user.save()
    responseFinish(response, {"messageType":OK})
        