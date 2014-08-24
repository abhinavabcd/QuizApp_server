from mongoengine import *
import random
import string
import datetime
import time
import bson
from Config import *
import itertools

db =connect('quizDoctor')
#db.dropDatabase('ideaVault')


class UserSolvedIds(Document):
    uid = StringField()
    uid2 = StringField()
    type = StringField()
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
    
    isActivated = BooleanField(default = False)
    stats = DictField()#quiz to xp
    winsLosses = DictField() #quiz to [wins , totals]

    activationKey = StringField()
    gcmRegId = StringField()
    
    badges = ListField(IntField())
    
    googlePlus = StringField()
    facebook = StringField()
    activationCode = StringField()
    newDeviceId = StringField()

class Tags():
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
    assetPath = StringField()
    quizList = ListField(StringField())
    type = StringField()
    modifiedTimestamp = DateTimeField()

class Quiz(Document):
    quizId = StringField(unique= True)
    quizType = StringField()
    name = StringField()
    shortDescription = StringField()
    assetPath = StringField()
    tags = ListField(StringField())
    nQuestions = IntField()
    nPeople = IntField()
    modifiedTimestamp = DateTimeField()


def getListFromString(s):
    ret = []
    a = s.split("\n")
    for i in a:
        for j in i.split(","):
            ret.append(j.strip())
            

class DbUtils():

    def __init__(self):
        pass

    def addOrModifyCategory(self, categoryId=None, shortDescription=None, description=None, quizListNew=None,isDirty=1):
        if(isinstance(quizListNew,str)):
            quizListNew = getListFromString(quizListNew)
            
        c= Categories.objects(categoryId = categoryId)
        if(c):
            c= c.get(0)
        else:
            c = Categories()
            c.categoryId = categoryId
        c.shortDescription = shortDescription
        c.description = description
        quizList = []
        for i in c.quizList:
            quizList.append(i.quizId)
        addQuizList = set(quizListNew)-set(quizList)
        removeQuizList = set(quizList)-set(quizListNew)
        for i in removeQuizList:
            c.quizList.remove(i)

        for i in addQuizList:
            quiz = Quiz.objects(quizId=i)
            if(quiz):
                c.quizList.append(quiz.get(0).quizId)

        c.modifiedTimestamp = datetime.datetime.now()
        c.save()

    def addOrModifyQuiz(self, quizId=None,quizType=None, name=None, tags=None, nQuestions=None,nPeople=None,isDirty=1):
        if(isinstance(tags,str)):
            tags = getListFromString(tags)
        
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
            tags=getListFromString(tags)
            for tag in tags:
                tag =  Tags.objects(tag=tag)
                if(not tag or len(tag)==0):
                    print "Tags Not found in Db"
                    return False
               
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

    def getAllQuizzes(self,modifiedTimestamp):
        return Categories.objects(modifiedTimeStamp__gte = modifiedTimestamp)

    def setUserGCMRegistationId(self, user , gcmRedId):
        user.gcmRegId = gcmRedId
        user.save()
        return


    def registerUser(self, uid, name, deviceId, emailId, pictureUrl, coverUrl , birthday, gender, place, facebookToken=None , gPlusToken=None, isActivated=False):
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
        user.facebook = facebookToken
        user.googlePlus = gPlusToken
        user.isActivated = isActivated
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
        
        tag = Tags.objects(tag)
        if(not tag):
            tag = Tags()
            tag.tag = tag
            tag.save()
        return tag
            

dbUtils = DbUtils()

#save user testing
if __name__ == "__main__":
    #dbUtils.addQuestion("question1","What is c++ first program" , None, "abcd", "a", "asdasd" , "hello world dude!" , 10, 10 , ["c","c++","computerScience"])
    dbUtils.addOrModifyQuestion(**{'questionType': 0, 'questionId': "1_8", 'hint': '', 'pictures': '', 'explanation': '', 'tags': 'movies, puri-jagannath,pokiri', 'isDirty': 1, 'questionDescription': 'how many movies did puri jagannath made in year 2007?', 'time': 10, 'answer': 4, 'xp': 10, 'options': '4 , 7 , 1 , 3 , 2'})
    pass


#edit user

#add message of user









