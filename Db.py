import bson
import datetime
import itertools
import json
from mongoengine import *
import random
import string
import time

import Config
from Constants import *
import HelperFunctions


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

#very dynamic db
class ServerState(Document):
    quizId = StringField()
    peopleWaiting = IntField()
    serverId = StringField()
    lastWaitingUserId = StringField()
    
class Servers(Document):
    serverId = StringField(unique=True)
    ip = StringField()
    


class UserInboxMessages(Document):
    fromUid_toUid_index = StringField()#tag to identify block of messages
    fromUid = StringField()
    toUid = StringField()
    message = StringField()
    timestamp = DateTimeField()
    fromUid_LoginIndex = StringField() #uid1_LOGININDEX
    toUid_LoginIndex = StringField() #uid2_LOGININDEX
    meta = {
        'indexes': [
               ('toUid_LoginIndex','-timestamp'),
               'fromUid_toUid_index'
            ]
            }
    def to_json(self):
        son = self.to_mongo()
        del son["fromUid_LoginIndex"]
        del son["toUid_LoginIndex"]
        son["timestamp"] = HelperFunctions.toUtcTimestamp(self.timestamp)
        return bson.json_util.dumps(son)
        
        
class UserActivityStep(Document):
    uid = StringField()
    index = IntField(default = 0)
    userLoginIndex = IntField()
    def getAndIncrement(self, user):
        if(self.userLoginIndex!= user.loginIndex):
            self.index+=1
            self.save()
        return self
        
class OfflineChallenge(Document):
    offlineChallengeId = StringField(unique=True)
    fromUid_userChallengeIndex = StringField()
    toUid_userChallengeIndex = StringField()
    challengeType = IntField(default=0)
    challengeData = StringField() #{quizId:asdasd ,userAnswers:[], questions:[]}
    challengeData2 = StringField()
    wonUid = StringField()
    meta = {
            'indexes':['toUid_userChallengeIndex']
            }
    def toJson(self):
        sonObj = self.to_mongo()
        if(self.offlineChallengeId==None):
            sonObj["offlineChallengeId"] =self._id
        del sonObj["_id"]
        return bson.json_util.dumps(sonObj)
        
         
class UserFeed(Document):
    uidFeedIndex = StringField()#uid_LOGININDEX
    feedMessage = ReferenceField('Feed')
    

class Feedback(Document):
    user = ReferenceField('Users')
    message = StringField()
    

    
class Feed(Document):
    fromUid = StringField()
    type = IntField(default = 0)
    message = StringField()
    message2= StringField()
    timestamp = FloatField()
    
    
##### contains all quiz history of all games , offline online
class UserGamesHistory(Document):
    uid = StringField()
    uid2 = StringField()
    uid_uid2 = StringField()
    type = StringField() #WIN , LOSE , CHALLENGE , 
    solvedId= StringField() # to indentify exactly what type of quiz between what users
    points = IntField()
    userAnswers1 = StringField()
    userAnswers2 = StringField()
    

class UserStats(Document):
    uid  = StringField() # uid
    quizId = StringField() # use double index here
    xpPoints = IntField(default = 0)#rev index
    meta = {
        'indexes': [
                    'uid',
                    ('uid','quizId'),
                    ('quizId','-xpPoints')
                ]
        }
                    
class UserWinsLosses(Document):
    uid = StringField()
    quizId = StringField()
    wins = IntField(default = 0)
    loss = IntField(default = 0)
    ties = IntField(default = 0)
    meta = {
        'indexes': [
                    'uid',
                    ('uid','quizId')
                ]
        }
