from db.admin.server import BotUids
__author__ = "abhinav"


import bson
import datetime
import itertools
import json
from mongoengine import *
import random
import string
import time

import Config
from Constants import *
import HelperFunctions








class DbUtils():

    dbServer = []
    dbConnection = None
    rrCount = 0
    rrPriorities = 0
    _users_cached_lru = 0
    _botUids = []
    def __init__(self , dbServer):
        self._updateDbServer(dbServer)
        self.loadBotUids()
#         self.dbServerAliases = dbServers.keys()
#         self.rrPriorities = datetime.date.today()
    def _updateDbServer(self, dbServer):
        self.dbServer = dbServer
        self.dbConnection = connect(dbServer.dbName, host=dbServer.ip, port=dbServer.port, username=dbServer.username, password=dbServer.password)
    


