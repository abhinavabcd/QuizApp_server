#     
#     def getDbAliasFromUid(self, uid):
#         alias =  uid[0:4]
#         if(alias==DEFAULT_SERVER_ALIAS):
#             return "default"
#         return alias
#         
#     
#     def getRRDbAliasForUid(self):
#         #arrange by priority here
#         self.dbServerAliases[self.rrCount]
#         self.rrCount+=1
    # ## this should rather be connect to fb , gplus or refresh users list too not just register User
              
   

def test_insertInboxMessages(dbUtils , user1, user2):
    dbUtils.insertInboxMessage(user2, user1, "hello 1 ")
    dbUtils.insertInboxMessage(user1, user2, "hello 12 ")
    dbUtils.insertInboxMessage(user2, user1, "hello 123 ")
    dbUtils.insertInboxMessage(user2, user1, "hello 1234 ")
    dbUtils.insertInboxMessage(user1, user2, "hello 1345 ")
    dbUtils.insertInboxMessage(user1, user2, "hello 1346 ")
    
    for i in dbUtils.getMessagesBetween(user1, user2, -1):
        print i.to_json()
    

def test_insertFeed(dbUtils , user1 , user2):
    dbUtils.publishFeed(user1, "hello man , how are you doing ? ")
    print dbUtils.getRecentUserFeed(user2)
    
    
        
# save user testing
if __name__ == "__main__":
    import Config
#    dbUtils = DbUtils(Config.dbServer) 
    # dbUtils.addQuestion("question1","What is c++ first program" , None, "abcd", "a", "asdasd" , "hello world dude!" , 10, 10 , ["c","c++","computerScience"])
    # dbUtils.addOrModifyQuestion(**{'questionType': 0, 'questionId': "1_8", 'hint': '', 'pictures': '', 'explanation': '', 'tags': 'movies, puri-jagannath,pokiri', 'isDirty': 1, 'questionDescription': 'how many movies did puri jagannath made in year 2007?', 'time': 10, 'answer': 4, 'xp': 10, 'options': '4 , 7 , 1 , 3 , 2'})
    
    
#    user = json.loads('{"uid":"110040773460941325994","deviceId":"31e7d9178c3ca41f","emailId":"ramasolipuram@gmail.com","gender":"female","googlePlus":"ya29.bwDeBz20zufq7EsAAABrdZMKlgQzN92fxmcJNfFfWITpqkWp1o28YO4ZjOsAzNSurK-2NPS-lZ2xXE1326uxKdtorm8wn7dh4m-G9NT1nYfIO1ebw8jcARYscDIi-g","name":"Rama Reddy","pictureUrl":"https://lh3.googleusercontent.com/-TyulralhJFw/AAAAAAAAAAI/AAAAAAAAA9o/8KyUnpS-j_Y/photo.jpg?sz\\u003d200","isActivated":false,"createdAt":0.0,"birthday":0.0}')
#    userIp = "192.168.0.10"
#    userObject = dbUtils.registerUser( user["name"], user["deviceId"], user["emailId"], user.get("pictureUrl",None),user.get("coverUrl",None),user.get("birthday",None),user.get("gender",None),user.get("place",None),userIp , user.get("facebook",None),user.get("googlePlus",None),True)
                
    
#     user1 = dbUtils.registerUser("Abhinav reddy", "1234567", "abhinavabcd@gmail.com", "http://192.168.0.10:8081/images/kajal/kajal1.jpg", "", 0.0, "male", "india", "192.168.0.10", "something else", None, True)
#     user2 = dbUtils.registerUser("vinay reddy", "1234547", "vinaybhargavreddy@gmail.com", "http://192.168.0.10:8081/images/kajal/kajal2.jpg", "", 0.0, "male", "india", "192.168.0.10", "something else", None, True)
#     dbUtils.addsubscriber(user1, user2)
#     dbUtils.incrementLoginIndex(user1)
#     dbUtils.incrementLoginIndex(user2)
#     test_insertFeed(dbUtils , user1, user2)
    
#    test_insertInboxMessages(dbUtils)
    
    pass

# edit user

# add message of user