from random import randrange, random

from Db import UserWinsLosses


def generateRandomStats(user, quizzes):
        if(not user.getStats()): 
            for quiz in random.sample(quizzes,6):
                xpPoints = random.randrange(400, 2000)
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



def createBots(dbUtils):
    l= []
    quizzes = map(lambda x: x , dbUtils.getAllQuizzes())
    l.append(dbUtils.registerUser("Prashanthi", "123456789", "saloni123@gmail.com", "userb/prashanthi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True, preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    
    l.append(dbUtils.registerUser("Swathi reddy", "123456789", "swathi123@gmail.com", "userb/swathi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Shanvitha", "123457890", "Shanvitha@gmail.com", "userb/shanvitha.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Shradda", "123456789", "shradda@gmail.com", "userb/shradda.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Tanushri", "123456789", "Tanushri@gmail.com", "userb/tanushree.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Nidhi", "123456789", "nidhi@gmail.com", "userb/nidhi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    l.append(dbUtils.registerUser("Nandini chauhan", "123456789", "nandidni@gmail.com", "userb/namratha.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    generateRandomStats(l[-1] , quizzes) 
    return l