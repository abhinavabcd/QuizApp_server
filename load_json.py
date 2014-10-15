import gspread
from Db import *
import os
import json
import re

#loads all json data into questions collection present in the folder
def loadJsonData(dbUtils):
    
    'questions'
    while True:
        direc = raw_input("Enter Directory Name:")
        if os.path.exists(direc):
            fileList = os.listdir(direc)
#            print fileList
            for fileName in fileList:
                if re.match(".*\.json", fileName)==None:
                    continue
                fname = fileName.split('_')
                records = json.load(open(direc+"/"+fileName))
                records = eval(records.decode('utf-8'))
                count = len(records)
                for i in range(0,count):
                    row = records[i]
                    del row['tagsAllSubjects']
                    del row['tagsAllIndex']
                    del row['_id']
                    row["questionId"] = fname[0][0]+"_"+fname[1][0]+"_"+str(row["questionId"])
#                    print row
                    if(not dbUtils.addOrModifyQuestion(**row)):
                        print "unable to update"
        else:
            print "Enter Valid Path"

if __name__=="__main__":
    import Config
    dbUtils = DbUtils(["192.168.0.10",27017,datetime.date(2014, 10 , 15) , 10] ) 
    loadJsonData(dbUtils)