class Users(Document):
    uid = StringField(unique=True)
    name = StringField()
    status = StringField()
    deviceId = StringField(required = True)
    emailId = EmailField()
    pictureUrl = StringField()#cdn link
    coverUrl = StringField()
    birthday = FloatField()
    gender = StringField()
    place = StringField()
    country = StringField(default=None)
    ipAddress = StringField()
    isActivated = BooleanField(default = False)
    #winsLosses = DictField() #quizId to [wins , totals]
    stats = None
    winsLosses= None
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
        if(quizId==None):
            stats = UserStats.objects(uid=self.uid)
        else:
            stats = UserStats.objects(uid=self.uid,quizId=quizId)
            
        for x in stats:
            ret[x.quizId] = x.xpPoints
        self.stats = ret
        return ret
    
    def updateStats(self , quizId , addXpPoints):
        stat = UserStats.objects(uid=self.uid, quizId = quizId)
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
        if(quizId==None):
            stats = UserWinsLosses.objects(uid=self.uid)
        else:
            stats = UserWinsLosses.objects(uid=self.uid,quizId=quizId)
            
        for x in stats:
            ret[x.quizId] = [x.wins, x.loss , x.ties]
        self.winsLosses = ret
        return ret
    
    def updateWinsLosses(self, quizId , win=0 , loss=0 , tie=0 , winStatus = -2):
        if(winStatus==-1):
            loss = 1
        elif(winStatus==0):
            tie = 1
        elif(winStatus==1):
            win = 1
            
        wl = UserWinsLosses.objects(uid=self.uid, quizId = quizId)
        if(wl):
            wl = wl.get(0)
        else:
            wl = UserWinsLosses()
            wl.uid = self.uid
            wl.quizId = quizId
        if((win or loss) and not tie):
            if(win):
                wl.wins+=1
            if(loss):
                wl.loss+=1
        else:
            wl.ties+=1
        if(self.winsLosses): # update
            self.winsLosses[quizId] = [wl.wins , wl.loss,wl.ties ]  
        wl.save()

        
    
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
    
    userStats = property(getStats)
    userWinsLosses = property(getWinsLosses)

class Tags(Document):
    tag = StringField(unique=True)

class Badges(Document):
    badgeId = StringField(unique=True)
    name = StringField()
    description = StringField()
    assetPath = StringField()
    condition = StringField()
    type=IntField(default=0)
    modifiedTimestamp = DateTimeField()
    
    meta = {
        'indexes': [
            '-modifiedTimestamp'
            ]
        }
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["modifiedTimestamp"] = HelperFunctions.toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)



class Questions(Document):
    questionId = StringField(unique=True)
    questionType = IntField(default = 0)
    questionDescription = StringField()# special formatted inside the description itself
    pictures = ListField(StringField())
    options = StringField()
    answer = StringField()
    hint = StringField()
    explanation = StringField()
    time = IntField()
    xp = IntField()
    tagsAllSubjects = ListField(StringField()) #categorynameIndex , ....
    tagsAllIndex = ListField(StringField())
    tags=ListField(StringField())
    meta = {
        'indexes': [
                    'tags',
                    'tagsAllSubjects',
                    'tagsAllIndex'
                ]
        }
    def to_json(self):
        return json.dumps({"questionId":self.questionId,
                           "questionType":self.questionType,
                           "questionDescription":self.questionDescription,
                           "pictures":self.pictures,
                           "options":self.options,
                           "answer":self.answer,
                           "explanation":self.explanation,
                           "time":self.time,
                           "xp":self.xp
                           })


class TopicMaxQuestions(Document):
    mixedTag = StringField(unique=True)
    max = IntField(default=0)
    unused = ListField(IntField())
    @staticmethod
    def getNewId(tag):
        c = TopicMaxQuestions.objects(mixedTag = tag)
        if(not c):
            c = TopicMaxQuestions()
            c.mixedTag = tag
            c.max=1
            c.unused=[]
            c.save()
            return 0
        else:
            c= c.get(0)
            if(c.unused and len(c.unused)>0):
                ret = c.unused.pop()
                c.save()
                return ret

            c.max+=1
            c.save()
            return c.max-1

    @staticmethod
    def addToUnUsedId(tag, _id):
        c = TopicMaxQuestions.objects(mixedTag = tag).get(0)
        if(c.unused):
            c.unused.append(_id)
        else:
            c.unused = [_id]
        c.save()

    @staticmethod
    def getMax(tag):
        c = TopicMaxQuestions.objects(mixedTag = tag)
        if(not c):
            return 0
        else:
            return c.get(0).max


# class Subscribers(Document):
#     user  = ReferenceField('Users')
#     user2 = ReferenceField('User')

class BotUids(Document):
    uid = StringField(unique=True)


class Configs(Document):
    key = StringField(unique=True)
    value = StringField()


class Categories(Document):
    categoryId = StringField(unique=True)
    shortDescription = StringField()
    description = StringField()
    quizList = ListField(StringField())
    assetPath = StringField()
    bgAssetPath = StringField()
    titleAssetPath = StringField()
    type = StringField()
    modifiedTimestamp = DateTimeField()
    
    meta = {
        'indexes': [
            '-modifiedTimestamp'
            ]
        }
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["quizList"] = bson.json_util.dumps(self.quizList)
        sonObj["modifiedTimestamp"] = HelperFunctions.toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)

