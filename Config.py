'''
Created on Aug 26, 2014

@author: abhinav2
'''

import datetime
from collections import namedtuple

SERVER_ID = "master"

WebServersMap = {
                 "master":"http://10.240.118.190:8085"
                # "1":"http://192.168.0.10:8083"
                }

ExternalWebServersMap = {
                 "master":"http://130.211.241.110:8085"
                # "1":"http://192.168.0.10:8083"
                }

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




