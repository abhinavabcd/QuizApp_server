
def createBots(dbUtils):
    l= []
    l.append(dbUtils.registerUser("Prashanthi", "123456789", "saloni123@gmail.com", "userb/prashanthi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True, preUidText="00"))
    l.append(dbUtils.registerUser("Swathi reddy", "123456789", "swathi123@gmail.com", "userb/swathi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    l.append(dbUtils.registerUser("Shanvitha", "123457890", "Shanvitha@gmail.com", "userb/shanvitha.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    l.append(dbUtils.registerUser("Shradda", "123456789", "shradda@gmail.com", "userb/shradda.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    l.append(dbUtils.registerUser("Tanushri", "123456789", "Tanushri@gmail.com", "userb/tanushree.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    l.append(dbUtils.registerUser("Nidhi", "123456789", "nidhi@gmail.com", "userb/nidhi.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    l.append(dbUtils.registerUser("Nandini chauhan", "123456789", "nandidni@gmail.com", "userb/namratha.jpg", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    return l