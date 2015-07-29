'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired, responseFinish
from server.constants import OK_SCORE_BOARD,OK_SERVER_DETAILS,\
    OK, GameTypes
import json
from db.quizzes import Quiz
from server.router_server import routerServer


    
@userAuthRequired
def getLeaderboards(response , user = None):
    quizId = response.get_argument("quizId")
    globalList = Quiz.getGlobalLeaderboards(quizId)
    localList  = Quiz.getLocalLeaderboards(quizId, user)
    responseFinish(response, {"messageType":OK_SCORE_BOARD,
                              "payload":json.dumps(globalList),
                              "payload1":json.dumps(localList)
                              })
    
    
    
@userAuthRequired
def activatingBotPQuiz(response, user=None):
    quizId = response.get_argument("quizId")
    sid = response.get_argument("sid")
    routerServer.waitingUserBotOrCancelled(quizId, sid, user.uid)
    responseFinish(response, {"messageType":OK})


@userAuthRequired
def getQuizServer(response, user=None):
    _type = int(response.get_argument("quizType",GameTypes.RANDOM_USER_TYPE))
    if(_type==GameTypes.RANDOM_USER_TYPE): 
        quizId = response.get_argument("quizId")
        quiz = Quiz.getQuizDetails(quizId)
        sid , serverAddr = routerServer.getQuizWebSocketServer(quiz, user)
        responseFinish(response, {"messageType":OK_SERVER_DETAILS,   "payload1": sid , "payload2":serverAddr})
        return
    
    elif(_type==GameTypes.CHALLENGE_QUIZ_TYPE):
        quizId = response.get_argument("quizId")
        quiz = Quiz.getQuizDetails(quizId)
        sid , serverAddr = routerServer.getRandomWebSocketServer()
        responseFinish(response, {"messageType":OK_SERVER_DETAILS,   "payload1": sid , "payload2":serverAddr})
        return