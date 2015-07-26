import AndroidUtils
import urllib
import json
import sys
import random
import datetime
from db.admin.server import GameServer, SecretKeys, Servers
from server.logging import logger
from server import configuration
# 
# LI_N_PEOPLE_WAITING = 0
# LI_USERS_WAITING_SERVERID =1
# LI_LAST_WAITING_UID =2

class RouterServerUtils():
    rrCount = 0#static variables
    servers = {}#static variables
  
#     dbUtils = None
    
    
    def __init__(self):
        self.reloadServers()
        
        secretKey = SecretKeys.objects()[0].secretKey
        for server in self.servers.values():#while starting inform all other local servers to update this map
            try:
                logger.info(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey)
                logger.info(AndroidUtils.get_data(server.addr+"/func?task=reloadServerMap&secretKey="+secretKey).read())
            except:
                logger.error(sys.exc_info()[0])


    def reloadServers(self):# this will reload the map appropirately
        self.servers = {server.serverId : server for server in Servers.objects(group=configuration.serverGroup)}    
    
    def getRandomWebSocketServer(self):
        id = random.choice(self.servers.keys())
        addr = self.servers[id].addr
        return id , addr
    
    def getQuizWebSocketServer(self,quiz, user):
        # move this to db utils
        retries = 0
        gameServer = None
        while(retries<5):
            try:
                gameServer = GameServer.objects(quizId = quiz.quizId)
                if(gameServer):
                    gameServer = gameServer.get(0)
                    
                if(gameServer):
                    # if server is removed or renew server
                    if(not self.servers.get(gameServer.serverId, None) or gameServer.peopleWaiting<=0):
                        gameServer.peopleWaiting = quiz.nPeople*3
                        #wait on a new server from now randomizing so to reduce the load of perticular quiz in round robin fashion
                        gameServer.serverId = self.getRoundRobinServerId()
                        gameServer.lastWaitingUserId = user.uid
                else:
                    gameServer = GameServer()
                    gameServer.quizId = quiz.quizId
                    gameServer.peopleWaiting = quiz.nPeople*3
                    gameServer.serverId =  self.getRoundRobinServerId()
                    gameServer.lastWaitingUserId = user.uid
                    
                gameServer.peopleWaiting-=1
                gameServer.lastUpdatedTimestamp = datetime.datetime.now()
                gameServer.save()
                break
            except:
                retries+=1
            
        return gameServer.serverId , self.servers[gameServer.serverId].addr
    
    
    def waitingUserBotOrCancelled(self, quizId, sid ,uid):#corection
        gameServer = GameServer.objects(quizId = quizId)
        if(gameServer):
            gameServer = gameServer.get(0)
        if(gameServer and gameServer.serverId == sid and gameServer.lastWaitingUserId == uid):
            gameServer.peopleWaiting+=1
            gameServer.save()
            
    def getRoundRobinServerId(self):
        self.rrCount+=1
        self.rrCount%=len(self)
        return self.servers.values()[self.rrCount].serverId








routerServer = RouterServerUtils()
#    m = RouterServerUtils({"master":"192.168.0.1:8084"})