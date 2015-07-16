from random import randrange, random, sample
from Db import BotUids

UserWinsLosses = None

def generateRandomStats(user, quizzes):
        if(not user.getStats()): 
            for quiz in sample(quizzes,min(len(quizzes), 6)):
                xpPoints = randrange(400, 2000)
                user.updateStats(quiz.quizId , xpPoints) 
                wl = UserWinsLosses.objects(uid=user.uid, quizId = quiz.quizId)
                if(wl):
                    wl = wl.get(0)
                else:
                    wl = UserWinsLosses()
                    wl.uid = user.uid
                    wl.quizId = quiz.quizId
                    wl.wins=xpPoints/randrange(50, 120)#avg points 
                    wl.loss=xpPoints/randrange(50, 120)
                    wl.ties=xpPoints/randrange(50, 120)
                wl.save()


def addToBots(user):
    try:
        BotUids(uid = user.uid).save()
    except:
        print "error saving bot"
        pass

def createBots(dbUtils , _UserWinsLosses):
    global UserWinsLosses
    UserWinsLosses = _UserWinsLosses
    l= []
    import datetime
    quizzes = map(lambda x: x , dbUtils.getAllQuizzes(datetime.datetime.utcfromtimestamp(0)))
    print quizzes
    
    l.append(dbUtils.registerUser("Prashanthi", "123456789", "saloni123@gmail.com", "userb/prashanthi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True, preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Swathi reddy", "123456789", "swathi123@gmail.com", "userb/swathi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Venkat", "123457890", "Shanvitha@gmail.com", "https://storage.googleapis.com/quizapp-tollywood/userb/venkat.jpg", None , 0, "male", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Shradda", "123456789", "shradda@gmail.com", "userb/shradda.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Mahesh", "123456789", "Tanushri@gmail.com", "https://storage.googleapis.com/quizapp-tollywood/userb/abhinav_bindra.jpg", None , 0, "male", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Nidhi", "123456789", "nidhi@gmail.com", "userb/nidhi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Saket", "123456789", "nandidni@gmail.com", "https://storage.googleapis.com/quizapp-tollywood/userb/saketh.jpeg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    for user in l:
        addToBots(user)
    return l