class Quiz(Document):
    quizId = StringField(unique= True)
    quizType = IntField()
    name = StringField()
    shortDescription = StringField()
    assetPath = StringField()
    tags = ListField(StringField())
    nQuestions = IntField()
    nPeople = IntField()
    modifiedTimestamp = DateTimeField()
    meta = {
        'indexes': [
            '-modifiedTimestamp',
            'tags'
            ]
        }
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["tags"] = bson.json_util.dumps(self.tags)
        sonObj["modifiedTimestamp"] = HelperFunctions.toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)

def getTagsFromString(s,toLower=True):
    ret = []
    a = s.split("\n")
    for i in a:
        for j in i.split(","):
            t = j.strip()
            if(not t):#empty not tolerated 
                continue
            t.replace(" ","-")
            t.replace("_","-")
            if(toLower):
                t = t.lower()
            ret.append(t)
    return ret


def getListFromString(s,toLower=False):
    ret = []
    a = s.split("\n")
    for i in a:
        for j in i.split(","):
            t = j.strip()
            if(not t):
                continue 
            if(toLower):
                t = t.lower()
            ret.append(t)
    return ret

class SecretKeys(Document):
    secretKey = StringField(unique=True)
    
class DbUtils():

    dbServer = []
    dbConnection = None
    rrCount = 0
    rrPriorities = 0
    _users_cached_lru= 0
    _botUids = []
    def __init__(self , dbServer):
        self._updateDbServer(dbServer)
        self.loadBotUids()
#         self.dbServerAliases = dbServers.keys()
#         self.rrPriorities = datetime.date.today()
    def _updateDbServer(self, dbServer):
        self.dbServer = dbServer
        self.dbConnection = connect(dbServer.dbName,host= dbServer.ip, port = dbServer.port, username= dbServer.username, password=dbServer.password)
    
    def loadBotUids(self):
        self._botUids = [x.uid for x in  BotUids.objects()]
        
        
    def getUserByUid(self, uid , long = True):
        users =Users.objects(uid=uid)
        if(users):
            user = users.get(0)
            if(long):
                user.getStats() # will update the values
                user.getWinsLosses()#will update the values
            return user
        return None
    
    def getBotUser(self):
        return self.getUserByUid(random.choice(self._botUids))


    def addOrModifyCategory(self, categoryId=None, shortDescription=None, description=None, assetPath=None, bgAssetPath=None, titleAssetPath=None,  quizList=None,isDirty=1):
        categoryId = str(categoryId)
        if(isinstance(quizList,str) or isinstance(quizList, int)):
            quizList = getListFromString(quizList)
            
        c= Categories.objects(categoryId = categoryId)
        if(c):
            c= c.get(0)
        else:
            c = Categories()
            c.categoryId = categoryId
        c.shortDescription = shortDescription
        c.description = description
        c.assetPath = assetPath
        c.bgAssetPath = bgAssetPath
        c.titleAssetPath = titleAssetPath
        
        quizListTemp = []
        ##TODO: below check if quiz is present in quizList
        for i in c.quizList:
            quizListTemp.append(i)
        addQuizList = set(quizList)-set(quizListTemp)
        removeQuizList = set(quizListTemp)-set(quizList)
        for i in removeQuizList:
            c.quizList.remove(i)

        for i in addQuizList:
            quiz = Quiz.objects(quizId=i)
            if(quiz):
                c.quizList.append(quiz.get(0).quizId)

        c.modifiedTimestamp = datetime.datetime.now()
        c.save()

    def addOrModifyQuiz(self, quizId=None,quizType=None, name=None, assetPath=None, tags=None, nQuestions=None,nPeople=None,isDirty=1):
        quizId = str(quizId)
        if(isinstance(tags,str)):
            tags = getTagsFromString(tags)
        
        q = Quiz.objects(quizId = quizId)
        if(q):
            q = q.get(0)
        else:
            q = Quiz()

        q.quizId = quizId
        q.quizType = quizType
        q.name = name
        q.tags = tags
        q.nQuestions = nQuestions
        q.assetPath = assetPath
        q.nPeople = nPeople
        q.modifiedTimestamp = datetime.datetime.now()
        q.save()
        return q

    def addQuestion(self,questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags):
        questionId = str(questionId)
        question = Questions.objects(questionId=questionId)
        
        if(len(question)>0):
            q = question=question.get(0)
            #print "Modifying question"
        else:
            q = question = Questions()
            q.questionId = questionId

        q.questionType = questionType
        q.questionDescription = questionDescription
        q.pictures = pictures
        q.options = options
        q.answer = answer
        q.hint = hint
        q.explanation=explanation
        q.time=time
        q.xp = xp
        q.save()
        ##################### save tags after the question is saved and save again if there was an error it should help
        oldTags =question.tags[:]
        if(set(oldTags) != set(tags)):
            #print "Modifying old tags"
            for i in question.tagsAllIndex:
                tagSet= i.split("_")
                _id = tagSet.pop()
                tagSet.sort()
                tag = "_".join(tagSet)
                TopicMaxQuestions.addToUnUsedId(tag, _id)#remove old tags , add to unused list to reuse later
                
            tags.sort()
            tagsAll = []
            tagsAll2 = []
            for L in range(1, len(tags)+1):
                for subset in itertools.combinations(tags, L):
                    fullTag = "_".join(sorted(subset))
                    _max = TopicMaxQuestions.getNewId(fullTag)
                    tagsAll.append(fullTag+"_"+str(_max))
                    tagsAll2.append(fullTag)
