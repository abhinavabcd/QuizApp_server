'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import OK, OK_CLASH_INFO, OK_CLASH_GAMES,\
    OK_QUIZ_GAME_INFO
from db.user.games import UserGamesHistory
import json



@userAuthRequired
def updateQuizWinStatus(response, user=None):
    quizId = response.get_argument("quizId")
    xpPoints = float(response.get_argument("xpPoints"))
    relativeXpGain = float(response.get_argument("relativeXpGain",0))
    winStatus = int(response.get_argument("winStatus"))
    uid2 = response.get_argument("uid2")
    userAnswers1 = response.get_argument("userAnswers1",None)
    userAnswers2 = response.get_argument("userAnswers2",None)
    #### unsecure , do some mechanism to secure this like a one time cookie in db , so user has to do it from the app itself
    user.updateQuizWinStatus( quizId , xpPoints, relativeXpGain, winStatus , uid2, userAnswers1 , userAnswers2)
    responseFinish(response , {"messageType":OK})
    
    
@userAuthRequired
def getUserClashStats(response , user=None):
    uid2 = response.get_argument("uid")
    quizId = response.get_argument("quizId",None)
    
    responseFinish(response, {"messageType":OK_CLASH_INFO,
                              "payload" : json.dumps(UserGamesHistory.getWinsLossesBetweenUsers(user.uid, uid2, quizId=None)),
                              "payload2" : "["+','.join(map(lambda x:x.to_json(isLong=False) , UserGamesHistory.getGamesBetweenUsers(user.uid, uid2, quizId, fromIndex=0)))+"]"
                            }
    )
    

@userAuthRequired
def getUserGameById(response, user=None):
    id = response.get_argument("gameId")
    responseFinish(response, {"messageType":OK_QUIZ_GAME_INFO,
                              "payload": UserGamesHistory.objects.get(id=id).to_json(isLong=True)
                            }
    )
    
    

@userAuthRequired
def getUserClashGames(response, user=None):
    uid2 = response.get_argument("uid")
    quizId = response.get_argument("quizId",None)
    fromIndex = int(response.get_argument("from_index",0))
    responseFinish(response, {"messageType":OK_CLASH_GAMES,
                              "payload2" : json.dumps([ x for x in UserGamesHistory.getGamesBetweenUsers(user.uid, uid2, quizId, fromIndex=0 , short=True).to_json(isLong=False)])
                            }
                  )