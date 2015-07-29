import HelperFunctions
from datetime import datetime
from db.badges import Badges
from db.user.feeds import UserFeedV2, UserFeed 
from server.constants import FEED_USER_WON_BADGES, FEED_USER_JOINED,\
    WHAT_USER_HAS_GOT, FEED_CHALLENGE, GameEventType,\
    GameTypes
from db.user.challenge import OfflineChallenge
from db.user.chats import UserChatMessages
from db.admin.server import Feedback
from db.user.games import UserGamesHistory
import bson
__author__ = "abhinav"


from mongoengine import Document , StringField, EmailField, BooleanField, FloatField , ListField , DateTimeField , IntField , ReferenceField
from db.user.utils import UserActivityStep, Uid1Uid2Index
import json


    
class GameEvent(Document):
    uid = StringField()# belongs to user
    uidGameEventIndex = StringField()
    type = IntField(default = 0)
    message = StringField()
    message2= StringField()
    message3 = StringField()
    timestamp = DateTimeField()
    meta = {
        'indexes': [
                    'uid'
                    ('uid','-timestamp')
                ]
        }
    
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.timestamp = datetime.datetime.now()

    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["timestamp"] = HelperFunctions.toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)


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
    userFeedIndex = ReferenceField(UserActivityStep)#old , remove eventually
    userFeedV2Index = ReferenceField(UserActivityStep)
    userChallengesIndex = ReferenceField(UserActivityStep)
    gameEventsIndex = ReferenceField(UserActivityStep)
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

            
            user.subscribers = []
            user.subscribedTo = []
            user.emailId = emailId
            user.createdAt = datetime.datetime.now()
            user.loginIndex = 0
        
        user.stats = user.stats or {}
        user.winsLosses =user.winsLosses or {}
        user.activationKey = ""
        user.badges = user.badges or []
        user.offlineChallenges = user.offlineChallenges or []
        # user feed index , # few changes to the way lets see 
        user.userFeedIndex = user.userFeedIndex or UserActivityStep.create(user, "feed")
                
        user.userFeedV2Index = user.userFeedV2Index or UserActivityStep.create(user, "feed_V2")
        # ##
        user.userChallengesIndex = user.userChallengesIndex or UserActivityStep.create(user, "challenges")        
        # ##
        user.gameEventsIndex = user.gameEventsIndex or UserActivityStep.create(user, "gameEvents")
        

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
        
        gameEvent = user.createGameEvent(GameEventType.USER_JOINED, user.uid, None, None , postFeed=False)
        for user2 in subscribersList.values():
            user.addsubscriber(user2)
            user2.addsubscriber(user)
            user2.publishToUserFeed(gameEvent) # post that a new user joined
            
        return user
    
    def incrementLoginIndex(self):
        self.loginIndex += 1
        self.save()

    def addsubscriber(self, user):
        self.update(add_to_set__subscribers=user.uid)
        user.update(add_to_set__subscribedTo=self.uid)
        
    def removeSubscriber(self , user):
        self.update(pull__subscribedTo=user.uid)
        user.update(pull__subscribers=self.uid)
        
    '''
     user2 is just additional data to use in the function , especially when posting to feed
    '''
    def createGameEvent(self, gameEventType, message, message2, message3 , postFeed=True ,user2 = None):
        gameEvent = GameEvent()
        gameEvent.uid = self.uid
        gameEvent.uid_index = self.gameEventsIndex.getAndIncrement(self).index
        gameEvent.type = gameEventType
        gameEvent.message = message
        if(message2!=None):
            gameEvent.message2 = message2
        if(message3!=None):
            gameEvent.message3 = message3
        gameEvent.save()
        if(not postFeed):
            return gameEvent
        ### TODO: decide on sending a feed to subscribers based on type
        #delay this process TODO: important!
        if(gameEventType == GameEventType.UNLOCKED_BADGE):
            self.postFeedToSubscribers(gameEvent)
        
        if(gameEventType == GameEventType.PLAYED_A_QUIZ):
            self.postFeedToSubscribers(gameEvent)
        
        if(gameEventType == GameEventType.CHALLENGE_COMPLETED):
            #add it to completed user and post to feed for the challenging user which is message2
            # add gcm notification #TODO:
            if(user2):
                user2.publishToUserFeed(gameEvent)
            
        return gameEvent
    
    def publishToUserFeed(self, gameEvent):
        userFeed = UserFeedV2()
        userFeed.uidFeedIndex= self.uid+"_"+str(self.userFeedV2Index.getAndIncrement(self).index)
        userFeed.gameEvent = gameEvent
        userFeed.save()
        pass
    
    ###TODO: remove this to do it automatically from addGameEvent
    def postFeedToSubscribers(self, gameEvent):

        #### move to tasks other server if possible
        for uid in self.subscribers:
            user = Users.getUserByUid(uid)
            userFeed = UserFeedV2()
            userFeed.uidFeedIndex = uid+"_"+str(user.userFeedV2Index.getAndIncrement(user).index)
            userFeed.gameEvent = gameEvent
            userFeed.save()
    
    def getRecentUserFeedV2(self, toIndex=-1, fromIndex=0):
        ind = toIndex if toIndex>0 else self.userFeedV2Index.index
        cnt =50
        userFeedMessages = []
        while(ind>fromIndex):
            for i in UserFeedV2.objects(uidFeedIndex = self.uid+"_"+str(ind)):
                userFeedMessages.append(i.gameEvent)#getting from reference field
                cnt-=1
            if(cnt<=0):
                break
            ind-=1
        return userFeedMessages
    
    
    def getGameEvents(self, toIndex=-1, fromIndex=0):
        ind = toIndex if toIndex>0 else self.userGameEventsIndex.index
        cnt =50
        userGameEvents = []
        while(ind>fromIndex):
            for i in GameEvent.objects(uidGameEventIndex = self.uid+"_"+str(ind)):
                userGameEvents.append(i.gameEvent)#getting from reference field
                cnt-=1
            if(cnt<=0):
                break
            ind-=1
        return userGameEvents
    
    
    ## OLD:
    def getRecentUserFeed(self, user, toIndex=-1, fromIndex=0):
        ind = toIndex if toIndex>0 else user.userFeedIndex.index
        cnt =50
        userFeedMessages = []
        while(ind>fromIndex):
            for i in UserFeed.objects(uidFeedIndex = user.uid+"_"+str(ind)):
                userFeedMessages.append(i.feedMessage)#getting from reference field
                cnt-=1
            if(cnt<=0):
                break
            ind-=1
        return userFeedMessages
    
    
    def getUserChallenges(self,  toIndex =-1 , fromIndex = 0):
        limit =20
        if(fromIndex!=0):
            limit = 1000000
        index = toIndex
        if(toIndex==-1):
            index = self.userChallengesIndex.index
        userChallenges = []
        count =0
        while(index>fromIndex):
            for i in OfflineChallenge.objects(toUid_userChallengeIndex = self.uid+"_"+str(index)):
                userChallenges.append(i)#getting from reference field
                count+=1
            if(count>limit):
                break
            index-=1
        return userChallenges
    
    def getRecentMessagesIfAny(self, afterTimestamp):
        messagesAfterTimestamp = UserChatMessages.objects(toUid_LoginIndex=self.uid + "_" + str(self.loginIndex) , timestamp__gt=afterTimestamp)
        return messagesAfterTimestamp
    
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
            self.createGameEvent(GameEventType.UNLOCKED_BADGE , json.dumps(badgeIds) , None , None)
            return True
        return False
    
    def addFeedback(self,  message):
        feedback  = Feedback()
        feedback.user = self
        feedback.message = message
        feedback.save()
        
        
        
        '''
    this is called by both users after the quiz ends
    '''
    def updateQuizWinStatus(self, quizId , xpGain , relativeXpGain , winStatus, uid2 , userAnswers1 , userAnswers2 , gameType=GameTypes.RANDOM_USER_TYPE):
        if(self.uid > uid2 or uid2[:2]=="00"): #or uid2 is bot or # with greater user id updates the table
            s = UserGamesHistory()
            s.uid = self.uid
            s.uid2 = uid2
            s.uid_uid2 = self.uid+"_"+uid2
            s.solvedId = self.uid+"_"+uid2+"_"+quizId
            #s.type = WIN_TYPE #WIN , LOSE , CHALLENGE , 
            s.gameStatus = winStatus
            s.points = xpGain
            s.gameType = gameType
            s.userAnswers1 = userAnswers1
            s.userAnswers2 = userAnswers2
            s.timestamp = datetime.datetime.now()
            
        #TODO : addEvent
        # played a quiz with uid2 in quizId with relativeXpGain(this indicated win loset or tie too) 
        if(gameType==GameTypes.RANDOM_USER_TYPE):
            self.createGameEvent(GameEventType.PLAYED_A_QUIZ, uid2, quizId , str(relativeXpGain))
        self.updateStats(quizId, xpGain)
        self.updateWinsLosses(quizId, winStatus = winStatus)
    

    def postOfflineChallenge(self, toUid , challengeData, offlineChallengeId=None):
        toUser = Users.getUserByUid(toUid)
        
        offlineChallenge = OfflineChallenge()
        if(offlineChallengeId!=None):
            offlineChallenge.offlineChallengeId = offlineChallengeId
        else:
            offlineChallenge.offlineChallengeId = HelperFunctions.generateKey(10)
        offlineChallenge.fromUid_userChallengeIndex = self.uid+"_"+str(self.userChallengesIndex.index) # yeah , its a little bit funny too # fuck you , i was not funny , that was over optimization for an unreleased app !!!
        offlineChallenge.toUid_userChallengeIndex = toUid+"_"+str(toUser.userChallengesIndex.getAndIncrement(toUser).index)
        offlineChallenge.challengeData = challengeData
        offlineChallenge.save()
        return offlineChallenge
    
    
    
    def onChallengeComplete(self, challengeId , challengeData2):# user does the challenge
        offlineChallenge = OfflineChallenge.objects(offlineChallengeId=challengeId).get(0) 
        offlineChallenge.challengeData2 = challengeData2
        fromUser = Users.getUserByUid(offlineChallenge.fromUid_userChallengeIndex.split("_")[0])
        
        if(offlineChallenge.challengeType==0):
            try:
                challengeData1= json.loads(offlineChallenge.challengeData)
                challengeData2= json.loads(offlineChallenge.challengeData2)
                quizId = challengeData1["quizId"]
                a = challengeData1["userAnswers"][-1][WHAT_USER_HAS_GOT] # this belongs to first user who challenged
                b = challengeData2["userAnswers"][-1][WHAT_USER_HAS_GOT] # this belongs to current User
                relativeXpGain = b-a
                
                won , lost , tie = 0, 0, 0 
                winStatus = -2
                if(a==b):
                    offlineChallenge.whoWon = ""
                    winStatus  = 0
                    won , lost,tie = 0 ,0 ,1
                elif(a>b):
                    offlineChallenge.whoWon = offlineChallenge.fromUid_userChallengeIndex
                    won , lost , tie = 0 ,1 ,0 
                    winStatus = -1
                else:
                    offlineChallenge.whoWon = offlineChallenge.toUid_userChallengeIndex
                    won , lost ,tie = 1 , 0 ,0
                    winStatus = 1
                
                
                offlineChallenge.save()
                
                
                userAnswers1_str = json.loads(challengeData1["userAnswers"])# current user
                userAnswers2_str = json.loads(challengeData2["userAnswers"])
                
                self.updateQuizWinStatus(quizId, a+20*won, relativeXpGain,  winStatus,fromUser.uid, userAnswers2_str , userAnswers1_str , GameTypes.CHALLENGE_QUIZ_TYPE)
                fromUser.updateQuizWinStatus(quizId, b+20*lost, -relativeXpGain ,  -winStatus, self.uid , userAnswers1_str, userAnswers2_str, GameTypes.CHALLENGE_QUIZ_TYPE)
                # game event
                self.createGameEvent(GameEventType.CHALLENGE_COMPLETED, challengeId, fromUser.uid, str(relativeXpGain) , user2 = fromUser)
                #UserFeed.publishFeedToUser(user, fromUser, FEED_CHALLENGE, challengeId , None )
                
                return True
            except:
                return False
        return True


