'''
Created on Aug 27, 2014

@author: abhinav2
'''
import tornado
from Constants import *
import HelperFunctions
import json
from Config import SERVER_ID

quizWaitingConnectionsPool = {}#based on type_of quiz we have the waiting pool
runningQuizes = {} # all currently running quizes in this server
def GenerateProgressiveQuizClass(dbUtils, responseFinish , userAuthRequired , addToGcmQueue):
    
    def generateProgressiveQuiz(quizId , quizType, uids):
        quiz = dbUtils.getQuizDetails(quizId)
        if(quizId):
            nQuestions = quiz.nQuestions
        else:
            nQuestions = 7
        
        if quizType==SIMO_USER_TYPE:
            questions = dbUtils.getSIMOQuestions(quiz)
        else:
            questions = dbUtils.getRandomQuestions(quiz)
        id = HelperFunctions.generateKey(10)
        userStates={}
        for i in uids:
            userStates[i]={}
            
        runningQuizes[id] = quizState = {   QUESTIONS: questions,
                                            CURRENT_QUESTION :0,
                                            N_CURRENT_QUESTION_ANSWERED:[],
                                            USERS:userStates,##{uid:something}
                                            CREATED_AT:datetime.datetime.now(),
                                            POINTS:{},
                                            N_CURRENT_REMATCH_REQUEST:set(),
                                            N_CURRENT_USERS_READY:set()
                                        }
        return id , quizState
    
    
    
    
            
    class ProgressiveQuizHandler(tornado.websocket.WebSocketHandler):
        quizPoolWaitId = None   
        uid = None
        quizConnections =None
        runningQuizId= None
        runningQuiz = None
        user = None
        quiz = None
        isChallenge = None
        isChallenged = None
        quizType = None
        
        
        def broadcastToGroup(self, message, allClients):
            for i in allClients:
                if(i!=self):
                    i.write_message(message)
    
        def broadcastToAll(self, message, allClients):
            for i in allClients:
                i.write_message(message)
    
        
        
        @userAuthRequired
        def open(self, user = None):
            #print self.request.arguments
            runningQuizId = self.get_argument("isRunningQuiz",None)
            self.isChallenge = isChallenge = self.get_argument("isChallenge",None)#uid of other user
            self.isChallenged =isChallenged = self.get_argument("isChallenged",None)#uid of the first user
            quizId = self.get_argument("quizId")
            quizType = self.get_argument("quizType")
            
            if(runningQuizId):
                pass
            
            self.quiz = quiz = dbUtils.getQuizDetails(quizId)
            self.quizPoolWaitId =  quizPoolWaitId = "_".join(quiz.tags)+"_"+str(quiz.nPeople)
            self.user = user
            self.uid = user.uid
            if(isChallenge!=None):
                self.quizPoolWaitId = quizPoolWaitId = self.user.uid+"_"+HelperFunctions.generateKey(10)
            elif(isChallenged!=None):
                self.quizPoolWaitId = quizPoolWaitId = isChallenged
                
            quizConnections = quizWaitingConnectionsPool.get(quizPoolWaitId,None)
            if(quizConnections):
                quizConnections.append(self)
            else:
                if(not isChallenged):# not challenge type , so we add insert into new pool
                    quizConnections = quizWaitingConnectionsPool[quizPoolWaitId] = [self]
                else:#is challenged then user have definitely left
                    self.write_message(json.dumps({"messageType":USER_HAS_LEFT_POOL}))
                    return # client should close connection after this
                                        
            self.quizConnections = quizConnections
            #print self.user
            #print self.uid
            #print self.quizConnections
            if(isChallenge!=None):#send notification to other user
                   addToGcmQueue(self.isChallenge, {"fromUser":self.uid,
                                "fromUserName":self.user.name,
                                "quizPoolWaitId":self.quizPoolWaitId,   
                                "serverId":SERVER_ID,
                                "quizId": quiz.quizId,
                                "quizName":quiz.name,
                                "messageType":NOTIFICATION_GCM_CHALLENGE_NOTIFICATION,  
                                "timeStamp":HelperFunctions.toUtcTimestamp(datetime.datetime.now())
                    })

            
            if(len(quizConnections)>=int(quiz.nPeople)):# we have enough people
                self.quizConnections = [quizConnections.pop() for i in range(0, quiz.nPeople)]#nPeople into current quiz
                uids = map(lambda x:x.uid , self.quizConnections)
                _runningQuizId , _runningQuiz = generateProgressiveQuiz(quiz.quizId,quizType, uids)
                for conn in self.quizConnections:
                    conn.runningQuizId = _runningQuizId
                    conn.runningQuiz = _runningQuiz
                    if(conn!=self):
                        conn.quizConnections = self.quizConnections
                #question_one = self.runningQuiz[QUESTIONS][0]
                self.broadcastToAll({"messageType":LOAD_QUESTIONS,
                                                   "payload":self.runningQuizId,
                                                   "payload1":"["+",".join(map(lambda uid:dbUtils.getUserByUid(uid).toJson() , uids))+"]",
                                                   "payload2":"["+",".join(map(lambda x:x.to_json() ,self.runningQuiz[QUESTIONS]))+"]"
                                                  },
                                self.quizConnections
                               )                          
        # the client sent the message
        def on_message(self, message):
            uPayload = userQuizUpdate = json.loads(message)
            messageType = int(userQuizUpdate[MESSAGE_TYPE])
            if(messageType==USER_READY): 
                self.runningQuiz[N_CURRENT_USERS_READY].add(self.uid)
                if(len(self.runningQuiz[N_CURRENT_USERS_READY])>=len(self.quizConnections)):
                    self.broadcastToAll({"messageType":STARTING_QUESTIONS},
                                         self.quizConnections)
                else:
                    self.broadcastToGroup({"messageType":USER_READY, "payload":self.uid},
                                         self.quizConnections)
                    
            
            elif(messageType==USER_ANSWERED_QUESTION):
                questionId = userQuizUpdate[QUESTION_ID]
                userAnswer = userQuizUpdate[USER_ANSWER]
                elapsedTime = userQuizUpdate[ELAPSED_TIME]
                whatUserGot = userQuizUpdate[WHAT_USER_HAS_GOT]
                self.runningQuiz[POINTS][self.uid]=whatUserGot
                self.broadcastToGroup({"messageType":USER_ANSWERED_QUESTION,"payload":message},self.quizConnections)
                #whatUserGot = int(whatUserGot)
                self.runningQuiz[N_CURRENT_QUESTION_ANSWERED].append(self.uid)
                if(len(self.runningQuiz[N_CURRENT_QUESTION_ANSWERED])>=len(self.quizConnections)):#if everyone aswered
                    self.runningQuiz[N_CURRENT_QUESTION_ANSWERED]=[]
                    currentQuestion = self.runningQuiz[CURRENT_QUESTION]
                    self.runningQuiz[CURRENT_QUESTION]=currentQuestion+1# next question
                    #print currentQuestion
                    if(currentQuestion>=self.quiz.nQuestions-1):
                        pointsMap = self.runningQuiz[POINTS]
                        max = 0
                        maxUid = None
                        for uid in pointsMap.keys():
                            if(pointsMap[uid]>max):
                                maxUid = uid
                                max = pointsMap[uid]
                                
                        self.broadcastToAll({"messageType":ANNOUNCING_WINNER,
                                               "payload":json.dumps(self.runningQuiz[USERS]),
                                               "payload1":maxUid #winning user
                                            },
                                         self.quizConnections)
                        #TODO: calculate winner and save in Db
