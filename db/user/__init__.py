import HelperFunctions
from datetime import datetime
from Constants import FEED_USER_JOINED, FEED_USER_WON_BADGES
from db.badges import Badges
from db.user.feeds import UserFeed, Feed
__author__ = "abhinav"


from mongoengine import Document , StringField, EmailField, BooleanField, FloatField , ListField , DateTimeField , IntField , ReferenceField
from db.user.utils import UserActivityStep, Uid1Uid2Index
import json



class UserStats(Document):
    uid = StringField()  # uid
    quizId = StringField()  # use double index here
    xpPoints = IntField(default=0)  # rev index
    meta = {
        'indexes': [
                    'uid',
                    ('uid', 'quizId'),
                    ('quizId', '-xpPoints')
                ]
        }
                    
class UserWinsLosses(Document):
    uid = StringField()
    quizId = StringField()
    wins = IntField(default=0)
    loss = IntField(default=0)
    ties = IntField(default=0)
    meta = {
        'indexes': [
                    'uid',
                    ('uid', 'quizId')
                ]
        }



class Users(Document):
    uid = StringField(unique=True)
    name = StringField()
    status = StringField()
    deviceId = StringField(required=True)
    emailId = EmailField()
    pictureUrl = StringField()  # cdn link
    coverUrl = StringField()
    birthday = FloatField()
    gender = StringField()
    place = StringField()
    country = StringField(default=None)
    ipAddress = StringField()
    isActivated = BooleanField(default=False)
    # winsLosses = DictField() #quizId to [wins , totals]
    stats = None
    winsLosses = None
    activationKey = StringField()
    gcmRegId = StringField()
    
    badges = ListField(StringField())
    loginIndex = IntField()
    googlePlus = StringField(default=None)
    facebook = StringField(default=None) 
    gPlusUid = StringField()
    fbUid = StringField()
    activationCode = StringField()
    newDeviceId = StringField()
    createdAt = DateTimeField()
    subscribers = ListField(StringField())
    subscribedTo = ListField(StringField())
    userFeedIndex = ReferenceField(UserActivityStep)
    userChallengesIndex = ReferenceField(UserActivityStep)
    userType = IntField(default=0)
    gPlusFriends = StringField()
    fbFriends = StringField()
    
    
    userStats = property(getStats)
    userWinsLosses = property(getWinsLosses)
    
    
    meta = {
        'indexes': [
            'fbUid',
            'gPlusUid',
            'emailId'
            ]
        }
    def getStats(self, quizId=None):
        ret = {}
        stats = None
        if(quizId == None):
            stats = UserStats.objects(uid=self.uid)
        else:
            stats = UserStats.objects(uid=self.uid, quizId=quizId)
            
        for x in stats:
            ret[x.quizId] = x.xpPoints
        self.stats = ret
        return ret
    
    def updateStats(self , quizId , addXpPoints):
        stat = UserStats.objects(uid=self.uid, quizId=quizId)
        if(stat):
            stat = stat.get(0)
        else:
            stat = UserStats()
            stat.uid = self.uid
            stat.quizId = quizId
        stat.xpPoints += addXpPoints
        if(self.stats):
            self.stats[quizId] = stat.xpPoints
        stat.save()
            
    def getWinsLosses(self, quizId=None):
        ret = {}
        stats = None
        if(quizId == None):
            stats = UserWinsLosses.objects(uid=self.uid)
        else:
            stats = UserWinsLosses.objects(uid=self.uid, quizId=quizId)
            
        for x in stats:
            ret[x.quizId] = [x.wins, x.loss , x.ties]
        self.winsLosses = ret
        return ret
    
    def updateWinsLosses(self, quizId , win=0 , loss=0 , tie=0 , winStatus=-2):
        if(winStatus == -1):
            loss = 1
        elif(winStatus == 0):
            tie = 1
        elif(winStatus == 1):
            win = 1
            
        wl = UserWinsLosses.objects(uid=self.uid, quizId=quizId)
        if(wl):
            wl = wl.get(0)
        else:
            wl = UserWinsLosses()
            wl.uid = self.uid
            wl.quizId = quizId
        if((win or loss) and not tie):
            if(win):
                wl.wins += 1
            if(loss):
                wl.loss += 1
        else:
            wl.ties += 1
        if(self.winsLosses):  # update
            self.winsLosses[quizId] = [wl.wins , wl.loss, wl.ties ]  
        wl.save()

    @staticmethod
    def getUserByUid(uid , long=True):
        users = Users.objects(uid=uid)
        if(users):
            user = users.get(0)
            if(long):
                user.getStats()  # will update the values
                user.getWinsLosses()  # will update the values
            return user
        return None
    
    
    def toJson(self):
        return json.dumps({"uid":self.uid,
                "name":self.name,
                "badges":self.badges,
                "stats":self.stats,
                "winsLosses":self.winsLosses,
                "pictureUrl":self.pictureUrl,
                "subscribers":self.subscribers,
                "subscribedTo":self.subscribedTo,
                "coverUrl":self.coverUrl,
                "gender":self.gender,
                "country":self.country,
                "status":self.status,
                "gPlusUid":self.gPlusUid,
                "fbUid":self.fbUid
                })
    
    @staticmethod
    def registerUser(name, deviceId, emailId, pictureUrl, coverUrl , birthday, gender, place, ipAddress, facebookToken=None , gPlusToken=None, isActivated=False, preUidText="" , fbUid=None, gPlusUid=None , gPlusFriends=[] , fbFriends=[], connectUid=None):
        if(connectUid != None):
            user = Users.objects(uid=connectUid)
        elif(emailId):
            user = Users.objects(emailId=emailId)
        elif(gPlusUid):
            user = Users.objects(gPlusUid=gPlusUid)
        elif(fbUid):
            user = Users.objects(fbUid=fbUid)
            
        if(user or len(user) > 0):
            user = user.get(0)
        else:
            user = Users()
            user.uid = preUidText + HelperFunctions.generateKey(10)
            user.stats = {}
            user.winsLosses = {}
            user.activationKey = ""
            user.badges = []
            user.offlineChallenges = []
            # user feed index , # few changes to the way lets see s
            user.userFeedIndex = userFeedIndex = UserActivityStep()
            userFeedIndex.uid = user.uid + "_feed"
            userFeedIndex.index = 0
            userFeedIndex.userLoginIndex = 0
            userFeedIndex.save()
            # ##
            user.userChallengesIndex = userChallengesIndex = UserActivityStep()
            userChallengesIndex.uid = user.uid + "_challenges"
            userChallengesIndex.index = 0
            userChallengesIndex.userLoginIndex = 0
            userChallengesIndex.save()
            # ##
            user.subscribers = []
            user.subscribedTo = []
            user.emailId = emailId
            user.createdAt = datetime.datetime.now()
            user.loginIndex = 0
        
        
        subscribersList = {}
        if(fbUid != None):
            user.fbUid = fbUid
            newFriends = []
            if(user.fbFriends == None):
                newFriends = fbFriends
            elif(fbFriends):
                newFriends = list(set(fbFriends) - set(json.loads(user.fbFriends)))
            for i in newFriends:
                if(i == fbUid): continue
                user2 = Users.objects(fbUid=i)
                if(user2):
                    user2 = user2.get(0)
                    # mutual friends
                    subscribersList[user2.uid] = user2
        if(gPlusUid != None):
            user.gPlusUid = gPlusUid
            newFriends = []
            if(user.gPlusFriends == None):
                newFriends = gPlusFriends
            else:
                newFriends = list(set(gPlusFriends) - set(json.loads(user.gPlusFriends)))
            for i in newFriends:
                if(i == gPlusUid): continue
                user2 = Users.objects(gPlusUid=i)
                if(user2):
                    user2 = user2.get(0)
                    subscribersList[user2.uid] = user2
                    # mutual friends
        
        user.newDeviceId = deviceId
        user.name = name
        user.deviceId = deviceId
        user.pictureUrl = pictureUrl
        user.coverUrl = coverUrl
        user.birthday = birthday
        user.gender = gender
        user.place = place
        user.ipAddress = ipAddress
        user.facebook = facebookToken if facebookToken != None else user.facebook
        user.googlePlus = gPlusToken if gPlusToken != None else user.googlePlus
        user.isActivated = isActivated
        user.save()
        for user2 in subscribersList.values():
            user.addsubscriber(user2)
            user2.addsubscriber(user)
            UserFeed.publishFeedToUser(user, user2, FEED_USER_JOINED, user.uid, None)
            
        return user
    
    def incrementLoginIndex(self):
        self.loginIndex += 1
        self.save()

    def addsubscriber(self, user):
        self.update(add_to_set__subscribers=user.uid)
        user.update(add_to_set__subscribedTo=self.uid)
        
    def removeSubscriber(self , user):
        self.update(pull__subscribers=user.uid)
        user.update(pull__subscribedTo=self.uid)
    
    
    def publishFeedToSubscribers(self, _type ,  message, message2=None):
        f = Feed()
        f.fromUid = self.uid
        f.message = message
        f.type = _type
        if(message2!=None):
            f.message2 = message2
        f.timestamp = HelperFunctions.toUtcTimestamp(datetime.datetime.now())
        f.save()
        #### move to tasks other server if possible
        for uid in self.subscribers:
            user = Users.getUserByUid(uid)
            userFeed = UserFeed()
            userFeed.uidFeedIndex = uid+"_"+str(user.userFeedIndex.getAndIncrement(user).index)
            userFeed.feedMessage = f
            userFeed.save()
    
    
    def toJsonShort(self):
        return json.dumps({"uid":self.uid,
                "name":self.name,
                "badges":self.badges,
#                 "stats":self.getStats(),
#                 "winsLosses":self.getWinsLosses(),
                "pictureUrl":self.pictureUrl,
                "coverUrl":self.coverUrl,
                "gender":self.gender,
                "country":self.country,
                "status":self.status,
                "gPlusUid":self.gPlusUid,
                "fbUid":self.fbUid
                })
    
    def setUserGCMRegistationId(self, gcmRedId):
        self.gcmRegId = gcmRedId
        self.save()
        return
    
    @staticmethod
    def searchByStartsWithUserName(startsWithStr):
        return Users.objects(name__istartswith=startsWithStr)[:20]
    
    
    
    def getChatFriends(self):
        # TODO: OPTIMIZE
        objs = Uid1Uid2Index.objects(uid1=self.uid)
        uidList = [] 
        for i in objs:
            uidList.append(i.uid2)
        objs2 = Uid1Uid2Index.objects(uid2=self.uid)
        for i in objs2:
            uidList.append(i.uid1)
        return uidList
  
        
    def addBadges(self , badgeIds):
        badges = Badges.objects(badgeId__in=badgeIds)
        name = self.name
        if(badges and len(badges) > 0):
            badgeIds = []
            for i in badges:
                self.update(add_to_set__badges=i.badgeId)
                badgeIds.append(i.badgeId)
            self.publishFeedToSubscribers(FEED_USER_WON_BADGES , json.dumps(badgeIds) , None)
            return True
        return False
