'''
Created on Jul 25, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import RATING_OK, OK
import json
import HelperFunctions
import datetime


@userAuthRequired
def initAppConfig(response , user=None):
    responseFinish(response,{"messageType":OK, "payload1":json.dumps({"serverTime":HelperFunctions.toUtcTimestamp(datetime.datetime.now())})})

@userAuthRequired
def updateUserRating(response , user=None):
    user.rating = float(response.get_argument("rating",0))
    user.save()
    responseFinish(response,{"messageType":RATING_OK})
    return
