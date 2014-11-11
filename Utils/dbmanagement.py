



from Config import *
from Db import DbUtils
from mongoengine import *

def drop_db_all():
    dbConnection = connect('quizApp',host= dbServer[0], port = dbServer[1])
    print dir(dbConnection)
    dbConnection.drop_database('quizApp')
    