#             print tagsAll
#             print tagsAll2
    
            q.tagsAllSubjects= tagsAll2
            q.tagsAllIndex= tagsAll
            q.tags = tags
            q.save()
            
        

    def addOrModifyQuestion(self,questionId=None, questionType=0 , questionDescription=None, pictures=None, options=None, answer=None, hint=None, explanation=None, time=None, xp=None, tags=None ,isDirty=1):
        if(isinstance(tags,str)):
            tags=getTagsFromString(tags)
            for tag in tags:
#                 tag =  Tags.objects(tag=tag)
#                 if(not tag or len(tag)==0):
#                     print "Tags Not found in Db"
#                     return False
                ############FOR NOW INITIAL PHASE
                self.addOrModifyTag(tag)

               
        if(isinstance(pictures,str)):
            pictures=getListFromString(pictures)
        answer = str(answer)
        #print questionId, questionType , questionDescription, pictures, options, answer, hint, explanation, time, xp, tags
        self.addQuestion(questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags)
        return True
    
    def addOrModifyBadge(self,badgeId=None, name=None, description=None, assetPath=None, condition=None,  type=0, isDirty=1):
        #print badgeId, type , description, assetPath, condition
        badgeId = str(badgeId)
        badge = Badges.objects(badgeId=badgeId)
        
        if(len(badge)>0):
            bdg = badge=badge.get(0)
        else:
            bdg = badge = Badges()
            bdg.badgeId = badgeId

        bdg.type = type
        bdg.name = name
        bdg.description = description
        bdg.assetPath = assetPath
        bdg.condition = condition
        bdg.modifiedTimestamp = datetime.datetime.now()
        bdg.save()
        return True
    
    def getOfflineChallengeById(self, offlineChallengeId, user):
        
        offlineChallenge =  OfflineChallenge.objects(offlineChallengeId=offlineChallengeId).get(0)
        if(user.uid in offlineChallenge.fromUid_userChallengeIndex or user.uid in offlineChallenge.toUid_userChallengeIndex):
            return offlineChallenge
        return None
            
        
    def addOfflineChallenge(self , fromUser, toUid , challengeData, offlineChallengeId=None):
        toUser = self.getUserByUid(toUid)
        
        offlineChallenge = OfflineChallenge()
        if(offlineChallengeId!=None):
            offlineChallenge.offlineChallengeId = offlineChallengeId
        else:
            offlineChallenge.offlineChallengeId = HelperFunctions.generateKey(10)
        offlineChallenge.fromUid_userChallengeIndex = fromUser.uid+"_"+str(fromUser.userChallengesIndex.index) # yeah , its a little bit funny too
        offlineChallenge.toUid_userChallengeIndex = toUid+"_"+str(toUser.userChallengesIndex.getAndIncrement(toUser).index)
        offlineChallenge.challengeData = challengeData
        offlineChallenge.save()
        return offlineChallenge
        
    def onUserCompletedChallenge(self, user ,challengeId,challengeData2):
        offlineChallenge = OfflineChallenge.objects(offlineChallengeId=challengeId).get(0)
        offlineChallenge.challengeData2 = challengeData2
        fromUser = self.getUserByUid(offlineChallenge.fromUid_userChallengeIndex.split("_")[0])
        
        if(offlineChallenge.challengeType==0):
            challengeData1= json.loads(offlineChallenge.challengeData)
            challengeData2= json.loads(offlineChallenge.challengeData2)
            quizId = challengeData1["quizId"]
            a = challengeData1["userAnswers"][-1][WHAT_USER_HAS_GOT]
            b = challengeData2["userAnswers"][-1][WHAT_USER_HAS_GOT]
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
            self.updateQuizWinStatus(user, quizId, a+20*won, winStatus,fromUser.uid, None, None)
            self.publishFeedToUser(user.uid, fromUser, FEED_CHALLENGE, challengeId , None )
            self.updateQuizWinStatus(fromUser, quizId, b+20*lost, -winStatus, user.uid , None, None)
            return True
        return True
    def getUserChallenges(self, user , toIndex =-1 , fromIndex = 0):
        limit =20
        if(fromIndex!=0):
            limit = 1000000
        index = toIndex
        if(toIndex==-1):
            index = user.userChallengesIndex.index
        userChallenges = []
        count =0
        while(index>fromIndex):
            for i in OfflineChallenge.objects(toUid_userChallengeIndex = user.uid+"_"+str(index)):
                userChallenges.append(i)#getting from reference field
                count+=1
            if(count>limit):
                break
            index-=1
        return userChallenges

    def searchByStartsWithUserName(self, startsWithStr):
        return Users.objects(name__istartswith=startsWithStr)[:20]
            
    def updateQuizWinStatus(self, user, quizId , xpGain , winStatus, uid2 , userAnswers1 , userAnswers2):
        if(user.uid > uid2 or uid2[:2]=="00"): #or uid2 is bot or 
            s = UserGamesHistory()
            s.uid = user.uid
            s.uid2 = uid2
            s.uid_uid2 = user.uid+"_"+uid2
            s.solvedId = user.uid+"_"+uid2+"_"+quizId
            s.type = WIN_TYPE #WIN , LOSE , CHALLENGE , 
            s.points = xpGain
            s.userAnswers1 = userAnswers1
            s.userAnswers2 = userAnswers2
            

        user.updateStats(quizId, xpGain)
        user.updateWinsLosses(quizId, winStatus = winStatus)
    
    def getTopicMaxCount(self, fullTag):
        return TopicMaxQuestions.getMax(fullTag)
            
    def getRandomQuestions(self , quiz):
        fullTag = "_".join(sorted(quiz.tags))
        questionsCount = quiz.nQuestions
        
        count =  self.getTopicMaxCount(fullTag)
        questions = []
        if(count <= questionsCount):
            questions = [x for x in Questions.objects(tagsAllSubjects= fullTag)]
            numQuestions = len(questions)
            for i in range(questionsCount-count):#needed questions 
                questions.append(questions[i%numQuestions])#repeat
            return questions
        questionIds= {}
        c=0
        maxIterations = 50
        while(c<questionsCount):
            if(maxIterations<0):
                break
            maxIterations-=1
            numRand = random.randint(0,count)
            if(questionIds.get(int(numRand),None)==None):
                questionIds[numRand]=True
                question = Questions.objects(tagsAllIndex=fullTag+"_"+str(numRand))
                if(question):
                    question = question.get(0)
                    questions.append(question)
                    c+=1
        
        for i in range(questionsCount-len(questions)):
            questions.append(questions[i])# repeat them 
                    
        return questions
            
                
                
            
                
            
            
            
            
        

    def getAllCategories(self,modifiedTimestamp):
        return Categories.objects(modifiedTimestamp__gt = modifiedTimestamp)
    
    def getAllQuizzes(self,modifiedTimestamp):
        return Quiz.objects(modifiedTimestamp__gte = modifiedTimestamp)
   
    def setUserGCMRegistationId(self, user , gcmRedId):
        user.gcmRegId = gcmRedId
        user.save()
        return
    
    def getQuestionsById(self, questionIds):
        return Questions.objects(questionId__in = questionIds)
