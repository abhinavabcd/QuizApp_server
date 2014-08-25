import yajl as json
import os
import random
import string
from tornado.httpclient import HTTPRequest
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options, parse_command_line
import tornado.options
import tornado.web

from Config import *
from db import  *
from androidUtils import *


import logging
from tornado import websocket
logging.basicConfig(filename='log',level=logging.INFO)




def generateKey(N=8):
    ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N))


gcmQueue = []
phoneNumberQueue = []
GCM_BATCH_COUNT = 10
def sendGcmMessages():
    while(len(phoneNumberQueue)>0):
        phNumbers , packetData = phoneNumberQueue.pop()
        registrationIds = None
        if(isinstance(phNumbers, list)):
            registrationIds = []
            for phNumber in phNumbers:
                user =Users.getUserByPhoneNumber(phNumber)
                if(user and user.gcmRegId):
                    registrationIds.append(user.gcmRegId)
            if(registrationIds):
                addGcmToQueue(registrationIds, packetData)            
        else:
            user =Users.getUserByPhoneNumber(phNumbers)
            if(user and user.gcmRegId):
                addGcmToQueue([user.gcmRegId], packetData)            
                                          
    c = len(gcmQueue)
    if(c >0):
        for i in range(min(c , GCM_BATCH_COUNT)):
            data = gcmQueue.pop()  # { registrationIds:[] , data :{} }
            data = json.dumps(data)
            logging.info("GCM:PUSH:")
            logging.info(data)
            logging.info(get_data('https://android.googleapis.com/gcm/send',post= data,headers = GCM_HEADERS).read()) 
            
def addGcmToQueue(registrationIds, packetData):
    gcmQueue.append({"registration_ids":registrationIds,"data":packetData })

def addPhoneNumberToQueue(phoneNumber, packetData):
    phoneNumberQueue.append([phoneNumber,packetData])

def addPhoneNumbersToQueue(phoneNumbers, packetData):
    phoneNumberQueue.append([phoneNumbers,packetData])

        
def userAuthRequired(func):
    def wrapper(response,*args,**kwargs):
        encodedValue = response.get_argument("encodedKey")
        uid = tornado.web.decode_signed_value(secret_auth , "key", encodedValue)
        if(uid):
            pass
        user = Users.objects(uid=uid)
        if(not user):
            responseFinish(response,{"messageType":NOT_AUTHORIZED})
            return
        user = user.get(0)
        kwargs.update({"user":user})
        return func(response,*args,**kwargs)
    return wrapper

