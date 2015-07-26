'''
Created on Jul 24, 2015

@author: abhinav
'''


from mongoengine import Document , StringField, EmailField, BooleanField, FloatField , ListField , DateTimeField , IntField , ReferenceField
import json
from db.utils import getTagsFromString, getListFromString

import itertools
import random

class Tags(Document):
    tag = StringField(unique=True)
    
    @staticmethod
    def addOrModifyTag(tag=None,isDirty=1):
        if(not tag):
            return None
        
        tagObj = Tags.objects(tag=tag)
        if(not tagObj):
            tagObj = Tags()
            tagObj.tag = tag.lower()
            tagObj.save()
        return tagObj
    


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
    
    
    
    
    @staticmethod
    def addQuestion(questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags):
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
            
        
    @staticmethod
    def addOrModifyQuestion(questionId=None, questionType=0 , questionDescription=None, pictures=None, options=None, answer=None, hint=None, explanation=None, time=None, xp=None, tags=None ,isDirty=1):
        if(isinstance(tags,str)):
            tags=getTagsFromString(tags)
            for tag in tags:
#                 tag =  Tags.objects(tag=tag)
#                 if(not tag or len(tag)==0):
#                     print "Tags Not found in Db"
#                     return False
                ############FOR NOW INITIAL PHASE
                Tags.addOrModifyTag(tag)

               
        if(isinstance(pictures,str)):
            pictures=getListFromString(pictures)
        answer = str(answer)
        #print questionId, questionType , questionDescription, pictures, options, answer, hint, explanation, time, xp, tags
        Questions.addQuestion(questionId, questionType ,questionDescription , pictures, options, answer, hint , explanation , time, xp , tags)
        return True
    
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
    
    
                

    @staticmethod
    def getRandomQuestions( quiz):
        fullTag = "_".join(sorted(quiz.tags))
        questionsCount = quiz.nQuestions
        
        count =  TopicMaxQuestions.getTopicMaxCount(fullTag)
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
    
    @staticmethod
    def getQuestionsById(questionIds):
        return Questions.objects(questionId__in = questionIds)

'''
Maintains how many questions are there for each combination of tags
maintain an unused number list , so when adding a new question the unused number is used
it says that there are questions with ids , midexTag_1, mixedTag_2.....mixedTag_max
'''
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
    
    @staticmethod
    def getTopicMaxCount(fullTag):
        return TopicMaxQuestions.getMax(fullTag)



    @staticmethod
    def getQuestionsById(self, questionIds):
        return Questions.objects(questionId__in = questionIds)
# class Subscribers(Document):
#     user  = ReferenceField('Users')
#     user2 = ReferenceField('User')
