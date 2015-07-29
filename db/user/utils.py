
from mongoengine import Document , StringField, IntField 

'''
for a login index that increments every time user logs in , user activity changes for every login index change.
that means between logins  the useractivity step remains same index
'''
class UserActivityStep(Document):
    uid = StringField()
    index = IntField(default = 0)
    subIndex = IntField(default=0)
    userLoginIndex = IntField()
    def getAndIncrement(self, user):
        if(self.userLoginIndex!= user.loginIndex or self.subIndex>50): #increments for every 50 changes
            self.index+=1
            self.subIndex = 0
            self.userLoginIndex = user.loginIndex
            self.save()
        else:
            self.subIndex+=1
            self.save()
        return self
    
    @staticmethod
    def create(user, name):
        ret = UserActivityStep()
        ret.uid = user.uid + "_" + name
        ret.index = 0
        ret.userLoginIndex = 0
        ret.save()
        return ret
        
            

def reorderUids(uid1, uid2):
    if(uid1 < uid2):#swap maintain same order always
        return uid2, uid1
    return uid1, uid2

def reorder(user1, user2):
    if(user1.uid < user2.uid):#swap maintain same order always
        temp = user1
        user1 = user2
        user2 = temp
    return user1, user2

class Uid1Uid2Index(Document): 
    uid1_uid2 = StringField(unique=True)
    index = IntField(default=0)
    uid1 = StringField()
    uid2 = StringField()
    uid1LoginIndex = IntField()
    uid2LoginIndex = IntField()
    meta = {
        'indexes': [
            'uid1','uid2',
            'uid1_uid2'
            
            ]
        }
    @staticmethod 
    def getAndIncrementIndex(user1, user2):
        if(user1.uid < user2.uid):#swap maintain same order always
            temp = user1
            user1 = user2
            user2 = temp
            
        obj = Uid1Uid2Index.objects(uid1_uid2 = user1.uid+"_"+user2.uid)
        saveObj = False
        if(not obj):
            obj = Uid1Uid2Index()
            obj.uid1_uid2 = user1.uid+"_"+user2.uid
            obj.uid1 = user1.uid
            obj.uid2 = user2.uid
            saveObj = True
        else:
            obj = obj.get(0)
        if(obj.uid1LoginIndex!=user1.loginIndex or obj.uid2LoginIndex!=user2.loginIndex): # totally new sessions
            obj.index+=1
            obj.uid1LoginIndex = user1.loginIndex
            obj.uid2LoginIndex = user2.loginIndex
            saveObj = True
            
        if(saveObj):
            obj.save()

        return obj.index