#     
#     def getDbAliasFromUid(self, uid):
#         alias =  uid[0:4]
#         if(alias==DEFAULT_SERVER_ALIAS):
#             return "default"
#         return alias
#         
#     
#     def getRRDbAliasForUid(self):
#         #arrange by priority here
#         self.dbServerAliases[self.rrCount]
#         self.rrCount+=1
    ### this should rather be connect to fb , gplus or refresh users list too not just register User
    def registerUser(self, name, deviceId, emailId, pictureUrl, coverUrl , birthday, gender, place, ipAddress,facebookToken=None , gPlusToken=None, isActivated=False, preUidText = "" , fbUid=None, gPlusUid=None , gPlusFriends = [] , fbFriends = [], connectUid=None):
        if(connectUid!=None):
            user = Users.objects(uid=connectUid)
        elif(emailId):
            user = Users.objects(emailId=emailId)
        elif(gPlusUid):
            user = Users.objects(gPlusUid = gPlusUid)
        elif(fbUid):
            user = Users.objects(fbUid=fbUid)
            
        if(user or len(user)>0):
            user = user.get(0)
        else:
            user = Users()
            user.uid = preUidText+HelperFunctions.generateKey(10)
            user.stats = {}
            user.winsLosses = {}
            user.activationKey = ""
            user.badges = []
            user.offlineChallenges = []
            #user feed index , # few changes to the way lets see s
            user.userFeedIndex = userFeedIndex = UserActivityStep()
            userFeedIndex.uid = user.uid+"_feed"
            userFeedIndex.index = 0
            userFeedIndex.userLoginIndex = 0
            userFeedIndex.save()
            ###
            user.userChallengesIndex = userChallengesIndex = UserActivityStep()
            userChallengesIndex.uid = user.uid+"_challenges"
            userChallengesIndex.index = 0
            userChallengesIndex.userLoginIndex = 0
            userChallengesIndex.save()
            ###
            user.subscribers = []
            user.subscribedTo = []
            user.emailId = emailId
            user.createdAt = datetime.datetime.now()
            user.loginIndex = 0
        
        
        subscribersList = {}
        if(fbUid!=None):
            user.fbUid = fbUid
            newFriends = []
            if(user.fbFriends==None):
                newFriends= fbFriends
            elif(fbFriends):
                newFriends = list(set(fbFriends) - set(json.loads(user.fbFriends)))
            for i in newFriends:
                if(i==fbUid): continue
                user2 = Users.objects(fbUid = i)
                if(user2):
                    user2= user2.get(0)
                    # mutual friends
                    subscribersList[user2.uid] = user2
        if(gPlusUid!=None):
            user.gPlusUid = gPlusUid
            newFriends = []
            if(user.gPlusFriends==None):
                newFriends= gPlusFriends
            else:
                newFriends = list(set(gPlusFriends) - set(json.loads(user.gPlusFriends)))
            for i in newFriends:
                if(i==gPlusUid): continue
                user2 = Users.objects(gPlusUid = i)
                if(user2):
                    user2= user2.get(0)
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
        user.facebook = facebookToken if facebookToken!=None else user.facebook
        user.googlePlus = gPlusToken if gPlusToken!=None else user.googlePlus
        user.isActivated = isActivated
        user.save()
        for user2 in subscribersList.values():
            self.addsubscriber(user, user2)
            self.addsubscriber(user2, user)
            self.publishFeedToUser(user.uid, user2, FEED_USER_JOINED, user.uid,None)

        return user
    
    def incrementLoginIndex(self, user):
        user.loginIndex+=1
        user.save()

    def addsubscriber(self, toUser, user):
        toUser.update(add_to_set__subscribers = user.uid)
        user.update(add_to_set__subscribedTo = toUser.uid)
        
    def removeSubscriber(self , fromUser , user):
        fromUser.update(pull__subscribers =user.uid)
        user.update(pull__subscribedTo =fromUser.uid)
        
    def activateUser(self, user, activationCode, deviceId):
        if(user.activationCode == activationCode):
            user.isActivated = True
            user.newDeviceId = deviceId
            user.deviceId = deviceId
            
    def getQuizDetails(self,quizId):
        return Quiz.objects(quizId=quizId).get(0)
    
    def getUserStats(self):
        return

    def addOrModifyTag(self,tag=None,isDirty=1):
        if(not tag):
            return None
        
        tagObj = Tags.objects(tag=tag)
        if(not tagObj):
            tagObj = Tags()
            tagObj.tag = tag.lower()
            tagObj.save()
        return tagObj
    
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
    
    def publishFeed(self, user, _type ,  message, message2=None):
        f = Feed()
        f.fromUid = user.uid
        f.message = message
        f.type = _type
        if(message2!=None):
            f.message2 = message2
        f.timestamp = HelperFunctions.toUtcTimestamp(datetime.datetime.now())
        f.save()
        #### move to tasks other server if possible
        for uid in user.subscribers:
            user = self.getUserByUid(uid)
            userFeed = UserFeed()
            userFeed.uidFeedIndex = uid+"_"+str(user.userFeedIndex.getAndIncrement(user).index)
            userFeed.feedMessage = f
            userFeed.save()
    
    def publishFeedToUser(self,fromUid ,  user, _type, message, message2):
        f = Feed()
        f.fromUid = fromUid
        f.type = _type
        f.message = message
        if(message2!=None):
            f.message2 = message2
        f.timestamp = HelperFunctions.toUtcTimestamp(datetime.datetime.now())
        f.save()
        
        userFeed = UserFeed()
        userFeed.uidFeedIndex= user.uid+"_"+str(user.userFeedIndex.getAndIncrement(user).index)
        userFeed.feedMessage = f
        userFeed.save()
                
    def insertInboxMessage(self,fromUser, toUser , message):
        inboxMessage = UserInboxMessages()
        inboxMessage.fromUid = fromUser.uid
        inboxMessage.toUid = toUser.uid
        inboxMessage.message = message
        inboxMessage.timestamp = datetime.datetime.now()
        inboxMessage.fromUid_LoginIndex = fromUser.uid +"_"+str(fromUser.loginIndex)
        inboxMessage.toUid_LoginIndex = toUser.uid+"_"+str(toUser.loginIndex)
        user1 , user2 = reorder(fromUser, toUser)
        #experimental only
        inboxMessage.fromUid_toUid_index = user1.uid+"_"+user2.uid+"_"+str(Uid1Uid2Index.getAndIncrementIndex(fromUser, toUser))
        inboxMessage.save()
        #if user is logged in , send him some notification
        
    def getNewBadges(self,userMaxTimestamp):
        return Badges.objects(modifiedTimestamp__gte = userMaxTimestamp)

        #experimental only
    def getRecentMessagesIfAny(self, user , afterTimestamp):
        messagesAfterTimestamp = UserInboxMessages.objects(toUid_LoginIndex = user.uid+"_"+str(user.loginIndex) , timestamp__gt = afterTimestamp)
        return messagesAfterTimestamp
        
    def userHasWon(self,user, quizId, xpGain):
        user.updateStats(quizId, xpGain)
        
    def getPeopleWithWhomUserConversed(self , user):
        #TODO: OPTIMIZE
        objs = Uid1Uid2Index.objects(uid1 = user.uid)
        uidList = [] 
        for i in objs:
            uidList.append(i.uid2)
        objs2 = Uid1Uid2Index.objects(uid2 = user.uid)
        for i in objs2:
            uidList.append(i.uid1)
        return uidList
    
    def addFeedback(self, user, message):
        feedback  = Feedback()
        feedback.user = user
        feedback.message = message
        feedback.save()
        
    
    def getGlobalLeaderboards(self,quizId):
        ret = {}
        count = 0
        for i in UserStats.objects(quizId= quizId).order_by("-xpPoints")[:20]:
            count+=1
            ret[i.uid]=[count , i.xpPoints]
        return ret
    
    def getLocalLeaderboards(self, quizId , user):
        xpPoints = user.getStats(quizId)
        xpPoints = xpPoints.get(quizId,0)
        ret = {}
        results  = UserStats.objects(quizId= quizId , xpPoints__gt=xpPoints).order_by("xpPoints")
        count = user_rank = len(results)+1
        for i in results[:10]:
            count -=1
            ret[i.uid]=[count , i.xpPoints]
        count = user_rank-1# to include user into this
        for i in UserStats.objects(quizId= quizId , xpPoints__lte=xpPoints).order_by("-xpPoints")[:10]:
            count +=1
            ret[i.uid]=[count , i.xpPoints]
            
        return ret
        
    def addBadges(self ,user , badgeIds):
        badges = Badges.objects(badgeId__in=badgeIds)
        name = user.name
        if(badges and len(badges)>0):
            badgeIds=[]
            for i in badges:
                user.update(add_to_set__badges = i.badgeId)
                badgeIds.append(i.badgeId)
            self.publishFeed(user, FEED_USER_WON_BADGES , json.dumps(badgeIds) , None)
            return True
        return False


    
    def getMessagesBetween(self,uid1, uid2 , toIndex=-1, fromIndex=0):
        uid1 , uid2 = reorderUids(uid1, uid2)
        if(toIndex == -1):
            r = Uid1Uid2Index.objects(uid1_uid2 = uid1+"_"+uid2)
            if(not r):
                return []
            r = r.get(0)
            toIndex = r.index
        messages = []
        i=toIndex+1
        count =0 
        while(i>fromIndex):
            tag = uid1+"_"+uid2+"_"+str(i)
            for message in UserInboxMessages.objects(fromUid_toUid_index = tag):
                messages.append(message)
                count+=1
            i-=1
            if(count>20):
                break 
            
        return messages
    
    def updateServerMap(self, serverMap):#{ id: ip:port}
        for serverId in serverMap:
            server = Servers.objects(serverId = serverId)
            if(server):
                server = server.get(0)
            else:
                server = Servers()
                server.serverId = serverId
                
            server.ip = serverMap.get(serverId)
            server.save()
        return True
    
    
    def isSecretKey(self, secretKey):
        return SecretKeys.objects(secretKey=secretKey)!=None
    
    def addSecretKey(self, secretKey):
        try:
            s = SecretKeys()
            s.secretKey = secretKey
            s.save()
        except:
            pass
        
    def config(self, key , value=None):
        config = Configs.objects(key=key)
        if(not config):
            config = Configs()
            config.key = key
            config.value = value
            config.save()
        else:
            config = config.get(0)
            if(value):
                config.value = value
                config.save()
        
        return config.value
            
            
