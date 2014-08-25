from mongoengine import *
import random
import string
import datetime
import time
import bson
from Config import *
import itertools

db =connect('quizApp')
#db.dropDatabase('ideaVault')


def reorder(user1, user2):
    if(user1.uid < user2.uid):#swap maintain same order always
        temp = user1
        user1 = user2
        user2 = temp
    return user1, user2

class Uid1Uid2Index(Document):
    uid1_uid2 = StringField(unique=True)
    index = IntField(default=0)
    uid1Login = IntField()
    uid2Login = IntField()
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
            saveObj = True
        else:
            obj = obj.get(0)
        if(obj.uid1Login!=user1.loginIndex or obj.uid2Login!=user2.loginIndex): # totally new sessions
            obj.index+=1
            obj.uid1Login = user1.loginIndex
            obj.uid2Login = user2.loginIndex
            saveObj = True
            
        if(saveObj):
            obj.save()

        return obj.index

class UserInboxMessages(Document):
    fromUid_toUid_index = StringField()#tag to identify block of messages
    fromUid = StringField()
    toUid = StringField()
    message = StringField()
    timestamp = DateTimeField()
    fromUid_LoginIndex = StringField() #uid1_LOGININDEX
    toUid_LoginIndex = StringField() #uid2_LOGININDEX
    
    @staticmethod
    def insertMessage(fromUser, toUser , message):
        inboxMessage = UserInboxMessages()
        inboxMessage.fromUid = fromUser.uid
        inboxMessage.toUid = toUser.uid
        inboxMessage.message = message
        inboxMessage.timestamp = datetime.datetime.now()
        inboxMessage.fromUid_LoginIndex = fromUser.uid +"_"+str(fromUser.loginIndex)
        inboxMessage.toUid_LoginIndex = toUser.uid+"_"+str(toUser.loginIndex)
        user1 , user2 = reorder(fromUser, toUser)
        inboxMessage.fromUid_toUid_index = user1.uid+"_"+user2.uid+"_"+str(Uid1Uid2Index.getAndIncrementIndex(fromUser, toUser))
        inboxMessage.save()
        #if user is logged in , send him some notification
        
 
    @staticmethod
    def getNewMessagesBetween(user1, user2 , index1, index2):
        user1 , user2 = reorder(user1, user2)
        if(index2 == -1):
            r = Uid1Uid2Index.objects(uid1_uid2 = user1.uid+"_"+user2.uid)
            if(not r):
                return None
            r = r.get(0)
            index2 = r.index
        messages = []
        for i in range(index1+1 , index2+1):
            tag = user1.uid+"_"+user2.uid+"_"+str(i)
            for i in UserInboxMessages.objects(fromUid_toUid_index = tag):
                messages.append(i)
        return messages

class UserFeed(Document):
    uidLoginIndex = StringField()#uid_LOGININDEX
    feedMessage = ReferenceField('Feed')
    
        
class Feed(Document):
    fromUid = StringField()
    message = StringField()
        
    @staticmethod
    def publishFeed(user , message):
        f = Feed()
        f.fromUid = user.uid
        f.message = message
        f.save()
        #### move to tasks other server if possible
        for fuser in user.subscribers:
            userFeed = UserFeed()
            userFeed.uidLoginIndex = fuser.uid+"_"+fuser.loginIndex
            userFeed.feedMessage = f
            userFeed.save()
    
    
    
    

class UserSolvedIds(Document):
    uid = StringField()
    uid2 = StringField()
    type = StringField() #WIN , LOSE , CHALLENGE , 
    solvedId= StringField()
    points = StringField()
    questionIdToPointsMap = DictField()


    
class UserBadges():
    uid = StringField(unique=True)
    badgeId = IntField()
    createdTimeStamp = DateTimeField()

class Users(Document):
    uid = StringField(unique=True)
    name = StringField()
    status = StringField()
    deviceId = StringField(required = True)
    emailId = EmailField(required=True)
    pictureUrl = StringField()#cdn link
    coverUrl = StringField()
    birthday = FloatField()
    gender = StringField()
    place = StringField()
    country = StringField(default=None)
    ipAddress = StringField()
    isActivated = BooleanField(default = False)
    stats = DictField()#quiz to xp
    winsLosses = DictField() #quizId to [wins , totals]

    activationKey = StringField()
    gcmRegId = StringField()
    
    badges = ListField(IntField())
    loginIndex = IntField()
    googlePlus = StringField()
    facebook = StringField()
    activationCode = StringField()
    newDeviceId = StringField()
    createdAt = DateTimeField()
    friends = ListField(StringField())
    subscribers = ListField(StringField())
    
    
class Tags(Document):
    tag = StringField(unique=True)

class Badges():
    badgeId = IntField()
    name = StringField()
    description = StringField()
    modifiedTimeStamp = DateTimeField()
    @staticmethod
    def getNewBadges(userMaxTimeStamp):
        return Badges.objects(modifiedTimeStamp__gte = userMaxTimeStamp)

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



class TopicMaxQuestions(Document):
    categoryTag = StringField(unique=True)
    max = IntField(default=0)
    unused = ListField(IntField())
    @staticmethod
    def getNewId(tag):
        c = TopicMaxQuestions.objects(categoryTag = tag)
        if(not c):
            c = TopicMaxQuestions(categoryTag = tag, max=1)
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
        c = TopicMaxQuestions.objects(categoryTag = tag).get(0)
        if(c.unused):
            c.unused.append(_id)
        else:
            c.unused = [_id]
        c.save()



    @staticmethod
    def getMax(tag):
        c = TopicMaxQuestions.objects(categoryTag = tag)
        if(not c):
            return 0
        else:
            return c.max


