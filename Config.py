'''
Created on Aug 26, 2014

@author: abhinav2
'''

import datetime
from collections import namedtuple

SERVER_ID = "master"



DBServer= namedtuple("DBServer",["dbName","ip","port","username","password"],verbose=False, rename=False)

dbServer = DBServer(**{"dbName":"quizApp",
                       "ip":"XXXXXX",# "db.quizapp.appsandlabs.com",
                       "port": 27017,
                       "username": "quizapp",
                       "password":"XXXXX"
                       }) #10 => priority to choost/computing power


##### other 

GCM_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # # YOUR GCM API KEY HERE
GCM_HEADERS ={'Content-Type':'application/json',
              'Authorization':'key='+GCM_API_KEY
        }




