'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import OK_FEED



@userAuthRequired
def getPreviousFeed(response, user=None):
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_FEED, 
                              "payload":"["+','.join(map(lambda x:x.to_json() ,user.getRecentUserFeed(toIndex,fromIndex) ))+"]",
                               })
    
    
@userAuthRequired
def getFeedV2(response, user=None):
    toIndex = int(response.get_argument("toIndex",-1))
    fromIndex = int(response.get_argument("fromIndex",0))
    
    responseFinish(response, {"messageType":OK_FEED, 
                              "payload":"["+','.join(map(lambda x:x.to_json() ,user.getRecentUserFeedV2(toIndex,fromIndex) ))+"]",
                               })
    