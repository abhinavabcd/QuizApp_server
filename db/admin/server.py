from mongoengine import Document , StringField , DateTimeField, IntField, ReferenceField
from db.user import Users
import random

class Configs(Document):
    key = StringField(unique=True)
    value = StringField()
    
    @staticmethod
    def getConfig(key , defValue=None):
        config = Configs.objects(key=key)
        if(not config):
            return defValue
        else:
            config = config.get(0)
            return config.value
    
    @staticmethod  
    def setConfig(key , value):
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
    