class Categories(Document):
    categoryId = StringField(unique=True)
    shortDescription = StringField()
    description = StringField()
    quizList = ListField(StringField())
    assetPath = StringField()
    type = StringField()
    modifiedTimestamp = DateTimeField()
    
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["quizList"] = bson.json_util.dumps(self.quizList)
        sonObj["modifiedTimestamp"] = toUtcTimestamp(self.modifiedTimestamp)
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
    
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["tags"] = bson.json_util.dumps(self.tags)
        sonObj["modifiedTimestamp"] = toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)

def getTagsFromString(s,toLower=True):
    ret = []
    a = s.split("\n")
    for i in a:
        for j in i.split(","):
            t = j.strip()
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
            if(toLower):
                t = t.lower()
            ret.append(t)
    return ret

class DbUtils():

    def __init__(self):
        pass

    def addOrModifyCategory(self, categoryId=None, shortDescription=None, description=None, quizList=None,isDirty=1):
        categoryId = str(categoryId)
        if(isinstance(quizList,str)):
            quizList = getListFromString(quizList)
            
        c= Categories.objects(categoryId = categoryId)
        if(c):
            c= c.get(0)
        else:
            c = Categories()
            c.categoryId = categoryId
        c.shortDescription = shortDescription
        c.description = description
        quizListTemp = []
        for i in c.quizList:
            quizListTemp.append(i.quizId)
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

    def addOrModifyQuiz(self, quizId=None,quizType=None, name=None, tags=None, nQuestions=None,nPeople=None,isDirty=1):
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
        q.nPeople = nPeople
        q.modifiedTimestamp = datetime.datetime.now()
        q.save()
        return q

    def addQuestion(self,questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags):
        questionId = str(questionId)
        question = Questions.objects(questionId=questionId)
        
        if(len(question)>0):
            q = question=question.get(0)
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
            print tagsAll
            print tagsAll2
    
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
        print questionId, questionType , questionDescription, pictures, options, answer, hint, explanation, time, xp, tags
        self.addQuestion(questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags)
        return True
        

    def getRandomQuestions(self,quiz):
        questions = []
        count = 0
        quiz.tags
        while(count<quiz.nQuestions):
            questions.append(None)

    def getAllCategories(self,modifiedTimestamp):
        return Categories.objects(modifiedTimestamp__gte = modifiedTimestamp)
    
    def getAllQuizzes(self,modifiedTimestamp):
        return Quiz.objects(modifiedTimestamp__gte = modifiedTimestamp)
    

    def setUserGCMRegistationId(self, user , gcmRedId):
        user.gcmRegId = gcmRedId
        user.save()
        return


    def registerUser(self, uid, name, deviceId, emailId, pictureUrl, coverUrl , birthday, gender, place, ipAddress,facebookToken=None , gPlusToken=None, isActivated=False):
        user = Users.objects(uid=uid)
        if(user):
            user = user.get(0)
        else:
            user = Users()
            user.stats = {}
            user.winsLosses = {}
            user.activationKey = ""
            user.badges = []
        
        user.newDeviceId = deviceId
        user.uid = uid
        user.name = name
        user.deviceId = deviceId
        user.emailId = emailId
        user.pictureUrl = pictureUrl
        user.coverUrl = coverUrl
        user.birthday = birthday
        user.gender = gender
        user.place = place
        user.ipAddress = ipAddress
        user.facebook = facebookToken
        user.loginIndex = 0
        user.googlePlus = gPlusToken
        user.isActivated = isActivated
        user.createdAt = datetime.datetime.now()
        user.save()
        return user
    
    def activateUser(self, user, activationCode, deviceId):
        if(user.activationCode == activationCode):
            user.isActivated = True
            user.newDeviceId = deviceId
            user.deviceId = deviceId
            
    def getQuizDetails(self,quizId):
        return Quiz.objects(quizId=quizId)
    
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
            

dbUtils = DbUtils()





def test_insertInboxMessages():
    user1 , user2 = Users.objects(uid="qa1").get(0),Users.objects(uid="qa2").get(0)
    UserInboxMessages.insertMessage(user1, user2, "how are you doing")
    for i in UserInboxMessages.getNewMessagesBetween(user1, user2, 0, -1):
        print i.to_json()
    
def test_insetFeed():
    user1 , user2 = Users.objects(uid="qa1").get(0),Users.objects(uid="qa2").get(0)
    UserInboxMessages.insertMessage(user1, user2, "how are you doing")
    for i in UserInboxMessages.getNewMessagesBetween(user1, user2, 0, -1):
        print i.to_json()
    


#save user testing
if __name__ == "__main__":
    #dbUtils.addQuestion("question1","What is c++ first program" , None, "abcd", "a", "asdasd" , "hello world dude!" , 10, 10 , ["c","c++","computerScience"])
    #dbUtils.addOrModifyQuestion(**{'questionType': 0, 'questionId': "1_8", 'hint': '', 'pictures': '', 'explanation': '', 'tags': 'movies, puri-jagannath,pokiri', 'isDirty': 1, 'questionDescription': 'how many movies did puri jagannath made in year 2007?', 'time': 10, 'answer': 4, 'xp': 10, 'options': '4 , 7 , 1 , 3 , 2'})
#     dbUtils.registerUser("qa1", "Abhinav reddy", "1234567", "abhinavabcd@gmail.com", "http://192.168.0.10:8081/images/kajal/kajal1.jpg", "", 0.0, "male", "india", "192.168.0.10", "something else", None, True)
#     dbUtils.registerUser("qa2", "vinay reddy", "1234547", "vinaybhargavreddy@gmail.com", "http://192.168.0.10:8081/images/kajal/kajal2.jpg", "", 0.0, "male", "india", "192.168.0.10", "something else", None, True)
#    test_insertInboxMessages()
    pass

#edit user

#add message of user









