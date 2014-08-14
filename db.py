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
    solvedId= StringField()

class UserStats(EmbeddedDocument):
    badges = ListField(StringField())
    stats = DictField()#quizType to xp
    winsLosses = DictField() #quizType to [wins , totals]

class User(Document):
    uid = StringField(unique=True)
    deviceId = StringField(required = True)
    emailId = EmailField(required=True)
    picture = StringField()#cdn link
    isActivated = BooleanField(default = False)
    status = StringField()
    gcmRegId = StringField()
    userStats = EmbeddedDocument(UserStats)
    googlePlus = StringField()
    facebook = StringField()
    activationCode = StringField()
    newDeviceId = StringField()

class Tag():
    tag = StringField(unique=True)


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
    def addToUnUsedId(tag, id):
        c = TopicMaxQuestions.objects(categoryTag = tag).get(0)
        if(c.unused):
            c.unused.append(id)
        else:
            c.unused = [id]
        c.save()



    @staticmethod
    def getMax(tag):
        c = TopicMaxQuestions.objects(categoryTag = tag)
        if(not c):
            return 0
        else:
            return c.max


class CategoriesOfTopics(Document):
    categoryId = StringField()
    shortDescription = StringField()
    description = StringField()
    quizList = ListField('Quiz')
    modifiedTimestamp = DateTimeField()

class Quiz(Document):
    quizId = StringField(unique= True)
    quizType = StringField()
    name = StringField()
    tags = ListField(StringField())
    nQuestions = IntField()
    nPeople = IntField()
    modifiedTimestamp = DateTimeField()

class DbUtils():

    def __init__(self):
        pass

    

    def modifyCategory(self, categoryId, shortDescription, description , quizListNew):
        c= CategoriesOfTopics.objects(categoryId = categoryId)
        if(c):
            c= c.get(0)
        else:
            c = CategoriesOfTopics()
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
                c.quizList.append(quiz.get(0))

        c.modifiedTimestamp = datetime.datetime.now()
        c.save()

    def modifyQuiz(self, quizId ,quizType, name , tags , nQuestions ,nPeople):
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

    def addQuestion(self,questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags):
        question = Questions.objects(questionId=questionId)
        tags.sort()
        if(len(question)>0):
            return
        tagsAll = []
        tagsAll2 = []
        for L in range(1, len(tags)+1):
            for subset in itertools.combinations(tags, L):
                fullTag = "_".join(sorted(subset))
                max = TopicMaxQuestions.getNewId(fullTag)
                tagsAll.append(fullTag+"_"+str(max))
                tagsAll2.append(fullTag)
        print tagsAll
        print tagsAll2

        q = Questions()
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
        q.tagsAllSubjects= tagsAll2
        q.tagsAllIndex= tagsAll
        q.tags = tags
        q.save()

    def modifyQuestion(self,questionId,  newTags):
        question = Questions.objects(questionId=questionId).get(0)
        #TODO add all others
        tags =question.tags[:]
        if(set(tags) != set(newTags)):
            newTags.sort()
            for i in question.tagsAllIndex:
                tagSet= i.split("_")
                id = tagSet.pop()
                tagSet.sort()
                tag = "_".join(tagSet)
                TopicMaxQuestions.addToUnUsedId(tag, id)

            tagsAll = []
            tagsAll2 = []
            tags= newTags
            for L in range(1, len(tags)+1):
                for subset in itertools.combinations(tags, L):
                    fullTag = "_".join(sorted(subset))
                    max = TopicMaxQuestions.getNewId(fullTag)
                    tagsAll.append(fullTag+"_"+str(max))
                    tagsAll2.append(fullTag)

            question.tagsAllSubjects = tagsAll2
            question.tagsAllIndex = tagsAll
            question.tags = newTags
            question.save()

    def getRandomQuestions(self,quizType):
        questions = []
        count = 0
        while(count<quizType.nQuestions):
            questions.append(None)

    def getAllQuizzes(self,modifiedTimestamp):
        return CategoriesOfTopics.objects(modifiedTimeStamp__gte = modifiedTimestamp)

    def setUserGCMRegistationId(self, user , gcmRedId):
        user.gcmRegId = gcmRedId
        user.save()
        return


    def registerUserFromGooglePlus(self, uid, deviceId, emailId, picture):
        user = User()
        user.uid = uid
        user.deviceId = deviceId
        user.emailId = emailId
        user.picture = picture
        user.isActivated = True
        user.userStats = stats= UserStats()
        user.googlePlus ="google"
        user.save()

    def registerUserWithFacebook(self, uid, deviceId, emailId, picture):
        user = User()
        user.uid = uid
        user.deviceId = deviceId
        user.emailId = emailId
        user.picture = picture
        user.isActivated = True
        user.userStats = stats= UserStats()
        user.facebook ="facebook"
        user.save()

    def registerUser(self , uid, deviceId, emailId, picture):
        user = User()
        user.uid = uid
        user.deviceId = deviceId
        user.emailId = emailId
        user.picture = picture
        user.isActivated = False
        user.userStats = stats= UserStats()
        user.newDeviceId = deviceId
        user.activationCode = generateKey(6)
        user.save()

    def activateUser(self, user, activationCode, deviceId):
        if(user.activationCode == activationCode):
            user.isActivated = True
            user.newDeviceId = deviceId

    def getQuizDetails(self,quizId):
        return Quiz.objects(quizId=quizId)
    
    def getUserStats(self):
        return


dbUtils = DbUtils()

#save user testing
if __name__ == "__main__":
    dbUtils.addQuestion("question1","What is c++ first program" , None, "abcd", "a", "asdasd" , "hello world dude!" , 10, 10 , ["c","c++","computerScience"])
    dbUtils.modifyQuestion("question1", ["c","c++","computerScience"])
    dbUtils.modifyQuestion("question1", ["c","hello","computerScience"])
    pass


#edit user

#add message of user









