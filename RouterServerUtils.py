import AndroidUtils
import urllib
import json
import sys
import random
from Config import ExternalWebServersMap
from Db import ServerState

# 
# LI_N_PEOPLE_WAITING = 0
# LI_USERS_WAITING_SERVERID =1
# LI_LAST_WAITING_UID =2

class RouterServerUtils():
    rrCount = 0
    webServerMap= {}
    externalWebServerMap = {}
    
    webServerIds=[]
    dbUtils = None
    
    
    def __init__(self,dbUtils , webServerMap, externalServerMap):
        self.dbUtils = dbUtils
        self.updateWebServerMap(webServerMap, externalServerMap)
        for i in webServerMap.values():#while starting inform all other local servers to update this map
            try:
                print AndroidUtils.get_data(i+"/func?task=updateServerMap",urllib.urlencode({"webServerMap":json.dumps(webServerMap) , "externalWebServerMap":json.dumps(ExternalWebServersMap)})).read()
            except:
                print sys.exc_info()[0]
#     def addServer(self, sid , addr):
#         self.webServerMap[sid]=addr
#         self.updateWebServerMap(self.webServerMap)
#     

        
    def updateWebServerMap(self, webServerMap , externalServerMap):
        for i in webServerMap.keys():
                self.webServerMap[i] = webServerMap[i]
                self.externalWebServerMap[i] = externalServerMap[i]
        #ExternalWebServersMap = externalServerMap
        self.webServerIds = webServerMap.keys()
    
    
    def getRandomWebSocketServer(self, isExternal=True):
        id = random.choice(self.webServerIds)
        if(not isExternal):
            addr = self.webServerMap[id]
        else:
            addr = self.externalWebServerMap[id]
        return id , addr
    
    def getQuizWebSocketServer(self,quiz, user , isExternal=True):
        quizState = self.dbUtils.getQuizState(quiz.quizId)
                 
        if(quizState):
            quizState.peopleWaiting-=1
            if(quizState.peopleWaiting<=0):
                quizState.peopleWaiting = quiz.nPeople*3
                quizState.serverId = self.getRoundRobinServerId()
                quizState.lastWaitingUserId = user.uid
        else:
            quizState = ServerState()
            quizState.peopleWaiting = quiz.nPeople*3
            quizState.serverId =  self.getRoundRobinServerId()
            quizState.lastWaitingUserId = user.uid
            
        quizState.save()
                   
        if(not isExternal):
            return quizState.serverId , self.webServerMap[quizState.serverId]
        else:
            return quizState.serverId , self.externalWebServerMap[quizState.serverId]

    
    def waitingUserBotOrCancelled(self, quizId, sid ,uid):#corection
        quizState = self.dbUtils.getQuizState(quizId)
        if(quizState and quizState.serverId == sid and quizState.lastWaitingUserId == uid):
            quizState.peopleWaiting = 0
            quizState.save()
            
    
    def getRoundRobinServerId(self):
        self.rrCount+=1
        self.rrCount%=len(self.webServerIds)
        return self.webServerIds[self.rrCount]



if __name__=="__main__":
    pass
#    m = RouterServerUtils({"master":"192.168.0.1:8084"})