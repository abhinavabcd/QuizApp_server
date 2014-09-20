
def createBots(dbUtils):
    l= []
    l.append(dbUtils.registerUser("Saloni", "123456789", "saloni123@gmail.com", "https://fbcdn-sphotos-c-a.akamaihd.net/hphotos-ak-xfp1/v/t1.0-9/254233_106415232786092_8382725_n.jpg?oh=473c3822974e6c05d7b2399c741b5486&oe=54C1B0FA&__gda__=1419196588_c35a7705666af1a9ecf78bbf11020e93", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True, preUidText="00"))
    l.append(dbUtils.registerUser("Swathi reddy", "123456789", "swathi123@gmail.com", "https://scontent-a-ams.xx.fbcdn.net/hphotos-xfa1/v/t1.0-9/1891022_1438348099735451_286927087_n.jpg?oh=255cbf8b8d7d8e05d0508dca27fd1277&oe=549560CB", None , 0, "female", "", "",facebookToken=None , gPlusToken=None, isActivated=True , preUidText="00"))
    return l