def test_insertInboxMessages(dbUtils , user1, user2):
    dbUtils.insertInboxMessage(user2, user1, "hello 1 ")
    dbUtils.insertInboxMessage(user1, user2, "hello 12 ")
    dbUtils.insertInboxMessage(user2, user1, "hello 123 ")
    dbUtils.insertInboxMessage(user2, user1, "hello 1234 ")
    dbUtils.insertInboxMessage(user1, user2, "hello 1345 ")
    dbUtils.insertInboxMessage(user1, user2, "hello 1346 ")
    
    for i in dbUtils.getMessagesBetween(user1, user2, -1):
        print i.to_json()
    

def test_insertFeed(dbUtils , user1 , user2):
    dbUtils.publishFeed(user1, "hello man , how are you doing ? ")
    print dbUtils.getRecentUserFeed(user2)
    
    
        
#save user testing
if __name__ == "__main__":
    import Config
#    dbUtils = DbUtils(Config.dbServer) 
    #dbUtils.addQuestion("question1","What is c++ first program" , None, "abcd", "a", "asdasd" , "hello world dude!" , 10, 10 , ["c","c++","computerScience"])
    #dbUtils.addOrModifyQuestion(**{'questionType': 0, 'questionId': "1_8", 'hint': '', 'pictures': '', 'explanation': '', 'tags': 'movies, puri-jagannath,pokiri', 'isDirty': 1, 'questionDescription': 'how many movies did puri jagannath made in year 2007?', 'time': 10, 'answer': 4, 'xp': 10, 'options': '4 , 7 , 1 , 3 , 2'})
    
    
