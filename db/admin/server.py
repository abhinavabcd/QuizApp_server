from mongoengine import Document , StringField , DateTimeField, IntField, ReferenceField
from db.user import Users
import random

class Configs(Document):
    key = StringField(unique=True)
    value = StringField()
    
    @staticmethod
    def getKey(key , defValue=None):
        config = Configs.objects(key=key)
        if(not config):
            return defValue
        else:
            config = config.get(0)
            return config.value
    
    @staticmethod  
    def setkey(key , value):
        config = Configs.objects(key=key)
        if(not config):
            config = Configs()
            config.key = key
            config.value = value
            config.save()
        else:
            config = config.get(0)
            config.value = value
            config.save()
        
        return config.value


class SecretKeys(Document):
    secretKey = StringField(unique=True)
   
    @staticmethod
    def isSecretKey(secretKey):
        return SecretKeys.objects(secretKey=secretKey) != None
    @staticmethod
    def addSecretKey(secretKey):
        try:
            s = SecretKeys()
            s.secretKey = secretKey
            s.save()
        except:
            pass
        
        
#very dynamic db
class GameServer(Document):
    quizId = StringField(unique=True)
    peopleWaiting = IntField()
    serverId = StringField()
    lastWaitingUserId = StringField()
    lastUpdatedTimestamp = DateTimeField()
    
    
class Servers(Document):
    serverId = StringField()
    group = StringField()
    addr = StringField()
    
    meta = {
    'indexes': [
           ('serverId','group'),
           "group"
           ]
    }

   
    @staticmethod
    def getAllServers(group):
        return Servers.objects(group=group)
    
    @staticmethod
    def updateServerMap(serverMap, group):  # { id: ip:port}
        for serverId in serverMap:
            server = Servers.objects(serverId=serverId , group=group)
            if(server):
                server = server.get(0)
            else:
                server = Servers()
                server.group = group
                server.serverId = serverId
                
            server.addr = serverMap.get(serverId)
            server.save()
        return True
    
    @staticmethod
    def isServerIdExists(serverId , group):
        server = Servers.objects(serverId=serverId , group=group)
        return True if server else False
    
    
class BotUids(Document):
    _botUids = None
    
    uid = StringField(unique=True)
    
    @classmethod
    def loadBotUids(cls):
        cls._botUids = [x.uid for x in  BotUids.objects()]
        
        
    @classmethod
    def getBotUser(cls):
        if(cls._botUids==None):#cache them
            cls.loadBotUids()
            
        return cls.getUserByUid(random.choice(cls._botUids))



class Feedback(Document):
    user = ReferenceField(Users)
    message = StringField()
    