@tornado.web.asynchronous 
def registerWithGoogle(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['googlePlus']
    callback = onRegisterWithSocialNetwork(response,user,GPLUS_USER_SAVED)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="+userAccessToken,callback) # here we try     

@tornado.web.asynchronous
def registerWithFacebook(response):
    user = json.loads(response.get_argument("userJson"))
    userAccessToken = user['facebook']
    callback = onRegisterWithSocialNetwork(response,user,GPLUS_USER_SAVED)
    http_client = tornado.httpclient.AsyncHTTPClient() # we initialize our http client instance
    http_client.fetch("https://graph.facebook.com/me?access_token="+userAccessToken,callback) # here we try     

def onRegisterWithSocialNetwork(response, user, responseCode = FACEBOOK_USER_SAVED):
    def newFunc(httpResponse):
        data = httpResponse.buffer  
        temp =json.loads(data.read())
        if(not temp or temp.get("error",None)):
            responseFinish(response, {"messageType":NOT_AUTHORIZED})
        else:
            try:
                userIp = response.request.remote_ip
                userObject = dbUtils.registerUser(user.get("uid",generateKey(9)), user["name"], user["deviceId"], user["emailId"], user.get("pictureUrl",None),user.get("coverUrl",None),user.get("birthday",None),user.get("gender",None),user.get("place",None),userIp , user.get("facebook",None),user.get("googlePlus",None),True)
                encodedKey = tornado.web.create_signed_value(secret_auth , "key",userObject.uid)
                responseFinish(response,{"messageType":responseCode , "payload":encodedKey})
            except:
                responseFinish(response, {"messageType":NOT_AUTHORIZED})
    return newFunc

@userAuthRequired
def getAllUpdates(response, user=None):
    userMaxTimeStamp = datetime.datetime.utcfromtimestamp(float(response.get_argument("maxQuizTimestamp")))
    quizzes = dbUtils.getAllQuizzes(userMaxTimeStamp)
    categories = dbUtils.getAllCategories(userMaxTimeStamp)
    user.loginIndex+=1
    user.save()
    responseFinish(response, {"messageType":OK_UPDATES,
                              "payload":"["+','.join(map(lambda x:x.toJson() , quizzes ))+"]" ,
                               "payload1":"["+','.join(map(lambda x:x.toJson() , categories ))+"]",
#                                "payload2":"",
#                                "payload3":"",
#                                "payload4":""
                              })
    

@userAuthRequired
def getUserDetails(response, user=None):
    uid = response.get_argument("uid")
    user = Users.objects(uid = uid)
    try:
        user = user.get(0)
        responseFinish(response, {"messageType":OK_DETAILS,"payload":user.to_json()}) 
    except:
        responseFinish(response, {"messageType":NOT_FOUND})
    
    
@userAuthRequired
def getServerAddress(response, quizId,user=None):
    #round robin routes appropriately , this appears in our main loadbalancer/main server
    responseFinish(response, {"messageType":OK_SERVER_DETAILS,"payload1":"127.0.0.1:8084"})

@userAuthRequired
def getQuestionById(response, user=None):
    qId = response.get_argument("qId",None)
    question = dbUtils.getQuestionById(qId)
    if(question):
        response.finish({"messageType":OK_QUESTION , "payload1":question.to_json()})
    else:
        response.finish({"messageType": NOT_FOUND})

@userAuthRequired
def getUserInfo(response, user =None):
    responseFinish(response,{"messageType": OK_USER_INFO, "payload":dbUtils.getUserInfo(user).to_json()})

def responseFinish(response,data):
    data = json.dumps(data)
    logging.info(data)
    print data
    response.finish(data) 

@userAuthRequired
def setGCMRegistrationId(response, user=None):
    regId = response.get_argument("regId")
    dbUtils.setUserGCMRegistationId(user, regId)
    responseFinish(response,{"messageType":REG_SAVED })


def reloadConfiguration(response):
    pass
    

def getEncodedKey(response,uid=None, deviceId = None):
    uid = uid if uid else response.get_argument("uid")
    deviceId = deviceId if deviceId else response.get_argument("deviceId")
    user = Users.objects(uid=uid)
    if(user):
        user = user.get(0)
    else:
        return
    if(not user.isActivated or user.deviceId !=deviceId):
        responseFinish(response,{"statusCode":NOT_ACTIVATED,"payload":user.activationKey})#change to not activated 
        return
    
    encodedValue = tornado.web.create_signed_value(secret_auth , "key",uid)
    responseFinish(response,{"statusCode":ACTIVATED,"payload":encodedValue})#change to not activated 

@userAuthRequired
def initAppConfig(response , user=None):
    responseFinish(response,{"messageType":OK, "payload1":json.dumps({"serverTime":toUtcTimestamp(datetime.datetime.now())})})

@userAuthRequired
def updateUserRating(response , user=None):
    user.rating = float(response.get_argument("rating",0))
    user.save()
    responseFinish(response,{"messageType":RATING_OK})
    return



quizWaitingConnectionsPool = {}#based on type_of quiz we have the waiting pool
runningQuizes = {} # all currently running quizes in this server

def generateProgressiveQuiz(quizId , uids):
    quiz = dbUtils.getQuizDetails(quizId).get(0)
    if(quizId):
        n_questions = quiz.n_questions
    else:
        n_questions = 7
    
    questions = dbUtils.getRandomQuestions(quiz)
    id = generateKey(10)
    userStates={}
    for i in uids:
        userStates[i]={}
        
    runningQuizes[id] = quizState = {   QUESTIONS: questions,
                                        CURRENT_QUESTION :-1,
                                        N_CURRENT_QUESTION_ANSWERED:[],
                                        USERS:userStates##{uid:something}
                                    }
    return id , quizState



def broadcastToGroup(client , message, allClients):
    for i in allClients:
        if(i!=client):
            client.write_message(message)

def broadcastToAll(client , message, allClients):
    for i in allClients:
        client.write_message(message)

        
class ProgressiveQuizHandler(websocket.WebSocketHandler):
    quizPoolWaitId = None   
    uid = None
    quizConnections =None
    runningQuizId= None
    runningQuiz = None
    @userAuthRequired
    def open(self,quizId , user = None):
        runningQuizId = self.get_argument("isRunningQuiz",None)
        if(runningQuizId):
            pass
        
        quiz = dbUtils.getQuizDetails(quizId)
        self.quizPoolWaitId =  quizPoolWaitId = "_".join(quiz.tags)+"_"+quiz.n_people
        self.user = user
        quizConnections = quizWaitingConnectionsPool.get(quizPoolWaitId,None)
        if(quizConnections):
            quizConnections.append(self)
        else:
            quizWaitingConnectionsPool[quizPoolWaitId] = [self]
        
        self.quizConnections = quizConnections
        if(len(quizConnections)>=int(quiz.n_people)):# we have enough people
            self.quizConnections = [quizConnections.pop() for i in range(0, quiz.n_people)]#n_people into current quiz
            uids = map(lambda x:x.user.to_short_json() , quizConnections)
            self.runningQuizId , self.runningQuiz = generateProgressiveQuiz(quiz, uids)
            #question_one = self.runningQuiz[QUESTIONS][0]
            broadcastToAll(self,{"messageType":STARTING_QUESTIONS,
                                               "payload":self.runningQuizId,
                                               "payload1":uids
                                              },
                            quizConnections
                           )
    # the client sent the message
    def on_message(self, message):
        userQuizUpdate = json.loads(message)
        messageType = userQuizUpdate[MESSAGE_TYPE]
        if(messageType==USER_ANSWERED_QUESTION):
            questionId = userQuizUpdate[QUESTION_ID]
            userAnswer = userQuizUpdate[USER_ANSWER]
            whatUserGot = userQuizUpdate[WHAT_USER_HAS_GOT]
            broadcastToAll(self,{"messageType":USER_ANSWERED_QUESTION,"payload":whatUserGot,"payload1":questionId},self.quizConnections)
            self.runningQuiz[N_CURRENT_QUESTION_ANSWERED].append(self.uid)
            if(len(self.runningQuiz[N_CURRENT_QUESTION_ANSWERED])==len(self.quizConnections)):#if everyone aswered
                self.runningQuiz[N_CURRENT_QUESTION_ANSWERED]=[]
                currentQuestion = self.runningQuiz[CURRENT_QUESTION]
                self.runningQuiz[CURRENT_QUESTION]=currentQuestion+1
                if(currentQuestion>=self.quiz.n_questions):
                    broadcastToAll(self,{"messageType":ANNOUNCING_WINNER,
                                           "payload":json.dumps(self.runningQuiz[USERS])
                                        },
                                     self.quizConnections)
                    #TODO: calculate winner and save in db
                    return
                currentQuestionIndex = self.runningQuiz[CURRENT_QUESTION]
                question = self.runningQuiz[QUESTIONS][currentQuestionIndex]
                broadcastToAll(self,{"messageType":NEXT_QUESTION,
                                       "payload":question.to_json(),
                                      },
                                 self.quizConnections)
            
        elif(messageType==GET_NEXT_QUESTION):#user explicitly calls this function on if other doesn't responsd
            n_answered =self.runningQuiz[N_CURRENT_QUESTION_ANSWERED]
            isFirstQuestion = False
            if(self.runningQuiz[CURRENT_QUESTION]==-1):
                isFirstQuestion = True
                self.runningQuiz[CURRENT_QUESTION]==0
                
            if(isFirstQuestion or len(n_answered) ==len(self.quizConnections)):#if everyone aswered
                self.runningQuiz[N_CURRENT_QUESTION_ANSWERED]=[]
                currentQuestionIndex = self.runningQuiz[CURRENT_QUESTION]
                question = self.runningQuiz[QUESTIONS][currentQuestionIndex]
                broadcastToAll(self,{"messageType":NEXT_QUESTION,
                                       "payload":question.to_json(),
                                      },
                                 self.quizConnections
                              )
            else:
                #some state to clean TODO
                pass
            # client disconnected
    def on_close(self):
        broadcastToGroup(self,{"messageType":USER_DISCONNECTED,"payload1":self.user.uid},self.quizConnections)
        self.quizConnections.remove(self.quizConnections.index(self))#either waiting or something , we don't care
        if(len(self.quizConnections)):
            del runningQuizes[self.runningQuizId]

#sample functionality
serverFunc = {
              "registerWithGoogle":registerWithGoogle,
              "registerWithFacebook":registerWithFacebook,
              "getAllUpdates":getAllUpdates
             }

#server web request commands with json
class Func(tornado.web.RequestHandler):
    def get(self,task=None):
        task = task if task!=None else self.get_argument("task",None)
        logging.info(task)
        logging.info(self.request.arguments)
        print self.request.arguments
        func = serverFunc.get(task,None)
        if(func):
            func(self)
            return
        self.send_error(404)
        
        
    def post(self,*args,**kwargs):
        return self.get(*args,**kwargs)

#create a mongo class that is a test document that is same as the Test class in testSampleGson project java file
class QuizApp(tornado.web.Application):
    def __init__(self):
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "html/"),
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            autoescape=None,
        )
        static_path = dict(path=settings['static_path'], default_filename='index.html')
           
        handlers = [                    
            (r"/func", Func),    
            (r"/(.*)", tornado.web.StaticFileHandler,static_path)               
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(QuizApp())
    http_server.listen(HTTP_PORT)
    tornado.ioloop.PeriodicCallback(sendGcmMessages, 2000).start()
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    main()

    #testCases





