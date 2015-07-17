import AndroidUtils
import urllib
import json
import sys
import random
from Db import ServerState, Servers, SecretKeys

# 
# LI_N_PEOPLE_WAITING = 0
# LI_USERS_WAITING_SERVERID =1
# LI_LAST_WAITING_UID =2

class RouterServerUtils():
    rrCount = 0
    servers = {}
    
    dbUtils = None
    
    
    def __init__(self,dbUtils):
        self.dbUtils = dbUtils
        self.reloadServers()
        
        secretKey = SecretKeys.objects()[0]
        for server in self.servers.values():#while starting inform all other local servers to update this map
            try:
                print server.ip+"/func?task=reloadServerMap&secretKey="+secretKey
                print AndroidUtils.get_data(server.ip+"/func?task=reloadServerMap&secretKey="+secretKey).read()
            except:
                print sys.exc_info()[0]


        
    def reloadServers(self):# this will reload the map appropirately
        self.servers = {server.serverId : server for server in Servers.objects()}    
    
    def getRandomWebSocketServer(self):
        id = random.choice(self.servers.keys())
        addr = self.servers[id].ip
        return id , addr
    
    def getQuizWebSocketServer(self,quiz, user):
        
        # move this to db utils
        quizState = ServerState.objects(quizId = quiz.quizId)
        if(quizState):
            quizState = quizState.get(0)
            
        if(quizState):
            quizState.peopleWaiting-=1
            if(quizState.peopleWaiting<=0):
                quizState.peopleWaiting = quiz.nPeople*3
                #wait on a new server from now randomizing so to reduce the load of perticular quiz in round robin fashion
                quizState.serverId = self.getRoundRobinServerId()
                quizState.lastWaitingUserId = user.uid
        else:
            quizState = ServerState()
            quizState.peopleWaiting = quiz.nPeople*3
            quizState.serverId =  self.getRoundRobinServerId()
            quizState.lastWaitingUserId = user.uid
            
        quizState.save()
                   
        return quizState.serverId , self.servers[quizState.serverId].ip

    
    def waitingUserBotOrCancelled(self, quizId, sid ,uid):#corection
        quizState = self.dbUtils.getQuizState(quizId)
        if(quizState and quizState.serverId == sid and quizState.lastWaitingUserId == uid):
            quizState.peopleWaiting = 0
            quizState.save()
            
    
    def getRoundRobinServerId(self):
        self.rrCount+=1
        self.rrCount%=len(self.servers)
        return self.servers.values()[self.rrCount]



if __name__=="__main__":
    pass
#    m = RouterServerUtils({"master":"192.168.0.1:8084"})