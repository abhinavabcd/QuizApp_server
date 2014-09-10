'''
Created on Aug 26, 2014

@author: abhinav2
'''

import datetime

SERVER_ID = "1"
WebServersMap = {
                 "master":"http://192.168.0.10:8085"
                # "1":"http://192.168.0.10:8083"
                }

ExternalWebServersMap = {
                 "master":"http://192.168.0.10:8085"
                # "1":"http://192.168.0.10:8083"
                }


dbServer = ["192.168.0.10",27017,datetime.date(2014, 8 , 27) , 10] #10 => priority to choost/computing power