#                         for conn in self.quizConnections:
#                             currentUsersPoints =self.runningQuiz[POINTS]
#                             dbUtils.onUserQuizWonLost( conn.user, conn.quiz.quizId , currentUsersPoints[conn.uid] , currentUsersPoints[conn.uid]==max , currentUsersPoints[conn.uid]<max , currentUsersPoints[conn.uid]==max)
                        return
                    currentQuestionIndex = self.runningQuiz[CURRENT_QUESTION]
                    question = self.runningQuiz[QUESTIONS][currentQuestionIndex]
                    self.broadcastToAll({"messageType":NEXT_QUESTION,
#                                            "payload":question.to_json(),
                                          },
                                     self.quizConnections)
                    
                
            elif(messageType==GET_NEXT_QUESTION):#user explicitly calls this function on if other doesn't responsd
                n_answered = self.runningQuiz[N_CURRENT_QUESTION_ANSWERED]
                isFirstQuestion = False
                if(self.runningQuiz[CURRENT_QUESTION]==0):
                    isFirstQuestion = True
                    
                if(isFirstQuestion or len(n_answered) ==len(self.quizConnections)==self.quiz.nPeople):#if everyone aswered
                    self.runningQuiz[N_CURRENT_QUESTION_ANSWERED]=[]
                    currentQuestionIndex = self.runningQuiz[CURRENT_QUESTION]
                    question = self.runningQuiz[QUESTIONS][currentQuestionIndex]
                    self.broadcastToAll({"messageType":NEXT_QUESTION,
                                           "payload":question.to_json(),
                                          },
                                     self.quizConnections
                                  )
                else:
                    ### can calculate which user caused this error
                    self.broadcastToAll(json.dumps({"messageType":NO_REPLY_FROM_OTHER_USERS}), self.quizConnections)
                    pass
                # client disconnected
            elif(messageType==ACTIVATE_BOT):
                self.write_message(json.dumps({"messageType":OK_ACTIVATING_BOT, "payload1": dbUtils.getBotUser().toJson(), 
                                               "payload2":"["+",".join(map(lambda x:x.to_json() ,dbUtils.getRandomQuestions(self.quiz)))+"]"}))
                #THEN CLIENT CLOSES CONNECTION
            elif(messageType==REMATCH_REQUEST):
                currentRequests = self.runningQuiz[N_CURRENT_REMATCH_REQUEST]
                currentRequests.add(self.uid) 
                if(len(currentRequests)>=self.quiz.nPeople):#every one agreed to rematch
                    self.broadcastToAll(json.dumps({"messageType":OK_START_REMATCH,"payload": dbUtils.getBotUser().toJson(), 
                                               "payload1":"["+",".join(map(lambda x:x.to_json() ,dbUtils.getRandomQuestions(self.quiz)))+"]"}) , self.quizConnections)
                else:
                    self.broadcastToGroup( json.dumps({"messageType":REMATCH_REQUEST,"payload": self.uid }), self.quizConnections)
                    
                    
                
            elif(messageType==START_CHALLENGE_NOW):
                self.write_message(json.dumps({"messageType":OK_CHALLENGE_WITHOUT_OPPONENT ,"payload1": dbUtils.getUserByUid(self.isChallenge).toJson(), 
                                               "payload2":"["+",".join(map(lambda x:x.to_json() ,dbUtils.getRandomQuestions(self.quiz)))+"]",
                                               "payload3":self.quizPoolWaitId
                                              }))
                
                
        def on_close(self):
            #print "Socket CLosed ..."
            try:
                if(self.isChallenge):
                    del quizWaitingConnectionsPool[self.quizPoolWaitId]
            except:
                #print "ERRRRRRR, careful , resolve later"
                pass
            
            self.broadcastToGroup({"messageType":USER_DISCONNECTED,"payload1":self.user.uid},self.quizConnections)
            self.quizConnections.remove(self)#either waiting or something , we don't care
            if(len(self.quizConnections)):
                del runningQuizes[self.runningQuizId]
            super(ProgressiveQuizHandler, self).on_close()

#         def close(self):#?
#             self.on_close()
#             super(ProgressiveQuizHandler, self).close()

        
    return ProgressiveQuizHandler