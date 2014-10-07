import AndroidUtils
import urllib
import json
import sys
import random
from Config import ExternalWebServersMap

ss = {}  #server state


LI_N_PEOPLE_WAITING = 0
LI_USERS_WAITING_SERVERID =1
LI_LAST_WAITING_UID =2
class MasterServerUtils():
    rrCount = 0
    webServerMap= {}
    webServerIds=[]
    def __init__(self,webServerMap, externalServerMap):
        self.updateWebServerMap(webServerMap, externalServerMap)
        for i in webServerMap.values():#while starting inform all other local servers to update this map
            try:
                print AndroidUtils.get_data(i+"/func?task=updateServerMap",urllib.urlencode({"webServerMap":json.dumps(webServerMap) , "externalWebServerMap":json.dumps(ExternalWebServersMap)})).read()
            except:
                print sys.exc_info()[0]
    def addServer(self, sid , addr):
        self.webServerMap[sid]=addr
        self.updateWebServerMap(self.webServerMap)
    
    def removeServer(self, sid):
        del self.webServerMap[sid]
        if(sid=="master"):#fail safe 
            master = min(self.webServerMap.keys())
            self.webServerMap["master"]  =self.webServerMap[master]
        self.updateWebServerMap(self.webServerMap)
    
        
    def updateWebServerMap(self, webServerMap , externalServerMap):
        for i in webServerMap.keys():
                self.webServerMap[i] = webServerMap[i]
        ExternalWebServersMap = externalServerMap
        self.webServerIds = webServerMap.keys()
    
    
    def getRandomWebSocketServer(self):
        id = random.choice(self.webServerIds)
        addr = self.webServerMap[id]
        return id , addr
    
    def getQuizWebSocketServer(self,quiz, user):
        quizState = ss.get(quiz.quizId,None)
        if(quizState):
            quizState[LI_N_PEOPLE_WAITING]-=1
            if(quizState[LI_N_PEOPLE_WAITING]<=0):
                ss[quiz.quizId]= quizState = [quiz.nPeople*3 , self.getRoundRobinServerId(),None]
        else:
            ss[quiz.quizId]= quizState = [quiz.nPeople*3 , self.getRoundRobinServerId(),None]
        
        quizState[LI_LAST_WAITING_UID] = user.uid
        return quizState[LI_USERS_WAITING_SERVERID] , self.webServerMap[quizState[LI_USERS_WAITING_SERVERID]]
    
    def waitingUserBotOrCancelled(self, quizId, sid ,uid):#corection
        quizState = ss.get(quizId,None)
        if(quizState and quizState[LI_USERS_WAITING_SERVERID]== sid and quizState[LI_LAST_WAITING_UID]== uid):
            ss[quizId]=None
    
    def getRoundRobinServerId(self):
        self.rrCount+=1
        self.rrCount%=len(self.webServerIds)
        return self.webServerIds[self.rrCount]



if __name__=="__main__":
    m = MasterServerUtils({"master":"192.168.0.1:8084"})