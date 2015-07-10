import gspread
from Db import *
import json
from oauth2client.client import SignedJwtAssertionCredentials

def syncSpreadSheets(dbUtils, spreadSheetKey= '1fXS6D8crBo9p-xWyFG4keqHI5P8-9qqi230IKlcw5Iw',syncSpecific = ["tags"] , excludeSheets=[]):
#def syncSpreadSheets(dbUtils, spreadSheetKey= '18vi7Glhc_4qb8v1nMbnFz3NeYPamcVTQV0g7OzTQBZU',syncSpecific = ["tags"] , excludeSheets=[]):
    credentials_data = json.load(open('config_files/credentials.json'))
    scope = ['https://spreadsheets.google.com/feeds']    
    credentials = SignedJwtAssertionCredentials(credentials_data['client_email'], credentials_data['private_key'], scope)
    gc = gspread.authorize(credentials)

    wb = gc.open_by_key(spreadSheetKey)
    worksheets = wb.worksheets()
    
    'tags'
    tagWorksheet = None
    for i in worksheets:
        if(i.title.lower().startswith('tags') and  (not syncSpecific or i.title.lower() in syncSpecific) and not (i.title.lower in excludeSheets)):
            tagWorksheet = i
            records = tagWorksheet.get_all_records()
            count = len(records)
            for i in range(0,count): #exclude heading
                row = records[i]
                #after updating
                if(IS_NEW_DB or row.get("isDirty",False)):
                    print row
                    if(dbUtils.addOrModifyTag(**row)):
                        tagWorksheet.update_cell(i+2, len(row.keys()), 0)
                    
    
    'quiz'
    quiz_worksheet = None
    for i in worksheets:
        if(i.title.lower().startswith('quiz') and (not syncSpecific or i.title.lower() in syncSpecific) and not (i.title.lower in excludeSheets)):
            quiz_worksheet = i
            records = quiz_worksheet.get_all_records()
            count = len(records)
            for i in range(0,count): #exclude heading
                row = records[i]
                #after updating
                if(IS_NEW_DB or row.get("isDirty",False)):
                    print row
                    if(dbUtils.addOrModifyQuiz(**row)):
                        quiz_worksheet.update_cell(i+2, len(row.keys()), 0)
                    
    'categories'
    categoryWorksheet = None
    for i in worksheets:
        if(i.title.lower().startswith('categories') and (not syncSpecific or i.title.lower() in syncSpecific) and not (i.title.lower in excludeSheets)):
            categoryWorksheet = i
            records = categoryWorksheet.get_all_records()
            count = len(records)
            for i in range(0,count): #exclude heading
                row = records[i]
                #after updating
                if(IS_NEW_DB or row.get("isDirty",False)):
                    print row
                    if(dbUtils.addOrModifyCategory(**row)):
                        categoryWorksheet.update_cell(i+2, len(row.keys()), 0)
                    
    
    'questions'
    questionsWorksheet = None
    for i in worksheets:
        if(i.title.lower().startswith('questions') and (not syncSpecific or i.title.lower() in syncSpecific) and not (i.title.lower in excludeSheets)):
            questionsWorksheet = i
            records = questionsWorksheet.get_all_records()
            count = len(records)
            for i in range(0,count): #exclude heading
                row = records[i]
                row["questionId"] = "_".join(questionsWorksheet.title.lower().split("_")[1:])+"_"+str(row["questionId"])
                #after updating
                if(IS_NEW_DB or row.get("isDirty",False)):
                    print row
                    if(dbUtils.addOrModifyQuestion(**row)):
                        questionsWorksheet.update_cell(i+2, len(row.keys()), 0)

    'badges'
    badgesWorksheet = None
    for i in worksheets:
        if(i.title.lower().startswith('badges') and (not syncSpecific or i.title.lower() in syncSpecific) and not (i.title.lower in excludeSheets)):
            badgesWorksheet = i
            records = badgesWorksheet.get_all_records()
            count = len(records)
            for i in range(0,count): #exclude heading
                row = records[i]
                row["badgeId"] = "_".join(badgesWorksheet.title.lower().split("_")[1:])+"_"+str(row["badgeId"])
                #after updating
                if(IS_NEW_DB or row.get("isDirty",False)):
                    print row
                    if(dbUtils.addOrModifyBadge(**row)):
                        badgesWorksheet.update_cell(i+2, len(row.keys()), 0)

import sys
IS_NEW_DB = True if (len(sys.argv)>1  and sys.argv[1]=='syncall') else False

if __name__=="__main__":
    import Config
    dbUtils = DbUtils(Config.dbServer , _createBots = False) 
    syncSpreadSheets(dbUtils, syncSpecific=[] , excludeSheets=["tags"])
