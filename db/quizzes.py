'''
Created on Jul 24, 2015

@author: abhinav
'''


from mongoengine import Document , StringField,ListField , DateTimeField , IntField

from db.utils import getListFromString , getTagsFromString
import HelperFunctions
import datetime
import bson
from db.user import UserStats

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
    @staticmethod
    def addOrModifyCategory(categoryId=None, shortDescription=None, description=None, assetPath=None, bgAssetPath=None, titleAssetPath=None,  quizList=None,isDirty=1):
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

    
    @staticmethod
    def getAllCategories(modifiedTimestamp):
        return Categories.objects(modifiedTimestamp__gt = modifiedTimestamp)    
    
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
    
    @staticmethod
    def addOrModifyQuiz(quizId=None,quizType=None, name=None, assetPath=None, tags=None, nQuestions=None,nPeople=None,isDirty=1):
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


    @staticmethod
    def getAllQuizzes(self,modifiedTimestamp):
        return Quiz.objects(modifiedTimestamp__gte = modifiedTimestamp)
    
    @staticmethod
    def getQuizDetails(quizId):
        return Quiz.objects(quizId=quizId).get(0)
    
    
    @staticmethod
    def getGlobalLeaderboards(quizId):
        ret = {}
        count = 0
        for i in UserStats.objects(quizId=quizId).order_by("-xpPoints")[:20]:
            count += 1
            ret[i.uid] = [count , i.xpPoints]
        return ret
    
    @staticmethod
    def getLocalLeaderboards(quizId , user):
        xpPoints = user.getStats(quizId)
        xpPoints = xpPoints.get(quizId, 0)
        ret = {}
        results = UserStats.objects(quizId=quizId , xpPoints__gt=xpPoints).order_by("xpPoints")
        count = user_rank = len(results) + 1
        for i in results[:10]:
            count -= 1
            ret[i.uid] = [count , i.xpPoints]
        count = user_rank - 1  # to include user into this
        for i in UserStats.objects(quizId=quizId , xpPoints__lte=xpPoints).order_by("-xpPoints")[:10]:
            count += 1
            ret[i.uid] = [count , i.xpPoints]
            
        return ret
    
    
    def toJson(self):
        sonObj = self.to_mongo()
        sonObj["tags"] = bson.json_util.dumps(self.tags)
        sonObj["modifiedTimestamp"] = HelperFunctions.toUtcTimestamp(self.modifiedTimestamp)
        return bson.json_util.dumps(sonObj)