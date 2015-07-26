'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.utils import userAuthRequired
from server.constants import OK



@userAuthRequired
def updateQuizWinStatus(response, user=None):
    quizId = response.get_argument("quizId")
    xpPoints = float(response.get_argument("xpPoints"))
    winStatus = int(response.get_argument("winStatus"))
    uid2 = response.get_argument("uid2")
    userAnswers1 = response.get_argument("userAnswers1",None)
    userAnswers2 = response.get_argument("userAnswers2",None)
    
    user.updateQuizWinStatus( quizId , xpPoints, winStatus , uid2, userAnswers1 , userAnswers2)
    responseFinish(response , {"messageType":OK})