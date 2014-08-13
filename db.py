from mongoengine import *
import random
import string
import datetime
import time
import bson
from Config import *
import itertools

db =connect('quizDoctor')
#db.drop_database('ideaVault')


class UserSolvedIds(Document):
    uid = StringField()
    solved_id= StringField()

class UserStats(EmbeddedDocument):
    badges = ListField(StringField())
    stats = DictField()#quizType to xp
    wins_losses = DictField() #quizType to [wins , totals]

class User(Document):
    uid = StringField(unique=True)
    deviceId = StringField(required = True)
    emailId = EmailField(required=True)
    picture = StringField()#cdn link
    isActivated = BooleanField(default = False)
    status = StringField()
    gcmRegId = StringField()
    userStats = EmbeddedDocument(UserStats)
    
class Questions(Document):
    question_id = StringField(unique=True)
    question_type = IntField(default = 0)
    question_description = StringField()# special formatted inside the description itself
    pictures = ListField(StringField())
    options = StringField()
    answer = StringField()
    hint = StringField()
    explanation = StringField()
    time = IntField()
    xp = IntField()
    tags_all_subjects = ListField(StringField()) #categoryname_index , ....
    tags_all_index = ListField(StringField())
    tags=ListField(StringField())
   
class TopicMaxQuestions(Document):
    category_tag = StringField(unique=True)
    max = IntField(default=0)
    unused = ListField(IntField())
    @staticmethod
    def getNewId(tag):
        c = TopicMaxQuestions.objects(category_tag = tag)
        if(not c):
            c = TopicMaxQuestions(category_tag = tag, max=1)
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
        c = TopicMaxQuestions.objects(category_tag = tag).get(0)        
        if(c.unused):
            c.unused.append(id)
        else:
            c.unused = [id]
        c.save()
        
        
    
    @staticmethod
    def getMax(tag):
        c = TopicMaxQuestions.objects(category_tag = tag)
        if(not c):
            return 0
        else:
            return c.max


class CategoriesOfTopics(Document):
    category_id = StringField()
    shortDescription = StringField()
    description = StringField()
    quiz_list = ListField('Quiz')
    modified_timestamp = DateTimeField()
    
class Quiz(Document):
    quiz_id = IntField(unique= True)
    quiz_type = StringField()
    name = StringField()
    tags = ListField(StringField())
    n_questions = IntField()
    n_people = IntField()
    modified_timestamp = DateTimeField()
    
class DbUtils():
    
    def __init__(self):
        pass
    
    def getQuizDetails(self,quiz_id):
        return Quiz.objects(quiz_id=quiz_id)
    
    
    def modifyCategory(self, category_id, shortDescription, description , quiz_list_new):
        c= CategoriesOfTopics.objects(category_id = category_id)
        if(c):
            c= c.get(0)
        else:
            c = CategoriesOfTopics()
            c.category_id = category_id
        c.shortDescription = shortDescription
        c.description = description
        quiz_list = []
        for i in c.quiz_list:
            quiz_list.append(i.quiz_id)
        add_quiz_list = set(quiz_list_new)-set(quiz_list)
        remove_quiz_list = set(quiz_list)-set(quiz_list_new)
        for i in remove_quiz_list:
            c.quiz_list.remove(i)
            
        for i in add_quiz_list:
            quiz = Quiz.objects(quiz_id=i)
            if(quiz):
                c.quiz_list.append(quiz.get(0))
        
        c.modified_timestamp = datetime.datetime.now()
        c.save()
            
    def modifyQuiz(self, quiz_id ,quiz_type, name , tags , n_questions ,n_people):
        q = Quiz.objects(quiz_id = quiz_id)
        if(q):
            q = q.get(0)
        else:
            q = Quiz()
            
        q.quiz_id = quiz_id
        q.quiz_type = quiz_type
        q.name = name
        q.tags = tags
        q.n_questions = n_questions
        q.n_people = n_people
        q.modified_timestamp = datetime.datetime.now()
        q.save()
        
    def addQuestion(self,question_id, question_type ,question_description , pictures, options, answer, hint , explanation , time, xp , tags):
        question = Questions.objects(question_id=question_id)
        tags.sort()
        if(len(question)>0):
            return
        tags_all = []
        tags_all_2 = []
        for L in range(1, len(tags)+1):
            for subset in itertools.combinations(tags, L):
                full_tag = "_".join(sorted(subset))
                max = TopicMaxQuestions.getNewId(full_tag)
                tags_all.append(full_tag+"_"+str(max))
                tags_all_2.append(full_tag)
        print tags_all
        print tags_all_2
        
        q = Questions()
        q.question_id = question_id
        q.question_type = question_type
        q.question_description = question_description
        q.pictures = pictures
        q.options = options
        q.answer = answer
        q.hint = hint
        q.explanation=explanation
        q.time=time
        q.xp = xp
        q.tags_all_subjects= tags_all_2
        q.tags_all_index= tags_all
        q.tags = tags
        q.save()
    
    def modifyQuestion(self,question_id,  newTags):
        question = Questions.objects(question_id=question_id).get(0)
        #TODO add all others
        tags =question.tags[:]
        if(set(tags) != set(newTags)):
            newTags.sort()
            for i in question.tags_all_index:
                tagSet= i.split("_")
                id = tagSet.pop()
                tagSet.sort()
                tag = "_".join(tagSet)
                TopicMaxQuestions.addToUnUsedId(tag, id)
            
            tags_all = []
            tags_all_2 = []
            tags= newTags
            for L in range(1, len(tags)+1):
                for subset in itertools.combinations(tags, L):
                    full_tag = "_".join(sorted(subset))
                    max = TopicMaxQuestions.getNewId(full_tag)
                    tags_all.append(full_tag+"_"+str(max))
                    tags_all_2.append(full_tag)
            
            question.tags_all_subjects = tags_all_2
            question.tags_all_index = tags_all
            question.tags = newTags
            question.save()
            
    def getRandomQuestions(self,quizType):
        questions = []
        count = 0
        while(count<quizType.n_questions):
            questions.append(None)
        
    def getAllQuizzes(self,modified_timestamp):
        return CategoriesOfTopics.objects(modifiedTimeStamp__gte = modified_timestamp)
        
    def setUserGCMRegistationId(self, user , gcmRedId):
        user.gcmRegId = gcmRedId
        user.save()
        return
    
dbUtils = DbUtils()

#save user testing
if __name__ == "__main__":
    dbUtils.addQuestion("question_1","What is c++ first program" , None, "abcd", "a", "asdasd" , "hello world dude!" , 10, 10 , ["c","c++","computerScience"])
    dbUtils.modifyQuestion("question_1", ["c","c++","computerScience"])
    dbUtils.modifyQuestion("question_1", ["c","hello","computerScience"])
    pass


#edit user

#add message of user


    



    
    
    
    
