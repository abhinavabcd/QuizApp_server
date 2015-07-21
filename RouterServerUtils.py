import AndroidUtils
import urllib
import json
import sys
import random
import datetime
from Db import ServerState, Servers, SecretKeys
import Utils
import Config
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
        
        secretKey = SecretKeys.objects()[0].secretKey
        for server in self.servers.values():#while starting inform all other local servers to update this map
            try:
                Utils.logger.info(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey)
                Utils.logger.info(AndroidUtils.get_data(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey).read())
            except:
                Utils.logger.error(sys.exc_info()[0])


        
    def reloadServers(self):# this will reload the map appropirately
        self.servers = {server.serverId : server for server in Servers.objects(group=Config.serverGroup)}    
    
    def getRandomWebSocketServer(self):
        id = random.choice(self.servers.keys())
        addr = self.servers[id].addr
        return id , addr
    
    def getQuizWebSocketServer(self,quiz, user):
        
        # move this to db utils
        retries = 0
        quizState = None
        while(retries<5):
            try:
                quizState = ServerState.objects(quizId = quiz.quizId)
                if(quizState):
                    quizState = quizState.get(0)
                    
                if(quizState):
                    # if server is removed or renew server
                    if(not self.servers.get(quizState.serverId, None) or quizState.peopleWaiting<=0):
                        quizState.peopleWaiting = quiz.nPeople*3
                        #wait on a new server from now randomizing so to reduce the load of perticular quiz in round robin fashion
                        quizState.serverId = self.getRoundRobinServerId()
                        quizState.lastWaitingUserId = user.uid
                else:
                    quizState = ServerState()
                    quizState.quizId = quiz.quizId
                    quizState.peopleWaiting = quiz.nPeople*3
                    quizState.serverId =  self.getRoundRobinServerId()
                    quizState.lastWaitingUserId = user.uid
                    
                quizState.peopleWaiting-=1
                quizState.lastUpdatedTimestamp = datetime.datetime.now()
                quizState.save()
                break
            except:
                retries+=1
            
        return quizState.serverId , self.servers[quizState.serverId].addr
    
    def waitingUserBotOrCancelled(self, quizId, sid ,uid):#corection
        quizState = ServerState.objects(quizId = quizId)
        if(quizState):
            quizState = quizState.get(0)
        if(quizState and quizState.serverId == sid and quizState.lastWaitingUserId == uid):
            quizState.peopleWaiting+=1
            quizState.save()
            
    
    def getRoundRobinServerId(self):
        self.rrCount+=1
        self.rrCount%=len(self.servers)
        return self.servers.values()[self.rrCount].serverId



if __name__=="__main__":
    pass
#    m = RouterServerUtils({"master":"192.168.0.1:8084"})