
from mongoengine import Document , StringField, EmailField, BooleanField, FloatField , ListField , DateTimeField , IntField , ReferenceField
from Constants import WIN_TYPE, RANDOM_USER_TYPE
import datetime



class UserClashHistory(Document):
    uid1_uid2 = StringField()
    quizId = StringField()
    wins = IntField(default = 0)
    losses = IntField(default = 0)
    ties = IntField(default=0)
    meta = {
        'indexes': [
                    'uid1_uid2',
                    ('uid1_uid2' , 'quizId')
        ]
    }
    

##### contains all quiz history of all games , offline online
class UserGamesHistory(Document):
    uid = StringField()
    uid2 = StringField()
    uid_uid2 = StringField()
    type = StringField() #NORMAL , CHALLENGE , 
    gameType = IntField()
    solvedId= StringField() # to indentify exactly what type of quiz between what users
    points = IntField()
    userAnswers1 = StringField()
    userAnswers2 = StringField()
    timestamp = DateTimeField()
    meta = {
        'indexes': [
                    'uid_uid2',
                    'solvedId'
                ]
        }
    
    '''
    this is called by both users after the quiz ends
    '''    
    @staticmethod
    def updateQuizWinStatus(user, quizId , xpGain , winStatus, uid2 , userAnswers1 , userAnswers2 , gameType=RANDOM_USER_TYPE):
        if(user.uid > uid2 or uid2[:2]=="00"): #or uid2 is bot or # with greater user id updates the table
            s = UserGamesHistory()
            s.uid = user.uid
            s.uid2 = uid2
            s.uid_uid2 = user.uid+"_"+uid2
            s.solvedId = user.uid+"_"+uid2+"_"+quizId
            #s.type = WIN_TYPE #WIN , LOSE , CHALLENGE , 
            s.gameStatus = winStatus
            s.points = xpGain
            s.gameType = gameType
            s.userAnswers1 = userAnswers1
            s.userAnswers2 = userAnswers2
            s.timestamp = datetime.datetime.now()

        user.updateStats(quizId, xpGain)
        user.updateWinsLosses(quizId, winStatus = winStatus)
    
    @staticmethod
    def getGamesBetweenUsers(uid1 , uid2 , quizId , fromIndex=0):
        c= ""
        if(uid1 > uid1 or uid2[:2]=='00'):
            c = uid1+"_"+uid2
        else:
            c = uid2+"_"+uid1
        if(quizId):
            return UserGamesHistory.objects(solvedId = c+"_"+quizId)[fromIndex:fromIndex+50]
        else:
            UserGamesHistory.objects(uid_uid2 = c)[fromIndex:fromIndex+50]

    
    @staticmethod
    def getWinsLossesBetweenUsers(uid1 , uid2, quizId, fromIndex=0):
        c= ""
        wins_lossed = [0,0,0]
        reversed = False
        if(uid1 > uid1 or uid2[:2]=='00'):
            c = uid1+"_"+uid2
        else:
            reversed = True
            c = uid2+"_"+uid1
        
        if(quizId):
            ret =  UserClashHistory.objects(uid1_uid2 = c , quizId = quizId )
            if(ret):
                ret = ret[0]
                wins_losses =  [ret.wins , ret.ties, ret.losses]
        else:
            ret =  UserClashHistory.objects(uid1_uid2 = c , quizId = None)
            if(ret):
                ret = ret[0]
                wins_losses [ret.wins , ret.ties, ret.losses]
        
        
        if(reversed):
            wins_losses.reverse()
            
        return wins_losses