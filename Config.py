'''
Created on Aug 26, 2014

@author: abhinav2
'''

import datetime

SERVER_ID = "master"

WebServersMap = {
                 "master":"http://10.240.118.190:8085"
                # "1":"http://192.168.0.10:8083"
                }

ExternalWebServersMap = {
                 "master":"http://130.211.241.110:8085"
                # "1":"http://192.168.0.10:8083"
                }

dbServer = ["10.240.64.162",27017,datetime.date(2014, 8 , 27) , 10] #10 => priority to choost/computing power
