'''
Created on Jul 26, 2015

@author: abhinav
'''
from server.constants import OK_QUESTIONS, OK_QUESTION, NOT_FOUND
from server.utils import userAuthRequired, responseFinish
import json
from db.questions import Questions




@userAuthRequired
def loadQuestionsInOrder(response, user=None):
    questionIds = json.loads(response.get_argument("questionIds"))
    questions = Questions.getQuestionsById(questionIds)
    responseFinish(response, {"messageType":OK_QUESTIONS, "payload":"["+",".join(map( lambda x:x.to_json(),questions))+"]"})
    
    


@userAuthRequired
def getQuestionById(response, user=None):
    qId = response.get_argument("qId",None)
    questions = Questions.getQuestionsById([qId])
    if(questions):
        question = questions.get()
        response.finish({"messageType":OK_QUESTION , "payload1":question.to_json()})
    else:
        response.finish({"messageType": NOT_FOUND})
