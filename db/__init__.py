from db.admin.server import BotUids
from server import configuration
__author__ = "abhinav"


import bson
import datetime
import itertools
import json
from mongoengine import *
import random
import string
import time

from Constants import *
import HelperFunctions








dbServer = []
dbConnection = None

def updateDbServer(self, dbServer):
    global dbServer , dbConnection
    dbServer = dbServer
    dbConnection = connect(dbServer.dbName, host=dbServer.ip, port=dbServer.port, username=dbServer.username, password=dbServer.password)

def init():
    BotUids.loadBotUids()
    updateDbServer(configuration.dbServer)