#    user = json.loads('{"uid":"110040773460941325994","deviceId":"31e7d9178c3ca41f","emailId":"ramasolipuram@gmail.com","gender":"female","googlePlus":"ya29.bwDeBz20zufq7EsAAABrdZMKlgQzN92fxmcJNfFfWITpqkWp1o28YO4ZjOsAzNSurK-2NPS-lZ2xXE1326uxKdtorm8wn7dh4m-G9NT1nYfIO1ebw8jcARYscDIi-g","name":"Rama Reddy","pictureUrl":"https://lh3.googleusercontent.com/-TyulralhJFw/AAAAAAAAAAI/AAAAAAAAA9o/8KyUnpS-j_Y/photo.jpg?sz\\u003d200","isActivated":false,"createdAt":0.0,"birthday":0.0}')
#    userIp = "192.168.0.10"
#    userObject = dbUtils.registerUser( user["name"], user["deviceId"], user["emailId"], user.get("pictureUrl",None),user.get("coverUrl",None),user.get("birthday",None),user.get("gender",None),user.get("place",None),userIp , user.get("facebook",None),user.get("googlePlus",None),True)
                
    
#     user1 = dbUtils.registerUser("Abhinav reddy", "1234567", "abhinavabcd@gmail.com", "http://192.168.0.10:8081/images/kajal/kajal1.jpg", "", 0.0, "male", "india", "192.168.0.10", "something else", None, True)
#     user2 = dbUtils.registerUser("vinay reddy", "1234547", "vinaybhargavreddy@gmail.com", "http://192.168.0.10:8081/images/kajal/kajal2.jpg", "", 0.0, "male", "india", "192.168.0.10", "something else", None, True)
#     dbUtils.addsubscriber(user1, user2)
#     dbUtils.incrementLoginIndex(user1)
#     dbUtils.incrementLoginIndex(user2)
#     test_insertFeed(dbUtils , user1, user2)
    
#    test_insertInboxMessages(dbUtils)
    
    pass

#edit user

#add message of user

